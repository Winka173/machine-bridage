// Map / visual / audio master spec, lane W1-A (GameplayTopology): the values live in Resources/Data/tunables.json under
// "maps" -> "topology" / "terrainSemantics" / "weatherPresentation"; these defaults equal the file's. Audit references and
// presentation metadata only: nothing here is a combat value (no damage, accuracy, armour, sight or speed changes).
#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    public static partial class SimTunables
    {
        public static partial class Maps
        {
            public static partial class Topology
            {
                /// <summary>maps.topology.sizeBands (m): hull widths that start Medium, Heavy and SuperHeavy (bosses are Boss).</summary>
                public static float[] SizeBands = { 2.9f, 3.4f, 4.5f };
                /// <summary>maps.topology.sideClearance (m): room a hull keeps on each side when it drives a route.</summary>
                public static float SideClearance = 0.5f;
                /// <summary>maps.topology.separationMargin (m): gap between hulls side by side in a choke (spec E1).</summary>
                public static float SeparationMargin = 1f;
                /// <summary>maps.topology.navalSafety (x): a route's curve radius must be this many times a ship's Rmin (spec M: 1.10-1.25).</summary>
                public static float NavalSafety = 1.15f;
                /// <summary>maps.topology.navalMargin (m): water kept between a turning hull and the shore or the map's edge.</summary>
                public static float NavalMargin = 2f;
                /// <summary>maps.topology.directFireRef (m): reference direct-fire reach of the spawn audit (an audit reference, not a weapon).</summary>
                public static float DirectFireRef = 60f;
                /// <summary>maps.topology.artilleryRef (m): reference artillery reach of the spawn and pocket audits.</summary>
                public static float ArtilleryRef = 120f;
                /// <summary>maps.topology.artilleryMinRef (m): reference minimum range of the artillery pocket audit.</summary>
                public static float ArtilleryMinRef = 20f;
                /// <summary>maps.topology.reconRef (m): reference observation reach of the recon audit.</summary>
                public static float ReconRef = 70f;
                /// <summary>maps.topology.towerRangeRef (m): reference tower reach of the breach audit (a camp's defensive coverage).</summary>
                public static float TowerRangeRef = 40f;
                /// <summary>maps.topology.spawnRing (m): the ring round a spawn whose openings are its exits (as the static map audit).</summary>
                public static float SpawnRing = 30f;
                /// <summary>maps.topology.fullExposureShare (share): this share of a spawn exit under enemy direct fire is "the whole exit".</summary>
                public static float FullExposureShare = 0.9f;
                /// <summary>maps.topology.shoreBand (m): ground this far inland of the waterline can belong to a shore fire region.</summary>
                public static float ShoreBand = 24f;
                /// <summary>maps.topology.shoreStep (m): the waterline is cut into shore fire regions this long.</summary>
                public static float ShoreStep = 16f;
                /// <summary>maps.topology.stagingDistance (m): staging areas stand this far back from an objective's edge along a lane.</summary>
                public static float StagingDistance = 45f;
                /// <summary>maps.topology.stagingRadius (m): a staging area's radius.</summary>
                public static float StagingRadius = 12f;
                /// <summary>maps.topology.positionSpacing (m): the least distance between two tactical positions of one kind.</summary>
                public static float PositionSpacing = 15f;
                /// <summary>maps.topology.positionsPerObjective (count): direct-fire positions kept per objective.</summary>
                public static int PositionsPerObjective = 4;
                /// <summary>maps.topology.laneAlternatives (count): alternative camp-to-camp lanes searched after the main one.</summary>
                public static int LaneAlternatives = 3;
                /// <summary>maps.topology.lanePenalty (x): cost added round a found lane before the next search (as the static map audit).</summary>
                public static float LanePenalty = 25f;
                /// <summary>maps.topology.sizeClassFeasibility (flag): the buying AI also asks whether the unit's size class fits the route. Off: P0-B as before.</summary>
                public static bool SizeClassFeasibility;
                /// <summary>maps.topology.telemetry (flag): the map telemetry counters (spec CA / 64) are kept.</summary>
                public static bool Telemetry = true;
                /// <summary>maps.topology.telemetrySeconds (s): the telemetry's sampling period.</summary>
                public static float TelemetrySeconds = 1f;
            }

            /// <summary>
            /// maps.terrainSemantics.&lt;tag&gt; (spec P): per terrain tag [traction, visualCover, artilleryExposure, mineSuitability,
            /// largeVehiclePenalty], 0-1 metadata for pathing, AI positioning and presentation. Movement cost and concealment are
            /// not here: they are TerrainRules' own values (path cost, forest sight). Never a combat buff.
            /// </summary>
            public static partial class TerrainSemantics
            {
                public static float[] Normal = { 0.9f, 0f, 1f, 0.6f, 0f };
                public static float[] Road = { 1f, 0f, 1f, 1f, 0f };
                public static float[] Rough = { 0.7f, 0.1f, 0.9f, 0.8f, 0.2f };
                public static float[] Forest = { 0.75f, 0.5f, 0.8f, 0.4f, 0.4f };
                public static float[] ShallowWater = { 0.5f, 0f, 1f, 0f, 0.5f };
            }

            /// <summary>
            /// maps.weatherPresentation.&lt;weather&gt; (spec Q): presentation metadata only, never visibility (campaign.json
            /// weatherSight keeps it): [fogDensity, ambientLight, cloudiness, rainIntensity, snowIntensity, windStrength,
            /// windDirectionDeg, lightningIntensity, dustIntensity, contrailVisibility, muzzleFlashVisibility,
            /// lowpassEnvironmentAmount, telegraphBoost]. telegraphBoost (x) is the least boost a danger telegraph gets in that
            /// weather so it never vanishes (spec Q1).
            /// </summary>
            public static partial class WeatherPresentation
            {
                public static float[] Clear = { 0f, 1f, 0.1f, 0f, 0f, 0.2f, 225f, 0f, 0f, 1f, 1f, 0f, 1f };
                public static float[] Overcast = { 0.05f, 0.75f, 0.8f, 0f, 0f, 0.35f, 225f, 0f, 0f, 0.8f, 1.1f, 0.05f, 1f };
                public static float[] Rain = { 0.15f, 0.6f, 0.9f, 0.6f, 0f, 0.5f, 210f, 0f, 0f, 0.5f, 1.15f, 0.2f, 1.1f };
                public static float[] Storm = { 0.25f, 0.45f, 1f, 1f, 0f, 0.9f, 200f, 0.8f, 0f, 0.3f, 1.25f, 0.35f, 1.2f };
                public static float[] Snow = { 0.3f, 0.8f, 0.9f, 0f, 0.8f, 0.4f, 330f, 0f, 0f, 0.6f, 1.1f, 0.3f, 1.2f };
                public static float[] Sandstorm = { 0.45f, 0.6f, 0.4f, 0f, 0f, 1f, 90f, 0f, 1f, 0.2f, 1.2f, 0.4f, 1.3f };
                public static float[] Fog = { 0.8f, 0.65f, 0.6f, 0f, 0f, 0.1f, 180f, 0f, 0f, 0.2f, 1.2f, 0.45f, 1.3f };
                public static float[] Night = { 0.1f, 0.2f, 0.3f, 0f, 0f, 0.2f, 225f, 0f, 0f, 0.4f, 1.6f, 0.1f, 1f };
            }
        }

        private static readonly Entry[] MapTopologyW1A =
        {
            Entry.FloatArray("maps.topology.sizeBands", "m", () => Maps.Topology.SizeBands, v => Maps.Topology.SizeBands = v),
            new Entry("maps.topology.sideClearance", "m", () => Maps.Topology.SideClearance, v => Maps.Topology.SideClearance = (float)v),
            new Entry("maps.topology.separationMargin", "m", () => Maps.Topology.SeparationMargin, v => Maps.Topology.SeparationMargin = (float)v),
            new Entry("maps.topology.navalSafety", "x", () => Maps.Topology.NavalSafety, v => Maps.Topology.NavalSafety = (float)v),
            new Entry("maps.topology.navalMargin", "m", () => Maps.Topology.NavalMargin, v => Maps.Topology.NavalMargin = (float)v),
            new Entry("maps.topology.directFireRef", "m", () => Maps.Topology.DirectFireRef, v => Maps.Topology.DirectFireRef = (float)v),
            new Entry("maps.topology.artilleryRef", "m", () => Maps.Topology.ArtilleryRef, v => Maps.Topology.ArtilleryRef = (float)v),
            new Entry("maps.topology.artilleryMinRef", "m", () => Maps.Topology.ArtilleryMinRef, v => Maps.Topology.ArtilleryMinRef = (float)v),
            new Entry("maps.topology.reconRef", "m", () => Maps.Topology.ReconRef, v => Maps.Topology.ReconRef = (float)v),
            new Entry("maps.topology.towerRangeRef", "m", () => Maps.Topology.TowerRangeRef, v => Maps.Topology.TowerRangeRef = (float)v),
            new Entry("maps.topology.spawnRing", "m", () => Maps.Topology.SpawnRing, v => Maps.Topology.SpawnRing = (float)v),
            new Entry("maps.topology.fullExposureShare", "share", () => Maps.Topology.FullExposureShare, v => Maps.Topology.FullExposureShare = (float)v),
            new Entry("maps.topology.shoreBand", "m", () => Maps.Topology.ShoreBand, v => Maps.Topology.ShoreBand = (float)v),
            new Entry("maps.topology.shoreStep", "m", () => Maps.Topology.ShoreStep, v => Maps.Topology.ShoreStep = (float)v),
            new Entry("maps.topology.stagingDistance", "m", () => Maps.Topology.StagingDistance, v => Maps.Topology.StagingDistance = (float)v),
            new Entry("maps.topology.stagingRadius", "m", () => Maps.Topology.StagingRadius, v => Maps.Topology.StagingRadius = (float)v),
            new Entry("maps.topology.positionSpacing", "m", () => Maps.Topology.PositionSpacing, v => Maps.Topology.PositionSpacing = (float)v),
            new Entry("maps.topology.positionsPerObjective", "count", () => Maps.Topology.PositionsPerObjective, v => Maps.Topology.PositionsPerObjective = (int)Math.Round(v)),
            new Entry("maps.topology.laneAlternatives", "count", () => Maps.Topology.LaneAlternatives, v => Maps.Topology.LaneAlternatives = (int)Math.Round(v)),
            new Entry("maps.topology.lanePenalty", "x", () => Maps.Topology.LanePenalty, v => Maps.Topology.LanePenalty = (float)v),
            new Entry("maps.topology.sizeClassFeasibility", "flag", () => Maps.Topology.SizeClassFeasibility ? 1 : 0, v => Maps.Topology.SizeClassFeasibility = v >= 0.5, flag: true),
            new Entry("maps.topology.telemetry", "flag", () => Maps.Topology.Telemetry ? 1 : 0, v => Maps.Topology.Telemetry = v >= 0.5, flag: true),
            new Entry("maps.topology.telemetrySeconds", "s", () => Maps.Topology.TelemetrySeconds, v => Maps.Topology.TelemetrySeconds = (float)v),
            Entry.FloatArray("maps.terrainSemantics.normal", "share", () => Maps.TerrainSemantics.Normal, v => Maps.TerrainSemantics.Normal = v),
            Entry.FloatArray("maps.terrainSemantics.road", "share", () => Maps.TerrainSemantics.Road, v => Maps.TerrainSemantics.Road = v),
            Entry.FloatArray("maps.terrainSemantics.rough", "share", () => Maps.TerrainSemantics.Rough, v => Maps.TerrainSemantics.Rough = v),
            Entry.FloatArray("maps.terrainSemantics.forest", "share", () => Maps.TerrainSemantics.Forest, v => Maps.TerrainSemantics.Forest = v),
            Entry.FloatArray("maps.terrainSemantics.shallowWater", "share", () => Maps.TerrainSemantics.ShallowWater, v => Maps.TerrainSemantics.ShallowWater = v),
            Entry.FloatArray("maps.weatherPresentation.clear", "x", () => Maps.WeatherPresentation.Clear, v => Maps.WeatherPresentation.Clear = v),
            Entry.FloatArray("maps.weatherPresentation.overcast", "x", () => Maps.WeatherPresentation.Overcast, v => Maps.WeatherPresentation.Overcast = v),
            Entry.FloatArray("maps.weatherPresentation.rain", "x", () => Maps.WeatherPresentation.Rain, v => Maps.WeatherPresentation.Rain = v),
            Entry.FloatArray("maps.weatherPresentation.storm", "x", () => Maps.WeatherPresentation.Storm, v => Maps.WeatherPresentation.Storm = v),
            Entry.FloatArray("maps.weatherPresentation.snow", "x", () => Maps.WeatherPresentation.Snow, v => Maps.WeatherPresentation.Snow = v),
            Entry.FloatArray("maps.weatherPresentation.sandstorm", "x", () => Maps.WeatherPresentation.Sandstorm, v => Maps.WeatherPresentation.Sandstorm = v),
            Entry.FloatArray("maps.weatherPresentation.fog", "x", () => Maps.WeatherPresentation.Fog, v => Maps.WeatherPresentation.Fog = v),
            Entry.FloatArray("maps.weatherPresentation.night", "x", () => Maps.WeatherPresentation.Night, v => Maps.WeatherPresentation.Night = v),
        };
    }
}
