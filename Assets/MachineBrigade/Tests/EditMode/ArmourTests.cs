using NUnit.Framework;
using MachineBrigade.Sim.Combat;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Armour by facing: a hull is thickest in front, thinner on the sides, thinnest behind.</summary>
    public class ArmourTests
    {
        [Test]
        public void SidesAndRearAreThinner()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var ahead = tank.Position + new Vector2(0f, 20f);
            Assert.AreEqual(1f, DamageSystem.FacingFactor(tank, ahead), 1e-4f, "heading 0 faces +Y: a shot from there hits the front");
            Assert.AreEqual(DamageSystem.SideFactor, DamageSystem.FacingFactor(tank, tank.Position + new Vector2(20f, 0f)), 1e-4f, "the side");
            Assert.AreEqual(DamageSystem.RearFactor, DamageSystem.FacingFactor(tank, tank.Position + new Vector2(0f, -20f)), 1e-4f, "the rear");
            Assert.AreEqual(1f, DamageSystem.FacingFactor(tank, tank.Position + new Vector2(10f, 20f)), 1e-4f, "a little off the nose is still the front");
        }
    }
}
