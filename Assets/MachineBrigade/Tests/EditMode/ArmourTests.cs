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
            // DECISIONS 20X: the six steps, overmatch first.
            var table = GameContent.LoadCatalog().Damage;
            Assert.AreEqual(1.2f, table.Penetration(4, 2), 1e-5f, "two levels above: the round overmatches the face");
            Assert.AreEqual(1.2f, table.Penetration(4, 0), 1e-5f);
            Assert.AreEqual(1f, table.Penetration(4, 3), 1e-5f, "a level above: all of it");
            Assert.AreEqual(0.85f, table.Penetration(3, 3), 1e-5f, "level");
            Assert.AreEqual(0.5f, table.Penetration(2, 3), 1e-5f, "one under");
            Assert.AreEqual(0.25f, table.Penetration(1, 3), 1e-5f, "two under");
            Assert.AreEqual(0.1f, table.Penetration(0, 3), 1e-5f, "three under");
            Assert.AreEqual(0.1f, table.Penetration(0, 4), 1e-5f, "four under");
            Assert.AreEqual((0.85f + 0.5f) / 2f, table.Penetration(2.5f, 3), 1e-5f, "a part level lies between");
            Assert.AreEqual((1.2f + 1f) / 2f, table.Penetration(4.5f, 3), 1e-5f, "and between one and two above");
            // A flank shot beats a front shot for a gun that pierces both (a battle tank's 3 front, 2 side).
            Assert.Greater(table.Penetration(4, 2), table.Penetration(4, 3));
            // No overmatch on a roof or an aircraft: one level above is the most.
            Assert.AreEqual(1f, table.Penetration(4, 1, overmatch: false), 1e-5f, "a roof");
            Assert.AreEqual(table.Type(DamageType.Fragmentation, TargetKind.Air), table.Effective(DamageType.Fragmentation, 4, 0, TargetKind.Air), 1e-5f, "an aircraft");
            // Prompt 15's five-value row (no overmatch step) still reads: two above is one above.
            var old = new DamageTable(new float[6, 3], new[] { 1f, 0.75f, 0.4f, 0.15f, 0.05f });
            Assert.AreEqual(1f, old.Penetration(4, 0), 1e-5f);
            Assert.AreEqual(0.75f, old.Penetration(3, 3), 1e-5f);
            Assert.AreEqual(0.05f, old.Penetration(0, 4), 1e-5f);
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
            Assert.AreEqual(ArmorFace.Side, DamageSystem.FaceFrom(tank, new Vector2(20f, 20f)), "45 degrees off the nose: the side (a 40-degree front, DECISIONS 20X)");
            Assert.AreEqual(ArmorFace.Side, DamageSystem.FaceFrom(tank, new Vector2(20f, 0f)));
            Assert.AreEqual(ArmorFace.Rear, DamageSystem.FaceFrom(tank, new Vector2(0f, -20f)));

            // A 12.7 mm-like round (kinetic, penetration 1) from the front, the side and behind: two under, one under, level.
            var table = world.Catalog.Damage;
            var hmg = new WeaponDef("hmg_test", DamageType.Kinetic, 100f, 1f, 30f, 0f, 200f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Bullet) { Penetration = 1 };
            float Hit(WeaponDef w, Vector2 from)
            {
                tank.Hp = tank.MaxHp;
                return world.Damage.Apply(tank, 100f, w.DamageType, new HitInfo(null, 0, w, from, HitKind.Direct, w.Indirect));
            }
            Assert.AreEqual(100f * table.Penetration(1, 3), Hit(hmg, new Vector2(0f, 20f)), 1e-3f, "front: two levels under");
            Assert.AreEqual(100f * table.Penetration(1, 2), Hit(hmg, new Vector2(20f, 0f)), 1e-3f, "side: one under");
            Assert.AreEqual(100f * table.Penetration(1, 1), Hit(hmg, new Vector2(0f, -20f)), 1e-3f, "rear: level");
            Assert.Less(Hit(hmg, new Vector2(0f, 20f)), Hit(hmg, new Vector2(20f, 0f)), "a flank shot beats a front shot");

            // A top-attack missile strikes the roof (level 1) wherever it comes from; the same missile without the
            // tag the front. Penetration 1 on both keeps the difference visible.
            var javelin = new WeaponDef("top_test", DamageType.ShapedCharge, 100f, 1f, 30f, 0f, 20f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Missile)
                { Penetration = 1, TopAttack = true };
            var direct = new WeaponDef("direct_test", DamageType.ShapedCharge, 100f, 1f, 30f, 0f, 20f, 0f, 0f, ExplosionTier.Small, ProjectileKind.Missile)
                { Penetration = 1 };
            Assert.AreEqual(100f * table.Penetration(1, 1), Hit(javelin, new Vector2(0f, 20f)), 1e-3f, "top attack: the roof's level 1");
            Assert.AreEqual(100f * table.Penetration(1, 3), Hit(direct, new Vector2(0f, 20f)), 1e-3f, "direct: the front's level 3");
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
            Assert.AreEqual(0.85f, row[(int)EffectColumn.Armour4], 1e-5f);
            Assert.AreEqual(1.2f, row[(int)EffectColumn.Armour2], 1e-5f, "it overmatches level 2");
            Assert.AreEqual(0f, row[(int)EffectColumn.Air], "a tank gun cannot reach aircraft");
            var summary = Matchup.Summary(catalog.Damage, catalog.Vehicle("scout_jeep"));
            Assert.AreEqual(Threat.SmallArms, summary.WeakTo[0], "a jeep falls to anything");
            Assert.IsFalse(Matchup.Summary(catalog.Damage, catalog.Vehicle("heavy_tank")).WeakTo.Contains(Threat.HeavyMachineGuns));
        }

        private static WeaponDef Round(string id, DamageType type, ProjectileKind kind, int pen, TargetLayers targets = TargetLayers.Ground) =>
            new(id, type, 100f, 1f, 40f, 0f, 60f, 0f, 0f, ExplosionTier.Small, kind, targets: targets) { Penetration = pen };

        /// <summary>
        /// Prompt 15 C (the counter table): reactive armour and cages cut shaped charges, not kinetic rounds (nor a
        /// thermobaric blast, for the cage); APS shoots down missiles, rockets and drones, never shells, bullets or
        /// beams; flares fool missiles only; smoke scatters beams (and blinds a point-defence laser).
        /// </summary>
        [Test]
        public void CountersFollowTheTable()
        {
            var kinetic = TestWorlds.Gun;
            var missile = TestWorlds.Missile;
            var rocket = Round("rpg_test", DamageType.ShapedCharge, ProjectileKind.Rocket, 4);
            var thermo = Round("tos_test", DamageType.HighExplosive, ProjectileKind.Rocket, 4);
            thermo.Thermobaric = true;
            var drone = Round("fpv_test", DamageType.ShapedCharge, ProjectileKind.Drone, 4);
            var bullet = Round("bullet_test", DamageType.Kinetic, ProjectileKind.Bullet, 4);
            var beam = Round("beam_test", DamageType.Energy, ProjectileKind.Bullet, 4, TargetLayers.All);
            beam.Beam = true;

            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 1, Vector2.Zero, 0f);
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, 20f), 0f);
            float Hit(WeaponDef w)
            {
                tank.Hp = tank.MaxHp;
                return world.Damage.Apply(tank, 100f, w.DamageType, new HitInfo(shooter, 0, w, shooter.Position, HitKind.Direct, false));
            }
            Assert.AreEqual(100f, Hit(kinetic), 1e-3f, "pen 4 on a level-3 front");
            Assert.AreEqual(100f, Hit(missile), 1e-3f);

            // Reactive armour: shaped charges only.
            tank.Special = SpecialModule.ReactiveArmor;
            tank.SpecialPower = 0.5f;
            Assert.AreEqual(50f, Hit(missile), 1e-3f, "reactive armour cuts a shaped charge");
            Assert.AreEqual(50f, Hit(rocket), 1e-3f);
            Assert.AreEqual(100f, Hit(kinetic), 1e-3f, "not a kinetic dart");
            tank.Special = SpecialModule.None;

            // A cage: shaped charges on rockets, missiles and drones; not kinetic rounds, not a thermobaric blast.
            tank.Gear = new MachineBrigade.Sim.Entities.GearState();
            tank.Gear.Stats[(int)StatId.ResistRocket] = 0.3f;
            Assert.AreEqual(70f, Hit(rocket), 1e-3f, "the cage stops part of a shaped-charge rocket");
            // A drone dives on the roof (level 1): a roof is never overmatched, one level above is the most (DECISIONS 20X).
            Assert.AreEqual(70f * world.Catalog.Damage.Penetration(4, 1, overmatch: false), Hit(drone), 1e-3f, "and of a drone");
            Assert.AreEqual(70f, Hit(drone), 1e-3f);
            Assert.AreEqual(100f, Hit(kinetic), 1e-3f, "not a kinetic round");
            Assert.AreEqual(100f, Hit(thermo), 1e-3f, "not a thermobaric blast");
            tank.Gear = null;

            // APS: missiles, rockets and drones are shot down; shells, bullets and beams land.
            tank.Aps = new ApsDef(12f, 99, 1f);
            tank.ApsCharges = 99;
            bool Lands(WeaponDef w)
            {
                tank.Hp = tank.MaxHp;
                var p = new MachineBrigade.Sim.Entities.Projectile(shooter.Id, 0, w, tank.Position, tank.Id, 0f)
                    { Origin = shooter.Position, Shooter = shooter, Main = true };
                world.Damage.ResolveImpact(p);
                return tank.Hp < tank.MaxHp;
            }
            Assert.IsFalse(Lands(missile), "APS shoots down a missile");
            Assert.IsFalse(Lands(rocket), "a rocket");
            Assert.IsFalse(Lands(drone), "a drone");
            Assert.IsTrue(Lands(kinetic), "not a tank shell");
            Assert.IsTrue(Lands(bullet), "not a bullet");
            Assert.IsTrue(Lands(beam), "not a beam");
            // A point-defence laser is blinded by smoke round it.
            tank.Aps = new ApsDef(12f, 99, 1f) { Laser = true };
            Assert.IsFalse(Lands(missile), "the laser takes the missile in clear air");
            world.Strikes.AddSmoke(1, tank.Position, 8f, 60f);
            Assert.IsTrue(Lands(missile), "not through smoke");
            tank.Aps = null;

            // Smoke scatters a beam (round the target or the shooter), nothing else.
            Assert.AreEqual(100f * (1f - DamageSystem.SmokeEnergyCut), Hit(beam), 1e-3f, "a beam into smoke");
            Assert.AreEqual(100f, Hit(kinetic), 1e-3f, "a shell through smoke");

            // Flares fool missiles only: at a flaring helicopter some missiles go wide, every flak round and beam lands.
            var air = TestWorlds.World();
            var heli = air.SpawnVehicle("heli", 1, Vector2.Zero, 0f);
            var aa = air.SpawnVehicle("aa", 0, new Vector2(0f, 30f), 0f);
            heli.FlaresUntil = 1e9;
            var sam = Round("sam_test", DamageType.Fragmentation, ProjectileKind.Missile, 3, TargetLayers.Air);
            int Landed(WeaponDef w)
            {
                var landed = 0;
                for (var i = 0; i < 60; i++)
                {
                    heli.Hp = heli.MaxHp;
                    var p = new MachineBrigade.Sim.Entities.Projectile(aa.Id, 0, w, heli.Position, heli.Id, 0f, targetFlying: true)
                        { Origin = aa.Position, Shooter = aa, Main = true, LaunchedAt = 0.0 };
                    air.Damage.ResolveImpact(p);
                    if (heli.Hp < heli.MaxHp) landed++;
                }
                return landed;
            }
            var sams = Landed(sam);
            Assert.That(sams, Is.InRange(1, 59), "flares pull some missiles off");
            Assert.AreEqual(60, Landed(TestWorlds.Flak), "flak ignores flares");
            Assert.AreEqual(60, Landed(beam), "so does a beam");
        }
    }
}
