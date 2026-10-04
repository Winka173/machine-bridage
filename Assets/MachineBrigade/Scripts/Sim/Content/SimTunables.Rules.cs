#nullable enable

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Balance pack (lane B, rules B and C): the formulas' numbers that were literals inside the code (the supply's upkeep
    /// curve, the catch-up, the kill pay) and the locked pricing rules the data was built by (price groups, the power
    /// bonus, the drop time by group), plus the HOLD flags kept off. Same defaults as the code had.
    /// </summary>
    public static partial class SimTunables
    {
        public static partial class Modes
        {
            /// <summary>The supply (upkeep) curve, the underdog's catch-up and the kill pay (TeamEconomy / EconomySystem).</summary>
            public static partial class EconomyRules
            {
                /// <summary>Supply = floor(army cap x this): the army value kept up at full income (was "ArmyCap * 3 / 2").</summary>
                public static float SupplyPerArmyCap = 1.5f;

                /// <summary>Income share lost per supply's worth of army above the supply (half at twice the supply).</summary>
                public static float UpkeepSlope = 0.5f;

                /// <summary>The lowest income share upkeep leaves (0.25: at most -75 %).</summary>
                public static float UpkeepFloor = 0.25f;

                /// <summary>The army ratio at which the catch-up boost is full (it starts at CatchUpBelow).</summary>
                public static float CatchUpOddsFloor = 0.2f;

                /// <summary>A kill's pay by the odds: the square root of the armies' ratio, clamped to this range.</summary>
                public static float BountyMin = 0.5f, BountyMax = 1.5f;

                /// <summary>Seconds after its last hit that a destroyed vehicle still pays the side that hit it.</summary>
                public static double KillCreditSeconds = 10.0;

                /// <summary>
                /// Balance pack rule C (the HOLD supply threshold, E2): the mode's army cap (the supply threshold's base) x this, for
                /// the prices the price groups raised; 1.16 is the repo's average price factor (economy.startCp.scale, prompt 32 L6).
                /// Bonuses (modules, hunt supports) are added after it, unscaled.
                /// </summary>
                public static float SupplyPriceScale = 1.16f;
            }

            /// <summary>Flags for rules kept off (HOLD): true has no code path yet; off is today's behaviour.</summary>
            public static partial class HoldFlags
            {
                /// <summary>Forward drops at a held outpost in the quick modes (today: only campaign missions that mark outposts).</summary>
                public static bool OutpostForwardDropsQuickModes;

                /// <summary>The sheet's LATER battle events in the quick modes (today: campaign missions only).</summary>
                public static bool LaterEventsQuickModes;

                /// <summary>The sheet's LATER neutral sites (today: none in the data).</summary>
                public static bool LaterNeutrals;
            }
        }

        public static partial class Bosses
        {
            public static partial class BossHunt
            {
                /// <summary>Main bosses in the week's hunt.</summary>
                public static int WeeklyMains = 3;

                /// <summary>The full hunt's strength ramp, first boss to last (x).</summary>
                public static float FullFrom = 0.8f, FullTo = 1.3f;

                /// <summary>The week's hunt: each next boss this much stronger (x per boss).</summary>
                public static float WeeklyStep = 0.06f;
            }

            /// <summary>The Boss Hunt's time-to-kill targets (BossRushRules; seconds a mini and a main boss should take).</summary>
            public static partial class BossRushRules
            {
                public static float MiniSeconds = 66f, MainSeconds = 168f;

                /// <summary>The full hunt's targets.</summary>
                public static float FullMiniSeconds = 60f, FullMainSeconds = 150f;

                /// <summary>The share of power x time the boss's health is (the army does not hit all the time).</summary>
                public static float HpShare = 0.6f;
            }
        }

        public static partial class Weapons
        {
            /// <summary>
            /// Play-test 13 (lane C): the two vehicle self-defences (flares, hard-kill APS) work on every threat that arrives
            /// together, as a flare cloud or one APS activation does in real life; the APS reloads slower to pay for it.
            /// </summary>
            public static partial class Countermeasures
            {
                /// <summary>A flare release is cued when an IR missile is this close to arriving (s): the missile warner's terminal cue.</summary>
                public static float FlareCueSeconds = 1.5f;

                /// <summary>A missile arriving up to this long after the cloud burns out is still inside its window (s).</summary>
                public static float FlareGraceSeconds = 0.5f;

                /// <summary>One APS activation takes every round reaching the vehicle within this long of it (s).</summary>
                public static float ApsVolleySeconds = 0.4f;

                /// <summary>A vehicle APS's interceptor comes back this many times slower (x): the price of the volley rule.</summary>
                public static float ApsRechargeScale = 1.5f;
            }
        }

        public static partial class Modes
        {
            public static partial class EndlessRules
            {
                /// <summary>The enemy's strength per boss step in the boss-only endless run (x per step).</summary>
                public static float EnemyPerBoss = 0.08f;

                /// <summary>Each next reward of the same kind pays this share of the last (coins x 0.9^k).</summary>
                public static double CoinDecay = 0.9;
            }
        }

        public static partial class Vehicles
        {
            /// <summary>
            /// The locked pricing rules (owner, balance round 2; manifest_v2 B1 / B5 / S04): the data's prices, outgoing damage
            /// and drop times were built by them. The game reads the built numbers; the export reads these (Xe_suy_ra).
            /// </summary>
            public static partial class PriceRules
            {
                /// <summary>Upper baseCP of each price group but the last (≤ 4, 5-8, 9-13, ≥ 14).</summary>
                public static int[] GroupMaxCp = { 4, 8, 13 };

                /// <summary>Each group's price factor (rounded half up after it).</summary>
                public static float[] GroupFactor = { 1f, 1.15f, 1.25f, 1.3f };

                /// <summary>Power bonus = min(BonusCap, BonusPerCp x (baseCP - BonusFromCp)), never below 0.</summary>
                public static float BonusPerCp = 0.0125f, BonusFromCp = 8f, BonusCap = 0.15f;

                /// <summary>HOLD: splash (area) units get the power bonus too (false today: their bonus is held).</summary>
                public static bool SplashBonus;

                /// <summary>Drop time by baseCP: ≤ DropSmallMaxCp the small time, ≥ DropLargeMinCp the large one, else the middle.</summary>
                public static int DropSmallMaxCp = 4, DropLargeMinCp = 15;

                /// <summary>Seconds of the three drop times.</summary>
                public static float DropSmallSeconds = 2.5f, DropMiddleSeconds = 3.5f, DropLargeSeconds = 5f;
            }
        }

        // ------------------------------------------------------------------ balance pack pass 2 (lane B, rule B)
        public static partial class Weapons
        {
            /// <summary>The blast falloff of a plain splash (DamageSystem.ApplyFalloff; was DamageSystem.EdgeFalloff).</summary>
            public static partial class DamageRules
            {
                /// <summary>Damage at the rim of a one-layer blast, relative to the centre (support strikes, plain splash).</summary>
                public static float EdgeFalloff = 0.25f;
            }

            /// <summary>What an enemy jammer does (CombatSystem.Launch, StrikeSystem.Launch, BossSystem.BigAttacks swarm).</summary>
            public static partial class JamRules
            {
                /// <summary>A jammed (or lock-lost) guided round lands this far off its mark at least (m; was 5f).</summary>
                public static float GuidedMissMin = 5f;

                /// <summary>Plus up to this much more, rolled (m; was 6f).</summary>
                public static float GuidedMissSpread = 6f;

                /// <summary>Fire support called into an enemy jammer's bubble lands this many times as wide (x; was 2.2f).</summary>
                public static float StrikeScatter = 2.2f;

                /// <summary>The chance a boss's swarm drone over an enemy jammer loses its target (was 0.5).</summary>
                public static double SwarmJamChance = 0.5;
            }
        }

        public static partial class Vehicles
        {
            /// <summary>The Trophy APS module (GearSystem.Equip, prompt 29 B2-APS-trophy D7).</summary>
            public static partial class TrophyRules
            {
                /// <summary>RETROFIT_ELIGIBLE: the fitted APS's radius when the vehicle has none of its own (m).</summary>
                public static float Radius = 20f;

                /// <summary>RETROFIT_ELIGIBLE: its interceptors.</summary>
                public static int Charges = 2;

                /// <summary>RETROFIT_ELIGIBLE: seconds to get one interceptor back.</summary>
                public static float Recharge = 20f;

                /// <summary>BUILT_IN: interceptors added to its own APS.</summary>
                public static int BuiltInExtraCharges = 1;

                /// <summary>BUILT_IN: its own recharge times this.</summary>
                public static float BuiltInRechargeScale = 0.75f;
            }

            /// <summary>
            /// Play-test 14 (lane J): how long a wreck stays solid (WreckField): a ship until it has gone under (the view's
            /// ShipSinking takes it down by 18 s), a boss's hulk as long as the view keeps it, any other hulk 30 s plus up to
            /// the spread (fixed by its id; the view sinks it on the same clock).
            /// </summary>
            public static partial class WreckRules
            {
                /// <summary>A ground hulk's shortest life (s).</summary>
                public static double GroundSeconds = 30.0;

                /// <summary>Up to this much longer (s), by the vehicle's id.</summary>
                public static double GroundSpread = 15.0;

                /// <summary>A mobile boss's hulk (s).</summary>
                public static double BossSeconds = 90.0;

                /// <summary>A ship going down, until it is under the water (s).</summary>
                public static double ShipSeconds = 18.0;
            }
        }

        public static partial class Modes
        {
            /// <summary>Defend and its endless run: the wave curve's numbers by difficulty (ModeSessions DefendSession.Build).</summary>
            public static partial class DefendWaves
            {
                /// <summary>Vehicles in wave 1 (Easy / Normal / Hard and above).</summary>
                public static int StartEasy = 2, StartNormal = 3, StartHard = 4;

                /// <summary>The endless run's wave 1.</summary>
                public static int EndlessStartEasy = 4, EndlessStartNormal = 5, EndlessStartHard = 6;

                /// <summary>Vehicles added per wave (Normal and Easy / Hard and above / endless).</summary>
                public static float Growth = 1.8f, GrowthHard = 2.0f, EndlessGrowth = 1.2f;

                /// <summary>Endless: each wave this share bigger than the last.</summary>
                public static float EndlessCompound = 0.06f;

                /// <summary>The most vehicles in one wave.</summary>
                public static int WaveMax = 36;
            }

            /// <summary>The waves' size factor by the reference base (BaseStrength.WaveScale).</summary>
            public static partial class BaseStrengthRules
            {
                /// <summary>Wave scale = clamp((score / 100) ^ exponent, min, max).</summary>
                public static float WaveScaleExponent = 0.75f, WaveScaleMin = 0.75f, WaveScaleMax = 2.5f;
            }
        }

        private static readonly Entry[] RuleEntries =
        {
            new Entry("weapons.damageRules.edgeFalloff", "share", () => Weapons.DamageRules.EdgeFalloff, v => Weapons.DamageRules.EdgeFalloff = (float)v),
            new Entry("weapons.jamRules.guidedMissMin", "m", () => Weapons.JamRules.GuidedMissMin, v => Weapons.JamRules.GuidedMissMin = (float)v),
            new Entry("weapons.jamRules.guidedMissSpread", "m", () => Weapons.JamRules.GuidedMissSpread, v => Weapons.JamRules.GuidedMissSpread = (float)v),
            new Entry("weapons.jamRules.strikeScatter", "x", () => Weapons.JamRules.StrikeScatter, v => Weapons.JamRules.StrikeScatter = (float)v),
            new Entry("weapons.jamRules.swarmJamChance", "share", () => Weapons.JamRules.SwarmJamChance, v => Weapons.JamRules.SwarmJamChance = v),
            new Entry("vehicles.trophyRules.radius", "m", () => Vehicles.TrophyRules.Radius, v => Vehicles.TrophyRules.Radius = (float)v),
            new Entry("vehicles.trophyRules.charges", "count", () => Vehicles.TrophyRules.Charges, v => Vehicles.TrophyRules.Charges = (int)System.Math.Round(v)),
            new Entry("vehicles.trophyRules.recharge", "s", () => Vehicles.TrophyRules.Recharge, v => Vehicles.TrophyRules.Recharge = (float)v),
            new Entry("vehicles.trophyRules.builtInExtraCharges", "count", () => Vehicles.TrophyRules.BuiltInExtraCharges,
                v => Vehicles.TrophyRules.BuiltInExtraCharges = (int)System.Math.Round(v)),
            new Entry("vehicles.trophyRules.builtInRechargeScale", "x", () => Vehicles.TrophyRules.BuiltInRechargeScale, v => Vehicles.TrophyRules.BuiltInRechargeScale = (float)v),
            new Entry("modes.defendWaves.startEasy", "count", () => Modes.DefendWaves.StartEasy, v => Modes.DefendWaves.StartEasy = (int)System.Math.Round(v)),
            new Entry("modes.defendWaves.startNormal", "count", () => Modes.DefendWaves.StartNormal, v => Modes.DefendWaves.StartNormal = (int)System.Math.Round(v)),
            new Entry("modes.defendWaves.startHard", "count", () => Modes.DefendWaves.StartHard, v => Modes.DefendWaves.StartHard = (int)System.Math.Round(v)),
            new Entry("modes.defendWaves.endlessStartEasy", "count", () => Modes.DefendWaves.EndlessStartEasy, v => Modes.DefendWaves.EndlessStartEasy = (int)System.Math.Round(v)),
            new Entry("modes.defendWaves.endlessStartNormal", "count", () => Modes.DefendWaves.EndlessStartNormal, v => Modes.DefendWaves.EndlessStartNormal = (int)System.Math.Round(v)),
            new Entry("modes.defendWaves.endlessStartHard", "count", () => Modes.DefendWaves.EndlessStartHard, v => Modes.DefendWaves.EndlessStartHard = (int)System.Math.Round(v)),
            new Entry("modes.defendWaves.growth", "count/wave", () => Modes.DefendWaves.Growth, v => Modes.DefendWaves.Growth = (float)v),
            new Entry("modes.defendWaves.growthHard", "count/wave", () => Modes.DefendWaves.GrowthHard, v => Modes.DefendWaves.GrowthHard = (float)v),
            new Entry("modes.defendWaves.endlessGrowth", "count/wave", () => Modes.DefendWaves.EndlessGrowth, v => Modes.DefendWaves.EndlessGrowth = (float)v),
            new Entry("modes.defendWaves.endlessCompound", "share/wave", () => Modes.DefendWaves.EndlessCompound, v => Modes.DefendWaves.EndlessCompound = (float)v),
            new Entry("modes.defendWaves.waveMax", "count", () => Modes.DefendWaves.WaveMax, v => Modes.DefendWaves.WaveMax = (int)System.Math.Round(v)),
            new Entry("modes.baseStrengthRules.waveScaleExponent", "x", () => Modes.BaseStrengthRules.WaveScaleExponent, v => Modes.BaseStrengthRules.WaveScaleExponent = (float)v),
            new Entry("modes.baseStrengthRules.waveScaleMin", "x", () => Modes.BaseStrengthRules.WaveScaleMin, v => Modes.BaseStrengthRules.WaveScaleMin = (float)v),
            new Entry("modes.baseStrengthRules.waveScaleMax", "x", () => Modes.BaseStrengthRules.WaveScaleMax, v => Modes.BaseStrengthRules.WaveScaleMax = (float)v),
            new Entry("modes.economyRules.supplyPerArmyCap", "x", () => Modes.EconomyRules.SupplyPerArmyCap, v => Modes.EconomyRules.SupplyPerArmyCap = (float)v),
            new Entry("modes.economyRules.upkeepSlope", "share", () => Modes.EconomyRules.UpkeepSlope, v => Modes.EconomyRules.UpkeepSlope = (float)v),
            new Entry("modes.economyRules.upkeepFloor", "share", () => Modes.EconomyRules.UpkeepFloor, v => Modes.EconomyRules.UpkeepFloor = (float)v),
            new Entry("modes.economyRules.catchUpOddsFloor", "share", () => Modes.EconomyRules.CatchUpOddsFloor, v => Modes.EconomyRules.CatchUpOddsFloor = (float)v),
            new Entry("modes.economyRules.bountyMin", "x", () => Modes.EconomyRules.BountyMin, v => Modes.EconomyRules.BountyMin = (float)v),
            new Entry("modes.economyRules.bountyMax", "x", () => Modes.EconomyRules.BountyMax, v => Modes.EconomyRules.BountyMax = (float)v),
            new Entry("modes.economyRules.supplyPriceScale", "x", () => Modes.EconomyRules.SupplyPriceScale, v => Modes.EconomyRules.SupplyPriceScale = (float)v),
            new Entry("modes.economyRules.killCreditSeconds", "s", () => Modes.EconomyRules.KillCreditSeconds, v => Modes.EconomyRules.KillCreditSeconds = v),
            new Entry("modes.holdFlags.outpostForwardDropsQuickModes", "flag", () => Modes.HoldFlags.OutpostForwardDropsQuickModes ? 1 : 0,
                v => Modes.HoldFlags.OutpostForwardDropsQuickModes = v != 0, flag: true),
            new Entry("modes.holdFlags.laterEventsQuickModes", "flag", () => Modes.HoldFlags.LaterEventsQuickModes ? 1 : 0,
                v => Modes.HoldFlags.LaterEventsQuickModes = v != 0, flag: true),
            new Entry("modes.holdFlags.laterNeutrals", "flag", () => Modes.HoldFlags.LaterNeutrals ? 1 : 0, v => Modes.HoldFlags.LaterNeutrals = v != 0, flag: true),
            new Entry("bosses.bossHunt.weeklyMains", "count", () => Bosses.BossHunt.WeeklyMains, v => Bosses.BossHunt.WeeklyMains = (int)System.Math.Round(v)),
            new Entry("bosses.bossHunt.fullFrom", "x", () => Bosses.BossHunt.FullFrom, v => Bosses.BossHunt.FullFrom = (float)v),
            new Entry("bosses.bossHunt.fullTo", "x", () => Bosses.BossHunt.FullTo, v => Bosses.BossHunt.FullTo = (float)v),
            new Entry("bosses.bossHunt.weeklyStep", "x", () => Bosses.BossHunt.WeeklyStep, v => Bosses.BossHunt.WeeklyStep = (float)v),
            new Entry("bosses.bossRushRules.miniSeconds", "s", () => Bosses.BossRushRules.MiniSeconds, v => Bosses.BossRushRules.MiniSeconds = (float)v),
            new Entry("bosses.bossRushRules.mainSeconds", "s", () => Bosses.BossRushRules.MainSeconds, v => Bosses.BossRushRules.MainSeconds = (float)v),
            new Entry("bosses.bossRushRules.fullMiniSeconds", "s", () => Bosses.BossRushRules.FullMiniSeconds, v => Bosses.BossRushRules.FullMiniSeconds = (float)v),
            new Entry("bosses.bossRushRules.fullMainSeconds", "s", () => Bosses.BossRushRules.FullMainSeconds, v => Bosses.BossRushRules.FullMainSeconds = (float)v),
            new Entry("bosses.bossRushRules.hpShare", "share", () => Bosses.BossRushRules.HpShare, v => Bosses.BossRushRules.HpShare = (float)v),
            new Entry("weapons.countermeasures.flareCueSeconds", "s", () => Weapons.Countermeasures.FlareCueSeconds, v => Weapons.Countermeasures.FlareCueSeconds = (float)v),
            new Entry("weapons.countermeasures.flareGraceSeconds", "s", () => Weapons.Countermeasures.FlareGraceSeconds, v => Weapons.Countermeasures.FlareGraceSeconds = (float)v),
            new Entry("weapons.countermeasures.apsVolleySeconds", "s", () => Weapons.Countermeasures.ApsVolleySeconds, v => Weapons.Countermeasures.ApsVolleySeconds = (float)v),
            new Entry("weapons.countermeasures.apsRechargeScale", "x", () => Weapons.Countermeasures.ApsRechargeScale, v => Weapons.Countermeasures.ApsRechargeScale = (float)v),
            new Entry("modes.endlessRules.enemyPerBoss", "share/step", () => Modes.EndlessRules.EnemyPerBoss, v => Modes.EndlessRules.EnemyPerBoss = (float)v),
            new Entry("modes.endlessRules.coinDecay", "x", () => Modes.EndlessRules.CoinDecay, v => Modes.EndlessRules.CoinDecay = v),
            Entry.IntArray("vehicles.priceRules.groupMaxCp", "CP", () => Vehicles.PriceRules.GroupMaxCp, v => Vehicles.PriceRules.GroupMaxCp = v),
            Entry.FloatArray("vehicles.priceRules.groupFactor", "x", () => Vehicles.PriceRules.GroupFactor, v => Vehicles.PriceRules.GroupFactor = v),
            new Entry("vehicles.priceRules.bonusPerCp", "share/CP", () => Vehicles.PriceRules.BonusPerCp, v => Vehicles.PriceRules.BonusPerCp = (float)v),
            new Entry("vehicles.priceRules.bonusFromCp", "CP", () => Vehicles.PriceRules.BonusFromCp, v => Vehicles.PriceRules.BonusFromCp = (float)v),
            new Entry("vehicles.priceRules.bonusCap", "share", () => Vehicles.PriceRules.BonusCap, v => Vehicles.PriceRules.BonusCap = (float)v),
            new Entry("vehicles.priceRules.splashBonus", "flag", () => Vehicles.PriceRules.SplashBonus ? 1 : 0, v => Vehicles.PriceRules.SplashBonus = v != 0, flag: true),
            new Entry("vehicles.priceRules.dropSmallMaxCp", "CP", () => Vehicles.PriceRules.DropSmallMaxCp, v => Vehicles.PriceRules.DropSmallMaxCp = (int)System.Math.Round(v)),
            new Entry("vehicles.priceRules.dropLargeMinCp", "CP", () => Vehicles.PriceRules.DropLargeMinCp, v => Vehicles.PriceRules.DropLargeMinCp = (int)System.Math.Round(v)),
            new Entry("vehicles.priceRules.dropSmallSeconds", "s", () => Vehicles.PriceRules.DropSmallSeconds, v => Vehicles.PriceRules.DropSmallSeconds = (float)v),
            new Entry("vehicles.priceRules.dropMiddleSeconds", "s", () => Vehicles.PriceRules.DropMiddleSeconds, v => Vehicles.PriceRules.DropMiddleSeconds = (float)v),
            new Entry("vehicles.priceRules.dropLargeSeconds", "s", () => Vehicles.PriceRules.DropLargeSeconds, v => Vehicles.PriceRules.DropLargeSeconds = (float)v),
            new Entry("vehicles.wreckRules.groundSeconds", "s", () => Vehicles.WreckRules.GroundSeconds, v => Vehicles.WreckRules.GroundSeconds = v),
            new Entry("vehicles.wreckRules.groundSpread", "s", () => Vehicles.WreckRules.GroundSpread, v => Vehicles.WreckRules.GroundSpread = v),
            new Entry("vehicles.wreckRules.bossSeconds", "s", () => Vehicles.WreckRules.BossSeconds, v => Vehicles.WreckRules.BossSeconds = v),
            new Entry("vehicles.wreckRules.shipSeconds", "s", () => Vehicles.WreckRules.ShipSeconds, v => Vehicles.WreckRules.ShipSeconds = v),
        };
    }
}
