using System;
using System.Collections.Generic;
using MachineBrigade.Game.Input;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UIElements;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Hud
{
    public enum HudMode
    {
        /// <summary>Main menu over an AI battle; no battle controls.</summary>
        Menu,

        /// <summary>Both sides' score as bars round the objective chips (Conquest, Deathmatch, King of the Hill, Assault).</summary>
        Score,

        /// <summary>Army, enemies, wave and the next wave's countdown (Survival).</summary>
        Waves,

        /// <summary>A campaign mission's objective, clock and boss.</summary>
        Mission,
    }

    /// <summary>
    /// The battle HUD, built with UI Toolkit on the Field Command 2.0 kit (Tokens.uss, Screens.uss):
    /// the minimap and its tools top left, the score (or the mission, or the waves) top centre with the
    /// boss, the fortress pieces and the notices under it, pause top right, the commander's controls
    /// down the right, the deck along the bottom and the selection's orders just above it. Buttons keep
    /// fixed size and position in every state (V2 R09).
    /// <para>
    /// Two layouts share the code (prompt 11 A): the compact HUD (Settings: Compact battle HUD, on by
    /// default; the root carries <see cref="CompactClass"/>), which keeps the battlefield clear (a
    /// smaller minimap, icon toggles, a lower tray with short names, a collapsible boss bar, one strip
    /// for the objective and the clock, small notices at the top), and the full HUD of prompt 10 G.
    /// Every control stays a full touch target in both: where a face is smaller than 44 pt, an invisible
    /// target of 44 pt surrounds it.
    /// </para>
    /// <para>
    /// Slots for later additions (documented for the balance agent, prompt 13): the ammo icons of the
    /// selection go in <see cref="SelectionExtras"/> (a row under the health bar, empty and hidden until
    /// something is added); a card's extra badge goes in DeckBar's <c>fc-hcard__badges</c> row.
    /// </para>
    /// </summary>
    public sealed class BattleHud : IDisposable
    {
        /// <summary>The class on the HUD's kit root while the compact layout is in use.</summary>
        public const string CompactClass = "fc-hud--compact";

        private readonly GameObject _host;
        private readonly GameObject _eventSystem;
        private readonly PanelSettings _settings;
        private readonly VisualElement _root;
        private readonly VisualElement _safe;
        private readonly Label _allies, _enemies, _wave, _next, _fps;
        private readonly IconElement _portraitIcon;
        private readonly Label _unitName, _selectedCount, _hpText;
        private readonly VisualElement _hpFill;
        private readonly VisualElement _attackMove;
        private readonly VisualElement _boxTool;
        private readonly VisualElement _toast;
        private readonly Label _toastText;
        private readonly Label _hint;
        private readonly VisualElement _hintBar;
        private readonly VisualElement _selectionBox;
        private readonly VisualElement _targeting;
        private readonly Label _targetingText;
        private readonly VisualElement _banner;
        private readonly ScoreBar _score;
        private readonly MissionBar _missionBar;
        private readonly BossBar _boss;
        private readonly SuperGunTimer _superGun;
        private readonly WavePreview _wavePreview;
        private readonly VisualElement _attackStance, _defendStance;
        private readonly KitToggle _autoDeploy, _autoStrike;
        private readonly KitButton _towerButton;
        private readonly VisualElement _stanceSwitch;
        private readonly HudIconToggle _buyToggle, _supportToggle;
        private readonly VisualElement _towerMini;
        private readonly Label _towerMiniText;
        private readonly VisualElement _portrait;
        private readonly DeckBar _deck;
        private readonly ResultPanel _result;
        private readonly PausePanel _pause;
        private readonly MenuScreen _menu;
        private readonly string _autoHint = "hint.auto";
        private float _toastUntil, _bannerUntil;
        private bool _attackArmed, _boxMode, _defending;
        private Rect _appliedSafeArea;

        public BattleHud(HudSpec spec, IReadOnlyList<CardInfo> cards, Catalog catalog) : this(spec, cards, catalog, null)
        {
        }

        /// <summary>
        /// The HUD built into <paramref name="root"/> instead of a UIDocument of its own (the screenshot
        /// tool and the UI checks lay it out in their own panels); null makes the document.
        /// </summary>
        internal BattleHud(HudSpec spec, IReadOnlyList<CardInfo> cards, Catalog catalog, VisualElement root)
        {
            var mode = spec.Mode;
            Mode = mode;
            Catalog = catalog;
            if (root != null) _root = root;
            else
            {
                if (EventSystem.current == null)
                    _eventSystem = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));

                _settings = ScriptableObject.CreateInstance<PanelSettings>();
                _settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
                _settings.referenceResolution = new Vector2Int(1280, 720);
                _settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
                _menuPanel = mode == HudMode.Menu;
                ApplyScale();
                _settings.sortingOrder = 10;

                _host = new GameObject("HUD");
                var document = _host.AddComponent<UIDocument>();
                document.panelSettings = _settings;
                _root = document.rootVisualElement;
            }
            if (Match.DebugFlags.Has("-mb-no-hud")) _root.style.display = DisplayStyle.None;
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            // The screens' sheet after the old HUD sheet. It is not in the theme: UI Toolkit counts every sheet
            // a theme imports as a default sheet, which loses to any other sheet whatever its selectors, so the
            // screens could not restyle an old class there (Field Command 2.0, DECISIONS 10).
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
            _root.pickingMode = PickingMode.Ignore;
            // Colour-blind safe teams re-tint every ally and enemy colour in the styles.
            _root.EnableInClassList("cb", Match.MatchSettings.ColorBlind);

            // The flash of a huge blast: a warm wash over the battlefield, under every control.
            _flash = Kit.Box("fc-hud-flash");
            _flash.style.opacity = 0f;
            _root.Add(_flash);
            // Equipment proc words over vehicles, under every control.
            if (mode != HudMode.Menu) _words = new TraitWords(_root);

            Compact = mode != HudMode.Menu && (spec.Compact ?? Match.MatchSettings.CompactHud);
            var hud = UiKit.Box("hud");
            // The battle's controls are a kit root (Field Command 2.0, G): the kit's fonts, sizes and text size.
            if (mode != HudMode.Menu) hud = Kit.Root("hud fc-hud" + (Compact ? " " + CompactClass : ""));
            _root.Add(hud);
            _safe = UiKit.Box("safe");
            hud.Add(_safe);

            if (mode == HudMode.Menu)
            {
                _menu = new MenuScreen(catalog, () => PlayPressed?.Invoke());
                _menu.SettingsChanged += () => SettingsChanged?.Invoke();
                _menu.VolumeChanged += () => VolumeChanged?.Invoke();
                _menu.SkinPreviewed += id => SkinPreviewed?.Invoke(id);
                // The menu's opaque backdrop spans the whole screen, the notch's side too; its pages sit in the safe area.
                hud.Insert(0, _menu.Backdrop);
                _safe.Add(_menu.Root);
                _toast = UiKit.Box("toast");
                _toastText = UiKit.Text("", "toast-text");
                _selectionBox = UiKit.Box("selection-box");
                return;
            }

            // Top: the score (or the mission, or the waves) in the middle, pause in the corner ----------------
            // Compact: one low strip with the objective and the clock together (prompt 11 A5).
            var top = Kit.Box("fc-hud__top");
            if (mode == HudMode.Score)
            {
                _score = new ScoreBar(spec.ScoreLabel, Compact);
                top.Add(_score.Root);
            }
            else if (mode == HudMode.Mission)
            {
                _missionBar = new MissionBar(Compact);
                _missionBar.PointPressed += id => PointPressed?.Invoke(id);
                top.Add(_missionBar.Root);
            }
            else
            {
                var stats = Kit.Box(Compact ? KitPanel.SurfaceClass + " fc-surface--field fc-hud__stats" : "fc-hud__stats");
                _allies = Stat(stats, "tank", Strings.Get("stat.allies"), "fc-hud__stat--ours", Compact);
                _enemies = Stat(stats, "crosshair", Strings.Get("stat.enemies"), "fc-hud__stat--theirs", Compact);
                _wave = Stat(stats, "flag", Strings.Get("stat.wave"), null, Compact);
                _next = Stat(stats, "bolt", Strings.Get("stat.next"), null, Compact);
                if (spec.Sandbox)
                {
                    HideStat(_wave);
                    HideStat(_next);
                }
                top.Add(stats);
            }
            _safe.Add(top);

            var corner = Kit.Box("fc-hud__corner");
            _corner = corner;
            _fps = Kit.Text("", "fc-small fc-hud__fps");
            corner.Add(_fps);
            corner.Add(new KitIconButton("pause", Strings.Get("pause.title"), () => PausePressed?.Invoke(), plain: Compact));
            _safe.Add(corner);

            // Under the top bar: the boss, then the fortress modes' set pieces (the super-gun's countdown, the next wave).
            var under = Kit.Box("fc-hud__under");
            if (mode == HudMode.Mission)
            {
                _boss = new BossBar(Compact);
                _boss.Parts.Tapped += (boss, part) => BossPartTapped?.Invoke(boss, part);
                // Play-test 6: the compact bar shares the top row with the goal (or the bosses destroyed count), smaller.
                (Compact ? top : under).Add(_boss.Root);
                var fortress = UiKit.Box("fortress-panel");
                _superGun = new SuperGunTimer();
                fortress.Add(_superGun.Root);
                _wavePreview = new WavePreview(DescribeVehicle);
                fortress.Add(_wavePreview.Root);
                under.Add(fortress);
                // Prompt 20 N: the Boss Hunt's rest between bosses.
                _huntRest = new HuntRestPanel();
                under.Add(_huntRest.Root);
            }
            _safe.Add(under);

            // Left column: the minimap and the map tools ---------------------------------------------
            // Compact: a smaller minimap, select-all and box-select as small icons on its right-hand corners (prompt 11 A1),
            // and beside them zoom in and out (play-test 6: the owner looked for them; pinch and the wheel zoom too).
            var left = Kit.Box("fc-hud__left");
            Minimap = new Minimap();
            Minimap.Clicked += p => MinimapClicked?.Invoke(p);
            left.Add(Minimap);
            var tools = Kit.Box("fc-hud__tools");
            _boxTool = new KitIconButton("expand", Strings.Get("hud.boxSelect"), () => BoxModeToggled?.Invoke(), plain: Compact);
            if (!spec.Sandbox)
            {
                tools.Add(new KitIconButton("people", Strings.Get("hud.selectAll"), () => SelectAllPressed?.Invoke(), plain: Compact));
                tools.Add(_boxTool);
            }
            tools.Add(new KitIconButton("plus", Strings.Get("hud.zoomIn"), () => ZoomPressed?.Invoke(1.25f), plain: Compact) { name = "zoom-in" });
            tools.Add(new KitIconButton("minus", Strings.Get("hud.zoomOut"), () => ZoomPressed?.Invoke(0.8f), plain: Compact) { name = "zoom-out" });
            left.Add(tools);
            _safe.Add(left);

            // Commander: the army fights on its own; the player sets intent ---------------------------------
            if (Compact)
            {
                // One small switch for Attack / Defend (icons only), and Auto buy and Support as icon toggles
                // (prompt 11 A2); the rail itself lets taps through to the battlefield between them.
                var rail = Kit.Box("fc-hud__rail");
                _stanceSwitch = Kit.Tappable("fc-hud__switch", () => StancePressed?.Invoke(!_defending));
                _stanceSwitch.tooltip = Strings.Get("rail.stance");
                var face = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__switch-face");
                var attackHalf = Kit.Box("fc-hud__switch-half fc-hud__switch-half--attack");
                attackHalf.Add(Kit.Icon("attack"));
                face.Add(attackHalf);
                var defendHalf = Kit.Box("fc-hud__switch-half fc-hud__switch-half--defend");
                defendHalf.Add(Kit.Icon("shield"));
                face.Add(defendHalf);
                _stanceSwitch.Add(face);
                rail.Add(_stanceSwitch);
                _buyToggle = new HudIconToggle("cart", "rail.buyOn", "rail.buyOff", () => AutoDeployToggled?.Invoke());
                rail.Add(_buyToggle);
                _supportToggle = new HudIconToggle("airstrike", "rail.supportOn", "rail.supportOff", () => AutoStrikeToggled?.Invoke());
                rail.Add(_supportToggle);
                // Destroyed towers can be flown back in: shown only while one can.
                _towerMini = Kit.Tappable("fc-hud__tool fc-hud__tower-mini", () => TowerPressed?.Invoke());
                var towerFace = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__tool-face");
                towerFace.Add(Kit.Icon("tower"));
                _towerMiniText = Kit.Text("", "fc-number-small fc-hud__tool-text");
                towerFace.Add(_towerMiniText);
                _towerMini.Add(towerFace);
                _towerMini.style.display = DisplayStyle.None;
                rail.Add(_towerMini);
                if (!spec.Sandbox) _safe.Add(rail);
            }
            else
            {
                // Attack / Defend with their full names (the one on is the text colour with dark text), then
                // Auto buy and Support as the kit's on/off switches.
                var commander = Kit.Box("fc-hud__rail", PickingMode.Position);
                var stance = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__group");
                _attackStance = Stance(stance, "attack", Strings.Get("rail.attack"), () => StancePressed?.Invoke(false));
                _defendStance = Stance(stance, "shield", Strings.Get("rail.defend"), () => StancePressed?.Invoke(true));
                commander.Add(stance);
                var autos = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__group fc-hud__switches");
                _autoDeploy = new KitToggle(Strings.Get("rail.buy"), false, _ => AutoDeployToggled?.Invoke());
                autos.Add(_autoDeploy);
                _autoStrike = new KitToggle(Strings.Get("rail.support"), false, _ => AutoStrikeToggled?.Invoke());
                autos.Add(_autoStrike);
                commander.Add(autos);
                // Destroyed towers can be flown back in: shown only while one can.
                _towerButton = new KitButton(ButtonTier.Secondary, Strings.Get("rail.tower"), () => TowerPressed?.Invoke(), "reinforce");
                _towerButton.AddToClassList("fc-hud__tower");
                _towerButton.style.display = DisplayStyle.None;
                commander.Add(_towerButton);
                if (!spec.Sandbox) _safe.Add(commander);
            }
            if (_score != null) _score.PointPressed += id => PointPressed?.Invoke(id);

            // Selection (hand orders for selected vehicles) --------------------------------------------------
            // Compact: the picture with the count on it, the name, the health, and Advance / Stop / Back, in one
            // low strip just above the deck (prompt 11 A8); the weapons and counters are on the detail page.
            var command = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__command", PickingMode.Position);
            _command = command;
            _selectedCount = Kit.Text("", "fc-caption fc-hud__count");
            if (!Compact)
            {
                var header = Kit.Box("fc-hud__command-head");
                header.Add(Kit.Caption(Strings.Get("panel.selection")));
                header.Add(_selectedCount);
                command.Add(header);
            }

            var details = Kit.Box("fc-hud__details");
            _portrait = Kit.Box("fc-hud__portrait");
            _portraitIcon = Kit.Icon("tank", "fc-hud__portrait-icon");
            _portrait.Add(_portraitIcon);
            if (Compact) _portrait.Add(_selectedCount);
            details.Add(_portrait);
            var detailsText = Kit.Box("fc-hud__details-text");
            _unitName = Kit.Text("", (Compact ? "fc-caption fc-hud__name" : "fc-panel-title") + " fc-row-text");
            detailsText.Add(_unitName);
            var track = Kit.Box("fc-hud__hp");
            _hpFill = Kit.Box("fc-hud__hp-fill");
            track.Add(_hpFill);
            detailsText.Add(track);
            _hpText = Kit.Text("", "fc-small");
            detailsText.Add(_hpText);
            SelectionExtras = Kit.Box("fc-row fc-hud__extras");
            SelectionExtras.style.display = DisplayStyle.None;
            detailsText.Add(SelectionExtras);
            details.Add(detailsText);
            // Prompt 15 E4: the armour and the weapons' chips beside the health bar; a tap says them in words.
            _combat = Kit.Box("fc-hud__combat");
            KitCombat.TapTip(_combat, () => _combatFor != null ? Strings.Unit(_combatFor) : "",
                () => _combatFor != null && Catalog != null && Catalog.Vehicles.TryGetValue(_combatFor, out var shown) ? KitCombat.RowTip(shown) : "");
            details.Add(_combat);
            command.Add(details);
            if (!Compact)
            {
                _weapons = Kit.Box("fc-row fc-row--wrap fc-hud__weapons");
                command.Add(_weapons);
                _counterText = Kit.Text("", "fc-small fc-hud__counter");
                command.Add(_counterText);
            }

            var buttons = Kit.Box("fc-hud__orders");
            _attackMove = Order(buttons, "crosshair", Strings.Get("cmd.attackShort"), () => AttackMovePressed?.Invoke());
            Order(buttons, "stop", Strings.Get("cmd.stopShort"), () => StopPressed?.Invoke());
            Order(buttons, "retreat", Strings.Get("cmd.retreatShort"), () => RetreatPressed?.Invoke());
            (Compact ? details : command).Add(buttons);
            // Play-test 6: a close mark over the panel's corner lets the group go (a tap on a selected unit does the same;
            // a tap on the ground stays a move order). Over the corner, so the panel does not grow over the battlefield.
            var deselect = new KitIconButton("close", Strings.Get("cmd.deselectShort"), () => DeselectPressed?.Invoke(), plain: true) { name = "deselect" };
            deselect.AddToClassList("fc-hud__deselect");
            command.Add(deselect);
            _safe.Add(command);

            // Deck -------------------------------------------------------------------------------------------
            if (cards != null && cards.Count > 0)
            {
                _deck = new DeckBar(cards, Compact);
                _deck.TipRow = id => Catalog != null && Catalog.Vehicles.TryGetValue(id, out var held) ? KitCombat.Row(held, 4) : null;
                _deck.CardPressed += i => CardPressed?.Invoke(i);
                _deck.CpTapped += () => Toast(Strings.Get("hud.cpInfo"), seconds: 5f);
                _safe.Add(_deck.Root);
            }

            // Overlays -----------------------------------------------------------------------------------------
            _autoHint = spec.HintKey;
            _hint = Kit.Text(Strings.Get(_autoHint), "fc-small fc-row-text");
            // The standing hint is for the first moments of a player's first few matches only (prompt 11 A7);
            // mode hints (attack-move, box select) bring it back while they are active.
            var startHint = !spec.Sandbox && (spec.StartHint ?? Match.MatchSettings.ShowStartHint);
            _hintUntil = startHint ? Time.unscaledTime + 9f : -1f;
            _hintBar = Kit.Box("fc-hud__hint");
            var hintFace = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__hint-face");
            hintFace.Add(_hint);
            _hintBar.Add(hintFace);
            _hintBar.EnableInClassList("fc-hud__hint--gone", !startHint);
            _safe.Add(_hintBar);

            _targeting = Kit.Box("fc-hud__targeting", PickingMode.Ignore);
            var targetFace = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__targeting-face", PickingMode.Position);
            targetFace.Add(Kit.Icon("crosshair", "fc-hud__targeting-icon"));
            _targetingText = Kit.Text("", "fc-body fc-row-text");
            targetFace.Add(_targetingText);
            targetFace.Add(new KitButton(ButtonTier.Secondary, Strings.Get("target.cancel"), () => TargetCancelled?.Invoke(), "close"));
            _targeting.Add(targetFace);
            _targeting.style.display = DisplayStyle.None;
            _safe.Add(_targeting);

            _banner = Kit.Box("fc-hud__banner");
            _safe.Add(_banner);

            // Radio chatter: a portrait and one line (a tap skips it), in the toasts' style. The campaign's, and in every
            // battle the commander's words at the start and the end (prompt 22 F.4).
            if (mode != HudMode.Menu && !spec.Sandbox)
            {
                _radio = new RadioPanel();
                under.Add(_radio.Root);
            }

            // Notices (a point lost, air raids, an elite's arrival): the kit's toast on the battlefield, in the
            // column under the top strip; compact: small, gone after about 3 s, one after another (prompt 11 A6).
            _toast = Kit.Box("fc-hud__toast");
            var toastBox = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-toast fc-hud__toast-face");
            toastBox.Add(Kit.Icon("info", "fc-hud__toast-icon"));
            _toastText = Kit.Text("", (Compact ? "fc-small" : "fc-body") + " fc-row-text fc-hud__toast-text");
            toastBox.Add(_toastText);
            _toast.Add(toastBox);
            under.Add(_toast);

            // Pause holds Auto buy and Support too (prompt 11 A2), whatever the layout.
            _pause = new PausePanel(() => ResumePressed?.Invoke(), () => RestartPressed?.Invoke(), () => MenuPressed?.Invoke(),
                () => AutoDeployToggled?.Invoke(), () => AutoStrikeToggled?.Invoke(), Relocalise);
            _safe.Add(_pause.Root);
            _result = new ResultPanel(() => RestartPressed?.Invoke(), () => MenuPressed?.Invoke(), () => DoubleRewardPressed?.Invoke(),
                () => NextMissionPressed?.Invoke(), () => CheckpointPressed?.Invoke(), () => DeckPressed?.Invoke());
            _safe.Add(_result.Root);
            _choice = new ChoicePanel();
            _safe.Add(_choice.Root);
            _supportPick = new SupportPickPanel();
            _safe.Add(_supportPick.Root);

            _selectionBox = UiKit.Box("selection-box");
            _root.Add(_selectionBox);

            SetSelection(default);
        }

        public HudMode Mode { get; }

        /// <summary>The compact layout is in use (prompt 11 A; Settings: Compact battle HUD).</summary>
        public bool Compact { get; }

        /// <summary>
        /// A row under the selection's health bar for more of what the selected vehicle carries (the balance
        /// agent's ammo icons, prompt 13 C.9): hidden while empty; show it when adding to it. Null in the menu.
        /// </summary>
        public VisualElement SelectionExtras { get; }

        private readonly RadioPanel _radio;

        /// <summary>A line of radio chatter (every battle but the menu's and the Sandbox's).</summary>
        internal void Radio(Match.RadioLine line) => _radio?.Say(line);

        private readonly VisualElement _corner;
        private CommanderBadge _commanderBadge;

        /// <summary>Prompt 22 F.4: the side's commander as a small face beside pause; a tap shows its strength and weakness.</summary>
        internal CommanderBadge ShowCommanderBadge(CommanderDef commander)
        {
            if (_corner == null || commander == null) return null;
            if (_commanderBadge != null)
            {
                _commanderBadge.Face.RemoveFromHierarchy();
                _commanderBadge.Card.RemoveFromHierarchy();
            }
            _commanderBadge = new CommanderBadge(commander);
            // Before pause, after the frame counter.
            _corner.Insert(Math.Max(0, _corner.childCount - 1), _commanderBadge.Face);
            _safe.Add(_commanderBadge.Card);
            return _commanderBadge;
        }

        /// <summary>Null in the menu.</summary>
        public Minimap Minimap { get; }

        /// <summary>
        /// The language changed in the pause menu (prompt 21 L): every text of the HUD is read again in the new
        /// language, in place; the battle under the pause is not reloaded.
        /// </summary>
        public void Relocalise(bool wasVietnamese)
        {
            Relabel.Apply(_root, wasVietnamese);
            LanguageSwitched?.Invoke();
        }

        /// <summary>The HUD was relabelled in the new language.</summary>
        public event Action LanguageSwitched;

        /// <summary>The pause menu, for the checks (the language switch).</summary>
        internal PausePanel Pause => _pause;

        public event Action SelectAllPressed;

        /// <summary>The selection panel's Deselect order (play-test 6).</summary>
        public event Action DeselectPressed;
        public event Action StopPressed;
        public event Action RetreatPressed;
        public event Action AttackMovePressed;
        public event Action RestartPressed;
        public event Action BoxModeToggled;

        /// <summary>The zoom buttons beside the minimap (both HUDs since play-test 6): the factor to zoom by.</summary>
        public event Action<float> ZoomPressed;
        public event Action<int> CardPressed;
        public event Action TargetCancelled;
        public event Action PausePressed;

        /// <summary>A part's icon under the boss bar was tapped (prompt 9): the boss and the part's index.</summary>
        public event Action<MachineBrigade.Sim.Core.EntityId, int> BossPartTapped;
        public event Action ResumePressed;
        public event Action MenuPressed;
        public event Action PlayPressed;
        public event Action SettingsChanged;
        public event Action VolumeChanged;
        public event Action<Vector2> MinimapClicked;
        public event Action<bool> StancePressed;
        public event Action AutoDeployToggled;

        /// <summary>The player asks for the front destroyed tower to be flown back in.</summary>
        public event Action TowerPressed;

        /// <summary>How many destroyed towers can be flown back in now, and the next one's price (0: hide the button).</summary>
        public void SetTowers(int count, int cost)
        {
            if (_towerMini != null)
            {
                _towerMini.style.display = count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
                if (count <= 0) return;
                _towerMiniText.text = count > 1 ? $"×{count} · {cost}" : cost.ToString();
                _towerMini.tooltip = Strings.Format("rail.towerCost", ("count", count), ("cp", cost));
                return;
            }
            if (_towerButton == null) return;
            _towerButton.style.display = count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            if (count > 0) _towerButton.Label = Strings.Format("rail.towerCost", ("count", count), ("cp", cost));
        }
        public event Action AutoStrikeToggled;
        public event Action<string> PointPressed;

        /// <summary>The shop is trying a skin on (null: back to the equipped one).</summary>
        public event Action<string> SkinPreviewed;

        /// <summary>The result screen's "watch an ad for double coins" button.</summary>
        public event Action DoubleRewardPressed;

        /// <summary>The result screen's "next mission" button (campaign).</summary>
        public event Action NextMissionPressed;

        /// <summary>The result screen's "back to the checkpoint" button (a lost multi-stage mission).</summary>
        public event Action CheckpointPressed;

        /// <summary>The result screen's "open the deck" button under a defeat's hints: back to the menu, on the Army tab's deck.</summary>
        public event Action DeckPressed;

        private ChoicePanel _choice;
        private HuntRestPanel _huntRest;
        private SupportPickPanel _supportPick;

        /// <summary>Prompt 20 N: the Boss Hunt's rest strip (a null title hides it).</summary>
        public void SetHuntRest(string title, float seconds, string next, string held) => _huntRest?.Set(title, seconds, next, held);

        /// <summary>Prompt 20 N: the pick of one of three combat supports after a main boss.</summary>
        public void ShowSupportPick(string title, IReadOnlyList<(string icon, string name, string info)> options, Action<int> chosen) =>
            _supportPick?.Show(title, options, chosen);

        public void SetSupportPickTime(float seconds, string key = null) => _supportPick?.SetTime(seconds, key);

        public void HideSupportPick() => _supportPick?.Hide();

        public bool SupportPickShown => _supportPick != null && _supportPick.Visible;

        /// <summary>A multi-stage mission's branching point: the ways on (a name and a line each).</summary>
        public void ShowChoice(string title, IReadOnlyList<(string, string)> options, Action<int> chosen) => _choice?.Show(title, options, chosen);

        public void SetChoiceTime(float seconds) => _choice?.SetTime(seconds);

        public void HideChoice() => _choice?.Hide();

        public bool ChoiceShown => _choice != null && _choice.Visible;

        /// <summary>Shows the commander's current intent.</summary>
        public void SetCommander(bool defend, bool autoDeploy, bool autoStrike, string focus)
        {
            _pause?.SetCommander(autoDeploy, autoStrike);
            _score?.SetFocus(focus);
            if (_stanceSwitch != null)
            {
                if (_defending != defend || !_stanceShown)
                {
                    _defending = defend;
                    _stanceShown = true;
                    _stanceSwitch.EnableInClassList("fc-hud__switch--defend", defend);
                    _stanceSwitch.tooltip = Strings.Get(defend ? "rail.stanceDefend" : "rail.stanceAttack");
                }
                _buyToggle.On = autoDeploy;
                _supportToggle.On = autoStrike;
                return;
            }
            if (_attackStance == null) return;
            _defending = defend;
            _attackStance.EnableInClassList("fc-stance--on", !defend);
            _defendStance.EnableInClassList("fc-stance--on", defend);
            if (_autoDeploy.On != autoDeploy) _autoDeploy.On = autoDeploy;
            if (_autoStrike.On != autoStrike) _autoStrike.On = autoStrike;
        }

        private bool _stanceShown;

        public bool ShowFps { get; set; }

        /// <summary>Takes a stat of the top strip off (the Sandbox has no waves).</summary>
        private static void HideStat(VisualElement value)
        {
            for (var e = value; e != null; e = e.parent)
                if (e.ClassListContains("fc-hud__stat"))
                {
                    e.style.display = DisplayStyle.None;
                    return;
                }
        }

        public void SetStats(int allies, int enemies, int wave, float secondsToNextWave, float fps)
        {
            if (_allies != null)
            {
                var seconds = Mathf.CeilToInt(secondsToNextWave);
                if (allies != _shownAllies) _allies.text = (_shownAllies = allies).ToString();
                if (enemies != _shownEnemies) _enemies.text = (_shownEnemies = enemies).ToString();
                if (wave != _shownWave) _wave.text = (_shownWave = wave).ToString();
                if (seconds != _shownSeconds) _next.text = $"{(_shownSeconds = seconds) / 60}:{seconds % 60:00}";
            }
            var shownFps = ShowFps ? Mathf.RoundToInt(fps) : -1;
            if (_fps != null && shownFps != _shownFps)
            {
                _fps.text = (_shownFps = shownFps) >= 0 ? $"{shownFps} FPS" : "";
                _fps.style.display = shownFps >= 0 ? DisplayStyle.Flex : DisplayStyle.None;
            }
        }

        private int _shownAllies = -1, _shownEnemies = -1, _shownWave = -1, _shownSeconds = -1, _shownFps = -2;
        private SelectionSummary _shownSelection = new(-1, null, 0f, 0f);

        public void SetScore(int ours, int theirs, int max, IReadOnlyList<PointInfo> points) => _score?.Update(ours, theirs, max, points);

        /// <summary>Time left under the objective chips (negative hides it).</summary>
        public void SetTimer(float secondsLeft) => _score?.SetTimer(secondsLeft);

        public void SetMission(string goal, string detail, float progress, float secondsLeft, IReadOnlyList<PointInfo> points) =>
            _missionBar?.Update(goal, detail, progress, secondsLeft, points);

        /// <summary>The boss's parts under its bar (prompt 9); <paramref name="focused"/> is the part the player has ordered fire at, or -1.</summary>
        public void SetBossParts(MachineBrigade.Sim.Entities.Vehicle boss, int focused) => _boss?.Parts.Set(boss, focused);

        /// <summary>The boss's health bar, hidden when <paramref name="name"/> is null.</summary>
        public void SetBoss(string name, float health)
        {
            _boss?.Set(name, health);
            BossOnTop(name);
        }

        /// <summary>The compact HUD's boss bar is in the top row: the column under the row makes room while it shows.</summary>
        private void BossOnTop(string name) => _safe?.EnableInClassList("fc-hud--boss-top", Compact && _boss != null && name != null);

        /// <summary>A multi-phase boss: its bar marked at each phase, the phase it is in, and whether it is transforming.</summary>
        public void SetBoss(string name, float health, int phase, IReadOnlyList<float> marks, bool transforming)
        {
            _boss?.Set(name, health, phase, marks, transforming);
            BossOnTop(name);
        }
        /// <summary>The safe area the controls sit in (the screenshot tool sets its insets).</summary>
        internal VisualElement SafeArea => _safe;

        /// <summary>The boss's parts without a battle (the screenshot tool): each part's share of health and whether it is broken.</summary>
        internal void PreviewBossParts(VehicleDef def, IReadOnlyList<float> shares, IReadOnlyList<bool> broken, int focused) =>
            _boss?.Parts.Preview(def, shares, broken, focused);

        /// <summary>Opens the compact boss bar as a tap does (the screenshot tool and the checks).</summary>
        internal void PreviewBossExpanded() => _boss?.Expand();

        /// <summary>Prompt 16 F: the boss's escorts still alive, on its bar.</summary>
        public void SetBossEscorts(int alive) => _boss?.SetEscorts(alive);

        /// <summary>Prompt 20: the boss bar's rank label (null: none).</summary>
        public void SetBossRank(MachineBrigade.Sim.Content.BossRankDef rank) => _boss?.SetRank(rank);

        /// <summary>Prompt 18: the boss's big attack on its bar (the icon, the cooldown, lit while it charges) and its charging parts flashing.</summary>
        public void SetBossBigAttack(MachineBrigade.Sim.Entities.Vehicle boss)
        {
            if (_boss == null) return;
            var big = boss?.BigAttack;
            if (big == null)
            {
                _boss.SetBigAttack(null, 0f, false, 0f);
                _boss.Parts.SetCharging(null, false);
                return;
            }
            var charging = big.Stage == MachineBrigade.Sim.Entities.BigStage.Charging;
            var left = charging && !double.IsInfinity(big.FireAt) ? big.WarnLeft : -1f;
            _boss.SetBigAttack(big.Def.Icon, big.Ready, charging, left);
            // The parts to break: flashing about three times a second while it charges.
            _boss.Parts.SetCharging(charging ? big.Parts : null, Mathf.Repeat(Time.unscaledTime, 0.36f) < 0.18f);
        }

        /// <summary>
        /// Prompt 19 B.5: a tiered boss's altitude on its bar (its icon, the tier's name and the seconds to the next change;
        /// none once it holds low with its main engine broken, or has crashed).
        /// </summary>
        public void SetBossTier(MachineBrigade.Sim.Entities.Vehicle boss, double now)
        {
            if (_boss == null) return;
            if (boss?.Def.Tiers == null || boss.Crashed)
            {
                _boss.SetTier(null, null, null);
                return;
            }
            var key = boss.Crashing ? "tier.ground" : boss.Shifting ? "tier.shift" : "tier." + boss.TierFrom.ToString().ToLowerInvariant();
            var icon = boss.TierFrom switch
            {
                AltitudeTier.Orbit => "cbradar",
                AltitudeTier.High => "sam",
                _ => "aa",
            };
            var left = Mathf.CeilToInt((float)(boss.TierNext - now));
            var text = Kit.Caps(Strings.Get(key)) + (boss.StuckLow || boss.Crashing || left <= 0 ? "" : "  " + left + "s");
            _boss.SetTier(icon, text, Strings.Get("hud.tier"));
        }

        /// <summary>The boss's health in numbers beside its name (after <see cref="SetBoss(string, float)"/>).</summary>
        public void SetBossHp(float hp, float maxHp) => _boss?.SetHp(hp, maxHp);

        /// <summary>The fortress super-gun's countdown (negative seconds: none standing).</summary>
        public void SetSuperGun(float seconds, bool down, bool ours) => _superGun?.Set(seconds, down, ours);

        /// <summary>The next enemy wave's make-up, its countdown and number, and vehicles of earlier waves still waiting.</summary>
        public void SetWavePreview(IReadOnlyList<(string id, int count)> wave, float seconds, int number, int held) =>
            _wavePreview?.Set(wave, seconds, number, held);

        /// <summary>A vehicle's card icon (an elite's is its base vehicle's), and whether it is an elite.</summary>
        private (string icon, bool elite) DescribeVehicle(string id)
        {
            if (Catalog == null || !Catalog.Vehicles.TryGetValue(id, out var def)) return (CardIcons.For(id), false);
            return (CardIcons.For(def.Elite && def.EliteOf != null ? def.EliteOf : id), def.Elite);
        }

        public void SetDeck(float cp, float bank, float earning, float upkeep, IReadOnlyList<CardState> states) =>
            _deck?.Update(cp, bank, earning, upkeep, states);

        /// <summary>Shows the strike-targeting prompt, or hides it when <paramref name="message"/> is null.</summary>
        public void SetTargeting(string message)
        {
            if (_targeting == null) return;
            _targeting.style.display = message != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (message != null) _targetingText.text = message;
            _hintBar.style.display = message != null ? DisplayStyle.None : DisplayStyle.Flex;
        }

        /// <summary>Closes an open menu page; false when there is none (main menu or in a match).</summary>
        public bool MenuBack() => _menu != null && _menu.Back();

        /// <summary>The vehicle turntable for the menu's detail page.</summary>
        public Rendering.UnitPreview MenuPreview
        {
            set
            {
                if (_menu != null) _menu.Preview = value;
            }
        }

        /// <summary>A menu page covers the whole lobby battle (it can rest).</summary>
        public bool MenuCoversBattle => _menu != null && _menu.CoversBattle;

        public void SetPaused(bool paused)
        {
            if (_pause != null) _pause.Visible = paused;
        }

        /// <param name="title">The mission's name or the mode's.</param>
        /// <param name="note">A line under the title (an endless run's record); null for none.</param>
        /// <param name="hints">After a defeat: one or two things to change, with a button to the deck.</param>
        public void ShowResult(int outcome, string title, IReadOnlyList<(string, string)> rows, RewardView reward = null,
            string note = null, IReadOnlyList<string> hints = null)
        {
            if (_pause != null) _pause.Visible = false;
            _result?.Show(outcome, title, rows, reward, note, hints);
        }

        private VisualElement _letterTop, _letterBottom;
        private float _shownLetterbox = -1f;

        /// <summary>Cinematic bars sliding in from the top and bottom (0 hidden, 1 fully in).</summary>
        public void SetLetterbox(float amount)
        {
            if (Mathf.Abs(amount - _shownLetterbox) < 0.01f) return;
            _shownLetterbox = amount;
            if (_letterTop == null)
            {
                _letterTop = UiKit.Box("letterbox top");
                _letterBottom = UiKit.Box("letterbox bottom");
                _root.Add(_letterTop);
                _root.Add(_letterBottom);
            }
            var height = Length.Percent(amount * 9f);
            _letterTop.style.height = height;
            _letterBottom.style.height = height;
            var display = amount > 0.001f ? DisplayStyle.Flex : DisplayStyle.None;
            _letterTop.style.display = display;
            _letterBottom.style.display = display;
        }

        private VisualElement _ad, _adClaim;
        private Label _adCount;
        private Action<bool> _adDone;
        private float _adUntil;

        /// <summary>
        /// The stand-in rewarded ad: a solid screen with a five-second countdown, then a claim
        /// button. Closing it early reports false.
        /// </summary>
        public void ShowPlaceholderAd(Action<bool> done)
        {
            if (_ad == null)
            {
                _ad = Kit.Root(KitDialog.ScrimClass + " fc-overlay fc-ad");
                _ad.pickingMode = PickingMode.Position;
                var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog", PickingMode.Position);
                card.Add(Kit.Text(Kit.Caps(Strings.Get("ad.title")), "fc-panel-title fc-dialog__title"));
                card.Add(Kit.Text(Strings.Get("ad.body"), "fc-body-2 fc-dialog__body"));
                _adCount = Kit.Text("", "fc-number fc-ad__count");
                card.Add(_adCount);
                var row = Kit.Box("fc-dialog__buttons");
                row.Add(new KitButton(ButtonTier.Secondary, Strings.Get("ad.close"), () => CloseAd(false), "close"));
                _adClaim = new KitButton(ButtonTier.Claim, Strings.Get("ad.claim"), () => CloseAd(true));
                row.Add(_adClaim);
                card.Add(row);
                _ad.Add(card);
                _safe.Add(_ad);
            }
            _adDone = done;
            _adUntil = Time.unscaledTime + 5f;
            _adClaim.style.display = DisplayStyle.None;
            _ad.style.display = DisplayStyle.Flex;
        }

        private void CloseAd(bool watched)
        {
            if (_ad == null || _ad.style.display == DisplayStyle.None) return;
            _ad.style.display = DisplayStyle.None;
            var done = _adDone;
            _adDone = null;
            done?.Invoke(watched);
        }

        private void TickAd()
        {
            if (_ad == null || _ad.style.display == DisplayStyle.None) return;
            var left = Mathf.CeilToInt(_adUntil - Time.unscaledTime);
            _adCount.text = left > 0 ? left.ToString() : "";
            if (left <= 0 && _adClaim.style.display == DisplayStyle.None) _adClaim.style.display = DisplayStyle.Flex;
        }

        /// <summary>The reward was paid (doubled after an ad): the result screen updates its numbers.</summary>
        public void ShowRewardClaimed(int coins, bool doubled) => _result?.ShowClaimed(coins, doubled);

        public bool ResultVisible => _result != null && _result.Visible;

        /// <summary>Big mission title across the screen for a few seconds (compact: a strip under the top one).</summary>
        public void ShowBanner(string kicker, string title, string subtitle, float seconds = 3.5f)
        {
            if (_banner == null) return;
            _banner.Clear();
            var strip = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__banner-face");
            if (!string.IsNullOrEmpty(kicker)) strip.Add(Kit.Text(Kit.Caps(kicker), "fc-caption fc-hud__banner-kicker"));
            strip.Add(Kit.Text(Kit.Caps(title), Compact ? "fc-panel-title" : "fc-title"));
            if (!string.IsNullOrEmpty(subtitle)) strip.Add(Kit.Text(subtitle, Compact ? "fc-small" : "fc-body-2"));
            _banner.Add(strip);
            _banner.AddToClassList("fc-hud__banner--visible");
            _bannerUntil = Time.unscaledTime + seconds;
        }

        private VisualElement _command, _weapons;
        private float _hintUntil;
        private string _weaponsFor;

        public void SetSelection(SelectionSummary summary)
        {
            if (_unitName == null) return;
            _command.style.display = summary.Count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            // Only rebuild the panel when what it shows has changed (whole hit points).
            if (summary.Count == _shownSelection.Count && summary.DefId == _shownSelection.DefId &&
                Mathf.CeilToInt(summary.Hp) == Mathf.CeilToInt(_shownSelection.Hp) &&
                Mathf.CeilToInt(summary.MaxHp) == Mathf.CeilToInt(_shownSelection.MaxHp)) return;
            _shownSelection = summary;
            if (summary.Count == 0)
            {
                _selectedCount.text = "";
                _unitName.text = Strings.Get("panel.none");
                _hpText.text = Strings.Get("panel.noneHint");
                _hpFill.style.width = Length.Percent(0f);
                _portraitIcon.Name = "tank";
                _portrait.style.backgroundImage = StyleKeyword.None;
                _portraitIcon.style.display = DisplayStyle.Flex;
                if (_counterText != null) _counterText.text = "";
                return;
            }

            _selectedCount.text = Kit.Caps(Compact ? "×" + summary.Count : Strings.Format("panel.selected", summary.Count));
            // Compact: the short name, on one line (prompt 11 B).
            var name = summary.DefId == null ? Strings.Get("panel.mixed") : Compact ? Strings.Short(summary.DefId) : Strings.Unit(summary.DefId);
            _unitName.text = Kit.Caps(name);
            _portraitIcon.Name = summary.DefId != null ? CardIcons.For(summary.DefId) : "people";
            // The vehicle's render where there is one (a mixed group keeps the icon).
            var render = summary.DefId != null ? CardArt.For(summary.DefId) : null;
            _portrait.style.backgroundImage = render != null ? new StyleBackground(render) : new StyleBackground(StyleKeyword.None);
            _portraitIcon.style.display = render != null ? DisplayStyle.None : DisplayStyle.Flex;
            var health = summary.MaxHp > 0f ? Mathf.Clamp01(summary.Hp / summary.MaxHp) : 0f;
            _hpFill.style.width = Length.Percent(health * 100f);
            _hpFill.EnableInClassList("fc-hud__hp-fill--hurt", health < 0.6f && health >= 0.3f);
            _hpFill.EnableInClassList("fc-hud__hp-fill--critical", health < 0.3f);
            _hpText.text = Strings.Format("panel.hp", ("health", Mathf.CeilToInt(summary.Hp)), ("max", Mathf.CeilToInt(summary.MaxHp)));
            if (_combatFor != summary.DefId)
            {
                _combatFor = summary.DefId;
                _combat.Clear();
                if (summary.DefId != null && Catalog != null && Catalog.Vehicles.TryGetValue(summary.DefId, out var shown))
                    _combat.Add(KitCombat.Row(shown, 2));
                _combat.style.display = _combat.childCount > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            }
            if (_weapons == null) return;
            // The full HUD: what this unit is for (who it beats and who beats it), and what it fights with.
            VehicleDef def = null;
            var known = summary.DefId != null && Catalog != null && Catalog.Vehicles.TryGetValue(summary.DefId, out def);
            _counterText.text = known ? MachineBrigade.Game.Match.Counters.Line(def) : "";
            if (_weaponsFor != summary.DefId)
            {
                _weaponsFor = summary.DefId;
                _weapons.Clear();
                // Its weapons in one line ("120 mm gun · machine gun"), so the panel stays low over the battlefield.
                if (known)
                {
                    var names = new List<string>();
                    foreach (var line in WeaponInfo.Of(def)) names.Add(line.Name);
                    if (names.Count > 0) _weapons.Add(Kit.Text(string.Join(" · ", names), "fc-body fc-row-text"));
                }
            }
        }

        private Label _counterText;
        private ItemBar _items;
        private VisualElement _combat, _enemyTip;
        private string _combatFor;

        /// <summary>A tray card shown as held (the screenshots); -1 lets go.</summary>
        internal void PreviewHeld(int index) => _deck?.PreviewHeld(index);

        /// <summary>
        /// Prompt 15 E5: a tapped enemy's front armour and each vehicle of our deck marked ✓ ~ ✕ by its main weapon
        /// against it. It stays 5 s (a tap on it closes it); a new tap replaces it.
        /// </summary>
        public void ShowEnemyTip(VehicleDef enemy, IEnumerable<VehicleDef> deck, AltitudeTier tier = AltitudeTier.None)
        {
            if (enemy == null || _safe == null) return;
            _enemyTip?.RemoveFromHierarchy();
            // Prompt 19 B.5: a boss on altitude tiers is judged by what reaches its tier now.
            var tip = _enemyTip = KitCombat.EnemyTip(enemy, deck, tier);
            tip.AddToClassList("fc-hud__enemy-tip");
            tip.pickingMode = PickingMode.Position;
            tip.AddManipulator(new Tap(() => tip.RemoveFromHierarchy()));
            _safe.Add(tip);
            tip.schedule.Execute(() => tip.RemoveFromHierarchy()).StartingIn(5000);
        }

        /// <summary>An item button was tapped (index into the list given to <see cref="SetupItems"/>).</summary>
        public event Action<int> ItemPressed;

        /// <summary>Builds the item strip for the items the player brought into this match.</summary>
        public void SetupItems(IReadOnlyList<string> items)
        {
            if (_items != null || items.Count == 0 || _safe == null) return;
            _items = new ItemBar(items);
            _items.Pressed += i => ItemPressed?.Invoke(i);
            _safe.Add(_items.Root);
        }

        public void SetItems(IReadOnlyList<ItemState> states) => _items?.Update(states);

        /// <summary>The loaded catalog, for card and unit details.</summary>
        private Catalog Catalog { get; }

        public void SetModes(bool attackMoveArmed, bool boxMode)
        {
            if (_attackMove == null || (_attackArmed == attackMoveArmed && _boxMode == boxMode)) return;
            _attackArmed = attackMoveArmed;
            _boxMode = boxMode;
            _attackMove.EnableInClassList("fc-hud__order--armed", attackMoveArmed);
            _boxTool.EnableInClassList("fc-icon-btn--on", boxMode);
            _hint.text = Strings.Get(attackMoveArmed ? "hint.attackMove" : boxMode ? "hint.box" : _autoHint);
            if (attackMoveArmed || boxMode) _hintUntil = float.MaxValue;
            else if (_hintUntil == float.MaxValue) _hintUntil = Time.unscaledTime;
        }

        public void ShowError(CommandError error) => Toast(Strings.Error(error), error: true);

        /// <summary>How long a compact notice stays up (prompt 11 A6: about 3 s), whatever the caller asked.</summary>
        private const float CompactToastMin = 2.5f, CompactToastMax = 3.5f;

        /// <summary>
        /// Shows a message. One that arrives while another is fresh waits its turn (a few at
        /// most), so "point lost" is not wiped by "APC on the way"; errors go straight up.
        /// </summary>
        public void Toast(string message, bool error = false, float seconds = 3f)
        {
            if (Compact) seconds = Mathf.Clamp(seconds, CompactToastMin, CompactToastMax);
            var busy = _toast.ClassListContains("fc-hud__toast--visible") && Time.unscaledTime - _toastShownAt < 1.2f;
            if (busy && !error)
            {
                if (_toastQueue.Count < 3 && _toastText.text != message) _toastQueue.Enqueue((message, false, seconds));
                return;
            }
            ShowToast(message, error, seconds);
        }

        private readonly Queue<(string message, bool error, float seconds)> _toastQueue = new();
        private float _toastShownAt = -10f;

        private void ShowToast(string message, bool error, float seconds)
        {
            _toastText.text = message;
            _toastText.parent?.EnableInClassList("fc-toast--alert", error);
            _toast.AddToClassList("fc-hud__toast--visible");
            _toastShownAt = Time.unscaledTime;
            _toastUntil = Time.unscaledTime + seconds;
        }

        public void ShowSelectionBox(Vector2 fromScreen, Vector2 toScreen)
        {
            var a = ToPanel(fromScreen);
            var b = ToPanel(toScreen);
            _selectionBox.style.left = Mathf.Min(a.x, b.x);
            _selectionBox.style.top = Mathf.Min(a.y, b.y);
            _selectionBox.style.width = Mathf.Abs(b.x - a.x);
            _selectionBox.style.height = Mathf.Abs(b.y - a.y);
            _selectionBox.style.display = DisplayStyle.Flex;
        }

        public void HideSelectionBox() => _selectionBox.style.display = DisplayStyle.None;

        /// <summary>True when a screen point is over an interactive HUD element.</summary>
        public bool IsOverUi(Vector2 screen)
        {
            var panel = _root.panel;
            return panel != null && panel.Pick(ToPanel(screen)) != null;
        }

        private readonly VisualElement _flash;
        private float _flashLevel;
        private readonly TraitWords _words;

        /// <summary>A short word over a vehicle whose equipment just went off (see <see cref="TraitWords"/>).</summary>
        public void TraitWord(Vector3 world, string word, bool ours, Camera camera) => _words?.Show(world, word, ours, camera);

        /// <summary>Flashes the screen (a huge blast in view); the stronger of overlapping flashes wins, and it fades in a fifth of a second.</summary>
        public void Flash(float strength) => _flashLevel = Mathf.Max(_flashLevel, Mathf.Clamp01(strength));

        public void Tick()
        {
            _radio?.Tick();
            _commanderBadge?.Tick();
            _words?.Tick();
            _boss?.Tick();
            if (_flashLevel > 0f)
            {
                _flashLevel = Mathf.Max(0f, _flashLevel - Time.unscaledDeltaTime * 1.1f);
                _flash.style.opacity = _flashLevel;
            }
            var toastDone = Time.unscaledTime > _toastUntil || (_toastQueue.Count > 0 && Time.unscaledTime - _toastShownAt > 1.2f);
            if (toastDone && _toastQueue.Count > 0)
            {
                var (message, error, seconds) = _toastQueue.Dequeue();
                ShowToast(message, error, seconds);
            }
            else if (_toast.ClassListContains("fc-hud__toast--visible") && Time.unscaledTime > _toastUntil)
            {
                _toast.RemoveFromClassList("fc-hud__toast--visible");
            }
            if (_banner != null && _banner.ClassListContains("fc-hud__banner--visible") && Time.unscaledTime > _bannerUntil)
                _banner.RemoveFromClassList("fc-hud__banner--visible");
            _hintBar?.EnableInClassList("fc-hud__hint--gone", Time.unscaledTime > _hintUntil);
            TickAd();
            if (_settings != null && (Screen.width != _screenWidth || Screen.height != _screenHeight))
            {
                // A new screen shape (another device, a rotated tablet, a resized Game view).
                _screenWidth = Screen.width;
                _screenHeight = Screen.height;
                ApplyScale();
                _appliedSafeArea = default;
            }
            if (_settings != null && Screen.safeArea != _appliedSafeArea) ApplySafeArea();
        }

        private int _screenWidth, _screenHeight;
        private readonly bool _menuPanel;

        /// <summary>
        /// The panel's scale: the menus in device points (prompt 14: <see cref="MenuScale"/>), the battle HUD with
        /// the screen (<see cref="MatchFor"/>); the Settings' UI size multiplies either.
        /// </summary>
        private void ApplyScale()
        {
            if (_menuPanel)
            {
                _settings.scaleMode = PanelScaleMode.ConstantPixelSize;
                _settings.scale = MenuScale(Screen.width, Screen.height, Screen.dpi, Application.isMobilePlatform) * Match.MatchSettings.UiScale;
            }
            else
            {
                _settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
                _settings.match = MatchFor(Screen.width, Screen.height);
                _settings.scale = Match.MatchSettings.UiScale;
            }
        }

        /// <summary>
        /// The menus' scale (screen pixels per panel pixel) in device points (prompt 14): one point is
        /// <see cref="Kit.PanelPxPerPoint"/> panel pixels whatever the screen's width, so a tablet shows more and a
        /// phone the same as a phone. A point is a 160th of an inch (Android's dp, iOS's point is a 163rd). Where
        /// the density is unknown or not a phone's (the editor, a desktop), the screen is taken for a phone 395 pt
        /// high: the height scaling the menus had before.
        /// </summary>
        internal static float MenuScale(int width, int height, float dpi, bool mobile)
        {
            if (width <= 0 || height <= 0) return 1f;
            if (!mobile || dpi < 100f) dpi = height / Kit.ReferencePhonePoints * Kit.PointsPerInch;
            return dpi / (Kit.PointsPerInch * Kit.PanelPxPerPoint);
        }

        /// <summary>
        /// Responsive scaling. The layout is authored for 1280 x 720. On screens at least that
        /// wide for their height (16:9 and the long 19.5:9 and 21:9 phones) the panel scales with
        /// the height, so everything keeps its size and the extra width goes to the battlefield
        /// between the edge clusters; on squarer screens (16:10, 3:2, 4:3 tablets) it blends over
        /// to scaling with the width, so the deck and the side columns always fit across.
        /// </summary>
        internal static float MatchFor(int width, int height)
        {
            if (width <= 0 || height <= 0) return 1f;
            var aspect = width / (float)height;
            return Mathf.Clamp01((aspect - 4f / 3f) / (16f / 9f - 4f / 3f));
        }

        public void Dispose()
        {
            if (_host != null) Object.Destroy(_host);
            if (_eventSystem != null) Object.Destroy(_eventSystem);
            if (_settings != null) Object.Destroy(_settings);
        }

        private Vector2 ToPanel(Vector2 screen)
        {
            var panel = _root.panel;
            return panel == null ? screen : RuntimePanelUtils.ScreenToPanel(panel, new Vector2(screen.x, Screen.height - screen.y));
        }

        private void ApplySafeArea()
        {
            _appliedSafeArea = Screen.safeArea;
            if (_root.panel == null) return;
            var min = ToPanel(new Vector2(_appliedSafeArea.xMin, _appliedSafeArea.yMax));
            var max = ToPanel(new Vector2(_appliedSafeArea.xMax, _appliedSafeArea.yMin));
            var size = ToPanel(new Vector2(Screen.width, 0f));
            _safe.style.left = min.x;
            _safe.style.top = min.y;
            _safe.style.right = Mathf.Max(0f, size.x - max.x);
            _safe.style.bottom = Mathf.Max(0f, ToPanel(new Vector2(0f, 0f)).y - max.y);
        }

        /// <summary>A number with its icon (and, in the full HUD, its caption); compact stats share one strip.</summary>
        private static Label Stat(VisualElement parent, string icon, string label, string side, bool compact)
        {
            var classes = (compact ? "" : KitPanel.SurfaceClass + " fc-surface--field ") + "fc-hud__stat" + (side != null ? " " + side : "");
            var stat = Kit.Box(classes);
            stat.tooltip = label;
            stat.Add(Kit.Icon(icon, "fc-hud__stat-icon"));
            var column = Kit.Box("fc-hud__stat-text");
            var number = Kit.Text("0", "fc-number-small");
            column.Add(number);
            if (!compact) column.Add(Kit.Caption(label));
            stat.Add(column);
            parent.Add(stat);
            return number;
        }

        /// <summary>One of Attack / Defend: its icon and its full name; the one on is the text colour with dark text.</summary>
        private static VisualElement Stance(VisualElement parent, string icon, string label, Action onClick)
        {
            var option = Kit.Tappable("fc-stance", onClick);
            option.Add(Kit.Icon(icon, "fc-stance__icon"));
            option.Add(Kit.Text(Kit.Caps(label), "fc-stance__label fc-row-text"));
            parent.Add(option);
            return option;
        }

        /// <summary>A hand order for the selected vehicles (attack-move, stop, back): an icon over its name.</summary>
        private static VisualElement Order(VisualElement parent, string icon, string label, Action onClick)
        {
            var button = Kit.Tappable("fc-hud__order", onClick);
            button.Add(Kit.Icon(icon, "fc-hud__order-icon"));
            button.Add(Kit.Text(Kit.Caps(label), "fc-stance__label fc-hud__order-label"));
            parent.Add(button);
            return button;
        }
    }

    /// <summary>
    /// An on/off control of the compact HUD's rail (Auto buy, Support): a small icon face in a full
    /// touch target. On is the text colour with a dark icon; off is the field panel with a dim icon
    /// struck through, so the state reads without colour. The tooltip says it in words.
    /// </summary>
    internal sealed class HudIconToggle : VisualElement
    {
        private readonly string _onKey, _offKey;
        private bool _on, _shown;

        public HudIconToggle(string icon, string onKey, string offKey, Action toggled)
        {
            _onKey = onKey;
            _offKey = offKey;
            pickingMode = PickingMode.Position;
            AddToClassList("fc-hud__tool");
            AddToClassList("fc-hud__toggle");
            var face = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__tool-face");
            face.Add(Kit.Icon(icon));
            face.Add(Kit.Box("fc-hud__toggle-slash"));
            Add(face);
            On = false;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                On = !On;
                toggled?.Invoke();
            }));
        }

        public bool On
        {
            get => _on;
            set
            {
                if (_shown && value == _on) return;
                _shown = true;
                _on = value;
                EnableInClassList("fc-hud__toggle--on", value);
                tooltip = Strings.Get(value ? _onKey : _offKey);
            }
        }
    }
}
