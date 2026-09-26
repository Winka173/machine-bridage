using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The battlefield from above, turned to match the camera (the square map shows as a
    /// diamond). Shows objectives, friendly and spotted enemy vehicles, incoming strikes and the
    /// camera's view; tapping it moves the camera there.
    /// </summary>
    public sealed class Minimap : VisualElement
    {
        private const float Cos45 = 0.70710678f;

        private readonly List<(Vector2 at, int team, bool air)> _blips = new();
        private readonly List<(Vector2 at, float radius, int owner, float progress)> _points = new();
        private readonly List<(Vector2 at, float radius)> _warnings = new();
        private readonly Vector2[] _view = new Vector2[4];
        private float _half = 80f;
        private bool _hasView;

        public Minimap()
        {
            AddToClassList("minimap");
            pickingMode = PickingMode.Position;
            generateVisualContent += Draw;
            RegisterCallback<PointerDownEvent>(e =>
            {
                Clicked?.Invoke(FromLocal(e.localPosition));
                e.StopPropagation();
            });
        }

        /// <summary>World position (x, z) tapped on the minimap.</summary>
        public event Action<Vector2> Clicked;

        /// <summary>Colour of the battlefield square (follows the map's ground).</summary>
        public Color Ground { get; set; } = new(0.25f, 0.33f, 0.24f, 0.85f);

        public void Begin(float halfSize)
        {
            _half = halfSize;
            _blips.Clear();
            _points.Clear();
            _warnings.Clear();
            _hasView = false;
        }

        public void Blip(Vector2 world, int team, bool air) => _blips.Add((world, team, air));

        public void Point(Vector2 world, float radius, int owner, float progress) => _points.Add((world, radius, owner, progress));

        public void Warning(Vector2 world, float radius) => _warnings.Add((world, radius));

        public void View(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
        {
            _view[0] = a;
            _view[1] = b;
            _view[2] = c;
            _view[3] = d;
            _hasView = true;
        }

        public void Flush() => MarkDirtyRepaint();

        private float Scale => Mathf.Min(contentRect.width, contentRect.height) / (_half * 2f * 1.4142f) * 0.96f;

        /// <summary>World (x, z) to local pixels: rotated -45 degrees so the camera's forward points up.</summary>
        private Vector2 ToLocal(Vector2 w)
        {
            var mx = (w.x + w.y) * Cos45;
            var my = (w.y - w.x) * Cos45;
            var c = contentRect.center;
            return new Vector2(c.x + mx * Scale, c.y - my * Scale);
        }

        private Vector2 FromLocal(Vector2 local)
        {
            var c = contentRect.center;
            var mx = (local.x - c.x) / Scale;
            var my = -(local.y - c.y) / Scale;
            return new Vector2((mx - my) * Cos45, (mx + my) * Cos45);
        }

        private void Draw(MeshGenerationContext context)
        {
            if (contentRect.width < 4f) return;
            var p = context.painter2D;

            // Map area.
            p.fillColor = Ground;
            p.strokeColor = new Color(0.65f, 0.89f, 0.75f, 0.35f);
            p.lineWidth = 1.2f;
            p.BeginPath();
            p.MoveTo(ToLocal(new Vector2(-_half, -_half)));
            p.LineTo(ToLocal(new Vector2(_half, -_half)));
            p.LineTo(ToLocal(new Vector2(_half, _half)));
            p.LineTo(ToLocal(new Vector2(-_half, _half)));
            p.ClosePath();
            p.Fill();
            p.Stroke();

            foreach (var (at, radius, owner, progress) in _points)
            {
                var colour = owner == 0 ? UiKit.Mint : owner == 1 ? UiKit.Danger : new Color(0.85f, 0.85f, 0.8f);
                p.fillColor = new Color(colour.r, colour.g, colour.b, 0.28f);
                p.strokeColor = colour;
                p.lineWidth = 1.5f;
                p.BeginPath();
                p.Arc(ToLocal(at), Mathf.Max(4f, radius * Scale), 0f, 360f);
                p.Fill();
                p.Stroke();
            }

            foreach (var (at, radius) in _warnings)
            {
                p.strokeColor = new Color(1f, 0.35f, 0.25f, 0.9f);
                p.lineWidth = 1.5f;
                p.BeginPath();
                p.Arc(ToLocal(at), Mathf.Max(5f, radius * Scale), 0f, 360f);
                p.Stroke();
            }

            foreach (var (at, team, air) in _blips)
            {
                p.fillColor = team == 0 ? UiKit.Mint : UiKit.Danger;
                var c = ToLocal(at);
                p.BeginPath();
                if (air)
                {
                    // Aircraft as small triangles.
                    p.MoveTo(c + new Vector2(0f, -3.5f));
                    p.LineTo(c + new Vector2(3f, 2.5f));
                    p.LineTo(c + new Vector2(-3f, 2.5f));
                    p.ClosePath();
                }
                else
                {
                    p.Arc(c, 2.2f, 0f, 360f);
                }
                p.Fill();
            }

            if (_hasView)
            {
                p.strokeColor = new Color(1f, 1f, 1f, 0.75f);
                p.lineWidth = 1f;
                p.BeginPath();
                p.MoveTo(ToLocal(_view[0]));
                for (var i = 1; i < 4; i++) p.LineTo(ToLocal(_view[i]));
                p.ClosePath();
                p.Stroke();
            }
        }
    }
}
