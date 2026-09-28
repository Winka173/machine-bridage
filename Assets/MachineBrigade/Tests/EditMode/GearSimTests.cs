using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Equipment in battle, one family of hooks at a time, in small hand-built worlds: weapon
    /// copies, resistances, status effects, hit, kill, death, standing-still and target-change
    /// hooks, shots, defensive traits, set behaviours, modules and the proc events.
    /// </summary>
    public class GearSimTests
    {
        private static VehicleBoost Traits(params GearTrait[] traits) =>
            new(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, null, traits);

        private static VehicleBoost Stats(params (StatId stat, float value)[] lines)
        {
            var stats = new float[(int)StatId.Count];
            foreach (var (stat, value) in lines) stats[(int)stat] = value;
            return new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, stats);
        }

        private static VehicleBoost Module(SpecialModule module, float power, float power2 = 0f) =>
            new(1f, 1f, 1f, 1f, 1f, 0f, module, power, null, null, power2);

        /// <summary>A world where team 0's vehicles get <paramref name="boost"/>.</summary>
        private static SimWorld World(VehicleBoost boost)
        {
            var world = TestWorlds.World();
            world.SetBoosts(0, _ => boost);
            return world;
        }

        /// <summary>One round from the shooter's main weapon strikes the target now (no flight, no range check); returns what the target lost.</summary>
        private static float Shoot(SimWorld world, Vehicle shooter, Vehicle target, float scale = 1f)
        {
            var before = target.Hp;
            var p = new Projectile(shooter.Id, shooter.Team, shooter.Weapon, target.Position, target.Id, 0f)
            {
                Origin = shooter.Position, Shooter = shooter, Main = true, DamageScale = shooter.DamageBoost * scale,
            };
            world.Damage.ResolveImpact(p);
            return before - target.Hp;
        }

        private static float Hit(SimWorld world, Vehicle target, float amount, WeaponDef weapon, HitKind kind = HitKind.Direct, bool indirect = false)
        {
            var before = target.Hp;
            world.Damage.Apply(target, amount, weapon.DamageType, new HitInfo(null, 1, weapon, target.Position + new Vector2(0f, 5f), kind, indirect));
            return before - target.Hp;
        }

        private static List<SimEvent> Run(SimWorld world, float seconds)
        {
            var events = new List<SimEvent>();
            var steps = (int)(seconds / TestWorlds.Step + 0.5f);
            for (var i = 0; i < steps; i++)
            {
                world.Step(TestWorlds.Step);
                events.AddRange(world.Events);
                world.ClearEvents();
            }
            return events;
        }

        // ------------------------------------------------------------------ stat lines and weapon copies

        [Test]
        public void EquipmentTunesItsOwnWeaponCopyAndLeavesTheCatalogAlone()
        {
            var world = World(Stats((StatId.Range, 0.1f), (StatId.ProjectileSpeed, 0.2f), (StatId.TurretRate, 0.3f), (StatId.Vision, 0.2f)));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var plain = world.SpawnVehicle("tank", 1, new Vector2(0f, 30f), 0f);
            Assert.AreEqual(22f, tank.Weapon.Range, 1e-3f);
            Assert.AreEqual(120f, tank.Weapon.ProjectileSpeed, 1e-3f);
            Assert.AreEqual(1.3f, tank.TurretFactor, 1e-5f);
            Assert.AreEqual(1.2f, tank.VisionFactor, 1e-5f);
            Assert.AreSame(TestWorlds.Gun, plain.Weapon, "a vehicle without equipment keeps the shared weapon");
            Assert.AreEqual(20f, TestWorlds.Gun.Range, "the catalog's weapon is untouched");
            Assert.AreEqual("gun", tank.Weapon.Id, "the copy looks and sounds the same");

            // The longer barrel reaches a target the plain gun cannot (combat only, so nobody drives closer).
            float Fire(SimWorld w)
            {
                var gunner = w.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
                var mark = w.SpawnVehicle("decoy", 1, new Vector2(22.5f, 0f), 0f);
                w.Step(TestWorlds.Step);
                for (var i = 0; i < 40; i++)
                {
                    w.Combat.Step(TestWorlds.Step);
                    w.Damage.Step();
                }
                Assert.AreSame(TestWorlds.Gun, gunner.Def.Weapon);
                return mark.MaxHp - mark.Hp;
            }
            Assert.Greater(Fire(World(Stats((StatId.Range, 0.1f)))), 0f, "in reach at 22.5 m with +10 % range");
            Assert.AreEqual(0f, Fire(TestWorlds.World()), "out of reach for the plain gun");

            // Magazine and reload on a real rocket launcher.
            var real = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            real.SetBoosts(0, _ => Stats((StatId.Magazine, 0.25f), (StatId.MagazineReload, 0.2f)));
            var mlrs = real.SpawnVehicle("mlrs", 0, new Vector2(0f, 0f), 0f);
            var stock = real.Catalog.Vehicle("mlrs").Weapon;
            Assert.AreEqual(stock.Ammo + 1, mlrs.Ammo(0), "a bigger magazine, and it starts full");
            Assert.AreEqual(stock.MagazineReload * 0.8f, mlrs.Weapon.MagazineReload, 1e-3f);
        }

        [Test]
        public void ResistancesCutDamageByTypeProjectileAndIndirectFire()
        {
            var world = World(Stats((StatId.ResistArmorPiercing, 0.2f), (StatId.ResistRocket, 0.1f), (StatId.ResistIndirect, 0.15f), (StatId.ResistMine, 0.5f)));
            var armoured = world.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            var plain = world.SpawnVehicle("decoy", 1, new Vector2(20f, 0f), 0f);
            float Ratio(WeaponDef w, HitKind kind = HitKind.Direct, bool indirect = false) =>
                Hit(world, armoured, 100f, w, kind, indirect) / Hit(world, plain, 100f, w, kind, indirect);
            Assert.AreEqual(0.8f, Ratio(TestWorlds.Gun), 1e-3f, "armour-piercing resistance");
            Assert.AreEqual(0.7f, Ratio(TestWorlds.Missile), 1e-3f, "and the slat cage against missiles on top");
            Assert.AreEqual(0.85f, Ratio(TestWorlds.Howitzer, HitKind.Splash, true), 1e-3f, "the overhead screen against artillery");
            Assert.AreEqual(0.5f, Ratio(TestWorlds.Shell, HitKind.Mine), 1e-3f, "mine rollers");
        }

        // ------------------------------------------------------------------ status effects

        [Test]
        public void IncendiaryRoundsSetTheTargetOnFire()
        {
            var world = World(Traits(new GearTrait(TraitId.IncendiaryRounds, 0.2f)));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("decoy", 1, new Vector2(40f, 0f), 0f);
            var dealt = Shoot(world, shooter, target);
            Assert.Greater(dealt, 0f);
            Assert.IsTrue(world.Status.Burning(target));
            var burning = target.Hp;
            Run(world, 2f);
            Assert.AreEqual(dealt * 0.2f * 0.5f, burning - target.Hp, dealt * 0.01f, "half the burn (a fifth of the hit over 4 s) in 2 s");
            Run(world, 2.5f);
            Assert.IsFalse(world.Status.Burning(target), "and it burns out");
            Assert.AreEqual(dealt * 0.2f, burning - target.Hp, dealt * 0.01f);
        }

        [Test]
        public void SuppressionSlowsAndShredStacksFromEveryone()
        {
            var world = World(Traits(new GearTrait(TraitId.SuppressionRounds, 0.25f), new GearTrait(TraitId.ShredderRounds, 0.04f),
                new GearTrait(TraitId.LaserDesignator, 0.1f, 4f)));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("decoy", 1, new Vector2(40f, 0f), 0f);
            var plainTarget = world.SpawnVehicle("decoy", 1, new Vector2(40f, 20f), 0f);
            Shoot(world, shooter, target);
            Run(world, 0.1f);
            Assert.AreEqual(0.75f, target.SpeedGear, 1e-4f, "slowed by a quarter");
            Shoot(world, shooter, target);
            Shoot(world, shooter, target);
            // The proc coefficient: a gun firing once a second earns two thirds of a stack a hit.
            Assert.AreEqual(2, target.Statuses[(int)StatusKind.Shred].Stacks);
            // Anyone's hit (here with no attacker) lands 8 % harder on the shredded target.
            Assert.AreEqual(1.08f, Hit(world, target, 100f, TestWorlds.Gun) / Hit(world, plainTarget, 100f, TestWorlds.Gun), 1e-3f);
            Run(world, 2.5f);
            Assert.AreEqual(1f, target.SpeedGear, 1e-5f, "the slow wears off after 2 s");
            // The mark: the shooter's side hits the marked target 10 % harder, the other side does not.
            Shoot(world, shooter, plainTarget);
            var marked = plainTarget.Statuses[(int)StatusKind.Mark];
            Assert.AreEqual(0, marked.Team);
            var fromUs = world.Gear.Outgoing(shooter, plainTarget, new HitInfo(shooter, 0, TestWorlds.Gun, shooter.Position, HitKind.Direct, false));
            var fromThem = world.Gear.Outgoing(shooter, plainTarget, new HitInfo(shooter, 1, TestWorlds.Gun, shooter.Position, HitKind.Direct, false));
            Assert.AreEqual(1.1f, fromUs, 1e-5f);
            Assert.AreEqual(1f, fromThem, 1e-5f);
        }

        [Test]
        public void AnAegisBarrierSoaksDamageBeforeHealth()
        {
            var world = World(Traits(new GearTrait(TraitId.AegisBarrier, 0.1f, 20f)));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            Run(world, 0.1f);
            Assert.AreEqual(tank.MaxHp * 0.1f, tank.Barrier, 1e-3f);
            Hit(world, tank, 20f, TestWorlds.Gun);
            Assert.AreEqual(tank.MaxHp, tank.Hp, 1e-3f, "the barrier took it");
            Assert.AreEqual(tank.MaxHp * 0.1f - 20f, tank.Barrier, 1e-3f);
            Hit(world, tank, 100f, TestWorlds.Gun);
            Assert.AreEqual(0f, tank.Barrier, 1e-5f);
            Assert.AreEqual(tank.MaxHp - (100f - (tank.MaxHp * 0.1f - 20f)), tank.Hp, 1e-2f, "the rest goes through");
        }

        // ------------------------------------------------------------------ hit hooks

        [Test]
        public void RicochetShellsBounceToTheNextEnemy()
        {
            var world = World(Traits(new GearTrait(TraitId.RicochetShells, 0.5f, 10f)));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var first = world.SpawnVehicle("decoy", 1, new Vector2(40f, 0f), 0f);
            var second = world.SpawnVehicle("decoy", 1, new Vector2(40f, 6f), 0f);
            var far = world.SpawnVehicle("decoy", 1, new Vector2(40f, 30f), 0f);
            // A gun firing once a second earns two thirds of a bounce a hit: the second hit bounces.
            var dealt = Shoot(world, shooter, first);
            Run(world, 0.5f);
            Assert.AreEqual(second.MaxHp, second.Hp, "not yet a whole bounce");
            first.Hp = first.MaxHp;
            dealt = Shoot(world, shooter, first);
            var events = Run(world, 0.5f);
            // Half the damage of the hits that earned it (one and a half hits' worth: 1 / (2/3)), striking the
            // second from where the first stood (armour facing).
            var bounced = TestWorlds.Gun.Damage * 0.5f * 1.5f * DamageSystem.FacingFactor(second, first.Position);
            Assert.AreEqual(bounced, second.MaxHp - second.Hp, 1e-2f, "half the earning hits' damage bounces on to the nearest enemy");
            Assert.AreEqual(TestWorlds.Gun.Damage * DamageSystem.FacingFactor(first, shooter.Position), dealt, 1e-2f);
            Assert.AreEqual(far.MaxHp, far.Hp, "only one bounce, to the nearest");
            Assert.AreEqual(first.MaxHp - dealt, first.Hp, 1e-3f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "ricochet_shells"), "the RICOCHET word");
        }

        // ------------------------------------------------------------------ kill and death hooks

        [Test]
        public void KillsReloadHealAndPayMore()
        {
            var world = World(new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.WarProfiteer, 0.5f, null,
                new[] { new GearTrait(TraitId.KillReload, 0.25f), new GearTrait(TraitId.SalvageTeam, 0.1f) }));
            world.EnableEconomy(new TeamEconomy(0, startCp: 0f, income: 0f, bank: 100f));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var victim = world.SpawnVehicle("boomer", 1, new Vector2(40f, 0f), 0f);
            shooter.Hp = shooter.MaxHp * 0.5f;
            shooter.Cooldown = 5f;
            Shoot(world, shooter, victim);
            Assert.IsFalse(victim.IsAlive);
            Assert.AreEqual(3f, shooter.Cooldown, 1e-4f, "Kill Reload: two seconds off the reload");
            Assert.AreEqual(shooter.MaxHp * 0.6f, shooter.Hp, 1e-2f, "Salvage Team: a tenth of its health back");
            world.TryGetEconomy(0, out var economy);
            Assert.AreEqual(4 * 0.25f * 1.5f, economy.Cp, 1e-3f, "War Profiteer: half as much again for the kill");
            Run(world, 0.1f);
            Assert.AreEqual(1.25f, shooter.FireGear, 1e-5f, "and fires faster for a while");
        }

        [Test]
        public void DeathTraitsBlowUpStunAndCrown()
        {
            var world = World(Traits(new GearTrait(TraitId.VolatileFuelTanks, 0.3f, 8f)));
            var victim = world.SpawnVehicle("mortar", 0, new Vector2(0f, 0f), 0f);
            var friend = world.SpawnVehicle("decoy", 0, new Vector2(4f, 0f), 0f);
            var enemy = world.SpawnVehicle("decoy", 1, new Vector2(-4f, 0f), 0f);
            friend.Gear = null;
            world.Damage.Apply(victim, 10000f, DamageType.HighExplosive);
            Assert.IsFalse(victim.IsAlive);
            var events = Run(world, 0.4f);
            Assert.Less(enemy.Hp, enemy.MaxHp, "the fuel blast hurts the enemy");
            Assert.AreEqual(friend.MaxHp, friend.Hp, "and spares its own side");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.Explosion));

            var emp = World(Module(SpecialModule.EmpPayload, 2f, 10f));
            var carrier = emp.SpawnVehicle("mortar", 0, new Vector2(0f, 0f), 0f);
            var tank = emp.SpawnVehicle("tank", 1, new Vector2(6f, 0f), 0f);
            emp.Damage.Apply(carrier, 10000f, DamageType.HighExplosive);
            Run(emp, 0.1f);
            Assert.IsTrue(tank.Stunned, "EMP Payload: the enemy nearby is knocked out");
            Run(emp, 2.2f);
            Assert.IsFalse(tank.Stunned);

            var crown = World(Traits(new GearTrait(TraitId.DarkCrown, 0.04f, 0.03f)));
            var king = crown.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var doomed = crown.SpawnVehicle("boomer", 1, new Vector2(15f, 0f), 0f);
            king.Hp = king.MaxHp * 0.5f;
            crown.Damage.Apply(doomed, 10000f, DamageType.HighExplosive);
            Assert.AreEqual(1, king.Gear.CrownStacks);
            Assert.AreEqual(king.MaxHp * 0.53f, king.Hp, 1e-2f, "Dark Crown heals a little for a death nearby");
        }

        // ------------------------------------------------------------------ standing still

        [Test]
        public void StandingStillDigsIn()
        {
            var world = World(Traits(new GearTrait(TraitId.HullDownCrew, 0.15f), new GearTrait(TraitId.SiegeAnchor, 0.2f, 0.1f)));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var plain = world.SpawnVehicle("tank", 1, new Vector2(40f, 40f), 0f);
            Run(world, 1f);
            Assert.AreEqual(1f, tank.FireGear, 1e-5f, "not yet");
            Run(world, 1.5f);
            Assert.AreEqual(1.15f, tank.FireGear, 1e-5f, "Hull-Down Crew after 2 s still");
            Assert.IsFalse(tank.Gear.Anchored);
            Run(world, 1f);
            Assert.IsTrue(tank.Gear.Anchored, "Siege Anchor after 3 s");
            Assert.AreEqual(1.1f, tank.RangeFactor, 1e-5f);
            Assert.AreEqual(0.8f, Hit(world, tank, 100f, TestWorlds.Gun) / Hit(world, plain, 100f, TestWorlds.Gun), 1e-3f);
            // Ordered away, it needs a second to pull the anchor up.
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 0, new[] { tank.Id }, new Vector2(20f, 0f)));
            var start = tank.Position;
            Run(world, 0.8f);
            Assert.Less(Vector2.Distance(start, tank.Position), 0.01f, "still pulling the anchor up");
            Run(world, 1.5f);
            Assert.Greater(Vector2.Distance(start, tank.Position), 1f, "then away");
            Assert.AreEqual(1f, tank.FireGear, 1e-5f, "moving: no hull-down bonus");
        }

        // ------------------------------------------------------------------ shots and target changes

        private static List<float> DamageTo(List<SimEvent> events, Vehicle target) =>
            events.Where(e => e.Kind == SimEventKind.Damaged && e.Entity == target.Id).Select(e => e.Value).ToList();

        [Test]
        public void OpeningSalvoHitsTheFirstShotHarder()
        {
            var world = World(Traits(new GearTrait(TraitId.OpeningSalvo, 0.5f)));
            world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var hits = DamageTo(Run(world, 3.5f), target);
            Assert.GreaterOrEqual(hits.Count, 3);
            Assert.AreEqual(1.5f, hits[0] / hits[1], 1e-3f, "the first shot at a new target");
            Assert.AreEqual(hits[1], hits[2], 1e-3f, "later shots are plain");
        }

        [Test]
        public void TwinFeedAndHeavyRoundsChangeTheShots()
        {
            var world = World(Traits(new GearTrait(TraitId.TwinFeed, 0.1f, 0.2f)));
            world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var plainWorld = TestWorlds.World();
            plainWorld.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var plainTarget = plainWorld.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var twin = DamageTo(Run(world, 3.5f), target);
            var plain = DamageTo(Run(plainWorld, 3.5f), plainTarget);
            // A one-round gun: every round a fifth harder, no second round (prompt 8 I.2).
            Assert.AreEqual(plain[0] * 1.2f, twin[0], 1e-2f, "each round a fifth harder");
            Assert.AreEqual(plain.Count, twin.Count, "no extra round on a one-round gun");

            var heavy = World(Traits(new GearTrait(TraitId.OverpressureChamber, 4f)));
            heavy.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var anvil = heavy.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var shots = DamageTo(Run(heavy, 5.5f), anvil);
            Assert.GreaterOrEqual(shots.Count, 5);
            Assert.AreEqual(shots[0], shots[1], 1e-3f);
            Assert.AreEqual(1.5f, shots[3] / shots[0], 1e-2f, "every fourth shot of Overpressure Chamber hits half again as hard");
        }

        // ------------------------------------------------------------------ defensive traits

        [Test]
        public void ArmourTraitsBlockBounceSoakAndSurvive()
        {
            var world = World(Traits(new GearTrait(TraitId.ReactiveBlocks, 2f, 20f), new GearTrait(TraitId.AngledGlacis, 5f),
                new GearTrait(TraitId.Unbreakable, 2f)));
            var tank = world.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            var hits = new List<float>();
            for (var i = 0; i < 5; i++) hits.Add(Hit(world, tank, 100f, TestWorlds.Gun));
            Assert.AreEqual(50f, hits[0], 1e-3f, "a reactive block halves the hit");
            Assert.AreEqual(50f, hits[1], 1e-3f);
            Assert.AreEqual(100f, hits[2], 1e-3f, "until the blocks are used up");
            Assert.AreEqual(0f, hits[4], 1e-3f, "Angled Glacis: the fifth hit bounces off");

            tank.Hp = 10f;
            Hit(world, tank, 5000f, TestWorlds.Gun);
            Assert.AreEqual(1f, tank.Hp, 1e-3f, "Unbreakable: the killing blow leaves it on 1 HP");
            Assert.AreEqual(0f, Hit(world, tank, 5000f, TestWorlds.Gun), "and untouchable for a moment");
            Run(world, 2.2f);
            Hit(world, tank, 5000f, TestWorlds.Gun);
            Assert.IsFalse(tank.IsAlive, "but only once a life");

            var layer = World(Traits(new GearTrait(TraitId.AblativeLayer, 0.2f)));
            var soaked = layer.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(30f, Hit(layer, soaked, 60f, TestWorlds.Gun), 1e-3f, "the ablative layer halves the first 60 hp (a fifth of 300)");
            Assert.AreEqual(60f, Hit(layer, soaked, 60f, TestWorlds.Gun), 1e-3f, "then it is gone");
        }

        [Test]
        public void AGuardianTakesItsShareOfALightAllysDamage()
        {
            var world = World(Traits(new GearTrait(TraitId.GuardianLink, 0.25f)));
            var guardian = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var light = world.SpawnVehicle("mortar", 0, new Vector2(5f, 0f), 0f);
            light.Gear = null;
            Run(world, 0.1f);
            var taken = Hit(world, light, 100f, TestWorlds.Shell);
            Assert.AreEqual(75f, taken, 1e-3f, "the light vehicle takes three quarters");
            Assert.AreEqual(guardian.MaxHp - 25f, guardian.Hp, 1e-3f, "the guardian the rest");
        }

        // ------------------------------------------------------------------ set behaviours

        [Test]
        public void SetBehavioursWork()
        {
            var world = World(Traits(new GearTrait(TraitId.SetBulwark, 0.15f), new GearTrait(TraitId.SetHitAndRun, 0.2f, 0.5f),
                new GearTrait(TraitId.SetSalvageRights, 0.2f, 0.1f)));
            world.EnableEconomy(new TeamEconomy(0, startCp: 0f, income: 0f, bank: 100f));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var plain = world.SpawnVehicle("tank", 1, new Vector2(40f, 40f), 0f);
            Run(world, 2.5f);
            Assert.AreEqual(0.85f, Hit(world, tank, 100f, TestWorlds.Gun) / Hit(world, plain, 100f, TestWorlds.Gun), 1e-3f, "Bulwark after 2 s still");
            var victim = world.SpawnVehicle("boomer", 1, new Vector2(15f, 0f), 0f);
            Run(world, 1.5f);
            Assert.IsFalse(victim.IsAlive, "it shot the boomer");
            Assert.Greater(tank.SpeedGear, 1.19f, "Hit and Run: faster after firing");
            world.TryGetEconomy(0, out var economy);
            Assert.AreEqual(4 * 0.25f * 1.2f, economy.Cp, 1e-3f, "Salvage Rights: a fifth more for the kill");
            world.Damage.Apply(tank, 100000f, DamageType.HighExplosive);
            Assert.AreEqual(4 * 0.25f * 1.2f + 4 * 0.1f, economy.Cp, 1e-3f, "and a tenth of its own cost back when it falls");

            var heavy = World(Traits(new GearTrait(TraitId.SetHeavyRound, 3f, 1f)));
            heavy.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var anvil = heavy.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var shots = DamageTo(Run(heavy, 3.5f), anvil);
            Assert.AreEqual(2f, shots[2] / shots[0], 1e-2f, "Hammerfall: every third shot here doubles");
        }

        // ------------------------------------------------------------------ modules and timers

        [Test]
        public void ModulesFireOnTheirTriggers()
        {
            var world = World(Module(SpecialModule.DroneEscort, 2f, 20f));
            world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("decoy", 1, new Vector2(25f, 0f), 0f);
            var events = Run(world, 7f);
            Assert.AreEqual(2, events.Count(e => e.Kind == SimEventKind.WeaponFired && e.DefId == "gear_drone"), "two drones after 4 s");
            Assert.Less(target.Hp, target.MaxHp, "and they strike");

            var trophy = World(Module(SpecialModule.TrophyAps, 2f, 20f));
            var guarded = trophy.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(2, guarded.ApsCharges, "a Trophy module brings its interceptors");
            trophy.SpawnVehicle("hunter", 1, new Vector2(0f, 25f), 0f);
            var shot = Run(trophy, 6f);
            Assert.GreaterOrEqual(shot.Count(e => e.Kind == SimEventKind.Intercepted), 1, "and shoots down a missile");

            var rapid = World(Traits(new GearTrait(TraitId.RapidResponse, 1.5f, 18f), new GearTrait(TraitId.EmergencyRepairKit, 0.3f)));
            var tank = rapid.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            rapid.SpawnVehicle("aa", 1, new Vector2(12f, 0f), 0f);
            tank.Hp = tank.MaxHp * 0.35f;
            Run(rapid, 1.5f);
            Assert.IsTrue(tank.Barraging, "Rapid Response: fires faster once hit");
            Assert.Greater(tank.HealUntil, rapid.Time, "Emergency Repair Kit below 40 % health");
        }

        [Test]
        public void DamageControlClearsBurnsAndProcsAreThrottled()
        {
            var world = World(Traits(new GearTrait(TraitId.DamageControl, 10f)));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            world.Status.Burn(tank, 20f, 4f, 1, default);
            var events = Run(world, 0.1f);
            Assert.IsFalse(world.Status.Burning(tank), "Damage Control puts the fire out");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "damage_control"));
            world.Status.Burn(tank, 20f, 4f, 1, default);
            Assert.IsFalse(world.Status.Burning(tank), "and keeps it off for 2 s");

            // A proc word shows at most once every two seconds per vehicle.
            var noisy = World(Traits(new GearTrait(TraitId.SuppressionRounds, 0.2f)));
            noisy.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            noisy.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var procs = Run(noisy, 5f).Where(e => e.Kind == SimEventKind.TraitProc).Select(e => e.DefId).ToList();
            Assert.That(procs.Count, Is.InRange(2, 3), string.Join(",", procs));
            Assert.IsTrue(procs.All(p => p == "suppression_rounds"));
        }

        [Test]
        public void GhillieHidesAStillVehicleAndTheFirstShotHitsHarder()
        {
            var world = World(Traits(new GearTrait(TraitId.GhillieMode, 0.4f, 3f)));
            // The watcher sees further (45 m) than the sniper (30 m), so the sniper has nothing to drive at.
            world.SetBoosts(1, _ => Stats((StatId.Vision, 0.5f)));
            var sniper = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var watcher = world.SpawnVehicle("decoy", 1, new Vector2(35f, 0f), 0f);
            Run(world, 0.5f);
            Assert.IsTrue(sniper.IsVisibleTo(1), "seen at first");
            Run(world, 3f);
            Assert.IsTrue(sniper.Gear.Hidden);
            Assert.IsFalse(sniper.IsVisibleTo(1), "hidden beyond 8 m after 3 s still and silent");
            Assert.IsNotNull(watcher);
        }
    }
}
