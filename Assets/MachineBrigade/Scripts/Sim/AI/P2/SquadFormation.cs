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
    /// AI MASTER P2, formations: Part G's threat-specific switching with hysteresis (splash -> Spread, choke / bridge / gate
    /// -> Travel (86), static defence -> Hold, validated flank -> Flank, low cohesion -> Regroup), spec 27's role placement,
    /// 159 morphing through a halfway slot, 160 stable slot assignment, 161 a stable travel column, 162 splash-aware
    /// spacing and packets, spec 22's choke packets (2-4 s apart), and Part D's firing-position pick for TD / MBT slots.
    /// </summary>
    public sealed partial class SquadLayer
    {
        // ------------------------------------------------------------------------------------------------ placement (27)

        /// <summary>
        /// Spec 27: front heavy / durable / breacher; middle main gun / generalist / AT; rear artillery / SAM / EW / repair
        /// (never front: artillery, ammo carriers, fragile radars); outer recon and fast flankers. Part F: a lost main gun,
        /// a lost APS or a crippled engine takes a vehicle off the front row (no retreat: it stays in the squad).
        /// </summary>
        internal static Placement PlacementOf(SimWorld world, Vehicle v, bool fastSquad)
        {
            var role = CombatRoleDoctrine.BaseRole(world, v);
            var p = role switch
            {
                DoctrineRole.Breacher or DoctrineRole.MainBattle => Placement.Front,
                DoctrineRole.FireSupport or DoctrineRole.AntiAir or DoctrineRole.Support or DoctrineRole.Siege or
                    DoctrineRole.LoiterAntiArmour or DoctrineRole.LoiterAntiArtillery => Placement.Rear,
                DoctrineRole.Recon => Placement.Outer,
                _ => Placement.Middle,
            };
            if (p == Placement.Middle && v.Def.Class == UnitClass.Heavy) p = Placement.Front;
            if (p == Placement.Middle && !fastSquad && v.Def.Speed >= 11f) p = Placement.Outer;
            if (p == Placement.Front)
            {
                var state = world.Components.Of(v);
                if (state.MainGunLost || state.ApsLost || state.EngineCrippled) p = Placement.Middle;
            }
            return p;
        }

        private static int Rank(Placement p) => p switch
        {
            Placement.Front => 0,
            Placement.Middle => 1,
            Placement.Outer => 2,
            _ => 3,
        };

        /// <summary>Spec 161: the travel column, rebuilt only when members changed (split, merge, loss, reinforcement, component change).</summary>
        internal void RebuildColumn(SimWorld world, Squad s)
        {
            var same = !s.ColumnDirty && s.ColumnOrderList.Count == s.MemberList.Count;
            if (same)
                foreach (var id in s.MemberList)
                    if (!s.ColumnOrderList.Contains(id))
                    {
                        same = false;
                        break;
                    }
            if (same) return;
            var members = new List<Vehicle>();
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) members.Add(v);
            members.Sort((a, b) =>
            {
                var ra = Rank(PlacementOf(world, a, s.Fast));
                var rb = Rank(PlacementOf(world, b, s.Fast));
                if (ra != rb) return ra.CompareTo(rb);
                if (a.MaxHp != b.MaxHp) return b.MaxHp.CompareTo(a.MaxHp);
                return a.Id.Value.CompareTo(b.Id.Value);
            });
            s.ColumnOrderList.Clear();
            foreach (var v in members) s.ColumnOrderList.Add(v.Id);
            s.ColumnDirty = false;
        }

        // ------------------------------------------------------------------------------------------------ switching (G, 86)

        /// <summary>The widest a formation stands across its facing (spec 22's requiredFormationWidth).</summary>
        internal float RequiredWidth(SimWorld world, Squad s, FormationMode mode)
        {
            var radius = 1.5f;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) radius = MathF.Max(radius, v.Radius);
            var n = Math.Max(1, s.MemberList.Count);
            var spacing = SpacingOf(world, s, mode);
            return mode switch
            {
                FormationMode.Travel => radius * 2f + 2f,
                FormationMode.Flank => n * spacing * 0.7f + radius * 2f,
                FormationMode.Regroup => RingRadius(n, spacing, radius) * 2f + radius * 2f,
                _ => (n - 1) * spacing + radius * 2f,
            };
        }

        private static float RingRadius(int n, float spacing, float radius) => n > 1 ? MathF.Max(spacing, (radius * 2f + 1.5f) * n / (2f * MathF.PI)) : 0f;

        /// <summary>The narrowest choke on the squad's next stretch towards <paramref name="goal"/> (+inf: none).</summary>
        internal float ChokeAhead(SimWorld world, Squad s, Vector2 goal)
        {
            var dist = Vector2.Distance(s.Centre, goal);
            if (dist < 1f) return float.PositiveInfinity;
            var dir = (goal - s.Centre) / dist;
            var length = MathF.Min(dist, Tun.Formation.ChokeLookahead);
            var narrowest = float.PositiveInfinity;
            foreach (var c in world.Topology.Chokes)
            {
                var along = Math.Clamp(Vector2.Dot(c.Centre - s.Centre, dir), 0f, length);
                if (Vector2.Distance(s.Centre + dir * along, c.Centre) < c.Width * 0.5f + 6f) narrowest = MathF.Min(narrowest, c.Width);
            }
            return narrowest;
        }

        /// <summary>Part G: the formation the squad wants now, with hysteresis (min commitment) unless an emergency trigger.</summary>
        internal void ChooseFormation(SimWorld world, TeamIntel intel, Squad s, Vector2 goal)
        {
            var now = world.Time;
            FormationMode want;
            string reason;
            var emergency = false;
            var byState = s.State switch
            {
                SquadState.Travel or SquadState.Approach => FormationMode.Travel,
                SquadState.Combat => FormationMode.Spread,
                SquadState.Hold or SquadState.Overwatch => FormationMode.Hold,
                SquadState.Flank => FormationMode.Flank,
                _ => FormationMode.Regroup,
            };
            var moving = s.State is SquadState.Travel or SquadState.Approach or SquadState.Flank || s.Action == SquadAction.Join;
            var choke = moving ? ChokeAhead(world, s, goal) : float.PositiveInfinity;
            var current = s.Formation == FormationMode.Travel ? byState : s.Formation;
            var splash = intel.EnemySplash > 0f && (intel.ThreatAt(ThreatKind.Splash, s.Centre) > 0f || intel.ThreatAt(ThreatKind.Artillery, s.Centre) > 0f);
            if (s.State == SquadState.Regroup || s.Action == SquadAction.Regroup)
            {
                want = FormationMode.Regroup;
                reason = P2Reasons.FormationLowCohesion;
            }
            else if (!float.IsInfinity(choke) && RequiredWidth(world, s, current) > Tun.Formation.ChokeShare * choke)
            {
                want = FormationMode.Travel;
                reason = P2Reasons.FormationChokeTravel;
                emergency = true;
            }
            else if (splash)
            {
                want = FormationMode.Spread;
                reason = P2Reasons.FormationSplashSpread;
                emergency = s.Formation != FormationMode.Spread;
            }
            else if (byState == FormationMode.Hold)
            {
                want = FormationMode.Hold;
                reason = P2Reasons.FormationStaticHold;
            }
            else if (byState == FormationMode.Flank)
            {
                want = FormationMode.Flank;
                reason = P2Reasons.FormationFlankOpen;
            }
            else
            {
                want = byState;
                reason = P2Reasons.FormationState;
            }
            if (want == s.Formation) return;
            // Hysteresis: hold the formation for its minimum commitment unless an emergency (choke, splash) overrides.
            if (!emergency && now - s.FormationSince < Tun.Formation.CommitSeconds) return;
            P2Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.State, reason, $"{s.Formation} -> {want}");
            s.Formation = want;
            s.FormationReason = reason;
            s.FormationSince = now;
            s.MorphUntil = now + Tun.Formation.MorphSeconds;
            s.MorphPending = s.SlotOf.Count > 0;
            s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            if (want == FormationMode.Regroup) s.ColumnDirty = true;
        }

        // ------------------------------------------------------------------------------------------------ slots

        private float SpacingOf(SimWorld world, Squad s, FormationMode mode) => mode switch
        {
            FormationMode.Spread => SpreadDistance(world, s),
            FormationMode.Hold => 9f,
            FormationMode.Regroup => 5f,
            _ => 6f,
        };

        /// <summary>
        /// The formation's slots round <paramref name="goal"/> facing <paramref name="facing"/>, each tagged with the
        /// placement it is for (spec 27): Travel a column in the stable column order; Spread / Hold a front row (front roles
        /// in the middle, outer roles at the ends; Hold an arc whose ends reach forward) and the rear row behind; Flank an
        /// echelon with the outer roles at its far end; Regroup a compact ring, nobody overlapping.
        /// </summary>
        private List<(Vector2 at, Placement tag)> FormationSlots(SimWorld world, Squad s, List<Vehicle> order, Vector2 goal, Vector2 facing,
            FormationMode mode, float spacing)
        {
            var slots = new List<(Vector2, Placement)>();
            var n = order.Count;
            var side = new Vector2(facing.Y, -facing.X);
            var places = new List<Placement>();
            foreach (var v in order) places.Add(PlacementOf(world, v, s.Fast));
            switch (mode)
            {
                case FormationMode.Travel:
                    for (var i = 0; i < n; i++) slots.Add((goal - facing * (i * spacing), places[i]));
                    break;
                case FormationMode.Flank:
                {
                    var sign = s.Action == SquadAction.FlankLeft ? -1f : 1f;
                    var tags = new List<Placement>();
                    foreach (var p in places) if (p is Placement.Front or Placement.Middle) tags.Add(p);
                    foreach (var p in places) if (p == Placement.Outer) tags.Add(p);
                    var i = 0;
                    foreach (var t in tags)
                    {
                        slots.Add((goal - facing * (i * spacing * 0.7f) + side * sign * (i * spacing * 0.7f), t));
                        i++;
                    }
                    var r = 0;
                    foreach (var p in places)
                        if (p == Placement.Rear) slots.Add((goal - facing * (Tun.Formation.RearRow + r * spacing * 0.7f) - side * sign * (r++ * spacing * 0.5f), p));
                    break;
                }
                case FormationMode.Regroup:
                {
                    var radius = 1.5f;
                    foreach (var v in order) radius = MathF.Max(radius, v.Radius);
                    var ring = RingRadius(n, spacing, radius);
                    for (var i = 0; i < n; i++)
                    {
                        var angle = i * MathF.PI * 2f / n;
                        slots.Add((goal + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * ring, places[i]));
                    }
                    break;
                }
                default:
                {
                    // The front row: front roles in the centre, middle roles round them, outer roles at the ends.
                    var row = new List<Placement>();
                    foreach (var p in places) if (p == Placement.Front) row.Add(p);
                    var middle = 0;
                    foreach (var p in places) if (p == Placement.Middle) middle++;
                    for (var k = 0; k < middle; k++)
                        if (k % 2 == 0) row.Add(Placement.Middle);
                        else row.Insert(0, Placement.Middle);
                    var outer = 0;
                    foreach (var p in places) if (p == Placement.Outer) outer++;
                    for (var k = 0; k < outer; k++)
                        if (k % 2 == 0) row.Add(Placement.Outer);
                        else row.Insert(0, Placement.Outer);
                    var m = row.Count;
                    for (var k = 0; k < m; k++)
                    {
                        var x = (k - (m - 1) * 0.5f) * spacing;
                        var arc = mode == FormationMode.Hold ? x * x / 120f : 0f;
                        slots.Add((goal + side * x + facing * arc, row[k]));
                    }
                    var rear = 0;
                    foreach (var p in places) if (p == Placement.Rear) rear++;
                    for (var k = 0; k < rear; k++)
                    {
                        var x = (k - (rear - 1) * 0.5f) * spacing;
                        slots.Add((goal - facing * Tun.Formation.RearRow + side * x, Placement.Rear));
                    }
                    break;
                }
            }
            return slots;
        }

        /// <summary>
        /// Spec 160: members keep their slot (same formation, same placement) when it is still there; the others take the
        /// nearest free slot of their placement, else the nearest free one. Travel follows the column order (161).
        /// </summary>
        private int[] AssignSlots(Squad s, List<Vehicle> order, List<(Vector2 at, Placement tag)> slots, List<Placement> places, FormationMode mode)
        {
            var n = order.Count;
            var pick = new int[n];
            var used = new bool[slots.Count];
            for (var i = 0; i < n; i++) pick[i] = -1;
            if (mode == FormationMode.Travel)
            {
                for (var i = 0; i < n && i < slots.Count; i++)
                {
                    pick[i] = i;
                    used[i] = true;
                }
                return pick;
            }
            if (s.SlotFormation == mode)
                for (var i = 0; i < n; i++)
                    if (s.SlotOf.TryGetValue(order[i].Id, out var k) && k < slots.Count && !used[k] && slots[k].tag == places[i])
                    {
                        pick[i] = k;
                        used[k] = true;
                    }
            for (var pass = 0; pass < 2; pass++)
                for (var i = 0; i < n; i++)
                {
                    if (pick[i] >= 0) continue;
                    var best = -1;
                    var bestD = float.MaxValue;
                    for (var k = 0; k < slots.Count; k++)
                    {
                        if (used[k] || (pass == 0 && slots[k].tag != places[i])) continue;
                        var d = Vector2.DistanceSquared(slots[k].at, order[i].Position);
                        if (d < bestD)
                        {
                            bestD = d;
                            best = k;
                        }
                    }
                    if (best < 0) continue;
                    pick[i] = best;
                    used[best] = true;
                }
            return pick;
        }

        /// <summary>
        /// Gives each member its slot (replaces the prompt-28 slots): stable, role-placed, morphing through a halfway point
        /// after a formation change, TD / MBT slots refined to the best firing position near them in Hold (Part D, not when the
        /// objective's timing is critical), and choke / splash packets (spec 22, 162) that go 2-4 s apart.
        /// </summary>
        internal void SlotsP2(SimWorld world, Squad s, Vector2 goal, Vector2 facing, FormationMode mode, CommandType type)
        {
            if (s.MemberList.Count == 0) return;
            var now = world.Time;
            RebuildColumn(world, s);
            var order = new List<Vehicle>();
            foreach (var id in s.ColumnOrderList)
                if (world.TryGetVehicle(id, out var v)) order.Add(v);
            if (order.Count == 0) return;
            // Flank: the fastest leads (prompt 28) within the placement bands.
            var spacing = SpacingOf(world, s, mode);
            // AI MASTER P1 (spec 28-31, 85-86): the shared corridor and the passage on it (column, packets, queue).
            var plan = PlanTraffic(world, s, goal, type, order);
            // Stage 1 of a member's jam loosens the formation a little (spec 38).
            foreach (var v in order)
                if (now < v.Traffic.LoosenUntil)
                {
                    spacing += 2f;
                    break;
                }
            var places = new List<Placement>();
            foreach (var v in order) places.Add(PlacementOf(world, v, s.Fast));
            var slots = FormationSlots(world, s, order, goal, facing, mode, spacing);
            var pick = AssignSlots(s, order, slots, places, mode);
            var morph = s.MorphPending && now < s.MorphUntil;
            var intel = world.Intel.For(_commander.Team);
            // Packets: a choke narrower than the formation needs (spec 22), a crowded passage (G.2), smaller under splash (162).
            // A passage reserved through P1's TrafficCoordinator makes its own packets / queue: these only without one.
            var packetSize = 0;
            if (plan.Passage == null && mode == FormationMode.Travel && order.Count > 2)
            {
                var choke = ChokeAhead(world, s, goal);
                var narrow = !float.IsInfinity(choke) && RequiredWidth(world, s, FormationMode.Travel) > Tun.Formation.ChokeShare * choke;
                if (narrow || Crowded(intel, s.Centre, goal)) packetSize = (order.Count + 1) / 2;
                if (packetSize > 0 && intel.EnemySplash > 0f && intel.ThreatAt(ThreatKind.Splash, s.Centre) + intel.ThreatAt(ThreatKind.Artillery, s.Centre) > 0f)
                    packetSize = Math.Max(1, Math.Min(packetSize, Tun.Formation.SplashPacket));
                if (packetSize > 0)
                {
                    s.StaggerUntil = now + Tun.Formation.PacketDelay;
                    P2Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P2Reasons.FormationPackets,
                        $"{(order.Count + packetSize - 1) / packetSize} packets of {packetSize}");
                }
            }
            var threat = NearestEnemy(intel, s.Centre);
            var urgent = s.Task.Window && s.Task.Kind == TaskKind.Primary && s.Action == SquadAction.Attack;
            s.SlotOf.Clear();
            for (var i = 0; i < order.Count; i++)
            {
                var v = order[i];
                if (packetSize > 0 && i >= packetSize)
                {
                    var packet = i / packetSize;
                    s.ReleaseAt[v.Id] = now + packet * Math.Clamp(Tun.Formation.PacketDelay, 2f, 4f);
                    world.Submit(new Command(CommandType.Stop, _commander.Team, new[] { v.Id }));
                    s.Progress[v.Id] = (v.Position, now, 0);
                    continue;
                }
                s.ReleaseAt.Remove(v.Id);
                var k = pick[i];
                var slot = k >= 0 ? slots[k].at : goal;
                if (k >= 0) s.SlotOf[v.Id] = k;
                slot = world.Map.Clamp(slot, 4f);
                if (!world.Grid.IsWalkable(slot)) slot = goal;
                // Part D: a TD / MBT holding ground takes the best firing position near its slot (hull-down first).
                if (mode == FormationMode.Hold && !urgent && places[i] is Placement.Front or Placement.Middle)
                {
                    var role = CombatRoleDoctrine.RoleOf(world, v);
                    if (role is DoctrineRole.TankDestroyer or DoctrineRole.MainBattle)
                    {
                        var aim = threat ?? goal + facing * MathF.Max(20f, s.Reach * 0.8f);
                        slot = FiringPositionScorer.Best(world, v, slot, aim, aim, role);
                    }
                }
                var final = slot;
                // Spec 159: morph through the halfway point, never a snap across the formation.
                if (morph && s.LastSlot.TryGetValue(v.Id, out var before)) slot = Vector2.Lerp(before, final, 0.5f);
                s.LastSlot[v.Id] = final;
                IssueSlot(world, s, v, i, slot, type, plan);
                s.Progress[v.Id] = (v.Position, now, 0);
            }
            s.SlotFormation = mode;
            if (!morph) s.MorphPending = false;
        }

        /// <summary>A member's release time after a packet wait (spec 22); 0 when it may go.</summary>
        private static double ReleaseOf(Squad s, EntityId id) => s.ReleaseAt.TryGetValue(id, out var at) ? at : 0.0;
    }
}
