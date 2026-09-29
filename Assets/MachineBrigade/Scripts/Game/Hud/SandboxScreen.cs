using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Sandbox's screen (prompt 21 G), rebuilt lean (DECISIONS 21S) in the compact HUD's style: small drawn faces
    /// inside full 44 pt targets, nothing on the battlefield that is not in use. At rest: a slim icon rail on the left
    /// under the minimap and one thin simulation bar along the bottom (run, pause, one tick, speed, seed, reset, the
    /// overlays' tray). The unit picker (an icon grid with a category, a search chip and filters) opens beside the
    /// rail; a selected unit's settings are a small card on the right; the battle's settings, scenarios, duel, A/B,
    /// statistics and both sides' switches are one sheet at a time beside the rail. It has its own UI document over
    /// the battle HUD (or a host panel, for the screenshots and the layout checks).
    /// </summary>
    internal sealed partial class SandboxScreen
    {
        private readonly SandboxController _c;
        private readonly GameObject _host;
        private readonly PanelSettings _settings;
        private readonly VisualElement _root, _frame;
        private readonly VisualElement _rail, _drawer, _grid, _searchRow, _filterRow, _countRow, _card, _cardBody, _bar, _tray, _sheet, _sheetBody,
            _menu, _status, _seedBox;
        private readonly Label _armedLine, _countLabel, _speedLabel, _seedLabel, _clock, _sheetTitle;
        private readonly KitIconButton _unitsButton, _sideButton, _undoButton, _redoButton, _sidesButton, _freeButton, _searchButton, _filterButton,
            _playButton, _pauseButton, _stepButton, _slowerButton, _fasterButton, _layersButton;
        private readonly KitButton _runButton;
        private readonly KitDropdown _shapeDrop;
        private static readonly List<SandboxFormation?> Shapes = new() { null, SandboxFormation.Line, SandboxFormation.Column, SandboxFormation.Cluster, SandboxFormation.Arc };
        private readonly TextField _searchField;
        private bool _drawerOpen, _trayOpen, _bossOpen;
        private SandboxTab _tab;
        private string _search = "";
        private ArmyBranch? _branch;
        private int? _armour;
        private DamageType? _damage;
        private float _refreshIn;
        private Action _sheetRefresh;
        private string _cardFor;

        public SandboxScreen(SandboxController controller, VisualElement host = null)
        {
            _c = controller;
            if (host != null) _root = host;
            else
            {
                _settings = ScriptableObject.CreateInstance<PanelSettings>();
                _settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
                _settings.scaleMode = PanelScaleMode.ConstantPixelSize;
                _settings.scale = BattleHud.MenuScale(Screen.width, Screen.height, Screen.dpi, Application.isMobilePlatform) * MatchSettings.UiScale;
                _settings.sortingOrder = 12;
                _host = new GameObject("Sandbox UI");
                var document = _host.AddComponent<UIDocument>();
                document.panelSettings = _settings;
                _root = document.rootVisualElement;
            }
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Sandbox"));
            _root.pickingMode = PickingMode.Ignore;
            _root.EnableInClassList("cb", MatchSettings.ColorBlind);

            LabelLayer = Kit.Box("sb-labels");
            _root.Add(LabelLayer);
            _frame = Kit.Root("sb");
            _frame.pickingMode = PickingMode.Ignore;
            _root.Add(_frame);
            // In its own document the Sandbox keeps to the safe area itself (a host panel's owner insets it).
            if (host == null) KitSafeArea.Track(_frame);
            _frame.RegisterCallback<GeometryChangedEvent>(_ => _frame.EnableInClassList("sb--wide", _frame.resolvedStyle.width > 1500f));

            // The rail: the picker, the side new units go to, undo and redo; running, both sides' switches; always, more.
            _rail = Kit.Box("sb-rail");
            _unitsButton = Icon(_rail, "sb_grid", "sandbox.units", () =>
            {
                _drawerOpen = !_drawerOpen;
                if (_drawerOpen) CloseSheet();
                Refresh();
            });
            _sideButton = Icon(_rail, "flag", "sandbox.side", () =>
            {
                _c.Editor.Team = 1 - _c.Editor.Team;
                Refresh();
            });
            _undoButton = Icon(_rail, "sb_undo", "sandbox.undo", () => _c.Editor.Undo());
            _redoButton = Icon(_rail, "sb_redo", "sandbox.redo", () => _c.Editor.Redo());
            _sidesButton = Icon(_rail, "cp", "sandbox.sides", () => Open("sandbox.sides", SidesPanel));
            Icon(_rail, "sb_more", "sandbox.more", () => Show(_menu, _menu.style.display == DisplayStyle.None));
            _frame.Add(_rail);

            // More: the rest, one sheet at a time.
            _menu = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-menu", PickingMode.Position);
            MenuRow("settings", "sandbox.settings", () => Open("sandbox.settings", BattlePanel));
            MenuRow("deck", "sandbox.scenarios", () => Open("sandbox.scenarios", ScenariosPanel));
            MenuRow("swords", "sandbox.duel", () => Open("sandbox.duel", DuelPanel));
            MenuRow("sb_ab", "sandbox.ab", () => Open("sandbox.ab", AbPanel));
            MenuRow("sb_chart", "sandbox.stats", () => Open("sandbox.stats.title", StatsPanel));
            MenuRow("home", "sandbox.quit", Quit);
            _menu.style.display = DisplayStyle.None;
            _frame.Add(_menu);

            // The picker (B.2-B.5): category, search, filters, the grid, and how many at once.
            _drawer = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-drawer", PickingMode.Position);
            var head = Kit.Box("fc-row sb-drawer__head");
            var tabs = new List<string>();
            foreach (SandboxTab tab in Enum.GetValues(typeof(SandboxTab))) tabs.Add(Strings.Get("sandbox.tab." + tab));
            var tabDrop = Drop(Strings.Get("sandbox.tab"), tabs, 0, i =>
            {
                _tab = (SandboxTab)i;
                FillGrid();
            });
            tabDrop.AddToClassList("sb-grow");
            head.Add(tabDrop);
            _searchButton = Icon(head, "sb_search", "sandbox.search", () =>
            {
                var show = _searchRow.style.display == DisplayStyle.None;
                Show(_searchRow, show);
                if (show) _searchField.Focus();
                Refresh();
            });
            _filterButton = Icon(head, "sb_filter", "sandbox.filter", () =>
            {
                Show(_filterRow, _filterRow.style.display == DisplayStyle.None);
                Refresh();
            });
            _drawer.Add(head);
            _searchRow = Kit.Box("sb-drawer__row");
            _searchField = new TextField { label = "" };
            _searchField.AddToClassList("sb-field");
            _searchField.textEdition.placeholder = Strings.Get("sandbox.search");
            _searchField.RegisterValueChangedCallback(e =>
            {
                _search = e.newValue ?? "";
                FillGrid();
            });
            _searchRow.Add(_searchField);
            Show(_searchRow, false);
            _drawer.Add(_searchRow);
            _filterRow = Filters();
            Show(_filterRow, false);
            _drawer.Add(_filterRow);
            var gridScroll = Kit.Scroll(ScrollViewMode.Vertical, "sb-drawer__grid");
            _grid = gridScroll.contentContainer;
            _grid.AddToClassList("sb-grid");
            _drawer.Add(gridScroll);
            var foot = Kit.Box("sb-drawer__foot");
            var shapeNames = new List<string>();
            foreach (var s in Shapes) shapeNames.Add(Strings.Get("sandbox.formation." + (s?.ToString() ?? "Single")));
            var footRow = Kit.Box("fc-row");
            _shapeDrop = Drop(Strings.Get("sandbox.formation"), shapeNames, Math.Max(0, Shapes.IndexOf(_c.Formation)), i =>
            {
                _c.Formation = Shapes[i];
                Refresh();
            });
            _shapeDrop.AddToClassList("sb-grow");
            footRow.Add(_shapeDrop);
            _freeButton = Icon(footRow, "sb_free", "sandbox.freeRotate", () =>
            {
                _c.Editor.FreeRotation = !_c.Editor.FreeRotation;
                Refresh();
            });
            foot.Add(footRow);
            _countRow = Kit.Box("fc-row sb-step");
            _countLabel = Kit.Text("", "fc-body sb-step__label");
            _countRow.Add(_countLabel);
            Icon(_countRow, "minus", "sandbox.fewer", () =>
            {
                _c.FormationCount = Math.Max(2, _c.FormationCount - 1);
                Refresh();
            });
            Icon(_countRow, "plus", "sandbox.more.units", () =>
            {
                _c.FormationCount = Math.Min(16, _c.FormationCount + 1);
                Refresh();
            });
            foot.Add(_countRow);
            _armedLine = Kit.Text("", "fc-small sb-hint");
            foot.Add(_armedLine);
            _drawer.Add(foot);
            _frame.Add(_drawer);

            // The selection's card (B.6, B.9, C.3, D).
            _card = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-card", PickingMode.Position);
            var cardScroll = Kit.Scroll(ScrollViewMode.Vertical, "sb-card__scroll");
            _cardBody = cardScroll.contentContainer;
            _card.Add(cardScroll);
            _frame.Add(_card);

            // One sheet at a time: settings, scenarios, duel, A/B, statistics, both sides.
            _sheet = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-sheet", PickingMode.Position);
            var sheetHead = Kit.Box("fc-row sb-sheet__head");
            _sheetTitle = Kit.Text("", "fc-panel-title fc-row-text sb-grow");
            sheetHead.Add(_sheetTitle);
            Icon(sheetHead, "close", "sandbox.close", () =>
            {
                CloseSheet();
                Refresh();
            });
            _sheet.Add(sheetHead);
            var sheetScroll = Kit.Scroll(ScrollViewMode.Vertical, "sb-sheet__scroll");
            _sheetBody = sheetScroll.contentContainer;
            _sheet.Add(sheetScroll);
            Show(_sheet, false);
            _frame.Add(_sheet);

            // The simulation bar (C.1, C.6): one row.
            _bar = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-bar", PickingMode.Position);
            // Run from set-up; Edit (stop, back to set-up) while running: the scene is built anew for each, so the icon holds.
            _runButton = new KitButton(ButtonTier.Primary, Strings.Get(_c.Editing ? "sandbox.run" : "sandbox.edit"), () => _c.Rebuild(_c.Editing), _c.Editing ? "play" : "stop");
            _runButton.AddToClassList("sb-run");
            _bar.Add(_runButton);
            _pauseButton = Icon(_bar, "pause", "sandbox.pause", () =>
            {
                _c.Paused = true;
                Refresh();
            });
            _playButton = Icon(_bar, "play", "sandbox.resume", () =>
            {
                _c.Paused = false;
                Refresh();
            });
            _stepButton = Icon(_bar, "sb_step", "sandbox.step", () =>
            {
                _c.StepOnce();
                Refresh();
            });
            _slowerButton = Icon(_bar, "minus", "sandbox.slower", () =>
            {
                _c.SpeedIndex = Math.Max(0, _c.SpeedIndex - 1);
                Refresh();
            });
            _speedLabel = Kit.Text("", "fc-number-small sb-bar__speed");
            _bar.Add(_speedLabel);
            _fasterButton = Icon(_bar, "plus", "sandbox.faster", () =>
            {
                _c.SpeedIndex = Math.Min(SandboxController.Speeds.Length - 1, _c.SpeedIndex + 1);
                Refresh();
            });
            var seed = Kit.Tappable("sb-seed", () => Show(_seedBox, _seedBox.style.display == DisplayStyle.None));
            seed.tooltip = Strings.Get("sandbox.seed.hint");
            var seedFace = Kit.Box("sb-face");
            seedFace.Add(Kit.Icon("dice", "sb-face__icon"));
            _seedLabel = Kit.Text("", "fc-small sb-face__text");
            seedFace.Add(_seedLabel);
            seed.Add(seedFace);
            _bar.Add(seed);
            _clock = Kit.Text("", "fc-small sb-bar__clock");
            _bar.Add(_clock);
            Icon(_bar, "restart", "sandbox.reset", () => _c.Rebuild(!_c.Editing));
            _layersButton = Icon(_bar, "sb_layers", "sandbox.layers", () =>
            {
                _trayOpen = !_trayOpen;
                FillTray();
                Refresh();
            });
            _frame.Add(_bar);

            // The seed (C.6), just above its chip.
            _seedBox = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-seedbox", PickingMode.Position);
            var seedField = new TextField(Strings.Get("sandbox.seed")) { value = _c.Editor.Scenario.Seed.ToString(), isDelayed = true };
            seedField.AddToClassList("sb-field");
            seedField.RegisterValueChangedCallback(e =>
            {
                if (int.TryParse(e.newValue, out var n)) _c.Editor.Settings(x => x.Seed = n);
                Refresh();
            });
            _seedBox.Add(seedField);
            _seedBox.Add(Kit.Text(Strings.Get("sandbox.seed.hint"), "fc-small sb-hint"));
            Show(_seedBox, false);
            _frame.Add(_seedBox);

            // The overlays' tray (E), over the bar.
            _tray = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field sb-tray", PickingMode.Position);
            _frame.Add(_tray);

            _status = Kit.Box("sb-status");
            _frame.Add(_status);

            Kit.ApplyTextSize(_frame);
            FillGrid();
            FillTray();
            Refresh();
        }

        /// <summary>Where the overlays' words go (under the panels).</summary>
        public VisualElement LabelLayer { get; }

        public bool IsOverUi(Vector2 screen)
        {
            var panel = _root.panel;
            if (panel == null) return false;
            var p = RuntimePanelUtils.ScreenToPanel(panel, new Vector2(screen.x, Screen.height - screen.y));
            var picked = panel.Pick(p);
            return picked != null && picked != _root && !LabelLayer.Contains(picked);
        }

        // ------------------------------------------------------------------ small building blocks

        /// <summary>A small face in a full touch target, with its words as its label (the compact HUD's icon buttons).</summary>
        private static KitIconButton Icon(VisualElement parent, string icon, string labelKey, Action onTap)
        {
            var b = new KitIconButton(icon, Strings.Get(labelKey), onTap, plain: true);
            parent.Add(b);
            return b;
        }

        private static void On(KitIconButton b, bool on) => b.EnableInClassList("fc-icon-btn--on", on);

        private static void Show(VisualElement e, bool show) => e.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;

        private void MenuRow(string icon, string key, Action onTap)
        {
            var row = Kit.Tappable("sb-menu__row", () =>
            {
                Show(_menu, false);
                onTap();
            });
            row.Add(Kit.Icon(icon, "sb-face__icon"));
            row.Add(Kit.Text(Strings.Get(key), "fc-body fc-row-text sb-menu__label"));
            _menu.Add(row);
        }

        /// <summary>A text button for the sheets (the card and the bars use icons).</summary>
        private static VisualElement Small(string label, Action onTap)
        {
            var b = Kit.Tappable("sb-button", onTap);
            var face = Kit.Box("sb-face");
            face.Add(Kit.Text(label, "fc-small sb-face__text"));
            b.Add(face);
            return b;
        }

        private static VisualElement Row(params VisualElement[] items)
        {
            var row = Kit.Box("fc-row sb-wrap");
            foreach (var i in items) row.Add(i);
            return row;
        }

        private static Label Caption(string key) => Kit.Text(Kit.Caps(Strings.Get(key)), "fc-caption sb-caption");

        private static KitDropdown Drop(string label, IReadOnlyList<string> options, int selected, Action<int> changed)
        {
            var list = new List<KitOption>();
            foreach (var o in options) list.Add(new KitOption(o));
            var d = new KitDropdown(label, list, Mathf.Clamp(selected, 0, Math.Max(0, list.Count - 1)), changed, thumbnail: false);
            d.AddToClassList("sb-drop");
            return d;
        }

        /// <summary>A number with its minus and plus: "Rank 3 [-] [+]".</summary>
        private VisualElement Stepper(string text, Action down, Action up)
        {
            var row = Kit.Box("fc-row sb-step");
            row.Add(Kit.Text(text, "fc-body sb-step__label"));
            Icon(row, "minus", "sandbox.less", () =>
            {
                down();
                Refresh();
            });
            Icon(row, "plus", "sandbox.more.value", () =>
            {
                up();
                Refresh();
            });
            return row;
        }

        /// <summary>An icon that toggles, its words as its label.</summary>
        private KitIconButton Toggle(VisualElement parent, string icon, string labelKey, bool on, Action<bool> changed)
        {
            var b = Icon(parent, icon, labelKey, () => changed(!on));
            On(b, on);
            return b;
        }

        public void Toast(string text, bool error = false) => KitToast.Show(_frame, text, error ? ToastKind.Alert : ToastKind.Info, 3f);

        /// <summary>A unit's icon on the grid and the card: its card icon, a boss's skull (a mini boss's crown), a ship's anchor.</summary>
        internal static string IconFor(VehicleDef def)
        {
            if (def.Naval != null) return "anchor";
            if (def.Boss) return def.MiniBoss ? "crown" : "skull";
            var icon = CardIcons.For(def.Elite && def.EliteOf != null ? def.EliteOf : def.Id);
            if (icon == "tank" && def.Flying) icon = def.Class == UnitClass.Helicopter ? "helicopter" : "jet";
            return Icons.Exists(icon) ? icon : "tank";
        }

        // ------------------------------------------------------------------ the picker

        private VisualElement Filters()
        {
            var box = Kit.Box("sb-drawer__row");
            var all = Strings.Get("sandbox.filter.all");
            var branches = new List<string> { all };
            foreach (ArmyBranch b in Enum.GetValues(typeof(ArmyBranch))) branches.Add(Strings.Get("kit.branch." + b.ToString().ToLowerInvariant()));
            box.Add(Drop(Strings.Get("sandbox.filter.branch"), branches, 0, i =>
            {
                _branch = i == 0 ? null : (ArmyBranch)(i - 1);
                FillGrid();
            }));
            var levels = new List<string> { all };
            for (var l = 0; l <= ArmourLevels.Max; l++) levels.Add(Strings.Get("armour.level." + l));
            box.Add(Drop(Strings.Get("sandbox.filter.armour"), levels, 0, i =>
            {
                _armour = i == 0 ? null : i - 1;
                FillGrid();
            }));
            var types = new List<string> { all };
            var typeValues = (DamageType[])Enum.GetValues(typeof(DamageType));
            foreach (var t in typeValues) types.Add(Strings.Get("dtype." + t));
            box.Add(Drop(Strings.Get("sandbox.filter.weapon"), types, 0, i =>
            {
                _damage = i == 0 ? null : typeValues[i - 1];
                FillGrid();
            }));
            return box;
        }

        private void FillGrid()
        {
            _grid.Clear();
            var catalog = _c.World.Catalog;
            var list = SandboxRules.Palette(catalog, _tab, Strings.Unit, _search, _branch, _armour, _damage, def => _c.Session.Access.Allowed(catalog, def));
            if (list.Count == 0) _grid.Add(Kit.Text(Strings.Get("sandbox.empty"), "fc-small sb-hint"));
            foreach (var def in list)
            {
                var id = def.Id;
                var cell = Kit.Tappable("sb-cell" + (_c.Placing == id ? " sb-cell--armed" : ""), () =>
                {
                    _c.Placing = _c.Placing == id ? null : id;
                    _c.Picking = SandboxController.Pick.None;
                    FillGrid();
                    Refresh();
                });
                cell.tooltip = Strings.Unit(id);
                cell.Add(Kit.Icon(IconFor(def), "sb-cell__icon"));
                var name = Kit.Text(Strings.Short(id), "fc-small sb-cell__name");
                cell.Add(name);
                if (def.CpCost > 0) cell.Add(Kit.Text(SandboxText.Number(def.CpCost), "fc-small sb-cell__cost"));
                if (def.Elite) cell.Add(Kit.Icon("elite", "sb-cell__mark"));
                _grid.Add(cell);
            }
        }

        // ------------------------------------------------------------------ the overlays' tray

        private void FillTray()
        {
            _tray.Clear();
            var chips = Kit.Box("fc-row sb-wrap");
            void Chip(SandboxLayer layer, string icon, string key)
            {
                var chip = new KitChip(Strings.Get("sandbox.layer.short." + key), _c.LayerOn(layer), () =>
                {
                    _c.Layers[layer] = !_c.LayerOn(layer);
                    FillTray();
                }, icon);
                chip.tooltip = Strings.Get("sandbox.layer." + key);
                chips.Add(chip);
            }
            Chip(SandboxLayer.Range, "crosshair", "range");
            Chip(SandboxLayer.Hits, "bolt", "hits");
            Chip(SandboxLayer.Dps, "gauge", "dps");
            Chip(SandboxLayer.Ammo, "ammo", "ammo");
            Chip(SandboxLayer.Zones, "shield", "zones");
            // E.6: never in the player version.
            if (SandboxSession.Internal)
            {
                Chip(SandboxLayer.Hull, "expand", "hull");
                Chip(SandboxLayer.Route, "move", "route");
                Chip(SandboxLayer.Stuck, "lock", "stuck");
                Chip(SandboxLayer.Buy, "cart", "buy");
            }
            _tray.Add(chips);
            if (_c.LayerOn(SandboxLayer.Buy)) BuyScores(_tray);
        }

        private void BuyScores(VisualElement box)
        {
            for (var team = 0; team < 2; team++)
            {
                if (_c.Battle.Commander(team)?.BuyScores is not { Count: > 0 } buy) continue;
                box.Add(Kit.Text(SandboxText.Format("sandbox.buy.title", ("side", Strings.Get("sandbox.side." + team))), "fc-caption sb-caption"));
                var list = new List<KeyValuePair<string, float>>(buy);
                list.Sort((a, b) => b.Value.CompareTo(a.Value));
                var line = new List<string>();
                for (var i = 0; i < Math.Min(5, list.Count); i++) line.Add(Strings.Short(list[i].Key) + " " + SandboxText.Number(list[i].Value, 1));
                box.Add(Kit.Text(string.Join(" · ", line), "fc-small sb-hint"));
            }
        }

        // ------------------------------------------------------------------ every frame

        public void Tick()
        {
            RunJobs();
            var w = _c.World;
            if (!_c.Editing)
                _clock.text = SandboxText.Format("sandbox.clock", ("seconds", SandboxText.Number(w.Time, 1)), ("tick", w.Tick.ToString()));
            _refreshIn -= Time.unscaledDeltaTime;
            if (!_c.Editing && _refreshIn <= 0f)
            {
                _refreshIn = 0.5f;
                _cardFor = null;
                FillCard();
                ShowStatus();
                _sheetRefresh?.Invoke();
                if (_trayOpen && _c.LayerOn(SandboxLayer.Buy)) FillTray();
            }
        }

        /// <summary>Everything that depends on the state and the selection.</summary>
        public void Refresh()
        {
            var editing = _c.Editing;
            var e = _c.Editor;
            Show(_unitsButton, editing);
            Show(_sideButton, editing);
            Show(_undoButton, editing);
            Show(_redoButton, editing);
            Show(_sidesButton, !editing);
            On(_unitsButton, _drawerOpen && editing);
            _sideButton.EnableInClassList("sb-side--0", e.Team == 0);
            _sideButton.EnableInClassList("sb-side--1", e.Team == 1);
            _sideButton.tooltip = SandboxText.Format("sandbox.side.pick", ("side", Strings.Get("sandbox.side." + e.Team)));
            _undoButton.SetDisabled(!e.CanUndo);
            _redoButton.SetDisabled(!e.CanRedo);
            Show(_drawer, _drawerOpen && editing);
            On(_searchButton, _searchRow.style.display != DisplayStyle.None);
            On(_filterButton, _filterRow.style.display != DisplayStyle.None);
            On(_freeButton, e.FreeRotation);
            Show(_countRow, _c.Formation != null);
            _shapeDrop.Select(Math.Max(0, Shapes.IndexOf(_c.Formation)), false);
            _countLabel.text = SandboxText.Format("sandbox.count", ("count", _c.FormationCount));
            _armedLine.text = _c.Placing != null ? SandboxText.Format("sandbox.place.armed", ("unit", Strings.Unit(_c.Placing))) : Strings.Get("sandbox.place.hint");

            _runButton.Label = Strings.Get(editing ? "sandbox.run" : "sandbox.edit");
            Show(_pauseButton, !editing && !_c.Paused);
            Show(_playButton, !editing && _c.Paused);
            Show(_stepButton, !editing);
            Show(_slowerButton, !editing);
            Show(_speedLabel, !editing);
            Show(_fasterButton, !editing);
            Show(_clock, !editing);
            if (!editing)
                _clock.text = SandboxText.Format("sandbox.clock", ("seconds", SandboxText.Number(_c.World.Time, 1)), ("tick", _c.World.Tick.ToString()));
            _speedLabel.text = SandboxText.Format("sandbox.speed.value", ("speed", SandboxText.Number(_c.Speed, _c.Speed < 1f ? 2 : 0)));
            _slowerButton.SetDisabled(_c.SpeedIndex <= 0);
            _fasterButton.SetDisabled(_c.SpeedIndex >= SandboxController.Speeds.Length - 1);
            _seedLabel.text = SandboxText.Format("sandbox.seed.chip", ("seed", e.Scenario.Seed.ToString()));
            On(_layersButton, _trayOpen);
            Show(_tray, _trayOpen);
            _cardFor = null;
            FillCard();
            ShowStatus();
        }

        private void ShowStatus()
        {
            _status.Clear();
            var b = _c.Battle;
            string text = null;
            if (_c.Picking == SandboxController.Pick.MoveUnits) text = Strings.Get("sandbox.move.hint");
            else if (_c.Picking == SandboxController.Pick.OrderMove) text = Strings.Get("sandbox.order.pickPoint");
            else if (_c.Picking == SandboxController.Pick.OrderTarget) text = Strings.Get("sandbox.order.pickTarget");
            else if (_c.Picking == SandboxController.Pick.Strike) text = Strings.Get("sandbox.call.pick");
            else if (b.Result is { } r) text = ResultLine(r.WinningTeam, b.EndedAt, SandboxBattle.HealthShare(_c.World, 0), SandboxBattle.HealthShare(_c.World, 1));
            if (text == null) return;
            _status.Add(Kit.Text(text, "fc-small sb-status__text"));
        }

        internal static string ResultLine(int winner, double seconds, float blue, float red) =>
            SandboxText.Format("sandbox.result.line",
                ("result", Strings.Get(winner == 0 ? "sandbox.result.0" : winner == 1 ? "sandbox.result.1" : winner == -1 ? "sandbox.result.draw" : "sandbox.result.open")),
                ("seconds", SandboxText.Number(seconds, 1)), ("blue", SandboxText.Number(blue * 100f)), ("red", SandboxText.Number(red * 100f)));

        // ------------------------------------------------------------------ the card

        private void FillCard()
        {
            var key = string.Join(",", _c.Selected) + (_c.Editing ? "e" : "r") + _bossOpen;
            if (key == _cardFor) return;
            _cardFor = key;
            _cardBody.Clear();
            Show(_card, _c.Selected.Count > 0);
            if (_c.Selected.Count == 0) return;
            if (_c.Editing) EditingCard(_c.Selected);
            else RunningCard();
        }

        private void CardHead(string defId, VehicleDef def, string line, bool delete)
        {
            var head = Kit.Box("fc-row sb-card__head");
            if (def != null) head.Add(Kit.Icon(IconFor(def), "sb-card__icon"));
            head.Add(Kit.Text(Kit.Caps(Strings.Short(defId)), "fc-caption fc-row-text sb-grow sb-card__name"));
            if (delete)
                Icon(head, "sb_trash", "sandbox.delete", () =>
                {
                    _c.Editor.Delete(new List<int>(_c.Selected));
                    _c.Selected.Clear();
                    Refresh();
                });
            Icon(head, "close", "sandbox.close", () =>
            {
                _c.Selected.Clear();
                Refresh();
            });
            _cardBody.Add(head);
            _cardBody.Add(Kit.Text(line, "fc-small sb-card__line"));
        }

        private void EditingCard(List<int> sel)
        {
            var e = _c.Editor;
            var catalog = _c.World.Catalog;
            var first = e.Units[sel[0]];
            catalog.Vehicles.TryGetValue(first.Def, out var def);
            CardHead(first.Def, def, SandboxText.Format("sandbox.selected", ("count", sel.Count)) + " · " + Strings.Get("sandbox.side." + first.Team) + " · " +
                SandboxText.Format("sandbox.heading", ("degrees", SandboxText.Number(first.Heading, e.FreeRotation ? 1 : 0))), true);
            var actions = Kit.Box("fc-row sb-card__icons");
            Icon(actions, "sb_turn_left", "sandbox.turnLeft", () => e.RotateBy(sel, -SandboxRules.RotationStep));
            Icon(actions, "sb_turn_right", "sandbox.turnRight", () => e.RotateBy(sel, SandboxRules.RotationStep));
            Icon(actions, "move", "sandbox.move", () =>
            {
                _c.Placing = null;
                _c.Picking = SandboxController.Pick.MoveUnits;
                FillGrid();
                ShowStatus();
            });
            Icon(actions, "sb_copy", "sandbox.copy", () =>
            {
                var copies = e.Copy(sel, new System.Numerics.Vector2(6f, -6f));
                sel.Clear();
                sel.AddRange(copies);
                Refresh();
            });
            _cardBody.Add(actions);
            var toggles = Kit.Box("fc-row sb-card__icons");
            var side = Icon(toggles, "flag", "sandbox.side.switch", () => e.Edit(sel, u => u.Team = 1 - first.Team));
            side.AddToClassList("sb-side--" + first.Team);
            if (def != null && catalog.EliteVariant(def.Id) != null) Toggle(toggles, "elite", "sandbox.elite", first.Elite, on => e.Edit(sel, u => u.Elite = on));
            Toggle(toggles, "shield", "sandbox.immortal", first.Immortal, on => e.Edit(sel, u => u.Immortal = on));
            _cardBody.Add(toggles);
            _cardBody.Add(Stepper(SandboxText.Format("sandbox.rank", ("rank", first.Rank)), () => e.Edit(sel, u => u.Rank--), () => e.Edit(sel, u => u.Rank++)));
            _cardBody.Add(Stepper(SandboxText.Format("sandbox.hp", ("percent", first.Hp)), () => e.Edit(sel, u => u.Hp -= 10), () => e.Edit(sel, u => u.Hp += 10)));
            _cardBody.Add(Stepper(SandboxText.Format("sandbox.ammo", ("percent", first.Ammo)), () => e.Edit(sel, u => u.Ammo -= 10), () => e.Edit(sel, u => u.Ammo += 10)));
            var gears = (SandboxGear[])Enum.GetValues(typeof(SandboxGear));
            var gearNames = new List<string>();
            foreach (var g in gears) gearNames.Add(Strings.Get("sandbox.gear." + g));
            _cardBody.Add(Drop(Strings.Get("sandbox.gear"), gearNames, (int)first.Gear, i => e.Edit(sel, u => u.Gear = gears[i])));
            if (def != null && SandboxRules.IsTower(def)) TowerBranch(sel[0], first, def);
            if (def is { Tiers: not null })
            {
                var tiers = new[] { "", "low", "high" };
                _cardBody.Add(Drop(Strings.Get("sandbox.tier"), new[] { Strings.Get("sandbox.tier.none"), Strings.Get("sandbox.tier.low"), Strings.Get("sandbox.tier.high") },
                    Math.Max(0, Array.IndexOf(tiers, first.Tier)), i => e.Edit(sel, u => u.Tier = tiers[i])));
            }
            if (def is { Boss: true } && first.Boss is { } boss && BossHeader())
            {
                var phases = Math.Min(3, Math.Max(def.Phases.Count, def.Tiers?.Marks.Count ?? 0) + 1);
                var names = new List<string>();
                for (var p = 0; p < phases; p++) names.Add(SandboxText.Format("sandbox.boss.phase", ("phase", p + 1)));
                _cardBody.Add(Drop(Strings.Get("sandbox.boss.startPhase"), names, boss.Phase, i => e.Edit(sel, u => (u.Boss ??= new SandboxBossState()).Phase = i)));
                var row = Kit.Box("fc-row sb-card__icons");
                Toggle(row, "bolt", "sandbox.boss.bigOff", boss.BigOff, on => e.Edit(sel, u => (u.Boss ??= new SandboxBossState()).BigOff = on));
                Toggle(row, "people", "sandbox.boss.escorts", !boss.NoEscorts, on => e.Edit(sel, u => (u.Boss ??= new SandboxBossState()).NoEscorts = !on));
                _cardBody.Add(row);
                for (var i = 0; i < def.Parts.Count; i++)
                {
                    var part = i;
                    _cardBody.Add(new KitToggle(SandboxText.Format("sandbox.boss.break", ("part", Strings.Get("part." + def.Parts[i].Kind))), boss.Broken.Contains(i), on => e.Edit(sel, u =>
                    {
                        var b = u.Boss ??= new SandboxBossState();
                        b.Broken.Remove(part);
                        if (on) b.Broken.Add(part);
                    })));
                }
            }
        }

        private void TowerBranch(int index, SandboxUnit first, VehicleDef def)
        {
            var e = _c.Editor;
            var tower = def.BranchOf ?? def.Id;
            var branches = SandboxRules.Branches(_c.World.Catalog, tower);
            if (branches.Count == 0) return;
            if (first.Rank < SandboxRules.BranchRank)
            {
                _cardBody.Add(Kit.Text(Strings.Get("sandbox.branch.locked"), "fc-small sb-hint"));
                return;
            }
            var names = new List<string> { Strings.Get("sandbox.branch.none") };
            foreach (var b in branches) names.Add(Strings.Branch(b));
            _cardBody.Add(Drop(Strings.Get("sandbox.branch"), names, def.BranchOf == null ? 0 : branches.IndexOf(first.Def) + 1, i =>
            {
                if (!e.SetBranch(index, i == 0 ? null : branches[i - 1])) Toast(Strings.Get("sandbox.refuse.Locked"), true);
            }));
        }

        /// <summary>The boss section's header, folded until opened; true when open.</summary>
        private bool BossHeader()
        {
            var head = Kit.Tappable("fc-row sb-fold", () =>
            {
                _bossOpen = !_bossOpen;
                _cardFor = null;
                FillCard();
            });
            head.Add(Kit.Text(Kit.Caps(Strings.Get("sandbox.boss")), "fc-caption fc-row-text sb-grow"));
            var caret = Kit.Icon("caret", "sb-fold__caret" + (_bossOpen ? " sb-fold__caret--open" : ""));
            head.Add(caret);
            _cardBody.Add(head);
            return _bossOpen;
        }

        private void RunningCard()
        {
            var vehicles = new List<Vehicle>(_c.SelectedVehicles());
            if (vehicles.Count == 0)
            {
                Show(_card, false);
                return;
            }
            var first = vehicles[0];
            CardHead(first.Def.Id, first.Def, SandboxText.Format("sandbox.selected", ("count", vehicles.Count)) + " · " + Strings.Get("sandbox.side." + first.Team) + " · " +
                SandboxText.Format("sandbox.hp", ("percent", SandboxText.Number(first.Hp / Mathf.Max(1f, first.MaxHp) * 100f))), false);
            var ids = _c.Selected.ToArray();
            var orders = Kit.Box("fc-row sb-card__icons");
            Icon(orders, "move", "sandbox.order.move", () =>
            {
                _c.Picking = SandboxController.Pick.OrderMove;
                ShowStatus();
            });
            Icon(orders, "crosshair", "sandbox.order.fire", () =>
            {
                _c.Picking = SandboxController.Pick.OrderTarget;
                ShowStatus();
            });
            Icon(orders, "anchor", "sandbox.order.hold", () => _c.Queue(SandboxOp.For(SandboxOpKind.Hold, ids)));
            Icon(orders, "retreat", "sandbox.order.release", () => _c.Queue(SandboxOp.For(SandboxOpKind.Release, ids)));
            _cardBody.Add(orders);
            var toggles = Kit.Box("fc-row sb-card__icons");
            Toggle(toggles, "stop", "sandbox.order.holdFire", first.HoldFire, on => _c.Queue(SandboxOp.For(SandboxOpKind.HoldFire, ids, on ? 1 : 0)));
            Toggle(toggles, "shield", "sandbox.immortal", _c.Battle.IsImmortal(first.Id.Value), on => _c.Queue(SandboxOp.For(SandboxOpKind.Immortal, ids, on ? 1 : 0)));
            _cardBody.Add(toggles);
            if (first.Def.Boss && BossHeader()) BossTools(first);
        }

        /// <summary>D: the boss tools on a running boss.</summary>
        private void BossTools(Vehicle boss)
        {
            var id = boss.Id.Value;
            var def = boss.Def;
            // Play-test 6 (DECISIONS 21B): the boss's file, the menu's boss page as a dialog.
            var file = Kit.Box("fc-row sb-card__icons");
            Icon(file, "info", "guide.boss.fileButton", () => BossFile.Show(_root, _c.World.Catalog, def));
            _cardBody.Add(file);
            var phases = Math.Min(3, Math.Max(def.Phases.Count, def.Tiers?.Marks.Count ?? 0) + 1);
            var row = Kit.Box("fc-row sb-wrap");
            for (var p = 1; p < phases; p++)
            {
                var ph = p;
                row.Add(new KitChip(SandboxText.Format("sandbox.boss.phase", ("phase", p + 1)), false, () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossPhase, id, ph))));
            }
            _cardBody.Add(row);
            var icons = Kit.Box("fc-row sb-card__icons");
            if (boss.BigAttack is { } big)
            {
                Icon(icons, "airstrike", "sandbox.boss.big", () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossBig, id)));
                Toggle(icons, "bolt", "sandbox.boss.bigOff", big.Off, on => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossBigOff, id, on ? 1 : 0)));
            }
            Toggle(icons, "people", "sandbox.boss.escorts", _c.World.EscortsAlive(boss.Id) > 0, on => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossEscorts, id, on ? 1 : 0)));
            if (def.MiniVariant != null || def.VariantOf != null)
                Icon(icons, "restart", "sandbox.boss.swap", () =>
                {
                    _c.Queue(SandboxOp.Boss(SandboxOpKind.BossSwap, id));
                    _c.Selected.Clear();
                });
            _cardBody.Add(icons);
            if (def.Tiers != null)
                _cardBody.Add(Row(new KitChip(Strings.Get("sandbox.tier.low"), boss.TierFrom == AltitudeTier.Low, () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossTier, id, 1))),
                    new KitChip(Strings.Get("sandbox.tier.high"), boss.TierFrom == AltitudeTier.High, () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossTier, id, 2)))));
            for (var i = 0; i < boss.PartCount; i++)
            {
                var part = i;
                _cardBody.Add(new KitToggle(SandboxText.Format("sandbox.boss.break", ("part", Strings.Get("part." + def.Parts[i].Kind))), boss.IsPartBroken(i),
                    on => _c.Queue(SandboxOp.Boss(on ? SandboxOpKind.BossBreak : SandboxOpKind.BossRestore, id, part))));
            }
            var diffNames = new List<string>();
            foreach (var d in Difficulties) diffNames.Add(Strings.Get("sandbox.diff." + d));
            _cardBody.Add(Drop(Strings.Get("sandbox.boss.difficulty"), diffNames, Math.Max(0, Array.IndexOf(Difficulties, _c.Battle.Scenario.Difficulty)),
                i => _c.Queue(new SandboxOp { Kind = SandboxOpKind.Difficulty, Text = Difficulties[i] })));
        }

        internal static readonly string[] Difficulties = { "Easy", "Normal", "Hard", "Heroic", "Iron" };

        // ------------------------------------------------------------------ sheets

        private void Open(string titleKey, Action<VisualElement> fill)
        {
            Show(_menu, false);
            _drawerOpen = false;
            _sheetTitle.text = Kit.Caps(Strings.Get(titleKey));
            _sheetBody.Clear();
            _sheetRefresh = null;
            fill(_sheetBody);
            Show(_sheet, true);
            Refresh();
        }

        private void CloseSheet()
        {
            Show(_sheet, false);
            _sheetRefresh = null;
        }

        private void Reopen(Action<VisualElement> fill)
        {
            _sheetBody.Clear();
            fill(_sheetBody);
        }

        private void Quit()
        {
            SandboxSession.Scenario = _c.Editor.Scenario.Clone();
            MatchSettings.InMatch = false;
            Curtain.Close(Strings.Get("sandbox.title").ToUpperInvariant(), "", () => UnityEngine.SceneManagement.SceneManager.LoadScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene().buildIndex));
        }

        /// <summary>The screenshots' and layout checks' states: a panel open, a unit armed (the selection is the caller's).</summary>
        internal void Preview(string state)
        {
            switch (state)
            {
                case "sandbox-palette":
                    _drawerOpen = true;
                    var list = SandboxRules.Palette(_c.World.Catalog, _tab);
                    if (list.Count > 1) _c.Placing = list[1].Id;
                    _c.Formation = SandboxFormation.Line;
                    FillGrid();
                    break;
                case "sandbox-sheet":
                    Open("sandbox.settings", BattlePanel);
                    break;
                case "sandbox-run":
                    _trayOpen = true;
                    _bossOpen = true;
                    FillTray();
                    break;
            }
            Refresh();
        }

        public void Dispose()
        {
            if (_host != null) UnityEngine.Object.Destroy(_host);
            if (_settings != null) UnityEngine.Object.Destroy(_settings);
        }
    }
}
