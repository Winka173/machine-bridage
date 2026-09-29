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
    /// <summary>What the HUD shows about the current selection.</summary>
    public readonly struct SelectionSummary
    {
        public SelectionSummary(int count, string defId, float hp, float maxHp)
        {
            Count = count;
            DefId = defId;
            Hp = hp;
            MaxHp = maxHp;
        }

        public int Count { get; }

        /// <summary>Shared vehicle type, or null for a mixed group.</summary>
        public string DefId { get; }

        public float Hp { get; }
        public float MaxHp { get; }
    }

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

        /// <summary>A tap landed on a part of an enemy boss (prompt 9): the boss and the part's index.</summary>
        public event Action<EntityId, int> PartTapped;

        /// <summary>Raised when a command is refused, so the HUD can say why.</summary>
        public event Action<CommandError> Rejected;

        public event Action<Vector3> MoveOrdered;
        public event Action<Vector2, Vector2> BoxChanged;
        public event Action BoxHidden;

        public int SelectedCount => _selected.Count;

        /// <summary>When armed, the next ground tap issues attack-move instead of move.</summary>
        public bool AttackMoveArmed { get; private set; }

        /// <summary>When on, a one-finger drag box-selects instead of panning (the HUD's Box tool).</summary>
        public bool BoxMode { get; set; }

        public SelectionSummary Summary()
        {
            string defId = null;
            var mixed = false;
            float hp = 0f, maxHp = 0f;
            var count = 0;
            foreach (var view in _views.All)
            {
                if (!_selected.Contains(view.Id)) continue;
                count++;
                hp += view.Sim.Hp;
                maxHp += view.Sim.MaxHp;
                if (defId == null) defId = view.DefId;
                else if (defId != view.DefId) mixed = true;
            }
            return new SelectionSummary(count, mixed ? null : defId, hp, maxHp);
        }

        /// <summary>
        /// Prompt 13 C.9: what the selection carries for the panel's ammunition bar: each aircraft's biggest
        /// store (its bombs, rockets or missiles), a launcher's salvos, summed over the selected vehicles of
        /// that kind; slow while any of them takes its stores on at the slow rate or waits to reload.
        /// </summary>
        public (int left, int full, MachineBrigade.Sim.Content.ProjectileKind kind, bool slow) Stores()
        {
            int left = 0, full = 0;
            var kind = MachineBrigade.Sim.Content.ProjectileKind.Bullet;
            var slow = false;
            var chosen = false;
            foreach (var view in _views.All)
            {
                if (!_selected.Contains(view.Id)) continue;
                var v = view.Sim;
                var mounts = v.Def.Mounts;
                var best = -1;
                if (v.HasStores)
                {
                    for (var i = 0; i < mounts.Count; i++)
                        if (v.Stores(i).full > 0 && (best < 0 || v.Stores(i).full > v.Stores(best).full)) best = i;
                    if (v.RearmRate > 0f && v.RearmRate < 1f) slow = true;
                }
                else if (!v.Def.Static && mounts.Count > 0 && mounts[0].Weapon.Ammo > 0)
                {
                    best = 0;
                    if (v.ReloadPaused) slow = true;
                }
                if (best < 0) continue;
                var weapon = mounts[best].Weapon;
                if (!chosen)
                {
                    kind = weapon.Projectile;
                    chosen = true;
                }
                if (weapon.Projectile != kind) continue;
                if (v.HasStores)
                {
                    var (l, f) = v.Stores(best);
                    left += l;
                    full += f;
                }
                else
                {
                    left += Math.Max(0, v.Ammo(0));
                    full += weapon.Ammo;
                }
            }
            return (left, full, kind, slow);
        }

        /// <summary>Gets first refusal on taps (strike targeting); returns true when it used the tap.</summary>
        public Func<Vector2, bool> TapInterceptor { get; set; }

        /// <summary>After a tap is used for strike targeting, a quick second tap is not an order.</summary>
        private float _ignoreTapsUntil;

        private bool Intercepted(Vector2 screen)
        {
            if (TapInterceptor != null && TapInterceptor(screen))
            {
                _ignoreTapsUntil = Time.unscaledTime + 0.35f;
                return true;
            }
            return Time.unscaledTime < _ignoreTapsUntil;
        }

        public void OnTap(Vector2 screen)
        {
            if (Intercepted(screen)) return;
            var picked = _views.Pick(screen, _camera.Camera, _pickMargin);
            if (picked != null && Mine(picked))
            {
                _selected.Clear();
                _selected.Add(picked.Id);
                return;
            }
            // A tap on one of an enemy boss's parts: every unit in reach goes for it (and the selection attacks the boss).
            if (picked != null && picked.Team != _team && picked.Sim.HasParts && PartTapped != null)
            {
                var part = PartUnder(picked, screen);
                if (part >= 0) PartTapped(picked.Id, part);
            }
            if (_selected.Count == 0 || (picked != null && picked.Team == _team)) return;

            if (picked != null)
            {
                Issue(new Command(CommandType.Attack, _team, Selection(), target: picked.Id, manual: true));
                return;
            }
            if (!_camera.TryGroundPoint(screen, out var ground)) return;
            var point = new SimVector2(ground.x, ground.z);

            if (!AttackMoveArmed)
            {
                var prop = _map.PropAt(point);
                if (prop != null)
                {
                    Issue(new Command(CommandType.Attack, _team, Selection(), target: prop.Id, manual: true));
                    return;
                }
            }

            var type = AttackMoveArmed ? CommandType.AttackMove : CommandType.Move;
            AttackMoveArmed = false;
            if (Issue(new Command(type, _team, Selection(), point, manual: true))) MoveOrdered?.Invoke(ground);
        }

        public void OnDoubleTap(Vector2 screen)
        {
            if (Intercepted(screen)) return;
            var picked = _views.Pick(screen, _camera.Camera, _pickMargin);
            if (picked == null || !Mine(picked))
            {
                // A quick second tap on the ground or an enemy is still an order.
                OnTap(screen);
                return;
            }
            _selected.Clear();
            var viewport = new Rect(0f, 0f, Screen.width, Screen.height);
            foreach (var view in _views.All)
                if (Mine(view) && view.DefId == picked.DefId && OnScreen(view, viewport)) _selected.Add(view.Id);
        }

        public void OnPan(Vector2 fromScreen, Vector2 toScreen) =>
            _camera.Pan(fromScreen, fromScreen + (toScreen - fromScreen) * Match.MatchSettings.PanScale);

        public void OnPinch(float scale, Vector2 centreScreen) => _camera.ZoomBy(scale, centreScreen);

        public void OnBoxUpdate(Vector2 startScreen, Vector2 currentScreen) => BoxChanged?.Invoke(startScreen, currentScreen);

        public void OnBoxEnd(Vector2 startScreen, Vector2 endScreen)
        {
            BoxHidden?.Invoke();
            BoxMode = false;
            // A long press that barely moved is a slow tap (for example choosing a strike target).
            if (Vector2.Distance(startScreen, endScreen) < Screen.dpi * 0.12f + 8f)
            {
                OnTap(endScreen);
                return;
            }
            var rect = Rect.MinMaxRect(Mathf.Min(startScreen.x, endScreen.x), Mathf.Min(startScreen.y, endScreen.y),
                Mathf.Max(startScreen.x, endScreen.x), Mathf.Max(startScreen.y, endScreen.y));
            var found = new List<EntityId>();
            foreach (var view in _views.All)
                if (Mine(view) && OnScreen(view, rect)) found.Add(view.Id);
            if (found.Count == 0) return;
            _selected.Clear();
            foreach (var id in found) _selected.Add(id);
        }

        public void OnBoxCancel() => BoxHidden?.Invoke();

        public void SelectAll()
        {
            _selected.Clear();
            foreach (var view in _views.All)
                if (Mine(view)) _selected.Add(view.Id);
        }

        public void Stop() => Issue(new Command(CommandType.Stop, _team, Selection(), manual: true));

        public void Retreat() => Issue(new Command(CommandType.Retreat, _team, Selection(), manual: true));

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

        /// <summary>The player's own vehicle (not the allied commander's).</summary>
        private bool Mine(VehicleView view) => view.Team == _team && !view.Sim.Ally;

        /// <summary>The live part of a boss nearest the tap on screen, within a finger's reach of it, or -1.</summary>
        private int PartUnder(VehicleView boss, Vector2 screen)
        {
            var best = -1;
            var bestDistance = _pickMargin * 2.2f;
            for (var i = 0; i < boss.Sim.PartCount; i++)
            {
                if (boss.Sim.IsPartBroken(i)) continue;
                var at = _camera.Camera.WorldToScreenPoint(boss.PartWorld(i));
                if (at.z <= 0f) continue;
                var d = Vector2.Distance(new Vector2(at.x, at.y), screen);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = i;
            }
            return best;
        }

        private bool Issue(Command command)
        {
            var result = _world.SubmitPlayer(command);
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
