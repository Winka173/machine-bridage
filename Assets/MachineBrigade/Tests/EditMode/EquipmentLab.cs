using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The equipment lab (prompt 8): controlled measurements behind the fit matrix, the value
    /// table, the proc coefficients, the elite frame and the risky combinations.
    /// <list type="bullet">
    /// <item>A duel: shooters of one card (team 0, with the equipment under test) stand and fire at a
    /// row of targets that move across their front and hit back for nothing; a target that falls is
    /// replaced 1.5 s later. What the shooters deal (their rounds, splash, burns, bounces, drones and
    /// called rounds) is summed through <see cref="DamageSystem.DamageLog"/>.</item>
    /// <item>A soak: one vehicle (with the equipment) stands under the fire of a fixed group; it is
    /// replaced when it falls, and its mean time alive per life is what the equipment buys.</item>
    /// </list>
    /// Every vehicle is in sight of everyone (<see cref="SimWorld.RevealAll"/>), so the artillery and
    /// the aircraft need no spotters. Results go to the directory in MB_LAB_OUT.
    /// </summary>
    internal static class Lab
    {
        public const float Step = 0.05f;

        private static Catalog _catalog;
        public static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        public static void Reload() => _catalog = GameContent.LoadCatalog();

        public static SimWorld Field(int seed, float size = 260f)
        {
            var world = new SimWorld(Catalog, new MapDefinition("lab", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed) { RevealAll = true };
            return world;
        }

        /// <summary>A boost that leaves a vehicle as it is but makes its rounds harmless (a target that shoots back for nothing).</summary>
        public static readonly VehicleBoost Harmless = new(1f, 0f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f);

        public static VehicleBoost Traits(params GearTrait[] traits) => new(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, null, traits);

        public static VehicleBoost Stats(params (StatId stat, float value)[] lines)
        {
            var stats = new float[(int)StatId.Count];
            foreach (var (stat, value) in lines) stats[(int)stat] = value;
            return With(new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, stats), stats);
        }

        /// <summary>A boost whose folded stats (damage, fire rate, health, speed, damage taken, regeneration) are in the multipliers too, as the game builds it.</summary>
        public static VehicleBoost With(VehicleBoost b, float[] stats, GearTrait[] traits = null, SpecialModule module = SpecialModule.None, float power = 0f, float power2 = 0f) =>
            new(1f + stats[(int)StatId.Health], 1f + stats[(int)StatId.Damage], 1f + stats[(int)StatId.FireRate], 1f + stats[(int)StatId.Speed],
                1f - stats[(int)StatId.DamageTaken], stats[(int)StatId.Regen], module, power, stats, traits ?? b.Traits, power2);

        public static VehicleBoost Module(SpecialModule module, float power, float power2 = 0f)
        {
            var b = new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, module, power, null, null, power2);
            return b;
        }

        // ------------------------------------------------------------------ duels

        public sealed class Duel
        {
            public string Shooter;
            public int Count = 2;
            public Func<VehicleDef, VehicleBoost> Boost;
            public string[] Targets = { "main_battle_tank", "ifv", "armored_car" };
            public float Distance = -1f;
            public float Seconds = 180f;
            public bool Moving = true;
            public float Spacing = 9f;

            /// <summary>Only the shooters' main weapon fires (a line that acts on the main weapon measured on it alone).</summary>
            public bool MainOnly;

            /// <summary>Seconds before a destroyed target is replaced.</summary>
            public float Respawn = 0.5f;

            /// <summary>Called every step (a test's own hook: a mark, a smoke screen).</summary>
            public Action<SimWorld, List<Vehicle>, List<Vehicle>> Each;

            public Duel With(Func<VehicleDef, VehicleBoost> boost) => new()
            {
                Shooter = Shooter, Count = Count, Boost = boost, Targets = Targets, Distance = Distance, Seconds = Seconds, Moving = Moving,
                Spacing = Spacing, MainOnly = MainOnly, Respawn = Respawn, Each = Each,
            };
        }

        public sealed class DuelResult
        {
            public float Dealt, Seconds, Kills, Shots;
            public float Dps => Seconds > 0f ? Dealt / Seconds : 0f;
        }

        /// <summary>A sensible firing distance: seven tenths of the main weapon's reach, clear of its minimum range.</summary>
        public static float DistanceFor(VehicleDef def)
        {
            var w = def.Weapon;
            if (def.Flying) return 50f;
            return MathF.Max(w.MinRange + 8f, MathF.Min(w.Range * 0.7f, w.MinRange > 0f ? 70f : 60f));
        }

        public static DuelResult Run(Duel d, int seed)
        {
            var world = Field(seed);
            world.SetBoosts(0, d.Boost);
            world.SetBoosts(1, _ => Harmless);
            var def = Catalog.Vehicle(d.Shooter);
            var distance = d.Distance > 0f ? d.Distance : DistanceFor(def);
            var shooters = new List<Vehicle>();
            for (var i = 0; i < d.Count; i++)
            {
                var s = world.SpawnVehicle(d.Shooter, 0, new Vector2((i - (d.Count - 1) * 0.5f) * 9f, -distance * 0.5f), 0f);
                // Main weapon only: the other mounts are left with an empty magazine that never refills.
                if (d.MainOnly)
                    for (var m = 1; m < s.Weapons.Length; m++) s.Weapons[m].Ammo = 0;
                shooters.Add(s);
            }
            var slots = new List<Vector2>();
            for (var i = 0; i < d.Targets.Length; i++) slots.Add(new Vector2((i - (d.Targets.Length - 1) * 0.5f) * d.Spacing, distance * 0.5f));
            var targets = new List<Vehicle>();
            for (var i = 0; i < d.Targets.Length; i++) targets.Add(world.SpawnVehicle(d.Targets[i], 1, slots[i], MathF.PI));
            var respawnAt = new double[targets.Count];
            // Each target drives between spots round its own, on its own clock (seeded), so salvos and
            // the targets' moves never fall into one rhythm.
            var rng = new System.Random(seed * 7919 + 13);
            var nextMove = new double[targets.Count];
            for (var i = 0; i < nextMove.Length; i++) nextMove[i] = rng.NextDouble() * 4.0;
            var result = new DuelResult();
            DamageSystem.DamageLog = (attacker, victim, amount, kind, weapon) =>
            {
                if (attacker != null && attacker.Team == 0 && victim.Team == 1) result.Dealt += amount;
            };
            try
            {
                foreach (var s in shooters)
                    if (s.Flying) world.Submit(new Command(CommandType.AttackMove, 0, new[] { s.Id }, new Vector2(0f, distance * 0.5f)));
                var steps = (int)(d.Seconds / Step);
                for (var k = 0; k < steps; k++)
                {
                    if (d.Moving)
                        for (var i = 0; i < targets.Count; i++)
                        {
                            if (!targets[i].IsAlive || world.Time < nextMove[i]) continue;
                            nextMove[i] = world.Time + 3.0 + rng.NextDouble() * 4.0;
                            var spot = slots[i] + new Vector2((float)(rng.NextDouble() * 2.0 - 1.0) * 14f, (float)(rng.NextDouble() * 2.0 - 1.0) * 6f);
                            world.Submit(new Command(CommandType.Move, 1, new[] { targets[i].Id }, spot));
                        }
                    d.Each?.Invoke(world, shooters, targets);
                    world.Step(Step);
                    foreach (var e in world.Events)
                        if (e.Kind == Sim.Events.SimEventKind.WeaponFired && e.Team == 0) result.Shots++;
                    world.ClearEvents();
                    for (var i = 0; i < targets.Count; i++)
                    {
                        if (targets[i].IsAlive) continue;
                        if (respawnAt[i] <= 0.0)
                        {
                            respawnAt[i] = world.Time + d.Respawn;
                            result.Kills++;
                        }
                        else if (world.Time >= respawnAt[i])
                        {
                            targets[i] = world.SpawnVehicle(d.Targets[i], 1, slots[i], MathF.PI);
                            respawnAt[i] = 0.0;
                        }
                    }
                }
                result.Seconds = d.Seconds;
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            return result;
        }

        /// <summary>Mean damage a second over the seeds.</summary>
        public static float Dps(Duel d, int seeds = 5)
        {
            var sum = 0f;
            for (var s = 1; s <= seeds; s++) sum += Run(d, s * 7 + 1).Dps;
            return sum / seeds;
        }

        /// <summary>What a boost adds to a duel's damage a second, as a share (0.12 = +12 %), over the seeds.</summary>
        public static float Gain(Duel d, Func<VehicleDef, VehicleBoost> boost, int seeds = 5, float? baseline = null)
        {
            var plain = baseline ?? Dps(d.With(null), seeds);
            var with = Dps(d.With(boost), seeds);
            return plain > 0f ? with / plain - 1f : 0f;
        }

        // ------------------------------------------------------------------ soaks

        public sealed class Soak
        {
            public string Target;
            public Func<VehicleDef, VehicleBoost> Boost;
            public string[] Attackers = { "main_battle_tank", "ifv", "armored_car" };
            public float Distance = 26f;
            public float Seconds = 150f;
            public bool Moving;

            /// <summary>Friends of the soaking vehicle standing round it (Guardian Link, Aegis Dome, Wolfpack).</summary>
            public string[] Friends = Array.Empty<string>();

            public Action<SimWorld, Vehicle> Each;
        }

        public sealed class SoakResult
        {
            public float Lives, Alive, Taken;
            public float TimePerLife => Lives > 0f ? Alive / Lives : Alive;
        }

        public static SoakResult Run(Soak s, int seed)
        {
            var world = Field(seed);
            world.SetBoosts(0, s.Boost);
            var result = new SoakResult();
            Vehicle Spawn() => world.SpawnVehicle(s.Target, 0, new Vector2(0f, -s.Distance * 0.5f), 0f);
            var v = Spawn();
            var friends = new List<Vehicle>();
            for (var i = 0; i < s.Friends.Length; i++)
                friends.Add(world.SpawnVehicle(s.Friends[i], 0, new Vector2((i % 2 == 0 ? -1f : 1f) * (5f + 3f * (i / 2)), -s.Distance * 0.5f - 3f), 0f));
            var attackers = new List<Vehicle>();
            for (var i = 0; i < s.Attackers.Length; i++)
                attackers.Add(world.SpawnVehicle(s.Attackers[i], 1, new Vector2((i - (s.Attackers.Length - 1) * 0.5f) * 8f, s.Distance * 0.5f), MathF.PI));
            var born = world.Time;
            DamageSystem.DamageLog = (attacker, victim, amount, kind, weapon) =>
            {
                if (victim == v) result.Taken += amount;
            };
            try
            {
                var steps = (int)(s.Seconds / Step);
                var side = 1f;
                for (var k = 0; k < steps; k++)
                {
                    if (s.Moving && k % (int)(5f / Step) == 0 && v.IsAlive)
                    {
                        side = -side;
                        world.Submit(new Command(CommandType.Move, 0, new[] { v.Id }, new Vector2(10f * side, -s.Distance * 0.5f)));
                    }
                    s.Each?.Invoke(world, v);
                    world.Step(Step);
                    world.ClearEvents();
                    if (!v.IsAlive)
                    {
                        result.Lives++;
                        result.Alive += (float)(world.Time - born);
                        v = Spawn();
                        born = world.Time;
                    }
                    for (var i = 0; i < attackers.Count; i++)
                        if (!attackers[i].IsAlive)
                            attackers[i] = world.SpawnVehicle(s.Attackers[i], 1, new Vector2((i - (s.Attackers.Length - 1) * 0.5f) * 8f, s.Distance * 0.5f), MathF.PI);
                    for (var i = 0; i < friends.Count; i++)
                        if (!friends[i].IsAlive)
                            friends[i] = world.SpawnVehicle(s.Friends[i], 0, new Vector2((i % 2 == 0 ? -1f : 1f) * (5f + 3f * (i / 2)), -s.Distance * 0.5f - 3f), 0f);
                }
                // The life still under way counts as far as it got.
                result.Alive += (float)(world.Time - born);
                if (result.Lives == 0f) result.Lives = 1f;
                else result.Lives += 0.5f;
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            return result;
        }

        public static float TimePerLife(Soak s, int seeds = 3)
        {
            var sum = 0f;
            for (var k = 1; k <= seeds; k++) sum += Run(s, k * 11 + 3).TimePerLife;
            return sum / seeds;
        }

        /// <summary>What a boost adds to a soak's time alive per life, as a share, over the seeds.</summary>
        public static float Toughness(Soak s, Func<VehicleDef, VehicleBoost> boost, int seeds = 3, float? baseline = null)
        {
            var plain = baseline ?? TimePerLife(new Soak { Target = s.Target, Attackers = s.Attackers, Distance = s.Distance, Seconds = s.Seconds, Moving = s.Moving, Friends = s.Friends, Each = s.Each }, seeds);
            var with = TimePerLife(new Soak { Target = s.Target, Attackers = s.Attackers, Distance = s.Distance, Seconds = s.Seconds, Moving = s.Moving, Friends = s.Friends, Boost = boost, Each = s.Each }, seeds);
            return plain > 0f ? with / plain - 1f : 0f;
        }

        // ------------------------------------------------------------------ the catalogue's own numbers

        /// <summary>A card's damage a second against each armour class, from its numbers (every weapon's cycle times the damage table and its armour-only bonuses).</summary>
        public static float[] PaperDps(VehicleDef v)
        {
            var dps = new float[4];
            foreach (var m in v.Mounts)
            {
                var w = m.Weapon;
                if (w.Damage <= 0f) continue;
                var raw = UnitStats.Dps(w);
                foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass)))
                {
                    if (!w.CanTarget(a == ArmorClass.Air)) continue;
                    var bonus = 1f;
                    foreach (var b in w.Bonuses)
                        if (b.Armor == a && b.Class == null && b.StillFor <= 0f && !b.Flank) bonus *= b.Mult;
                    dps[(int)a] += raw * v.DamageScale * Matchup.ClassEffect(Catalog.Damage, w, a) * bonus;
                }
            }
            return dps;
        }

        // ------------------------------------------------------------------ output

        public static string OutDir
        {
            get
            {
                var dir = Environment.GetEnvironmentVariable("MB_LAB_OUT");
                if (string.IsNullOrEmpty(dir)) dir = Path.Combine(Application.temporaryCachePath, "lab");
                Directory.CreateDirectory(dir);
                return dir;
            }
        }

        public static string Tag => Environment.GetEnvironmentVariable("MB_LAB_TAG") ?? "now";

        public static void Write(string name, string text)
        {
            var path = Path.Combine(OutDir, $"{name}_{Tag}.md");
            File.WriteAllText(path, text);
            Debug.Log($"LAB wrote {path}");
        }

        public static void Gate()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("measurement: set MB_BALANCE=1 to run it");
        }

        public static string Pct(float v) => (v >= 0f ? "+" : "") + (v * 100f).ToString("0.0") + "%";
    }

    /// <summary>The lab's measurements (MB_BALANCE=1; results in MB_LAB_OUT, tagged by MB_LAB_TAG).</summary>
    public class EquipmentLabTests
    {
        /// <summary>The weapon groups every proc line is measured on: a card for each, and what it fights.</summary>
        internal static readonly (string group, string shooter, string[] targets)[] Groups =
        {
            ("tank cannon", "main_battle_tank", new[] { "main_battle_tank", "ifv", "light_tank" }),
            ("long gun", "tank_destroyer", new[] { "main_battle_tank", "heavy_tank", "ifv" }),
            ("railgun", "railgun_truck", new[] { "main_battle_tank", "main_battle_tank", "ifv" }),
            ("autocannon", "ifv", new[] { "ifv", "armored_car", "light_tank" }),
            ("machine gun", "scout_jeep", new[] { "armored_car", "scout_jeep", "rocket_technical" }),
            ("flame", "flame_tank", new[] { "ifv", "armored_car", "light_tank" }),
            ("ATGM", "atgm_carrier", new[] { "main_battle_tank", "heavy_tank", "ifv" }),
            ("flak", "aa_vehicle", new[] { "attack_helicopter", "scout_heli", "attack_helicopter" }),
            ("heavy flak", "heavy_aa", new[] { "attack_helicopter", "gunship_heli", "scout_heli" }),
            ("howitzer", "artillery", new[] { "main_battle_tank", "ifv", "armored_car" }),
            ("rocket salvo", "mlrs", new[] { "main_battle_tank", "ifv", "armored_car" }),
            ("heli missiles", "attack_helicopter", new[] { "main_battle_tank", "ifv", "armored_car" }),
            ("jet cannon", "attack_jet", new[] { "main_battle_tank", "ifv", "armored_car" }),
            ("bombs", "heavy_bomber", new[] { "main_battle_tank", "ifv", "armored_car" }),
        };

        [Test, Category("Balance"), Timeout(7200000)]
        public void RosterDpsTable()
        {
            Lab.Gate();
            var catalog = Lab.Catalog;
            var sb = new StringBuilder();
            sb.AppendLine("| Vehicle | id | class | branch | CP | HP | DPS/CP L / H / Air / Str |");
            sb.AppendLine("|---|---|---|---|---|---|---|");
            foreach (var v in catalog.Vehicles.Values.Where(v => v.CpCost > 0 && !v.Static && !v.Boss).OrderBy(v => v.CpCost).ThenBy(v => v.Id))
            {
                var d = Lab.PaperDps(v);
                var cp = (float)v.CpCost;
                sb.AppendLine($"| {Game.Hud.Strings.Card(v.Id)} | {v.Id} | {v.Class} | {v.Branch} | {v.CpCost} | {v.MaxHp:0} | " +
                              $"{d[0] / cp:0.0} / {d[1] / cp:0.0} / {d[2] / cp:0.0} / {d[3] / cp:0.0} |");
            }
            Lab.Write("roster_dps", sb.ToString());
        }

        /// <summary>Every elite against its base card: health, damage a second on paper and in a duel, time alive in a soak, and the ratios.</summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void ElitePower()
        {
            Lab.Gate();
            var catalog = Lab.Catalog;
            var sb = new StringBuilder();
            sb.AppendLine("| Elite | base | HP x | paper DPS x (best class) | duel DPS x | soak time x | power x (duel DPS x soak) | skills |");
            sb.AppendLine("|---|---|---|---|---|---|---|---|");
            foreach (var e in catalog.Vehicles.Values.Where(v => v.Elite && v.EliteOf != null).OrderBy(v => v.Id))
            {
                var b = catalog.Vehicle(e.EliteOf);
                var pe = Lab.PaperDps(e);
                var pb = Lab.PaperDps(b);
                var best = 0;
                for (var i = 1; i < 4; i++) if (pb[i] > pb[best]) best = i;
                var paper = pb[best] > 0f ? pe[best] / pb[best] : 0f;
                var air = e.Class == UnitClass.AntiAir;
                var targets = air ? new[] { "attack_helicopter", "scout_heli", "attack_helicopter" } : new[] { "main_battle_tank", "ifv", "armored_car" };
                var duelE = Lab.Dps(new Lab.Duel { Shooter = e.Id, Count = 1, Targets = targets }, 3);
                var duelB = Lab.Dps(new Lab.Duel { Shooter = b.Id, Count = 1, Targets = targets }, 3);
                var attackers = e.Flying ? new[] { "aa_vehicle", "aa_vehicle", "heavy_aa" } : new[] { "main_battle_tank", "ifv", "armored_car" };
                var soakE = Lab.TimePerLife(new Lab.Soak { Target = e.Id, Attackers = attackers, Seconds = 480f }, 3);
                var soakB = Lab.TimePerLife(new Lab.Soak { Target = b.Id, Attackers = attackers, Seconds = 480f }, 3);
                var dx = duelB > 0f ? duelE / duelB : 0f;
                var sx = soakB > 0f ? soakE / soakB : 0f;
                sb.AppendLine($"| {e.Id} | {b.Id} | {e.MaxHp / b.MaxHp:0.00} | {paper:0.00} ({(ArmorClass)best}) | {dx:0.00} | {sx:0.00} | {dx * sx:0.00} | " +
                              $"{string.Join(", ", e.Skills.Select(s => s.Id))} |");
            }
            Lab.Write("elite_power", sb.ToString());
        }

        /// <summary>Each offensive line at its Legendary numbers on every weapon group: what it adds to the duel's damage a second.</summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void OffensiveLinesByWeapon()
        {
            Lab.Gate();
            var lines = OffensiveLines();
            var sb = new StringBuilder();
            sb.Append("| line |");
            foreach (var g in Groups) sb.Append($" {g.group} |");
            sb.AppendLine(" max/min |");
            sb.Append("|---|");
            foreach (var _ in Groups) sb.Append("---|");
            sb.AppendLine("---|");
            var baselines = new Dictionary<string, float>();
            foreach (var g in Groups)
                baselines[g.group] = Lab.Dps(new Lab.Duel { Shooter = g.shooter, Targets = g.targets }, 3);
            foreach (var (name, boost) in lines)
            {
                sb.Append($"| {name} |");
                var gains = new List<float>();
                foreach (var g in Groups)
                {
                    var gain = Lab.Gain(new Lab.Duel { Shooter = g.shooter, Targets = g.targets }, _ => boost, 3, baselines[g.group]);
                    gains.Add(gain);
                    sb.Append($" {Lab.Pct(gain)} |");
                }
                var positive = gains.Where(x => x > 0.005f).ToList();
                var spread = positive.Count > 1 ? positive.Max() / positive.Min() : 1f;
                sb.AppendLine($" {spread:0.0} |");
            }
            sb.AppendLine();
            sb.AppendLine("Baseline damage a second (two shooters): " + string.Join(", ", Groups.Select(g => $"{g.group} {baselines[g.group]:0}")));
            Lab.Write("offensive_lines", sb.ToString());
        }

        /// <summary>The offensive unique lines and set behaviours at their Legendary numbers.</summary>
        internal static List<(string name, VehicleBoost boost)> OffensiveLines()
        {
            var list = new List<(string, VehicleBoost)>();
            foreach (var t in GearCatalog.Traits)
            {
                if (t.Slot is not (GearSlot.Weapon or GearSlot.Loader)) continue;
                if (t.Id is TraitId.SkywardPintle or TraitId.HotSwap or TraitId.RapidResponse) continue;
                list.Add((t.Key, Lab.Traits(t.At(Rarity.Legendary))));
            }
            list.Add(("laser_designator", Lab.Traits(GearCatalog.Trait(TraitId.LaserDesignator).At(Rarity.Legendary))));
            foreach (var brand in GearCatalog.Brands)
                if (brand.FourPiece.Id is TraitId.SetHeavyRound or TraitId.SetStrafingRun or TraitId.SetDeepStrike or TraitId.SetFirestorm)
                    list.Add(("set " + brand.Id, Lab.Traits(brand.FourPiece)));
            return list;
        }

        /// <summary>Twin Feed at its Legendary numbers on the tank cannon and the railgun (and the other groups), before and after its rework.</summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void TwinFeedByWeapon()
        {
            Lab.Gate();
            var twin = Lab.Traits(GearCatalog.Trait(TraitId.TwinFeed).At(Rarity.Legendary));
            var sb = new StringBuilder();
            sb.AppendLine("| group | shooter | damage a second plain | with Twin Feed | gain |");
            sb.AppendLine("|---|---|---|---|---|");
            foreach (var g in Groups)
            {
                var plain = Lab.Dps(new Lab.Duel { Shooter = g.shooter, Targets = g.targets }, 5);
                var with = Lab.Dps(new Lab.Duel { Shooter = g.shooter, Targets = g.targets, Boost = _ => twin }, 5);
                sb.AppendLine($"| {g.group} | {g.shooter} | {plain:0} | {with:0} | {Lab.Pct(with / plain - 1f)} |");
            }
            Lab.Write("twin_feed", sb.ToString());
        }
    }
}
