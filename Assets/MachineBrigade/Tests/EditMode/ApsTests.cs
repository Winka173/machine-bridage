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
    /// <summary>A tank with a Trophy APS module shoots down incoming missiles while it has interceptors.</summary>
    public class ApsTests
    {
        [Test]
        public void ActiveProtectionShootsDownMissilesUntilItRunsDry()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 120f,
                new[] { new TeamStart(0, new Vector2(-50f, -50f)), new TeamStart(1, new Vector2(50f, 50f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            // The Legendary module: two interceptors (the APS tank's), recharging.
            var module = new GearItem
            {
                id = 1, slot = (int)GearSlot.Special, rarity = (int)Rarity.Legendary, level = 1,
                special = (int)SpecialModule.TrophyAps, baseType = GearKeys.Module(SpecialModule.TrophyAps),
            };
            world.SetBoosts(1, _ => Gear.Boost(1, new[] { module }));
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 0f), 3.14f);
            Assert.IsNotNull(tank.Aps, "the module fits the tank with an active protection system");
            // In sight and missile range, beyond the carrier's machine gun and the tank's gun: only missiles fly.
            var carrier = world.SpawnVehicle("atgm_tower", 0, new Vector2(0f, -34f), 0f);
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
            Assert.AreEqual(2, intercepted, "one interceptor for each missile of the first launch, and none back yet");
            Assert.Less(tank.Hp, tank.MaxHp, "until it runs dry and a missile gets through");
        }
    }
}
