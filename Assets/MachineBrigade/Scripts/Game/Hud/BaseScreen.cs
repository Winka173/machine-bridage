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
    /// The base loadout screen (the Army tab's Base view), in the Field Command style: along the
    /// top the HQ level (1-5, what it opens), the map and Save; the tower cards down the left;
    /// in the middle the map's camp from above, front up, with the HQ and every hardpoint as a
    /// frame sized by its class with its size icon (closed ones greyed, utility ones "soon"); on
    /// the right the picked tower card's branch choice and gear, and the outpost's two towers.
    /// Towers are dragged onto a slot (only the slots they fit light up) or tapped and then
    /// placed with a tap; a placed tower is dragged to another slot or back onto the list. The
    /// rules live in <see cref="BaseLayout"/>; Save writes the layout to the profile (leaving
    /// the view saves too).
    /// </summary>
    internal sealed class BaseScreen
    {
        private enum PanelTab
        {
            Branch,
            Gear,
        }

        /// <summary>A tower's equipment slots, as the tower gear will have them.</summary>
        internal static readonly string[] GearSlots = { "weapon", "structure", "systems" };

        /// <summary>How far (panel pixels) a press travels before it turns into a drag.</summary>
        private const float DragStart = 12f;

        /// <summary>A hardpoint frame on the diagram or in the outpost box.</summary>
        internal sealed class SlotView
        {
            public VisualElement Element;
            public IconElement Icon;
            public Label Caption;
            public LoadoutSlot Slot;
            public bool Open;
            public bool Utility;
            public int Hardpoint = -1;
            public Vector2 World;
            public float Facing;
        }

        private readonly Catalog _catalog;
        private readonly Action<string, bool> _note;
        private readonly Action _changed;
        private readonly Dictionary<string, MapDefinition> _maps = new();
        private readonly List<string> _towers, _modules;

        /// <summary>Whether the catalog has utility modules; without any the utility slots show as "soon".</summary>
        private readonly bool _hasModules;
        private readonly List<SlotView> _campViews = new(), _outpostViews = new();
        private readonly List<(VisualElement row, string id)> _rows = new();
        private readonly List<(VisualElement button, int level)> _levelButtons = new();
        private readonly List<(VisualElement button, PanelTab tab)> _tabButtons = new();
        private readonly Dictionary<SlotSize, Label> _legendCounts = new();

        private VisualElement _left, _canvasBox, _hq, _panelBody, _headArt, _takeOut, _ghost, _confirm, _save;
        private CampCanvas _canvas;
        private IconElement _headIcon, _headSize, _ghostIcon;
        private Label _mapName, _levelInfo, _hint, _hqLevel, _headName, _headLine, _headCount, _confirmText, _utilityCount, _saveTitle;

        private BaseLoadout _layout;
        private bool _dirty;
        private string _mapId;
        private BaseSiteDef _site;
        private string _selected, _armed;
        private LoadoutSlot? _picked;
        private PanelTab _tab = PanelTab.Branch;
        private Action _confirmed;

        // A press on a tower or a filled slot that may become a drag.
        private int _pressPointer = -1;
        private Vector2 _pressStart;
        private string _pressId;
        private LoadoutSlot? _pressFrom;
        private bool _pressHorizontal, _dragging;
        private SlotView _hover;

        public BaseScreen(Catalog catalog, Action<string, bool> note, Action changed)
        {
            _catalog = catalog;
            _note = note ?? ((_, _) => { });
            _changed = changed ?? (() => { });
            // Cheapest first, then by size: light towers at the top of the list.
            _towers = TowerCards.All(catalog).OrderBy(id => catalog.Vehicles[id].Fort.Size).ThenBy(id => id, StringComparer.Ordinal).ToList();
            _modules = catalog.Vehicles.Values.Where(d => d.Fort is { Kind: FortKind.Utility } && d.BranchOf == null).Select(d => d.Id)
                .OrderBy(id => id, StringComparer.Ordinal).ToList();
            _hasModules = _modules.Count > 0;
            _layout = PlayerProfile.BaseLoadout;
            _selected = _towers.FirstOrDefault();
            Root = UiKit.Box("base-view", PickingMode.Position);
            Build();
            Root.RegisterCallback<PointerMoveEvent>(OnPointerMove, TrickleDown.TrickleDown);
            Root.RegisterCallback<PointerUpEvent>(OnPointerUp, TrickleDown.TrickleDown);
            Root.RegisterCallback<PointerCancelEvent>(_ => EndDrag(), TrickleDown.TrickleDown);
            Root.RegisterCallback<PointerCaptureOutEvent>(e =>
            {
                // Only the view's own capture (a scroll view giving the pointer up bubbles here too).
                if (_dragging && e.target == Root) EndDrag();
            });
            var start = MatchSettings.CurrentMap.Id;
            ShowMap(MapFlag() ?? start);
        }

        public VisualElement Root { get; }

        /// <summary>Debug flags for device checks: -mb-base-gear opens the Gear tab, -mb-base-pick=&lt;tower&gt; arms a tower (its slots lit).</summary>
        public void DebugOpen()
        {
            if (DebugFlags.Has("-mb-base-gear")) _tab = PanelTab.Gear;
            var pick = DebugFlags.Value("-mb-base-pick=");
            if (!string.IsNullOrEmpty(pick) && (_towers.Contains(pick) || _modules.Contains(pick)))
            {
                _selected = pick;
                _armed = pick;
            }
            Refresh();
            // -mb-base-confirm: the question a branch change asks, for a look at it (below rank 7 the answer is refused).
            if (DebugFlags.Has("-mb-base-confirm") && _selected != null && TowerCards.Branches(_catalog, _selected) is { Count: > 1 } branches)
                AskBranch(_selected, branches[1]);
        }

        /// <summary>The layout being edited (not yet saved while <see cref="Dirty"/>).</summary>
        internal BaseLoadout Layout => _layout;

        internal bool Dirty => _dirty;
        internal string MapId => _mapId;
        internal IReadOnlyList<SlotView> CampSlots => _campViews;
        internal IReadOnlyList<SlotView> OutpostSlots => _outpostViews;

        private static string MapFlag()
        {
            var id = DebugFlags.Value("-mb-base-map=");
            return string.IsNullOrEmpty(id) ? null : id;
        }

        // ------------------------------------------------------------------ building

        private void Build()
        {
            // Top: HQ level, what it opens, the map, Save.
            var toolbar = UiKit.Box("base-toolbar");
            var levelBox = UiKit.Box("base-level-box");
            levelBox.Add(UiKit.Text(Strings.Get("camp.level"), "menu-caps base-level-caption"));
            var levels = UiKit.Box("base-levels");
            for (var l = 1; l <= _catalog.Base.MaxLevel; l++)
            {
                var level = l;
                var button = UiKit.Button("segment base-level", () => SetLevel(level));
                button.Add(UiKit.Text(level.ToString(), "base-level-text"));
                levels.Add(button);
                _levelButtons.Add((button, level));
            }
            levelBox.Add(levels);
            toolbar.Add(levelBox);
            _levelInfo = UiKit.Text("", "base-level-info");
            toolbar.Add(_levelInfo);
            var previous = UiKit.Button("icon-button base-map-arrow left", () => StepMap(-1));
            previous.Add(UiKit.Icon("arrow", UiKit.Ink, 2.2f));
            toolbar.Add(previous);
            var mapText = UiKit.Box("base-map-text");
            _mapName = UiKit.Text("", "base-map-name");
            mapText.Add(_mapName);
            toolbar.Add(mapText);
            var next = UiKit.Button("icon-button base-map-arrow right", () => StepMap(1));
            next.Add(UiKit.Icon("arrow", UiKit.Ink, 2.2f));
            toolbar.Add(next);
            _save = UiKit.WideButton("base-save", "check", Strings.Get("camp.save"), null, Save);
            _saveTitle = _save.Q<Label>(className: "wide-title");
            toolbar.Add(_save);
            Root.Add(toolbar);

            var body = UiKit.Box("base-body");

            // Left: the tower cards.
            _left = UiKit.Box("base-left");
            _left.Add(UiKit.Text(Strings.Get("camp.towers"), "menu-caps base-caps"));
            var scroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Hidden,
                touchScrollBehavior = ScrollView.TouchScrollBehavior.Clamped,
            };
            scroll.AddToClassList("base-list");
            MouseDragScroll.Attach(scroll);
            foreach (var id in _towers) scroll.Add(TowerRow(id));
            if (_hasModules)
            {
                scroll.Add(UiKit.Text(Strings.Get("camp.utility"), "menu-caps base-caps base-list-caps"));
                foreach (var id in _modules) scroll.Add(TowerRow(id));
            }
            _left.Add(scroll);
            body.Add(_left);

            // Middle: the camp.
            var centre = UiKit.Box("base-centre");
            var legend = UiKit.Box("base-legend");
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
            {
                var chip = UiKit.Box("base-legend-chip");
                chip.Add(UiKit.Icon(SizeIcon(size), UiKit.Ink, 1.8f));
                var count = UiKit.Text("", "base-legend-count");
                chip.Add(count);
                _legendCounts[size] = count;
                legend.Add(chip);
            }
            var utilityChip = UiKit.Box("base-legend-chip utility");
            utilityChip.Add(UiKit.Icon("module", UiKit.Ink, 1.8f));
            _utilityCount = UiKit.Text("", "base-legend-count");
            utilityChip.Add(_utilityCount);
            legend.Add(utilityChip);
            // Which way is up on the diagram: the camp's front, towards the enemy.
            var front = UiKit.Box("base-front");
            var arrow = UiKit.Icon("arrow", UiKit.Ink, 2f);
            arrow.AddToClassList("base-front-arrow");
            front.Add(arrow);
            front.Add(UiKit.Text(Strings.Get("camp.front"), "base-front-text"));
            legend.Add(front);
            _hint = UiKit.Text("", "base-hint");
            legend.Add(_hint);
            centre.Add(legend);
            _canvasBox = UiKit.Box("base-canvas-box");
            _canvas = new CampCanvas();
            _canvas.AddToClassList("base-canvas");
            _canvas.RegisterCallback<GeometryChangedEvent>(_ => Arrange());
            _canvasBox.Add(_canvas);
            centre.Add(_canvasBox);
            body.Add(centre);

            // Right: the picked tower card (branch, gear) and the outpost.
            var right = UiKit.Box("base-right");
            var head = UiKit.Box("base-head");
            _headArt = UiKit.Box("base-head-art");
            _headIcon = UiKit.Icon("tower", UiKit.Ink, 1.6f);
            _headIcon.AddToClassList("base-head-icon");
            _headArt.Add(_headIcon);
            var sizeBadge = UiKit.Box("base-size-badge");
            _headSize = UiKit.Icon("slot_small", UiKit.Ink, 2f);
            sizeBadge.Add(_headSize);
            _headArt.Add(sizeBadge);
            head.Add(_headArt);
            var headText = UiKit.Box("base-head-text");
            _headName = UiKit.Text("", "base-head-name");
            _headLine = UiKit.Text("", "base-head-line");
            _headCount = UiKit.Text("", "base-head-line base-head-count");
            headText.Add(_headName);
            headText.Add(_headLine);
            headText.Add(_headCount);
            head.Add(headText);
            right.Add(head);
            var tabs = UiKit.Box("base-tabs");
            foreach (var (tab, icon, key) in new[] { (PanelTab.Branch, "upgrade", "camp.branch"), (PanelTab.Gear, "gear", "camp.gear") })
            {
                var t = tab;
                var button = UiKit.Button(tab == PanelTab.Gear ? "segment base-tab last-segment" : "segment base-tab", () =>
                {
                    _tab = t;
                    Refresh();
                });
                button.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
                button.Add(UiKit.Text(Strings.Get(key), "segment-label"));
                tabs.Add(button);
                _tabButtons.Add((button, tab));
            }
            // Take a picked slot's tower out (shown only then).
            _takeOut = UiKit.Button("icon-button base-takeout", TakeOut);
            _takeOut.Add(UiKit.Icon("close", UiKit.Ink, 2f));
            _takeOut.tooltip = Strings.Get("camp.remove");
            tabs.Add(_takeOut);
            right.Add(tabs);
            var panelScroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Hidden,
                touchScrollBehavior = ScrollView.TouchScrollBehavior.Clamped,
            };
            panelScroll.AddToClassList("base-panel-scroll");
            MouseDragScroll.Attach(panelScroll);
            _panelBody = panelScroll.contentContainer;
            right.Add(panelScroll);
            // The outpost: its two slots, with its caption and what it is beside them.
            var outpost = UiKit.Box("base-outpost");
            var outpostSlots = UiKit.Box("base-outpost-slots");
            for (var i = 0; i < BaseLayout.DefaultOutpost.Length; i++)
            {
                var view = new SlotView { Slot = LoadoutSlot.Outpost(i), Open = true };
                BuildSlot(view, "base-outpost-slot");
                outpostSlots.Add(view.Element);
                _outpostViews.Add(view);
            }
            outpost.Add(outpostSlots);
            var outpostText = UiKit.Box("base-outpost-text");
            outpostText.Add(UiKit.Text(Strings.Get("camp.outpost"), "menu-caps base-caps"));
            outpostText.Add(UiKit.Text(Strings.Get("camp.outpostInfo"), "base-note base-outpost-info"));
            outpost.Add(outpostText);
            right.Add(outpost);
            body.Add(right);
            Root.Add(body);

            // What follows the finger while a tower is dragged.
            _ghost = UiKit.Box("base-ghost base-hidden");
            _ghostIcon = UiKit.Icon("tower", UiKit.Ink, 1.6f);
            _ghostIcon.AddToClassList("base-ghost-icon");
            _ghost.Add(_ghostIcon);
            Root.Add(_ghost);

            // Changing a branch that was already chosen costs coins: asked first.
            _confirm = UiKit.Box("base-confirm base-hidden", PickingMode.Position);
            var card = UiKit.Box("base-confirm-card");
            _confirmText = UiKit.Text("", "base-confirm-text");
            card.Add(_confirmText);
            var buttons = UiKit.Box("base-confirm-buttons");
            buttons.Add(UiKit.WideButton("base-confirm-button", "close", Strings.Get("camp.cancel"), null, HideConfirm));
            buttons.Add(UiKit.WideButton("primary base-confirm-button", "check", Strings.Get("camp.change"), null, () =>
            {
                var action = _confirmed;
                HideConfirm();
                action?.Invoke();
            }));
            card.Add(buttons);
            _confirm.Add(card);
            Root.Add(_confirm);
        }

        private VisualElement TowerRow(string id)
        {
            var row = UiKit.Button("base-tower", () => TapTower(id));
            var art = UiKit.Box("base-tower-art");
            art.Add(UiKit.Icon(IconFor(id), UiKit.Ink, 1.6f));
            var badge = UiKit.Box("base-size-badge");
            badge.Add(UiKit.Icon(IsModule(id) ? "module" : SizeIcon(_catalog.Vehicles[id].Fort.Size), UiKit.Ink, 2f));
            art.Add(badge);
            row.Add(art);
            var text = UiKit.Box("base-tower-text");
            text.Add(UiKit.Text(Strings.Card(id), "base-tower-name"));
            text.Add(UiKit.Text("", "base-tower-line"));
            row.Add(text);
            row.Add(UiKit.Text("", "base-tower-count"));
            row.RegisterCallback<PointerDownEvent>(e => Press(e, id, null, true));
            _rows.Add((row, id));
            return row;
        }

        private void BuildSlot(SlotView view, string extra)
        {
            var element = UiKit.Button("base-slot " + extra + " size-" + view.Slot.Size.ToString().ToLowerInvariant(), () => TapSlot(view));
            element.EnableInClassList("utility", view.Utility);
            view.Icon = UiKit.Icon("plus", UiKit.Ink, 1.7f);
            view.Icon.AddToClassList("base-slot-icon");
            element.Add(view.Icon);
            var badge = UiKit.Box("base-slot-size");
            badge.Add(UiKit.Icon(view.Utility ? "module" : SizeIcon(view.Slot.Size), UiKit.Ink, 2f));
            element.Add(badge);
            view.Caption = UiKit.Text("", "base-slot-caption");
            element.Add(view.Caption);
            element.RegisterCallback<PointerDownEvent>(e =>
            {
                if (Soon(view) || !view.Open) return;
                var tower = BaseLayout.At(_layout, view.Slot);
                if (tower != null) Press(e, tower, view.Slot, false);
            });
            view.Element = element;
        }

        private bool IsModule(string id) => _catalog.Vehicles.TryGetValue(id, out var def) && def.Fort is { Kind: FortKind.Utility };

        /// <summary>A card's icon (a utility module without an icon of its own shows the module chip).</summary>
        private string IconFor(string id)
        {
            var icon = CardIcons.For(id);
            return icon == "tank" && IsModule(id) ? "module" : icon;
        }

        /// <summary>A slot that takes nothing yet: a utility slot while there are no utility modules.</summary>
        private bool Soon(SlotView view) => view.Utility && !_hasModules;

        internal static string SizeIcon(SlotSize size) => size switch
        {
            SlotSize.Small => "slot_small",
            SlotSize.Medium => "slot_medium",
            _ => "slot_large",
        };

        private static string SizeName(SlotSize size) => Strings.Get("camp.size." + size.ToString().ToLowerInvariant());

        // ------------------------------------------------------------------ the map's camp

        private MapDefinition Map(string id)
        {
            if (_maps.TryGetValue(id, out var map)) return map;
            try
            {
                map = GameContent.LoadMap(id + "_conquest");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[BaseScreen] No conquest map for {id}: {e.Message}");
                map = null;
            }
            _maps[id] = map;
            return map;
        }

        /// <summary>Shows a map's camp: its HQ and hardpoints as frames on the diagram.</summary>
        public void ShowMap(string id)
        {
            var map = Map(id);
            if (map?.BaseOf(0) == null && id != MatchSettings.AllMaps[0].Id)
            {
                id = MatchSettings.AllMaps[0].Id;
                map = Map(id);
            }
            _mapId = id;
            _site = map?.BaseOf(0);
            _canvas.Map = map;
            _canvas.Clear();
            _campViews.Clear();
            _hq = null;
            if (_site != null)
            {
                foreach (var slot in BaseLayout.Camp(_site, _catalog.Base, _layout.HqLevel))
                {
                    var view = new SlotView
                    {
                        Slot = slot.Slot, Open = slot.Open, Utility = slot.Def.Kind == HardpointKind.Utility, Hardpoint = slot.Hardpoint,
                        World = CampLayout.ToUnity(slot.Def.Position), Facing = slot.Def.Facing,
                    };
                    BuildSlot(view, "base-camp-slot");
                    _canvas.Add(view.Element);
                    _campViews.Add(view);
                }
                _hq = UiKit.Box("base-hq");
                _hq.Add(UiKit.Icon("hq", UiKit.Ink, 1.6f));
                _hqLevel = UiKit.Text("", "base-hq-level");
                _hq.Add(_hqLevel);
                _canvas.Add(_hq);
            }
            else _canvas.Add(UiKit.Text(Strings.Get("camp.noCamp"), "base-note base-no-camp"));
            _mapName.text = Strings.Get("map." + id);
            _mapName.tooltip = Strings.Has("map." + id + ".sub") ? Strings.Get("map." + id + ".sub") : "";
            Refresh();
            if (_canvas.panel != null) _canvas.schedule.Execute(Arrange);
        }

        private void StepMap(int step)
        {
            var maps = MatchSettings.AllMaps.Where(m => Map(m.Id)?.BaseOf(0) != null).Select(m => m.Id).ToList();
            if (maps.Count == 0) return;
            var i = maps.IndexOf(_mapId);
            ShowMap(maps[((i < 0 ? 0 : i + step) % maps.Count + maps.Count) % maps.Count]);
        }

        /// <summary>Places the frames: the camp scaled to the diagram, front up, frames pushed apart where they would overlap.</summary>
        private void Arrange()
        {
            if (_site == null || _hq == null) return;
            var box = _canvas.contentRect.size;
            if (box.x < 10f || box.y < 10f || float.IsNaN(box.x)) return;
            var world = new List<Vector2> { CampLayout.ToUnity(_site.Hq) };
            var sizes = new List<float> { Size(_hq) };
            foreach (var view in _campViews)
            {
                world.Add(view.World);
                sizes.Add(Size(view.Element));
            }
            if (sizes.Any(s => s <= 0f))
            {
                // Styles not resolved yet (the view was just built): try again next frame.
                if (_canvas.panel != null) _canvas.schedule.Execute(Arrange);
                return;
            }
            var fit = CampLayout.Arrange(CampLayout.ToUnity(_site.Hq), _site.Heading, world, sizes, box, _canvas.Gap, _canvas.Pad);
            Place(_hq, fit.Centres[0], sizes[0]);
            var facings = new List<(Vector2 centre, Vector2 direction, float half)>();
            for (var i = 0; i < _campViews.Count; i++)
            {
                Place(_campViews[i].Element, fit.Centres[i + 1], sizes[i + 1]);
                if (!_campViews[i].Utility) facings.Add((fit.Centres[i + 1], fit.PanelDirection(_campViews[i].Facing), sizes[i + 1] * 0.5f));
            }
            _canvas.Fit = fit;
            _canvas.Facings = facings;
            _canvas.MarkDirtyRepaint();
        }

        private static float Size(VisualElement e)
        {
            var w = e.resolvedStyle.width;
            return float.IsNaN(w) ? 0f : w;
        }

        private static void Place(VisualElement e, Vector2 centre, float size)
        {
            e.style.left = centre.x - size * 0.5f;
            e.style.top = centre.y - size * 0.5f;
        }

        // ------------------------------------------------------------------ taps

        /// <summary>A tower card tapped: picked for the panel and armed for a tap on a slot (or into the slot picked first).</summary>
        internal void TapTower(string id)
        {
            if (_picked is { } slot && SlotFor(slot) is { } view && view.Open && !Soon(view))
            {
                Drop(id, null, view);
                return;
            }
            _selected = id;
            _armed = _armed == id ? null : id;
            Refresh();
        }

        /// <summary>A slot tapped: the armed tower goes in; otherwise the slot is picked (tap a tower next, or take its tower out).</summary>
        internal void TapSlot(SlotView view)
        {
            if (Soon(view))
            {
                _note(Strings.Get("camp.utilitySoon"), false);
                return;
            }
            if (!view.Open)
            {
                _note(Strings.Format("camp.closed", OpensAt(view.Slot)), true);
                return;
            }
            if (_armed != null)
            {
                Drop(_armed, null, view);
                return;
            }
            if (_picked is { } picked && picked.Equals(view.Slot)) _picked = null;
            else
            {
                _picked = view.Slot;
                if (BaseLayout.At(_layout, view.Slot) is { } tower) _selected = tower;
            }
            Refresh();
        }

        internal void TapSlot(LoadoutSlot slot)
        {
            if (SlotFor(slot) is { } view) TapSlot(view);
        }

        private SlotView SlotFor(LoadoutSlot slot) =>
            _campViews.FirstOrDefault(v => v.Slot.Equals(slot)) ?? _outpostViews.FirstOrDefault(v => v.Slot.Equals(slot));

        /// <summary>A tower dropped (or tapped) into a slot: from the list it replaces what was there; from another slot it moves (a swap when both fit).</summary>
        private bool Drop(string id, LoadoutSlot? from, SlotView target)
        {
            if (!target.Open || Soon(target)) return false;
            if (!BaseLayout.Fits(_catalog, id, target.Slot))
            {
                _note(Strings.Format("camp.tooBig", Strings.Card(id), SizeName(target.Slot.Size).ToLowerInvariant()), true);
                Refresh();
                return false;
            }
            var done = from is { } source ? BaseLayout.Move(_layout, _catalog, source, target.Slot) : BaseLayout.Place(_layout, _catalog, target.Slot, id);
            if (!done)
            {
                if (from is { Kind: LoadoutSlotKind.Outpost }) _note(Strings.Get("camp.outpostKeep"), true);
                Refresh();
                return false;
            }
            _dirty = true;
            _armed = null;
            _picked = null;
            _selected = id;
            _note(Strings.Format("camp.placed", Strings.Card(id)), false);
            Refresh();
            return true;
        }

        private void TakeOut()
        {
            if (_picked is not { } slot || BaseLayout.At(_layout, slot) is not { } tower) return;
            if (!BaseLayout.CanClear(slot))
            {
                _note(Strings.Get("camp.outpostKeep"), true);
                return;
            }
            BaseLayout.Clear(_layout, slot);
            _dirty = true;
            _picked = null;
            _note(Strings.Format("camp.removed", Strings.Card(tower)), false);
            Refresh();
        }

        internal void SetLevel(int level)
        {
            if (_layout.HqLevel == level) return;
            _layout.HqLevel = level;
            _dirty = true;
            _picked = null;
            ShowMap(_mapId);
        }

        /// <summary>The HQ level that opens a place.</summary>
        private int OpensAt(LoadoutSlot slot)
        {
            var rules = _catalog.Base;
            for (var l = 1; l <= rules.MaxLevel; l++)
                if ((slot.Kind == LoadoutSlotKind.Utility ? rules.UtilitySlots(l) : rules.Slots(l, slot.Size)) > slot.Index) return l;
            return rules.MaxLevel + 1;
        }

        // ------------------------------------------------------------------ saving

        /// <summary>Writes the layout to the profile (only a valid one: see <see cref="BaseLayout.ForSaving"/>).</summary>
        internal void Save()
        {
            if (!_dirty) return;
            PlayerProfile.BaseLoadout = BaseLayout.ForSaving(_layout, _catalog);
            _layout = PlayerProfile.BaseLoadout;
            _dirty = false;
            _note(Strings.Get("camp.savedNote"), false);
            Refresh();
        }

        /// <summary>The view is left (another view, tab or page): nothing is lost.</summary>
        public void Leave()
        {
            EndDrag();
            HideConfirm();
            _armed = null;
            _picked = null;
            if (_dirty) Save();
        }

        /// <summary>The Android back button: closes the question, drops a pick; false when there was nothing to close.</summary>
        public bool Back()
        {
            if (!_confirm.ClassListContains("base-hidden"))
            {
                HideConfirm();
                return true;
            }
            if (_dragging || _armed != null || _picked != null)
            {
                EndDrag();
                _armed = null;
                _picked = null;
                Refresh();
                return true;
            }
            return false;
        }

        // ------------------------------------------------------------------ drag and drop

        private void Press(PointerDownEvent e, string id, LoadoutSlot? from, bool horizontal)
        {
            if (e.pointerType == UnityEngine.UIElements.PointerType.mouse && e.button != 0) return;
            if (_dragging) return;
            _pressPointer = e.pointerId;
            _pressStart = e.position;
            _pressId = id;
            _pressFrom = from;
            _pressHorizontal = horizontal;
        }

        private void OnPointerMove(PointerMoveEvent e)
        {
            if (_pressPointer != e.pointerId || _pressId == null) return;
            var at = (Vector2)e.position;
            if (!_dragging)
            {
                var delta = at - _pressStart;
                if (delta.sqrMagnitude < DragStart * DragStart) return;
                // In the list a mostly vertical pull is a scroll; sideways (towards the camp) it is a drag.
                if (_pressHorizontal && Mathf.Abs(delta.x) < Mathf.Abs(delta.y))
                {
                    _pressPointer = -1;
                    _pressId = null;
                    return;
                }
                BeginDrag();
            }
            MoveGhost(at);
            var over = SlotUnder(at);
            var target = over != null && over.Open && !Soon(over) && BaseLayout.Fits(_catalog, _pressId, over.Slot) ? over : null;
            if (target != _hover)
            {
                _hover?.Element.RemoveFromClassList("hover");
                _hover = target;
                _hover?.Element.AddToClassList("hover");
            }
            _left.EnableInClassList("drop-out", _pressFrom != null && _left.worldBound.Contains(at));
            e.StopPropagation();
        }

        private void BeginDrag()
        {
            _dragging = true;
            _armed = null;
            _picked = null;
            _selected = _pressId;
            _ghostIcon.Name = IconFor(_pressId);
            _ghost.RemoveFromClassList("base-hidden");
            _ghost.BringToFront();
            if (Root.panel != null) Root.CapturePointer(_pressPointer);
            Refresh();
        }

        private void OnPointerUp(PointerUpEvent e)
        {
            if (_pressPointer != e.pointerId) return;
            if (!_dragging)
            {
                _pressPointer = -1;
                _pressId = null;
                return;
            }
            var at = (Vector2)e.position;
            var id = _pressId;
            var from = _pressFrom;
            var over = SlotUnder(at);
            EndDrag();
            if (over != null && !(from is { } f && f.Equals(over.Slot)))
            {
                if (Soon(over)) _note(Strings.Get("camp.utilitySoon"), false);
                else if (!over.Open) _note(Strings.Format("camp.closed", OpensAt(over.Slot)), true);
                else Drop(id, from, over);
            }
            else if (from is { } source && over == null && _left.worldBound.Contains(at))
            {
                // Dragged back onto the list: taken out of its slot.
                _picked = source;
                TakeOut();
            }
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
            _hover?.Element.RemoveFromClassList("hover");
            _hover = null;
            _ghost?.AddToClassList("base-hidden");
            _left?.RemoveFromClassList("drop-out");
            if (was) Refresh();
        }

        private void MoveGhost(Vector2 at)
        {
            var origin = Root.worldBound.position;
            var size = _ghost.resolvedStyle.width;
            if (float.IsNaN(size)) size = 0f;
            _ghost.style.left = at.x - origin.x - size * 0.5f;
            _ghost.style.top = at.y - origin.y - size * 0.5f;
        }

        private SlotView SlotUnder(Vector2 at)
        {
            foreach (var view in _campViews)
                if (view.Element.worldBound.Contains(at)) return view;
            foreach (var view in _outpostViews)
                if (view.Element.worldBound.Contains(at)) return view;
            return null;
        }

        // ------------------------------------------------------------------ refresh

        /// <summary>Brings every part up to date with the layout and the profile (ranks, branches, coins).</summary>
        public void Refresh()
        {
            // Nothing unsaved: follow the profile (a branch chosen, a rank gained elsewhere).
            if (!_dirty && !_dragging) _layout = PlayerProfile.BaseLoadout;
            var carrying = _dragging ? _pressId : _armed;
            RefreshToolbar();
            RefreshSlots(carrying);
            RefreshRows(carrying);
            RefreshPanel();
            RefreshHint(carrying);
            UiKit.Uppercase(Root);
        }

        private void RefreshToolbar()
        {
            var rules = _catalog.Base;
            var level = _layout.HqLevel;
            foreach (var (button, l) in _levelButtons) button.EnableInClassList("chosen", l == level);
            _levelInfo.text = Strings.Format("camp.opens", rules.Slots(level, SlotSize.Small), rules.Slots(level, SlotSize.Medium),
                rules.Slots(level, SlotSize.Large), rules.UtilitySlots(level));
            _save.EnableInClassList("disabled", !_dirty);
            _saveTitle.text = Strings.Get(_dirty ? "camp.save" : "camp.saved").ToUpperInvariant();
            if (_hqLevel != null) _hqLevel.text = Strings.Format("camp.hqLevel", level);
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
            {
                var open = _campViews.Where(v => !v.Utility && v.Slot.Size == size && v.Open).ToList();
                _legendCounts[size].text = $"{open.Count(v => BaseLayout.At(_layout, v.Slot) != null)}/{open.Count}";
            }
            var utilities = _campViews.Where(v => v.Utility && v.Open).ToList();
            _utilityCount.text = $"{utilities.Count(v => BaseLayout.At(_layout, v.Slot) != null)}/{utilities.Count}";
        }

        private void RefreshSlots(string carrying)
        {
            foreach (var view in _campViews.Concat(_outpostViews))
            {
                var soon = Soon(view);
                var tower = soon ? null : BaseLayout.At(_layout, view.Slot);
                var e = view.Element;
                e.EnableInClassList("soon", soon);
                e.EnableInClassList("filled", tower != null);
                e.EnableInClassList("closed", !view.Open);
                var lit = carrying != null && view.Open && !soon && BaseLayout.Fits(_catalog, carrying, view.Slot);
                e.EnableInClassList("lit", lit);
                e.EnableInClassList("dim", carrying != null && !lit);
                e.EnableInClassList("picked", _picked is { } p && p.Equals(view.Slot));
                e.EnableInClassList("selected-type", tower != null && tower == _selected && carrying == null);
                view.Icon.Name = soon ? "module" : tower != null ? IconFor(tower) : view.Open ? "plus" : "lock";
                view.Caption.text = soon ? Strings.Get("camp.soon")
                    : !view.Open ? Strings.Format("camp.hqLevel", OpensAt(view.Slot))
                    : "";
                e.tooltip = tower != null ? Strings.Card(tower) : SizeName(view.Slot.Size);
            }
        }

        private void RefreshRows(string carrying)
        {
            var slot = _picked;
            foreach (var (row, id) in _rows)
            {
                var fort = _catalog.Vehicles[id].Fort;
                var module = fort.Kind == FortKind.Utility;
                row.EnableInClassList("armed", id == carrying);
                row.EnableInClassList("chosen", id == _selected);
                var fits = slot is not { } s || BaseLayout.Fits(_catalog, id, s);
                row.EnableInClassList("nofit", !fits);
                var branch = PlayerProfile.TowerBranch(id);
                var line = Strings.Format("camp.cardLine", module ? Strings.Get("camp.utility") : SizeName(fort.Size), PlayerProfile.Rank(id));
                if (branch != null) line += " · " + Strings.Branch(branch);
                row.Q<Label>(className: "base-tower-line").text = line;
                var placed = PlacedCount(id);
                var count = row.Q<Label>(className: "base-tower-count");
                count.text = placed > 0 ? "×" + placed : "";
                count.EnableInClassList("base-hidden", placed == 0);
            }
        }

        /// <summary>How many places hold a card: the camp's (every HQ level's), the outpost's and the utility slots.</summary>
        private int PlacedCount(string id) => BaseLayout.Placed(_layout, id) + _layout.Outpost.Count(o => o == id) + _layout.Utilities.Count(u => u == id);

        private void RefreshHint(string carrying)
        {
            if (carrying != null) _hint.text = Strings.Format("camp.hintArmed", Strings.Card(carrying));
            else if (_picked is { Kind: LoadoutSlotKind.Outpost }) _hint.text = Strings.Get("camp.outpostKeep");
            else if (_picked is { } slot && BaseLayout.At(_layout, slot) != null) _hint.text = Strings.Get("camp.hintFilled");
            else if (_picked is { } empty) _hint.text = Strings.Format("camp.hintSlot", SizeName(empty.Size).ToLowerInvariant());
            else _hint.text = Strings.Get("camp.hint");
        }

        // ------------------------------------------------------------------ the tower card panel

        private void RefreshPanel()
        {
            var id = _selected;
            _takeOut.EnableInClassList("base-hidden", !(_picked is { } p && BaseLayout.At(_layout, p) != null && BaseLayout.CanClear(p)));
            foreach (var (button, tab) in _tabButtons) button.EnableInClassList("chosen", tab == _tab);
            _panelBody.Clear();
            if (id == null || !_catalog.Vehicles.TryGetValue(id, out var def))
            {
                _headName.text = "";
                _headLine.text = _headCount.text = "";
                return;
            }
            var module = def.Fort.Kind == FortKind.Utility;
            _headIcon.Name = IconFor(id);
            _headSize.Name = module ? "module" : SizeIcon(def.Fort.Size);
            _headName.text = Strings.Card(id);
            var branch = PlayerProfile.TowerBranch(id);
            _headLine.text = Strings.Format("camp.cardLine", module ? Strings.Get("camp.utility") : SizeName(def.Fort.Size), PlayerProfile.Rank(id)) +
                             (branch != null ? " · " + Strings.Branch(branch) : "");
            _headCount.text = Strings.Format("camp.inCamp", PlacedCount(id));
            if (_tab == PanelTab.Branch) BranchPanel(id);
            else GearPanel(id);
        }

        private void BranchPanel(string id)
        {
            var branches = TowerCards.Branches(_catalog, id);
            if (branches.Count == 0)
            {
                _panelBody.Add(UiKit.Text(Strings.Get("camp.branchNone"), "base-note"));
                return;
            }
            var rank = PlayerProfile.Rank(id);
            var chosen = PlayerProfile.TowerBranch(id);
            var locked = rank < TowerCards.BranchRank;
            _panelBody.Add(UiKit.Text(locked ? Strings.Format("camp.branchLocked", TowerCards.BranchRank, rank)
                : chosen == null ? Strings.Get("camp.branchFree")
                : Strings.Format("camp.branchSwap", PlayerProfile.BranchSwapCoins.ToString("N0")), "base-note"));
            foreach (var b in branches)
            {
                var branchId = b;
                var card = UiKit.Button("base-branch", () => ChooseBranch(id, branchId));
                card.EnableInClassList("locked", locked);
                card.EnableInClassList("chosen", branchId == chosen);
                var head = UiKit.Box("base-branch-head");
                head.Add(UiKit.Text(Strings.Branch(branchId), "base-branch-name"));
                if (locked) head.Add(UiKit.Icon("lock", UiKit.Ink, 1.8f));
                else if (branchId == chosen) head.Add(UiKit.Text(Strings.Get("camp.current"), "base-branch-tag"));
                card.Add(head);
                card.Add(UiKit.Text(Strings.Get("branch." + branchId + ".info"), "base-branch-info"));
                _panelBody.Add(card);
            }
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
            if (chosen == null)
            {
                ApplyBranch(towerId, branchId);
                return;
            }
            AskBranch(towerId, branchId);
        }

        /// <summary>Asks before a branch change spends coins.</summary>
        private void AskBranch(string towerId, string branchId)
        {
            _confirmText.text = Strings.Format("camp.branchConfirm", Strings.Card(towerId), Strings.Branch(branchId), PlayerProfile.BranchSwapCoins.ToString("N0"));
            _confirmed = () => ApplyBranch(towerId, branchId);
            _confirm.RemoveFromClassList("base-hidden");
            _confirm.BringToFront();
            UiKit.Uppercase(_confirm);
        }

        private void ApplyBranch(string towerId, string branchId)
        {
            if (!PlayerProfile.TryChooseBranch(towerId, branchId))
            {
                _note(Strings.Get("arsenal.needCoins"), true);
                return;
            }
            if (_layout.Towers.Contains(towerId)) _layout.Branches[towerId] = branchId;
            _note(Strings.Format("camp.branchChosen", Strings.Card(towerId), Strings.Branch(branchId)), false);
            _changed();
            Refresh();
        }

        private void HideConfirm()
        {
            _confirmed = null;
            _confirm?.AddToClassList("base-hidden");
        }

        private void GearPanel(string id)
        {
            var row = UiKit.Box("base-gear-slots");
            var any = false;
            for (var i = 0; i < GearSlots.Length; i++)
            {
                var item = TowerGearIn(id, i);
                any |= item != null;
                var cell = UiKit.Box("base-gear-slot");
                if (item != null) cell.Add(GearArt.Tile(item, GearTile));
                else
                {
                    var empty = UiKit.Box("base-gear-empty");
                    empty.Add(UiKit.Icon(GearSlotIcon(i), UiKit.Ink, 1.6f));
                    cell.Add(empty);
                }
                cell.Add(UiKit.Text(Strings.Get("camp.gearSlot." + GearSlots[i]), "base-gear-name"));
                row.Add(cell);
            }
            _panelBody.Add(row);
            _panelBody.Add(UiKit.Text(any ? Strings.Format("camp.gearShared", Strings.Card(id)) : Strings.Get("camp.gearNone"), "base-note"));
        }

        /// <summary>The gear tile's size (GearArt draws its tiles at a size given in pixels).</summary>
        private const float GearTile = 84f;

        private static string GearSlotIcon(int slot) => slot switch { 0 => "cannon", 1 => "shield", _ => "cbradar" };

        /// <summary>
        /// The piece a tower type wears in one of its three slots (0 Weapon, 1 Structure, 2
        /// Systems), or null. The one place the tower equipment connects: until it is in,
        /// <see cref="PlayerProfile.TowerGear"/> is empty and the pieces are taken in slot order.
        /// </summary>
        internal static GearItem TowerGearIn(string towerId, int slot) => PlayerProfile.TowerGear(towerId).Skip(slot).FirstOrDefault();
    }

    /// <summary>
    /// The camp diagram's ground: a grid turned with the camp, the map's roads and edge, and a
    /// tick from each hardpoint the way its tower faces. Colours and spacings come from the
    /// stylesheet (--camp-* properties on .base-canvas).
    /// </summary>
    internal sealed class CampCanvas : VisualElement
    {
        private static readonly CustomStyleProperty<Color> GridColour = new("--camp-grid");
        private static readonly CustomStyleProperty<Color> RoadColour = new("--camp-road");
        private static readonly CustomStyleProperty<Color> EdgeColour = new("--camp-edge");
        private static readonly CustomStyleProperty<Color> FacingColour = new("--camp-facing");
        private static readonly CustomStyleProperty<float> GridStep = new("--camp-grid-step");
        private static readonly CustomStyleProperty<float> GapSize = new("--camp-gap");
        private static readonly CustomStyleProperty<float> PadSize = new("--camp-pad");
        private static readonly CustomStyleProperty<float> TickLength = new("--camp-tick");

        private Color _grid = Color.clear, _road = Color.clear, _edge = Color.clear, _facing = Color.clear;
        private float _step = 10f, _tick = 10f;

        public CampCanvas()
        {
            pickingMode = PickingMode.Position;
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                var s = e.customStyle;
                if (s.TryGetValue(GridColour, out var c)) _grid = c;
                if (s.TryGetValue(RoadColour, out c)) _road = c;
                if (s.TryGetValue(EdgeColour, out c)) _edge = c;
                if (s.TryGetValue(FacingColour, out c)) _facing = c;
                if (s.TryGetValue(GridStep, out var f)) _step = f;
                if (s.TryGetValue(GapSize, out f)) Gap = f;
                if (s.TryGetValue(PadSize, out f)) Pad = f;
                if (s.TryGetValue(TickLength, out f)) _tick = f;
                MarkDirtyRepaint();
            });
        }

        public MapDefinition Map { get; set; }
        public CampLayout.Fit? Fit { get; set; }
        public List<(Vector2 centre, Vector2 direction, float half)> Facings { get; set; } = new();

        /// <summary>The space kept between two frames (pixels).</summary>
        public float Gap { get; private set; } = 8f;

        /// <summary>The margin inside the diagram (pixels).</summary>
        public float Pad { get; private set; } = 12f;

        private void Draw(MeshGenerationContext context)
        {
            if (Fit is not { } fit) return;
            var p = context.painter2D;
            var rect = contentRect;
            // The grid, every so many metres in the camp's own axes.
            var step = Mathf.Max(8f, _step * fit.Scale);
            p.strokeColor = _grid;
            p.lineWidth = 1f;
            p.BeginPath();
            for (var x = Mathf.Repeat(fit.Origin.x, step); x < rect.width; x += step)
            {
                p.MoveTo(new Vector2(x, 0f));
                p.LineTo(new Vector2(x, rect.height));
            }
            for (var y = Mathf.Repeat(fit.Origin.y, step); y < rect.height; y += step)
            {
                p.MoveTo(new Vector2(0f, y));
                p.LineTo(new Vector2(rect.width, y));
            }
            p.Stroke();
            if (Map != null)
            {
                p.lineCap = LineCap.Round;
                p.lineJoin = LineJoin.Round;
                p.strokeColor = _road;
                foreach (var road in Map.Roads)
                {
                    if (road.Points.Count < 2) continue;
                    p.lineWidth = Mathf.Max(2f, road.Width * fit.Scale);
                    p.BeginPath();
                    p.MoveTo(fit.ToPanel(CampLayout.ToUnity(road.Points[0])));
                    for (var i = 1; i < road.Points.Count; i++) p.LineTo(fit.ToPanel(CampLayout.ToUnity(road.Points[i])));
                    p.Stroke();
                }
                if (Map.Boundary.Count > 2)
                {
                    p.strokeColor = _edge;
                    p.lineWidth = 2f;
                    p.BeginPath();
                    p.MoveTo(fit.ToPanel(CampLayout.ToUnity(Map.Boundary[0])));
                    for (var i = 1; i < Map.Boundary.Count; i++) p.LineTo(fit.ToPanel(CampLayout.ToUnity(Map.Boundary[i])));
                    p.ClosePath();
                    p.Stroke();
                }
            }
            // Which way each tower faces.
            p.strokeColor = _facing;
            p.lineWidth = 2f;
            p.lineCap = LineCap.Round;
            foreach (var (centre, direction, half) in Facings)
            {
                // From the frame's edge outwards (a square: the edge is further along a diagonal).
                var edge = half / Mathf.Max(0.3f, Mathf.Max(Mathf.Abs(direction.x), Mathf.Abs(direction.y))) + 2f;
                p.BeginPath();
                p.MoveTo(centre + direction * edge);
                p.LineTo(centre + direction * (edge + _tick));
                p.Stroke();
            }
        }
    }
}
