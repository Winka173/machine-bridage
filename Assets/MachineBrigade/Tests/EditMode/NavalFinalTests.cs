using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Naval FINAL spec (09/10, Docs/naval/final, DECISIONS "Naval FINAL spec (09/10)"): the acceptance rows that a static
    /// read of the catalog can answer (ids, weapon ids, AShM 80 m/s / Pen 4, torpedo slower than AShM, no player naval
    /// Armour 5, CP per the spec and monotonic per tier, HP ratios against the anchors, a doctrine for every ship, the naval
    /// salvo guard, the escort stances). Written by the naval lane, not run by it (the lead runs the suite after merge).
    /// </summary>
    public class NavalFinalTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        /// <summary>Spec section 2's purchasable CP, the conditional ASW corvette and attack submarine left out (blocked).</summary>
        private static readonly (string id, int cp)[] Roster =
        {
            ("torpedo_boat", 7), ("ciws_escort_craft", 8), ("ashm_corvette", 9), ("aa_corvette", 9), ("ew_corvette", 9),
            ("frigate", 11), ("missile_frigate", 12), ("aa_frigate", 12), ("rocket_artillery_ship", 12), ("naval_monitor", 13),
            ("destroyer", 14), ("gun_destroyer", 14), ("missile_destroyer", 15), ("aa_destroyer", 15),
            ("sea_cruiser.gun", 17), ("sea_cruiser.missile", 18), ("battlecruiser", 19), ("battleship", 23),
        };

        /// <summary>The tiers, lightest first (spec section 2: patrol / FAC, corvette, frigate, monitor, destroyer, cruiser, capital).</summary>
        private static readonly string[][] Tiers =
        {
            new[] { "torpedo_boat", "ciws_escort_craft" },
            new[] { "ashm_corvette", "aa_corvette", "ew_corvette" },
            new[] { "frigate", "missile_frigate", "aa_frigate", "rocket_artillery_ship" },
            new[] { "naval_monitor" },
            new[] { "destroyer", "gun_destroyer", "missile_destroyer", "aa_destroyer" },
            new[] { "sea_cruiser.gun", "sea_cruiser.missile" },
            new[] { "battlecruiser" },
            new[] { "battleship" },
        };

        private static readonly string[] PlayerAshm =
        {
            "anti_ship_missile_corvette", "anti_ship_missile_light", "anti_ship_missile_quad", "anti_ship_missile_frigate",
            "anti_ship_missile_destroyer", "anti_ship_missile_cruiser",
        };

        private static VehicleDef V(string id)
        {
            Assert.That(Catalog.Vehicles.TryGetValue(id, out var def), Is.True, $"{id} is missing");
            return def;
        }

        private static IEnumerable<WeaponDef> WeaponsOf(VehicleDef def) => def.Mounts.Select(m => m.Weapon);

        [Test]
        public void EveryRosterIdExistsAndTheOldIdsAreGone()
        {
            foreach (var (id, _) in Roster) Assert.That(V(id).Naval, Is.Not.Null, $"{id}: a ship (\"naval\")");
            foreach (var old in new[] { "ciws_escort_ship", "heavy_monitor", "missile_cruiser" })
                Assert.That(Catalog.Vehicles.ContainsKey(old), Is.False, $"{old} was renamed");
            // The conditional pair is BLOCKED_BY_NO_COMPLEX_NEW_MECHANIC (the only submarine runtime is the bosses').
            Assert.That(Catalog.Vehicles.ContainsKey("asw_corvette"), Is.False);
            Assert.That(Catalog.Vehicles.ContainsKey("attack_submarine"), Is.False);
            // The renamed ships keep their 06/10 models.
            Assert.That(V("ciws_escort_craft").Model, Is.EqualTo("ciws_escort_ship"));
            Assert.That(V("naval_monitor").Model, Is.EqualTo("heavy_monitor"));
            Assert.That(V("sea_cruiser.missile").Model, Is.EqualTo("missile_cruiser"));
            Assert.That(V("sea_cruiser.gun").Model, Is.EqualTo("sea_cruiser"));
        }

        [Test]
        public void SpecWeaponIdsExistAndArePlayerVariants()
        {
            Assert.That(V("torpedo_boat").Weapon.Id, Is.EqualTo("naval_torpedo_light"));
            Assert.That(V("ashm_corvette").Weapon.Id, Is.EqualTo("anti_ship_missile_corvette"));
            var bossPrefixes = new[] { "p26_", "pt14_", "nyx_", "scylla_", "boss_", "train_" };
            foreach (var (id, _) in Roster)
                foreach (var w in WeaponsOf(V(id)))
                    Assert.That(bossPrefixes.Any(p => w.Id.StartsWith(p, StringComparison.Ordinal)), Is.False, $"{id} carries the boss weapon {w.Id}");
        }

        [Test]
        public void PlayerAntiShipMissilesArePen4At80()
        {
            foreach (var id in PlayerAshm)
            {
                Assert.That(Catalog.Weapons.TryGetValue(id, out var w), Is.True, id);
                Assert.That(w.Penetration, Is.EqualTo(4), id);
                Assert.That(w.ProjectileSpeed, Is.EqualTo(80f).Within(0.01f), id);
            }
        }

        [Test]
        public void TorpedoIsSlowerThanEveryAntiShipMissile()
        {
            var torpedo = Catalog.Weapons["naval_torpedo_light"];
            foreach (var id in PlayerAshm) Assert.That(torpedo.ProjectileSpeed, Is.LessThan(Catalog.Weapons[id].ProjectileSpeed), id);
        }

        [Test]
        public void SamAndHeavyGunSpeedsFollowTheLockedMaster()
        {
            Assert.That(Catalog.Weapons["sam_48n6"].ProjectileSpeed, Is.EqualTo(115f).Within(0.01f), "long SAM 115");
            // Heavy gun shells keep their gun speed (no missile speed rule on direct shells).
            Assert.That(Catalog.Weapons["naval_406_bs"].ProjectileSpeed, Is.GreaterThanOrEqualTo(85f));
            // The battleship's turrets: three barrels each, one volley (3 x 200).
            var bs = Catalog.Weapons["naval_406_bs"];
            Assert.That(bs.Barrels, Is.EqualTo(3));
            Assert.That(bs.Simultaneous, Is.True);
            Assert.That(bs.Damage * bs.RoundsPerPull, Is.EqualTo(600f).Within(0.01f));
        }

        [Test]
        public void NoPlayerNavalArmourFive()
        {
            foreach (var def in Catalog.Vehicles.Values.Where(d => d.Naval != null && !d.Boss))
            {
                var a = def.Armour;
                Assert.That(Math.Max(Math.Max(a.Front, a.Side), Math.Max(a.Rear, a.Top)), Is.LessThan(5), def.Id);
            }
            Assert.That(V("battleship").Armour.Front, Is.EqualTo(4));
        }

        [Test]
        public void CpFollowsTheSpecAndRisesTierByTier()
        {
            foreach (var (id, cp) in Roster) Assert.That(V(id).CpCost, Is.EqualTo(cp), id);
            for (var i = 1; i < Tiers.Length; i++)
            {
                var below = Tiers[i - 1].Max(id => V(id).CpCost);
                var here = Tiers[i].Min(id => V(id).CpCost);
                Assert.That(here, Is.GreaterThanOrEqualTo(below), $"tier {i} ({string.Join(",", Tiers[i])}) costs less than the tier below");
            }
        }

        [Test]
        public void HpRatiosFollowTheAnchors()
        {
            float Hp(string id) => V(id).MaxHp;
            Assert.That(Hp("torpedo_boat") / Hp("missile_boat"), Is.InRange(1.15f, 1.30f));
            Assert.That(Hp("ciws_escort_craft") / Hp("hover_gunboat"), Is.InRange(1.0f, 1.25f));
            Assert.That(Hp("ashm_corvette") / Hp("sea_corvette"), Is.InRange(0.85f, 0.95f));
            Assert.That(Hp("frigate") / Hp("sea_corvette"), Is.InRange(1.20f, 1.35f));
            Assert.That(Hp("destroyer") / Hp("frigate"), Is.InRange(1.35f, 1.50f));
            Assert.That(Hp("missile_destroyer"), Is.LessThanOrEqualTo(Hp("destroyer")));
            var battleship = Hp("battleship");
            foreach (var def in Catalog.Vehicles.Values.Where(d => d.Naval != null && !d.Boss && d.Id != "battleship"))
                Assert.That(def.MaxHp, Is.LessThan(battleship), $"{def.Id}: the battleship has the highest player naval HP");
            Assert.That(Hp("battlecruiser"), Is.InRange(Hp("sea_cruiser.gun"), battleship));
            Assert.That(V("battlecruiser").Speed, Is.GreaterThan(V("battleship").Speed));
        }

        [Test]
        public void EveryShipHasAnExplicitDoctrine()
        {
            var world = new SimWorld(Catalog, SandboxMaps.Coast(), seed: 3);
            var expected = new Dictionary<string, DoctrineRole>
            {
                ["torpedo_boat"] = DoctrineRole.TankDestroyer, ["ciws_escort_craft"] = DoctrineRole.Support, ["ashm_corvette"] = DoctrineRole.TankDestroyer,
                ["aa_corvette"] = DoctrineRole.AntiAir, ["ew_corvette"] = DoctrineRole.Support, ["frigate"] = DoctrineRole.MainBattle,
                ["missile_frigate"] = DoctrineRole.TankDestroyer, ["aa_frigate"] = DoctrineRole.AntiAir, ["rocket_artillery_ship"] = DoctrineRole.FireSupport,
                ["naval_monitor"] = DoctrineRole.MainBattle, ["destroyer"] = DoctrineRole.MainBattle, ["gun_destroyer"] = DoctrineRole.MainBattle,
                ["missile_destroyer"] = DoctrineRole.TankDestroyer, ["aa_destroyer"] = DoctrineRole.AntiAir, ["sea_cruiser.gun"] = DoctrineRole.MainBattle,
                ["sea_cruiser.missile"] = DoctrineRole.TankDestroyer, ["battlecruiser"] = DoctrineRole.MainBattle, ["battleship"] = DoctrineRole.MainBattle,
            };
            var k = 0;
            foreach (var (id, _) in Roster)
            {
                Assert.That(Catalog.AiData.RoleOf(id), Is.Not.Null, $"{id}: no aiBehaviour.units entry");
                var v = world.SpawnVehicle(id, 0, new Vector2(SandboxMaps.LaneX[1], -120f + k++ * 14f), 0f);
                Assert.That(CombatRoleDoctrine.BaseRole(world, v), Is.EqualTo(expected[id]), id);
                Assert.That(V(id).Naval.Patrol, Is.Not.Null, $"{id}: a patrol lane (its stance alone)");
            }
            // Escorts that must not lead keep station astern; the standoff ships hold the far lane, the gun ships the near one.
            Assert.That(V("ciws_escort_craft").Naval.Station, Is.LessThan(0f));
            Assert.That(V("ew_corvette").Naval.Station, Is.LessThan(0f));
            foreach (var id in new[] { "ashm_corvette", "missile_frigate", "missile_destroyer", "sea_cruiser.missile", "aa_frigate", "aa_destroyer" })
                Assert.That(V(id).Naval.Patrol, Is.EqualTo("far"), id);
            foreach (var id in new[] { "frigate", "gun_destroyer", "naval_monitor" })
                Assert.That(V(id).Naval.Patrol, Is.EqualTo("near"), id);
        }

        [Test]
        public void ArmedShipsCanFireOnTheMove()
        {
            // The naval system keeps a ship sailing: a stop-to-fire main weapon or a stand-still reload would idle it.
            foreach (var (id, _) in Roster)
            {
                var def = V(id);
                Assert.That(def.FiresWhileMoving, Is.True, id);
                Assert.That(def.Weapon.Ammo, Is.EqualTo(0), $"{id}: {def.Weapon.Id} needs a stand-still reload");
            }
        }

        [Test]
        public void BigNavalSalvoSkipsACheapLightTarget()
        {
            Assert.That(CombatRoleDoctrine.NavalSalvo(V("battleship"), V("battleship").Weapon), Is.True);
            Assert.That(CombatRoleDoctrine.NavalSalvo(V("missile_destroyer"), V("missile_destroyer").Weapon), Is.True);
            Assert.That(CombatRoleDoctrine.NavalSalvo(V("ew_corvette"), V("ew_corvette").Weapon), Is.False, "a self-defence gun is no salvo");
            var light = CombatRoleDoctrine.Worth(DoctrineRole.MainBattle, TargetClass.Light, false, 0f, false, false, false, 6f, false, navalSalvo: true);
            var heavy = CombatRoleDoctrine.Worth(DoctrineRole.MainBattle, TargetClass.Heavy, false, 0f, false, false, false, 14f, false, navalSalvo: true);
            var urgent = CombatRoleDoctrine.Worth(DoctrineRole.MainBattle, TargetClass.Light, true, 0f, false, false, false, 6f, false, navalSalvo: true);
            Assert.That(light, Is.EqualTo(SimTunables.Ai.RoleDoctrine.LastResort).Within(1e-4f));
            Assert.That(heavy, Is.GreaterThan(light));
            Assert.That(urgent, Is.GreaterThan(light), "a light boat that threatens it is still answered");
            Assert.That(light, Is.GreaterThan(0f), "never an idle gun: a last resort is still shot");
        }

        [Test]
        public void NoForbiddenMechanicOnTheRoster()
        {
            foreach (var (id, _) in Roster)
            {
                var def = V(id);
                Assert.That(def.Craft, Is.Null, $"{id}: no transport / landing craft");
                Assert.That(def.Fleet.Count, Is.EqualTo(0), $"{id}: no fleet spawning");
                Assert.That(def.AirWaves.Count, Is.EqualTo(0), $"{id}: no aircraft spawning");
                Assert.That(def.Card, Is.False, $"{id}: AI / codex only (the naval pattern)");
            }
        }
    }
}
