using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 C1-C2 (DECISIONS 25C): the balance sheet's bosses ("Boss đề xuất"). Only the twelve main bosses have a
    /// super weapon (a mini boss has its ordinary weapons only); each main boss's is the prompt 18 big attack with the
    /// sheet's rounds, damage, blast, cycle, warning and counter, its words in both languages and a warning sound of its
    /// own. Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class Prompt25BossTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        [Test]
        public void NoMiniBossHasASuperWeapon()
        {
            var catalog = C;
            var minis = catalog.Vehicles.Values.Where(v => v.Boss && v.Rank == BossRank.Mini).ToList();
            Assert.AreEqual(21, minis.Count, "the sheet's 21 mini bosses");
            foreach (var m in minis)
            {
                Assert.IsNull(m.BigAttack, m.Id + ": a mini boss has no super weapon");
                Assert.IsNull(m.Duel?.BigAttack, m.Id + ": nor in a duel");
                Assert.Greater(m.Mounts.Count(w => w.Weapon.Damage > 0f), 0, m.Id + ": it keeps its ordinary weapons");
            }
            // Nothing left over: every big attack in the data is a main boss's.
            var named = catalog.Vehicles.Values.Where(v => v.BigAttack != null).Select(v => v.BigAttack.Id).ToList();
            CollectionAssert.AreEquivalent(named, catalog.BigAttacks.Keys, "every big attack is one main boss's super weapon");
        }

        /// <summary>A main boss's super weapon as the sheet gives it: the first strike's shape, rounds, damage and blast, the cycle and warning, and how it is stopped.</summary>
        private sealed class Super
        {
            public string Attack;
            public BigShape Shape;
            public int Rounds;
            public float Damage, Radius, Cooldown, Warn;
            public Action<VehicleDef, BigAttackDef> Counter;
        }

        private static void CarriedBy(BigAttackDef big, params string[] parts) =>
            CollectionAssert.AreEquivalent(parts, big.Strikes.SelectMany(s => s.Parts).Distinct(), big.Id + ": carried by " + string.Join(", ", parts) + " (break them to stop it)");

        private static readonly Dictionary<string, Super> Sheet = new()
        {
            // "Loạt pháo chính dồn: 6 × 400 · nổ lan 8 m · mỗi 50 s · vạch 6 vòng tròn trước 3,5 s"
            ["behemoth"] = new Super { Attack = "behemoth_barrage", Shape = BigShape.Circle, Rounds = 6, Damage = 600, Radius = 8.5f, Cooldown = 45, Warn = 3.5f,
                Counter = (v, b) => { CarriedBy(b, "main_gun"); Assert.IsTrue(b.Strikes[0].Rings, "six rings drawn at the warning"); } },
            // "Loạt pháo 203 mm: 4 × 700 · nổ lan 8 m · mỗi 55 s · cảnh báo 4 s"
            ["mobile_fortress"] = new Super { Attack = "fortress_203_barrage", Shape = BigShape.Circle, Rounds = 4, Damage = 900, Radius = 10, Cooldown = 50, Warn = 4,
                Counter = (v, b) => { CarriedBy(b, "howitzer", "howitzer_2"); Assert.AreEqual(2, b.Strikes[0].PerPart, "each howitzer its two shells"); } },
            // "Bom trượt hạng nặng: 1 quả × 1.600 · nổ lan 16 m · mỗi 60 s · bom bay chậm 3 s, bắn hạ được"
            ["drone_mothership"] = new Super { Attack = "carrier_heavy_bomb", Shape = BigShape.Missile, Rounds = 1, Damage = 1600, Radius = 16, Cooldown = 45, Warn = 3.5f,
                Counter = (v, b) => { CarriedBy(b, "bomb_bay"); Assert.Greater(b.Strikes[0].Hp, 0f, "it can be shot down"); Assert.AreEqual(3f, b.Strikes[0].Flight, 1e-3f, "3 s gliding"); } },
            // "Tên lửa Tận thế: 1 × 2.500 · nổ lan 18 m · mỗi 90 s · đồng hồ bay 6 s · PAC-3 và Vòm Sắt bắn hạ được"
            ["nuke_train"] = new Super { Attack = "doomsday_missile", Shape = BigShape.Missile, Rounds = 1, Damage = 3500, Radius = 18, Cooldown = 50, Warn = 4,
                Counter = (v, b) => { CarriedBy(b, "erector"); Assert.Greater(b.Strikes[0].Hp, 0f, "PAC-3 and Iron Dome shoot it down"); Assert.AreEqual(6f, b.Strikes[0].Flight, 1e-3f, "a 6 s flight clock"); } },
            // "Mưa thanh tungsten: 7 × 1.800 · nổ lan 7 m · mỗi 60 s (pha 3: 9 thanh, mỗi 50 s) · cảnh báo 4 s · khói và APS không chặn, khiên hấp thụ một phần"
            ["silver_bug"] = new Super { Attack = "bug_rod_rain", Shape = BigShape.Rods, Rounds = 7, Damage = 1800, Radius = 7, Cooldown = 45, Warn = 4,
                Counter = (v, b) =>
                {
                    CarriedBy(b, "uplink");
                    Assert.AreEqual(2, b.LatePhase, "phase 3");
                    Assert.AreEqual(9, b.LateCount, "nine rods");
                    Assert.AreEqual(45f, b.LateCooldown, 1e-3f, "every 45 s");
                    Assert.AreEqual(9, b.CountIn(b.Strikes[0], 2));
                    Assert.AreEqual(7, b.CountIn(b.Strikes[0], 1));
                } },
            // "Pháo cối 420 mm: 1 quả × 2.000 · nổ lan 14 m · mỗi 60 s · cảnh báo vòng đỏ 4 s · Máy phát khiên hấp thụ được; phá khẩu cối thì mất đòn"
            ["fortress_bastion"] = new Super { Attack = "bastion_420_shell", Shape = BigShape.Circle, Rounds = 1, Damage = 2000, Radius = 10, Cooldown = 45, Warn = 4,
                Counter = (v, b) => CarriedBy(b, "mortar") },
            // "Rải bom thảm: 16 × 350 · nổ lan 7 m · dải 80 × 12 m · mỗi 70 s · cảnh báo 4 s"
            ["command_airship"] = new Super { Attack = "airship_carpet", Shape = BigShape.Strip, Rounds = 16, Damage = 400, Radius = 7, Cooldown = 50, Warn = 4,
                Counter = (v, b) => { CarriedBy(b, "bomb_bay"); Assert.AreEqual(80f, b.Strikes[0].Length, 1e-3f); Assert.AreEqual(12f, b.Strikes[0].Width, 1e-3f); } },
            // "Loạt pháo chính 9 phát 460 mm: 9 × 950 · nổ lan 13 m · rải theo dải 60 × 12 m · mỗi 70 s · cảnh báo 4 s"
            ["leviathan"] = new Super { Attack = "leviathan_volley", Shape = BigShape.Strip, Rounds = 9, Damage = 950, Radius = 12, Cooldown = 50, Warn = 4,
                Counter = (v, b) =>
                {
                    CarriedBy(b, "turret_fore", "turret_super", "turret_aft");
                    Assert.AreEqual(60f, b.Strikes[0].Length, 1e-3f);
                    Assert.AreEqual(12f, b.Strikes[0].Width, 1e-3f);
                } },
            // "Xả xưởng: 8 × 300 · nổ lan 6 m + thả 6 xe · mỗi 75 s · cảnh báo cửa xưởng mở 4 s"
            ["moloch"] = new Super { Attack = "moloch_factory_dump", Shape = BigShape.Drop, Rounds = 6, Damage = 0, Radius = 0, Cooldown = 50, Warn = 4,
                Counter = (v, b) =>
                {
                    CarriedBy(b, "door_l", "door_r");
                    var shells = b.Strikes.Single(s => s.Shape == BigShape.Circle);
                    Assert.AreEqual(8, shells.FullCount);
                    Assert.AreEqual(350f, shells.Damage, 1e-3f);
                    Assert.AreEqual(6f, shells.Radius, 1e-3f);
                } },
            // "Đổ bộ ồ ạt: 8 khoang × 500 · nổ lan 6 m + thả xe · mỗi 70 s · cảnh báo 4 s"
            ["daedalus"] = new Super { Attack = "daedalus_mass_drop", Shape = BigShape.Circle, Rounds = 8, Damage = 600, Radius = 6, Cooldown = 50, Warn = 4,
                Counter = (v, b) => { CarriedBy(b, "pod_bay_1", "pod_bay_2", "pod_bay_3"); Assert.Greater(b.Strikes[0].Seats, 0, "each pod lands a vehicle"); } },
            // "Quét gầu: cung 120° × 25 m, 1.200 · mỗi 60 s · cảnh báo 4 s"
            ["kronos"] = new Super { Attack = "kronos_bucket_sweep", Shape = BigShape.Arc, Rounds = 1, Damage = 2500, Radius = 25, Cooldown = 45, Warn = 4,
                Counter = (v, b) => { CarriedBy(b, "boom"); Assert.AreEqual(120f, b.Strikes[0].Width, 1e-3f, "a 120° arc"); } },
            // "Loạt tên lửa từ dưới nước: 6 × 600 · nổ lan 9 m · mỗi 75 s · cảnh báo 4 s + đồng hồ bay"
            ["typhon"] = new Super { Attack = "typhon_underwater_launch", Shape = BigShape.Missile, Rounds = 6, Damage = 700, Radius = 9, Cooldown = 50, Warn = 4,
                Counter = (v, b) => { CarriedBy(b, "doors_l", "doors_r"); Assert.Greater(b.Strikes[0].Hp, 0f, "they can be shot down"); } },
        };

        [Test]
        public void EveryMainBossHasTheSheetsSuperWeaponItsCycleWarningAndCounter()
        {
            var catalog = C;
            var mains = catalog.Vehicles.Values.Where(v => v.Boss && v.Rank == BossRank.Main).Select(v => v.Id).ToList();
            CollectionAssert.AreEquivalent(Sheet.Keys, mains, "the twelve main bosses, each with its super weapon");
            foreach (var (id, want) in Sheet)
            {
                var v = catalog.Vehicle(id);
                var big = v.BigAttack;
                Assert.IsNotNull(big, id + " has a super weapon");
                Assert.AreEqual(want.Attack, big.Id, id);
                Assert.AreEqual(want.Cooldown, big.Cooldown, 1e-3f, id + ": its cycle");
                Assert.AreEqual(want.Warn, big.Warn, 1e-3f, id + ": its warning");
                var s = big.Strikes[0];
                Assert.AreEqual(want.Shape, s.Shape, id + ": its shape");
                Assert.AreEqual(want.Rounds, s.Shape == BigShape.Drop ? s.PerPart * s.Parts.Count : s.FullCount, id + ": its rounds");
                if (want.Damage > 0f) Assert.AreEqual(want.Damage, s.Damage, 1e-3f, id + ": its damage");
                if (want.Radius > 0f) Assert.AreEqual(want.Radius, s.Radius, 1e-3f, id + ": its blast (or its sweep's reach)");
                want.Counter(v, big);
                // Its words and its warning sound.
                foreach (var key in new[] { big.NameKey, big.RadioKey, big.CancelledKey, big.GuideKey("how"), big.GuideKey("dodge"), big.GuideKey("stop") })
                    Assert.IsTrue(Strings.Has(key), $"{id}: text '{key}'");
                Assert.IsTrue(AudioDirector.SuperCues.ContainsKey(big.Id), id + ": its own warning sound");
            }
        }

        [Test]
        public void EverySuperWeaponSoundsItsOwnWarning()
        {
            var cues = AudioDirector.SuperCues;
            Assert.AreEqual(12, cues.Count);
            var patterns = cues.Values.Select(c => (Mathf(c.Pitch), c.Pulses, Mathf(c.Sweep * 100f), Mathf(c.Square * 10f))).ToList();
            Assert.AreEqual(patterns.Count, patterns.Distinct().Count(), "no two alike in pitch, rhythm, sweep and timbre");
            Assert.AreEqual(cues.Count, cues.Values.Select(c => c.Seed).Distinct().Count(), "each its own noise");
            foreach (var id in cues.Keys) Assert.IsTrue(C.BigAttacks.ContainsKey(id), id + " is a super weapon in the data");
        }

        private static int Mathf(float x) => (int)Math.Round(x);

        /// <summary>C2: the Gungnir's 80 cm gun and the Kronos's bucket wheel are weapons (the design document's tables and the Guide list them), fired by the boss system.</summary>
        [Test]
        public void TheGungnirsGunAndTheKronossBucketWheelAreWeapons()
        {
            var catalog = C;
            var gungnir = catalog.Vehicle("rail_supergun");
            var gun = gungnir.Weapon;
            Assert.AreEqual("supergun_800", gun.Id, "the 80 cm gun is its main weapon");
            Assert.IsTrue(gun.Laid, "laid by its shot: the combat system never fires it");
            // "1 × 900 mỗi 25 s, nổ lan 12 m", and its shot fires with those numbers.
            Assert.AreEqual(900f, gun.Damage, 1e-3f);
            Assert.AreEqual(25f, gun.Cooldown, 1e-3f);
            Assert.AreEqual(12f, gun.SplashRadius, 1e-3f);
            Assert.AreEqual(gun.Damage, gungnir.Bombard.Damage, 1e-3f);
            Assert.AreEqual(gun.SplashRadius, gungnir.Bombard.Radius, 1e-3f);
            Assert.AreEqual(gun.Cooldown, gungnir.Bombard.Every, 1e-3f);
            var kronos = catalog.Vehicle("kronos");
            var index = -1;
            for (var i = 0; i < kronos.Mounts.Count; i++)
                if (kronos.Mounts[i].Weapon.Id == "bucket_wheel") index = i;
            Assert.GreaterOrEqual(index, 0, "the bucket wheel is one of its weapons");
            var wheel = kronos.Mounts[index].Weapon;
            Assert.IsTrue(wheel.Laid, "the crusher is it: the combat system never fires it");
            CollectionAssert.Contains(kronos.Parts[kronos.PartIndex("bucket_wheel")].Mounts, index, "on its wheel: broken, the crushing stops");
            Assert.AreEqual(wheel.Damage / wheel.Cooldown, kronos.Crush.Dps, 1e-3f, "the crusher's damage a second is the weapon's");
            Assert.AreEqual(wheel.Range, kronos.Crush.Reach, 1e-3f);
            Assert.Greater(MachineBrigade.Sim.Combat.FirePower.Sustained(gun, gungnir), 0f, "the tables give it a damage a second");
            Assert.Greater(MachineBrigade.Sim.Combat.FirePower.Sustained(wheel, kronos), 0f);
        }

        [Test]
        public void TheBossesTakeTheSheetsHealthBeforeTheCampaignsScale()
        {
            // Prompt 26 A.1-A.3 (DECISIONS 26AB): the prompt's table by chapter (main 22,000 at chapter 1, 35,000 at 3, 63,000 at 6, 100,000
            // at 9, 150,000 at 12; mini 9,000 / 14,000 / 25,000 / 38,000 / 57,000; straight lines between), over the bosses' toughness
            // (0.85) and a mini boss's share (0.55), to the nearest 50. Nothing scales it by the player's arsenal.
            var catalog = C;
            foreach (var (id, shown) in new Dictionary<string, float>
                     {
                         ["fortress_bastion"] = 22000, ["behemoth"] = 28500, ["mobile_fortress"] = 35000, ["leviathan"] = 44350, ["moloch"] = 63000,
                         ["kronos"] = 87650, ["typhon"] = 100000, ["command_airship"] = 116650, ["daedalus"] = 133350, ["silver_bug"] = 150000,
                         ["bastion_mk0"] = 9000, ["behemoth_inferno"] = 11500, ["scylla"] = 17650, ["rail_supergun"] = 50650,
                     })
                Assert.AreEqual(shown, catalog.Vehicle(id).MaxHp, 60f, id);
            Assert.AreEqual(catalog.Vehicle("silver_bug").MaxHp, catalog.Vehicle("hyperion").MaxHp, 1e-3f, "chapter 12: Icarus and Hyperion");
            Assert.AreEqual(catalog.Vehicles.Values.Where(v => v.Boss).Max(v => v.MaxHp), catalog.Vehicle("silver_bug").MaxHp, 1e-3f, "the last chapter's bosses have the most");
        }
    }
}
