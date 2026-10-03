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
            public static class EconomyRules
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
            public static class HoldFlags
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
            public static class BossRushRules
            {
                public static float MiniSeconds = 66f, MainSeconds = 168f;

                /// <summary>The full hunt's targets.</summary>
                public static float FullMiniSeconds = 60f, FullMainSeconds = 150f;

                /// <summary>The share of power x time the boss's health is (the army does not hit all the time).</summary>
                public static float HpShare = 0.6f;
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
            public static class PriceRules
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

        private static readonly Entry[] RuleEntries =
        {
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
        };
    }
}
