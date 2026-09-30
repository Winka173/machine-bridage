using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 G (DECISIONS 25G): second rounds, data-driven over every gun that has one. The data: a rule its round can
    /// meet, the gun's reload as the switch, elite-only rounds kept off ordinary carriers. The sim, on an open field for
    /// every gun with a carrier that can stand there: a target its round is for makes the gun change to it (the switch
    /// taking the gun's time) and fire it; targets swapping every 0.5 s never make a gun change rounds within 2 s; the
    /// same battle twice gives the same changes and the same fingerprint. Written for the testing phase; not run yet.
    /// </summary>
    public class SecondRoundTests
    {
        private const float Dt = TestWorlds.Step;

        private static Catalog Shipped => GameContent.LoadCatalog();

        private static IEnumerable<WeaponDef> Guns(Catalog c) => c.Weapons.Values.Where(w => w.HasRounds && w.RoundOf == null).OrderBy(w => w.Id);

        private static SimWorld Field(Catalog c, int seed = 7) =>
            new SimWorld(c, new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        /// <summary>A carrier that can stand on an open field and fire the gun on its own (no boss, ship, aircraft, pit or deploying gun).</summary>
        private static (VehicleDef def, int mount)? Carrier(Catalog c, WeaponDef gun, bool elite)
        {
            foreach (var d in c.Vehicles.Values.OrderBy(d => d.Id))
            {
                if (d.Boss || d.Flying || d.Naval != null || d.NavalOnly || d.Hidden != null || d.Deploy != null || d.Passive) continue;
                if (elite != (d.Elite || d.BranchOf != null)) continue;
                for (var i = 0; i < d.Mounts.Count; i++)
                    if (d.Mounts[i].Weapon.Id == gun.Id && !d.Mounts[i].Weapon.Laid) return (d, i);
            }
            return null;
        }

        /// <summary>A target the round's rule takes.</summary>
        private static string TargetFor(RoundUse use) =>
            (use & RoundUse.Air) != 0 && (use & RoundUse.Ground) == 0 ? "attack_helicopter"
            : (use & (RoundUse.Ground | RoundUse.Armour)) != 0 ? "main_battle_tank"
            : (use & RoundUse.Light) != 0 ? "scout_jeep"
            : (use & RoundUse.Structure) != 0 ? "guard_tower"
            : "main_battle_tank";

        [Test]
        public void EveryGunsSecondRoundHasARuleItsRoundCanMeet()
        {
            var catalog = Shipped;
            var failures = new List<string>();
            var guns = Guns(catalog).ToList();
            foreach (var gun in guns)
                foreach (var r in gun.Rounds)
                {
                    var round = r.Round;
                    if ((r.Use & RoundUse.Air) != 0 && !round.CanTarget(true)) failures.Add($"{round.Id}: for aircraft but cannot hit them");
                    if ((r.Use & ~RoundUse.Air) != 0 && !round.CanTarget(false)) failures.Add($"{round.Id}: for the ground but cannot hit it");
                    if (round.RoundOf != gun) failures.Add($"{round.Id}: loaded in {gun.Id} but says {round.RoundOf?.Id}");
                    if (round.HasRounds) failures.Add($"{round.Id}: a second round with rounds of its own");
                    var expected = System.MathF.Max(WeaponDef.MinSwitchSeconds, gun.Clip > 0 ? gun.ClipReload : gun.Cooldown);
                    if (r.SwitchSeconds <= 0f && System.MathF.Abs(gun.SwitchSeconds(r) - expected) > 1e-4f)
                        failures.Add($"{round.Id}: switches in {gun.SwitchSeconds(r)} s, not the gun's {expected} s");
                    // No rebalance (the owner's rule): a round hits as hard as its calibre, its gun's own damage, or the real
                    // round it is (the 2A83's HE-FRAG).
                    if (round.Damage != gun.Damage && round.WeaponFamily == null) failures.Add($"{round.Id}: {round.Damage} a round, its gun {gun.Damage}");
                    if (r.EliteOnly && catalog.Vehicles.Values.Any(d => !d.Elite && d.BranchOf == null && r.CarriedBy(d)))
                        failures.Add($"{round.Id}: an elite-only round carried by an ordinary unit");
                }
            Assert.IsEmpty(failures, string.Join("\n", failures));
            Assert.GreaterOrEqual(guns.Count, 60, "the sheet's 69 suggestions (three skipped) and prompt 17's two rounds");
            Assert.IsTrue(guns.Any(g => g.Rounds.Any(r => r.Round.Flak)), "the autocannons' air-burst rounds");
        }

        [Test]
        public void EachGunChangesToTheRoundForItsTargetAndFiresIt()
        {
            var catalog = Shipped;
            var failures = new List<string>();
            var tried = 0;
            foreach (var gun in Guns(catalog))
                foreach (var r in gun.Rounds)
                {
                    if ((r.Use & RoundUse.Cluster) != 0 && r.Use == RoundUse.Cluster) continue;
                    if (Carrier(catalog, gun, r.EliteOnly) is not { } carrier) continue;
                    tried++;
                    var world = Field(catalog);
                    var shooter = world.SpawnVehicle(carrier.def.Id, 0, Vector2.Zero, 0f);
                    world.MakeSparring(shooter);
                    var reach = System.MathF.Max(gun.MinRange + 5f, System.MathF.Min(gun.Range * 0.6f, 24f));
                    var target = world.SpawnVehicle(TargetFor(r.Use), 1, new Vector2(0f, reach), System.MathF.PI);
                    world.MakeSparring(target);
                    double? switchAt = null, firedAt = null;
                    float took = 0f;
                    for (var i = 0; i < (int)(14f / Dt) && firedAt == null; i++)
                    {
                        world.Step(Dt);
                        foreach (var e in world.Events)
                        {
                            if (e.Entity != shooter.Id || e.Mount != carrier.mount) continue;
                            if (e.Kind == SimEventKind.RoundSwitched && e.DefId == r.Round.Id && switchAt == null)
                            {
                                switchAt = world.Time;
                                took = e.Value;
                            }
                            if (e.Kind == SimEventKind.WeaponFired && e.Round == r.Round.Id) firedAt = world.Time;
                        }
                        world.ClearEvents();
                    }
                    if (switchAt == null) failures.Add($"{gun.Id} on {carrier.def.Id}: never loaded {r.Round.Id} for a {TargetFor(r.Use)}");
                    else if (firedAt == null) failures.Add($"{gun.Id} on {carrier.def.Id}: loaded {r.Round.Id} but never fired it");
                    else if (firedAt < switchAt + took - Dt * 1.5) failures.Add($"{gun.Id}: fired {r.Round.Id} {firedAt - switchAt:0.00} s into a {took:0.0} s switch");
                }
            Assert.IsEmpty(failures, string.Join("\n", failures));
            Assert.GreaterOrEqual(tried, 30, "most guns have a carrier that stands on an open field");
        }

        [Test]
        public void TargetsSwappingEveryHalfSecondNeverMakeAGunFlicker()
        {
            // Play-test 8 A's re-check is every 0.5 s: orders swapping between an aircraft and a ground target at that rate
            // change the round at most once per switch plus 2 s held.
            var catalog = Shipped;
            var failures = new List<string>();
            var tried = 0;
            foreach (var gun in Guns(catalog))
            {
                var air = gun.Rounds.Any(r => !r.EliteOnly && (r.Use & RoundUse.Air) != 0);
                var ground = gun.Rounds.Any(r => !r.EliteOnly && (r.Use & ~RoundUse.Air) != 0);
                if (!air && !ground) continue;
                if (Carrier(catalog, gun, false) is not { } carrier || carrier.mount != 0) continue;
                tried++;
                var world = Field(catalog);
                var shooter = world.SpawnVehicle(carrier.def.Id, 0, Vector2.Zero, 0f);
                world.MakeSparring(shooter);
                var reach = System.MathF.Max(gun.MinRange + 5f, System.MathF.Min(gun.Range * 0.6f, 22f));
                var a = world.SpawnVehicle("attack_helicopter", 1, new Vector2(-3f, reach), 0f);
                var b = world.SpawnVehicle(air ? "main_battle_tank" : "scout_jeep", 1, new Vector2(3f, reach), System.MathF.PI);
                world.MakeSparring(a);
                world.MakeSparring(b);
                var starts = new List<double>();
                var hold = WeaponDef.RoundHoldSeconds;
                for (var i = 0; i < (int)(12f / Dt); i++)
                {
                    if (i % (int)(0.5f / Dt) == 0)
                    {
                        var on = (i / (int)(0.5f / Dt)) % 2 == 0 ? a : b;
                        world.Submit(new Command(CommandType.Attack, 0, new[] { shooter.Id }, on.Position, on.Id));
                    }
                    world.Step(Dt);
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.RoundSwitched && e.Entity == shooter.Id && e.Mount == 0) starts.Add(world.Time);
                    world.ClearEvents();
                }
                var least = gun.Rounds.Min(r => gun.SwitchSeconds(r)) + hold;
                for (var k = 1; k < starts.Count; k++)
                    if (starts[k] - starts[k - 1] < least - Dt * 1.5)
                        failures.Add($"{gun.Id} on {carrier.def.Id}: changed rounds {starts[k] - starts[k - 1]:0.00} s apart (at least {least:0.0})");
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
            Assert.Greater(tried, 5, "the autocannons and flak guns on ground carriers");
        }

        [Test]
        public void TheSameBattleTwiceChangesTheSameRounds()
        {
            // Every gun with a second round on one side (one carrier each), aircraft, armour, a jeep and a tower on the other:
            // the same seed must give the same changes of round, step for step, and the same fingerprint.
            var catalog = Shipped;
            (List<(long, int, int, string)> switches, ulong hash) Run()
            {
                var world = Field(catalog, 11);
                var x = -60f;
                foreach (var gun in Guns(catalog))
                {
                    if (Carrier(catalog, gun, false) is not { } c) continue;
                    world.SpawnVehicle(c.def.Id, 0, new Vector2(x, 0f), 0f);
                    x += 6f;
                    if (x > 60f) break;
                }
                world.SpawnVehicle("attack_helicopter", 1, new Vector2(-10f, 22f), 0f);
                world.SpawnVehicle("attack_helicopter", 1, new Vector2(20f, 24f), 0f);
                world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 26f), System.MathF.PI);
                world.SpawnVehicle("scout_jeep", 1, new Vector2(-25f, 20f), System.MathF.PI);
                world.SpawnVehicle("guard_tower", 1, new Vector2(30f, 28f), System.MathF.PI);
                var log = new List<(long, int, int, string)>();
                for (var i = 0; i < (int)(20f / Dt); i++)
                {
                    world.Step(Dt);
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.RoundSwitched) log.Add((world.Tick, e.Entity.Value, e.Mount, e.DefId));
                    world.ClearEvents();
                }
                return (log, world.StateHash());
            }
            var first = Run();
            var second = Run();
            Assert.Greater(first.switches.Count, 0, "some gun changed rounds");
            CollectionAssert.AreEqual(first.switches, second.switches, "the same changes of round, step for step");
            Assert.AreEqual(first.hash, second.hash, "the same fingerprint (the loaded rounds are in it)");
        }
    }
}
