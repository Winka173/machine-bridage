using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using UnityEngine;
using SimVector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Input
{
    /// <summary>
    /// The player's hands: selection, orders from taps, and camera gestures. Every order goes
    /// through <see cref="SimWorld.Submit"/>, exactly like the AI's.
    /// </summary>
    public sealed class SelectionController : IGestureHandler
    {
        private readonly SimWorld _world;
        private readonly ViewRegistry _views;
        private readonly RtsCamera _camera;
        private readonly MapView _map;
        private readonly int _team;
        private readonly HashSet<EntityId> _selected = new();
        private readonly List<EntityId> _order = new();
        private readonly float _pickMargin;

        public SelectionController(SimWorld world, ViewRegistry views, RtsCamera camera, MapView map, int team)
        {
            _world = world;
            _views = views;
            _camera = camera;
            _map = map;
            _team = team;
            _pickMargin = 28f * Mathf.Max(1f, Screen.dpi / 160f);
        }

        /// <summary>Raised when a command is refused, so the HUD can say why.</summary>
        public event Action<CommandError> Rejected;

        public event Action<Vector3> MoveOrdered;
        public event Action<Vector2, Vector2> BoxChanged;
        public event Action BoxHidden;

        public int SelectedCount => _selected.Count;

        /// <summary>When armed, the next ground tap issues attack-move instead of move.</summary>
        public bool AttackMoveArmed { get; private set; }

        public void OnTap(Vector2 screen)
        {
            var picked = _views.Pick(screen, _camera.Camera, _pickMargin);
            if (picked != null && picked.Team == _team)
            {
                _selected.Clear();
                _selected.Add(picked.Id);
                return;
            }
            if (_selected.Count == 0) return;

            if (picked != null)
            {
                Issue(new Command(CommandType.Attack, _team, Selection(), target: picked.Id));
                return;
            }
            if (!_camera.TryGroundPoint(screen, out var ground)) return;
            var point = new SimVector2(ground.x, ground.z);

            if (!AttackMoveArmed)
            {
                var prop = _map.PropAt(point);
                if (prop != null)
                {
                    Issue(new Command(CommandType.Attack, _team, Selection(), target: prop.Id));
                    return;
                }
            }

            var type = AttackMoveArmed ? CommandType.AttackMove : CommandType.Move;
            AttackMoveArmed = false;
            if (Issue(new Command(type, _team, Selection(), point))) MoveOrdered?.Invoke(ground);
        }

        public void OnDoubleTap(Vector2 screen)
        {
            var picked = _views.Pick(screen, _camera.Camera, _pickMargin);
            if (picked == null || picked.Team != _team) return;
            _selected.Clear();
            var viewport = new Rect(0f, 0f, Screen.width, Screen.height);
            foreach (var view in _views.All)
                if (view.Team == _team && view.DefId == picked.DefId && OnScreen(view, viewport)) _selected.Add(view.Id);
        }

        public void OnPan(Vector2 fromScreen, Vector2 toScreen) => _camera.Pan(fromScreen, toScreen);

        public void OnPinch(float scale, Vector2 centreScreen) => _camera.ZoomBy(scale, centreScreen);

        public void OnBoxUpdate(Vector2 startScreen, Vector2 currentScreen) => BoxChanged?.Invoke(startScreen, currentScreen);

        public void OnBoxEnd(Vector2 startScreen, Vector2 endScreen)
        {
            BoxHidden?.Invoke();
            var rect = Rect.MinMaxRect(Mathf.Min(startScreen.x, endScreen.x), Mathf.Min(startScreen.y, endScreen.y),
                Mathf.Max(startScreen.x, endScreen.x), Mathf.Max(startScreen.y, endScreen.y));
            var found = new List<EntityId>();
            foreach (var view in _views.All)
                if (view.Team == _team && OnScreen(view, rect)) found.Add(view.Id);
            if (found.Count == 0) return;
            _selected.Clear();
            foreach (var id in found) _selected.Add(id);
        }

        public void OnBoxCancel() => BoxHidden?.Invoke();

        public void SelectAll()
        {
            _selected.Clear();
            foreach (var view in _views.All)
                if (view.Team == _team) _selected.Add(view.Id);
        }

        public void Stop() => Issue(new Command(CommandType.Stop, _team, Selection()));

        public void Retreat() => Issue(new Command(CommandType.Retreat, _team, Selection()));

        public void ToggleAttackMove()
        {
            if (_selected.Count == 0)
            {
                Rejected?.Invoke(CommandError.NoUnits);
                return;
            }
            AttackMoveArmed = !AttackMoveArmed;
        }

        /// <summary>Drops dead vehicles from the selection and updates selection rings.</summary>
        public void Tick()
        {
            _selected.RemoveWhere(id => !_views.TryGet(id, out _));
            foreach (var view in _views.All) view.Selected = _selected.Contains(view.Id);
            if (_selected.Count == 0) AttackMoveArmed = false;
        }

        private bool Issue(Command command)
        {
            var result = _world.Submit(command);
            if (!result.Accepted) Rejected?.Invoke(result.Error);
            return result.Accepted;
        }

        private IReadOnlyList<EntityId> Selection()
        {
            _order.Clear();
            _order.AddRange(_selected);
            return _order.ToArray();
        }

        private bool OnScreen(VehicleView view, Rect rect)
        {
            var sp = _camera.Camera.WorldToScreenPoint(view.Position + Vector3.up);
            return sp.z > 0f && rect.Contains(new Vector2(sp.x, sp.y));
        }
    }
}
