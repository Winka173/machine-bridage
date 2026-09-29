using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 22 D.1: the Meridian Coast at the head of the chapter screen (FrontMap has the rules). The land the brigade
    /// holds, Hegemon's, and from chapter 7 Thorne's, in their colours; the front line between them; a flag where a base
    /// was taken; a pin for each chapter shown (done, the current one, locked, "Coming soon" as prompt 20 C says), which
    /// opens it. Drawn in code from the save: a placeholder until an illustrated map comes (Docs/ASSET_DEBT.md).
    /// </summary>
    internal sealed class FrontMapView : VisualElement
    {
        private const int Across = 96, Down = 42;

        private static readonly CustomStyleProperty<Color> SeaColour = new("--front-sea"), LandColour = new("--front-land"),
            OursColour = new("--front-ours"), EnemyColour = new("--front-enemy"), ThorneColour = new("--front-thorne"),
            LineColour = new("--front-line"), CoastColour = new("--front-coast");

        private Color _sea = new(0.07f, 0.08f, 0.10f), _land = new(0.13f, 0.15f, 0.18f), _ours = new(0.42f, 0.75f, 1f),
            _enemy = new(0.88f, 0.32f, 0.23f), _thorne = new(0.66f, 0.47f, 0.91f), _lineColour = new(0.95f, 0.64f, 0.23f), _coast = new(0.23f, 0.26f, 0.29f);

        private readonly Action<int> _open;
        private readonly VisualElement _layer;
        private readonly List<(VisualElement pin, Vector2 at)> _pins = new();
        private readonly List<(VisualElement flag, Vector2 at)> _flags = new();
        private FrontState[,] _grid = new FrontState[Across, Down];
        private List<(Vector2 a, Vector2 b)> _line = new();
        private List<FrontSector> _sectors = new();

        public FrontMapView(Action<int> open)
        {
            _open = open;
            AddToClassList("fc-front__map");
            generateVisualContent += Draw;
            _layer = UiKit.Box("fc-front__layer");
            _layer.pickingMode = PickingMode.Ignore;
            Add(_layer);
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                var s = e.customStyle;
                if (s.TryGetValue(SeaColour, out var c)) _sea = c;
                if (s.TryGetValue(LandColour, out c)) _land = c;
                if (s.TryGetValue(OursColour, out c)) _ours = c;
                if (s.TryGetValue(EnemyColour, out c)) _enemy = c;
                if (s.TryGetValue(ThorneColour, out c)) _thorne = c;
                if (s.TryGetValue(LineColour, out c)) _lineColour = c;
                if (s.TryGetValue(CoastColour, out c)) _coast = c;
                MarkDirtyRepaint();
            });
            RegisterCallback<GeometryChangedEvent>(_ => Place());
        }

        /// <summary>The pieces of the front as last drawn (the checks read them).</summary>
        public IReadOnlyList<FrontSector> Sectors => _sectors;

        /// <summary>Reads the save again: the front, the flags and the pins.</summary>
        public void Refresh()
        {
            _sectors = FrontMap.Sectors();
            _grid = FrontMap.Grid(_sectors, Across, Down);
            _line = FrontMap.FrontLine(_grid);
            _layer.Clear();
            _pins.Clear();
            _flags.Clear();
            foreach (var map in FrontMap.Flags(_sectors))
            {
                var flag = Kit.Icon("flag", "fc-front__flag");
                flag.pickingMode = PickingMode.Ignore;
                _layer.Add(flag);
                _flags.Add((flag, FrontMap.Sites[map]));
            }
            var current = Campaign.All.Count > 0 ? Campaign.All[Campaign.Next].Chapter : 0;
            foreach (var chapter in Campaign.ShownChapters)
            {
                var number = chapter.Number;
                var soon = !Campaign.ChapterEnabled(number);
                var state = soon ? "soon" : Campaign.ChapterDone(number) ? "done" : number == current ? "current" : Campaign.ChapterOpen(number) ? "open" : "locked";
                var pin = Kit.Tappable("fc-front__pin fc-front__pin--" + state, () => _open(number));
                pin.Add(Kit.Text(chapter.Short, "fc-panel-title fc-front__pin-number"));
                pin.tooltip = Campaign.ChapterName(number) + " · " + Strings.Get($"chapter.{number}.title");
                pin.style.width = pin.style.height = Kit.TouchTarget;
                _layer.Add(pin);
                _pins.Add((pin, FrontMap.PinOf(chapter)));
            }
            _layer.pickingMode = PickingMode.Ignore;
            MarkDirtyRepaint();
            Place();
        }

        /// <summary>The pins and flags where their battlefields are, kept apart and inside the map.</summary>
        private void Place()
        {
            var r = contentRect;
            if (r.width <= 0f || r.height <= 0f || float.IsNaN(r.width)) return;
            var size = Kit.TouchTarget;
            var placed = new List<Rect>();
            foreach (var (pin, at) in _pins)
            {
                var x = Mathf.Clamp(at.x * r.width - size / 2f, 0f, r.width - size);
                var y = Mathf.Clamp(at.y * r.height - size / 2f, 0f, r.height - size);
                // A pin on another's place moves along, then down a row.
                for (var tries = 0; tries < 24 && placed.Exists(p => p.Overlaps(new Rect(x, y, size, size))); tries++)
                {
                    x += size * 0.55f;
                    if (x > r.width - size)
                    {
                        x = Mathf.Clamp(at.x * r.width - size / 2f, 0f, r.width - size);
                        y = y + size <= r.height - size ? y + size : Mathf.Max(0f, y - size);
                    }
                }
                placed.Add(new Rect(x, y, size, size));
                pin.style.left = x;
                pin.style.top = y;
                pin.style.width = size;
                pin.style.height = size;
            }
            foreach (var (flag, at) in _flags)
            {
                flag.style.left = Mathf.Clamp(at.x * r.width - 4f, 0f, r.width - 28f);
                flag.style.top = Mathf.Clamp(at.y * r.height - 30f, 0f, r.height - 28f);
            }
        }

        private void Draw(MeshGenerationContext context)
        {
            var r = contentRect;
            if (r.width <= 0f || r.height <= 0f) return;
            var p = context.painter2D;
            Vector2 At(Vector2 v) => new(r.x + v.x * r.width, r.y + v.y * r.height);
            // The sea, the land.
            p.fillColor = _sea;
            p.BeginPath();
            p.MoveTo(new Vector2(r.xMin, r.yMin));
            p.LineTo(new Vector2(r.xMax, r.yMin));
            p.LineTo(new Vector2(r.xMax, r.yMax));
            p.LineTo(new Vector2(r.xMin, r.yMax));
            p.ClosePath();
            p.Fill();
            void Shape(Vector2[] poly, bool fill)
            {
                p.BeginPath();
                p.MoveTo(At(poly[0]));
                for (var i = 1; i < poly.Length; i++) p.LineTo(At(poly[i]));
                p.ClosePath();
                if (fill) p.Fill();
                else p.Stroke();
            }
            p.fillColor = _land;
            Shape(FrontMap.Coast, true);
            foreach (var island in FrontMap.Islands) Shape(island, true);
            // Who holds what: a row's cells of one colour in one run.
            var cw = r.width / Across;
            var ch = r.height / Down;
            for (var y = 0; y < Down; y++)
                for (var x = 0; x < Across;)
                {
                    var state = _grid[x, y];
                    var end = x + 1;
                    while (end < Across && _grid[end, y] == state) end++;
                    if (state != FrontState.None)
                    {
                        var c = state switch { FrontState.Ours => _ours, FrontState.Betrayed => _thorne, _ => _enemy };
                        c.a = 0.42f;
                        p.fillColor = c;
                        p.BeginPath();
                        p.MoveTo(new Vector2(r.x + x * cw, r.y + y * ch));
                        p.LineTo(new Vector2(r.x + end * cw, r.y + y * ch));
                        p.LineTo(new Vector2(r.x + end * cw, r.y + (y + 1) * ch));
                        p.LineTo(new Vector2(r.x + x * cw, r.y + (y + 1) * ch));
                        p.ClosePath();
                        p.Fill();
                    }
                    x = end;
                }
            // The coast over the colours, then the front line.
            p.strokeColor = _coast;
            p.lineWidth = 2f;
            p.lineJoin = LineJoin.Round;
            Shape(FrontMap.Coast, false);
            foreach (var island in FrontMap.Islands) Shape(island, false);
            if (_line.Count > 0)
            {
                p.strokeColor = _lineColour;
                p.lineWidth = 4f;
                p.lineCap = LineCap.Round;
                p.BeginPath();
                foreach (var (a, b) in _line)
                {
                    p.MoveTo(At(a));
                    p.LineTo(At(b));
                }
                p.Stroke();
            }
            // The battlefields.
            foreach (var site in FrontMap.Sites.Values)
            {
                p.fillColor = _coast;
                p.BeginPath();
                p.Arc(At(site), 4f, Angle.Degrees(0f), Angle.Degrees(360f));
                p.Fill();
            }
        }
    }
}
