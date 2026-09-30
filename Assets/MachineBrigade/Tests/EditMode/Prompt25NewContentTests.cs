using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 F2 batch A (DECISIONS 25F2-A): the balance sheet's new units and structures ("Đề xuất thêm", "Công trình
    /// mới"), one row each: the sheet's numbers, the texts and the shop, and a short check of each one's mechanism. Written
    /// under the owner's rule of 30/09 (no test runs until the test phase): not run yet.
    /// </summary>
    public class Prompt25NewContentTests
    {
        public sealed class Row
        {
            public Row(string id, float sheetHp, int cp, int front, float vision, string weapon, float damage, float range, float dps, string mechanism)
            {
                Id = id;
                SheetHp = sheetHp;
                Cp = cp;
                Front = front;
                Vision = vision;
                Weapon = weapon;
                Damage = damage;
                Range = range;
                Dps = dps;
                Mechanism = mechanism;
            }

            public string Id, Weapon, Mechanism;
            public float SheetHp, Vision, Damage, Range, Dps;
            public int Cp, Front;

            public override string ToString() => Id;
        }

        public static readonly Row[] Rows =
        {
            new Row("heavy_flak_tower", 3000, 0, 2, 64, "flak_88", 120, 70, 60, "groundRange"),
            new Row("aa_gun_vehicle", 1000, 5, 1, -1, "bofors_l70", 30, 48, 75, "air"),
            new Row("shorad_vehicle", 700, 4, 0, -1, "avenger_stingers", 170, 44, -1, "ripple"),
            new Row("microwave_vehicle", 900, 6, 1, -1, "none", -1, -1, -1, "microwave"),
            new Row("at_gun_emplacement", 1500, 0, 2, 40, "at_gun_100", 200, 38, 40, "arc"),
            new Row("nlos_atgm_vehicle", 900, 8, 1, -1, "spike_nlos", 300, 90, 30, "lofted"),
            new Row("radar_atgm_vehicle", 1300, 7, 2, -1, "khrizantema", 250, 50, -1, "smokeSight"),
            new Row("recoilless_jeep", 350, 3, 0, -1, "recoilless_106", 220, 32, 33, "ambush"),
            new Row("airborne_vehicle", 1100, 6, 1, -1, "gun_100_2a70", -1, -1, -1, "paradrop"),
            new Row("wheeled_howitzer", 700, 6, 0, -1, "caesar_155", 320, 90, 41.3f, "scoot"),
            new Row("sp_mortar", 1200, 5, 2, -1, "amos_120", 150, 60, -1, "mrsi"),
            new Row("glide_bomber", 2200, 16, 1, -1, "glide_fab500", 420, 90, -1, "glide"),
            new Row("recon_jet", 800, 8, 0, -1, "none", -1, -1, -1, "pass"),
            new Row("interceptor_jet", 1300, 13, 0, -1, "r37m", 400, 90, -1, "bigGame"),
            new Row("radar_scout", 700, 4, 1, 50, "hmg_selfdef_21", -1, -1, -1, "mast"),
            new Row("blast_wall", 3000, 0, 3, -1, "none", -1, -1, -1, "wall"),
            new Row("inflatable_decoy", 300, 0, 0, -1, "none", -1, -1, -1, "decoy"),
            new Row("fire_control_centre", 2500, 0, 1, 40, "none", -1, -1, -1, "link"),
            new Row("searchlight", 1200, 0, 1, 70, "none", -1, -1, -1, "light"),
            new Row("barrage_balloon", 800, 0, 0, -1, "none", -1, -1, -1, "balloon"),
            new Row("visual_jammer", 2000, 0, 1, 30, "none", -1, -1, -1, "screen"),
            new Row("fibre_fpv_carrier", 950, 7, 1, -1, "fpv_fibre", 160, 60, 26.7f, "jamProof"),
            new Row("interceptor_drone_vehicle", 900, 5, 1, -1, "interceptor_drone", 120, 60, 30, "rotors"),
            new Row("troop_shelter", 4000, 0, 3, 30, "none", -1, -1, -1, "shelter"),
            new Row("flare_tower", 1000, 0, 1, 60, "illum_flare", -1, 40, -1, "flares"),
            new Row("laser_ad_station", 2500, 0, 1, 56, "laser_50kw", 6, 40, 90, "drones"),
            new Row("aa_gun_tower", 2800, 0, 2, 56, "bofors_l70", 30, 48, 75, "air"),
            // (batch A rows: new ones above)
        };

        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 240f,
                new[] { new TeamStart(0, new Vector2(-100f, -100f)), new TeamStart(1, new Vector2(100f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds, System.Action<SimEvent> seen = null, System.Action each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                if (seen != null)
                    foreach (var e in world.Events) seen(e);
                world.ClearEvents();
                each?.Invoke();
            }
        }

        /// <summary>A unit held where it is put, never firing, never dying.</summary>
        private static Vehicle Target(SimWorld world, string id, int team, Vector2 at)
        {
            var v = world.SpawnVehicle(id, team, at, 0f);
            v.HoldFire = true;
            world.MakeSparring(v);
            world.Submit(new Command(CommandType.Stop, team, new[] { v.Id }));
            return v;
        }

        /// <summary>Rounds <paramref name="shooter"/> fires at <paramref name="target"/> in <paramref name="seconds"/>, the target held at <paramref name="at"/>.</summary>
        private static int ShotsAt(SimWorld world, Vehicle shooter, Vehicle target, Vector2 at, float seconds)
        {
            var n = 0;
            Run(world, seconds, e =>
            {
                if (e.Kind == SimEventKind.WeaponFired && e.Entity == shooter.Id && e.Other == target.Id) n++;
            }, () =>
            {
                target.Position = at;
                target.Hp = target.MaxHp;
            });
            return n;
        }

        private static float Hit(SimWorld world, Vehicle v, string round, Vector2 from)
        {
            var weapon = world.Catalog.Weapons[round];
            var hp = v.Hp;
            world.Damage.Apply(v, 100f, weapon.DamageType, new HitInfo(null, 1 - v.Team, weapon, from, HitKind.Direct, weapon.Indirect));
            var lost = hp - v.Hp;
            v.Hp = v.MaxHp;
            return lost;
        }

        /// <summary>The sheet's numbers (health over the vehicles' toughness, CP, front armour, vision, the main weapon), the texts and the one unlock source.</summary>
        [TestCaseSource(nameof(Rows))]
        public void MatchesTheSheetAndHasItsTextsAndShopPrice(Row row)
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Vehicles.TryGetValue(row.Id, out var def), row.Id);
            Assert.AreEqual(row.SheetHp, def.MaxHp, row.SheetHp * 0.01f, "the sheet's health (data x 2.2)");
            Assert.AreEqual(row.Cp, def.CpCost);
            Assert.AreEqual(row.Front, def.Armour.Front);
            if (row.Vision > 0f) Assert.AreEqual(row.Vision, def.VisionRange);
            Assert.AreEqual(row.Weapon, def.Weapon.Id);
            if (row.Damage > 0f) Assert.AreEqual(row.Damage, def.Weapon.Damage);
            if (row.Range > 0f) Assert.AreEqual(row.Range, def.Weapon.Range);
            if (row.Dps > 0f) Assert.AreEqual(row.Dps, def.Weapon.SustainedDps, row.Dps * 0.05f, "sustained damage a second within 5 %");
            Assert.Greater(def.ModelLength, 0f, "modelSize");
            foreach (var key in new[] { "unit.", "short.", "note.", "guide." }) Assert.IsTrue(Strings.Has(key + row.Id), key + row.Id);
            foreach (var vi in new[] { false, true })
            {
                Strings.Vietnamese = vi;
                Assert.LessOrEqual(Strings.Short(row.Id).Length, 15, "a short name on one line");
                foreach (var other in Rows)
                    if (other.Id != row.Id) Assert.AreNotEqual(Strings.Card(other.Id), Strings.Card(row.Id), "a name of its own");
            }
            Strings.Vietnamese = false;
            Assert.IsTrue(Progression.IsNewContent(row.Id) && Progression.Price(row.Id, catalog) > 0, "sold in the shop");
            Assert.IsNull(Progression.UnlockMission(row.Id), "the shop is its one source");
            Assert.IsTrue(Progression.EnemyMayUse(row.Id), "the enemy may field it");
            if (def.Fort == null) CollectionAssert.Contains(MatchSettings.AllVehicles, row.Id);
            else Assert.IsTrue(Icons.Exists(TowerIcons.For(row.Id)), "a structure icon");
        }

        /// <summary>Each item's mechanism, a short scene each.</summary>
        [TestCaseSource(nameof(Rows))]
        public void ItsMechanismWorks(Row row)
        {
            var world = Field();
            var c = world.Catalog;
            var here = Vector2.Zero;
            switch (row.Mechanism)
            {
                case "groundRange":
                {
                    var flak = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, 60f));
                    Assert.AreEqual(0, ShotsAt(world, flak, tank, new Vector2(0f, 60f), 5f), "no ground shot past 50 m");
                    Assert.Greater(ShotsAt(world, flak, tank, new Vector2(0f, 45f), 5f), 0, "one inside it");
                    Assert.IsTrue(c.Weapons["flak_88"].GroupPriority);
                    break;
                }
                case "air":
                {
                    var gun = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var heli = Target(world, "attack_helicopter", 1, new Vector2(0f, 44f));
                    Assert.Greater(ShotsAt(world, gun, heli, new Vector2(0f, 44f), 5f), 0, "a helicopter at 44 m");
                    break;
                }
                case "ripple":
                {
                    var sam = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var heli = Target(world, "attack_helicopter", 1, new Vector2(0f, 40f));
                    Assert.AreEqual(8, ShotsAt(world, sam, heli, new Vector2(0f, 40f), 12f), "eight in the ripple, then the 15 s reload (its roof gun aside)");
                    break;
                }
                case "microwave":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var a = world.SpawnVehicle("recon_drone", 1, new Vector2(0f, 20f), 0f);
                    var b = world.SpawnVehicle("recon_drone", 1, new Vector2(4f, 24f), 0f);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(-2f, 18f));
                    Run(world, 1.5f, each: () =>
                    {
                        if (a.IsAlive) a.Position = new Vector2(0f, 20f);
                        if (b.IsAlive) b.Position = new Vector2(4f, 24f);
                    });
                    Assert.IsFalse(a.IsAlive || b.IsAlive, "both drones in the cone down");
                    Assert.AreEqual(tank.MaxHp, tank.Hp, 1e-3f, "the tank in the cone unharmed");
                    break;
                }
                case "arc":
                {
                    var gun = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, -30f));
                    Assert.AreEqual(0, ShotsAt(world, gun, tank, new Vector2(0f, -30f), 8f), "nothing behind its arc");
                    Assert.Greater(ShotsAt(world, gun, tank, new Vector2(8f, 30f), 12f), 0, "a tank ahead");
                    break;
                }
                case "lofted":
                {
                    var nlos = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, 80f));
                    Assert.AreEqual(0, ShotsAt(world, nlos, tank, new Vector2(0f, 80f), 3f), "unseen: no shot");
                    Target(world, "scout_jeep", 0, new Vector2(0f, 45f));
                    Assert.Greater(ShotsAt(world, nlos, tank, new Vector2(0f, 80f), 12f), 0, "a friend spots it");
                    Assert.IsTrue(c.Weapons["spike_nlos"].Indirect && c.Weapons["spike_nlos"].TopAttack);
                    break;
                }
                case "smokeSight":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, 30f));
                    world.Strikes.AddSmoke(1, new Vector2(0f, 30f), 8f, 30f);
                    Run(world, 1f, each: () => tank.Position = new Vector2(0f, 30f));
                    Assert.IsTrue(tank.IsSeenBy(0), "seen in the smoke");
                    break;
                }
                case "ambush":
                {
                    var jeep = Target(world, row.Id, 0, here);
                    Target(world, "main_battle_tank", 1, new Vector2(0f, 28f));
                    Run(world, 3f);
                    Assert.IsFalse(jeep.IsSeenBy(1), "parked, hidden from a tank's 30 m sight");
                    break;
                }
                case "paradrop":
                {
                    world.EnableEconomy(new TeamEconomy(0, 100f, bank: 200f));
                    Assert.AreEqual(CommandError.DropNotSeen, world.Submit(Command.Paradrop(0, row.Id, new Vector2(40f, 40f))).Error, "nobody sees there");
                    Target(world, "scout_jeep", 0, new Vector2(30f, 30f));
                    Assert.AreEqual(CommandError.DropNotSeen, world.Submit(Command.Paradrop(0, row.Id, new Vector2(100f, 100f))).Error, "never into the enemy base");
                    Assert.IsTrue(world.Submit(Command.Paradrop(0, row.Id, new Vector2(40f, 40f))).Accepted);
                    Assert.IsTrue(world.Vehicles.Any(v => v.IsPod && v.Flying && v.Def.Id == "airborne_vehicle_chute"), "falling, a low-altitude target");
                    Run(world, 7f);
                    Assert.IsTrue(world.Vehicles.Any(v => v.IsAlive && v.Def.Id == row.Id), "landed");
                    break;
                }
                case "scoot":
                {
                    var how = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, 60f));
                    Target(world, "scout_jeep", 0, new Vector2(0f, 30f));
                    Assert.AreEqual(4, ShotsAt(world, how, tank, new Vector2(0f, 60f), 10f), "one salvo of four");
                    Assert.Greater(Vector2.Distance(how.Position, here), 5f, "then it drives off");
                    break;
                }
                case "mrsi":
                {
                    var mortar = world.SpawnVehicle(row.Id, 0, here, 0f);
                    Target(world, "main_battle_tank", 1, new Vector2(0f, 45f));
                    Target(world, "scout_jeep", 0, new Vector2(0f, 20f));
                    var lands = new List<double>();
                    Run(world, 6f, e => { if (e.Kind == SimEventKind.WeaponFired && e.Entity == mortar.Id && e.DefId == row.Weapon) lands.Add(world.Time + e.Value); });
                    Assert.AreEqual(4, lands.Count);
                    Assert.Less(lands.Max() - lands.Min(), 0.15, "all four land at once");
                    break;
                }
                case "glide":
                {
                    var bomb = c.Weapons[row.Weapon];
                    Assert.IsTrue(bomb.Glides && bomb.GuidedBomb);
                    Assert.IsTrue(DamageSystem.GunTakes(c.Vehicles["c_ram"].Aps, bomb, out _), "a C-RAM takes it");
                    var bomber = world.SpawnVehicle(row.Id, 0, new Vector2(0f, -100f), 0f);
                    var tower = Target(world, "gun_turret", 1, new Vector2(0f, 40f));
                    var closest = float.MaxValue;
                    Run(world, 25f, each: () => { if (bomber.IsAlive) closest = System.MathF.Min(closest, Vector2.Distance(bomber.Position, tower.Position)); });
                    Assert.Greater(closest, 40f, "it never flies over its target");
                    break;
                }
                case "pass":
                {
                    var jet = world.SpawnVehicle(row.Id, 0, new Vector2(-100f, -100f), 0.785f);
                    Assert.AreEqual(AltitudeTier.High, jet.Tier);
                    Assert.IsFalse(TierRules.Reaches(c.Weapons["flak_35"], c.Vehicles["aa_vehicle"], AltitudeTier.High, true), "short-range AA cannot reach it");
                    var stealth = Target(world, "stealth_fighter", 1, here);
                    Run(world, 3f, each: () => stealth.Position = here);
                    Assert.IsTrue(stealth.IsVisibleTo(0), "the strip shows stealth");
                    Run(world, 8f, each: () => stealth.Position = here);
                    Assert.IsFalse(jet.IsAlive, "it left off the far edge");
                    break;
                }
                case "bigGame":
                {
                    var jet = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var bomber = Target(world, "heavy_bomber", 1, new Vector2(20f, 80f));
                    var fighter = Target(world, "fighter_jet", 1, new Vector2(-20f, 70f));
                    var onBomber = 0;
                    var onFighter = 0;
                    Run(world, 3f, e =>
                    {
                        if (e.Kind != SimEventKind.WeaponFired || e.Entity != jet.Id) return;
                        if (e.Other == bomber.Id) onBomber++;
                        if (e.Other == fighter.Id) onFighter++;
                    }, () => { jet.Position = here; jet.Heading = 0f; bomber.Position = new Vector2(20f, 80f); fighter.Position = new Vector2(-20f, 70f); });
                    Assert.Greater(onBomber, 0, "the bomber first");
                    Assert.AreEqual(0, onFighter);
                    Assert.AreEqual(15f, c.Weapons[row.Weapon].MinReach);
                    break;
                }
                case "mast":
                {
                    var scout = Target(world, row.Id, 0, here);
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, 70f));
                    Run(world, 0.5f);
                    Assert.IsFalse(tank.IsSeenBy(0), "70 m: beyond its 50 m on the move");
                    Run(world, 3f, each: () => scout.Position = here);
                    Assert.IsTrue(tank.IsSeenBy(0), "mast up: 80 m");
                    break;
                }
                case "wall":
                {
                    var tower = world.SpawnVehicle("gun_turret", 0, here, 0f);
                    world.SpawnVehicle(row.Id, 0, new Vector2(0f, 6f), 0f);
                    Run(world, 0.1f);
                    Assert.AreEqual(0.7f, Hit(world, tower, "gun_120mm", new Vector2(0f, 40f)) / Hit(world, tower, "gun_120mm", new Vector2(0f, -40f)), 0.01f, "30 % less from its side");
                    Assert.AreEqual(Hit(world, tower, "howitzer", new Vector2(0f, -60f)), Hit(world, tower, "howitzer", new Vector2(0f, 60f)), 0.01f, "shells come over it");
                    break;
                }
                case "decoy":
                {
                    var decoy = world.SpawnVehicle(row.Id, 0, here, 0f);
                    world.MakeSparring(decoy);
                    var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 25f), 3.14159f);
                    world.Submit(new Command(CommandType.Stop, 1, new[] { tank.Id }));
                    Assert.Greater(ShotsAt(world, tank, decoy, here, 8f), 0, "taken for a gun turret");
                    Target(world, "scout_jeep", 1, new Vector2(10f, 20f));
                    Run(world, 1.5f);
                    Assert.IsTrue(decoy.DecoyExposedTo(1), "a scout finds it out");
                    Assert.AreEqual(0, ShotsAt(world, tank, decoy, here, 6f), "no more fire on it");
                    break;
                }
                case "link":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var near = world.SpawnVehicle("gun_turret", 0, new Vector2(20f, 0f), 0f);
                    var far = world.SpawnVehicle("gun_turret", 0, new Vector2(-50f, 0f), 0f);
                    Run(world, 0.2f);
                    Assert.IsTrue(near.FireLinked && !far.FireLinked, "linked within 30 m only");
                    break;
                }
                case "light":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var jet = Target(world, "stealth_fighter", 1, new Vector2(0f, 32f));
                    Run(world, 3f);
                    Assert.IsFalse(jet.IsVisibleTo(0), "by day only a lookout (stealth shows at 28 m)");
                    world.SetDarkness(true);
                    Run(world, 0.2f);
                    Assert.IsTrue(jet.IsVisibleTo(0), "at night the beam reaches 35 m");
                    var tank = Target(world, "main_battle_tank", 1, new Vector2(0f, 20f));
                    Assert.AreEqual(1.25f, world.Works.SpreadFactor(tank, c.Weapons["gun_120mm"], here), 1e-3f, "dazzled: 20 % less accurate");
                    break;
                }
                case "balloon":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var bomber = Target(world, "heavy_bomber", 1, new Vector2(0f, 30f));
                    Run(world, 0.2f, each: () => bomber.Position = new Vector2(0f, 30f));
                    Assert.AreEqual(1.5f, world.Works.SpreadFactor(bomber, c.Weapons["bomber_payload"], here), 1e-3f, "bombs 50 % wider");
                    var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 10f), 0f);
                    heli.HoldFire = true;
                    world.Submit(new Command(CommandType.Move, 1, new[] { heli.Id }, here));
                    Run(world, 4f);
                    Assert.GreaterOrEqual(Vector2.Distance(heli.Position, here), 38f, "helicopters keep out");
                    break;
                }
                case "screen":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tower = world.SpawnVehicle("guard_tower", 0, new Vector2(10f, 0f), 0f);
                    tower.HoldFire = true;
                    Target(world, "main_battle_tank", 1, new Vector2(10f, 28f));
                    Run(world, 1f);
                    Assert.IsFalse(tower.IsSeenBy(1), "a tank 28 m off sees nothing");
                    Target(world, "scout_jeep", 1, new Vector2(10f, 40f));
                    Run(world, 1f);
                    Assert.IsTrue(tower.IsSeenBy(1), "a scout sees through it");
                    break;
                }
                case "jamProof":
                {
                    var carrier = world.SpawnVehicle(row.Id, 0, here, 0f);
                    Target(world, "main_battle_tank", 1, new Vector2(0f, 40f));
                    Target(world, "ew_jammer", 1, new Vector2(4f, 44f));
                    var fired = 0;
                    var jammed = 0;
                    Run(world, 14f, e =>
                    {
                        if (e.Kind != SimEventKind.WeaponFired || e.Entity != carrier.Id) return;
                        fired++;
                        if (e.Jammed) jammed++;
                    });
                    Assert.Greater(fired, 0);
                    Assert.AreEqual(0, jammed, "never jammed");
                    break;
                }
                case "rotors":
                {
                    var hunter = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var jet = Target(world, "fighter_jet", 1, new Vector2(0f, 40f));
                    Assert.AreEqual(0, ShotsAt(world, hunter, jet, new Vector2(0f, 40f), 5f), "a jet is no prey");
                    jet.Hp = 0f;
                    var heli = Target(world, "attack_helicopter", 1, new Vector2(0f, 40f));
                    Assert.Greater(ShotsAt(world, hunter, heli, new Vector2(0f, 40f), 5f), 0, "a helicopter is");
                    break;
                }
                case "shelter":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var tank = Target(world, "main_battle_tank", 0, new Vector2(10f, 0f));
                    var other = Target(world, "main_battle_tank", 0, new Vector2(60f, 0f));
                    Run(world, 0.1f);
                    Assert.AreEqual(0.5f, Hit(world, tank, "howitzer", new Vector2(10f, 80f)) / Hit(world, other, "howitzer", new Vector2(60f, 80f)), 0.01f, "half from shells");
                    Assert.AreEqual(Hit(world, other, "gun_120mm", new Vector2(60f, 40f)), Hit(world, tank, "gun_120mm", new Vector2(10f, 40f)), 0.01f, "not direct fire");
                    break;
                }
                case "flares":
                {
                    world.SpawnVehicle(row.Id, 0, here, 0f);
                    var jet = Target(world, "stealth_fighter", 1, new Vector2(0f, 30f));
                    Run(world, 3f);
                    Assert.IsFalse(jet.IsVisibleTo(0), "by day no flare");
                    world.SetDarkness(true);
                    Run(world, 2f);
                    Assert.IsTrue(jet.IsVisibleTo(0), "a flare ahead shows it");
                    break;
                }
                case "drones":
                {
                    var laser = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var heli = Target(world, "attack_helicopter", 1, new Vector2(0f, 30f));
                    Assert.AreEqual(0, ShotsAt(world, laser, heli, new Vector2(0f, 30f), 3f), "no helicopter");
                    heli.Hp = 0f;
                    var drone = Target(world, "recon_drone", 1, new Vector2(0f, 30f));
                    Assert.Greater(ShotsAt(world, laser, drone, new Vector2(0f, 30f), 3f), 0, "a drone");
                    Assert.IsTrue(laser.Def.Aps.Laser && laser.Def.Aps.Rockets, "interceptors for rockets, blinded by smoke");
                    break;
                }
                default:
                    Assert.Fail("no check for " + row.Mechanism);
                    break;
            }
        }
    }
}
