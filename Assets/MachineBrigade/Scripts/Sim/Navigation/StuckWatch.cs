#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Numerics;
using System.Text;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>Why a stuck vehicle is not getting anywhere, as the stuck report files it (prompt 12).</summary>
    public enum StuckCause
    {
        /// <summary>No progress, and none of the reasons below fits.</summary>
        Unknown,

        /// <summary>Its centre stands on blocked ground (a tower raised on it, a landing inside a footprint): it cannot drive off.</summary>
        Embedded,

        /// <summary>The route search found no way to its goal.</summary>
        NoPath,

        /// <summary>Its goal lies in ground that cannot be reached from where it stands (behind a closed gate, inside walls or a building).</summary>
        GoalUnreachable,

        /// <summary>The route it is driving crosses ground blocked since it was planned (a tower raised, a gate shut).</summary>
        StalePath,

        /// <summary>Waiting its turn at a doorway (a gate, a gap).</summary>
        GateWait,

        /// <summary>Waiting for a friend to make way, or queued behind one.</summary>
        YieldWait,

        /// <summary>Another vehicle of its own side is in the way.</summary>
        BlockedByFriend,

        /// <summary>A fixed defence (a tower, a bastion) is in the way.</summary>
        BlockedByDefence,

        /// <summary>An enemy vehicle is in the way.</summary>
        BlockedByEnemy,

        /// <summary>Pressed against a wall, a building or the map's edge.</summary>
        BlockedByObstacle,

        /// <summary>Its new route is still waiting for the path budget.</summary>
        PathQueued,

        /// <summary>Pushed or steered off its route into a corner: the straight line to its next waypoint runs into blocked ground.</summary>
        OffRoute,
    }

    /// <summary>One stuck vehicle: who, where, going where, why, what was round it, and how it ended.</summary>
    public sealed class StuckRecord
    {
        public int VehicleId;
        public string DefId = "";
        public int Team;
        public long StartTick;
        public double StartTime;
        public double EndTime = -1;

        /// <summary>Seconds it made no headway (from its last real move to the end of the episode, or the match).</summary>
        public double Seconds;

        public Vector2 Position;
        public Vector2 Goal;
        public string Order = "";
        public StuckCause Cause;
        public string Detail = "";

        /// <summary>Where it stood: "fortress", "camp", "field" (and "gate" when in a doorway or its mouth).</summary>
        public string Area = "";
        public string Lanes = "";
        public string Nearby = "";

        /// <summary>How it ended: moved, gave up (no goal any more), died, still stuck when the match ended.</summary>
        public string Outcome = "open";

        /// <summary>Safety-net activations during the episode (see MovementSystem.Rescue).</summary>
        public int Rescues;
        public string RescueKinds = "";

        public double Duration => Seconds;
    }

    /// <summary>
    /// The stuck detector (prompt 12): a ground vehicle that has somewhere to go (a route, a route
    /// waiting for its step, or a failed search for one) but has not moved more than
    /// <see cref="Tolerance"/> metres for <see cref="Threshold"/> seconds is written down, with the
    /// map, mode, seed, tick, side, vehicle, place, goal, why it is held up and what is round it.
    /// It only watches (it never changes the battle), so it can run in tests, the batch runs and
    /// the internal build alike; the report carries what it takes to play the battle again.
    /// </summary>
    public sealed class StuckWatch
    {
        /// <summary>Seconds without headway before a vehicle counts as stuck.</summary>
        public float Threshold = 8f;

        /// <summary>Moving this far from where it last got going counts as headway.</summary>
        public float Tolerance = 2.5f;

        /// <summary>A goal this close (plus the hull) is as good as reached: shuffling there is not being stuck.</summary>
        public float GoalReach = 6f;

        /// <summary>It looks every this many steps (0.5 s at 20 Hz).</summary>
        public int SampleTicks = 10;

        public readonly string Map, Mode, Config;
        public readonly int Seed;

        private readonly Dictionary<int, Track> _tracks = new();
        private readonly List<StuckRecord> _records = new();
        private readonly List<int> _gone = new();
        private int _rescuesSeen;

        public StuckWatch(string map, string mode, int seed, string config = "")
        {
            Map = map;
            Mode = mode;
            Seed = seed;
            Config = config;
        }

        public IReadOnlyList<StuckRecord> Records => _records;

        /// <summary>Every safety-net activation seen so far (tick, vehicle, def, side, kind, where).</summary>
        public List<string> Rescues { get; } = new();

        /// <summary>Episodes of at least <paramref name="seconds"/> without headway.</summary>
        public int CountOver(double seconds)
        {
            var n = 0;
            foreach (var r in _records)
                if (r.Seconds >= seconds) n++;
            return n;
        }

        /// <summary>
        /// Seconds without a goal that do not end an episode, when the stuck rules have just given
        /// up on the vehicle's route or found none: its commander sends it again a moment later, and
        /// it still gets nowhere.
        /// </summary>
        public float Grace = 6f;

        private sealed class Track
        {
            public Vector2 Anchor;
            public double Since;
            public StuckRecord? Open;
            public int RescuesAtOpen;
        }

        /// <summary>Call after each step of the battle.</summary>
        public void Observe(SimWorld world)
        {
            if (world.Tick % SampleTicks != 0) return;
            var now = world.Time;
            CollectRescues(world);
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Def.Static) continue;
                if (!_tracks.TryGetValue(v.Id.Value, out var t))
                {
                    _tracks[v.Id.Value] = new Track { Anchor = v.Position, Since = now };
                    continue;
                }
                var wants = Wants(world, v, out var goal);
                // Underground, landing troops or knocked out: something else holds it still.
                var held = v.Burrow != Vehicle.BurrowState.Surface || v.Landing || v.Stunned;
                // Given up on a moment ago (or no route found): still stuck, if nothing else sends it anywhere.
                var between = !wants && Between(world, v);
                if ((!wants && !between) || held || Vector2.Distance(v.Position, t.Anchor) > Tolerance)
                {
                    Close(t, v, now, !wants || held ? "gave up" : "moved");
                    t.Anchor = v.Position;
                    t.Since = now;
                    continue;
                }
                var still = now - t.Since;
                if (t.Open != null)
                {
                    t.Open.Seconds = still;
                    t.Open.Rescues = v.Traffic.Rescues - t.RescuesAtOpen;
                    continue;
                }
                if (still < Threshold || between) continue;
                t.Open = Describe(world, v, goal, t.Since);
                t.Open.Seconds = still;
                t.RescuesAtOpen = v.Traffic.Rescues;
                _records.Add(t.Open);
            }
            // The dead: an open episode ends with them.
            _gone.Clear();
            foreach (var (id, t) in _tracks)
                if (!world.TryGetVehicle(new EntityId(id), out var v) || !v.IsAlive)
                {
                    if (t.Open != null)
                    {
                        t.Open.Outcome = "died";
                        t.Open.EndTime = now;
                    }
                    _gone.Add(id);
                }
            foreach (var id in _gone) _tracks.Remove(id);
        }

        /// <summary>The battle is over: episodes still open stay "open" with their time so far.</summary>
        public void Finish(SimWorld world)
        {
            CollectRescues(world);
            foreach (var t in _tracks.Values)
                if (t.Open != null)
                {
                    t.Open.Seconds = world.Time - t.Open.StartTime;
                    t.Open.EndTime = world.Time;
                    t.Open = null;
                }
        }

        private void Close(Track t, Vehicle v, double now, string outcome)
        {
            if (t.Open == null) return;
            t.Open.Outcome = outcome;
            t.Open.EndTime = now;
            t.Open.Seconds = now - t.Open.StartTime;
            t.Open.Rescues = v.Traffic.Rescues - t.RescuesAtOpen;
            t.Open = null;
        }

        private void CollectRescues(SimWorld world)
        {
            var log = world.Movement.RescueLog;
            for (; _rescuesSeen < log.Count; _rescuesSeen++)
            {
                var r = log[_rescuesSeen];
                Rescues.Add(string.Format(CultureInfo.InvariantCulture, "{0},{1},{2},{3},{4},{5:0.0},{6:0.0},{7:0.0},{8:0.0}",
                    r.Tick, r.Vehicle, r.DefId, r.Team, r.Kind, r.From.X, r.From.Y, r.To.X, r.To.Y));
                foreach (var t in _tracks.Values)
                    if (t.Open != null && t.Open.VehicleId == r.Vehicle && !t.Open.RescueKinds.Contains(r.Kind))
                        t.Open.RescueKinds += (t.Open.RescueKinds.Length > 0 ? "+" : "") + r.Kind;
            }
        }

        /// <summary>Without a goal just now because the stuck rules gave up on it, or no route was found, within the last <see cref="Grace"/> seconds.</summary>
        private bool Between(SimWorld world, Vehicle v) =>
            world.Time - Math.Max(v.Traffic.GaveUpAt, v.Traffic.PathFailedAt) < Grace;

        /// <summary>Whether the vehicle has somewhere to go, and where.</summary>
        internal static bool Wants(SimWorld world, Vehicle v, out Vector2 goal)
        {
            goal = v.Position;
            if (v.PathQueued) goal = v.QueuedGoal;
            else if (v.HasPath) goal = v.PathGoal;
            else if (world.Time - v.Traffic.PathFailedAt < 1.5) goal = v.Traffic.PathFailedGoal;
            else return false;
            return Vector2.Distance(goal, v.Position) > MathF.Max(6f, v.Def.HullBound * 2f);
        }

        // ------------------------------------------------------------------ why it is stuck

        private StuckRecord Describe(SimWorld world, Vehicle v, Vector2 goal, double since)
        {
            var r = new StuckRecord
            {
                VehicleId = v.Id.Value, DefId = v.Def.Id, Team = v.Team, StartTick = world.Tick - (long)Math.Round((world.Time - since) / 0.05),
                StartTime = since, Position = v.Position, Goal = goal, Order = v.Order.Kind.ToString(),
            };
            (r.Cause, r.Detail) = Classify(world, v, goal);
            r.Lanes = LaneText(world.Lanes.At(v.Position));
            r.Area = AreaOf(world, v.Position) + ((world.Lanes.At(v.Position) & LaneFlags.NoPark) != 0 ? "+gate" : "");
            r.Nearby = NearbyText(world, v);
            return r;
        }

        internal (StuckCause cause, string detail) Classify(SimWorld world, Vehicle v, Vector2 goal)
        {
            var grid = world.Grid;
            var t = v.Traffic;
            if (!grid.IsWalkable(v.Position)) return (StuckCause.Embedded, "on " + BlockerAt(world, v.Position));
            var here = ComponentOf(world, v.Position);
            if (world.Time - t.PathFailedAt < 2.0)
                return (StuckCause.NoPath, $"goal {Fmt(t.PathFailedGoal)} in {GoalText(world, t.PathFailedGoal, here)}");
            if (!Reaches(world, goal, here)) return (StuckCause.GoalUnreachable, $"goal {Fmt(goal)} in {GoalText(world, goal, here)}");
            if (v.HasPath)
            {
                // The route as planned (waypoint to waypoint) crossing blocked ground: it was planned before something closed it.
                for (var i = v.PathIndex; i < v.Path.Count; i++)
                {
                    var a = i == v.PathIndex ? v.Path[i] : v.Path[i - 1];
                    if (!grid.IsWalkable(v.Path[i]) || (i > v.PathIndex && BlockedLine(world, a, v.Path[i])))
                        return (StuckCause.StalePath, $"leg {i - v.PathIndex + 1}/{v.Path.Count - v.PathIndex} to {Fmt(v.Path[i])} crosses {BlockerOnLine(world, a, v.Path[i])}");
                }
                // The way from where it stands to the next waypoint: off its line, into a corner.
                if (BlockedLine(world, v.Position, v.Path[v.PathIndex]))
                    return (StuckCause.OffRoute, $"to {Fmt(v.Path[v.PathIndex])} past {BlockerOnLine(world, v.Position, v.Path[v.PathIndex])}");
            }
            if (t.WaitingForGate || t.GateWaitId != 0) return (StuckCause.GateWait, $"doorway {world.Lanes.DoorwayAt(v.Position)}");
            if (t.WaitingOnYield || t.QueueBehind.IsValid)
                return (StuckCause.YieldWait, t.QueueBehind.IsValid && world.TryGetVehicle(t.QueueBehind, out var q) ? $"behind {q.Def.Id}#{q.Id.Value}" : "waiting on a yield");
            if (v.PathQueued) return (StuckCause.PathQueued, "");
            var ahead = Ahead(world, v);
            if (ahead != null)
            {
                var cause = ahead.Team != v.Team ? StuckCause.BlockedByEnemy : ahead.Def.Static ? StuckCause.BlockedByDefence : StuckCause.BlockedByFriend;
                return (cause, $"{ahead.Def.Id}#{ahead.Id.Value}{(ahead.HasPath ? " moving" : " parked")}");
            }
            var forward = SimMath.Forward(v.Heading);
            var probe = v.Position + forward * (v.Def.HullHalf + 1.5f);
            if (!grid.IsWalkable(probe) || !world.Map.Contains(probe)) return (StuckCause.BlockedByObstacle, BlockerAt(world, probe));
            return (StuckCause.Unknown, $"speed {v.Speed:0.0} strikes {v.StuckStrikes}");
        }

        /// <summary>The nearest hull in front of the vehicle, close enough to be what holds it up.</summary>
        private static Vehicle? Ahead(SimWorld world, Vehicle v)
        {
            var forward = SimMath.Forward(v.Heading);
            Vehicle? best = null;
            var bestD = float.MaxValue;
            foreach (var o in world.VehicleList)
            {
                if (o == v || !o.IsAlive || o.Flying || o.Burrowed) continue;
                var off = o.Position - v.Position;
                var d = off.Length();
                if (d > v.Def.HullBound + o.Def.HullBound + 1.5f || d >= bestD) continue;
                if (d > 0.01f && Vector2.Dot(off / d, forward) < 0.2f) continue;
                best = o;
                bestD = d;
            }
            return best;
        }

        private static int ComponentOf(SimWorld world, Vector2 p) => world.Grid.RegionOf(p);

        /// <summary>Whether a goal can be reached from region <paramref name="from"/>: open ground of it within 16 cells, as the route search resolves it.</summary>
        private static bool Reaches(SimWorld world, Vector2 goal, int from) =>
            from == 0 || world.Grid.TryNearestInRegion(goal, from, 16, out _);

        private static string GoalText(SimWorld world, Vector2 goal, int from)
        {
            var what = !world.Grid.IsWalkable(goal) ? "blocked ground (" + BlockerAt(world, goal) + ")" : "open ground";
            var region = world.Grid.RegionOf(goal);
            var reach = region == from ? "reachable" : region > 0 ? $"other region ({world.Grid.RegionSize(region)} cells)" :
                Reaches(world, goal, from) ? "reachable ground near" : "no reachable ground near";
            return $"{what}, {reach}, {AreaOf(world, goal)}";
        }

        // ------------------------------------------------------------------ text

        private static string AreaOf(SimWorld world, Vector2 p)
        {
            if (world.Map.Fortress is { } f && f.Contains(p)) return "fortress";
            foreach (var b in world.Bases.All)
                if (Vector2.Distance(b.HqPosition, p) < SimWorld.HomeRadius) return "camp" + b.Team;
            foreach (var team in world.Map.Teams)
                if (world.TryGetRally(team.Team, out var rally) && Vector2.Distance(rally, p) < SimWorld.HomeRadius) return "camp" + team.Team;
            return "field";
        }

        private static string LaneText(LaneFlags f)
        {
            if (f == LaneFlags.None) return "";
            var parts = new List<string>();
            if ((f & LaneFlags.Road) != 0) parts.Add("road");
            if ((f & LaneFlags.Route) != 0) parts.Add("route");
            if ((f & LaneFlags.Narrow) != 0) parts.Add("narrow");
            if ((f & LaneFlags.NoPark) != 0) parts.Add("nopark");
            return string.Join("+", parts);
        }

        /// <summary>What blocks the ground at <paramref name="p"/>: the prop or fixed defence whose footprint (with the clearance) covers it, else the outline.</summary>
        private static string BlockerAt(SimWorld world, Vector2 p)
        {
            var reach = SimWorld.ObstacleClearance + world.Grid.CellSize;
            foreach (var prop in world.Props)
                if (prop.IsAlive && prop.Def.BlocksMovement && MathF.Abs(prop.Position.X - p.X) <= prop.Width * 0.5f + reach &&
                    MathF.Abs(prop.Position.Y - p.Y) <= prop.Depth * 0.5f + reach) return prop.Def.Id;
            foreach (var o in world.VehicleList)
            {
                if (!o.IsAlive || !o.BlocksRoutes) continue;
                var half = MathF.Max(o.Def.Length, o.Def.Width) * 0.4f + reach;
                if (MathF.Abs(o.Position.X - p.X) <= half && MathF.Abs(o.Position.Y - p.Y) <= half) return o.Def.Id + "(defence)";
            }
            return world.Map.InsideBoundary(p) ? "?" : "outline";
        }

        /// <summary>Whether the centre line from a to b crosses a blocked cell (no side strips: the hull's own line).</summary>
        private static bool BlockedLine(SimWorld world, Vector2 a, Vector2 b)
        {
            var steps = Math.Max(1, (int)MathF.Ceiling(Vector2.Distance(a, b) / 0.5f));
            for (var i = 0; i <= steps; i++)
                if (!world.Grid.IsWalkable(Vector2.Lerp(a, b, i / (float)steps))) return true;
            return false;
        }

        private static string BlockerOnLine(SimWorld world, Vector2 a, Vector2 b)
        {
            var steps = Math.Max(1, (int)MathF.Ceiling(Vector2.Distance(a, b) / 0.5f));
            for (var i = 0; i <= steps; i++)
            {
                var p = Vector2.Lerp(a, b, i / (float)steps);
                if (!world.Grid.IsWalkable(p)) return BlockerAt(world, p);
            }
            var side = b - a;
            side = side.LengthSquared() > 1e-4f ? Vector2.Normalize(new Vector2(-side.Y, side.X)) * (world.Grid.CellSize * 0.25f) : Vector2.Zero;
            for (var i = 0; i <= steps; i++)
            {
                var p = Vector2.Lerp(a, b, i / (float)steps);
                if (!world.Grid.IsWalkable(p + side)) return BlockerAt(world, p + side) + " (corner)";
                if (!world.Grid.IsWalkable(p - side)) return BlockerAt(world, p - side) + " (corner)";
            }
            return "?";
        }

        private static string NearbyText(SimWorld world, Vehicle v)
        {
            var sb = new StringBuilder();
            foreach (var o in world.VehicleList)
            {
                if (o == v || !o.IsAlive || o.Flying) continue;
                var d = Vector2.Distance(o.Position, v.Position);
                if (d > 10f) continue;
                sb.Append(o.Def.Id).Append(o.Team == v.Team ? "" : "(foe)").Append(o.Def.Static ? "(fixed)" : o.HasPath ? "(moving)" : "(parked)")
                    .Append('@').Append(d.ToString("0.0", CultureInfo.InvariantCulture)).Append(' ');
            }
            foreach (var p in world.Props)
            {
                if (!p.IsAlive || !p.Def.BlocksMovement) continue;
                var d = Vector2.Distance(p.Position, v.Position);
                if (d > 10f) continue;
                sb.Append(p.Def.Id).Append('@').Append(d.ToString("0", CultureInfo.InvariantCulture)).Append(' ');
            }
            return sb.ToString().TrimEnd();
        }

        private static string Fmt(Vector2 p) => string.Format(CultureInfo.InvariantCulture, "({0:0.0},{1:0.0})", p.X, p.Y);

        // ------------------------------------------------------------------ the report

        /// <summary>CSV header of <see cref="CsvRows"/>.</summary>
        public const string CsvHeader =
            "map,mode,seed,config,vehicle,def,team,start_tick,start_s,end_s,seconds,x,y,goal_x,goal_y,order,cause,area,lanes,outcome,rescues,rescue_kinds,detail,nearby";

        /// <summary>One CSV row per record (commas inside texts become semicolons).</summary>
        public IEnumerable<string> CsvRows()
        {
            foreach (var r in _records)
                yield return string.Format(CultureInfo.InvariantCulture,
                    "{0},{1},{2},{3},{4},{5},{6},{7},{8:0.0},{9:0.0},{10:0.0},{11:0.0},{12:0.0},{13:0.0},{14:0.0},{15},{16},{17},{18},{19},{20},{21},{22},{23}",
                    Map, Mode, Seed, Config, r.VehicleId, r.DefId, r.Team, r.StartTick, r.StartTime, r.EndTime, r.Seconds, r.Position.X, r.Position.Y,
                    r.Goal.X, r.Goal.Y, r.Order, r.Cause, r.Area, r.Lanes, r.Outcome, r.Rescues, r.RescueKinds, Clean(r.Detail), Clean(r.Nearby));
        }

        private static string Clean(string s) => s.Replace(',', ';').Replace('\n', ' ');

        /// <summary>
        /// The report as JSON: how to play the battle again (map, mode, seed, configuration, data
        /// version and the player's commands from the journal), then every record and every
        /// safety-net activation.
        /// </summary>
        public string ToJson(SimWorld world, string? dataVersion = null)
        {
            var sb = new StringBuilder();
            sb.Append("{\n");
            sb.Append("  \"map\": ").Append(Str(Map)).Append(",\n");
            sb.Append("  \"mode\": ").Append(Str(Mode)).Append(",\n");
            sb.Append("  \"seed\": ").Append(Seed).Append(",\n");
            sb.Append("  \"config\": ").Append(Str(Config)).Append(",\n");
            sb.Append("  \"dataVersion\": ").Append(Str(dataVersion ?? "")).Append(",\n");
            sb.Append("  \"ticks\": ").Append(world.Tick).Append(",\n");
            sb.Append("  \"journal\": [");
            var first = true;
            foreach (var (tick, c) in world.Journal)
            {
                sb.Append(first ? "\n    " : ",\n    ");
                first = false;
                sb.Append("{\"tick\": ").Append(tick).Append(", \"type\": ").Append(Str(c.Type.ToString())).Append(", \"team\": ").Append(c.Team)
                    .Append(", \"units\": [").Append(string.Join(",", Ids(c.Units))).Append("]")
                    .Append(", \"x\": ").Append(F(c.Point.X)).Append(", \"y\": ").Append(F(c.Point.Y))
                    .Append(", \"target\": ").Append(c.Target.Value).Append(", \"def\": ").Append(Str(c.DefId ?? "")).Append('}');
            }
            sb.Append(first ? "],\n" : "\n  ],\n");
            sb.Append("  \"records\": [");
            first = true;
            foreach (var r in _records)
            {
                sb.Append(first ? "\n    " : ",\n    ");
                first = false;
                sb.Append("{\"vehicle\": ").Append(r.VehicleId).Append(", \"def\": ").Append(Str(r.DefId)).Append(", \"team\": ").Append(r.Team)
                    .Append(", \"startTick\": ").Append(r.StartTick).Append(", \"start\": ").Append(F(r.StartTime)).Append(", \"end\": ").Append(F(r.EndTime))
                    .Append(", \"seconds\": ").Append(F(r.Seconds)).Append(", \"x\": ").Append(F(r.Position.X)).Append(", \"y\": ").Append(F(r.Position.Y))
                    .Append(", \"goalX\": ").Append(F(r.Goal.X)).Append(", \"goalY\": ").Append(F(r.Goal.Y)).Append(", \"order\": ").Append(Str(r.Order))
                    .Append(", \"cause\": ").Append(Str(r.Cause.ToString())).Append(", \"detail\": ").Append(Str(r.Detail)).Append(", \"area\": ").Append(Str(r.Area))
                    .Append(", \"lanes\": ").Append(Str(r.Lanes)).Append(", \"outcome\": ").Append(Str(r.Outcome)).Append(", \"rescues\": ").Append(r.Rescues)
                    .Append(", \"rescueKinds\": ").Append(Str(r.RescueKinds)).Append(", \"nearby\": ").Append(Str(r.Nearby)).Append('}');
            }
            sb.Append(first ? "],\n" : "\n  ],\n");
            sb.Append("  \"rescues\": [");
            first = true;
            foreach (var line in Rescues)
            {
                sb.Append(first ? "\n    " : ",\n    ");
                first = false;
                sb.Append(Str(line));
            }
            sb.Append(first ? "]\n" : "\n  ]\n");
            sb.Append("}\n");
            return sb.ToString();
        }

        private static IEnumerable<int> Ids(IReadOnlyList<EntityId> ids)
        {
            foreach (var id in ids) yield return id.Value;
        }

        private static string F(double x) => x.ToString("0.###", CultureInfo.InvariantCulture);

        private static string Str(string s)
        {
            var sb = new StringBuilder("\"");
            foreach (var ch in s)
            {
                if (ch == '"' || ch == '\\') sb.Append('\\').Append(ch);
                else if (ch < ' ') sb.Append(' ');
                else sb.Append(ch);
            }
            return sb.Append('"').ToString();
        }
    }
}
