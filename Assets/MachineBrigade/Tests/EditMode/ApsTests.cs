using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>The active protection tank shoots down incoming missiles while it has interceptors.</summary>
    public class ApsTests
    {
        [Test]
        public void ActiveProtectionShootsDownMissilesUntilItRunsDry()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 120f,
                new[] { new TeamStart(0, new Vector2(-50f, -50f)), new TeamStart(1, new Vector2(50f, 50f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            var tank = world.SpawnVehicle("aps_tank", 1, new Vector2(0f, 0f), 3.14f);
            // In sight and missile range, beyond the carrier's machine gun and the tank's gun: only missiles fly.
            var carrier = world.SpawnVehicle("atgm_carrier", 0, new Vector2(0f, -34f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { carrier.Id }, target: tank.Id));
            var intercepted = 0;
            var hpAfterFirstVolley = -1f;
            for (var t = 0f; t < 16f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.Intercepted) intercepted++;
                world.ClearEvents();
                if (hpAfterFirstVolley < 0f && t >= 5f) hpAfterFirstVolley = tank.Hp;
            }
            Assert.AreEqual(tank.MaxHp, hpAfterFirstVolley, 0.01f, "both missiles of the first launch are shot down");
            Assert.GreaterOrEqual(intercepted, 3, "and the reloaded interceptor takes one of the next pair");
            Assert.Less(tank.Hp, tank.MaxHp, "until it runs dry and a missile gets through");
        }
    }
}
