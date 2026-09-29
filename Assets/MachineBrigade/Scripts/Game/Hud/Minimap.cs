using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The battlefield from above, turned to match the camera (the camera's forward is up: north-west on the square
    /// maps, west on a long battlefield, whose rectangle it keeps, prompt 17 A.4). Under
    /// everything lies a picture of the map itself (<see cref="SetPicture"/>): the painted ground
    /// with roads, buildings, rock, trees, water and lava, in the map's real shape. On top it shows
    /// objectives, friendly and spotted enemy vehicles, incoming strikes and the camera's view;
    /// tapping it moves the camera there.
    /// </summary>
    public sealed class Minimap : VisualElement
    {
        private const float Cos45 = 0.70710678f;

        private readonly List<(Vector2 at, int team, bool air, bool dim)> _blips = new();
        private readonly List<(Vector2 at, float radius, int owner, float progress)> _points = new();
        private readonly List<(Vector2 at, float radius)> _warnings = new();

        /// <summary>Prompt 13 C.9: our aircraft's holding patterns, faint rings.</summary>
        private readonly List<Vector2> _holds = new();
        private readonly List<(Vector2 at, int kind)> _marks = new();
        private readonly Vector2[] _view = new Vector2[4];
        private readonly VisualElement _picture;
        private readonly VisualElement _overlay;
        private float _half = 80f;

        // The map's rectangle and the camera's forward and right on the ground (the square maps': north-west, north-east).
        private Vector2 _mapMin = new(-80f, -80f), _mapMax = new(80f, 80f);
        private Vector2 _forward = new(-Cos45, Cos45), _right = new(Cos45, Cos45);
        private float _turn = 45f;
        private bool _hasView;
        private bool _hasPicture;

        public Minimap()
        {
            AddToClassList("minimap");
            pickingMode = PickingMode.Position;
            generateVisualContent += DrawGround;

            // The map picture, turned 45 degrees like the camera; sized and centred on layout.
            _picture = new VisualElement { pickingMode = PickingMode.Ignore };
            _picture.style.position = Position.Absolute;
            _picture.style.rotate = new Rotate(_turn);
            _picture.style.display = DisplayStyle.None;
            Add(_picture);

            _overlay = new VisualElement { pickingMode = PickingMode.Ignore };
            _overlay.style.position = Position.Absolute;
            _overlay.style.left = _overlay.style.top = _overlay.style.right = _overlay.style.bottom = 0;
            _overlay.generateVisualContent += DrawMarks;
            Add(_overlay);

            RegisterCallback<GeometryChangedEvent>(_ => FitPicture());
            RegisterCallback<PointerDownEvent>(e =>
            {
                Clicked?.Invoke(FromLocal(e.localPosition));
                e.StopPropagation();
            });
        }

        /// <summary>World position (x, z) tapped on the minimap.</summary>
        public event Action<Vector2> Clicked;

        /// <summary>Colour of the battlefield square when there is no picture (follows the map's ground).</summary>
        public Color Ground { get; set; } = new(0.25f, 0.33f, 0.24f, 0.85f);

        /// <summary>Shows the map's own picture (north up, transparent beyond its outline) under the marks.</summary>
        public void SetPicture(Texture2D picture, float halfSize) => SetPicture(picture, new Vector2(-halfSize, -halfSize), new Vector2(halfSize, halfSize), -45f);

        /// <summary>The picture over a map's rectangle, the minimap turned so the camera's forward (its yaw, degrees) is up.</summary>
        public void SetPicture(Texture2D picture, Vector2 mapMin, Vector2 mapMax, float cameraYaw)
        {
            _mapMin = mapMin;
            _mapMax = mapMax;
            _half = Mathf.Max(mapMax.x - mapMin.x, mapMax.y - mapMin.y) * 0.5f;
            var yaw = cameraYaw * Mathf.Deg2Rad;
            _forward = new Vector2(Mathf.Sin(yaw), Mathf.Cos(yaw));
            _right = new Vector2(_forward.y, -_forward.x);
            // The picture is north up: turned clockwise until the camera's forward points up.
            _turn = -cameraYaw;
            _picture.style.rotate = new Rotate(_turn);
            _hasPicture = picture != null;
            _picture.style.backgroundImage = picture != null ? new StyleBackground(picture) : new StyleBackground(StyleKeyword.None);
            _picture.style.display = _hasPicture ? DisplayStyle.Flex : DisplayStyle.None;
            FitPicture();
            MarkDirtyRepaint();
        }

        public void Begin(float halfSize)
        {
            _blips.Clear();
            _points.Clear();
            _warnings.Clear();
            _holds.Clear();
            _marks.Clear();
            _bosses.Clear();
            _elites.Clear();
            _hasView = false;
        }

        public void Blip(Vector2 world, int team, bool air, bool dim = false) => _blips.Add((world, team, air, dim));

        /// <summary>A boss: a big pulsing red marker, wherever it is.</summary>
        public void Boss(Vector2 world) => _bosses.Add(world);

        private readonly List<Vector2> _bosses = new();

        /// <summary>An enemy elite: a gold ring round its blip (drawn over the blips).</summary>
        public void Elite(Vector2 world, bool air, bool dim) => _elites.Add((world, air, dim));

        private readonly List<(Vector2 at, bool air, bool dim)> _elites = new();

        public void Point(Vector2 world, float radius, int owner, float progress) => _points.Add((world, radius, owner, progress));

        public void Warning(Vector2 world, float radius) => _warnings.Add((world, radius));

        /// <summary>One of our aircraft's holding patterns (drawn once however many circle it).</summary>
        public void Holding(Vector2 world)
        {
            foreach (var h in _holds)
                if ((h - world).sqrMagnitude < 36f) return;
            _holds.Add(world);
        }

        /// <summary>A mission target: 0 destroy (red), 1 keep standing (blue), 2 scout (amber).</summary>
        public void Mark(Vector2 world, int kind) => _marks.Add((world, kind));

        public void View(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
        {
            _view[0] = a;
            _view[1] = b;
            _view[2] = c;
            _view[3] = d;
            _hasView = true;
        }

        public void Flush() => _overlay.MarkDirtyRepaint();

        private Vector2 MapCentre => (_mapMin + _mapMax) * 0.5f;

        /// <summary>The turned map's box: how wide and tall the rectangle stands on the minimap.</summary>
        private Vector2 Box
        {
            get
            {
                var size = _mapMax - _mapMin;
                return new Vector2(Mathf.Abs(size.x * _right.x) + Mathf.Abs(size.y * _right.y), Mathf.Abs(size.x * _forward.x) + Mathf.Abs(size.y * _forward.y));
            }
        }

        private float Scale => Mathf.Min(contentRect.width / Box.x, contentRect.height / Box.y) * 0.96f;

        /// <summary>The map's rectangle as a picture: its sides on screen, centred, then turned by the style's rotation.</summary>
        private void FitPicture()
        {
            if (!_hasPicture || contentRect.width < 4f) return;
            var size = (_mapMax - _mapMin) * Scale;
            var c = contentRect.center;
            _picture.style.width = size.x;
            _picture.style.height = size.y;
            _picture.style.left = c.x - size.x * 0.5f;
            _picture.style.top = c.y - size.y * 0.5f;
        }

        /// <summary>World (x, z) to local pixels: turned so the camera's forward points up.</summary>
        private Vector2 ToLocal(Vector2 w)
        {
            var d = w - MapCentre;
            var mx = Vector2.Dot(d, _right);
            var my = Vector2.Dot(d, _forward);
            var c = contentRect.center;
            return new Vector2(c.x + mx * Scale, c.y - my * Scale);
        }

        private Vector2 FromLocal(Vector2 local)
        {
            var c = contentRect.center;
            var mx = (local.x - c.x) / Scale;
            var my = -(local.y - c.y) / Scale;
            return MapCentre + _right * mx + _forward * my;
        }

        /// <summary>Without a picture: the plain map square, in the ground's colour.</summary>
        private void DrawGround(MeshGenerationContext context)
        {
            if (_hasPicture || contentRect.width < 4f) return;
            var p = context.painter2D;
            p.fillColor = Ground;
            p.strokeColor = new Color(0.65f, 0.89f, 0.75f, 0.35f);
            p.lineWidth = 1.2f;
            p.BeginPath();
            p.MoveTo(ToLocal(_mapMin));
            p.LineTo(ToLocal(new Vector2(_mapMax.x, _mapMin.y)));
            p.LineTo(ToLocal(_mapMax));
            p.LineTo(ToLocal(new Vector2(_mapMin.x, _mapMax.y)));
            p.ClosePath();
            p.Fill();
            p.Stroke();
        }

        private void DrawMarks(MeshGenerationContext context)
        {
            if (contentRect.width < 4f) return;
            var p = context.painter2D;

            foreach (var (at, radius, owner, progress) in _points)
            {
                var colour = owner == 0 ? UiKit.Mint : owner == 1 ? UiKit.Danger : new Color(0.95f, 0.95f, 0.9f);
                p.fillColor = new Color(colour.r, colour.g, colour.b, 0.3f);
                p.strokeColor = colour;
                p.lineWidth = 2f;
                p.BeginPath();
                p.Arc(ToLocal(at), Mathf.Max(5f, radius * Scale), 0f, 360f);
                p.Fill();
                p.Stroke();
            }

            foreach (var at in _holds)
            {
                p.strokeColor = new Color(UiKit.Mint.r, UiKit.Mint.g, UiKit.Mint.b, 0.45f);
                p.lineWidth = 1.2f;
                p.BeginPath();
                p.Arc(ToLocal(at), Mathf.Max(4f, 12f * Scale), 0f, 360f);
                p.Stroke();
            }

            foreach (var (at, radius) in _warnings)
            {
                p.strokeColor = new Color(1f, 0.35f, 0.25f, 0.95f);
                p.lineWidth = 1.8f;
                p.BeginPath();
                p.Arc(ToLocal(at), Mathf.Max(5f, radius * Scale), 0f, 360f);
                p.Stroke();
            }

            foreach (var (at, team, air, dim) in _blips)
            {
                var c = ToLocal(at);
                // A dark halo keeps each blip readable on any ground.
                p.fillColor = new Color(0.05f, 0.06f, 0.06f, dim ? 0.35f : 0.75f);
                p.BeginPath();
                p.Arc(c, air ? 4.6f : 3.6f, 0f, 360f);
                p.Fill();
                var tint = team == 0 ? UiKit.Mint : team == 2 ? new Color(0.92f, 0.9f, 0.8f) : UiKit.Danger;
                // Out of sight: dimmer, as the radar has it.
                p.fillColor = dim ? new Color(tint.r, tint.g, tint.b, 0.45f) : tint;
                p.BeginPath();
                if (air)
                {
                    // Aircraft as small triangles.
                    p.MoveTo(c + new Vector2(0f, -3.8f));
                    p.LineTo(c + new Vector2(3.3f, 2.6f));
                    p.LineTo(c + new Vector2(-3.3f, 2.6f));
                    p.ClosePath();
                }
                else
                {
                    p.Arc(c, 2.5f, 0f, 360f);
                }
                p.Fill();
            }

            // Elites: a gold ring with a dark edge round the blip, dimmer out of sight.
            foreach (var (at, air, dim) in _elites)
            {
                var c = ToLocal(at);
                var r = air ? 6.4f : 5.6f;
                p.strokeColor = new Color(0.05f, 0.06f, 0.06f, dim ? 0.4f : 0.8f);
                p.lineWidth = 3.2f;
                p.BeginPath();
                p.Arc(c, r, 0f, 360f);
                p.Stroke();
                p.strokeColor = new Color(1f, 0.78f, 0.25f, dim ? 0.5f : 1f);
                p.lineWidth = 1.7f;
                p.BeginPath();
                p.Arc(c, r, 0f, 360f);
                p.Stroke();
            }

            // Mission targets on top of everything, as diamonds (the markers over them in the battle).
            foreach (var (at, kind) in _marks)
            {
                var c = ToLocal(at);
                var colour = kind == 1 ? new Color(0.35f, 0.7f, 1f) : kind == 2 ? new Color(1f, 0.72f, 0.2f) : new Color(1f, 0.3f, 0.22f);
                void Diamond(float r)
                {
                    p.BeginPath();
                    p.MoveTo(c + new Vector2(0f, -r));
                    p.LineTo(c + new Vector2(r, 0f));
                    p.LineTo(c + new Vector2(0f, r));
                    p.LineTo(c + new Vector2(-r, 0f));
                    p.ClosePath();
                    p.Fill();
                }
                p.fillColor = new Color(0.05f, 0.06f, 0.06f, 0.85f);
                Diamond(7f);
                p.fillColor = colour;
                Diamond(5f);
            }

            // Bosses: a red disc in a pulsing ring, over everything but the view frame.
            var pulse = 0.5f + 0.5f * Mathf.Sin(Time.unscaledTime * 5f);
            foreach (var at in _bosses)
            {
                var c = ToLocal(at);
                p.strokeColor = new Color(1f, 0.25f, 0.2f, 0.5f + 0.5f * pulse);
                p.lineWidth = 2f;
                p.BeginPath();
                p.Arc(c, 9f + 3f * pulse, 0f, 360f);
                p.Stroke();
                p.fillColor = new Color(0.05f, 0.06f, 0.06f, 0.9f);
                p.BeginPath();
                p.Arc(c, 7f, 0f, 360f);
                p.Fill();
                p.fillColor = new Color(1f, 0.28f, 0.22f);
                p.BeginPath();
                p.Arc(c, 5.2f, 0f, 360f);
                p.Fill();
            }

            if (_hasView)
            {
                p.strokeColor = new Color(1f, 1f, 1f, 0.85f);
                p.lineWidth = 1.2f;
                p.BeginPath();
                p.MoveTo(ToLocal(_view[0]));
                for (var i = 1; i < 4; i++) p.LineTo(ToLocal(_view[i]));
                p.ClosePath();
                p.Stroke();
            }
        }
    }
}
