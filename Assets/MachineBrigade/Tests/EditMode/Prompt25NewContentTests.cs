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
            new Row("aa_gun_vehicle", 1000, 5, 1, -1, "bofors_l70", 30, 48, 75, "air"),
            new Row("recoilless_jeep", 350, 3, 0, -1, "recoilless_106", 220, 32, 33, "ambush"),
            new Row("sp_mortar", 1200, 5, 2, -1, "amos_120", 150, 60, -1, "mrsi"),
            new Row("blast_wall", 3000, 0, 3, -1, "none", -1, -1, -1, "wall"),
            new Row("fire_control_centre", 2500, 0, 1, 40, "none", -1, -1, -1, "link"),
            new Row("barrage_balloon", 800, 0, 0, -1, "none", -1, -1, -1, "balloon"),
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
            // Prompt 32 L1: a tower folded into another card or retired from the roster is no longer sold.
            if (!CardMerges.TowerInto.ContainsKey(row.Id) && System.Array.IndexOf(CardMerges.RetiredTowers, row.Id) < 0)
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
                case "air":
                {
                    var gun = world.SpawnVehicle(row.Id, 0, here, 0f);
                    var heli = Target(world, "attack_helicopter", 1, new Vector2(0f, 44f));
                    Assert.Greater(ShotsAt(world, gun, heli, new Vector2(0f, 44f), 5f), 0, "a helicopter at 44 m");
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
                case "wall":
                {
                    var tower = world.SpawnVehicle("gun_turret", 0, here, 0f);
                    world.SpawnVehicle(row.Id, 0, new Vector2(0f, 6f), 0f);
                    Run(world, 0.1f);
                    Assert.AreEqual(0.7f, Hit(world, tower, "gun_120mm", new Vector2(0f, 40f)) / Hit(world, tower, "gun_120mm", new Vector2(0f, -40f)), 0.01f, "30 % less from its side");
                    Assert.AreEqual(Hit(world, tower, "howitzer", new Vector2(0f, -60f)), Hit(world, tower, "howitzer", new Vector2(0f, 60f)), 0.01f, "shells come over it");
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
