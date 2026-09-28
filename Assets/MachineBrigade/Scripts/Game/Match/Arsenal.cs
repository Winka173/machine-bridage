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

    /// <summary>
    /// The six equipment slots of a vehicle loadout and the seventh, special one; then the three
    /// slots of a tower type (<see cref="TowerWeapon"/>, <see cref="TowerStructure"/>,
    /// <see cref="TowerSystems"/>), which only tower pieces go into (see Gear.Tower.cs).
    /// </summary>
    public enum GearSlot
    {
        /// <summary>Main gun upgrade: more damage.</summary>
        Weapon,

        /// <summary>Autoloader: a higher rate of fire.</summary>
        Loader,

        /// <summary>Armour kit: more health (plating base types: less damage taken instead).</summary>
        Armor,

        /// <summary>Optics: more vision; sights, camouflage, marking and electronic warfare.</summary>
        Optics,

        /// <summary>Engine: more speed.</summary>
        Engine,

        /// <summary>Field repair kit: repairs itself out of combat.</summary>
        Repair,

        /// <summary>A special module with its own ability (epic and legendary only).</summary>
        Special,

        /// <summary>A tower's gun: more damage (one base type: rate of fire).</summary>
        TowerWeapon,

        /// <summary>A tower's walls: more health (screens: less damage taken; an engineer bay: repairs).</summary>
        TowerStructure,

        /// <summary>A tower's sensors and drives: vision, turret traverse, magazine handling.</summary>
        TowerSystems,
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

    /// <summary>A sub-stat on a piece: which stat, and where its roll landed (0.6 to 1 of the rarity's top).</summary>
    [Serializable]
    public sealed class GearSub
    {
        public int stat;
        public float roll = 1f;

        public StatId Stat => (StatId)stat;
    }

    /// <summary>One piece of equipment the player owns (saved in the profile). See <see cref="Gear"/> for what it gives.</summary>
    [Serializable]
    public sealed class GearItem
    {
        public int id;
        public int slot;
        public int rarity;
        public int level = 1;

        /// <summary>The special module (<see cref="SpecialModule"/>) of a Special piece.</summary>
        public int special;

        /// <summary>Base type id (a stat piece: "long_barrel") or module key (a Special piece: "trophy_aps"); also its picture's name.</summary>
        public string baseType = "";

        /// <summary>Set brand, 1 to 10 (0: none; Special pieces have none).</summary>
        public int brand;

        /// <summary>Sub-stats (0/1/2/2/2 by rarity).</summary>
        public List<GearSub> subs = new();

        /// <summary>The trait key on an Epic or Legendary piece ("ricochet_shells"), or empty.</summary>
        public string trait = "";

        /// <summary>The three traits rolled when it reached Epic (a menu can offer the choice).</summary>
        public List<string> traitOptions = new();

        /// <summary>Seeds its later rolls (a merge's new sub-stat and trait).</summary>
        public int seed;

        public GearSlot Slot => (GearSlot)slot;
        public Rarity Rarity => (Rarity)rarity;
        public SpecialModule Module => special > 0 ? (SpecialModule)special : GearKeys.ParseModule(baseType);
        public TraitId Trait => GearKeys.ParseTrait(trait);
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

        /// <summary>Coins spent to bring a card from rank 1 to <paramref name="rank"/>.</summary>
        public static int CoinsSpent(int rank)
        {
            var total = 0;
            for (var r = 1; r < Mathf.Clamp(rank, 1, Max); r++) total += Coins[r];
            return total;
        }

        /// <summary>Blueprints spent to bring a card from rank 1 to <paramref name="rank"/>.</summary>
        public static int BlueprintsSpent(int rank)
        {
            var total = 0;
            for (var r = 1; r < Mathf.Clamp(rank, 1, Max); r++) total += Prints[r];
            return total;
        }

        /// <summary>The extra health and damage a card of this rank brings (0.05 a rank above the first).</summary>
        public static float Bonus(int rank) => 0.05f * (Mathf.Clamp(rank, 1, Max) - 1);

        /// <summary>Share off a card's call cost at this rank, in basis points: 5 % from rank 7, 10 % from rank 9.</summary>
        public static int CutBasisPoints(int rank) => rank >= 9 ? 1000 : rank >= 7 ? 500 : 0;

        /// <summary>
        /// A card's call cost at this rank, in whole CP (after Arknights' Potential: small steps with a
        /// cap, and a floor): cards of 5 CP or less never change, exact halves go to the player.
        /// </summary>
        public static int CallCost(int cost, int rank)
        {
            var bp = CutBasisPoints(rank);
            if (cost <= 5 || bp == 0) return cost;
            return cost - (cost * bp + 5000) / 10000;
        }
    }

    /// <summary>
    /// Equipment: what each rarity and level gives, the caps on every stat, merging three pieces
    /// of a slot into the next rarity, and what a loadout does to a vehicle (the affix model is in
    /// Gear.Model.cs, the catalogue in GearCatalog.cs).
    /// </summary>
    public static partial class Gear
    {
        public const int Slots = 7;

        /// <summary>Highest level of each rarity.</summary>
        public static readonly int[] LevelCap = { 5, 10, 15, 20, 25 };

        // The main stat at a rarity's top level, by slot (Weapon, Loader, Armor, Optics, Engine, Repair).
        private static readonly float[][] Top =
        {
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f },
            new[] { 0.02f, 0.035f, 0.05f, 0.065f, 0.08f },
            new[] { 0.002f, 0.004f, 0.006f, 0.008f, 0.01f },
        };

        /// <summary>
        /// Caps on what a whole loadout can add to each slot's main stat (damage, fire rate, health,
        /// vision, speed, regeneration): no loadout turns a vehicle into another. Sub-stats and set
        /// bonuses count towards them; every other stat has its own cap in <see cref="GearCatalog.StatCap"/>.
        /// </summary>
        public static readonly float[] Cap = { 0.25f, 0.15f, 0.25f, 0.25f, 0.15f, 0.02f };

        /// <summary>The cap on less damage taken (plating base types, the Aegis brand).</summary>
        public static float TakenCap => GearCatalog.StatCap[(int)StatId.DamageTaken];

        /// <summary>A special module's strength at epic and legendary rarity.</summary>
        public static float ModulePower(SpecialModule module, Rarity rarity)
        {
            var def = GearCatalog.Module(module);
            return def == null ? 0f : rarity >= Rarity.Legendary ? def.Legendary : def.Epic;
        }

        /// <summary>A piece's main stat: from 40 % of its rarity's top at level 1 to all of it at the cap.</summary>
        public static float Value(GearItem item)
        {
            if (item.Slot == GearSlot.Special) return ModulePower(item.Module, item.Rarity);
            var b = BaseOf(item);
            if (IsTower(item.Slot)) return TowerTop(MainStat(item), item.rarity) * (b?.MainScale ?? 1f) * LevelShare(item);
            var top = b != null && b.Plating ? PlatingTop[item.rarity] : Top[item.slot][item.rarity];
            return top * (b?.MainScale ?? 1f) * LevelShare(item);
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

        /// <summary>Three pieces merge when they are the same slot and rarity, below legendary (the kept one keeps its base type, sub-stats and trait).</summary>
        public static bool CanMerge(GearItem a, GearItem b) =>
            a.slot == b.slot && a.rarity == b.rarity && a.rarity < (int)Rarity.Legendary;

        /// <summary>
        /// The branch whose loadout a vehicle wears: data (balance.json "branches", see
        /// <see cref="VehicleDef.Branch"/>): aircraft Air, guns that lob over cover Artillery, the rest by class.
        /// </summary>
        public static GearBranch BranchOf(VehicleDef def) => (GearBranch)(int)def.Branch;

        /// <summary>
        /// What a card's rank and its branch's loadout do to a vehicle: every piece's main stat,
        /// implicit line and sub-stats, and the two-piece set bonuses, summed and capped per stat
        /// (trade-off drawbacks after the cap); the traits, the four-piece set behaviours and the
        /// special module ride along for the battle.
        /// </summary>
        public static VehicleBoost Boost(int rank, IEnumerable<GearItem> loadout) => Boost(rank, loadout, GearCatalog.StatCap);

        /// <summary>
        /// A loadout's boost with these caps per stat (a vehicle's <see cref="GearCatalog.StatCap"/>,
        /// a tower type's <see cref="GearCatalog.TowerStatCap"/>).
        /// </summary>
        public static VehicleBoost Boost(int rank, IEnumerable<GearItem> loadout, float[] caps) => Boost(rank, loadout, caps, null);

        /// <summary>
        /// A loadout's boost; <paramref name="brandCounts"/> overrides the brand pieces counted for the
        /// set bonuses (a tower type's Bulwark pieces count across the whole base), null counts the loadout's own.
        /// </summary>
        public static VehicleBoost Boost(int rank, IEnumerable<GearItem> loadout, float[] caps, int[] brandCounts)
        {
            var count = (int)StatId.Count;
            var sum = new float[count];
            var penalty = new float[count];
            var traits = new List<GearTrait>();
            var module = SpecialModule.None;
            var power = 0f;
            var power2 = 0f;
            var worn = new List<GearItem>();
            foreach (var item in loadout)
            {
                if (item == null) continue;
                worn.Add(item);
                if (item.Slot == GearSlot.Special)
                {
                    module = item.Module;
                    power = Value(item);
                    power2 = ModulePower2(module, item.Rarity);
                    continue;
                }
                sum[(int)MainStat(item)] += Value(item);
                var b = BaseOf(item);
                if (b != null)
                {
                    if (b.Implicit != StatId.Count) sum[(int)b.Implicit] += ImplicitValue(item);
                    if (b.Implicit2 != StatId.Count) sum[(int)b.Implicit2] += Implicit2Value(item);
                    if (b.TradeOff) penalty[(int)b.Penalty] += PenaltyValue(item);
                    if (b.Extra != TraitId.None && item.rarity >= b.ExtraFrom) traits.Add(new GearTrait(b.Extra, 1f));
                }
                if (item.subs != null)
                    foreach (var sub in item.subs)
                    {
                        var v = SubValue(item, sub);
                        sum[sub.stat] += v;
                        // The turret sub-stat turns the hull faster as well.
                        if (sub.stat == (int)StatId.TurretRate) sum[(int)StatId.TurnRate] += v;
                    }
                var trait = TraitOf(item);
                if (trait.Id != TraitId.None) traits.Add(trait);
            }
            var brands = brandCounts ?? BrandCounts(worn);
            for (var i = 1; i < brands.Length; i++)
            {
                var brand = GearCatalog.Brand(i);
                if (brand == null) continue;
                if (brands[i] >= 2)
                {
                    if (brand.Stat != StatId.Count) sum[(int)brand.Stat] += brand.Value;
                    if (brand.TwoPiece.Id != TraitId.None) traits.Add(brand.TwoPiece);
                }
                if (brands[i] >= 4) traits.Add(brand.FourPiece);
            }
            var stats = new float[count];
            var any = false;
            for (var i = 0; i < count; i++)
            {
                stats[i] = Mathf.Min(sum[i], caps[i]) + penalty[i];
                any |= stats[i] != 0f;
            }
            var rankBonus = CardRanks.Bonus(rank);
            return new VehicleBoost(
                hp: (1f + rankBonus) * (1f + stats[(int)StatId.Health]),
                damage: (1f + rankBonus) * (1f + stats[(int)StatId.Damage]),
                fireRate: 1f + stats[(int)StatId.FireRate],
                speed: 1f + stats[(int)StatId.Speed],
                damageTaken: 1f - stats[(int)StatId.DamageTaken],
                regen: Mathf.Max(0f, stats[(int)StatId.Regen]),
                special: module,
                specialPower: power,
                stats: any ? stats : null,
                traits: traits.Count > 0 ? traits.ToArray() : null,
                specialPower2: power2);
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
        /// <summary>How much of the player's edge the enemy matches by default (the data's economy.enemyScaling wins).</summary>
        public const float Share = 0.55f;

        public static VehicleBoost Match(IEnumerable<VehicleBoost> deck) => Match(deck, Share);

        /// <summary>
        /// A deck's power as one number: 100 for rank 1 cards with no equipment, then the average
        /// over its vehicles of the square root of toughness times firepower (a rank 5 card, +20 %
        /// health and damage, is 120).
        /// </summary>
        public static int Power(IEnumerable<VehicleBoost> deck)
        {
            var sum = 0f;
            var n = 0;
            foreach (var b in deck)
            {
                sum += Mathf.Sqrt(b.Hp / Mathf.Max(0.1f, b.DamageTaken) * b.Damage * b.FireRate);
                n++;
            }
            return n == 0 ? 100 : Mathf.RoundToInt(100f * sum / n);
        }

        /// <summary>
        /// The elite budget's edge taken out of a matched boost (prompt 8 H): elites make the enemy
        /// <paramref name="eliteEdge"/> stronger per CP, so the boost that keeps pace with the
        /// arsenal is that much smaller (split evenly between health and damage, never below none).
        /// </summary>
        public static VehicleBoost WithElites(VehicleBoost matched, float eliteEdge)
        {
            if (eliteEdge <= 0f) return matched;
            var f = Mathf.Sqrt(1f + eliteEdge);
            return new VehicleBoost(Mathf.Max(1f, matched.Hp / f), Mathf.Max(1f, matched.Damage / f), 1f, 1f, 1f, 0f, SpecialModule.None, 0f);
        }

        public static VehicleBoost Match(IEnumerable<VehicleBoost> deck, float share)
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
            var hp = 1f + Mathf.Max(0f, tough / n - 1f) * share;
            var damage = 1f + Mathf.Max(0f, fire / n - 1f) * share;
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
        /// The share of equipment rolls that are tower equipment, per crate (the rest are vehicle
        /// equipment). The rarity is rolled first, at the same odds for both, so the pity counters
        /// and the rarity table are the same whichever kind comes out.
        /// </summary>
        public static readonly float[] TowerShare = { 0.2f, 0.2f, 0.2f, 0.2f };

        /// <summary>
        /// Opens a crate: coins, blueprints for cards the player has, and equipment rolls. The pity
        /// counters (crates opened since the last epic, the last legendary) are advanced and reset.
        /// </summary>
        public static Loot Open(CrateKind kind, System.Random rng, IReadOnlyList<string> cards, ref int sinceEpic, ref int sinceLegendary, Func<int> nextId,
            BranchMask deck = BranchMask.All, IReadOnlyList<TowerNeed> towers = null)
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
                var rarity = Pick(TableFor(kind, roll), rng);
                // Pity on the last roll: the run without one is over.
                if (roll == Rolls[k] - 1)
                {
                    if (LegendaryPity[k] > 0 && !bestLegendary && rarity < Rarity.Legendary && sinceLegendary + 1 >= LegendaryPity[k]) rarity = Rarity.Legendary;
                    else if (EpicPity[k] > 0 && !bestEpic && rarity < Rarity.Epic && sinceEpic + 1 >= EpicPity[k]) rarity = Rarity.Epic;
                }
                if (rarity >= Rarity.Epic) bestEpic = true;
                if (rarity >= Rarity.Legendary) bestLegendary = true;
                // Then whether it is a tower piece (favouring the towers of the player's base) or a vehicle one.
                var tower = rng.NextDouble() < TowerShare[k];
                loot.Gear.Add(tower ? Gear.CreateTower(rarity, rng, nextId(), towers) : Roll(rarity, rng, nextId(), deck));
            }
            sinceEpic = bestEpic ? 0 : sinceEpic + 1;
            sinceLegendary = bestLegendary ? 0 : sinceLegendary + 1;
            return loot;
        }

        /// <summary>
        /// A new piece of this rarity in a random slot (the special slot only for epic and up): a base
        /// type favouring the deck's branches, a brand, its sub-stats and, from epic, a trait.
        /// </summary>
        public static GearItem Roll(Rarity rarity, System.Random rng, int id, BranchMask deck = BranchMask.All) => Gear.Create(rarity, rng, id, deck);

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
                var table = TableFor(kind, roll);
                var p = 0f;
                for (var r = (int)rarity; r < table.Length; r++) p += table[r];
                none *= 1f - p;
            }
            return 1f - none;
        }

        /// <summary>The rarity table of one roll of a crate (the gold and legendary crates' first roll is their guaranteed one).</summary>
        public static float[] TableFor(CrateKind kind, int roll) =>
            roll == 0 && kind == CrateKind.Gold ? GoldGuaranteed
            : roll == 0 && kind == CrateKind.Legendary ? LegendaryGuaranteed
            : Odds[(int)kind];

        /// <summary>
        /// The chance that one roll of a crate is a piece of this rarity and kind (tower or vehicle
        /// equipment): the rarity's odds times the kind's share. Over every rarity and both kinds a
        /// roll's odds add up to 1.
        /// </summary>
        public static float PieceOdds(CrateKind kind, int roll, Rarity rarity, bool tower)
        {
            var share = TowerShare[(int)kind];
            return TableFor(kind, roll)[(int)rarity] * (tower ? share : 1f - share);
        }

        /// <summary>The chance of at least one tower piece from one crate (for the odds screen).</summary>
        public static float AtLeastOneTower(CrateKind kind)
        {
            var k = (int)kind;
            return 1f - Mathf.Pow(1f - TowerShare[k], Rolls[k]);
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
