#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Prompt 8's boss mechanisms, general and data-driven (balance.json):
    /// <list type="bullet">
    /// <item>Parts (<see cref="BossPartDef"/>): each with its own health, where it sits on the model and
    /// the weapon mounts and skills it carries. Only a round that strikes the part hurts it (a blast
    /// lands on the body); a broken part's mounts and skills stop, and its penalties apply (an engine:
    /// speed; a radar: its guns' accuracy). A lock (<see cref="PartLockDef"/>) shuts the body to damage
    /// until enough parts of one kind are broken (the command airship's engines). Prompt 9 gives every
    /// boss its parts on this.</item>
    /// <item>Boring (<see cref="BurrowDef"/>): the Earth Worm dives, bores unseen and untouchable to
    /// under the enemy's biggest group of ground vehicles, cracks the ground as a warning, breaks out
    /// with a quake that stuns, and is exposed for a moment.</item>
    /// <item>Landings (<see cref="LandingDef"/>): the hovercraft stops, lowers its ramp and lands troops.</item>
    /// <item>The supergun's shot (<see cref="BombardDef"/>): one shell anywhere on the map, its landing
    /// marked seconds ahead.</item>
    /// <item>Guards (<see cref="GuardDef"/>): the emplacements a boss arrives with.</item>
    /// </list>
    /// </summary>
    internal sealed class BossSystem
    {
        private readonly SimWorld _world;
        private readonly List<(string def, int team, Vector2 at, float heading)> _spawns = new();

        public BossSystem(SimWorld world) => _world = world;

        /// <summary>A vehicle just joined the battle: its parts, timers, radio line and guards.</summary>
        public void Joined(Vehicle v)
        {
            v.InitParts();
            var now = _world.Time;
            var def = v.Def;
            if (def.Burrow is { } burrow) v.BurrowNext = now + burrow.First;
            if (def.Landing is { } landing) v.LandingNext = now + landing.First;
            if (def.Bombard is { } bombard) v.BombardNext = now + bombard.First;
            if (def.RadioSpawn != null) _world.Emit(SimEvent.RadioMessage(def.RadioSpawn, v.Team));
            foreach (var guard in def.Guards)
            {
                var forward = SimMath.Forward(v.Heading);
                var right = new Vector2(forward.Y, -forward.X);
                var at = _world.ClampToMap(v.Position + forward * guard.At.Y + right * guard.At.X);
                _world.SpawnVehicle(guard.Def, v.Team, at, v.Heading + SimMath.DegToRad(guard.Heading));
            }
        }

        public void Step(float dt)
        {
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var def = v.Def;
                if (def.Burrow != null) Bore(v, def.Burrow, now, dt);
                if (def.Landing != null) Land(v, def.Landing, now);
                if (def.Bombard != null) Bombard(v, def.Bombard, now);
            }
            foreach (var (id, team, at, heading) in _spawns) _world.SpawnVehicle(id, team, at, heading);
            _spawns.Clear();
        }

        // ================================================================== parts

        /// <summary>
        /// Which part of a boss a shooter aims at (-1: the body). While the body is locked, the parts
        /// that unlock it, nearest first; else the live part whose guns can reach the shooter (it is
        /// the one hurting it), and now and then the body. Prompt 9 adds the player's own pick.
        /// </summary>
        public int ChoosePart(Vehicle shooter, Vehicle boss, WeaponDef weapon)
        {
            if (!boss.HasParts) return -1;
            var parts = boss.Def.Parts;
            var locked = boss.BodyLocked;
            var best = -1;
            var bestScore = float.MaxValue;
            for (var i = 0; i < parts.Count; i++)
            {
                if (boss.PartBroken[i]) continue;
                var score = Vector2.Distance(boss.PartPosition(i), shooter.Position);
                if (locked && parts[i].Kind == boss.Def.PartLock!.Kind) score -= 1000f;
                else if (locked) score += 500f;
                if (!locked && Threatens(boss, parts[i], shooter)) score -= 30f;
                if (score >= bestScore) continue;
                bestScore = score;
                best = i;
            }
            if (locked || best < 0) return best;
            // The body stays the main target: about two shots in five go at it.
            return _world.Random.NextDouble() < 0.4 ? -1 : best;
        }

        /// <summary>A part carries a gun that can reach this shooter.</summary>
        private static bool Threatens(Vehicle boss, BossPartDef part, Vehicle shooter)
        {
            foreach (var m in part.Mounts)
            {
                var w = boss.Arms[m];
                if (w.Damage > 0f && w.CanTarget(shooter.Flying) && Vector2.Distance(boss.Position, shooter.Position) <= w.Range + boss.Radius) return true;
            }
            return false;
        }

        /// <summary>Takes <paramref name="damage"/> off a part (already through the damage rules); returns what it lost, and breaks it at zero.</summary>
        public float DamagePart(Vehicle boss, int i, float damage, in HitInfo hit)
        {
            if (i < 0 || i >= boss.PartHp.Length || boss.PartBroken[i] || !(damage > 0f)) return 0f;
            var lost = MathF.Min(boss.PartHp[i], damage);
            boss.PartHp[i] -= lost;
            if (boss.PartHp[i] <= 0.01f) Break(boss, i, hit);
            return lost;
        }

        /// <summary>A part breaks: its guns fall silent, its skills stop, its penalties apply, and the body takes its share.</summary>
        public void Break(Vehicle boss, int i, in HitInfo hit = default)
        {
            if (boss.PartBroken[i]) return;
            var part = boss.Def.Parts[i];
            boss.PartBroken[i] = true;
            boss.PartHp[i] = 0f;
            foreach (var m in part.Mounts)
            {
                boss.MountOff[m] = true;
                boss.Weapons[m].Target = EntityId.None;
                boss.Weapons[m].BurstLeft = 0;
            }
            for (var k = 0; k < boss.Def.Skills.Count; k++)
                foreach (var id in part.Skills)
                    if (boss.Def.Skills[k].Id == id) boss.SkillOff[k] = true;
            boss.PartSpeed *= part.Speed;
            for (var m = 0; m < boss.Def.Mounts.Count; m++)
            {
                if (part.Affects.Count > 0 && !Contains(part.Affects, m)) continue;
                boss.MountSpread[m] *= part.Spread;
                boss.MountFail[m] = MathF.Min(0.9f, boss.MountFail[m] + part.Fail);
            }
            var at = boss.PartPosition(i);
            _world.Emit(SimEvent.PartLost(boss, i, at, part.Id));
            _world.Emit(SimEvent.Exploded(at, new ExplosionDef(0f, MathF.Max(3f, part.Radius * 1.4f), 0f, ExplosionTier.Huge), boss.Id));
            // The body takes its share of the broken part (prompt 9: 30 %); none on the airship.
            if (part.BreakDamage > 0f && boss.IsAlive)
                _world.Damage.Apply(boss, boss.MaxHp * part.BreakDamage, DamageType.HighExplosive,
                    new HitInfo(hit.Attacker, hit.Team, null, at, HitKind.Redirect, false));
        }

        private static bool Contains(IReadOnlyList<int> list, int x)
        {
            foreach (var y in list)
                if (y == x) return true;
            return false;
        }

        // ================================================================== boring

        private void Bore(Vehicle v, BurrowDef b, double now, float dt)
        {
            switch (v.Burrow)
            {
                case Vehicle.BurrowState.Surface:
                    if (now < v.BurrowNext || v.Stunned || v.Transforming) return;
                    // Nothing on the ground to go under: look again in a moment.
                    if (BiggestGroup(v, out _) < 1)
                    {
                        v.BurrowNext = now + 3.0;
                        return;
                    }
                    v.Burrow = Vehicle.BurrowState.Diving;
                    v.BurrowNext = now + b.Dive;
                    v.ClearPath();
                    _world.Emit(SimEvent.Burrow(v, 0, v.Position));
                    return;
                case Vehicle.BurrowState.Diving:
                    if (now < v.BurrowNext) return;
                    v.Burrow = Vehicle.BurrowState.Under;
                    v.Invulnerable = true;
                    BiggestGroup(v, out v.BurrowGoal);
                    return;
                case Vehicle.BurrowState.Under:
                {
                    // Follows the group as it moves (checked every step: the group is cheap to find).
                    if (_world.Tick % 10 == 0 && BiggestGroup(v, out var goal) > 0) v.BurrowGoal = goal;
                    var to = v.BurrowGoal - v.Position;
                    var distance = to.Length();
                    var stepLength = b.Speed * dt;
                    if (distance > stepLength)
                    {
                        v.Position = _world.ClampToMap(v.Position + to / distance * stepLength);
                        v.Heading = SimMath.HeadingOf(to);
                        return;
                    }
                    v.Position = _world.ClampToMap(v.BurrowGoal);
                    v.Burrow = Vehicle.BurrowState.Cracking;
                    v.BurrowNext = now + b.Warn;
                    _world.Emit(SimEvent.Burrow(v, 1, v.Position, b.Warn));
                    return;
                }
                case Vehicle.BurrowState.Cracking:
                    if (now < v.BurrowNext) return;
                    v.Burrow = Vehicle.BurrowState.Surface;
                    v.Invulnerable = false;
                    v.ExposedUntil = now + b.Exposed;
                    v.BurrowNext = now + b.Surface;
                    Quake(v, b, now);
                    _world.Emit(SimEvent.Burrow(v, 2, v.Position));
                    return;
            }
        }

        /// <summary>The ground vehicles of the other side round its densest spot: how many, and where.</summary>
        private int BiggestGroup(Vehicle v, out Vector2 centre)
        {
            centre = v.Position;
            var best = 0f;
            var count = 0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Def.Static || e.Def.Boss) continue;
                var weight = 0f;
                var n = 0;
                var sum = Vector2.Zero;
                foreach (var o in _world.VehicleList)
                {
                    if (!o.IsAlive || o.Team != e.Team || o.Flying || o.Def.Static) continue;
                    if (Vector2.DistanceSquared(o.Position, e.Position) > 15f * 15f) continue;
                    weight += MathF.Max(1f, o.Def.CpCost);
                    n++;
                    sum += o.Position;
                }
                if (weight <= best) continue;
                best = weight;
                count = n;
                centre = sum / n;
            }
            return count;
        }

        /// <summary>It breaks out: a quake that hurts and stuns every enemy ground vehicle round it (not bosses).</summary>
        private void Quake(Vehicle v, BurrowDef b, double now)
        {
            var info = new HitInfo(v, v.Team, null, v.Position, HitKind.Strike, true);
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Def.Boss) continue;
                if (Vector2.Distance(e.Position, v.Position) > b.Radius + e.Def.HullRadius) continue;
                if (!e.Def.Static)
                {
                    _world.Status.Stun(e, now + b.Stun);
                    e.ClearPath();
                    e.Speed = 0f;
                }
                _world.Damage.Apply(e, b.Damage, DamageType.HighExplosive, info);
            }
            _world.Emit(SimEvent.Exploded(v.Position, new ExplosionDef(0f, b.Radius, 0f, ExplosionTier.Ultimate), v.Id));
        }

        // ================================================================== landings

        private void Land(Vehicle v, LandingDef l, double now)
        {
            if (v.Landing)
            {
                if (now < v.LandingUntil) return;
                v.Landing = false;
                v.LandingNext = now + l.Every;
                return;
            }
            if (now < v.LandingNext || v.Landings >= l.Landings || l.Units.Count == 0 || v.Stunned) return;
            v.Landing = true;
            v.LandingUntil = now + l.Stop;
            v.Landings++;
            var forward = SimMath.Forward(v.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            var ramp = _world.ClampToMap(v.Position + forward * l.Ramp.Y + right * l.Ramp.X);
            var count = l.Min + (l.Max > l.Min ? _world.Random.Next(l.Max - l.Min + 1) : 0);
            for (var k = 0; k < count; k++)
            {
                var id = l.Units[(v.Landings * 3 + k) % l.Units.Count];
                var spot = ramp + forward * (3f + 4f * (k / 2)) + right * ((k % 2 == 0 ? -1f : 1f) * 3f);
                _spawns.Add((id, v.Team, _world.ClampToMap(spot), v.Heading));
            }
            _world.Emit(SimEvent.Landed(v, ramp, count));
        }

        // ================================================================== the supergun's shot

        private void Bombard(Vehicle v, BombardDef b, double now)
        {
            if (now < v.BombardNext || v.Stunned || v.Transforming) return;
            v.BombardNext = now + b.Every;
            if (BiggestGroup(v, out var aim) < 1) return;
            // Its fire-control post gone: the shell falls much wider of the mark.
            var scatter = b.Scatter * (b.Spotter != null && !SpotterStands(v, b.Spotter) ? b.BlindScatter : 1f);
            var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
            var reach = scatter * MathF.Sqrt((float)_world.Random.NextDouble());
            var at = _world.ClampToMap(aim + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach);
            // The warning ring is as wide as the shell may fall, and the blast.
            if (b.Warning != null && _world.Catalog.TryGetSupport(b.Warning, out var warning))
                _world.Emit(SimEvent.StrikeWarning(v.Team, warning, at, at, b.Warn));
            if (b.Weapon != null && _world.Catalog.Weapons.TryGetValue(b.Weapon, out var gun))
            {
                var origin = v.Position + SimMath.Forward(v.TurretHeading) * v.Radius;
                _world.Emit(SimEvent.FiredWith(v, gun, origin, at, b.Warn, EntityId.None));
            }
            v.TurretHeading = SimMath.HeadingOf(at - v.Position);
            v.LastFiredAt = now;
            _world.Damage.Queue(at, new ExplosionDef(b.Damage, b.Radius, 0f, ExplosionTier.Ultimate), b.Warn, v.Team, v, HitKind.Strike, v.Id);
        }

        private bool SpotterStands(Vehicle v, string spotter)
        {
            foreach (var o in _world.VehicleList)
                if (o.IsAlive && o.Team == v.Team && o.Def.Id == spotter) return true;
            return false;
        }
    }
}
