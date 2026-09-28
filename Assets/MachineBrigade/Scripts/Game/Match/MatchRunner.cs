using System.Collections;
using System.Collections.Generic;
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
    public sealed class MatchRunner : MonoBehaviour
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
        private float _cinematicZoom;
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
        private MissionMarkers _markers;
        private PlayAreaView _playArea;

        /// <summary>The battle was brought back to a checkpoint (replayed before its views were built).</summary>
        private bool _resumed;

        private int _replayCommand, _replayInput;
        private readonly List<MissionMark> _marks = new();
        private EffectsDirector _effects;
        private AudioDirector _audio;
        private MusicDirector _music;
        private Weather _weather;
        private Weather _leavingWeather;
        private RtsCamera _camera;
        private SelectionController _selection;
        private TouchGestures _gestures;
        private BattleHud _hud;
        private PlayerCommander _commander;
        private readonly List<(Vector2 at, float radius, float until)> _warnings = new();
        private readonly List<PointInfo> _pointInfo = new();
        private bool _menu, _paused, _resultShown;
        private float _fps = 60f, _minimapAt, _attractAt;
        private Vector3 _attractFocus;
        private int _announcedWave, _kills, _losses;
        private bool _warnedAir;
        private float _lastInput;
        private PerfProbe _perf;
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
            MatchSettings.Load();
            _frameRate = new FrameRateGovernor(_frameRateTarget, MatchSettings.SavingBattery ? 30 : MatchSettings.Options.FrameRate);
            ApplyDebugFlags();
            _perf = PerfProbe.Create();
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
            foreach (var campaignMission in Campaign.All)
                    if (DebugFlags.Has("-mb-" + campaignMission.Id))
                    {
                        MatchSettings.Mode = GameModeKind.Campaign;
                        MatchSettings.Mission = campaignMission.Id;
                    }
            }
            var options = MatchSettings.Options;
            // High graphics draws the most-seen vehicles with their high-detail models.
            ModelLibrary.HighDetail = options.Shadows == ShadowLevel.High && options.RichScenery;
            _builtGraphics = GraphicsSignature();
            _atmosphere = new Atmosphere(options);
            _cinematics.Enabled = MatchSettings.CinematicMoments && !DebugFlags.Has("-mb-no-cinematics");
            AudioListener.volume = MatchSettings.Volume;

            _menu = !MatchSettings.InMatch;
            var kind = _menu ? GameModeKind.Conquest : MatchSettings.Mode;
            var seed = _menu ? System.Environment.TickCount : 1234 + (int)MatchSettings.Difficulty * 7;
            var catalog = GameContent.LoadCatalog();
            // A campaign mission names its own battlefield and version of it.
            var mission = !_menu && kind == GameModeKind.Campaign ? Campaign.Get(MatchSettings.Mission) ?? Campaign.All[0] : null;
            var mapFile = mission != null ? mission.Map + "_" + mission.Variant : ModeSession.MapFile(kind, MatchSettings.CurrentMap.Id);
            var map = GameContent.LoadMap(mapFile);
            _world = new SimWorld(catalog, map, seed);
            // The player's arsenal: card ranks and equipment toughen and sharpen their own vehicles and strikes.
            if (!_menu) _world.SetBoosts(PlayerTeam, PlayerProfile.BoostFor, PlayerProfile.StrikeBoost, strikeRank: PlayerProfile.Rank);
            // A campaign enemy keeps pace with the arsenal as it grows (its boss and towers too).
            if (mission != null)
            {
                var deck = new List<VehicleBoost>();
                foreach (var id in MatchSettings.DeckVehicles)
                    if (catalog.Vehicles.TryGetValue(id, out var def)) deck.Add(PlayerProfile.BoostFor(def));
                var edge = EnemyScaling.Match(deck, catalog.EnemyScaling);
                _world.SetBoosts(1, _ => edge, _ => edge.Damage, everything: true);
            }
            _session = ModeSession.Create(kind, _menu, _world, seed);
            if (!_menu) ApplyRankDiscounts(catalog, mission != null);
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

            _world.TryGetRally(PlayerTeam, out var rally);
            var start = _menu ? Vector3.zero : new Vector3(rally.X + 16f, 0f, rally.Y + 16f);
            _camera = new RtsCamera(Camera.main, map.HalfSize, start, _menu ? 30f : 19f)
            {
                ShakeScale = MatchSettings.ShakeScale,
            };
            FitCameraToArea();
            _attractFocus = start;
            // Device check of the scenery: the north-west corner, zoomed right out.
            // Device check of the whole battlefield: its outline, terrain and objectives in one view.
            if (DebugFlags.Has("-mb-overview"))
            {
                _camera.MaxZoom = 95f;
                _camera.ZoomBy(0.05f, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                _camera.FocusOn(Vector3.zero);
                _lastInput = float.MaxValue;
            }
            if (DebugFlags.Has("-mb-far"))
            {
                _camera.ZoomBy(0.1f, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                // The north-west edge: the boundary line and the country beyond it.
                var edge = _world.Map.HalfSize * 0.8f;
                _camera.FocusOn(new Vector3(-edge, 0f, edge));
                _lastInput = float.MaxValue;
            }
            _effects = new EffectsDirector(catalog, _materials, _meshes, _models, _camera, worldRoot,
                options.MaxEffects ? EffectBudget.High : EffectBudget.Eco);
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
            _effects.Prewarm();
            Curtain.Progress(0.85f);
            yield return null;
            // The menu battle has no player side, so no alarms or chimes.
            _audio = new AudioDirector(_camera, worldRoot, catalog, _menu ? -1 : PlayerTeam);
            // The soundtrack: the menu theme, the siege track for fortress battles, else a battle track.
            var fortress = MatchSettings.Mode is GameModeKind.Siege or GameModeKind.Defend or GameModeKind.Endless;
            _music = new MusicDirector(worldRoot, _menu ? MusicDirector.Mood.Menu : fortress ? MusicDirector.Mood.Siege : MusicDirector.Mood.Battle,
                System.Environment.TickCount);
            UiKit.Clicked += _audio.Click;
            var weather = _menu ? WeatherKind.Clear
                // An Operations mutator's weather over the mission's own.
                : mission != null && MatchSettings.Run?.Mission == mission.Id && System.Enum.TryParse<WeatherKind>(MatchSettings.Run.Weather, out var mutated) ? mutated
                : mission != null && System.Enum.TryParse<WeatherKind>(mission.Weather, out var missionWeather) ? missionWeather
                : MatchSettings.ResolveWeather(seed);
            // A clear day still has the map's own air: warm desert haze, cold snow light, sea mist.
            _weather = new Weather(weather, _atmosphere, _materials, _camera, _audio, worldRoot, options.MaxEffects, theme.Cast, theme.Haze);
            _weatherKind = weather;
            _effects.Night = weather == WeatherKind.Night;
            _worldRoot = worldRoot;
            _richEffects = options.MaxEffects;
            _crates = new CrateViews(_models, worldRoot);
            _mineViews = new MineViews(_models, worldRoot, _menu ? -1 : PlayerTeam);
            // Quick battles sometimes turn: a storm rolls in, the fog comes down, night falls.
            if (!_menu && mission == null) _nextWeatherShift = 150 + new System.Random(seed).NextDouble() * 120;
            ApplyPost(options.Bloom, MatchSettings.Brightness);
            _views.BlobShadows = options.Shadows == ShadowLevel.Off;

            var cards = _menu ? null : PlayerCommander.Cards(_world, MatchSettings.DeckVehicles, MatchSettings.DeckSupports);
            _hud = new BattleHud(_session.Hud, cards, catalog)
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
                _hud.Minimap.SetPicture(_map.MinimapTexture, _world.Map.HalfSize);
            }
            _selection = new SelectionController(_world, _views, _camera, _map, PlayerTeam);
            if (!_menu)
            {
                // Items bought with coins come along into every real match.
                if (_world.TryGetEconomy(PlayerTeam, out var economy))
                    foreach (var item in Progression.Items)
                    {
                        var owned = PlayerProfile.ItemCount(item);
                        if (owned > 0) economy.Items[item] = owned;
                    }
                _commander = new PlayerCommander(_world, _hud, _camera, PlayerTeam, cards);
                _selection.TapInterceptor = _commander.TryTap;
                _gestures = new TouchGestures(_selection, _hud.IsOverUi) { BoxMode = () => _selection.BoxMode };
                if (isActiveAndEnabled) _gestures.Enable();
            }
            Wire();

            DispatchEvents();
            // Built: lift the curtain once this scene has drawn a few frames.
            _built = true;
            Curtain.Progress(1f);
            Curtain.Open();
        }

        /// <summary>-mb-killboss: when each boss was first seen.</summary>
        private readonly Dictionary<MachineBrigade.Sim.Core.EntityId, float> _bossSeen = new();

        private bool BossOnField()
        {
            foreach (var v in _world.Vehicles)
                if (v.IsAlive && v.Def.Boss && v.Team == EnemyTeam) return true;
            return false;
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
            // The new weather rolls in over a few seconds while the old one thins out (see Weather).
            _leavingWeather?.Dispose();
            _leavingWeather = _weather;
            _weatherKind = next;
            var theme = MapTheme.For(_world.Map.Theme);
            _weather = new Weather(next, _atmosphere, _materials, _camera, _audio, _worldRoot, _richEffects, theme.Cast, theme.Haze, _leavingWeather);
            _effects.Night = next == WeatherKind.Night;
            _hud.Toast(Strings.Format("toast.weather", Strings.Get("menu." + next.ToString().ToLowerInvariant())), seconds: 3f);
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
                Add(mission.Convoy?.Def);
                if (mission.Waves != null) foreach (var id in mission.Waves.Roster) Add(id);
                foreach (var u in mission.Units) Add(u.DefId);
            }
            // Boss Rush brings its bosses and their escorts later.
            if (MatchSettings.Mode == GameModeKind.BossRush && !_menu)
                foreach (var boss in BossRushRules.Everyone())
                {
                    Add(boss);
                    if (new BossRushRules().Escorts.TryGetValue(boss, out var escorts)) foreach (var e in escorts) Add(e);
                }
            return ids;
        }

        /// <summary>
        /// Ranked cards cost the player less to call (rank 7: -5 %, rank 9: -10 %; see
        /// CardRanks.CallCost). In the campaign the enemy gets 80 % of the deck's average cut as
        /// extra income, as it gets 80 % of the arsenal's edge.
        /// </summary>
        private void ApplyRankDiscounts(Catalog catalog, bool campaign)
        {
            if (!_world.TryGetEconomy(PlayerTeam, out var mine)) return;
            float full = 0f, paid = 0f;
            void Card(string id, int cost)
            {
                var price = CardRanks.CallCost(cost, PlayerProfile.Rank(id));
                if (price < cost) mine.Discounts[id] = cost - price;
                full += cost;
                paid += price;
            }
            foreach (var id in MatchSettings.DeckVehicles)
                if (catalog.Vehicles.TryGetValue(id, out var v)) Card(id, v.CpCost);
            foreach (var id in MatchSettings.DeckSupports)
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
            if (!_paused && !_resultShown) _gestures?.Tick(Time.unscaledTime);
            // Android's back button arrives as Escape: close a menu page, or pause and resume.
            if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
            {
                if (_menu) _hud.MenuBack();
                else if (_commander?.ArmedSupport != null) _commander.Disarm();
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
            if (!_paused && !_resultShown) Time.timeScale = _cinematics.TimeScale(Time.unscaledTime);
            _hud.SetLetterbox(_cinematics.Letterbox(Time.unscaledTime));
            var steps = _paused || _lobbyCovered ? 0 : _clock.Advance(Time.deltaTime);
            var dt = (float)_clock.StepSeconds;
            _perf?.CountSteps(steps);
            for (var i = 0; i < steps; i++)
            {
                _perf?.Begin();
                _session.Mode.Tick(_world, dt);
                _session.TickAi(_world, dt);
                _world.Step(dt);
                _views.SnapshotAll();
                _perf?.End(PerfProbe.Section.Sim);
                _perf?.Begin();
                DispatchEvents();
                _perf?.End(PerfProbe.Section.Events);
            }

            if (!_menu && !_paused && DebugFlags.Has("-mb-demolish") && Time.time >= _demolishAt) Demolish();
            if (!_menu && !_paused && DebugFlags.Has("-mb-towerwatch")) WatchTower();
            if (!_menu && !_paused && DebugFlags.Has("-mb-bastion")) WatchBastion();
            if (!_menu && !_paused && DebugFlags.Has("-mb-smokescreen") && Time.time >= _smokeAt)
            {
                // Device check: a smoke screen in the thick of the fight every few seconds.
                _smokeAt = Time.time + 9f;
                _effects.DebugSmokeScreen(_camera.Focus + new Vector3(UnityEngine.Random.Range(-6f, 6f), 0f, UnityEngine.Random.Range(-6f, 6f)));
            }
            if (_cinematics.Active(Time.unscaledTime)) _camera.Glide(_cinematics.Focus, _cinematicZoom, Time.unscaledDeltaTime, 2.5f);
            else if (_menu) Attract();
            else FollowTheFight();
            _selection.Tick();
            _perf?.Begin();
            if (!_paused)
            {
                _effects.Tick(_views);
                _weather.Tick();
                if (_leavingWeather != null && !_leavingWeather.TickLeaving())
                {
                    _leavingWeather.Dispose();
                    _leavingWeather = null;
                }
                // A boss on the field: the boss track (the old war-drum loop stays silent).
                if (!_menu && Time.frameCount % 15 == 0) _music.Boss = BossOnField();
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
            _music?.Tick(Time.unscaledDeltaTime);
            _perf?.End(PerfProbe.Section.Audio);
            _perf?.Begin();
            _commander?.Update();
            _hud.Tick();
            UpdateStatus();
            CheckResult();
            _perf?.End(PerfProbe.Section.Hud);
        }

        private void LateUpdate()
        {
            if (!_built) return;
            _camera.Apply(Time.unscaledDeltaTime);
            _atmosphere.FitShadows(_camera.Camera);
            _perf?.Begin();
            _views.Render(_clock.Alpha, _camera.Rotation);
            _perf?.End(PerfProbe.Section.Views);
            _perf?.Begin();
            _objectives?.Render(Time.time);
            if (_markers != null && _session is MissionSession mission)
            {
                mission.Mission.Marks(_world, _marks);
                _markers.Render(_marks, _views, _map, _camera.Rotation, Time.time);
            }
            _effects.Draw();
            if (!DebugFlags.Has("-mb-no-scenery")) _surroundings.Draw();
            _map.Animate(Time.time);
            _map.DrawShields(_camera.Rotation, Time.time);
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

        /// <summary>A slow-motion moment on a blast that is on screen.</summary>
        private void StartCinematic(System.Numerics.Vector2 at, bool force = false)
        {
            var point = new Vector3(at.X, 0f, at.Y);
            var viewport = _camera.Camera.WorldToViewportPoint(point);
            if (viewport.x < 0.05f || viewport.x > 0.95f || viewport.y < 0.05f || viewport.y > 0.95f) return;
            if (!_cinematics.Trigger(point, Time.unscaledTime, force)) return;
            Haptics.Pulse(70, 190);
            _cinematicZoom = Mathf.Max(12f, _camera.Zoom * 0.82f);
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
            PlayerProfile.Changed -= OnProfileChanged;
            if (_audio != null) UiKit.Clicked -= _audio.Click;
            _perf?.Dispose();
            _leavingWeather?.Dispose();
            _weather?.Dispose();
            _effects?.Dispose();
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
                        if (!_menu && !_warnedAir && vehicle.Team == EnemyTeam && vehicle.Flying)
                        {
                            _warnedAir = true;
                            _hud.Toast(Strings.Get("toast.airDefence"), error: true, seconds: 3f);
                        }
                        break;
                    case SimEventKind.VehicleDestroyed:
                        if (e.Team == PlayerTeam) _losses++;
                        else if (e.Team == EnemyTeam) _kills++;
                        if (!_menu && e.Team == EnemyTeam && _world.Catalog.Vehicles.TryGetValue(e.DefId, out var slain))
                        {
                            DailyMissions.Record("kills");
                            if (slain.Elite) DailyMissions.Record("elites");
                            if (slain.Boss) DailyMissions.Record("bosses");
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
                            _hud.Toast(e.DefId != null ? Strings.Get(e.DefId) : Strings.Format("toast.bossPhase", Strings.Card(phased.Def.Id), (int)e.Value),
                                error: true, seconds: 5f);
                        }
                        // Its new form: drawn again with the phase's model.
                        else if (phased.Form != null) _views.Rebuild(phased);
                        break;
                    case SimEventKind.Defected when _world.TryGetVehicle(e.Entity, out var turned):
                        _views.Rebuild(turned);
                        break;
                    case SimEventKind.Radio when !_menu && e.DefId != null:
                        _hud.Toast(Strings.Get(e.DefId), error: e.DefId == "radio.betrayal", seconds: 5f);
                        break;
                    case SimEventKind.StageStarted when !_menu && e.Value > 1f && _session is MissionSession staged:
                        _hud.ShowBanner(Strings.Format("stage.kicker", (int)e.Value), staged.StageTitle(e.DefId, (int)e.Value),
                            Strings.Get("goal." + staged.Mission.Def.Goal.ToString().ToLowerInvariant()));
                        Haptics.Pulse(90, 200);
                        break;
                    case SimEventKind.AreaChanged:
                        _playArea?.Show(_world.PlayArea);
                        FitCameraToArea();
                        if (!_menu && _world.Time > 1.0) _hud.Toast(Strings.Get(e.Value > 0f ? "toast.areaChanged" : "toast.areaOpened"), seconds: 4f);
                        break;
                    case SimEventKind.StageCleared when !_menu:
                    case SimEventKind.FortressAlert when !_menu:
                        if (e.DefId != null) _hud.Toast(Strings.Get(e.DefId), error: e.Kind == SimEventKind.FortressAlert);
                        if (e.Kind == SimEventKind.StageCleared) Haptics.Pulse(90, 200);
                        break;
                    case SimEventKind.TraitProc when !_menu:
                        ShowTraitWord(e);
                        break;
                    case SimEventKind.Bounty when !_menu && e.Team == PlayerTeam:
                        _hud.Toast(Strings.Format("toast.bounty", Mathf.RoundToInt(e.Value)), seconds: 2f);
                        break;
                    case SimEventKind.PropDestroyed when !_menu:
                        if (e.DefId != null && _world.Catalog.Props.TryGetValue(e.DefId, out var fallen) && fallen.BlocksMovement)
                            DailyMissions.Record("buildings");
                        break;
                    case SimEventKind.PointCaptured when !_menu:
                        if (e.Team == PlayerTeam) DailyMissions.Record("captures");
                        var letter = Strings.Get("point." + e.DefId);
                        if (e.Team == PlayerTeam) _hud.Toast(Strings.Format("toast.captured", letter));
                        else if (e.Team == EnemyTeam) _hud.Toast(Strings.Format("toast.lost", letter), error: true);
                        break;
                    case SimEventKind.CrateIncoming when !_menu:
                        _hud.Toast(Strings.Get("toast.crate"));
                        break;
                    case SimEventKind.CrateClaimed when !_menu:
                        if (e.Team == PlayerTeam) _hud.Toast(Strings.Get("toast.crateOurs"));
                        else _hud.Toast(Strings.Get("toast.crateTheirs"), error: true);
                        break;
                    case SimEventKind.StrikeWarning when !_menu && e.Team == MachineBrigade.Sim.Entities.Teams.Environment:
                        _hud.Toast(Strings.Get("toast.raid"), error: true);
                        if (_world.Catalog.TryGetSupport(e.DefId, out var raid))
                            _warnings.Add((new Vector2(e.Position.X, e.Position.Y), raid.Length * 0.5f, Time.time + e.Value + raid.Duration + 0.5f));
                        break;
                    case SimEventKind.StrikeWarning:
                        if (_world.Catalog.TryGetSupport(e.DefId, out var support))
                            _warnings.Add((new Vector2(e.Position.X, e.Position.Y), support.IsLine ? support.Length * 0.5f : support.Radius,
                                Time.time + e.Value + support.Duration + 0.5f));
                        if (!_menu && e.Team == EnemyTeam) _hud.Toast(Strings.Format("toast.enemyStrike", Strings.Support(e.DefId)), error: true);
                        // An item was used: it is gone from the profile too.
                        if (!_menu && e.Team == PlayerTeam && support != null && support.Consumable) PlayerProfile.UseItem(e.DefId);
                        if (!_menu && e.Team == PlayerTeam && support != null) DailyMissions.Record(support.Consumable ? "items" : "strikes");
                        break;
                }
            }
            if (!DebugFlags.Has("-mb-no-fx")) _effects.Consume(_world.Events, _views, _map);
            _audio.Consume(_world.Events);
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
            _hud.ZoomPressed += factor => _camera.ZoomBy(factor, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
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
            _hud.CheckpointPressed += () =>
            {
                if (Curtain.Busy || _session is not MissionSession staged) return;
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
                var next = Campaign.IndexOf(MatchSettings.Mission) + 1;
                if (next > 0 && next < Campaign.All.Count) MatchSettings.Mission = Campaign.All[next].Id;
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
            _hud.PausePressed += () => SetPaused(!_paused);
            _hud.ResumePressed += () => SetPaused(false);
            _hud.MinimapClicked += p => _camera.FocusOn(new Vector3(p.x, 0f, p.y));
            var playerAi = _session.PlayerAi;
            _hud.StancePressed += defend =>
            {
                playerAi.Stance = defend ? CommanderStance.Defend : CommanderStance.Attack;
                MatchJournal.Record(_world, "stance", defend ? "defend" : "attack");
                _hud.Toast(Strings.Get(defend ? "toast.defend" : "toast.attack"));
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
            _selection.MoveOrdered += _effects.ShowMoveMarker;
            _selection.BoxChanged += _hud.ShowSelectionBox;
            _selection.BoxHidden += _hud.HideSelectionBox;

            _hud.ShowBanner(_session.Kicker, _session.Title, _session.Subtitle);
            _hud.Toast(_session.StartToast, seconds: 5f);
        }

        private void SetPaused(bool paused)
        {
            if (_resultShown) return;
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
                _hud.SetTowers(callable.Count, callable.Count > 0 ? _world.Bases.CostOf(callable[0]) : 0);
            }
            if (Time.unscaledDeltaTime > 0f) _fps = Mathf.Lerp(_fps, 1f / Time.unscaledDeltaTime, 0.05f);
            if (_menu) return;

            var wave = _session is SurvivalSession survival ? survival.Survival.Wave : _session is MissionSession m ? m.Mission.Wave : 0;
            if (wave != _announcedWave)
            {
                _announcedWave = wave;
                if (_announcedWave > 0) _hud.Toast(Strings.Format("toast.wave", _announcedWave), error: true);
            }
            _session.UpdateHud(_hud, _world, _pointInfo, _fps);
            _hud.SetModes(_selection.AttackMoveArmed, _selection.BoxMode);
            var playerAi = _session.PlayerAi;
            if (playerAi != null)
                _hud.SetCommander(playerAi.Stance == CommanderStance.Defend, playerAi.AutoDeploy, playerAi.AutoStrike, playerAi.FocusPoint);
            _hud.SetSelection(_selection.Summary());
            UpdateMinimap();
        }

        private void UpdateMinimap()
        {
            var minimap = _hud.Minimap;
            if (minimap == null || Time.unscaledTime < _minimapAt) return;
            _minimapAt = Time.unscaledTime + MinimapInterval;
            minimap.Begin(_world.Map.HalfSize);
            if (_session.Objectives != null)
                foreach (var p in _session.Objectives.Points)
                    minimap.Point(new Vector2(p.Def.Position.X, p.Def.Position.Y), p.Def.Radius, p.Owner, p.Progress);
            for (var i = _warnings.Count - 1; i >= 0; i--)
            {
                if (Time.time > _warnings[i].until) _warnings.RemoveAt(i);
                else minimap.Warning(_warnings[i].at, _warnings[i].radius);
            }
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
                minimap.Blip(new Vector2(v.Position.X, v.Position.Y), v.Team == PlayerTeam ? 0 : v.Team == MachineBrigade.Sim.Entities.Teams.Hostile ? 2 : 1, v.Flying, !seen);
            }
            // A mission's targets are known wherever they are (the briefing's intelligence).
            foreach (var mark in _marks) minimap.Mark(new Vector2(mark.Position.X, mark.Position.Y), (int)mark.Kind);
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
            minimap.Flush();
        }

        private void CheckResult()
        {
            if (_menu || _resultShown || _session == null) return;
            // Let a boss's death play out in slow motion before the result card covers it.
            if (_cinematics.Active(Time.unscaledTime)) return;
            var outcome = _session.Outcome(_world, _kills, _losses);
            if (outcome == null) return;
            if (outcome.Result > 0) DailyMissions.Record("wins");
            _resultShown = true;
            Time.timeScale = 1f;
            _reward = outcome.Reward;
            RewardView view = null;
            if (_reward != null)
            {
                view = new RewardView
                {
                    Coins = _reward.Coins, Xp = _reward.Xp, Stars = _reward.MissionId != null ? _reward.Stars : -1,
                    CanDouble = Ads.Rewarded.Ready,
                };
                foreach (var id in _reward.Unlocks) view.Unlocked.Add(Strings.Card(id));
                // Crates: one for each of the first five wins of the day, a silver one for a mission's first clear.
                if (outcome.Result > 0 && PlayerProfile.GrantWinCrate()) view.Crates.Add(Strings.Get("crate.battle"));
                if (outcome.Result > 0 && _reward.MissionId != null && !PlayerProfile.Completed(_reward.MissionId))
                {
                    PlayerProfile.AddCrate(CrateKind.Silver);
                    view.Crates.Add(Strings.Get("crate.silver"));
                }
                var index = _session is MissionSession ? Campaign.IndexOf(MatchSettings.Mission) : -1;
                view.HasNext = outcome.Result > 0 && index >= 0 && index + 1 < Campaign.All.Count;
                view.CanResume = outcome.Result < 0 && _session is MissionSession staged && staged.Operation != null && staged.Operation.Checkpoints.Count > 0;
            }
            _hud.ShowResult(outcome.Result, outcome.Subtitle, outcome.Rows, view);
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
            _replayCommand = _replayInput = 0;
            var dt = (float)_clock.StepSeconds;
            while (_world.Tick < resume.Tick && !_world.IsOver)
            {
                FeedJournal(resume);
                _session.Mode.Tick(_world, dt);
                _session.TickAi(_world, dt);
                _world.Step(dt);
                _world.ClearEvents();
                if (_world.Tick % 500 != 0) continue;
                Curtain.Progress(0.15f + 0.25f * _world.Tick / Mathf.Max(1f, resume.Tick));
                yield return null;
            }
            FeedJournal(resume);
            if (_world.StateHash() != resume.Hash)
                Debug.LogWarning($"Checkpoint replay drifted at step {_world.Tick}: {_world.StateHash():X16}, kept {resume.Hash:X16}");
        }

        /// <summary>The journal's commands and switches for the step the replay is on.</summary>
        private void FeedJournal(ResumePoint resume)
        {
            while (_replayCommand < resume.Commands.Count && resume.Commands[_replayCommand].tick <= _world.Tick)
                _world.SubmitPlayer(resume.Commands[_replayCommand++].command);
            while (_replayInput < resume.Inputs.Count && resume.Inputs[_replayInput].tick <= _world.Tick)
            {
                var (_, input, value) = resume.Inputs[_replayInput++];
                var ai = _session.PlayerAi;
                if (input != "choose") MatchJournal.Record(_world, input, value);
                switch (input)
                {
                    case "stance" when ai != null:
                        ai.Stance = value == "defend" ? CommanderStance.Defend : CommanderStance.Attack;
                        break;
                    case "autoDeploy" when ai != null:
                        ai.AutoDeploy = value == "1";
                        break;
                    case "autoStrike" when ai != null:
                        ai.AutoStrike = value == "1";
                        break;
                    case "focus" when ai != null:
                        ai.FocusPoint = string.IsNullOrEmpty(value) ? null : value;
                        break;
                    case "choose":
                        (_session as MissionSession)?.Choose(_world, value);
                        break;
                }
            }
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
