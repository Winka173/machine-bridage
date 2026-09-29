using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Input;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using SimVector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 21: the Sandbox's glue in the battle scene. It owns the editor, the screen (<see cref="SandboxScreen"/>)
    /// and the overlays (<see cref="SandboxOverlays"/>), turns taps and drags into placements, turns and orders, and
    /// decides how many steps the battle takes a frame (paused, one tick, x0.25 to x4). While setting up, every
    /// change of the scenario is mirrored onto the standing field; Run and Reset rebuild the scene from the scenario,
    /// so a run always starts from exactly what the scenario says (and its seed).
    /// </summary>
    internal sealed class SandboxController : IGestureHandler
    {
        public static readonly float[] Speeds = { 0.25f, 0.5f, 1f, 2f, 4f };

        private readonly SimWorld _world;
        private readonly ViewRegistry _views;
        private readonly RtsCamera _camera;
        private readonly SelectionController _selection;
        private int _stepsWanted;
        private Vector2 _pressAt;
        private bool _dragging;

        public SandboxController(SimWorld world, SandboxSession session, ViewRegistry views, RtsCamera camera, SelectionController selection,
            MaterialLibrary materials, MeshLibrary meshes, Transform worldRoot)
        {
            _world = world;
            Session = session;
            _views = views;
            _camera = camera;
            _selection = selection;
            Editor = new SandboxEditor(world.Catalog, world.Map, session.Battle.Scenario.Clone(), SandboxSession.Internal,
                def => session.Access.Allowed(world.Catalog, def));
            Editor.Changed += OnEdited;
            Overlays = new SandboxOverlays(this, world, views, camera, materials, worldRoot);
            Screen = new SandboxScreen(this);
            Overlays.Labels = Screen.LabelLayer;
            if (!SandboxProfile.HintSeen) Screen.ShowHint();
            if (!Editing) Screen.Toast(Strings.Get("sandbox.noRewards"));
        }

        /// <summary>
        /// A preview with no battlefield drawn (the screenshots and the layout checks): the screen built into
        /// <paramref name="host"/>, no overlays, no input.
        /// </summary>
        internal SandboxController(SimWorld world, SandboxSession session, VisualElement host)
        {
            _world = world;
            Session = session;
            Editor = new SandboxEditor(world.Catalog, world.Map, session.Battle.Scenario.Clone(), SandboxSession.Internal,
                def => session.Access.Allowed(world.Catalog, def));
            Editor.Changed += OnEdited;
            Screen = new SandboxScreen(this, host);
        }

        /// <summary>Which overlays are on (E): kept here so the screen's tray works with or without the overlays drawn.</summary>
        public Dictionary<SandboxLayer, bool> Layers { get; } = new() { [SandboxLayer.Range] = true, [SandboxLayer.Hits] = true };

        public bool LayerOn(SandboxLayer layer) => Layers.TryGetValue(layer, out var on) && on && (!SandboxOverlays.Internal(layer) || SandboxSession.Internal);

        public SimWorld World => _world;
        public SandboxSession Session { get; }
        public SandboxBattle Battle => Session.Battle;
        public SandboxEditor Editor { get; }
        public SandboxScreen Screen { get; }
        public SandboxOverlays Overlays { get; }
        public RtsCamera Camera => _camera;

        public bool Editing => Session.Editing;
        public bool Paused { get; set; }
        public int SpeedIndex { get; set; } = 2;
        public float Speed => Speeds[Mathf.Clamp(SpeedIndex, 0, Speeds.Length - 1)];

        // ------------------------------------------------------------------ selection and armed tools

        /// <summary>Set-up: the selected scenario units (indices). Running: the selected vehicles (entity ids).</summary>
        public List<int> Selected { get; } = new();

        /// <summary>The unit kind the next tap places (null: taps select).</summary>
        public string Placing { get; set; }

        /// <summary>Several at once (B.5); null places one.</summary>
        public SandboxFormation? Formation { get; set; }

        public int FormationCount { get; set; } = 4;

        public enum Pick
        {
            None,
            MoveUnits,
            OrderMove,
            OrderTarget,
            Strike,
        }

        /// <summary>What the next tap means besides placing and selecting.</summary>
        public Pick Picking { get; set; }

        /// <summary>The support the next tap calls (with <see cref="Pick.Strike"/>).</summary>
        public string Strike { get; set; }

        public int StrikeTeam { get; set; }

        /// <summary>Several taps add to the selection instead of replacing it.</summary>
        public bool MultiSelect { get; set; }

        public bool IsOverUi(Vector2 screen) => Screen.IsOverUi(screen);

        // ------------------------------------------------------------------ stepping

        /// <summary>The steps this frame: none while setting up or paused (one for a tick), else by the speed.</summary>
        public int Steps(float deltaTime, SimClock clock)
        {
            if (Editing) return 0;
            if (Paused)
            {
                if (_stepsWanted <= 0) return 0;
                _stepsWanted--;
                return 1;
            }
            return clock.Advance(deltaTime * Speed);
        }

        public void StepOnce()
        {
            Paused = true;
            _stepsWanted++;
        }

        /// <summary>Every frame after the battle's steps: the screen and the overlays.</summary>
        public void Tick(float unscaledDt)
        {
            TrackPress();
            Selected.RemoveAll(i => Editing ? i < 0 || i >= Editor.Units.Count : !_world.TryGetVehicle(new EntityId(i), out var v) || !v.IsAlive);
            if (!Editing && Battle.LastSwapped > 0 && !Selected.Contains(Battle.LastSwapped) && Selected.Count == 0) Selected.Add(Battle.LastSwapped);
            Screen.Tick();
            Overlays?.Tick(unscaledDt);
        }

        // ------------------------------------------------------------------ set-up: the field follows the scenario

        private void OnEdited()
        {
            if (!Editing) return;
            var removed = Battle.Rebuild(_world, Editor.Scenario);
            if (_views != null)
            {
                foreach (var id in removed)
                {
                    var view = _views.Detach(new EntityId(id));
                    if (view != null) Object.Destroy(view.Root.gameObject);
                }
                foreach (var v in _world.Vehicles)
                    if (v.IsAlive) _views.Add(v);
                _views.SnapshotAll();
                _views.SnapshotAll();
            }
            Screen.Refresh();
        }

        /// <summary>The entity standing for scenario unit <paramref name="index"/> while setting up (0: none).</summary>
        public int EntityOf(int index) => index >= 0 && index < Battle.Spawned.Count ? Battle.Spawned[index] : 0;

        /// <summary>The selection's vehicles (either state).</summary>
        public IEnumerable<MachineBrigade.Sim.Entities.Vehicle> SelectedVehicles()
        {
            foreach (var i in Selected)
                if (_world.TryGetVehicle(new EntityId(Editing ? EntityOf(i) : i), out var v) && v.IsAlive) yield return v;
        }

        // ------------------------------------------------------------------ run, reset, leave

        /// <summary>Rebuilds the scene from the scenario: running at once, or back in set-up.</summary>
        public void Rebuild(bool run)
        {
            SandboxSession.Scenario = Editor.Scenario.Clone();
            SandboxSession.RunOnLoad = run;
            var scene = SceneManager.GetActiveScene().buildIndex;
            Curtain.Close(Strings.Get("sandbox.title").ToUpperInvariant(), Strings.Get(run ? "sandbox.running" : "sandbox.editing"), () => SceneManager.LoadScene(scene));
        }

        /// <summary>Queues a control for the running battle (it takes effect on the next step, in the journal).</summary>
        public void Queue(SandboxOp op)
        {
            if (Editing) return;
            Battle.Queue(op);
        }

        // ------------------------------------------------------------------ gestures

        private void TrackPress()
        {
            if (Touchscreen.current != null && Touchscreen.current.primaryTouch.press.wasPressedThisFrame)
                _pressAt = Touchscreen.current.primaryTouch.position.ReadValue();
            else if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame)
                _pressAt = Mouse.current.position.ReadValue();
        }

        /// <summary>A drag that starts on a selected unit turns it (B.4) instead of moving the camera.</summary>
        public bool DragTurns()
        {
            if (!Editing || Selected.Count == 0) return false;
            foreach (var v in SelectedVehicles())
            {
                var p = _camera.Camera.WorldToScreenPoint(new Vector3(v.Position.X, 0f, v.Position.Y));
                if (p.z > 0f && Vector2.Distance(new Vector2(p.x, p.y), _pressAt) < 60f) return true;
            }
            return false;
        }

        private bool Ground(Vector2 screen, out SimVector2 point)
        {
            point = default;
            if (!_camera.TryGroundPoint(screen, out var g)) return false;
            point = new SimVector2(g.x, g.z);
            return true;
        }

        private float LastHeading => Selected.Count > 0 && Editing && Selected[0] < Editor.Units.Count ? Editor.Units[Selected[0]].Heading : Editor.Team == 0 ? 0f : 180f;

        public void OnTap(Vector2 screen)
        {
            var picked = _views.Pick(screen, _camera.Camera, 24f);
            if (Editing) TapEditing(screen, picked);
            else TapRunning(screen, picked);
            Screen.Refresh();
        }

        private void TapEditing(Vector2 screen, VehicleView picked)
        {
            if (!Ground(screen, out var at)) return;
            if (Picking == Pick.MoveUnits)
            {
                Picking = Pick.None;
                if (!Editor.Move(Selected, at)) Screen.Toast(Strings.Get("sandbox.refuse.OffMap"), true);
                return;
            }
            if (Placing != null)
            {
                var refusal = Formation is { } shape
                    ? Editor.PlaceFormation(Placing, at, LastHeading, shape, FormationCount, out var placed)
                    : Editor.Place(Placing, at, LastHeading, out var one);
                if (refusal != SandboxRefusal.None)
                {
                    Screen.Toast(Refusal(refusal), true);
                    return;
                }
                Selected.Clear();
                if (Formation != null)
                {
                    for (var i = Editor.Units.Count - 1; i >= 0 && Selected.Count < FormationCount; i--) Selected.Add(i);
                }
                else Selected.Add(Editor.Units.Count - 1);
                if (Editor.OverCapWarning) Screen.Toast(CapText("sandbox.cap.warn"), true);
                return;
            }
            var index = -1;
            if (picked != null)
                for (var i = 0; i < Battle.Spawned.Count; i++)
                    if (Battle.Spawned[i] == picked.Id.Value) index = i;
            if (index < 0) index = Editor.NearestUnit(at, 3f);
            if (!MultiSelect) Selected.Clear();
            if (index >= 0)
            {
                if (Selected.Contains(index)) Selected.Remove(index);
                else Selected.Add(index);
            }
        }

        private void TapRunning(Vector2 screen, VehicleView picked)
        {
            switch (Picking)
            {
                case Pick.OrderMove when Ground(screen, out var to):
                    Picking = Pick.None;
                    Queue(new SandboxOp { Kind = SandboxOpKind.Move, Units = Selected.ToArray(), Point = to });
                    return;
                case Pick.OrderTarget when picked != null:
                    Picking = Pick.None;
                    Queue(new SandboxOp { Kind = SandboxOpKind.FireAt, Units = Selected.ToArray(), Target = picked.Id.Value });
                    return;
                case Pick.Strike when Ground(screen, out var there) && Strike != null:
                    Picking = Pick.None;
                    Queue(new SandboxOp { Kind = SandboxOpKind.Strike, Team = StrikeTeam, Text = Strike, Point = there });
                    return;
            }
            if (!MultiSelect) Selected.Clear();
            if (picked == null) return;
            if (Selected.Contains(picked.Id.Value)) Selected.Remove(picked.Id.Value);
            else Selected.Add(picked.Id.Value);
        }

        public void OnDoubleTap(Vector2 screen) { }

        public void OnPan(Vector2 fromScreen, Vector2 toScreen) => _selection.OnPan(fromScreen, toScreen);

        public void OnPinch(float scale, Vector2 centreScreen) => _selection.OnPinch(scale, centreScreen);

        public void OnBoxUpdate(Vector2 startScreen, Vector2 currentScreen)
        {
            _dragging = true;
            if (Overlays != null && Ground(currentScreen, out var to)) Overlays.DragTo = to;
        }

        public void OnBoxEnd(Vector2 startScreen, Vector2 endScreen)
        {
            _dragging = false;
            if (Overlays != null) Overlays.DragTo = null;
            if (!Editing || Selected.Count == 0 || !Ground(endScreen, out var to)) return;
            var from = Editor.Units[Selected[0]].Position;
            Editor.Rotate(Selected, SandboxRules.HeadingTowards(from, to, Editor.FreeRotation));
        }

        public void OnBoxCancel()
        {
            _dragging = false;
            if (Overlays != null) Overlays.DragTo = null;
        }

        public bool Dragging => _dragging;

        // ------------------------------------------------------------------ words

        public static string Refusal(SandboxRefusal r) =>
            r == SandboxRefusal.CapReached ? CapText("sandbox.refuse.CapReached") : Strings.Get("sandbox.refuse." + r);

        private static string CapText(string key) =>
            SandboxText.Format(key, ("vehicles", SandboxRules.VehicleCap), ("aircraft", SandboxRules.AircraftCap));
    }
}
