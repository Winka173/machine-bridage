using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Prompt 29 B3-AI (C12): aircraft never fly home for their health, and still go back for ammunition. Not yet run.</summary>
    public class AircraftReturnTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static (SimWorld world, SandboxBattle battle, Vehicle craft) Build(int seed)
        {
            var s = new SandboxScenario { Seed = seed };
            s.Sides[0].Ai = SandboxAi.Combat; // TacticalAi alone: the path that had the low-health return
            s.Sides[0].Base = SandboxBase.Ai;  // an HQ to fly home to
            s.Sides[1].Ai = SandboxAi.Idle;
            s.Units.Add(new SandboxUnit { Def = "main_battle_tank", Team = 1, X = 20f, Y = 20f });
            s.Units.Add(new SandboxUnit { Def = "main_battle_tank", Team = 1, X = 24f, Y = 18f });
            var world = new SimWorld(Catalog, SandboxMaps.Flat(), s.Seed);
            var battle = new SandboxBattle(s);
            battle.Setup(world);
            world.TryGetRally(0, out var home);
            var craft = world.SpawnVehicle("attack_helicopter", 0, home + new Vector2(10f, 10f), 0f);
            return (world, battle, craft);
        }

        private static void Run(SimWorld world, SandboxBattle battle, float seconds)
        {
            for (var t = 0f; t < seconds && !world.IsOver; t += 0.05f)
            {
                battle.Tick(world, 0.05f);
                world.Step(0.05f);
                world.ClearEvents();
            }
        }

        [Test, Explicit("prompt 29: run once the owner allows the runs"), Category("P29")]
        public void AnAircraftLowOnHealthFightsOn()
        {
            var (world, battle, craft) = Build(41);
            craft.Hp = craft.MaxHp * 0.15f;
            var home = world.Vehicles.First(v => v.Team == 0 && v.Def.Fort is { Kind: FortKind.Hq }).Position;
            var headedHome = 0;
            for (var t = 0f; t < 20f && craft.IsAlive; t += 0.05f)
            {
                Run(world, battle, 0.05f);
                if (craft.Order.Kind == OrderKind.Move && Vector2.Distance(craft.Order.Point, home) < 6f && !craft.OutOfAmmo) headedHome++;
            }
            Assert.That(headedHome, Is.Zero, "no trip home for health");
        }

        [Test, Explicit("prompt 29: run once the owner allows the runs"), Category("P29")]
        public void AnAircraftOutOfAmmunitionStillGoesBack()
        {
            var (world, battle, craft) = Build(43);
            for (var i = 0; i < craft.Weapons.Length; i++)
                if (craft.Weapons[i].Load > 0 || craft.Weapons[i].Ammo > 0) craft.Weapons[i].Ammo = 0;
            var left = false;
            for (var t = 0f; t < 20f && craft.IsAlive && !left; t += 0.05f)
            {
                Run(world, battle, 0.05f);
                left = craft.Supply != SupplyState.Fighting;
            }
            Assert.That(left, Is.True, "it leaves to take its stores on again");
        }
    }
}
