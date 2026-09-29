using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// A camp as the Base screen draws it (prompt 14 B): world points to the picture's 0..1 across and down, the
    /// camp's front up. From the map's captured picture when there is one (BaseMapArt), else worked out from the
    /// camp itself (the HQ, its slots and a margin).
    /// </summary>
    internal sealed class CampFrame
    {
        public Texture2D Picture;
        public UnityEngine.Vector2 Centre;
        public UnityEngine.Vector2 Up;
        public float Width, Height;

        /// <summary>The captured picture's own frame, when there is one (its projection is used as it is).</summary>
        public BaseMapPicture Art;

        /// <summary>
        /// The ways the enemy comes in: the arrow's head at the camp's edge (picture space, 0..1) and the way in as a
        /// unit direction on the picture (y down; the same in pixels and on screen).
        /// </summary>
        public readonly List<(UnityEngine.Vector2 at, UnityEngine.Vector2 dir)> Arrows = new();

        /// <summary>The drop zone (picture space) and its radius as a share of the picture's width; a radius of 0: none.</summary>
        public UnityEngine.Vector2 DropZone;

        public float DropRadius;

        /// <summary>How bright the camp's ground is (0 dark .. 1 snow): the map dims a bright one under its slots.</summary>
        public float Brightness = 0.4f;

        /// <summary>Metres kept round the camp's slots when the frame is worked out from the camp.</summary>
        public const float Margin = 16f;

        private UnityEngine.Vector2 Right => new(Up.y, -Up.x);

        public UnityEngine.Vector2 ToPicture(System.Numerics.Vector2 world)
        {
            if (Art != null) return Art.ToPicture(world);
            var d = new UnityEngine.Vector2(world.X, world.Y) - Centre;
            return new UnityEngine.Vector2(0.5f + UnityEngine.Vector2.Dot(d, Right) / Width, 0.5f - UnityEngine.Vector2.Dot(d, Up) / Height);
        }

        /// <summary>A frame from the camp alone: front up, the slots and the HQ with a margin, no picture.</summary>
        public static CampFrame FromCamp(BaseSiteDef site)
        {
            var up = new UnityEngine.Vector2(Mathf.Sin(site.Heading), Mathf.Cos(site.Heading));
            var right = new UnityEngine.Vector2(up.y, -up.x);
            var hq = new UnityEngine.Vector2(site.Hq.X, site.Hq.Y);
            float minX = 0f, maxX = 0f, minY = 0f, maxY = 0f;
            foreach (var s in site.Slots)
            {
                var d = new UnityEngine.Vector2(s.Position.X, s.Position.Y) - hq;
                var x = UnityEngine.Vector2.Dot(d, right);
                var y = UnityEngine.Vector2.Dot(d, up);
                minX = Mathf.Min(minX, x);
                maxX = Mathf.Max(maxX, x);
                minY = Mathf.Min(minY, y);
                maxY = Mathf.Max(maxY, y);
            }
            var centre = hq + right * ((minX + maxX) * 0.5f) + up * ((minY + maxY) * 0.5f);
            return new CampFrame
            {
                Centre = centre, Up = up, Width = maxX - minX + Margin * 2f, Height = maxY - minY + Margin * 2f,
            };
        }

        /// <summary>The frame for a map's camp: its captured picture's (see <see cref="BaseMapArt"/>) when there is one, else the camp's own.</summary>
        public static CampFrame For(string mapId, BaseSiteDef site)
        {
            var art = BaseMapArt.For(mapId);
            if (art == null) return FromCamp(site);
            var frame = new CampFrame
            {
                Art = art, Picture = art.Texture, Centre = new UnityEngine.Vector2(art.Centre.X, art.Centre.Y), Up = new UnityEngine.Vector2(art.Up.X, art.Up.Y),
                Width = art.MetresPerWidth, Height = art.MetresPerHeight, DropZone = art.DropZone, DropRadius = art.DropRadius, Brightness = art.Brightness,
            };
            foreach (var (at, dir) in art.Arrows) frame.Arrows.Add((at, dir));
            return frame;
        }
    }

    /// <summary>
    /// A slot's face on the base map (prompt 14 B3-B6): square for towers, sized by class (small, medium 1.4 times,
    /// large twice), a hexagon for a utility module; an empty one says its size in words, a filled one shows the
    /// tower's render, its rank as small ticks and a mark when a branch is chosen; a slot the HQ level has not
    /// opened is locked with the level it needs. Its fill and line come from the stylesheet (--slot-fill,
    /// --slot-line), so its states are classes.
    /// </summary>
    internal sealed class SlotFace : VisualElement
    {
        private static readonly CustomStyleProperty<Color> Fill = new("--slot-fill");
        private static readonly CustomStyleProperty<Color> Line = new("--slot-line");
        private static readonly CustomStyleProperty<Color> Tick = new("--slot-tick");

        private Color _fill = Color.clear, _line = Color.clear, _tick = Color.clear;
        private readonly bool _hex;
        private int _rank;

        public SlotFace(bool hex)
        {
            _hex = hex;
            pickingMode = PickingMode.Ignore;
            AddToClassList("fc-base-face");
            EnableInClassList("fc-base-face--hex", hex);
            Art = Kit.Box("fc-base-face__art");
            Add(Art);
            Word = Kit.Text("", "fc-base-face__word");
            Add(Word);
            Lock = Kit.Icon("lock", "fc-base-face__lock");
            Add(Lock);
            Need = Kit.Text("", "fc-base-face__need");
            Add(Need);
            Branch = Kit.Icon("upgrade", "fc-base-face__branch");
            Add(Branch);
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                if (e.customStyle.TryGetValue(Fill, out var f)) _fill = f;
                if (e.customStyle.TryGetValue(Line, out var l)) _line = l;
                if (e.customStyle.TryGetValue(Tick, out var t)) _tick = t;
                MarkDirtyRepaint();
            });
        }

        public VisualElement Art { get; }
        public Label Word { get; }
        public IconElement Lock { get; }

        /// <summary>A closed slot's HQ level, inside its face (the lock at its corner).</summary>
        public Label Need { get; }
        public IconElement Branch { get; }

        /// <summary>The tower's rank as ticks along the face's foot (0: none).</summary>
        public int Rank
        {
            get => _rank;
            set
            {
                if (_rank == value) return;
                _rank = value;
                MarkDirtyRepaint();
            }
        }

        private void Draw(MeshGenerationContext context)
        {
            var r = contentRect;
            if (r.width < 2f) return;
            var p = context.painter2D;
            if (_hex)
            {
                // A flat-topped hexagon filling the face's box.
                var c = r.center;
                var rx = r.width * 0.5f;
                var ry = r.height * 0.5f;
                p.BeginPath();
                for (var i = 0; i < 6; i++)
                {
                    var a = Mathf.Deg2Rad * (60f * i);
                    var v = c + new UnityEngine.Vector2(Mathf.Cos(a) * rx, Mathf.Sin(a) * ry);
                    if (i == 0) p.MoveTo(v);
                    else p.LineTo(v);
                }
                p.ClosePath();
                p.fillColor = _fill;
                p.Fill();
                p.strokeColor = _line;
                p.lineWidth = 2f;
                p.Stroke();
            }
            if (_rank <= 0) return;
            // Up to ten ticks, 2 px wide with 1 px between, centred at the foot.
            var n = Mathf.Min(_rank, 10);
            var width = n * 3f - 1f;
            var x0 = r.center.x - width * 0.5f;
            p.fillColor = _tick;
            for (var i = 0; i < n; i++)
            {
                p.BeginPath();
                p.MoveTo(new UnityEngine.Vector2(x0 + i * 3f, r.yMax - 6f));
                p.LineTo(new UnityEngine.Vector2(x0 + i * 3f + 2f, r.yMax - 6f));
                p.LineTo(new UnityEngine.Vector2(x0 + i * 3f + 2f, r.yMax - 2f));
                p.LineTo(new UnityEngine.Vector2(x0 + i * 3f, r.yMax - 2f));
                p.ClosePath();
                p.Fill();
            }
        }
    }

    /// <summary>
    /// The base map (prompt 14 B): the camp's picture, zoomed and panned with two fingers (or the mouse wheel and a
    /// drag on the ground), the enemy's ways in as red arrows, and on request the ground and air cover of every
    /// tower (B7) and one tower's range rings. Slots are placed by the screen through <see cref="Place"/>; their
    /// targets keep their size at every zoom, their faces grow with it.
    /// </summary>
    internal sealed class CampMap : VisualElement
    {
        private static readonly CustomStyleProperty<Color> ArrowColour = new("--base-arrow");
        private static readonly CustomStyleProperty<Color> GroundColour = new("--base-range-ground");
        private static readonly CustomStyleProperty<Color> AirColour = new("--base-range-air");
        private static readonly CustomStyleProperty<Color> RingColour = new("--base-ring");
        private static readonly CustomStyleProperty<Color> DropColour = new("--base-drop");

        public const float MinZoom = 1f, MaxZoom = 3f;

        private readonly VisualElement _world, _paint, _scrim;
        private Color _arrow = Color.red, _ground = Color.clear, _air = Color.clear, _ring = Color.white, _drop = Color.clear;
        private CampFrame _frame;
        private float _zoom = 1f;
        private UnityEngine.Vector2 _pan;
        private readonly Dictionary<int, UnityEngine.Vector2> _pointers = new();
        private float _pinchDistance;
        private UnityEngine.Vector2 _dragFrom;
        private bool _panning;
        private Rect? _focus;
        private bool _moved;

        public CampMap()
        {
            AddToClassList("fc-base-map");
            pickingMode = PickingMode.Position;
            style.overflow = Overflow.Hidden;
            _world = Kit.Box("fc-base-map__world");
            _world.style.position = Position.Absolute;
            Add(_world);
            // A scrim over a bright picture (snow) so the slots read on it; its strength is the picture's brightness.
            _scrim = Kit.Box("fc-base-map__scrim");
            _scrim.style.position = Position.Absolute;
            _scrim.style.left = _scrim.style.top = _scrim.style.right = _scrim.style.bottom = 0;
            _world.Add(_scrim);
            _paint = new VisualElement { pickingMode = PickingMode.Ignore };
            _paint.AddToClassList("fc-base-map__paint");
            _paint.style.position = Position.Absolute;
            _paint.style.left = _paint.style.top = _paint.style.right = _paint.style.bottom = 0;
            _paint.generateVisualContent += Draw;
            _world.Add(_paint);
            Slots = Kit.Box("fc-base-map__slots");
            Slots.style.position = Position.Absolute;
            Slots.style.left = Slots.style.top = Slots.style.right = Slots.style.bottom = 0;
            _world.Add(Slots);
            RegisterCallback<GeometryChangedEvent>(_ => Layout());
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                if (e.customStyle.TryGetValue(ArrowColour, out var a)) _arrow = a;
                if (e.customStyle.TryGetValue(GroundColour, out var g)) _ground = g;
                if (e.customStyle.TryGetValue(AirColour, out var air)) _air = air;
                if (e.customStyle.TryGetValue(RingColour, out var r)) _ring = r;
                if (e.customStyle.TryGetValue(DropColour, out var d)) _drop = d;
                _paint.MarkDirtyRepaint();
            });
            RegisterCallback<PointerDownEvent>(OnDown);
            RegisterCallback<PointerMoveEvent>(OnMove);
            RegisterCallback<PointerUpEvent>(OnUp);
            RegisterCallback<PointerCancelEvent>(e => _pointers.Remove(e.pointerId));
            RegisterCallback<WheelEvent>(e =>
            {
                ZoomAt(e.localMousePosition, e.delta.y < 0f ? 1.15f : 1f / 1.15f);
                e.StopPropagation();
            });
        }

        /// <summary>The layer the slots go on (the screen fills it).</summary>
        public VisualElement Slots { get; }

        /// <summary>Raised after every layout, zoom or pan: the screen re-places its slots.</summary>
        public event Action Moved;

        public CampFrame Frame
        {
            get => _frame;
            set
            {
                _frame = value;
                _zoom = 1f;
                _pan = UnityEngine.Vector2.zero;
                _focus = null;
                _moved = false;
                _world.style.backgroundImage = value?.Picture != null ? new StyleBackground(value.Picture) : new StyleBackground(StyleKeyword.None);
                _scrim.style.opacity = value?.Picture != null ? Mathf.Clamp((value.Brightness - 0.3f) * 1.1f, 0f, 0.55f) : 0f;
                Layout();
            }
        }

        public float Zoom => _zoom;

        /// <summary>Panel pixels a metre at the current zoom.</summary>
        public float PixelsPerMetre => _frame == null ? 1f : WorldSize.x / _frame.Width;

        /// <summary>The towers' cover to draw (B7): each tower's position in picture space and its ground and air reach (metres); null: none.</summary>
        public List<(UnityEngine.Vector2 at, float ground, float air)> Cover { get; set; }

        /// <summary>One tower's rings (the picked one): its position, reach and shortest range (metres); null: none.</summary>
        public (UnityEngine.Vector2 at, float reach, float min)? Rings { get; set; }

        public void Repaint() => _paint.MarkDirtyRepaint();

        /// <summary>A point in picture space (0..1) in the map's own coordinates.</summary>
        public UnityEngine.Vector2 ToLocal(UnityEngine.Vector2 picture)
        {
            var size = WorldSize;
            return WorldOrigin + new UnityEngine.Vector2(picture.x * size.x, picture.y * size.y);
        }

        /// <summary>Puts an element's centre at a point in picture space (in the slot layer).</summary>
        public void Place(VisualElement element, UnityEngine.Vector2 picture, float size)
        {
            var w = WorldSize;
            element.style.left = picture.x * w.x - size * 0.5f;
            element.style.top = picture.y * w.y - size * 0.5f;
        }

        /// <summary>The picture's size at zoom 1: the frame fitted inside the map's box.</summary>
        private UnityEngine.Vector2 FitSize()
        {
            var box = contentRect.size;
            if (_frame == null || box.x < 2f || box.y < 2f || float.IsNaN(box.x)) return new UnityEngine.Vector2(Mathf.Max(1f, box.x), Mathf.Max(1f, box.y));
            var scale = Mathf.Min(box.x / _frame.Width, box.y / _frame.Height);
            return new UnityEngine.Vector2(_frame.Width * scale, _frame.Height * scale);
        }

        private UnityEngine.Vector2 WorldSize => FitSize() * _zoom;

        private UnityEngine.Vector2 WorldOrigin
        {
            get
            {
                var box = contentRect.size;
                return (box - WorldSize) * 0.5f + _pan;
            }
        }

        /// <summary>
        /// The view the map opens on: this part of the picture (0..1) filling the box, the rest a pinch away (the camp,
        /// not the whole picture with its margins, so the slots are as big as they can be at the default zoom).
        /// </summary>
        public void Focus(Rect picture)
        {
            _focus = picture;
            _moved = false;
            Layout();
        }

        private void ApplyFocus()
        {
            if (_focus is not { } r || _moved) return;
            var box = contentRect.size;
            var fit = FitSize();
            if (box.x < 2f || fit.x < 2f || r.width <= 0f || r.height <= 0f) return;
            _zoom = Mathf.Clamp(Mathf.Min(box.x / (r.width * fit.x), box.y / (r.height * fit.y)), MinZoom, MaxZoom);
            var size = fit * _zoom;
            _pan = new UnityEngine.Vector2(size.x * (0.5f - r.center.x), size.y * (0.5f - r.center.y));
        }

        private void Layout()
        {
            ApplyFocus();
            ClampPan();
            var size = WorldSize;
            var origin = WorldOrigin;
            _world.style.left = origin.x;
            _world.style.top = origin.y;
            _world.style.width = size.x;
            _world.style.height = size.y;
            _paint.MarkDirtyRepaint();
            Moved?.Invoke();
        }

        private void ClampPan()
        {
            var box = contentRect.size;
            var size = FitSize() * _zoom;
            var slack = (size - box) * 0.5f;
            _pan.x = Mathf.Clamp(_pan.x, -Mathf.Max(0f, slack.x), Mathf.Max(0f, slack.x));
            _pan.y = Mathf.Clamp(_pan.y, -Mathf.Max(0f, slack.y), Mathf.Max(0f, slack.y));
        }

        /// <summary>Zooms by a factor round a point of the map (its own coordinates).</summary>
        public void ZoomAt(UnityEngine.Vector2 local, float factor)
        {
            var before = _zoom;
            _zoom = Mathf.Clamp(_zoom * factor, MinZoom, MaxZoom);
            if (Mathf.Approximately(before, _zoom)) return;
            _moved = true;
            // Keep the point under the fingers where it was.
            var centre = contentRect.size * 0.5f;
            _pan = (_pan - (local - centre)) * (_zoom / before) + (local - centre);
            Layout();
        }

        public void ResetView()
        {
            _zoom = 1f;
            _pan = UnityEngine.Vector2.zero;
            _moved = false;
            Layout();
        }

        private void OnDown(PointerDownEvent e)
        {
            _pointers[e.pointerId] = e.localPosition;
            if (_pointers.Count == 2)
            {
                var it = _pointers.Values.GetEnumerator();
                it.MoveNext();
                var a = it.Current;
                it.MoveNext();
                _pinchDistance = UnityEngine.Vector2.Distance(a, it.Current);
                _panning = false;
            }
            else if (_pointers.Count == 1)
            {
                _dragFrom = e.localPosition;
                _panning = false;
            }
        }

        private void OnMove(PointerMoveEvent e)
        {
            if (!_pointers.ContainsKey(e.pointerId)) return;
            _pointers[e.pointerId] = e.localPosition;
            if (_pointers.Count == 2)
            {
                var it = _pointers.Values.GetEnumerator();
                it.MoveNext();
                var a = it.Current;
                it.MoveNext();
                var b = it.Current;
                var d = UnityEngine.Vector2.Distance(a, b);
                if (_pinchDistance > 1f && d > 1f) ZoomAt((a + b) * 0.5f, d / _pinchDistance);
                _pinchDistance = d;
                e.StopPropagation();
                return;
            }
            // One finger on the ground: a pan once it has moved a little (a tap stays a tap).
            var delta = (UnityEngine.Vector2)e.localPosition - _dragFrom;
            if (!_panning && delta.sqrMagnitude < 144f) return;
            if (!DragsGround) return;
            _panning = true;
            _moved = true;
            _pan += delta;
            _dragFrom = e.localPosition;
            Layout();
        }

        private void OnUp(PointerUpEvent e)
        {
            _pointers.Remove(e.pointerId);
            if (_pointers.Count < 2) _pinchDistance = 0f;
            if (_pointers.Count == 0) _panning = false;
        }

        /// <summary>Whether a one-finger drag pans the map now (not while the screen drags a tower).</summary>
        public bool DragsGround { get; set; } = true;

        /// <summary>A one-finger drag panned the map since the finger went down.</summary>
        public bool Panned => _panning;

        private void Draw(MeshGenerationContext context)
        {
            if (_frame == null) return;
            var p = context.painter2D;
            var size = WorldSize;
            var ppm = size.x / _frame.Width;
            UnityEngine.Vector2 Px(UnityEngine.Vector2 picture) => new(picture.x * size.x, picture.y * size.y);

            // The cover: every tower's ground reach, then its air reach, each filled as one union (a place covered twice is
            // no darker than once), so the lit areas are what is defended and the bare ground is not.
            if (Cover != null)
            {
                void Union(Color colour, Func<(UnityEngine.Vector2 at, float ground, float air), float> reach)
                {
                    var any = false;
                    p.BeginPath();
                    foreach (var c in Cover)
                    {
                        var r = reach(c) * ppm;
                        if (r <= 0.5f) continue;
                        var centre = Px(c.at);
                        p.MoveTo(centre + new UnityEngine.Vector2(r, 0f));
                        p.Arc(centre, r, 0f, 360f);
                        p.ClosePath();
                        any = true;
                    }
                    if (!any) return;
                    p.fillColor = colour;
                    p.Fill(FillRule.NonZero);
                }
                Union(_ground, c => c.ground);
                Union(_air, c => c.air);
            }
            if (Rings is { } rings)
            {
                var centre = Px(rings.at);
                p.strokeColor = _ring;
                p.lineWidth = 2f;
                if (rings.reach > 0f)
                {
                    p.BeginPath();
                    p.Arc(centre, rings.reach * ppm, 0f, 360f);
                    p.Stroke();
                }
                if (rings.min > 0f)
                {
                    p.lineWidth = 1.5f;
                    p.BeginPath();
                    p.Arc(centre, rings.min * ppm, 0f, 360f);
                    p.Stroke();
                }
            }
            // The drop zone, where bought vehicles arrive.
            if (_frame.DropRadius > 0f)
            {
                p.strokeColor = _drop;
                p.lineWidth = 2f;
                p.BeginPath();
                p.Arc(Px(_frame.DropZone), _frame.DropRadius * size.x, 0f, 360f);
                p.Stroke();
            }
            // The enemy's ways in: a red arrow at the camp's edge pointing in.
            p.fillColor = _arrow;
            foreach (var (at, dir) in _frame.Arrows)
            {
                var tip = Px(at);
                var d = dir.normalized;
                var side = new UnityEngine.Vector2(-d.y, d.x);
                const float length = 34f, head = 16f, shaft = 5f;
                var back = tip - d * length;
                var neck = tip - d * head;
                p.BeginPath();
                p.MoveTo(tip);
                p.LineTo(neck + side * head * 0.75f);
                p.LineTo(neck + side * shaft);
                p.LineTo(back + side * shaft);
                p.LineTo(back - side * shaft);
                p.LineTo(neck - side * shaft);
                p.LineTo(neck - side * head * 0.75f);
                p.ClosePath();
                p.Fill();
            }
        }
    }


    /// <summary>
    /// The tower tray down the Base and Outpost screens' left (prompt 14 C): tabs by size (small, medium, large,
    /// utility) down its edge, and the cards of the chosen size as compact rows (the render, the short name, how
    /// many stand in the base); a tower not unlocked yet is dimmed and says where it unlocks. The list scrolls, with
    /// room after its last row. The screen tells it which card is carried and which fit (<see cref="Refresh"/>).
    /// </summary>
    internal sealed class TowerTray
    {
        public enum Tab
        {
            Small,
            Medium,
            Large,
            Utility,
        }

        private readonly Catalog _catalog;
        private readonly Action<string> _tapped;
        private readonly Action<PointerDownEvent, string> _pressed;
        private readonly List<(VisualElement tab, Tab kind)> _tabs = new();
        private readonly ScrollView _list;
        private readonly Tab[] _kinds;
        private Tab _tab;

        public TowerTray(Catalog catalog, Tab[] kinds, Action<string> tapped, Action<PointerDownEvent, string> pressed = null)
        {
            _catalog = catalog;
            _kinds = kinds;
            _tapped = tapped;
            _pressed = pressed;
            _tab = kinds[0];
            Root = Kit.Box("fc-base-tray");
            var tabs = Kit.Box("fc-base-tray__tabs");
            foreach (var kind in kinds)
            {
                var k = kind;
                var tab = Kit.Tappable("fc-base-tray__tab", () =>
                {
                    _tab = k;
                    Changed?.Invoke();
                });
                tab.Add(Kit.Icon(kind == Tab.Utility ? "module" : BaseScreen.SizeIcon((SlotSize)(int)kind), "fc-base-tray__tab-icon"));
                tab.Add(Kit.Text(Kit.Caps(Name(kind)), "fc-base-tray__tab-word"));
                tabs.Add(tab);
                _tabs.Add((tab, kind));
            }
            Root.Add(tabs);
            _list = Kit.Scroll(ScrollViewMode.Vertical, "fc-base-tray__list");
            Root.Add(_list);
        }

        public VisualElement Root { get; }

        /// <summary>The size tab in view.</summary>
        public Tab Shown
        {
            get => _tab;
            set => _tab = value;
        }

        /// <summary>A tab was chosen (the screen refreshes).</summary>
        public event Action Changed;

        public static string Name(Tab kind) => kind == Tab.Utility ? Strings.Get("camp.utility") : Strings.Get("camp.size." + kind.ToString().ToLowerInvariant());

        /// <summary>The cards of a tab: the loadout towers of that size, or the utility modules, by name.</summary>
        public List<string> CardsOf(Tab kind)
        {
            var list = new List<string>();
            foreach (var def in _catalog.Vehicles.Values)
            {
                if (def.Fort == null || def.BranchOf != null) continue;
                if (kind == Tab.Utility ? def.Fort.Kind != FortKind.Utility : def.Fort.Kind != FortKind.Tower || !Sim.Modes.TowerCards.IsLoadoutTower(def.Id) || (int)def.Fort.Size != (int)kind) continue;
                list.Add(def.Id);
            }
            list.Sort((a, b) => string.Compare(Strings.Short(a), Strings.Short(b), StringComparison.CurrentCulture));
            return list;
        }

        /// <param name="carried">The card being placed (armed or dragged), or null.</param>
        /// <param name="inUse">How many of a card stand in the base.</param>
        /// <param name="fits">Whether a card fits the slot picked first (null: no slot picked).</param>
        public void Refresh(string carried, Func<string, int> inUse, Func<string, bool> fits)
        {
            foreach (var (tab, kind) in _tabs) tab.EnableInClassList("fc-base-tray__tab--on", kind == _tab);
            _list.Clear();
            foreach (var id in CardsOf(_tab))
            {
                var card = id;
                var locked = !PlayerProfile.IsUnlocked(id);
                var row = Kit.Box("fc-base-row", PickingMode.Position);
                row.AddManipulator(new Tap(() =>
                {
                    UiKit.RaiseClicked();
                    _tapped?.Invoke(card);
                }));
                if (_pressed != null && !locked) row.RegisterCallback<PointerDownEvent>(e => _pressed(e, card));
                var art = Kit.Box("fc-base-row__art");
                if (CardArt.For(id) is { } render) art.style.backgroundImage = Background.FromTexture2D(render);
                else art.Add(Kit.Icon(CardIcons.For(id), "fc-base-row__icon"));
                row.Add(art);
                var text = Kit.Box("fc-base-row__text");
                text.Add(Kit.Text(Strings.Short(id), "fc-base-row__name"));
                var count = inUse?.Invoke(id) ?? 0;
                text.Add(Kit.Text(locked ? VehicleCardData.UnlockText(id) : count > 0 ? Strings.Format("camp.inUse", count) : Strings.Get("camp.notInUse"),
                    "fc-small fc-base-row__line"));
                row.Add(text);
                row.EnableInClassList("fc-base-row--locked", locked);
                row.EnableInClassList("fc-base-row--armed", card == carried);
                row.EnableInClassList("fc-base-row--nofit", fits != null && !fits(card));
                row.tooltip = Strings.Card(id);
                _list.Add(row);
            }
            _list.Add(Kit.Box("fc-base-tray__end"));
        }
    }
}
