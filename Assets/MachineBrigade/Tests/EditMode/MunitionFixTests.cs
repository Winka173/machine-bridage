using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Fix prompt L4 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): munition behaviour by the rules A-G with the shipped data:
    /// guided rounds land on a target that drove off, unguided rockets lead a moving tank, flares decoy IR missiles only and
    /// a decoyed missile bursts beside its flare, a guided round out of its reach self-destructs, the shot clock keeps a
    /// drawn round on the Sim's time. Written, not run (the owner's rule).
    /// </summary>
    public class MunitionFixTests
    {
        private static Catalog Shipped => GameContent.LoadCatalog();

        private static SimWorld Field(Catalog c) =>
            new SimWorld(c, new MapDefinition("field", 300f,
                new[] { new TeamStart(0, new Vector2(-120f, -120f)), new TeamStart(1, new Vector2(120f, 120f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), 11);

        [Test]
        public void TheRulesComeFromTheirOwnBlock()
        {
            var c = Shipped;
            var m = c.Munitions;
            Assert.AreEqual(7f, m.ProximityFuze, 1e-4f, "proximity fuze");
            Assert.GreaterOrEqual(m.FlareOffset, m.ProximityFuze + 2f, "a decoyed missile bursts outside its fuze");
            Assert.IsTrue(m.IsSightGuided(c.Weapons["atgm_heavy"]), "Kornet: beam riding");
            Assert.IsTrue(m.IsSightGuided(c.Weapons["heli_atgm"]), "Hellfire: laser");
            Assert.IsFalse(m.IsSightGuided(c.Weapons["hellfire_standoff"]), "Hellfire Longbow: fire and forget");
            Assert.IsTrue(m.IsRadarGuided(c.Weapons["patriot"]), "Patriot");
            Assert.IsFalse(m.IsRadarGuided(c.Weapons["stinger_atas"]), "Stinger");
            Assert.AreEqual(4, m.FlaresFighter.min);
            Assert.AreEqual(16, m.FlaresLarge.max);
        }

        [Test]
        public void FlaresTakeInfraRedMissilesOnly()
        {
            var c = Shipped;
            Assert.IsTrue(CombatSystem.FlareTakes(c.Weapons["stinger_atas"], c.Munitions), "Stinger");
            Assert.IsTrue(CombatSystem.FlareTakes(c.Weapons["r60"], c.Munitions), "R-60");
            Assert.IsFalse(CombatSystem.FlareTakes(c.Weapons["air_to_air"], c.Munitions), "AMRAAM: radar");
            Assert.IsFalse(CombatSystem.FlareTakes(c.Weapons["sam_48n6"], c.Munitions), "48N6: radar");
            Assert.IsFalse(CombatSystem.FlareTakes(c.Weapons["fighter_cannon"], c.Munitions), "a gun");
        }

        [Test]
        public void GuidedRocketsHomeAndUnguidedOnesLead()
        {
            var c = Shipped;
            Assert.IsTrue(c.Weapons["apkws_rocket"].GuidedRocket, "APKWS");
            Assert.IsTrue(CombatSystem.Homes(c.Weapons["apkws_rocket"]));
            Assert.IsFalse(CombatSystem.Leads(c.Weapons["apkws_rocket"], false));
            Assert.IsTrue(CombatSystem.Leads(c.Weapons["heli_rockets"], false), "Hydra");
            Assert.IsFalse(CombatSystem.Leads(c.Weapons["hellfire_standoff"], false), "a missile homes instead");
            Assert.IsFalse(CombatSystem.Leads(c.Weapons["heli_rockets"], true), "a free-falling stick falls where its drop puts it");
        }

        [Test]
        public void UnguidedRocketsAimWhereAMovingTankWillBe()
        {
            var c = Shipped;
            var world = Field(c);
            var heli = world.SpawnVehicle("attack_helicopter", 0, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 30f), System.MathF.PI * 0.5f);
            tank.Speed = 8f;
            var rockets = c.Weapons["heli_rockets"];
            var lead = CombatSystem.LeadPoint(heli, tank, rockets, c.Munitions.LeadCap);
            var flight = Vector2.Distance(heli.Position, lead) / rockets.ProjectileSpeed;
            var expected = tank.Position + MachineBrigade.Sim.Core.SimMath.Forward(tank.Heading) * tank.Speed * flight;
            Assert.Less(Vector2.Distance(lead, expected), 0.5f, "the lead is the tank's motion over the rocket's flight");
            Assert.Greater(Vector2.Distance(lead, tank.Position), 3f, "well ahead of where the tank is");
            tank.Speed = 0f;
            Assert.AreEqual(tank.Position, CombatSystem.LeadPoint(heli, tank, rockets, c.Munitions.LeadCap), "a still tank: its own spot");
        }

        [Test]
        public void AGuidedMissileLandsOnATankThatDroveOff()
        {
            var c = Shipped;
            var world = Field(c);
            var heli = world.SpawnVehicle("attack_helicopter", 0, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("light_tank", 1, new Vector2(0f, 40f), System.MathF.PI * 0.5f);
            var missile = c.Weapons["hellfire_standoff"];
            var p = new Projectile(heli.Id, heli.Team, missile, tank.Position, tank.Id, 2f)
            {
                Origin = heli.Position, Shooter = heli, Main = true, LaunchedAt = world.Time,
            };
            // It drove 14 m on while the missile flew (still inside its reach).
            tank.Position += new Vector2(14f, 0f);
            var before = tank.Hp;
            world.Damage.ResolveImpact(p);
            Assert.Less(tank.Hp, before, "the missile followed it");
        }

        [Test]
        public void ADecoyedMissileBurstsBesideItsFlareAndSparesTheAircraft()
        {
            var c = Shipped;
            var world = Field(c);
            var shooter = world.SpawnVehicle("aa_vehicle", 1, new Vector2(0f, -40f), 0f);
            var jet = world.SpawnVehicle("fighter_jet", 0, new Vector2(0f, 20f), 0f);
            var p = new Projectile(shooter.Id, shooter.Team, c.Weapons["stinger_atas"], jet.Position, jet.Id, 1.5f, targetFlying: true)
            {
                Origin = shooter.Position, Shooter = shooter, LaunchedAt = world.Time,
                Diverted = Divert.Flare, DivertAt = jet.Position + new Vector2(-8f, -7f),
            };
            var before = jet.Hp;
            world.ClearEvents();
            world.Damage.ResolveImpact(p);
            Assert.AreEqual(before, jet.Hp, 1e-3f, "no damage to the aircraft it lost");
            var burst = false;
            foreach (var e in world.Events)
                if (e.Kind == SimEventKind.ProjectileImpact && e.Airborne && Vector2.Distance(e.Position, p.DivertAt) < 0.01f) burst = true;
            Assert.IsTrue(burst, "it bursts in the air at its flare, with its effect and sound (an impact event there)");
        }

        [Test]
        public void AGuidedRoundSelfDestructsOnceItsTargetIsOutOfReach()
        {
            var c = Shipped;
            var world = Field(c);
            var heli = world.SpawnVehicle("attack_helicopter", 0, Vector2.Zero, 0f);
            world.MakeSparring(heli);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 50f), 0f);
            var missile = c.Weapons["hellfire_standoff"];
            var p = new Projectile(heli.Id, heli.Team, missile, tank.Position, tank.Id, 3f)
            {
                Origin = heli.Position, Shooter = heli, Main = true, LaunchedAt = world.Time,
            };
            world.Combat.AddProjectile(p);
            // Far beyond range x reachScale from where it left.
            tank.Position = new Vector2(0f, missile.Range * c.Munitions.ReachScale + 30f);
            world.ClearEvents();
            world.Step(TestWorlds.Step);
            Assert.AreEqual(Divert.Reach, p.Diverted, "diverted on the tick it got out of reach");
            Assert.LessOrEqual(Vector2.Distance(p.Origin, p.DivertAt), missile.Range * c.Munitions.ReachScale + 0.5f, "at the end of its reach");
            var told = false;
            foreach (var e in world.Events)
                if (e.Kind == SimEventKind.RoundDiverted && e.Other == tank.Id && e.Mount == (int)Divert.Reach) told = true;
            Assert.IsTrue(told, "the view is told");
        }

        [Test]
        public void OneFlareCloudDecoysTheWholeSalvoOrNone()
        {
            // Play-test 13 (lane C): a flare cloud seduces every IR seeker arriving inside its window on its one roll, so a
            // salvo arriving together is all decoyed or all flies true; a missile still far out is left for the next release.
            var c = Shipped;
            for (var seed = 1; seed <= 8; seed++)
            {
                var world = new SimWorld(c, new MapDefinition("field", 300f,
                    new[] { new TeamStart(0, new Vector2(-120f, -120f)), new TeamStart(1, new Vector2(120f, 120f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>()), seed);
                var shooter = world.SpawnVehicle("aa_vehicle", 1, new Vector2(0f, -40f), 0f);
                var jet = world.SpawnVehicle("fighter_jet", 0, new Vector2(0f, 20f), 0f);
                jet.FlaresUntil = world.Time + 3.0;
                var salvo = new List<Projectile>();
                for (var k = 0; k < 3; k++)
                {
                    var round = new Projectile(shooter.Id, shooter.Team, c.Weapons["stinger_atas"], jet.Position, jet.Id, 1f + 0.1f * k, targetFlying: true)
                        { Origin = shooter.Position, Shooter = shooter, LaunchedAt = world.Time };
                    salvo.Add(round);
                    world.Combat.AddProjectile(round);
                }
                var far = new Projectile(shooter.Id, shooter.Team, c.Weapons["stinger_atas"], jet.Position, jet.Id, 9f, targetFlying: true)
                    { Origin = shooter.Position, Shooter = shooter, LaunchedAt = world.Time };
                world.Combat.AddProjectile(far);
                world.Step(TestWorlds.Step);
                foreach (var round in salvo)
                {
                    Assert.IsTrue(round.FlareRolled, $"seed {seed}: a missile inside the cloud's window meets it");
                    Assert.AreEqual(salvo[0].Diverted, round.Diverted, $"seed {seed}: one cloud, one outcome for the salvo");
                }
                Assert.IsFalse(far.FlareRolled, $"seed {seed}: a missile 9 s out is not tested by this cloud");
            }
        }

        [Test]
        public void OneApsActivationTakesEveryRoundArrivingTogether()
        {
            // Play-test 13 (lane C): one hard-kill activation meets a whole salvo for one charge; it stays open even with no
            // charge left; the interceptor then reloads slower (SimTunables countermeasures.apsRechargeScale).
            var c = Shipped;
            var world = Field(c);
            var shooter = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 40f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            Assert.AreEqual(InterceptionMode.SelfAps, tank.Def.InterceptionMode, "a tank's own APS");
            tank.Aps = new ApsDef(12f, 1, 4f);
            tank.ApsCharges = 1;
            var missile = c.Weapons["hellfire_standoff"];
            bool Lands()
            {
                tank.Hp = tank.MaxHp;
                var round = new Projectile(shooter.Id, shooter.Team, missile, tank.Position, tank.Id, 0f)
                    { Origin = shooter.Position, Shooter = shooter, Main = true };
                world.Damage.ResolveImpact(round);
                return tank.Hp < tank.MaxHp;
            }
            Assert.IsFalse(Lands(), "the first missile opens the activation");
            Assert.AreEqual(0, tank.ApsCharges, "one charge spent");
            Assert.IsFalse(Lands(), "the second, arriving together, is taken by the same activation");
            Assert.IsFalse(Lands(), "and the third");
            Assert.AreEqual(0, tank.ApsCharges, "still one charge for the salvo");
            Assert.Greater(SimTunables.Weapons.Countermeasures.ApsRechargeScale, 1f, "paid for by a slower reload");
        }

        [Test]
        public void TheShotClockIsOffOutsideABattle()
        {
            var clock = new Game.Effects.ShotClock();
            Assert.IsFalse(clock.Active, "a clock never advanced is off");
            Assert.AreEqual(12.5f, clock.Map(12.5f), 1e-5f);
            Assert.AreEqual(12.5f, Game.Effects.ShotClock.Map(null, 12.5f), 1e-5f, "no clock: the time as given");
            clock.Advance(40.0, false, 0.016f);
            Assert.IsTrue(clock.Active);
            Assert.AreEqual(40f, clock.SimNow, 1e-4f, "the Sim's time as drawn");
            clock.Advance(99.0, true, 0.5f);
            Assert.AreEqual(40.5f, clock.SimNow, 1e-4f, "frozen: it runs on with the frame");
        }

        [Test]
        public void EachWorldKeepsItsOwnShotClock()
        {
            // Play-test 12: the lobby resting behind the menu must not freeze the preview's rounds.
            var lobby = new Game.Effects.ShotClock();
            var preview = new Game.Effects.ShotClock();
            lobby.Advance(10.0, false, 0.016f);
            preview.Advance(1.0, false, 0.016f);
            preview.Advance(1.5, false, 0.016f);
            Assert.AreEqual(10f, lobby.SimNow, 1e-4f);
            Assert.AreEqual(1.5f, preview.SimNow, 1e-4f, "the preview's clock moves on its own");
        }
    }
}
