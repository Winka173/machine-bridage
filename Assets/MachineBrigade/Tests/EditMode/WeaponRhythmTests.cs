using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>A vehicle's weapons fire on their own timings (play-test 7), machine guns fire in bursts, and guns leave aircraft to anti-aircraft.</summary>
    public class WeaponRhythmTests
    {
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 120f,
                new[] { new TeamStart(0, new Vector2(-50f, -50f)), new TeamStart(1, new Vector2(50f, 50f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        [Test]
        public void MainGunAndMachineGunFireOnTheirOwnTimings()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -12f), 0f);
            var target = world.SpawnVehicle("ifv", 1, new Vector2(0f, 6f), 0f);
            target.HpScale = 1000f;
            target.Hp = target.MaxHp;
            double lastMain = double.NegativeInfinity, lastGun = double.NegativeInfinity;
            int main = 0, gun = 0, together = 0, runs = 0;
            // 30 s (it was 20): play-test 6 (DECISIONS 21F) gave the machine guns longer streams.
            for (var t = 0f; t < 30f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind != SimEventKind.WeaponFired || e.Entity != tank.Id) continue;
                    if (e.Mount == 0)
                    {
                        main++;
                        lastMain = world.Time;
                    }
                    else if (e.DefId == "mg_coax")
                    {
                        gun++;
                        if (world.Time - lastMain < 0.3) together++;
                        if (world.Time - lastGun > 0.6) runs++;
                        lastGun = world.Time;
                    }
                }
                world.ClearEvents();
            }
            Assert.Greater(main, 3, "the main gun keeps firing");
            Assert.Greater(gun, 20, "and so does the coaxial gun");
            Assert.Greater(together, 0, "play-test 7: the coaxial gun no longer waits round a main-gun shot");
            Assert.GreaterOrEqual(runs, 3, "and in separate bursts, not one endless stream");
        }

        [Test]
        public void GunsPreferGroundTargetsAntiAircraftPrefersAircraft()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -10f), 0f);
            var aa = world.SpawnVehicle("aa_vehicle", 0, new Vector2(6f, -10f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 4f), 3.14f);
            var jeep = world.SpawnVehicle("scout_jeep", 1, new Vector2(3f, 8f), 3.14f);
            heli.HpScale = jeep.HpScale = 1000f;
            heli.Hp = heli.MaxHp;
            jeep.Hp = jeep.MaxHp;
            for (var t = 0f; t < 1.5f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Assert.AreEqual(jeep.Id, tank.Target, "the tank shoots the jeep, not the helicopter");
            Assert.AreEqual(heli.Id, aa.Target, "the anti-aircraft vehicle goes for the helicopter");
        }
    }
}
