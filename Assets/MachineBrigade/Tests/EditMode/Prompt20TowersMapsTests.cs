using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 20 L and M: the C-RAM's Iron Dome branch (lobbed rounds only, out to 60 m, a launcher reloaded whole, the
    /// AI's choice by the deck it faces), the rocket battery's rockets over a wall, the AA tower's SAM post at 60 m, and
    /// the two new battlefields (every version, their bases, the mine's fixed route, names and guides).
    /// </summary>
    public class Prompt20TowersMapsTests
    {
        private static readonly string[] NewMaps = { "openpit", "orbitalgate" };

        private static SimWorld Field(List<PropPlacement> props = null) =>
            new(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                props ?? new List<PropPlacement>(), new List<UnitPlacement>())) { RevealAll = true };

        private static Vehicle Tower(SimWorld world, string id, int team, Vector2 at, float heading = 0f)
        {
            var t = world.SpawnVehicle(id, team, at, heading);
            world.AnchorDefence(t);
            return t;
        }

        private static void Run(SimWorld world, float seconds, Action<SimEvent> seen = null, params Vehicle[] keep)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                foreach (var v in keep) v.Hp = v.MaxHp;
                world.Step(TestWorlds.Step);
                if (seen != null)
                    foreach (var e in world.Events) seen(e);
                world.ClearEvents();
            }
        }

        private static bool Lobbed(WeaponDef w) => w.Projectile == ProjectileKind.Drone || w.MinRange > 0f;

        [Test]
        public void TheCRamBranchesAreTheIronDomeAndTheCloseInCenturion()
        {
            var catalog = GameContent.LoadCatalog();
            CollectionAssert.AreEquivalent(new[] { "c_ram.centurion", "c_ram.dome" }, TowerCards.Branches(catalog, "c_ram"));
            var dome = catalog.Vehicles["c_ram.dome"];
            Assert.AreEqual(60f, dome.Aps.Radius, 0.01f, "interceptors reach about 60 m");
            Assert.IsFalse(dome.Aps.Direct, "no direct fire");
            Assert.Greater(dome.Aps.Reload, 0f, "a launcher reloaded whole");
            Assert.Less(dome.Aps.Charges / dome.Aps.Reload, 1f / catalog.Vehicles["c_ram.centurion"].Aps.Recharge, "fewer shots than the close-in C-RAM");
            Assert.AreEqual(60f, dome.Weapon.Range, 0.01f);
            Assert.IsTrue(dome.Weapon.Guided && dome.Weapon.Ammo > 0, "its launcher's missiles run on prompt 13's magazine");
            // The branch icon, the generated behaviour lines and the base screen's cover and reach.
            // The C-RAM's second branch: its icon is t_cram_b (tower-branch prompt C.4 names branch icons by letter).
            Assert.AreEqual("t_cram_b", TowerIcons.For("c_ram.dome"));
            Assert.IsTrue(Icons.Exists("t_cram_b"));
            var lines = UnitLines.Behaviour(catalog, dome);
            Assert.Contains(Strings.Get("ul.apsLobbed"), lines);
            Assert.IsTrue(Strings.Has("branch.c_ram.dome") && Strings.Has("branch.c_ram.dome.info") && Strings.Has("short.c_ram.dome"));
            var roles = BaseRoles.Of(dome);
            Assert.IsTrue(roles.Contains(CoverRole.Intercept) && roles.Contains(CoverRole.AntiAir));
            Assert.AreEqual(60f, BaseRoles.Reach(dome).air, 0.01f);
        }

        [Test]
        public void TheIronDomeTakesLobbedRoundsOutTo60mButNotDirectFire()
        {
            var world = Field();
            var dome = Tower(world, "c_ram.dome", 1, new Vector2(0f, 0f));
            // A tank 48 m off: past the close-in C-RAM's 35 m, inside the dome's 60.
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(48f, 0f), 0f);
            tank.HoldFire = true;
            var mlrs = world.SpawnVehicle("mlrs", 0, new Vector2(48f, -80f), 0f);
            var ifv = world.SpawnVehicle("ifv", 0, new Vector2(48f, -30f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { mlrs.Id, ifv.Id }, target: tank.Id));
            var taken = new List<string>();
            var atgm = 0f;
            DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (victim == tank && weapon != null && weapon.Guided && !Lobbed(weapon)) atgm += amount;
            };
            try
            {
                Run(world, 40f, e =>
                {
                    if (e.Kind == SimEventKind.Intercepted && e.Entity == dome.Id && e.DefId != null) taken.Add(e.DefId);
                }, dome, tank, ifv, mlrs);
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            Assert.Contains("mlrs_rockets", taken, "artillery rockets aimed 48 m away");
            foreach (var id in taken) Assert.IsTrue(Lobbed(world.Catalog.Weapons[id]), id + " is not lobbed");
            Assert.Greater(atgm, 0f, "the ATGMs got through");
            Assert.LessOrEqual(taken.Count, 24, "six a launcher, 12 s to reload");
        }

        [Test]
        public void TheIronDomeReloadsItsWholeLauncherAfterAQuietSpell()
        {
            var world = Field();
            var dome = Tower(world, "c_ram.dome", 1, new Vector2(0f, 0f));
            dome.ApsCharges = 0;
            dome.ApsReload = 0f;
            Run(world, dome.Aps.Reload - 1f);
            Assert.AreEqual(0, dome.ApsCharges, "nothing trickles back");
            Run(world, 2f);
            Assert.AreEqual(dome.Aps.Charges, dome.ApsCharges, "the whole launcher back at once");
        }

        [Test]
        public void TheAiChoosesTheIronDomeAgainstLobbedFireAndCenturionAgainstMissiles()
        {
            var catalog = GameContent.LoadCatalog();
            string Pick(params string[] deck)
            {
                var loadout = new BaseLoadout { HqLevel = 5 };
                loadout.Medium.Add("c_ram");
                BaseLoadout.ChooseAiBranches(catalog, loadout, deck);
                return loadout.Branches.TryGetValue("c_ram", out var b) ? b : null;
            }
            Assert.AreEqual("c_ram.dome", Pick("artillery", "mlrs", "mortar_carrier", "main_battle_tank"));
            Assert.AreEqual("c_ram.centurion", Pick("attack_helicopter", "tank_destroyer", "ifv", "main_battle_tank"));
            // An easy AI keeps its towers plain.
            var easy = BaseLoadout.ForAi(catalog, "Easy", against: new[] { "artillery", "mlrs" });
            Assert.IsEmpty(easy.Branches);
        }

        [Test]
        public void TheRocketBatteryFiresOverAWallOntoTargetsAtItsFootButNotInsideEightMetres()
        {
            // A wall across the field at z = 6; the battery 10 m behind it, a tank 8 m beyond it.
            var wall = new List<PropPlacement>();
            for (var x = -24f; x <= 24f; x += 8f) wall.Add(new PropPlacement("base_wall", new Vector2(x, 6f), 0));
            var world = Field(wall);
            var battery = Tower(world, "rocket_turret", 1, new Vector2(0f, 16f), MathF.PI);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -2f), 0f);
            tank.HoldFire = true;
            float rockets = 0f, bullets = 0f;
            DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (by != battery || victim != tank || weapon == null) return;
                if (weapon.Projectile == ProjectileKind.Rocket) rockets += amount;
                else if (weapon == battery.Def.Mounts[1].Weapon) bullets += amount;
            };
            try
            {
                // Two salvos: long enough for the rockets, too short for their near misses to bring the wall down.
                Run(world, 12f, null, battery, tank);
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            Assert.Greater(rockets, 0f, "its rockets arc over the wall");
            Assert.AreEqual(0f, bullets, "its machine gun cannot see through the wall");

            // Inside 8 m only the machine gun fires.
            var close = Field();
            var near = Tower(close, "rocket_turret", 1, new Vector2(0f, 0f), MathF.PI);
            var hugging = close.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -5f), 0f);
            hugging.HoldFire = true;
            var inside = 0f;
            DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (by == near && victim == hugging && weapon is { Projectile: ProjectileKind.Rocket }) inside += amount;
            };
            try
            {
                Run(close, 12f, null, near, hugging);
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            Assert.AreEqual(0f, inside, "no rockets inside the minimum range");
            Assert.AreEqual(8f, world.Catalog.Vehicles["rocket_turret"].Weapon.MinRange, 0.01f);
        }

        [Test]
        public void TheSamPostReaches60mBetweenTheFlakAndThePatriot()
        {
            var catalog = GameContent.LoadCatalog();
            var sam = BaseRoles.Reach(catalog.Vehicles["aa_turret.sam"]).air;
            var flak = BaseRoles.Reach(catalog.Vehicles["aa_turret.flak"]).air;
            var patriot = BaseRoles.Reach(catalog.Vehicles["missile_battery"]).air;
            // Prompt 32 L1: the Stinger post (the MANPADS tower folded in), 56 m.
            Assert.AreEqual(56f, sam, 0.01f);
            Assert.Less(flak, sam, "the flak stays close in");
            Assert.Greater(patriot, sam, "the Patriot reaches furthest");
            Assert.GreaterOrEqual(catalog.Vehicles["aa_turret.sam"].VisionRange, sam, "it sees what it reaches");
        }

        [Test]
        public void TheNewBattlefieldsHaveEveryVersionANameAndAGuide()
        {
            foreach (var id in NewMaps)
            {
                var conquest = GameContent.LoadMap(id + "_conquest");
                Assert.AreEqual(2, conquest.Bases.Count, id + ": both camps");
                Assert.AreEqual(3, conquest.Points.Count, id + ": three objectives");
                foreach (var camp in conquest.Bases)
                {
                    var places = SlotPlaces.Keys(camp).Select(k => k.Place).ToList();
                    Assert.AreEqual(camp.Slots.Count, places.Count, id + ": a label for every slot");
                    Assert.IsTrue(places.Contains(SlotPlace.Gate) && places.Contains(SlotPlace.Utility), $"{id} team {camp.Team}: gate and utility slots");
                }
                Assert.IsNotNull(GameContent.LoadMap(id + "_sandbox"), id + ": Survival");
                Assert.IsNotNull(GameContent.LoadMap(id + "_siege").Fortress, id + ": Siege");
                Assert.IsTrue(GameContent.LoadMap(id + "_long").IsLong, id + ": the long battlefield");
                Assert.IsTrue(MatchSettings.AllMaps.Any(m => m.Id == id), id + ": in the skirmish list");
                foreach (var key in new[] { "map." + id, "map." + id + ".sub", "guide.map." + id })
                    Assert.IsTrue(Strings.Has(key), key);
            }
        }

        [Test]
        public void TheMineHasAFixedRouteOnOpenGroundToThePlayersCamp()
        {
            var map = GameContent.LoadMap("openpit_conquest");
            // Play-test 14: the haul road (the route Kronos drove, renamed when it was deleted).
            var route = map.Route("haul");
            Assert.IsNotNull(route, "the haul road");
            Assert.GreaterOrEqual(route.Count, 2);
            var camp = map.BaseOf(0).Hq;
            Assert.Greater(route[0].X + route[0].Y, 0f, "it starts on the enemy's side");
            Assert.Less(Vector2.Distance(route[route.Count - 1], camp), 45f, "it ends at the player's camp");
            var world = new SimWorld(GameContent.LoadCatalog(), map);
            for (var i = 1; i < route.Count; i++)
            {
                var a = route[i - 1];
                var b = route[i];
                var steps = Math.Max(1, (int)(Vector2.Distance(a, b) / 2f));
                for (var k = 0; k <= steps; k++)
                {
                    var p = Vector2.Lerp(a, b, k / (float)steps);
                    Assert.IsTrue(map.InsideBoundary(p), $"{p} is outside the outline");
                    var (x, y) = world.Grid.CellOf(p);
                    Assert.IsTrue(world.Grid.IsWalkable(x, y), $"{p} is blocked");
                }
            }
            // A campaign mission from the other side walks it the other way.
            var back = map.Reversed().Route("haul");
            Assert.AreEqual(route[0], back[back.Count - 1]);
        }
    }
}
