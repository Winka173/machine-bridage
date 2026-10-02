using System.Collections;
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Input;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Composition root for a match: builds the simulation, views, effects, input and HUD for the
    /// mode chosen in <see cref="MatchSettings"/>, then drives the fixed-step loop. Without a
    /// chosen match it runs the menu over an AI-versus-AI battle. Restarting reloads the scene,
    /// which resets every system and view in one go (V2 rule 9).
    /// </summary>
    public sealed partial class MatchRunner : MonoBehaviour
    {
        private const int PlayerTeam = 0;
        private const int EnemyTeam = 1;
        private const float MinimapInterval = 0.1f;

        private static bool _debugStarted;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _debugStarted = false;
            _frameRateTarget = 60;
        }

        private SimWorld _world;
        private UnitPreview _preview;
        private bool _lobbyCovered;
        private int _lobbyMask;
        private CameraClearFlags _lobbyClear;
        private bool _lobbyPost;
        private ModeSession _session;
        private MatchReward _reward;
        private readonly Cinematics _cinematics = new();

        /// <summary>The campaign's radio chatter (null outside a mission).</summary>
        private RadioDirector _radio;

        /// <summary>The stuck detector of the internal build (prompt 12; null in a release build and on the menu).</summary>
        private StuckReporter _stuck;

        /// <summary>A story moment the camera goes to (a boss, reinforcements, a general): where, and until when.</summary>
        private Vector3 _storyFocus;
        private float _storyUntil;
        private float _cinematicZoom;

        /// <summary>The player moved the view during the slow-motion shot: it stops steering the camera.</summary>
        private bool _viewTaken;
        private SimClock _clock;
        private MaterialLibrary _materials;
        private MeshLibrary _meshes;
        private ModelLibrary _models;
        private Atmosphere _atmosphere;
        private MapView _map;
        private CrateViews _crates;
        private MineViews _mineViews;
        private Transform _worldRoot;
        private bool _richEffects;
        private double _nextWeatherShift = double.MaxValue;
        private WeatherKind _weatherKind;
        private Surroundings _surroundings;
        private ViewRegistry _views;
        private ObjectiveView _objectives;
        private NeutralSiteView _neutralSites;
        private MissionMarkers _markers;
        private PlayAreaView _playArea;

        /// <summary>A siege fortress's set pieces (dome, line in, searchlights, super-gun); null elsewhere.</summary>
        private FortressView _fortress;

        /// <summary>The battle was brought back to a checkpoint (replayed before its views were built).</summary>
        private bool _resumed;

        private readonly List<MissionMark> _marks = new();
        private EffectsDirector _effects;
        private AudioDirector _audio;
        private MusicDirector _music;
        private Weather _weather;
        private Weather _leavingWeather;
        private RtsCamera _camera;

        /// <summary>Prompt 17 A.4: a long battlefield's default zoom and widest zoom (the square maps' are 19 and 42).</summary>
        internal const float LongZoom = 21f, LongMaxZoom = 50f;
        private SelectionController _selection;
        private TouchGestures _gestures;
        private BattleHud _hud;
        private StoresStrip _storesStrip;
        private PlayerCommander _commander;

        /// <summary>Prompt 21: the Sandbox's editor, screen and overlays (null in every other battle).</summary>
        private SandboxController _sandbox;
        private readonly List<(Vector2 at, float radius, float until)> _warnings = new();
        private readonly List<PointInfo> _pointInfo = new();
        private bool _menu, _paused, _resultShown;
        private float _fps = 60f, _minimapAt, _attractAt;
        private Vector3 _attractFocus;
        private int _announcedWave, _kills, _losses;
        private bool _warnedAir;

        /// <summary>What the enemy brought (for a defeat's hints).</summary>
        private readonly BattleTally _tally = new();
        private float _lastInput;
        private PerfProbe _perf;
        private CrowdCheck _crowd;
        private FrameRateGovernor _frameRate;

        /// <summary>The rate the governor settled on carries over to the next scene load.</summary>
        private static int _frameRateTarget = 60;
        private bool _censusDone;

        /// <summary>Seconds without touching the screen before the camera starts following the fighting.</summary>
        private const float AutoCameraDelay = 8f;

        /// <summary>
        /// Builds the battle over several frames behind the loading curtain (world, map, models,
        /// effects, interface), so its bar moves instead of the whole build freezing one frame;
        /// nothing runs in Update until it is done.
        /// </summary>
        private IEnumerator Start()
        {
            // Nothing needs PhysX: debris, turrets and wrecks move on their own kinematics.
            Physics.simulationMode = SimulationMode.Script;
#if UNITY_EDITOR
            // A click on the Game view counts even while another editor window has focus; by
            // default pointer input waits for the Game view to be focused, so clicks went missing.
            UnityEngine.InputSystem.InputSystem.settings.editorInputBehaviorInPlayMode =
                UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
#endif
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            Time.timeScale = 1f;
            // The build happens behind the curtain, the first scene of a session too: shown once before the work starts.
            Curtain.Cover();
            yield return null;
            MatchSettings.Load();
            _frameRate = new FrameRateGovernor(_frameRateTarget, MatchSettings.SavingBattery ? 30 : MatchSettings.Options.FrameRate);
            ApplyDebugFlags();
            _perf = PerfProbe.Create();
            if (_perf != null) _perf.Detail = () => _views?.LodSummary();
            if (!_debugStarted && DebugFlags.Has("-mb-play"))
            {
                // Device testing: skip the menu once and play straight away.
                _debugStarted = true;
                MatchSettings.InMatch = true;
                if (DebugFlags.Has("-mb-survival")) MatchSettings.Mode = GameModeKind.Survival;
                if (DebugFlags.Has("-mb-rain")) MatchSettings.Weather = WeatherKind.Rain;
                if (DebugFlags.Has("-mb-storm")) MatchSettings.Weather = WeatherKind.Storm;
                if (DebugFlags.Has("-mb-clear")) MatchSettings.Weather = WeatherKind.Clear;
                if (DebugFlags.Has("-mb-snow")) MatchSettings.Weather = WeatherKind.Snow;
                if (DebugFlags.Has("-mb-sandstorm")) MatchSettings.Weather = WeatherKind.Sandstorm;
                if (DebugFlags.Has("-mb-fog")) MatchSettings.Weather = WeatherKind.Fog;
                if (DebugFlags.Has("-mb-night")) MatchSettings.Weather = WeatherKind.Night;
                foreach (var info in MatchSettings.AllMaps)
                    if (DebugFlags.Has("-mb-" + info.Id)) MatchSettings.Map = info.Id;
                if (DebugFlags.Has("-mb-deathmatch")) MatchSettings.Mode = GameModeKind.Deathmatch;
                if (DebugFlags.Has("-mb-hill")) MatchSettings.Mode = GameModeKind.KingOfTheHill;
                if (DebugFlags.Has("-mb-assault")) MatchSettings.Mode = GameModeKind.Assault;
                if (DebugFlags.Has("-mb-defend")) MatchSettings.Mode = GameModeKind.Defend;
                if (DebugFlags.Has("-mb-endless")) MatchSettings.Mode = GameModeKind.Endless;
                if (DebugFlags.Has("-mb-weekly")) MatchSettings.Mode = GameModeKind.Weekly;
                if (DebugFlags.Has("-mb-siege")) MatchSettings.Mode = GameModeKind.Siege;
            if (DebugFlags.Has("-mb-bossrush")) MatchSettings.Mode = GameModeKind.BossRush;
            // A campaign mission: -mb-c3m05, or an old id (-mb-m09) for the mission it became.
            foreach (var campaignMission in Campaign.All)
                    if (DebugFlags.Has("-mb-" + campaignMission.Id) || (campaignMission.Legacy != null && DebugFlags.Has("-mb-" + campaignMission.Legacy)))
                    {
                        MatchSettings.Mode = GameModeKind.Campaign;
                        MatchSettings.Mission = campaignMission.Id;
                    }
            }
            var options = MatchSettings.Options;
            // High graphics draws the most-seen vehicles with their high-detail models.
            ModelLibrary.HighDetail = options.Shadows == ShadowLevel.High && options.RichScenery;
            // Low graphics: the towers' rank details come without bolts or a second plate layer (tower-branch C.6).
            TowerArt.Lean = options.Shadows <= ShadowLevel.Low && !options.RichScenery;
            _builtGraphics = GraphicsSignature();
            _atmosphere = new Atmosphere(options);
            _cinematics.Enabled = MatchSettings.CinematicMoments && !DebugFlags.Has("-mb-no-cinematics");
            AudioListener.volume = MatchSettings.Volume;

            _menu = !MatchSettings.InMatch;
            var kind = _menu ? GameModeKind.Conquest : MatchSettings.Mode;
            // Prompt 21 C.6: a Sandbox battle runs on its scenario's own seed.
            var seed = _menu ? System.Environment.TickCount : kind == GameModeKind.Sandbox ? (SandboxSession.Scenario ??= SandboxSession.NewScenario()).Seed
                : 1234 + (int)MatchSettings.Difficulty * 7;
            var catalog = GameContent.LoadCatalog();
            Curtain.Progress(0.05f);
            yield return null;
            // A campaign mission names its own battlefield and version of it.
            var mission = !_menu && kind == GameModeKind.Campaign ? Campaign.Get(MatchSettings.Mission) ?? Campaign.All[0] : null;
            var mapFile = mission != null ? mission.Map + "_" + mission.Variant : kind == GameModeKind.Sandbox ? SandboxSession.Scenario.Map
                : ModeSession.MapFile(kind, MatchSettings.CurrentMap.Id);
            // A mission that returns to a map from the other side plays it reversed.
            var map = mission != null ? Campaign.LoadMap(mission) : kind == GameModeKind.Sandbox ? SandboxSession.LoadMap(SandboxSession.Scenario) : GameContent.LoadMap(mapFile);
            _world = new SimWorld(catalog, map, seed);
            // Tower-branch C.2: towers show their card's rank, the player's from the profile and the other
            // side's from its HQ level (1, 3, 5 ...); the menu's backdrop battle shows none.
            var ranked = _world;
            TowerArt.Ranks = _menu ? null : (team, card) => team == PlayerTeam ? PlayerProfile.Rank(card)
                : Mathf.Clamp(2 * (ranked.Bases.Of(team)?.Loadout.HqLevel ?? 1) - 1, 1, TowerArt.MaxBars);
            Curtain.Progress(0.1f);
            yield return null;
            // The player's arsenal: card ranks and equipment toughen and sharpen their own vehicles and strikes.
            // Prompt 31 L1: a fixed deck's cards fight at the campaign's rank curve with no equipment (MissionDecks).
            if (!_menu && kind != GameModeKind.Sandbox)
            {
                if (MissionDecks.IsFixed(mission))
                    _world.SetBoosts(PlayerTeam, unit => MissionDecks.BoostFor(mission, unit), card => MissionDecks.StrikeBoost(mission, card), strikeRank: card => MissionDecks.Rank(mission, card));
                else _world.SetBoosts(PlayerTeam, PlayerProfile.BoostFor, PlayerProfile.StrikeBoost, strikeRank: PlayerProfile.Rank);
            }
            // Prompt 22 F: the player's commander (a story mission's own, else the one picked; every mode) and the passive of
            // the general a mission is tied to, through the loadout's caps. The Sandbox sets each side's from its scenario.
            _world.SetStatCaps(GearCatalog.StatCap, GearCatalog.TowerStatCap);
            _playerCommander = _menu || kind == GameModeKind.Sandbox ? null : CommanderPick.ForBattle(mission);
            if (!_menu && kind != GameModeKind.Sandbox)
            {
                _world.SetCommander(PlayerTeam, _playerCommander);
                _world.SetCommander(EnemyTeam, CommanderPick.EnemyFor(mission));
            }
            // A campaign enemy keeps pace with the arsenal as it grows (its boss and towers too).
            if (mission != null)
            {
                var deck = new List<VehicleBoost>();
                // The commander's lines count towards the army's strength like its equipment (prompt 22 F.1).
                foreach (var id in MissionDecks.Deck(mission, MatchSettings.DeckVehicles))
                    if (catalog.Vehicles.TryGetValue(id, out var def)) deck.Add(CommanderRules.Merge(MissionDecks.BoostFor(mission, def), _playerCommander, def, GearCatalog.StatCap));
                // Prompt 26 A.4: ... but its bosses do not (their health is set by the target time).
                _world.BossesUnscaled = true;
                var edge = EnemyScaling.Match(deck, catalog.EnemyScaling);
                // The elite budget is part of that pace, not on top of it (prompt 8 H).
                edge = EnemyScaling.WithElites(edge, catalog.Elites.PowerEdge(catalog.Elites.BudgetFor(ModeSession.EliteKey(mission.Difficulty, MatchSettings.MissionTier))));
                _world.SetBoosts(1, _ => edge, _ => edge.Damage, everything: true);
            }
            // Play-test 6 (DECISIONS 21G): a quick mode's enemy keeps pace too, by its difficulty's share.
            else if (!_menu && kind != GameModeKind.Sandbox)
            {
                var deck = new List<VehicleBoost>();
                foreach (var id in MatchSettings.DeckVehicles)
                    if (catalog.Vehicles.TryGetValue(id, out var def)) deck.Add(PlayerProfile.BoostFor(def));
                ModeSession.KeepPace(_world, deck, MatchSettings.Difficulty, kind);
                // Prompt 26 E.1: a Boss Hunt's P, estimated once from the carried deck (a resumed run brings its own).
                if (kind == GameModeKind.BossRush) BossRushSession.Power = HuntPower.ForDeck(catalog, MatchSettings.DeckVehicles, _playerCommander);
            }
            _session = ModeSession.Create(kind, _menu, _world, seed);
            _stuck = _menu ? null : StuckReporter.Create(mapFile, kind, seed);
            if (!_menu && kind != GameModeKind.Sandbox) ApplyRankDiscounts(catalog, mission);
            // Prompt 21 A.2: nothing in the Sandbox counts towards today's challenges.
            DailyMissions.Suspended = kind == GameModeKind.Sandbox && !_menu;
            StartDialogue();
            if (!_menu && _session is MissionSession storySession)
            {
                _radio = new RadioDirector(storySession.Def, seed);
                _radio.Spoke += line => Say(line.Key, line.Priority, line.Team, line.Moment, line.Unit, speaker: line.Speaker);
                _radio.GeneralAppeared += general =>
                {
                    // A general's first words: the camera goes to their camp for a moment.
                    if (_world.Bases.Of(EnemyTeam) is { } camp && camp.Hq.IsValid) StoryPan(camp.HqPosition);
                    else if (_world.TryGetRally(EnemyTeam, out var rally)) StoryPan(rally);
                };
            }
            Curtain.Progress(0.15f);
            yield return null;
            // A campaign tier holds for the one mission it was chosen for.
            if (kind != GameModeKind.Campaign) MatchSettings.MissionTier = 0;
            _clock = new SimClock();
            // The player's switches as the battle starts, so a replay starts from the same ones.
            MatchJournal.Inputs.Clear();
            var resume = MatchJournal.Pending;
            MatchJournal.Pending = null;
            if (!_menu && _session.PlayerAi != null)
            {
                MatchJournal.Record(_world, "autoDeploy", _session.PlayerAi.AutoDeploy ? "1" : "0");
                MatchJournal.Record(_world, "autoStrike", _session.PlayerAi.AutoStrike ? "1" : "0");
                // Prompt 28 H.4, H.10, K.2: the picked tactic, the per-squad presets, Normal skill (ModeSession.Tactics.cs).
                if (kind != GameModeKind.Sandbox)
                {
                    _session.PreparePlayerAi(_world, kind, _playerCommander);
                    MatchJournal.Record(_world, "tactic.start", _session.PlayerAi.Tactic ?? "");
                    MatchJournal.Record(_world, "squad.presets", _session.SquadPresetsText);
                }
            }
            // Back to a checkpoint: the battle so far, replayed behind the loading screen.
            if (resume != null && !_menu && mission != null && resume.Mission == mission.Id)
            {
                var replay = Replay(resume);
                while (replay.MoveNext()) yield return replay.Current;
            }

            var worldRoot = new GameObject("Battlefield").transform;
            _materials = new MaterialLibrary();
            _meshes = new MeshLibrary();
            _models = new ModelLibrary(_materials);
            ApplySkin(PlayerProfile.EquippedSkin);
            PlayerProfile.Changed += OnProfileChanged;
            var theme = MapTheme.For(map.Theme);
            if (theme.ModelGrass.HasValue) _materials.ForModel("Grass", -1).SetColor("_BaseColor", theme.ModelGrass.Value);
            _map = new MapView(_world, _models, _materials, theme, worldRoot, options.Shadows);
            // Buildings already down before the battle (the weekly fortress's broken rings) show as rubble.
            foreach (var prop in _world.Props)
                if (!prop.IsAlive) _map.TryDestroy(prop.Id, out _);
            Curtain.Progress(0.4f);
            yield return null;
            _surroundings = new Surroundings(_world, _models, _materials, theme, worldRoot, options);
            _views = new ViewRegistry(_models, _meshes, _materials, worldRoot, PlayerTeam);
            // A replayed battle's vehicles were raised with nobody watching: their views are made now.
            if (_resumed)
                foreach (var v in _world.Vehicles)
                    if (v.IsAlive) _views.Add(v);
            _playArea = new PlayAreaView(_materials, worldRoot);
            _playArea.Show(_world.PlayArea);
            if (_session.Objectives != null && _session.Objectives.Points.Count > 0)
                _objectives = new ObjectiveView(_session.Objectives, _meshes, _materials, worldRoot);
            if (_session is MissionSession) _markers = new MissionMarkers(_meshes, _materials, worldRoot);
            // Prompt 30 L6: the neutral sites and the supply drop's landing spot on the field.
            if (!_menu) _neutralSites = new NeutralSiteView(_meshes, _materials, worldRoot);

            _world.TryGetRally(PlayerTeam, out var rally);
            // Prompt 17 A.4: a long battlefield is seen looking west (its length across the screen), from a little further
            // out, and may be zoomed further out; the view starts ahead of the rally towards the enemy.
            var longMap = map.IsLong;
            var ahead = longMap ? new Vector3(0f, 0f, 22f) : new Vector3(16f, 0f, 16f);
            var start = _menu ? new Vector3(map.Centre.X, 0f, map.Centre.Y) : new Vector3(rally.X, 0f, rally.Y) + ahead;
            _camera = new RtsCamera(Camera.main, new Vector2(map.Min.X, map.Min.Y), new Vector2(map.Max.X, map.Max.Y), start,
                _menu ? 30f : longMap ? LongZoom : 19f, longMap ? RtsCamera.LongYaw : RtsCamera.SquareYaw)
            {
                ShakeScale = MatchSettings.ShakeScale,
            };
            if (longMap) _camera.MaxZoom = LongMaxZoom;
            FitCameraToArea();
            _attractFocus = start;
            // Device check of the scenery: the north-west corner, zoomed right out.
            // Device check of the whole battlefield: its outline, terrain and objectives in one view.
            if (DebugFlags.Has("-mb-overview"))
            {
                _camera.MaxZoom = 95f;
                _camera.ZoomBy(0.05f, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                _camera.FocusOn(new Vector3(map.Centre.X, 0f, map.Centre.Y));
                _lastInput = float.MaxValue;
            }
            // Device check at a chosen zoom (-mb-zoom=42: the widest the player can go).
            if (float.TryParse(DebugFlags.Value("-mb-zoom="), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var zoom) && zoom > 0f)
            {
                _camera.MaxZoom = Mathf.Max(_camera.MaxZoom, zoom);
                _camera.ZoomBy(_camera.Zoom / zoom, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
            }
            if (!_menu) _crowd = CrowdCheck.Create(_world, start);
            if (DebugFlags.Has("-mb-far"))
            {
                _camera.ZoomBy(0.1f, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                // The north-west edge: the boundary line and the country beyond it.
                _camera.FocusOn(new Vector3(map.Min.X + map.Width * 0.1f, 0f, map.Max.Y - map.Length * 0.1f));
                _lastInput = float.MaxValue;
            }
            _effects = new EffectsDirector(catalog, _materials, _meshes, _models, _camera, worldRoot,
                options.MaxEffects ? EffectBudget.High : EffectBudget.Eco);
            _effects.SetMapBounds(new Vector3(map.Centre.X, 0f, map.Centre.Y), map.Width * 0.5f, map.Length * 0.5f);
            // Build every vehicle's merged model and the munitions now, not on first use mid-battle.
            // Build the merged models of every vehicle this battle can field now, not on first use
            // mid-battle, and only those: the catalogue holds bosses, elites and defences most
            // battles never see, and every merged model costs load time and memory on a phone.
            var fieldable = new List<string>(Fieldable(catalog, mission));
            for (var i = 0; i < fieldable.Count; i++)
            {
                _models.Prewarm(catalog.Vehicles[fieldable[i]].Model);
                if (i % 6 != 5) continue;
                Curtain.Progress(0.45f + 0.3f * i / fieldable.Count);
                yield return null;
            }
            if (_models.Has("strike_jet")) _models.Prewarm("strike_jet");
            // The transport that flies reinforcements in (see AirDrops).
            if (_models.Has("sky_gunship")) _models.Prewarm("sky_gunship");
            if (_models.Has(Effects.AirDrops.TransportModel)) _models.Prewarm(Effects.AirDrops.TransportModel);
            _effects.Prewarm();
            Curtain.Progress(0.85f);
            yield return null;
            // The menu battle has no player side, so no alarms or chimes.
            _audio = new AudioDirector(_camera, worldRoot, catalog, _menu ? -1 : PlayerTeam);
            // The soundtrack: the menu theme, the siege track for fortress battles, else a battle track.
            var fortress = MatchSettings.Mode is GameModeKind.Siege or GameModeKind.Defend or GameModeKind.Endless;
            _music = MusicDirector.Play(_menu ? MusicDirector.Mood.Menu : fortress ? MusicDirector.Mood.Siege : MusicDirector.Mood.Battle,
                System.Environment.TickCount);
            UiKit.Clicked += _audio.Click;
            var weather = _menu ? WeatherKind.Clear
                // An Operations mutator's weather over the mission's own.
                : mission != null && MatchSettings.Run?.Mission == mission.Id && System.Enum.TryParse<WeatherKind>(MatchSettings.Run.Weather, out var mutated) ? mutated
                : mission != null && System.Enum.TryParse<WeatherKind>(mission.Weather, out var missionWeather) ? missionWeather
                : kind == GameModeKind.Sandbox && !_menu ? SandboxSession.WeatherOf(SandboxSession.Scenario)
                : MatchSettings.ResolveWeather(seed);
            // A clear day still has the map's own air: warm desert haze, cold snow light, sea mist.
            _weather = new Weather(weather, _atmosphere, _materials, _camera, _audio, worldRoot, options.MaxEffects, theme.Cast, theme.Haze);
            _weatherKind = weather;
            _effects.Night = weather == WeatherKind.Night;
            _session.SetNight(weather == WeatherKind.Night);
            // Prompt 25 F2 batch A: searchlights and flare towers light the dark (night, fog, a sandstorm).
            _world.SetDarkness(weather is WeatherKind.Night or WeatherKind.Fog or WeatherKind.Sandstorm);
            if (!_menu && _session.Mode is MachineBrigade.Sim.Modes.SiegeMode siegeMode && _world.Map.Fortress != null)
            {
                _fortress = new FortressView(_world, siegeMode, _models, _materials, _effects, worldRoot, PlayerTeam);
                _fortress.SetNight(weather == WeatherKind.Night);
                // The objectives' shields are the defender's (blue when the player holds the fortress).
                _map.ShieldTeam = siegeMode.Defender;
                _map.PlayerTeam = PlayerTeam;
            }
            _worldRoot = worldRoot;
            _richEffects = options.MaxEffects;
            _crates = new CrateViews(_models, worldRoot);
            _mineViews = new MineViews(_models, worldRoot, _menu ? -1 : PlayerTeam);
            // Quick battles sometimes turn: a storm rolls in, the fog comes down, night falls.
            if (!_menu && mission == null && kind != GameModeKind.Sandbox) _nextWeatherShift = 150 + new System.Random(seed).NextDouble() * 120;
            ApplyPost(options.Bloom, MatchSettings.Brightness);
            _views.BlobShadows = options.Shadows == ShadowLevel.Off;

            // The Sandbox has no deck along the bottom: its own screen places and calls everything.
            var cards = _menu ? null : kind == GameModeKind.Sandbox ? PlayerCommander.Cards(_world, new List<string>(), new List<string>())
                : PlayerCommander.Cards(_world, MissionDecks.Vehicles(catalog, mission, MatchSettings.DeckVehicles, PlayerProfile.IsUnlocked),
                    MissionDecks.Supports(mission, MatchSettings.DeckSupports));
            var hudSpec = _session.Hud;
            if (!_menu)
            {
                // The standing hint shows in the player's first few matches only (prompt 11 A7).
                hudSpec.StartHint = MatchSettings.ShowStartHint;
                MatchSettings.CountHintMatch();
            }
            _hud = new BattleHud(hudSpec, cards, catalog)
            {
                ShowFps = MatchSettings.ShowFps,
            };
            // The menu's vehicle detail page shows the model on a turntable.
            if (_menu)
            {
                _preview = new UnitPreview(catalog, _materials, _meshes, _models, worldRoot);
                _hud.MenuPreview = _preview;
                _preview.Audio = _audio;
                RangeCapture.TryStart(gameObject, _preview, catalog);
            }
            if (!_menu) _effects.Flash = strength => _hud?.Flash(strength);
            if (_hud.Minimap != null)
            {
                _hud.Minimap.Ground = theme.Minimap;
                _hud.Minimap.SetPicture(_map.MinimapTexture, new Vector2(map.Min.X, map.Min.Y), new Vector2(map.Max.X, map.Max.Y), _camera.Yaw);
            }
            _selection = new SelectionController(_world, _views, _camera, _map, PlayerTeam);
            if (!_menu)
            {
                // Items bought with coins come along into every real match.
                if (_session is not SandboxSession && _world.TryGetEconomy(PlayerTeam, out var economy))
                    foreach (var item in Progression.Items)
                    {
                        var owned = PlayerProfile.ItemCount(item);
                        if (owned > 0) economy.Items[item] = owned;
                    }
                _commander = new PlayerCommander(_world, _hud, _camera, PlayerTeam, cards);
                if (_session is SandboxSession sandboxSession)
                {
                    // Prompt 21: taps place and select, a drag from a unit turns it, the camera pans and zooms as ever.
                    _sandbox = new SandboxController(_world, sandboxSession, _views, _camera, _selection, _materials, _meshes, worldRoot);
                    _gestures = new TouchGestures(_sandbox, p => _hud.IsOverUi(p) || _sandbox.IsOverUi(p)) { BoxMode = _sandbox.DragTurns };
                }
                else
                {
                    _selection.TapInterceptor = _commander.TryTap;
                    _gestures = new TouchGestures(_selection, _hud.IsOverUi) { BoxMode = () => _selection.BoxMode };
                }
                if (isActiveAndEnabled) _gestures.Enable();
            }
            Wire();
            WireDialogue();
            // Prompt 22 F.4: the commander's face beside pause, and its first words (prompt 23 H: an event line, on our side).
            if (!_menu && _playerCommander != null && _hud != null)
            {
                _hud.ShowCommanderBadge(_playerCommander);
                if (!_resumed) Say(new DialogueLine("cmdr." + _playerCommander.Id + ".radio.start", DialoguePriority.Event, _playerCommander.Portrait, enemy: false));
            }

            DispatchEvents();
            // Built: lift the curtain once this scene has drawn a few frames.
            _built = true;
            Curtain.Progress(1f);
            Curtain.Open();
        }

        /// <summary>Prompt 22 F: the player's commander in this battle (null in the menu and the Sandbox).</summary>
        private CommanderDef _playerCommander;

        /// <summary>-mb-killboss: when each boss was first seen.</summary>
        private readonly Dictionary<MachineBrigade.Sim.Core.EntityId, float> _bossSeen = new();

        private bool BossOnField()
        {
            foreach (var v in _world.Vehicles)
                if (v.IsAlive && v.Def.Boss && v.Team == EnemyTeam) return true;
            return false;
        }

        /// <summary>Prompt 20: a main boss on the field plays its own track (else its rank's); mini bosses alone, theirs.</summary>
        private string BossTrack()
        {
            string track = null;
            foreach (var v in _world.Vehicles)
            {
                if (!v.IsAlive || !v.Def.Boss || v.Team != EnemyTeam) continue;
                var own = v.Def.Music ?? v.Def.RankDef?.Music ?? "boss";
                if (!v.Def.MiniBoss) return own;
                track ??= own;
            }
            return track ?? "boss";
        }

        /// <summary>The weather turns mid-battle, to another of this map's weathers.</summary>
        private void ShiftWeather()
        {
            _nextWeatherShift = double.MaxValue;
            var choices = MatchSettings.CurrentMap.Weathers;
            if (choices == null || choices.Length < 2) return;
            var next = _weatherKind;
            var random = new System.Random((int)_world.Tick);
            for (var i = 0; i < 8 && next == _weatherKind; i++) next = choices[random.Next(choices.Length)];
            if (next == _weatherKind) return;
            ShiftWeatherTo(next, 0f);
            _hud.Toast(Strings.Format("toast.weather", Strings.Get("menu." + next.ToString().ToLowerInvariant())), seconds: 3f, kind: NoticeKind.Weather);
        }

        /// <summary>The new weather rolls in over <paramref name="seconds"/> (0: the usual few) while the old one thins out (see Weather).</summary>
        private void ShiftWeatherTo(WeatherKind next, float seconds)
        {
            if (next == _weatherKind || _weather == null) return;
            _leavingWeather?.Dispose();
            _leavingWeather = _weather;
            _weatherKind = next;
            var theme = MapTheme.For(_world.Map.Theme);
            _weather = new Weather(next, _atmosphere, _materials, _camera, _audio, _worldRoot, _richEffects, theme.Cast, theme.Haze, _leavingWeather, seconds);
            _effects.Night = next == WeatherKind.Night;
            _session.SetNight(next == WeatherKind.Night);
            _world.SetDarkness(next is WeatherKind.Night or WeatherKind.Fog or WeatherKind.Sandstorm);
            _fortress?.SetNight(next == WeatherKind.Night);
        }

        /// <summary>Vehicles that can appear this battle: both decks (and their elite versions), units on the
        /// field, the mission's boss, waves and placed units, fire-support escorts and every summon.</summary>
        private HashSet<string> Fieldable(Catalog catalog, MissionDef mission)
        {
            var ids = new HashSet<string>();
            void Add(string id)
            {
                if (id == null || !catalog.Vehicles.TryGetValue(id, out var def) || !ids.Add(id)) return;
                if (catalog.EliteVariant(id) is { } elite) Add(elite);
                foreach (var skill in def.Skills)
                    if (skill.Unit != null) Add(skill.Unit);
                // A boss's guards and the troops it lands (prompt 8).
                foreach (var guard in def.Guards) Add(guard.Def);
                if (def.Landing != null) foreach (var unit in def.Landing.Units) Add(unit);
                // A flagship's fleet, its landing craft and what they carry, its aircraft (prompt 16).
                foreach (var ship in def.Fleet) Add(ship.Unit);
                foreach (var wave in def.AirWaves) foreach (var unit in wave.Units) Add(unit);
                if (def.Craft != null)
                {
                    Add(def.Craft.Unit);
                    foreach (var unit in def.Craft.Carries) Add(unit);
                }
                // Its escorts (prompt 16 F).
                if (catalog.Escorts.TryGetValue(id, out var escort))
                {
                    if (escort.Arrive != null) foreach (var u in escort.Arrive.Units) Add(u.Unit);
                    foreach (var wave in escort.Phases) foreach (var u in wave.Units) Add(u.Unit);
                }
            }
            for (var team = 0; team <= 1; team++)
                if (_world.TryGetEconomy(team, out var economy))
                {
                    if (economy.Vehicles.Count == 0) foreach (var id in catalog.Vehicles.Keys) Add(id);
                    foreach (var id in economy.Vehicles) Add(id);
                }
            foreach (var v in _world.Vehicles) Add(v.Def.Id);
            foreach (var support in catalog.Supports.Values)
                foreach (var unit in support.Units) Add(unit);
            if (mission != null)
            {
                Add(mission.Boss?.Def);
                // Prompt 20: a boss slot pass 2 has not built is fought as its stand-in.
                Add(mission.Boss?.Fallback);
                Add(mission.Convoy?.Def);
                if (mission.Waves != null) foreach (var id in mission.Waves.Roster) Add(id);
                foreach (var u in mission.Units) Add(u.DefId);
                // Prompt 31: a fixed deck's placed allies (and the stand-ins of those still being modelled).
                if (mission.FixedDeck != null)
                    foreach (var ally in mission.FixedDeck.PlacedAllies)
                    {
                        Add(ally.Def);
                        Add(ally.Fallback);
                    }
            }
            // Boss Rush brings its bosses and their escorts later.
            if (MatchSettings.Mode == GameModeKind.BossRush && !_menu)
            {
                foreach (var boss in BossRushRules.Everyone()) Add(boss);
                // Prompt 20 N: the hunts bring every chapter's bosses.
                foreach (var boss in BossHunts.Story) Add(boss.Id);
            }
            return ids;
        }

        /// <summary>
        /// Ranked cards cost the player less to call (rank 7: -5 %, rank 9: -10 %; see
        /// CardRanks.CallCost). In the campaign the enemy gets 80 % of the deck's average cut as
        /// extra income, as it gets 80 % of the arsenal's edge.
        /// </summary>
        private void ApplyRankDiscounts(Catalog catalog, MissionDef mission)
        {
            if (!_world.TryGetEconomy(PlayerTeam, out var mine)) return;
            var campaign = mission != null;
            float full = 0f, paid = 0f;
            void Card(string id, int cost)
            {
                // Prompt 31 L1: a fixed deck's cards at its fixed rank.
                var price = CardRanks.CallCost(cost, MissionDecks.Rank(mission, id));
                if (price < cost) mine.Discounts[id] = cost - price;
                full += cost;
                paid += price;
            }
            foreach (var id in MissionDecks.Deck(mission, MatchSettings.DeckVehicles))
                if (catalog.Vehicles.TryGetValue(id, out var v)) Card(id, v.CpCost);
            foreach (var id in MissionDecks.SupportDeck(mission, MatchSettings.DeckSupports))
                if (catalog.TryGetSupport(id, out var s)) Card(id, s.CpCost);
            if (campaign && full > 0f && paid < full && _world.TryGetEconomy(1, out var foe))
                foe.ScaleIncome(1f + 0.8f * (1f - paid / full));
        }

        private string _builtGraphics;

        /// <summary>Everything that needs a rebuild to take effect.</summary>
        private static string GraphicsSignature()
        {
            var o = MatchSettings.Options;
            return $"{o.Shadows}|{o.RenderScale}|{o.AntiAliasing}|{o.FrameRate}|{o.Bloom}|{o.RichScenery}|{o.MaxEffects}|" +
                   $"{MatchSettings.UiSize}|{MatchSettings.SavingBattery}|{MatchSettings.Brightness}|{MatchSettings.ColorBlind}";
        }

        /// <summary>
        /// Glow level and brightness on this match's copy of the volume profile. Low glow starts
        /// at quarter resolution with four passes and the cheap dual filter (the mobile recipe);
        /// high glow at half resolution with six.
        /// </summary>
        private static void ApplyPost(int bloomLevel, int brightness)
        {
            foreach (var volume in FindObjectsByType<UnityEngine.Rendering.Volume>())
            {
                var profile = volume.profile;
                if (profile.TryGet<UnityEngine.Rendering.Universal.Bloom>(out var bloom))
                {
                    bloom.active = bloomLevel > 0;
                    var low = bloomLevel == 1;
                    bloom.downscale.Override(low ? UnityEngine.Rendering.Universal.BloomDownscaleMode.Quarter
                        : UnityEngine.Rendering.Universal.BloomDownscaleMode.Half);
                    bloom.maxIterations.Override(low ? 4 : 6);
                    bloom.filter.Override(low ? UnityEngine.Rendering.Universal.BloomFilterMode.Dual
                        : UnityEngine.Rendering.Universal.BloomFilterMode.Gaussian);
                    bloom.highQualityFiltering.Override(!low && !Application.isMobilePlatform);
                }
                if (brightness != 100 && profile.TryGet<UnityEngine.Rendering.Universal.ColorAdjustments>(out var colour))
                    colour.postExposure.Override(colour.postExposure.value + Mathf.Log(brightness / 100f, 2f));
            }
        }

        private static void ApplyDebugFlags()
        {
            // URP copies its asset's setting into GraphicsSettings every frame, so switch the asset.
            if (DebugFlags.Has("-mb-no-srpbatcher") && GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)
                urp.useSRPBatcher = false;
            if (DebugFlags.Has("-mb-no-shadows"))
                foreach (var light in FindObjectsByType<Light>())
                    if (light.type == LightType.Directional) light.shadows = LightShadows.None;
            if (DebugFlags.Has("-mb-no-post") && Camera.main != null)
                Camera.main.GetUniversalAdditionalCameraData().renderPostProcessing = false;
        }

        private void OnEnable() => _gestures?.Enable();

        private void OnDisable() => _gestures?.Disable();

        /// <summary>The battle is built (see <see cref="Start"/>): until then nothing ticks.</summary>
        private bool _built;

        private void Update()
        {
            if (!_built) return;
            // No battlefield input under the pause and result screens.
            if (!_paused && !_resultShown && !_presenting) _gestures?.Tick(Time.unscaledTime);
            // Android's back button arrives as Escape: close a menu page, or pause and resume.
            if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
            {
                if (_menu) _hud.MenuBack();
                else if (_commander?.ArmedSupport != null) _commander.Disarm();
                // Prompt 30 L3: during the match end, Back skips it (after 0.75 s) instead of pausing.
                else if (_presenting) _world.Ending.Skip();
                else if (!_resultShown) SetPaused(!_paused);
            }
            _frameRate.Tick();
            _frameRateTarget = _frameRate.Target;
            if (!RangeCapture.Active) _preview?.Tick(Time.unscaledDeltaTime);
            // A menu page covering the whole lobby: its battle rests and its camera stops drawing.
            var covered = _menu && _hud.MenuCoversBattle;
            if (covered != _lobbyCovered)
            {
                _lobbyCovered = covered;
                RestLobbyCamera(covered);
            }
            // Menus and pause draw every other frame until touched: the battle behind them keeps
            // moving, the phone does half the work.
            UnityEngine.Rendering.OnDemandRendering.renderFrameInterval =
                (_menu || _paused) && !(Touchscreen.current?.primaryTouch.press.isPressed ?? false) &&
                !(Mouse.current?.leftButton.isPressed ?? false) ? 2 : 1;

            // A cinematic moment slows the whole battle (sim, particles) for a second.
            // Prompt 23 H.8: a story moment slows it too (the slower of the two wins).
            // Prompt 30 L3: during the match end the pace is the presentation's (TickEnding), for the pictures only.
            if (!_paused && !_resultShown && !_presenting) Time.timeScale = Mathf.Min(_cinematics.TimeScale(Time.unscaledTime), DialogueTimeScale);
            _hud.SetLetterbox(Mathf.Max(_cinematics.Letterbox(Time.unscaledTime), EndingLetterbox));
            // Prompt 30 L3: once the world is resolved nothing of the battle is stepped (mode, AI, Sim): the time scale reaches
            // only what is drawn, so the end's slow motion is the view's clock alone.
            var frozen = _world.Ending.Phase != MatchPhase.Running;
            var steps = _paused || _lobbyCovered || frozen ? 0 : _sandbox != null ? _sandbox.Steps(Time.deltaTime, _clock) : _clock.Advance(Time.deltaTime);
            var dt = (float)_clock.StepSeconds;
            _perf?.CountSteps(steps);
            for (var i = 0; i < steps; i++)
            {
                _perf?.Begin();
                _session.Mode.Tick(_world, dt);
                _session.TickAi(_world, dt);
                _world.Step(dt);
                _stuck?.Observe(_world);
                _views.SnapshotAll();
                _perf?.End(PerfProbe.Section.Sim);
                _perf?.Begin();
                DispatchEvents();
                _perf?.End(PerfProbe.Section.Events);
            }

            if (_crowd != null && !_paused)
            {
                // The crowd check holds the view on the two armies.
                _crowd.Tick(_world, Time.time);
                _lastInput = Time.unscaledTime;
            }
            if (!_menu && !_paused && DebugFlags.Has("-mb-demolish") && Time.time >= _demolishAt) Demolish();
            if (!_menu && !_paused && _fortress != null && Time.time >= _fortressCheckAt) FortressCheck();
            if (!_menu && !_paused && DebugFlags.Has("-mb-towerwatch")) WatchTower();
            if (!_menu && !_paused && DebugFlags.Has("-mb-bastion")) WatchBastion();
            if (!_menu && !_paused && DebugFlags.Has("-mb-smokescreen") && Time.time >= _smokeAt)
            {
                // Device check: a smoke screen in the thick of the fight every few seconds.
                _smokeAt = Time.time + 9f;
                _effects.DebugSmokeScreen(_camera.Focus + new Vector3(UnityEngine.Random.Range(-6f, 6f), 0f, UnityEngine.Random.Range(-6f, 6f)));
            }
            if (_presenting) EndingCamera();
            else if (_cinematics.Active(Time.unscaledTime))
            {
                if (!_viewTaken) _camera.Glide(_cinematics.Focus, _cinematicZoom, Time.unscaledDeltaTime, 2.5f);
            }
            else if (_menu) Attract();
            else if (Time.unscaledTime < _storyUntil) _camera.Follow(_storyFocus, Time.unscaledDeltaTime, 0.7f);
            // Play-test 6: after a boss's shot the view goes back to where the player had it, at their zoom.
            else if (_camera.Held) _camera.ReturnHeld(Time.unscaledDeltaTime);
            else if (_sandbox == null) FollowTheFight();
            if (_radio != null && _session is MissionSession radioSession && !_paused) _radio.Tick(_world, radioSession);
            TickDialogue();
            _selection.Tick();
            _sandbox?.Tick(Time.unscaledDeltaTime);
            _perf?.Begin();
            if (!_paused)
            {
                _effects.Tick(_views);
                _weather.Presence = StormPresence();
                _weather.Tick();
                if (_leavingWeather != null && !_leavingWeather.TickLeaving())
                {
                    _leavingWeather.Dispose();
                    _leavingWeather = null;
                }
                // A boss on the field: the boss track (the old war-drum loop stays silent).
                if (!_menu && Time.frameCount % 15 == 0)
                {
                    _music.BossTrack = BossTrack();
                    _music.Boss = BossOnField();
                }
                // Device check of a boss's death: it goes down after twelve seconds on the field.
                if (!_menu && DebugFlags.Has("-mb-killboss") && Time.frameCount % 15 == 0)
                    foreach (var v in _world.Vehicles)
                        if (v.IsAlive && v.Def.Boss && _bossSeen.TryAdd(v.Id, Time.time) is var first && Time.time - _bossSeen[v.Id] > 12f)
                        {
                            _camera.FocusOn(new Vector3(v.Position.X, 0f, v.Position.Y));
                            _lastInput = float.MaxValue;
                            _world.DebugDamage(v, 5f);
                        }
                if (_world.Time >= _nextWeatherShift) ShiftWeather();
            }
            _perf?.End(PerfProbe.Section.Effects);
            _perf?.Begin();
            _audio.Tick(_views);
            _perf?.End(PerfProbe.Section.Audio);
            _perf?.Begin();
            _commander?.Update();
            _hud.Tick();
            UpdateStatus();
            CheckResult();
            TickEnding();
            TickEndless();
            _perf?.End(PerfProbe.Section.Hud);
        }

        private void LateUpdate()
        {
            if (!_built) return;
            _camera.Apply(Time.unscaledDeltaTime);
            _atmosphere.FitShadows(_camera.Camera);
            _perf?.Begin();
            _views.Render(_clock.Alpha, _camera.Rotation);
            // Prompt 23 F.4 and F.5: the Accord's marks and the generals' name labels (MatchRunner.EventHud.cs).
            TickEventHud();
            // Prompt 16: ships' wakes (and a ship that got away, hidden).
            if (_world.Map.Sea != null)
            {
                _wakes ??= new WakeView(_materials, null, MatchSettings.Options.Shadows <= ShadowLevel.Low);
                _wakes.Update(_world, _views);
            }
            // Rounds leave from the barrels as they have just been drawn.
            _effects.LaunchShots(_views);
            _perf?.End(PerfProbe.Section.Views);
            _perf?.Begin();
            _objectives?.Render(Time.time);
            _neutralSites?.Render(_world, Time.time);
            if (_markers != null && _session is MissionSession mission)
            {
                mission.Mission.Marks(_world, _marks);
                _markers.Render(_marks, _views, _map, _camera.Rotation, Time.time);
            }
            _effects.Draw();
            if (!DebugFlags.Has("-mb-no-scenery")) _surroundings.Draw();
            _map.Animate(Time.time);
            _map.DrawShields(_camera.Rotation, Time.time);
            _fortress?.Tick(Time.time, Time.deltaTime);
            _crates?.Update(_world);
            _mineViews?.Update(_world);
            _perf?.End(PerfProbe.Section.Scenery);
            _perf?.EndFrame(_views.All.Count);
            if (_perf != null && !_censusDone && Time.time > 6f)
            {
                _censusDone = true;
                _perf.Census(_surroundings.InstancedTriangles, _surroundings.Batches);
            }
        }

        private float _demolishAt = 8f;

        private float _fortressCheckAt = 1.5f;
        private int _fortressStep;

        /// <summary>
        /// Device checks of the siege set pieces (debug flags, one at a time): -mb-fortress looks over
        /// the walls and the keep; -mb-breach blows in the gate nearest the attackers and the wall
        /// beside it on camera; -mb-domedown takes out the relays, then the generators, so the dome
        /// drops; -mb-arrival brings the fortress's reinforcements in by its line; -mb-supergun has the
        /// super-gun fire in 12 s at the player's army.
        /// </summary>
        private void FortressCheck()
        {
            _fortressCheckAt = float.MaxValue;
            if (_session.Mode is not SiegeMode siege || _world.Map.Fortress is not { } fortress) return;
            var step = _fortressStep++;
            void Look(System.Numerics.Vector2 at, float zoom)
            {
                _camera.FocusOn(new Vector3(at.X, 0f, at.Y));
                _camera.ZoomBy(zoom, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                _lastInput = float.MaxValue;
            }
            if (DebugFlags.Has("-mb-fortress") && step == 0)
            {
                _camera.MaxZoom = 90f;
                Look(new System.Numerics.Vector2(70f, 70f), 0.4f);
            }
            if (DebugFlags.Has("-mb-breach"))
            {
                MachineBrigade.Sim.Entities.Prop gate = null;
                foreach (var (id, ring, _) in siege.Gates)
                    if (ring == 2 && _world.TryGetProp(id, out var g) && g.IsAlive && (gate == null || g.Position.X < gate.Position.X)) gate = g;
                if (gate == null) return;
                if (step == 0)
                {
                    Look(gate.Position, 1.6f);
                    _fortressCheckAt = Time.time + 3f;
                    return;
                }
                _world.DebugDestroyProp(gate);
                foreach (var prop in _world.Props)
                    if (prop.IsAlive && prop.Def.Id == "base_wall" && System.Numerics.Vector2.Distance(prop.Position, gate.Position) < 14f)
                        _world.DebugDestroyProp(prop);
            }
            if (DebugFlags.Has("-mb-domedown"))
            {
                if (step == 0)
                {
                    Look(siege.DomeCentre, 0.8f);
                    _fortressCheckAt = Time.time + 5f;
                    return;
                }
                foreach (var prop in _world.Props)
                    if (prop.IsAlive && (step == 1 ? prop.Def.Id == "radar_station" : prop.Def.Id == "shield_generator")) _world.DebugDestroyProp(prop);
                if (step == 1) _fortressCheckAt = Time.time + 2f;
            }
            if (DebugFlags.Has("-mb-arrival") && fortress.Arrival is { } line)
            {
                Look(line.Stop, 1.2f);
                siege.DebugReinforce(_world, "main_battle_tank", "ifv", "light_tank", "armored_car");
            }
            if (DebugFlags.Has("-mb-supergun") && step == 0)
            {
                siege.DebugFireSuperGunIn(_world, 12f);
                Look(siege.SuperGunAt, 0.7f);
            }
        }
        private MachineBrigade.Sim.Entities.Vehicle _watched;
        private float _watchHitAt, _watchUntil, _raidAt = 6f;

        /// <summary>
        /// Device check for fixed defences: the camera sits on one while it is shot down in steps
        /// (smoke, then fire, then the blast and the ruin), then moves on to the next.
        /// </summary>
        private void WatchTower()
        {
            if (_watched == null || (!_watched.IsAlive && Time.time > _watchUntil))
            {
                _watched = null;
                var focus = new System.Numerics.Vector2(_camera.Focus.x, _camera.Focus.z);
                var nearest = float.MaxValue;
                foreach (var v in _world.Vehicles)
                {
                    if (!v.IsAlive || !v.Def.Static || v.Invulnerable || v.Team == PlayerTeam) continue;
                    var d = System.Numerics.Vector2.Distance(v.Position, focus);
                    if (d >= nearest) continue;
                    nearest = d;
                    _watched = v;
                }
                if (_watched == null) return;
                _watchHitAt = Time.time + 3f;
            }
            _camera.FocusOn(new Vector3(_watched.Position.X, 0f, _watched.Position.Y));
            _lastInput = Time.unscaledTime;
            if (!_watched.IsAlive || Time.time < _watchHitAt) return;
            _watchHitAt = Time.time + 1.6f;
            _world.DebugDamage(_watched, 0.14f);
            if (!_watched.IsAlive) _watchUntil = Time.time + 14f;
        }

        /// <summary>Device check for the camp bastions: the camera on the player's, with an enemy raid every so often.</summary>
        private void WatchBastion()
        {
            MachineBrigade.Sim.Entities.Vehicle bastion = null;
            foreach (var v in _world.Vehicles)
                if (v.IsAlive && v.Team == PlayerTeam && v.Def.Id == MachineBrigade.Sim.Modes.BaseDefences.Bastion) bastion = v;
            if (bastion == null) return;
            _camera.FocusOn(new Vector3(bastion.Position.X, 0f, bastion.Position.Y));
            _lastInput = Time.unscaledTime;
            if (Time.time < _raidAt) return;
            _raidAt = Time.time + 18f;
            var at = bastion.Position + new System.Numerics.Vector2(20f, 20f);
            foreach (var id in new[] { "light_tank", "ifv", "armored_car", "attack_helicopter" })
                _world.SpawnVehicle(id, EnemyTeam, at + new System.Numerics.Vector2(UnityEngine.Random.Range(-6f, 6f), UnityEngine.Random.Range(-6f, 6f)), 3.9f);
        }
        private float _smokeAt = 10f;

        /// <summary>Device check for building collapses: every few seconds the building nearest the view comes down.</summary>
        private void Demolish()
        {
            _demolishAt = Time.time + 5f;
            var focus = new System.Numerics.Vector2(_camera.Focus.x, _camera.Focus.z);
            MachineBrigade.Sim.Entities.Prop best = null;
            var nearest = 70f;
            foreach (var prop in _world.Props)
            {
                if (!prop.IsAlive || !prop.Def.BlocksMovement || prop.Def.Indestructible || prop.Def.Width * prop.Def.Depth < 30f) continue;
                var d = System.Numerics.Vector2.Distance(prop.Position, focus);
                if (d >= nearest) continue;
                nearest = d;
                best = prop;
            }
            if (best == null) return;
            // Look at it first, so the collapse is in view.
            _camera.FocusOn(new Vector3(best.Position.X, 0f, best.Position.Y));
            _lastInput = Time.unscaledTime;
            _world.DebugDestroyProp(best);
        }

        /// <summary>
        /// A story moment (a boss or the enemy's reinforcements arriving, a general's first words):
        /// the camera pans there for a few seconds under the letterbox, unless the player is busy
        /// with the view; a touch hands it straight back.
        /// </summary>
        private void StoryPan(System.Numerics.Vector2 at, float seconds = 3.5f)
        {
            if (_menu || !_cinematics.Enabled || Time.unscaledTime - _lastInput < 2f) return;
            _storyFocus = new Vector3(at.X, 0f, at.Y);
            _storyUntil = Time.unscaledTime + seconds;
            _camera.StopFollowing();
            _camera.Hold();
        }

        /// <summary>
        /// The player panned or zoomed (or used the zoom buttons or the minimap): a story shot under way gives them the
        /// view at once and does not pull it back afterwards (play-test 6).
        /// </summary>
        private void TakeTheView()
        {
            _lastInput = Time.unscaledTime;
            _storyUntil = 0f;
            _viewTaken = true;
            _camera.Release();
            _camera.StopFollowing();
        }

        /// <summary>A slow-motion moment on a blast that is on screen.</summary>
        private void StartCinematic(System.Numerics.Vector2 at, bool force = false)
        {
            var point = new Vector3(at.X, 0f, at.Y);
            var viewport = _camera.Camera.WorldToViewportPoint(point);
            if (viewport.x < 0.05f || viewport.x > 0.95f || viewport.y < 0.05f || viewport.y > 0.95f) return;
            if (!_cinematics.Trigger(point, Time.unscaledTime, force)) return;
            Haptics.Pulse(70, 190);
            // Play-test 6: the shot keeps the player's zoom (it used to close in to 82 %) and gives the view back after.
            _camera.Hold();
            _viewTaken = false;
            _cinematicZoom = _camera.Zoom;
            _camera.AddTrauma(0.6f);
        }

        private string _previewSkin;

        private void ApplySkin(string id)
        {
            var skin = Skins.Get(id);
            _materials.ApplySkin(skin.Base, skin.Second, skin.Third, (int)skin.Pattern, skin.Scale, skin.Metallic, skin.Roughness);
        }

        private void OnProfileChanged()
        {
            if (_materials != null && _previewSkin == null) ApplySkin(PlayerProfile.EquippedSkin);
        }

        /// <summary>
        /// A menu page covers the lobby: its camera draws nothing but a plain clear (no scene, no
        /// post), which keeps the screen clean round the safe area and the phone cool; restored on return.
        /// </summary>
        private void RestLobbyCamera(bool rest)
        {
            var cam = Camera.main;
            if (cam == null) return;
            var data = cam.GetUniversalAdditionalCameraData();
            if (rest)
            {
                _lobbyMask = cam.cullingMask;
                _lobbyClear = cam.clearFlags;
                _lobbyPost = data.renderPostProcessing;
                cam.cullingMask = 0;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(0.067f, 0.078f, 0.094f);
                data.renderPostProcessing = false;
            }
            else
            {
                cam.cullingMask = _lobbyMask;
                cam.clearFlags = _lobbyClear;
                data.renderPostProcessing = _lobbyPost;
            }
        }

        private void OnDestroy()
        {
            _sandbox?.Screen.Dispose();
            DailyMissions.Suspended = false;
            _stuck?.Finish(_world);
            PlayerProfile.Changed -= OnProfileChanged;
            if (_audio != null) UiKit.Clicked -= _audio.Click;
            _perf?.Dispose();
            _leavingWeather?.Dispose();
            _weather?.Dispose();
            _effects?.Dispose();
            _fortress?.Dispose();
            _audio?.Dispose();
            _music?.Dispose();
            _views?.Dispose();
            _map?.Dispose();
            _surroundings?.Dispose();
            _hud?.Dispose();
            _meshes?.Dispose();
            _models?.Dispose();
            _materials?.Dispose();
            _atmosphere?.Dispose();
            Time.timeScale = 1f;
            AudioListener.pause = false;
        }

        /// <summary>An equipment proc: its word over the vehicle (not over an enemy the player cannot see).</summary>
        private void ShowTraitWord(in SimEvent e)
        {
            var word = GearText.Proc(e.DefId);
            if (word == null) return;
            Vector3 at;
            if (_views.TryGet(e.Entity, out var view))
            {
                if (e.Team != PlayerTeam && !view.Sim.IsVisibleTo(PlayerTeam)) return;
                at = view.Position + Vector3.up * 3.2f;
            }
            else at = new Vector3(e.Position.X, 3.2f, e.Position.Y);
            _hud.TraitWord(at, word, e.Team == PlayerTeam, _camera.Camera);
        }

        private void DispatchEvents()
        {
            foreach (var e in _world.Events)
            {
                switch (e.Kind)
                {
                    case SimEventKind.VehicleSpawned when _world.TryGetVehicle(e.Entity, out var vehicle):
                        _views.Add(vehicle);
                        // A boss comes onto the field: the camera goes to meet it.
                        if (!_menu && _sandbox == null && vehicle.Def.Boss && vehicle.Team == EnemyTeam) StoryPan(vehicle.Position, vehicle.Def.RankDef?.Intro ?? 3.5f);
                        EliteArrived(vehicle);
                        if (vehicle.Team == EnemyTeam) _tally.Saw(vehicle.Def);
                        if (!_menu && !_warnedAir && vehicle.Team == EnemyTeam && vehicle.Flying)
                        {
                            _warnedAir = true;
                            _hud.Toast(Strings.Get("toast.airDefence"), error: true, seconds: 3f, kind: NoticeKind.Air);
                        }
                        break;
                    case SimEventKind.VehicleDestroyed:
                        if (e.Team == PlayerTeam) _losses++;
                        else if (e.Team == EnemyTeam) _kills++;
                        NoteEndTarget(e);   // prompt 30 L3: the match end's last target
                        if (!_menu && e.Team == EnemyTeam && _world.Catalog.Vehicles.TryGetValue(e.DefId, out var slain))
                        {
                            DailyMissions.Record("kills");
                            if (slain.Elite) DailyMissions.Record("elites");
                            if (slain.Elite && !slain.Boss) _elitesSlain.Add(slain.EliteOf ?? slain.Id);
                            if (slain.Boss) DailyMissions.Record("bosses");
                            // Prompt 21 A.2: the player version of the Sandbox offers the bosses beaten in the campaign or the Boss Hunt.
                            if (slain.Boss && _session is MissionSession or BossRushSession) SandboxProfile.MarkBeaten(slain.Id);
                        }
                        if (!_menu && _world.Catalog.Vehicles.TryGetValue(e.DefId, out var dead) && dead.Boss)
                        {
                            StartCinematic(e.Position, force: true);
                            Haptics.Pulse(180, 255);
                        }
                        break;
                    case SimEventKind.BossPhase when !_menu && _world.TryGetVehicle(e.Entity, out var phased):
                        if (e.Mount == 1)
                        {
                            // The boss transforms: the camera goes to it, its general speaks.
                            StartCinematic(e.Position, force: true);
                            Haptics.Pulse(160, 255);
                            var spoken = e.DefId != null && e.DefId.StartsWith("radio.", System.StringComparison.Ordinal);
                            if (spoken) Say(e.DefId, DialoguePriority.Story, phased.Team); // prompt 30 L12: boss_phase_change is P1
                            _hud.Toast(e.DefId != null && !spoken ? Strings.Get(e.DefId)
                                    : Strings.Format("toast.bossPhase", ("card", Strings.Card(phased.Def.Id)), ("phase", (int)e.Value)),
                                error: true, seconds: spoken ? 3f : 5f, kind: NoticeKind.Boss);
                        }
                        // Its new form: drawn again with the phase's model.
                        else if (phased.Form != null) _views.Rebuild(phased);
                        break;
                    // Prompt 8 bosses: a part broken, the Earth Worm diving and the ground cracking, a landing.
                    case SimEventKind.PartBroken when !_menu:
                        PartBrokenToast(e);
                        break;
                    case SimEventKind.PartRepaired when !_menu:
                        PartRepairedToast(e);
                        break;
                    case SimEventKind.Burrowing when !_menu:
                        if (e.Value < 0.5f) _hud.Toast(Strings.Get("toast.burrow"), error: true, seconds: 3f, kind: NoticeKind.Boss);
                        else if (e.Value < 1.5f && _world.TryGetVehicle(e.Entity, out var borer) && borer.Def.Burrow is { } bore)
                        {
                            _warnings.Add((new Vector2(e.Position.X, e.Position.Y), bore.Radius, Time.time + e.Target.X + 0.5f));
                            _hud.Toast(Strings.Get("toast.cracking"), error: true, seconds: 2.5f, kind: NoticeKind.Boss);
                        }
                        break;
                    case SimEventKind.TroopsLanding when !_menu:
                        _hud.Toast(Strings.Format("toast.landing", Mathf.RoundToInt(e.Value)), error: true, seconds: 3f, kind: NoticeKind.Landing);
                        break;
                    case SimEventKind.Defected when _world.TryGetVehicle(e.Entity, out var turned):
                        _views.Rebuild(turned);
                        break;
                    // Prompt 23: a mission event's notice, and the weather it turns.
                    case SimEventKind.EventNotice when !_menu:
                        MissionEventNotice(e);
                        break;
                    case SimEventKind.WeatherShift when !_menu:
                        MissionWeather(e);
                        break;
                    case SimEventKind.Radio when !_menu && e.DefId != null:
                        // Prompt 23 H: a line for the dialogue. In a campaign mission the radio director hears it (below).
                        if (_radio == null) Say(DialogueRules.FromEvent(e.DefId, e.Team, e.Value, e.Mount, e.Entity, DialogueGeneral));
                        break;
                    case SimEventKind.StageStarted when !_menu && e.Value > 1f && _session is MissionSession staged:
                        _hud.ShowBanner(Strings.Format("stage.kicker", (int)e.Value), staged.StageTitle(e.DefId, (int)e.Value),
                            Strings.Get("goal." + staged.Mission.Def.Goal.ToString().ToLowerInvariant()));
                        Haptics.Pulse(90, 200);
                        break;
                    case SimEventKind.AreaChanged:
                        _playArea?.Show(_world.PlayArea);
                        FitCameraToArea();
                        if (!_menu && _world.Time > 1.0) _hud.Toast(Strings.Get(e.Value > 0f ? "toast.areaChanged" : "toast.areaOpened"), seconds: 4f, kind: NoticeKind.Area);
                        break;
                    case SimEventKind.FortressAlert when !_menu && e.DefId == "toast.enemyReinforce":
                        _hud.Toast(Strings.Get(e.DefId), error: true, kind: NoticeKind.Reinforce);
                        StoryPan(e.Position);
                        break;
                    case SimEventKind.StageCleared when !_menu:
                    case SimEventKind.FortressAlert when !_menu:
                        // A fortress alarm is bad news for the player (Team 1) or good (0: the enemy's gate blown in).
                        if (e.DefId != null) _hud.Toast(Strings.Get(e.DefId), error: e.Kind == SimEventKind.FortressAlert && e.Team == 1, kind: NoticeKind.Objective);
                        if (e.Kind == SimEventKind.StageCleared) Haptics.Pulse(90, 200);
                        break;
                    case SimEventKind.TraitProc when !_menu:
                        ShowTraitWord(e);
                        break;
                    case SimEventKind.Bounty when !_menu && e.Team == PlayerTeam:
                        _hud.Toast(Strings.Format(e.DefId switch { "retreat" => "toast.retreat", "super_gun" => "toast.superGun", "escort" => "toast.escort", _ => "toast.bounty" },
                            Mathf.RoundToInt(e.Value)), seconds: e.DefId == "retreat" ? 4f : 2f, kind: NoticeKind.Reward);
                        break;
                    case SimEventKind.PropDestroyed when !_menu:
                        if (e.DefId != null && _world.Catalog.Props.TryGetValue(e.DefId, out var fallen) && fallen.BlocksMovement)
                            DailyMissions.Record("buildings");
                        break;
                    case SimEventKind.PointCaptured when !_menu:
                        if (e.Team == PlayerTeam) DailyMissions.Record("captures");
                        var letter = Strings.Get("point." + e.DefId);
                        if (e.Team == PlayerTeam) _hud.Toast(Strings.Format("toast.captured", letter), kind: NoticeKind.Captured);
                        else if (e.Team == EnemyTeam) _hud.Toast(Strings.Format("toast.lost", letter), error: true, kind: NoticeKind.Lost);
                        break;
                    // Prompt 18 D.3: a short notice when the player cancels a boss's big attack (or makes the Spectre break off).
                    case SimEventKind.BigAttack when !_menu && e.Team == EnemyTeam && e.Mount is 2 or 3 && e.DefId != null:
                        _hud.Toast(Strings.Get("bigattack." + e.DefId + ".cancelled"), kind: NoticeKind.Done);
                        break;
                    // Prompt 19: a tiered boss leaves orbit, sends pods down, warns of its drone seizure.
                    case SimEventKind.TierChanged when !_menu && e.Team == EnemyTeam && e.DefId is "descend" or "pods" || e.DefId == "hijack" && e.Mount == 0:
                        if (_menu || e.Team != EnemyTeam) break;
                        _hud.Toast(Strings.Get(e.DefId == "descend" ? "toast.tier.descend" : e.DefId == "pods" ? "toast.pods" : "toast.hijack"),
                            error: e.DefId != "pods", seconds: 3f, kind: NoticeKind.Boss);
                        break;
                    // Prompt 30 L6: a neutral site changed hands (the radio's neutral_captured line is the RadioDirector's).
                    case SimEventKind.NeutralCaptured when !_menu && e.DefId != null && (e.Team == PlayerTeam || e.Team == EnemyTeam):
                        var site = Strings.Get("neutral." + e.DefId);
                        if (e.Team == PlayerTeam) _hud.Toast(Strings.Format("toast.neutralTaken", ("site", site)), kind: NoticeKind.Captured);
                        else _hud.Toast(Strings.Format("toast.neutralLost", ("site", site)), error: true, kind: NoticeKind.Lost);
                        break;
                    case SimEventKind.CrateIncoming when !_menu:
                        _hud.Toast(Strings.Get("toast.crate"), kind: NoticeKind.Crate);
                        break;
                    case SimEventKind.CrateClaimed when !_menu:
                        if (e.Team == PlayerTeam) _hud.Toast(Strings.Get("toast.crateOurs"), kind: NoticeKind.Crate);
                        else _hud.Toast(Strings.Get("toast.crateTheirs"), error: true, kind: NoticeKind.Crate);
                        break;
                    case SimEventKind.StrikeWarning when !_menu && e.Team == MachineBrigade.Sim.Entities.Teams.Environment:
                        _hud.Toast(Strings.Get("toast.raid"), error: true, kind: NoticeKind.AirRaid);
                        if (_world.Catalog.TryGetSupport(e.DefId, out var raid))
                            _warnings.Add((new Vector2(e.Position.X, e.Position.Y), raid.Length * 0.5f, Time.time + e.Value + raid.Duration + 0.5f));
                        break;
                    case SimEventKind.StrikeWarning:
                        if (_world.Catalog.TryGetSupport(e.DefId, out var support))
                            _warnings.Add((new Vector2(e.Position.X, e.Position.Y), support.IsLine ? support.Length * 0.5f : support.Radius,
                                Time.time + e.Value + support.Duration + 0.5f));
                        // Prompt 16 F: a boss's escorts parachuting in have their own line.
                        if (!_menu && e.Team == EnemyTeam && e.DefId.StartsWith("escort_drop", System.StringComparison.Ordinal))
                            _hud.Toast(Strings.Get("toast.escortDrop"), error: true, kind: NoticeKind.Reinforce);
                        else if (!_menu && e.Team == EnemyTeam) _hud.Toast(Strings.Format("toast.enemyStrike", Strings.Support(e.DefId)), error: true, kind: NoticeKind.Strike);
                        // An item was used: it is gone from the profile too.
                        if (!_menu && _sandbox == null && e.Team == PlayerTeam && support != null && support.Consumable) PlayerProfile.UseItem(e.DefId);
                        if (!_menu && e.Team == PlayerTeam && support != null) DailyMissions.Record(support.Consumable ? "items" : "strikes");
                        break;
                }
            }
            if (!DebugFlags.Has("-mb-no-fx")) _effects.Consume(_world.Events, _views, _map);
            _fortress?.Consume(_world.Events);
            _audio.Consume(_world.Events);
            _radio?.Consume(_world, _world.Events);
            _world.ClearEvents();
        }

        private void Wire()
        {
            _hud.PlayPressed += () =>
            {
                if (Curtain.Busy) return;
                MatchSettings.InMatch = true;
                Reload("loading.deploy", DeployDetail());
            };
            var builtInVietnamese = Strings.Vietnamese;
            _hud.VolumeChanged += () => AudioListener.volume = MatchSettings.Volume;
            _hud.SkinPreviewed += id =>
            {
                _previewSkin = id;
                ApplySkin(id ?? PlayerProfile.EquippedSkin);
            };
            _hud.SettingsChanged += () =>
            {
                AudioListener.volume = MatchSettings.Volume;
                MatchSettings.ApplyLanguage();
                // The HUD is built once; rebuild it in the new language. New graphics options
                // rebuild the scene too, so the menu battle shows them straight away.
                if (Strings.Vietnamese != builtInVietnamese || GraphicsSignature() != _builtGraphics)
                {
                    _frameRateTarget = MatchSettings.Options.FrameRate;
                    Reload("loading.apply");
                }
            };
            // The stand-in ad screen, in the menu too (the arsenal's ad crates); set per scene, as the HUD is.
            PlaceholderAds.Presenter = _hud.ShowPlaceholderAd;
            if (_menu) return;

            _hud.SelectAllPressed += _selection.SelectAll;
            _hud.StopPressed += _selection.Stop;
            _hud.RetreatPressed += _selection.Retreat;
            _hud.AttackMovePressed += _selection.ToggleAttackMove;
            _hud.BoxModeToggled += () => _selection.BoxMode = !_selection.BoxMode;
            _hud.ZoomPressed += factor =>
            {
                _camera.ZoomBy(factor, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                TakeTheView();
            };
            _hud.DeselectPressed += _selection.Deselect;
            _selection.ViewMoved += TakeTheView;
            _hud.RestartPressed += () =>
            {
                if (Curtain.Busy) return;
                ClaimReward();
                Reload("loading.deploy", DeployDetail());
            };
            _hud.MenuPressed += () =>
            {
                if (Curtain.Busy) return;
                ClaimReward();
                MatchSettings.InMatch = false;
                Reload("loading.base");
            };
            _hud.DeckPressed += () =>
            {
                if (Curtain.Busy) return;
                ClaimReward();
                MatchSettings.InMatch = false;
                MenuScreen.OpenDeckNext();
                Reload("loading.base");
            };
            _hud.CheckpointPressed += () =>
            {
                if (Curtain.Busy) return;
                // Prompt 20 N: a Boss Hunt starts again from its last checkpoint (the carry saved as the rest after a boss ended).
                if (_session is BossRushSession hunt)
                {
                    if (hunt.ResumeFrom() is not { } from) return;
                    ClaimReward();
                    BossRushSession.Pending = from;
                    BossRushSession.Full = hunt.IsFull;
                    Reload("loading.checkpoint", DeployDetail());
                    return;
                }
                if (_session is not MissionSession staged) return;
                var point = MatchJournal.Checkpoint(_world, MatchSettings.Mission, MatchSettings.MissionTier, staged.Operation);
                if (point == null) return;
                ClaimReward();
                MatchJournal.Pending = point;
                Reload("loading.checkpoint", DeployDetail());
            };
            _hud.NextMissionPressed += () =>
            {
                if (Curtain.Busy) return;
                ClaimReward();
                var next = Campaign.NextAfter(MatchSettings.Mission);
                if (next >= 0) MatchSettings.Mission = Campaign.All[next].Id;
                MatchSettings.Save();
                Reload("loading.deploy", DeployDetail());
            };
            _hud.DoubleRewardPressed += () =>
            {
                if (_reward == null || _reward.Claimed) return;
                Ads.Rewarded.Show(watched =>
                {
                    if (_reward == null || _reward.Claimed) return;
                    _reward.Claim(watched ? 2 : 1);
                    _hud.ShowRewardClaimed(_reward.Coins * (watched ? 2 : 1), watched);
                });
            };
            _hud.ContinueEndlessPressed += ContinueEndless;   // prompt 30 L5
            _hud.PausePressed += () => SetPaused(!_paused);
            _hud.ResumePressed += () => SetPaused(false);
            _hud.MinimapClicked += p =>
            {
                _camera.FocusOn(new Vector3(p.x, 0f, p.y));
                TakeTheView();
            };
            var playerAi = _session.PlayerAi;
            _hud.StancePressed += defend =>
            {
                playerAi.Stance = defend ? CommanderStance.Defend : CommanderStance.Attack;
                MatchJournal.Record(_world, "stance", defend ? "defend" : "attack");
                _hud.Toast(Strings.Get(defend ? "toast.defend" : "toast.attack"), kind: NoticeKind.Order);
            };
            _hud.TowerPressed += () =>
            {
                var callable = _world.Bases.Callable(PlayerTeam);
                if (callable.Count == 0) return;
                var result = _world.SubmitPlayer(new Command(CommandType.CallTower, PlayerTeam, System.Array.Empty<MachineBrigade.Sim.Core.EntityId>(), callable[0].Def.Position));
                if (result.Accepted) _hud.Toast(Strings.Get("toast.towerCalled")); else _hud.ShowError(result.Error);
            };
            _hud.AutoDeployToggled += () =>
            {
                MatchSettings.AutoDeploy = playerAi.AutoDeploy = !playerAi.AutoDeploy;
                MatchJournal.Record(_world, "autoDeploy", playerAi.AutoDeploy ? "1" : "0");
                MatchSettings.Save();
            };
            _hud.AutoStrikeToggled += () =>
            {
                MatchSettings.AutoStrike = playerAi.AutoStrike = !playerAi.AutoStrike;
                MatchJournal.Record(_world, "autoStrike", playerAi.AutoStrike ? "1" : "0");
                MatchSettings.Save();
            };
            _hud.PointPressed += id =>
            {
                playerAi.FocusPoint = playerAi.FocusPoint == id ? null : id;
                MatchJournal.Record(_world, "focus", playerAi.FocusPoint ?? "");
                _hud.Toast(playerAi.FocusPoint != null
                    ? Strings.Format("toast.focus", Strings.Get("point." + id))
                    : Strings.Get("toast.focusClear"));
            };
            _selection.Rejected += _hud.ShowError;
            // Prompt 28 H.6, H.10, E.1 (MatchRunner.Tactics.cs).
            WireTactics();
            _selection.EnemyTapped += def => _hud.ShowEnemyTip(def,
                MissionDecks.Deck((_session as MissionSession)?.Def, MatchSettings.DeckVehicles).Select(v => _world.Catalog.Vehicles.TryGetValue(v, out var d) ? d : null).Where(d => d != null), TierOf(def));
            WireBossParts();
            _selection.MoveOrdered += _effects.ShowMoveMarker;
            _selection.BoxChanged += _hud.ShowSelectionBox;
            _selection.BoxHidden += _hud.HideSelectionBox;

            _hud.ShowBanner(_session.Kicker, _session.Title, _session.Subtitle);
            _hud.Toast(_session.StartToast, seconds: 5f);
        }

        private void SetPaused(bool paused)
        {
            if (_resultShown || _presenting) return;
            _paused = paused;
            _hud.SetPaused(paused);
            Time.timeScale = paused ? 0f : 1f;
            AudioListener.pause = paused;
        }

        /// <summary>
        /// Rebuilds the scene behind the curtain: the screen and sound fade out, the scene loads
        /// behind black with what is being loaded on screen, and it fades back in once drawn.
        /// </summary>
        private static void Reload(string statusKey, string detail = null)
        {
            Time.timeScale = 1f;
            AudioListener.pause = false;
            var scene = SceneManager.GetActiveScene().buildIndex;
            Curtain.Close(Strings.Get(statusKey).ToUpperInvariant(), detail, () => SceneManager.LoadScene(scene));
        }

        /// <summary>What the loading screen names: the mission, or the mode and the battlefield.</summary>
        private static string DeployDetail()
        {
            if (MatchSettings.Mode == GameModeKind.Campaign) return Strings.Get("mission." + MatchSettings.Mission + ".name");
            var mode = MatchSettings.Mode switch
            {
                GameModeKind.Deathmatch => "mode.deathmatch",
                GameModeKind.KingOfTheHill => "mode.hill",
                GameModeKind.Assault => "mode.assault",
                GameModeKind.Defend => "mode.defend",
                GameModeKind.Endless => "mode.endless",
                GameModeKind.Weekly => "mode.weekly",
                GameModeKind.Survival => "mode.survival",
                GameModeKind.Siege => "mode.siege",
                GameModeKind.BossRush => "mode.bossrush",
                _ => "mode.conquest",
            };
            return Strings.Get(mode) + "  ·  " + Strings.Get("map." + MatchSettings.CurrentMap.Id);
        }

        /// <summary>Menu background: the camera drifts towards wherever the fighting is.</summary>
        private void Attract()
        {
            if (Time.time >= _attractAt)
            {
                _attractAt = Time.time + 6f;
                var sum = Vector3.zero;
                var count = 0;
                foreach (var v in _world.Vehicles)
                {
                    if (!v.Target.IsValid) continue;
                    sum += new Vector3(v.Position.X, 0f, v.Position.Y);
                    count++;
                }
                _attractFocus = count > 0 ? sum / count : new Vector3(Mathf.Sin(Time.time * 0.1f) * 30f, 0f, Mathf.Cos(Time.time * 0.13f) * 30f);
                // Keep the action to the right of the menu panel.
                _attractFocus -= _camera.Camera.transform.right * 18f;
            }
            _camera.Glide(_attractFocus, 24f, Time.unscaledDeltaTime, 0.35f);
        }

        /// <summary>
        /// Left alone for a while, the camera drifts towards the heaviest fighting so the battle
        /// plays out on screen; any touch hands it straight back.
        /// </summary>
        private void FollowTheFight()
        {
            var touching = (Touchscreen.current != null && Touchscreen.current.primaryTouch.press.isPressed) ||
                           (Mouse.current != null && (Mouse.current.leftButton.isPressed || Mouse.current.rightButton.isPressed ||
                                                      Mouse.current.scroll.ReadValue().sqrMagnitude > 0f));
            if (touching || _commander?.ArmedSupport != null || _paused)
            {
                _lastInput = Time.unscaledTime;
                _camera.StopFollowing();
            }
            if (Time.unscaledTime - _lastInput < AutoCameraDelay) return;
            if (Time.time >= _attractAt)
            {
                _attractAt = Time.time + 3f;
                var sum = Vector3.zero;
                var count = 0;
                foreach (var v in _world.Vehicles)
                {
                    if (v.Team != PlayerTeam || !v.Target.IsValid) continue;
                    sum += new Vector3(v.Position.X, 0f, v.Position.Y);
                    count++;
                }
                if (count > 0) _attractFocus = sum / count;
            }
            if (_attractFocus != Vector3.zero) _camera.Follow(_attractFocus, Time.unscaledDeltaTime);
        }

        private void UpdateStatus()
        {
            if (!_menu)
            {
                var callable = _world.Bases.Callable(PlayerTeam);
                _hud.SetTowers(callable.Count, callable.Count > 0 ? _world.Bases.RuntimeCostOf(PlayerTeam, callable[0]) : 0);
            }
            if (Time.unscaledDeltaTime > 0f) _fps = Mathf.Lerp(_fps, 1f / Time.unscaledDeltaTime, 0.05f);
            if (_menu) return;

            var wave = _session is SurvivalSession survival ? survival.Survival.Wave : _session is MissionSession m ? m.Mission.Wave : 0;
            if (wave != _announcedWave)
            {
                _announcedWave = wave;
                if (_announcedWave > 0) _hud.Toast(Strings.Format("toast.wave", _announcedWave), error: true, kind: NoticeKind.Wave);
            }
            _session.UpdateHud(_hud, _world, _pointInfo, _fps);
            _hud.SetModes(_selection.AttackMoveArmed, _selection.BoxMode);
            var playerAi = _session.PlayerAi;
            if (playerAi != null)
                _hud.SetCommander(playerAi.Stance == CommanderStance.Defend, playerAi.AutoDeploy, playerAi.AutoStrike, playerAi.FocusPoint);
            UpdateTactics();
            _hud.SetSelection(_selection.Summary());
            // Prompt 13 C.9: the selection's ammunition bar under its health bar.
            _storesStrip ??= new StoresStrip(_hud.SelectionExtras);
            var (storesLeft, storesFull, storesKind, storesSlow) = _selection.Stores();
            var (missilesLeft, missilesFull, flaresLeft, flaresFull) = _selection.Loadout();
            _storesStrip.Set(storesLeft, storesFull, storesKind, storesSlow, _hud.SelectionExtras,
                StoresStrip.KitLine(missilesLeft, missilesFull, flaresLeft, flaresFull));
            UpdateMinimap();
            UpdateBossPartOutline();
        }

        private void UpdateMinimap()
        {
            var minimap = _hud.Minimap;
            if (minimap == null || Time.unscaledTime < _minimapAt) return;
            _minimapAt = Time.unscaledTime + MinimapInterval;
            minimap.Begin(_world.Map.HalfSize);
            // Prompt 23 D.6: an EW blackout: the minimap is dark but for the camera's frame.
            if (!_menu && _world.BlackedOut(PlayerTeam))
            {
                MinimapView(minimap);
                minimap.Flush();
                return;
            }
            if (_session.Objectives != null)
                foreach (var p in _session.Objectives.Points)
                    minimap.Point(new Vector2(p.Def.Position.X, p.Def.Position.Y), p.Def.Radius, p.Owner, p.Progress);
            // Prompt 30 L6: the neutral sites (holder, capture) and the supply drop falling.
            if (!_menu && _world.Map.Neutrals.Count > 0)
                foreach (var (_, at, team, taking, progress, waiting) in _world.Neutrals.SiteStates)
                    minimap.Site(new Vector2(at.X, at.Y), team, taking, progress, waiting);
            if (!_menu)
                foreach (var crate in _world.Crates)
                    if (crate.IsAlive && crate.LandsAt > _world.Time)
                        minimap.Drop(new Vector2(crate.Position.X, crate.Position.Y), Mathf.Clamp01(1f - (float)(crate.LandsAt - _world.Time) / 15f));
            for (var i = _warnings.Count - 1; i >= 0; i--)
            {
                if (Time.time > _warnings[i].until) _warnings.RemoveAt(i);
                else minimap.Warning(_warnings[i].at, _warnings[i].radius);
            }
            // Prompt 31 L3: the places the battlefield events mark (a gate shutting, the storm's half, the grid's towers, the pods).
            if (!_menu) MinimapEventMarks(minimap);
            // Every enemy is on the map (the radar picture): the ones in sight bright, the rest dim;
            // a boss always, as a big marker.
            foreach (var v in _world.Vehicles)
            {
                if (!v.IsAlive) continue;
                var seen = v.Team == PlayerTeam || v.IsVisibleTo(PlayerTeam);
                if (v.Def.Boss && v.Team != PlayerTeam)
                {
                    minimap.Boss(new Vector2(v.Position.X, v.Position.Y));
                    continue;
                }
                // An enemy elite has a symbol of its own (a gold ring round its blip).
                if (v.Def.Elite && v.Team != PlayerTeam) minimap.Elite(new Vector2(v.Position.X, v.Position.Y), v.Flying, !seen);
                // Prompt 13 C.9: our aircraft's holding patterns, faint rings.
                if (v.Team == PlayerTeam && v.HasStores && v.Supply != MachineBrigade.Sim.Entities.SupplyState.Fighting)
                    minimap.Holding(new Vector2(v.HoldPoint.X, v.HoldPoint.Y));
                // Prompt 23 F.4: the Meridian Accord's units in their own colour.
                var blip = v.Team == PlayerTeam ? IsAccord(v) ? Minimap.AccordTeam : 0 : v.Team == MachineBrigade.Sim.Entities.Teams.Hostile ? 2 : 1;
                minimap.Blip(new Vector2(v.Position.X, v.Position.Y), blip, v.Flying, !seen);
            }
            // A mission's targets are known wherever they are (the briefing's intelligence).
            foreach (var mark in _marks) minimap.Mark(new Vector2(mark.Position.X, mark.Position.Y), (int)mark.Kind);
            MinimapView(minimap);
            minimap.Flush();
        }

        /// <summary>The camera's frame on the minimap.</summary>
        private void MinimapView(Minimap minimap)
        {
            var cam = _camera;
            var corners = new[] { new Vector2(0f, 0f), new Vector2(Screen.width, 0f), new Vector2(Screen.width, Screen.height), new Vector2(0f, Screen.height) };
            var ground = new Vector2[4];
            var ok = true;
            for (var i = 0; i < 4 && ok; i++)
            {
                ok = cam.TryGroundPoint(corners[i], out var g);
                ground[i] = new Vector2(g.x, g.z);
            }
            if (ok) minimap.View(ground[0], ground[1], ground[2], ground[3]);
        }

        /// <summary>Prompt 19 B.5: the tier a tapped tiered boss (or pod) of that def is at now (None: the ordinary matchup).</summary>
        private MachineBrigade.Sim.Content.AltitudeTier TierOf(VehicleDef def)
        {
            foreach (var v in _world.Vehicles)
                if (v.IsAlive && v.Def == def && v.Tier != MachineBrigade.Sim.Content.AltitudeTier.None) return v.Tier;
            return MachineBrigade.Sim.Content.AltitudeTier.None;
        }

        private bool _switching;
        private WakeView _wakes;

        /// <summary>
        /// Prompt 16 D.2: Boss Rush's sea boss is fought on Lighthouse Bay and the next boss back on the rush's
        /// own battlefield: the battle so far is carried over and the scene rebuilt behind the curtain.
        /// </summary>
        private void CheckBattlefieldSwitch()
        {
            if (_menu || _switching || _session is not BossRushSession rush || rush.SwitchTo is not { } carry) return;
            _switching = true;
            // Prompt 20 N: the checkpoint the rest just kept, saved before the scene goes.
            rush.KeepCheckpoint();
            BossRushSession.Pending = carry;
            // Prompt 19 G.2: a boss's own battlefield (the Silver Bug's Launch Site) reads as a redeployment, not "back to the front".
            var home = MatchSettings.CurrentMap.Id;
            Reload(carry.Map == BossRushSession.SeaMap ? "loading.toSea" : carry.Map == home ? "loading.backAshore" : "loading.toArena", Strings.Get("map." + carry.Map));
        }

        private void CheckResult()
        {
            CheckBattlefieldSwitch();
            if (_menu || _resultShown || _presenting || _session == null || _switching) return;
            var outcome = _session.Outcome(_world, _kills, _losses);
            if (outcome == null) return;
            _stuck?.Finish(_world);
            if (outcome.Result > 0) DailyMissions.Record("wins");
            // Prompt 30 L3: the match end plays first (MatchRunner.Ending.cs); the results panel follows it (ShowOutcome).
            BeginEnding(outcome);
        }

        /// <summary>RESULTS: the result card, with what the battle paid (prompt 30 L3: after the match end's presentation).</summary>
        private void ShowOutcome(MatchOutcome outcome)
        {
            _resultShown = true;
            Time.timeScale = 1f;
            _reward = outcome.Reward;
            Rewards.AddElites(_reward, outcome.Rows, _elitesSlain, _world.Catalog, _elitesSlain.Count * 7919 + (int)_world.Time);
            RewardView view = null;
            if (_reward != null)
            {
                view = new RewardView
                {
                    Coins = _reward.Coins, Xp = _reward.Xp, Stars = _reward.MissionId != null ? _reward.Stars : -1,
                    CanDouble = Ads.Rewarded.Ready,
                };
                foreach (var id in _reward.Unlocks) view.Unlocked.Add(Strings.Card(id));
                // The campaign's other pay-outs.
                if (_reward.Prints > 0) view.Extras.Add(("star", $"{Strings.Get("result.prints")} +{_reward.Prints}"));
                if (_reward.RarePrints > 0) view.Extras.Add(("star", Strings.Format("campaign.rareReward", _reward.RarePrints)));
                if (_reward.TowerGear != null) view.Extras.Add(("shield", $"{Strings.Get("result.towerPiece")} · {Strings.Get("rarity." + _reward.TowerGear.ToLowerInvariant())}"));
                if (_reward.HqLevel > 0) view.Extras.Add(("home", Strings.Format("result.hqLevel", _reward.HqLevel)));
                if (_reward.Fragment != null) view.Extras.Add(("eye", Strings.Format("result.fragment", Strings.Get("mission." + _reward.Fragment + ".fragment.title"))));
                // Prompt 22 D.6-D.7: why the story hands a card out, and the intel files a side objective recovered.
                foreach (var id in _reward.Unlocks)
                    if (Narrative.LootReason(id) is { } reason) view.Extras.Add(("star", Strings.Get(reason)));
                // Prompt 23 E: and the files an intercepted convoy carried, won or lost.
                if (_reward.MissionId != null)
                    foreach (var file in Narrative.FoundBy(_reward, outcome.Result > 0))
                        view.Extras.Add(("eye", Strings.Format("result.intel", ("title", Strings.Get($"intel.{file.Id}.title")))));
                // Crates: one for each of the first five wins of the day, a silver one for a mission's first clear.
                if (outcome.Result > 0 && PlayerProfile.GrantWinCrate()) view.Crates.Add(Strings.Get("crate.battle"));
                if (outcome.Result > 0 && _reward.MissionId != null && !PlayerProfile.Completed(_reward.MissionId))
                {
                    PlayerProfile.AddCrate(CrateKind.Silver);
                    view.Crates.Add(Strings.Get("crate.silver"));
                }
                view.HasNext = outcome.Result > 0 && _session is MissionSession && Campaign.NextAfter(MatchSettings.Mission) >= 0;
                view.CanResume = outcome.Result < 0 && ((_session is MissionSession staged && staged.Operation != null && staged.Operation.Checkpoints.Count > 0) ||
                                                        (_session is BossRushSession hunt && hunt.ResumeFrom() != null));
            }
            if (outcome.Result <= 0)
                outcome.Hints.AddRange(DefeatHints.For(_tally, _world.Catalog, MissionDecks.Deck((_session as MissionSession)?.Def, MatchSettings.DeckVehicles),
                    MissionDecks.SupportDeck((_session as MissionSession)?.Def, MatchSettings.DeckSupports),
                    MatchSettings.DeckVehicleSlots, _kills, _losses, _session is SiegeSession or AssaultSession or WeeklySession));
            // Prompt 22 F.4: the commander's word as the battle is decided, on the result card (a checkpoint's note comes first).
            var note = outcome.Note;
            if (note == null && _playerCommander != null && outcome.Result != 0 && !(outcome.Result < 0 && view is { CanResume: true }))
                note = Strings.Format("cmdr.quote", ("name", CommanderText.Call(_playerCommander)),
                    ("line", Strings.Get("cmdr." + _playerCommander.Id + (outcome.Result > 0 ? ".radio.win" : ".radio.loss"))));
            // Prompt 30 L5: a won Defend, Survival or Boss Rush may go on into its endless part.
            var endless = outcome.Result > 0 && _session.CanContinue;
            if (endless && note == null) note = Strings.Get("result.endlessKept");
            _hud.ShowResult(outcome.Result, outcome.Subtitle, outcome.Rows, view, note, outcome.Hints, _missedStory, endless);
            _music?.Result(outcome.Result > 0);
        }

        /// <summary>
        /// Brings the battle back to a checkpoint: from the same seed, the player's commands and
        /// switches are fed in at the steps they were given, and the battle is stepped as it was
        /// played, with nothing drawn, up to the checkpoint's step. The fingerprint there must match
        /// the one kept; if it does not, the battle goes on from where the replay reached, and the
        /// difference is logged.
        /// </summary>
        private IEnumerator Replay(ResumePoint resume)
        {
            _resumed = true;
            var replay = new CheckpointReplay(resume, _session, _world);
            var dt = (float)_clock.StepSeconds;
            while (replay.Advance(dt, 500))
            {
                Curtain.Progress(0.15f + 0.25f * replay.Progress);
                yield return null;
            }
            if (!replay.Matches)
                Debug.LogWarning($"Checkpoint replay drifted at step {_world.Tick}: {_world.StateHash():X16}, kept {resume.Hash:X16}");
        }

        /// <summary>The camera keeps to the play area as it is now (the whole map when there is none).</summary>
        private void FitCameraToArea()
        {
            if (_camera == null) return;
            if (_world.PlayArea is { } area)
                _camera.SetArea(new Vector2(area.Min.X, area.Min.Y), new Vector2(area.Max.X, area.Max.Y));
            else _camera.SetArea(null, null);
        }

        /// <summary>Pays the battle's reward if the player leaves without claiming it.</summary>
        private void ClaimReward()
        {
            if (_reward == null || _reward.Claimed) return;
            _reward.Claim();
        }
    }
}
