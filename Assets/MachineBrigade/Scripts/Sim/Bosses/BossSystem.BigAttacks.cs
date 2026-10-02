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
    /// Prompt 18 (DECISIONS 17A): every boss's one telegraphed big attack, from its entry in balance.json
    /// "bigAttacks" (a shape template and its numbers per strike, <see cref="BigShape"/>).
    /// <list type="bullet">
    /// <item>The first about 30 s after the boss appears, then one per cooldown (start to start); the difficulty
    /// scales damage and cooldown and lengthens the warning (<see cref="BigAttackSettings"/>), the boss's own
    /// scaling on top (a mini boss).</item>
    /// <item>The warning: its zones exactly as they will land (circle, strip, line, sweep, the points of a
    /// walking barrage, a missile's landing), its parts charging (their mounts hold their fire), a radio line;
    /// the other side's ground units inside get out if they can in time and go back after (deterministic).</item>
    /// <item>Breaking a part that carries a strike during the warning cancels that strike (each part of a
    /// <see cref="BigStrikeDef.PerPart"/> strike takes its own rounds); with every part of it broken the boss
    /// has lost it until a self-repair puts one back. An EMP delays the charge where the entry says so.</item>
    /// <item>Missiles and drones fly and can be shot down: anti-air guns under them, and APS, C-RAM and
    /// point-defence lasers spend an interceptor each on one in reach.</item>
    /// </list>
    /// Only when the world has <see cref="SimWorld.BigAttackSettings"/> (the modes set them): bare test battles
    /// have none. Everything runs in vehicle-list order off the world's clock and random stream.
    /// </summary>
    internal sealed partial class BossSystem
    {
        /// <summary>A round of a big attack on its way down.</summary>
        private sealed class BigBlast
        {
            public double Due;
            public Vehicle Boss = null!;
            public BigAttackState State = null!;
            public BigStrikeDef Strike = null!;
            public Vector2 At, From;
            public float Scale;
            public int Mount = -1;
            public WeaponDef? Look;
            public bool Shot;
            public Vector2 Side;
        }

        /// <summary>A missile or drone of a big attack in flight (it can be shot down).</summary>
        private sealed class BigFlyer
        {
            public Vehicle Boss = null!;
            public BigAttackState State = null!;
            public BigStrikeDef Strike = null!;
            public Vector2 From, To;
            public double Launch, Arrive;
            public float Hp, Scale;
            public EntityId Target;
            public int Mount = -1;
            public WeaponDef? Look;
            public bool Shot;
        }

        private readonly List<BigBlast> _bigBlasts = new();
        private readonly List<BigFlyer> _bigFlyers = new();
        private readonly List<(Vector2 at, float radius, double until, float dps, Vehicle boss, Vector2 side)> _bigFires = new();
        private readonly List<(Vehicle unit, Order before, Vector2 from, Vector2 exit, double back)> _dodges = new();
        private readonly List<(BigAttackState state, string unit, Vector2 at, float heading, int team)> _bigSpawns = new();
        private readonly List<(Vehicle e, float along)> _line = new();
        private readonly List<Vehicle> _picked = new();

        /// <summary>Drones and missiles are checked against the other side's anti-air this often (ticks).</summary>
        private const int FlyerTicks = 5;

        /// <summary>
        /// Play-test 4 (DECISIONS 19R): a big attack's missile is never faster than the attack helicopter's Hellfire
        /// (24 m/s); a long way off it flies longer than its entry's "flight".
        /// </summary>
        internal const float MissileTopSpeed = 24f;

        // ================================================================== joining

        private void JoinBig(Vehicle v, BigAttackDef? instead = null)
        {
            if ((instead ?? v.Def.BigAttack) is not { } def || !v.HasParts && def.Strikes[0].Parts.Count > 0) return;
            var parts = new List<int>();
            foreach (var s in def.Strikes)
                foreach (var id in s.Parts)
                {
                    var i = v.Def.PartIndex(id);
                    if (i >= 0 && !parts.Contains(i)) parts.Add(i);
                }
            var now = _world.Time;
            v.BigAttack = new BigAttackState(def, parts) { Next = now + (def.First ?? _world.Catalog.BigAttackRules.First), LastStart = now, Now = now };
        }

        // ================================================================== the step

        private void StepBig(double now, float dt)
        {
            var settings = _world.BigAttackSettings;
            if (settings == null) return;
            foreach (var v in _world.VehicleList)
            {
                if (v.BigAttack is not { } s) continue;
                s.Now = now;
                if (!v.IsAlive || v.Escaped)
                {
                    if (s.Stage != BigStage.Ready) Finish(v, s);
                    continue;
                }
                switch (s.Stage)
                {
                    case BigStage.Ready:
                        if (now >= s.Next) TryBegin(v, s, settings, now);
                        break;
                    case BigStage.Charging:
                        Charge(v, s, settings, now);
                        break;
                    case BigStage.Firing:
                        Firing(v, s, now);
                        break;
                }
            }
            StepBlasts(now);
            StepFlyers(now);
            StepFires(now);
            StepDodges(now);
            foreach (var (state, unit, at, heading, team) in _bigSpawns) state.Dropped.Add(_world.SpawnVehicle(unit, team, at, heading));
            _bigSpawns.Clear();
        }

        private BigAttackScale ScaleOf(Vehicle v, BigAttackSettings settings) => settings.Scale.Then(v.Def.BigAttackScale);

        /// <summary>Prompt 25 C1: the boss's phase for its attack's late numbers (a tiered boss's altitude phase: Icarus's third is the crash).</summary>
        private static int AttackPhase(Vehicle v) => v.Def.Tiers != null ? v.TierPhase : v.Phase;

        /// <summary>A big attack's damage multiplier on this boss: the difficulty's and the boss's own (campaign scaling, a phase's).</summary>
        private static float DamageOf(Vehicle v, BigAttackScale scale) => scale.Damage * v.DamageBoost * v.Def.DamageScale;

        /// <summary>How many of the parts carrying a strike stand (1 for a strike the boss itself carries).</summary>
        private static int Armed(Vehicle v, BigStrikeDef s)
        {
            if (s.Parts.Count == 0) return 1;
            var n = 0;
            foreach (var id in s.Parts)
            {
                var i = v.Def.PartIndex(id);
                if (i >= 0 && !v.IsPartBroken(i)) n++;
            }
            // Prompt 20: a strike that any broken part stops (Ixion's charge on a broken wheel).
            if (s.Cut == 0f && n < s.Parts.Count) return 0;
            return n;
        }

        private static bool AnyArmed(Vehicle v, BigAttackDef def)
        {
            foreach (var s in def.Strikes)
                if (Armed(v, s) > 0) return true;
            return false;
        }

        /// <summary>A standing part carrying the strike, the <paramref name="k"/>-th in turn (-1: none).</summary>
        private static int ArmedPart(Vehicle v, BigStrikeDef s, int k)
        {
            var n = Armed(v, s);
            if (n <= 0 || s.Parts.Count == 0) return -1;
            var want = k % n;
            foreach (var id in s.Parts)
            {
                var i = v.Def.PartIndex(id);
                if (i < 0 || v.IsPartBroken(i)) continue;
                if (want-- == 0) return i;
            }
            return -1;
        }

        // ================================================================== beginning: aim, zones, warning

        private void TryBegin(Vehicle v, BigAttackState s, BigAttackSettings settings, double now)
        {
            var def = s.Def;
            var quake = def.Strikes[0].Shape == BigShape.Quake;
            if (s.Off || v.Transforming || v.Stunned || v.HoldFire || (v.Burrowed && !quake && !def.Surface) || v.Landing || v.Charging)
            {
                s.Next = now + 1.0;
                return;
            }
            // Every part that carries it broken: it has lost it until a self-repair puts one back.
            if (!AnyArmed(v, def))
            {
                s.Next = now + 2.0;
                return;
            }
            if (quake)
            {
                // The Earth Worm: its next dive is the big one (the burrow runs it; the warning comes as the ground cracks).
                if (v.Burrow != Vehicle.BurrowState.Surface || v.BurrowOff)
                {
                    s.Next = now + 1.0;
                    return;
                }
                v.BigQuake = true;
                v.BurrowNext = now;
                s.Stage = BigStage.Charging;
                s.LastStart = s.WarnStart = now;
                s.FireAt = double.PositiveInfinity;
                s.Next = now + def.CooldownIn(AttackPhase(v)) * ScaleOf(v, settings).Cooldown;
                return;
            }
            // A held mechanism's own round still in the air (the supergun's ordinary shell): wait for it to land first,
            // so the two never come down together.
            if (HeldInFlight(v, def, now))
            {
                s.Next = now + 1.0;
                return;
            }
            if (!AimAt(v, def, out var aim))
            {
                s.Next = now + 3.0;
                return;
            }
            var scale = ScaleOf(v, settings);
            var warn = MathF.Max(0.5f, def.Warn + scale.Warn);
            s.Stage = BigStage.Charging;
            s.LastStart = s.WarnStart = now;
            s.FireAt = now + warn;
            s.Next = now + MathF.Max(warn + 1f, def.CooldownIn(AttackPhase(v)) * scale.Cooldown);
            s.Aim = aim;
            s.Origin = v.Position;
            s.Forward = SimMath.Forward(v.Heading);
            var toward = aim - v.Position;
            s.Axis = toward.LengthSquared() > 0.01f ? Vector2.Normalize(toward) : SimMath.Forward(v.Heading);
            s.Blind = def.Spotter != null && v.IsPartBroken(v.Def.PartIndex(def.Spotter));
            s.WasStunned = false;
            // Prompt 20 J.4: a diving boss comes up to launch; only the parts carrying it show until it fires.
            if (def.Surface) Rise(v, warn);
            Plan(v, s, now);
            Hold(v, s, true);
            if (def.Exposed > 1f) v.BigTaken = def.Exposed;
            if (def.Halt) _world.Status.Slow(v, 0.95f, warn);
            foreach (var m in def.Hold)
                switch (m)
                {
                    case "bombard": v.BombardNext = Math.Max(v.BombardNext, s.FireAt + 1.0); break;
                    case "cruise": v.CruiseNext = Math.Max(v.CruiseNext, s.FireAt + 1.0); break;
                }
            _world.Emit(SimEvent.Big(v, def.Id, 0, s.Aim, warn));
            _world.Emit(SimEvent.RadioMessage(def.RadioKey, v.Team));
            Dodge(v, s, now);
        }

        /// <summary>A mechanism the attack holds fired a moment ago and its round has not landed yet.</summary>
        private static bool HeldInFlight(Vehicle v, BigAttackDef def, double now)
        {
            foreach (var m in def.Hold)
                switch (m)
                {
                    case "bombard" when v.Def.Bombard is { } b && v.BombardNext - b.Every * v.PartCadence > now - b.Warn - 0.5:
                    case "cruise" when v.Def.Cruise is { } c && v.CruiseNext - c.Every * v.PartCadence > now - c.Warn - 0.5:
                        return true;
                }
            return false;
        }

        /// <summary>Where it goes: the enemy's biggest group within its reach (towers count), standing still, its HQ, its base, or round the boss.</summary>
        private bool AimAt(Vehicle v, BigAttackDef def, out Vector2 aim)
        {
            aim = v.Position;
            switch (def.Aim)
            {
                case BigAim.Self:
                    // Only worth it with an enemy on the ground inside the ring.
                    return Spot(v, def.Strikes[0].Radius + 2f, false, out _) > 0;
                case BigAim.Still:
                    return Spot(v, def.Reach, true, out aim) > 0 || Spot(v, def.Reach, false, out aim) > 0;
                case BigAim.Hq:
                {
                    var n = Spot(v, def.Reach, false, out aim);
                    if (n >= 4) return true;
                    var enemy = v.Team == 0 ? 1 : 0;
                    if (_world.Bases.Of(enemy) is { HqFallen: false } camp)
                    {
                        aim = camp.HqPosition;
                        return true;
                    }
                    return n > 0;
                }
                case BigAim.Base:
                {
                    var list = BaseSpots(v, 1);
                    if (list.Count == 0) return false;
                    aim = list[0];
                    return true;
                }
                case BigAim.Prey:
                {
                    // Prompt 22 E: the first of its prey (an aircraft, else an anti-air unit) within reach; with none, the biggest group.
                    foreach (var st in def.Strikes)
                    {
                        if (st.Prey == BigPrey.None || Armed(v, st) == 0) continue;
                        var prey = Prey(v, st, def.Reach, 1);
                        if (prey.Count == 0) continue;
                        aim = prey[0].Position;
                        return true;
                    }
                    return Spot(v, def.Reach, false, out aim) > 0;
                }
                default:
                    // Prompt 28 F.3: aimed by the boss's behaviour type where it has one (the warning stays the same).
                    if (BehaviourAim(v, def, out aim)) return true;
                    return Spot(v, def.Reach, false, out aim) > 0;
            }
        }

        /// <summary>
        /// The densest spot of the other side's ground units and towers within <paramref name="reach"/> of the boss
        /// (0: anywhere; <paramref name="still"/>: only those standing still): how many, and their middle.
        /// </summary>
        private int Spot(Vehicle v, float reach, bool still, out Vector2 centre)
        {
            centre = v.Position;
            var best = 0f;
            var count = 0;
            var list = _world.VehicleList;
            foreach (var e in list)
            {
                if (!Target(v, e, still)) continue;
                if (reach > 0f && Vector2.DistanceSquared(e.Position, v.Position) > reach * reach) continue;
                var weight = 0f;
                var n = 0;
                var sum = Vector2.Zero;
                foreach (var o in list)
                {
                    if (!Target(v, o, still) || Vector2.DistanceSquared(o.Position, e.Position) > 15f * 15f) continue;
                    weight += o.Def.Static ? 4f : MathF.Max(1f, o.Def.CpCost);
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

        /// <summary>
        /// Prompt 19 F: up to <paramref name="n"/> spots for rods of <paramref name="radius"/>: the middles of the other side's
        /// densest groups within reach (0: anywhere), each unit weighing more the thicker its armour (heavy tanks first),
        /// no two rings overlapping much; with fewer groups than rods the rest go on the heaviest units not yet under a
        /// ring, then round the first spot. Deterministic (vehicle-list order, ties by id).
        /// </summary>
        private List<Vector2> RodSpots(Vehicle v, float reach, int n, float radius, Vector2 fallback)
        {
            var spots = new List<Vector2>();
            var candidates = new List<(Vector2 at, float weight, int id)>();
            var list = _world.VehicleList;
            foreach (var e in list)
            {
                if (!Target(v, e, false) || (reach > 0f && Vector2.DistanceSquared(e.Position, v.Position) > reach * reach)) continue;
                var sum = Vector2.Zero;
                var weight = 0f;
                var count = 0;
                foreach (var o in list)
                {
                    if (!Target(v, o, false) || Vector2.DistanceSquared(o.Position, e.Position) > radius * radius) continue;
                    weight += RodWeight(o);
                    sum += o.Position;
                    count++;
                }
                candidates.Add((sum / count, weight, e.Id.Value));
            }
            candidates.Sort((a, b) => a.weight != b.weight ? b.weight.CompareTo(a.weight) : a.id.CompareTo(b.id));
            var apart = radius * 1.6f;
            foreach (var c in candidates)
            {
                if (spots.Count >= n) break;
                var clear = true;
                foreach (var p in spots)
                    if (Vector2.DistanceSquared(p, c.at) < apart * apart) clear = false;
                if (clear) spots.Add(_world.ClampToMap(c.at));
            }
            // Fewer groups than rods: round the first spot, a ring's width out, evenly.
            var centre = spots.Count > 0 ? spots[0] : fallback;
            for (var k = 0; spots.Count < n && k < n * 2; k++)
            {
                var a = k * SimMath.Tau / Math.Max(1, n - 1);
                spots.Add(_world.ClampToMap(centre + new Vector2(MathF.Cos(a), MathF.Sin(a)) * radius * 1.7f));
            }
            return spots;
        }

        /// <summary>How much a rod wants a unit: the thicker its armour the more (a heavy tank before a jeep), a tower a little.</summary>
        private static float RodWeight(Vehicle o) => o.Def.Static ? 3f : (1f + o.Def.Armour.Front) * (1f + o.Def.Armour.Front) + MathF.Max(1f, o.Def.CpCost) * 0.5f;

        /// <summary>What a big attack aims at: the other side's ground units and towers (not walls, not bosses).</summary>
        private static bool Target(Vehicle v, Vehicle e, bool still) =>
            e.IsAlive && e.Team != v.Team && e.Team >= 0 && !e.Flying && !e.Invulnerable && !e.Def.Untargetable && !e.Def.Obstacle && !e.Def.Boss &&
            (!still || e.Def.Static || !e.IsMoving);

        /// <summary>
        /// Prompt 22 E: a homing strike's prey within <paramref name="reach"/> of the boss (0: anywhere), best first, at most
        /// <paramref name="max"/>: aircraft the dearest first (then the nearest); anti-air (vehicles and towers whose main
        /// weapon hits aircraft) the strongest first. A hidden stealth unit counts only once it is seen.
        /// </summary>
        internal List<Vehicle> Prey(Vehicle v, BigStrikeDef st, float reach, int max)
        {
            var list = new List<Vehicle>();
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Invulnerable || e.Def.Untargetable || e.Def.Obstacle || e.Def.Boss) continue;
                if (reach > 0f && Vector2.DistanceSquared(e.Position, v.Position) > reach * reach) continue;
                var fits = st.Prey switch
                {
                    BigPrey.Air => e.Flying,
                    BigPrey.AntiAir => !e.Flying && e.Arms.Length > 0 && e.Arms[0].CanTarget(true) && Combat.CombatSystem.IsAntiAir(e.Arms[0]),
                    _ => false,
                };
                if (fits && e.IsVisibleTo(v.Team)) list.Add(e);
            }
            list.Sort((a, b) =>
            {
                var pa = a.Def.CpCost + (a.Def.Static ? 4f : 0f);
                var pb = b.Def.CpCost + (b.Def.Static ? 4f : 0f);
                if (MathF.Abs(pa - pb) > 1e-3f) return pb.CompareTo(pa);
                var da = Vector2.DistanceSquared(a.Position, v.Position);
                var db = Vector2.DistanceSquared(b.Position, v.Position);
                return da != db ? da.CompareTo(db) : a.Id.Value.CompareTo(b.Id.Value);
            });
            if (list.Count > max) list.RemoveRange(max, list.Count - max);
            return list;
        }

        /// <summary>The other side's base for a volley: its HQ, its towers (the toughest first), then its biggest groups.</summary>
        private List<Vector2> BaseSpots(Vehicle v, int count)
        {
            var list = new List<Vector2>();
            var enemy = v.Team == 0 ? 1 : 0;
            if (_world.Bases.Of(enemy) is { HqFallen: false } camp) list.Add(camp.HqPosition);
            _picked.Clear();
            foreach (var o in _world.VehicleList)
                if (o.IsAlive && o.Team == enemy && o.Def.Static && o.Def.Fort != null && !o.Def.Obstacle) _picked.Add(o);
            _picked.Sort((a, b) => b.MaxHp != a.MaxHp ? b.MaxHp.CompareTo(a.MaxHp) : a.Id.Value.CompareTo(b.Id.Value));
            foreach (var o in _picked)
            {
                if (list.Count >= count) break;
                list.Add(o.Position);
            }
            if (list.Count < count && Spot(v, 0f, false, out var group) > 0)
                while (list.Count < count) list.Add(group);
            return list;
        }

        /// <summary>The warning's zones, exactly as each strike will land, and the points planned now (a walk, a volley).</summary>
        private void Plan(Vehicle v, BigAttackState s, double now)
        {
            var def = s.Def;
            s.ZoneList.Clear();
            s.Points.Clear();
            var fire = s.FireAt;
            var forward = s.Forward;
            foreach (var st in def.Strikes)
            {
                if (Armed(v, st) == 0) continue;
                switch (st.Shape)
                {
                    case BigShape.Circle:
                    {
                        var self = def.Aim == BigAim.Self;
                        var centre = self ? v.Position : s.Aim;
                        if (st.Rings && !self && st.Area > 0f)
                        {
                            // Prompt 25 C1: every round's landing rolled now and drawn as its own ring (the Behemoth's six).
                            var n = RoundsOf(v, st);
                            for (var k = 0; k < n; k++)
                            {
                                var at = _world.ClampToMap(centre + RandomIn(_world.Random, st.Area));
                                var due = fire + CircleDelay(st, n, k);
                                s.Points.Add((at, due));
                                s.ZoneList.Add(new BigZone(at, st.Radius, due, true));
                            }
                            break;
                        }
                        var radius = st.Area > 0f ? st.Area : st.Radius + (s.Blind ? def.BlindScatter : st.Scatter);
                        s.ZoneList.Add(new BigZone(centre, radius, fire, true, st.Area > 0f ? st.Radius : 0f));
                        break;
                    }
                    case BigShape.Strip:
                    {
                        var axis = AxisOf(st.Axis, forward, s.Axis);
                        s.ZoneList.Add(new BigZone(s.Aim, axis, st.Length * 0.5f, st.Width * 0.5f, fire, true, st.Radius));
                        // A walking barrage: each point with its own countdown.
                        if (st.Interval > 0f)
                        {
                            var n = RoundsOf(v, st);
                            for (var k = 0; k < n; k++)
                            {
                                var at = _world.ClampToMap(s.Aim + axis * (-st.Length * 0.5f + st.Length * (k + 0.5f) / n));
                                s.ZoneList.Add(new BigZone(at, st.Radius, fire + k * st.Interval, true));
                            }
                        }
                        break;
                    }
                    case BigShape.Line:
                        s.ZoneList.Add(new BigZone(s.Origin + s.Axis * st.Length * 0.5f, s.Axis, st.Length * 0.5f, st.Width * 0.5f, fire, true, 1f));
                        break;
                    case BigShape.Sweep:
                    {
                        var axis = AxisOf(st.Axis, forward, s.Axis);
                        s.ZoneList.Add(new BigZone(s.Aim, axis, st.Length * 0.5f, st.Width * 0.5f, fire, true, 1f));
                        break;
                    }
                    case BigShape.Swarm:
                        s.ZoneList.Add(new BigZone(s.Aim, MathF.Max(8f, st.Area), fire, false));
                        break;
                    case BigShape.Missile:
                    {
                        var n = RoundsOf(v, st);
                        var spots = def.Aim == BigAim.Base ? BaseSpots(v, Math.Min(n, st.Targets)) : new List<Vector2> { s.Aim };
                        if (spots.Count == 0) spots.Add(s.Aim);
                        for (var k = 0; k < n; k++)
                        {
                            var at = spots[k % spots.Count];
                            var due = fire + 0.35 * k + MathF.Max(st.Flight, Vector2.Distance(v.Position, at) / MissileTopSpeed);
                            s.Points.Add((at, due));
                            // One ring a target (the second missile at the same spot shares it).
                            if (k < spots.Count) s.ZoneList.Add(new BigZone(at, st.Radius, due, true));
                        }
                        break;
                    }
                    case BigShape.Drop:
                        s.ZoneList.Add(new BigZone(Offset(v, st.At), 8f, fire, false));
                        break;
                    case BigShape.Rods:
                    {
                        // Prompt 19 F: one rod on each group, each its own ring and moment (a fifth of a second apart).
                        var spots = RodSpots(v, def.Reach, RoundsOf(v, st), st.Radius, s.Aim);
                        // From the craft itself while it is still in orbit, else from the satellite it left there (since play-test 6
                        // it comes down within the first second, so they all fall from the satellite).
                        s.FromSatellite = v.HasSatellite;
                        s.Origin = v.HasSatellite ? v.SatelliteAt : v.Position;
                        for (var k = 0; k < spots.Count; k++)
                        {
                            var due = fire + 0.2 * k;
                            s.Points.Add((spots[k], due));
                            s.ZoneList.Add(new BigZone(spots[k], st.Radius, due, true));
                        }
                        break;
                    }
                    case BigShape.Buff:
                        s.ZoneList.Add(new BigZone(v.Position, st.Reach, fire, false));
                        break;
                    case BigShape.Arc:
                    {
                        // Three rings across the swing (the view draws rings and strips only).
                        var half = st.Width * 0.5f * MathF.PI / 180f;
                        for (var k = -1; k <= 1; k++)
                        {
                            var dir = SimMath.Forward(v.Heading + k * half * 0.66f);
                            s.ZoneList.Add(new BigZone(_world.ClampToMap(SwingCentre(v) + dir * st.Radius * 0.55f), st.Radius * 0.5f, fire, true));
                        }
                        break;
                    }
                    case BigShape.Charge:
                    {
                        var to = ChargeEnd(v, s.Axis, st.Length);
                        var mid = (v.Position + to) * 0.5f;
                        s.ZoneList.Add(new BigZone(mid, s.Axis, Vector2.Distance(v.Position, to) * 0.5f, st.Width * 0.5f, fire, true, 1f));
                        break;
                    }
                }
            }
        }

        private static Vector2 AxisOf(BigAxis axis, Vector2 forward, Vector2 toward) => axis switch
        {
            BigAxis.Heading => forward,
            BigAxis.Across => new Vector2(toward.Y, -toward.X),
            _ => toward,
        };

        /// <summary>How many rounds a strike fires with the parts standing now.</summary>
        private static int RoundsOf(Vehicle v, BigStrikeDef st)
        {
            var armed = Armed(v, st);
            if (armed <= 0) return 0;
            int n;
            if (st.PerPart > 0) n = st.PerPart * armed;
            else if (st.Every > 0f) n = st.FullCount;
            else n = v.BigAttack is { } state ? state.Def.CountIn(st, AttackPhase(v)) : st.Count;
            // Prompt 20: a part carrying it broken cuts it to its share (Daedalus: six pods fall as three).
            if (st.Cut > 0f && st.PerPart <= 0 && armed < st.Parts.Count) n = Math.Max(1, (int)MathF.Round(n * st.Cut));
            return n;
        }

        /// <summary>Its mounts hold their fire while it charges and fires (A.2), and fire again after.</summary>
        private static void Hold(Vehicle v, BigAttackState s, bool on)
        {
            if (v.MountHeld.Length == 0) return;
            foreach (var i in s.Parts)
                foreach (var m in v.Def.Parts[i].Mounts)
                    if (m < v.MountHeld.Length) v.MountHeld[m] = on;
        }

        // ================================================================== the warning

        private void Charge(Vehicle v, BigAttackState s, BigAttackSettings settings, double now)
        {
            var def = s.Def;
            // The quake waits for the dive; the burrow calls it once the ground cracks (QuakeWarned, BigQuakeHits).
            if (double.IsPositiveInfinity(s.FireAt))
            {
                if (v.BurrowOff && v.Burrow == Vehicle.BurrowState.Surface)
                {
                    v.BigQuake = false;
                    Cancel(v, s);
                }
                return;
            }
            if (def.Strikes[0].Shape == BigShape.Quake) return;
            // Every part carrying it broken in time: cancelled.
            if (!AnyArmed(v, def))
            {
                Cancel(v, s);
                return;
            }
            // An EMP on the boss slows its charge (the entries that say so).
            if (def.EmpDelay > 0f && v.Stunned && !s.WasStunned)
            {
                s.FireAt += def.EmpDelay;
                for (var i = 0; i < s.ZoneList.Count; i++) s.ZoneList[i] = s.ZoneList[i].Later(def.EmpDelay);
                for (var i = 0; i < s.Points.Count; i++) s.Points[i] = (s.Points[i].at, s.Points[i].due + def.EmpDelay);
                _world.Emit(SimEvent.Big(v, def.Id, 4, s.Aim, def.EmpDelay));
            }
            s.WasStunned = v.Stunned;
            if (now >= s.FireAt) Fire(v, s, settings, now);
        }

        private void Cancel(Vehicle v, BigAttackState s)
        {
            v.BodyShut = false;
            _world.Emit(SimEvent.Big(v, s.Def.Id, 2, s.Aim, 0f));
            Finish(v, s);
        }

        private void Finish(Vehicle v, BigAttackState s)
        {
            s.Stage = BigStage.Ready;
            s.ZoneList.Clear();
            s.Points.Clear();
            s.BuffUntil = 0;
            Hold(v, s, false);
            v.BigTaken = 1f;
            // Its dodgers go back now.
            for (var i = 0; i < _dodges.Count; i++)
                if (_dodges[i].back > s.Now + 0.5) _dodges[i] = (_dodges[i].unit, _dodges[i].before, _dodges[i].from, _dodges[i].exit, Math.Min(_dodges[i].back, s.Now + 1.0));
        }

        // ================================================================== firing

        private void Fire(Vehicle v, BigAttackState s, BigAttackSettings settings, double now)
        {
            var def = s.Def;
            var scale = DamageOf(v, ScaleOf(v, settings));
            s.ChargeScale = scale;
            s.Stage = BigStage.Firing;
            s.Rounds = 0;
            s.ShotDown = 0;
            s.HpAtFire = v.Hp;
            s.EndsAt = now;
            var forward = s.Forward;
            var rng = _world.Random;
            foreach (var st in def.Strikes)
            {
                var n = RoundsOf(v, st);
                if (n <= 0) continue;
                switch (st.Shape)
                {
                    case BigShape.Circle when def.Aim == BigAim.Self:
                        SelfBlast(v, s, st, scale, now);
                        break;
                    case BigShape.Circle when st.Rings && st.Area > 0f && s.Points.Count > 0:
                        // Prompt 25 C1: the rings drawn at the warning are where the rounds land.
                        for (var k = 0; k < n && k < s.Points.Count; k++) Round(v, s, st, s.Points[k].at, now + CircleDelay(st, n, k), scale, k);
                        break;
                    case BigShape.Circle:
                    {
                        var salvo = Math.Max(1, st.Salvo);
                        var volleys = (n + salvo - 1) / salvo;
                        var gap = st.Every > 0f ? st.Every : volleys > 1 ? st.Duration / (volleys - 1) : 0f;
                        for (var k = 0; k < n; k++)
                        {
                            var at = s.Aim;
                            if (st.Area > 0f) at += RandomIn(rng, st.Area);
                            else
                            {
                                var scatter = s.Blind ? def.BlindScatter : st.Scatter;
                                if (scatter > 0f) at += RandomIn(rng, scatter);
                            }
                            Round(v, s, st, _world.ClampToMap(at), now + (k / salvo) * gap + 0.08 * (k % salvo), scale, k);
                        }
                        break;
                    }
                    case BigShape.Strip:
                    {
                        var axis = AxisOf(st.Axis, forward, s.Axis);
                        var across = new Vector2(axis.Y, -axis.X);
                        for (var k = 0; k < n; k++)
                        {
                            var along = -st.Length * 0.5f + st.Length * (k + 0.5f) / n;
                            var lateral = st.Width > 0f && st.Interval <= 0f ? ((float)rng.NextDouble() - 0.5f) * st.Width * 0.7f : 0f;
                            var due = st.Interval > 0f ? now + k * st.Interval : now + (n > 1 ? st.Duration * k / (n - 1) : 0f);
                            Round(v, s, st, _world.ClampToMap(s.Aim + axis * along + across * lateral), due, scale, k);
                        }
                        if (st.Pass != null && _world.Catalog.TryGetSupport(st.Pass, out var pass))
                            _world.Emit(SimEvent.AircraftPass(v.Team, pass, s.Aim - axis * st.Length * 0.5f, s.Aim + axis * st.Length * 0.5f, MathF.Max(0.5f, st.Duration)));
                        break;
                    }
                    case BigShape.Line:
                        Pierce(v, s, st, scale);
                        break;
                    case BigShape.Sweep:
                        s.SweepDone = 0f;
                        s.Swept.Clear();
                        s.EndsAt = Math.Max(s.EndsAt, now + st.Duration);
                        break;
                    case BigShape.Swarm:
                        Swarm(v, s, st, n, scale, now);
                        break;
                    case BigShape.Missile:
                        for (var k = 0; k < n && k < s.Points.Count; k++)
                        {
                            var (at, due) = s.Points[k];
                            var part = ArmedPart(v, st, k);
                            var from = part >= 0 ? v.PartPosition(part) : v.Position;
                            var launch = now + 0.35 * k;
                            Launch(v, s, st, from, at, launch, Math.Max(launch + 0.5, due), scale, EntityId.None, part);
                        }
                        break;
                    case BigShape.Drop:
                        Drop(v, s, st, n);
                        break;
                    case BigShape.Rods:
                        for (var k = 0; k < s.Points.Count; k++) Round(v, s, st, s.Points[k].at, s.Points[k].due, scale, k);
                        break;
                    case BigShape.Buff:
                        s.BuffUntil = now + st.Seconds;
                        s.EndsAt = Math.Max(s.EndsAt, s.BuffUntil);
                        break;
                    case BigShape.Arc:
                        Swing(v, st, scale);
                        break;
                    case BigShape.Charge:
                        BeginCharge(v, st, now);
                        s.EndsAt = Math.Max(s.EndsAt, v.ChargeEnd);
                        break;
                }
            }
            // Prompt 20 J.4: launched; it may go down again.
            if (def.Surface) v.BodyShut = false;
            _world.Emit(SimEvent.Big(v, def.Id, 1, s.Aim, 0f));
        }

        /// <summary>When a circle's k-th round of n lands after it fires: its salvos spread over the duration (or every "every" s).</summary>
        private static double CircleDelay(BigStrikeDef st, int n, int k)
        {
            var salvo = Math.Max(1, st.Salvo);
            var volleys = (n + salvo - 1) / salvo;
            var gap = st.Every > 0f ? st.Every : volleys > 1 ? st.Duration / (volleys - 1) : 0f;
            return (k / salvo) * gap + 0.08 * (k % salvo);
        }

        private static Vector2 RandomIn(Random rng, float radius)
        {
            var angle = (float)rng.NextDouble() * SimMath.Tau;
            var r = radius * MathF.Sqrt((float)rng.NextDouble());
            return new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r;
        }

        /// <summary>A round on its way to <paramref name="at"/>, landing at <paramref name="due"/>: fired from the k-th standing part.</summary>
        private void Round(Vehicle v, BigAttackState s, BigStrikeDef st, Vector2 at, double due, float scale, int k)
        {
            var part = ArmedPart(v, st, k);
            var blast = new BigBlast
            {
                Due = due, Boss = v, State = s, Strike = st, At = at, Scale = scale, From = part >= 0 ? v.PartPosition(part) : v.Position,
                Mount = part >= 0 && v.Def.Parts[part].Mounts.Count > 0 ? v.Def.Parts[part].Mounts[0] : -1, Look = LookOf(st),
            };
            _bigBlasts.Add(blast);
            s.Rounds++;
            s.EndsAt = Math.Max(s.EndsAt, due);
        }

        private WeaponDef? LookOf(BigStrikeDef st) =>
            st.Weapon != null && _world.Catalog.Weapons.TryGetValue(st.Weapon, out var w) ? w : null;

        private void StepBlasts(double now)
        {
            for (var i = 0; i < _bigBlasts.Count; i++)
            {
                var b = _bigBlasts[i];
                // Its gun fires a moment before it lands (the view's round and flash).
                if (!b.Shot && now >= b.Due - 0.9)
                {
                    b.Shot = true;
                    if (b.Boss.IsAlive) Shoot(b.Boss, b.Mount, b.Look, b.From, b.At, (float)Math.Max(0.05, b.Due - now), EntityId.None);
                }
                if (now < b.Due) continue;
                _bigBlasts.RemoveAt(i--);
                BlastAt(b.Boss, b.Strike, b.At, b.Scale, b.Side);
                // Prompt 20 E.3: a pod lands its vehicles where it came down.
                if (b.Strike.Seats > 0 && b.Boss.IsAlive) Seat(b.Boss, b.State, b.Strike, b.At);
                if (b.Strike.Fire is { } fire) Burn(b.Boss, b.At, fire, b.Side, now);
            }
        }

        private void Shoot(Vehicle v, int mount, WeaponDef? look, Vector2 from, Vector2 to, float seconds, EntityId target)
        {
            if (look != null) _world.Emit(SimEvent.FiredWith(v, look, from, to, seconds, target));
            else if (mount >= 0 && mount < v.Def.Mounts.Count) _world.Emit(SimEvent.Fired(v, mount, from, to, seconds, target));
        }

        /// <summary>
        /// A blast of a big attack: every ground unit and building of the other sides within its radius, the damage
        /// falling to <see cref="BigStrikeDef.Falloff"/> at the rim; structures by the strike's multiplier; a quake
        /// stuns. Only one half when <paramref name="side"/> is set (a flamer's half of the ring).
        /// </summary>
        private void BlastAt(Vehicle boss, BigStrikeDef s, Vector2 at, float scale, Vector2 side = default)
        {
            var damage = s.Damage * scale;
            var now = _world.Time;
            // Prompt 19 F: a rod is a kinetic penetrator, not a blast's fragments: its own penetration on the roof.
            var info = s.Shape == BigShape.Rods
                ? new HitInfo(boss, boss.Team, null, at, HitKind.Direct, true).WithPen(s.Pen, true)
                : new HitInfo(boss, boss.Team, null, at, HitKind.Strike, true).At(at).WithPen(s.Pen, true, s.Thermo);
            var half = side.LengthSquared() > 0.01f;
            // Prompt 26 B.3: two flat layers: the core (s.Radius) at full damage, the edge (twice as wide) at its share.
            var outer = s.EdgeRadius;
            var reach = outer > s.Radius ? outer : s.Radius;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == boss.Team || e.Flying || e.Invulnerable) continue;
                var edge = MathF.Max(0f, Vector2.Distance(e.Position, at) - e.Radius);
                if (edge > reach || (half && Vector2.Dot(e.Position - at, side) < 0f)) continue;
                var share = outer > s.Radius ? edge <= s.Radius ? 1f : s.EdgeShare : 1f - (1f - s.Falloff) * Math.Clamp(edge / s.Radius, 0f, 1f);
                var mult = e.Kind == TargetKind.Structure ? s.Structure : 1f;
                if (damage > 0f) _world.Damage.Apply(e, damage * share * mult, s.Type, info);
                if (s.Stun > 0f && e.IsAlive && !e.Def.Static && !e.Def.Boss)
                {
                    _world.Status.Stun(e, now + s.Stun);
                    e.ClearPath();
                    e.Speed = 0f;
                }
            }
            if (damage > 0f)
                foreach (var prop in _world.PropList)
                {
                    if (!prop.IsAlive || prop.Invulnerable) continue;
                    var edge = MathF.Max(0f, Vector2.Distance(prop.Position, at) - prop.Radius);
                    if (edge > reach || (half && Vector2.Dot(prop.Position - at, side) < 0f)) continue;
                    var share = outer > s.Radius ? edge <= s.Radius ? 1f : s.EdgeShare : 1f - (1f - s.Falloff) * Math.Clamp(edge / s.Radius, 0f, 1f);
                    _world.Damage.Apply(prop, damage * share * (prop.Kind == TargetKind.Structure ? s.Structure : 1f), s.Type, info);
                }
            var tier = damage >= 800f ? ExplosionTier.Ultimate : damage >= 200f ? ExplosionTier.Huge : damage >= 50f ? ExplosionTier.Large : ExplosionTier.Medium;
            _world.Emit(SimEvent.Exploded(at, new ExplosionDef(0f, s.Radius, 0f, tier) { Edge = outer }, boss.Id));
        }

        /// <summary>Round the boss (the Inferno's ring): all round with every part standing, else each standing part's half.</summary>
        private void SelfBlast(Vehicle v, BigAttackState s, BigStrikeDef st, float scale, double now)
        {
            var centre = s.ZoneList.Count > 0 ? s.ZoneList[0].Centre : v.Position;
            var armed = Armed(v, st);
            if (!st.Sectors || armed >= st.Parts.Count)
            {
                BlastAt(v, st, centre, scale);
                if (st.Fire is { } fire) Burn(v, centre, fire, default, now);
                return;
            }
            var forward = SimMath.Forward(v.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            foreach (var id in st.Parts)
            {
                var i = v.Def.PartIndex(id);
                if (i < 0 || v.IsPartBroken(i)) continue;
                var side = right * (v.Def.Parts[i].At.X >= 0f ? 1f : -1f);
                BlastAt(v, st, centre, scale, side);
                if (st.Fire is { } fire) Burn(v, centre, fire, side, now);
            }
        }

        /// <summary>The Tempest's slug: through every ground unit on its line, each one after the first taking a share less.</summary>
        private void Pierce(Vehicle v, BigAttackState s, BigStrikeDef st, float scale)
        {
            _line.Clear();
            var across = new Vector2(s.Axis.Y, -s.Axis.X);
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Flying || e.Invulnerable) continue;
                var d = e.Position - s.Origin;
                var along = Vector2.Dot(d, s.Axis);
                if (along < 0f || along > st.Length + e.Radius || MathF.Abs(Vector2.Dot(d, across)) > st.Width * 0.5f + e.Radius) continue;
                _line.Add((e, along));
            }
            _line.Sort((a, b) => a.along != b.along ? a.along.CompareTo(b.along) : a.e.Id.Value.CompareTo(b.e.Id.Value));
            var damage = st.Damage * scale;
            var info = new HitInfo(v, v.Team, null, s.Origin, HitKind.Pierce, false).WithPen(st.Pen, st.Top);
            foreach (var (e, _) in _line)
            {
                _world.Damage.Apply(e, damage, st.Type, info);
                damage *= 1f - st.ChainCut;
            }
            var part = ArmedPart(v, st, 0);
            var mount = part >= 0 && v.Def.Parts[part].Mounts.Count > 0 ? v.Def.Parts[part].Mounts[0] : -1;
            Shoot(v, mount, LookOf(st), part >= 0 ? v.PartPosition(part) : v.Position, s.Origin + s.Axis * st.Length, 0.12f, EntityId.None);
        }

        /// <summary>While it fires: the sweep runs, the boost holds, a boss hurt enough breaks off; done once all has landed.</summary>
        private void Firing(Vehicle v, BigAttackState s, double now)
        {
            var def = s.Def;
            if (def.AbortDamage > 0f && s.HpAtFire - v.Hp >= def.AbortDamage * v.MaxHp)
            {
                for (var i = _bigBlasts.Count - 1; i >= 0; i--)
                    if (_bigBlasts[i].State == s) _bigBlasts.RemoveAt(i);
                _world.Emit(SimEvent.Big(v, def.Id, 3, s.Aim, 0f));
                Finish(v, s);
                return;
            }
            foreach (var st in def.Strikes)
            {
                if (st.Shape == BigShape.Sweep && s.SweepDone >= 0f && s.SweepDone < 1f) Sweep(v, s, st, now);
                if (st.Shape == BigShape.Charge && v.Charging) StepCharge(v, st, s.ChargeScale, now);
                if (st.Shape == BigShape.Buff && now < s.BuffUntil)
                {
                    // The antenna broken: the boost goes with it.
                    if (Armed(v, st) == 0) s.BuffUntil = now;
                    else Boost(v, st);
                }
            }
            if (now < s.EndsAt || (s.SweepDone >= 0f && s.SweepDone < 1f) || v.Charging) return;
            foreach (var b in _bigBlasts)
                if (b.State == s) return;
            foreach (var f in _bigFlyers)
                if (f.State == s) return;
            Finish(v, s);
        }

        /// <summary>The beam's spot moves on down its line: everything it crosses is hit once.</summary>
        private void Sweep(Vehicle v, BigAttackState s, BigStrikeDef st, double now)
        {
            if (Armed(v, st) == 0)
            {
                s.SweepDone = 1f;
                return;
            }
            var zone = s.ZoneList.Count > 0 ? s.ZoneList[0] : new BigZone(s.Aim, s.Axis, st.Length * 0.5f, st.Width * 0.5f, now, true);
            var t = (float)Math.Clamp((now - s.FireAt) / Math.Max(0.1, st.Duration), 0.0, 1.0);
            Vector2 At(float u) => zone.Centre + zone.Axis * (-zone.HalfLength + 2f * zone.HalfLength * u);
            var from = At(s.SweepDone);
            var to = At(t);
            var damage = st.Damage * DamageOf(v, ScaleOf(v, _world.BigAttackSettings!));
            var info = new HitInfo(v, v.Team, null, v.Position, HitKind.Pierce, false).WithPen(st.Pen, st.Top);
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Flying || e.Invulnerable || s.Swept.Contains(e.Id)) continue;
                if (SegmentDistance(e.Position, from, to) > st.Width * 0.5f + e.Radius) continue;
                s.Swept.Add(e.Id);
                _world.Damage.Apply(e, damage, st.Type, info);
            }
            s.SweepDone = t >= 1f ? 1f : t;
            // The beam, from its emitter to the spot (every other step).
            if (_world.Tick % 2 == 0)
            {
                var part = ArmedPart(v, st, 0);
                var mount = part >= 0 && v.Def.Parts[part].Mounts.Count > 0 ? v.Def.Parts[part].Mounts[0] : -1;
                Shoot(v, mount, LookOf(st), part >= 0 ? v.PartPosition(part) : v.Position, to, 0f, EntityId.None);
            }
        }

        private static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var len = ab.LengthSquared();
            var t = len > 1e-4f ? Math.Clamp(Vector2.Dot(p - a, ab) / len, 0f, 1f) : 0f;
            return Vector2.Distance(p, a + ab * t);
        }

        /// <summary>The Supreme Commander's offensive: its side within reach hits harder and fires faster while it lasts.</summary>
        private void Boost(Vehicle v, BigStrikeDef st)
        {
            var reach = st.Reach * st.Reach;
            foreach (var o in _world.VehicleList)
            {
                if (!o.IsAlive || o.Team != v.Team || o.Def.Boss || Vector2.DistanceSquared(o.Position, v.Position) > reach) continue;
                o.CommandDamage = MathF.Max(o.CommandDamage, 1f + st.Damage);
                o.CommandFire = MathF.Max(o.CommandFire, 1f + st.FireRate);
            }
        }

        /// <summary>A landing party off the ramp: as many as keep this attack's vehicles alive at its most.</summary>
        private void Drop(Vehicle v, BigAttackState s, BigStrikeDef st, int n)
        {
            var alive = 0;
            foreach (var d in s.Dropped)
                if (d.IsAlive) alive++;
            var room = Math.Min(n > 1 ? n : st.Units.Count, st.Max - alive);
            if (room <= 0) return;
            var forward = SimMath.Forward(v.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            var ramp = _world.ClampToMap(Offset(v, st.At));
            for (var k = 0; k < room; k++)
            {
                var id = _world.Economy.ForWave(v.Team, st.Units[k % st.Units.Count]);
                var spot = ramp + forward * (3f + 4f * (k / 2)) + right * ((k % 2 == 0 ? -1f : 1f) * 3f);
                _bigSpawns.Add((s, id, _world.ClampToMap(spot), v.Heading, v.Team));
            }
            _world.Emit(SimEvent.Landed(v, ramp, room));
        }

        // ================================================================== drones and missiles in flight

        private void Swarm(Vehicle v, BigAttackState s, BigStrikeDef st, int n, float scale, double now)
        {
            // Its targets: the heaviest armour in the group first (it strikes the roof), at most so many; a strike with
            // prey (prompt 22 E) takes its prey within the attack's reach, and the group round the aim only with none.
            _picked.Clear();
            var area = MathF.Max(8f, st.Area);
            if (st.Prey != BigPrey.None) _picked.AddRange(Prey(v, st, s.Def.Reach, st.Targets));
            if (_picked.Count == 0)
            {
                foreach (var e in _world.VehicleList)
                    if (Target(v, e, false) && Vector2.DistanceSquared(e.Position, s.Aim) <= area * area) _picked.Add(e);
                _picked.Sort((a, b) =>
                {
                    var pa = a.Def.Armour.Front * 100 + a.Def.CpCost;
                    var pb = b.Def.Armour.Front * 100 + b.Def.CpCost;
                    return pa != pb ? pb.CompareTo(pa) : a.Id.Value.CompareTo(b.Id.Value);
                });
            }
            var targets = Math.Min(_picked.Count, st.Targets);
            for (var k = 0; k < n; k++)
            {
                var part = ArmedPart(v, st, k);
                var from = part >= 0 ? v.PartPosition(part) : v.Position;
                var target = targets > 0 ? _picked[k % targets] : null;
                var to = target?.Position ?? _world.ClampToMap(s.Aim + RandomIn(_world.Random, area));
                var launch = now + 0.12 * k;
                Launch(v, s, st, from, to, launch, launch + Vector2.Distance(from, to) / st.Speed, scale, target?.Id ?? EntityId.None, part);
            }
        }

        private void Launch(Vehicle v, BigAttackState s, BigStrikeDef st, Vector2 from, Vector2 to, double launch, double arrive, float scale, EntityId target, int part)
        {
            _bigFlyers.Add(new BigFlyer
            {
                Boss = v, State = s, Strike = st, From = from, To = to, Launch = launch, Arrive = arrive, Hp = MathF.Max(1f, st.Hp), Scale = scale,
                Target = target, Mount = part >= 0 && v.Def.Parts[part].Mounts.Count > 0 ? v.Def.Parts[part].Mounts[0] : -1, Look = LookOf(st),
            });
            s.Rounds++;
            s.EndsAt = Math.Max(s.EndsAt, arrive);
        }

        private void StepFlyers(double now)
        {
            if (_bigFlyers.Count == 0) return;
            var check = _world.Tick % FlyerTicks == 0;
            for (var i = 0; i < _bigFlyers.Count; i++)
            {
                var f = _bigFlyers[i];
                if (now < f.Launch) continue;
                // A drone homes on its target.
                if (f.Target.IsValid && _world.TryGetVehicle(f.Target, out var aimed) && aimed.IsAlive) f.To = aimed.Position;
                if (!f.Shot)
                {
                    f.Shot = true;
                    if (f.Boss.IsAlive) Shoot(f.Boss, f.Mount, f.Look, f.From, f.To, (float)Math.Max(0.1, f.Arrive - now), f.Target);
                }
                if (now >= f.Arrive)
                {
                    _bigFlyers.RemoveAt(i--);
                    Arrived(f, now);
                    continue;
                }
                if (!check) continue;
                var t = (float)Math.Clamp((now - f.Launch) / Math.Max(0.1, f.Arrive - f.Launch), 0.0, 1.0);
                var at = Vector2.Lerp(f.From, f.To, t);
                if (!Intercepted(f, at)) continue;
                _bigFlyers.RemoveAt(i--);
                f.State.ShotDown++;
                _world.Emit(SimEvent.Big(f.Boss, f.State.Def.Id, 5, at, 0f));
            }
        }

        /// <summary>
        /// The other side's air defence under a missile or drone: each anti-air gun in reach hits it for a share of its
        /// damage a second; an APS, a C-RAM or a point-defence laser in reach spends an interceptor on it. True: down.
        /// </summary>
        private bool Intercepted(BigFlyer f, Vector2 at)
        {
            var rules = _world.Catalog.BigAttackRules;
            var table = _world.Catalog.Damage;
            var seconds = FlyerTicks * 0.05f;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == f.Boss.Team || e.Team < 0 || e.Stunned) continue;
                var d2 = Vector2.DistanceSquared(e.Position, at);
                if (d2 > 90f * 90f) continue;
                if (e.Aps is { } aps && !e.ApsOff && e.ApsCharges > 0 && d2 <= aps.Radius * aps.Radius &&
                    !(aps.Laser && (_world.Strikes.InSmoke(e.Position) || _world.Strikes.InSmoke(at))))
                {
                    e.ApsCharges--;
                    e.ApsLeft = !e.ApsLeft;
                    f.Hp -= rules.Intercept;
                    var look = f.Look ?? (f.Mount >= 0 ? f.Boss.Def.Mounts[f.Mount].Weapon : e.Def.Weapon);
                    _world.Emit(SimEvent.Intercept(e, look, at, e.ApsLeft));
                    if (f.Hp <= 0f) return true;
                }
                for (var m = 0; m < e.Arms.Length; m++)
                {
                    var w = e.Arms[m];
                    if (w.Damage <= 0f || !w.CanTarget(true) || !e.MountWorks(m) || d2 > w.Range * w.Range) continue;
                    f.Hp -= Firepower(w) * table.TypeOf(w, TargetKind.Air) * rules.AaHit * seconds;
                }
                if (f.Hp <= 0f) return true;
            }
            return false;
        }

        /// <summary>A drone strikes its target's roof (a jammer may throw it off); a missile blasts where it lands.</summary>
        private void Arrived(BigFlyer f, double now)
        {
            var st = f.Strike;
            var boss = f.Boss;
            if (st.Shape != BigShape.Swarm)
            {
                BlastAt(boss, st, f.To, f.Scale);
                if (st.Fire is { } fire) Burn(boss, f.To, fire, default, now);
                return;
            }
            var jammed = _world.Abilities.Jammed(f.To, boss.Team) && _world.Random.NextDouble() < 0.5;
            Vehicle? target = null;
            if (!jammed && f.Target.IsValid && _world.TryGetVehicle(f.Target, out var t) && t.IsAlive && Vector2.Distance(t.Position, f.To) < 8f) target = t;
            if (!jammed && target == null)
            {
                // Its target gone: the nearest other one on the ground close by.
                var best = 12f * 12f;
                foreach (var e in _world.VehicleList)
                {
                    if (!Target(boss, e, false)) continue;
                    var d2 = Vector2.DistanceSquared(e.Position, f.To);
                    if (d2 >= best) continue;
                    best = d2;
                    target = e;
                }
            }
            var at = target?.Position ?? f.To + (jammed ? RandomIn(_world.Random, 7f) : Vector2.Zero);
            if (target != null)
                _world.Damage.Apply(target, st.Damage * f.Scale, st.Type, new HitInfo(boss, boss.Team, null, f.From, HitKind.Direct, true).WithPen(st.Pen, st.Top));
            _world.Emit(SimEvent.Exploded(at, new ExplosionDef(0f, st.Radius, 0f, ExplosionTier.Large), boss.Id));
        }

        // ================================================================== burning ground

        private void Burn(Vehicle boss, Vector2 at, BigFireDef fire, Vector2 side, double now)
        {
            _bigFires.Add((at, fire.Radius, now + fire.Seconds, fire.Dps, boss, side));
            // Patches of fire for the view: one for a small fire, a ring of them for a sea of flame (one half with a side).
            if (fire.Radius <= 9f)
            {
                _world.Emit(SimEvent.FireTrail(boss, at, fire.Seconds, fire.Radius));
                return;
            }
            _world.Emit(SimEvent.FireTrail(boss, at, fire.Seconds, fire.Radius * 0.35f));
            for (var k = 0; k < 8; k++)
            {
                var a = k * SimMath.Tau / 8f;
                var dir = new Vector2(MathF.Cos(a), MathF.Sin(a));
                if (side.LengthSquared() > 0.01f && Vector2.Dot(dir, side) < 0f) continue;
                _world.Emit(SimEvent.FireTrail(boss, _world.ClampToMap(at + dir * fire.Radius * 0.65f), fire.Seconds, fire.Radius * 0.35f));
            }
        }

        /// <summary>Twice a second: the burning ground sets the other side's ground units in it on fire.</summary>
        private void StepFires(double now)
        {
            if (_bigFires.Count == 0 || _world.Tick % 10 != 5) return;
            for (var i = _bigFires.Count - 1; i >= 0; i--)
            {
                var (at, radius, until, dps, boss, side) = _bigFires[i];
                if (now >= until)
                {
                    _bigFires.RemoveAt(i);
                    continue;
                }
                var half = side.LengthSquared() > 0.01f;
                foreach (var e in _world.VehicleList)
                {
                    if (!e.IsAlive || e.Team == boss.Team || e.Team < 0 || e.Flying || e.Def.Boss) continue;
                    var reach = radius + e.Radius;
                    if (Vector2.DistanceSquared(e.Position, at) > reach * reach || (half && Vector2.Dot(e.Position - at, side) < 0f)) continue;
                    _world.Status.Burn(e, dps, 1.2f, boss.Team, boss.Id);
                }
            }
        }

        // ================================================================== the Earth Worm's quake

        /// <summary>The worm reached its group under a big dive: the ground cracks for the big attack's warning.</summary>
        internal float QuakeWarned(Vehicle v, Vector2 at, float warn)
        {
            if (!v.BigQuake || v.BigAttack is not { } s || _world.BigAttackSettings is not { } settings) return warn;
            var st = s.Def.Strikes[0];
            var scale = ScaleOf(v, settings);
            warn = MathF.Max(0.5f, s.Def.Warn + scale.Warn);
            var now = _world.Time;
            s.WarnStart = now;
            s.FireAt = now + warn;
            s.Aim = at;
            s.ZoneList.Clear();
            s.ZoneList.Add(new BigZone(at, st.Radius, s.FireAt, true));
            _world.Emit(SimEvent.Big(v, s.Def.Id, 0, at, warn));
            _world.Emit(SimEvent.RadioMessage(s.Def.RadioKey, v.Team));
            Dodge(v, s, now);
            return warn;
        }

        /// <summary>The big quake breaks out: the attack's damage and stun instead of the ordinary dive's.</summary>
        internal bool BigQuakeHits(Vehicle v)
        {
            if (!v.BigQuake || v.BigAttack is not { } s || _world.BigAttackSettings is not { } settings) return false;
            v.BigQuake = false;
            var st = s.Def.Strikes[0];
            BlastAt(v, st, v.Position, DamageOf(v, ScaleOf(v, settings)));
            _world.Emit(SimEvent.Big(v, s.Def.Id, 1, v.Position, 0f));
            Finish(v, s);
            return true;
        }

        // ================================================================== getting out of the way

        /// <summary>
        /// The other side's ground units inside a harmful zone make for the nearest way out if they can reach it in
        /// time (not into another zone), and go back once it has landed: their earlier order again, or where they were.
        /// </summary>
        private void Dodge(Vehicle boss, BigAttackState s, double now)
        {
            var margin = _world.Catalog.BigAttackRules.Dodge;
            var back = now;
            foreach (var z in s.ZoneList) back = Math.Max(back, z.Due);
            foreach (var st in s.Def.Strikes) back = Math.Max(back, s.FireAt + st.Duration + (st.Fire?.Seconds ?? 0f));
            back += 1.0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == boss.Team || e.Team < 0 || e.Flying || e.Def.Static || e.Def.Boss || e.Scripted || e.Stunned) continue;
                var inside = -1;
                for (var i = 0; i < s.ZoneList.Count; i++)
                    if (s.ZoneList[i].Harmful && s.ZoneList[i].Contains(e.Position, e.Radius + s.ZoneList[i].Pad))
                    {
                        inside = i;
                        break;
                    }
                if (inside < 0) continue;
                var zone = s.ZoneList[inside];
                var pad = margin + e.Radius + zone.Pad;
                var fallback = SimMath.Forward(e.Heading);
                var (best, other) = zone.Exits(e.Position, pad, fallback);
                var exit = _world.ClampToMap(best);
                if (InAnyZone(s, exit, e.Radius)) exit = _world.ClampToMap(other);
                if (InAnyZone(s, exit, e.Radius)) continue;
                var speed = e.Def.Speed * e.SpeedFactor;
                if (speed <= 0.1f || Vector2.Distance(e.Position, exit) / speed > zone.Due - now - 0.2) continue;
                var before = e.Order;
                for (var k = _dodges.Count - 1; k >= 0; k--)
                    if (_dodges[k].unit == e)
                    {
                        // Already dodging another one: keep its first order to go back to.
                        before = _dodges[k].before;
                        _dodges.RemoveAt(k);
                    }
                Steer(e, CommandType.Move, exit, EntityId.None);
                _dodges.Add((e, before, e.Position, _world.ClampToMap(exit), back));
            }
        }

        private static bool InAnyZone(BigAttackState s, Vector2 p, float pad)
        {
            foreach (var z in s.ZoneList)
                if (z.Harmful && z.Contains(p, pad + z.Pad)) return true;
            return false;
        }

        private void StepDodges(double now)
        {
            for (var i = _dodges.Count - 1; i >= 0; i--)
            {
                var (unit, before, from, exit, back) = _dodges[i];
                if (now < back) continue;
                _dodges.RemoveAt(i);
                // Still on our order (or there and idle); given another since (by the player or its commander): leave it be.
                var ours = unit.Order.Kind == OrderKind.Idle || (unit.Order.Kind == OrderKind.Move && Vector2.Distance(unit.Order.Point, exit) <= 2f);
                if (!unit.IsAlive || !ours) continue;
                switch (before.Kind)
                {
                    case OrderKind.Move:
                    case OrderKind.AttackMove:
                    case OrderKind.Retreat:
                        Steer(unit, before.Kind == OrderKind.AttackMove ? CommandType.AttackMove : before.Kind == OrderKind.Retreat ? CommandType.Retreat : CommandType.Move,
                            before.Point, EntityId.None);
                        break;
                    case OrderKind.Attack when _world.TryGetVehicle(before.Target, out var target) && target.IsAlive:
                        Steer(unit, CommandType.Attack, target.Position, before.Target);
                        break;
                    default:
                        Steer(unit, CommandType.Move, from, EntityId.None);
                        break;
                }
            }
        }

        /// <summary>Big attacks into the battle's fingerprint.</summary>
        private void MixBig(Action<long> mix)
        {
            foreach (var v in _world.VehicleList)
                if (v.BigAttack is { } s) mix((long)s.Stage * 1_000_000 + (long)Math.Round(s.Next * 10.0));
            mix(_bigBlasts.Count * 4096 + _bigFlyers.Count * 64 + _bigFires.Count);
            mix(_dodges.Count);
        }
    }
}
