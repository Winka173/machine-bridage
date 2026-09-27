using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>Equipment rarity, white to gold (as in most mobile games: Archero, Survivor.io, Hero Wars).</summary>
    public enum Rarity
    {
        Common,
        Uncommon,
        Rare,
        Epic,
        Legendary,
    }

    /// <summary>The six equipment slots of a loadout, and the seventh, special one.</summary>
    public enum GearSlot
    {
        /// <summary>Main gun upgrade: more damage.</summary>
        Weapon,

        /// <summary>Autoloader: a higher rate of fire.</summary>
        Loader,

        /// <summary>Armour kit: more health.</summary>
        Armor,

        /// <summary>Composite plating: less damage taken.</summary>
        Plating,

        /// <summary>Engine: more speed.</summary>
        Engine,

        /// <summary>Field repair kit: repairs itself out of combat.</summary>
        Repair,

        /// <summary>A special module with its own ability (epic and legendary only).</summary>
        Special,
    }

    /// <summary>Loadouts are per branch of the army, so changing the deck never undoes them.</summary>
    public enum GearBranch
    {
        Armor,
        Light,
        Artillery,
        Air,
    }

    public enum CrateKind
    {
        Battle,
        Silver,
        Gold,
        Legendary,
    }

    /// <summary>One piece of equipment the player owns (saved in the profile).</summary>
    [Serializable]
    public sealed class GearItem
    {
        public int id;
        public int slot;
        public int rarity;
        public int level = 1;
        public int special;

        public GearSlot Slot => (GearSlot)slot;
        public Rarity Rarity => (Rarity)rarity;
        public SpecialModule Module => (SpecialModule)special;
    }

    /// <summary>
    /// Card ranks 1 to 10 (after Brawl Stars' power levels: linear gains, costs that climb): each
    /// rank adds 5 % health and damage to a vehicle card, 5 % damage to a strike card, and costs
    /// coins and the card's blueprints. Blueprints come from crates.
    /// </summary>
    public static class CardRanks
    {
        public const int Max = 10;

        private static readonly int[] Coins = { 0, 50, 100, 200, 400, 700, 1200, 2000, 3200, 5000 };
        private static readonly int[] Prints = { 0, 2, 4, 8, 12, 20, 30, 45, 65, 90 };

        /// <summary>Coins to go from <paramref name="rank"/> to the next (0 at the top).</summary>
        public static int CoinsToNext(int rank) => rank >= 1 && rank < Max ? Coins[rank] : 0;

        public static int BlueprintsToNext(int rank) => rank >= 1 && rank < Max ? Prints[rank] : 0;

        /// <summary>The extra health and damage a card of this rank brings (0.05 a rank above the first).</summary>
        public static float Bonus(int rank) => 0.05f * (Mathf.Clamp(rank, 1, Max) - 1);
    }

    /// <summary>
    /// Equipment: what each rarity and level gives, the caps on every stat, merging three
    /// identical pieces into the next rarity, and what a loadout does to a vehicle.
    /// </summary>
    public static class Gear
    {
        public const int Slots = 7;

        /// <summary>Highest level of each rarity.</summary>
        public static readonly int[] LevelCap = { 5, 10, 15, 20, 25 };

        // The main stat at a rarity's top level, by slot (Weapon, Loader, Armor, Plating, Engine, Repair).
        private static readonly float[][] Top =
        {
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.02f, 0.035f, 0.055f, 0.075f, 0.095f },
            new[] { 0.02f, 0.035f, 0.05f, 0.065f, 0.08f },
            new[] { 0.002f, 0.004f, 0.006f, 0.008f, 0.01f },
        };

        /// <summary>Caps on what a whole loadout can add, by slot: no loadout turns a vehicle into another.</summary>
        public static readonly float[] Cap = { 0.25f, 0.15f, 0.25f, 0.2f, 0.15f, 0.02f };

        /// <summary>A special module's strength at epic and legendary rarity.</summary>
        public static float ModulePower(SpecialModule module, Rarity rarity)
        {
            var legendary = rarity >= Rarity.Legendary;
            return module switch
            {
                SpecialModule.ReactiveArmor => legendary ? 0.18f : 0.12f,
                SpecialModule.AutoRepair => legendary ? 0.018f : 0.012f,
                SpecialModule.VeteranCrew => legendary ? 0.12f : 0.08f,
                SpecialModule.SmokeDischarger => legendary ? 10f : 8f,
                _ => 0f,
            };
        }

        /// <summary>A piece's main stat: from 40 % of its rarity's top at level 1 to all of it at the cap.</summary>
        public static float Value(GearItem item)
        {
            if (item.Slot == GearSlot.Special) return ModulePower(item.Module, item.Rarity);
            var cap = LevelCap[item.rarity];
            var level = Mathf.Clamp(item.level, 1, cap);
            return Top[item.slot][item.rarity] * (0.4f + 0.6f * (level - 1) / Mathf.Max(1, cap - 1));
        }

        /// <summary>Coins for the next level (30 a level, so a legendary costs 9,000 to max).</summary>
        public static int LevelCost(GearItem item) => item.level >= LevelCap[item.rarity] ? 0 : 30 * item.level;

        /// <summary>Coins spent levelling a piece so far (refunded when it is merged away).</summary>
        public static int Spent(GearItem item)
        {
            var total = 0;
            for (var l = 1; l < item.level; l++) total += 30 * l;
            return total;
        }

        /// <summary>Three pieces merge when they are the same slot, rarity and (for modules) module, below legendary.</summary>
        public static bool CanMerge(GearItem a, GearItem b) =>
            a.slot == b.slot && a.rarity == b.rarity && a.special == b.special && a.rarity < (int)Rarity.Legendary;

        public static GearBranch BranchOf(VehicleDef def) =>
            def.Flying ? GearBranch.Air
            : def.Weapon.MinRange > 0f ? GearBranch.Artillery
            : def.Class is UnitClass.Tank or UnitClass.Heavy or UnitClass.TankHunter ? GearBranch.Armor
            : GearBranch.Light;

        /// <summary>What a card's rank and its branch's loadout do to a vehicle.</summary>
        public static VehicleBoost Boost(int rank, IEnumerable<GearItem> loadout)
        {
            var sum = new float[6];
            var module = SpecialModule.None;
            var power = 0f;
            foreach (var item in loadout)
            {
                if (item == null) continue;
                if (item.Slot == GearSlot.Special)
                {
                    module = item.Module;
                    power = Value(item);
                    continue;
                }
                sum[item.slot] += Value(item);
            }
            for (var i = 0; i < sum.Length; i++) sum[i] = Mathf.Min(sum[i], Cap[i]);
            var rankBonus = CardRanks.Bonus(rank);
            return new VehicleBoost(
                hp: (1f + rankBonus) * (1f + sum[(int)GearSlot.Armor]),
                damage: (1f + rankBonus) * (1f + sum[(int)GearSlot.Weapon]),
                fireRate: 1f + sum[(int)GearSlot.Loader],
                speed: 1f + sum[(int)GearSlot.Engine],
                damageTaken: 1f - sum[(int)GearSlot.Plating],
                regen: sum[(int)GearSlot.Repair],
                special: module,
                specialPower: power);
        }
    }

    /// <summary>
    /// Campaign enemies keep pace with the player's arsenal: they get most (not all) of the edge
    /// the card ranks and equipment give the player's deck on average, so upgrades still tell but
    /// the missions do not turn into walkovers. Toughness (health over the share of damage taken)
    /// goes on health, firepower (damage times rate of fire) on damage.
    /// </summary>
    public static class EnemyScaling
    {
        /// <summary>How much of the player's edge the enemy matches.</summary>
        public const float Share = 0.8f;

        public static VehicleBoost Match(IEnumerable<VehicleBoost> deck)
        {
            var tough = 0f;
            var fire = 0f;
            var n = 0;
            foreach (var b in deck)
            {
                tough += b.Hp / Mathf.Max(0.1f, b.DamageTaken);
                fire += b.Damage * b.FireRate;
                n++;
            }
            if (n == 0) return VehicleBoost.None;
            var hp = 1f + Mathf.Max(0f, tough / n - 1f) * Share;
            var damage = 1f + Mathf.Max(0f, fire / n - 1f) * Share;
            return new VehicleBoost(hp, damage, 1f, 1f, 1f, 0f, SpecialModule.None, 0f);
        }
    }

    /// <summary>
    /// Crates: what each holds and the odds of every rarity, with pity (a guaranteed epic or
    /// legendary after a run without one), after Clash Royale, Archero and Hearthstone. The
    /// odds are shown in the game before a crate is bought or opened (Apple 3.1.1, Google Play,
    /// Korea's 2024 disclosure law).
    /// </summary>
    public static class Crates
    {
        /// <summary>What came out of a crate.</summary>
        public sealed class Loot
        {
            public int Coins;
            public int Universal;
            public readonly List<(string card, int count)> Blueprints = new();
            public readonly List<GearItem> Gear = new();
        }

        /// <summary>The odds of each rarity on one equipment roll, per crate.</summary>
        public static readonly float[][] Odds =
        {
            new[] { 0.70f, 0.25f, 0.045f, 0.005f, 0f },
            new[] { 0.50f, 0.35f, 0.12f, 0.028f, 0.002f },
            new[] { 0.20f, 0.42f, 0.28f, 0.085f, 0.015f },
            new[] { 0f, 0.25f, 0.45f, 0.24f, 0.06f },
        };

        public static readonly int[] Rolls = { 1, 2, 4, 6 };
        public static readonly int[] CoinsLow = { 60, 250, 800, 2000 };
        public static readonly int[] CoinsHigh = { 120, 350, 1000, 2500 };
        public static readonly int[] PrintCount = { 6, 15, 45, 120 };
        public static readonly int[] PrintCards = { 1, 2, 3, 4 };

        /// <summary>The gold crate's first roll is at least rare, the legendary crate's at least epic, with these odds.</summary>
        public static readonly float[] GoldGuaranteed = { 0f, 0f, 0.81f, 0.16f, 0.03f };
        public static readonly float[] LegendaryGuaranteed = { 0f, 0f, 0f, 0.8f, 0.2f };

        /// <summary>Pity: an epic or better within this many gold crates, a legendary within this many (per crate kind; 0: none).</summary>
        public static readonly int[] EpicPity = { 0, 0, 5, 0 };
        public static readonly int[] LegendaryPity = { 0, 0, 25, 4 };

        /// <summary>Prices in coins, the one currency (0: not for sale; battle crates are won).</summary>
        public static readonly int[] CoinPrice = { 0, 900, 3000, 8000 };

        /// <summary>
        /// Opens a crate: coins, blueprints for cards the player has, and equipment rolls. The pity
        /// counters (crates opened since the last epic, the last legendary) are advanced and reset.
        /// </summary>
        public static Loot Open(CrateKind kind, System.Random rng, IReadOnlyList<string> cards, ref int sinceEpic, ref int sinceLegendary, Func<int> nextId)
        {
            var k = (int)kind;
            var loot = new Loot { Coins = rng.Next(CoinsLow[k], CoinsHigh[k] + 1) };
            if (cards.Count > 0)
            {
                var picks = Math.Min(PrintCards[k], cards.Count);
                var left = PrintCount[k];
                var chosen = new List<string>();
                while (chosen.Count < picks)
                {
                    var card = cards[rng.Next(cards.Count)];
                    if (!chosen.Contains(card)) chosen.Add(card);
                }
                for (var i = 0; i < chosen.Count; i++)
                {
                    var share = i == chosen.Count - 1 ? left : Math.Max(1, (int)(PrintCount[k] * (0.5f / picks + 0.5f * (float)rng.NextDouble() / picks)));
                    share = Math.Min(share, left - (chosen.Count - 1 - i));
                    left -= share;
                    loot.Blueprints.Add((chosen[i], share));
                }
            }
            if (kind == CrateKind.Gold && rng.NextDouble() < 0.1) loot.Universal = 5;
            if (kind == CrateKind.Legendary) loot.Universal = 10;

            var bestEpic = false;
            var bestLegendary = false;
            for (var roll = 0; roll < Rolls[k]; roll++)
            {
                var table = roll == 0 && kind == CrateKind.Gold ? GoldGuaranteed
                    : roll == 0 && kind == CrateKind.Legendary ? LegendaryGuaranteed
                    : Odds[k];
                var rarity = Pick(table, rng);
                // Pity on the last roll: the run without one is over.
                if (roll == Rolls[k] - 1)
                {
                    if (LegendaryPity[k] > 0 && !bestLegendary && rarity < Rarity.Legendary && sinceLegendary + 1 >= LegendaryPity[k]) rarity = Rarity.Legendary;
                    else if (EpicPity[k] > 0 && !bestEpic && rarity < Rarity.Epic && sinceEpic + 1 >= EpicPity[k]) rarity = Rarity.Epic;
                }
                if (rarity >= Rarity.Epic) bestEpic = true;
                if (rarity >= Rarity.Legendary) bestLegendary = true;
                loot.Gear.Add(Roll(rarity, rng, nextId()));
            }
            sinceEpic = bestEpic ? 0 : sinceEpic + 1;
            sinceLegendary = bestLegendary ? 0 : sinceLegendary + 1;
            return loot;
        }

        /// <summary>A new piece of this rarity in a random slot (the special slot only for epic and up).</summary>
        public static GearItem Roll(Rarity rarity, System.Random rng, int id)
        {
            var slots = rarity >= Rarity.Epic ? Gear.Slots : Gear.Slots - 1;
            var slot = rng.Next(slots);
            var item = new GearItem { id = id, slot = slot, rarity = (int)rarity, level = 1 };
            if ((GearSlot)slot == GearSlot.Special) item.special = 1 + rng.Next(4);
            return item;
        }

        private static Rarity Pick(float[] table, System.Random rng)
        {
            var x = (float)rng.NextDouble();
            for (var i = 0; i < table.Length; i++)
            {
                x -= table[i];
                if (x < 0f) return (Rarity)i;
            }
            for (var i = table.Length - 1; i >= 0; i--)
                if (table[i] > 0f) return (Rarity)i;
            return Rarity.Common;
        }

        /// <summary>The chance of at least one piece of <paramref name="rarity"/> or better from one crate (for the odds screen).</summary>
        public static float AtLeastOne(CrateKind kind, Rarity rarity)
        {
            var k = (int)kind;
            var none = 1f;
            for (var roll = 0; roll < Rolls[k]; roll++)
            {
                var table = roll == 0 && kind == CrateKind.Gold ? GoldGuaranteed
                    : roll == 0 && kind == CrateKind.Legendary ? LegendaryGuaranteed
                    : Odds[k];
                var p = 0f;
                for (var r = (int)rarity; r < table.Length; r++) p += table[r];
                none *= 1f - p;
            }
            return 1f - none;
        }
    }

    /// <summary>
    /// Daily sources: a battle crate for each of the first five wins of the day, and three crates
    /// a day for watching an ad (the first a silver one), ten minutes apart.
    /// </summary>
    public static class DailyCrates
    {
        public const int WinCrates = 5;
        public const int AdCrates = 3;
        public static readonly TimeSpan AdCooldown = TimeSpan.FromMinutes(10);

        /// <summary>Which crate the next ad pays (the first of the day a silver one).</summary>
        public static CrateKind AdCrate(int watchedToday) => watchedToday == 0 ? CrateKind.Silver : CrateKind.Battle;
    }

    /// <summary>
    /// Buying coins with real money: the game has one currency, so the store sells coins (larger
    /// packs give more per dollar). Until a store (Google Play Billing, the App Store) is wired
    /// in, test builds grant the coins at once (marked TEST in the shop) and release builds say
    /// the store is coming. See Docs/RELEASE_CHECKLIST.md.
    /// </summary>
    public static class CoinStore
    {
        /// <summary>Test builds: a purchase grants its coins without a payment.</summary>
        public static bool TestPurchases = true;

        public static readonly (string id, int coins, string price)[] Packs =
        {
            ("coins_1200", 1200, "$0.99"), ("coins_7000", 7000, "$4.99"), ("coins_15000", 15000, "$9.99"),
            ("coins_32000", 32000, "$19.99"), ("coins_85000", 85000, "$49.99"), ("coins_180000", 180000, "$99.99"),
        };

        /// <summary>Buys a coin pack; <paramref name="done"/> gets whether coins were granted.</summary>
        public static void Buy(string packId, Action<bool> done)
        {
            foreach (var (id, coins, _) in Packs)
            {
                if (id != packId) continue;
                if (!TestPurchases)
                {
                    done?.Invoke(false);
                    return;
                }
                PlayerProfile.AddCoins(coins);
                done?.Invoke(true);
                return;
            }
            done?.Invoke(false);
        }
    }
}
