#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Sim.Content
{
    /// <summary>An Operations tier: how much stronger the enemy, how much poorer the player, and what it is worth.</summary>
    public sealed class OperationTier
    {
        public string Id { get; set; } = "";
        public float Enemy { get; set; } = 1f;
        public float PlayerIncome { get; set; } = 1f;
        public bool Supports { get; set; } = true;
        public float Score { get; set; } = 1f;
    }

    /// <summary>
    /// A weekly mutator (prompt 6): one twist on a battle, combinable with others. Every field is
    /// data; a field left at its default changes nothing.
    /// </summary>
    public sealed class MutatorDef
    {
        public string Id { get; set; } = "";

        /// <summary>Added to the score multiplier.</summary>
        public float Score { get; set; }

        public IReadOnlyList<string> Excludes { get; set; } = Array.Empty<string>();

        public string? Weather { get; set; }
        public float EnemyCp { get; set; } = 1f;
        public float EnemyIncome { get; set; } = 1f;
        public float PlayerIncome { get; set; } = 1f;
        public bool NoSupports { get; set; }

        /// <summary>The player may only bring vehicles cheaper than this (0: any).</summary>
        public int PlayerMaxCp { get; set; }

        /// <summary>The player may only bring heavy armour.</summary>
        public bool PlayerHeavy { get; set; }

        /// <summary>The enemy fields aircraft only.</summary>
        public bool EnemyAir { get; set; }

        /// <summary>Neither side may field aircraft.</summary>
        public bool NoAir { get; set; }

        public bool ExtraBoss { get; set; }
        public float TowerHp { get; set; } = 1f;
        public float TowerDamage { get; set; } = 1f;
        public float EnemyHp { get; set; } = 1f;
        public float BothDamage { get; set; } = 1f;
        public float BothHp { get; set; } = 1f;

        /// <summary>The time limit scaled (a battle without one gets 25 minutes scaled).</summary>
        public float TimeScale { get; set; } = 1f;

        /// <summary>Bomber raids on the busiest fight, for both sides.</summary>
        public bool Raids { get; set; }

        /// <summary>The enemy's reinforcements come twice as many, in cheap swarms.</summary>
        public bool Swarm { get; set; }

        /// <summary>The player's base has no towers (the HQ alone).</summary>
        public bool EmptyBase { get; set; }

        /// <summary>No repair bay, no repair drops.</summary>
        public bool NoRepair { get; set; }

        /// <summary>Prompt 16: sight out onto the sea (the "Sea storm": fog on the water).</summary>
        public float SeaSight { get; set; } = 1f;

        /// <summary>Prompt 16: escorts and attack boats added to a flagship's fleet (the "Fleet").</summary>
        public int ExtraEscorts { get; set; }
        public int ExtraRaiders { get; set; }

        public bool Clashes(MutatorDef other) => Contains(Excludes, other.Id) || Contains(other.Excludes, Id) || other.Id == Id ||
                                                   (Weather != null && other.Weather != null);

        private static bool Contains(IReadOnlyList<string> list, string id)
        {
            foreach (var s in list)
                if (s == id) return true;
            return false;
        }
    }

    /// <summary>How a won Operations battle is scored (operations.json "score").</summary>
    public sealed class OperationScoring
    {
        public float Win { get; set; } = 5000f;
        public float Time { get; set; } = 3000f;
        public float Par { get; set; } = 1500f;
        public float Losses { get; set; } = 2000f;
        public float LossesAtZero { get; set; } = 20f;
        public float Hq { get; set; } = 2000f;

        /// <summary>
        /// The score: 0 for a loss; for a win, a base plus the time under par, the losses under
        /// <see cref="LossesAtZero"/> and the HQ's health left, all times the tier's and the
        /// mutators' multipliers.
        /// </summary>
        public int Score(bool won, double seconds, int losses, float hqLeft, OperationTier tier, IReadOnlyList<MutatorDef> mutators)
        {
            if (!won) return 0;
            var raw = Win + Time * MathF.Max(0f, 1f - (float)seconds / MathF.Max(1f, Par)) +
                      Losses * MathF.Max(0f, 1f - losses / MathF.Max(1f, LossesAtZero)) + Hq * Math.Clamp(hqLeft, 0f, 1f);
            var mult = tier.Score;
            foreach (var m in mutators) mult += m.Score;
            return (int)MathF.Round(raw * mult);
        }
    }

    /// <summary>The Operations data (Resources/Data/operations.json).</summary>
    public sealed class OperationsData
    {
        public IReadOnlyList<OperationTier> Tiers { get; set; } = Array.Empty<OperationTier>();
        public IReadOnlyList<MutatorDef> Mutators { get; set; } = Array.Empty<MutatorDef>();
        public OperationScoring Scoring { get; set; } = new();
        public int WeeklyFortressReward { get; set; } = 600;
        public int WeeklyOperationReward { get; set; } = 800;

        public MutatorDef? Mutator(string id)
        {
            foreach (var m in Mutators)
                if (m.Id == id) return m;
            return null;
        }

        /// <summary>Every pair of mutators that may be drawn together, in data order.</summary>
        public List<(MutatorDef a, MutatorDef b)> Pairs()
        {
            var pairs = new List<(MutatorDef, MutatorDef)>();
            for (var i = 0; i < Mutators.Count; i++)
                for (var j = i + 1; j < Mutators.Count; j++)
                    if (!Mutators[i].Clashes(Mutators[j])) pairs.Add((Mutators[i], Mutators[j]));
            return pairs;
        }

        /// <summary>Weeks in the rotation before it repeats.</summary>
        public const int RotationWeeks = 26;

        /// <summary>
        /// The rotation: for each of <see cref="RotationWeeks"/> weeks an operation (round the
        /// list) and a pair of mutators, drawn once from all the allowed pairs with a fixed seed so
        /// every mutator comes up and no pair repeats. The same data always gives the same table.
        /// </summary>
        public List<(int operation, MutatorDef a, MutatorDef b)> Rotation(int operations)
        {
            var table = new List<(int, MutatorDef, MutatorDef)>();
            var pairs = Pairs();
            if (operations <= 0 || pairs.Count == 0) return table;
            // A fixed shuffle (Fisher-Yates with a small LCG), then pairs taken so each mutator
            // appears before any appears a third time.
            var order = new List<(MutatorDef a, MutatorDef b)>(pairs);
            uint state = 0x9E3779B9;
            for (var i = order.Count - 1; i > 0; i--)
            {
                state = state * 1664525u + 1013904223u;
                var j = (int)(state % (uint)(i + 1));
                (order[i], order[j]) = (order[j], order[i]);
            }
            var uses = new Dictionary<string, int>();
            var used = new bool[order.Count];
            for (var week = 0; week < RotationWeeks; week++)
            {
                var pick = -1;
                for (var cap = 1; pick < 0 && cap < 100; cap++)
                    for (var k = 0; k < order.Count; k++)
                    {
                        if (used[k]) continue;
                        var (a, b) = order[k];
                        if (uses.GetValueOrDefault(a.Id) >= cap || uses.GetValueOrDefault(b.Id) >= cap) continue;
                        pick = k;
                        break;
                    }
                if (pick < 0) break;
                used[pick] = true;
                var (x, y) = order[pick];
                uses[x.Id] = uses.GetValueOrDefault(x.Id) + 1;
                uses[y.Id] = uses.GetValueOrDefault(y.Id) + 1;
                table.Add((week % operations, x, y));
            }
            return table;
        }

        /// <summary>The week's entry of the rotation (a week number: year x 100 + ISO week).</summary>
        public (int operation, MutatorDef a, MutatorDef b)? Weekly(int week, int operations)
        {
            var table = Rotation(operations);
            if (table.Count == 0) return null;
            var index = (week / 100 * 53 + week % 100) % table.Count;
            return table[index];
        }

        public static OperationsData FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "operations");
            var tiers = new List<OperationTier>();
            foreach (var t in root.Array("tiers"))
                tiers.Add(new OperationTier
                {
                    Id = t.String("id"), Enemy = t.Float("enemy", 1f), PlayerIncome = t.Float("playerIncome", 1f),
                    Supports = t.Bool("supports", true), Score = t.Float("score", 1f),
                });
            var mutators = new List<MutatorDef>();
            foreach (var m in root.Array("mutators"))
                mutators.Add(new MutatorDef
                {
                    Id = m.String("id"), Score = m.Float("score", 0f), Excludes = m.Has("excludes") ? m.StringArray("excludes") : Array.Empty<string>(),
                    Weather = m.Has("weather") ? m.String("weather") : null,
                    EnemyCp = m.Float("enemyCp", 1f), EnemyIncome = m.Float("enemyIncome", 1f), PlayerIncome = m.Float("playerIncome", 1f),
                    NoSupports = m.Bool("noSupports", false), PlayerMaxCp = m.Int("playerMaxCp", 0), PlayerHeavy = m.Bool("playerHeavy", false),
                    EnemyAir = m.Bool("enemyAir", false), NoAir = m.Bool("noAir", false), ExtraBoss = m.Bool("extraBoss", false),
                    TowerHp = m.Float("towerHp", 1f), TowerDamage = m.Float("towerDamage", 1f), EnemyHp = m.Float("enemyHp", 1f),
                    BothDamage = m.Float("bothDamage", 1f), BothHp = m.Float("bothHp", 1f), TimeScale = m.Float("timeScale", 1f),
                    Raids = m.Bool("raids", false), Swarm = m.Bool("swarm", false), EmptyBase = m.Bool("emptyBase", false),
                    NoRepair = m.Bool("noRepair", false),
                    SeaSight = Math.Clamp(m.Float("seaSight", 1f), 0.1f, 1f), ExtraEscorts = m.Int("extraEscorts", 0), ExtraRaiders = m.Int("extraRaiders", 0),
                });
            var data = new OperationsData { Tiers = tiers, Mutators = mutators };
            if (root.Has("score"))
            {
                var s = root.Object("score");
                data.Scoring = new OperationScoring
                {
                    Win = s.Float("win", 5000f), Time = s.Float("time", 3000f), Par = s.Float("par", 1500f),
                    Losses = s.Float("losses", 2000f), LossesAtZero = s.Float("lossesAtZero", 20f), Hq = s.Float("hq", 2000f),
                };
            }
            if (root.Has("weekly"))
            {
                var w = root.Object("weekly");
                data.WeeklyFortressReward = w.Int("fortress", 600);
                data.WeeklyOperationReward = w.Int("operation", 800);
            }
            return data;
        }
    }

    /// <summary>What mutators do to a battle before it starts: the mission, both sides' cards, their vehicles' strength.</summary>
    public static class Mutators
    {
        /// <summary>Cheap vehicles a swarm is made of.</summary>
        public static readonly string[] SwarmUnits = { "armored_car", "rocket_technical", "zu23_technical", "scout_jeep", "light_tank" };

        /// <summary>The mission with the mutators' time limit, reinforcements and waves (every stage too); the original is untouched.</summary>
        public static MissionDef Apply(MissionDef def, IReadOnlyList<MutatorDef> mutators, Catalog catalog)
        {
            if (mutators.Count == 0) return def;
            var copy = def.Harder(1f);
            copy.Reinforcements = def.Reinforcements;
            copy.ReinforceSize = def.ReinforceSize;
            foreach (var m in mutators)
            {
                if (m.TimeScale != 1f && copy.Goal is not (MissionGoal.Survive or MissionGoal.Protect))
                    copy.TimeLimit = (copy.TimeLimit > 0f ? copy.TimeLimit : 1500f) * m.TimeScale;
                if (m.Swarm) copy.ReinforceSize *= 2;
                if (copy.Waves != null)
                {
                    if (m.EnemyAir) copy.Waves.Roster = Aircraft(catalog);
                    else if (m.Swarm) copy.Waves.Roster = SwarmUnits;
                    else if (m.NoAir) copy.Waves.Roster = Filter(copy.Waves.Roster, id => !catalog.Vehicles[id].Flying, catalog);
                }
            }
            if (copy.Stages.Count > 0)
            {
                var stages = new List<StageDef>();
                foreach (var s in copy.Stages)
                    stages.Add(new StageDef
                    {
                        Id = s.Id, Mission = Apply(s.Mission, mutators, catalog), Cp = s.Cp, Events = s.Events, Next = s.Next,
                        Choices = s.Choices, Checkpoint = s.Checkpoint,
                    });
                copy.Stages = stages;
            }
            return copy;
        }

        /// <summary>
        /// Both sides' cards under the mutators. A player's deck that a mutator empties is filled
        /// from <paramref name="fallback"/> (vehicles the player owns) so there is always something to field.
        /// </summary>
        public static void Apply(SideSetup player, SideSetup? enemy, IReadOnlyList<MutatorDef> mutators, Catalog catalog, IReadOnlyList<string> fallback)
        {
            foreach (var m in mutators)
            {
                player.Income *= m.PlayerIncome;
                if (m.NoSupports) player.Supports = Array.Empty<string>();
                if (m.NoRepair) player.Supports = Filter(player.Supports, id => !id.Contains("repair"), null);
                bool Allowed(string id) => catalog.Vehicles.TryGetValue(id, out var d) &&
                                           (m.PlayerMaxCp <= 0 || d.CpCost < m.PlayerMaxCp) &&
                                           (!m.PlayerHeavy || d.Armor == ArmorClass.Heavy) &&
                                           (!m.NoAir || !d.Flying);
                if (m.PlayerMaxCp > 0 || m.PlayerHeavy || m.NoAir)
                {
                    var kept = Filter(player.Vehicles, Allowed, catalog);
                    if (kept.Count < 4)
                    {
                        var more = new List<string>(kept);
                        foreach (var id in fallback)
                            if (more.Count < 8 && !more.Contains(id) && Allowed(id)) more.Add(id);
                        kept = more;
                    }
                    player.Vehicles = kept;
                }
                if (enemy == null) continue;
                enemy.StartCp *= m.EnemyCp;
                enemy.Income *= m.EnemyIncome;
                if (m.EnemyAir) enemy.Vehicles = Aircraft(catalog);
                if (m.NoAir) enemy.Vehicles = Filter(enemy.Vehicles, id => catalog.Vehicles.TryGetValue(id, out var d) && !d.Flying, catalog);
                if (m.Swarm)
                {
                    var list = new List<string>(enemy.Vehicles);
                    foreach (var id in SwarmUnits)
                        if (!list.Contains(id) && catalog.Vehicles.ContainsKey(id)) list.Add(id);
                    enemy.Vehicles = list;
                }
            }
        }

        /// <summary>Prompt 16: what the mutators do at sea (the sight over the water, the flagship's fleet).</summary>
        public static void ApplySea(Bosses.NavalRules rules, IReadOnlyList<MutatorDef> mutators)
        {
            foreach (var m in mutators)
            {
                rules.SeaSight *= m.SeaSight;
                rules.ExtraEscorts += m.ExtraEscorts;
                rules.ExtraRaiders += m.ExtraRaiders;
            }
        }

        /// <summary>What the mutators do to one side's vehicles as they enter: health and damage, per def.</summary>
        public static Func<VehicleDef, (float hp, float damage)>? Strength(IReadOnlyList<MutatorDef> mutators, int team)
        {
            var hp = 1f;
            var damage = 1f;
            var towerHp = 1f;
            var towerDamage = 1f;
            foreach (var m in mutators)
            {
                hp *= m.BothHp;
                damage *= m.BothDamage;
                if (team != 1) continue;
                hp *= m.EnemyHp;
                towerHp *= m.TowerHp;
                towerDamage *= m.TowerDamage;
            }
            if (hp == 1f && damage == 1f && towerHp == 1f && towerDamage == 1f) return null;
            return def => def.Static && def.Fort != null ? (hp * towerHp, damage * towerDamage) : (hp, damage);
        }

        /// <summary>The aircraft an all-air enemy fields: every flying card that is not a boss or an elite.</summary>
        public static IReadOnlyList<string> Aircraft(Catalog catalog)
        {
            var list = new List<string>();
            foreach (var d in catalog.Vehicles.Values)
                if (d.Flying && !d.Boss && !d.Elite && d.CpCost > 0) list.Add(d.Id);
            list.Sort(StringComparer.Ordinal);
            return list;
        }

        private static IReadOnlyList<string> Filter(IReadOnlyList<string> ids, Func<string, bool> keep, Catalog? catalog)
        {
            var list = new List<string>();
            foreach (var id in ids)
                if (keep(id)) list.Add(id);
            return list;
        }
    }
}
