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
        private ModeSession _session;
        private MatchReward _reward;
        private SimClock _clock;
        private MaterialLibrary _materials;
        private MeshLibrary _meshes;
        private ModelLibrary _models;
        private Atmosphere _atmosphere;
        private MapView _map;
        private Surroundings _surroundings;
        private ViewRegistry _views;
        private ObjectiveView _objectives;
        private EffectsDirector _effects;
        private AudioDirector _audio;
        private Weather _weather;
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

        private void Awake()
        {
            // Nothing needs PhysX: debris, turrets and wrecks move on their own kinematics.
            Physics.simulationMode = SimulationMode.Script;
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
            }
            var options = MatchSettings.Options;
            _builtGraphics = GraphicsSignature();
            _atmosphere = new Atmosphere(options);
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
            _session = ModeSession.Create(kind, _menu, _world, seed);
            _clock = new SimClock();

            var worldRoot = new GameObject("Battlefield").transform;
            _materials = new MaterialLibrary();
            _meshes = new MeshLibrary();
            _models = new ModelLibrary(_materials);
            var theme = MapTheme.For(map.Theme);
            if (theme.ModelGrass.HasValue) _materials.ForModel("Grass", -1).SetColor("_BaseColor", theme.ModelGrass.Value);
            _map = new MapView(_world, _models, _materials, theme, worldRoot, options.Shadows);
            _surroundings = new Surroundings(_world, _models, _materials, theme, worldRoot, options);
            _views = new ViewRegistry(_models, _meshes, _materials, worldRoot, PlayerTeam);
            if (_session.Objectives != null && _session.Objectives.Points.Count > 0)
                _objectives = new ObjectiveView(_session.Objectives, _meshes, _materials, worldRoot);

            _world.TryGetRally(PlayerTeam, out var rally);
            var start = _menu ? Vector3.zero : new Vector3(rally.X + 16f, 0f, rally.Y + 16f);
            _camera = new RtsCamera(Camera.main, map.HalfSize, start, _menu ? 30f : 19f)
            {
                ShakeScale = MatchSettings.ShakeScale,
            };
            _attractFocus = start;
            // Device check of the scenery: the north-west corner, zoomed right out.
            if (DebugFlags.Has("-mb-far"))
            {
                _camera.ZoomBy(0.1f, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
                _camera.FocusOn(new Vector3(-80f, 0f, 80f));
                _lastInput = float.MaxValue;
            }
            _effects = new EffectsDirector(catalog, _materials, _meshes, _models, _camera, worldRoot,
                options.MaxEffects ? EffectBudget.High : EffectBudget.Eco);
            // Build every vehicle's merged model and the munitions now, not on first use mid-battle.
            foreach (var def in catalog.Vehicles.Values) _models.Prewarm(def.Model);
            if (_models.Has("strike_jet")) _models.Prewarm("strike_jet");
            _effects.Prewarm();
            // The menu battle has no player side, so no alarms or chimes.
            _audio = new AudioDirector(_camera, worldRoot, catalog, _menu ? -1 : PlayerTeam);
            UiKit.Clicked += _audio.Click;
            var weather = _menu ? WeatherKind.Clear
                : mission != null && System.Enum.TryParse<WeatherKind>(mission.Weather, out var missionWeather) ? missionWeather
                : MatchSettings.ResolveWeather(seed);
            // A clear day still has the map's own air: warm desert haze, cold snow light, sea mist.
            if (weather == WeatherKind.Clear) _atmosphere.SetMood(1f, theme.Cast, theme.Haze, 100f, 220f);
            _weather = new Weather(weather, _atmosphere, _materials, _camera, _audio, worldRoot, options.MaxEffects);
            ApplyPost(options.Bloom, MatchSettings.Brightness);
            _views.BlobShadows = options.Shadows == ShadowLevel.Off;

            var cards = _menu ? null : PlayerCommander.Cards(_world, MatchSettings.DeckVehicles, MatchSettings.DeckSupports);
            _hud = new BattleHud(_session.Hud, cards, catalog)
            {
                ShowFps = MatchSettings.ShowFps,
            };
            if (_hud.Minimap != null) _hud.Minimap.Ground = theme.Minimap;
            _selection = new SelectionController(_world, _views, _camera, _map, PlayerTeam);
            if (!_menu)
            {
                _commander = new PlayerCommander(_world, _hud, _camera, PlayerTeam, cards);
                _selection.TapInterceptor = _commander.TryTap;
                _gestures = new TouchGestures(_selection, _hud.IsOverUi) { BoxMode = () => _selection.BoxMode };
            }
            Wire();

            DispatchEvents();
        }

        private string _builtGraphics;

        /// <summary>Everything that needs a rebuild to take effect.</summary>
        private static string GraphicsSignature()
        {
            var o = MatchSettings.Options;
            return $"{o.Shadows}|{o.RenderScale}|{o.AntiAliasing}|{o.FrameRate}|{o.Bloom}|{o.RichScenery}|{o.MaxEffects}|" +
                   $"{MatchSettings.UiSize}|{MatchSettings.SavingBattery}|{MatchSettings.Brightness}";
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

        private void Update()
        {
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
            // Menus and pause draw every other frame until touched: the battle behind them keeps
            // moving, the phone does half the work.
            UnityEngine.Rendering.OnDemandRendering.renderFrameInterval =
                (_menu || _paused) && !(Touchscreen.current?.primaryTouch.press.isPressed ?? false) &&
                !(Mouse.current?.leftButton.isPressed ?? false) ? 2 : 1;

            var steps = _paused ? 0 : _clock.Advance(Time.deltaTime);
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

            if (_menu) Attract();
            else FollowTheFight();
            _selection.Tick();
            _perf?.Begin();
            if (!_paused)
            {
                _effects.Tick(_views);
                _weather.Tick();
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
            _perf?.End(PerfProbe.Section.Hud);
        }

        private void LateUpdate()
        {
            _camera.Apply(Time.unscaledDeltaTime);
            _atmosphere.FitShadows(_camera.Camera);
            _perf?.Begin();
            _views.Render(_clock.Alpha, _camera.Rotation);
            _perf?.End(PerfProbe.Section.Views);
            _perf?.Begin();
            _objectives?.Render(Time.time);
            _effects.Draw();
            if (!DebugFlags.Has("-mb-no-scenery")) _surroundings.Draw();
            _map.Animate(Time.time);
            _perf?.End(PerfProbe.Section.Scenery);
            _perf?.EndFrame(_views.All.Count);
            if (_perf != null && !_censusDone && Time.time > 6f)
            {
                _censusDone = true;
                _perf.Census(_surroundings.InstancedTriangles, _surroundings.Batches);
            }
        }

        private void OnDestroy()
        {
            if (_audio != null) UiKit.Clicked -= _audio.Click;
            _perf?.Dispose();
            _weather?.Dispose();
            _effects?.Dispose();
            _audio?.Dispose();
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
                        else _kills++;
                        break;
                    case SimEventKind.PointCaptured when !_menu:
                        var letter = Strings.Get("point." + e.DefId);
                        if (e.Team == PlayerTeam) _hud.Toast(Strings.Format("toast.captured", letter));
                        else if (e.Team == EnemyTeam) _hud.Toast(Strings.Format("toast.lost", letter), error: true);
                        break;
                    case SimEventKind.StrikeWarning:
                        if (_world.Catalog.TryGetSupport(e.DefId, out var support))
                            _warnings.Add((new Vector2(e.Position.X, e.Position.Y), support.IsLine ? support.Length * 0.5f : support.Radius,
                                Time.time + e.Value + support.Duration + 0.5f));
                        if (!_menu && e.Team == EnemyTeam) _hud.Toast(Strings.Format("toast.enemyStrike", Strings.Support(e.DefId)), error: true);
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
                MatchSettings.InMatch = true;
                Reload();
            };
            var builtInVietnamese = Strings.Vietnamese;
            _hud.VolumeChanged += () => AudioListener.volume = MatchSettings.Volume;
            _hud.SettingsChanged += () =>
            {
                AudioListener.volume = MatchSettings.Volume;
                MatchSettings.ApplyLanguage();
                // The HUD is built once; rebuild it in the new language. New graphics options
                // rebuild the scene too, so the menu battle shows them straight away.
                if (Strings.Vietnamese != builtInVietnamese || GraphicsSignature() != _builtGraphics)
                {
                    _frameRateTarget = MatchSettings.Options.FrameRate;
                    Reload();
                }
            };
            if (_menu) return;

            _hud.SelectAllPressed += _selection.SelectAll;
            _hud.StopPressed += _selection.Stop;
            _hud.RetreatPressed += _selection.Retreat;
            _hud.AttackMovePressed += _selection.ToggleAttackMove;
            _hud.BoxModeToggled += () => _selection.BoxMode = !_selection.BoxMode;
            _hud.ZoomPressed += factor => _camera.ZoomBy(factor, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
            _hud.RestartPressed += () =>
            {
                ClaimReward();
                Reload();
            };
            _hud.MenuPressed += () =>
            {
                ClaimReward();
                MatchSettings.InMatch = false;
                Reload();
            };
            _hud.NextMissionPressed += () =>
            {
                ClaimReward();
                var next = Campaign.IndexOf(MatchSettings.Mission) + 1;
                if (next > 0 && next < Campaign.All.Count) MatchSettings.Mission = Campaign.All[next].Id;
                MatchSettings.Save();
                Reload();
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
            PlaceholderAds.Presenter = _hud.ShowPlaceholderAd;
            _hud.PausePressed += () => SetPaused(!_paused);
            _hud.ResumePressed += () => SetPaused(false);
            _hud.MinimapClicked += p => _camera.FocusOn(new Vector3(p.x, 0f, p.y));
            var playerAi = _session.PlayerAi;
            _hud.StancePressed += defend =>
            {
                playerAi.Stance = defend ? CommanderStance.Defend : CommanderStance.Attack;
                _hud.Toast(Strings.Get(defend ? "toast.defend" : "toast.attack"));
            };
            _hud.AutoDeployToggled += () =>
            {
                MatchSettings.AutoDeploy = playerAi.AutoDeploy = !playerAi.AutoDeploy;
                MatchSettings.Save();
            };
            _hud.AutoStrikeToggled += () =>
            {
                MatchSettings.AutoStrike = playerAi.AutoStrike = !playerAi.AutoStrike;
                MatchSettings.Save();
            };
            _hud.PointPressed += id =>
            {
                playerAi.FocusPoint = playerAi.FocusPoint == id ? null : id;
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

        private static void Reload()
        {
            Time.timeScale = 1f;
            AudioListener.pause = false;
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
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
            if (touching || _commander?.ArmedSupport != null || _paused) _lastInput = Time.unscaledTime;
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
            if (_attractFocus != Vector3.zero) _camera.Glide(_attractFocus, _camera.Zoom, Time.unscaledDeltaTime, 0.5f);
        }

        private void UpdateStatus()
        {
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
            foreach (var v in _world.Vehicles)
            {
                if (!v.IsAlive || (v.Team != PlayerTeam && !v.IsVisibleTo(PlayerTeam))) continue;
                minimap.Blip(new Vector2(v.Position.X, v.Position.Y), v.Team == PlayerTeam ? 0 : 1, v.Flying);
            }
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
            var outcome = _session.Outcome(_world, _kills, _losses);
            if (outcome == null) return;
            _resultShown = true;
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
                var index = _session is MissionSession ? Campaign.IndexOf(MatchSettings.Mission) : -1;
                view.HasNext = outcome.Result > 0 && index >= 0 && index + 1 < Campaign.All.Count;
            }
            _hud.ShowResult(outcome.Result, outcome.Subtitle, outcome.Rows, view);
        }

        /// <summary>Pays the battle's reward if the player leaves without claiming it.</summary>
        private void ClaimReward()
        {
            if (_reward == null || _reward.Claimed) return;
            _reward.Claim();
        }
    }
}
