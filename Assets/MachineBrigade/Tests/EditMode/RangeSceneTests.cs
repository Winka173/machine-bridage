using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Test feedback 11D: the In action clips show abilities working on real fire. A sparring
    /// partner fires but cannot be destroyed, and the jammer's scene works in the simulation: the
    /// enemy's guided missiles at its friends lose their lock (and hit without the jammer).
    /// </summary>
    public class RangeSceneTests
    {
        private static SimWorld Range(Catalog catalog) =>
            new SimWorld(catalog, new MapDefinition("range", 90f,
                new[] { new TeamStart(0, new Vector2(0f, -70f)), new TeamStart(1, new Vector2(0f, 70f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 11);

        [Test]
        public void SparringPartnerFiresButCannotBeDestroyed()
        {
            var world = Range(GameContent.LoadCatalog());
            var target = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -10f), 0f);
            world.MakeDummy(target);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 12f), System.MathF.PI);
            world.MakeSparring(enemy);
            world.DebugDamage(enemy, 5f);
            Assert.IsTrue(enemy.IsAlive, "a sparring partner survives any hit");
            world.Submit(new Command(CommandType.Attack, 1, new[] { enemy.Id }, default, target.Id));
            var fired = 0;
            for (var t = 0f; t < 10f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == enemy.Id) fired++;
                world.ClearEvents();
            }
            Assert.Greater(fired, 0, "a sparring partner fires as usual");
            Assert.IsTrue(enemy.IsAlive);
        }

        [Test]
        public void JammerScramblesTheMissilesAtItsFriends()
        {
            var (jammed, jammedFired) = MissileHits(withJammer: true);
            var (clear, clearFired) = MissileHits(withJammer: false);
            Assert.GreaterOrEqual(jammedFired, 2, "the ATGM post fired");
            Assert.GreaterOrEqual(clearFired, 2, "the ATGM post fired");
            Assert.AreEqual(0, jammed, "inside the jammer's field no missile hits");
            Assert.Greater(clear, 0, "without the jammer the missiles hit");
        }

        /// <summary>The jammer's clip: an enemy ATGM post shoots at a friend beside the jammer.</summary>
        private static (int hits, int fired) MissileHits(bool withJammer)
        {
            var world = Range(GameContent.LoadCatalog());
            if (withJammer) world.MakeDummy(world.SpawnVehicle("ew_jammer", 0, new Vector2(0f, -10.5f), 0f));
            var friend = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-6f, -6.5f), 0f);
            world.MakeDummy(friend);
            var enemy = world.SpawnVehicle("atgm_tower", 1, new Vector2(-7f, 28.5f), System.MathF.PI);
            world.MakeSparring(enemy);
            world.Submit(new Command(CommandType.Attack, 1, new[] { enemy.Id }, default, friend.Id));
            int hits = 0, fired = 0;
            for (var t = 0f; t < 20f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == enemy.Id && e.DefId == "kornet_twin") fired++;
                    if (e.Kind == SimEventKind.Damaged && e.Entity == friend.Id) hits++;
                }
                world.ClearEvents();
            }
            return (hits, fired);
        }
    }
}
