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
        public HuntBoss(string id, bool main, int chapter, bool airDefence = false)
        {
            Id = id;
            Main = main;
            Chapter = chapter;
            AirDefence = airDefence;
        }

        public string Id { get; }
        public bool Main { get; }
        public int Chapter { get; }

        /// <summary>Play-test 6 (DECISIONS 21G): it answers aircraft itself (flak, SAMs).</summary>
        public bool AirDefence { get; }
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
        public static int WeeklyMinis => global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossHunt.WeeklyMinis;

        /// <summary>Play-test 6 (DECISIONS 21G): the week's run has at least this many main and mini bosses that answer aircraft.</summary>
        public static int AirDefenceMains => global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossHunt.AirDefenceMains;
        public static int AirDefenceMinis => global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossHunt.AirDefenceMinis;

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
            // Play-test 6: aircraft ruled a run of bosses with no air defence; swap the last picks without it for ones with it.
            Mix(story, mains, pickedMains, AirDefenceMains, ref state);
            Mix(story, minis, pickedMinis, AirDefenceMinis, ref state);
            var run = new List<string>();
            var groups = pickedMains.Count;
            var m = 0;
            for (var g = 0; g < groups; g++)
            {
                // The minis spread over the groups, the extra ones in the first (7 over 3: 3, 2, 2, so the mains stand at 4, 7 and 10; prompt 26 E.2).
                var take = pickedMinis.Count / groups + (g < pickedMinis.Count % groups ? 1 : 0);
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

        /// <summary>The full hunt's first and last boss multipliers (prompt 26 E.3).</summary>
        public const float FullFrom = 0.8f, FullTo = 1.3f;

        /// <summary>The week's step per boss (prompt 26 E.2: 1 + 0.06 (i - 1), x1.0 to x1.54 over ten).</summary>
        public const float WeeklyStep = 0.06f;

        /// <summary>
        /// Prompt 26 E.2/E.3: the i-th (0-based) of n bosses' multiplier m on its health and damage. The week's hunt: 1 + 0.06 i.
        /// The full hunt: a straight line in story order from x0.8 at the first boss to x1.3 at the last.
        /// </summary>
        public static float Multiplier(int index, int count, bool full)
        {
            var i = Math.Clamp(index, 0, Math.Max(0, count - 1));
            if (!full) return 1f + WeeklyStep * i;
            return count <= 1 ? 1f : FullFrom + (FullTo - FullFrom) * i / (count - 1);
        }

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

        /// <summary>
        /// Play-test 6: at least <paramref name="want"/> of <paramref name="picked"/> answer aircraft: a drawn boss without air
        /// defence (the latest in story order first) gives way to one with it not drawn (drawn from the rest), back in story order.
        /// </summary>
        private static void Mix(IReadOnlyList<HuntBoss> story, List<int> pool, List<int> picked, int want, ref ulong state)
        {
            var have = 0;
            foreach (var i in picked)
                if (story[i].AirDefence) have++;
            var spare = new List<int>();
            foreach (var i in pool)
                if (story[i].AirDefence && !picked.Contains(i)) spare.Add(i);
            for (var k = picked.Count - 1; k >= 0 && have < want && spare.Count > 0; k--)
            {
                if (story[picked[k]].AirDefence) continue;
                var j = (int)(Next(ref state) % (ulong)spare.Count);
                picked[k] = spare[j];
                spare.RemoveAt(j);
                have++;
            }
            picked.Sort();
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
        public HuntSupportDef(string id, string icon, HuntSupportKind kind, float value, float strength = 0f)
        {
            Strength = strength;
            Id = id;
            Icon = icon;
            Kind = kind;
            Value = value;
        }

        public string Id { get; }

        /// <summary>Its icon on the pick screen.</summary>
        public string Icon { get; }

        public HuntSupportKind Kind { get; }

        /// <summary>
        /// Prompt 26 E.2: how much army strength it adds (a share, 0.15 = +15 %); the supports held may add up to
        /// <see cref="HuntSupports.Cap"/>. 0: it changes how the run is played instead (an extra drop, quicker cards) and is never capped.
        /// </summary>
        public float Strength { get; }

        public bool PlayChanging => Strength <= 0f;

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

        /// <summary>Prompt 26 E.2: all the supports together add at most this much army strength (+40 %).</summary>
        public static float Cap => global::MachineBrigade.Sim.Content.SimTunables.Bosses.HuntSupports.Cap;

        public static readonly IReadOnlyList<HuntSupportDef> All = new[]
        {
            new HuntSupportDef("hull", "shield", HuntSupportKind.Hull, 0.15f, 0.15f),          // the army's health +15 %
            new HuntSupportDef("gunnery", "crosshair", HuntSupportKind.Gunnery, 0.10f, 0.10f), // its damage +10 %
            new HuntSupportDef("loaders", "ammo", HuntSupportKind.Loaders, 0.12f, 0.12f),      // its fire rate +12 %
            new HuntSupportDef("engines", "move", HuntSupportKind.Engines, 0.12f, 0.06f),      // its speed +12 %
            new HuntSupportDef("regen", "repair", HuntSupportKind.Regen, 0.01f, 0.08f),        // 1 % of health a second out of fire
            new HuntSupportDef("rapid", "airstrike", HuntSupportKind.Rapid, 0.25f),     // fire support cooldowns -25 %
            new HuntSupportDef("logistics", "cp", HuntSupportKind.Logistics, 0.20f, 0.10f),    // CP income +20 %
            new HuntSupportDef("warchest", "coin", HuntSupportKind.WarChest, 35f, 0.05f),      // 35 CP now
            new HuntSupportDef("supply", "people", HuntSupportKind.Supply, 6f, 0.08f),         // army cap +6
            new HuntSupportDef("workshop", "gear", HuntSupportKind.Workshop, 1f, 0.05f),       // rests repair twice as much
            new HuntSupportDef("bounty", "trophy", HuntSupportKind.Bounty, 0.5f, 0.05f),       // boss bounties +50 %
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
            // Prompt 26 E.2/E.3: a support that would take the held ones past the +40 % cap is not offered; once the cap is
            // reached only the play-changing ones are (the extra drop, the quicker cards).
            var used = Strength(held);
            var pool = new List<string>();
            foreach (var s in All)
                if (!Contains(held, s.Id) && (s.PlayChanging || used + s.Strength <= Cap + 1e-4f)) pool.Add(s.Id);
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

        /// <summary>The army strength the supports held add together (counts against <see cref="Cap"/>).</summary>
        public static float Strength(IReadOnlyCollection<string> held)
        {
            var sum = 0f;
            foreach (var id in held)
                if (Get(id) is { } s) sum += s.Strength;
            return sum;
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
                    v.SpeedScale *= 1f + s.Value;
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

        /// <summary>
        /// Play-test 6 (DECISIONS 21G): once the last boss is down the player may carry on: the roster again from the
        /// top, each boss stronger than the one before and with more escorts, until the army falls. The rush is won
        /// either way; the endless bosses pay as the rush's do.
        /// </summary>
        public bool EndlessOffer { get; set; }

        /// <summary>Seconds the choice stays open (unanswered: the rush ends there, won).</summary>
        public float EndlessChoice { get; set; } = 20f;

        /// <summary>
        /// Prompt 30 L5: the choice comes on the results (the win recorded first: Continue / End) instead of in the battle.
        /// The rush ends won at its last boss; "Continue" reopens it (<see cref="BossRushMode.ContinueEndless"/>).
        /// </summary>
        public bool EndlessAtResults { get; set; } = true;

        /// <summary>Each endless boss's health and damage over the rush's last, a share per step (sheet "Vô hạn": +8 % a boss).</summary>
        public float EndlessHp { get; set; } = EndlessRules.EnemyPerBoss;

        public float EndlessDamage { get; set; } = EndlessRules.EnemyPerBoss;

        /// <summary>The escorts of the endless run: one more alive at once every this many bosses, all their guards, and this much tougher and harder-hitting a step.</summary>
        public int EndlessEscortEvery { get; set; } = 2;

        /// <summary>Prompt 30 L5: the endless escorts grow in stats only (+8 % a boss), not in number.</summary>
        public float EndlessEscort { get; set; } = EndlessRules.EnemyPerBoss;

        public bool EndlessMoreEscorts { get; set; }

        /// <summary>
        /// Prompt 26 E.1: the player's estimated damage a second on a boss (<c>HuntPower</c>), set once from the carried deck. A boss's
        /// health is then P x its target seconds x <see cref="HpShare"/> x m x the tier's health; its damage the data's x m x the
        /// tier's. 0: no estimate (a bare test battle): the ramp and the tier's factors only.
        /// </summary>
        public float Power { get; set; }

        /// <summary>Seconds a mini and a main boss should take to bring down (weekly 66 s / 2.8 min; the full hunt 1 / 2.5 min).</summary>
        public float MiniSeconds { get; set; } = 66f;

        public float MainSeconds { get; set; } = 168f;

        /// <summary>The share of P x t the boss's health is (0.6: the army does not hit all the time).</summary>
        public float HpShare { get; set; } = 0.6f;

        /// <summary>Prompt 26 E.3: the ramp is the full hunt's (x0.8 to x1.3 in story order), not the week's.</summary>
        public bool FullRamp { get; set; }

        /// <summary>Prompt 26 E.3: every boss is a fresh battle: the army is not kept and the CP is the starting CP; only supports are.</summary>
        public bool Fresh { get; set; }

        /// <summary>Prompt 26 E.2: the share of the CP held that is kept between two bosses (1: all, as before; the week's 0.5).</summary>
        public float CpKept { get; set; } = 1f;

        /// <summary>Play-test 6: the difficulty's strength on every boss (health, damage).</summary>
        public float BossHp { get; set; } = 1f;

        public float BossDamage { get; set; } = 1f;
    }

    public sealed partial class BossRushCarry
    {
        /// <summary>Prompt 20 N: the combat supports held.</summary>
        public List<string> Supports { get; } = new();

        /// <summary>Prompt 20 N: this carry is a checkpoint (the rest before the next boss starts again).</summary>
        public bool Checkpoint { get; set; }

        /// <summary>Prompt 20 N: bosses already paid for in earlier sittings (a resumed run pays only for the rest).</summary>
        public int Paid { get; set; }

        /// <summary>Play-test 6: the run is in its endless part (a switch of battlefield for a sea boss carries it).</summary>
        public bool Endless { get; set; }

        /// <summary>Prompt 26 E.1: the run's P (measured once at its start, kept over checkpoints and sittings); 0: estimate again.</summary>
        public float Power { get; set; }
    }

    public sealed partial class BossRushMode : IEndlessMode
    {
        /// <summary>Prompt 30 L5: the rush won at its last boss, the results may carry on.</summary>
        public bool CanContinue => _rules.EndlessOffer && _rules.EndlessAtResults && !Endless && Defeated >= Total && Result is { WinningTeam: PlayerTeam };

        public bool InEndless => Endless;

        public int EndlessSteps => Endless ? Math.Max(0, Defeated - Total) : 0;

        /// <summary>"Continue" on the results: the next boss after the breather, stronger each time.</summary>
        public void ContinueEndless(SimWorld world)
        {
            if (!CanContinue) return;
            Result = null;
            Endless = true;
            _nextBossAt = world.Time + _rules.Breather;
        }

        private readonly List<string> _held = new();
        private readonly HashSet<EntityId> _fitted = new();
        private IReadOnlyList<string>? _offer;
        private bool _checkpointDue;
        private float _bountyScale = 1f, _repairScale = 1f, _ramp = 1f;
        private float _endlessHp = 1f, _endlessDamage = 1f, _escortStrength = 1f;
        private double _endlessUntil = -1;
        private int _escortBase = -1;

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
            !Boss.IsValid && Defeated > 0 && (Defeated < Total || Endless) && !EndlessOpen && SwitchTo == null && Result == null
                ? MathF.Max(0f, (float)(_nextBossAt - world.Time)) : -1f;

        /// <summary>The boss that comes next (null once all are down, until the endless run).</summary>
        public string? Next => Defeated < Total || Endless ? BossAt(Defeated) : null;

        /// <summary>Play-test 6 (DECISIONS 21G): the run has gone on past its last boss.</summary>
        public bool Endless { get; private set; }

        /// <summary>The choice after the last boss is open (the rush ends, won, when it runs out).</summary>
        public bool EndlessOpen => _endlessUntil >= 0.0;

        /// <summary>Seconds left to choose (negative: no choice open).</summary>
        public float EndlessChoiceLeft(SimWorld world) => EndlessOpen ? MathF.Max(0f, (float)(_endlessUntil - world.Time)) : -1f;

        /// <summary>Bosses brought down in the endless run.</summary>
        public int EndlessDefeated => Endless ? Math.Max(0, Defeated - Total) : 0;

        /// <summary>The rush's bosses in order, then (endless) the same again from the top.</summary>
        private string BossAt(int index) => _rules.Bosses[index % _rules.Bosses.Count];

        private void OfferEndless(SimWorld world)
        {
            _endlessUntil = world.Time + _rules.EndlessChoice;
            _offer = null;
        }

        /// <summary>The answer to the choice after the last boss (a recorded input): carry on, or end the rush now (won).</summary>
        public bool ChooseEndless(SimWorld world, bool carryOn)
        {
            if (!EndlessOpen || Result != null) return false;
            _endlessUntil = -1;
            if (!carryOn)
            {
                Finish(world, PlayerTeam);
                return true;
            }
            Endless = true;
            _nextBossAt = world.Time + _rules.Breather;
            return true;
        }

        /// <summary>While the choice is open nothing comes; unanswered, the rush ends won. True while it holds the run.</summary>
        private bool EndlessTick(SimWorld world)
        {
            if (!EndlessOpen) return false;
            if (world.Time >= _endlessUntil) ChooseEndless(world, false);
            return true;
        }

        /// <summary>The endless run's next step: its boss's strength, and the escorts' number and strength.</summary>
        private void EndlessRamp(SimWorld world)
        {
            if (!Endless) return;
            var step = Math.Max(1, Defeated - Total + 1);
            _endlessHp = 1f + _rules.EndlessHp * step;
            _endlessDamage = 1f + _rules.EndlessDamage * step;
            _escortStrength = 1f + _rules.EndlessEscort * step;
            if (world.EscortSettings is not { } escorts || !_rules.EndlessMoreEscorts) return;
            if (_escortBase < 0) _escortBase = escorts.Cap;
            escorts.Cap = _escortBase + step / Math.Max(1, _rules.EndlessEscortEvery);
            escorts.Guards = 1f;
        }

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
            // The week's ramp, the difficulty's strength and (play-test 6) the endless run's steps on each boss and escort as it comes.
            if (_rules.Ramp || _rules.Power > 0f || _rules.EndlessOffer || _rules.BossHp != 1f || _rules.BossDamage != 1f || _rules.Resume is { Endless: true })
                world.SetMutators(EnemyTeam, def => def.Boss
                    ? (BossHealthScale(def) * _endlessHp, _ramp * _rules.BossDamage * _endlessDamage)
                    : (_escortStrength, _escortStrength));
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
            // Play-test 6: after the last boss the choice to go on comes instead (no support, no checkpoint past the roster).
            if (_rules.Supports && main && !EndlessOpen) _offer = HuntSupports.Offer(_rules.Seed, Defeated - 1, _held);
            if (_offer is { Count: 0 }) _offer = null;
            if (Defeated < Total && (_rules.Checkpoints == HuntCheckpoints.EveryBoss || (_rules.Checkpoints == HuntCheckpoints.MainBosses && main))) _checkpointDue = true;
        }

        /// <summary>The rest is over: an offer not answered takes its first support; the checkpoint is kept (with it).</summary>
        private void HuntRestOver(SimWorld world)
        {
            if (_offer is { Count: > 0 } offer) Choose(world, offer[0]);
            if (!_checkpointDue) return;
            _checkpointDue = false;
            var carry = Carry(world, BaseMap(world, _rules.HomeMap ?? world.Map.Id));
            carry.Checkpoint = true;
            Checkpoint = carry;
            CheckpointsTaken++;
        }

        /// <summary>A map's id without its version (prompt 22 E's "veyra_old_quarter" has underscores of its own); default: the battle's map.</summary>
        private static string BaseMap(SimWorld world, string? map = null)
        {
            map ??= world.Map.Id;
            foreach (var suffix in new[] { "_conquest", "_sandbox", "_siege", "_long" })
                if (map.EndsWith(suffix, StringComparison.Ordinal))
                    return map.Substring(0, map.Length - suffix.Length);
            return map;
        }

        /// <summary>Tests: offers these supports now (as after a main boss).</summary>
        internal void DebugOffer(IReadOnlyList<string> offer) => _offer = offer;

        /// <summary>
        /// Prompt 26 E.1: the factor on a boss def's health. With P: health = P x t x 0.6 x m x the tier's, so the factor is that over
        /// the def's own; without (no estimate): m x the tier's.
        /// </summary>
        private float BossHealthScale(VehicleDef def)
        {
            if (_rules.Power <= 0f || def.MaxHp <= 0f) return _ramp * _rules.BossHp;
            var seconds = def.Rank == BossRank.Main ? _rules.MainSeconds : _rules.MiniSeconds;
            return _rules.Power * seconds * _rules.HpShare * _ramp * _rules.BossHp / def.MaxHp;
        }

        /// <summary>The next boss's multiplier m (prompt 26 E.2/E.3), on its health and damage.</summary>
        private void HuntRamp(SimWorld world)
        {
            _ramp = _rules.Ramp ? BossHunt.Multiplier(Math.Min(Defeated, Total - 1), Total, _rules.FullRamp) : 1f;
            EndlessRamp(world);
        }

        /// <summary>Prompt 26 E.2: when a boss falls only this share of the CP held is kept (the bounty comes on top).</summary>
        private void HuntCpCut(SimWorld world)
        {
            if (_rules.CpKept >= 1f || !world.TryGetEconomy(PlayerTeam, out var economy)) return;
            economy.Cp *= Math.Clamp(_rules.CpKept, 0f, 1f);
        }
    }
}
