#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>One boss (or escort) a stress scene adds: its unit id, side and where it starts ("sea": the naval route node nearest the focus; "rally").</summary>
    public readonly struct StressSceneUnit
    {
        public StressSceneUnit(string unit, int team, string at, int count = 1)
        {
            Unit = unit;
            Team = team;
            At = at;
            Count = count;
        }

        public string Unit { get; }
        public int Team { get; }
        public string At { get; }
        public int Count { get; }
    }

    /// <summary>
    /// Map spec BT / owner prompt 62 (lane W2-A): one repeatable stress scene: the map file, the mode, the armies (each side
    /// topped up to <see cref="PerSide"/> ground units from <see cref="Roster"/>), the extra bosses / escorts, the weather
    /// presentation (the Sim's sight stays 1: a mission's own weather is 1, campaign.json weatherSight), the wrecks seeded at the
    /// focus, the seconds measured after the warm-up, the seed, and the metrics each part records.
    /// </summary>
    public sealed class MapStressScene
    {
        public string Id { get; internal set; } = "";
        public string Title { get; internal set; } = "";
        public string MapId { get; internal set; } = "";

        /// <summary>"conquest" (two layered ConquestAi, as the AI MASTER P5 48v48 harness) or "siege" (ModeSessions' siege session: Unity play).</summary>
        public string Mode { get; internal set; } = "conquest";

        public int PerSide { get; internal set; } = 48;
        public IReadOnlyList<string> Roster { get; internal set; } = Array.Empty<string>();
        public IReadOnlyList<StressSceneUnit> Extra { get; internal set; } = Array.Empty<StressSceneUnit>();

        /// <summary>WeatherPresentation kind (presentation and audio only).</summary>
        public string Weather { get; internal set; } = "Clear";

        /// <summary>Vehicles destroyed round the focus at the start, as wrecks (0: none).</summary>
        public int WreckSeed { get; internal set; }

        /// <summary>What the scene centres on: "choke" (the busiest critical street-canyon / gate choke on the main lane), "open"
        /// (the main lane's middle), "naval" (the sea route node nearest the map centre), "wall" (the breach saving the most path).</summary>
        public string Focus { get; internal set; } = "open";

        public float WarmupSeconds { get; internal set; } = 10f;
        public float Seconds { get; internal set; } = 120f;
        public int Seed { get; internal set; } = 7;

        /// <summary>Map metrics (Sim, this lane's harness): route failures, blocked spawn, choke queue, boss route corrections.</summary>
        public static readonly string[] MapMetrics =
        {
            "routeFailures (SevereUnstuck + heavyRouteFailure)", "spawnBlockEvents", "chokeQueueSeconds", "bossRouteReplanCount",
            "navalCollisionEvents", "averageLosEngagementDistance", "laneUsageShare", "staleChokesDropped",
        };

        /// <summary>Render metrics (Unity play, the final part): prompt 62 Render.</summary>
        public static readonly string[] RenderMetrics = { "CPU render ms", "GPU ms", "draw calls / batches", "renderers", "transparent overdraw", "particles" };

        /// <summary>Audio metrics (Unity play, the final part): prompt 62 Audio + 63 (critical warning miss count = 0).</summary>
        public static readonly string[] AudioMetrics =
        {
            "events", "physical voices", "virtual voices", "dropped voices", "priority distribution", "occlusion queries", "audio CPU",
            "critical warning miss count (target 0)",
        };
    }

    /// <summary>
    /// Map spec BT (lane W2-A): the six map stress scenes for the final part (48v48 urban choke, 48v48 open desert, naval boss +
    /// escorts, fortress siege, weather storm, maximum wreck density). Definitions only: the Sim harness
    /// (Tests/EditMode MapVaW2AStressHarness, Explicit) runs the conquest scenes headless for the map metrics; the render and
    /// audio metrics and the siege scene are recorded in Unity play by the final part.
    /// </summary>
    public static class MapStressScenes
    {
        /// <summary>The 48v48 army (the AI MASTER P5 harness's mix).</summary>
        public static readonly string[] Army =
        {
            "main_battle_tank", "main_battle_tank", "ifv", "ifv", "heavy_tank", "tank_destroyer", "aa_vehicle", "mlrs", "artillery",
            "scout_jeep", "armored_car", "armored_car", "light_tank", "mortar_carrier",
        };

        /// <summary>The siege army: the 48v48 mix with breachers.</summary>
        public static readonly string[] SiegeArmy =
        {
            "main_battle_tank", "heavy_tank", "armored_bulldozer", "ifv", "tank_destroyer", "artillery", "mlrs", "aa_vehicle",
            "armored_car", "engineer_vehicle",
        };

        public static readonly IReadOnlyList<MapStressScene> All = new[]
        {
            new MapStressScene
            {
                Id = "urban_choke_48v48", Title = "48v48 in an urban choke", MapId = "metrocity_conquest", Roster = Army, Focus = "choke", Seed = 7,
            },
            new MapStressScene
            {
                Id = "open_desert_48v48", Title = "48v48 open desert", MapId = "saltflat_conquest", Roster = Army, Focus = "open", Seed = 11,
            },
            new MapStressScene
            {
                Id = "naval_boss_escorts", Title = "Naval boss + escorts", MapId = "lighthousebay_conquest", Roster = Army, PerSide = 32, Focus = "naval", Seed = 13,
                Extra = new[]
                {
                    new StressSceneUnit("leviathan", 1, "sea"), new StressSceneUnit("sea_cruiser", 1, "sea", 2), new StressSceneUnit("sea_corvette", 1, "sea", 3),
                    new StressSceneUnit("sea_corvette", 0, "sea", 2), new StressSceneUnit("missile_boat", 0, "sea", 3),
                },
            },
            new MapStressScene
            {
                Id = "fortress_siege", Title = "Fortress siege", MapId = "ashfield_siege", Mode = "siege", Roster = SiegeArmy, PerSide = 40, Focus = "wall", Seed = 17,
            },
            new MapStressScene
            {
                Id = "weather_storm", Title = "Weather storm", MapId = "junglepass_conquest", Roster = Army, Weather = "Storm", Focus = "open", Seed = 19,
            },
            new MapStressScene
            {
                Id = "wreck_density", Title = "Maximum wreck density", MapId = "rustyard_conquest", Roster = Army, WreckSeed = 40, Focus = "choke", Seed = 23,
            },
        };

        public static MapStressScene? Get(string id)
        {
            foreach (var s in All)
                if (s.Id == id) return s;
            return null;
        }

        /// <summary>The scene's focus on <paramref name="g"/>: (what, point); ("none", centre) when the map has no such feature.</summary>
        public static (string what, Vector2 at) FocusOf(MapStressScene scene, GameplayTopology g, Vector2 mapCentre)
        {
            TacticalLane? main = null;
            foreach (var l in g.Lanes)
                if (l.Kind == LaneKind.Main)
                {
                    main = l;
                    break;
                }
            switch (scene.Focus)
            {
                case "choke":
                {
                    TacticalChoke? best = null;
                    foreach (var c in g.Chokes)
                    {
                        if (!c.Critical || c.Type is not (ChokeType.StreetCanyon or ChokeType.Gate or ChokeType.NaturalTerrainGap)) continue;
                        if (main != null && main.DistanceTo(c.Centre) > c.Reach + 6f) continue;
                        if (best == null || c.UsableWidthM < best.UsableWidthM ||
                            (c.UsableWidthM == best.UsableWidthM && Vector2.Distance(c.Centre, mapCentre) < Vector2.Distance(best.Centre, mapCentre))) best = c;
                    }
                    if (best != null) return ($"choke{best.Id} ({best.Type}, {best.UsableWidthM:0.0} m)", best.Centre);
                    break;
                }
                case "naval":
                {
                    NavalNodeInfo? best = null;
                    foreach (var n in g.NavalNodes)
                        if (n.Kind != SeaNodeKind.Exit && (best == null || Vector2.Distance(n.Position, mapCentre) < Vector2.Distance(best.Position, mapCentre))) best = n;
                    if (best != null) return ($"sea node {best.Id}", best.Position);
                    break;
                }
                case "wall":
                {
                    BreachInfo? best = null;
                    foreach (var b in g.Breaches)
                        if (best == null || b.PathCostReductionOnDestroy > best.PathCostReductionOnDestroy) best = b;
                    if (best != null) return ($"breach {best.Id}", best.Centre);
                    break;
                }
            }
            if (main != null && main.Points.Count > 0)
            {
                // The main lane's middle by length.
                var half = main.LengthM * 0.5f;
                var walked = 0f;
                for (var i = 0; i + 1 < main.Points.Count; i++)
                {
                    var d = Vector2.Distance(main.Points[i], main.Points[i + 1]);
                    if (walked + d >= half && d > 0f) return ("main lane middle", Vector2.Lerp(main.Points[i], main.Points[i + 1], (half - walked) / d));
                    walked += d;
                }
                return ("main lane middle", main.Points[main.Points.Count / 2]);
            }
            return ("none", mapCentre);
        }
    }
}
