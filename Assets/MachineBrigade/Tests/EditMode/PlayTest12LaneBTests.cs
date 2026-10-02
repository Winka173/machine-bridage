using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 12, lane B (DECISIONS "Play-test 12 (lane B)"): wreck variants by id, blasts by calibre, the preview's
    /// hooks for a boss. Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class PlayTest12LaneBTests
    {
        [Test]
        public void EveryWreckVariantComesUpAndStaysWithItsVehicle()
        {
            foreach (var c in new[] { WreckClass.Helicopter, WreckClass.Tank, WreckClass.Truck })
            {
                var seen = new HashSet<int>();
                for (var id = 1; id <= 60; id++)
                {
                    var v = WreckClasses.Variant(new EntityId(id), c);
                    Assert.That(v, Is.InRange(0, WreckClasses.Variants(c) - 1), c + " id " + id);
                    Assert.AreEqual(v, WreckClasses.Variant(new EntityId(id), c), "the same vehicle breaks the same way");
                    seen.Add(v);
                }
                Assert.AreEqual(WreckClasses.Variants(c), seen.Count, c + ": every way comes up");
            }
            Assert.AreEqual(0, WreckClasses.Variant(new EntityId(7), WreckClass.Drone), "a drone has one way");
        }

        [Test]
        public void BigGunsBurstByTheirCalibre()
        {
            var c = GameContent.LoadCatalog();
            var ap155 = c.Weapons["gun_155_twin_ap"];
            Assert.Greater(BlastSizes.CalibreShell(ap155), BlastSizes.TankShell(ap155), "a 155 mm AP hit is no longer a 125 mm one's");
            Assert.AreEqual(BlastSizes.TankShell(c.Weapons["gun_120mm"]), BlastSizes.CalibreShell(c.Weapons["gun_120mm"]), 1e-4f,
                "a tank's 120 mm unchanged");
            Assert.AreEqual(BlastSizes.ArtilleryGrow, BlastSizes.Round(c.Weapons["gun_155_twin_fort"]), 1e-4f,
                "the heavy turret's 155 mm HE as big as any 155 mm shell");
        }

        [Test]
        public void ALingeringPlumeIsShorterButKeepsItsOrder()
        {
            Assert.LessOrEqual(EffectLife.Of(5).SmokeMax, 15f);
            Assert.LessOrEqual(EffectLife.Of(4).SmokeMax, 10f);
            for (var b = 1; b <= EffectLife.Top; b++)
                Assert.GreaterOrEqual(EffectLife.Of(b).SmokeMin, EffectLife.Of(b - 1).SmokeMax, "band " + b);
        }

        [Test]
        public void TheFlagshipsSalvoFiresInAPreviewWithoutASea()
        {
            var c = GameContent.LoadCatalog();
            var map = new MapDefinition("range", 220f,
                new[] { new TeamStart(0, new System.Numerics.Vector2(0f, -70f)), new TeamStart(1, new System.Numerics.Vector2(0f, 70f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            var world = new SimWorld(c, map, seed: 11);
            var ship = world.SpawnVehicle("leviathan", 0, System.Numerics.Vector2.Zero, 0f);
            var target = world.SpawnVehicle("missile_boat", 1, new System.Numerics.Vector2(-50f, 10f), 1.57f);
            world.MakeDummy(target);
            world.Step(0.05f);
            world.ClearEvents();
            Assert.IsTrue(world.PreviewSalvo(ship), "its main turrets fire");
            var fired = 0;
            foreach (var e in world.Events)
                if (e.Kind == Sim.Events.SimEventKind.WeaponFired) fired++;
            Assert.Greater(fired, 0, "the turrets' shots are drawn");
            world.Hasten(ship, 8f);
            Assert.LessOrEqual(ship.MountCooldown(3), 8f);
        }
    }
}
