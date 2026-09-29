using System;
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Army tab's Base view (prompt 14, rebuilt on the Field Command 2.0 kit):
    /// <list type="bullet">
    /// <item><description>along the top, the HQ's level and what the next one opens, the map picker (its picture,
    /// and a mark on maps set up on their own or where the plan does not fit exactly), the three saved plans, and
    /// Auto-arrange; every change saves at once and a small "Saved" shows;</description></item>
    /// <item><description>down the left, the tower tray by size (<see cref="TowerTray"/>);</description></item>
    /// <item><description>in the middle the camp from above (<see cref="CampMap"/>): the map's picture, the enemy's
    /// ways in, every slot at its real place sized by class, utility slots as hexagons, the range cover on
    /// request, zoom and pan with two fingers;</description></item>
    /// <item><description>on the right the picked slot or tower: its render, name, size and rank, its numbers
    /// against the towers of its size, its range, its branch and gear, Replace, Remove and its detail page; with
    /// nothing picked, how to lay a base out and how it stands;</description></item>
    /// <item><description>along the bottom the base's cover (like the deck's), its strength (the number the Defend
    /// and Endless waves scale with, <see cref="BaseStrength"/>) and the slots in words.</description></item>
    /// </list>
    /// The base is a plan by place for every map (<see cref="BasePlan"/>, prompt 14 G); a map can be set up on its
    /// own. Towers are dragged onto a slot or tapped and then placed with a tap; only the slots they fit light up.
    /// The outpost has its own view (<see cref="OutpostScreen"/>).
    /// </summary>
    internal sealed class BaseScreen
    {
        private enum PanelTab
        {
            Branch,
            Gear,
        }

        /// <summary>A tower's equipment slots.</summary>
        internal static readonly string[] GearSlots = { "weapon", "structure", "systems" };

        private static readonly GearSlot[] TowerSlots = { GearSlot.TowerWeapon, GearSlot.TowerStructure, GearSlot.TowerSystems };

        /// <summary>How far (panel pixels) a press travels before it turns into a drag.</summary>
        private const float DragStart = 12f;

        /// <summary>The largest a small slot's face may be, in metres of the map (medium 1.4 times, large twice: prompt 14 B3).</summary>
        internal const float SmallFaceMetres = 12f;

        /// <summary>The HQ mark's size to a small slot's.</summary>
        internal const float HqRatio = 1.6f;

        /// <summary>The face sizes' ratio to a small slot's: medium, large, a utility hexagon.</summary>
        internal const float MediumRatio = 1.4f, LargeRatio = 2f, UtilityRatio = 1.4f;

        /// <summary>A slot of the camp on the map.</summary>
        internal sealed class SlotView
        {
            public VisualElement Element;
            public SlotFace Face;
            public int Hardpoint;
            public PlaceKey Key;
            public SlotSize Size;
            public bool Utility;
            public bool Open;
            public UnityEngine.Vector2 Picture;

            /// <summary>The loadout place this slot reads (for the fit rules).</summary>
            public LoadoutSlot Slot => Utility ? LoadoutSlot.Utility(0, Size) : LoadoutSlot.Tower(Size, 0);
        }

        private readonly Catalog _catalog;
        private readonly Action<string, bool> _note;
        private readonly Action _changed;
        private readonly List<SlotView> _slots = new();
        private readonly TowerTray _tray;
        private readonly CampMap _map;
        private readonly VisualElement _panelBody, _strip, _hq, _saved, _mapBox, _legend, _dropHost;
        private readonly Label _hqTitle, _hqNext;
        private readonly List<(KitChip chip, int plan)> _planChips = new();
        private readonly KitChip _customChip, _rangeChip;
        private VisualElement _hqMark;
        private KitDropdown _mapDrop;
        private readonly VisualElement _ghost;
        private readonly IconElement _ghostIcon;
        private IVisualElementScheduledItem _savedHide;

        private string _mapId;
        private BaseSiteDef _site;
        private float _faceMetres = SmallFaceMetres;
        private CampFrame _frame;
        private string _selected, _armed;
        private int _picked = -1;
        private PanelTab _tab = PanelTab.Branch;
        private int _gearOpen = -1;
        private bool _ranges;

        // A press on a tray card or a filled slot that may become a drag.
        private int _pressPointer = -1;
        private UnityEngine.Vector2 _pressStart;
        private string _pressId;
        private int _pressFrom = -1;
        private bool _pressFromTray, _dragging;
        private SlotView _hover;

        public BaseScreen(Catalog catalog, Action<string, bool> note, Action changed)
        {
            _catalog = catalog;
            _note = note ?? ((_, _) => { });
            _changed = changed ?? (() => { });
            Root = Kit.Box("fc-base", PickingMode.Position);

            // Top: the HQ's level, the map, the three plans, Auto-arrange, "Saved".
            var bar = Kit.Box("fc-base__bar");
            _hq = Kit.Box("fc-base__hq");
            _hq.Add(Kit.Icon(TowerIcons.For("headquarters") ?? "hq", "fc-base__hq-icon"));
            var hqText = Kit.Box("fc-base__hq-text");
            _hqTitle = Kit.Text("", "fc-panel-title fc-row-text");
            hqText.Add(_hqTitle);
            _hqNext = Kit.Text("", "fc-small fc-row-text");
            hqText.Add(_hqNext);
            _hq.Add(hqText);
            bar.Add(_hq);
            _dropHost = Kit.Box("fc-base__map-pick");
            bar.Add(_dropHost);
            var plans = Kit.Box("fc-base__plans");
            for (var i = 0; i < PlayerProfile.BasePlanCount; i++)
            {
                var index = i;
                var chip = new KitChip(Strings.Format("camp.plan", i + 1), false, () => ChoosePlan(index));
                plans.Add(chip);
                _planChips.Add((chip, i));
            }
            bar.Add(plans);
            bar.Add(new KitButton(ButtonTier.Secondary, Strings.Get("camp.auto"), AutoArrange, "bolt"));
            _saved = Kit.Box("fc-base__saved");
            _saved.Add(Kit.Icon("check", "fc-base__saved-icon"));
            _saved.Add(Kit.Text(Strings.Get("camp.saved"), "fc-small"));
            bar.Add(_saved);
            Root.Add(bar);

            var body = Kit.Box("fc-base__body");
            _tray = new TowerTray(catalog, new[] { TowerTray.Tab.Small, TowerTray.Tab.Medium, TowerTray.Tab.Large, TowerTray.Tab.Utility }, TapTower,
                (e, id) => Press(e, id, -1, true));
            _tray.Changed += Refresh;
            _tray.Root.AddToClassList("fc-base__tray");
            body.Add(_tray.Root);

            _mapBox = Kit.Box("fc-base__centre");
            _map = new CampMap();
            _map.Moved += PlaceSlots;
            _mapBox.Add(_map);
            var tools = Kit.Box("fc-base__map-tools");
            // Short words on the map's corner (the camp is under them on a narrow screen); the full ones as tooltips.
            _customChip = new KitChip(Strings.Get("camp.customShort"), false, ToggleCustom, "settings") { tooltip = Strings.Get("camp.custom") };
            tools.Add(_customChip);
            _rangeChip = new KitChip(Strings.Get("camp.rangesShort"), false, ToggleRanges, "crosshair") { tooltip = Strings.Get("camp.ranges") };
            tools.Add(_rangeChip);
            _mapBox.Add(tools);
            _legend = Kit.Box(KitPanel.SurfaceClass + " fc-base__legend");
            var ground = Kit.Box("fc-row");
            ground.Add(Kit.Box("fc-base__swatch fc-base__swatch--ground"));
            ground.Add(Kit.Text(Strings.Get("camp.rangeGround"), "fc-small"));
            _legend.Add(ground);
            var air = Kit.Box("fc-row");
            air.Add(Kit.Box("fc-base__swatch fc-base__swatch--air"));
            air.Add(Kit.Text(Strings.Get("camp.rangeAir"), "fc-small"));
            _legend.Add(air);
            _mapBox.Add(_legend);
            body.Add(_mapBox);

            var panel = Kit.Box(KitPanel.SurfaceClass + " fc-base__panel", PickingMode.Position);
            var panelScroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-base__panel-scroll");
            _panelBody = panelScroll.contentContainer;
            panel.Add(panelScroll);
            body.Add(panel);
            Root.Add(body);

            _strip = Kit.Box(KitPanel.SurfaceClass + " fc-base__strip");
            Root.Add(_strip);

            // What follows the finger while a tower is dragged.
            _ghost = Kit.Box(KitPanel.SurfaceClass + " fc-base__ghost");
            _ghostIcon = Kit.Icon("tower", "fc-base__ghost-icon");
            _ghost.Add(_ghostIcon);
            _ghost.style.display = DisplayStyle.None;
            Root.Add(_ghost);

            Root.RegisterCallback<PointerMoveEvent>(OnPointerMove, TrickleDown.TrickleDown);
            Root.RegisterCallback<PointerUpEvent>(OnPointerUp, TrickleDown.TrickleDown);
            Root.RegisterCallback<PointerCancelEvent>(_ => EndDrag(), TrickleDown.TrickleDown);
            Root.RegisterCallback<PointerCaptureOutEvent>(e =>
            {
                if (_dragging && e.target == Root) EndDrag();
            });
            ShowMap(MapFlag() ?? MatchSettings.CurrentMap.Id);
        }

        public VisualElement Root { get; }

        /// <summary>A structure's detail page asked for: set by the menu.</summary>
        internal Action<string> OpenDetail { get; set; }

        internal string MapId => _mapId;
        internal IReadOnlyList<SlotView> CampSlots => _slots;
        internal CampMap Map => _map;
        internal bool RangesShown => _ranges;

        /// <summary>The base on the map in view as the battle will have it (the plan laid on the camp, or the map's own).</summary>
        internal BaseLoadout Layout => _site != null ? Plan.Resolve(_mapId, _site, Level) : new BaseLoadout { HqLevel = Level };

        /// <summary>The base strength shown (prompt 14 E2): <see cref="BaseStrength.Score(Catalog, BaseLoadout, Func{VehicleDef, VehicleBoost})"/>.</summary>
        internal float Strength => BaseStrength.Score(_catalog, PlayerProfile.BaseLoadoutFor(_mapId), PlayerProfile.BoostFor);

        private static BasePlan Plan => PlayerProfile.ActivePlan;

        private static int Level => Mathf.Clamp(Campaign.HqLevelCap, 1, Campaign.MaxHqLevel);

        private static string MapFlag()
        {
            var id = DebugFlags.Value("-mb-base-map=");
            return string.IsNullOrEmpty(id) ? null : id;
        }

        /// <summary>Debug flags for device checks: -mb-base-gear opens the Gear tab, -mb-base-pick=&lt;tower&gt; arms a tower, -mb-base-ranges shows the cover.</summary>
        public void DebugOpen()
        {
            if (DebugFlags.Has("-mb-base-gear")) _tab = PanelTab.Gear;
            if (DebugFlags.Has("-mb-base-ranges")) _ranges = true;
            var pick = DebugFlags.Value("-mb-base-pick=");
            if (!string.IsNullOrEmpty(pick) && _catalog.Vehicles.ContainsKey(pick))
            {
                _selected = pick;
                _armed = pick;
            }
            Refresh();
        }

        // ------------------------------------------------------------------ the map's camp

        /// <summary>Shows a map's camp: the picture, the HQ and every slot at its place.</summary>
        public void ShowMap(string id)
        {
            var site = BaseSites.CampOf(id);
            if (site == null)
            {
                id = MatchSettings.AllMaps[0].Id;
                site = BaseSites.CampOf(id);
            }
            // (A long battlefield's layered base is a base of its own: "ashfield_long", prompt 17 B.5.)
            _mapId = BaseSites.PlanKey(id);
            _site = site;
            _picked = -1;
            _map.Slots.Clear();
            _slots.Clear();
            if (_site == null)
            {
                _map.Frame = null;
                Refresh();
                return;
            }
            _frame = CampFrame.For(_mapId, _site);
            _faceMetres = FaceMetres(_site);
            var keys = SlotPlaces.Keys(_site);
            var camp = BaseLayout.Camp(_site, _catalog.Base, Level);
            // The HQ.
            _hqMark = Kit.Box("fc-base-hq");
            _hqMark.Add(Kit.Icon(TowerIcons.For("headquarters") ?? "hq", "fc-base-hq__icon"));
            _map.Slots.Add(_hqMark);
            // Larger slots first, so a small one's target is on top where two targets meet.
            var order = Enumerable.Range(0, _site.Slots.Count).OrderByDescending(i => _site.Slots[i].Kind == HardpointKind.Utility ? 1 : (int)_site.Slots[i].Class).ToList();
            foreach (var i in order)
            {
                var def = _site.Slots[i];
                var utility = def.Kind == HardpointKind.Utility;
                var view = new SlotView
                {
                    Hardpoint = i, Key = keys[i], Size = def.Class, Utility = utility, Open = camp[i].Open,
                    Picture = _frame.ToPicture(def.Position),
                };
                var hardpoint = i;
                view.Element = Kit.Tappable("fc-base-slot fc-base-slot--" + (utility ? "utility" : def.Class.ToString().ToLowerInvariant()), () => TapSlot(view));
                view.Face = new SlotFace(utility);
                view.Element.Add(view.Face);
                view.Element.RegisterCallback<PointerDownEvent>(e =>
                {
                    if (!view.Open) return;
                    if (Plan.At(_mapId, _site, hardpoint) is { } tower) Press(e, tower, hardpoint, false);
                });
                _map.Slots.Add(view.Element);
                _slots.Add(view);
            }
            _map.Frame = _frame;
            _map.Focus(CampRect());
            Refresh();
        }

        /// <summary>The camp in picture space: the HQ and every slot, with a margin for the faces and the arrows' heads.</summary>
        private Rect CampRect()
        {
            var min = _frame.ToPicture(_site.Hq);
            var max = min;
            foreach (var s in _site.Slots)
            {
                var p = _frame.ToPicture(s.Position);
                min = UnityEngine.Vector2.Min(min, p);
                max = UnityEngine.Vector2.Max(max, p);
            }
            foreach (var (at, _) in _frame.Arrows)
            {
                min = UnityEngine.Vector2.Min(min, at);
                max = UnityEngine.Vector2.Max(max, at);
            }
            var margin = new UnityEngine.Vector2(12f / Mathf.Max(1f, _frame.Width), 12f / Mathf.Max(1f, _frame.Height));
            min -= margin;
            max += margin;
            return Rect.MinMaxRect(Mathf.Max(0f, min.x), Mathf.Max(0f, min.y), Mathf.Min(1f, max.x), Mathf.Min(1f, max.y));
        }

        /// <summary>
        /// A small slot's face in metres of this camp: as large as it can be with no two faces (the HQ's too) touching,
        /// each by its class's ratio, and a tenth kept between them; at most <see cref="SmallFaceMetres"/>.
        /// </summary>
        internal static float FaceMetres(BaseSiteDef site)
        {
            var points = new List<(System.Numerics.Vector2 at, float ratio)> { (site.Hq, HqRatio) };
            foreach (var s in site.Slots)
                points.Add((s.Position, s.Kind == HardpointKind.Utility ? UtilityRatio : s.Class switch { SlotSize.Small => 1f, SlotSize.Medium => MediumRatio, _ => LargeRatio }));
            var best = SmallFaceMetres;
            for (var i = 0; i < points.Count; i++)
                for (var j = i + 1; j < points.Count; j++)
                    best = Mathf.Min(best, 0.9f * 2f * System.Numerics.Vector2.Distance(points[i].at, points[j].at) / (points[i].ratio + points[j].ratio));
            return best;
        }

        /// <summary>The ratio of a slot's face to a small one's (prompt 14 B3: medium 1.4, large 2; a utility hexagon 1.4).</summary>
        internal static float RatioOf(SlotView view) => view.Utility ? UtilityRatio : view.Size switch { SlotSize.Small => 1f, SlotSize.Medium => MediumRatio, _ => LargeRatio };

        /// <summary>The face of a slot at the map's zoom, in panel pixels.</summary>
        internal float FaceSize(SlotView view) => _faceMetres * _map.PixelsPerMetre * RatioOf(view);

        /// <summary>Puts every slot at its place on the map at the current zoom: its target the touch size, its face by class.</summary>
        private void PlaceSlots()
        {
            if (_site == null || _frame == null) return;
            var target = Kit.TouchTarget + 1f;
            foreach (var view in _slots)
            {
                var face = FaceSize(view);
                var size = Mathf.Max(target, face);
                view.Element.style.width = size;
                view.Element.style.height = size;
                view.Face.style.width = face;
                view.Face.style.height = face;
                _map.Place(view.Element, view.Picture, size);
            }
            if (_hqMark != null)
            {
                var hq = _faceMetres * _map.PixelsPerMetre * HqRatio;
                _hqMark.style.width = hq;
                _hqMark.style.height = hq;
                _map.Place(_hqMark, _frame.ToPicture(_site.Hq), hq);
            }
        }

        // ------------------------------------------------------------------ taps

        /// <summary>A tray card tapped: into the slot picked first when it fits, else armed for a tap on a slot (tap again to put it down).</summary>
        internal void TapTower(string id)
        {
            if (!PlayerProfile.IsUnlocked(id))
            {
                _note(VehicleCardData.UnlockText(id), true);
                return;
            }
            if (_picked >= 0 && ViewOf(_picked) is { Open: true } view)
            {
                Drop(id, -1, view);
                return;
            }
            _selected = id;
            _armed = _armed == id ? null : id;
            Refresh();
        }

        /// <summary>A slot tapped: the armed tower goes in; otherwise the slot is picked (the panel shows it; tap a card to put one in).</summary>
        internal void TapSlot(SlotView view)
        {
            if (!view.Open)
            {
                _note(Strings.Format("camp.closed", OpensAt(view)), true);
                return;
            }
            if (_armed != null)
            {
                Drop(_armed, -1, view);
                return;
            }
            if (_picked == view.Hardpoint) _picked = -1;
            else
            {
                _picked = view.Hardpoint;
                _selected = Plan.At(_mapId, _site, view.Hardpoint);
                _tray.Shown = view.Utility ? TowerTray.Tab.Utility : (TowerTray.Tab)(int)view.Size;
            }
            Refresh();
        }

        /// <summary>A slot tapped by its hardpoint (tests).</summary>
        internal void TapSlot(int hardpoint)
        {
            if (ViewOf(hardpoint) is { } view) TapSlot(view);
        }

        private SlotView ViewOf(int hardpoint) => _slots.FirstOrDefault(v => v.Hardpoint == hardpoint);

        private bool Fits(string id, SlotView view) => BaseLayout.Fits(_catalog, id, view.Slot);

        /// <summary>A tower dropped (or tapped) into a slot: from the tray it replaces what was there; from another slot it moves (a swap when both fit).</summary>
        private bool Drop(string id, int from, SlotView target)
        {
            if (!target.Open) return false;
            if (!Fits(id, target))
            {
                _note(Strings.Format("camp.tooBig", ("card", Strings.Card(id)), ("size", (target.Utility ? Strings.Get("camp.utility") : SizeName(target.Size)).ToLowerInvariant())), true);
                Refresh();
                return false;
            }
            if (from >= 0 && from != target.Hardpoint)
            {
                var displaced = Plan.At(_mapId, _site, target.Hardpoint);
                Plan.Set(_mapId, _site, target.Hardpoint, id);
                var source = ViewOf(from);
                Plan.Set(_mapId, _site, from, displaced != null && source != null && Fits(displaced, source) ? displaced : null);
            }
            else Plan.Set(_mapId, _site, target.Hardpoint, id);
            _armed = null;
            _picked = target.Hardpoint;
            _selected = id;
            Saved(Strings.Format("camp.placed", Strings.Card(id)));
            return true;
        }

        private void TakeOut(int hardpoint)
        {
            var tower = Plan.At(_mapId, _site, hardpoint);
            if (tower == null) return;
            Plan.Set(_mapId, _site, hardpoint, null);
            _picked = -1;
            Saved(Strings.Format("camp.removed", Strings.Card(tower)));
        }

        /// <summary>A change saved at once (prompt 14 F3): the profile is written, "Saved" shows a moment, the note says what changed.</summary>
        private void Saved(string note)
        {
            PlayerProfile.SaveBasePlans();
            if (note != null) _note(note, false);
            _saved.AddToClassList("fc-base__saved--on");
            _savedHide?.Pause();
            if (_saved.panel != null) _savedHide = _saved.schedule.Execute(() => _saved.RemoveFromClassList("fc-base__saved--on")).StartingIn(1600);
            _changed();
            Refresh();
        }

        private void ChoosePlan(int index)
        {
            if (PlayerProfile.ActiveBasePlan == index) return;
            PlayerProfile.ActiveBasePlan = index;
            _picked = -1;
            _armed = null;
            _note(Strings.Format("camp.planChosen", index + 1), false);
            _changed();
            Refresh();
        }

        private void ToggleCustom()
        {
            if (_site == null) return;
            var own = !Plan.Custom.ContainsKey(_mapId);
            Plan.SetCustom(_mapId, _site, own, Level);
            Saved(Strings.Get(own ? "camp.customOn" : "camp.customOff"));
        }

        /// <summary>Picks the first filled large slot, else any filled one (the screenshot of the panel and the range rings).</summary>
        internal void DebugPickFilled()
        {
            var filled = _slots.Where(v => v.Open && !v.Utility && Plan.At(_mapId, _site, v.Hardpoint) != null).OrderByDescending(v => v.Size).FirstOrDefault();
            if (filled != null) TapSlot(filled);
        }

        internal void ToggleRanges()
        {
            _ranges = !_ranges;
            Refresh();
        }

        /// <summary>
        /// Auto-arrange (prompt 14 G5): the enemy AI's own way of choosing a base, among the towers the player has, laid
        /// on this camp; the utility modules stay. Into the map's own set-up when it has one, else the plan.
        /// </summary>
        internal void AutoArrange()
        {
            if (_site == null) return;
            var seed = 17;
            foreach (var c in _mapId) seed = seed * 31 + c;
            var ai = BaseLoadout.ForAi(_catalog, "Normal", "default", seed, Level, PlayerProfile.IsUnlocked, layered: _site.Layered);
            var towers = BasePlan.ToAssignment(_site, ai);
            for (var i = 0; i < towers.Length; i++)
                if (_site.Slots[i].Kind == HardpointKind.Utility) towers[i] = Plan.At(_mapId, _site, i);
            if (Plan.Custom.ContainsKey(_mapId)) Plan.Custom[_mapId] = BasePlan.FromAssignment(_site, towers, Level);
            else Plan.FromCamp(_site, towers);
            _picked = -1;
            _armed = null;
            Saved(Strings.Get("camp.autoDone"));
        }

        /// <summary>The HQ level that opens a slot.</summary>
        private int OpensAt(SlotView view)
        {
            var rules = _catalog.Base;
            var index = 0;
            foreach (var slot in BaseLayout.Camp(_site, rules, rules.MaxLevel))
                if (slot.Hardpoint == view.Hardpoint) index = slot.Slot.Index;
            var layered = _site.Layered;
            for (var l = 1; l <= rules.MaxLevel; l++)
                if ((view.Utility ? rules.UtilitySlots(l, layered) : rules.Slots(l, view.Size, layered)) > index) return l;
            return rules.MaxLevel + 1;
        }

        internal static string SizeIcon(SlotSize size) => size switch
        {
            SlotSize.Small => "slot_small",
            SlotSize.Medium => "slot_medium",
            _ => "slot_large",
        };

        private static string SizeName(SlotSize size) => Strings.Get("camp.size." + size.ToString().ToLowerInvariant());

        /// <summary>The view is left (another view, tab or page): a drag or a pick is let go (changes are already saved).</summary>
        public void Leave()
        {
            EndDrag();
            _armed = null;
            _picked = -1;
        }

        /// <summary>The Android back button: drops a drag, an armed card or a pick; false when there was nothing to drop.</summary>
        public bool Back()
        {
            if (_dragging || _armed != null || _picked >= 0)
            {
                EndDrag();
                _armed = null;
                _picked = -1;
                Refresh();
                return true;
            }
            return false;
        }

        /// <summary>Picks a tower or module for the panel (its Gear tab when <paramref name="gear"/>), from its detail page.</summary>
        internal void Pick(string id, bool gear = false)
        {
            if (!_catalog.Vehicles.TryGetValue(id, out var def) || def.Fort == null) return;
            _selected = id;
            _armed = null;
            _picked = -1;
            _tray.Shown = def.Fort.Kind == FortKind.Utility ? TowerTray.Tab.Utility : (TowerTray.Tab)(int)def.Fort.Size;
            if (gear) _tab = PanelTab.Gear;
            Refresh();
        }

        // ------------------------------------------------------------------ drag and drop

        private void Press(PointerDownEvent e, string id, int from, bool fromTray)
        {
            if (e.pointerType == UnityEngine.UIElements.PointerType.mouse && e.button != 0) return;
            if (_dragging) return;
            _pressPointer = e.pointerId;
            _pressStart = e.position;
            _pressId = id;
            _pressFrom = from;
            _pressFromTray = fromTray;
            // A press on a filled slot moves its tower, not the map.
            _map.DragsGround = fromTray;
        }

        private void OnPointerMove(PointerMoveEvent e)
        {
            if (_pressPointer != e.pointerId || _pressId == null) return;
            var at = (UnityEngine.Vector2)e.position;
            if (!_dragging)
            {
                var delta = at - _pressStart;
                if (delta.sqrMagnitude < DragStart * DragStart) return;
                // In the tray a mostly vertical pull is a scroll; sideways (towards the map) it is a drag.
                if (_pressFromTray && Mathf.Abs(delta.x) < Mathf.Abs(delta.y))
                {
                    _pressPointer = -1;
                    _pressId = null;
                    _map.DragsGround = true;
                    return;
                }
                BeginDrag();
            }
            MoveGhost(at);
            var over = SlotUnder(at);
            var target = over != null && over.Open && Fits(_pressId, over) ? over : null;
            if (target != _hover)
            {
                _hover?.Element.RemoveFromClassList("fc-base-slot--hover");
                _hover = target;
                _hover?.Element.AddToClassList("fc-base-slot--hover");
            }
            e.StopPropagation();
        }

        private void BeginDrag()
        {
            _dragging = true;
            _armed = null;
            _selected = _pressId;
            _ghostIcon.Name = CardIcons.For(_pressId);
            if (CardArt.For(_pressId) is { } render) _ghost.style.backgroundImage = Background.FromTexture2D(render);
            _ghost.style.display = DisplayStyle.Flex;
            _ghost.BringToFront();
            if (Root.panel != null) Root.CapturePointer(_pressPointer);
            Refresh();
        }

        private void OnPointerUp(PointerUpEvent e)
        {
            _map.DragsGround = true;
            if (_pressPointer != e.pointerId) return;
            if (!_dragging)
            {
                _pressPointer = -1;
                _pressId = null;
                return;
            }
            var at = (UnityEngine.Vector2)e.position;
            var id = _pressId;
            var from = _pressFrom;
            var over = SlotUnder(at);
            EndDrag();
            if (over != null && over.Hardpoint != from)
            {
                if (!over.Open) _note(Strings.Format("camp.closed", OpensAt(over)), true);
                else Drop(id, from, over);
            }
            else if (from >= 0 && over == null && _tray.Root.worldBound.Contains(at)) TakeOut(from);
            Refresh();
            e.StopPropagation();
        }

        private void EndDrag()
        {
            var was = _dragging;
            var pointer = _pressPointer;
            _dragging = false;
            _pressPointer = -1;
            if (was && Root.panel != null && Root.HasPointerCapture(pointer)) Root.ReleasePointer(pointer);
            _pressId = null;
            _hover?.Element.RemoveFromClassList("fc-base-slot--hover");
            _hover = null;
            if (_ghost != null) _ghost.style.display = DisplayStyle.None;
            if (was) Refresh();
        }

        private void MoveGhost(UnityEngine.Vector2 at)
        {
            var origin = Root.worldBound.position;
            var size = _ghost.resolvedStyle.width;
            if (float.IsNaN(size)) size = 0f;
            _ghost.style.left = at.x - origin.x - size * 0.5f;
            _ghost.style.top = at.y - origin.y - size * 0.5f;
        }

        private SlotView SlotUnder(UnityEngine.Vector2 at)
        {
            // The nearest face under the finger (targets of neighbouring slots may overlap).
            SlotView best = null;
            var bestDistance = float.MaxValue;
            foreach (var view in _slots)
            {
                var b = view.Element.worldBound;
                if (!b.Contains(at)) continue;
                var d = (b.center - at).sqrMagnitude;
                if (d < bestDistance)
                {
                    bestDistance = d;
                    best = view;
                }
            }
            return best;
        }

        // ------------------------------------------------------------------ refresh

        /// <summary>Brings every part up to date with the plan and the profile (ranks, branches, the level).</summary>
        public void Refresh()
        {
            var carrying = _dragging ? _pressId : _armed;
            var layout = Layout;
            RefreshBar(layout);
            RefreshSlots(carrying);
            var picked = _picked >= 0 ? ViewOf(_picked) : null;
            _tray.Refresh(carrying, id => PlacedCount(layout, id), picked != null ? id => Fits(id, picked) : null);
            RefreshMap(layout);
            RefreshPanel(layout);
            RefreshStrip(layout);
        }

        private void RefreshBar(BaseLoadout layout)
        {
            var rules = _catalog.Base;
            var level = layout.HqLevel;
            _hqTitle.text = Kit.Caps(Strings.Format("camp.hqBadge", level));
            if (level >= rules.MaxLevel) _hqNext.text = Strings.Get("camp.hqTop");
            else
            {
                var more = new List<string>();
                var layered = _site != null && _site.Layered;
                foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                {
                    var n = rules.Slots(level + 1, size, layered) - rules.Slots(level, size, layered);
                    if (n > 0) more.Add(Strings.Format("camp.more." + size.ToString().ToLowerInvariant(), n));
                }
                var u = rules.UtilitySlots(level + 1, layered) - rules.UtilitySlots(level, layered);
                if (u > 0) more.Add(Strings.Format("camp.more.utility", u));
                _hqNext.text = Strings.Format("camp.hqNext", ("current", level), ("level", level + 1), ("more", more.Count > 0 ? string.Join(", ", more) : Strings.Get("camp.moreNothing")));
            }
            foreach (var (chip, plan) in _planChips) chip.Selected = plan == PlayerProfile.ActiveBasePlan;
            // The map picker: every map's picture, and a word on maps set up on their own or where the plan moved a tower.
            // Prompt 17 B.5: each map with a long battlefield is in it twice, its camp and then its layered base.
            var maps = new List<string>();
            foreach (var m in MatchSettings.AllMaps)
            {
                if (BaseSites.CampOf(m.Id) != null) maps.Add(m.Id);
                if (BaseSites.HasLong(m.Id)) maps.Add(m.Id + BaseSites.LongSuffix);
            }
            var options = new List<KitOption>();
            var selected = 0;
            for (var i = 0; i < maps.Count; i++)
            {
                var id = maps[i];
                if (id == _mapId) selected = i;
                var key = BaseSites.MapKey(id);
                var name = BaseSites.IsLong(id) ? Strings.Format("camp.longMap", Strings.Get("map." + key)) : Strings.Get("map." + key);
                options.Add(new KitOption(name, MapNote(id), MapArt.For(key)));
            }
            _dropHost.Clear();
            // The pictures are in the list it opens; closed, it is the map's name only (the bar stays one row).
            _mapDrop = new KitDropdown(Strings.Get("camp.map"), options, selected, i => ShowMap(maps[i]), thumbnail: false);
            _dropHost.Add(_mapDrop);
            var mark = KitDot.Attach(_mapDrop, MapNote(_mapId) != null);
            mark.AddToClassList("fc-base__map-dot");
        }

        /// <summary>A map's mark on the picker: its own set-up, or a plan that does not fit it exactly (null: none).</summary>
        private string MapNote(string mapId)
        {
            if (Plan.Custom.ContainsKey(mapId)) return Strings.Get("camp.customMark");
            var site = BaseSites.CampOf(mapId);
            return site != null && Plan.Misfits(mapId, site) ? Strings.Get("camp.misfit") : null;
        }

        private void RefreshSlots(string carrying)
        {
            if (_site == null) return;
            var towers = _site != null ? (Plan.Custom.ContainsKey(_mapId) ? BasePlan.ToAssignment(_site, Plan.Custom[_mapId]) : Plan.Assign(_site, out _)) : null;
            foreach (var view in _slots)
            {
                var tower = towers?[view.Hardpoint];
                var e = view.Element;
                var face = view.Face;
                e.EnableInClassList("fc-base-slot--filled", tower != null);
                e.EnableInClassList("fc-base-slot--closed", !view.Open);
                var lit = carrying != null && view.Open && Fits(carrying, view);
                e.EnableInClassList("fc-base-slot--lit", lit);
                e.EnableInClassList("fc-base-slot--dim", carrying != null && !lit);
                e.EnableInClassList("fc-base-slot--picked", _picked == view.Hardpoint);
                // A closed slot keeps its tower for a higher level but does not show it: it does not fight.
                var render = tower != null && view.Open ? CardArt.For(tower) : null;
                face.Art.style.backgroundImage = render != null ? new StyleBackground(render) : new StyleBackground(StyleKeyword.None);
                face.Art.style.display = render != null ? DisplayStyle.Flex : DisplayStyle.None;
                // An empty slot says what it takes in words under its face (B5); a closed one is locked with the HQ level
                // it needs inside (F1).
                face.Word.text = view.Open && tower == null ? (view.Utility ? Strings.Get("camp.utility") : SizeName(view.Size)) : "";
                face.Word.style.display = face.Word.text.Length > 0 ? DisplayStyle.Flex : DisplayStyle.None;
                face.Lock.style.display = view.Open ? DisplayStyle.None : DisplayStyle.Flex;
                face.Need.text = view.Open ? "" : OpensAt(view).ToString();
                face.Need.style.display = view.Open ? DisplayStyle.None : DisplayStyle.Flex;
                face.Rank = tower != null && view.Open ? PlayerProfile.Rank(tower) : 0;
                face.Branch.style.display = tower != null && view.Open && PlayerProfile.TowerBranch(tower) != null ? DisplayStyle.Flex : DisplayStyle.None;
                e.tooltip = !view.Open ? Strings.Format("camp.closed", OpensAt(view)) : tower != null ? Strings.Card(tower) : view.Utility ? Strings.Get("camp.utility") : SizeName(view.Size);
            }
        }

        private void RefreshMap(BaseLoadout layout)
        {
            _customChip.Selected = _site != null && Plan.Custom.ContainsKey(_mapId);
            _rangeChip.Selected = _ranges;
            _legend.style.display = _ranges ? DisplayStyle.Flex : DisplayStyle.None;
            if (_site == null) return;
            var towers = BasePlan.ToAssignment(_site, layout);
            var camp = BaseLayout.Camp(_site, _catalog.Base, layout.HqLevel);
            if (_ranges)
            {
                var cover = new List<(UnityEngine.Vector2, float, float)>();
                for (var i = 0; i < towers.Length; i++)
                {
                    if (towers[i] == null || !camp[i].Open || !_catalog.Vehicles.TryGetValue(layout.DefFor(towers[i]), out var def)) continue;
                    var (ground, air, _) = BaseRoles.Reach(def);
                    cover.Add((_frame.ToPicture(_site.Slots[i].Position), ground, air));
                }
                _map.Cover = cover;
            }
            else _map.Cover = null;
            // The picked slot's tower: its reach and its shortest range as rings.
            _map.Rings = null;
            if (_picked >= 0 && towers[_picked] is { } picked && _catalog.Vehicles.TryGetValue(layout.DefFor(picked), out var pd))
            {
                var (ground, air, min) = BaseRoles.Reach(pd);
                _map.Rings = (_frame.ToPicture(_site.Slots[_picked].Position), Mathf.Max(ground, air), min);
            }
            _map.Repaint();
            PlaceSlots();
        }

        private static int PlacedCount(BaseLoadout layout, string id) =>
            BaseLayout.Placed(layout, id) + layout.Utilities.Count(u => u == id);

        // ------------------------------------------------------------------ the panel

        private void RefreshPanel(BaseLoadout layout)
        {
            _panelBody.Clear();
            var slot = _picked >= 0 ? ViewOf(_picked) : null;
            var id = slot != null ? BasePlan.ToAssignment(_site, layout)[slot.Hardpoint] : _selected;
            if (id == null || !_catalog.Vehicles.TryGetValue(id, out var def))
            {
                if (slot != null) EmptySlotPanel(slot);
                else IdlePanel(layout);
                return;
            }
            var module = def.Fort?.Kind == FortKind.Utility;
            var head = Kit.Box("fc-base__head");
            var art = Kit.Box("fc-base__head-art");
            if (CardArt.For(id) is { } render) art.style.backgroundImage = Background.FromTexture2D(render);
            else art.Add(Kit.Icon(CardIcons.For(id), "fc-base__head-icon"));
            head.Add(art);
            var text = Kit.Box("fc-base__head-text");
            text.Add(Kit.Text(Kit.Caps(Strings.Card(id)), "fc-panel-title fc-row-text"));
            var branch = PlayerProfile.TowerBranch(id);
            var sizeWord = module ? Strings.Get("camp.utility") : SizeName(def.Fort.Size);
            text.Add(Kit.Text(Strings.Format("camp.cardLine", ("size", sizeWord), ("rank", PlayerProfile.Rank(id))) + (branch != null ? " · " + Strings.Branch(branch) : ""),
                "fc-small fc-row-text"));
            head.Add(text);
            _panelBody.Add(head);

            // Its numbers against the towers of its size (D1), and its range.
            var shown = _catalog.Vehicles.TryGetValue(branch ?? id, out var fights) ? fights : def;
            var boost = PlayerProfile.BoostFor(shown);
            if (!module)
            {
                var best = BaseRoles.BestOfSize(_catalog, def.Fort.Size);
                var (ground, air, min) = BaseRoles.Reach(shown);
                var reach = Mathf.Max(ground, air);
                _panelBody.Add(Kit.Text(Kit.Caps(Strings.Format("camp.vsSize", sizeWord.ToLowerInvariant())), "fc-caption fc-base__caption"));
                StatRow("camp.statHp", shown.MaxHp * boost.Hp, best.hp, "N0");
                StatRow("camp.statDps", UnitStats.Dps(shown.Weapon) * boost.Damage * boost.FireRate, best.dps, "N0");
                StatRow("camp.statRange", reach, best.range, "0");
                var reachLine = ground > 0f && air > 0f ? Strings.Format("camp.reachBoth", ("metres", Mathf.RoundToInt(ground)), ("metres2", Mathf.RoundToInt(air)))
                    : air > 0f ? Strings.Format("camp.reachAir", Mathf.RoundToInt(air))
                    : ground > 0f ? Strings.Format("camp.reachGround", Mathf.RoundToInt(ground)) : Strings.Get("camp.reachNone");
                if (min > 0f) reachLine += " · " + Strings.Format("camp.minRange", Mathf.RoundToInt(min));
                _panelBody.Add(Kit.Text(reachLine, "fc-small fc-base__reach"));
            }
            else _panelBody.Add(Kit.Text(Strings.Get("guide." + id), "fc-small fc-base__reach"));

            // Branch and gear (D2).
            if (!module)
            {
                var tabs = new KitTabs(new[] { Strings.Get("camp.branch"), Strings.Get("camp.gear") }, (int)_tab, i =>
                {
                    _tab = (PanelTab)i;
                    Refresh();
                });
                tabs.AddToClassList("fc-base__tabs");
                _panelBody.Add(tabs);
                if (_tab == PanelTab.Branch) BranchPanel(id);
                else GearPanel(id);
            }
            // A module with rank-7 branches (the landing pad's, prompt 13 F.1) has no gear: its branches only.
            else if (TowerCards.Branches(_catalog, id).Count > 0) BranchPanel(id);

            // Replace, Remove, the detail page (D3).
            var buttons = Kit.Box("fc-base__buttons");
            if (slot != null)
            {
                buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("camp.replace"), () =>
                {
                    _armed = null;
                    _tray.Shown = slot.Utility ? TowerTray.Tab.Utility : (TowerTray.Tab)(int)slot.Size;
                    _note(Strings.Get("camp.replaceHint"), false);
                    Refresh();
                }, "restart"));
                buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("camp.removeButton"), () => TakeOut(slot.Hardpoint), "close"));
            }
            if (OpenDetail != null) buttons.Add(new KitButton(ButtonTier.Text, Strings.Get("army.info"), () => OpenDetail(id), "info"));
            _panelBody.Add(buttons);
        }

        private void StatRow(string key, float value, float best, string format)
        {
            var row = Kit.Box("fc-base__stat");
            var line = Kit.Box("fc-row fc-row--spread");
            line.Add(Kit.Text(Strings.Get(key), "fc-small fc-row-text"));
            line.Add(Kit.Text(value.ToString(format, Kit.Culture), "fc-number-small"));
            row.Add(line);
            var track = Kit.Box("fc-statbar");
            var fill = Kit.Box("fc-statbar__base");
            fill.style.width = Length.Percent(Mathf.Clamp01(value / Mathf.Max(1f, best)) * 100f);
            track.Add(fill);
            row.Add(track);
            _panelBody.Add(row);
        }

        private void EmptySlotPanel(SlotView slot)
        {
            var size = slot.Utility ? Strings.Get("camp.utility") : SizeName(slot.Size);
            _panelBody.Add(Kit.Text(Kit.Caps(Strings.Format("camp.emptySlot", size)), "fc-panel-title"));
            _panelBody.Add(Kit.Text(Strings.Get("camp.place." + slot.Key.Place.ToString().ToLowerInvariant()), "fc-small fc-mt-1"));
            _panelBody.Add(Kit.Text(slot.Utility ? Strings.Get("camp.takesModule") : Strings.Format("camp.takes", size.ToLowerInvariant()), "fc-body-2 fc-mt-2"));
        }

        /// <summary>Nothing picked (D4): how to lay a base out, and the base's overview (E).</summary>
        private void IdlePanel(BaseLoadout layout)
        {
            _panelBody.Add(Kit.Text(Kit.Caps(Strings.Get("camp.overview")), "fc-panel-title"));
            _panelBody.Add(Kit.Text(Strings.Get("camp.idleHint"), "fc-body-2 fc-mt-2"));
            var strength = Kit.Box("fc-base__strength-big");
            strength.Add(Kit.Caption(Strings.Get("camp.strength")));
            strength.Add(Kit.Text(Mathf.RoundToInt(Strength).ToString(), "fc-number"));
            strength.Add(Kit.Text(Strings.Get("camp.strengthNote"), "fc-small"));
            _panelBody.Add(strength);
            if (_site != null) _panelBody.Add(Kit.Text(CountsLine(layout), "fc-small fc-mt-2"));
        }

        private string CountsLine(BaseLoadout layout)
        {
            var c = BaseRoles.Counts(_site, _catalog.Base, layout);
            return Strings.Format("camp.counts", ("small", c[0].filled), ("smallSlots", c[0].open), ("medium", c[1].filled), ("mediumSlots", c[1].open), ("large", c[2].filled), ("largeSlots", c[2].open), ("utility", c[3].filled), ("utilitySlots", c[3].open));
        }

        private void BranchPanel(string id)
        {
            var branches = TowerCards.Branches(_catalog, id);
            if (branches.Count == 0)
            {
                _panelBody.Add(Kit.Text(Strings.Get("camp.branchNone"), "fc-small"));
                return;
            }
            var rank = PlayerProfile.Rank(id);
            var chosen = PlayerProfile.TowerBranch(id);
            var locked = rank < TowerCards.BranchRank;
            _panelBody.Add(Kit.Text(locked ? Strings.Format("camp.branchLocked", ("rank", TowerCards.BranchRank), ("rank2", rank))
                : chosen == null ? Strings.Get("camp.branchFree")
                : PlayerProfile.FreeBranchSwap(id) ? Strings.Get("camp.branchFreeSwap")
                : Strings.Format("camp.branchSwap", Kit.Count(PlayerProfile.BranchSwapCoins)), "fc-small fc-base__note"));
            // The tower-branch rework (D.1): both branches side by side, from their data.
            _panelBody.Add(BranchLines.Picker(_catalog, id, chosen, locked, b => ChooseBranch(id, b)));
        }

        private void ChooseBranch(string towerId, string branchId)
        {
            if (PlayerProfile.Rank(towerId) < TowerCards.BranchRank)
            {
                _note(Strings.Format("camp.branchNeedRank", TowerCards.BranchRank), true);
                return;
            }
            var chosen = PlayerProfile.TowerBranch(towerId);
            if (chosen == branchId) return;
            if (chosen == null || PlayerProfile.FreeBranchSwap(towerId))
            {
                ApplyBranch(towerId, branchId);
                return;
            }
            KitDialog.Confirm(Root, Strings.Get("camp.branch"),
                Strings.Format("camp.branchConfirm", ("card", Strings.Card(towerId)), ("branch", Strings.Branch(branchId)), ("coins", Kit.Count(PlayerProfile.BranchSwapCoins))),
                Strings.Get("camp.change"), () => ApplyBranch(towerId, branchId));
        }

        private void ApplyBranch(string towerId, string branchId)
        {
            if (!PlayerProfile.TryChooseBranch(towerId, branchId))
            {
                _note(Strings.Get("arsenal.needCoins"), true);
                return;
            }
            _note(Strings.Format("camp.branchChosen", ("card", Strings.Card(towerId)), ("branch", Strings.Branch(branchId))), false);
            _changed();
            Refresh();
        }

        private void GearPanel(string id)
        {
            var row = Kit.Box("fc-base__gear");
            var any = false;
            for (var i = 0; i < GearSlots.Length; i++)
            {
                var slot = i;
                var item = TowerGearIn(id, i);
                any |= item != null;
                var cell = Kit.Tappable("fc-base__gear-slot" + (i == _gearOpen ? " fc-base__gear-slot--open" : ""), () =>
                {
                    _gearOpen = _gearOpen == slot ? -1 : slot;
                    Refresh();
                });
                if (item != null) cell.Add(GearArt.Tile(item, GearTile));
                else
                {
                    var empty = Kit.Box("fc-base__gear-empty");
                    empty.Add(Kit.Icon(GearSlotIcon(i)));
                    cell.Add(empty);
                }
                cell.Add(Kit.Text(GearText.TowerSlotName(TowerSlots[i]), "fc-small fc-base__gear-name"));
                row.Add(cell);
            }
            _panelBody.Add(row);
            if (_gearOpen >= 0) GearChoices(id, TowerSlots[_gearOpen]);
            else _panelBody.Add(Kit.Text(any ? Strings.Format("camp.gearShared", Strings.Card(id)) : Strings.Get("camp.gearPick"), "fc-small"));
        }

        /// <summary>The pieces in the bag that fit one of a tower type's slots: a tap wears one, and the worn one can come off.</summary>
        private void GearChoices(string id, GearSlot slot)
        {
            var worn = PlayerProfile.TowerEquipped(id, slot);
            var pieces = PlayerProfile.TowerGearFor(id, slot);
            var grid = Kit.Box("fc-base__gear-choices");
            if (worn != null)
            {
                var off = Kit.Tappable("fc-base__gear-choice", () =>
                {
                    PlayerProfile.UnequipTower(id, slot);
                    _note(Strings.Format("camp.gearRemoved", ("slot", GearText.TowerSlotName(slot)), ("card", Strings.Card(id))), false);
                    Refresh();
                });
                off.Add(Kit.Text(Strings.Get("camp.gearOff"), "fc-small"));
                grid.Add(off);
            }
            foreach (var piece in pieces)
            {
                var item = piece;
                var choice = Kit.Tappable("fc-base__gear-choice" + (item == worn ? " fc-base__gear-choice--worn" : ""), () =>
                {
                    if (!PlayerProfile.EquipTower(id, item)) return;
                    _note(Strings.Format("camp.gearWorn", Strings.Card(id)), false);
                    Refresh();
                });
                choice.Add(GearArt.Tile(item, GearTile));
                grid.Add(choice);
            }
            _panelBody.Add(grid);
            if (pieces.Count == 0) _panelBody.Add(Kit.Text(Strings.Get("camp.gearNoPieces"), "fc-small"));
        }

        /// <summary>The gear tile's size (GearArt draws its tiles at a size given in pixels).</summary>
        private const float GearTile = 72f;

        private static string GearSlotIcon(int slot) => slot switch { 0 => "cannon", 1 => "shield", _ => "cbradar" };

        /// <summary>The piece a tower type wears in one of its three slots (0 Weapon, 1 Structure, 2 Systems), or null.</summary>
        internal static GearItem TowerGearIn(string towerId, int slot) => PlayerProfile.TowerEquipped(towerId, TowerSlots[slot]);

        /// <summary>The gear slot at a place in a tower type's three (weapon, structure, systems).</summary>
        internal static GearSlot TowerSlotOf(int slot) => TowerSlots[slot];

        // ------------------------------------------------------------------ the strip: cover, strength, slots

        /// <summary>
        /// The base's cover (E1: light vehicles, tanks, aircraft, rockets and missiles, stealth, repair and rearm; a
        /// missing one in the warning colour), its strength (E2: the number the Defend and Endless waves scale with)
        /// and the slots in words (E3: "Nhỏ 6/6 · Vừa 3/3 · Lớn 2/2 · Tiện ích 0/3").
        /// </summary>
        private void RefreshStrip(BaseLoadout layout)
        {
            _strip.Clear();
            var cover = Kit.Box("fc-base__cover");
            var tags = Kit.Box("fc-row fc-row--wrap");
            tags.Add(Kit.Text(Kit.Caps(Strings.Get("camp.cover")), "fc-caption fc-base__cover-title"));
            var roles = BaseRoles.Cover(_catalog, layout);
            foreach (var role in BaseRoles.All)
            {
                var has = roles.Contains(role);
                var tag = Kit.Box("fc-tag " + (has ? "fc-tag--ok" : "fc-tag--missing"));
                tag.Add(Kit.Icon(has ? RoleIcon(role) : "info"));
                tag.Add(Kit.Text(Strings.Get("camp.role." + role.ToString().ToLowerInvariant()), "fc-small" + (has ? "" : " fc-danger-text")));
                tags.Add(tag);
            }
            cover.Add(tags);
            // Prompt 15 E7: the five shields, lit where a tower pierces that armour well.
            var fitted = layout.Fitted(_catalog);
            var towers = fitted.Towers.Select(id => _catalog.Vehicles.TryGetValue(fitted.DefFor(id), out var d) ? d : null).Where(d => d != null).ToList();
            var shields = Kit.Box("fc-row fc-base__shields");
            shields.Add(Kit.Text(Kit.Caps(Strings.Get("combat.armourCover")), "fc-caption fc-base__cover-title"));
            shields.Add(KitCombat.CoverShields(level => KitCombat.Covers(towers, level), "cover.base"));
            cover.Add(shields);
            _strip.Add(cover);
            var numbers = Kit.Box("fc-base__numbers");
            var strength = Kit.Box("fc-row");
            strength.Add(Kit.Caption(Strings.Get("camp.strength")));
            StrengthLabel = Kit.Text(Mathf.RoundToInt(Strength).ToString(), "fc-number-small fc-base__strength");
            strength.Add(StrengthLabel);
            numbers.Add(strength);
            if (_site != null) numbers.Add(Kit.Text(CountsLine(layout), "fc-small"));
            _strip.Add(numbers);
        }

        /// <summary>The strength number on the strip (tests: it is <see cref="Strength"/>).</summary>
        internal Label StrengthLabel { get; private set; }

        private static string RoleIcon(CoverRole role) => role switch
        {
            CoverRole.AntiLight => "t_mg",
            CoverRole.AntiTank => "t_atgm",
            CoverRole.AntiAir => "t_aa",
            CoverRole.Intercept => "t_cram",
            CoverRole.Stealth => "eye",
            _ => "t_repair",
        };
    }
}
