#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P4 (lane A), the air side of the advanced planning (1 Hz, for the aircraft outside squads): SEAD packages
    /// (174: suppression -> strike ingress -> egress; delay or reroute when the suppression fails), aircraft risk routing on
    /// the AirRiskMap (175: low-risk ingress, egress, no repeated pass through the strongest SAM bubble), CAP patrol zones
    /// (176: boss, main force, objective, expected approach corridor; no chase to the map edge), air target handoff (177:
    /// 1-2 attackers by TTK, never six on one weak target), bomber packages (178: a valuable target, an acceptable route, the
    /// blast clear of friends, the SEAD window) and predictive air interception. The aircraft's orders are owned by the
    /// package while it holds them (TacticalAi leaves a held aircraft alone). Fog-fair: known anti-air and seen aircraft only.
    /// </summary>
    public sealed partial class AiCommander
    {
        private enum AirRole : byte
        {
            Fighter,
            Bomber,
            Strike,
        }

        private sealed class SeadState
        {
            public double Start, Made, SuppressedAt = double.NaN;
            public bool Rerouted, Delayed, GaveUp;
        }

        private Vector2? _seadWanted;
        private double _seadWantedAt = double.NegativeInfinity, _airPreparedAt = double.NegativeInfinity;
        private readonly List<Vector2> _capZones = new();
        private readonly List<Vehicle> _fighters = new();
        private readonly List<Contact> _airTargets = new();
        private readonly Dictionary<EntityId, Contact> _airAssign = new();
        private readonly Dictionary<EntityId, double> _patrolAt = new(), _egressAt = new(), _airFreeUntil = new();
        private readonly Dictionary<EntityId, (Vector2 goal, double since)> _bomberHold = new(), _strikeHold = new();
        private readonly Dictionary<long, SeadState> _sead = new();
        private readonly Dictionary<EntityId, (int passes, bool inside)> _airPasses = new();
        private Contact? _strongestAa;

        private static AirRole RoleOf(Vehicle v)
        {
            var w = v.Def.Weapon;
            if (v.Def.Interceptor || (w.CanTarget(true) && !w.CanTarget(false))) return AirRole.Fighter;
            if (v.Def.FixedWing)
                foreach (var m in v.Def.Mounts)
                    if (m.Weapon.Projectile == ProjectileKind.Bomb) return AirRole.Bomber;
            return AirRole.Strike;
        }

        private static float BlastOf(Vehicle v)
        {
            var r = 8f;
            foreach (var m in v.Def.Mounts)
                if (m.Weapon.Projectile == ProjectileKind.Bomb) r = MathF.Max(r, m.Weapon.SplashRadius);
            return r;
        }

        private static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var len = ab.LengthSquared();
            if (len < 1e-4f) return Vector2.Distance(p, a);
            var t = Math.Clamp(Vector2.Dot(p - a, ab) / len, 0f, 1f);
            return Vector2.Distance(p, a + ab * t);
        }

        /// <summary>The air part for one aircraft: true when the P4 air logic gave (or keeps) its order this look.</summary>
        private bool AirP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            if (PlanningP4 is not { } tp || !DifficultyGate.AirPackages(Level) || v.Def.Weapon.Damage <= 0f ||
                (_airFreeUntil.TryGetValue(v.Id, out var free) && now < free))
            {
                v.P4Held = false;
                return false;
            }
            PrepareAirP4(world, intel);
            var role = RoleOf(v);
            var handled = role switch
            {
                AirRole.Fighter => FighterP4(world, intel, v),
                AirRole.Bomber => BomberP4(world, intel, v) || StrikeP4(world, intel, v),
                _ => StrikeP4(world, intel, v),
            };
            v.P4Held = handled;
            if (handled) tp.Ownership.Claim(v.Id.Value, IntentOwner.AirPackage, now + Tun.Ownership.AirClaimS, now);
            else tp.Ownership.Release(v.Id.Value, IntentOwner.AirPackage);
            return handled;
        }

        private void PrepareAirP4(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            if (now <= _airPreparedAt) return;
            _airPreparedAt = now;
            _airTargets.Clear();
            _strongestAa = null;
            foreach (var c in intel.Contacts)
            {
                if (c.Flying && (c.InSight || c.Age(now) < 3f)) _airTargets.Add(c);
                if ((c.AntiAir || c.Group == ForceGroup.AntiAir) && !c.Flying && c.Age(now) < 30f && !c.Displaced &&
                    (_strongestAa == null || c.Strength > _strongestAa.Strength + 1e-4f)) _strongestAa = c;
            }
            _airTargets.Sort((a, b) =>
            {
                var k = b.Strength.CompareTo(a.Strength);
                return k != 0 ? k : a.Id.Value.CompareTo(b.Id.Value);
            });
            // Spec 176: CAP zones: the own boss, the main force, the objective, the expected approach corridor.
            _capZones.Clear();
            void Zone(Vector2 p)
            {
                foreach (var z in _capZones)
                    if (Vector2.Distance(z, p) < 40f) return;
                _capZones.Add(world.Map.Clamp(p, 10f));
            }
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && v.Def.Boss) Zone(v.Position);
            Squad? main = null;
            foreach (var s in Squads.Squads)
                if (s.MemberList.Count > 0 && (main == null || s.Strength > main.Strength)) main = s;
            if (main != null) Zone(main.Centre);
            if (Intent.PrimaryObjective is { } o) Zone(o);
            var anchor = main?.Centre ?? Intent.PrimaryObjective;
            if (anchor is { } a)
            {
                var found = false;
                var nearest = Vector2.Zero;
                foreach (var g in intel.EnemyGroups)
                    if (g.Air && (!found || Vector2.Distance(g.Centre, a) < Vector2.Distance(nearest, a)))
                    {
                        nearest = g.Centre;
                        found = true;
                    }
                if (found) Zone(Vector2.Lerp(a, nearest, 0.5f));
            }
            // Spec 177: handoff: each seen aircraft gets the attackers its TTK needs (1-2), nearest fighters whose zone it is in.
            _fighters.Clear();
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && v.Flying && !v.Scripted && !v.IsEscort && RoleOf(v) == AirRole.Fighter && v.Def.Weapon.Damage > 0f) _fighters.Add(v);
            _fighters.Sort((a2, b2) => a2.Id.Value.CompareTo(b2.Id.Value));
            _airAssign.Clear();
            if (_fighters.Count == 0 || _capZones.Count == 0) return;
            var used = new HashSet<EntityId>();
            var pick = new List<(float d, Vehicle f)>();
            foreach (var t in _airTargets)
            {
                if (!ContactUnit(world, t, out var unit)) continue;
                var w = _fighters[0].Def.Weapon;
                var dps = WeaponDps(w) * world.Catalog.Damage.Effective(w, unit.def.Armour.Front, TargetKind.Air);
                var need = AirRules.Attackers(unit.hp, dps, Tun.AirOps.HandoffTtkS, Tun.AirOps.HandoffMax);
                pick.Clear();
                for (var i = 0; i < _fighters.Count; i++)
                {
                    var f = _fighters[i];
                    if (used.Contains(f.Id) || AirRules.OutsideCap(_capZones[i % _capZones.Count], t.Position)) continue;
                    pick.Add((Vector2.Distance(f.Position, t.Position), f));
                }
                pick.Sort((x, y) =>
                {
                    var k = x.d.CompareTo(y.d);
                    return k != 0 ? k : x.f.Id.Value.CompareTo(y.f.Id.Value);
                });
                for (var k = 0; k < pick.Count && k < need; k++)
                {
                    _airAssign[pick[k].f.Id] = t;
                    used.Add(pick[k].f.Id);
                }
            }
        }

        // ------------------------------------------------------------------------------------------------ 176-177 fighters

        private bool FighterP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            var tp = _p4!;
            var index = _fighters.IndexOf(v);
            if (index < 0 || _capZones.Count == 0) return false;
            var zone = _capZones[index % _capZones.Count];
            if (_airAssign.TryGetValue(v.Id, out var t))
            {
                if (v.Order.Kind == OrderKind.Attack && v.Order.Target == t.Id) return true;
                var reach = v.Def.Weapon.Range;
                var d = Vector2.Distance(v.Position, t.Position);
                if (d > reach * 1.2f && t.Velocity.LengthSquared() > 1f)
                {
                    // Predictive interception: where the aircraft will be, not where it is.
                    var ip = world.Map.Clamp(PursuitDiscipline.Intercept(v.Position, MathF.Max(1f, v.Def.Speed), t.Position, t.Velocity, Tun.AirOps.InterceptHorizonS, t.Age(now), out _), 10f);
                    if (v.Order.Kind != OrderKind.AttackMove || Vector2.Distance(v.Order.Point, ip) > 15f)
                    {
                        world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, ip));
                        tp.Metrics.AirIntercepts++;
                        if (LogDue(0x5000 + (v.Id.Value & 0xfff), 5.0)) P4Reasons.Unit(world, v, DecisionKind.Target, P4Reasons.AirIntercept, $"#{t.Id.Value} at ({ip.X:0},{ip.Y:0})");
                    }
                    return true;
                }
                var had = v.Order.Kind == OrderKind.Attack ? v.Order.Target : EntityId.None;
                world.Submit(new Command(CommandType.Attack, Team, new[] { v.Id }, t.Position, t.Id));
                tp.Metrics.Handoffs++;
                P4Reasons.Unit(world, v, DecisionKind.Target, P4Reasons.Handoff, had.IsValid ? $"#{had.Value} -> #{t.Id.Value}" : $"#{t.Id.Value}");
                return true;
            }
            // Not needed on the aircraft it chases (enough attackers on it already): back to the CAP.
            if (v.Order.Kind == OrderKind.Attack && world.TryGetVehicle(v.Order.Target, out var chased) && chased.Flying)
            {
                world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, AirRules.PatrolPoint(zone, v.Id.Value, now)));
                tp.Metrics.Handoffs++;
                P4Reasons.Unit(world, v, DecisionKind.Target, P4Reasons.Handoff, $"#{chased.Id.Value} has its attackers: back to CAP");
                return true;
            }
            if (AirRules.OutsideCap(zone, v.Position))
            {
                var back = AirRules.PatrolPoint(zone, v.Id.Value, now);
                if (v.Order.Kind != OrderKind.Move || Vector2.Distance(v.Order.Point, back) > 15f)
                {
                    world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, back));
                    tp.Metrics.CapReturns++;
                    P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.CapReturn, $"zone ({zone.X:0},{zone.Y:0})");
                }
                return true;
            }
            if (!_patrolAt.TryGetValue(v.Id, out var next) || now >= next || v.Order.Kind == OrderKind.Idle)
            {
                _patrolAt[v.Id] = now + Tun.AirOps.CapPatrolS;
                var p = AirRules.PatrolPoint(zone, v.Id.Value, now);
                world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, p));
                if (LogDue(0x5100 + (v.Id.Value & 0xfff), 30.0)) P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.CapPatrol, $"zone ({zone.X:0},{zone.Y:0})");
            }
            return true;
        }

        // ------------------------------------------------------------------------------------------------ 178 bombers

        private float SeenGroundStrength(TeamIntel intel, Vector2 at, float radius)
        {
            var sum = 0f;
            foreach (var c in intel.Contacts)
                if (c.InSight && !c.Flying && Vector2.Distance(c.Position, at) <= radius) sum += c.Strength;
            return sum;
        }

        private bool FriendsNear(SimWorld world, Vector2 at, float radius)
        {
            foreach (var u in world.VehicleList)
                if (u.IsAlive && u.Team == Team && !u.Flying && Vector2.Distance(u.Position, at) <= radius + u.Radius) return true;
            return false;
        }

        private bool SeadReadyP4(TeamIntel intel, Vector2 goal, float strength, double now)
        {
            if (!DifficultyGate.Sead(Level) || !AirRules.SeadNeeded(intel.ThreatAt(ThreatKind.AntiAir, goal), strength)) return true;
            var tp = _p4!;
            if (tp.WindowNear(goal, OpportunityRoles.Air, 10f) is { Kind: OpportunityKind.AntiAirDown }) return true;
            return tp.SeadUsed is { } su && now - su.time <= 15.0 && Vector2.Distance(su.at, goal) <= 80f;
        }

        private bool BomberP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            var tp = _p4!;
            Vector2 goal;
            var held = _bomberHold.TryGetValue(v.Id, out var h);
            if (held) goal = h.goal;
            else if (v.Order.Kind == OrderKind.AttackMove) goal = v.Order.Point;
            else if (v.Order.Kind == OrderKind.Attack && world.TryGetVehicle(v.Order.Target, out var tg)) goal = tg.Position;
            else return false;
            var blast = BlastOf(v);
            var strength = MathF.Max(1f, TeamIntel.StrengthOf(v));
            float Risk(Vector2 a, Vector2 b) => AirRules.LegRisk(p => intel.ThreatAt(ThreatKind.AntiAir, p), a, b, Tun.AirOps.RiskSamples) / strength;
            var value = SeenGroundStrength(intel, goal, blast + 4f);
            var urgent = _urgency >= Tun.Pursuit.UrgencyDrop && Intent.PrimaryObjective is { } po && Vector2.Distance(po, goal) < 40f;
            var waited = held && now - h.since >= Tun.AirOps.BomberWaitMaxS;
            var risk = Risk(v.Position, goal);
            var clear = !FriendsNear(world, goal, blast + Tun.AirOps.BomberBlastGap) && tp.DropClear(goal, blast, now);
            var sead = SeadReadyP4(intel, goal, strength, now);
            if (AirRules.BomberGo(value, urgent, waited, risk, clear, sead) || waited)
            {
                if (held)
                {
                    _bomberHold.Remove(v.Id);
                    world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, goal));
                    P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.BomberGo, waited ? "waited out: goes as before" : $"value {value:0.0}");
                    if (waited) _airFreeUntil[v.Id] = now + Tun.AirOps.BomberWaitMaxS;
                }
                tp.ReserveDrop(goal, blast, now + 6.0);
                return false;
            }
            // A better target in reach: the most valuable seen cluster on an acceptable route with the blast clear.
            Vector2? best = null;
            var bestValue = Tun.AirOps.BomberMinValue;
            foreach (var c in intel.Contacts)
            {
                if (!c.InSight || c.Flying) continue;
                var val = SeenGroundStrength(intel, c.Position, blast + 4f);
                if (val < bestValue - 1e-4f || Risk(v.Position, c.Position) > Tun.AirOps.BomberRiskMax) continue;
                if (FriendsNear(world, c.Position, blast + Tun.AirOps.BomberBlastGap) || !tp.DropClear(c.Position, blast, now)) continue;
                if (!SeadReadyP4(intel, c.Position, strength, now)) continue;
                if (best == null || val > bestValue + 1e-4f)
                {
                    best = c.Position;
                    bestValue = val;
                }
            }
            if (best is { } b)
            {
                _bomberHold.Remove(v.Id);
                world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, b));
                tp.ReserveDrop(b, blast, now + 6.0);
                tp.Metrics.BomberRetargets++;
                P4Reasons.Unit(world, v, DecisionKind.Target, P4Reasons.BomberRetarget, $"value {bestValue:0.0} at ({b.X:0},{b.Y:0})");
                return true;
            }
            var why = value < Tun.AirOps.BomberMinValue && !urgent ? "value" : risk > Tun.AirOps.BomberRiskMax ? "route" : !clear ? "blast" : "sead";
            if (!held)
            {
                _bomberHold[v.Id] = (goal, now);
                tp.Metrics.BomberWaits++;
                P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.BomberWait, $"{why} ({value:0.0} at ({goal.X:0},{goal.Y:0}))");
            }
            var loiter = OwnCentre(world, out _);
            if (v.Order.Kind != OrderKind.Move || Vector2.Distance(v.Order.Point, loiter) > 15f)
                world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, world.Map.Clamp(loiter, 10f)));
            return true;
        }

        // ------------------------------------------------------------------------------------------------ 174-175 strike aircraft

        private bool StrikeP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            if (EgressP4(world, intel, v)) return true;
            if (DifficultyGate.Sead(Level) && SeadP4(world, intel, v)) return true;
            return RiskRouteP4(world, intel, v);
        }

        /// <summary>The best of five approach waypoints 50 m out of the goal by AirRiskMap risk (spec 175), with its risk.</summary>
        private Vector2? Approach(SimWorld world, TeamIntel intel, Vehicle v, Vector2 goal, out float cost)
        {
            float Leg(Vector2 a, Vector2 b) => AirRules.LegRisk(p => intel.ThreatAt(ThreatKind.AntiAir, p), a, b, Tun.AirOps.RiskSamples);
            var inbound = goal - v.Position;
            inbound = inbound.LengthSquared() > 0.01f ? Vector2.Normalize(inbound) : Vector2.UnitX;
            Vector2? pick = null;
            cost = float.MaxValue;
            foreach (var angle in new[] { 0f, -1.05f, 1.05f, -1.75f, 1.75f })
            {
                float c = MathF.Cos(angle), s = MathF.Sin(angle);
                var dir = new Vector2(inbound.X * c - inbound.Y * s, inbound.X * s + inbound.Y * c);
                var wp = world.Map.Clamp(goal - dir * 50f, 10f);
                var k = Leg(v.Position, wp) + Leg(wp, goal);
                if (k < cost - 1e-4f)
                {
                    cost = k;
                    pick = wp;
                }
            }
            return pick;
        }

        private bool SeadP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            var tp = _p4!;
            Vector2 goal;
            var held = _strikeHold.TryGetValue(v.Id, out var h);
            if (held) goal = h.goal;
            else if (v.Order.Kind == OrderKind.AttackMove) goal = v.Order.Point;
            else return false;
            var strength = MathF.Max(1f, TeamIntel.StrengthOf(v));
            if (!AirRules.SeadNeeded(intel.ThreatAt(ThreatKind.AntiAir, goal), strength) || !SeadMeansP4(world))
            {
                if (held)
                {
                    _strikeHold.Remove(v.Id);
                    world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, goal));
                }
                return false;
            }
            var key = (long)MathF.Floor(goal.X / 30f) * 100003L + (long)MathF.Floor(goal.Y / 30f);
            if (!_sead.TryGetValue(key, out var st) || now - st.Made > 90.0)
            {
                _sead[key] = st = new SeadState { Start = now, Made = now };
                tp.Metrics.SeadPackages++;
                if (_sead.Count > 32)
                {
                    var old = new List<long>();
                    foreach (var kv in _sead)
                        if (now - kv.Value.Made > 90.0) old.Add(kv.Key);
                    foreach (var k in old) _sead.Remove(k);
                }
            }
            if (st.GaveUp) return false;
            if (SeadReadyP4(intel, goal, strength, now))
            {
                if (double.IsNaN(st.SuppressedAt))
                {
                    st.SuppressedAt = now;
                    tp.Metrics.SeadSuccess++;
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.SeadGo, $"({goal.X:0},{goal.Y:0})");
                }
                // Spec 217: the strikers go a little apart (deterministic stagger), not as one robot wave.
                if (now - st.SuppressedAt < HumanStagger.Delay(v.Id.Value, (int)(key & 0x7fffffff))) return held;
                if (held)
                {
                    _strikeHold.Remove(v.Id);
                    world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, goal));
                }
                return false;
            }
            Contact? aa = null;
            foreach (var c in intel.Contacts)
                if ((c.AntiAir || c.Group == ForceGroup.AntiAir) && !c.Flying && c.Age(now) < 30f && Vector2.Distance(c.Position, goal) <= 80f &&
                    (aa == null || c.Strength > aa.Strength + 1e-4f)) aa = c;
            if (now - st.Start < Tun.AirOps.SeadHoldS)
            {
                var inbound = goal - v.Position;
                inbound = inbound.LengthSquared() > 0.01f ? Vector2.Normalize(inbound) : Vector2.UnitX;
                var centre = aa?.Position ?? goal;
                var ingress = world.Map.Clamp(centre - inbound * ((aa?.Reach ?? 40f) + Tun.AirOps.SeadStandoff), 10f);
                if (!held) _strikeHold[v.Id] = (goal, now);
                if (v.Order.Kind != OrderKind.Move || Vector2.Distance(v.Order.Point, ingress) > 15f)
                {
                    world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, ingress));
                    P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.SeadHold, $"SAM ({centre.X:0},{centre.Y:0}): wait for suppression");
                }
                _seadWanted = centre;
                _seadWantedAt = now;
                return true;
            }
            _strikeHold.Remove(v.Id);
            if (!st.Rerouted)
            {
                st.Rerouted = true;
                if (Approach(world, intel, v, goal, out var cost) is { } wp && cost / strength <= Tun.AirOps.BomberRiskMax)
                {
                    _approach[v.Id] = (goal, now + 25.0);
                    world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, wp));
                    tp.Metrics.SeadReroutes++;
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.SeadReroute, $"via ({wp.X:0},{wp.Y:0}) risk {cost / strength:0.00}");
                    return true;
                }
            }
            if (!st.Delayed)
            {
                st.Delayed = true;
                st.Start = now;
                P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.SeadDelay, $"({goal.X:0},{goal.Y:0})");
                _strikeHold[v.Id] = (goal, now);
                return true;
            }
            st.GaveUp = true;
            world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, goal));
            return false;
        }

        /// <summary>Spec 175 egress: just fired inside dense anti-air: out by the lowest-risk way, away from the strongest SAM.</summary>
        private bool EgressP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            if (now - v.LastFiredAt > 2.0 || (_egressAt.TryGetValue(v.Id, out var at) && now < at)) return false;
            var strength = MathF.Max(1f, TeamIntel.StrengthOf(v));
            if (intel.ThreatAt(ThreatKind.AntiAir, v.Position) < strength * 0.5f) return false;
            var from = _strongestAa?.Position ?? (v.Order.Kind == OrderKind.AttackMove ? v.Order.Point : v.Position + SimMath.Forward(v.Heading) * 10f);
            var away = v.Position - from;
            away = away.LengthSquared() > 0.01f ? Vector2.Normalize(away) : -SimMath.Forward(v.Heading);
            Vector2? pick = null;
            var best = float.MaxValue;
            foreach (var angle in new[] { 0f, -0.87f, 0.87f, -1.75f, 1.75f })
            {
                float c = MathF.Cos(angle), s = MathF.Sin(angle);
                var dir = new Vector2(away.X * c - away.Y * s, away.X * s + away.Y * c);
                var p = world.Map.Clamp(v.Position + dir * 70f, 10f);
                var risk = AirRules.LegRisk(q => intel.ThreatAt(ThreatKind.AntiAir, q), v.Position, p, Tun.AirOps.RiskSamples);
                if (risk < best - 1e-4f)
                {
                    best = risk;
                    pick = p;
                }
            }
            if (pick is not { } egress) return false;
            _egressAt[v.Id] = now + 6.0;
            world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, egress));
            _p4!.Metrics.Egresses++;
            if (LogDue(0x5200 + (v.Id.Value & 0xfff), 5.0)) P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.Egress, $"risk {best:0.0}");
            return true;
        }

        /// <summary>Spec 175 ingress: no second pass through the strongest SAM bubble when a lower-risk way exists; Hard and up weigh five approaches.</summary>
        private bool RiskRouteP4(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            var crosses = false;
            if (_strongestAa is { } aa)
            {
                var inside = Vector2.Distance(v.Position, aa.Position) < aa.Reach;
                _airPasses.TryGetValue(v.Id, out var ps);
                if (inside && !ps.inside) ps.passes++;
                ps.inside = inside;
                _airPasses[v.Id] = ps;
                if (v.Order.Kind == OrderKind.AttackMove) crosses = SegmentDistance(aa.Position, v.Position, v.Order.Point) < aa.Reach && ps.passes >= Tun.AirOps.RiskPassLimit;
            }
            if (_approach.ContainsKey(v.Id) || v.Order.Kind != OrderKind.AttackMove) return false;
            var goal = v.Order.Point;
            if (Vector2.Distance(v.Position, goal) < 60f || (!crosses && Level < 2)) return false;
            var direct = AirRules.LegRisk(p => intel.ThreatAt(ThreatKind.AntiAir, p), v.Position, goal, Tun.AirOps.RiskSamples);
            if (direct <= 0f) return false;
            if (Approach(world, intel, v, goal, out var cost) is not { } wp || cost >= direct * (crosses ? 1f : 0.7f)) return false;
            _approach[v.Id] = (goal, now + 25.0);
            world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, wp));
            _p4!.Metrics.RiskReroutes++;
            P4Reasons.Unit(world, v, DecisionKind.Action, P4Reasons.RiskRoute, $"{(crosses ? "no second pass through the SAM; " : "")}risk {direct:0.0} -> {cost:0.0}");
            return true;
        }
    }
}
