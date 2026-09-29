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
    /// The Sandbox's screen (prompt 21 G) on the Field Command kit: the unit picker down the left (it folds away),
    /// the selection's panel down the right, the simulation's controls along the bottom, and pop-up panels for the
    /// battle's settings, the overlays, scenarios, the quick duel, the A/B comparison and the statistics. Every
    /// control is at least 44 pt; a wide screen (a tablet) gets wider panels. It has its own UI document above the
    /// battle HUD, so the HUD is left as it is.
    /// </summary>
    internal sealed partial class SandboxScreen
    {
        private readonly SandboxController _c;
        private readonly GameObject _host;
        private readonly PanelSettings _settings;
        private readonly VisualElement _root, _frame;
        private readonly VisualElement _left, _leftBody, _list, _right, _rightBody, _bottom, _popup, _popupBody, _status;
        private readonly Label _clock, _state;
        private readonly KitButton _runButton, _pauseButton;
        private readonly List<KitChip> _speedChips = new(), _sideChips = new(), _formationChips = new();
        private SandboxTab _tab;
        private string _search = "";
        private ArmyBranch? _branch;
        private int? _armour;
        private DamageType? _damage;
        private float _refreshIn;
        private Action _popupRefresh;

        public SandboxScreen(SandboxController controller)
        {
            _c = controller;
            _settings = ScriptableObject.CreateInstance<PanelSettings>();
            _settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
            _settings.scaleMode = PanelScaleMode.ConstantPixelSize;
            _settings.scale = BattleHud.MenuScale(Screen.width, Screen.height, Screen.dpi, Application.isMobilePlatform) * MatchSettings.UiScale;
            _settings.sortingOrder = 12;
            _host = new GameObject("Sandbox UI");
            var document = _host.AddComponent<UIDocument>();
            document.panelSettings = _settings;
            _root = document.rootVisualElement;
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
            _frame.RegisterCallback<GeometryChangedEvent>(_ => _frame.EnableInClassList("sb--wide", _frame.resolvedStyle.width > 1100f));

            // Left: the unit picker (B.2-B.5) ---------------------------------------------------------------
            _left = Kit.Box(KitPanel.SurfaceClass + " sb-left", PickingMode.Position);
            var head = Kit.Box("fc-row sb-left__head");
            head.Add(Kit.Text(Kit.Caps(Strings.Get("sandbox.units")), "fc-panel-title sb-grow"));
            head.Add(Small(Strings.Get("sandbox.hide"), ToggleLeft));
            _left.Add(head);
            _leftBody = Kit.Box("sb-left__body");
            var sides = Kit.Box("fc-row sb-wrap");
            for (var team = 0; team < 2; team++)
            {
                var t = team;
                var chip = new KitChip(Strings.Get("sandbox.side." + team), _c.Editor.Team == team, () => SetSide(t));
                chip.AddToClassList("sb-side sb-side--" + team);
                _sideChips.Add(chip);
                sides.Add(chip);
            }
            _leftBody.Add(sides);
            var tabs = Kit.Box("fc-row sb-wrap sb-tabs");
            foreach (SandboxTab tab in Enum.GetValues(typeof(SandboxTab)))
            {
                var tb = tab;
                tabs.Add(new KitChip(Strings.Get("sandbox.tab." + tab), tab == _tab, () =>
                {
                    _tab = tb;
                    foreach (var c in tabs.Children()) if (c is KitChip k) k.Selected = false;
                    ((KitChip)tabs[(int)tb]).Selected = true;
                    FillList();
                }));
            }
            _leftBody.Add(tabs);
            var search = new TextField { label = "" };
            search.AddToClassList("sb-field");
            search.textEdition.placeholder = Strings.Get("sandbox.search");
            search.RegisterValueChangedCallback(e =>
            {
                _search = e.newValue ?? "";
                FillList();
            });
            _leftBody.Add(search);
            _leftBody.Add(Filters());
            var listScroll = Kit.Scroll(ScrollViewMode.Vertical, "sb-list");
            _list = listScroll.contentContainer;
            _leftBody.Add(listScroll);
            _leftBody.Add(PlacementOptions());
            _left.Add(_leftBody);
            _frame.Add(_left);

            // Right: the selection (B.6, B.9, C.3, D) ------------------------------------------------------
            _right = Kit.Box(KitPanel.SurfaceClass + " sb-right", PickingMode.Position);
            var rightScroll = Kit.Scroll(ScrollViewMode.Vertical, "sb-right__scroll");
            _rightBody = rightScroll.contentContainer;
            _right.Add(rightScroll);
            _frame.Add(_right);

            // Bottom: the simulation (C.1, C.6) ------------------------------------------------------------
            _bottom = Kit.Box(KitPanel.SurfaceClass + " sb-bottom", PickingMode.Position);
            _runButton = new KitButton(ButtonTier.Primary, Strings.Get(_c.Editing ? "sandbox.run" : "sandbox.edit"), () => _c.Rebuild(_c.Editing), _c.Editing ? "play" : "restart");
            _bottom.Add(_runButton);
            _pauseButton = new KitButton(ButtonTier.Secondary, Strings.Get("sandbox.pause"), () =>
            {
                _c.Paused = !_c.Paused;
                Refresh();
            });
            _bottom.Add(_pauseButton);
            _bottom.Add(new KitButton(ButtonTier.Secondary, Strings.Get("sandbox.step"), () =>
            {
                _c.StepOnce();
                Refresh();
            }));
            var speeds = Kit.Box("fc-row sb-speeds");
            for (var i = 0; i < SandboxController.Speeds.Length; i++)
            {
                var index = i;
                var chip = new KitChip("×" + SandboxText.Number(SandboxController.Speeds[i], SandboxController.Speeds[i] < 1f ? 2 : 0), i == _c.SpeedIndex, () =>
                {
                    _c.SpeedIndex = index;
                    Refresh();
                });
                _speedChips.Add(chip);
                speeds.Add(chip);
            }
            _bottom.Add(speeds);
            _bottom.Add(new KitButton(ButtonTier.Secondary, Strings.Get("sandbox.reset"), () => _c.Rebuild(!_c.Editing), "restart"));
            var info = Kit.Box("sb-bottom__info");
            _state = Kit.Text("", "fc-small sb-state");
            _clock = Kit.Text("", "fc-small sb-clock");
            info.Add(_state);
            info.Add(_clock);
            _bottom.Add(info);
            var menus = Kit.Box("fc-row sb-wrap sb-menus");
            menus.Add(Small(Strings.Get("sandbox.settings"), () => Open(BattlePanel)));
            menus.Add(Small(Strings.Get("sandbox.layers"), () => Open(LayersPanel)));
            menus.Add(Small(Strings.Get("sandbox.scenarios"), () => Open(ScenariosPanel)));
            menus.Add(Small(Strings.Get("sandbox.duel"), () => Open(DuelPanel)));
            menus.Add(Small(Strings.Get("sandbox.ab"), () => Open(AbPanel)));
            menus.Add(Small(Strings.Get("sandbox.stats"), () => Open(StatsPanel)));
            menus.Add(Small(Strings.Get("sandbox.quit"), Quit));
            _bottom.Add(menus);
            _frame.Add(_bottom);

            _status = Kit.Box("sb-status");
            _frame.Add(_status);

            _popup = Kit.Box(KitPanel.SurfaceClass + " sb-popup", PickingMode.Position);
            var popupHead = Kit.Box("fc-row sb-popup__head");
            popupHead.Add(Kit.Box("sb-grow"));
            popupHead.Add(Small("✕", Close));
            _popup.Add(popupHead);
            var popupScroll = Kit.Scroll(ScrollViewMode.Vertical, "sb-popup__scroll");
            _popupBody = popupScroll.contentContainer;
            _popup.Add(popupScroll);
            _popup.style.display = DisplayStyle.None;
            _frame.Add(_popup);

            Kit.ApplyTextSize(_frame);
            FillList();
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

        private static VisualElement Small(string label, Action onTap)
        {
            var b = Kit.Tappable("sb-button", onTap);
            b.Add(Kit.Text(label, "fc-small sb-button__label"));
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

        private VisualElement Stepper(string text, Action down, Action up)
        {
            var row = Kit.Box("fc-row sb-stepper");
            row.Add(Small("−", () =>
            {
                down();
                Refresh();
            }));
            row.Add(Kit.Text(text, "fc-body sb-stepper__value"));
            row.Add(Small("+", () =>
            {
                up();
                Refresh();
            }));
            return row;
        }

        public void Toast(string text, bool error = false) => KitToast.Show(_frame, text, error ? ToastKind.Alert : ToastKind.Info, 3f);

        // ------------------------------------------------------------------ left: the picker

        private void ToggleLeft()
        {
            var open = !_left.ClassListContains("sb-left--closed");
            _left.EnableInClassList("sb-left--closed", open);
        }

        private void SetSide(int team)
        {
            _c.Editor.Team = team;
            for (var i = 0; i < _sideChips.Count; i++) _sideChips[i].Selected = i == team;
        }

        private VisualElement Filters()
        {
            var row = Kit.Box("fc-row sb-wrap sb-filters");
            var all = Strings.Get("sandbox.filter.all");
            var branches = new List<string> { all };
            foreach (ArmyBranch b in Enum.GetValues(typeof(ArmyBranch))) branches.Add(Strings.Get("kit.branch." + b.ToString().ToLowerInvariant()));
            row.Add(Drop(Strings.Get("sandbox.filter.branch"), branches, 0, i =>
            {
                _branch = i == 0 ? null : (ArmyBranch)(i - 1);
                FillList();
            }));
            var levels = new List<string> { all };
            for (var l = 0; l <= ArmourLevels.Max; l++) levels.Add(Strings.Get("armour.level." + l));
            row.Add(Drop(Strings.Get("sandbox.filter.armour"), levels, 0, i =>
            {
                _armour = i == 0 ? null : i - 1;
                FillList();
            }));
            var types = new List<string> { all };
            var typeValues = (DamageType[])Enum.GetValues(typeof(DamageType));
            foreach (var t in typeValues) types.Add(Strings.Get("dtype." + t));
            row.Add(Drop(Strings.Get("sandbox.filter.weapon"), types, 0, i =>
            {
                _damage = i == 0 ? null : typeValues[i - 1];
                FillList();
            }));
            return row;
        }

        private VisualElement PlacementOptions()
        {
            var box = Kit.Box("sb-place");
            box.Add(Caption("sandbox.formation"));
            var row = Kit.Box("fc-row sb-wrap");
            var shapes = new List<SandboxFormation?> { null, SandboxFormation.Line, SandboxFormation.Column, SandboxFormation.Cluster, SandboxFormation.Arc };
            foreach (var shape in shapes)
            {
                var s = shape;
                var chip = new KitChip(Strings.Get("sandbox.formation." + (shape?.ToString() ?? "Single")), _c.Formation == shape, () =>
                {
                    _c.Formation = s;
                    for (var i = 0; i < _formationChips.Count; i++) _formationChips[i].Selected = shapes[i] == s;
                });
                _formationChips.Add(chip);
                row.Add(chip);
            }
            box.Add(row);
            var countLabel = Kit.Text("", "fc-body sb-stepper__value");
            void ShowCount() => countLabel.text = SandboxText.Format("sandbox.count", ("count", _c.FormationCount));
            ShowCount();
            var stepper = Kit.Box("fc-row sb-stepper");
            stepper.Add(Small("−", () =>
            {
                _c.FormationCount = Math.Max(2, _c.FormationCount - 1);
                ShowCount();
            }));
            stepper.Add(countLabel);
            stepper.Add(Small("+", () =>
            {
                _c.FormationCount = Math.Min(16, _c.FormationCount + 1);
                ShowCount();
            }));
            box.Add(stepper);
            box.Add(new KitToggle(Strings.Get("sandbox.freeRotate"), _c.Editor.FreeRotation, on => _c.Editor.FreeRotation = on));
            box.Add(Kit.Text(Strings.Get("sandbox.place.hint"), "fc-small sb-hint"));
            return box;
        }

        private void FillList()
        {
            _list.Clear();
            var catalog = _c.World.Catalog;
            var list = SandboxRules.Palette(catalog, _tab, Strings.Unit, _search, _branch, _armour, _damage, def => _c.Session.Access.Allowed(catalog, def));
            if (list.Count == 0) _list.Add(Kit.Text(Strings.Get("sandbox.empty"), "fc-small sb-hint"));
            foreach (var def in list)
            {
                var id = def.Id;
                var row = Kit.Tappable("sb-unit" + (_c.Placing == id ? " sb-unit--armed" : ""), () =>
                {
                    _c.Placing = _c.Placing == id ? null : id;
                    _c.Picking = SandboxController.Pick.None;
                    FillList();
                });
                row.Add(KitCombat.ArmourIcon(def.Armour.Front, CombatFacts.KindOf(def.Kind)));
                row.Add(Kit.Text(Strings.Short(id), "fc-body sb-unit__name"));
                if (def.CpCost > 0) row.Add(Kit.Text(SandboxText.Format("sandbox.cp.value", ("cp", def.CpCost)), "fc-small sb-unit__cost"));
                row.tooltip = Strings.Unit(id);
                // Play-test 6 (DECISIONS 21B): a boss's file, the menu's boss page as a dialog (no menu in a battle).
                if (def.Boss)
                {
                    var boss = def;
                    row.Add(new KitIconButton("info", Strings.Get("guide.boss.fileButton"), () => BossFile.Show(_root, catalog, boss), plain: true));
                }
                _list.Add(row);
            }
        }

        // ------------------------------------------------------------------ every frame

        public void Tick()
        {
            RunJobs();
            var w = _c.World;
            _state.text = Strings.Get(_c.Editing ? "sandbox.editing" : _c.Paused ? "sandbox.paused" : "sandbox.running");
            _clock.text = SandboxText.Format("sandbox.clock", ("seconds", SandboxText.Number(w.Time, 1)), ("tick", w.Tick));
            _refreshIn -= Time.unscaledDeltaTime;
            if (!_c.Editing && _refreshIn <= 0f)
            {
                _refreshIn = 0.5f;
                FillRight();
                ShowResult();
                _popupRefresh?.Invoke();
            }
        }

        /// <summary>Everything that depends on the selection and the state.</summary>
        public void Refresh()
        {
            _runButton.Label = Strings.Get(_c.Editing ? "sandbox.run" : "sandbox.edit");
            _pauseButton.Label = Strings.Get(_c.Paused ? "sandbox.resume" : "sandbox.pause");
            _pauseButton.EnableInClassList("sb-hidden", _c.Editing);
            for (var i = 0; i < _speedChips.Count; i++) _speedChips[i].Selected = i == _c.SpeedIndex;
            _left.EnableInClassList("sb-hidden", !_c.Editing);
            FillRight();
            ShowResult();
        }

        private void ShowResult()
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
            _status.Add(Kit.Text(text, "fc-body sb-status__text"));
        }

        internal static string ResultLine(int winner, double seconds, float blue, float red) =>
            SandboxText.Format("sandbox.result.line",
                ("result", Strings.Get(winner == 0 ? "sandbox.result.0" : winner == 1 ? "sandbox.result.1" : winner == -1 ? "sandbox.result.draw" : "sandbox.result.open")),
                ("seconds", SandboxText.Number(seconds, 1)), ("blue", SandboxText.Number(blue * 100f)), ("red", SandboxText.Number(red * 100f)));

        // ------------------------------------------------------------------ right: the selection

        private void FillRight()
        {
            _rightBody.Clear();
            var sel = _c.Selected;
            if (sel.Count == 0)
            {
                _rightBody.Add(Kit.Text(Strings.Get("sandbox.none"), "fc-small sb-hint"));
                if (_c.Editing) _rightBody.Add(Row(Small(Strings.Get("sandbox.undo"), () => _c.Editor.Undo()), Small(Strings.Get("sandbox.redo"), () => _c.Editor.Redo())));
                else SideTools();
                return;
            }
            if (_c.Editing) EditingPanel(sel);
            else RunningPanel();
        }

        private void EditingPanel(List<int> sel)
        {
            var e = _c.Editor;
            var catalog = _c.World.Catalog;
            var first = e.Units[sel[0]];
            catalog.Vehicles.TryGetValue(first.Def, out var def);
            _rightBody.Add(Kit.Text(Kit.Caps(Strings.Unit(first.Def)), "fc-panel-title"));
            _rightBody.Add(Kit.Text(SandboxText.Format("sandbox.selected", ("count", sel.Count)) + " · " + Strings.Get("sandbox.side." + first.Team) + " · " +
                SandboxText.Format("sandbox.heading", ("degrees", SandboxText.Number(first.Heading, e.FreeRotation ? 1 : 0))), "fc-small"));
            _rightBody.Add(Row(Small(Strings.Get("sandbox.turnLeft"), () => e.RotateBy(sel, -SandboxRules.RotationStep)),
                Small(Strings.Get("sandbox.turnRight"), () => e.RotateBy(sel, SandboxRules.RotationStep))));
            _rightBody.Add(Row(Small(Strings.Get("sandbox.side.0"), () => e.Edit(sel, u => u.Team = 0)), Small(Strings.Get("sandbox.side.1"), () => e.Edit(sel, u => u.Team = 1))));
            _rightBody.Add(Stepper(SandboxText.Format("sandbox.rank", ("rank", first.Rank)), () => e.Edit(sel, u => u.Rank--), () => e.Edit(sel, u => u.Rank++)));
            if (def != null && SandboxRules.IsTower(def))
            {
                _rightBody.Add(Caption("sandbox.branch"));
                var tower = def.BranchOf ?? def.Id;
                var branches = SandboxRules.Branches(catalog, tower);
                if (branches.Count > 0)
                {
                    if (first.Rank < SandboxRules.BranchRank) _rightBody.Add(Kit.Text(Strings.Get("sandbox.branch.locked"), "fc-small sb-hint"));
                    else
                    {
                        var row = Row(new KitChip(Strings.Get("sandbox.branch.none"), def.BranchOf == null, () => e.SetBranch(sel[0], null)));
                        foreach (var b in branches)
                        {
                            var id = b;
                            row.Add(new KitChip(Strings.Branch(b), first.Def == b, () =>
                            {
                                if (!e.SetBranch(sel[0], id)) Toast(Strings.Get("sandbox.refuse.Locked"), true);
                            }));
                        }
                        _rightBody.Add(row);
                    }
                }
            }
            _rightBody.Add(Caption("sandbox.gear"));
            var gears = Row();
            foreach (SandboxGear g in Enum.GetValues(typeof(SandboxGear)))
            {
                var gear = g;
                gears.Add(new KitChip(Strings.Get("sandbox.gear." + g), first.Gear == g, () => e.Edit(sel, u => u.Gear = gear)));
            }
            _rightBody.Add(gears);
            if (def != null && catalog.EliteVariant(def.Id) != null)
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.elite"), first.Elite, on => e.Edit(sel, u => u.Elite = on)));
            _rightBody.Add(Stepper(SandboxText.Format("sandbox.hp", ("percent", first.Hp)), () => e.Edit(sel, u => u.Hp -= 10), () => e.Edit(sel, u => u.Hp += 10)));
            _rightBody.Add(Stepper(SandboxText.Format("sandbox.ammo", ("percent", first.Ammo)), () => e.Edit(sel, u => u.Ammo -= 10), () => e.Edit(sel, u => u.Ammo += 10)));
            _rightBody.Add(new KitToggle(Strings.Get("sandbox.immortal"), first.Immortal, on => e.Edit(sel, u => u.Immortal = on)));
            if (def is { Tiers: not null })
            {
                _rightBody.Add(Caption("sandbox.tier"));
                _rightBody.Add(Row(new KitChip(Strings.Get("sandbox.tier.none"), first.Tier == "", () => e.Edit(sel, u => u.Tier = "")),
                    new KitChip(Strings.Get("sandbox.tier.low"), first.Tier == "low", () => e.Edit(sel, u => u.Tier = "low")),
                    new KitChip(Strings.Get("sandbox.tier.high"), first.Tier == "high", () => e.Edit(sel, u => u.Tier = "high"))));
            }
            if (def is { Boss: true } && first.Boss is { } boss)
            {
                _rightBody.Add(Caption("sandbox.boss"));
                var phases = Math.Max(def.Phases.Count, def.Tiers?.Marks.Count ?? 0) + 1;
                var row = Row();
                for (var p = 0; p < Math.Min(3, phases); p++)
                {
                    var ph = p;
                    row.Add(new KitChip(SandboxText.Format("sandbox.boss.phase", ("phase", p + 1)), boss.Phase == p, () => e.Edit(sel, u => (u.Boss ??= new SandboxBossState()).Phase = ph)));
                }
                _rightBody.Add(row);
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.boss.bigOff"), boss.BigOff, on => e.Edit(sel, u => (u.Boss ??= new SandboxBossState()).BigOff = on)));
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.boss.escorts"), !boss.NoEscorts, on => e.Edit(sel, u => (u.Boss ??= new SandboxBossState()).NoEscorts = !on)));
                for (var i = 0; i < def.Parts.Count; i++)
                {
                    var part = i;
                    var broken = boss.Broken.Contains(i);
                    _rightBody.Add(new KitToggle(SandboxText.Format("sandbox.boss.break", ("part", Strings.Get("part." + def.Parts[i].Kind))), broken, on => e.Edit(sel, u =>
                    {
                        var b = u.Boss ??= new SandboxBossState();
                        b.Broken.Remove(part);
                        if (on) b.Broken.Add(part);
                    })));
                }
            }
            _rightBody.Add(Row(Small(Strings.Get("sandbox.move"), () =>
                {
                    _c.Placing = null;
                    _c.Picking = SandboxController.Pick.MoveUnits;
                    FillList();
                    ShowResult();
                }),
                Small(Strings.Get("sandbox.copy"), () =>
                {
                    var copies = e.Copy(sel, new System.Numerics.Vector2(6f, -6f));
                    sel.Clear();
                    sel.AddRange(copies);
                    Refresh();
                }),
                Small(Strings.Get("sandbox.delete"), () =>
                {
                    e.Delete(new List<int>(sel));
                    sel.Clear();
                    Refresh();
                })));
            _rightBody.Add(Row(Small(Strings.Get("sandbox.undo"), () => e.Undo()), Small(Strings.Get("sandbox.redo"), () => e.Redo())));
        }

        private void RunningPanel()
        {
            var vehicles = new List<Vehicle>(_c.SelectedVehicles());
            if (vehicles.Count == 0) return;
            var first = vehicles[0];
            _rightBody.Add(Kit.Text(Kit.Caps(Strings.Unit(first.Def.Id)), "fc-panel-title"));
            _rightBody.Add(Kit.Text(SandboxText.Format("sandbox.selected", ("count", vehicles.Count)) + " · " + Strings.Get("sandbox.side." + first.Team) + " · " +
                SandboxText.Format("sandbox.hp", ("percent", SandboxText.Number(first.Hp / Mathf.Max(1f, first.MaxHp) * 100f))), "fc-small"));
            var ids = _c.Selected.ToArray();
            _rightBody.Add(Row(Small(Strings.Get("sandbox.order.move"), () =>
                {
                    _c.Picking = SandboxController.Pick.OrderMove;
                    ShowResult();
                }),
                Small(Strings.Get("sandbox.order.fire"), () =>
                {
                    _c.Picking = SandboxController.Pick.OrderTarget;
                    ShowResult();
                })));
            _rightBody.Add(Row(Small(Strings.Get("sandbox.order.hold"), () => _c.Queue(SandboxOp.For(SandboxOpKind.Hold, ids))),
                Small(Strings.Get("sandbox.order.release"), () => _c.Queue(SandboxOp.For(SandboxOpKind.Release, ids)))));
            _rightBody.Add(new KitToggle(Strings.Get("sandbox.order.holdFire"), first.HoldFire, on => _c.Queue(SandboxOp.For(SandboxOpKind.HoldFire, ids, on ? 1 : 0))));
            _rightBody.Add(new KitToggle(Strings.Get("sandbox.immortal"), _c.Battle.IsImmortal(first.Id.Value), on => _c.Queue(SandboxOp.For(SandboxOpKind.Immortal, ids, on ? 1 : 0))));
            if (first.Def.Boss) BossTools(first);
        }

        /// <summary>D: the boss tools on a running boss.</summary>
        private void BossTools(Vehicle boss)
        {
            var id = boss.Id.Value;
            var def = boss.Def;
            _rightBody.Add(Caption("sandbox.boss"));
            _rightBody.Add(Small(Strings.Get("guide.boss.fileButton"), () => BossFile.Show(_root, _c.World.Catalog, def)));
            var phases = Math.Max(def.Phases.Count, def.Tiers?.Marks.Count ?? 0) + 1;
            var row = Row();
            for (var p = 1; p < Math.Min(3, phases); p++)
            {
                var ph = p;
                row.Add(Small(SandboxText.Format("sandbox.boss.phase", ("phase", p + 1)), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossPhase, id, ph))));
            }
            _rightBody.Add(row);
            if (boss.BigAttack is { } big)
            {
                _rightBody.Add(Small(Strings.Get("sandbox.boss.big"), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossBig, id))));
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.boss.bigOff"), big.Off, on => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossBigOff, id, on ? 1 : 0))));
            }
            for (var i = 0; i < boss.PartCount; i++)
            {
                var part = i;
                var name = Strings.Get("part." + def.Parts[i].Kind);
                _rightBody.Add(boss.IsPartBroken(i)
                    ? Small(SandboxText.Format("sandbox.boss.restore", ("part", name)), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossRestore, id, part)))
                    : Small(SandboxText.Format("sandbox.boss.break", ("part", name)), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossBreak, id, part))));
            }
            if (def.Tiers != null)
                _rightBody.Add(Row(Small(Strings.Get("sandbox.boss.low"), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossTier, id, 1))),
                    Small(Strings.Get("sandbox.boss.high"), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossTier, id, 2)))));
            _rightBody.Add(Row(Small(Strings.Get("sandbox.boss.escorts") + " · " + Strings.Get("kit.on"), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossEscorts, id, 1))),
                Small(Strings.Get("sandbox.boss.escorts") + " · " + Strings.Get("kit.off"), () => _c.Queue(SandboxOp.Boss(SandboxOpKind.BossEscorts, id, 0)))));
            if (def.MiniVariant != null || def.VariantOf != null)
                _rightBody.Add(Small(Strings.Get("sandbox.boss.swap"), () =>
                {
                    _c.Queue(SandboxOp.Boss(SandboxOpKind.BossSwap, id));
                    _c.Selected.Clear();
                }));
            _rightBody.Add(Caption("sandbox.boss.difficulty"));
            var diffs = Row();
            foreach (var d in Difficulties)
            {
                var key = d;
                diffs.Add(Small(Strings.Get("sandbox.diff." + d), () => _c.Queue(new SandboxOp { Kind = SandboxOpKind.Difficulty, Text = key })));
            }
            _rightBody.Add(diffs);
        }

        internal static readonly string[] Difficulties = { "Easy", "Normal", "Hard", "Heroic", "Iron" };

        /// <summary>C.4-C.5 while running with nothing selected: each side's CP, cooldowns, immortality and a support to call.</summary>
        private void SideTools()
        {
            for (var team = 0; team < 2; team++)
            {
                var t = team;
                _rightBody.Add(Kit.Text(Kit.Caps(Strings.Get("sandbox.side." + team)), "fc-caption sb-caption sb-side--" + team));
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.cp.unlimited"), _c.Battle.Unlimited(team), on => _c.Queue(SandboxOp.Side(SandboxOpKind.SideCp, t, on ? -1 : 20))));
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.cooldowns"), _c.Battle.CooldownsOn(team), on => _c.Queue(SandboxOp.Side(SandboxOpKind.Cooldowns, t, on ? 1 : 0))));
                _rightBody.Add(new KitToggle(Strings.Get("sandbox.sideImmortal"), _c.Battle.SideImmortal(team), on => _c.Queue(SandboxOp.Side(SandboxOpKind.SideImmortal, t, on ? 1 : 0))));
                if (_c.World.TryGetEconomy(team, out var economy) && economy.Supports.Count > 0)
                {
                    var row = Row();
                    foreach (var s in economy.Supports)
                    {
                        var support = s;
                        row.Add(Small(Strings.Support(s), () =>
                        {
                            _c.Strike = support;
                            _c.StrikeTeam = t;
                            _c.Picking = SandboxController.Pick.Strike;
                            ShowResult();
                        }));
                    }
                    _rightBody.Add(Caption("sandbox.call"));
                    _rightBody.Add(row);
                }
            }
        }

        // ------------------------------------------------------------------ pop-ups

        private void Open(Action<VisualElement> fill)
        {
            _popupBody.Clear();
            _popupRefresh = null;
            fill(_popupBody);
            _popup.style.display = DisplayStyle.Flex;
        }

        private void Close()
        {
            _popup.style.display = DisplayStyle.None;
            _popupRefresh = null;
        }

        private void Reopen(Action<VisualElement> fill)
        {
            _popupBody.Clear();
            fill(_popupBody);
        }

        private void Quit()
        {
            SandboxSession.Scenario = _c.Editor.Scenario.Clone();
            MatchSettings.InMatch = false;
            Curtain.Close(Strings.Get("sandbox.title").ToUpperInvariant(), "", () => UnityEngine.SceneManagement.SceneManager.LoadScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene().buildIndex));
        }

        public void Dispose()
        {
            if (_host != null) UnityEngine.Object.Destroy(_host);
            if (_settings != null) UnityEngine.Object.Destroy(_settings);
        }
    }
}
