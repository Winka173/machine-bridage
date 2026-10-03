using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Defend's fallback lines and waves: the player's fortress is exactly their base loadout;
    /// losing a line blows up its towers and pays a retreat reward; the inner lines' towers are
    /// the stronger; the next wave is known before it lands and is the wave that lands; waves are
    /// swarms that grow in numbers and never put more attackers on the field than the ceiling.
    /// </summary>
    public class DefendLinesTests
    {
        private const float Step = 0.05f;

        private static BaseLoadout Loadout() => new()
        {
            HqLevel = 5,
            Small = { "guard_tower", "mg_bunker" },
            Medium = { "gun_turret" },
            Large = { "artillery_emplacement" },
            Utilities = { "repair_bay" },
        };

        private static (SimWorld world, SiegeMode mode) Fortress(SiegeRules rules = null, string map = "greenvale")
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_siege"), seed: 5);
            rules ??= new SiegeRules();
            rules.PlayerDefends = true;
            rules.FortressLoadout ??= Loadout();
            rules.Attacker ??= new SideSetup();
            rules.Attacker = new SideSetup { StartCp = 0f, Income = 0.01f, Vehicles = new[] { "armored_car" } };
            rules.Defender = new SideSetup { StartCp = 0f, Income = 0.01f, Bank = 200f };
            var mode = new SiegeMode(rules);
            mode.Setup(world);
            return (world, mode);
        }

        private static void Run(SimWorld world, SiegeMode mode, float seconds, System.Action each = null)
        {
            for (var t = 0f; t < seconds && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                each?.Invoke();
            }
        }

        [Test]
        public void ThePlayersFortressIsExactlyTheirLoadout()
        {
            var (world, mode) = Fortress();
            var fortress = world.Bases.Of(SiegeMode.PlayerTeam);
            Assert.IsNotNull(fortress, "the fortress is the player's base");
            Assert.AreEqual(BaseRole.Defend, fortress.Role);
            var loadout = Loadout();
            var towers = new HashSet<string>(loadout.Towers);
            var utilities = new List<string>();
            foreach (var slot in fortress.Slots)
            {
                if (slot.Def.Kind == HardpointKind.Utility)
                {
                    if (slot.Tower != null) utilities.Add(slot.Tower);
                    continue;
                }
                Assert.IsNotNull(slot.Tower, $"every tower hardpoint is manned (ring {slot.Ring}, {slot.Def.Class})");
                Assert.IsTrue(towers.Contains(slot.Tower), $"the {slot.Tower} is one of the player's");
                Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var v) && v.Team == SiegeMode.PlayerTeam, "and stands, the player's");
                var size = world.Catalog.Vehicle(slot.Tower).Fort.Size;
                Assert.LessOrEqual(size, slot.Def.Class, "it fits its hardpoint");
                if (slot.Def.Class == SlotSize.Small) Assert.AreEqual(SlotSize.Small, size, "a small hardpoint takes the loadout's small towers");
            }
            CollectionAssert.AreEqual(new[] { "repair_bay" }, utilities, "each of the loadout's modules once");
            Assert.IsFalse(world.Vehicles.Any(v => v.Team == SiegeMode.EnemyTeam && v.Def.Static), "the enemy has no towers of its own");
        }

        [Test]
        public void LosingALineBlowsUpItsTowersAndPaysARetreat()
        {
            var (world, mode) = Fortress();
            var fortress = world.Bases.Of(SiegeMode.PlayerTeam);
            var outer = fortress.Slots.Where(s => s.Ring == 1 && s.Structure.IsValid).Select(s => s.Structure).ToList();
            var inner = fortress.Slots.Where(s => s.Ring == 2 && s.Structure.IsValid).Select(s => s.Structure).ToList();
            Assert.Greater(outer.Count, 5, "the outer line is manned");
            world.TryGetEconomy(SiegeMode.PlayerTeam, out var ours);
            var cp = ours.Cp;
            foreach (var relay in world.Props.Where(p => p.IsAlive && p.Def.Id == "radar_station_prop").ToList()) world.DebugDestroyProp(relay);
            Run(world, mode, 0.2f);
            Assert.AreEqual(2, mode.Stage, "the outer line is lost");
            Assert.GreaterOrEqual(ours.Cp, cp + mode.Rules.RetreatCp[0] - 0.5f, "the player gets a retreat reward to spend on the next line");
            Run(world, mode, outer.Count * 0.25f + 2f);
            Assert.IsTrue(outer.All(id => !world.TryGetVehicle(id, out var v) || !v.IsAlive), "the lost line's towers have blown up");
            Assert.IsTrue(inner.All(id => world.TryGetVehicle(id, out var v) && v.IsAlive), "the next line's still stand");
            Assert.IsTrue(fortress.Slots.Where(s => s.Ring == 1).All(s => s.Lost), "the lost line's hardpoints are gone for good");
            Assert.IsFalse(world.Bases.Callable(SiegeMode.PlayerTeam).Any(s => s.Ring == 1), "nothing is flown back into a lost line");
        }

        [Test]
        public void TheInnerLinesHoldTheStrongerTowers()
        {
            var (world, mode) = Fortress();
            var fortress = world.Bases.Of(SiegeMode.PlayerTeam);
            float Worth(int ring) => fortress.Slots.Where(s => s.Ring == ring && s.Def.Kind == HardpointKind.Tower && s.Structure.IsValid)
                .Average(s => world.TryGetVehicle(s.Structure, out var v) ? v.MaxHp : 0f);
            float Toughness(int ring) => fortress.Slots.Where(s => s.Ring == ring && s.Structure.IsValid)
                .Average(s => world.TryGetVehicle(s.Structure, out var v) ? v.MaxHp / v.Def.MaxHp : 0f);
            Assert.Greater(Worth(2), Worth(1), "the walls' towers are stronger than the outer line's");
            Assert.Greater(Worth(3), Worth(2), "the keep's are the strongest");
            Assert.That(Toughness(3), Is.EqualTo(mode.Rules.LineHealth[2]).Within(0.01f), "and ranked up");
            Assert.That(Toughness(1), Is.EqualTo(mode.Rules.LineHealth[0]).Within(0.01f));
            Assert.IsTrue(fortress.Slots.Where(s => s.Ring == 3 && s.Def.Kind == HardpointKind.Tower).Any(s => s.Def.Class == SlotSize.Large),
                "the keep has large hardpoints");
            Assert.IsFalse(fortress.Slots.Where(s => s.Ring == 1).Any(s => s.Def.Class == SlotSize.Large), "the outer line has none");
        }

        private static SiegeRules Waves(int maxAlive = 48) => new()
        {
            Endless = true, WaveSeconds = 20f, WaveSeed = 9, MaxAlive = maxAlive,
            WaveRoster = DefendSession.Swarm, WaveHeavy = DefendSession.Heavy, WaveStart = 5, WaveGrowth = 2f, WaveMax = 36, EliteFrom = 2,
        };

        [Test]
        public void TheWavePreviewIsTheWaveThatLands()
        {
            var (world, mode) = Fortress(Waves());
            var previews = new Dictionary<int, List<(string, int)>>();
            var sent = mode.Wave;
            previews[1] = mode.NextWave.ToList();
            Run(world, mode, 170f, () =>
            {
                if (mode.Wave == sent) return;
                sent = mode.Wave;
                previews[sent + 1] = mode.NextWave.ToList();
            });
            Assert.GreaterOrEqual(mode.Wave, 4, "a wave every 20 s");
            for (var wave = 1; wave <= mode.Wave; wave++)
            {
                var landed = new List<(string, int)>();
                foreach (var id in mode.Landed[wave])
                {
                    var k = landed.FindIndex(p => p.Item1 == id);
                    if (k >= 0) landed[k] = (id, landed[k].Item2 + 1);
                    else landed.Add((id, 1));
                }
                CollectionAssert.AreEqual(previews[wave], landed, $"wave {wave} is what its preview showed");
                Assert.Greater(previews[wave].Count, 0);
            }
            Assert.IsTrue(previews.Values.SelectMany(p => p).Any(p => p.Item1.StartsWith("elite_")), "elites turn up in the later waves, shown as they are");
        }

        [Test]
        public void WavesNeverPutMoreAttackersOnTheFieldThanTheCeiling()
        {
            var (world, mode) = Fortress(Waves(maxAlive: 14));
            var most = 0;
            var held = 0;
            Run(world, mode, 90f, () =>
            {
                most = System.Math.Max(most, mode.AttackersAlive(world));
                held = System.Math.Max(held, mode.Held);
            });
            Assert.LessOrEqual(most, 14, "never more alive at once than the ceiling");
            Assert.Greater(held, 0, "the rest waited off the map");
            // As attackers fall, the ones waiting come in.
            var landed = mode.Landed.Values.Sum(l => l.Count);
            foreach (var v in world.Vehicles.Where(v => v.Team == mode.Attacker && !v.Def.Static).Take(6).ToList()) world.DebugDamage(v, 5f);
            Run(world, mode, 6f);
            Assert.Greater(mode.Landed.Values.Sum(l => l.Count), landed, "they come in as room frees up");
            Assert.LessOrEqual(mode.AttackersAlive(world), 14);
            Assert.AreEqual(48, new SiegeRules().MaxAlive, "the default ceiling");
        }

        [Test]
        public void WavesGrowAsSwarmsOfCheapVehicles()
        {
            var (world, mode) = Fortress(Waves());
            var counts = new List<int>();
            var costs = new List<float>();
            var seen = -1;
            Run(world, mode, 20f * 10 + 1f, () =>
            {
                if (mode.Wave == seen) return;
                seen = mode.Wave;
                var n = mode.NextWave.Sum(p => p.count);
                counts.Add(n);
                costs.Add(mode.NextWave.Sum(p => p.count * world.Catalog.Vehicle(p.id).CpCost) / (float)n);
            });
            Assert.GreaterOrEqual(counts.Count, 8);
            for (var i = 1; i < counts.Count; i++) Assert.GreaterOrEqual(counts[i], counts[i - 1], "each wave at least as big as the last");
            Assert.GreaterOrEqual(counts[counts.Count - 1], counts[0] * 3, "the swarm grows in numbers");
            Assert.LessOrEqual(costs.Max(), 7f, "made of cheap vehicles, not ever heavier ones");
        }
    }
}
