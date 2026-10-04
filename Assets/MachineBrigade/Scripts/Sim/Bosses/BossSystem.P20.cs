#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Prompt 20 (DECISIONS 19E): the new bosses' mechanisms, data any boss opts into:
    /// <list type="bullet">
    /// <item>A workshop (<see cref="FactoryDef"/>, Moloch): vehicles out of its standing doors on a clock that
    /// quickens, capped apart from its escorts.</item>
    /// <item>A crusher (<see cref="CrushDef"/>, Kronos, Ixion): what is in front of its hull is crushed as it goes,
    /// walls and towers too; an HQ it reaches is flattened.</item>
    /// <item>Its own route (the open-pit mine's "haul") when the mode gives it none.</item>
    /// <item>Argus's fire direction: its side's artillery falls tighter while it and its radar live.</item>
    /// <item>The big-attack library's new shapes: the swing (<see cref="BigShape.Arc"/>), the charge
    /// (<see cref="BigShape.Charge"/>), pods that land troops (a circle's "seats"), a submarine up to launch.</item>
    /// <item>Prompt 21's Sandbox calls: a part mended, escorts off and on, a boss swapped for its main or mini
    /// version, a phase jumped on a boss without tiers.</item>
    /// </list>
    /// </summary>
    internal sealed partial class BossSystem
    {
        private readonly List<(Vehicle boss, string unit, Vector2 at, float heading)> _built = new();
        private readonly float[] _spot = { 1f, 1f, 1f, 1f, 1f, 1f, 1f, 1f };
        private readonly EntityId[] _oneRoute = new EntityId[1];

        private void JoinP20(Vehicle v)
        {
            var now = _world.Time;
            if (v.Def.Factory is { } f)
            {
                v.FactoryNext = now + f.First;
                v.FactoryStart = now;
            }
            // Its own route, from the waypoint nearest it on (a mission's route replaces it: MissionMode clears it).
            // A boss that does not move (the railway gun) is only placed by its route (Boss Rush's spawn).
            if (v.Def.RouteName != null && !v.Def.Static && _world.Map.Route(v.Def.RouteName) is { Count: > 0 } route)
            {
                var best = 0;
                for (var i = 1; i < route.Count; i++)
                    if (Vector2.DistanceSquared(route[i], v.Position) < Vector2.DistanceSquared(route[best], v.Position)) best = i;
                v.OwnRoute = route;
                v.OwnRouteAt = best;
                v.Scripted = true;
                v.RouteDriven = double.NegativeInfinity;
            }
        }

        private void StepP20(double now, float dt)
        {
            for (var t = 0; t < _spot.Length; t++) _spot[t] = 1f;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var def = v.Def;
                if (def.Factory is { } f) Factory(v, f, now);
                if (def.Crush is { } c)
                {
                    Crush(v, c, dt);
                    if (c.DebrisPhase >= 0 && v.Phase >= c.DebrisPhase && !v.CrushOff && now >= v.DebrisNext) Debris(v, c, now);
                }
                if (def.GuardRing is { } ring) Guard(v, ring, now);
                // Prompt 20 J.4: its later phase's guns (Typhon's deck gun).
                if (def.WakePhase >= 0 && v.Phase >= def.WakePhase)
                    foreach (var m in def.WakeMounts)
                        if (m < v.MountDormant.Length) v.MountDormant[m] = false;
                if (v.OwnRoute != null) FollowRoute(v, now);
                if (def.SpotAura < 1f && !v.SpotOff && v.Team is >= 0 and < 8) _spot[v.Team] = MathF.Min(_spot[v.Team], def.SpotAura);
            }
            foreach (var (boss, unit, at, heading) in _built)
            {
                var built = _world.SpawnVehicle(unit, boss.Team, at, heading);
                boss.Built.Add(built.Id);
            }
            _built.Clear();
        }

        /// <summary>
        /// Prompt 26 B.2: a close guard. Four or more of the other side's ground vehicles within the ring's reach of the hull, and
        /// the boss blasts the ground round its body (a two-layer blast, its core a few metres past the hull), then again after
        /// its interval while they stay.
        /// </summary>
        private void Guard(Vehicle v, GuardRingDef ring, double now)
        {
            if (now < v.GuardNext || v.Transforming || v.Burrowed) return;
            var near = 0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Def.Static || e.Def.Boss) continue;
                if (Vector2.Distance(e.Position, v.Position) - v.Radius - e.Radius <= ring.Radius) near++;
            }
            if (near < ring.Count)
            {
                v.GuardNext = now + 0.5;
                return;
            }
            v.GuardNext = now + ring.Every;
            _world.Damage.Queue(v.Position, ExplosionDef.TwoLayer(ring.Damage * v.DamageBoost * v.Def.DamageScale, v.Radius + ring.Pad, ExplosionTier.Huge),
                0.6, v.Team, v, HitKind.Strike, v.Id);
        }

        /// <summary>Prompt 20 I.7: how widely the side's artillery scatters now (an Argus directing it: tighter).</summary>
        public float SpotAuraFor(int team) => team is >= 0 and < 8 ? _spot[team] : 1f;

        // ================================================================== the workshop (Moloch)

        private void Factory(Vehicle v, FactoryDef f, double now)
        {
            if (now < v.FactoryNext || v.FactoryOff || v.Transforming || v.Stunned) return;
            v.FactoryNext = now + f.Every * v.PartCadence;
            v.Built.RemoveAll(id => !_world.TryGetVehicle(id, out var b) || !b.IsAlive);
            var room = f.Cap - v.Built.Count;
            var units = f.UnitsFor(v.Phase);
            if (room <= 0 || units.Count == 0) return;
            var more = (int)((now - v.FactoryStart) / f.Grow);
            var count = f.Min + (f.Max > f.Min ? _world.Random.Next(f.Max - f.Min + 1) : 0) + more;
            // Each standing door sends its share.
            count = Math.Min(room, Math.Max(1, (int)MathF.Round(count * v.FactoryShare)));
            var doors = new List<int>();
            foreach (var id in f.Doors)
            {
                var i = v.Def.PartIndex(id);
                if (i >= 0 && !v.IsPartBroken(i)) doors.Add(i);
            }
            var forward = SimMath.Forward(v.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            for (var k = 0; k < count; k++)
            {
                var from = doors.Count > 0 ? v.PartPosition(doors[k % doors.Count]) : v.Position - forward * (v.Def.Length * 0.5f);
                var row = doors.Count > 0 ? k / doors.Count : k;
                var spot = from - forward * (5f + 4f * row) + right * ((k % 2 == 0 ? -1f : 1f) * 1.5f);
                if (_world.Grid.TryNearestWalkable(_world.ClampToMap(spot), 8, out var open)) spot = open;
                var unit = _world.Economy.ForWave(v.Team, FeasibleUnit(v, units, v.FactoryBuilt + k, _world.ClampToMap(spot)));
                _built.Add((v, unit, _world.ClampToMap(spot), v.Heading + MathF.PI));
            }
            v.FactoryBuilt += count;
            _world.Emit(SimEvent.Landed(v, v.Position - forward * (v.Def.Length * 0.5f), count));
        }

        /// <summary>
        /// AI MASTER section 67 (lane P0-B): the workshop's unit for slot <paramref name="index"/>, through the same feasibility
        /// as buying: a unit that could not reach the other camp, a point or fire on an enemy from where it comes out gives
        /// way to the next of the list that can (logged REJECT ... reason=no-map-influence); none can: the list's own (the
        /// boss's data keeps its say).
        /// </summary>
        private string FeasibleUnit(Vehicle boss, IReadOnlyList<string> units, int index, Vector2 at)
        {
            var first = units[index % units.Count];
            for (var k = 0; k < units.Count; k++)
            {
                var id = units[(index + k) % units.Count];
                if (!_world.Catalog.Vehicles.TryGetValue(id, out var def) || _world.Feasibility.SpawnUseful(def, boss.Team, at, out _)) return id;
                if (k == 0)
                    _world.AiLog.Add(new MachineBrigade.Sim.AI.DecisionEntry(_world.Time, boss.Team, MachineBrigade.Sim.AI.AiLayer.Commander, boss.Id.Value,
                        MachineBrigade.Sim.AI.DecisionKind.Purchase, $"REJECT {id} reason=no-map-influence (factory spawn)"));
            }
            return first;
        }

        /// <summary>The workshop's vehicles alive now (tests, the Guide's numbers).</summary>
        public int BuiltAlive(Vehicle boss)
        {
            var n = 0;
            foreach (var id in boss.Built)
                if (_world.TryGetVehicle(id, out var b) && b.IsAlive) n++;
            return n;
        }

        // ================================================================== the crusher (Kronos, Ixion)

        private void Crush(Vehicle v, CrushDef c, float dt)
        {
            if (v.CrushOff || v.Burrowed || v.Flying || v.Transforming) return;
            if (!v.Charging && MathF.Abs(v.Speed) < c.MinSpeed) return;
            var forward = SimMath.Forward(v.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            var front = MathF.Max(v.Def.Length * 0.5f, v.Radius * 0.6f);
            var half = MathF.Max(v.Def.Width * 0.5f, v.Radius * 0.5f);
            var info = new HitInfo(v, v.Team, null, v.Position, HitKind.Strike, false).WithPen(ArmourLevels.MaxUnit, false);
            var damage = c.Dps * dt * v.DamageBoost * v.Def.DamageScale;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Flying || e.Def.Boss || e.Invulnerable || e.Def.Naval != null) continue;
                var d = e.Position - v.Position;
                var along = Vector2.Dot(d, forward);
                if (along < front - 2.5f || along > front + c.Reach + e.Radius || MathF.Abs(Vector2.Dot(d, right)) > half + e.Radius) continue;
                if (c.Hq && e.Def.Fort is { Kind: FortKind.Hq })
                {
                    // It has reached the HQ: flattened (a mission that has one to lose is lost).
                    _world.Damage.Apply(e, e.MaxHp * 50f, DamageType.Kinetic, info);
                    continue;
                }
                var mult = MathF.Max(0.1f, 1f - c.ArmourCut * e.Def.Armour.Front) * (e.Kind == TargetKind.Structure ? c.Structure : 1f);
                _world.Damage.Apply(e, damage * mult, DamageType.Kinetic, info);
            }
            foreach (var prop in _world.PropList)
            {
                if (!prop.IsAlive || prop.Invulnerable) continue;
                var d = prop.Position - v.Position;
                var along = Vector2.Dot(d, forward);
                if (along < front - 2.5f || along > front + c.Reach + prop.Radius || MathF.Abs(Vector2.Dot(d, right)) > half + prop.Radius) continue;
                _world.Damage.Apply(prop, damage * c.Structure, DamageType.Kinetic, info);
            }
        }

        /// <summary>Prompt 20 J.1: the bucket wheel spinning fast throws rock round it (three blasts, a moment's warning).</summary>
        private void Debris(Vehicle v, CrushDef c, double now)
        {
            v.DebrisNext = now + c.DebrisEvery;
            for (var k = 0; k < 3; k++)
            {
                var at = _world.ClampToMap(v.Position + RandomIn(_world.Random, c.DebrisRadius));
                _world.Damage.Queue(at, ExplosionDef.TwoLayer(c.DebrisDamage * v.DamageBoost, 4f, ExplosionTier.Large), 0.8 + 0.3 * k, v.Team, v, HitKind.Strike, v.Id);
            }
        }

        // ================================================================== its own route (Kronos)

        private void FollowRoute(Vehicle v, double now)
        {
            var route = v.OwnRoute!;
            if (v.Burrowed || v.Charging || v.Def.Naval != null) return;
            var reach = MathF.Max(6f, v.Radius * 0.8f);
            if (v.OwnRouteAt < route.Count - 1 && Vector2.Distance(v.Position, route[v.OwnRouteAt]) < reach)
            {
                v.OwnRouteAt++;
                v.RouteDriven = double.NegativeInfinity;
            }
            // Play-test 6 (DECISIONS 21G): a train at the end of its line runs it back (the Boss Hunt's trains).
            else if (v.OwnRouteAt == route.Count - 1 && route.Count > 1 && v.Def.Frame?.Move == BossMove.Rail &&
                     Vector2.Distance(v.Position, route[v.OwnRouteAt]) < reach)
            {
                var back = new List<Vector2>(route);
                back.Reverse();
                v.OwnRoute = back;
                v.OwnRouteAt = 1;
                v.RouteDriven = double.NegativeInfinity;
                route = back;
            }
            // Sent on to its waypoint now and again (a push off its line, a path lost).
            if (now - v.RouteDriven < 6.0) return;
            v.RouteDriven = now;
            _oneRoute[0] = v.Id;
            _world.Submit(new Command(CommandType.Move, v.Team, _oneRoute, _world.ClampToMap(route[v.OwnRouteAt])));
        }

        /// <summary>A mode that drives the boss on its own route (a mission's) takes over from the battlefield's.</summary>
        internal static void DropOwnRoute(Vehicle v) => v.OwnRoute = null;

        // ================================================================== the big attacks' new shapes

        /// <summary>A diving boss comes up for its launch (Typhon): only the parts carrying it can be hit until it fires.</summary>
        private void Rise(Vehicle v, float warn)
        {
            if (v.Burrow == Vehicle.BurrowState.Surface) return;
            v.Burrow = Vehicle.BurrowState.Surface;
            v.Invulnerable = false;
            v.BodyShut = true;
            v.BurrowNext = _world.Time + warn + 6.0;
            _world.Emit(SimEvent.Burrow(v, 2, v.Position));
        }

        /// <summary>The swing (Kronos's bucket wheel): everything in the arc round its front, walls and towers harder.</summary>
        private void Swing(Vehicle v, BigStrikeDef st, float scale)
        {
            var forward = SimMath.Forward(v.Heading);
            var centre = SwingCentre(v);
            var cos = MathF.Cos(st.Width * 0.5f * MathF.PI / 180f);
            var info = new HitInfo(v, v.Team, null, v.Position, HitKind.Strike, false).WithPen(st.Pen, st.Top);
            var damage = st.Damage * scale;
            var now = _world.Time;
            bool Inside(Vector2 p, float radius)
            {
                var d = p - centre;
                var length = d.Length();
                if (length - radius > st.Radius) return false;
                return length < 2f || Vector2.Dot(d / MathF.Max(0.01f, length), forward) >= cos - radius / MathF.Max(1f, length);
            }
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Flying || e.Def.Boss || e.Invulnerable || !Inside(e.Position, e.Radius)) continue;
                _world.Damage.Apply(e, damage * (e.Kind == TargetKind.Structure ? st.Structure : 1f), st.Type, info);
                if (st.Stun > 0f && e.IsAlive && !e.Def.Static)
                {
                    _world.Status.Stun(e, now + st.Stun);
                    e.ClearPath();
                    e.Speed = 0f;
                }
            }
            foreach (var prop in _world.PropList)
                if (prop.IsAlive && !prop.Invulnerable && Inside(prop.Position, prop.Radius))
                    _world.Damage.Apply(prop, damage * st.Structure, st.Type, info);
            for (var k = -2; k <= 2; k++)
            {
                var dir = SimMath.Forward(v.Heading + k * st.Width * 0.2f * MathF.PI / 180f);
                _world.Emit(SimEvent.Exploded(_world.ClampToMap(centre + dir * st.Radius * 0.7f), new ExplosionDef(0f, 6f, 0f, ExplosionTier.Huge), v.Id));
            }
        }

        /// <summary>Where a swing is measured from: the front of its hull (the bucket wheel), not its middle.</summary>
        private static Vector2 SwingCentre(Vehicle v) => v.Position + SimMath.Forward(v.Heading) * MathF.Max(0f, v.Def.Length * 0.5f - 4f);

        private Vector2 ChargeEnd(Vehicle v, Vector2 axis, float length) => _world.ClampToMap(v.Position + axis * length);

        /// <summary>The charge (Ixion's): down its warned line in its time.</summary>
        private void BeginCharge(Vehicle v, BigStrikeDef st, double now)
        {
            var axis = v.BigAttack?.Axis ?? SimMath.Forward(v.Heading);
            v.Charging = true;
            v.ChargeFrom = v.Position;
            v.ChargeTo = ChargeEnd(v, axis, st.Length);
            v.ChargeStart = now;
            v.ChargeEnd = now + st.Duration;
            v.ChargeHit.Clear();
            v.ClearPath();
            v.Speed = 0f;
            v.Heading = SimMath.HeadingOf(v.ChargeTo - v.ChargeFrom);
        }

        private void StepCharge(Vehicle v, BigStrikeDef st, float scale, double now)
        {
            // A wheel broken under way: it slews off its line and stops.
            if (Armed(v, st) == 0 || v.Stunned)
            {
                v.Charging = false;
                v.Heading += 0.6f;
                return;
            }
            var u = (float)Math.Clamp((now - v.ChargeStart) / Math.Max(0.1, v.ChargeEnd - v.ChargeStart), 0.0, 1.0);
            v.Position = _world.ClampToMap(Vector2.Lerp(v.ChargeFrom, v.ChargeTo, u));
            var info = new HitInfo(v, v.Team, null, v.Position, HitKind.Strike, false).WithPen(st.Pen, false);
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Flying || e.Def.Boss || e.Invulnerable || v.ChargeHit.Contains(e.Id)) continue;
                if (Vector2.Distance(e.Position, v.Position) > st.Width * 0.5f + e.Radius + v.Radius * 0.3f) continue;
                v.ChargeHit.Add(e.Id);
                _world.Damage.Apply(e, st.Damage * scale * (e.Kind == TargetKind.Structure ? st.Structure : 1f), st.Type, info);
                if (st.Stun > 0f && e.IsAlive && !e.Def.Static)
                {
                    _world.Status.Stun(e, now + st.Stun);
                    e.ClearPath();
                    e.Speed = 0f;
                }
            }
            if (u >= 1f) v.Charging = false;
        }

        /// <summary>A pod down (Daedalus's mass drop): its vehicles out where it landed, at most the strike's cap alive.</summary>
        private void Seat(Vehicle boss, BigAttackState s, BigStrikeDef st, Vector2 at)
        {
            var alive = 0;
            foreach (var d in s.Dropped)
                if (d.IsAlive) alive++;
            foreach (var p in _bigSpawns)
                if (p.state == s) alive++;
            var forward = SimMath.Forward(boss.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            for (var k = 0; k < st.Seats && alive < st.Max; k++, alive++)
            {
                var id = _world.Economy.ForWave(boss.Team, st.Units[s.Seated++ % st.Units.Count]);
                var spot = _world.ClampToMap(at + right * ((k - (st.Seats - 1) * 0.5f) * 4.5f) + forward * 2f);
                if (_world.Grid.TryNearestWalkable(spot, 8, out var open)) spot = open;
                _bigSpawns.Add((s, id, spot, boss.Heading, boss.Team));
            }
        }

        // ================================================================== the Sandbox's calls (prompt 21) and tests

        /// <summary>Straight into the next phase on a boss with ordinary phases (one a call; its transformation as usual).</summary>
        private void JumpPhaseP20(Vehicle v, int phase)
        {
            var phases = v.Def.Phases;
            if (phase <= v.Phase || v.Phase >= phases.Count || v.Transforming) return;
            v.Hp = MathF.Min(v.Hp, phases[v.Phase].At * v.MaxHp);
            _world.Abilities.BeginPhase(v);
        }

        /// <summary>A broken part put back whole (its guns, skills and mechanisms again).</summary>
        public bool Restore(Vehicle boss, int i)
        {
            if (!boss.HasParts || i < 0 || i >= boss.PartCount || !boss.IsPartBroken(i)) return false;
            boss.PartBroken[i] = false;
            boss.PartPatched[i] = false;
            boss.PartFrac[i] = 1f;
            Recompute(boss);
            _world.Emit(SimEvent.PartBack(boss, i, boss.PartPosition(i), boss.Def.Parts[i].Id));
            return true;
        }

        /// <summary>Its escorts sent home (off) or its arrival wave brought in again (on).</summary>
        public void SetEscorts(Vehicle boss, bool on)
        {
            if (on)
            {
                _groups.RemoveAll(g => g.Boss == boss);
                JoinEscorts(boss);
                return;
            }
            foreach (var g in _groups)
            {
                if (g.Boss != boss) continue;
                foreach (var m in g.Members)
                    if (m.Unit.IsAlive)
                    {
                        m.Unit.Hp = 0f;
                        _world.Emit(SimEvent.Retired(m.Unit));
                    }
            }
            _groups.RemoveAll(g => g.Boss == boss);
            _drops.RemoveAll(d => d.group.Boss == boss);
        }

        /// <summary>
        /// The boss swapped for its other version in place (a main boss for its mini variant, a variant for its main
        /// boss), at the same share of its health; null when it has none.
        /// </summary>
        public Vehicle? SwapRank(Vehicle boss)
        {
            var other = boss.Def.MiniVariant ?? boss.Def.VariantOf;
            if (other == null || !boss.IsAlive || !_world.Catalog.Vehicles.ContainsKey(other)) return null;
            var share = boss.Hp / MathF.Max(1f, boss.MaxHp);
            SetEscorts(boss, false);
            boss.Hp = 0f;
            _world.Emit(SimEvent.Retired(boss));
            var swapped = _world.SpawnVehicle(other, boss.Team, boss.Position, boss.Heading);
            swapped.Hp = MathF.Max(1f, swapped.MaxHp * share);
            return swapped;
        }
    }
}
