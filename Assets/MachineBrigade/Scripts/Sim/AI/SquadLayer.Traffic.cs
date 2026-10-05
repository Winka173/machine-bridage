#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Movement;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P1 (lane B), spec 28-32, 85-86, 188-189: how a squad travels as a group. One shared corridor per order
    /// (phase 1: shared waypoints + local avoidance) instead of one route search per member; a passage on it within reach
    /// (gate, choke, bridge, narrow road) is reserved from the TrafficCoordinator: granted, the squad goes through in a
    /// column, in packets 2-4 s apart sized by the passage's lanes; queued (the other way holds it), the members wait at
    /// the queue positions Q1, Q2... beside the way in and go when the turn comes. An overloaded passage (more arrivals in
    /// 5 s than it passes) is avoided when the way round is under 1.5 x. The requested formation stands at the goal.
    /// </summary>
    public sealed partial class SquadLayer
    {
        /// <summary>One order's traffic plan (none: plain orders).</summary>
        private struct TrafficPlan
        {
            public SquadCorridor? Corridor;
            public Passage? Passage;
            public int Direction;
            public bool Queued;
            public int QueueBase;
            public int PacketSize;
            public double Start;
            public int Priority;
        }

        /// <summary>The squad's key with the coordinator (its side's squads are numbered by this commander).</summary>
        private int OwnerKey(Squad s) => _commander.Team * 65536 + s.Id;

        /// <summary>Spec 32 for a squad: heavy 80, main effort 70, artillery 60, normal 50, reinforcement (joining) 40, scouts 30.</summary>
        private static int SquadRightOfWay(Squad s, List<Vehicle> members)
        {
            int heavy = 0, artillery = 0;
            foreach (var v in members)
            {
                if (v.Def.Boss || v.Scripted) return TrafficSteering.PriorityBoss;
                if (v.Def.Class == UnitClass.Heavy) heavy++;
                if (v.Def.Class == UnitClass.Artillery || v.Def.Weapon.MinRange > 0f) artillery++;
            }
            if (members.Count > 0 && heavy * 2 >= members.Count) return TrafficSteering.PriorityHeavy;
            if (s.Task.Kind == TaskKind.Primary && s.Action is SquadAction.Attack or SquadAction.FlankLeft or SquadAction.FlankRight)
                return TrafficSteering.PriorityMainEffort;
            if (members.Count > 0 && artillery * 2 > members.Count) return TrafficSteering.PriorityArtilleryMove;
            if (s.Action == SquadAction.Join) return TrafficSteering.PriorityReinforcement;
            if (s.Fast) return TrafficSteering.PriorityScout;
            return TrafficSteering.PriorityCombat;
        }

        /// <summary>
        /// Plans an order's travel: the corridor, then the first passage on it within ai.traffic.approachM, its reservation
        /// and the packets. Plain orders (no plan) when the traffic layer is off, the squad is small, the goal near, or no
        /// corridor could be planned this step.
        /// </summary>
        private TrafficPlan PlanTraffic(SimWorld world, Squad s, Vector2 goal, CommandType type, List<Vehicle> members)
        {
            var plan = new TrafficPlan { Start = world.Time, Priority = SquadRightOfWay(s, members) };
            if (!SimTunables.Ai.Traffic.Enabled || members.Count == 0 || type is not (CommandType.Move or CommandType.AttackMove)) return plan;
            foreach (var v in members)
                if (v.Flying || v.Def.Naval != null) return plan;
            var team = _commander.Team;
            var owner = OwnerKey(s);
            var traffic = world.Traffic;
            if (members.Count < SimTunables.Ai.Traffic.CorridorMinMembers || Vector2.Distance(s.Centre, goal) < SimTunables.Ai.Traffic.CorridorMinDistance)
            {
                ReleasePassage(world, s);
                return plan;
            }
            var from = world.Grid.IsWalkable(s.Centre) ? s.Centre : members[0].Position;
            var corridor = traffic.Corridors.Get(team, owner, from, goal);
            if (corridor == null) return plan;
            plan.Corridor = corridor;
            var passage = traffic.FirstPassageAlong(from, corridor.Points, NearestIndex(corridor, from) + 1, SimTunables.Ai.Traffic.ApproachM, out _, out var dir);
            // (One the squad is already past the mouth of is no passage ahead.)
            if (passage != null && Vector2.Dot(from - passage.Centre, passage.Through * dir) > -passage.Length * 0.5f) passage = null;
            if (passage == null)
            {
                ReleasePassage(world, s);
                return plan;
            }
            float hullWidth = 0f, hullLength = 0f, speed = float.MaxValue;
            foreach (var v in members)
            {
                hullWidth += v.Def.HullRadius * 2f;
                hullLength += v.Def.HullHalf * 2f + v.Def.HullRadius * 2f;
                speed = MathF.Min(speed, v.Def.Speed * v.SpeedFactor);
            }
            hullWidth /= members.Count;
            hullLength /= members.Count;
            // Spec 188: overloaded (and not ours already): the way round when it is under 1.5 x the way through.
            var overloaded = !traffic.Holds(passage, team, owner) && traffic.Overloaded(passage, team, hullWidth, hullLength, speed);
            if (overloaded)
            {
                var round = traffic.Corridors.Get(team, owner, from, goal, avoid: passage);
                if (round != null)
                {
                    var next = traffic.FirstPassageAlong(round.Points[0], round.Points, 1, SimTunables.Ai.Traffic.ApproachM, out _, out var roundDir);
                    plan.Corridor = round;
                    if (next != passage)
                    {
                        world.Traffic.Log(team, s.Id, $"ROUTE_ALT_CONGESTION passage={passage.Id} arrivals={traffic.ArrivalsAt(passage, team)}");
                        if (next == null)
                        {
                            ReleasePassage(world, s);
                            return plan;
                        }
                        passage = next;
                        dir = roundDir;
                    }
                }
            }
            if (s.PassageId != 0 && s.PassageId != passage.Id) ReleasePassage(world, s);
            var grant = traffic.Request(passage, team, owner, dir, plan.Priority, members.Count, out var queueSlot);
            var lanes = passage.Lanes(hullWidth);
            plan.Passage = passage;
            plan.Direction = dir;
            plan.Queued = grant == PassageGrant.Queued;
            plan.QueueBase = queueSlot;
            // Spec 86 / 188: packets of the passage's lanes (two rows of them unless it is overloaded), 1-4 hulls.
            plan.PacketSize = Math.Clamp(lanes * (overloaded ? 1 : 2), 1, 4);
            var changed = s.PassageId != passage.Id || s.PassageQueued != plan.Queued;
            if (s.PassageId != passage.Id) s.PassageSince = world.Time;
            s.PassageId = passage.Id;
            s.PassageDir = dir;
            s.PassageQueued = plan.Queued;
            if (changed)
                world.Traffic.Log(team, s.Id, plan.Queued
                    ? $"JAM_CHOKE_QUEUE passage={passage.Id} {passage.Kind} way={dir} q={queueSlot + 1}"
                    : $"TRAFFIC_GRANT passage={passage.Id} {passage.Kind} way={dir} packets of {plan.PacketSize}");
            return plan;
        }

        /// <summary>Gives one member its slot: through the plan (a queue position, a later packet, the corridor) or a plain order.</summary>
        private void IssueSlot(SimWorld world, Squad s, Vehicle v, int index, Vector2 slot, CommandType type, in TrafficPlan plan)
        {
            var t = v.Traffic;
            var now = world.Time;
            t.SquadPriority = plan.Priority;
            t.TaskLabel = s.Action.ToString();
            t.InColumn = plan.Passage != null;
            // Stage 5 broke it out of formation a moment ago: it is left to get clear first.
            if (now < t.FormationBreakUntil) return;
            if (plan.Passage != null)
            {
                var gap = Math.Clamp(SimTunables.Ai.Traffic.ChokeBatchGapS, 2f, 4f);
                var release = plan.Queued ? double.PositiveInfinity : plan.Start + (index / Math.Max(1, plan.PacketSize)) * gap;
                if (release > now)
                {
                    var q = UnsharedSlot(world, v, QueueSpot(world, plan.Passage, plan.Direction, plan.QueueBase + index, v));
                    s.Packets[v.Id] = (release, slot, type);
                    world.Submit(new Command(CommandType.Move, _commander.Team, new[] { v.Id }, q));
                    return;
                }
            }
            s.Packets.Remove(v.Id);
            slot = UnsharedSlot(world, v, slot);
            var kind = type == CommandType.Move ? OrderKind.Move : OrderKind.AttackMove;
            if (plan.Corridor != null && world.IssueAlongCorridor(v, kind, slot, plan.Corridor)) return;
            world.Submit(new Command(type, _commander.Team, new[] { v.Id }, slot));
        }

        /// <summary>
        /// Spec 111 ("never share a slot"): squads of one side sent at one objective lay their formations over the same
        /// ground, and a squad's fallbacks (its goal, a queue spot) can match another's. A point another friendly ground hull
        /// is already ordered to (within 1 m) moves to the nearest free walkable point on rings 2.5 m apart (off no-parking
        /// cells), deterministically. Unchanged when it is free (or nothing free is near).
        /// </summary>
        private static Vector2 UnsharedSlot(SimWorld world, Vehicle v, Vector2 slot)
        {
            for (var ring = 0; ring <= 4; ring++)
            {
                var steps = ring == 0 ? 1 : ring * 8;
                for (var k = 0; k < steps; k++)
                {
                    var angle = k * MathF.PI * 2f / steps;
                    var p = slot + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (ring * 2.5f);
                    if (ring > 0 && (!world.Map.Contains(p) || !world.Grid.IsWalkable(p) || world.Lanes.NoParkAt(p))) continue;
                    if (!SlotTaken(world, v, p)) return p;
                }
            }
            return slot;
        }

        private static bool SlotTaken(SimWorld world, Vehicle v, Vector2 p)
        {
            foreach (var o in world.VehicleList)
            {
                if (o == v || !o.IsAlive || o.Team != v.Team || o.Flying || o.Def.Static) continue;
                if (o.Order.Kind is not (OrderKind.Move or OrderKind.AttackMove)) continue;
                if (Vector2.DistanceSquared(o.Order.Point, p) < 1f) return true;
            }
            return false;
        }

        /// <summary>Queue position Q(slot+1) before the passage, on open ground off doorways (else the nearest parkable spot).</summary>
        private static Vector2 QueueSpot(SimWorld world, Passage passage, int dir, int slot, Vehicle v)
        {
            var q = world.Map.Clamp(passage.QueuePoint(dir, slot), 4f);
            if (world.Grid.IsWalkable(q) && !world.Lanes.NoParkAt(q)) return q;
            if (world.Lanes.TryParkable(q, 12f, out var spot)) return spot;
            return world.Grid.TryNearestWalkable(q, 6, out var near) ? near : v.Position;
        }

        /// <summary>
        /// Each squad tick, before it thinks: a queued squad asks again (granted: its orders are issued anew, in packets);
        /// a granted one renews its hold and sends the packets whose turn came; once every member is through, the passage
        /// is released and the column ends (the formation at the goal was the requested one all along).
        /// </summary>
        private void TrafficTick(SimWorld world, Squad s)
        {
            if (s.PassageId == 0) return;
            var traffic = world.Traffic;
            var passage = traffic.PassageById(s.PassageId);
            var team = _commander.Team;
            var owner = OwnerKey(s);
            var now = world.Time;
            if (passage == null || s.MemberList.Count == 0)
            {
                s.PassageId = 0;
                s.PassageQueued = false;
                s.Packets.Clear();
                return;
            }
            var through = passage.Through * (s.PassageDir >= 0 ? 1f : -1f);
            var past = true;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                if (Vector2.Dot(v.Position - passage.Centre, through) < passage.Length * 0.5f + 6f)
                {
                    past = false;
                    break;
                }
            }
            if (past)
            {
                ReleasePassage(world, s);
                return;
            }
            var span = Interval * 2f + 0.5f;
            if (s.PassageQueued)
            {
                foreach (var id in s.MemberList) world.CombatWatch.Explain(id, CombatIdleReason.WaitingFormation, span);
                if (now - s.PassageSince > 30.0)
                {
                    // Waited long enough: plain orders (the vehicles' doorway turns and jam stages carry on).
                    world.Traffic.Log(team, s.Id, $"TRAFFIC_QUEUE_TIMEOUT passage={passage.Id}");
                    ReleasePassage(world, s);
                    s.IssuedGoal = new Vector2(float.NaN, float.NaN);
                    return;
                }
                if (traffic.Request(passage, team, owner, s.PassageDir, QueuedPriority(world, s), s.MemberList.Count, out _) ==
                    PassageGrant.Granted)
                {
                    s.PassageQueued = false;
                    s.Packets.Clear();
                    // The orders are issued anew: through the passage now, in packets.
                    s.IssuedGoal = new Vector2(float.NaN, float.NaN);
                    world.Traffic.Log(team, s.Id, $"TRAFFIC_GRANT passage={passage.Id} after {now - s.PassageSince:0.0}s");
                }
                return;
            }
            traffic.Request(passage, team, owner, s.PassageDir, QueuedPriority(world, s), s.MemberList.Count, out _);
            if (s.Packets.Count == 0) return;
            var corridor = traffic.Corridors.ById(CorridorOf(world, s));
            foreach (var id in s.MemberList)
            {
                if (!s.Packets.TryGetValue(id, out var packet)) continue;
                if (packet.at > now)
                {
                    world.CombatWatch.Explain(id, CombatIdleReason.WaitingFormation, span);
                    continue;
                }
                s.Packets.Remove(id);
                if (!world.TryGetVehicle(id, out var v)) continue;
                var kind = packet.type == CommandType.Move ? OrderKind.Move : OrderKind.AttackMove;
                var to = UnsharedSlot(world, v, packet.slot);
                if (corridor != null && world.IssueAlongCorridor(v, kind, to, corridor)) continue;
                world.Submit(new Command(packet.type, team, new[] { id }, to));
            }
        }

        private static int NearestIndex(SquadCorridor c, Vector2 p)
        {
            var best = 0;
            var bestD = float.MaxValue;
            for (var i = 0; i < c.Points.Count; i++)
            {
                var d = Vector2.DistanceSquared(c.Points[i], p);
                if (d >= bestD) continue;
                bestD = d;
                best = i;
            }
            return best;
        }

        /// <summary>The squad's right of way now (its members' kinds and its action).</summary>
        private int QueuedPriority(SimWorld world, Squad s)
        {
            var members = new List<Vehicle>(s.MemberList.Count);
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) members.Add(v);
            return SquadRightOfWay(s, members);
        }

        /// <summary>The corridor the squad's members follow (the first member on one), 0 for none.</summary>
        private static int CorridorOf(SimWorld world, Squad s)
        {
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && v.Traffic.CorridorId != 0) return v.Traffic.CorridorId;
            return 0;
        }

        private void ReleasePassage(SimWorld world, Squad s)
        {
            if (s.PassageId == 0) return;
            if (world.Traffic.PassageById(s.PassageId) is { } passage) world.Traffic.Release(passage, _commander.Team, OwnerKey(s));
            s.PassageId = 0;
            s.PassageQueued = false;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) v.Traffic.InColumn = false;
            // Members still waiting for their packet go now (plain orders to their slots).
            foreach (var id in s.MemberList)
            {
                if (!s.Packets.TryGetValue(id, out var packet)) continue;
                world.Submit(new Command(packet.type, _commander.Team, new[] { id }, packet.slot));
            }
            s.Packets.Clear();
        }

        /// <summary>Members the traffic plan or the jam stages are looking after: the squad's own unstick leaves them be.</summary>
        private static bool TrafficOwns(Squad s, Vehicle v) =>
            s.Packets.ContainsKey(v.Id) || s.PassageQueued ||
            (SimTunables.Ai.Navigation.JamStages && v.Traffic.Jam.Stage is > JamStage.None and < JamStage.Emergency);
    }
}
