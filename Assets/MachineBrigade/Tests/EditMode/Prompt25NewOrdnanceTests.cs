using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 F2 batch C (DECISIONS 25F2-C): the balance sheet's new ordnance ("Tên lửa & bom mới") and support
    /// cards ("Thẻ hỗ trợ mới"), one row each. Written under the owner's rule of 30/09 (no test runs until the test
    /// phase): not run yet.
    /// </summary>
    public class Prompt25NewOrdnanceTests
    {
        /// <summary>One new weapon: its own numbers, its family, and the vehicle it is a secondary on (null: not fitted, DECISIONS 25F2-C).</summary>
        public sealed class WeaponRow
        {
            public WeaponRow(string id, string family, string host, int pen, float range, float speed, int clusterCount = 0)
            {
                Id = id;
                Family = family;
                Host = host;
                Pen = pen;
                Range = range;
                Speed = speed;
                ClusterCount = clusterCount;
            }

            public string Id, Family, Host;
            public int Pen, ClusterCount;
            public float Range, Speed;

            public override string ToString() => Id;
        }

        public static readonly WeaponRow[] Weapons =
        {
            new WeaponRow("cluster_at_bomb", "cbu_97_sfw", "glide_bomber", 4, 30, 35, clusterCount: 10),
            new WeaponRow("bunker_buster_bomb", "gbu_28", "glide_bomber", 4, 30, 35),
            new WeaponRow("thermobaric_bomb", "odab_500", "glide_bomber", 3, 28, 35),
            new WeaponRow("anti_radar_missile", "agm_88_harm", "interceptor_jet", 3, 90, 45),
            new WeaponRow("apkws_rocket", "apkws", "attack_helicopter", 2, 40, 45),
            new WeaponRow("coyote_interceptor", "coyote_block_2", "interceptor_drone_vehicle", 2, 45, 40),
            new WeaponRow("smart_at_shell", "smart_155_bonus", "wheeled_howitzer", 4, 90, 45, clusterCount: 2),
            new WeaponRow("fpv_swarm_mini", "switchblade_300", "fibre_fpv_carrier", 3, 50, 30),
            new WeaponRow("anti_ship_missile", "nsm_oniks", null, 4, 140, 30),
        };

        /// <summary>One new support card: its kind and the numbers that matter for it.</summary>
        public sealed class SupportRow
        {
            public SupportRow(string id, SupportKind kind, int cp, float cooldown, float radius, int count, float damage, int price, bool dronesOnly = false)
            {
                Id = id;
                Kind = kind;
                Cp = cp;
                Cooldown = cooldown;
                Radius = radius;
                Count = count;
                Damage = damage;
                Price = price;
                DronesOnly = dronesOnly;
            }

            public string Id;
            public SupportKind Kind;
            public int Cp, Price;
            public float Cooldown, Radius, Damage;
            public int Count;
            public bool DronesOnly;

            public override string ToString() => Id;
        }

        public static readonly SupportRow[] Supports =
        {
            new SupportRow("glide_bomb_strike", SupportKind.CruiseMissile, 8, 90, 10, 2, 420, 2500),
            new SupportRow("guided_shell_strike", SupportKind.Barrage, 4, 45, 1.5f, 1, 360, 1500),
            new SupportRow("cluster_at_strike", SupportKind.Homing, 9, 90, 25, 10, 160, 2500),
            new SupportRow("uav_loiter_strike_support", SupportKind.Escort, 6, 75, 40, 1, 0, 2500),
            new SupportRow("ammo_resupply", SupportKind.Resupply, 3, 60, 15, 1, 0, 1500),
            new SupportRow("jam_storm", SupportKind.JamStorm, 5, 90, 30, 1, 0, 1500),
            new SupportRow("illum_flare_strike", SupportKind.Scan, 1, 30, 35, 1, 0, 1500),
            new SupportRow("decoy_paradrop", SupportKind.Reinforce, 2, 45, 6, 3, 0, 1500),
            new SupportRow("instant_counter_battery", SupportKind.CounterBattery, 6, 75, 60, 4, 320, 2500),
            new SupportRow("drone_intercept_strike", SupportKind.Homing, 3, 40, 40, 6, 120, 1500, dronesOnly: true),
            new SupportRow("chaff_strike", SupportKind.Smoke, 2, 45, 30, 1, 0, 1500),
        };

        /// <summary>The sheet's duplicates of batch A / 25G content: no new weapon, just the tracker pointed at the existing one.</summary>
        [TestCase("glide_fab500")]
        [TestCase("r37m")]
        [TestCase("spike_nlos")]
        public void DuplicateOrdnanceAlreadyExists(string id)
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Weapons.ContainsKey(id), id);
        }

        /// <summary>tl08: the guided-shell secondRounds 25G built, on the mobile howitzer's own gun.</summary>
        [Test]
        public void GuidedShellRoundExists()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Weapons.ContainsKey("howitzer_guided"));
        }

        /// <summary>tl12: the sheet's stealth cruise missile updated the existing support card's own numbers.</summary>
        [Test]
        public void CruiseMissileUpdatedInPlace()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.TryGetSupport("cruise_missile", out var support));
            Assert.AreEqual(450f, support.Damage);
            Assert.AreEqual(9f, support.BlastRadius);
            Assert.AreEqual(3, support.Penetration);
        }

        [TestCaseSource(nameof(Weapons))]
        public void WeaponMatchesTheSheetAndItsHost(WeaponRow row)
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Weapons.TryGetValue(row.Id, out var weapon), row.Id);
            Assert.AreEqual(row.Family, weapon.WeaponFamily, "weaponFamily");
            Assert.AreEqual(row.Pen, weapon.Penetration, "pen");
            Assert.AreEqual(row.Range, weapon.Range, "range");
            Assert.AreEqual(row.Speed, weapon.ProjectileSpeed, "projectileSpeed");
            Assert.Greater(weapon.RoundLength, 0f, "roundLength (prompt 25 B3)");
            if (row.ClusterCount > 0)
            {
                Assert.IsNotNull(weapon.Cluster, "a self-seeking submunition round");
                Assert.AreEqual(row.ClusterCount, weapon.Cluster.Count);
            }
            if (row.Host == null)
            {
                // tl14: no host unit exists yet (DECISIONS 25F2-C); catalogued only.
                return;
            }
            Assert.IsTrue(catalog.Vehicles.TryGetValue(row.Host, out var host), row.Host);
            Assert.IsTrue(host.Mounts.Any(m => m.Weapon.Id == row.Id), $"{row.Host} carries {row.Id} as a secondary");
        }

        [TestCaseSource(nameof(Supports))]
        public void SupportMatchesTheSheetTextsAndShop(SupportRow row)
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.TryGetSupport(row.Id, out var support), row.Id);
            Assert.AreEqual(row.Kind, support.Kind, "kind");
            Assert.AreEqual(row.Cp, support.CpCost, "cp");
            Assert.AreEqual(row.Cooldown, support.Cooldown, "cooldown");
            Assert.AreEqual(row.Radius, support.Radius, "radius");
            Assert.AreEqual(row.Count, support.Count, "count");
            if (row.Damage > 0f) Assert.AreEqual(row.Damage, support.Damage, "damage");
            if (row.Kind == SupportKind.Homing) Assert.AreEqual(row.DronesOnly, support.DronesOnly, "dronesOnly");
            foreach (var key in new[] { "support.", "guide." }) Assert.IsTrue(Strings.Has(key + row.Id), key + row.Id);
            foreach (var vi in new[] { false, true })
            {
                Strings.Vietnamese = vi;
                Assert.LessOrEqual(Strings.Short(row.Id).Length, 24, "a short name that fits one line");
                foreach (var other in Supports)
                    if (other.Id != row.Id) Assert.AreNotEqual(Strings.Card(other.Id), Strings.Card(row.Id), "a name of its own");
            }
            Strings.Vietnamese = false;
            Assert.IsTrue(Progression.IsNewContent(row.Id) && Progression.Price(row.Id, catalog) == row.Price, "sold in the shop at its own price");
            Assert.IsNull(Progression.UnlockMission(row.Id), "the shop is its one source");
            Assert.IsTrue(Progression.EnemyMayUse(row.Id), "the enemy may field it");
            CollectionAssert.Contains(MatchSettings.AllSupports, row.Id);
        }

        /// <summary>ht04's loaned drone and ht08's decoy tank: spawned-only vehicles, not sold on their own.</summary>
        [TestCase("uav_loiter_strike")]
        [TestCase("decoy_tank")]
        public void SpawnedVehicleExistsAndIsNotSoldSeparately(string id)
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Vehicles.ContainsKey(id), id);
            Assert.IsFalse(Progression.IsNewContent(id), "spawned by its support card, not a card of its own");
            Assert.IsTrue(Strings.Has("unit." + id));
        }
    }
}
