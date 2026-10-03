#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Balance pack (lane B, rule B): gameplay constants that lived in the code, now read from
    /// Resources/Data/tunables.json (domain, owner class, name; each entry carries its unit). The fields keep the
    /// code's old values as defaults, so a battle without the file (a test catalog) plays exactly as before;
    /// <see cref="Apply"/> sets them from the file (GameContent.LoadCatalog). The owners read them through
    /// properties of the old names. Generated once from the old constants; edit the JSON, not these defaults.
    /// </summary>
    public static partial class SimTunables
    {
        public static partial class Weapons
        {
            public static class CombatSystem
            {
                /// <summary>weapons.combatSystem.axisRatio (x; nguong, was Sim/Combat/CombatSystem.Bombs.cs:106).</summary>
                public static float AxisRatio = 1.5f;
                /// <summary>weapons.combatSystem.counterBatteryPriority (score; gioi_han_thuc_the, was Sim/Combat/CombatSystem.P17.cs:17).</summary>
                public static float CounterBatteryPriority = 12f;
                /// <summary>weapons.combatSystem.crowdMax (count; tran, was Sim/Combat/CombatSystem.P26.cs:20).</summary>
                public static float CrowdMax = 4f;
                /// <summary>weapons.combatSystem.reloadStillSpeed (m/s; tan_suat, was Sim/Combat/CombatSystem.cs:145).</summary>
                public static float ReloadStillSpeed = 0.4f;
                /// <summary>weapons.combatSystem.retargetSeconds (s; thoi_gian, was Sim/Combat/CombatSystem.cs:226).</summary>
                public static float RetargetSeconds = 0.5f;
                /// <summary>weapons.combatSystem.bombedRadius (m; ban_kinh, was Sim/Combat/CombatSystem.cs:429).</summary>
                public static float BombedRadius = 16f;
                /// <summary>weapons.combatSystem.bombedSeconds (s; thoi_gian, was Sim/Combat/CombatSystem.cs:430).</summary>
                public static double BombedSeconds = 10.0;
                /// <summary>weapons.combatSystem.twinGap (s; thoi_gian, was Sim/Combat/CombatSystem.cs:629).</summary>
                public static float TwinGap = 0.15f;
                /// <summary>weapons.combatSystem.restSeconds (s; thoi_gian, was Sim/Combat/CombatSystem.cs:672).</summary>
                public static float RestSeconds = 1.0f;
                /// <summary>weapons.combatSystem.runDamage (x; sat_thuong, was Sim/Combat/CombatSystem.cs:679).</summary>
                public static float RunDamage = 1.7f;
                /// <summary>weapons.combatSystem.twinOffset (s; ban_kinh, was Sim/Combat/CombatSystem.cs:685).</summary>
                public static float TwinOffset = 0.1f;
            }
            public static class DamageSystem
            {
                /// <summary>weapons.damageSystem.engineerBreach (x; nguong, was Sim/Combat/DamageSystem.cs:258).</summary>
                public static float EngineerBreach = 3f;
                /// <summary>weapons.damageSystem.fireAfterburn (share; thoi_gian, was Sim/Combat/DamageSystem.cs:747).</summary>
                public static float FireAfterburn = 0.3f;
                /// <summary>weapons.damageSystem.fireBurnSeconds (s; thoi_gian, was Sim/Combat/DamageSystem.cs:747).</summary>
                public static float FireBurnSeconds = 3f;
                /// <summary>weapons.damageSystem.smokeEnergyCut (share; nguong, was Sim/Combat/DamageSystem.cs:750).</summary>
                public static float SmokeEnergyCut = 0.8f;
            }
            public static class DamageTable
            {
                /// <summary>weapons.damageTable.defaultPenetration (x; sat_thuong, was Sim/Content/DamageTable.cs:52).</summary>
                public static float[] DefaultPenetration = { 1.2f, 1f, 0.85f, 0.55f, 0.25f, 0.1f };
            }
            public static class WeaponDef
            {
                /// <summary>weapons.weaponDef.minSwitchSeconds (s; thoi_gian, was Sim/Content/SecondRounds.cs:68).</summary>
                public static float MinSwitchSeconds = 0.5f;
                /// <summary>weapons.weaponDef.roundHoldSeconds (s; thoi_gian, was Sim/Content/SecondRounds.cs:71).</summary>
                public static float RoundHoldSeconds = 2f;
                /// <summary>weapons.weaponDef.maxEdge (x; sat_thuong, was Sim/Content/WeaponDef.P17.cs:58).</summary>
                public static float MaxEdge = 20f;
                /// <summary>weapons.weaponDef.heArmourMax (armour level; sat_thuong, was Sim/Content/WeaponDef.P17.cs:77).</summary>
                public static int HeArmourMax = 1;
                /// <summary>weapons.weaponDef.maxEdgeT5 (x; sat_thuong, was Sim/Content/WeaponDef.P34.cs:44).</summary>
                public static float MaxEdgeT5 = 28f;
                /// <summary>weapons.weaponDef.escapeSpeed (m/s; tan_suat, was Sim/Content/WeaponDef.P34.cs:49).</summary>
                public static float EscapeSpeed = 4.5f;
                /// <summary>weapons.weaponDef.maxWarning (s; thoi_gian, was Sim/Content/WeaponDef.P34.cs:52).</summary>
                public static float MaxWarning = 6f;
            }
        }
        public static partial class Vehicles
        {
            public static class AbilitySystem
            {
                /// <summary>vehicles.abilitySystem.homeReach (m; ban_kinh, was Sim/Abilities/AbilitySystem.cs:25).</summary>
                public static float HomeReach = 20f;
                /// <summary>vehicles.abilitySystem.homeRearmSeconds (s; thoi_gian, was Sim/Abilities/AbilitySystem.cs:28).</summary>
                public static float HomeRearmSeconds = 3f;
                /// <summary>vehicles.abilitySystem.auraInterval (s; thoi_gian, was Sim/Abilities/AbilitySystem.cs:31).</summary>
                public static float AuraInterval = 0.5f;
                /// <summary>vehicles.abilitySystem.mineSpotting (m; ban_kinh, was Sim/Abilities/AbilitySystem.cs:34).</summary>
                public static float MineSpotting = 9f;
            }
            public static class FieldWorksSystem
            {
                /// <summary>vehicles.fieldWorksSystem.nightSight (x; ban_kinh, was Sim/Abilities/FieldWorksSystem.cs:59).</summary>
                public static float NightSight = 0.75f;
                /// <summary>vehicles.fieldWorksSystem.decoyCheckSeconds (s; thoi_gian, was Sim/Abilities/FieldWorksSystem.cs:155).</summary>
                public static double DecoyCheckSeconds = 0.5;
                /// <summary>vehicles.fieldWorksSystem.passScanSeconds (s; thoi_gian, was Sim/Abilities/FieldWorksSystem.cs:362).</summary>
                public static double PassScanSeconds = 0.5;
            }
            public static class GearSystem
            {
                /// <summary>vehicles.gearSystem.lastStandGap (s; thoi_gian, was Sim/Abilities/GearSystem.Lines.cs:30).</summary>
                public static float LastStandGap = 6f;
                /// <summary>vehicles.gearSystem.killReadySeconds (s; thoi_gian, was Sim/Abilities/GearSystem.Lines.cs:33).</summary>
                public static float KillReadySeconds = 2f;
                /// <summary>vehicles.gearSystem.fuelBlastCap (HP; sat_thuong, was Sim/Abilities/GearSystem.Lines.cs:36).</summary>
                public static float FuelBlastCap = 1500f;
                /// <summary>vehicles.gearSystem.laserWarningCooldown (s; thoi_gian, was Sim/Abilities/GearSystem.Lines.cs:138).</summary>
                public static float LaserWarningCooldown = 20f;
                /// <summary>vehicles.gearSystem.procGap (s; thoi_gian, was Sim/Abilities/GearSystem.cs:38).</summary>
                public static double ProcGap = 2.0;
                /// <summary>vehicles.gearSystem.auraInterval (s; thoi_gian, was Sim/Abilities/GearSystem.cs:40).</summary>
                public static float AuraInterval = 0.5f;
            }
            public static class SupplyRules
            {
                /// <summary>vehicles.supplyRules.slowShare (share; nguong, was Sim/Abilities/SupplySystem.cs:32).</summary>
                public static float SlowShare = 0.5f;
                /// <summary>vehicles.supplyRules.returnShare (share; nguong, was Sim/Abilities/SupplySystem.cs:35).</summary>
                public static float ReturnShare = 0.5f;
                /// <summary>vehicles.supplyRules.bomberShare (share; nguong, was Sim/Abilities/SupplySystem.cs:35).</summary>
                public static float BomberShare = 2f / 3f;
                /// <summary>vehicles.supplyRules.padRate (x; tan_suat, was Sim/Abilities/SupplySystem.cs:38).</summary>
                public static float PadRate = 2f;
                /// <summary>vehicles.supplyRules.hqRate (x; tan_suat, was Sim/Abilities/SupplySystem.cs:38).</summary>
                public static float HqRate = 1.5f;
                /// <summary>vehicles.supplyRules.carrierRate (x; tan_suat, was Sim/Abilities/SupplySystem.cs:38).</summary>
                public static float CarrierRate = 2f;
            }
            public static class SupplySystem
            {
                /// <summary>vehicles.supplySystem.safeSeconds (s; thoi_gian, was Sim/Abilities/SupplySystem.cs:53).</summary>
                public static double SafeSeconds = 3.0;
                /// <summary>vehicles.supplySystem.lowShare (share; nguong, was Sim/Abilities/SupplySystem.cs:56).</summary>
                public static float LowShare = 0.2f;
                /// <summary>vehicles.supplySystem.hqHeal (share/s; sat_thuong, was Sim/Abilities/SupplySystem.cs:62).</summary>
                public static float HqHeal = 0.01f;
                /// <summary>vehicles.supplySystem.hqReach (m; ban_kinh, was Sim/Abilities/SupplySystem.cs:65).</summary>
                public static float HqReach = 20f;
                /// <summary>vehicles.supplySystem.carrierReach (m; ban_kinh, was Sim/Abilities/SupplySystem.cs:65).</summary>
                public static float CarrierReach = 12f;
            }
            public static class VehicleDef
            {
                /// <summary>vehicles.vehicleDef.stealthSight (x; ban_kinh, was Sim/Content/Definitions.cs:555).</summary>
                public static float StealthSight = 0.4f;
            }
            public static class RelayDef
            {
                /// <summary>vehicles.relayDef.maxPerBase (count; tran, was Sim/Content/VehicleDef.P17.cs:80).</summary>
                public static int MaxPerBase = 2;
            }
            public static class MovementSystem
            {
                /// <summary>vehicles.movementSystem.ghostSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Rescue.cs:39).</summary>
                public static double GhostSeconds = 4.0;
                /// <summary>vehicles.movementSystem.maxYieldDepth (count; tran, was Sim/Movement/MovementSystem.Traffic.cs:37).</summary>
                public static int MaxYieldDepth = 2;
                /// <summary>vehicles.movementSystem.yieldMaxSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:48).</summary>
                public static double YieldMaxSeconds = 4.0;
                /// <summary>vehicles.movementSystem.yieldHoldSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:51).</summary>
                public static double YieldHoldSeconds = 2.5;
                /// <summary>vehicles.movementSystem.yieldCooldown (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:54).</summary>
                public static double YieldCooldown = 4.0;
                /// <summary>vehicles.movementSystem.yieldWaitSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:57).</summary>
                public static double YieldWaitSeconds = 3.0;
                /// <summary>vehicles.movementSystem.gatherReach (m; ban_kinh, was Sim/Movement/MovementSystem.Traffic.cs:63).</summary>
                public static float GatherReach = 12f;
                /// <summary>vehicles.movementSystem.minCostRepathGap (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:66).</summary>
                public static double MinCostRepathGap = 1.0;
                /// <summary>vehicles.movementSystem.pathNodeBudgetPerTick (nodes/tick; tan_suat, was Sim/Movement/MovementSystem.Traffic.cs:72).</summary>
                public static int PathNodeBudgetPerTick = 20000;
                /// <summary>vehicles.movementSystem.maxNodesPerSearch (nodes; tran, was Sim/Movement/MovementSystem.Traffic.cs:74).</summary>
                public static int MaxNodesPerSearch = 8000;
                /// <summary>vehicles.movementSystem.minSearchBudget (nodes; tan_suat, was Sim/Movement/MovementSystem.Traffic.cs:77).</summary>
                public static int MinSearchBudget = 2000;
                /// <summary>vehicles.movementSystem.detourCap (x; ban_kinh, was Sim/Movement/MovementSystem.Traffic.cs:86).</summary>
                public static float DetourCap = 1.5f;
                /// <summary>vehicles.movementSystem.noAlternativeLength (m; ban_kinh, was Sim/Movement/MovementSystem.Traffic.cs:94).</summary>
                public static float NoAlternativeLength = 12f;
                /// <summary>vehicles.movementSystem.queueSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:97).</summary>
                public static double QueueSeconds = 6.0;
                /// <summary>vehicles.movementSystem.headOnReverseMax (m; tran, was Sim/Movement/MovementSystem.Traffic.cs:100).</summary>
                public static float HeadOnReverseMax = 12f;
                /// <summary>vehicles.movementSystem.reverseSpeedShare (share; tan_suat, was Sim/Movement/MovementSystem.Traffic.cs:102).</summary>
                public static float ReverseSpeedShare = 0.5f;
                /// <summary>vehicles.movementSystem.headOnWait (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:103).</summary>
                public static double HeadOnWait = 1.5;
                /// <summary>vehicles.movementSystem.backOffDistance (m; ban_kinh, was Sim/Movement/MovementSystem.Traffic.cs:106).</summary>
                public static float BackOffDistance = 4f;
                /// <summary>vehicles.movementSystem.trafficBehindReach (m; ban_kinh, was Sim/Movement/MovementSystem.Traffic.cs:109).</summary>
                public static float TrafficBehindReach = 25f;
                /// <summary>vehicles.movementSystem.offLaneSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:116).</summary>
                public static double OffLaneSeconds = 4.0;
                /// <summary>vehicles.movementSystem.sameGoalReach (m; ban_kinh, was Sim/Movement/MovementSystem.Traffic.cs:282).</summary>
                public static float SameGoalReach = 18f;
                /// <summary>vehicles.movementSystem.gateHoldTicks (ticks; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:611).</summary>
                public static int GateHoldTicks = 10;
                /// <summary>vehicles.movementSystem.gateTurnSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:614).</summary>
                public static double GateTurnSeconds = 8.0;
                /// <summary>vehicles.movementSystem.gateWaitMax (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:617).</summary>
                public static double GateWaitMax = 12.0;
                /// <summary>vehicles.movementSystem.gateWaitLateral (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:733).</summary>
                public static float[] GateWaitLateral = { 5f, 7f, 9f };
                /// <summary>vehicles.movementSystem.gateWaitBack (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:735).</summary>
                public static float[] GateWaitBack = { 0f, 3f, 6f };
                /// <summary>vehicles.movementSystem.headOnOpenWait (s; thoi_gian, was Sim/Movement/MovementSystem.Traffic.cs:855).</summary>
                public static double HeadOnOpenWait = 1.0;
                /// <summary>vehicles.movementSystem.repathInterval (s; thoi_gian, was Sim/Movement/MovementSystem.cs:21).</summary>
                public static float RepathInterval = 0.5f;
                /// <summary>vehicles.movementSystem.stuckDistance (m; ban_kinh, was Sim/Movement/MovementSystem.cs:23).</summary>
                public static float StuckDistance = 0.4f;
                /// <summary>vehicles.movementSystem.stuckDetourDistance (m; ban_kinh, was Sim/Movement/MovementSystem.cs:26).</summary>
                public static float StuckDetourDistance = 3f;
                /// <summary>vehicles.movementSystem.arrivalReach (m; ban_kinh, was Sim/Movement/MovementSystem.cs:29).</summary>
                public static float ArrivalReach = 5f;
                /// <summary>vehicles.movementSystem.separationSlack (m; ban_kinh, was Sim/Movement/MovementSystem.cs:33).</summary>
                public static float SeparationSlack = 0.05f;
                /// <summary>vehicles.movementSystem.settleDistance (m; ban_kinh, was Sim/Movement/MovementSystem.cs:36).</summary>
                public static float SettleDistance = 2.5f;
                /// <summary>vehicles.movementSystem.avoidSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.cs:42).</summary>
                public static double AvoidSeconds = 0.9;
                /// <summary>vehicles.movementSystem.separationStiffness (x; nguong, was Sim/Movement/MovementSystem.cs:48).</summary>
                public static float SeparationStiffness = 0.55f;
                /// <summary>vehicles.movementSystem.maxPush (m; tran, was Sim/Movement/MovementSystem.cs:51).</summary>
                public static float MaxPush = 0.35f;
                /// <summary>vehicles.movementSystem.guardLeash (m; ban_kinh, was Sim/Movement/MovementSystem.cs:54).</summary>
                public static float GuardLeash = 16f;
                /// <summary>vehicles.movementSystem.answerFireSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.cs:57).</summary>
                public static float AnswerFireSeconds = 5f;
                /// <summary>vehicles.movementSystem.manualHoldSeconds (s; thoi_gian, was Sim/Movement/MovementSystem.cs:60).</summary>
                public static float ManualHoldSeconds = 20f;
                /// <summary>vehicles.movementSystem.hoverShare (share; nguong, was Sim/Movement/MovementSystem.cs:1023).</summary>
                public static float HoverShare = 0.6f;
                /// <summary>vehicles.movementSystem.chaseShare (share; nguong, was Sim/Movement/MovementSystem.cs:1023).</summary>
                public static float ChaseShare = 0.55f;
            }
            public static class RailSystem
            {
                /// <summary>vehicles.railSystem.minWarning (s; thoi_gian, was Sim/Movement/RailSystem.cs:123).</summary>
                public static float MinWarning = 4f;
                /// <summary>vehicles.railSystem.warnFloor (s; thoi_gian, was Sim/Movement/RailSystem.cs:130).</summary>
                public static float WarnFloor = 8f;
                /// <summary>vehicles.railSystem.clearHoldTicks (ticks; thoi_gian, was Sim/Movement/RailSystem.cs:133).</summary>
                public static int ClearHoldTicks = 10;
                /// <summary>vehicles.railSystem.ramDamage (HP; sat_thuong, was Sim/Movement/RailSystem.cs:136).</summary>
                public static float RamDamage = 600f;
                /// <summary>vehicles.railSystem.supportLength (m; ban_kinh, was Sim/Movement/RailSystem.cs:140).</summary>
                public static float SupportLength = 50f;
                /// <summary>vehicles.railSystem.supportWait (s; thoi_gian, was Sim/Movement/RailSystem.cs:143).</summary>
                public static float SupportWait = 7f;
                /// <summary>vehicles.railSystem.supportHalfWidth (m; ban_kinh, was Sim/Movement/RailSystem.cs:145).</summary>
                public static float SupportHalfWidth = 1.8f;
                /// <summary>vehicles.railSystem.tellEvery (s; thoi_gian, was Sim/Movement/RailSystem.cs:148).</summary>
                public static double TellEvery = 1.0;
                /// <summary>vehicles.railSystem.attachReach (m; ban_kinh, was Sim/Movement/RailSystem.cs:153).</summary>
                public static float AttachReach = 8f;
            }
        }
        public static partial class Bosses
        {
            public static class BossHunts
            {
                /// <summary>bosses.bossHunts.weeklyMinutes (min; thoi_gian, was Game/Match/BossHunts.cs:19).</summary>
                public static float WeeklyMinutes = 30f;
            }
            public static class BossSystem
            {
                /// <summary>bosses.bossSystem.flyerTicks (ticks; thoi_gian, was Sim/Bosses/BossSystem.BigAttacks.cs:74).</summary>
                public static int FlyerTicks = 5;
                /// <summary>bosses.bossSystem.missileTopSpeed (m/s; tan_suat, was Sim/Bosses/BossSystem.BigAttacks.cs:80).</summary>
                public static float MissileTopSpeed = 24f;
                /// <summary>bosses.bossSystem.escortTicks (ticks; thoi_gian, was Sim/Bosses/BossSystem.Escorts.cs:34).</summary>
                public static int EscortTicks = 10;
                /// <summary>bosses.bossSystem.bodyShare (share; nguong, was Sim/Bosses/BossSystem.Parts.cs:37).</summary>
                public static double BodyShare = 0.4;
            }
            public static class NavalSystem
            {
                /// <summary>bosses.navalSystem.bigShipLength (m; ban_kinh, was Sim/Bosses/NavalSystem.Routes.cs:38).</summary>
                public static float BigShipLength = 25f;
                /// <summary>bosses.navalSystem.gapExtra (m; ban_kinh, was Sim/Bosses/NavalSystem.Routes.cs:41).</summary>
                public static float GapExtra = 10f;
                /// <summary>bosses.navalSystem.closeRate (share/s; tan_suat, was Sim/Bosses/NavalSystem.Routes.cs:50).</summary>
                public static float CloseRate = 0.25f;
                /// <summary>bosses.navalSystem.holdAfterTicks (ticks; thoi_gian, was Sim/Bosses/NavalSystem.Routes.cs:53).</summary>
                public static int HoldAfterTicks = 60;
                /// <summary>bosses.navalSystem.holdMinTicks (ticks; thoi_gian, was Sim/Bosses/NavalSystem.Routes.cs:56).</summary>
                public static int HoldMinTicks = 40;
                /// <summary>bosses.navalSystem.slotSlack (m; ban_kinh, was Sim/Bosses/NavalSystem.Routes.cs:59).</summary>
                public static float SlotSlack = 4f;
                /// <summary>bosses.navalSystem.slotSample (m; ban_kinh, was Sim/Bosses/NavalSystem.Routes.cs:62).</summary>
                public static float SlotSample = 8f;
                /// <summary>bosses.navalSystem.turnWarn (deg; thoi_gian, was Sim/Bosses/NavalSystem.Routes.cs:384).</summary>
                public static float TurnWarn = 45f;
                /// <summary>bosses.navalSystem.captureRadius (m; ban_kinh, was Sim/Bosses/NavalSystem.cs:42).</summary>
                public static float CaptureRadius = 11f;
                /// <summary>bosses.navalSystem.lighthouseRadius (m; ban_kinh, was Sim/Bosses/NavalSystem.cs:43).</summary>
                public static float LighthouseRadius = 14f;
            }
            public static class BossHunt
            {
                /// <summary>bosses.bossHunt.weeklyMinis (count; gioi_han_thuc_the, was Sim/Modes/BossHunt.cs:50).</summary>
                public static int WeeklyMinis = 7;
                /// <summary>bosses.bossHunt.airDefenceMains (count; gioi_han_thuc_the, was Sim/Modes/BossHunt.cs:53).</summary>
                public static int AirDefenceMains = 1;
                /// <summary>bosses.bossHunt.airDefenceMinis (count; gioi_han_thuc_the, was Sim/Modes/BossHunt.cs:53).</summary>
                public static int AirDefenceMinis = 3;
            }
            public static class HuntSupports
            {
                /// <summary>bosses.huntSupports.cap (share; tran, was Sim/Modes/BossHunt.cs:219).</summary>
                public static float Cap = 0.40f;
            }
        }
        public static partial class Bases
        {
            public static class Gear
            {
                /// <summary>bases.gear.bulwarkShare (share; nguong, was Game/Match/Gear.Tower.cs:78).</summary>
                public static float BulwarkShare = 0.35f;
            }
            public static class BaseSystem
            {
                /// <summary>bases.baseSystem.lookEvery (s; thoi_gian, was Sim/Modes/BaseSystem.HqTypes.cs:60).</summary>
                public static double LookEvery = 0.25;
            }
        }
        public static partial class Modes
        {
            public static class TeamEconomy
            {
                /// <summary>modes.teamEconomy.maxVehicles (count; tran, was Sim/Economy/EconomySystem.cs:95).</summary>
                public static int MaxVehicles = 32;
                /// <summary>modes.teamEconomy.maxAircraft (count; tran, was Sim/Economy/EconomySystem.cs:107).</summary>
                public static int MaxAircraft = 6;
            }
            public static class EconomySystem
            {
                /// <summary>modes.economySystem.maxCatchUp (share; tran, was Sim/Economy/EconomySystem.cs:201).</summary>
                public static float MaxCatchUp = 0.5f;
                /// <summary>modes.economySystem.catchUpBelow (share; nguong, was Sim/Economy/EconomySystem.cs:204).</summary>
                public static float CatchUpBelow = 0.75f;
                /// <summary>modes.economySystem.catchUpMinimumArmy (CP; tran, was Sim/Economy/EconomySystem.cs:207).</summary>
                public static int CatchUpMinimumArmy = 14;
                /// <summary>modes.economySystem.catchUpSettle (s; tan_suat, was Sim/Economy/EconomySystem.cs:210).</summary>
                public static float CatchUpSettle = 4f;
                /// <summary>modes.economySystem.deliverySeconds (s; thoi_gian, was Sim/Economy/EconomySystem.cs:217).</summary>
                public static float DeliverySeconds = 3.5f;
                /// <summary>modes.economySystem.rollIn (m; khac, was Sim/Economy/EconomySystem.cs:220).</summary>
                public static float RollIn = 12f;
                /// <summary>modes.economySystem.killReward (share; thuong, was Sim/Economy/EconomySystem.cs:222).</summary>
                public static float KillReward = 0.25f;
                /// <summary>modes.economySystem.killRefundCap (share; tran, was Sim/Economy/EconomySystem.cs:456).</summary>
                public static float KillRefundCap = 0.45f;
                /// <summary>modes.economySystem.lossRefundCap (share; tran, was Sim/Economy/EconomySystem.cs:459).</summary>
                public static float LossRefundCap = 0.15f;
            }
            public static class BattleEvents
            {
                /// <summary>modes.battleEvents.crateFall (s; thoi_gian, was Sim/Modes/BattleEvents.cs:19).</summary>
                public static float CrateFall = 15f;
                /// <summary>modes.battleEvents.crateLife (s; thoi_gian, was Sim/Modes/BattleEvents.cs:20).</summary>
                public static float CrateLife = 50f;
                /// <summary>modes.battleEvents.claimReach (m; ban_kinh, was Sim/Modes/BattleEvents.cs:21).</summary>
                public static float ClaimReach = 6f;
                /// <summary>modes.battleEvents.claimSeconds (s; thoi_gian, was Sim/Modes/BattleEvents.cs:22).</summary>
                public static float ClaimSeconds = 2f;
                /// <summary>modes.battleEvents.crateCp (CP; thuong, was Sim/Modes/BattleEvents.cs:23).</summary>
                public static float CrateCp = 10f;
                /// <summary>modes.battleEvents.crateRepair (share; thuong, was Sim/Modes/BattleEvents.cs:24).</summary>
                public static float CrateRepair = 0.3f;
            }
            public static class EndlessRules
            {
                /// <summary>modes.endlessRules.enemyPerWave (share/wave; khac, was Sim/Modes/Endless.cs:30).</summary>
                public static float EnemyPerWave = 0.04f;
                /// <summary>modes.endlessRules.playerPerWave (share/wave; khac, was Sim/Modes/Endless.cs:33).</summary>
                public static float PlayerPerWave = 0.02f;
                /// <summary>modes.endlessRules.playerMax (share; tran, was Sim/Modes/Endless.cs:33).</summary>
                public static float PlayerMax = 0.30f;
                /// <summary>modes.endlessRules.miniBossEvery (waves; thoi_gian, was Sim/Modes/Endless.cs:39).</summary>
                public static int MiniBossEvery = 5;
                /// <summary>modes.endlessRules.bossEvery (waves; thoi_gian, was Sim/Modes/Endless.cs:39).</summary>
                public static int BossEvery = 10;
                /// <summary>modes.endlessRules.survivalWaves (waves; gioi_han_thuc_the, was Sim/Modes/Endless.cs:39).</summary>
                public static int SurvivalWaves = 10;
                /// <summary>modes.endlessRules.defendFiniteWaves (waves; gioi_han_thuc_the, was Sim/Modes/Endless.cs:42).</summary>
                public static int DefendFiniteWaves = 10;
                /// <summary>modes.endlessRules.waveCoins (coins; thuong, was Sim/Modes/Endless.cs:45).</summary>
                public static int WaveCoins = 18;
                /// <summary>modes.endlessRules.bossCoins (coins; thuong, was Sim/Modes/Endless.cs:45).</summary>
                public static int BossCoins = 60;
                /// <summary>modes.endlessRules.dailyCap (coins; tran, was Sim/Modes/Endless.cs:45).</summary>
                public static int DailyCap = 600;
                /// <summary>modes.endlessRules.waveBadges (waves; gioi_han_thuc_the, was Sim/Modes/Endless.cs:50).</summary>
                public static int[] WaveBadges = { 10, 20, 30 };
                /// <summary>modes.endlessRules.bossBadges (bosses; gioi_han_thuc_the, was Sim/Modes/Endless.cs:50).</summary>
                public static int[] BossBadges = { 5, 10 };
            }
            public static class Outposts
            {
                /// <summary>modes.outposts.neutralHealth (x; sat_thuong, was Sim/Modes/ModeSupport.cs:154).</summary>
                public static float NeutralHealth = 2f;
                /// <summary>modes.outposts.buildSeconds (s; thoi_gian, was Sim/Modes/ModeSupport.cs:155).</summary>
                public static float BuildSeconds = 8f;
                /// <summary>modes.outposts.rebuildSeconds (s; thoi_gian, was Sim/Modes/ModeSupport.cs:156).</summary>
                public static float RebuildSeconds = 35f;
                /// <summary>modes.outposts.respawnSeconds (s; thoi_gian, was Sim/Modes/ModeSupport.cs:157).</summary>
                public static float RespawnSeconds = 100f;
            }
            public static class NeutralSystem
            {
                /// <summary>modes.neutralSystem.interval (s; thoi_gian, was Sim/Modes/Neutrals.cs:38).</summary>
                public static float Interval = 0.5f;
            }
            public static class SandboxMode
            {
                /// <summary>modes.sandboxMode.firstWaveDelay (s; thoi_gian, was Sim/Modes/SandboxMode.cs:69).</summary>
                public static float FirstWaveDelay = 20f;
                /// <summary>modes.sandboxMode.waveInterval (s; thoi_gian, was Sim/Modes/SandboxMode.cs:70).</summary>
                public static float WaveInterval = 30f;
                /// <summary>modes.sandboxMode.reinforceCooldownSeconds (s; thoi_gian, was Sim/Modes/SandboxMode.cs:74).</summary>
                public static float ReinforceCooldownSeconds = 12f;
            }
            public static class SandboxBattle
            {
                /// <summary>modes.sandboxBattle.unlimitedCp (CP; tran, was Sim/Sandbox/SandboxBattle.cs:263).</summary>
                public static float UnlimitedCp = 999f;
            }
            public static class SandboxRules
            {
                /// <summary>modes.sandboxRules.vehicleCap (count; tran, was Sim/Sandbox/SandboxRules.cs:56).</summary>
                public static int VehicleCap = 64;
                /// <summary>modes.sandboxRules.aircraftCap (count; tran, was Sim/Sandbox/SandboxRules.cs:56).</summary>
                public static int AircraftCap = 12;
                /// <summary>modes.sandboxRules.maxRank (rank; tran, was Sim/Sandbox/SandboxRules.cs:109).</summary>
                public static int MaxRank = 10;
            }
            public static class SimWorld
            {
                /// <summary>modes.simWorld.homeRadius (m; ban_kinh, was Sim/SimWorld.cs:256).</summary>
                public static float HomeRadius = 35f;
                /// <summary>modes.simWorld.entrenchSeconds (s; thoi_gian, was Sim/SimWorld.cs:331).</summary>
                public static float EntrenchSeconds = 3f;
                /// <summary>modes.simWorld.lighthouseSight (m; ban_kinh, was Sim/SimWorld.cs:1344).</summary>
                public static float LighthouseSight = 170f;
            }
        }
        public static partial class Ai
        {
            public static class ConquestAi
            {
                /// <summary>ai.conquestAi.clusterRadius (m; ban_kinh, was Sim/AI/ConquestAi.cs:100).</summary>
                public static float ClusterRadius = 9f;
                /// <summary>ai.conquestAi.holdReach (m; ban_kinh, was Sim/AI/ConquestAi.cs:198).</summary>
                public static float HoldReach = 26f;
            }
            public static class SquadLayer
            {
                /// <summary>ai.squadLayer.shortMoveEvery (s; thoi_gian, was Sim/AI/SquadLayer.Units.cs:20).</summary>
                public static double ShortMoveEvery = 8.0;
                /// <summary>ai.squadLayer.threatMetres (m; ban_kinh, was Sim/AI/SquadLayer.Walls.cs:28).</summary>
                public static float ThreatMetres = 40f;
                /// <summary>ai.squadLayer.breachMargin (x; ban_kinh, was Sim/AI/SquadLayer.Walls.cs:31).</summary>
                public static float BreachMargin = 0.8f;
                /// <summary>ai.squadLayer.interval (s; thoi_gian, was Sim/AI/Squads.cs:129).</summary>
                public static float Interval = 0.25f;
                /// <summary>ai.squadLayer.minSquad (count; gioi_han_thuc_the, was Sim/AI/Squads.cs:130).</summary>
                public static int MinSquad = 3;
                /// <summary>ai.squadLayer.maxSquad (count; tran, was Sim/AI/Squads.cs:131).</summary>
                public static int MaxSquad = 6;
                /// <summary>ai.squadLayer.gatherRadius (m; ban_kinh, was Sim/AI/Squads.cs:132).</summary>
                public static float GatherRadius = 25f;
                /// <summary>ai.squadLayer.gatheredRadius (m; ban_kinh, was Sim/AI/Squads.cs:133).</summary>
                public static float GatheredRadius = 12f;
                /// <summary>ai.squadLayer.joinReach (m; ban_kinh, was Sim/AI/Squads.cs:134).</summary>
                public static float JoinReach = 60f;
                /// <summary>ai.squadLayer.supportReach (m; ban_kinh, was Sim/AI/Squads.cs:135).</summary>
                public static float SupportReach = 80f;
            }
            public static class TacticalAi
            {
                /// <summary>ai.tacticalAi.decisionInterval (s; thoi_gian, was Sim/AI/TacticalAi.cs:29).</summary>
                public static float DecisionInterval = 0.75f;
                /// <summary>ai.tacticalAi.boundLength (m; ban_kinh, was Sim/AI/TacticalAi.cs:31).</summary>
                public static float BoundLength = 24f;
                /// <summary>ai.tacticalAi.flankOffset (m; ban_kinh, was Sim/AI/TacticalAi.cs:32).</summary>
                public static float FlankOffset = 24f;
                /// <summary>ai.tacticalAi.fastSpeed (m/s; tan_suat, was Sim/AI/TacticalAi.cs:33).</summary>
                public static float FastSpeed = 11f;
                /// <summary>ai.tacticalAi.clusterRadius (m; ban_kinh, was Sim/AI/TacticalAi.cs:34).</summary>
                public static float ClusterRadius = 7f;
                /// <summary>ai.tacticalAi.fallBackSeconds (s; thoi_gian, was Sim/AI/TacticalAi.cs:40).</summary>
                public static float FallBackSeconds = 30f;
                /// <summary>ai.tacticalAi.outmatchedRatio (share; nguong, was Sim/AI/TacticalAi.cs:121).</summary>
                public static float OutmatchedRatio = 0.6f;
                /// <summary>ai.tacticalAi.recoveredRatio (share; nguong, was Sim/AI/TacticalAi.cs:124).</summary>
                public static float RecoveredRatio = 0.95f;
                /// <summary>ai.tacticalAi.commitSeconds (s; thoi_gian, was Sim/AI/TacticalAi.cs:139).</summary>
                public static double CommitSeconds = 60.0;
                /// <summary>ai.tacticalAi.assaultOdds (x; xac_suat, was Sim/AI/TacticalAi.cs:222).</summary>
                public static float AssaultOdds = 1.4f;
                /// <summary>ai.tacticalAi.shellingTime (s; thoi_gian, was Sim/AI/TacticalAi.cs:225).</summary>
                public static double ShellingTime = 35.0;
                /// <summary>ai.tacticalAi.crateDetour (m; ban_kinh, was Sim/AI/TacticalAi.cs:408).</summary>
                public static float CrateDetour = 50f;
                /// <summary>ai.tacticalAi.depotReach (m; ban_kinh, was Sim/AI/TacticalAi.cs:466).</summary>
                public static float DepotReach = 40f;
                /// <summary>ai.tacticalAi.breachReach (m; ban_kinh, was Sim/AI/TacticalAi.cs:609).</summary>
                public static float BreachReach = 30f;
                /// <summary>ai.tacticalAi.breacherReach (m; ban_kinh, was Sim/AI/TacticalAi.cs:612).</summary>
                public static float BreacherReach = 70f;
                /// <summary>ai.tacticalAi.bossReach (m; ban_kinh, was Sim/AI/TacticalAi.cs:841).</summary>
                public static float BossReach = 30f;
                /// <summary>ai.tacticalAi.reinforcementGap (m; thoi_gian, was Sim/AI/TacticalAi.cs:1388).</summary>
                public static float ReinforcementGap = 50f;
                /// <summary>ai.tacticalAi.homeReach (m; ban_kinh, was Sim/AI/TacticalAi.cs:1389).</summary>
                public static float HomeReach = 45f;
                /// <summary>ai.tacticalAi.waveSize (count; gioi_han_thuc_the, was Sim/AI/TacticalAi.cs:1395).</summary>
                public static int WaveSize = 2;
                /// <summary>ai.tacticalAi.waveWait (s; thoi_gian, was Sim/AI/TacticalAi.cs:1396).</summary>
                public static double WaveWait = 12.0;
            }
        }
        public static partial class Campaign
        {
            public static class MissionDecks
            {
                /// <summary>campaign.missionDecks.airMinimum (count; tran, was Game/Match/MissionDecks.cs:17).</summary>
                public static int AirMinimum = 3;
            }
            public static class Narrative
            {
                /// <summary>campaign.narrative.minersCp (CP; thuong, was Game/Match/Narrative.cs:81).</summary>
                public static int MinersCp = 6;
                /// <summary>campaign.narrative.radarVision (x; ban_kinh, was Game/Match/Narrative.cs:84).</summary>
                public static float RadarVision = 0.75f;
            }
            public static class MissionEventSystem
            {
                /// <summary>campaign.missionEventSystem.rowGap (s; thoi_gian, was Sim/Modes/MissionEvents.Ingress.cs:21).</summary>
                public static double RowGap = 1.0;
                /// <summary>campaign.missionEventSystem.pushSeconds (s; thoi_gian, was Sim/Modes/MissionEvents.cs:644).</summary>
                public static double PushSeconds = 40.0;
            }
            public static class MissionMode
            {
                /// <summary>campaign.missionMode.captureSeconds (s; thoi_gian, was Sim/Modes/MissionMode.cs:60).</summary>
                public static float CaptureSeconds = 10f;
                /// <summary>campaign.missionMode.waypointReach (m; ban_kinh, was Sim/Modes/MissionMode.cs:61).</summary>
                public static float WaypointReach = 5f;
                /// <summary>campaign.missionMode.scoutSeconds (s; thoi_gian, was Sim/Modes/MissionMode.cs:81).</summary>
                public static float ScoutSeconds = 3f;
                /// <summary>campaign.missionMode.escortReach (m; ban_kinh, was Sim/Modes/MissionMode.cs:127).</summary>
                public static float EscortReach = 22f;
                /// <summary>campaign.missionMode.reinforceFirst (s; thoi_gian, was Sim/Modes/MissionMode.cs:141).</summary>
                public static double ReinforceFirst = 45.0;
                /// <summary>campaign.missionMode.reinforceGap (s; thoi_gian, was Sim/Modes/MissionMode.cs:141).</summary>
                public static double ReinforceGap = 75.0;
                /// <summary>campaign.missionMode.reinforceBelow (share; nguong, was Sim/Modes/MissionMode.cs:144).</summary>
                public static float ReinforceBelow = 0.6f;
                /// <summary>campaign.missionMode.fleeSeconds (s; thoi_gian, was Sim/Modes/MissionMode.cs:157).</summary>
                public static double FleeSeconds = 8.0;
            }
            public static class OperationMode
            {
                /// <summary>campaign.operationMode.choiceSeconds (s; thoi_gian, was Sim/Modes/OperationMode.cs:48).</summary>
                public static double ChoiceSeconds = 15.0;
            }
        }
        public static partial class Maps
        {
            public static class EntryGate
            {
                /// <summary>maps.entryGate.outerLength (m; ban_kinh, was Sim/Navigation/EntryGate.cs:31).</summary>
                public static float OuterLength = 120f;
            }
            public static class LaneMap
            {
                /// <summary>maps.laneMap.narrowWidth (m; ban_kinh, was Sim/Navigation/LaneMap.cs:41).</summary>
                public static float NarrowWidth = 6f;
                /// <summary>maps.laneMap.maxNoParkCells (cells; tran, was Sim/Navigation/LaneMap.cs:51).</summary>
                public static int MaxNoParkCells = 30;
                /// <summary>maps.laneMap.routeHalfWidth (m; ban_kinh, was Sim/Navigation/LaneMap.cs:57).</summary>
                public static float RouteHalfWidth = 3f;
                /// <summary>maps.laneMap.maxClearance (cells; tran, was Sim/Navigation/LaneMap.cs:59).</summary>
                public static int MaxClearance = 15;
                /// <summary>maps.laneMap.rebuildInterval (s; thoi_gian, was Sim/Navigation/LaneMap.cs:62).</summary>
                public static double RebuildInterval = 2.0;
            }
            public static class SeaRouteGraph
            {
                /// <summary>maps.seaRouteGraph.exitReach (m; ban_kinh, was Sim/Navigation/SeaRouteGraph.cs:84).</summary>
                public static float ExitReach = 40f;
                /// <summary>maps.seaRouteGraph.bayReach (m; ban_kinh, was Sim/Navigation/SeaRouteGraph.cs:92).</summary>
                public static float BayReach = 60f;
            }
            public static class SpawnPoints
            {
                /// <summary>maps.spawnPoints.gateReach (m; ban_kinh, was Sim/Navigation/SpawnPoints.cs:249).</summary>
                public static float GateReach = 30f;
            }
            public static class TerrainRules
            {
                /// <summary>maps.terrainRules.roadSpeed (x; tan_suat, was Sim/Navigation/TerrainTags.cs:65).</summary>
                public static float RoadSpeed = 1.2f;
                /// <summary>maps.terrainRules.roughSpeed (x; tan_suat, was Sim/Navigation/TerrainTags.cs:66).</summary>
                public static float RoughSpeed = 0.85f;
                /// <summary>maps.terrainRules.forestSpeed (x; tan_suat, was Sim/Navigation/TerrainTags.cs:67).</summary>
                public static float ForestSpeed = 0.75f;
                /// <summary>maps.terrainRules.waterSpeed (x; tan_suat, was Sim/Navigation/TerrainTags.cs:68).</summary>
                public static float WaterSpeed = 0.5f;
                /// <summary>maps.terrainRules.forestSight (x; ban_kinh, was Sim/Navigation/TerrainTags.cs:71).</summary>
                public static float ForestSight = 0.7f;
            }
            public static class UnitCostField
            {
                /// <summary>maps.unitCostField.parkedSpeed (x; tan_suat, was Sim/Navigation/UnitCostField.cs:23).</summary>
                public static float ParkedSpeed = 0.5f;
                /// <summary>maps.unitCostField.ringReach (m; ban_kinh, was Sim/Navigation/UnitCostField.cs:29).</summary>
                public static float RingReach = 2f;
                /// <summary>maps.unitCostField.refreshTicks (ticks; thoi_gian, was Sim/Navigation/UnitCostField.cs:32).</summary>
                public static int RefreshTicks = 10;
            }
        }

        private static readonly Entry[] Entries =
        {
            new Entry("bosses.bossHunts.weeklyMinutes", "min", () => Bosses.BossHunts.WeeklyMinutes, v => Bosses.BossHunts.WeeklyMinutes = (float)v),
            new Entry("bases.gear.bulwarkShare", "share", () => Bases.Gear.BulwarkShare, v => Bases.Gear.BulwarkShare = (float)v),
            new Entry("campaign.missionDecks.airMinimum", "count", () => Campaign.MissionDecks.AirMinimum, v => Campaign.MissionDecks.AirMinimum = (int)Math.Round(v)),
            new Entry("campaign.narrative.minersCp", "CP", () => Campaign.Narrative.MinersCp, v => Campaign.Narrative.MinersCp = (int)Math.Round(v)),
            new Entry("campaign.narrative.radarVision", "x", () => Campaign.Narrative.RadarVision, v => Campaign.Narrative.RadarVision = (float)v),
            new Entry("ai.conquestAi.clusterRadius", "m", () => Ai.ConquestAi.ClusterRadius, v => Ai.ConquestAi.ClusterRadius = (float)v),
            new Entry("ai.conquestAi.holdReach", "m", () => Ai.ConquestAi.HoldReach, v => Ai.ConquestAi.HoldReach = (float)v),
            new Entry("ai.squadLayer.shortMoveEvery", "s", () => Ai.SquadLayer.ShortMoveEvery, v => Ai.SquadLayer.ShortMoveEvery = v),
            new Entry("ai.squadLayer.threatMetres", "m", () => Ai.SquadLayer.ThreatMetres, v => Ai.SquadLayer.ThreatMetres = (float)v),
            new Entry("ai.squadLayer.breachMargin", "x", () => Ai.SquadLayer.BreachMargin, v => Ai.SquadLayer.BreachMargin = (float)v),
            new Entry("ai.squadLayer.interval", "s", () => Ai.SquadLayer.Interval, v => Ai.SquadLayer.Interval = (float)v),
            new Entry("ai.squadLayer.minSquad", "count", () => Ai.SquadLayer.MinSquad, v => Ai.SquadLayer.MinSquad = (int)Math.Round(v)),
            new Entry("ai.squadLayer.maxSquad", "count", () => Ai.SquadLayer.MaxSquad, v => Ai.SquadLayer.MaxSquad = (int)Math.Round(v)),
            new Entry("ai.squadLayer.gatherRadius", "m", () => Ai.SquadLayer.GatherRadius, v => Ai.SquadLayer.GatherRadius = (float)v),
            new Entry("ai.squadLayer.gatheredRadius", "m", () => Ai.SquadLayer.GatheredRadius, v => Ai.SquadLayer.GatheredRadius = (float)v),
            new Entry("ai.squadLayer.joinReach", "m", () => Ai.SquadLayer.JoinReach, v => Ai.SquadLayer.JoinReach = (float)v),
            new Entry("ai.squadLayer.supportReach", "m", () => Ai.SquadLayer.SupportReach, v => Ai.SquadLayer.SupportReach = (float)v),
            new Entry("ai.tacticalAi.decisionInterval", "s", () => Ai.TacticalAi.DecisionInterval, v => Ai.TacticalAi.DecisionInterval = (float)v),
            new Entry("ai.tacticalAi.boundLength", "m", () => Ai.TacticalAi.BoundLength, v => Ai.TacticalAi.BoundLength = (float)v),
            new Entry("ai.tacticalAi.flankOffset", "m", () => Ai.TacticalAi.FlankOffset, v => Ai.TacticalAi.FlankOffset = (float)v),
            new Entry("ai.tacticalAi.fastSpeed", "m/s", () => Ai.TacticalAi.FastSpeed, v => Ai.TacticalAi.FastSpeed = (float)v),
            new Entry("ai.tacticalAi.clusterRadius", "m", () => Ai.TacticalAi.ClusterRadius, v => Ai.TacticalAi.ClusterRadius = (float)v),
            new Entry("ai.tacticalAi.fallBackSeconds", "s", () => Ai.TacticalAi.FallBackSeconds, v => Ai.TacticalAi.FallBackSeconds = (float)v),
            new Entry("ai.tacticalAi.outmatchedRatio", "share", () => Ai.TacticalAi.OutmatchedRatio, v => Ai.TacticalAi.OutmatchedRatio = (float)v),
            new Entry("ai.tacticalAi.recoveredRatio", "share", () => Ai.TacticalAi.RecoveredRatio, v => Ai.TacticalAi.RecoveredRatio = (float)v),
            new Entry("ai.tacticalAi.commitSeconds", "s", () => Ai.TacticalAi.CommitSeconds, v => Ai.TacticalAi.CommitSeconds = v),
            new Entry("ai.tacticalAi.assaultOdds", "x", () => Ai.TacticalAi.AssaultOdds, v => Ai.TacticalAi.AssaultOdds = (float)v),
            new Entry("ai.tacticalAi.shellingTime", "s", () => Ai.TacticalAi.ShellingTime, v => Ai.TacticalAi.ShellingTime = v),
            new Entry("ai.tacticalAi.crateDetour", "m", () => Ai.TacticalAi.CrateDetour, v => Ai.TacticalAi.CrateDetour = (float)v),
            new Entry("ai.tacticalAi.depotReach", "m", () => Ai.TacticalAi.DepotReach, v => Ai.TacticalAi.DepotReach = (float)v),
            new Entry("ai.tacticalAi.breachReach", "m", () => Ai.TacticalAi.BreachReach, v => Ai.TacticalAi.BreachReach = (float)v),
            new Entry("ai.tacticalAi.breacherReach", "m", () => Ai.TacticalAi.BreacherReach, v => Ai.TacticalAi.BreacherReach = (float)v),
            new Entry("ai.tacticalAi.bossReach", "m", () => Ai.TacticalAi.BossReach, v => Ai.TacticalAi.BossReach = (float)v),
            new Entry("ai.tacticalAi.reinforcementGap", "m", () => Ai.TacticalAi.ReinforcementGap, v => Ai.TacticalAi.ReinforcementGap = (float)v),
            new Entry("ai.tacticalAi.homeReach", "m", () => Ai.TacticalAi.HomeReach, v => Ai.TacticalAi.HomeReach = (float)v),
            new Entry("ai.tacticalAi.waveSize", "count", () => Ai.TacticalAi.WaveSize, v => Ai.TacticalAi.WaveSize = (int)Math.Round(v)),
            new Entry("ai.tacticalAi.waveWait", "s", () => Ai.TacticalAi.WaveWait, v => Ai.TacticalAi.WaveWait = v),
            new Entry("vehicles.abilitySystem.homeReach", "m", () => Vehicles.AbilitySystem.HomeReach, v => Vehicles.AbilitySystem.HomeReach = (float)v),
            new Entry("vehicles.abilitySystem.homeRearmSeconds", "s", () => Vehicles.AbilitySystem.HomeRearmSeconds, v => Vehicles.AbilitySystem.HomeRearmSeconds = (float)v),
            new Entry("vehicles.abilitySystem.auraInterval", "s", () => Vehicles.AbilitySystem.AuraInterval, v => Vehicles.AbilitySystem.AuraInterval = (float)v),
            new Entry("vehicles.abilitySystem.mineSpotting", "m", () => Vehicles.AbilitySystem.MineSpotting, v => Vehicles.AbilitySystem.MineSpotting = (float)v),
            new Entry("vehicles.fieldWorksSystem.nightSight", "x", () => Vehicles.FieldWorksSystem.NightSight, v => Vehicles.FieldWorksSystem.NightSight = (float)v),
            new Entry("vehicles.fieldWorksSystem.decoyCheckSeconds", "s", () => Vehicles.FieldWorksSystem.DecoyCheckSeconds, v => Vehicles.FieldWorksSystem.DecoyCheckSeconds = v),
            new Entry("vehicles.fieldWorksSystem.passScanSeconds", "s", () => Vehicles.FieldWorksSystem.PassScanSeconds, v => Vehicles.FieldWorksSystem.PassScanSeconds = v),
            new Entry("vehicles.gearSystem.lastStandGap", "s", () => Vehicles.GearSystem.LastStandGap, v => Vehicles.GearSystem.LastStandGap = (float)v),
            new Entry("vehicles.gearSystem.killReadySeconds", "s", () => Vehicles.GearSystem.KillReadySeconds, v => Vehicles.GearSystem.KillReadySeconds = (float)v),
            new Entry("vehicles.gearSystem.fuelBlastCap", "HP", () => Vehicles.GearSystem.FuelBlastCap, v => Vehicles.GearSystem.FuelBlastCap = (float)v),
            new Entry("vehicles.gearSystem.laserWarningCooldown", "s", () => Vehicles.GearSystem.LaserWarningCooldown, v => Vehicles.GearSystem.LaserWarningCooldown = (float)v),
            new Entry("vehicles.gearSystem.procGap", "s", () => Vehicles.GearSystem.ProcGap, v => Vehicles.GearSystem.ProcGap = v),
            new Entry("vehicles.gearSystem.auraInterval", "s", () => Vehicles.GearSystem.AuraInterval, v => Vehicles.GearSystem.AuraInterval = (float)v),
            new Entry("vehicles.supplyRules.slowShare", "share", () => Vehicles.SupplyRules.SlowShare, v => Vehicles.SupplyRules.SlowShare = (float)v),
            new Entry("vehicles.supplyRules.returnShare", "share", () => Vehicles.SupplyRules.ReturnShare, v => Vehicles.SupplyRules.ReturnShare = (float)v),
            new Entry("vehicles.supplyRules.bomberShare", "share", () => Vehicles.SupplyRules.BomberShare, v => Vehicles.SupplyRules.BomberShare = (float)v),
            new Entry("vehicles.supplyRules.padRate", "x", () => Vehicles.SupplyRules.PadRate, v => Vehicles.SupplyRules.PadRate = (float)v),
            new Entry("vehicles.supplyRules.hqRate", "x", () => Vehicles.SupplyRules.HqRate, v => Vehicles.SupplyRules.HqRate = (float)v),
            new Entry("vehicles.supplyRules.carrierRate", "x", () => Vehicles.SupplyRules.CarrierRate, v => Vehicles.SupplyRules.CarrierRate = (float)v),
            new Entry("vehicles.supplySystem.safeSeconds", "s", () => Vehicles.SupplySystem.SafeSeconds, v => Vehicles.SupplySystem.SafeSeconds = v),
            new Entry("vehicles.supplySystem.lowShare", "share", () => Vehicles.SupplySystem.LowShare, v => Vehicles.SupplySystem.LowShare = (float)v),
            new Entry("vehicles.supplySystem.hqHeal", "share/s", () => Vehicles.SupplySystem.HqHeal, v => Vehicles.SupplySystem.HqHeal = (float)v),
            new Entry("vehicles.supplySystem.hqReach", "m", () => Vehicles.SupplySystem.HqReach, v => Vehicles.SupplySystem.HqReach = (float)v),
            new Entry("vehicles.supplySystem.carrierReach", "m", () => Vehicles.SupplySystem.CarrierReach, v => Vehicles.SupplySystem.CarrierReach = (float)v),
            new Entry("bosses.bossSystem.flyerTicks", "ticks", () => Bosses.BossSystem.FlyerTicks, v => Bosses.BossSystem.FlyerTicks = (int)Math.Round(v)),
            new Entry("bosses.bossSystem.missileTopSpeed", "m/s", () => Bosses.BossSystem.MissileTopSpeed, v => Bosses.BossSystem.MissileTopSpeed = (float)v),
            new Entry("bosses.bossSystem.escortTicks", "ticks", () => Bosses.BossSystem.EscortTicks, v => Bosses.BossSystem.EscortTicks = (int)Math.Round(v)),
            new Entry("bosses.bossSystem.bodyShare", "share", () => Bosses.BossSystem.BodyShare, v => Bosses.BossSystem.BodyShare = v),
            new Entry("bosses.navalSystem.bigShipLength", "m", () => Bosses.NavalSystem.BigShipLength, v => Bosses.NavalSystem.BigShipLength = (float)v),
            new Entry("bosses.navalSystem.gapExtra", "m", () => Bosses.NavalSystem.GapExtra, v => Bosses.NavalSystem.GapExtra = (float)v),
            new Entry("bosses.navalSystem.closeRate", "share/s", () => Bosses.NavalSystem.CloseRate, v => Bosses.NavalSystem.CloseRate = (float)v),
            new Entry("bosses.navalSystem.holdAfterTicks", "ticks", () => Bosses.NavalSystem.HoldAfterTicks, v => Bosses.NavalSystem.HoldAfterTicks = (int)Math.Round(v)),
            new Entry("bosses.navalSystem.holdMinTicks", "ticks", () => Bosses.NavalSystem.HoldMinTicks, v => Bosses.NavalSystem.HoldMinTicks = (int)Math.Round(v)),
            new Entry("bosses.navalSystem.slotSlack", "m", () => Bosses.NavalSystem.SlotSlack, v => Bosses.NavalSystem.SlotSlack = (float)v),
            new Entry("bosses.navalSystem.slotSample", "m", () => Bosses.NavalSystem.SlotSample, v => Bosses.NavalSystem.SlotSample = (float)v),
            new Entry("bosses.navalSystem.turnWarn", "deg", () => Bosses.NavalSystem.TurnWarn, v => Bosses.NavalSystem.TurnWarn = (float)v),
            new Entry("bosses.navalSystem.captureRadius", "m", () => Bosses.NavalSystem.CaptureRadius, v => Bosses.NavalSystem.CaptureRadius = (float)v),
            new Entry("bosses.navalSystem.lighthouseRadius", "m", () => Bosses.NavalSystem.LighthouseRadius, v => Bosses.NavalSystem.LighthouseRadius = (float)v),
            new Entry("weapons.combatSystem.axisRatio", "x", () => Weapons.CombatSystem.AxisRatio, v => Weapons.CombatSystem.AxisRatio = (float)v),
            new Entry("weapons.combatSystem.counterBatteryPriority", "score", () => Weapons.CombatSystem.CounterBatteryPriority, v => Weapons.CombatSystem.CounterBatteryPriority = (float)v),
            new Entry("weapons.combatSystem.crowdMax", "count", () => Weapons.CombatSystem.CrowdMax, v => Weapons.CombatSystem.CrowdMax = (float)v),
            new Entry("weapons.combatSystem.reloadStillSpeed", "m/s", () => Weapons.CombatSystem.ReloadStillSpeed, v => Weapons.CombatSystem.ReloadStillSpeed = (float)v),
            new Entry("weapons.combatSystem.retargetSeconds", "s", () => Weapons.CombatSystem.RetargetSeconds, v => Weapons.CombatSystem.RetargetSeconds = (float)v),
            new Entry("weapons.combatSystem.bombedRadius", "m", () => Weapons.CombatSystem.BombedRadius, v => Weapons.CombatSystem.BombedRadius = (float)v),
            new Entry("weapons.combatSystem.bombedSeconds", "s", () => Weapons.CombatSystem.BombedSeconds, v => Weapons.CombatSystem.BombedSeconds = v),
            new Entry("weapons.combatSystem.twinGap", "s", () => Weapons.CombatSystem.TwinGap, v => Weapons.CombatSystem.TwinGap = (float)v),
            new Entry("weapons.combatSystem.restSeconds", "s", () => Weapons.CombatSystem.RestSeconds, v => Weapons.CombatSystem.RestSeconds = (float)v),
            new Entry("weapons.combatSystem.runDamage", "x", () => Weapons.CombatSystem.RunDamage, v => Weapons.CombatSystem.RunDamage = (float)v),
            new Entry("weapons.combatSystem.twinOffset", "s", () => Weapons.CombatSystem.TwinOffset, v => Weapons.CombatSystem.TwinOffset = (float)v),
            new Entry("weapons.damageSystem.engineerBreach", "x", () => Weapons.DamageSystem.EngineerBreach, v => Weapons.DamageSystem.EngineerBreach = (float)v),
            new Entry("weapons.damageSystem.fireAfterburn", "share", () => Weapons.DamageSystem.FireAfterburn, v => Weapons.DamageSystem.FireAfterburn = (float)v),
            new Entry("weapons.damageSystem.fireBurnSeconds", "s", () => Weapons.DamageSystem.FireBurnSeconds, v => Weapons.DamageSystem.FireBurnSeconds = (float)v),
            new Entry("weapons.damageSystem.smokeEnergyCut", "share", () => Weapons.DamageSystem.SmokeEnergyCut, v => Weapons.DamageSystem.SmokeEnergyCut = (float)v),
            Entry.FloatArray("weapons.damageTable.defaultPenetration", "x", () => Weapons.DamageTable.DefaultPenetration, v => Weapons.DamageTable.DefaultPenetration = v),
            new Entry("vehicles.vehicleDef.stealthSight", "x", () => Vehicles.VehicleDef.StealthSight, v => Vehicles.VehicleDef.StealthSight = (float)v),
            new Entry("weapons.weaponDef.minSwitchSeconds", "s", () => Weapons.WeaponDef.MinSwitchSeconds, v => Weapons.WeaponDef.MinSwitchSeconds = (float)v),
            new Entry("weapons.weaponDef.roundHoldSeconds", "s", () => Weapons.WeaponDef.RoundHoldSeconds, v => Weapons.WeaponDef.RoundHoldSeconds = (float)v),
            new Entry("vehicles.relayDef.maxPerBase", "count", () => Vehicles.RelayDef.MaxPerBase, v => Vehicles.RelayDef.MaxPerBase = (int)Math.Round(v)),
            new Entry("weapons.weaponDef.maxEdge", "x", () => Weapons.WeaponDef.MaxEdge, v => Weapons.WeaponDef.MaxEdge = (float)v),
            new Entry("weapons.weaponDef.heArmourMax", "armour level", () => Weapons.WeaponDef.HeArmourMax, v => Weapons.WeaponDef.HeArmourMax = (int)Math.Round(v)),
            new Entry("weapons.weaponDef.maxEdgeT5", "x", () => Weapons.WeaponDef.MaxEdgeT5, v => Weapons.WeaponDef.MaxEdgeT5 = (float)v),
            new Entry("weapons.weaponDef.escapeSpeed", "m/s", () => Weapons.WeaponDef.EscapeSpeed, v => Weapons.WeaponDef.EscapeSpeed = (float)v),
            new Entry("weapons.weaponDef.maxWarning", "s", () => Weapons.WeaponDef.MaxWarning, v => Weapons.WeaponDef.MaxWarning = (float)v),
            new Entry("modes.teamEconomy.maxVehicles", "count", () => Modes.TeamEconomy.MaxVehicles, v => Modes.TeamEconomy.MaxVehicles = (int)Math.Round(v)),
            new Entry("modes.teamEconomy.maxAircraft", "count", () => Modes.TeamEconomy.MaxAircraft, v => Modes.TeamEconomy.MaxAircraft = (int)Math.Round(v)),
            new Entry("modes.economySystem.maxCatchUp", "share", () => Modes.EconomySystem.MaxCatchUp, v => Modes.EconomySystem.MaxCatchUp = (float)v),
            new Entry("modes.economySystem.catchUpBelow", "share", () => Modes.EconomySystem.CatchUpBelow, v => Modes.EconomySystem.CatchUpBelow = (float)v),
            new Entry("modes.economySystem.catchUpMinimumArmy", "CP", () => Modes.EconomySystem.CatchUpMinimumArmy, v => Modes.EconomySystem.CatchUpMinimumArmy = (int)Math.Round(v)),
            new Entry("modes.economySystem.catchUpSettle", "s", () => Modes.EconomySystem.CatchUpSettle, v => Modes.EconomySystem.CatchUpSettle = (float)v),
            new Entry("modes.economySystem.deliverySeconds", "s", () => Modes.EconomySystem.DeliverySeconds, v => Modes.EconomySystem.DeliverySeconds = (float)v),
            new Entry("modes.economySystem.rollIn", "m", () => Modes.EconomySystem.RollIn, v => Modes.EconomySystem.RollIn = (float)v),
            new Entry("modes.economySystem.killReward", "share", () => Modes.EconomySystem.KillReward, v => Modes.EconomySystem.KillReward = (float)v),
            new Entry("modes.economySystem.killRefundCap", "share", () => Modes.EconomySystem.KillRefundCap, v => Modes.EconomySystem.KillRefundCap = (float)v),
            new Entry("modes.economySystem.lossRefundCap", "share", () => Modes.EconomySystem.LossRefundCap, v => Modes.EconomySystem.LossRefundCap = (float)v),
            new Entry("bases.baseSystem.lookEvery", "s", () => Bases.BaseSystem.LookEvery, v => Bases.BaseSystem.LookEvery = v),
            new Entry("modes.battleEvents.crateFall", "s", () => Modes.BattleEvents.CrateFall, v => Modes.BattleEvents.CrateFall = (float)v),
            new Entry("modes.battleEvents.crateLife", "s", () => Modes.BattleEvents.CrateLife, v => Modes.BattleEvents.CrateLife = (float)v),
            new Entry("modes.battleEvents.claimReach", "m", () => Modes.BattleEvents.ClaimReach, v => Modes.BattleEvents.ClaimReach = (float)v),
            new Entry("modes.battleEvents.claimSeconds", "s", () => Modes.BattleEvents.ClaimSeconds, v => Modes.BattleEvents.ClaimSeconds = (float)v),
            new Entry("modes.battleEvents.crateCp", "CP", () => Modes.BattleEvents.CrateCp, v => Modes.BattleEvents.CrateCp = (float)v),
            new Entry("modes.battleEvents.crateRepair", "share", () => Modes.BattleEvents.CrateRepair, v => Modes.BattleEvents.CrateRepair = (float)v),
            new Entry("bosses.bossHunt.weeklyMinis", "count", () => Bosses.BossHunt.WeeklyMinis, v => Bosses.BossHunt.WeeklyMinis = (int)Math.Round(v)),
            new Entry("bosses.bossHunt.airDefenceMains", "count", () => Bosses.BossHunt.AirDefenceMains, v => Bosses.BossHunt.AirDefenceMains = (int)Math.Round(v)),
            new Entry("bosses.bossHunt.airDefenceMinis", "count", () => Bosses.BossHunt.AirDefenceMinis, v => Bosses.BossHunt.AirDefenceMinis = (int)Math.Round(v)),
            new Entry("bosses.huntSupports.cap", "share", () => Bosses.HuntSupports.Cap, v => Bosses.HuntSupports.Cap = (float)v),
            new Entry("modes.endlessRules.enemyPerWave", "share/wave", () => Modes.EndlessRules.EnemyPerWave, v => Modes.EndlessRules.EnemyPerWave = (float)v),
            new Entry("modes.endlessRules.playerPerWave", "share/wave", () => Modes.EndlessRules.PlayerPerWave, v => Modes.EndlessRules.PlayerPerWave = (float)v),
            new Entry("modes.endlessRules.playerMax", "share", () => Modes.EndlessRules.PlayerMax, v => Modes.EndlessRules.PlayerMax = (float)v),
            new Entry("modes.endlessRules.miniBossEvery", "waves", () => Modes.EndlessRules.MiniBossEvery, v => Modes.EndlessRules.MiniBossEvery = (int)Math.Round(v)),
            new Entry("modes.endlessRules.bossEvery", "waves", () => Modes.EndlessRules.BossEvery, v => Modes.EndlessRules.BossEvery = (int)Math.Round(v)),
            new Entry("modes.endlessRules.survivalWaves", "waves", () => Modes.EndlessRules.SurvivalWaves, v => Modes.EndlessRules.SurvivalWaves = (int)Math.Round(v)),
            new Entry("modes.endlessRules.defendFiniteWaves", "waves", () => Modes.EndlessRules.DefendFiniteWaves, v => Modes.EndlessRules.DefendFiniteWaves = (int)Math.Round(v)),
            new Entry("modes.endlessRules.waveCoins", "coins", () => Modes.EndlessRules.WaveCoins, v => Modes.EndlessRules.WaveCoins = (int)Math.Round(v)),
            new Entry("modes.endlessRules.bossCoins", "coins", () => Modes.EndlessRules.BossCoins, v => Modes.EndlessRules.BossCoins = (int)Math.Round(v)),
            new Entry("modes.endlessRules.dailyCap", "coins", () => Modes.EndlessRules.DailyCap, v => Modes.EndlessRules.DailyCap = (int)Math.Round(v)),
            Entry.IntArray("modes.endlessRules.waveBadges", "waves", () => Modes.EndlessRules.WaveBadges, v => Modes.EndlessRules.WaveBadges = v),
            Entry.IntArray("modes.endlessRules.bossBadges", "bosses", () => Modes.EndlessRules.BossBadges, v => Modes.EndlessRules.BossBadges = v),
            new Entry("campaign.missionEventSystem.rowGap", "s", () => Campaign.MissionEventSystem.RowGap, v => Campaign.MissionEventSystem.RowGap = v),
            new Entry("campaign.missionEventSystem.pushSeconds", "s", () => Campaign.MissionEventSystem.PushSeconds, v => Campaign.MissionEventSystem.PushSeconds = v),
            new Entry("campaign.missionMode.captureSeconds", "s", () => Campaign.MissionMode.CaptureSeconds, v => Campaign.MissionMode.CaptureSeconds = (float)v),
            new Entry("campaign.missionMode.waypointReach", "m", () => Campaign.MissionMode.WaypointReach, v => Campaign.MissionMode.WaypointReach = (float)v),
            new Entry("campaign.missionMode.scoutSeconds", "s", () => Campaign.MissionMode.ScoutSeconds, v => Campaign.MissionMode.ScoutSeconds = (float)v),
            new Entry("campaign.missionMode.escortReach", "m", () => Campaign.MissionMode.EscortReach, v => Campaign.MissionMode.EscortReach = (float)v),
            new Entry("campaign.missionMode.reinforceFirst", "s", () => Campaign.MissionMode.ReinforceFirst, v => Campaign.MissionMode.ReinforceFirst = v),
            new Entry("campaign.missionMode.reinforceGap", "s", () => Campaign.MissionMode.ReinforceGap, v => Campaign.MissionMode.ReinforceGap = v),
            new Entry("campaign.missionMode.reinforceBelow", "share", () => Campaign.MissionMode.ReinforceBelow, v => Campaign.MissionMode.ReinforceBelow = (float)v),
            new Entry("campaign.missionMode.fleeSeconds", "s", () => Campaign.MissionMode.FleeSeconds, v => Campaign.MissionMode.FleeSeconds = v),
            new Entry("modes.outposts.neutralHealth", "x", () => Modes.Outposts.NeutralHealth, v => Modes.Outposts.NeutralHealth = (float)v),
            new Entry("modes.outposts.buildSeconds", "s", () => Modes.Outposts.BuildSeconds, v => Modes.Outposts.BuildSeconds = (float)v),
            new Entry("modes.outposts.rebuildSeconds", "s", () => Modes.Outposts.RebuildSeconds, v => Modes.Outposts.RebuildSeconds = (float)v),
            new Entry("modes.outposts.respawnSeconds", "s", () => Modes.Outposts.RespawnSeconds, v => Modes.Outposts.RespawnSeconds = (float)v),
            new Entry("modes.neutralSystem.interval", "s", () => Modes.NeutralSystem.Interval, v => Modes.NeutralSystem.Interval = (float)v),
            new Entry("campaign.operationMode.choiceSeconds", "s", () => Campaign.OperationMode.ChoiceSeconds, v => Campaign.OperationMode.ChoiceSeconds = v),
            new Entry("modes.sandboxMode.firstWaveDelay", "s", () => Modes.SandboxMode.FirstWaveDelay, v => Modes.SandboxMode.FirstWaveDelay = (float)v),
            new Entry("modes.sandboxMode.waveInterval", "s", () => Modes.SandboxMode.WaveInterval, v => Modes.SandboxMode.WaveInterval = (float)v),
            new Entry("modes.sandboxMode.reinforceCooldownSeconds", "s", () => Modes.SandboxMode.ReinforceCooldownSeconds, v => Modes.SandboxMode.ReinforceCooldownSeconds = (float)v),
            new Entry("vehicles.movementSystem.ghostSeconds", "s", () => Vehicles.MovementSystem.GhostSeconds, v => Vehicles.MovementSystem.GhostSeconds = v),
            new Entry("vehicles.movementSystem.maxYieldDepth", "count", () => Vehicles.MovementSystem.MaxYieldDepth, v => Vehicles.MovementSystem.MaxYieldDepth = (int)Math.Round(v)),
            new Entry("vehicles.movementSystem.yieldMaxSeconds", "s", () => Vehicles.MovementSystem.YieldMaxSeconds, v => Vehicles.MovementSystem.YieldMaxSeconds = v),
            new Entry("vehicles.movementSystem.yieldHoldSeconds", "s", () => Vehicles.MovementSystem.YieldHoldSeconds, v => Vehicles.MovementSystem.YieldHoldSeconds = v),
            new Entry("vehicles.movementSystem.yieldCooldown", "s", () => Vehicles.MovementSystem.YieldCooldown, v => Vehicles.MovementSystem.YieldCooldown = v),
            new Entry("vehicles.movementSystem.yieldWaitSeconds", "s", () => Vehicles.MovementSystem.YieldWaitSeconds, v => Vehicles.MovementSystem.YieldWaitSeconds = v),
            new Entry("vehicles.movementSystem.gatherReach", "m", () => Vehicles.MovementSystem.GatherReach, v => Vehicles.MovementSystem.GatherReach = (float)v),
            new Entry("vehicles.movementSystem.minCostRepathGap", "s", () => Vehicles.MovementSystem.MinCostRepathGap, v => Vehicles.MovementSystem.MinCostRepathGap = v),
            new Entry("vehicles.movementSystem.pathNodeBudgetPerTick", "nodes/tick", () => Vehicles.MovementSystem.PathNodeBudgetPerTick, v => Vehicles.MovementSystem.PathNodeBudgetPerTick = (int)Math.Round(v)),
            new Entry("vehicles.movementSystem.maxNodesPerSearch", "nodes", () => Vehicles.MovementSystem.MaxNodesPerSearch, v => Vehicles.MovementSystem.MaxNodesPerSearch = (int)Math.Round(v)),
            new Entry("vehicles.movementSystem.minSearchBudget", "nodes", () => Vehicles.MovementSystem.MinSearchBudget, v => Vehicles.MovementSystem.MinSearchBudget = (int)Math.Round(v)),
            new Entry("vehicles.movementSystem.detourCap", "x", () => Vehicles.MovementSystem.DetourCap, v => Vehicles.MovementSystem.DetourCap = (float)v),
            new Entry("vehicles.movementSystem.noAlternativeLength", "m", () => Vehicles.MovementSystem.NoAlternativeLength, v => Vehicles.MovementSystem.NoAlternativeLength = (float)v),
            new Entry("vehicles.movementSystem.queueSeconds", "s", () => Vehicles.MovementSystem.QueueSeconds, v => Vehicles.MovementSystem.QueueSeconds = v),
            new Entry("vehicles.movementSystem.headOnReverseMax", "m", () => Vehicles.MovementSystem.HeadOnReverseMax, v => Vehicles.MovementSystem.HeadOnReverseMax = (float)v),
            new Entry("vehicles.movementSystem.reverseSpeedShare", "share", () => Vehicles.MovementSystem.ReverseSpeedShare, v => Vehicles.MovementSystem.ReverseSpeedShare = (float)v),
            new Entry("vehicles.movementSystem.headOnWait", "s", () => Vehicles.MovementSystem.HeadOnWait, v => Vehicles.MovementSystem.HeadOnWait = v),
            new Entry("vehicles.movementSystem.backOffDistance", "m", () => Vehicles.MovementSystem.BackOffDistance, v => Vehicles.MovementSystem.BackOffDistance = (float)v),
            new Entry("vehicles.movementSystem.trafficBehindReach", "m", () => Vehicles.MovementSystem.TrafficBehindReach, v => Vehicles.MovementSystem.TrafficBehindReach = (float)v),
            new Entry("vehicles.movementSystem.offLaneSeconds", "s", () => Vehicles.MovementSystem.OffLaneSeconds, v => Vehicles.MovementSystem.OffLaneSeconds = v),
            new Entry("vehicles.movementSystem.sameGoalReach", "m", () => Vehicles.MovementSystem.SameGoalReach, v => Vehicles.MovementSystem.SameGoalReach = (float)v),
            new Entry("vehicles.movementSystem.gateHoldTicks", "ticks", () => Vehicles.MovementSystem.GateHoldTicks, v => Vehicles.MovementSystem.GateHoldTicks = (int)Math.Round(v)),
            new Entry("vehicles.movementSystem.gateTurnSeconds", "s", () => Vehicles.MovementSystem.GateTurnSeconds, v => Vehicles.MovementSystem.GateTurnSeconds = v),
            new Entry("vehicles.movementSystem.gateWaitMax", "s", () => Vehicles.MovementSystem.GateWaitMax, v => Vehicles.MovementSystem.GateWaitMax = v),
            Entry.FloatArray("vehicles.movementSystem.gateWaitLateral", "s", () => Vehicles.MovementSystem.GateWaitLateral, v => Vehicles.MovementSystem.GateWaitLateral = v),
            Entry.FloatArray("vehicles.movementSystem.gateWaitBack", "s", () => Vehicles.MovementSystem.GateWaitBack, v => Vehicles.MovementSystem.GateWaitBack = v),
            new Entry("vehicles.movementSystem.headOnOpenWait", "s", () => Vehicles.MovementSystem.HeadOnOpenWait, v => Vehicles.MovementSystem.HeadOnOpenWait = v),
            new Entry("vehicles.movementSystem.repathInterval", "s", () => Vehicles.MovementSystem.RepathInterval, v => Vehicles.MovementSystem.RepathInterval = (float)v),
            new Entry("vehicles.movementSystem.stuckDistance", "m", () => Vehicles.MovementSystem.StuckDistance, v => Vehicles.MovementSystem.StuckDistance = (float)v),
            new Entry("vehicles.movementSystem.stuckDetourDistance", "m", () => Vehicles.MovementSystem.StuckDetourDistance, v => Vehicles.MovementSystem.StuckDetourDistance = (float)v),
            new Entry("vehicles.movementSystem.arrivalReach", "m", () => Vehicles.MovementSystem.ArrivalReach, v => Vehicles.MovementSystem.ArrivalReach = (float)v),
            new Entry("vehicles.movementSystem.separationSlack", "m", () => Vehicles.MovementSystem.SeparationSlack, v => Vehicles.MovementSystem.SeparationSlack = (float)v),
            new Entry("vehicles.movementSystem.settleDistance", "m", () => Vehicles.MovementSystem.SettleDistance, v => Vehicles.MovementSystem.SettleDistance = (float)v),
            new Entry("vehicles.movementSystem.avoidSeconds", "s", () => Vehicles.MovementSystem.AvoidSeconds, v => Vehicles.MovementSystem.AvoidSeconds = v),
            new Entry("vehicles.movementSystem.separationStiffness", "x", () => Vehicles.MovementSystem.SeparationStiffness, v => Vehicles.MovementSystem.SeparationStiffness = (float)v),
            new Entry("vehicles.movementSystem.maxPush", "m", () => Vehicles.MovementSystem.MaxPush, v => Vehicles.MovementSystem.MaxPush = (float)v),
            new Entry("vehicles.movementSystem.guardLeash", "m", () => Vehicles.MovementSystem.GuardLeash, v => Vehicles.MovementSystem.GuardLeash = (float)v),
            new Entry("vehicles.movementSystem.answerFireSeconds", "s", () => Vehicles.MovementSystem.AnswerFireSeconds, v => Vehicles.MovementSystem.AnswerFireSeconds = (float)v),
            new Entry("vehicles.movementSystem.manualHoldSeconds", "s", () => Vehicles.MovementSystem.ManualHoldSeconds, v => Vehicles.MovementSystem.ManualHoldSeconds = (float)v),
            new Entry("vehicles.movementSystem.hoverShare", "share", () => Vehicles.MovementSystem.HoverShare, v => Vehicles.MovementSystem.HoverShare = (float)v),
            new Entry("vehicles.movementSystem.chaseShare", "share", () => Vehicles.MovementSystem.ChaseShare, v => Vehicles.MovementSystem.ChaseShare = (float)v),
            new Entry("vehicles.railSystem.minWarning", "s", () => Vehicles.RailSystem.MinWarning, v => Vehicles.RailSystem.MinWarning = (float)v),
            new Entry("vehicles.railSystem.warnFloor", "s", () => Vehicles.RailSystem.WarnFloor, v => Vehicles.RailSystem.WarnFloor = (float)v),
            new Entry("vehicles.railSystem.clearHoldTicks", "ticks", () => Vehicles.RailSystem.ClearHoldTicks, v => Vehicles.RailSystem.ClearHoldTicks = (int)Math.Round(v)),
            new Entry("vehicles.railSystem.ramDamage", "HP", () => Vehicles.RailSystem.RamDamage, v => Vehicles.RailSystem.RamDamage = (float)v),
            new Entry("vehicles.railSystem.supportLength", "m", () => Vehicles.RailSystem.SupportLength, v => Vehicles.RailSystem.SupportLength = (float)v),
            new Entry("vehicles.railSystem.supportWait", "s", () => Vehicles.RailSystem.SupportWait, v => Vehicles.RailSystem.SupportWait = (float)v),
            new Entry("vehicles.railSystem.supportHalfWidth", "m", () => Vehicles.RailSystem.SupportHalfWidth, v => Vehicles.RailSystem.SupportHalfWidth = (float)v),
            new Entry("vehicles.railSystem.tellEvery", "s", () => Vehicles.RailSystem.TellEvery, v => Vehicles.RailSystem.TellEvery = v),
            new Entry("vehicles.railSystem.attachReach", "m", () => Vehicles.RailSystem.AttachReach, v => Vehicles.RailSystem.AttachReach = (float)v),
            new Entry("maps.entryGate.outerLength", "m", () => Maps.EntryGate.OuterLength, v => Maps.EntryGate.OuterLength = (float)v),
            new Entry("maps.laneMap.narrowWidth", "m", () => Maps.LaneMap.NarrowWidth, v => Maps.LaneMap.NarrowWidth = (float)v),
            new Entry("maps.laneMap.maxNoParkCells", "cells", () => Maps.LaneMap.MaxNoParkCells, v => Maps.LaneMap.MaxNoParkCells = (int)Math.Round(v)),
            new Entry("maps.laneMap.routeHalfWidth", "m", () => Maps.LaneMap.RouteHalfWidth, v => Maps.LaneMap.RouteHalfWidth = (float)v),
            new Entry("maps.laneMap.maxClearance", "cells", () => Maps.LaneMap.MaxClearance, v => Maps.LaneMap.MaxClearance = (int)Math.Round(v)),
            new Entry("maps.laneMap.rebuildInterval", "s", () => Maps.LaneMap.RebuildInterval, v => Maps.LaneMap.RebuildInterval = v),
            new Entry("maps.seaRouteGraph.exitReach", "m", () => Maps.SeaRouteGraph.ExitReach, v => Maps.SeaRouteGraph.ExitReach = (float)v),
            new Entry("maps.seaRouteGraph.bayReach", "m", () => Maps.SeaRouteGraph.BayReach, v => Maps.SeaRouteGraph.BayReach = (float)v),
            new Entry("maps.spawnPoints.gateReach", "m", () => Maps.SpawnPoints.GateReach, v => Maps.SpawnPoints.GateReach = (float)v),
            new Entry("maps.terrainRules.roadSpeed", "x", () => Maps.TerrainRules.RoadSpeed, v => Maps.TerrainRules.RoadSpeed = (float)v),
            new Entry("maps.terrainRules.roughSpeed", "x", () => Maps.TerrainRules.RoughSpeed, v => Maps.TerrainRules.RoughSpeed = (float)v),
            new Entry("maps.terrainRules.forestSpeed", "x", () => Maps.TerrainRules.ForestSpeed, v => Maps.TerrainRules.ForestSpeed = (float)v),
            new Entry("maps.terrainRules.waterSpeed", "x", () => Maps.TerrainRules.WaterSpeed, v => Maps.TerrainRules.WaterSpeed = (float)v),
            new Entry("maps.terrainRules.forestSight", "x", () => Maps.TerrainRules.ForestSight, v => Maps.TerrainRules.ForestSight = (float)v),
            new Entry("maps.unitCostField.parkedSpeed", "x", () => Maps.UnitCostField.ParkedSpeed, v => Maps.UnitCostField.ParkedSpeed = (float)v),
            new Entry("maps.unitCostField.ringReach", "m", () => Maps.UnitCostField.RingReach, v => Maps.UnitCostField.RingReach = (float)v),
            new Entry("maps.unitCostField.refreshTicks", "ticks", () => Maps.UnitCostField.RefreshTicks, v => Maps.UnitCostField.RefreshTicks = (int)Math.Round(v)),
            new Entry("modes.sandboxBattle.unlimitedCp", "CP", () => Modes.SandboxBattle.UnlimitedCp, v => Modes.SandboxBattle.UnlimitedCp = (float)v),
            new Entry("modes.sandboxRules.vehicleCap", "count", () => Modes.SandboxRules.VehicleCap, v => Modes.SandboxRules.VehicleCap = (int)Math.Round(v)),
            new Entry("modes.sandboxRules.aircraftCap", "count", () => Modes.SandboxRules.AircraftCap, v => Modes.SandboxRules.AircraftCap = (int)Math.Round(v)),
            new Entry("modes.sandboxRules.maxRank", "rank", () => Modes.SandboxRules.MaxRank, v => Modes.SandboxRules.MaxRank = (int)Math.Round(v)),
            new Entry("modes.simWorld.homeRadius", "m", () => Modes.SimWorld.HomeRadius, v => Modes.SimWorld.HomeRadius = (float)v),
            new Entry("modes.simWorld.entrenchSeconds", "s", () => Modes.SimWorld.EntrenchSeconds, v => Modes.SimWorld.EntrenchSeconds = (float)v),
            new Entry("modes.simWorld.lighthouseSight", "m", () => Modes.SimWorld.LighthouseSight, v => Modes.SimWorld.LighthouseSight = (float)v),
        };
    }
}
