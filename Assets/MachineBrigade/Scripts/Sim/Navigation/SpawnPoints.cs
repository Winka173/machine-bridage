#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>Whose reinforcements come in at a spawn point (prompt 23 B).</summary>
    public enum SpawnSide
    {
        Enemy,
        Ally,
    }

    /// <summary>
    /// How reinforcements come in at a spawn point: over a map edge, at a rail head, off the water, at a landing zone, dropped
    /// from a transport's flight path; the allies' behind the player's area, at the drop zone, at an outpost.
    /// </summary>
    public enum SpawnKind
    {
        Edge,
        Rail,
        Sea,
        Landing,
        Air,
        Behind,
        Drop,
        Outpost,
    }

    /// <summary>Which way a spawn point lies from the player, along the line from the player's camp to the enemy's.</summary>
    public enum SpawnBearing
    {
        Front,
        Left,
        Right,
        Rear,
    }

    /// <summary>One place reinforcements come in, with the spots beside it in the same direction (B.3's fallbacks).</summary>
    public sealed class SpawnPoint
    {
        public string Id { get; internal set; } = "";
        public SpawnSide Side { get; internal set; }
        public SpawnKind Kind { get; internal set; }
        public SpawnBearing Bearing { get; internal set; }
        public Vector2 Position { get; internal set; }

        /// <summary>The way into the battle from it (a unit vector).</summary>
        public Vector2 Inward { get; internal set; }

        /// <summary>An air path's entry over the edge (a transport flies from here to <see cref="Position"/>); the point itself otherwise.</summary>
        public Vector2 From { get; internal set; }

        /// <summary>Spots beside it, in the same direction, for when the player's units stand at it.</summary>
        public IReadOnlyList<Vector2> Alternates { get; internal set; } = Array.Empty<Vector2>();

        /// <summary>
        /// Prompt 33 L2: its entry gate (the ingress contract): the map's gate it was moved onto, else one made where it stands.
        /// Every point has one; what comes in here exists from its entry tick at the gate (MissionEventSystem.Deliver).
        /// </summary>
        public EntryGate Gate { get; internal set; } = null!;
    }

    /// <summary>
    /// Prompt 23 B: every battlefield's spawn points, worked out from the map as the battle begins (so every variant, a
    /// reversed map and the long battlefields have them) and topped by the map's own "spawns" when it lists any. Enemy points:
    /// the map's edges in every direction (on open ground joined to the battlefield), the rail heads, the water's landing
    /// points, the enemy's landing zones and the transports' drop points on their flight paths. Allied points: behind the
    /// player's area, the drop zone, the player's side's objectives. A point is never used while a player's vehicle is
    /// within <see cref="EventRules.NearSight"/>: another in the same direction is taken instead.
    /// </summary>
    public sealed class SpawnPoints
    {
        /// <summary>How far in from the map's square an edge point may stand.</summary>
        private const float EdgeMargin = 7f;

        /// <summary>An enemy point is at least this far from the player's camp (the rear flank never lands in the base).</summary>
        public const float CampClearance = 95f;

        private readonly List<SpawnPoint> _all = new();

        public IReadOnlyList<SpawnPoint> All => _all;

        /// <summary>The player's camp and the axis to the enemy's (the bearings are measured from it).</summary>
        public Vector2 Home { get; private set; }

        public Vector2 Axis { get; private set; } = Vector2.UnitY;

        public IEnumerable<SpawnPoint> Of(SpawnSide side)
        {
            foreach (var p in _all)
                if (p.Side == side) yield return p;
        }

        /// <summary>The bearings a side has points on, front first.</summary>
        public List<SpawnBearing> Bearings(SpawnSide side)
        {
            var list = new List<SpawnBearing>();
            foreach (SpawnBearing b in Enum.GetValues(typeof(SpawnBearing)))
                foreach (var p in _all)
                    if (p.Side == side && p.Bearing == b && p.Kind != SpawnKind.Landing)
                    {
                        list.Add(b);
                        break;
                    }
            return list;
        }

        /// <summary>The bearing of a spot on the map (for a notice's direction).</summary>
        public SpawnBearing BearingOf(Vector2 at, Vector2 centre)
        {
            var v = at - centre;
            if (v.LengthSquared() < 1f) return SpawnBearing.Front;
            var angle = MathF.Atan2(Axis.X * v.Y - Axis.Y * v.X, Vector2.Dot(Axis, v)) * 180f / MathF.PI;
            return MathF.Abs(angle) <= 45f ? SpawnBearing.Front : angle > 45f && angle <= 135f ? SpawnBearing.Left
                : angle < -45f && angle >= -135f ? SpawnBearing.Right : SpawnBearing.Rear;
        }

        public static SpawnPoints Build(SimWorld world, int player = 0, int enemy = 1)
        {
            var sp = new SpawnPoints();
            var map = world.Map;
            var centre = map.Centre;
            var home = world.TryGetRally(player, out var h) ? h : map.Min;
            if (world.Bases.Of(player) is { } ours) home = ours.HqPosition;
            var camp = world.TryGetRally(enemy, out var c) ? c : map.Max;
            if (world.Bases.Of(enemy) is { } theirs) camp = theirs.HqPosition;
            var axis = camp - home;
            axis = axis.LengthSquared() > 1f ? Vector2.Normalize(axis) : Vector2.UnitY;
            sp.Home = home;
            sp.Axis = axis;
            var main = world.Grid.MainRegion;

            // The map's own points first.
            foreach (var d in map.Spawns)
                if (Snap(world, d.Position, main, out var at))
                    sp.Add(world, d.Side == 0 ? SpawnSide.Ally : SpawnSide.Enemy, d.Kind, at, d.From ?? at, centre, home);

            // The edges, every 22.5 degrees round the axis.
            var edges = new List<Vector2>();
            for (var k = 0; k < 16; k++)
            {
                var dir = Rotate(axis, k * MathF.PI / 8f);
                if (!EdgePoint(world, centre, dir, main, out var at)) continue;
                var near = false;
                foreach (var e in edges)
                    if (Vector2.DistanceSquared(e, at) < global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.BuildScale * global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.BuildScale) near = true;
                if (near) continue;
                edges.Add(at);
                if (Vector2.Distance(at, home) >= CampClearance) sp.Add(world, SpawnSide.Enemy, SpawnKind.Edge, at, at, centre, home);
                else if (Vector2.Dot(at - home, axis) < 25f) sp.Add(world, SpawnSide.Ally, SpawnKind.Behind, at, at, centre, home);
            }

            // Rail heads: where a line comes in at the edge (the enemy's end).
            if (map.Route("rail") is { Count: >= 2 } rail)
                foreach (var end in new[] { rail[0], rail[rail.Count - 1] })
                    if (Vector2.Distance(end, home) >= CampClearance && Snap(world, map.Clamp(end, EdgeMargin), main, out var at))
                        sp.Add(world, SpawnSide.Enemy, SpawnKind.Rail, at, at, centre, home);
            if (map.Fortress?.Arrival is { } arrival && arrival.Path.Count > 0)
            {
                Vector2? first = null;
                foreach (var p in arrival.Path)
                    if (map.Contains(p) && map.EdgeDistance(p) >= EdgeMargin)
                    {
                        first = p;
                        break;
                    }
                var kind = arrival.Kind == ArrivalKind.Rail ? SpawnKind.Rail : SpawnKind.Landing;
                var head = kind == SpawnKind.Rail ? first : arrival.Stop;
                if (head is { } point && Vector2.Distance(point, home) >= CampClearance && Snap(world, point, main, out var at))
                    sp.Add(world, SpawnSide.Enemy, kind, at, at, centre, home);
            }

            // The water: a sea's landing beaches, else where water reaches the edge (boats come down it).
            if (map.Sea is { } sea)
                foreach (var l in sea.Landings)
                    if (Vector2.Distance(l.Inland, home) >= CampClearance && Snap(world, l.Inland, main, out var at))
                        sp.Add(world, SpawnSide.Enemy, SpawnKind.Sea, at, l.At, centre, home);
            WaterLandings(world, sp, centre, home, main);

            // Landing zones: the enemy's drop zone and its forward drops, its side's objectives.
            if (Snap(world, camp, main, out var zone)) sp.Add(world, SpawnSide.Enemy, SpawnKind.Landing, zone, zone, centre, home);
            if (map.Fortress is { } fortress)
                foreach (var p in fortress.ForwardDrops)
                    if (Snap(world, p, main, out var at)) sp.Add(world, SpawnSide.Enemy, SpawnKind.Landing, at, at, centre, home);
            foreach (var p in map.Points)
            {
                var ourSide = Vector2.Distance(p.Position, home) < Vector2.Distance(p.Position, camp);
                if (!Snap(world, p.Position, main, out var at)) continue;
                sp.Add(world, ourSide ? SpawnSide.Ally : SpawnSide.Enemy, ourSide ? SpawnKind.Outpost : SpawnKind.Landing, at, at, centre, home);
            }

            // The transports' flight paths: in over an edge on the front and both flanks, the drop a little over halfway in.
            foreach (var e in edges)
            {
                var bearing = sp.BearingOf(e, centre);
                if (bearing == SpawnBearing.Rear || Vector2.Distance(e, home) < CampClearance) continue;
                if (Snap(world, Vector2.Lerp(centre, e, global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.BuildCentreLerp), main, out var drop) && Vector2.Distance(drop, home) >= CampClearance * global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.BuildCampClearanceScale)
                    sp.Add(world, SpawnSide.Enemy, SpawnKind.Air, drop, e, centre, home);
            }

            // Behind the player's area, and the drop zone.
            var back = home - axis * 22f;
            var across = new Vector2(-axis.Y, axis.X);
            foreach (var off in new[] { 0f, global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.BuildOff2, global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.BuildOff3 })
                if (Snap(world, back + across * off, main, out var at)) sp.Add(world, SpawnSide.Ally, SpawnKind.Behind, at, at, centre, home);
            var dropZone = world.Bases.TryGetDropZone(player, out var dz) ? dz : world.TryGetRally(player, out var r) ? r : home;
            if (Snap(world, dropZone, main, out var dropAt)) sp.Add(world, SpawnSide.Ally, SpawnKind.Drop, dropAt, dropAt, centre, home);
            return sp;
        }

        private void Add(SimWorld world, SpawnSide side, SpawnKind kind, Vector2 at, Vector2 from, Vector2 centre, Vector2 home)
        {
            // Prompt 33 L2: a point that comes in over the edge (or off the water) stands on the map's entry gate near it.
            var gate = GateFor(world, side, kind, at, home);
            if (gate != null) at = gate.Position;
            foreach (var p in _all)
                if (p.Side == side && p.Kind == kind && Vector2.DistanceSquared(p.Position, at) < global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddScale * global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddScale) return;
            var inward = centre - at;
            if (side == SpawnSide.Ally && kind is SpawnKind.Behind or SpawnKind.Drop) inward = Axis;
            inward = inward.LengthSquared() > 1f ? Vector2.Normalize(inward) : Axis;
            if (gate != null) inward = gate.Inward;
            if (gate == null)
            {
                // A drop's or an air path's way in is the flight's (from its entry over the edge), else the point's own.
                var way = inward;
                if ((kind == SpawnKind.Air || kind == SpawnKind.Landing) && (at - from).LengthSquared() > 1f) way = Vector2.Normalize(at - from);
                gate = EntryGate.At(world.Map, $"auto.{_all.Count}", GateKindOf(kind), at, way);
            }
            var across = new Vector2(-inward.Y, inward.X);
            var alternates = new List<Vector2>();
            var main = world.Grid.MainRegion;
            foreach (var off in new[] { global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddOff1, global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddOff2, global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddOff3, global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddOff4 })
                if (Snap(world, at + across * off, main, out var alt) && Vector2.DistanceSquared(alt, at) > global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddDistanceSquaredMin &&
                    (side == SpawnSide.Ally || Vector2.Distance(alt, home) >= CampClearance * global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.AddCampClearanceScale))
                    alternates.Add(alt);
            _all.Add(new SpawnPoint
            {
                Id = $"{side.ToString().ToLowerInvariant()}.{kind.ToString().ToLowerInvariant()}.{_all.Count}",
                Side = side, Kind = kind, Bearing = BearingOf(at, centre), Position = at, Inward = inward, From = from, Alternates = alternates,
                Gate = gate,
            });
        }

        /// <summary>How near a spawn point a gate of the map's data must be to take it (metres).</summary>
        public static float GateReach => global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.GateReach;

        /// <summary>
        /// Prompt 33 L2: the map's entry gate a point at the edge (an edge point, a rail head, the allies' behind their area within
        /// 14 m of the edge, a point on the water) moves onto: the nearest that takes its kind within <see cref="GateReach"/>, on
        /// the battlefield's ground and, for the enemy's, still clear of the player's camp. Null: the point keeps its place and
        /// gets a gate made there.
        /// </summary>
        private static EntryGate? GateFor(SimWorld world, SpawnSide side, SpawnKind kind, Vector2 at, Vector2 home)
        {
            var map = world.Map;
            if (map.EntryGates.Count == 0) return null;
            var edgeKind = kind is SpawnKind.Edge or SpawnKind.Rail || kind == SpawnKind.Behind && map.EdgeDistance(at) <= global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.GateForEdgeDistanceMax;
            if (!edgeKind && kind != SpawnKind.Sea) return null;
            var gate = EntryGate.Nearest(map.EntryGates, at, GateReach, kind);
            // On the battlefield's ground (a road gate stands on its road, where nobody parks: it is driven through).
            if (gate == null || !world.Grid.IsWalkable(gate.Position) || world.Grid.RegionOf(gate.Position) != world.Grid.MainRegion) return null;
            if (side == SpawnSide.Enemy && Vector2.Distance(gate.Position, home) < CampClearance * global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.GateForCampClearanceScale) return null;
            return gate;
        }

        private static EntryGateKind GateKindOf(SpawnKind kind) => kind switch
        {
            SpawnKind.Rail => EntryGateKind.Rail,
            SpawnKind.Sea => EntryGateKind.Sea,
            SpawnKind.Air or SpawnKind.Landing or SpawnKind.Drop => EntryGateKind.Air,
            _ => EntryGateKind.Edge,
        };

        /// <summary>
        /// B.3: where a wave of <paramref name="point"/> comes in: the point, else a spot beside it, else another point of the
        /// same side and direction, none within <paramref name="clearance"/> of a vehicle of <paramref name="watcher"/>. False
        /// when every one has the player's units on it (the event waits and tries again).
        /// </summary>
        public bool TryPlace(SimWorld world, SpawnPoint point, float clearance, int watcher, out Vector2 at)
        {
            if (Clear(world, point.Position, clearance, watcher))
            {
                at = point.Position;
                return true;
            }
            foreach (var alt in point.Alternates)
                if (Clear(world, alt, clearance, watcher))
                {
                    at = alt;
                    return true;
                }
            foreach (var other in _all)
            {
                if (other == point || other.Side != point.Side || other.Bearing != point.Bearing) continue;
                if (Clear(world, other.Position, clearance, watcher))
                {
                    at = other.Position;
                    return true;
                }
                foreach (var alt in other.Alternates)
                    if (Clear(world, alt, clearance, watcher))
                    {
                        at = alt;
                        return true;
                    }
            }
            at = point.Position;
            return false;
        }

        /// <summary>No vehicle of <paramref name="watcher"/>'s side (its allies' too) within <paramref name="clearance"/>.</summary>
        public static bool Clear(SimWorld world, Vector2 at, float clearance, int watcher)
        {
            if (clearance <= 0f) return true;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == watcher && Vector2.DistanceSquared(v.Position, at) < clearance * clearance) return false;
            return true;
        }

        private static Vector2 Rotate(Vector2 v, float a) => new(v.X * MathF.Cos(a) - v.Y * MathF.Sin(a), v.X * MathF.Sin(a) + v.Y * MathF.Cos(a));

        /// <summary>The open ground nearest the map's edge along a direction from the centre, joined to the battlefield.</summary>
        private static bool EdgePoint(SimWorld world, Vector2 centre, Vector2 dir, int main, out Vector2 at)
        {
            var map = world.Map;
            var tx = MathF.Abs(dir.X) > 1e-4f ? ((dir.X > 0 ? map.Max.X : map.Min.X) - centre.X) / dir.X : float.MaxValue;
            var ty = MathF.Abs(dir.Y) > 1e-4f ? ((dir.Y > 0 ? map.Max.Y : map.Min.Y) - centre.Y) / dir.Y : float.MaxValue;
            var t = MathF.Min(tx, ty) - EdgeMargin;
            for (; t > 30f; t -= 3f)
            {
                var p = centre + dir * t;
                if (map.Contains(p) && map.EdgeDistance(p) >= EdgeMargin - global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.EdgePointEdgeMarginSub && Open(world, p, main))
                {
                    at = p;
                    return true;
                }
            }
            at = default;
            return false;
        }

        private static bool Open(SimWorld world, Vector2 p, int main) =>
            world.Grid.IsWalkable(p) && world.Grid.RegionOf(p) == main && !world.Lanes.NoParkAt(p);

        /// <summary>The open ground of the battlefield nearest a spot (within about 16 m), or false.</summary>
        internal static bool Snap(SimWorld world, Vector2 p, int main, out Vector2 at)
        {
            p = world.Map.Clamp(p, EdgeMargin * global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.SnapEdgeMarginScale);
            if (Open(world, p, main))
            {
                at = p;
                return true;
            }
            if (world.Grid.TryNearestInRegion(p, main, 8, out at) && world.Map.Contains(at)) return true;
            at = default;
            return false;
        }

        /// <summary>Where water (a river's or the sea's props) meets the map's edge away from the player: boats land their vehicles there.</summary>
        private static void WaterLandings(SimWorld world, SpawnPoints sp, Vector2 centre, Vector2 home, int main)
        {
            var clusters = new List<(Vector2 sum, int n)>();
            foreach (var prop in world.PropList)
            {
                if (!prop.Def.Id.Contains("water") || world.Map.EdgeDistance(prop.Position) > global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.WaterLandingsEdgeDistanceMin || Vector2.Distance(prop.Position, home) < CampClearance + global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.WaterLandingsCampClearanceAdd) continue;
                var joined = false;
                for (var i = 0; i < clusters.Count; i++)
                {
                    var (sum, n) = clusters[i];
                    if (Vector2.Distance(sum / n, prop.Position) > global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.WaterLandingsDistanceMin) continue;
                    clusters[i] = (sum + prop.Position, n + 1);
                    joined = true;
                    break;
                }
                if (!joined) clusters.Add((prop.Position, 1));
            }
            clusters.Sort((a, b) => b.n.CompareTo(a.n));
            for (var i = 0; i < clusters.Count && i < global::MachineBrigade.Sim.Content.SimTunables.Maps.SpawnPoints.WaterLandingsIMax; i++)
            {
                var water = clusters[i].sum / clusters[i].n;
                var inland = centre - water;
                if (inland.LengthSquared() < 1f) continue;
                inland = Vector2.Normalize(inland);
                for (var d = 8f; d <= 40f; d += 4f)
                    if (Open(world, water + inland * d, main))
                    {
                        sp.Add(world, SpawnSide.Enemy, SpawnKind.Sea, water + inland * d, water, centre, home);
                        break;
                    }
            }
        }
    }
}
