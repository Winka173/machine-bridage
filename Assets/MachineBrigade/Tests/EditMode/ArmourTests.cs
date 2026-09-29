using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 15 A-B: armour levels by face, penetration against them, top attacks on the roof, and every unit
    /// and weapon carrying the new fields.
    /// </summary>
    public class ArmourTests
    {
        [Test]
        public void EveryUnitAndWeaponHasTheNewFields()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var v in catalog.Vehicles.Values)
            {
                var a = v.Armour;
                foreach (ArmorFace f in System.Enum.GetValues(typeof(ArmorFace)))
                    Assert.That(a[f], Is.InRange(0, 4), v.Id + " " + f);
                Assert.AreEqual(v.Flying ? TargetKind.Air : v.Armor == ArmorClass.Structure ? TargetKind.Structure : TargetKind.Ground, v.Kind, v.Id);
                // Towers, buildings and aircraft are the same all round, but for an embrasured front.
                if (v.Flying || v.Kind == TargetKind.Structure)
                {
                    Assert.AreEqual(a.Side, a.Rear, v.Id + ": all round");
                    Assert.AreEqual(a.Side, a.Top, v.Id + ": all round");
                    Assert.That(a.Front - a.Side, Is.InRange(0, 1), v.Id + ": at most an embrasured front");
                }
                else Assert.That(a.Front, Is.GreaterThanOrEqualTo(a.Top), v.Id + ": no roof thicker than the front");
                foreach (var part in v.Parts) Assert.That(part.ArmourOn(v), Is.InRange(0, 4), v.Id + " part " + part.Id);
                if (v.Boss) Assert.IsTrue(v.Parts.All(p => p.Armour >= 0), v.Id + ": every part has its own level");
            }
            // Elites: a level more in front than their card (at most 4; an aircraft at most 2).
            foreach (var e in catalog.Vehicles.Values.Where(x => x.Elite && x.EliteOf != null))
            {
                var b = catalog.Vehicle(e.EliteOf);
                var cap = e.Flying ? 2 : 4;
                Assert.AreEqual(System.Math.Min(cap, b.Armour.Front + 1), e.Armour.Front, e.Id + ": +1 front");
            }
            foreach (var w in catalog.Weapons.Values)
            {
                Assert.That(w.Penetration, Is.InRange(0, 4), w.Id);
                if (w.Damage > 0f) Assert.AreNotEqual(WeaponForm.None, w.Form, w.Id + ": a form for its icon");
            }
            // The data states them (the table in DECISIONS 14A), the defaults are only for hand-built weapons.
            var json = UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/balance").text;
            var weapons = json.Substring(json.IndexOf("\"weapons\": [", System.StringComparison.Ordinal));
            weapons = weapons.Substring(0, weapons.IndexOf("\"vehicles\": [", System.StringComparison.Ordinal));
            var entries = weapons.Split(new[] { "{ \"id\":" }, System.StringSplitOptions.None).Skip(1).ToList();
            Assert.AreEqual(catalog.Weapons.Count, entries.Count);
            foreach (var entry in entries) StringAssert.Contains("\"pen\":", entry, entry.Substring(0, System.Math.Min(40, entry.Length)));
        }

        [Test]
        public void PenetrationAgainstArmourFollowsTheTable()
        {
            var table = GameContent.LoadCatalog().Damage;
            Assert.AreEqual(1f, table.Penetration(4, 3), 1e-5f, "a level above: all of it");
            Assert.AreEqual(1f, table.Penetration(4, 0), 1e-5f);
            Assert.AreEqual(0.75f, table.Penetration(3, 3), 1e-5f, "level");
            Assert.AreEqual(0.4f, table.Penetration(2, 3), 1e-5f, "one under");
            Assert.AreEqual(0.15f, table.Penetration(1, 3), 1e-5f, "two under");
            Assert.AreEqual(0.05f, table.Penetration(0, 3), 1e-5f, "three under");
            Assert.AreEqual(0.05f, table.Penetration(0, 4), 1e-5f, "four under");
            Assert.AreEqual((0.75f + 0.4f) / 2f, table.Penetration(2.5f, 3), 1e-5f, "a part level lies between");
            Assert.AreEqual(1.5f, table.Type(DamageType.HighExplosive, TargetKind.Structure), 1e-5f, "high explosive's extra on structures");
            Assert.Greater(table.ThermobaricStructure, 1.5f, "more with the thermobaric tag");
            Assert.AreEqual(0f, table.Type(DamageType.HighExplosive, TargetKind.Air));
        }

        [Test]
        public void FacesTopAttacksAndTheMultiplierInBattle()
        {
            var world = TestWorlds.World();
            // The test tank: level 3 in front, 2 on the sides, 1 behind and on the roof (a battle tank's defaults).
            var tank = world.SpawnVehicle("tank", 1, Vector2.Zero, 0f);
            Assert.AreEqual(new ArmourLevels(3, 2, 1, 1), tank.Armour);
            Assert.AreEqual(ArmorFace.Front, DamageSystem.FaceFrom(tank, new Vector2(0f, 20f)), "heading 0 faces +Y");
            Assert.AreEqual(ArmorFace.Front, DamageSystem.FaceFrom(tank, new Vector2(10f, 20f)), "a little off the nose");
            Assert.AreEqual(ArmorFace.Side, DamageSystem.FaceFrom(tank, new Vector2(20f, 0f)));
            Assert.AreEqual(ArmorFace.Rear, DamageSystem.FaceFrom(tank, new Vector2(0f, -20f)));

            // A 12.7 mm-like round (kinetic, penetration 1) from the front, the side and behind: 0.15, 0.4, 0.75.
            var hmg = new WeaponDef("hmg_test", DamageType.Kinetic, 100f, 1f, 30f, 0f, 200f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Bullet) { Penetration = 1 };
            float Hit(WeaponDef w, Vector2 from)
            {
                tank.Hp = tank.MaxHp;
                return world.Damage.Apply(tank, 100f, w.DamageType, new HitInfo(null, 0, w, from, HitKind.Direct, w.Indirect));
            }
            Assert.AreEqual(15f, Hit(hmg, new Vector2(0f, 20f)), 1e-3f, "front: two levels under");
            Assert.AreEqual(40f, Hit(hmg, new Vector2(20f, 0f)), 1e-3f, "side: one under");
            Assert.AreEqual(75f, Hit(hmg, new Vector2(0f, -20f)), 1e-3f, "rear: level");

            // A top-attack missile strikes the roof (level 1) wherever it comes from; the same missile without the
            // tag the front. Penetration 1 on both keeps the difference visible.
            var javelin = new WeaponDef("top_test", DamageType.ShapedCharge, 100f, 1f, 30f, 0f, 20f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Missile)
                { Penetration = 1, TopAttack = true };
            var direct = new WeaponDef("direct_test", DamageType.ShapedCharge, 100f, 1f, 30f, 0f, 20f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Missile)
                { Penetration = 1 };
            Assert.AreEqual(75f, Hit(javelin, new Vector2(0f, 20f)), 1e-3f, "top attack: the roof's level 1");
            Assert.AreEqual(15f, Hit(direct, new Vector2(0f, 20f)), 1e-3f, "direct: the front's level 3");
            // Everything lobbed or dropped comes down on the roof too.
            Assert.AreEqual(ArmorFace.Top, DamageSystem.FaceOf(tank, new HitInfo(null, 0, TestWorlds.Howitzer, new Vector2(0f, 60f), HitKind.Direct, true)));

            // Final damage = round x penetration x damage type (x equipment): fragmentation on the ground is weaker.
            var frag = new WeaponDef("frag_test", DamageType.Fragmentation, 100f, 1f, 30f, 0f, 200f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Bullet) { Penetration = 4 };
            Assert.AreEqual(100f * world.Catalog.Damage.Type(DamageType.Fragmentation, TargetKind.Ground), Hit(frag, new Vector2(0f, 20f)), 1e-3f);

            // The pure helpers the interface reads agree with the battle.
            var catalog = GameContent.LoadCatalog();
            var mbt = catalog.Vehicle("main_battle_tank");
            Assert.AreEqual(new ArmourLevels(3, 2, 1, 1), Matchup.ArmourOf(mbt));
            Assert.AreEqual(MatchVerdict.Good, Matchup.Verdict(catalog.Damage, catalog.Vehicle("tank_destroyer"), mbt), "a 125 mm against a battle tank");
            Assert.AreEqual(MatchVerdict.None, Matchup.Verdict(catalog.Damage, catalog.Vehicle("scout_jeep"), catalog.Vehicle("heavy_tank")), "a jeep's 12.7 mm against a heavy tank");
            Assert.AreEqual(MatchVerdict.None, Matchup.Verdict(catalog.Damage, catalog.Vehicle("sam_launcher"), mbt), "a SAM cannot reach the ground");
            var row = Matchup.EffectRow(catalog.Damage, catalog.Weapons["gun_120mm"]);
            Assert.AreEqual(1f, row[(int)EffectColumn.Armour3], 1e-5f);
            Assert.AreEqual(0.75f, row[(int)EffectColumn.Armour4], 1e-5f);
            Assert.AreEqual(0f, row[(int)EffectColumn.Air], "a tank gun cannot reach aircraft");
            var summary = Matchup.Summary(catalog.Damage, catalog.Vehicle("scout_jeep"));
            Assert.AreEqual(Threat.SmallArms, summary.WeakTo[0], "a jeep falls to anything");
            Assert.IsFalse(Matchup.Summary(catalog.Damage, catalog.Vehicle("heavy_tank")).WeakTo.Contains(Threat.HeavyMachineGuns));
        }
    }
}
