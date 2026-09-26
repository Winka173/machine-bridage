using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Input;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Composition root for a match: builds the simulation, views, effects, input and HUD,
    /// then drives the fixed-step loop. Restarting reloads the scene, which resets every
    /// system and view in one go (V2 rule 9).
    /// </summary>
    public sealed class MatchRunner : MonoBehaviour
    {
        private const string MapId = "ashfield_sandbox";
        private const int PlayerTeam = SandboxMode.PlayerTeam;

        private SimWorld _world;
        private SandboxMode _mode;
        private SandboxAi _ai;
        private SimClock _clock;
        private MaterialLibrary _materials;
        private MeshLibrary _meshes;
        private ModelLibrary _models;
        private Atmosphere _atmosphere;
        private MapView _map;
        private ViewRegistry _views;
        private EffectsDirector _effects;
        private RtsCamera _camera;
        private SelectionController _selection;
        private TouchGestures _gestures;
        private BattleHud _hud;
        private float _fps = 60f;
        private int _announcedWave;

        private void Awake()
        {
            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            Time.timeScale = 1f;
            _atmosphere = new Atmosphere();

            var catalog = GameContent.LoadCatalog();
            var map = GameContent.LoadMap(MapId);
            _world = new SimWorld(catalog, map, seed: 1234);
            _mode = new SandboxMode();
            _mode.Setup(_world);
            _ai = new SandboxAi(SandboxMode.EnemyTeam, PlayerTeam);
            _clock = new SimClock();

            var worldRoot = new GameObject("Battlefield").transform;
            _materials = new MaterialLibrary();
            _meshes = new MeshLibrary();
            _models = new ModelLibrary(_materials);
            _map = new MapView(_world, _models, _materials, worldRoot);
            _views = new ViewRegistry(_models, _meshes, _materials, worldRoot, PlayerTeam);

            _world.TryGetRally(PlayerTeam, out var rally);
            _camera = new RtsCamera(Camera.main, map.HalfSize, new Vector3(rally.X + 16f, 0f, rally.Y + 16f));
            _effects = new EffectsDirector(_materials, _meshes, _models, _camera, worldRoot,
                Application.isMobilePlatform ? EffectBudget.Eco : EffectBudget.High);

            _hud = new BattleHud();
            _selection = new SelectionController(_world, _views, _camera, _map, PlayerTeam);
            _gestures = new TouchGestures(_selection, _hud.IsOverUi) { BoxMode = () => _selection.BoxMode };
            Wire();

            DispatchEvents();
        }

        private void OnEnable() => _gestures?.Enable();

        private void OnDisable() => _gestures?.Disable();

        private void Update()
        {
            _gestures.Tick(Time.unscaledTime);

            var steps = _clock.Advance(Time.deltaTime);
            var dt = (float)_clock.StepSeconds;
            for (var i = 0; i < steps; i++)
            {
                _mode.Tick(_world, dt);
                _ai.Tick(_world, dt);
                _world.Step(dt);
                _views.SnapshotAll();
                DispatchEvents();
            }

            _selection.Tick();
            _effects.Tick();
            _hud.Tick();
            UpdateStatus();
        }

        private void LateUpdate()
        {
            _camera.Apply(Time.unscaledDeltaTime);
            _views.Render(_clock.Alpha, _camera.Rotation);
        }

        private void OnDestroy()
        {
            _effects?.Dispose();
            _views?.Dispose();
            _map?.Dispose();
            _hud?.Dispose();
            _meshes?.Dispose();
            _materials?.Dispose();
            _atmosphere?.Dispose();
            Time.timeScale = 1f;
        }

        private void DispatchEvents()
        {
            foreach (var e in _world.Events)
                if (e.Kind == SimEventKind.VehicleSpawned && _world.TryGetVehicle(e.Entity, out var vehicle))
                    _views.Add(vehicle);
            _effects.Consume(_world.Events, _views, _map);
            _world.ClearEvents();
        }

        private void Wire()
        {
            _hud.SelectAllPressed += _selection.SelectAll;
            _hud.StopPressed += _selection.Stop;
            _hud.RetreatPressed += _selection.Retreat;
            _hud.AttackMovePressed += _selection.ToggleAttackMove;
            _hud.BoxModeToggled += () => _selection.BoxMode = !_selection.BoxMode;
            _hud.ZoomPressed += factor => _camera.ZoomBy(factor, new Vector2(Screen.width * 0.5f, Screen.height * 0.5f));
            _hud.ReinforcePressed += () =>
            {
                if (!_mode.TryReinforce(_world)) _hud.Toast(Strings.Get("toast.reinforceWait"), error: true);
            };
            _hud.RestartPressed += () => SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
            _selection.Rejected += _hud.ShowError;
            _selection.MoveOrdered += _effects.ShowMoveMarker;
            _selection.BoxChanged += _hud.ShowSelectionBox;
            _selection.BoxHidden += _hud.HideSelectionBox;
            _hud.Toast(Strings.Get("toast.start"), seconds: 4f);
        }

        private void UpdateStatus()
        {
            if (Time.unscaledDeltaTime > 0f) _fps = Mathf.Lerp(_fps, 1f / Time.unscaledDeltaTime, 0.05f);
            if (_mode.Wave != _announcedWave)
            {
                _announcedWave = _mode.Wave;
                if (_announcedWave > 0) _hud.Toast(Strings.Format("toast.wave", _announcedWave), error: true);
            }
            _hud.SetStats(_world.CountAlive(PlayerTeam), _world.CountAlive(SandboxMode.EnemyTeam), _mode.Wave,
                _mode.SecondsToNextWave, _fps);
            _hud.SetReinforceCooldown(_mode.ReinforceCooldown, SandboxMode.ReinforceCooldownSeconds);
            _hud.SetModes(_selection.AttackMoveArmed, _selection.BoxMode);
            _hud.SetSelection(_selection.Summary());
        }
    }
}
