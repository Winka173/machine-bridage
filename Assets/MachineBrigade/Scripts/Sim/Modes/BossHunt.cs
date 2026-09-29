#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>Prompt 20 N: a boss in the story's order (the chapters switched on): its id, its rank and its chapter.</summary>
    public readonly struct HuntBoss
    {
        public HuntBoss(string id, bool main, int chapter)
        {
            Id = id;
            Main = main;
            Chapter = chapter;
        }

        public string Id { get; }
        public bool Main { get; }
        public int Chapter { get; }
    }

    /// <summary>Prompt 20 N: where a Boss Hunt keeps a checkpoint.</summary>
    public enum HuntCheckpoints
    {
        None,

        /// <summary>The week's hunt: after each main boss.</summary>
        MainBosses,

        /// <summary>The full hunt: after every boss.</summary>
        EveryBoss,
    }

    /// <summary>
    /// Prompt 20 N (DECISIONS 19N): which bosses a Boss Hunt brings and in what order. The week's hunt: 3 main
    /// bosses and 7 mini bosses from the chapters switched on, drawn by the week's number (the same draw on every
    /// device), a few minis before each main (2, 2, 3), each group in story order, stronger down the run. The full
    /// hunt: every boss of the chapters switched on, in story order.
    /// </summary>
    public static class BossHunt
    {
        public const int WeeklyMains = 3;
        public const int WeeklyMinis = 7;

        /// <summary>The week's run (fewer when the chapters switched on have fewer bosses).</summary>
        public static IReadOnlyList<string> Weekly(int week, IReadOnlyList<HuntBoss> story)
        {
            var mains = new List<int>();
            var minis = new List<int>();
            var seen = new HashSet<string>();
            for (var i = 0; i < story.Count; i++)
                if (seen.Add(story[i].Id)) (story[i].Main ? mains : minis).Add(i);
            var state = 0x9E3779B97F4A7C15UL ^ (ulong)(uint)week * 0xD1B54A32D192ED03UL;
            var pickedMains = Pick(mains, WeeklyMains, ref state);
            var pickedMinis = Pick(minis, WeeklyMinis, ref state);
            var run = new List<string>();
            var groups = pickedMains.Count;
            var m = 0;
            for (var g = 0; g < groups; g++)
            {
                // The minis spread over the groups, the extra ones in the last (7 over 3: 2, 2, 3).
                var take = pickedMinis.Count / groups + (g >= groups - pickedMinis.Count % groups ? 1 : 0);
                for (var i = 0; i < take && m < pickedMinis.Count; i++) run.Add(story[pickedMinis[m++]].Id);
                run.Add(story[pickedMains[g]].Id);
            }
            for (; m < pickedMinis.Count; m++) run.Add(story[pickedMinis[m]].Id);
            return run;
        }

        /// <summary>The full hunt: every boss once, in story order.</summary>
        public static IReadOnlyList<string> Full(IReadOnlyList<HuntBoss> story)
        {
            var run = new List<string>();
            foreach (var b in story)
                if (!run.Contains(b.Id)) run.Add(b.Id);
            return run;
        }

        /// <summary>The week's hunt grows stronger down the run: the i-th of n bosses' health x this (0.9 to 1.2).</summary>
        public static float Ramp(int index, int count) => count <= 1 ? 1f : 0.9f + 0.3f * Math.Clamp(index, 0, count - 1) / (count - 1);

        /// <summary><paramref name="count"/> of the story indices drawn (a partial shuffle), back in story order.</summary>
        private static List<int> Pick(List<int> from, int count, ref ulong state)
        {
            var pool = new List<int>(from);
            var n = Math.Min(count, pool.Count);
            for (var i = 0; i < n; i++)
            {
                var j = i + (int)(Next(ref state) % (ulong)(pool.Count - i));
                (pool[i], pool[j]) = (pool[j], pool[i]);
            }
            var picked = pool.GetRange(0, n);
            picked.Sort();
            return picked;
        }

        /// <summary>SplitMix64: the same numbers on every runtime (System.Random's are not promised).</summary>
        internal static ulong Next(ref ulong state)
        {
            var z = state += 0x9E3779B97F4A7C15UL;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
            return z ^ (z >> 31);
        }
    }

    /// <summary>What a combat support does.</summary>
    public enum HuntSupportKind
    {
        Hull,
        Gunnery,
        Loaders,
        Engines,
        Regen,
        Rapid,
        Logistics,
        WarChest,
        Supply,
        Workshop,
        Bounty,
        Airdrop,
    }

    /// <summary>Prompt 20 N: a combat support picked after a main boss, kept for the rest of the run.</summary>
    public sealed class HuntSupportDef
    {
        public HuntSupportDef(string id, string icon, HuntSupportKind kind, float value)
        {
            Id = id;
            Icon = icon;
            Kind = kind;
            Value = value;
        }

        public string Id { get; }

        /// <summary>Its icon on the pick screen.</summary>
        public string Icon { get; }

        public HuntSupportKind Kind { get; }

        /// <summary>How much (a share, CP, vehicles: see <see cref="HuntSupports.All"/>).</summary>
        public float Value { get; }

        /// <summary>It changes each of the army's vehicles (and each one landed later).</summary>
        public bool PerVehicle => Kind is HuntSupportKind.Hull or HuntSupportKind.Gunnery or HuntSupportKind.Loaders
            or HuntSupportKind.Engines or HuntSupportKind.Regen;
    }

    /// <summary>
    /// Prompt 20 N: the twelve combat supports. Each is a modest edge of a different kind (toughness, damage, fire
    /// rate, speed, repair, the fire supports, CP, army size, bounties, a free drop), so none is the one to take:
    /// the right pick depends on the deck and the bosses left.
    /// </summary>
    public static class HuntSupports
    {
        public const int Offered = 3;

        public static readonly IReadOnlyList<HuntSupportDef> All = new[]
        {
            new HuntSupportDef("hull", "shield", HuntSupportKind.Hull, 0.15f),          // the army's health +15 %
            new HuntSupportDef("gunnery", "crosshair", HuntSupportKind.Gunnery, 0.10f), // its damage +10 %
            new HuntSupportDef("loaders", "ammo", HuntSupportKind.Loaders, 0.12f),      // its fire rate +12 %
            new HuntSupportDef("engines", "move", HuntSupportKind.Engines, 0.12f),      // its speed +12 %
            new HuntSupportDef("regen", "repair", HuntSupportKind.Regen, 0.01f),        // 1 % of health a second out of fire
            new HuntSupportDef("rapid", "airstrike", HuntSupportKind.Rapid, 0.25f),     // fire support cooldowns -25 %
            new HuntSupportDef("logistics", "cp", HuntSupportKind.Logistics, 0.20f),    // CP income +20 %
            new HuntSupportDef("warchest", "coin", HuntSupportKind.WarChest, 35f),      // 35 CP now
            new HuntSupportDef("supply", "people", HuntSupportKind.Supply, 6f),         // army cap +6
            new HuntSupportDef("workshop", "gear", HuntSupportKind.Workshop, 1f),       // rests repair twice as much
            new HuntSupportDef("bounty", "trophy", HuntSupportKind.Bounty, 0.5f),       // boss bounties +50 %
            new HuntSupportDef("airdrop", "reinforce", HuntSupportKind.Airdrop, 3f),    // three of the deck's vehicles, free
        };

        public static HuntSupportDef? Get(string id)
        {
            foreach (var s in All)
                if (s.Id == id) return s;
            return null;
        }

        /// <summary>Three supports not held yet, drawn from the run's seed and the boss just beaten (the same on a resumed run).</summary>
        public static IReadOnlyList<string> Offer(int seed, int boss, IReadOnlyCollection<string> held)
        {
            var pool = new List<string>();
            foreach (var s in All)
                if (!Contains(held, s.Id)) pool.Add(s.Id);
            var state = (ulong)(uint)seed * 0x9E3779B97F4A7C15UL ^ (ulong)(uint)(boss + 1) * 0xC2B2AE3D27D4EB4FUL;
            var n = Math.Min(Offered, pool.Count);
            for (var i = 0; i < n; i++)
            {
                var j = i + (int)(BossHunt.Next(ref state) % (ulong)(pool.Count - i));
                (pool[i], pool[j]) = (pool[j], pool[i]);
            }
            return pool.GetRange(0, n);
        }

        private static bool Contains(IReadOnlyCollection<string> list, string id)
        {
            foreach (var s in list)
                if (s == id) return true;
            return false;
        }

        /// <summary>A per-vehicle support on one of the army's vehicles (its share of health kept).</summary>
        internal static void Fit(Vehicle v, HuntSupportDef s)
        {
            switch (s.Kind)
            {
                case HuntSupportKind.Hull:
                    var share = v.MaxHp > 0f ? v.Hp / v.MaxHp : 1f;
                    v.HpScale *= 1f + s.Value;
                    v.Hp = v.MaxHp * share;
                    break;
                case HuntSupportKind.Gunnery:
                    v.DamageBoost *= 1f + s.Value;
                    break;
                case HuntSupportKind.Loaders:
                    v.FireBoost *= 1f + s.Value;
                    break;
                case HuntSupportKind.Engines:
                    v.DoctrineSpeed *= 1f + s.Value;
                    break;
                case HuntSupportKind.Regen:
                    v.Regen += s.Value;
                    break;
            }
        }
    }

    public sealed partial class BossRushRules
    {
        /// <summary>Prompt 20 N: where the run keeps checkpoints (none: the old Boss Rush).</summary>
        public HuntCheckpoints Checkpoints { get; set; } = HuntCheckpoints.None;

        /// <summary>Prompt 20 N: a pick of one of three combat supports after each main boss.</summary>
        public bool Supports { get; set; }

        /// <summary>Seeds the support offers (the week's number, or the full hunt's fixed seed).</summary>
        public int Seed { get; set; }

        /// <summary>Prompt 20 N: the bosses grow stronger down the run (<see cref="BossHunt.Ramp"/>).</summary>
        public bool Ramp { get; set; }

        /// <summary>Prompt 20 N: the share of its health each of the army's vehicles gets back when a boss falls.</summary>
        public float RestRepair { get; set; }
    }

    public sealed partial class BossRushCarry
    {
        /// <summary>Prompt 20 N: the combat supports held.</summary>
        public List<string> Supports { get; } = new();

        /// <summary>Prompt 20 N: this carry is a checkpoint (the rest before the next boss starts again).</summary>
        public bool Checkpoint { get; set; }

        /// <summary>Prompt 20 N: bosses already paid for in earlier sittings (a resumed run pays only for the rest).</summary>
        public int Paid { get; set; }
    }

    public sealed partial class BossRushMode
    {
        private readonly List<string> _held = new();
        private readonly HashSet<EntityId> _fitted = new();
        private IReadOnlyList<string>? _offer;
        private bool _checkpointDue;
        private float _bountyScale = 1f, _repairScale = 1f, _ramp = 1f;

        /// <summary>The supports offered after the main boss just beaten, until one is picked (null: none).</summary>
        public IReadOnlyList<string>? Offer => _offer;

        /// <summary>The supports held this run, in the order picked.</summary>
        public IReadOnlyList<string> Held => _held;

        /// <summary>The last checkpoint (the state as the rest after a boss ended), or null.</summary>
        public BossRushCarry? Checkpoint { get; private set; }

        /// <summary>Checkpoints kept this battle (the session saves each new one).</summary>
        public int CheckpointsTaken { get; private set; }

        /// <summary>Between two bosses: the rest's seconds left (negative: not resting).</summary>
        public float RestLeft(SimWorld world) =>
            !Boss.IsValid && Defeated > 0 && Defeated < Total && SwitchTo == null && Result == null ? MathF.Max(0f, (float)(_nextBossAt - world.Time)) : -1f;

        /// <summary>The boss that comes next (null once all are down).</summary>
        public string? Next => Defeated < Total ? _rules.Bosses[Defeated] : null;

        /// <summary>The share of its health each vehicle gets back when a boss falls (with the workshop support).</summary>
        public float RestRepairShare => _rules.RestRepair * _repairScale;

        /// <summary>Bosses already paid for in earlier sittings of this run.</summary>
        public int PaidBefore => _rules.Resume?.Paid ?? 0;

        /// <summary>The run's seconds so far, over every battlefield and sitting.</summary>
        public double TotalSeconds(SimWorld world) => TimeUsed + world.Time;

        /// <summary>Whether a boss is a main boss (by its data's rank).</summary>
        public static bool IsMain(SimWorld world, string id) => world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Rank == BossRank.Main;

        /// <summary>The support picked from the offer: kept for the rest of the run (a recorded input, so replays match).</summary>
        public bool Choose(SimWorld world, string id)
        {
            if (_offer == null || !Contains(_offer, id) || HuntSupports.Get(id) is not { } support) return false;
            _offer = null;
            _held.Add(id);
            Apply(world, support, fresh: true);
            return true;
        }

        private static bool Contains(IReadOnlyList<string> list, string id)
        {
            foreach (var s in list)
                if (s == id) return true;
            return false;
        }

        /// <summary>Setup's end: a resumed run takes its supports back (the one-off ones are in its CP and army already).</summary>
        private void HuntSetup(SimWorld world)
        {
            if (_rules.Ramp) world.SetMutators(EnemyTeam, def => def.Boss ? (_ramp, 1f + (_ramp - 1f) * 0.5f) : (1f, 1f));
            if (_rules.Resume is not { } resume) return;
            foreach (var id in resume.Supports)
                if (HuntSupports.Get(id) is { } support && !_held.Contains(id))
                {
                    _held.Add(id);
                    Apply(world, support, fresh: false);
                }
        }

        private void Apply(SimWorld world, HuntSupportDef s, bool fresh)
        {
            world.TryGetEconomy(PlayerTeam, out var economy);
            switch (s.Kind)
            {
                case HuntSupportKind.Rapid:
                    if (economy != null) economy.StrikeScale *= 1f - s.Value;
                    break;
                case HuntSupportKind.Logistics:
                    economy?.ScaleIncome(1f + s.Value);
                    break;
                case HuntSupportKind.Supply:
                    if (economy != null) economy.SupplyBonus += (int)s.Value;
                    break;
                case HuntSupportKind.Workshop:
                    _repairScale *= 1f + s.Value;
                    break;
                case HuntSupportKind.Bounty:
                    _bountyScale *= 1f + s.Value;
                    break;
                case HuntSupportKind.WarChest when fresh:
                    if (economy != null) economy.Cp = MathF.Min(economy.Bank, economy.Cp + s.Value);
                    break;
                case HuntSupportKind.Airdrop when fresh:
                    Airdrop(world, economy, (int)s.Value);
                    break;
            }
            if (!s.PerVehicle) return;
            // The vehicles already fitted take the new one; the rest get every support held when they are fitted.
            foreach (var v in world.VehicleList)
                if (v.IsAlive && _fitted.Contains(v.Id)) HuntSupports.Fit(v, s);
        }

        /// <summary>The deck's dearest vehicle cards, landed at the drop zone for free.</summary>
        private static void Airdrop(SimWorld world, Economy.TeamEconomy? economy, int count)
        {
            if (economy == null || !world.TryGetRally(PlayerTeam, out var rally)) return;
            var cards = new List<VehicleDef>();
            foreach (var id in economy.Vehicles)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && !def.Static && def.CpCost > 0) cards.Add(def);
            cards.Sort((a, b) => b.CpCost != a.CpCost ? b.CpCost.CompareTo(a.CpCost) : string.CompareOrdinal(a.Id, b.Id));
            for (var i = 0; i < count && cards.Count > 0; i++) world.Economy.Airlift(PlayerTeam, cards[i % cards.Count].Id, rally);
        }

        /// <summary>Each step: the army's vehicles not fitted yet take the per-vehicle supports held.</summary>
        private void HuntTick(SimWorld world)
        {
            if (_held.Count == 0) return;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != PlayerTeam || v.Def.Static || v.Def.Boss || !_fitted.Add(v.Id)) continue;
                foreach (var id in _held)
                    if (HuntSupports.Get(id) is { PerVehicle: true } s) HuntSupports.Fit(v, s);
            }
        }

        /// <summary>A boss fell and the rest begins: the army is partly repaired, a support offered after a main boss, a checkpoint due.</summary>
        private void HuntRest(SimWorld world, string fallen)
        {
            if (_rules.RestRepair > 0f)
                foreach (var v in world.VehicleList)
                    if (v.IsAlive && v.Team == PlayerTeam && !v.Def.Static)
                        v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * _rules.RestRepair * _repairScale);
            var main = IsMain(world, fallen);
            if (_rules.Supports && main) _offer = HuntSupports.Offer(_rules.Seed, Defeated - 1, _held);
            if (_offer is { Count: 0 }) _offer = null;
            if (_rules.Checkpoints == HuntCheckpoints.EveryBoss || (_rules.Checkpoints == HuntCheckpoints.MainBosses && main)) _checkpointDue = true;
        }

        /// <summary>The rest is over: an offer not answered takes its first support; the checkpoint is kept (with it).</summary>
        private void HuntRestOver(SimWorld world)
        {
            if (_offer is { Count: > 0 } offer) Choose(world, offer[0]);
            if (!_checkpointDue) return;
            _checkpointDue = false;
            var map = _rules.HomeMap ?? world.Map.Id;
            // The map's id without its version (prompt 22 E's "veyra_old_quarter" has underscores of its own).
            foreach (var suffix in new[] { "_conquest", "_sandbox", "_siege", "_long" })
                if (map.EndsWith(suffix, StringComparison.Ordinal))
                {
                    map = map.Substring(0, map.Length - suffix.Length);
                    break;
                }
            var carry = Carry(world, map);
            carry.Checkpoint = true;
            Checkpoint = carry;
            CheckpointsTaken++;
        }

        /// <summary>Tests: offers these supports now (as after a main boss).</summary>
        internal void DebugOffer(IReadOnlyList<string> offer) => _offer = offer;

        /// <summary>The next boss's strength in the week's hunt.</summary>
        private void HuntRamp() => _ramp = _rules.Ramp ? BossHunt.Ramp(Defeated, Total) : 1f;
    }
}
