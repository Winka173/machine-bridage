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
        private MapView _map;
        private ViewRegistry _views;
        private EffectsDirector _effects;
        private RtsCamera _camera;
        private SelectionController _selection;
        private TouchGestures _gestures;
        private SandboxHud _hud;
        private float _fps = 60f;

        private void Awake()
        {
            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            Time.timeScale = 1f;
            ConfigureAtmosphere();

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
            _map = new MapView(_world, _meshes, _materials, worldRoot);
            _views = new ViewRegistry(_meshes, _materials, worldRoot, PlayerTeam);

            _world.TryGetRally(PlayerTeam, out var rally);
            _camera = new RtsCamera(Camera.main, map.HalfSize, new Vector3(rally.X + 18f, 0f, rally.Y + 18f));
            _effects = new EffectsDirector(_materials, _meshes, _camera, worldRoot,
                Application.isMobilePlatform ? EffectBudget.Eco : EffectBudget.High);

            _hud = new SandboxHud();
            _selection = new SelectionController(_world, _views, _camera, _map, PlayerTeam);
            _gestures = new TouchGestures(_selection, _hud.IsOverUi);
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
            _hud.ReinforcePressed += () =>
            {
                if (!_mode.TryReinforce(_world)) _hud.Toast("Reinforcements not ready");
            };
            _hud.RestartPressed += () => SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
            _selection.Rejected += _hud.ShowError;
            _selection.MoveOrdered += _effects.ShowMoveMarker;
            _selection.BoxChanged += _hud.ShowSelectionBox;
            _selection.BoxHidden += _hud.HideSelectionBox;
        }

        private void UpdateStatus()
        {
            if (Time.unscaledDeltaTime > 0f) _fps = Mathf.Lerp(_fps, 1f / Time.unscaledDeltaTime, 0.05f);
            _hud.SetReinforceCooldown(_mode.ReinforceCooldown);
            _hud.SetAttackMoveArmed(_selection.AttackMoveArmed);
            _hud.SetStatus(
                $"Allies {_world.CountAlive(PlayerTeam)}    Enemies {_world.CountAlive(SandboxMode.EnemyTeam)}    " +
                $"Wave {_mode.Wave} (next in {Mathf.CeilToInt(_mode.SecondsToNextWave)} s)    {_fps:0} FPS\n" +
                (_selection.SelectedCount > 0
                    ? $"{_selection.SelectedCount} selected: tap ground to move, tap enemy or barrel to attack"
                    : "Tap a vehicle to select, hold and drag to box-select, double-tap for all of a type"));
        }

        /// <summary>
        /// Lighting that does not depend on baked data: explicit ambient colours for the voxel
        /// shader and linear fog to soften the horizon.
        /// </summary>
        private static void ConfigureAtmosphere()
        {
            Shader.SetGlobalColor("_MB_AmbientSky", new Color(0.46f, 0.5f, 0.6f));
            Shader.SetGlobalColor("_MB_AmbientGround", new Color(0.24f, 0.21f, 0.18f));
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.66f, 0.71f, 0.76f);
            RenderSettings.fogStartDistance = 110f;
            RenderSettings.fogEndDistance = 380f;
        }
    }
}
