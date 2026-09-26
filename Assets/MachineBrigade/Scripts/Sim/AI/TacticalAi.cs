#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Utility-style opponent (game plan section 9). Every decision it sorts its army into roles
    /// and gives each the most useful order:
    /// <list type="bullet">
    /// <item>badly damaged heavy vehicles pull back behind the line;</item>
    /// <item>artillery holds a standoff position, shells clusters, and backs away from anything
    /// inside its minimum range;</item>
    /// <item>fast vehicles swing around a flank while the main body advances;</item>
    /// <item>the main body moves in bounds and waits for stragglers at each rendezvous, so it
    /// arrives together instead of trickling into the guns one by one.</item>
    /// </list>
    /// It only knows about enemies its team can see and issues ordinary commands, so it plays by
    /// the same rules as the player (architecture rule 8).
    /// </summary>
    public sealed class TacticalAi
    {
        private const float DecisionInterval = 0.75f;
        private const float DamagedFraction = 0.3f;
        private const float BoundLength = 24f;
        private const float FlankOffset = 24f;
        private const float FastSpeed = 11f;
        private const float ClusterRadius = 7f;
        private const int ClusterSize = 3;
        private const float EdgeMargin = 6f;

        /// <summary>A pulled-back vehicle rejoins once repaired this far, or after this long.</summary>
        private const float RecoveredFraction = 0.6f;
        private const float FallBackSeconds = 30f;

        private readonly int _team;
        private readonly int _enemyTeam;
        private float _flankSide;
        private bool _hadFlankers;
        private readonly List<Vehicle> _line = new();
        private readonly List<Vehicle> _fast = new();
        private readonly List<Vehicle> _artillery = new();
        private readonly List<Vehicle> _enemies = new();
        /// <summary>Vehicles pulled back to recover, with when they left the line.</summary>
        private readonly Dictionary<EntityId, double> _fallingBack = new();

        private readonly List<EntityId> _released = new();
        private Vector2 _lastObjective;
        private readonly HashSet<EntityId> _flanked = new();
        private readonly List<EntityId> _ids = new();
        private readonly List<EntityId> _otherIds = new();
        private float _timer;

        /// <summary>
        /// Where to advance when no enemy is in sight (Conquest: the objective to take). Null
        /// falls back to the enemy rally point.
        /// </summary>
        public Func<SimWorld, Vector2?>? Objective { get; set; }

        /// <summary>Visible enemy vehicles, refreshed every decision.</summary>
        public IReadOnlyList<Vehicle> KnownEnemies => _enemies;

        public TacticalAi(int team, int enemyTeam, int seed = 7)
        {
            _team = team;
            _enemyTeam = enemyTeam;
            _flankSide = new Random(seed).Next(2) == 0 ? -1f : 1f;
        }

        public void Tick(SimWorld world, float dt)
        {
            _timer -= dt;
            if (_timer > 0f) return;
            _timer = DecisionInterval;
            if (world.IsOver) return;

            Sort(world);
            var body = _line.Count > 0 ? _line : _fast.Count > 0 ? _fast : _artillery;
            if (body.Count == 0) return;

            var front = Centre(body);
            var contact = _enemies.Count > 0;
            Vector2 objective;
            // Aircraft do not steer the army: ground forces go for ground targets and objectives.
            var groundContact = NearestGround(front, out _) < float.MaxValue;
            var goal = Objective?.Invoke(world);
            if (groundContact && (goal == null || NearestGround(front, out _) < 45f)) objective = NearestCluster(front);
            else if (goal.HasValue) objective = goal.Value;
            else if (groundContact) objective = NearestCluster(front);
            else if (!world.TryGetRally(_enemyTeam, out objective)) return;
            contact = groundContact;
            // A new objective: every fast vehicle may be sent round a flank again.
            if (Vector2.Distance(objective, _lastObjective) > 20f) _flanked.Clear();
            _lastObjective = objective;
            var forward = Direction(front, objective);

            PullBackDamaged(world, front, forward);
            DirectArtillery(world, front, objective, forward, contact);
            DirectFlankers(world, objective, forward, contact);
            DirectMainBody(world, objective, contact);
        }

        private void Sort(SimWorld world)
        {
            _line.Clear();
            _fast.Clear();
            _artillery.Clear();
            _enemies.Clear();
            // Pulled-back vehicles rejoin once repaired (or rested a while); the dead are forgotten.
            _released.Clear();
            foreach (var (id, since) in _fallingBack)
                if (!world.TryGetVehicle(id, out var v) || !v.IsAlive || v.Hp / v.MaxHp >= RecoveredFraction || world.Time - since > FallBackSeconds)
                    _released.Add(id);
            foreach (var id in _released) _fallingBack.Remove(id);
            _flanked.RemoveWhere(id => !world.TryGetVehicle(id, out _));
            // Once a flanking group is spent, the next one swings round the other side.
            if (_hadFlankers && _flanked.Count == 0) _flankSide = -_flankSide;
            _hadFlankers = _flanked.Count > 0;

            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive) continue;
                if (v.Team == _enemyTeam)
                {
                    if (v.IsVisibleTo(_team)) _enemies.Add(v);
                    continue;
                }
                // Vehicles the player is steering by hand are left alone.
                if (v.Team != _team || _fallingBack.ContainsKey(v.Id) || v.UnderPlayerControl(world.Time)) continue;
                if (v.Def.Weapon.MinRange > 0f) _artillery.Add(v);
                else if (v.Def.Speed >= FastSpeed) _fast.Add(v);
                else _line.Add(v);
            }
        }

        /// <summary>Heavy vehicles close to death drop behind the line while others cover them.</summary>
        private void PullBackDamaged(SimWorld world, Vector2 front, Vector2 forward)
        {
            if (_line.Count + _fast.Count < 3) return;
            _ids.Clear();
            for (var i = _line.Count - 1; i >= 0; i--)
            {
                var v = _line[i];
                if (v.Armor != ArmorClass.Heavy || v.Hp / v.MaxHp > DamagedFraction || Nearest(v.Position, out _) > v.Def.VisionRange)
                    continue;
                _ids.Add(v.Id);
                _fallingBack[v.Id] = world.Time;
                _line.RemoveAt(i);
            }
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, Clamp(world, front - forward * 16f));
        }

        private void DirectArtillery(SimWorld world, Vector2 front, Vector2 objective, Vector2 forward, bool contact)
        {
            foreach (var a in _artillery)
            {
                var weapon = a.Def.Weapon;
                var closest = Nearest(a.Position, out var threat);
                if (threat != null && closest < weapon.MinRange + 6f)
                {
                    // Too close to shoot back: open the distance.
                    var away = Direction(threat.Position, a.Position);
                    Issue(world, CommandType.Move, a.Id, Clamp(world, a.Position + away * (weapon.MinRange + 14f - closest)));
                    continue;
                }
                if (a.Order.Kind == OrderKind.Move) continue;

                if (contact && TryFindCluster(a, out var cluster))
                {
                    if (a.Order.Kind != OrderKind.Attack) Issue(world, CommandType.Attack, a.Id, cluster.Position, cluster.Id);
                    continue;
                }
                if (a.Order.Kind != OrderKind.Idle || a.Target.IsValid) continue;

                // Stand off behind the main body, close enough to reach the enemy.
                var standoff = contact ? objective - forward * (weapon.Range * 0.7f) : front - forward * 18f;
                if (Vector2.Distance(standoff, objective) < Vector2.Distance(front, objective)) standoff = front - forward * 10f;
                if (Vector2.Distance(a.Position, standoff) > 10f) Issue(world, CommandType.Move, a.Id, Clamp(world, standoff));
            }
        }

        /// <summary>Fast vehicles drive round the side of the fight, then attack from there.</summary>
        private void DirectFlankers(SimWorld world, Vector2 objective, Vector2 forward, bool contact)
        {
            if (!contact || _fast.Count < 2 || _line.Count < 2)
            {
                _line.AddRange(_fast); // not enough for a flank: they fight with the main body
                return;
            }
            var side = new Vector2(-forward.Y, forward.X) * _flankSide;
            var flankPoint = Clamp(world, objective + side * FlankOffset - forward * 6f);
            _ids.Clear();
            _otherIds.Clear();
            foreach (var f in _fast)
            {
                if (f.Order.Kind != OrderKind.Idle || Busy(world, f)) continue;
                if (!_flanked.Contains(f.Id) && Vector2.Distance(f.Position, flankPoint) < 9f) _flanked.Add(f.Id);
                if (_flanked.Contains(f.Id)) _otherIds.Add(f.Id);
                else _ids.Add(f.Id);
            }
            // Move (not attack-move) on the way round, so they do not stop for the first thing they see.
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, flankPoint);
            if (_otherIds.Count > 0) Issue(world, CommandType.AttackMove, _otherIds, Clamp(world, objective));
        }

        /// <summary>
        /// Out of contact the body advances in bounds anchored on its lead vehicle: everyone gets
        /// the same next rendezvous, and the next bound starts only once most have arrived, so
        /// stragglers and fresh waves catch up instead of dragging the front back. In contact,
        /// everyone free joins the fight.
        /// </summary>
        private void DirectMainBody(SimWorld world, Vector2 objective, bool contact)
        {
            _ids.Clear();
            Vehicle? lead = null;
            var leadDistance = float.MaxValue;
            foreach (var v in _line)
            {
                var distance = Vector2.Distance(v.Position, objective);
                if (distance < leadDistance)
                {
                    lead = v;
                    leadDistance = distance;
                }
                if (v.Order.Kind == OrderKind.Idle && !Busy(world, v)) _ids.Add(v.Id);
            }
            if (_ids.Count == 0 || lead == null) return;

            if (contact)
            {
                // Those already standing on the objective stay put rather than being re-sent every decision.
                for (var i = _ids.Count - 1; i >= 0; i--)
                    if (world.TryGetVehicle(_ids[i], out var there) && Vector2.Distance(there.Position, objective) < 8f) _ids.RemoveAt(i);
                if (_ids.Count > 0) Issue(world, CommandType.AttackMove, _ids, Clamp(world, objective));
                return;
            }
            if (_ids.Count < MathF.Ceiling(_line.Count * 0.75f)) return;
            var goal = leadDistance > BoundLength * 1.5f ? lead.Position + Direction(lead.Position, objective) * BoundLength : objective;
            Issue(world, CommandType.AttackMove, _ids, Clamp(world, goal));
        }

        /// <summary>
        /// Fighting something on the ground. Shooting at an aircraft overhead does not count, or a
        /// hovering helicopter would freeze the whole advance.
        /// </summary>
        private static bool Busy(SimWorld world, Vehicle v)
        {
            if (world.TryGetVehicle(v.Engaged, out var engaged) && engaged.IsAlive && !engaged.Flying) return true;
            return v.Target.IsValid && !(world.TryGetVehicle(v.Target, out var target) && target.Flying);
        }

        /// <summary>Centre of the enemy group nearest to <paramref name="from"/>.</summary>
        private float NearestGround(Vector2 from, out Vehicle? nearest)
        {
            nearest = null;
            var best = float.MaxValue;
            foreach (var e in _enemies)
            {
                if (e.Flying) continue;
                var d = Vector2.Distance(from, e.Position);
                if (d >= best) continue;
                best = d;
                nearest = e;
            }
            return best;
        }

        private Vector2 NearestCluster(Vector2 from)
        {
            NearestGround(from, out var lead);
            if (lead == null) return from;
            var sum = Vector2.Zero;
            var count = 0;
            foreach (var e in _enemies)
            {
                if (e.Flying || Vector2.Distance(e.Position, lead.Position) > 12f) continue;
                sum += e.Position;
                count++;
            }
            return sum / Math.Max(1, count);
        }

        /// <summary>An enemy in range with at least <see cref="ClusterSize"/> vehicles around it.</summary>
        private bool TryFindCluster(Vehicle shooter, out Vehicle target)
        {
            var weapon = shooter.Def.Weapon;
            target = null!;
            var best = ClusterSize - 1;
            foreach (var e in _enemies)
            {
                if (!weapon.CanTarget(e.Flying)) continue;
                var distance = Vector2.Distance(shooter.Position, e.Position);
                if (distance < weapon.MinRange + 2f || distance > weapon.Range) continue;
                var around = 0;
                foreach (var other in _enemies)
                    if (other.Flying == e.Flying && Vector2.Distance(other.Position, e.Position) <= ClusterRadius) around++;
                if (around <= best) continue;
                best = around;
                target = e;
            }
            return target != null;
        }

        private float Nearest(Vector2 from, out Vehicle? nearest)
        {
            nearest = null;
            var best = float.MaxValue;
            foreach (var e in _enemies)
            {
                var d = Vector2.Distance(from, e.Position);
                if (d >= best) continue;
                best = d;
                nearest = e;
            }
            return best;
        }

        private void Issue(SimWorld world, CommandType type, EntityId unit, Vector2 point, EntityId target = default)
        {
            world.Submit(new Command(type, _team, new[] { unit }, point, target));
        }

        private void Issue(SimWorld world, CommandType type, List<EntityId> units, Vector2 point)
        {
            world.Submit(new Command(type, _team, units.ToArray(), point));
        }

        private static Vector2 Centre(List<Vehicle> vehicles)
        {
            var sum = Vector2.Zero;
            foreach (var v in vehicles) sum += v.Position;
            return sum / vehicles.Count;
        }

        private static Vector2 Direction(Vector2 from, Vector2 to)
        {
            var d = to - from;
            var length = d.Length();
            return length > 0.01f ? d / length : Vector2.UnitX;
        }

        private static Vector2 Clamp(SimWorld world, Vector2 p)
        {
            var limit = world.Map.HalfSize - EdgeMargin;
            return new Vector2(Math.Clamp(p.X, -limit, limit), Math.Clamp(p.Y, -limit, limit));
        }
    }
}
