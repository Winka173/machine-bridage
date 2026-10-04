using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 14 after R2 (lane H, DECISIONS "Play-test 14 after R2 (lane H)"): the flying warships never swing their hull
    /// while they fire and turn slowly on the move; a death's smoke emits half the puffs; missile trails half as long and a
    /// quarter narrower; no boss or vehicle lays smoke; the bosses' SAM posts fly no faster than the ordinary SAMs. Written,
    /// not run.
    /// </summary>
    public class PlayTest14LaneHTests
    {
        private static readonly string[] Warships = { "hyperion", "silver_bug", "icarus_mk0", "daedalus", "argus", "command_airship" };

        [Test]
        public void TheFlyingWarshipsHoldToFireTurnSlowlyAndAimWithTheirTurrets()
        {
            var c = Lab.Catalog;
            foreach (var id in Warships)
            {
                var def = c.Vehicle(id);
                Assert.IsTrue(def.HoldsToFire, id + " holds to fire");
                Assert.LessOrEqual(def.TurnRate, SimMath.DegToRad(10f) + 1e-4f, id + " turns like a big ship");
                Assert.AreNotEqual(MountAim.Hull, def.Mounts[0].Aim, id + ": its main weapon is laid, not the hull");
            }
        }

        [Test]
        public void AHaltedWarshipFiresWithoutTurningItsHull()
        {
            var world = Lab.Field(7);
            var ship = world.SpawnVehicle("command_airship", 1, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(30f, 0f), 0f);
            tank.HpScale = 100f;
            tank.Hp = tank.MaxHp;
            tank.Scripted = true;
            var heading = ship.Heading;
            var fired = 0;
            for (var t = 0f; t < 10f; t += 0.05f)
            {
                world.Step(0.05f);
                fired += world.Events.Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == ship.Id);
                world.ClearEvents();
                if (fired > 0) Assert.AreEqual(heading, ship.Heading, 1e-4f, "the hull holds its heading while it fires");
            }
            Assert.Greater(fired, 0, "its turrets fire on the tank beside it");
        }

        [Test]
        public void ADeathEmitsHalfTheSmokeAndTrailsAreShorterAndNarrower()
        {
            Assert.AreEqual(0.5f, SmokeTimes.AmountOf(SmokeTimes.Death), 1e-6f, "a death's smoke: half the puffs");
            Assert.AreEqual(1f, SmokeTimes.AmountOf(SmokeTimes.Blast), 1e-6f, "a blast's smoke keeps its puffs");
            Assert.AreEqual(1f, SmokeTimes.AmountOf(DirectorTankSmoke), 1e-6f, "a tank round's impact keeps its puffs");
            Assert.AreEqual(0.5f, SmokeTimes.TrailLength, 1e-6f, "missile trails half as long");
            Assert.AreEqual(0.75f, SmokeTimes.TrailWidth, 1e-6f, "and a quarter narrower");
        }

        private const float DirectorTankSmoke = EffectsDirector.TankSmokeLife;

        [Test]
        public void NoBossOrVehicleLaysSmoke()
        {
            foreach (var def in Lab.Catalog.Vehicles.Values)
                Assert.IsFalse(def.Skills.Any(s => s.Kind == SkillKind.Smoke), def.Id + " lays no smoke");
        }

        [Test]
        public void TheBossSamPostsFlyNoFasterThanTheOrdinarySams()
        {
            var c = Lab.Catalog;
            // Play-test 14 lane I slowed both again (80 and 95; PlayTest14LaneITests).
            Assert.LessOrEqual(c.Weapons["sam_post"].ProjectileSpeed, 170f + 1e-3f, "the ships' and Typhon's Buk post");
            Assert.LessOrEqual(c.Weapons["sam_battery"].ProjectileSpeed, 200f + 1e-3f, "Nemesis' Patriot car");
            Assert.AreEqual(FlightProfile.Loft, c.Weapons["sam_battery"].Flight, "still leaves its canister upward");
            Assert.LessOrEqual(c.Weapons["sam_battery"].ProjectileSpeed, c.Weapons["sam"].ProjectileSpeed + 1e-3f, "no faster than the SHORAD");
            Assert.AreEqual(300f, c.Weapons["patriot"].ProjectileSpeed, 1e-3f, "the player's Patriot keeps its family's speed");
            Assert.AreEqual(250f, c.Weapons["buk_launcher"].ProjectileSpeed, 1e-3f, "the player's Buk keeps its family's speed");
        }
    }
}
