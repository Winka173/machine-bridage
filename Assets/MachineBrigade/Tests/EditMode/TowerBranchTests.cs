using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Bosses;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The tower-branch rework (DECISIONS 19T, F): each remade branch does what sets it apart, the two branches of every
    /// tower differ in what they hit, their reach band or a mechanism, the AI picks by the deck, the save migrates.
    /// </summary>
    public class TowerBranchTests
    {
        private const float Step = 0.05f;
        private static Catalog C => Lab.Catalog;

        private static void Run(SimWorld world, float seconds, System.Action<SimEvent> seen = null, System.Func<bool> until = null)
        {
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                if (seen != null) foreach (var e in world.Events) seen(e);
                world.ClearEvents();
                if (until != null && until()) break;
            }
        }

        private static Vehicle Tower(SimWorld world, string id, int team, Vector2 at)
        {
            var v = world.SpawnVehicle(id, team, at, 0f);
            world.AnchorDefence(v);
            return v;
        }

        private static Vehicle Dummy(SimWorld world, string id, int team, Vector2 at, float toughness = 50f)
        {
            var v = world.SpawnVehicle(id, team, at, System.MathF.PI);
            v.HpScale = toughness;
            v.Hp = v.MaxHp;
            v.Scripted = true;
            v.HoldFire = true;
            return v;
        }

        // ------------------------------------------------------------------ A.1: every pair differs in kind

        [Test]
        public void TheTwoBranchesOfEveryTowerDifferInTargetsReachOrMechanism()
        {
            var bad = new List<string>();
            foreach (var tower in TowerCards.All(C))
            {
                var branches = TowerCards.Branches(C, tower);
                if (branches.Count == 0) continue;
                if (branches.Count != 2) { bad.Add($"{tower}: {branches.Count} branches"); continue; }
                var a = C.Vehicles[branches[0]];
                var b = C.Vehicles[branches[1]];
                if (Kind(a) == Kind(b)) bad.Add($"{tower}: {a.Id} and {b.Id} differ only in numbers ({Kind(a)})");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        /// <summary>What a branch hits, its reach band and its mechanisms, as one string (numbers left out, bands kept).</summary>
        private static string Kind(VehicleDef d)
        {
            var weapons = d.Mounts.Select(m => m.Weapon).Where(w => w.Damage > 0f).ToList();
            var targets = weapons.Any(w => w.CanTarget(true)) ? weapons.Any(w => w.CanTarget(false)) ? "all" : "air" : weapons.Count > 0 ? "ground" : "none";
            var reach = weapons.Count == 0 ? "-" : weapons.Max(w => w.Range) switch { < 30f => "close", < 60f => "middle", _ => "far" };
            var mech = new List<string>();
            if (d.Aps is { } aps) mech.Add(aps.Heavy ? "aps-heavy" : aps.Direct ? "aps-direct" : "aps-lobbed");
            if (d.Dome != null) mech.Add("dome");
            if (d.Wards != null) mech.Add("wards");
            if (d.Loot != null) mech.Add("loot");
            if (d.Relay != null) mech.Add("relay");
            if (d.RevealAir > 0f) mech.Add("radar");
            if (d.CounterBattery != null) mech.Add("counter-battery");
            if (d.TowerRangeAura != null) mech.Add("range-aura");
            if (d.SlowAura != null) mech.Add("slow");
            if (d.Passable) mech.Add("passable");
            if (d.Jammer > 0f) mech.Add("jammer" + (d.Jammer > 35f ? "-wide" : ""));
            if (d.Mines is { } mines) mech.Add(mines.Max > 6 ? "mines-many" : "mines-few");
            if (weapons.Any(w => w.Indirect)) mech.Add("indirect");
            if (weapons.Any(w => w.AirRound != null)) mech.Add("air-burst");
            if (weapons.Any(w => w.DamageType == DamageType.Fire)) mech.Add("fire");
            if (weapons.Any(w => Armour.StrikesTop(w))) mech.Add("top");
            if (weapons.Any(w => w.Projectile == ProjectileKind.Drone && w.Bonuses.Any(bn => bn.Class == UnitClass.Artillery))) mech.Add("lancet");
            if (d.Mounts.Count >= 3) mech.Add("extra-guns");
            if (weapons.Any(w => w.Family == "autocannon" && w.Size >= 25f && w.CanTarget(false) && !w.CanTarget(true))) mech.Add("cannon");
            if (weapons.Any(w => w.Family == "mg" && w.Burst == 1 && d.Mounts.Count(m => m.Weapon.Family == "mg") >= 1 && w.Id.Contains("twin"))) mech.Add("twin");
            return $"{targets}/{reach}/{string.Join("+", mech)}";
        }

        // ------------------------------------------------------------------ B.10 the gun turret

        [Test]
        public void TheAutocannonShootsAircraftWithItsAirBurstRoundAndTheSniperGunCannot()
        {
            foreach (var (branch, hits) in new[] { ("gun_turret.auto", true), ("gun_turret.long", false) })
            {
                var world = Lab.Field(5);
                world.RevealAll = true;
                var gun = Tower(world, branch, 0, Vector2.Zero);
                var heli = Dummy(world, "attack_helicopter", 1, new Vector2(0f, 28f));
                var dealt = 0f;
                var rounds = new HashSet<string>();
                DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
                {
                    if (by != gun || victim != heli) return;
                    dealt += amount;
                    if (weapon != null) rounds.Add(weapon.Id);
                };
                try { Run(world, 20f); }
                finally { DamageSystem.DamageLog = null; }
                if (hits)
                {
                    Assert.Greater(dealt, 200f, "the 57 mm hits the helicopter");
                    CollectionAssert.Contains(rounds, "gun_57_air", "with its air-burst round");
                    Assert.AreEqual(DamageType.Fragmentation, C.Weapons["gun_57_air"].DamageType);
                }
                else Assert.AreEqual(0f, dealt, 1e-3f, "the sniper gun does not shoot aircraft");
            }
            Assert.Greater(C.Weapons["turret_gun_120_long"].Range, C.Weapons["gun_120mm"].Range + 8f, "the sniper outranges a tank's gun");
            Assert.Greater(C.Weapons["turret_gun_120_long"].Penetration, C.Weapons["gun_57_auto"].Penetration, "and pierces more");
        }

        // ------------------------------------------------------------------ B.12 the emplacement

        [Test]
        public void TheHeavyMortarFiresOverAWallIntoTheYard()
        {
            // A walled yard: a ring of wall round the target.
            var walls = new List<PropPlacement>();
            for (var x = -12f; x <= 12f; x += 8f)
            {
                walls.Add(new PropPlacement("base_wall", new Vector2(x, 28f), 0));
                walls.Add(new PropPlacement("base_wall", new Vector2(x, 52f), 0));
            }
            foreach (var branch in new[] { "artillery_emplacement.mortar", "gun_turret.long" })
            {
                var world = new SimWorld(C, new MapDefinition("yard", 260f,
                    new[] { new TeamStart(0, new Vector2(0f, -120f)), new TeamStart(1, new Vector2(0f, 120f)) }, walls, new List<UnitPlacement>()), seed: 7);
                world.RevealAll = true;
                var gun = Tower(world, branch, 0, Vector2.Zero);
                var target = Dummy(world, "main_battle_tank", 1, new Vector2(0f, 40f));
                var dealt = 0f;
                DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (victim == target) dealt += amount; };
                try { Run(world, 40f); }
                finally { DamageSystem.DamageLog = null; }
                if (branch.EndsWith("mortar")) Assert.Greater(dealt, 300f, "the mortar's bombs come down inside the walls");
                else Assert.AreEqual(0f, dealt, 1e-3f, "a direct-fire gun cannot see over the wall");
            }
        }

        [Test]
        public void TheCounterBatteryHowitzerGoesForTheGunThatJustFired()
        {
            var world = Lab.Field(9);
            world.RevealAll = false;
            var cb = Tower(world, "artillery_emplacement.cb", 0, Vector2.Zero);
            // A spotter so both targets are seen; the tank is nearer.
            Dummy(world, "scout_jeep", 0, new Vector2(0f, 40f)).HoldFire = true;
            var tank = Dummy(world, "main_battle_tank", 1, new Vector2(0f, 45f));
            var gun = world.SpawnVehicle("artillery", 1, new Vector2(0f, 85f), System.MathF.PI);
            gun.Scripted = true;
            gun.HpScale = 50f;
            gun.Hp = gun.MaxHp;
            var bait = Dummy(world, "armored_car", 0, new Vector2(12f, 10f));
            world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, new[] { gun.Id }, bait.Position, bait.Id));
            var fired = -1.0;
            var onGun = false;
            Run(world, 60f, e =>
            {
                if (e.Kind == SimEventKind.WeaponFired && e.Entity == gun.Id && fired < 0) fired = world.Time;
            }, () =>
            {
                if (fired >= 0 && cb.MountTarget(0) == gun.Id) onGun = true;
                return onGun;
            });
            Assert.GreaterOrEqual(fired, 0.0, "the enemy gun fired");
            Assert.IsTrue(onGun, "the counter-battery howitzer turned on the gun that fired, not the nearer tank");
        }

        // ------------------------------------------------------------------ B.14 the Patriot

        [Test]
        public void ThePac3ShootsDownABossesMissileAndACruiseMissileStrikeButNoRockets()
        {
            var world = Lab.Field(3);
            world.BigAttackSettings = BigAttackSettings.For(C.BigAttackRules, "Normal");
            world.SetBoosts(0, _ => Lab.Harmless);
            var train = world.SpawnVehicle("nuke_train", 1, new Vector2(-100f, -100f), 0f);
            var aim = new Vector2(40f, 40f);
            for (var i = 0; i < 5; i++)
            {
                var v = Dummy(world, "main_battle_tank", 0, aim + new Vector2(i * 2f, 0f), 60f);
                v.Scripted = true;
            }
            Tower(world, "missile_battery.pac3", 0, aim + new Vector2(0f, -20f));
            var events = new List<SimEvent>();
            Run(world, 60f, e => events.Add(e), () => train.BigAttack.Stage == BigStage.Ready && train.BigAttack.LastStart > 1.0);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 1), "it launched");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 5), "the PAC-3 shot it down");

            // A cruise-missile strike over a PAC-3: shot down, nothing lands.
            var field = Lab.Field(4);
            var pac3 = Tower(field, "missile_battery.pac3", 0, Vector2.Zero);
            var hurt = Dummy(field, "main_battle_tank", 0, new Vector2(10f, 10f));
            var before = hurt.Hp;
            var intercepted = 0;
            field.Strikes.Launch(C.Supports["cruise_missile"], 1, new Vector2(10f, 10f), new Vector2(11f, 10f));
            Run(field, 8f, e => { if (e.Kind == SimEventKind.Intercepted) intercepted++; });
            Assert.AreEqual(1, intercepted, "the strike was met");
            Assert.AreEqual(before, hurt.Hp, 1e-3f, "nothing landed");

            // Rockets are the C-RAM's: the PAC-3 lets an MLRS's salvo through.
            var range = Lab.Field(6);
            range.RevealAll = true;
            var battery = Tower(range, "missile_battery.pac3", 0, Vector2.Zero);
            var hit = Dummy(range, "main_battle_tank", 0, new Vector2(6f, 0f));
            var mlrs = range.SpawnVehicle("mlrs", 1, new Vector2(0f, 90f), System.MathF.PI);
            range.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, new[] { mlrs.Id }, hit.Position, hit.Id));
            var stopped = 0;
            Run(range, 30f, e => { if (e.Kind == SimEventKind.Intercepted && e.Entity == battery.Id) stopped++; });
            Assert.AreEqual(0, stopped, "no rockets");
        }

        [Test]
        public void TheLongRangeRadarShowsEnemyAircraftFarBeyondItsSightAndThePac3DoesNot()
        {
            foreach (var (branch, sees) in new[] { ("missile_battery.lrr", true), ("missile_battery.pac3", false) })
            {
                var world = Lab.Field(2, 400f);
                world.RevealAll = false;
                Tower(world, branch, 0, Vector2.Zero);
                var jet = world.SpawnVehicle("attack_jet", 1, new Vector2(0f, 130f), 0f);
                jet.Scripted = true;
                Run(world, 1f);
                Assert.AreEqual(sees, jet.IsVisibleTo(0), branch);
            }
        }

        // ------------------------------------------------------------------ B.13 the heavy fortress

        [Test]
        public void TheSteelFortressCarriesTwoMachineGunTurretsAllRound()
        {
            var steel = C.Vehicles["heavy_turret.bastion"];
            var guns = steel.Mounts.Where(m => m.Weapon.Family == "mg" && m.Aim == MountAim.Free && m.Weapon.CanTarget(true) && m.Weapon.CanTarget(false)).ToList();
            Assert.AreEqual(2, guns.Count, "two 360-degree machine guns for cars and drones");
            Assert.Greater(steel.MaxHp, C.Vehicles["heavy_turret"].MaxHp);
            Assert.IsFalse(C.Vehicles["heavy_turret.coastal"].Mounts.Any(m => m.Aim == MountAim.Free && m.Weapon.Family == "mg"));
        }

        // ------------------------------------------------------------------ B.15 the shield generator

        [Test]
        public void TowerShieldsAreEachTowersOwnComeBackAndNeverAddToADome()
        {
            var world = Lab.Field(1);
            var ward = Tower(world, "shield_tower.ward", 0, Vector2.Zero);
            var a = Tower(world, "gun_turret", 0, new Vector2(10f, 0f));
            var b = Tower(world, "gun_turret", 0, new Vector2(-10f, 0f));
            a.HoldFire = b.HoldFire = true;
            Run(world, 0.5f);
            Assert.Greater(a.WardHp, 0f, "the tower has a shield of its own");
            Assert.AreEqual(ward.Id, a.WardFrom);
            var hpA = a.Hp;
            var full = a.WardHp;
            var hit = new HitInfo(null, 1, null, new Vector2(10f, 20f), HitKind.Direct, false);
            world.Damage.Apply(a, 300f, DamageType.Kinetic, hit);
            Assert.AreEqual(hpA, a.Hp, 1e-3f, "its shield took the hit");
            Assert.Less(a.WardHp, full);
            Assert.AreEqual(full, b.WardHp, 1e-3f, "the other tower's shield is its own, untouched");
            world.Damage.Apply(a, 200f, DamageType.Energy, hit);
            Assert.Less(a.Hp, hpA, "energy goes through");
            Run(world, C.Vehicles["shield_tower.ward"].Wards.Recharge + 0.5f);
            Assert.AreEqual(full, a.WardHp, 1e-3f, "back at full after a quiet spell");

            // Under a dome as well: the dome takes the hit, the tower's own shield is not spent on top of it.
            Tower(world, "shield_tower", 0, new Vector2(12f, 4f));
            Run(world, 0.5f);
            world.Damage.Apply(a, 300f, DamageType.Kinetic, hit);
            Assert.AreEqual(full, a.WardHp, 1e-3f, "never both");
            // A tower out of reach carries none.
            var far = Tower(world, "gun_turret", 0, new Vector2(60f, 0f));
            Run(world, 0.5f);
            Assert.AreEqual(0f, far.WardHp);
        }

        // ------------------------------------------------------------------ B.16 the CP relay

        [Test]
        public void TheLootDepotPaysForKillsNearItAndNeverPastTheCap()
        {
            var world = Lab.Field(1);
            world.EnableEconomy(new TeamEconomy(0, 0f, income: 0f, bank: 999f));
            world.EnableEconomy(new TeamEconomy(1, 0f, income: 0f, bank: 999f));
            Tower(world, "cp_relay.loot", 0, Vector2.Zero);
            world.TryGetEconomy(0, out var own);
            float Kill(Vector2 at, bool credited)
            {
                var before = own.Cp;
                var car = world.SpawnVehicle("armored_car", 1, at, 0f);
                var hit = new HitInfo(null, 0, null, at, HitKind.Direct, false);
                if (credited)
                {
                    car.LastAttackerTeam = 0;
                    car.LastHitTime = world.Time;
                }
                world.Damage.Apply(car, car.MaxHp * 5f, DamageType.HighExplosive, hit);
                Run(world, 0.1f);
                return (own.Cp - before) / car.Def.ArmyCost;
            }
            var share = C.Vehicles["cp_relay.loot"].Loot.Share;
            var near = Kill(new Vector2(20f, 0f), credited: false);
            Assert.AreEqual(share, near, 0.01f, "a kill near it pays its share of the price");
            Assert.AreEqual(0f, Kill(new Vector2(80f, 0f), credited: false), 0.01f, "one far off pays nothing");
            Assert.LessOrEqual(Kill(new Vector2(15f, 0f), credited: true), EconomySystem.KillRefundCap + 0.01f, "the kill's refund and the depot's together stay under the cap");
            Assert.IsNull(C.Vehicles["cp_relay.loot"].Relay, "and it pays no steady CP");
        }

        // ------------------------------------------------------------------ A.5 the AI

        [Test]
        public void TheAiPicksBranchesByTheDeckItFaces()
        {
            string Pick(string tower, params string[] deck)
            {
                var loadout = new BaseLoadout { HqLevel = 5 };
                loadout.Medium.Add(tower);
                BaseLoadout.ChooseAiBranches(C, loadout, deck);
                return loadout.Branches.TryGetValue(tower, out var b) ? b : null;
            }
            Assert.AreEqual("gun_turret.long", Pick("gun_turret", "main_battle_tank", "heavy_tank", "tank_destroyer", "twin_tank"));
            Assert.AreEqual("gun_turret.auto", Pick("gun_turret", "armored_car", "scout_jeep", "attack_helicopter", "strike_drone"));
            Assert.AreEqual("missile_battery.pac3", Pick("missile_battery", "ballistic_launcher", "heavy_bomber", "main_battle_tank"));
            Assert.AreEqual("missile_battery.lrr", Pick("missile_battery", "attack_helicopter", "attack_jet", "gunship_heli", "stealth_fighter"));
            Assert.AreEqual("shield_tower.bulwark", Pick("shield_tower", "artillery", "mlrs", "heavy_rocket_artillery", "mortar_carrier"));
            Assert.AreEqual("shield_tower.ward", Pick("shield_tower", "main_battle_tank", "heavy_tank", "tank_destroyer", "attack_helicopter"));
            Assert.AreEqual("cp_relay.loot", Pick("cp_relay", "armored_car", "scout_jeep", "vbied", "armored_car"));
            // A general's taste: Orlov (artillery) likes the counter-battery howitzer.
            var orlov = C.Base.Style("orlov");
            Assert.Greater(orlov["artillery_emplacement.cb"], 1f);
        }

        // ------------------------------------------------------------------ E the save

        [TearDown]
        public void Reset() => PlayerProfile.ResetForTests();

        [Test]
        public void ARemadeBranchMovesToTheNearestNewOneWithOneFreeChangeAndOneNotice()
        {
            PlayerProfile.LoadForTests(@"{ ""rosterVersion"": 3, ""coins"": 0,
                ""rankIds"": [ ""rocket_turret"", ""cp_relay"", ""guard_tower"" ], ""ranks"": [ 7, 7, 7 ], ""prints"": [ 0, 0, 0 ],
                ""branchTowers"": [ ""rocket_turret"", ""cp_relay"", ""guard_tower"" ],
                ""branchChoices"": [ ""rocket_turret.thermo"", ""cp_relay.express"", ""guard_tower.watch"" ] }");
            Assert.AreEqual("rocket_turret.guided", PlayerProfile.TowerBranch("rocket_turret"));
            Assert.AreEqual("cp_relay.loot", PlayerProfile.TowerBranch("cp_relay"));
            Assert.AreEqual("guard_tower.watch", PlayerProfile.TowerBranch("guard_tower"), "a kept branch stays");
            Assert.IsTrue(PlayerProfile.FreeBranchSwap("rocket_turret"));
            Assert.IsFalse(PlayerProfile.FreeBranchSwap("guard_tower"), "an untouched tower has no free change");
            var news = PlayerProfile.TakeBranchNews();
            CollectionAssert.AreEquivalent(new[] { "rocket_turret", "cp_relay" }, news);
            Assert.IsEmpty(PlayerProfile.TakeBranchNews(), "the notice shows once");
            // One free change (no coins), then the usual price.
            Assert.IsTrue(PlayerProfile.TryChooseBranch("rocket_turret", "rocket_turret.cluster"), "free");
            Assert.IsFalse(PlayerProfile.FreeBranchSwap("rocket_turret"));
            Assert.IsFalse(PlayerProfile.TryChooseBranch("rocket_turret", "rocket_turret.guided"), "the next change costs coins (none held)");
        }
    }
}
