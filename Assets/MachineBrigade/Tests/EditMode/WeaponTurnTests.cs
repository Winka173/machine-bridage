using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// A tank's machine gun takes on aircraft when its main gun has nothing on the ground. (Round 6's "no two weapons
    /// of a vehicle fire together" is gone: play-test 7 lets every mount fire on its own timing, PlayTest7Tests.)
    /// </summary>
    public class WeaponTurnTests
    {
        private static SimWorld Range(Catalog catalog) =>
            new SimWorld(catalog, new MapDefinition("range", 220f,
                new[] { new TeamStart(0, new Vector2(0f, -90f)), new TeamStart(1, new Vector2(0f, 90f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 7);

        [Test]
        public void ATankWithNothingOnTheGroundChasesAnAircraftWithItsCoaxialGun()
        {
            var world = Range(GameContent.LoadCatalog());
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(12f, 10f), System.MathF.PI);
            world.MakeDummy(heli);
            int coax = 0, main = 0;
            for (var t = 0f; t < 10f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == tank.Id)
                    {
                        if (e.Mount == 1) coax++;
                        if (e.Mount == 0) main++;
                    }
                world.ClearEvents();
            }
            Assert.Greater(coax, 0, "the coaxial gun fires at the helicopter, the turret swung after it");
            Assert.AreEqual(0, main, "the main gun cannot hit aircraft and does not try");
        }
    }
}
