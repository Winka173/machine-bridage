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
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>Prompt 23 C-D: what each kind of event does (set up, happen, run).</summary>
    public sealed partial class MissionEventSystem
    {
        private const int Player = MissionMode.PlayerTeam;
        private const int Enemy = MissionMode.EnemyTeam;

        /// <summary>The convoys' truck (side objectives, the neutral supply column).</summary>
        public const string Truck = "supply_truck";

        private sealed class SpawnGroup
        {
            public SpawnPoint Point = null!;
            public SpawnKind Kind;
            public bool Pods;
            public readonly List<string> Units = new();
        }

        private sealed class WavePlan
        {
            public readonly List<SpawnGroup> Groups = new();
            public Vector2? Target;
        }

        private sealed class GeneralPlan
        {
            public string General = "";
            public string Def = "";
            public SpawnPoint Point = null!;
            public readonly List<string> Escorts = new();
            public bool Retreats;
            public bool Retreating;
            public bool PassiveSet;
            public CommanderDef? Before;
        }

        private sealed class ConvoyPlan
        {
            public string Type = "";
            public Vector2 From, To;
            public readonly Dictionary<EntityId, int> Hitter = new();
        }

        private sealed class CounterPlan
        {
            public double NextAllowed;
            public double FireAt = -1;
            public Vector2 At;
        }

        private sealed class WeatherPlan
        {
            public string To = "Storm";
            public float Seconds = 25f;
            public float From = 1f, Target = 1f;
        }

        /// <summary>E.1: the Hollow Dam's ceasefire: the sworn column, where it stands, whether it has been let go.</summary>
        private sealed class CeasefirePlan
        {
            public SpawnPoint Point = null!;
            public readonly List<string> Column = new();

            /// <summary>When the sworn side breaks its word ("breakAt"; -1: it keeps it).</summary>
            public double BreakAt = -1;

            public bool Released;

            /// <summary>Prompt 31 L4 ("faction"): the column is a ceasefire faction: nothing of ours can hurt it, so we cannot break it.</summary>
            public bool Faction;
        }

        /// <summary>E.1: Brandt's line: the towers and where each goes up.</summary>
        private sealed class LinePlan
        {
            public readonly List<(string def, Vector2 at)> Towers = new();
            public Vector2 Facing;
        }

        /// <summary>E.1: a mini boss that comes up out of the ground (Tartarus) at a spot, not over an edge.</summary>
        private sealed class SurfacePlan
        {
            public string Def = "";
            public Vector2 At, Facing;
        }

        /// <summary>E.1: the satellite's test rods on their way down: when, where, how big, the look, the event.</summary>
        private readonly List<(double due, Vector2 at, float radius, float damage, string look, int state)> _rods = new();

        /// <summary>Fire support on its way: when, which support, whose, where and which way.</summary>
        private readonly List<(double due, string support, int team, Vector2 at, Vector2 towards)> _strikes = new();

        private readonly List<Crate> _crates = new();
        private int _crateIds;
        private string? _weatherNow;

        // ================================================================== set up

        private bool Prepare(SimWorld world, EventState s)
        {
            var e = s.Def;
            switch (e.Kind)
            {
                case MissionEventKind.EnemyWave:
                    return PrepareWave(world, s);
                case MissionEventKind.SupplyRaid:
                    return PrepareRaid(world, s);
                case MissionEventKind.AllyWave:
                    return PrepareAllies(world, s);
                case MissionEventKind.GeneralField:
                    return PrepareGeneral(world, s);
                case MissionEventKind.MiniBoss:
                    return PrepareMini(world, s);
                case MissionEventKind.Barrage:
                case MissionEventKind.AirRaid:
                case MissionEventKind.OrbitalStrike:
                    if (Group(world, Player) is not { } mark) return false;
                    s.Where = mark;
                    return true;
                case MissionEventKind.AllyAirStrike:
                case MissionEventKind.AllyArtillery:
                case MissionEventKind.IntelReveal:
                    if ((e.Kind == MissionEventKind.IntelReveal ? Group(world, Enemy, true, Player) ?? Group(world, Enemy) : Group(world, Enemy)) is not { } foe)
                        return false;
                    s.Where = foe;
                    return true;
                case MissionEventKind.SupplyDrop:
                    s.Where = Group(world, Player) ?? (world.TryGetRally(Player, out var home) ? home : world.Map.Centre);
                    return true;
                case MissionEventKind.SideObjective:
                    return PrepareObjective(world, s);
                case MissionEventKind.NeutralConvoy:
                    return PrepareCrossing(world, s, "neutral");
                case MissionEventKind.LootDrop:
                    return PrepareCrate(world, s);
                case MissionEventKind.WeatherShift:
                {
                    var to = e.Word("to") ?? "Storm";
                    s.Variant = to.ToLowerInvariant();
                    s.Plan = new WeatherPlan { To = to, Seconds = Math.Clamp(e.Number("seconds", 25f), 20f, 30f) };
                    return true;
                }
                case MissionEventKind.CounterBattery:
                    s.Plan = new CounterPlan();
                    return true;
                case MissionEventKind.Ceasefire:
                    return PrepareCeasefire(world, s);
                case MissionEventKind.GroundChange:
                case MissionEventKind.SandstormTurn:
                case MissionEventKind.CityBlackout:
                case MissionEventKind.BetrayalWarning:
                case MissionEventKind.OrbitalPods:
                case MissionEventKind.IceCrack:
                    return PrepareP31(world, s);
                default:
                    return true;
            }
        }

        /// <summary>The roster a wave draws from: the event's own, else the mission's general's (C.1), else the common one.</summary>
        private IReadOnlyList<string> RosterFor(SimWorld world, MissionEventDef e, bool groundOnly = false, bool own = true)
        {
            var named = own ? e.Words("roster") : Array.Empty<string>();
            var general = GeneralOf(e);
            IReadOnlyList<string> source = named.Count > 0 ? named
                : general != null && Rules.Generals.TryGetValue(general, out var g) && g.Roster.Count > 0 ? g.Roster : Rules.GenericRoster;
            var list = new List<string>();
            foreach (var id in source)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && !def.Static && !def.Boss && (!groundOnly || !def.Flying)) list.Add(id);
            if (list.Count == 0 && groundOnly)
                foreach (var id in Rules.GenericRoster)
                    if (world.Catalog.Vehicles.TryGetValue(id, out var def) && !def.Flying) list.Add(id);
            return list;
        }

        /// <summary>A wave's vehicles (no dice: its index and repeat pick them, Very Hard mixes elites in), before the cap.</summary>
        private List<string> Compose(SimWorld world, EventState s, IReadOnlyList<string> roster, int size)
        {
            var units = new List<string>();
            if (roster.Count == 0) return units;
            for (var k = 0; k < size; k++)
            {
                var id = roster[(s.Index * 3 + s.Fired * 5 + k) % roster.Count];
                if (Difficulty.Elites && k % 3 == 2 && world.Catalog.EliteVariant(id) is { } elite) id = elite;
                units.Add(id);
            }
            return units;
        }

        private int WaveSize(MissionEventDef e, float fallback) => Math.Max(1, (int)MathF.Round(e.Number("size", fallback) * Difficulty.WaveScale));

        private bool PrepareWave(SimWorld world, EventState s)
        {
            var e = s.Def;
            var roster = RosterFor(world, e);
            var size = Math.Min(WaveSize(e, 6f), Room(world, Enemy));
            if (roster.Count == 0 || size <= 0) return false;
            var d = Difficulty;
            var count = e.Has("directions") ? Math.Max(1, e.Whole("directions", 2)) : d.MinDirections + _random.Next(d.MaxDirections - d.MinDirections + 1);
            var bearings = Spawns!.Bearings(SpawnSide.Enemy);
            if (bearings.Count == 0) return false;
            // Front first, then the flanks in either order, the rear last (Very Hard's fourth direction).
            var ordered = new List<SpawnBearing>();
            if (bearings.Contains(SpawnBearing.Front)) ordered.Add(SpawnBearing.Front);
            var flanks = _random.Next(2) == 0 ? new[] { SpawnBearing.Left, SpawnBearing.Right } : new[] { SpawnBearing.Right, SpawnBearing.Left };
            foreach (var f in flanks)
                if (bearings.Contains(f)) ordered.Add(f);
            if (bearings.Contains(SpawnBearing.Rear)) ordered.Add(SpawnBearing.Rear);
            var delivery = Delivery(e);
            var plan = new WavePlan();
            foreach (var b in ordered)
            {
                if (plan.Groups.Count >= count) break;
                if (PickPoint(b, delivery) is { } g) plan.Groups.Add(g);
            }
            if (plan.Groups.Count == 0) return false;
            var units = Compose(world, s, roster, size);
            for (var i = 0; i < units.Count; i++) plan.Groups[i % plan.Groups.Count].Units.Add(units[i]);
            Arrange(s, plan);
            s.Strength = Strength(world.Catalog, units);
            return true;
        }

        private IReadOnlyList<string> Delivery(MissionEventDef e)
        {
            var own = e.Words("delivery");
            if (own.Count > 0) return own;
            var general = GeneralOf(e);
            return general != null && Rules.Generals.TryGetValue(general, out var g) ? g.Delivery : new[] { "edge" };
        }

        /// <summary>A spawn point in a direction by the first way of coming in that it has (else over the edge).</summary>
        private SpawnGroup? PickPoint(SpawnBearing bearing, IReadOnlyList<string> delivery)
        {
            foreach (var word in delivery)
            {
                var pods = word == "pods";
                var kind = word switch
                {
                    "rail" => SpawnKind.Rail, "sea" => SpawnKind.Sea, "landing" => SpawnKind.Landing, "air" or "pods" => SpawnKind.Air, _ => SpawnKind.Edge,
                };
                if (Pick(SpawnSide.Enemy, bearing, kind) is { } p) return new SpawnGroup { Point = p, Kind = kind, Pods = pods };
            }
            if (Pick(SpawnSide.Enemy, bearing, SpawnKind.Edge) is { } edge) return new SpawnGroup { Point = edge, Kind = SpawnKind.Edge };
            return null;
        }

        private SpawnPoint? Pick(SpawnSide side, SpawnBearing? bearing, SpawnKind kind)
        {
            var list = new List<SpawnPoint>();
            foreach (var p in Spawns!.All)
                if (p.Side == side && p.Kind == kind && (bearing == null || p.Bearing == bearing)) list.Add(p);
            return list.Count == 0 ? null : list[_random.Next(list.Count)];
        }

        private static void Arrange(EventState s, WavePlan plan)
        {
            s.Plan = plan;
            s.Where = plan.Groups[0].Point.Position;
            foreach (var g in plan.Groups) s.Arrows.Add((g.Point.Position, g.Point.Inward, g.Point.Bearing));
        }

        /// <summary>D.4: a group for the player's CP supply station or depot (its HQ when it has neither); none without a base.</summary>
        private bool PrepareRaid(SimWorld world, EventState s)
        {
            Vehicle? target = null;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Player && v.Def.Static && (v.Def.Id.StartsWith("logistics_station", StringComparison.Ordinal) ||
                                                                      v.Def.Id.StartsWith("ammo_depot", StringComparison.Ordinal)))
                {
                    target = v;
                    break;
                }
            if (target == null && world.Bases.Of(Player) is { HqFallen: false } camp && world.TryGetVehicle(camp.Hq, out var hq) && hq.IsAlive) target = hq;
            if (target == null) return false;
            var roster = RosterFor(world, s.Def, groundOnly: true);
            var size = Math.Min(WaveSize(s.Def, 4f), Room(world, Enemy));
            if (roster.Count == 0 || size <= 0) return false;
            // In from the edge nearest the target (not the rear: never out of the player's own camp).
            SpawnPoint? best = null;
            foreach (var p in Spawns!.All)
                if (p.Side == SpawnSide.Enemy && p.Kind == SpawnKind.Edge && p.Bearing != SpawnBearing.Rear &&
                    (best == null || Vector2.DistanceSquared(p.Position, target.Position) < Vector2.DistanceSquared(best.Position, target.Position)))
                    best = p;
            if (best == null) return false;
            var plan = new WavePlan { Target = target.Position };
            var g = new SpawnGroup { Point = best, Kind = SpawnKind.Edge };
            g.Units.AddRange(Compose(world, s, roster, size));
            plan.Groups.Add(g);
            Arrange(s, plan);
            s.Others.Add(target.Id);
            s.Strength = Strength(world.Catalog, g.Units);
            return true;
        }

        /// <summary>
        /// C.2-C.3: an Accord wave worth the difficulty's share of an enemy wave (the one it names, else the mission's biggest),
        /// by C.3's measure; Very Hard sends one a mission.
        /// </summary>
        private bool PrepareAllies(SimWorld world, EventState s)
        {
            var e = s.Def;
            var d = Difficulty;
            if (d.AllyWaves >= 0 && AllyWaves >= d.AllyWaves) return false;
            // E.1: chapter 12's Total Offensive has a cap of its own (the enemy's); every other wave the allies' one.
            var room = Math.Min(e.Whole("max", 12), Room(world, Player, e.Whole("cap", Rules.AllyCap)));
            if (e.Flag("line", false)) return PrepareLine(world, s, room);
            // Its rosters: "rosters" (one group each: the Total Offensive's old allies), else "roster", else the Accord's.
            var rosters = new List<List<string>>();
            foreach (var list in e.Words("rosters"))
            {
                var r = new List<string>();
                foreach (var id in list.Split(','))
                    if (world.Catalog.Vehicles.ContainsKey(id.Trim())) r.Add(id.Trim());
                if (r.Count > 0) rosters.Add(r);
            }
            if (rosters.Count == 0)
            {
                var r = new List<string>();
                var named = e.Words("roster");
                foreach (var id in named.Count > 0 ? named : Rules.AccordRoster)
                    if (world.Catalog.Vehicles.ContainsKey(id)) r.Add(id);
                if (r.Count == 0) return false;
                rosters.Add(r);
            }
            // "share" sets its own (chapter 12's Total Offensive: as strong as the enemy's wave); "count" is a squad of that
            // many whatever the table (E.1: Veyra's militia, a few at a time).
            var target = (e.Has("share") ? e.Number("share", 1f) : d.AllyShare) * ReferenceStrength(world, e) * e.Number("scale", 1f);
            var squad = e.Whole("count", 0);
            var points = AllyPoints(e.Flag("scatter", false), rosters.Count);
            if (points.Count == 0) return false;
            var plan = new WavePlan();
            var all = new List<string>();
            var kind = e.Word("delivery") == "edge" ? SpawnKind.Edge : SpawnKind.Drop;
            // The strength is shared by the groups filled to it (a named unit comes on top).
            var shares = 0;
            foreach (var r in rosters)
                if (r.Count > 1) shares++;
            shares = Math.Max(1, shares);
            for (var i = 0; i < rosters.Count && room > 0; i++)
            {
                var roster = rosters[i];
                List<string> units;
                if (squad > 0)
                {
                    units = new List<string>();
                    for (var k = 0; k < Math.Min(squad, room); k++) units.Add(roster[(s.Fired * squad + k) % roster.Count]);
                }
                // A group of one (a named unit: Mara's Behemoth) brings that one.
                else if (roster.Count == 1) units = new List<string> { roster[0] };
                else units = Fill(world, roster, target / shares, Math.Max(1, room / (rosters.Count - i)));
                if (units.Count == 0) continue;
                room -= units.Count;
                var g = new SpawnGroup { Point = points[i % points.Count], Kind = kind };
                g.Units.AddRange(units);
                plan.Groups.Add(g);
                all.AddRange(units);
            }
            if (plan.Groups.Count == 0) return false;
            s.Plan = plan;
            s.Where = plan.Groups[0].Point.Position;
            s.Strength = Strength(world.Catalog, all);
            return true;
        }

        /// <summary>
        /// Where allied groups come in: behind the player's area first, then the drop zone, then the player's objectives, one
        /// point a group while there are enough (one group: the first kind that has a point, at random among them); scattered
        /// (the militia): any allied point at random.
        /// </summary>
        private List<SpawnPoint> AllyPoints(bool scatter, int groups)
        {
            var list = new List<SpawnPoint>();
            if (scatter)
            {
                var any = new List<SpawnPoint>();
                foreach (var p in Spawns!.All)
                    if (p.Side == SpawnSide.Ally) any.Add(p);
                if (any.Count > 0) list.Add(any[_random.Next(any.Count)]);
                return list;
            }
            if (groups <= 1)
            {
                if ((Pick(SpawnSide.Ally, null, SpawnKind.Behind) ?? Pick(SpawnSide.Ally, null, SpawnKind.Drop) ?? Pick(SpawnSide.Ally, null, SpawnKind.Outpost)) is { } one)
                    list.Add(one);
                return list;
            }
            foreach (var kind in new[] { SpawnKind.Behind, SpawnKind.Drop, SpawnKind.Outpost })
                foreach (var p in Spawns!.All)
                    if (p.Side == SpawnSide.Ally && p.Kind == kind && list.Count < groups) list.Add(p);
            return list;
        }

        /// <summary>
        /// E.1 (chapter 6): Brandt raises a line of towers in front of the player's biggest group, facing the enemy; they come
        /// down as a dropped tower does and stand there with the Accord's mark.
        /// </summary>
        private bool PrepareLine(SimWorld world, EventState s, int room)
        {
            var e = s.Def;
            var towers = new List<string>();
            foreach (var id in e.Words("roster"))
                if (world.Catalog.Vehicles.ContainsKey(id) && towers.Count < room) towers.Add(id);
            if (towers.Count == 0) return false;
            Vector2 centre;
            if (Group(world, Player) is { } group) centre = group;
            else if (world.TryGetRally(Player, out var home)) centre = home;
            else return false;
            var foe = _host.EnemyGoal(world) ?? (world.TryGetRally(Enemy, out var camp) ? camp : world.Map.Centre);
            var ahead = foe - centre;
            ahead = ahead.LengthSquared() > 1f ? Vector2.Normalize(ahead) : Vector2.UnitY;
            var across = new Vector2(-ahead.Y, ahead.X);
            var line = world.ClampToMap(centre + ahead * e.Number("ahead", 16f));
            var plan = new LinePlan { Facing = ahead };
            var spacing = e.Number("spacing", 10f);
            for (var k = 0; k < towers.Count; k++)
            {
                var spot = world.ClampToMap(line + across * ((k - (towers.Count - 1) * 0.5f) * spacing));
                plan.Towers.Add((towers[k], world.ClearSpot(world.Catalog.Vehicle(towers[k]), spot, Player)));
            }
            s.Plan = plan;
            s.Where = line;
            s.Strength = Strength(world.Catalog, towers);
            return true;
        }

        /// <summary>The enemy wave an allied one is measured against.</summary>
        private float ReferenceStrength(SimWorld world, MissionEventDef e)
        {
            if (e.Word("of") is { } of && Find(of) is { } named) return named.Strength > 0f ? named.Strength : Estimate(world, named);
            var best = 0f;
            foreach (var s in _states)
                if (s.Def.Kind == MissionEventKind.EnemyWave) best = MathF.Max(best, s.Strength > 0f ? s.Strength : Estimate(world, s));
            return best > 0f ? best : e.Number("strength", 40f);
        }

        private float Estimate(SimWorld world, EventState s) => Strength(world.Catalog, Compose(world, s, RosterFor(world, s.Def), WaveSize(s.Def, 6f)));

        /// <summary>Vehicles of the roster adding up as close to a strength as they can (the biggest that fit first), at most <paramref name="room"/>.</summary>
        internal static List<string> Fill(SimWorld world, IReadOnlyList<string> roster, float target, int room)
        {
            var ranked = new List<(string id, float value)>();
            foreach (var id in roster)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && !def.Static) ranked.Add((id, Strength(def)));
            ranked.Sort((a, b) => b.value != a.value ? b.value.CompareTo(a.value) : string.CompareOrdinal(a.id, b.id));
            var units = new List<string>();
            var sum = 0f;
            while (units.Count < room && ranked.Count > 0)
            {
                string? pick = null;
                foreach (var (id, value) in ranked)
                    if (sum + value <= target + value * 0.5f)
                    {
                        pick = id;
                        sum += value;
                        break;
                    }
                if (pick == null) break;
                units.Add(pick);
            }
            if (units.Count == 0 && room > 0 && target > 0f && ranked.Count > 0) units.Add(ranked[ranked.Count - 1].id);
            return units;
        }

        /// <summary>The story's order of the chapters (the interludes after the chapter before them).</summary>
        private static readonly int[] StoryOrder = { 1, 2, 3, 13, 4, 5, 6, 14, 7, 8, 9, 15, 10, 11, 12 };

        public static int StoryIndex(int chapter)
        {
            var i = Array.IndexOf(StoryOrder, chapter);
            return i < 0 ? 0 : i;
        }

        /// <summary>The act of a chapter (1-4; an interlude goes with the act before it).</summary>
        public static int ActOf(int chapter) => chapter switch { 13 => 1, 14 => 2, 15 => 3, <= 0 => 1, _ => Math.Clamp((chapter - 1) / 3 + 1, 1, 4) };

        /// <summary>
        /// D.2: the general's own vehicle: a mini boss of theirs once the act and the difficulty are high enough (never the
        /// mission's own boss), else the elite of their card; escorts from their roster; whether they break off at 30 %.
        /// </summary>
        private bool PrepareGeneral(SimWorld world, EventState s)
        {
            var e = s.Def;
            var general = e.Word("general") ?? General;
            if (general == null) return false;
            var gd = Rules.Generals.TryGetValue(general, out var g) ? g : new GeneralEventDef { Id = general };
            var form = e.Word("form") ?? "auto";
            var mini = form == "mini" || (form == "auto" && ActOf(_host.Def.Chapter) + Difficulty.Step >= Rules.MiniFrom);
            var pick = mini ? MiniOf(world, general, gd) : null;
            pick ??= world.Catalog.EliteVariant(gd.Elite) ?? (world.Catalog.Vehicles.ContainsKey(gd.Elite) ? gd.Elite : null);
            if (pick == null) return false;
            var point = PickPoint(SpawnBearing.Front, new[] { "edge" })?.Point ?? PickPoint(SpawnBearing.Left, new[] { "edge" })?.Point;
            if (point == null) return false;
            var plan = new GeneralPlan { General = general, Def = pick, Point = point };
            var roster = RosterFor(world, e, groundOnly: !world.Catalog.Vehicle(pick).Flying);
            var escorts = Math.Min(e.Whole("escorts", Difficulty.Escorts), Math.Max(0, Room(world, Enemy) - 1));
            for (var k = 0; k < escorts && roster.Count > 0; k++) plan.Escorts.Add(roster[(s.Index + k) % roster.Count]);
            // A general the story needs later breaks off (never at their last battle: the last chapter's operation).
            var last = StoryIndex(_host.Def.Chapter) >= StoryIndex(gd.LastChapter) && _host.Def.Operation;
            plan.Retreats = e.Has("retreat") ? e.Flag("retreat", true) : !last && !e.Flag("final", false);
            s.Plan = plan;
            s.Where = point.Position;
            s.Arrows.Add((point.Position, point.Inward, point.Bearing));
            return true;
        }

        /// <summary>A mini boss of the general's own (their listed ones first), not one the mission fights as its boss.</summary>
        private string? MiniOf(SimWorld world, string general, GeneralEventDef gd)
        {
            var taken = new HashSet<string>();
            void Take(ScriptedUnitDef? b)
            {
                if (b == null) return;
                taken.Add(b.Def);
                if (b.Fallback != null) taken.Add(b.Fallback);
            }
            Take(_host.Def.Boss);
            foreach (var st in _host.Def.Stages) Take(st.Mission.Boss);
            var list = new List<string>();
            foreach (var id in gd.Minis)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Boss && !taken.Contains(id)) list.Add(id);
            if (list.Count == 0)
            {
                foreach (var def in world.Catalog.Vehicles.Values)
                    if (def.MiniBoss && def.General == general && !taken.Contains(def.Id)) list.Add(def.Id);
                list.Sort(string.CompareOrdinal);
            }
            return list.Count == 0 ? null : list[_random.Next(list.Count)];
        }

        private bool PrepareMini(SimWorld world, EventState s)
        {
            var e = s.Def;
            string? pick = null;
            foreach (var id in e.Words("boss"))
                if (world.Catalog.Vehicles.ContainsKey(id))
                {
                    pick = id;
                    break;
                }
            if (pick == null && (e.Word("general") ?? General) is { } general)
                pick = MiniOf(world, general, Rules.Generals.TryGetValue(general, out var gd) ? gd : new GeneralEventDef { Id = general });
            if (pick == null) return false;
            if (e.Flag("surface", false))
            {
                // E.1 (chapter 8): Tartarus comes up out of the ground between the front and the player's biggest group, never
                // in their close sight (B.3), under a ring on the ground for the whole warning.
                if (SurfaceSpot(world) is not { } up) return false;
                var toward = (Group(world, Player) ?? world.Map.Centre) - up;
                s.Plan = new SurfacePlan { Def = pick, At = up, Facing = toward.LengthSquared() > 1f ? Vector2.Normalize(toward) : Vector2.UnitY };
                s.Where = up;
                if (world.Catalog.TryGetSupport(e.Word("look") ?? "pod_drop", out var ring))
                    world.Emit(SimEvent.StrikeWarning(Enemy, ring, up, up, MathF.Max(1f, Lead(s))));
                s.Strength = Strength(world.Catalog, new[] { pick });
                return true;
            }
            if (PickPoint(SpawnBearing.Front, new[] { "edge" }) is not { } g) return false;
            g.Units.Add(pick);
            var plan = new WavePlan();
            plan.Groups.Add(g);
            Arrange(s, plan);
            s.Strength = Strength(world.Catalog, g.Units);
            return true;
        }

        /// <summary>A spot on the open ground between the player's biggest group and the enemy's camp, out of the player's close sight.</summary>
        private Vector2? SurfaceSpot(SimWorld world)
        {
            if ((Group(world, Player) ?? Centre(world, Player)) is not { } to) return null;
            var from = world.TryGetRally(Enemy, out var camp) ? camp : world.Map.Centre;
            for (var k = 3; k <= 9; k++)
            {
                if (!SpawnPoints.Snap(world, Vector2.Lerp(to, from, k * 0.1f), world.Grid.MainRegion, out var spot)) continue;
                if (!Seen(world, spot)) return spot;
            }
            return null;
        }

        /// <summary>E.1 (chapter 6): the general's sworn column for a ceasefire, at an edge on the enemy's front.</summary>
        private bool PrepareCeasefire(SimWorld world, EventState s)
        {
            var e = s.Def;
            var roster = RosterFor(world, e, groundOnly: true);
            var size = Math.Min(Math.Max(1, e.Whole("size", 4)), Room(world, Enemy));
            if (roster.Count == 0 || size <= 0) return false;
            var point = PickPoint(SpawnBearing.Front, new[] { "edge" })?.Point ?? PickPoint(SpawnBearing.Left, new[] { "edge" })?.Point;
            if (point == null) return false;
            var plan = new CeasefirePlan { Point = point, Faction = e.Flag("faction", false) };
            plan.Column.AddRange(Compose(world, s, roster, size));
            s.Plan = plan;
            s.Where = point.Position;
            s.Strength = Strength(world.Catalog, plan.Column);
            return true;
        }

        /// <summary>D.3: a side objective: intercept a convoy of files, rescue a besieged allied column, or see a civilian one through.</summary>
        private bool PrepareObjective(SimWorld world, EventState s)
        {
            var type = s.Def.Word("type") ?? "intercept";
            s.Variant = type;
            if (type == "rescue")
            {
                var flank = Pick(SpawnSide.Enemy, SpawnBearing.Left, SpawnKind.Edge) ?? Pick(SpawnSide.Enemy, SpawnBearing.Right, SpawnKind.Edge);
                if (flank == null) return false;
                if (!SpawnPoints.Snap(world, Vector2.Lerp(world.Map.Centre, flank.Position, 0.55f), world.Grid.MainRegion, out var spot)) return false;
                s.Where = spot;
                s.Plan = new ConvoyPlan { Type = type, From = spot, To = spot };
                s.Arrows.Add((spot, Vector2.Normalize(world.Map.Centre - spot + new Vector2(0.01f, 0f)), Spawns!.BearingOf(spot, world.Map.Centre)));
                return true;
            }
            return PrepareCrossing(world, s, type);
        }

        /// <summary>A column's road across the map: from one flank's edge to the other's (an intercepted one from the enemy's side).</summary>
        private bool PrepareCrossing(SimWorld world, EventState s, string type)
        {
            var left = Pick(SpawnSide.Enemy, SpawnBearing.Left, SpawnKind.Edge);
            var right = Pick(SpawnSide.Enemy, SpawnBearing.Right, SpawnKind.Edge);
            var front = Pick(SpawnSide.Enemy, SpawnBearing.Front, SpawnKind.Edge);
            SpawnPoint? from = left, to = right;
            if (from == null || to == null)
            {
                from = front;
                to = left ?? right;
            }
            if (from == null || to == null) return false;
            if (_random.Next(2) == 0) (from, to) = (to, from);
            s.Variant ??= type == "neutral" ? null : type;
            s.Plan = new ConvoyPlan { Type = type, From = from.Position, To = to.Position };
            s.Where = from.Position;
            s.Arrows.Add((from.Position, from.Inward, from.Bearing));
            return true;
        }

        private bool PrepareCrate(SimWorld world, EventState s)
        {
            var map = world.Map;
            for (var attempt = 0; attempt < 24; attempt++)
            {
                var at = map.Centre + new Vector2((float)(_random.NextDouble() * 2 - 1) * map.Width * 0.2f, (float)(_random.NextDouble() * 2 - 1) * map.Length * 0.2f);
                if (!world.Grid.IsWalkable(at) || world.Grid.RegionOf(at) != world.Grid.MainRegion) continue;
                var clear = true;
                foreach (var team in map.Teams)
                    if (Vector2.Distance(team.Rally, at) < 40f) clear = false;
                if (!clear) continue;
                s.Where = at;
                return true;
            }
            return false;
        }

        // ================================================================== happen

        private Outcome Happen(SimWorld world, EventState s)
        {
            var e = s.Def;
            switch (e.Kind)
            {
                case MissionEventKind.MiniBoss when s.Plan is SurfacePlan up:
                {
                    if (Seen(world, up.At) && s.Tries < 5) return Outcome.Retry;
                    var boss = Arrive(world, s, up.Def, Enemy, up.At, up.Facing, false);
                    Line(world, s, "start", boss.Id);
                    return Outcome.Done;
                }
                case MissionEventKind.EnemyWave:
                case MissionEventKind.SupplyRaid:
                case MissionEventKind.MiniBoss:
                {
                    var plan = (WavePlan)s.Plan!;
                    var places = new List<Vector2>();
                    foreach (var g in plan.Groups)
                    {
                        if (!Spawns!.TryPlace(world, g.Point, Rules.NearSight, Player, out var at) && s.Tries < 5) return Outcome.Retry;
                        places.Add(at);
                    }
                    for (var i = 0; i < plan.Groups.Count; i++)
                    {
                        var g = plan.Groups[i];
                        var units = new List<string>();
                        foreach (var id in g.Units) units.Add(e.Kind == MissionEventKind.MiniBoss ? id : world.Economy.ForWave(Enemy, id));
                        Deliver(world, s, units, Enemy, places[i], g.Point.Inward, g.Kind, false, g.Pods, g.Point.From);
                    }
                    s.Where = places[0];
                    if (plan.Target is { } raid)
                        foreach (var id in s.Units)
                            if (world.TryGetVehicle(id, out var v)) Push(world, v, raid);
                    if (e.Kind == MissionEventKind.MiniBoss && s.Units.Count > 0) Line(world, s, "start", s.Units[0]);
                    return e.Kind == MissionEventKind.SupplyRaid ? Outcome.Running : Outcome.Done;
                }
                case MissionEventKind.AllyWave:
                {
                    if (s.Plan is LinePlan line)
                    {
                        // Brandt's towers come down as a dropped tower does, where the line runs.
                        foreach (var (def, at) in line.Towers)
                        {
                            world.Emit(SimEvent.DeploymentQueued(Player, def, at, -line.Facing, EconomySystemDelivery));
                            _drops.Add((world.Time + EconomySystemDelivery, def, Player, at, line.Facing, s.Index, true));
                        }
                    }
                    else
                        foreach (var g in ((WavePlan)s.Plan!).Groups)
                            Deliver(world, s, g.Units, Player, g.Point.Position, g.Point.Inward, g.Kind, true);
                    AllyWaves++;
                    Notice(world, s, "start", 0f);
                    Line(world, s, "start");
                    return Outcome.Done;
                }
                case MissionEventKind.Barrage:
                {
                    var support = e.Word("support") ?? "artillery_barrage";
                    var salvos = Math.Max(1, e.Whole("salvos", 3));
                    var radius = e.Number("radius", 18f);
                    for (var k = 0; k < salvos; k++)
                    {
                        var angle = (float)(_random.NextDouble() * SimMath.Tau);
                        var at = world.ClampToMap(s.Where + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * radius * (float)Math.Sqrt(_random.NextDouble()));
                        _strikes.Add((world.Time + k * 1.5, support, Enemy, at, at + Vector2.UnitX));
                    }
                    return Outcome.Done;
                }
                case MissionEventKind.AirRaid:
                {
                    if (!world.Catalog.TryGetSupport(e.Word("support") ?? "air_raid", out var raid)) return Outcome.Done;
                    var angle = (float)(_random.NextDouble() * SimMath.Tau);
                    var along = new Vector2(MathF.Cos(angle), MathF.Sin(angle));
                    var start = s.Where - along * (raid.Length * 0.5f);
                    world.Strikes.Launch(raid, Enemy, world.ClampToMap(start), start + along);
                    return Outcome.Done;
                }
                case MissionEventKind.AllyAirStrike:
                case MissionEventKind.AllyArtillery:
                {
                    var air = e.Kind == MissionEventKind.AllyAirStrike;
                    var id = e.Word("support") ?? (air ? "airstrike" : "artillery_barrage");
                    if (!world.Catalog.TryGetSupport(id, out var support)) return Outcome.Done;
                    var at = OperationMode.StrikeTarget(world, Player, support.IsLine ? support.Length * 0.5f : support.Radius) ?? s.Where;
                    s.Where = at;
                    world.TryGetRally(Player, out var home);
                    var along = at - home;
                    along = along.LengthSquared() > 1f ? Vector2.Normalize(along) : Vector2.UnitX;
                    var count = Math.Max(1, e.Whole(air ? "passes" : "salvos", air ? 1 : 3));
                    for (var k = 0; k < count; k++)
                    {
                        var start = support.IsLine ? at - along * (support.Length * 0.5f) : at + new Vector2((k % 2) * 6f - 3f, (k / 2) * 6f - 3f) * (k > 0 ? 1f : 0f);
                        _strikes.Add((world.Time + k * (air ? 3.0 : 1.5), id, Player, world.ClampToMap(start), start + along));
                    }
                    Notice(world, s, "start", support.Delay);
                    Line(world, s, "start");
                    return Outcome.Done;
                }
                case MissionEventKind.CounterBattery:
                    s.EndsAt = e.Number("seconds", 0f) > 0f ? world.Time + e.Number("seconds", 0f) : -1;
                    return Outcome.Running;
                case MissionEventKind.GeneralField:
                    return FieldGeneral(world, s);
                case MissionEventKind.SideObjective:
                case MissionEventKind.NeutralConvoy:
                    return StartConvoy(world, s);
                case MissionEventKind.LootDrop:
                {
                    var crate = new Crate(new EntityId(900000 + _crateIds++), s.Where, world.Time + 5.0, world.Time + 55.0);
                    world.CrateList.Add(crate);
                    _crates.Add(crate);
                    world.Emit(SimEvent.CrateIncoming(crate, 5f));
                    Notice(world, s, "start", 5f);
                    s.EndsAt = crate.ExpiresAt;
                    return Outcome.Running;
                }
                case MissionEventKind.SupplyDrop:
                {
                    if (world.Catalog.TryGetSupport(e.Word("support") ?? "repair_drop", out var drop))
                    {
                        world.Strikes.Launch(drop, Player, s.Where, s.Where + Vector2.UnitX);
                        s.EndsAt = world.Time + drop.Delay + 0.5;
                    }
                    else s.EndsAt = world.Time;
                    Notice(world, s, "start", 0f);
                    Line(world, s, "start");
                    return Outcome.Running;
                }
                case MissionEventKind.IntelReveal:
                {
                    var seconds = e.Number("seconds", 8f);
                    world.Strikes.AddScan(Player, s.Where, e.Number("radius", 30f), seconds);
                    Notice(world, s, "start", seconds);
                    Line(world, s, "start");
                    return Outcome.Done;
                }
                case MissionEventKind.Blackout:
                {
                    var seconds = e.Number("seconds", 20f);
                    world.Blackout(Player, world.Time + seconds);
                    s.EndsAt = world.Time + seconds;
                    Notice(world, s, "start", seconds);
                    return Outcome.Running;
                }
                case MissionEventKind.PlanChange:
                {
                    Notice(world, s, "start", 0f);
                    Line(world, s, "start");
                    if (!_host.ChangePlan(world, e)) Record(world, s, "unplanned");
                    return Outcome.Done;
                }
                case MissionEventKind.Ceasefire:
                    return StartCeasefire(world, s);
                case MissionEventKind.OrbitalStrike:
                {
                    // Prompt 18's big-attack rules, small: the ring on the ground for the rod's fall, then one kinetic hit.
                    var look = e.Word("look") ?? "leviathan_shell";
                    var fall = MathF.Max(0.5f, e.Number("fall", 4f));
                    if (world.Catalog.TryGetSupport(look, out var ring)) world.Emit(SimEvent.StrikeWarning(Enemy, ring, s.Where, s.Where, fall));
                    _rods.Add((world.Time + fall, s.Where, e.Number("radius", 6f), e.Number("damage", 900f), look, s.Index));
                    return Outcome.Done;
                }
                case MissionEventKind.WeatherShift:
                {
                    var plan = (WeatherPlan)s.Plan!;
                    var from = _weatherNow ?? _host.Def.Weather;
                    var sight = Rules.WeatherSight;
                    var ratio = (sight.TryGetValue(plan.To, out var to) ? to : 1f) / MathF.Max(0.1f, sight.TryGetValue(from, out var was) ? was : 1f);
                    plan.From = world.WeatherSight;
                    plan.Target = Math.Clamp(world.WeatherSight * ratio, 0.5f, 1.3f);
                    _weatherNow = plan.To;
                    world.Emit(SimEvent.WeatherShifting(plan.To, plan.Seconds));
                    s.EndsAt = world.Time + plan.Seconds;
                    return Outcome.Running;
                }
                case MissionEventKind.GroundChange:
                case MissionEventKind.SandstormTurn:
                case MissionEventKind.CityBlackout:
                case MissionEventKind.BetrayalWarning:
                case MissionEventKind.OrbitalPods:
                case MissionEventKind.IceCrack:
                    return HappenP31(world, s);
                default:
                    return Outcome.Done;
            }
        }

        private Outcome FieldGeneral(SimWorld world, EventState s)
        {
            var plan = (GeneralPlan)s.Plan!;
            if (!Spawns!.TryPlace(world, plan.Point, Rules.NearSight, Player, out var at) && s.Tries < 5) return Outcome.Retry;
            // The general's passive (prompt 22 F) while on the field, when the mission's enemy is not under it already.
            var passive = Commanders.General(plan.General);
            if (passive != null && world.CommanderOf(Enemy) != passive)
            {
                plan.Before = world.CommanderOf(Enemy);
                plan.PassiveSet = true;
                world.SetCommander(Enemy, passive);
            }
            var v = Arrive(world, s, plan.Def, Enemy, at, plan.Point.Inward, false);
            v.General = plan.General;
            var across = new Vector2(-plan.Point.Inward.Y, plan.Point.Inward.X);
            for (var k = 0; k < plan.Escorts.Count; k++)
            {
                var spot = world.ClampToMap(at + across * ((k % 2 == 0 ? 1f : -1f) * (6f + 4f * (k / 2))) - plan.Point.Inward * 4f);
                var escort = Arrive(world, s, world.Economy.ForWave(Enemy, plan.Escorts[k]), Enemy, spot, plan.Point.Inward, false);
                s.Others.Add(escort.Id);
            }
            s.Where = at;
            Notice(world, s, "start", 0f, v.Id);
            Line(world, s, "start", v.Id);
            return Outcome.Running;
        }

        private Outcome StartConvoy(SimWorld world, EventState s)
        {
            var e = s.Def;
            var plan = (ConvoyPlan)s.Plan!;
            var count = Math.Max(1, e.Whole("count", 3));
            var seconds = e.Number("seconds", 120f);
            var dir = plan.To - plan.From;
            dir = dir.LengthSquared() > 1f ? Vector2.Normalize(dir) : Vector2.UnitX;
            switch (plan.Type)
            {
                case "rescue":
                {
                    // The allied column, halted and holding, and the enemy group round it on the enemy's side.
                    if (Seen(world, plan.From) && s.Tries < 5) return Outcome.Retry;
                    // The held column: "column" (E.1: chapter 8's miners), else "roster", else an Accord column.
                    var roster = e.Words("column").Count > 0 ? e.Words("column")
                        : e.Words("roster").Count > 0 ? e.Words("roster") : new[] { "ifv", "armored_car", "main_battle_tank" };
                    for (var k = 0; k < count; k++)
                    {
                        var id = roster[k % roster.Count];
                        if (!world.Catalog.Vehicles.ContainsKey(id)) id = Truck;
                        var v = world.SpawnVehicle(id, Player, world.ClampToMap(plan.From + new Vector2((k % 3 - 1) * 5f, (k / 3) * 5f)), 0f);
                        v.Scripted = true;
                        s.Units.Add(v.Id);
                    }
                    var foes = e.Words("column").Count > 0 ? RosterFor(world, e, groundOnly: true, own: false) : RosterFor(world, e, groundOnly: true);
                    var size = Math.Min(WaveSize(e, 4f), Room(world, Enemy));
                    var away = world.TryGetRally(Enemy, out var camp) ? camp - plan.From : Vector2.UnitY;
                    away = away.LengthSquared() > 1f ? Vector2.Normalize(away) : Vector2.UnitY;
                    var besiegers = Compose(world, s, foes, size);
                    for (var k = 0; k < besiegers.Count; k++)
                    {
                        var angle = (k - (besiegers.Count - 1) * 0.5f) * 0.45f;
                        var off = new Vector2(away.X * MathF.Cos(angle) - away.Y * MathF.Sin(angle), away.X * MathF.Sin(angle) + away.Y * MathF.Cos(angle));
                        var v = world.SpawnVehicle(world.Economy.ForWave(Enemy, besiegers[k]), Enemy, world.ClampToMap(plan.From + off * 24f), SimMath.HeadingOf(-off));
                        v.Reinforcement = true;
                        v.ManualUntil = world.Time + seconds;
                        world.Submit(new Command(CommandType.AttackMove, Enemy, new[] { v.Id }, plan.From));
                        s.Others.Add(v.Id);
                    }
                    s.Needed = s.Others.Count;
                    break;
                }
                default:
                {
                    // A column of trucks along the road: the enemy's files, a civilian column, or a neutral supply train.
                    var team = plan.Type switch { "intercept" => Enemy, "neutral" => Teams.Hostile, _ => Player };
                    if (team != Player && Seen(world, plan.From) && s.Tries < 5) return Outcome.Retry;
                    for (var k = 0; k < count; k++)
                    {
                        var v = world.SpawnVehicle(Truck, team, world.ClampToMap(plan.From - dir * (k * 9f)), SimMath.HeadingOf(dir));
                        v.Scripted = true;
                        if (team != Enemy) world.HoldFire(v, true);
                        if (plan.Type == "intercept") v.Marked = true;
                        s.Units.Add(v.Id);
                        world.Submit(new Command(CommandType.Move, team, new[] { v.Id }, world.ClampToMap(plan.To)));
                    }
                    s.Needed = plan.Type == "protect" ? Math.Clamp(e.Whole("need", count - 1), 1, count) : count;
                    break;
                }
            }
            if (plan.Type != "neutral") s.EndsAt = world.Time + seconds;
            Notice(world, s, "start", plan.Type == "neutral" ? 0f : seconds);
            Line(world, s, "start");
            return Outcome.Running;
        }

        // ================================================================== running

        private void Update(SimWorld world, EventState s, float dt)
        {
            var e = s.Def;
            switch (e.Kind)
            {
                case MissionEventKind.CounterBattery:
                    CounterBattery(world, s);
                    break;
                case MissionEventKind.GeneralField:
                    WatchGeneral(world, s);
                    break;
                case MissionEventKind.SideObjective:
                case MissionEventKind.NeutralConvoy:
                    WatchConvoy(world, s);
                    break;
                case MissionEventKind.SupplyRaid:
                {
                    var target = s.Others.Count > 0 && world.TryGetVehicle(s.Others[0], out var t) && t.IsAlive;
                    if (!target)
                    {
                        Notice(world, s, "fail", 0f);
                        Finish(world, s, false);
                    }
                    else if (Alive(world, s.Units) == 0 && _drops.Count == 0)
                    {
                        Notice(world, s, "done", 0f);
                        Finish(world, s, true);
                    }
                    break;
                }
                case MissionEventKind.LootDrop:
                    WatchCrates(world, s, dt);
                    break;
                case MissionEventKind.Ceasefire:
                    WatchCeasefire(world, s);
                    break;
                case MissionEventKind.SupplyDrop:
                    if (world.Time < s.EndsAt) break;
                    // The drop's crates rearm what stands under them (the repair drop mends it over its seconds).
                    foreach (var v in world.VehicleList)
                        if (v.IsAlive && v.Team == Player && Vector2.Distance(v.Position, s.Where) < e.Number("radius", 16f)) world.Refill(v);
                    Finish(world, s, true);
                    break;
                case MissionEventKind.Blackout:
                    if (world.Time < s.EndsAt) break;
                    Notice(world, s, "end", 0f);
                    Line(world, s, "end");
                    Finish(world, s, true, "end");
                    break;
                case MissionEventKind.WeatherShift:
                {
                    var plan = (WeatherPlan)s.Plan!;
                    var t = (float)Math.Clamp((world.Time - s.StartAt) / Math.Max(0.1, plan.Seconds), 0.0, 1.0);
                    world.WeatherSight = plan.From + (plan.Target - plan.From) * t;
                    if (t >= 1f) Finish(world, s, true, "end");
                    break;
                }
                case MissionEventKind.SandstormTurn:
                case MissionEventKind.CityBlackout:
                case MissionEventKind.OrbitalPods:
                case MissionEventKind.IceCrack:
                    UpdateP31(world, s);
                    break;
                default:
                    s.Phase = EventPhase.Done;
                    break;
            }
        }

        private static int Alive(SimWorld world, List<EntityId> ids)
        {
            var n = 0;
            foreach (var id in ids)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive) n++;
            return n;
        }

        /// <summary>D.1: a player's gun that has stood firing in one place too long draws counter-battery fire (warned).</summary>
        private void CounterBattery(SimWorld world, EventState s)
        {
            var plan = (CounterPlan)s.Plan!;
            var e = s.Def;
            if (s.EndsAt >= 0 && world.Time >= s.EndsAt && plan.FireAt < 0)
            {
                Finish(world, s, true, "end");
                return;
            }
            if (plan.FireAt >= 0)
            {
                if (world.Time < plan.FireAt) return;
                var support = e.Word("support") ?? "artillery_barrage";
                for (var k = 0; k < Math.Max(1, e.Whole("salvos", 2)); k++) _strikes.Add((world.Time + k * 1.2, support, Enemy, plan.At, plan.At + Vector2.UnitX));
                plan.FireAt = -1;
                plan.NextAllowed = world.Time + e.Number("cooldown", 45f);
                return;
            }
            if (world.Time < plan.NextAllowed || world.Tick % 10 != 0) return;
            var still = e.Number("still", 20f);
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Player || v.Flying || v.Def.Static || v.Def.Class != UnitClass.Artillery) continue;
                if (world.Time - v.StillSince < still || world.Time - v.LastFiredAt > 3.0) continue;
                var lead = e.Number("lead", 5f);
                plan.At = v.Position;
                plan.FireAt = world.Time + lead;
                s.Where = v.Position;
                Notice(world, s, "warn", lead, v.Id);
                Line(world, s, "warn");
                Record(world, s, "warn");
                return;
            }
        }

        private void WatchGeneral(SimWorld world, EventState s)
        {
            var plan = (GeneralPlan)s.Plan!;
            var alive = s.Units.Count > 0 && world.TryGetVehicle(s.Units[0], out var v) && v.IsAlive ? v : null;
            if (alive == null)
            {
                if (plan.PassiveSet) world.SetCommander(Enemy, plan.Before);
                plan.PassiveSet = false;
                if (!plan.Retreating) Notice(world, s, "done", 0f);
                Finish(world, s, true, plan.Retreating ? "gone" : "done");
                return;
            }
            if (plan.Retreating || !plan.Retreats || alive.Hp > alive.MaxHp * Rules.RetreatAt) return;
            // Breaking off (D.2): it cannot be touched now, drives for the enemy's edge and leaves the battle; the push-back pays
            // (as a kill would) once it is gone.
            plan.Retreating = true;
            alive.Invulnerable = true;
            alive.Scripted = true;
            alive.ExpiresAt = world.Time + 8.0;
            var away = plan.Point.Position;
            foreach (var p in Spawns!.All)
                if (p.Side == SpawnSide.Enemy && p.Kind == SpawnKind.Edge &&
                    Vector2.DistanceSquared(p.Position, alive.Position) < Vector2.DistanceSquared(away, alive.Position)) away = p.Position;
            world.Submit(new Command(CommandType.Move, Enemy, new[] { alive.Id }, world.ClampToMap(away)));
            Notice(world, s, "retreat", 8f, alive.Id);
            Line(world, s, "retreat", alive.Id);
            Record(world, s, "retreat");
        }

        private void WatchConvoy(SimWorld world, EventState s)
        {
            var plan = (ConvoyPlan)s.Plan!;
            var now = world.Time;
            if (plan.Type == "rescue")
            {
                var convoy = Alive(world, s.Units);
                var foes = Alive(world, s.Others);
                s.Count = s.Needed - foes;
                if (foes == 0)
                {
                    // Relieved: the column joins the allied reinforcements.
                    foreach (var id in s.Units)
                        if (world.TryGetVehicle(id, out var v) && v.IsAlive)
                        {
                            v.Scripted = false;
                            v.Ally = true;
                            v.Reinforcement = true;
                        }
                    Notice(world, s, "done", 0f);
                    Line(world, s, "done");
                    Finish(world, s, true);
                }
                else if (convoy == 0 || now >= s.EndsAt)
                {
                    foreach (var id in s.Units)
                        if (world.TryGetVehicle(id, out var v) && v.IsAlive) v.ExpiresAt = now + 0.1;
                    Notice(world, s, "fail", 0f);
                    Line(world, s, "fail");
                    Finish(world, s, false);
                }
                return;
            }
            var driving = 0;
            foreach (var id in s.Units)
            {
                if (!world.TryGetVehicle(id, out var truck) || !truck.IsAlive) continue;
                if (plan.Type == "neutral" && truck.LastAttackerTeam >= 0) plan.Hitter[id] = truck.LastAttackerTeam;
                if (Vector2.Distance(truck.Position, plan.To) > 8f)
                {
                    driving++;
                    continue;
                }
                // Out over the edge.
                truck.Hp = 0f;
                world.Emit(SimEvent.Retired(truck));
                if (plan.Type == "protect") s.Count++;
                if (plan.Type == "intercept")
                {
                    Notice(world, s, "fail", 0f);
                    Line(world, s, "fail");
                    Finish(world, s, false);
                    return;
                }
            }
            if (plan.Type == "neutral")
            {
                // D.4: whoever knocks a truck out takes its load (CP).
                foreach (var id in s.Units)
                {
                    if (world.TryGetVehicle(id, out var t) && t.IsAlive) continue;
                    if (!plan.Hitter.TryGetValue(id, out var team)) continue;
                    plan.Hitter.Remove(id);
                    var cp = s.Def.Whole("cp", 8);
                    if (team is Player or Enemy && world.TryGetEconomy(team, out var economy))
                    {
                        economy.Cp = MathF.Min(economy.Bank, economy.Cp + cp);
                        world.Emit(SimEvent.BountyPaid(team, "convoy", s.Where, cp));
                    }
                }
                if (driving == 0) Finish(world, s, true, "end");
                return;
            }
            if (plan.Type == "intercept")
            {
                s.Count = s.Units.Count - driving;
                if (driving == 0)
                {
                    Notice(world, s, "done", 0f);
                    Line(world, s, "done");
                    Finish(world, s, true);
                }
                else if (now >= s.EndsAt)
                {
                    Notice(world, s, "fail", 0f);
                    Finish(world, s, false);
                }
                return;
            }
            // Protect: enough through, or too few left to make it.
            if (s.Count >= s.Needed)
            {
                Notice(world, s, "done", 0f);
                Line(world, s, "done");
                Finish(world, s, true);
            }
            else if (s.Count + driving < s.Needed || now >= s.EndsAt)
            {
                Notice(world, s, "fail", 0f);
                Line(world, s, "fail");
                Finish(world, s, false);
            }
        }

        /// <summary>D.4: the loot crate: the side that holds the ground round it for two seconds takes it.</summary>
        private void WatchCrates(SimWorld world, EventState s, float dt)
        {
            var now = world.Time;
            for (var i = _crates.Count - 1; i >= 0; i--)
            {
                var crate = _crates[i];
                if (now < crate.LandsAt) continue;
                if (now > crate.ExpiresAt || !crate.IsAlive)
                {
                    crate.IsAlive = false;
                    world.CrateList.Remove(crate);
                    _crates.RemoveAt(i);
                    Finish(world, s, false, "end");
                    continue;
                }
                var holder = -1;
                var contested = false;
                foreach (var v in world.VehicleList)
                {
                    if (!v.IsAlive || v.Flying || v.Team is < 0 or > 1 || Vector2.Distance(v.Position, crate.Position) > 6f + v.Def.HullRadius) continue;
                    if (holder < 0) holder = v.Team;
                    else if (holder != v.Team) contested = true;
                }
                if (holder < 0 || contested)
                {
                    crate.Claim = MathF.Max(0f, crate.Claim - dt / 2f);
                    continue;
                }
                if (holder != crate.Holder) crate.Claim = 0f;
                crate.Holder = holder;
                crate.Claim += dt / 2f;
                if (crate.Claim < 1f) continue;
                crate.IsAlive = false;
                world.CrateList.Remove(crate);
                _crates.RemoveAt(i);
                world.Emit(SimEvent.CrateClaimed(crate, holder));
                var repair = s.Def.Number("repair", 0f);
                if (repair > 0f)
                {
                    foreach (var v in world.VehicleList)
                        if (v.IsAlive && v.Team == holder && !v.Def.Boss && Vector2.Distance(v.Position, crate.Position) < 25f)
                        {
                            var amount = world.Gear.Heal(v, v.MaxHp * repair);
                            if (amount > 0f) world.Emit(SimEvent.RepairedBy(v, amount));
                        }
                }
                else if (world.TryGetEconomy(holder, out var economy)) economy.Cp = MathF.Min(economy.Bank, economy.Cp + s.Def.Whole("cp", 12));
                Notice(world, s, holder == Player ? "done" : "fail", 0f);
                Finish(world, s, holder == Player, holder == Player ? "done" : "fail");
            }
        }

        // ================================================================== the underdog and fire support on its way

        /// <summary>
        /// C.2: prompt 13's help for the side falling behind came up for the player: the mission's next allied wave comes now
        /// instead of the free drop (true: the drop is not given; a mission with allied waves never gives both).
        /// </summary>
        private bool CallAllies(SimWorld world)
        {
            foreach (var s in _states)
                if (s.Def.Kind == MissionEventKind.AllyWave && s.Phase == EventPhase.Waiting && s.Fired == 0)
                {
                    Record(world, s, "underdog");
                    Begin(world, s);
                    break;
                }
            return true;
        }

        /// <summary>E.1: a test rod lands: a kinetic penetrator from above (prompt 19 F's rods), on every side but the enemy's.</summary>
        private void StepRods(SimWorld world)
        {
            for (var i = 0; i < _rods.Count; i++)
            {
                var r = _rods[i];
                if (world.Time < r.due) continue;
                _rods.RemoveAt(i--);
                if (world.Catalog.TryGetSupport(r.look, out var look)) world.Emit(SimEvent.StrikeImpact(Enemy, look, r.at));
                world.Damage.Splash(r.at, r.radius, r.damage, DamageType.Kinetic, Enemy, EntityId.None,
                    info: new HitInfo(null, Enemy, null, r.at, HitKind.Direct, true).WithPen(4f, true));
                Record(world, _states[r.state], "impact");
            }
        }

        // ================================================================== the ceasefire (E.1, chapter 6)

        private Outcome StartCeasefire(SimWorld world, EventState s)
        {
            var e = s.Def;
            var plan = (CeasefirePlan)s.Plan!;
            if (!Spawns!.TryPlace(world, plan.Point, Rules.NearSight, Player, out var at) && s.Tries < 5) return Outcome.Retry;
            // The sworn column: its fire held, out of both commanders' hands and of every weapon's own choice of target.
            var across = new Vector2(-plan.Point.Inward.Y, plan.Point.Inward.X);
            for (var k = 0; k < plan.Column.Count; k++)
            {
                var spot = world.ClampToMap(at + across * ((k % 3) - 1f) * 7f - plan.Point.Inward * (k / 3) * 7f);
                var v = world.SpawnVehicle(world.Economy.ForWave(Enemy, plan.Column[k]), Enemy, spot, SimMath.HeadingOf(plan.Point.Inward));
                v.Reinforcement = true;
                v.Scripted = true;
                v.Truce = true;
                v.Sworn = plan.Faction;
                world.HoldFire(v, true);
                s.Units.Add(v.Id);
            }
            var seconds = e.Number("seconds", 150f);
            s.EndsAt = world.Time + seconds;
            if (e.Has("breakAt")) plan.BreakAt = world.Time + e.Number("breakAt", 0f);
            s.Where = at;
            Notice(world, s, "start", seconds);
            Line(world, s, "start");
            return Outcome.Running;
        }

        /// <summary>
        /// Who fires first loses their reward: our side hitting the sworn column (only an ordered attack or a strike can), or
        /// the column opening fire. Kept to the end, both sides are paid and the column joins the fight.
        /// </summary>
        private void WatchCeasefire(SimWorld world, EventState s)
        {
            var plan = (CeasefirePlan)s.Plan!;
            if (plan.Released) return;
            var ours = false;
            var theirs = plan.BreakAt >= 0 && world.Time >= plan.BreakAt;
            foreach (var id in s.Units)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                if (v.LastAttackerTeam == Player && !plan.Faction) ours = true;
                if (v.LastFiredAt >= s.StartAt) theirs = true;
            }
            if (ours)
            {
                // We fired first: the enemy keeps its reward and ours is lost.
                PayEnemy(world, s);
                Release(world, s, plan);
                Notice(world, s, "broken", 0f);
                Line(world, s, "broken");
                Finish(world, s, false, "broken");
            }
            else if (theirs)
            {
                // They fired first: their reward is lost and ours paid now.
                Release(world, s, plan);
                Notice(world, s, "betrayed", 0f);
                Line(world, s, "betrayed");
                Finish(world, s, true, "betrayed");
            }
            else if (world.Time >= s.EndsAt)
            {
                PayEnemy(world, s);
                Release(world, s, plan);
                Notice(world, s, "end", 0f);
                Line(world, s, "end");
                Finish(world, s, true, "end");
            }
        }

        private void PayEnemy(SimWorld world, EventState s)
        {
            if (world.TryGetEconomy(Enemy, out var foe)) foe.Cp = MathF.Min(foe.Bank, foe.Cp + s.Def.Whole("enemyCp", 20));
        }

        /// <summary>The ceasefire is over: the column is the enemy's to command again and goes for our side.</summary>
        private void Release(SimWorld world, EventState s, CeasefirePlan plan)
        {
            plan.Released = true;
            foreach (var id in s.Units)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive)
                {
                    v.Truce = false;
                    v.Sworn = false;
                    v.Scripted = false;
                    world.HoldFire(v, false);
                    Push(world, v, _host.EnemyGoal(world) ?? Centre(world, Player));
                }
        }

        private void StepStrikes(SimWorld world)
        {
            for (var i = 0; i < _strikes.Count; i++)
            {
                var (due, id, team, at, towards) = _strikes[i];
                if (world.Time < due) continue;
                _strikes.RemoveAt(i--);
                if (world.Catalog.TryGetSupport(id, out var support)) world.Strikes.Launch(support, team, at, towards);
            }
        }
    }
}
