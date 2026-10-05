#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Part I: where the line stands and who leads it.</summary>
    public enum FrontlinePolicy : byte
    {
        Advance,
        HoldLine,
        ObjectiveBody,
        ConvoyScreen,
        BossFocus,
        Mobile,
        Survival,
    }

    /// <summary>Part I / J: what a fire-support group anchors on (never the squad centroid).</summary>
    public enum FireSupportPolicy : byte
    {
        /// <summary>The friendly front / combat centroid as a logical anchor (Assault, Deathmatch, Duel).</summary>
        FrontLogical,

        /// <summary>Covers the current objective and its approaches from outside the capture circle (Conquest, Hill, Capture).</summary>
        ObjectiveCover,

        /// <summary>Behind the first defence line, launchers never meet the enemy (Defend, Hold, Protect, Outpost).</summary>
        DefenceLine,

        /// <summary>Pocket to pocket ahead of the convoy, not glued to it (Escort, Evacuate).</summary>
        ConvoyLeapfrog,

        /// <summary>The boss's predicted firing region, outside its telegraphs (BossRush, Boss goal).</summary>
        BossPredict,

        /// <summary>Layers on the defences: mortar closest, MLRS farther, heavy artillery deepest; shoot and scoot (Siege, Weekly).</summary>
        SiegeLayers,

        /// <summary>2-3 prepared pockets round the base, rotated by wave direction (Survival, Endless).</summary>
        PreparedPockets,

        /// <summary>The quarry's predicted area with enough intel, else the front (Hunt, Intercept).</summary>
        InterceptPredict,

        /// <summary>Deep and silent unless the target is worth breaking the quiet (Recon).</summary>
        Quiet,
    }

    /// <summary>Part I: pursuit.</summary>
    public enum PursuitPolicy : byte
    {
        Normal,
        Leash,
        NoChase,
    }

    /// <summary>Part I / J: what makes a fire-support group move.</summary>
    [Flags]
    public enum RepositionTrigger
    {
        None = 0,
        Utilization = 1,
        FrontMoved = 2,
        RangeBandLost = 4,
        CounterBattery = 8,
        RouteChanged = 16,
        ObjectiveUncovered = 32,
        WaveDirection = 64,
        Rotation = 128,
        PocketCompromised = 256,
        PhaseChange = 512,
        TerrainChange = 1024,
        All = 2047,
    }

    /// <summary>One Part I doctrine: the base RoleDoctrine's mode override (I15: base + mode + phase, no copies).</summary>
    public sealed class ModeDoctrine
    {
        public string Id { get; internal set; } = "balanced_objective";
        public string? Inherits { get; internal set; }
        public FrontlinePolicy Frontline { get; internal set; } = FrontlinePolicy.Advance;
        public FireSupportPolicy FireSupport { get; internal set; } = FireSupportPolicy.FrontLogical;

        /// <summary>Where in the Part I1 band the anchor sits: 0 its near end (forward), 1 its far end (deep).</summary>
        public float BandBias { get; internal set; } = 0.5f;

        public PursuitPolicy Pursuit { get; internal set; } = PursuitPolicy.Normal;
        public bool ReserveAllowed { get; internal set; } = true;

        /// <summary>I16 Endless: the reserve is committed only to an HQ / base emergency.</summary>
        public bool ReserveEmergencyOnly { get; internal set; }

        /// <summary>I3: the reserve is a fast response package (fast squads first).</summary>
        public bool FastReserve { get; internal set; }

        public RepositionTrigger Triggers { get; internal set; } = RepositionTrigger.All;

        /// <summary>I5 / I17: shoot and scoot after salvos when counter-battery fire is about.</summary>
        public bool ShootAndScoot { get; internal set; }

        /// <summary>I6 / I16: pockets rotate (seconds; 0 none).</summary>
        public bool Rotate { get; internal set; }

        /// <summary>I11: phases rebuild anchors, reserve, priorities.</summary>
        public bool Phased { get; internal set; }

        /// <summary>I12: Showdown's early / mid / final stages.</summary>
        public bool Escalating { get; internal set; }

        /// <summary>I21: heavy strikes hold unless the target is worth breaking the quiet.</summary>
        public bool QuietStrikes { get; internal set; }

        /// <summary>I13 / I22: AA coverage first; ground enemies matter when they threaten the AA / objective.</summary>
        public bool AirFirst { get; internal set; }

        /// <summary>I23: the mission structure is the strategic target of siege / strike / bomber roles.</summary>
        public bool MissionTarget { get; internal set; }

        /// <summary>Part I ObjectiveTargetWeights: the mode's factors on target classes (1 = none).</summary>
        public float TowerWeight { get; internal set; } = 1f;
        public float StructureWeight { get; internal set; } = 1f;
        public float BossWeight { get; internal set; } = 1f;
        public float EscortWeight { get; internal set; } = 1f;
        public float ArtilleryWeight { get; internal set; } = 1f;

        internal ModeDoctrine Copy(string id, string? inherits)
        {
            var c = (ModeDoctrine)MemberwiseClone();
            c.Id = id;
            c.Inherits = inherits;
            return c;
        }
    }

    /// <summary>
    /// AI MASTER P2 Part I: ModeCombatDoctrine. A doctrine per mode and campaign goal, built by inheritance (I15) from a
    /// BalancedObjectiveDoctrine base, resolved from the battle's mode tag, mission goal and AI profile (I26: every
    /// aiModeProfiles row and every goal mapping must resolve; an unknown one falls back to BalancedObjectiveDoctrine with a
    /// MODE_DOCTRINE_FALLBACK line, never to raw nearest-enemy behaviour). The policies drive the fire-support anchors (Part
    /// J), the squads' pursuit leash and reserve, and the mode target weights on the role ladders.
    /// </summary>
    public static class ModeCombatDoctrine
    {
        public const string Base = "balanced_objective";

        private static readonly Dictionary<string, ModeDoctrine> Table = Build();

        /// <summary>Every doctrine id (tests, the export).</summary>
        public static IEnumerable<string> Ids => Table.Keys;

        public static bool Has(string id) => Table.ContainsKey(id);

        public static ModeDoctrine Get(string id) => Table.TryGetValue(id, out var d) ? d : Table[Base];

        /// <summary>Mode tags whose doctrine is not their profile's (Endless plays Defend's profile with its own doctrine).</summary>
        private static readonly Dictionary<string, string> ModeTags = new(StringComparer.Ordinal)
        {
            ["Endless"] = "endless", ["Weekly"] = "weekly", ["KingOfTheHill"] = "hill", ["Sandbox"] = "conquest", ["FixedDeck"] = "fixed_deck",
            ["Assault"] = "assault", ["Siege"] = "siege", ["Defend"] = "defend", ["Survival"] = "survival", ["BossRush"] = "bossrush",
            ["Showdown"] = "showdown", ["Operation"] = "operation", ["Conquest"] = "conquest", ["Deathmatch"] = "deathmatch",
        };

        /// <summary>Campaign goals (aiModeProfiles.goals keys) to their doctrine.</summary>
        private static readonly Dictionary<string, string> Goals = new(StringComparer.Ordinal)
        {
            ["Capture"] = "capture", ["Destroy"] = "destroy", ["Duel"] = "duel", ["Hold"] = "hold", ["Survive"] = "survival",
            ["Escort"] = "escort", ["Evacuate"] = "evacuate", ["Protect"] = "protect", ["Recon"] = "recon", ["Hunt"] = "hunt",
            ["Intercept"] = "intercept", ["ShootDown"] = "shootdown", ["Outpost"] = "outpost", ["Relieve"] = "relieve", ["Boss"] = "bossrush_goal",
        };

        /// <summary>
        /// The doctrine id for a battle: the mission goal's (a campaign mission plays its type), else the mode tag's, else the
        /// profile's own "doctrine" key, else the profile id; <paramref name="fallback"/> when none of them names a doctrine.
        /// </summary>
        public static string Resolve(string? modeTag, string? missionGoal, AiModeProfile profile, out bool fallback)
        {
            fallback = false;
            if (missionGoal != null && Goals.TryGetValue(missionGoal, out var g)) return g;
            if (modeTag != null && ModeTags.TryGetValue(modeTag, out var m)) return m;
            if (profile.Doctrine is { } d && Table.ContainsKey(d)) return d;
            if (Table.ContainsKey(profile.Id)) return profile.Id;
            fallback = true;
            return Base;
        }

        /// <summary>
        /// I26: the profile rows and goal mappings that resolve to no doctrine (empty: complete). Run at load by the tests and
        /// at the battle's first look (a development warning line).
        /// </summary>
        public static List<string> Validate(AiModeProfiles profiles)
        {
            var missing = new List<string>();
            foreach (var kv in profiles.Profiles)
            {
                var p = kv.Value;
                if (!(p.Doctrine is { } d && Table.ContainsKey(d)) && !Table.ContainsKey(p.Id)) missing.Add("profile " + kv.Key);
            }
            foreach (var kv in profiles.Goals)
                if (!Goals.ContainsKey(kv.Key) && !Table.ContainsKey(kv.Value)) missing.Add("goal " + kv.Key + " -> " + kv.Value);
            foreach (var kv in profiles.Modes)
                if (!ModeTags.ContainsKey(kv.Key) && !Table.ContainsKey(kv.Value)) missing.Add("mode " + kv.Key + " -> " + kv.Value);
            return missing;
        }

        /// <summary>The Part I1 band (share of usable reach) of a fire class, the doctrine's bias applied.</summary>
        public static (float min, float max) Band(FireClass c)
        {
            var b = c switch
            {
                FireClass.Mortar => Tun.ModeDoctrine.MortarBand,
                FireClass.Mlrs => Tun.ModeDoctrine.MlrsBand,
                FireClass.LongRange => Tun.ModeDoctrine.LongBand,
                _ => Tun.ModeDoctrine.ArtilleryBand,
            };
            return b.Length >= 2 ? (b[0], b[1]) : (0.65f, 0.85f);
        }

        // ------------------------------------------------------------------------------------------------ the table

        private static Dictionary<string, ModeDoctrine> Build()
        {
            var t = new Dictionary<string, ModeDoctrine>(StringComparer.Ordinal);
            var basis = new ModeDoctrine { Id = Base };
            t[Base] = basis;

            ModeDoctrine Add(string id, string parent, Action<ModeDoctrine> set)
            {
                var d = t[parent].Copy(id, parent);
                set(d);
                t[id] = d;
                return d;
            }

            // I1 Assault / Breakthrough: heavy front, mortar 55-75 %, artillery 65-85 %, MLRS 75-90 %; towers, then breach.
            Add("assault", Base, d =>
            {
                d.Frontline = FrontlinePolicy.Advance;
                d.FireSupport = FireSupportPolicy.FrontLogical;
                d.TowerWeight = 1.4f;
                d.Triggers = RepositionTrigger.Utilization | RepositionTrigger.FrontMoved | RepositionTrigger.RangeBandLost |
                             RepositionTrigger.CounterBattery | RepositionTrigger.RouteChanged | RepositionTrigger.PhaseChange | RepositionTrigger.TerrainChange;
            });
            // I23 Destroy: Assault's positioning, the mission structure first for siege / strike / bomber.
            Add("destroy", "assault", d => { d.MissionTarget = true; d.StructureWeight = 1.3f; });
            // I2 Defend / Hold: launchers never meet the enemy; no chase; deeper band.
            Add("defend", Base, d =>
            {
                d.Frontline = FrontlinePolicy.HoldLine;
                d.FireSupport = FireSupportPolicy.DefenceLine;
                d.BandBias = 0.8f;
                d.Pursuit = PursuitPolicy.NoChase;
                d.Triggers = RepositionTrigger.Utilization | RepositionTrigger.RangeBandLost | RepositionTrigger.CounterBattery |
                             RepositionTrigger.PhaseChange | RepositionTrigger.TerrainChange;
            });
            // I18 campaign Hold / Protect / Outpost / Relieve inherit Defend with the mission object as anchor.
            Add("hold", "defend", d => d.Frontline = FrontlinePolicy.ObjectiveBody);
            Add("protect", "defend", d => d.Pursuit = PursuitPolicy.NoChase);
            Add("outpost", "defend", d => d.BandBias = 0.7f);
            Add("relieve", "defend", d =>
            {
                d.Frontline = FrontlinePolicy.Advance;
                d.Pursuit = PursuitPolicy.Leash;
                d.FireSupport = FireSupportPolicy.FrontLogical;
                d.BandBias = 0.6f;
            });
            // I16 Endless: Defend, rotating pockets, a reserve only for HQ emergencies.
            Add("endless", "defend", d =>
            {
                d.FireSupport = FireSupportPolicy.PreparedPockets;
                d.Rotate = true;
                d.ReserveEmergencyOnly = true;
                d.Triggers |= RepositionTrigger.Rotation | RepositionTrigger.WaveDirection;
            });
            // I3 Capture / Conquest / Hill: fire support outside the circle covering point and approaches; fast reserve.
            Add("conquest", Base, d =>
            {
                d.Frontline = FrontlinePolicy.ObjectiveBody;
                d.FireSupport = FireSupportPolicy.ObjectiveCover;
                d.FastReserve = true;
                d.Triggers = RepositionTrigger.ObjectiveUncovered | RepositionTrigger.Utilization | RepositionTrigger.CounterBattery |
                             RepositionTrigger.PhaseChange | RepositionTrigger.TerrainChange;
            });
            Add("capture", "conquest", d => { });
            Add("hill", "conquest", d => { });
            // I4 Escort: convoy-relative sectors, leapfrogging fire support, leash beats pursuit.
            Add("escort", Base, d =>
            {
                d.Frontline = FrontlinePolicy.ConvoyScreen;
                d.FireSupport = FireSupportPolicy.ConvoyLeapfrog;
                d.Pursuit = PursuitPolicy.Leash;
                d.Triggers = RepositionTrigger.RangeBandLost | RepositionTrigger.RouteChanged | RepositionTrigger.CounterBattery |
                             RepositionTrigger.PhaseChange | RepositionTrigger.TerrainChange;
            });
            // I19 Evacuate: Escort with the evac group's survival first (no pursuit off the corridor).
            Add("evacuate", "escort", d => d.Pursuit = PursuitPolicy.NoChase);
            // I5 Siege: recon, counter-battery, radar / SAM / tower, breach, defensive clusters; layered, shoot and scoot.
            Add("siege", Base, d =>
            {
                d.Frontline = FrontlinePolicy.Advance;
                d.FireSupport = FireSupportPolicy.SiegeLayers;
                d.ShootAndScoot = true;
                d.TowerWeight = 1.5f;
                d.ArtilleryWeight = 1.3f;
                d.ReserveAllowed = false;
            });
            // I17 Weekly: Siege on the fortress's current state.
            Add("weekly", "siege", d => d.MissionTarget = true);
            // I6 Survival: no chase; 2-3 pockets rotated by wave direction; no reserve in scripted waves.
            Add("survival", Base, d =>
            {
                d.Frontline = FrontlinePolicy.Survival;
                d.FireSupport = FireSupportPolicy.PreparedPockets;
                d.Pursuit = PursuitPolicy.NoChase;
                d.Rotate = true;
                d.ReserveAllowed = false;
                d.Triggers = RepositionTrigger.WaveDirection | RepositionTrigger.Rotation | RepositionTrigger.CounterBattery |
                             RepositionTrigger.RangeBandLost | RepositionTrigger.TerrainChange;
            });
            // I7 BossRush / I25 boss goal: dangerous parts, then escorts; artillery on the predicted region; no reserve.
            Add("bossrush", Base, d =>
            {
                d.Frontline = FrontlinePolicy.BossFocus;
                d.FireSupport = FireSupportPolicy.BossPredict;
                d.BossWeight = 1.3f;
                d.EscortWeight = 1.1f;
                d.ReserveAllowed = false;
            });
            Add("bossrush_goal", "bossrush", d => { });
            // I8 Deathmatch / I24 Duel: no capture anchor; the front as a moving logical anchor.
            Add("deathmatch", Base, d =>
            {
                d.Frontline = FrontlinePolicy.Mobile;
                d.FireSupport = FireSupportPolicy.FrontLogical;
                d.Triggers = RepositionTrigger.Utilization | RepositionTrigger.FrontMoved | RepositionTrigger.RangeBandLost |
                             RepositionTrigger.PocketCompromised | RepositionTrigger.CounterBattery | RepositionTrigger.TerrainChange;
            });
            Add("duel", "deathmatch", d => d.ReserveAllowed = false);
            // I9 Hunt / I20 Intercept: scouts and fast units find and cut off; launchers never chase.
            Add("hunt", Base, d =>
            {
                d.Frontline = FrontlinePolicy.Mobile;
                d.FireSupport = FireSupportPolicy.InterceptPredict;
                d.Pursuit = PursuitPolicy.Leash;
            });
            Add("intercept", "hunt", d => d.ReserveAllowed = false);
            // I10 / I21 Recon: recon stays the task; heavy support only on high-value spotted targets.
            Add("recon", Base, d =>
            {
                d.Frontline = FrontlinePolicy.Mobile;
                d.FireSupport = FireSupportPolicy.Quiet;
                d.BandBias = 1f;
                d.QuietStrikes = true;
                d.Pursuit = PursuitPolicy.NoChase;
            });
            // I11 Operation: Assault's positioning, rebuilt at each phase.
            Add("operation", "assault", d => d.Phased = true);
            // I12 Showdown: early defensive pocket, mid balanced, final forward enough, reserve cut.
            Add("showdown", Base, d =>
            {
                d.Escalating = true;
                d.FireSupport = FireSupportPolicy.FrontLogical;
                d.TowerWeight = 1.2f;
            });
            // I13 / I22 ShootDown: AA coverage first; ground units defend it; no chase of unrelated ground targets.
            Add("shootdown", Base, d =>
            {
                d.AirFirst = true;
                d.Frontline = FrontlinePolicy.HoldLine;
                d.FireSupport = FireSupportPolicy.DefenceLine;
                d.Pursuit = PursuitPolicy.NoChase;
            });
            // I14 Fixed deck: the scenario's rules first; the base doctrine inside the permitted set.
            Add("fixed_deck", Base, d => { });
            return t;
        }

        /// <summary>
        /// Part I ObjectiveTargetWeights for <paramref name="role"/> against a target class (1: none). <paramref name="mission"/>:
        /// the target is the mission's structure (I23); <paramref name="threatensMission"/>: it threatens the AA / objective
        /// (I13, I22); <paramref name="worth"/>: its CP worth (I21 quiet strikes).
        /// </summary>
        public static float TargetWeight(ModeDoctrine d, ShowdownStage stage, DoctrineRole role, TargetClass c, bool mission, bool threatensMission,
            bool escortOfBoss, float worth)
        {
            var w = 1f;
            if (c == TargetClass.Tower) w *= d.TowerWeight;
            if (c == TargetClass.Structure) w *= d.StructureWeight;
            if (c == TargetClass.Boss) w *= d.BossWeight;
            if (escortOfBoss) w *= d.EscortWeight;
            if (c == TargetClass.Artillery && role == DoctrineRole.FireSupport) w *= d.ArtilleryWeight;
            if (d.MissionTarget && mission && role is DoctrineRole.Siege or DoctrineRole.FireSupport or DoctrineRole.Bomber or DoctrineRole.LoiterAntiArmour)
                w *= Tun.ModeDoctrine.MissionTargetWeight;
            if (d.AirFirst && c is not (TargetClass.Bomber or TargetClass.StrikeAir or TargetClass.Fighter or TargetClass.Helicopter or TargetClass.Drone) &&
                !threatensMission) w *= Tun.ModeDoctrine.OffMissionGround;
            if (d.QuietStrikes && role is DoctrineRole.FireSupport or DoctrineRole.Bomber && worth < Tun.ModeDoctrine.QuietStrikeWorth && !threatensMission)
                w *= Tun.RoleDoctrine.LastResort;
            // I12: the final stage weighs time to value (towers, the HQ) a little more.
            if (stage == ShowdownStage.Final && c is TargetClass.Tower or TargetClass.Structure) w *= 1.15f;
            return w;
        }
    }

    /// <summary>Part I1's fire classes.</summary>
    public enum FireClass : byte
    {
        Mortar,
        Artillery,
        Mlrs,
        LongRange,
    }

    /// <summary>I12 Showdown stages.</summary>
    public enum ShowdownStage : byte
    {
        None,
        Early,
        Mid,
        Final,
    }

    /// <summary>
    /// AI MASTER P2: the battle's current mode doctrine and phase (I11: a phase change rebuilds anchors, reserve and
    /// priorities, so nothing stale is carried over). Refreshed lazily once per step; <see cref="Generation"/> counts the
    /// changes the layers rebuild on. Also carries the mission target each side's tactical AI found (I23).
    /// </summary>
    public sealed class ModeDoctrineState
    {
        private readonly SimWorld _world;
        private long _tick = -1;
        private string _key = "";
        private bool _validated;
        private readonly Dictionary<int, Core.EntityId> _missionTarget = new();

        internal ModeDoctrineState(SimWorld world) => _world = world;

        public ModeDoctrine Current { get; private set; } = ModeCombatDoctrine.Get(ModeCombatDoctrine.Base);
        private ShowdownStage _stage;
        private int _generation;

        /// <summary>I12: Showdown's stage now (None outside Showdown).</summary>
        public ShowdownStage Stage
        {
            get
            {
                Refresh();
                return _stage;
            }
        }

        /// <summary>Bumped on every doctrine or phase change (anchors, reserves rebuild on it).</summary>
        public int Generation
        {
            get
            {
                Refresh();
                return _generation;
            }
        }

        public string PhaseKey { get; private set; } = "";

        /// <summary>The doctrine now (refreshed at most once a step).</summary>
        public ModeDoctrine Now
        {
            get
            {
                Refresh();
                return Current;
            }
        }

        /// <summary>
        /// The doctrine of one side: a defend-family doctrine is the defender's, so the attacking side of a Defend / Survival /
        /// Hold battle plays Assault; an attack-family doctrine (Assault, Siege, Weekly, Destroy) is the attacker's, so the
        /// defending side plays Defend (the profile's "defender" says who defends).
        /// </summary>
        public ModeDoctrine For(int team)
        {
            var d = Now;
            var p = _world.AiProfile;
            if (p.Defender == "none") return d;
            var defends = p.Defends(team);
            if (defends && d.Id is "assault" or "siege" or "weekly" or "destroy" or "operation") return ModeCombatDoctrine.Get("defend");
            if (!defends && d.Id is "defend" or "endless" or "hold" or "protect" or "outpost" or "survival") return ModeCombatDoctrine.Get("assault");
            return d;
        }

        internal void Refresh()
        {
            if (_tick == _world.Tick) return;
            _tick = _world.Tick;
            var profile = _world.AiProfile;
            var id = ModeCombatDoctrine.Resolve(_world.ModeTag, _world.MissionGoal, profile, out var fallback);
            var stage = StageNow();
            var bossPhase = -1;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Def.Boss) bossPhase = Math.Max(bossPhase, v.Phase);
            var opStage = _world.Intel.Objectives is OperationMode op ? op.StageIndex : -1;
            var phase = $"{_world.AiPhase}|{(_world.Alarm ? 1 : 0)}|{opStage}|{(int)stage}|{bossPhase}|{profile.Id}";
            var key = id + "#" + phase;
            if (!_validated)
            {
                _validated = true;
                var missing = ModeCombatDoctrine.Validate(_world.Catalog.AiModes);
                if (missing.Count > 0) P2Reasons.Commander(_world, -1, DecisionKind.Plan, P2Reasons.ModeDoctrineFallback, "missing " + string.Join(", ", missing));
            }
            if (key == _key) return;
            var first = _key.Length == 0;
            _key = key;
            Current = ModeCombatDoctrine.Get(id);
            _stage = stage;
            PhaseKey = phase;
            _generation++;
            P2Reasons.Commander(_world, -1, DecisionKind.Plan, first ? P2Reasons.ModeDoctrine : P2Reasons.ModePhaseRebuild,
                $"{Current.Id} phase {phase}{(fallback ? " (fallback)" : "")}");
            if (fallback) P2Reasons.Commander(_world, -1, DecisionKind.Plan, P2Reasons.ModeDoctrineFallback, profile.Id);
        }

        private ShowdownStage StageNow()
        {
            if (_world.Intel.Objectives is not ShowdownMode s) return ShowdownStage.None;
            var t = (float)_world.Time;
            if (s.Phase == ShowdownPhase.SuddenDeath || t >= s.Rules.RebuildCutoff) return ShowdownStage.Final;
            return t >= s.Rules.EscalationAt ? ShowdownStage.Mid : ShowdownStage.Early;
        }

        /// <summary>The reserve share range now (spec 24; Showdown's final stage cuts it, I12).</summary>
        public (float min, float max) ReserveShareOf(int team)
        {
            {
                var d = For(team);
                if (!d.ReserveAllowed) return (0f, 0f);
                var r = Tun.ModeDoctrine.ReserveShare;
                var (min, max) = r.Length >= 2 ? (r[0], r[1]) : (0.15f, 0.25f);
                if (_stage == ShowdownStage.Final) return (0f, Tun.ModeDoctrine.FinalReserveShare);
                return (min, max);
            }
        }

        /// <summary>I23: the structure a side's tactical AI is sent to destroy (None: none).</summary>
        public Core.EntityId MissionTargetOf(int team) => _missionTarget.TryGetValue(team, out var id) ? id : Core.EntityId.None;

        internal void SetMissionTarget(int team, Core.EntityId id) => _missionTarget[team] = id;
    }
}
