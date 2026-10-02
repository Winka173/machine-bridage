#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Prompt 33 L4 (DECISIONS "Prompt 33 L4"): the big ships' traffic on the sea routes (<see cref="SeaRouteGraph"/>) and the
    /// escorts' slots. A big ship (a naval hull <see cref="BigShipLength"/> m or longer: boss ships, escorts, big transports;
    /// attack boats and landing craft keep to the lanes as before) holds its lane segment and the next one. Each step, after
    /// the ships' own goals and before they sail:
    /// <list type="bullet">
    /// <item>The gap: a ship never closes on a big ship in its way (ahead of it along the coast, their hulls overlapping across
    /// it) inside half its length + half the other's + <see cref="GapExtra"/> m: its speed is capped to the other's speed along
    /// its way plus <see cref="CloseRate"/> per metre of room left, so it slows, then waits. Nothing is ever pushed.</item>
    /// <item>Priority (fixed): the boss's run, then a boss or key ship, a scripted transport, an escort, then the lower entity
    /// id. Two ships holding the same segment head-on: the lower one pulls into the nearest free holding node at once; a ship
    /// held up for more than <see cref="HoldAfterTicks"/> ticks: the lower of it and the ship in its way does. Whoever is in
    /// the way of a boss on its run (Leviathan's last phase) does at once, its own escorts apart. A holding ship comes back
    /// out once the other has gone past and is clear.</item>
    /// <item>Escort slots: PORT_FORWARD, STARBOARD_FORWARD, PORT_REAR, STARBOARD_REAR in the boss's frame, kept as a place in
    /// the coast's frame (so a boss turning about at the end of its patrol leaves them where they are: a port-forward slot
    /// becomes starboard-rear). Each escort's slot comes from the fleet data (its "at" and "abeam"), its centre within the
    /// leash (28 m, escortRules) of the boss's hull, clear of the slots taken before it by the minimum gap (slid along away
    /// from them if needed), on the water and on the routes over the boss's whole patrol; else the next in a fixed order (the
    /// other end on the same side, the same end on the other side, both), then the same four a row further out. Resolved as
    /// the fleet sails out and again when the boss changes lane; an escort that changes side goes round astern of it.</item>
    /// </list>
    /// </summary>
    internal sealed partial class NavalSystem
    {
        /// <summary>A naval hull this long or longer is a big ship: it sails the route graph's traffic rules.</summary>
        internal const float BigShipLength = 25f;

        /// <summary>The minimum gap's extra: half this ship's length + half the other's + 10 m.</summary>
        internal const float GapExtra = 10f;

        /// <summary>Within this much of the minimum gap a ship starts to slow.</summary>
        internal const float SlowBand = 20f;

        /// <summary>Two hulls this far apart across the coast (beyond their half widths) never meet.</summary>
        internal const float LateralMargin = 1.5f;

        /// <summary>m/s of closing speed allowed per metre of room left inside the slowing band.</summary>
        internal const float CloseRate = 0.25f;

        /// <summary>Held up (stopped) this many ticks (3 s): the lower of the two pulls into a holding node.</summary>
        internal const int HoldAfterTicks = 60;

        /// <summary>A ship stays in its holding node at least this many ticks (2 s).</summary>
        internal const int HoldMinTicks = 40;

        /// <summary>Slack added to the minimum gap when a slot is slid clear of another.</summary>
        internal const float SlotSlack = 4f;

        /// <summary>The boss's patrol is sampled every this many metres to check a slot.</summary>
        internal const float SlotSample = 8f;

        private SeaRouteGraph? _routes;
        private bool _routesBuilt;
        private readonly List<Vehicle> _big = new();
        private readonly List<Vehicle> _fleet = new();
        private readonly List<(Vector2 at, VehicleDef def)> _taken = new();

        /// <summary>Escort slots that found no valid place (the data's own was kept): the tests read it.</summary>
        internal int SlotProblems { get; private set; }

        /// <summary>The big ships' route graph (the map's, else built from its sea lanes); null without a sea.</summary>
        internal SeaRouteGraph? Routes
        {
            get
            {
                if (_routesBuilt) return _routes;
                _routesBuilt = true;
                if (Sea is not { } sea) return null;
                _routes = _world.Map.SeaRoutes ?? SeaRouteGraph.FromSea(sea, _world.Map.HalfSize);
                _routes.Bind(sea);
                return _routes;
            }
        }

        /// <summary>The big ships of the last step, in priority order (the tests read them).</summary>
        internal IReadOnlyList<Vehicle> BigShips => _big;

        internal static bool IsBig(Vehicle v) => v.Def.Naval != null && v.Def.Length >= BigShipLength;

        /// <summary>The fixed priority: 0 the boss's run, 1 a boss or key ship, 2 a scripted transport, 3 an escort, 4 any other.</summary>
        internal static int Rank(Vehicle v)
        {
            if (v.Escaping) return 0;
            var role = v.Def.Naval?.Role;
            if (role == NavalRole.Flagship || v.Def.Boss) return 1;
            if (role == NavalRole.Lander) return 2;
            return role == NavalRole.Escort ? 3 : 4;
        }

        /// <summary>Whether <paramref name="a"/> goes before <paramref name="b"/>: the higher priority, then the lower entity id.</summary>
        internal static bool Before(Vehicle a, Vehicle b)
        {
            var ra = Rank(a);
            var rb = Rank(b);
            return ra != rb ? ra < rb : a.Id.Value < b.Id.Value;
        }

        private static int ByPriority(Vehicle a, Vehicle b) => a == b ? 0 : Before(a, b) ? -1 : 1;

        /// <summary>Which way along the coast a ship is sailing: +1, -1, or 0 (across it).</summary>
        private static int TravelDir(Vehicle v, SeaDef sea)
        {
            var d = Vector2.Dot(SimMath.Forward(v.Heading), sea.Along);
            return d > 0.3f ? 1 : d < -0.3f ? -1 : 0;
        }

        /// <summary>Whether <paramref name="b"/> is in <paramref name="a"/>'s way: ahead along the coast, their hulls overlapping across it.</summary>
        private static bool InWay(Vehicle a, Vehicle b, SeaDef sea, out float along, out float minGap)
        {
            minGap = (a.Def.Length + b.Def.Length) * 0.5f + GapExtra;
            along = 0f;
            var dir = TravelDir(a, sea);
            if (dir == 0) return false;
            var fa = sea.Frame(a.Position);
            var fb = sea.Frame(b.Position);
            along = (fb.X - fa.X) * dir;
            if (along <= 0f) return false;
            return MathF.Abs(fb.Y - fa.Y) < (a.Def.Width + b.Def.Width) * 0.5f + LateralMargin;
        }

        private static bool Reserved(Vehicle a, Vehicle b) =>
            (a.SeaSegment >= 0 && (a.SeaSegment == b.SeaSegment || a.SeaSegment == b.SeaNextSegment)) ||
            (a.SeaNextSegment >= 0 && (a.SeaNextSegment == b.SeaSegment || a.SeaNextSegment == b.SeaNextSegment));

        /// <summary>The traffic rules, after the ships' own goals and before they sail (see the class summary).</summary>
        private void RouteTraffic(SeaDef sea)
        {
            _big.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Def.Naval == null) continue;
                v.SeaCap = float.PositiveInfinity;
                if (v.Escaped || !IsBig(v) || v.Burrow != Vehicle.BurrowState.Surface)
                {
                    v.SeaSegment = v.SeaNextSegment = -1;
                    v.SeaHold = -1;
                    continue;
                }
                _big.Add(v);
            }
            var routes = Routes;
            if (_big.Count == 0 || routes == null) return;
            _big.Sort(ByPriority);
            foreach (var v in _big)
            {
                v.SeaSegment = routes.NearestTrack(v.Position, out _, out _);
                var dir = TravelDir(v, sea);
                v.SeaNextSegment = dir == 0 ? -1 : routes.NextAlong(v.SeaSegment, dir);
            }
            for (var i = 0; i < _big.Count; i++)
            {
                var a = _big[i];
                Vehicle? blocker = null;
                var dirA = TravelDir(a, sea);
                foreach (var b in _big)
                {
                    if (b == a) continue;
                    if (InWay(a, b, sea, out var along, out var minGap))
                    {
                        var room = along - minGap;
                        if (room < SlowBand)
                        {
                            var lead = Vector2.Dot(SimMath.Forward(b.Heading) * b.Speed, sea.Along * dirA);
                            var cap = MathF.Max(0f, lead + room * CloseRate);
                            if (cap < a.SeaCap)
                            {
                                a.SeaCap = cap;
                                blocker = b;
                            }
                        }
                        // A segment both hold, head-on: the lower of the two gives way at once.
                        if (a.SeaHold < 0 && Reserved(a, b) && TravelDir(b, sea) == -dirA && Before(b, a)) StartHold(a, b, sea);
                    }
                    // The boss's run: whoever is in its way (but its own fleet) pulls in at once.
                    if (b.Escaping && a.Flagship != b.Id && a.SeaHold < 0 && InWay(b, a, sea, out var runAlong, out var runGap) &&
                        runAlong < runGap + 3f * SlowBand)
                        StartHold(a, b, sea);
                }
                a.SeaWait = blocker != null && a.SeaCap < 0.05f && MathF.Abs(a.Speed) < 0.1f ? a.SeaWait + 1 : 0;
                if (blocker != null && a.SeaWait > HoldAfterTicks)
                {
                    var yielder = Before(a, blocker) ? blocker : a;
                    var cause = yielder == a ? blocker : a;
                    if (yielder.SeaHold < 0 && StartHold(yielder, cause, sea)) a.SeaWait = 0;
                }
            }
            // The holding ships: to their node, and out again once the way is clear.
            foreach (var v in _big)
            {
                if (v.SeaHold < 0) continue;
                if (v.SeaHold >= routes.Nodes.Count)
                {
                    v.SeaHold = -1;
                    continue;
                }
                var gone = !_world.TryGetVehicle(v.SeaHoldFor, out var cause) || !cause.IsAlive || cause.Escaped;
                if (gone || (_world.Tick - v.SeaHoldSince >= HoldMinTicks && Clear(v, cause!, sea)))
                {
                    v.SeaHold = -1;
                    continue;
                }
                v.NavalGoal = routes.Nodes[v.SeaHold].Frame;
            }
        }

        /// <summary>Whether a holding ship may come out: the ship it gave way to is past it, or clear and not coming its way.</summary>
        private static bool Clear(Vehicle v, Vehicle cause, SeaDef sea)
        {
            var gap = (v.Def.Length + cause.Def.Length) * 0.5f + GapExtra + SlowBand;
            if (Vector2.Distance(v.Position, cause.Position) <= gap) return false;
            var coming = Vector2.Dot(SimMath.Forward(cause.Heading) * cause.Speed, v.Position - cause.Position);
            return coming <= 0f || MathF.Abs(sea.Frame(v.Position).Y - sea.Frame(cause.Position).Y) >= (v.Def.Width + cause.Def.Width) * 0.5f + LateralMargin;
        }

        /// <summary>
        /// Sends <paramref name="v"/> to the nearest free holding node off <paramref name="cause"/>'s line (none taken by
        /// another ship, no big ship inside the minimum gap of it). False when there is none (it keeps waiting).
        /// </summary>
        private bool StartHold(Vehicle v, Vehicle cause, SeaDef sea)
        {
            var routes = Routes;
            if (routes == null) return false;
            var best = -1;
            var bestDistance = float.MaxValue;
            var line = sea.Frame(cause.Position).Y;
            foreach (var n in routes.Nodes)
            {
                if (n.Kind != SeaNodeKind.Holding) continue;
                if (MathF.Abs(n.Frame.Y - line) < (v.Def.Width + cause.Def.Width) * 0.5f + LateralMargin + 2f) continue;
                var free = true;
                foreach (var o in _big)
                {
                    if (o == v) continue;
                    if (o.SeaHold == n.Index || Vector2.Distance(o.Position, n.Position) < (v.Def.Length + o.Def.Length) * 0.5f + GapExtra) free = false;
                }
                if (!free) continue;
                var d = Vector2.Distance(v.Position, n.Position);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = n.Index;
            }
            if (best < 0) return false;
            v.SeaHold = best;
            v.SeaHoldFor = cause.Id;
            v.SeaHoldSince = _world.Tick;
            v.SeaWait = 0;
            v.NavalGoal = routes.Nodes[best].Frame;
            Holds++;
            return true;
        }

        /// <summary>Holding nodes taken so far (the tests read it).</summary>
        internal int Holds { get; private set; }

        // ================================================================== escort slots

        private static readonly (float along, float across)[] SlotOrder = { (1f, 1f), (-1f, 1f), (1f, -1f), (-1f, -1f) };

        /// <summary>The slot's name for a place beside the boss (coast frame) as it sails <paramref name="dir"/> along the coast.</summary>
        internal static string SlotName(Vector2 at, int dir)
        {
            var forward = at.X * dir > 0f;
            // Port is the left of its heading: inshore (-w) sailing +u, out to sea sailing -u.
            var port = at.Y * dir < 0f;
            return (port ? "PORT_" : "STARBOARD_") + (forward ? "FORWARD" : "REAR");
        }

        /// <summary>How far a place beside the boss (coast frame, from its middle) is from its hull: what the leash measures.</summary>
        internal static float HullDistance(VehicleDef boss, Vector2 at)
        {
            var dx = MathF.Max(0f, MathF.Abs(at.X) - boss.Length * 0.5f);
            var dy = MathF.Max(0f, MathF.Abs(at.Y) - boss.Width * 0.5f);
            return MathF.Sqrt(dx * dx + dy * dy);
        }

        private float Leash => _world.Catalog.EscortRules.Leash > 0f ? _world.Catalog.EscortRules.Leash : 28f;

        /// <summary>
        /// An escort's slot beside <paramref name="flag"/> on lane <paramref name="laneId"/>: <paramref name="preferred"/> (the
        /// fleet data's place) if it is good, else the fixed fallbacks (see the class summary), clear of <paramref name="taken"/>.
        /// </summary>
        private Vector2 ResolveSlot(Vehicle flag, VehicleDef escort, Vector2 preferred, List<(Vector2 at, VehicleDef def)> taken, string? laneId)
        {
            var sea = Sea!;
            var lane = sea.Lane(laneId);
            var boss = flag.Def;
            var minAcross = (boss.Width + escort.Width) * 0.5f + LateralMargin + 1f;
            var along0 = MathF.Abs(preferred.X);
            var across0 = MathF.Max(MathF.Abs(preferred.Y), minAcross);
            var sx = preferred.X >= 0f ? 1f : -1f;
            // No side in the data: inshore (the shore side, as the fleet kept station before).
            var sy = preferred.Y > 0f ? 1f : -1f;
            for (var row = 0; row < 2; row++)
            {
                var across = row == 0 ? across0 : across0 + 12f;
                foreach (var (ma, mc) in SlotOrder)
                {
                    var at = new Vector2(sx * ma * along0, sy * mc * across);
                    if (!Place(boss, escort, ref at, taken, Leash)) continue;
                    if (!SlotValid(escort, at, lane, sea)) continue;
                    return at;
                }
            }
            SlotProblems++;
            return new Vector2(sx * along0, sy * across0);
        }

        /// <summary>Slides a slot along, away from the slots taken before it, until it keeps the minimum gap; false if it then leaves the leash.</summary>
        private static bool Place(VehicleDef boss, VehicleDef escort, ref Vector2 at, List<(Vector2 at, VehicleDef def)> taken, float leash)
        {
            for (var pass = 0; pass < 4; pass++)
            {
                var moved = false;
                foreach (var (o, od) in taken)
                {
                    if (MathF.Abs(o.Y - at.Y) >= (escort.Width + od.Width) * 0.5f + LateralMargin) continue;
                    var gap = (escort.Length + od.Length) * 0.5f + GapExtra;
                    if (MathF.Abs(o.X - at.X) >= gap) continue;
                    var away = at.X > o.X || (MathF.Abs(at.X - o.X) < 1e-3f && at.X >= 0f) ? 1f : -1f;
                    at.X = o.X + away * (gap + SlotSlack);
                    moved = true;
                }
                if (!moved) break;
            }
            foreach (var (o, od) in taken)
                if (MathF.Abs(o.Y - at.Y) < (escort.Width + od.Width) * 0.5f + LateralMargin && MathF.Abs(o.X - at.X) < (escort.Length + od.Length) * 0.5f + GapExtra)
                    return false;
            return HullDistance(boss, at) <= leash;
        }

        /// <summary>
        /// Whether a slot is good over the boss's whole patrol on its lane: on the water clear of the shore, on the routes
        /// (within the graph's corridor), and inside the map while the boss is in the middle of its patrol (near the ends an
        /// escort is kept inside the square, as every ship is).
        /// </summary>
        private bool SlotValid(VehicleDef escort, Vector2 at, SeaLaneDef? lane, SeaDef sea)
        {
            if (lane == null) return true;
            var routes = Routes;
            var limit = _world.Map.HalfSize - 2f;
            var middle = sea.At(at.X, lane.W + at.Y);
            if (MathF.Abs(middle.X) > limit || MathF.Abs(middle.Y) > limit) return false;
            var margin = escort.Width * 0.5f + 2f;
            for (var u = -lane.Patrol; u <= lane.Patrol + 0.01f; u += SlotSample)
            {
                var p = sea.At(u + at.X, lane.W + at.Y);
                if (!sea.IsSea(p, margin)) return false;
                if (routes != null && !routes.InCorridor(p)) return false;
            }
            return true;
        }

        /// <summary>The flagship changed lane: its escorts' slots again, in entity-id order; one that changes side goes round astern.</summary>
        private void ResolveFleet(Vehicle flag)
        {
            flag.SlotLane = flag.NavalLane;
            _fleet.Clear();
            foreach (var o in _world.VehicleList)
                if (o.IsAlive && o.Flagship == flag.Id && o.OnStation && o.Def.Naval?.Role == NavalRole.Escort) _fleet.Add(o);
            _fleet.Sort((a, b) => a.Id.Value.CompareTo(b.Id.Value));
            _taken.Clear();
            foreach (var e in _fleet)
            {
                var at = ResolveSlot(flag, e.Def, e.StationAt, _taken, flag.NavalLane);
                if (MathF.Sign(at.Y) != MathF.Sign(e.StationAt.Y)) e.SlotVia = true;
                e.StationAt = at;
                _taken.Add((at, e.Def));
            }
        }

        /// <summary>A flagship this near the end of its patrol ahead of it is about to come about (its escorts stand out).</summary>
        internal const float TurnWarn = 45f;

        /// <summary>
        /// Whether a flagship is coming about (or about to, near the end of its patrol, or changing lane): not yet lined up
        /// with the way it is going. It turns where it is, its bow and stern sweeping a circle of half its length, so its
        /// escorts stand out beyond that circle on their own side until it is lined up again (the leash is kept on the
        /// slot, not in the turn).
        /// </summary>
        private static bool Turning(Vehicle flag, SeaDef sea, Vector2 ff)
        {
            var lane = sea.Lane(flag.NavalLane);
            if (lane == null) return false;
            var aligned = Vector2.Dot(SimMath.Forward(flag.Heading), sea.Along * flag.NavalDir) >= 0.97f;
            var toEnd = (flag.NavalDir * lane.Patrol - ff.X) * flag.NavalDir;
            return !aligned || toEnd < TurnWarn || MathF.Abs(ff.Y - lane.W) > 3f;
        }

        /// <summary>The traffic state into the battle's fingerprint.</summary>
        private void MixRoutes(Action<long> mix)
        {
            mix(Holds);
            foreach (var v in _big) mix(v.Id.Value * 1000L + (v.SeaHold + 1) * 10L + Math.Min(9, v.SeaWait / 20));
        }
    }
}
