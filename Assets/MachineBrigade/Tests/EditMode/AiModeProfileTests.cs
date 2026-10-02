using System.Linq;
using System.Reflection;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 28 appendix C: the AI profiles by mode (balance.json "aiModeProfiles"). Unit tests on the shipped data, no
    /// battle simulation. Written in the cloud session and not yet run (the owner runs them locally).
    /// </summary>
    public class AiModeProfileTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld World(string modeTag, string goal = null)
        {
            var world = new SimWorld(Catalog, SandboxMaps.Flat(), 1) { ModeTag = modeTag };
            if (goal != null) world.MissionGoal = goal;
            return world;
        }

        private static string GroundTank() =>
            Catalog.Vehicles.Values.First(d => !d.Static && !d.Flying && !d.Boss && d.Mounts.Count > 0 && d.CpCost > 0).Id;

        /// <summary>The defending side of every defending mode never gets stall pressure: no advance pressure, never the side pushed.</summary>
        [TestCase("Defend", null)]
        [TestCase("Endless", null)]
        [TestCase("Assault", null)]
        [TestCase("Siege", null)]
        [TestCase("Weekly", null)]
        [TestCase("Campaign", "Hold")]
        [TestCase("Campaign", "Survive")]
        [TestCase("Campaign", "Protect")]
        public void DefenderNeverGetsStallPressure(string mode, string goal)
        {
            var world = World(mode, goal);
            Assert.That(world.DefenderTeam, Is.Not.Null, $"{mode}/{goal}: the profile names its defender");
            var defender = world.DefenderTeam.Value;
            Assert.That(AiCommander.AdvancePressure(world, defender), Is.False, "the defender's attack threshold never falls");
            Assert.That(world.Stall == StallPolicy.Off || world.Stall == StallPolicy.AttackerOnly, Is.True, "stall pressure is off or on the attacker only");
            var id = GroundTank();
            var held = world.SpawnVehicle(id, defender, new Vector2(-40f, 0f), 0f);
            var attacker = world.SpawnVehicle(id, 1 - defender, new Vector2(30f, 0f), 180f);
            if (BattleEvents.MaxTier(world.Stall) > 0)
                Assert.That(BattleEvents.Pushed(world), Is.EqualTo(attacker.Position), "the barrage and reveal go to the attacker");
            Assert.That(held.IsAlive, Is.True);
        }

        /// <summary>Recon: no fire support before the alarm, and the combat profile after it.</summary>
        [Test]
        public void ReconCallsNoSupportBeforeTheAlarm()
        {
            var world = World("Campaign", "Recon");
            Assert.That(world.AiProfile.Support, Is.EqualTo(SupportPolicy.DisabledUntilAlert));
            Assert.That(world.SupportAllowed, Is.False);
            // A wave of difficulty cannot turn it on: the gate reads the profile and the alarm only.
            Assert.That(world.AiProfile.Engagement, Is.EqualTo(EngagementPolicy.AvoidUnlessBlocking));
            world.RaiseAlarm();
            Assert.That(world.SupportAllowed, Is.True);
            Assert.That(world.AiProfile.Id, Is.EqualTo("capture"), "the alert phase override plays the combat profile");
        }

        /// <summary>A ceasefire faction takes nothing from the player's fire, a strike or splash.</summary>
        [Test]
        public void CeasefireFactionTakesNoDamage()
        {
            const int ceasefire = 3;
            var world = World("Campaign", "Capture");
            world.SetCeasefire(ceasefire, true);
            var v = world.SpawnVehicle(GroundTank(), ceasefire, new Vector2(0f, 0f), 0f);
            var hp = v.Hp;
            world.Damage.Apply(v, 500f, DamageType.HighExplosive, new HitInfo(null, 0, null, new Vector2(10f, 0f), HitKind.Direct, false));
            world.Damage.Splash(v.Position, 12f, 500f, DamageType.HighExplosive, 0, default);
            if (Catalog.TryGetSupport("artillery_barrage", out var barrage)) world.Strikes.Launch(barrage, 0, v.Position, v.Position + Vector2.UnitX);
            for (var t = 0f; t < 20f; t += 0.05f)
            {
                world.Step(0.05f);
                world.ClearEvents();
            }
            Assert.That(v.IsAlive, Is.True);
            Assert.That(v.Hp, Is.EqualTo(hp), "no damage through any path");
            world.SetCeasefire(ceasefire, false);
            world.Damage.Apply(v, 50f, DamageType.HighExplosive, new HitInfo(null, 0, null, new Vector2(10f, 0f), HitKind.Direct, false));
            Assert.That(v.Hp, Is.LessThan(hp), "the gate is the ceasefire, not the test's setup");
        }

        /// <summary>Very Hard never turns advance pressure on where the profile has it off (the threshold never falls).</summary>
        [Test]
        public void VeryHardNeverTurnsOnAdvancePressure()
        {
            var profiles = Catalog.AiModes;
            var off = profiles.Profiles.Values.Where(p => !p.AdvancePressure).ToList();
            Assert.That(off, Is.Not.Empty);
            foreach (var p in off)
            {
                var tag = profiles.Modes.FirstOrDefault(m => m.Value == p.Id).Key;
                var goal = profiles.Goals.FirstOrDefault(g => g.Value == p.Id).Key;
                if (tag == null && goal == null) continue;
                var world = World(tag ?? "Campaign", tag == null ? goal : null);
                for (var team = 0; team <= 1; team++)
                {
                    var general = new AiCommander(team, 1 - team, AiSkill.For(AiDifficulty.VeryHard, Catalog.Ai), "balanced", _ => null);
                    general.RequestTactic(world, "balanced"); // binds the world
                    // A full army and bank for a long time: what would drop the threshold to its floor.
                    typeof(AiCommander).GetField("_fullSince", BindingFlags.NonPublic | BindingFlags.Instance)!.SetValue(general, -1000.0);
                    var standard = general.CurrentTactic.Modules.AttackThreshold ?? Catalog.Ai.AttackThreshold;
                    Assert.That(general.AttackThreshold(null), Is.EqualTo(standard), $"{p.Id}, team {team}");
                }
            }
        }

        /// <summary>Every mission goal in campaign.json, and every mode, has a profile.</summary>
        [Test]
        public void EveryMissionTypeHasAProfile()
        {
            var profiles = Catalog.AiModes;
            foreach (var goal in GameContent.LoadCampaign().Select(m => m.Goal.ToString()).Distinct())
                Assert.That(profiles.GoalProfile(goal), Is.Not.Null, $"goal {goal}");
            foreach (var mode in System.Enum.GetNames(typeof(GameModeKind)).Where(m => m != "Campaign"))
                Assert.That(profiles.Modes.ContainsKey(mode), Is.True, $"mode {mode}");
        }
    }
}
