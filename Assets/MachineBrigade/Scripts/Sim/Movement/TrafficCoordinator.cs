#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Bosses;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>What kind of narrow ground a passage is (spec 30).</summary>
    public enum PassageKind
    {
        Gate,
        Choke,
        Bridge,
        NarrowRoad,
    }

    /// <summary>
    /// One passage the TrafficCoordinator manages (spec 30): a gate or gap (the lane map's doorways), a choke of the map
    /// topology, a bridge (a choke over water) or a long narrow road. Stable ids in build order.
    /// </summary>
    public sealed class Passage
    {
        public int Id { get; internal set; }
        public PassageKind Kind { get; internal set; }
        public Vector2 Centre { get; internal set; }

        /// <summary>The way through (unit); direction +1 drives along it, -1 against it.</summary>
        public Vector2 Through { get; internal set; } = Vector2.UnitY;

        public float Width { get; internal set; }
        public float Length { get; internal set; }

        /// <summary>How far round the centre counts as in the passage (half its length, half its width, plus a hull).</summary>
        public float Reach => MathF.Max(Length, Width) * 0.5f + 3f;

        /// <summary>Hulls side by side through it (spec 189: usable width / average unit width).</summary>
        public int Lanes(float hullWidth) => Math.Max(1, (int)MathF.Floor(Width / MathF.Max(1f, hullWidth + 1f)));

        /// <summary>Spec 189: units a second through it, at the average speed and length of the units.</summary>
        public float Throughput(float hullWidth, float hullLength, float speed) =>
            Lanes(hullWidth) * MathF.Max(0.5f, speed) / MathF.Max(2f, hullLength + 4f);

        /// <summary>The way a move along <paramref name="dir"/> goes through it: +1, -1, or 0 (across).</summary>
        public int DirectionOf(Vector2 dir)
        {
            var along = Vector2.Dot(dir, Through);
            return along > 0.2f ? 1 : along < -0.2f ? -1 : 0;
        }

        public bool Contains(Vector2 p)
        {
            var d = p - Centre;
            var along = MathF.Abs(Vector2.Dot(d, Through));
            var across = MathF.Abs(Vector2.Dot(d, new Vector2(Through.Y, -Through.X)));
            return along <= Length * 0.5f + 1f && across <= Width * 0.5f + 1f;
        }

        /// <summary>
        /// Spec 85: queue position Q<paramref name="slot"/> (0 = Q1) before the passage for traffic going way
        /// <paramref name="dir"/>: back along the way in, two abreast off the centre line (packets wait beside the route).
        /// </summary>
        public Vector2 QueuePoint(int dir, int slot)
        {
            var back = -Through * (dir >= 0 ? 1f : -1f);
            var right = new Vector2(back.Y, -back.X);
            var row = slot / 2;
            var side = (slot & 1) == 0 ? 1f : -1f;
            var entry = Centre + back * (Length * 0.5f + SimTunables.Ai.Traffic.QueueStart);
            return entry + back * (row * SimTunables.Ai.Traffic.QueueSpacing) + right * side * (Width * 0.5f + 3f);
        }

        // Per side (0, 1, other): the reservation (spec 31) and its waiting list; predicted arrivals (spec 188).
        internal readonly PassageReservation?[] Holder = new PassageReservation?[TrafficCoordinator.Teams];
        internal readonly List<PassageReservation>[] Waiting =
            { new List<PassageReservation>(), new List<PassageReservation>(), new List<PassageReservation>() };
        internal readonly int[] LastDir = new int[TrafficCoordinator.Teams];
        internal readonly double[] OneWaySince = new double[TrafficCoordinator.Teams];
        internal readonly int[] Arrivals = new int[TrafficCoordinator.Teams];

        public override string ToString() => $"{Kind} {Id} at ({Centre.X:0},{Centre.Y:0}) w{Width:0.0} l{Length:0.0}";
    }

    /// <summary>Spec 31: who holds a passage, which way, since and until when, at which right of way.</summary>
    public sealed class PassageReservation
    {
        /// <summary>The owner key: a squad's (team * 65536 + squad id), or a vehicle's id negated.</summary>
        public int Owner;

        public double EnterTime;
        public double ExpireTime;
        public int Direction;
        public int Priority;

        /// <summary>The right of way is kept at least until then (spec 32: 2 s, so both sides never yield at once).</summary>
        public double PriorityHeldUntil;

        public int Members;

        /// <summary>Owners batched through behind it the same way (spec 31).</summary>
        internal readonly List<int> Riders = new();
    }

    /// <summary>A passage request's outcome.</summary>
    public enum PassageGrant
    {
        Granted,
        Queued,
    }

    /// <summary>Spec 40: a spawn's exit box (no parking, no firing spot), its clear zone and the rally ring outside it.</summary>
    public readonly struct SpawnExit
    {
        public SpawnExit(int team, Vector2 centre, Vector2 inward)
        {
            Team = team;
            Centre = centre;
            Inward = inward;
        }

        public int Team { get; }
        public Vector2 Centre { get; }
        public Vector2 Inward { get; }
        public float ExitRadius => SimTunables.Ai.Traffic.SpawnExitRadius;
        public float ClearRadius => SimTunables.Ai.Traffic.SpawnClearRadius;
        public float RallyRadius => SimTunables.Ai.Traffic.SpawnRallyRadius;
        public bool InExitBox(Vector2 p) => Vector2.DistanceSquared(p, Centre) < ExitRadius * ExitRadius;
        public bool InClearZone(Vector2 p) => Vector2.DistanceSquared(p, Centre) < ClearRadius * ClearRadius;

        /// <summary>Slot <paramref name="k"/> on the rally ring, fanning out from the inward bearing (0, +25, -25, +50 degrees...).</summary>
        public Vector2 RallySlot(int k)
        {
            var turn = ((k + 1) / 2) * ((k & 1) == 0 ? 1f : -1f) * SimMath.DegToRad(25f);
            return Centre + SimMath.Forward(SimMath.HeadingOf(Inward) + turn) * RallyRadius;
        }
    }

    /// <summary>
    /// Spec 33: where the friendly bosses reserve their way ahead. The default reads the P0-C boss brains
    /// (<see cref="BossBrains.Corridors"/>: half the boss's width + 2.5 m, 25-35 m ahead); a test or another provider may
    /// replace it (<see cref="TrafficCoordinator.BossCorridors"/>).
    /// </summary>
    public interface IBossCorridors
    {
        IReadOnlyList<BossCorridor> Corridors(SimWorld world);
    }

    internal sealed class BrainBossCorridors : IBossCorridors
    {
        public IReadOnlyList<BossCorridor> Corridors(SimWorld world) => world.Bosses.Brains.Corridors;
    }

    /// <summary>Spec 95: one vehicle's movement debug line.</summary>
    public readonly struct MovementDebug
    {
        public MovementDebug(Vector2 desired, Vector2 safe, Vector2 slot, int corridor, int priority, JamStage jam, EntityId blocker,
            Vector2 local, string task, string reason, int passage)
        {
            DesiredVelocity = desired;
            SafeVelocity = safe;
            FormationSlot = slot;
            SharedPathId = corridor;
            TrafficPriority = priority;
            JamStage = jam;
            BlockerId = blocker;
            LocalTarget = local;
            StrategicTask = task;
            Reason = reason;
            NextPassage = passage;
        }

        public Vector2 DesiredVelocity { get; }
        public Vector2 SafeVelocity { get; }
        public Vector2 FormationSlot { get; }
        public int SharedPathId { get; }
        public int TrafficPriority { get; }
        public JamStage JamStage { get; }
        public EntityId BlockerId { get; }
        public Vector2 LocalTarget { get; }
        public string StrategicTask { get; }
        public string Reason { get; }
        public int NextPassage { get; }

        public override string ToString() =>
            $"des({DesiredVelocity.X:0.0},{DesiredVelocity.Y:0.0}) safe({SafeVelocity.X:0.0},{SafeVelocity.Y:0.0}) slot({FormationSlot.X:0},{FormationSlot.Y:0}) " +
            $"path#{SharedPathId} pri{TrafficPriority} {JamStage} blk#{BlockerId.Value} local({LocalTarget.X:0},{LocalTarget.Y:0}) task {StrategicTask} {Reason}";
    }

    /// <summary>Counters the lead reads after a battle (Part K / V): every stage, fail-safe and traffic decision taken.</summary>
    public sealed class TrafficStats
    {
        /// <summary>SEVERE_UNSTUCK: relocations by the last fail-safe (put on open ground, hopped along the route).</summary>
        public int SevereUnstuck;
        public int SeverePlace, SevereHop;

        /// <summary>The fail-safe's non-relocating rung (drive through friends for a moment).</summary>
        public int GhostFailSafe;

        /// <summary>Jam stage actions taken, by stage (index = (int)JamStage).</summary>
        public readonly int[] JamActions = new int[6];

        public int EmergencyReverses, EmergencyAlternates, GiveUps;
        public int Deadlocks, WreckReplans, SpawnExitClears, CommandsDeduplicated, Anomalies;
        public int PassageGrants, PassageQueues, PassagePreempts, PassageAlternations;
        public int CorridorsBuilt, CorridorsReused, CorridorRoutes, CorridorAlternatives;
        public int ForcedYields;

        public override string ToString() =>
            $"severe {SevereUnstuck} (place {SeverePlace}, hop {SevereHop}), ghost {GhostFailSafe}, jam [{string.Join(",", JamActions)}], " +
            $"reverse {EmergencyReverses}, alt {EmergencyAlternates}, give-up {GiveUps}, deadlock {Deadlocks}, wreck {WreckReplans}, " +
            $"spawn {SpawnExitClears}, dedup {CommandsDeduplicated}, anomaly {Anomalies}, passage {PassageGrants}/{PassageQueues}/{PassagePreempts}, " +
            $"corridor {CorridorsBuilt}/{CorridorsReused}/{CorridorRoutes}";
    }

    /// <summary>
    /// AI MASTER spec 30-33, 40-41, 84-85, 188-189 (lane P1): the traffic subsystem above single vehicles. It knows the
    /// passages (gates, chokes, bridges, narrow roads), hands out passage reservations (same way batched, opposite ways
    /// taking turns, right of way held at least 2 s), the queue positions before them, predicted arrivals and throughput;
    /// the spawn exits (no parking in the exit box, parked friends cleared to the rally ring when the exit is blocked, the
    /// newly spawned' priority); the friendly bosses' corridors; the artillery parking rules; the dynamic path costs
    /// (congestion, boss corridors, booked firing spots) for routes planned round a jam; the shared squad corridors; the
    /// passing side per pair; and the counters. Ticks from the movement system (staggered, 1-2 Hz); deterministic (lists
    /// in build order, ties by id).
    /// </summary>
    public sealed class TrafficCoordinator
    {
        public const int Teams = 3;

        private readonly SimWorld _world;
        private readonly List<Passage> _passages = new();
        private readonly List<SpawnExit> _exits = new();
        private readonly double[] _exitBlockedSince;
        private readonly List<(int team, Vector2 at, float radius, double until)> _congestion = new();
        private readonly Dictionary<long, sbyte> _passing = new();
        private readonly List<long> _passingDrop = new();
        private int _lanesBuild = -1, _topologyGeneration = -1;
        private bool _built;

        internal TrafficCoordinator(SimWorld world)
        {
            _world = world;
            _exitBlockedSince = new double[8];
            Corridors = new SquadCorridors(world);
            for (var i = 0; i < _exitBlockedSince.Length; i++) _exitBlockedSince[i] = double.NaN;
        }

        public TrafficStats Stats { get; } = new();

        /// <summary>Spec 28-29: the shared squad corridors.</summary>
        public SquadCorridors Corridors { get; }

        /// <summary>Spec 33: the friendly bosses' corridors (P0-C's brains by default).</summary>
        public IBossCorridors BossCorridors { get; set; } = new BrainBossCorridors();

        public IReadOnlyList<Passage> Passages
        {
            get
            {
                EnsureBuilt();
                return _passages;
            }
        }

        public IReadOnlyList<SpawnExit> Exits => _exits;

        /// <summary>Congestion stamps still in force (stage 4), for the cost layer.</summary>
        internal int CongestionCount => _congestion.Count;

        internal static int TeamSlot(int team) => team >= 0 && team < Teams ? team : Teams - 1;

        // ------------------------------------------------------------------ the tick

        /// <summary>Runs at the start of each movement step; its parts are staggered over the second.</summary>
        internal void Step()
        {
            var tick = _world.Tick;
            if (tick % 20 == 0 || !_built) EnsureBuilt();
            if (tick % 10 == 3) ExpireReservations();
            if (tick % 10 == 5) RefreshExits();
            if (tick % 10 == 7) PredictArrivals();
            if (tick % 40 == 11) SweepPassing();
            if (tick % 20 == 13) ExpireCongestion();
            Corridors.Step();
        }

        private void EnsureBuilt()
        {
            var lanes = _world.Lanes;
            var topology = _world.Topology;
            if (_built && lanes.Builds == _lanesBuild && topology.Generation == _topologyGeneration) return;
            _built = true;
            _lanesBuild = lanes.Builds;
            _topologyGeneration = topology.Generation;
            // A rebuild keeps the reservations of passages that stay where they were (same centre within a cell).
            var old = new List<Passage>(_passages);
            _passages.Clear();
            BuildDoorways(lanes);
            BuildChokes(topology);
            for (var i = 0; i < _passages.Count; i++)
            {
                var p = _passages[i];
                p.Id = i + 1;
                foreach (var o in old)
                {
                    if (Vector2.DistanceSquared(o.Centre, p.Centre) > 4f) continue;
                    for (var t = 0; t < Teams; t++)
                    {
                        p.Holder[t] = o.Holder[t];
                        p.Waiting[t].AddRange(o.Waiting[t]);
                        p.LastDir[t] = o.LastDir[t];
                        p.OneWaySince[t] = o.OneWaySince[t];
                    }
                    break;
                }
            }
        }

        /// <summary>The lane map's doorways (gates, gaps): one passage each, measured from their cells.</summary>
        private void BuildDoorways(LaneMap lanes)
        {
            var grid = _world.Grid;
            var count = lanes.DoorwayCount;
            if (count == 0) return;
            var sum = new Vector2[count + 1];
            var cells = new int[count + 1];
            var road = new int[count + 1];
            for (var y = 0; y < grid.Height; y++)
            for (var x = 0; x < grid.Width; x++)
            {
                var f = lanes.FlagsOf(x, y);
                if ((f & LaneFlags.Narrow) == 0) continue;
                var c = grid.CellCenter(x, y);
                var id = lanes.DoorwayAt(c);
                if (id <= 0 || id > count) continue;
                sum[id] += c;
                cells[id]++;
                if ((f & LaneFlags.Road) != 0) road[id]++;
            }
            var lo = new float[count + 1];
            var hi = new float[count + 1];
            var wlo = new float[count + 1];
            var whi = new float[count + 1];
            for (var id = 1; id <= count; id++)
            {
                lo[id] = wlo[id] = float.MaxValue;
                hi[id] = whi[id] = float.MinValue;
            }
            for (var y = 0; y < grid.Height; y++)
            for (var x = 0; x < grid.Width; x++)
            {
                if ((lanes.FlagsOf(x, y) & LaneFlags.Narrow) == 0) continue;
                var c = grid.CellCenter(x, y);
                var id = lanes.DoorwayAt(c);
                if (id <= 0 || id > count || cells[id] == 0) continue;
                var through = lanes.DoorwayThrough(id);
                var across = new Vector2(through.Y, -through.X);
                var d = c - sum[id] / cells[id];
                var a = Vector2.Dot(d, through);
                var w = Vector2.Dot(d, across);
                lo[id] = MathF.Min(lo[id], a);
                hi[id] = MathF.Max(hi[id], a);
                wlo[id] = MathF.Min(wlo[id], w);
                whi[id] = MathF.Max(whi[id], w);
            }
            for (var id = 1; id <= count; id++)
            {
                if (cells[id] == 0) continue;
                var length = hi[id] - lo[id] + grid.CellSize;
                var width = whi[id] - wlo[id] + grid.CellSize;
                var kind = length > width * 3f && road[id] * 2 >= cells[id] ? PassageKind.NarrowRoad : PassageKind.Gate;
                _passages.Add(new Passage
                {
                    Kind = kind,
                    Centre = sum[id] / cells[id],
                    Through = lanes.DoorwayThrough(id),
                    Width = width,
                    Length = length,
                });
            }
        }

        /// <summary>The map topology's ground chokes not already a doorway; one over water (or beside it) is a bridge.</summary>
        private void BuildChokes(MapTopology topology)
        {
            var grid = _world.Grid;
            foreach (var choke in topology.Chokes)
            {
                var covered = false;
                foreach (var p in _passages)
                    if (Vector2.Distance(p.Centre, choke.Centre) < p.Reach + 4f)
                    {
                        covered = true;
                        break;
                    }
                if (covered) continue;
                // The narrowest of 8 bearings across it is "across"; the way through is square to it.
                var bestWidth = float.MaxValue;
                var across = Vector2.UnitX;
                for (var k = 0; k < 8; k++)
                {
                    var dir = SimMath.Forward(k * MathF.PI / 8f);
                    var width = Ray(grid, choke.Centre, dir, 30f) + Ray(grid, choke.Centre, -dir, 30f);
                    if (width >= bestWidth) continue;
                    bestWidth = width;
                    across = dir;
                }
                var through = new Vector2(-across.Y, across.X);
                var half = MathF.Max(choke.Width, bestWidth) * 0.5f + 3f;
                var water = topology.IsSea(choke.Centre + across * half) || topology.IsSea(choke.Centre - across * half) ||
                            grid.TerrainAt(choke.Centre + across * half) == TerrainTag.ShallowWater ||
                            grid.TerrainAt(choke.Centre - across * half) == TerrainTag.ShallowWater;
                var length = MathF.Max(6f, choke.Cells * topology.Cell * topology.Cell / MathF.Max(2f, choke.Width));
                _passages.Add(new Passage
                {
                    Kind = water ? PassageKind.Bridge : PassageKind.Choke,
                    Centre = choke.Centre,
                    Through = through,
                    Width = MathF.Max(2f, MathF.Min(choke.Width, bestWidth)),
                    Length = MathF.Min(length, 40f),
                });
            }
        }

        private static float Ray(NavGrid grid, Vector2 from, Vector2 dir, float max)
        {
            for (var d = 1f; d <= max; d += 1f)
                if (!grid.IsWalkable(from + dir * d)) return d;
            return max;
        }

        // ------------------------------------------------------------------ spec 31-32: reservations

        /// <summary>The first passage within <paramref name="reach"/> m along a route (from its point <paramref name="from"/>).</summary>
        public Passage? FirstPassageAlong(Vector2 start, IReadOnlyList<Vector2> route, int from, float reach, out float distance, out int direction)
        {
            EnsureBuilt();
            distance = 0f;
            direction = 0;
            var a = start;
            for (var i = Math.Max(0, from); i < route.Count && distance <= reach; i++)
            {
                var b = route[i];
                var length = Vector2.Distance(a, b);
                if (length > 1e-3f)
                {
                    var dir = (b - a) / length;
                    Passage? best = null;
                    var bestAlong = float.MaxValue;
                    foreach (var p in _passages)
                    {
                        var t = Math.Clamp(Vector2.Dot(p.Centre - a, dir), 0f, length);
                        if (Vector2.DistanceSquared(a + dir * t, p.Centre) > p.Reach * p.Reach * 0.5f || t >= bestAlong) continue;
                        if (p.DirectionOf(dir) == 0 && p.Kind != PassageKind.Choke) continue;
                        best = p;
                        bestAlong = t;
                    }
                    if (best != null)
                    {
                        distance += bestAlong;
                        direction = best.DirectionOf(dir);
                        if (direction == 0) direction = 1;
                        return distance <= reach ? best : null;
                    }
                }
                distance += length;
                a = b;
            }
            return null;
        }

        public Passage? PassageById(int id)
        {
            EnsureBuilt();
            return id > 0 && id <= _passages.Count ? _passages[id - 1] : null;
        }

        /// <summary>
        /// Spec 31-32: asks for passage <paramref name="passage"/> going way <paramref name="direction"/>. Free or expired:
        /// granted. Held by the same owner: renewed. Held the same way: batched behind it, unless the other way has waited
        /// past <c>ai.traffic.alternateSeconds</c> (then the turn goes over). Held the other way: queued, unless this right
        /// of way beats the holder's by <c>preemptMargin</c> after its 2 s hold. Ties between waiters: priority, then the
        /// earlier request, then the lower owner key.
        /// </summary>
        public PassageGrant Request(Passage passage, int team, int owner, int direction, int priority, int members, out int queueSlot)
        {
            var slot = TeamSlot(team);
            var now = _world.Time;
            var hold = SimTunables.Ai.Traffic.PriorityHoldS;
            var life = SimTunables.Ai.Traffic.ReservationSeconds + members * SimTunables.Ai.Traffic.ChokeBatchGapS;
            queueSlot = 0;
            var holder = passage.Holder[slot];
            if (holder != null && now >= holder.ExpireTime) holder = passage.Holder[slot] = Next(passage, slot, now);
            if (holder == null || holder.Owner == owner || holder.Riders.Contains(owner))
            {
                if (holder == null)
                {
                    RemoveWaiter(passage, slot, owner);
                    holder = passage.Holder[slot] = Grant(passage, slot, owner, direction, priority, members, now, life);
                    Stats.PassageGrants++;
                }
                else if (holder.Owner == owner && holder.Direction != direction)
                {
                    holder.Direction = direction;
                }
                holder.ExpireTime = Math.Max(holder.ExpireTime, now + life);
                return PassageGrant.Granted;
            }
            var opposite = passage.Waiting[slot].Exists(w => w.Direction != holder.Direction);
            if (holder.Direction == direction)
            {
                var turnOver = opposite && now - passage.OneWaySince[slot] > SimTunables.Ai.Traffic.AlternateSeconds;
                if (!turnOver)
                {
                    RemoveWaiter(passage, slot, owner);
                    holder.Riders.Add(owner);
                    holder.Members += members;
                    holder.ExpireTime = Math.Max(holder.ExpireTime, now + life);
                    Stats.PassageGrants++;
                    return PassageGrant.Granted;
                }
            }
            else if (priority >= holder.Priority + SimTunables.Ai.Traffic.PreemptMargin && now >= holder.PriorityHeldUntil)
            {
                RemoveWaiter(passage, slot, owner);
                passage.Holder[slot] = Grant(passage, slot, owner, direction, priority, members, now, life);
                Stats.PassagePreempts++;
                Log(team, owner > 0 ? owner & 0xFFFF : -owner, $"TRAFFIC_PREEMPT passage={passage.Id} from={holder.Owner} pri={priority}>{holder.Priority}");
                return PassageGrant.Granted;
            }
            var waiting = passage.Waiting[slot];
            var mine = waiting.Find(w => w.Owner == owner);
            if (mine == null)
            {
                waiting.Add(mine = new PassageReservation { Owner = owner, EnterTime = now });
                Stats.PassageQueues++;
            }
            mine.Direction = direction;
            mine.Priority = priority;
            mine.Members = members;
            mine.ExpireTime = now + life;
            foreach (var w in waiting)
                if (w != mine && w.Direction == direction && Before(w, mine)) queueSlot += Math.Max(1, w.Members);
            return PassageGrant.Queued;
        }

        /// <summary>Whether <paramref name="owner"/> holds or rides the passage now.</summary>
        public bool Holds(Passage passage, int team, int owner)
        {
            var h = passage.Holder[TeamSlot(team)];
            return h != null && _world.Time < h.ExpireTime && (h.Owner == owner || h.Riders.Contains(owner));
        }

        /// <summary>The owner is through (or gave up): its hold or ride and any wait end.</summary>
        public void Release(Passage passage, int team, int owner)
        {
            var slot = TeamSlot(team);
            RemoveWaiter(passage, slot, owner);
            var h = passage.Holder[slot];
            if (h == null) return;
            if (h.Riders.Remove(owner)) return;
            if (h.Owner != owner) return;
            if (h.Riders.Count > 0)
            {
                // The first rider carries the reservation on (same way, same expiry).
                h.Owner = h.Riders[0];
                h.Riders.RemoveAt(0);
                return;
            }
            passage.Holder[slot] = Next(passage, slot, _world.Time);
        }

        private static bool Before(PassageReservation a, PassageReservation b) =>
            a.Priority != b.Priority ? a.Priority > b.Priority : a.EnterTime != b.EnterTime ? a.EnterTime < b.EnterTime : a.Owner < b.Owner;

        private static void RemoveWaiter(Passage passage, int slot, int owner) => passage.Waiting[slot].RemoveAll(w => w.Owner == owner);

        private PassageReservation Grant(Passage passage, int slot, int owner, int direction, int priority, int members, double now, double life)
        {
            if (passage.LastDir[slot] != direction)
            {
                passage.OneWaySince[slot] = now;
                if (passage.LastDir[slot] != 0) Stats.PassageAlternations++;
            }
            passage.LastDir[slot] = direction;
            return new PassageReservation
            {
                Owner = owner,
                EnterTime = now,
                ExpireTime = now + life,
                Direction = direction,
                Priority = priority,
                PriorityHeldUntil = now + SimTunables.Ai.Traffic.PriorityHoldS,
                Members = members,
            };
        }

        /// <summary>The best waiter (the other way first when the last way held it: alternation), or nobody.</summary>
        private PassageReservation? Next(Passage passage, int slot, double now)
        {
            var waiting = passage.Waiting[slot];
            waiting.RemoveAll(w => now >= w.ExpireTime);
            PassageReservation? best = null;
            foreach (var w in waiting)
            {
                if (best == null) best = w;
                else
                {
                    var wOther = w.Direction != passage.LastDir[slot];
                    var bOther = best.Direction != passage.LastDir[slot];
                    if (wOther != bOther ? wOther : Before(w, best)) best = w;
                }
            }
            if (best == null) return null;
            waiting.Remove(best);
            Stats.PassageGrants++;
            return Grant(passage, slot, best.Owner, best.Direction, best.Priority, best.Members, now,
                SimTunables.Ai.Traffic.ReservationSeconds + best.Members * SimTunables.Ai.Traffic.ChokeBatchGapS);
        }

        private void ExpireReservations()
        {
            var now = _world.Time;
            foreach (var p in _passages)
                for (var t = 0; t < Teams; t++)
                {
                    var h = p.Holder[t];
                    if (h != null && now >= h.ExpireTime) p.Holder[t] = Next(p, t, now);
                    else if (h == null && p.Waiting[t].Count > 0) p.Holder[t] = Next(p, t, now);
                }
        }

        // ------------------------------------------------------------------ spec 188-189: predicted arrivals, throughput

        /// <summary>Ground vehicles of each side whose route reaches each passage within the prediction window.</summary>
        private void PredictArrivals()
        {
            foreach (var p in _passages) Array.Clear(p.Arrivals, 0, Teams);
            if (_passages.Count == 0) return;
            var window = SimTunables.Ai.Traffic.PredictWindowS;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Def.Static || v.Def.Naval != null || !v.HasPath) continue;
                var reach = MathF.Max(4f, v.Def.Speed * v.SpeedFactor * window);
                var p = FirstPassageAlong(v.Position, v.Path, v.PathIndex, reach, out _, out _);
                v.Traffic.NextPassage = p?.Id ?? 0;
                if (p != null) p.Arrivals[TeamSlot(v.Team)]++;
            }
        }

        /// <summary>Spec 188: more arrivals in the window than the passage passes in it.</summary>
        public bool Overloaded(Passage passage, int team, float hullWidth, float hullLength, float speed) =>
            passage.Arrivals[TeamSlot(team)] > passage.Throughput(hullWidth, hullLength, speed) * SimTunables.Ai.Traffic.PredictWindowS *
            SimTunables.Ai.Traffic.Overload;

        /// <summary>Spec 189: the wait for <paramref name="ahead"/> units before one through the passage (an ETA adds it).</summary>
        public static float QueueDelay(Passage passage, int ahead, float hullWidth, float hullLength, float speed) =>
            ahead / MathF.Max(0.05f, passage.Throughput(hullWidth, hullLength, speed));

        public int ArrivalsAt(Passage passage, int team) => passage.Arrivals[TeamSlot(team)];

        // ------------------------------------------------------------------ spec 32: right of way

        /// <summary>
        /// Spec 32: 100 boss or scripted convoy, 90 in the middle of a passage, 80 heavy, 75 just spawned (3 s), 70 the
        /// squad's main effort, 60 artillery moving, 50 normal, 40 reinforcement, 30 scout. Held at least 2 s.
        /// </summary>
        public int RightOfWay(Vehicle v)
        {
            if (v.Def.Boss || v.Scripted) return TrafficSteering.PriorityBoss;
            var t = v.Traffic;
            var now = _world.Time;
            if (now < t.RightOfWayUntil) return t.RightOfWay;
            var value = RawRightOfWay(v, now);
            t.RightOfWay = value;
            t.RightOfWayUntil = now + SimTunables.Ai.Traffic.PriorityHoldS;
            return value;
        }

        /// <summary>
        /// The right of way without the in-passage rank (90): between two hulls both in a passage (head-on in a gate) the
        /// heavier still keeps the road over the scout (spec 111). Not cached.
        /// </summary>
        public int BaseRightOfWay(Vehicle v) =>
            v.Def.Boss || v.Scripted ? TrafficSteering.PriorityBoss : RawRightOfWay(v, _world.Time, passage: false);

        private int RawRightOfWay(Vehicle v, double now, bool passage = true)
        {
            if (passage && v.HasPath && InPassage(v.Position)) return TrafficSteering.PriorityInChoke;
            if (v.Def.Class == UnitClass.Heavy) return TrafficSteering.PriorityHeavy;
            if (now - v.SpawnedAt < SimTunables.Ai.Traffic.SpawnPriorityS && InAnyExit(v.Team, v.Position, clear: true))
                return TrafficSteering.PriorityNewSpawn;
            var squad = v.Traffic.SquadPriority;
            if (squad >= TrafficSteering.PriorityMainEffort) return squad;
            if (v.HasPath && (v.Def.Class == UnitClass.Artillery || v.Def.Weapon.MinRange > 0f)) return TrafficSteering.PriorityArtilleryMove;
            if (v.Def.Class == UnitClass.Scout) return TrafficSteering.PriorityScout;
            if (squad > 0) return squad;
            return TrafficSteering.PriorityCombat;
        }

        public bool InPassage(Vector2 p)
        {
            foreach (var passage in _passages)
                if (passage.Contains(p)) return true;
            return false;
        }

        // ------------------------------------------------------------------ spec 36: passing side per pair

        /// <summary>The pair's passing side, fixed from first contact until they are 2 avoidance radii apart.</summary>
        public int PassingSide(Vehicle a, Vehicle b)
        {
            var key = PairKey(a.Id.Value, b.Id.Value);
            if (_passing.TryGetValue(key, out var side)) return side;
            side = (sbyte)TrafficSteering.PassingSide((int)a.Id.Value, (int)b.Id.Value);
            _passing[key] = side;
            return side;
        }

        private static long PairKey(long a, long b) => Math.Min(a, b) * 1_000_003L + Math.Max(a, b);

        private void SweepPassing()
        {
            if (_passing.Count == 0) return;
            _passingDrop.Clear();
            foreach (var key in _passing.Keys)
            {
                var a = key / 1_000_003L;
                var b = key % 1_000_003L;
                if (!_world.TryGetVehicle(new EntityId((int)a), out var va) || !_world.TryGetVehicle(new EntityId((int)b), out var vb) ||
                    !va.IsAlive || !vb.IsAlive ||
                    Vector2.Distance(va.Position, vb.Position) > SimTunables.Ai.Navigation.PassingRelease * (va.Def.HullBound + vb.Def.HullBound + 2f))
                    _passingDrop.Add(key);
            }
            foreach (var key in _passingDrop) _passing.Remove(key);
        }

        // ------------------------------------------------------------------ spec 40: spawn exits

        private void RefreshExits()
        {
            _exits.Clear();
            for (var team = 0; team <= 1; team++)
            {
                if (!_world.Bases.TryGetDropZone(team, out var zone)) continue;
                var inward = _world.TryGetRally(1 - team, out var enemy) && Vector2.DistanceSquared(enemy, zone) > 1f
                    ? Vector2.Normalize(enemy - zone)
                    : Vector2.UnitY;
                _exits.Add(new SpawnExit(team, zone, inward));
            }
            ClearBlockedExits();
        }

        /// <summary>Whether <paramref name="p"/> lies in a spawn exit box (or its clear zone) of <paramref name="team"/>.</summary>
        public bool InAnyExit(int team, Vector2 p, bool clear = false)
        {
            foreach (var e in _exits)
                if (e.Team == team && (clear ? e.InClearZone(p) : e.InExitBox(p))) return true;
            return false;
        }

        /// <summary>Spec 40: a rally or holding point is never in a spawn's exit box: one there moves out to the rally ring.</summary>
        public Vector2 OutOfExit(Vector2 p, int team)
        {
            if (!SimTunables.Ai.Traffic.Enabled) return p;
            foreach (var e in _exits)
            {
                if (e.Team != team || !e.InExitBox(p)) continue;
                var away = p - e.Centre;
                var dir = away.LengthSquared() > 0.25f ? Vector2.Normalize(away) : e.Inward;
                var q = _world.ClampToMap(e.Centre + dir * e.RallyRadius);
                return _world.Grid.IsWalkable(q) ? q : p;
            }
            return p;
        }

        /// <summary>
        /// Spec 40-41: a gun may park at <paramref name="p"/>: not in a spawn exit box, an artillery piece not on a main route
        /// nor within 1.5 x the splash spacing of another friendly gun's booked spot, and nobody in a friendly boss corridor.
        /// </summary>
        public bool CanPark(Vector2 p, Vehicle shooter)
        {
            if (!SimTunables.Ai.Traffic.Enabled) return true;
            if (InAnyExit(shooter.Team, p)) return false;
            foreach (var c in BossCorridors.Corridors(_world))
                if (c.Team == shooter.Team && c.Holds(p, shooter.Def.HullRadius)) return false;
            var artillery = shooter.Def.Class == UnitClass.Artillery || shooter.Def.Weapon.MinRange > 0f;
            if (!artillery) return true;
            if ((_world.Lanes.At(p) & LaneFlags.Route) != 0) return false;
            var spacing = SplashSpacing(shooter.Team) * SimTunables.Ai.Traffic.ParkingSplashSpacing;
            foreach (var o in _world.VehicleList)
            {
                if (o == shooter || !o.IsAlive || o.Team != shooter.Team || !o.Traffic.HasReservation || !LaneMap.InUse(o)) continue;
                if (o.Def.Class != UnitClass.Artillery && o.Def.Weapon.MinRange <= 0f) continue;
                if (Vector2.DistanceSquared(o.Traffic.ReservedAt, p) < spacing * spacing) return false;
            }
            return true;
        }

        /// <summary>The friendly splash spacing: the strongest known enemy blast (at least 6 m).</summary>
        private float SplashSpacing(int team)
        {
            return MathF.Max(6f, _world.Intel.Peek(team)?.EnemySplash ?? 0f);
        }

        /// <summary>A side's units should keep the wider splash spacing (spec 87).</summary>
        public bool SplashThreat(int team) =>
            (_world.Intel.Peek(team)?.EnemySplash ?? 0f) >= SimTunables.Ai.Navigation.SplashThreat;

        /// <summary>
        /// Spec 40: an exit with a hull on its way out crawling for 2 s is blocked; then the parked friends in the clear zone
        /// that did not just come in (they yield first) drive out to the rally ring.
        /// </summary>
        private void ClearBlockedExits()
        {
            var now = _world.Time;
            for (var i = 0; i < _exits.Count && i < _exitBlockedSince.Length; i++)
            {
                var e = _exits[i];
                var blocked = false;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != e.Team || v.Flying || v.Def.Static || v.Def.Naval != null || !v.HasPath) continue;
                    if (!e.InClearZone(v.Position)) continue;
                    if (MathF.Abs(v.Speed) < v.Def.Speed * v.SpeedFactor * SimTunables.Ai.Navigation.JamLowSpeedShare)
                    {
                        blocked = true;
                        break;
                    }
                }
                if (!blocked)
                {
                    _exitBlockedSince[i] = double.NaN;
                    continue;
                }
                if (double.IsNaN(_exitBlockedSince[i])) _exitBlockedSince[i] = now;
                if (now - _exitBlockedSince[i] < SimTunables.Ai.Traffic.SpawnBlockedS) continue;
                var k = 0;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != e.Team || v.Flying || v.Def.Static || v.Def.Naval != null || v.Def.Boss || v.Scripted) continue;
                    if (v.HasPath || v.PathQueued || v.Order.Kind != OrderKind.Idle || v.ManualOrder || v.Stunned) continue;
                    if (!e.InClearZone(v.Position) || now - v.SpawnedAt < SimTunables.Ai.Traffic.SpawnPriorityS) continue;
                    Vector2 spot = default;
                    var found = false;
                    for (var tries = 0; tries < 12 && !found; tries++, k++)
                    {
                        spot = _world.ClampToMap(e.RallySlot(k));
                        found = _world.Grid.IsWalkable(spot) && !_world.Lanes.NoParkAt(spot);
                    }
                    if (!found) continue;
                    v.GuardPoint = spot;
                    _world.PathTo(v, spot);
                    Stats.SpawnExitClears++;
                    Log(v.Team, (int)v.Id.Value, $"TRAFFIC_SPAWN_EXIT_CLEAR to=({spot.X:0},{spot.Y:0})", AiLayer.Unit);
                }
                _exitBlockedSince[i] = now;
            }
        }

        // ------------------------------------------------------------------ spec 84: dynamic path costs

        /// <summary>Stage 4: the jam's cells are dear for routes planned round it, for a while.</summary>
        public void AddCongestion(int team, Vector2 at)
        {
            _congestion.Add((TeamSlot(team), at, SimTunables.Ai.Navigation.CongestionRadius, _world.Time + SimTunables.Ai.Navigation.CongestionSeconds));
            Corridors.MarkDirtyNear(team, at, SimTunables.Ai.Navigation.CongestionRadius + 6f);
        }

        private void ExpireCongestion() => _congestion.RemoveAll(c => _world.Time >= c.until);

        /// <summary>
        /// Spec 84: stamps the dynamic costs into the per-side path cost layers (after the parked hulls and wrecks): the
        /// congestion of jams (stage 4), the friendly bosses' corridors (very high), the booked firing spots of the side's
        /// guns (high). Each cell keeps its dearest stamp, so the order does not matter. Static walls stay walls; the
        /// traffic lanes' low movement / high parking cost is the lane map's StandCost (kept).
        /// </summary>
        internal void StampCosts(byte[][] layers, NavGrid grid)
        {
            if (!SimTunables.Ai.Traffic.Enabled && _congestion.Count == 0) return;
            var now = _world.Time;
            foreach (var c in _congestion)
                if (now < c.until) Disc(grid, layers[c.team], c.at, c.radius, (byte)Math.Clamp(SimTunables.Ai.Navigation.CongestionCost, 0, 255));
            if (!SimTunables.Ai.Traffic.Enabled) return;
            var boss = (byte)Math.Clamp(SimTunables.Ai.Traffic.BossCorridorCost, 0, 255);
            foreach (var c in BossCorridors.Corridors(_world))
                Capsule(grid, layers[TeamSlot(c.Team)], c.From, c.To, c.HalfWidth, boss);
            var spot = (byte)Math.Clamp(SimTunables.Ai.Traffic.ReservedSpotCost, 0, 255);
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Traffic.HasReservation && LaneMap.InUse(v))
                    Disc(grid, layers[TeamSlot(v.Team)], v.Traffic.ReservedAt, grid.CellSize * 1.5f, spot);
        }

        private static void Disc(NavGrid grid, byte[] layer, Vector2 at, float radius, byte cost) => Capsule(grid, layer, at, at, radius, cost);

        private static void Capsule(NavGrid grid, byte[] layer, Vector2 a, Vector2 b, float radius, byte cost)
        {
            var min = Vector2.Min(a, b) - new Vector2(radius);
            var max = Vector2.Max(a, b) + new Vector2(radius);
            var (x0, y0) = grid.CellOf(min);
            var (x1, y1) = grid.CellOf(max);
            var ab = b - a;
            var length = ab.LengthSquared();
            for (var y = Math.Max(0, y0); y <= Math.Min(grid.Height - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(grid.Width - 1, x1); x++)
            {
                var c = grid.CellCenter(x, y);
                var t = length > 1e-6f ? Math.Clamp(Vector2.Dot(c - a, ab) / length, 0f, 1f) : 0f;
                if (Vector2.DistanceSquared(c, a + ab * t) > radius * radius) continue;
                var i = grid.Index(x, y);
                if (layer[i] < cost) layer[i] = cost;
            }
        }

        // ------------------------------------------------------------------ spec 95 / Part O: debug and log

        /// <summary>Spec 95: the movement debug fields of one vehicle (composed on demand; reading changes nothing).</summary>
        public MovementDebug DebugOf(Vehicle v)
        {
            var t = v.Traffic;
            var local = v.HasPath ? v.Path[v.PathIndex] : v.Position;
            var blocker = _world.Time - t.LastBlockerTime < 2.0 ? t.LastBlocker : EntityId.None;
            return new MovementDebug(t.DesiredVelocity, t.SafeVelocity, v.Order.Point, t.CorridorId, t.RightOfWay, t.Jam.Stage, blocker, local,
                t.TaskLabel.Length > 0 ? t.TaskLabel : v.Order.Kind.ToString(), t.Jam.Reason, t.NextPassage);
        }

        /// <summary>A Part O traffic line (TRAFFIC_*, JAM_*, ROUTE_*, SEVERE_UNSTUCK) in the replay log.</summary>
        internal void Log(int team, int subject, string text, AiLayer layer = AiLayer.Squad) =>
            _world.AiLog.Add(new DecisionEntry(_world.Time, team, layer, subject, DecisionKind.Traffic, text));
    }
}
