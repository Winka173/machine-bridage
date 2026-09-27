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
    /// <summary>Cluster rockets scatter bomblets that go off as their own blasts and spare their own side.</summary>
    public class ClusterTests
    {
        [Test]
        public void EliteRocketsScatterBombletsThatSpareTheirOwnSide()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-70f, -70f)), new TeamStart(1, new Vector2(70f, 70f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            var launcher = world.SpawnVehicle("elite_mlrs", 0, new Vector2(0f, -40f), 0f);
            var target = world.SpawnVehicle("heavy_tank", 1, new Vector2(0f, 20f), 3.14f);
            target.HpScale = 1000f;
            target.Hp = target.MaxHp;
            // The target never fires back (its shots would hurt the friend beside it).
            foreach (var weapon in target.Weapons) weapon.Cooldown = 1e6f;
            // A friend right beside the target, and a spotter so the launcher can see it.
            var friend = world.SpawnVehicle("heavy_tank", 0, new Vector2(4f, 20f), 3.14f);
            friend.HpScale = 1000f;
            friend.Hp = friend.MaxHp;
            world.SpawnVehicle("recon_drone", 0, new Vector2(0f, 0f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { launcher.Id }, target: target.Id));
            var bomblets = 0;
            var friendStart = friend.Hp;
            for (var t = 0f; t < 20f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.Explosion && e.Tier == ExplosionTier.Small) bomblets++;
                world.ClearEvents();
            }
            Assert.Greater(bomblets, 30, "each rocket of the salvo opens into bomblets");
            Assert.Less(target.Hp, target.MaxHp, "which hurt the enemy");
            Assert.AreEqual(friendStart, friend.Hp, 0.01f, "and spare the launcher's own side");
        }
    }
}
