#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>Map spec D1: how big a hull is for route clearance (hull width bands; bosses are Boss).</summary>
    public enum VehicleSizeClass
    {
        Light,
        Medium,
        Heavy,
        SuperHeavy,
        Boss,
    }

    /// <summary>Map spec D1: one size class's reference hull, measured from the catalog's ground vehicles.</summary>
    public readonly struct SizeClassInfo
    {
        public SizeClassInfo(VehicleSizeClass cls, int members, float referenceWidth, float medianWidth, float referenceLength,
            float medianSpeed, int clearanceCells)
        {
            Class = cls;
            Members = members;
            ReferenceWidth = referenceWidth;
            MedianWidth = medianWidth;
            ReferenceLength = referenceLength;
            MedianSpeed = medianSpeed;
            ClearanceCells = clearanceCells;
        }

        public VehicleSizeClass Class { get; }

        /// <summary>Catalog ground vehicles in the class.</summary>
        public int Members { get; }

        /// <summary>The widest hull of the class (m; Boss: the median boss hull): a route for the class must fit it.</summary>
        public float ReferenceWidth { get; }

        /// <summary>The class's median hull width (m): choke capacity (spec E1).</summary>
        public float MedianWidth { get; }

        /// <summary>The longest hull of the class (m): turn space.</summary>
        public float ReferenceLength { get; }

        /// <summary>The class's median drive speed (m/s).</summary>
        public float MedianSpeed { get; }

        /// <summary>The least clearance (navigation cells to the nearest closed cell) a route cell needs for the class.</summary>
        public int ClearanceCells { get; }

        /// <summary>The room (m) a hull of the class needs to pivot: half its diagonal.</summary>
        public float TurnRadius => 0.5f * MathF.Sqrt(ReferenceLength * ReferenceLength + ReferenceWidth * ReferenceWidth);
    }

    /// <summary>Map spec C / D: what a topology anchor is.</summary>
    public enum AnchorKind
    {
        Spawn,
        MissionSpawn,
        EntryGate,
        Objective,
        Base,
        Fortress,
        Battery,
        Landing,
        Pier,
        Neutral,
        NavalLane,
        NavalNode,
        BossRoute,
    }

    /// <summary>
    /// Map spec D: a place the game names (a spawn, an objective, a base, the fortress, a coastal battery, a naval lane, a boss
    /// route's point) resolved to its component per mobility domain and the size classes that reach it from its side's spawn.
    /// </summary>
    public sealed class TopologyAnchor
    {
        public string Id { get; internal set; } = "";
        public AnchorKind Kind { get; internal set; }
        public Vector2 Position { get; internal set; }

        /// <summary>Its side (-1: neither).</summary>
        public int Team { get; internal set; } = -1;

        /// <summary>The domain it must resolve in (Ground for land places, Naval for the sea's, Air: always).</summary>
        public MobilityDomain Domain { get; internal set; }

        public int GroundComponent { get; internal set; }
        public int NavalComponent { get; internal set; }
        public int AmphibiousComponent { get; internal set; }

        /// <summary>Per size class: its component in the class's graph (0: no cell of the class near it).</summary>
        public int[] ClassComponent { get; } = new int[5];

        /// <summary>Whether it resolved in its domain (a land place: ground or amphibious; a sea place: naval).</summary>
        public bool Resolved { get; internal set; }

        public int ComponentOf(MobilityDomain domain) => domain switch
        {
            MobilityDomain.Ground => GroundComponent,
            MobilityDomain.Naval => NavalComponent,
            MobilityDomain.Amphibious => AmphibiousComponent,
            MobilityDomain.Air => 1,
            _ => 0,
        };

        public override string ToString() => $"{Kind} {Id} g{GroundComponent} n{NavalComponent} a{AmphibiousComponent}";
    }

    /// <summary>The passage shapes the TrafficCoordinator manages (AI MASTER spec 30): the measured shape of a choke.</summary>
    public enum PassageShape
    {
        Gate,
        Choke,
        Bridge,
        NarrowRoad,
    }

    /// <summary>Map spec E: what a choke is on the ground.</summary>
    public enum ChokeType
    {
        Gate,
        Bridge,
        StreetCanyon,
        WallBreach,
        RiverCrossing,
        RailCrossing,
        HarborThroat,
        NaturalTerrainGap,
    }

    /// <summary>Map spec E2: a queue area before a choke (an oriented box), and whether it is safe to wait in.</summary>
    public readonly struct QueueArea
    {
        public QueueArea(Vector2 centre, Vector2 through, float halfAlong, float halfAcross, bool safe, string issue)
        {
            Centre = centre;
            Through = through;
            HalfAlong = halfAlong;
            HalfAcross = halfAcross;
            Safe = safe;
            Issue = issue;
        }

        public Vector2 Centre { get; }
        public Vector2 Through { get; }
        public float HalfAlong { get; }
        public float HalfAcross { get; }

        /// <summary>Spec E2: off the spawn clear zones and the capture circles, on open ground.</summary>
        public bool Safe { get; }

        /// <summary>Why it is not safe ("" when safe).</summary>
        public string Issue { get; }
    }

    /// <summary>
    /// Map spec E: a tactical choke. The geometry (centre, way through, open width, length, shape) is the measure the
    /// TrafficCoordinator's passages use (moved here from it: one measure for both); the capacity fields follow spec E1.
    /// </summary>
    public sealed class TacticalChoke
    {
        public int Id { get; internal set; }

        /// <summary>Where it came from: a lane-map doorway, or a ground choke of the map topology.</summary>
        public bool FromDoorway { get; internal set; }

        public PassageShape Shape { get; internal set; }
        public ChokeType Type { get; internal set; }
        public Vector2 Centre { get; internal set; }

        /// <summary>The way through (unit; its sign is arbitrary).</summary>
        public Vector2 Through { get; internal set; } = Vector2.UnitY;

        /// <summary>Open (hull-centre) width across it (m): what the traffic coordinator's lanes use.</summary>
        public float OpenWidth { get; internal set; }

        public float Length { get; internal set; }

        /// <summary>Spec E: the physical clear width (m): the open width plus the obstacles' grown margin on both sides.</summary>
        public float UsableWidthM { get; internal set; }

        public int MaxLightSideBySide { get; internal set; }
        public int MaxMediumSideBySide { get; internal set; }
        public int MaxHeavySideBySide { get; internal set; }

        /// <summary>Medium hulls a second through it at the class's median speed (AI MASTER spec 189's rule).</summary>
        public float EstimatedThroughput { get; internal set; }

        /// <summary>Two medium hulls fit side by side: traffic both ways at once.</summary>
        public bool OppositeTrafficAllowed { get; internal set; }

        public QueueArea QueueAreaA { get; internal set; }
        public QueueArea QueueAreaB { get; internal set; }

        /// <summary>The largest size class whose route clearance holds through it.</summary>
        public VehicleSizeClass LargestClass { get; internal set; }

        /// <summary>On a main route of the lane map (an army's way between camps and objectives).</summary>
        public bool Critical { get; internal set; }

        /// <summary>Its ground component.</summary>
        public int Component { get; internal set; }

        /// <summary>How far round the centre counts as in it (the traffic passage's reach).</summary>
        public float Reach => MathF.Max(Length, OpenWidth) * 0.5f + 3f;

        public bool Contains(Vector2 p)
        {
            var d = p - Centre;
            var along = MathF.Abs(Vector2.Dot(d, Through));
            var across = MathF.Abs(Vector2.Dot(d, new Vector2(Through.Y, -Through.X)));
            return along <= Length * 0.5f + 1f && across <= OpenWidth * 0.5f + 1f;
        }

        public override string ToString() => $"{Type} {Id} ({Centre.X:0},{Centre.Y:0}) w{UsableWidthM:0.0} l{Length:0.0}";
    }

    /// <summary>Map spec F: a tactical lane's role.</summary>
    public enum LaneKind
    {
        Main,
        Secondary,
        Flank,
        Service,
        BossCorridor,
    }

    /// <summary>Map spec F: one-way alternating or both ways.</summary>
    public enum LaneDirectionality
    {
        TwoWay,
        Alternating,
    }

    /// <summary>Map spec F: a tactical lane (a polyline on open ground) and its semantics.</summary>
    public sealed class TacticalLane
    {
        public string Id { get; internal set; } = "";
        public LaneKind Kind { get; internal set; }
        public string From { get; internal set; } = "";
        public string To { get; internal set; } = "";
        public IReadOnlyList<Vector2> Points { get; internal set; } = Array.Empty<Vector2>();
        public float LengthM { get; internal set; }

        /// <summary>The lane's P10 physical width (m).</summary>
        public float LaneWidth { get; internal set; }

        /// <summary>The narrowest physical width along it (m).</summary>
        public float MinWidth { get; internal set; }

        public LaneDirectionality Directionality { get; internal set; }

        /// <summary>The largest size class whose clearance holds along the whole lane.</summary>
        public VehicleSizeClass VehicleClassSupport { get; internal set; }

        /// <summary>A medium hull's speed along it (m/s: the class's median speed times the terrain's mean speed factor).</summary>
        public float ExpectedTravelSpeed { get; internal set; }

        /// <summary>The chokes it runs through (ids).</summary>
        public IReadOnlyList<int> ChokeDependency { get; internal set; } = Array.Empty<int>();

        /// <summary>The objectives it passes (anchor ids).</summary>
        public IReadOnlyList<string> ObjectiveCoverage { get; internal set; } = Array.Empty<string>();

        /// <summary>Medium hulls a second it carries (its tightest choke, else its width).</summary>
        public float TrafficCapacity { get; internal set; }

        /// <summary>Spec F: fire support never parks on it (main transit and boss corridors).</summary>
        public bool ParkingForbidden { get; internal set; }

        /// <summary>Distance (m) from a point to the lane's polyline.</summary>
        public float DistanceTo(Vector2 p)
        {
            var best = float.MaxValue;
            for (var i = 0; i + 1 < Points.Count; i++)
            {
                var a = Points[i];
                var ab = Points[i + 1] - a;
                var len2 = ab.LengthSquared();
                var t = len2 > 1e-6f ? Math.Clamp(Vector2.Dot(p - a, ab) / len2, 0f, 1f) : 0f;
                best = MathF.Min(best, Vector2.Distance(p, a + ab * t));
            }
            return Points.Count == 1 ? Vector2.Distance(p, Points[0]) : best;
        }
    }

    /// <summary>Map spec G: a team spawn's clear zone (the traffic coordinator's exit box, clear zone and rally ring radii).</summary>
    public readonly struct SpawnClearZone
    {
        public SpawnClearZone(int team, Vector2 centre, float exitRadius, float clearRadius, float rallyRadius)
        {
            Team = team;
            Centre = centre;
            ExitRadius = exitRadius;
            ClearRadius = clearRadius;
            RallyRadius = rallyRadius;
        }

        public int Team { get; }
        public Vector2 Centre { get; }
        public float ExitRadius { get; }
        public float ClearRadius { get; }
        public float RallyRadius { get; }
        public bool Contains(Vector2 p) => Vector2.DistanceSquared(p, Centre) < ClearRadius * ClearRadius;
    }

    /// <summary>Map spec G: a spawn's fairness metrics and flags.</summary>
    public sealed class SpawnFairness
    {
        public string SpawnId { get; internal set; } = "";
        public int Team { get; internal set; }
        public Vector2 Position { get; internal set; }

        /// <summary>Share of the clear zone's ground with a line of fire from ground the enemy can reach (within the direct-fire reference).</summary>
        public float EnemyDirectLosAtSpawn { get; internal set; }

        /// <summary>The same share for the exit openings on the spawn ring.</summary>
        public float EnemyDirectLosAtExit { get; internal set; }

        /// <summary>Share of the clear zone within the artillery reference of the enemy's own spawn ("from a normal position").</summary>
        public float EnemyArtilleryCoverageAtSpawn { get; internal set; }

        /// <summary>Ground path (m) from the spawn to the nearest cell beside fire-blocking cover.</summary>
        public float SpawnToFirstCoverM { get; internal set; }

        /// <summary>Total physical width of the exit openings on the ring (m); +inf when the ring is open all round.</summary>
        public float SpawnExitWidthM { get; internal set; }

        /// <summary>The narrowest exit opening (m).</summary>
        public float NarrowestExitM { get; internal set; }

        /// <summary>Exit openings beyond the first (0: one way out; the ring open all round counts 3).</summary>
        public int AlternateExitCount { get; internal set; }

        /// <summary>Medium hulls the clear zone holds.</summary>
        public int SpawnQueueCapacity { get; internal set; }

        /// <summary>Seconds a medium hull of the enemy needs from its spawn to this one.</summary>
        public float EnemyRushEta { get; internal set; }

        /// <summary>Seconds a medium hull needs from this spawn to the nearest objective.</summary>
        public float FriendlyObjectiveEta { get; internal set; }

        /// <summary>The spec G1 flags raised (empty: fair).</summary>
        public List<string> Flags { get; } = new();
    }

    /// <summary>Map spec K: a stretch of the shore from which ground units can affect a naval lane.</summary>
    public sealed class ShoreFireRegion
    {
        public int Id { get; internal set; }
        public int GroundComponentId { get; internal set; }

        /// <summary>The waterline stretch (u along the coast, from - to) and its two ends.</summary>
        public float FromU { get; internal set; }
        public float ToU { get; internal set; }
        public Vector2 FromPoint { get; internal set; }
        public Vector2 ToPoint { get; internal set; }

        /// <summary>The region's ground cells' centre.</summary>
        public Vector2 Centre { get; internal set; }

        public int Cells { get; internal set; }

        /// <summary>The nearest naval lane (id) and the distances (m) from the region's ground to its line.</summary>
        public string NearestLane { get; internal set; } = "";
        public float MinDistanceToNavalLane { get; internal set; }
        public float MaxDistanceToNavalLane { get; internal set; }

        /// <summary>Flat battlefield: 0 (the Sim has no height).</summary>
        public float Elevation { get; internal set; }

        /// <summary>Share of lines from the region's cells to the nearest lane that no fire-blocking cover stops.</summary>
        public float LosQuality { get; internal set; }

        /// <summary>Share of the region's cells beside fire-blocking cover.</summary>
        public float CoverScore { get; internal set; }

        /// <summary>Beyond this weapon range (m) nothing more of the lanes is reached from here (the farthest lane line + its corridor).</summary>
        public float MaxUsefulWeaponRange { get; internal set; }
    }

    /// <summary>Map spec L: a sea route node's kinematic fields.</summary>
    public sealed class NavalNodeInfo
    {
        public int Index { get; internal set; }
        public string Id { get; internal set; } = "";
        public SeaNodeKind Kind { get; internal set; }
        public string? Lane { get; internal set; }
        public Vector2 Position { get; internal set; }
        public int Component { get; internal set; }

        /// <summary>The route corridor's width here (m).</summary>
        public float Width { get; internal set; }

        /// <summary>The tightest turn radius a route through this node allows (m; +inf on a straight run).</summary>
        public float CurveRadiusM { get; internal set; } = float.PositiveInfinity;

        /// <summary>Water (m) from the lane line to the shore side and the sea side (the map's edge).</summary>
        public float BroadsideRoomLeft { get; internal set; }
        public float BroadsideRoomRight { get; internal set; }

        public float MaxRecommendedShipRadius { get; internal set; }
        public float MaxRecommendedShipLength { get; internal set; }

        /// <summary>A passing bay (holding node) within the graph's bay reach, or a cross link to another lane here.</summary>
        public bool PassingAllowed { get; internal set; }
        public string? PassingBay { get; internal set; }

        /// <summary>Every boss ship that may sail it fits here and turns here (with the controller's mitigations).</summary>
        public bool BossSafe { get; internal set; } = true;

        /// <summary>Coastal batteries and shore fire regions that reach this node.</summary>
        public int ShoreThreatExposure { get; internal set; }
    }

    /// <summary>Map spec L: a sea route segment's kinematic fields.</summary>
    public sealed class NavalSegmentInfo
    {
        public int Index { get; internal set; }
        public string A { get; internal set; } = "";
        public string B { get; internal set; } = "";
        public SeaSegmentKind Kind { get; internal set; }
        public bool OneWay { get; internal set; }
        public string? Lane { get; internal set; }
        public float Length { get; internal set; }

        /// <summary>Heading (degrees, 0 = +z, clockwise) leaving A, and arriving at B.</summary>
        public float EntryHeading { get; internal set; }
        public float ExitHeading { get; internal set; }

        /// <summary>The turn radius the segment allows as an S-curve between its two lines (+inf: straight on).</summary>
        public float CurveRadiusM { get; internal set; } = float.PositiveInfinity;

        public bool PassingAllowed { get; internal set; }

        /// <summary>No overtaking: a one-way segment or one too narrow for two hulls abreast.</summary>
        public bool NoOvertake { get; internal set; }
    }

    /// <summary>Map spec M: one ship's turn-radius check against one route manoeuvre.</summary>
    public sealed class NavalTurnAudit
    {
        public string Ship { get; internal set; } = "";
        public bool Boss { get; internal set; }

        /// <summary>"lane-change", "bay", "turnabout" or "straight".</summary>
        public string Manoeuvre { get; internal set; } = "";

        /// <summary>The node or segment checked.</summary>
        public string Where { get; internal set; } = "";

        public float Speed { get; internal set; }

        /// <summary>Degrees a second.</summary>
        public float TurnRateDeg { get; internal set; }

        /// <summary>Rmin = speed / angular speed (m).</summary>
        public float Rmin { get; internal set; }

        /// <summary>Rmin x the safety factor (m).</summary>
        public float Required { get; internal set; }

        /// <summary>What the route gives (m).</summary>
        public float Available { get; internal set; }

        public bool Pass { get; internal set; }

        /// <summary>A failed check the boss controller handles (coming about at its turnabout throttle: P0-C spec 52).</summary>
        public bool Mitigated { get; internal set; }

        public string Note { get; internal set; } = "";
    }

    /// <summary>Map spec O: what destroying one wall segment opens.</summary>
    public sealed class BreachInfo
    {
        public string Id { get; internal set; } = "";
        public string Owner { get; internal set; } = "";
        public int Ring { get; internal set; }
        public Vector2 Centre { get; internal set; }
        public float OpeningWidthM { get; internal set; }

        /// <summary>The attacker routes ("rally1->hq0") the segment lengthens while it stands.</summary>
        public List<string> BlockedRouteIds { get; } = new();

        /// <summary>The largest saving (m) on those routes once it is down.</summary>
        public float PathCostReductionOnDestroy { get; internal set; }

        /// <summary>Size classes the line's gate is too narrow for that the breach lets through.</summary>
        public List<VehicleSizeClass> HeavyAccessGained { get; } = new();

        /// <summary>A target the attacker could not reach before (or reaches 25 % sooner).</summary>
        public bool ObjectiveAccessGained { get; internal set; }

        /// <summary>The attacker reaches the targets with the segment standing (through the gate).</summary>
        public bool AlternateRouteExists { get; internal set; }

        /// <summary>The owner's towers and gun segments within the tower reach reference.</summary>
        public int DefensiveTowerCoverage { get; internal set; }
    }

    /// <summary>Map spec J: a tactical position's kind.</summary>
    public enum TacticalPositionKind
    {
        DirectFire,
        ArtilleryPocket,
        ReconObservation,
        HullDown,
    }

    /// <summary>Map spec J: a generated, role-aware position (scores 0-1; total is the kind's weighted sum).</summary>
    public sealed class TacticalPosition
    {
        public string Id { get; internal set; } = "";
        public TacticalPositionKind Kind { get; internal set; }
        public Vector2 Position { get; internal set; }

        /// <summary>The side it serves (-1: either).</summary>
        public int Team { get; internal set; } = -1;

        /// <summary>The objective (or lane) it watches.</summary>
        public string Subject { get; internal set; } = "";

        public float Score { get; internal set; }

        /// <summary>Its score terms by name (LOS, cover, escape, ...).</summary>
        public Dictionary<string, float> Terms { get; } = new();
    }

    /// <summary>Map spec I: a staging / rally area.</summary>
    public sealed class StagingArea
    {
        public string Id { get; internal set; } = "";
        public Vector2 Centre { get; internal set; }
        public float Radius { get; internal set; }
        public int Team { get; internal set; } = -1;
        public string Objective { get; internal set; } = "";
        public int CapacityLight { get; internal set; }
        public int CapacityHeavy { get; internal set; }
        public float CoverScore { get; internal set; }
        public float ThreatExposure { get; internal set; }
        public float DistanceToObjective { get; internal set; }
        public int LanesAvailable { get; internal set; }
    }

    /// <summary>Map spec P: a terrain tag's semantic fields (metadata for pathing, AI positioning and presentation; no combat buff).</summary>
    public readonly struct TerrainSemantics
    {
        public TerrainSemantics(TerrainTag tag, float movementCost, float traction, float concealment, float visualCover,
            float directFireCover, float artilleryExposure, float mineSuitability, float hullDownPotential, float largeVehiclePenalty)
        {
            Tag = tag;
            MovementCost = movementCost;
            Traction = traction;
            Concealment = concealment;
            VisualCover = visualCover;
            DirectFireCover = directFireCover;
            ArtilleryExposure = artilleryExposure;
            MineSuitability = mineSuitability;
            HullDownPotential = hullDownPotential;
            LargeVehiclePenalty = largeVehiclePenalty;
        }

        public TerrainTag Tag { get; }
        public float MovementCost { get; }
        public float Traction { get; }
        public float Concealment { get; }
        public float VisualCover { get; }
        public float DirectFireCover { get; }
        public float ArtilleryExposure { get; }
        public float MineSuitability { get; }
        public float HullDownPotential { get; }
        public float LargeVehiclePenalty { get; }
    }

    /// <summary>Map spec D1 / CI: one size class's route from a spawn to an objective.</summary>
    public sealed class RouteAudit
    {
        public string From { get; internal set; } = "";
        public string To { get; internal set; } = "";
        public VehicleSizeClass Class { get; internal set; }
        public bool Reachable { get; internal set; }
        public float LengthM { get; internal set; }
        public float MinClearWidthM { get; internal set; }

        /// <summary>The least pivot room (m) at the route's corners (+inf: no corner).</summary>
        public float MinTurnSpaceM { get; internal set; } = float.PositiveInfinity;

        /// <summary>The narrowest gate and bridge it crosses (m; +inf: none).</summary>
        public float GateMinWidthM { get; internal set; } = float.PositiveInfinity;
        public float BridgeMinWidthM { get; internal set; } = float.PositiveInfinity;

        /// <summary>Its corners all leave the class's pivot room (strict: at the corner cell a shortest path hugs; information).</summary>
        public bool TurnsFit { get; internal set; } = true;

        /// <summary>Lane W2-A: the least pivot room (m) a hull finds swinging wide at the route's corners (the best clearance within its pivot radius; +inf: no corner).</summary>
        public float SwingTurnSpaceM { get; internal set; } = float.PositiveInfinity;

        /// <summary>Lane W2-A: every corner leaves the pivot room when the hull swings wide (false: ROUTE_TURN_TIGHT, a real tight corner).</summary>
        public bool TurnsFitSwing { get; internal set; } = true;
    }

    /// <summary>Map spec U: a map warning's severity.</summary>
    public enum WarningSeverity
    {
        Info,
        Yellow,
        Red,
    }

    /// <summary>Map spec U: a generated map warning (its status, owner and reason come from the review file in Docs/maps).</summary>
    public sealed class MapWarning
    {
        public string WarningId { get; internal set; } = "";
        public WarningSeverity Severity { get; internal set; }
        public string Code { get; internal set; } = "";
        public string Metric { get; internal set; } = "";
        public string Value { get; internal set; } = "";
        public string Threshold { get; internal set; } = "";
        public string Subject { get; internal set; } = "";
    }

    /// <summary>Map spec BW: one load gate's result.</summary>
    public readonly struct LoadGateResult
    {
        public LoadGateResult(string gate, bool pass, string detail)
        {
            Gate = gate;
            Pass = pass;
            Detail = detail;
        }

        public string Gate { get; }
        public bool Pass { get; }
        public string Detail { get; }
        public override string ToString() => $"{Gate}: {(Pass ? "PASS" : "FAIL")} {Detail}";
    }
}
