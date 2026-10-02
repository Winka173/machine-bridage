using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 19 (DECISIONS 18A): the Silver Bug as an orbital spacecraft. Which weapons reach which altitude tier; the
    /// opening in orbit and the fixed schedule (never back to orbit, the lower tier during a change, each phase's cycle);
    /// the parts' jobs (main engine, thrusters, point-defence lasers, pod bay, uplink) and the armour by altitude; the
    /// tungsten rods (five rings, first from the craft then from the satellite, their damage, smoke and shields); drop
    /// pods (shot down in the air, never more than six vehicles); the crash into a ground fortress; the drone seizure at
    /// Very Hard only; no saucer left in the words.
    /// </summary>
    public class OrbitalBossTests
    {
        private const float Step = 0.05f;

        private static Catalog C => Lab.Catalog;

        private static SimWorld Field(string difficulty = "Normal", bool harmless = true)
        {
            var world = Lab.Field(3);
            if (difficulty != null) world.BigAttackSettings = BigAttackSettings.For(C.BigAttackRules, difficulty);
            if (harmless) world.SetBoosts(0, _ => Lab.Harmless);
            return world;
        }

        private static List<SimEvent> Run(SimWorld world, float seconds, System.Func<bool> until = null, System.Action each = null)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
                each?.Invoke();
                if (until != null && until()) break;
            }
            return events;
        }

        private static Vehicle Tough(SimWorld world, string def, Vector2 at, int team = 0)
        {
            var v = world.SpawnVehicle(def, team, at, SimMath.HeadingOf(-at));
            v.HpScale = 100f;
            v.Hp = v.MaxHp;
            v.Scripted = true;
            return v;
        }

        // ------------------------------------------------------------------ the tiers' rules

        [Test]
        public void EachWeaponReachesOnlyItsTier()
        {
            int V(string unit, AltitudeTier tier) => TierRules.Verdict(C.Vehicle(unit), tier);
            foreach (var high in new[] { "long_sam", "missile_battery", "fighter_jet", "stealth_fighter" })
            {
                Assert.AreEqual(2, V(high, AltitudeTier.High), high + " reaches high altitude");
                Assert.AreEqual(2, V(high, AltitudeTier.Low), high + " reaches low altitude");
            }
            foreach (var low in new[] { "aa_vehicle", "heavy_aa", "railgun_truck", "attack_helicopter" })
            {
                Assert.AreEqual(2, V(low, AltitudeTier.Low), low + " reaches low altitude");
                Assert.AreEqual(0, V(low, AltitudeTier.High), low + " does not reach high altitude");
            }
            Assert.AreEqual(0, V("main_battle_tank", AltitudeTier.High));
            Assert.AreNotEqual(2, V("main_battle_tank", AltitudeTier.Low), "a tank's gun never reaches it (its roof gun may)");
            foreach (var any in new[] { "long_sam", "fighter_jet", "railgun_truck", "aa_vehicle" })
                Assert.AreEqual(0, V(any, AltitudeTier.Orbit), any + ": nothing reaches orbit");
            // The railgun's exception is for tiered targets only: an ordinary aircraft is still out of its reach.
            var rail = C.Vehicle("railgun_truck");
            Assert.IsFalse(TierRules.Reaches(rail.Weapon, rail, AltitudeTier.None, true));
            Assert.IsTrue(TierRules.Reaches(rail.Weapon, rail, AltitudeTier.None, false));
        }

        // ------------------------------------------------------------------ the opening and the schedule

        [Test]
        public void TheOpeningIsOutOfReachThenItNeverGoesBackToOrbitAndKeepsItsSchedule()
        {
            var world = Field(difficulty: null);
            var bug = world.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            Tough(world, "main_battle_tank", new Vector2(0f, 20f));
            var t = bug.Def.Tiers;
            // Play-test 6 (DECISIONS 21G): half a second in orbit, then straight down (15 s up there overflowed the screen).
            Assert.AreEqual(0.5f, t.Opening, 1e-3f);
            Assert.AreEqual(AltitudeTier.Orbit, bug.Tier);
            Assert.IsTrue(bug.Invulnerable, "untouchable in orbit");
            var fired = Run(world, 0.4f).Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == bug.Id);
            Assert.AreEqual(0, fired, "its guns hold in orbit");
            Assert.AreEqual(AltitudeTier.Orbit, bug.Tier);
            var seen = new List<(double at, AltitudeTier tier, bool shifting)>();
            Run(world, 110f, each: () => seen.Add((world.Time, bug.Tier, bug.Shifting)));
            Assert.IsTrue(bug.LeftOrbit && bug.HasSatellite, "down from orbit, a satellite left up there");
            Assert.IsFalse(seen.Any(s => s.at > 0.7 && s.tier == AltitudeTier.Orbit), "never back to orbit");
            AltitudeTier At(double time) => seen.First(s => s.at >= time).tier;
            // 0.5-4.5 s the way down (counts as high), high to 29.5, the change to low (low meanwhile), low to 43, the
            // change back (still low), high from 46.5.
            Assert.AreEqual(AltitudeTier.High, At(1.5));
            Assert.AreEqual(AltitudeTier.High, At(29.0));
            Assert.AreEqual(AltitudeTier.Low, At(30.5), "during the change the lower tier counts");
            Assert.AreEqual(AltitudeTier.Low, At(35.5));
            Assert.AreEqual(AltitudeTier.Low, At(44.5), "climbing back it is still hit as low");
            Assert.AreEqual(AltitudeTier.High, At(47.5));
            Assert.AreEqual(AltitudeTier.High, At(70.5));
            Assert.AreEqual(AltitudeTier.Low, At(73.5));
            Assert.IsTrue(seen.Any(s => s.shifting), "each change takes its time");
            var shots = Run(world, 1f).Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == bug.Id);
            Assert.Greater(Run(world, 10f).Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == bug.Id) + shots, 0, "its laser fires once it is down");
        }

        [Test]
        public void PhaseTwoKeepsItsOwnCycleTheMainEngineHoldsItLowAndThrustersSlowTheChange()
        {
            var world = Field(difficulty: null);
            var bug = world.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            world.Bosses.JumpPhase(bug, 1);
            Run(world, 0.1f);
            Assert.AreEqual(1, bug.TierPhase);
            var start = world.Time;
            var seen = new List<(double at, AltitudeTier from, bool shifting)>();
            Run(world, 80f, each: () => seen.Add((world.Time - start, bug.TierFrom, bug.Shifting)));
            // After the way down (4 s): 15 s high, 3.5 s change, 20 s low, 3.5 s change, high again.
            var settledLow = seen.Where(s => s.from == AltitudeTier.Low && !s.shifting).ToList();
            Assert.IsNotEmpty(settledLow);
            var firstLow = settledLow.First().at;
            var lowEnds = seen.First(s => s.at > firstLow && s.shifting).at;
            Assert.AreEqual(20.0, lowEnds - firstLow, 0.2, "phase 2 stays low 20 s");
            // Its main engine broken: down it comes and stays low.
            world.Bosses.Break(bug, bug.Def.PartIndex("main_engine"));
            Run(world, 6f);
            Assert.AreEqual(AltitudeTier.Low, bug.Tier);
            Assert.IsTrue(bug.StuckLow);
            Run(world, 60f, () => bug.TierFrom == AltitudeTier.High || bug.TierTo == AltitudeTier.High);
            Assert.AreNotEqual(AltitudeTier.High, bug.TierTo, "it never climbs again");
            // Two manoeuvring thrusters broken: 12 % slower each, the change as much longer.
            var world2 = Field(difficulty: null);
            var bug2 = world2.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            world2.Bosses.Break(bug2, bug2.Def.PartIndex("thruster_fl"));
            world2.Bosses.Break(bug2, bug2.Def.PartIndex("thruster_rr"));
            world2.Bosses.JumpPhase(bug2, 0);
            Run(world2, 0.1f);
            Assert.IsTrue(world2.Bosses.ForceTier(bug2, AltitudeTier.Low));
            Assert.AreEqual(3.5 / (0.88 * 0.88), bug2.ShiftEnds - bug2.ShiftStart, 0.01, "a slower change");
        }

        // ------------------------------------------------------------------ what reaches it, and its armour

        [Test]
        public void AntiAirAndRailgunsHitItLowOnlyLongRangeSamsHitItHigh()
        {
            var world = Field(difficulty: null, harmless: false);
            var bug = world.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            bug.HpScale = 60f;
            bug.Hp = bug.MaxHp;
            world.Bosses.JumpPhase(bug, 0);
            Run(world, 0.1f);
            Assert.IsTrue(world.Bosses.ForceTier(bug, AltitudeTier.High));
            // Its point-defence lasers down, so the SAMs are not shot down on the way; its pod bay too, so the only target is the boss.
            world.Bosses.Break(bug, bug.Def.PartIndex("pod_bay"));
            world.Bosses.Break(bug, bug.Def.PartIndex("pd_laser_l"));
            world.Bosses.Break(bug, bug.Def.PartIndex("pd_laser_r"));
            var rail = Tough(world, "railgun_truck", new Vector2(0f, -30f));
            var aa = Tough(world, "aa_vehicle", new Vector2(18f, -22f));
            var sam = Tough(world, "long_sam", new Vector2(-40f, -30f));
            // Rounds that struck it (its body or a part), by weapon.
            bool Struck(List<SimEvent> events, Vehicle shooter) =>
                events.Any(e => e.Kind == SimEventKind.ProjectileImpact && e.Entity == bug.Id && e.DefId == shooter.Weapon.Id);
            var high = Run(world, 10f);
            Assert.AreEqual(AltitudeTier.High, bug.Tier);
            Assert.IsFalse(Struck(high, rail) || Struck(high, aa), "guns and railguns do not reach high altitude");
            Assert.IsTrue(Struck(high, sam), "the long-range SAM does");
            Assert.IsTrue(world.Bosses.ForceTier(bug, AltitudeTier.Low));
            Assert.AreEqual(AltitudeTier.Low, bug.Tier, "hit as low as soon as it starts down");
            var low = Run(world, 12f);
            Assert.IsTrue(Struck(low, rail), "the railgun reaches it low (this boss's exception)");
            Assert.IsTrue(Struck(low, aa), "anti-air guns reach it low");
            // Armour by altitude: the belly faces the ground low, the upper hull high.
            Run(world, 4f);
            Assert.AreEqual(2f, bug.ArmourOn(ArmorFace.Front), "belly, level 2");
            Assert.IsTrue(world.Bosses.ForceTier(bug, AltitudeTier.High));
            Run(world, 4f);
            Assert.AreEqual(4f, bug.ArmourOn(ArmorFace.Side), "upper hull, level 4");
            Assert.That(bug.Def.Parts.Where(p => p.Kind is "thruster" or "mainengine").Select(p => p.Armour), Is.All.InRange(1, 2), "engines 1-2");
        }

        // ------------------------------------------------------------------ the rods

        [Test]
        public void TheRodsFallOnFiveGroupsFromTheSatelliteOnceTheCraftIsDown()
        {
            var world = Field();
            var bug = world.SpawnVehicle("silver_bug", 1, new Vector2(0f, 90f), 0f);
            var groups = new List<List<Vehicle>>();
            for (var g = 0; g < 5; g++)
            {
                var a = g * SimMath.Tau / 5f;
                var centre = new Vector2(System.MathF.Cos(a), System.MathF.Sin(a)) * 50f;
                var list = new List<Vehicle>();
                foreach (var off in new[] { Vector2.Zero, new Vector2(4f, 0f), new Vector2(0f, 4f) }) list.Add(Tough(world, "heavy_tank", centre + off));
                groups.Add(list);
            }
            // Smoke over one group, a shield dome over another.
            world.Strikes.AddSmoke(0, groups[1][0].Position, 8f, 120f);
            Tough(world, "shield_carrier", groups[2][0].Position + new Vector2(-3f, -3f));
            var taken = new Dictionary<Vehicle, float>();
            DamageSystem.DamageLog = (attacker, victim, damage, kind, weapon) =>
            {
                if (attacker == bug && weapon == null && kind == HitKind.Direct) taken[victim] = (taken.TryGetValue(victim, out var d) ? d : 0f) + damage;
            };
            try
            {
                Run(world, 10f, () => bug.BigAttack.Stage == BigStage.Charging);
                var big = bug.BigAttack;
                Assert.AreEqual(BigStage.Charging, big.Stage);
                Assert.AreEqual(5.0, big.WarnStart, 0.1, "the first as it comes down");
                Assert.AreNotEqual(AltitudeTier.Orbit, bug.Tier, "down from orbit already (play-test 6)");
                // Play-test 6 (DECISIONS 21G): the craft is down by then, so the first already falls from the satellite it left.
                Assert.IsTrue(big.FromSatellite, "the first from the satellite (the craft came down at once)");
                Assert.AreEqual(4.0, big.FireAt - big.WarnStart, 1e-3, "4 s of warning");
                // Prompt 25 C1 (the balance sheet): seven rods of 1,800, 7 m each; five groups, the other two round the first.
                Assert.AreEqual(7, big.Zones.Count, "seven rings");
                Assert.IsTrue(big.Zones.All(z => System.Math.Abs(z.Radius - 7f) < 1e-3f), "7 m each");
                foreach (var list in groups)
                    Assert.IsTrue(big.Zones.Any(z => Vector2.Distance(z.Centre, list[0].Position) < 5f), "a ring on every group");
                Run(world, 8f, () => bug.BigAttack.Stage == BigStage.Ready);
                float Worst(List<Vehicle> list) => list.Max(v => taken.TryGetValue(v, out var d) ? d : 0f);
                // Play-test 6 (DECISIONS 21G): x the main rank's damage and big-attack scale (+20 %).
                var rank = bug.Def.DamageScale * bug.Def.BigAttackScale.Damage;
                Assert.AreEqual(1800f * rank, Worst(groups[0]), 18f * rank, "1 800 on a heavy tank's roof at the centre (penetration 4)");
                Assert.AreEqual(Worst(groups[0]), Worst(groups[1]), 16f, "smoke does nothing to a rod");
                var shielded = groups[2].Sum(v => taken.TryGetValue(v, out var d) ? d : 0f);
                var plain = groups[3].Sum(v => taken.TryGetValue(v, out var d) ? d : 0f);
                Assert.Less(shielded, plain * 0.9f, "the dome absorbs part of it");
                Run(world, 60f, () => bug.BigAttack.Stage == BigStage.Charging);
                Assert.AreEqual(BigStage.Charging, bug.BigAttack.Stage, "again a cooldown later");
                Assert.IsTrue(bug.BigAttack.FromSatellite, "the rest from the satellite");
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
        }

        [Test]
        public void TheUplinkCancelsTheRodsAndThePodBayStopsThePods()
        {
            var world = Field();
            var bug = world.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            for (var i = 0; i < 4; i++) Tough(world, "main_battle_tank", new Vector2(i * 4f, 50f));
            var events = Run(world, 10f, () => bug.BigAttack.Stage == BigStage.Charging);
            world.Bosses.Break(bug, bug.Def.PartIndex("uplink"));
            events.AddRange(Run(world, 0.2f));
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 2), "broken during the warning: cancelled");
            world.Bosses.TriggerBig(bug);
            Run(world, 3f);
            Assert.AreEqual(BigStage.Ready, bug.BigAttack.Stage, "the uplink gone, so are the rods");
            // The pod bay broken before its first drop: no pods at all.
            var world2 = Field();
            var bug2 = world2.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            world2.Bosses.Break(bug2, bug2.Def.PartIndex("pod_bay"));
            Run(world2, 25f);
            Assert.IsFalse(world2.VehicleList.Any(v => v.IsPod), "no pods");
        }

        // ------------------------------------------------------------------ drop pods

        [Test]
        public void PodsCanBeShotDownInTheAirAndNeverLandMoreThanSix()
        {
            var world = Field();
            var bug = world.SpawnVehicle("silver_bug", 1, Vector2.Zero, 0f);
            var pods = new List<Vehicle>();
            Run(world, 6f, () => (pods = world.VehicleList.Where(v => v.IsPod && v.IsAlive).ToList()).Count > 0);
            Assert.AreEqual(2, pods.Count, "two pods a drop");
            Assert.IsTrue(pods.All(p => p.Tier == AltitudeTier.Low && p.Flying), "low-altitude targets while they fall");
            var riders = world.Bosses.PodLoad(bug);
            world.Damage.Apply(pods[0], 1e6f, DamageType.Kinetic, new HitInfo(null, 0, null, pods[0].Position, HitKind.Direct, false));
            Assert.IsFalse(pods[0].IsAlive, "shot down");
            var left = world.Bosses.PodLoad(bug);
            Assert.Less(left, riders, "what it carried is lost");
            var most = 0;
            Run(world, 90f, each: () => most = System.Math.Max(most, world.Bosses.PodLoad(bug)));
            var landed = world.VehicleList.Count(v => v.IsAlive && v.Team == 1 && !v.Def.Boss && !v.IsPod);
            Assert.Greater(landed, 0, "the others landed their vehicles");
            Assert.LessOrEqual(most, 6, "never more than six of their vehicles at once");
            Assert.LessOrEqual(landed, 6);
        }

        // ------------------------------------------------------------------ the crash

        [Test]
        public void PhaseThreeCrashesAtItsPointAndFightsOnAsAGroundFortress()
        {
            var world = Field(harmless: false);
            var bug = world.SpawnVehicle("silver_bug", 1, new Vector2(60f, 60f), 0f);
            // Standing where it will come down: it must be put off that ground (prompt 12).
            var under = Tough(world, "main_battle_tank", new Vector2(2f, 3f));
            var shooter = Tough(world, "main_battle_tank", new Vector2(-34f, 0f));
            world.Bosses.JumpPhase(bug, 2);
            var events = Run(world, 12f, () => bug.Crashed);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TierChanged && e.DefId == "crash"), "it falls");
            Assert.IsTrue(bug.Crashed && !bug.Flying, "down on the ground");
            Assert.Less(Vector2.Distance(bug.Position, Vector2.Zero), 4f, "at its set point mid-map");
            Assert.AreEqual(TargetKind.Ground, bug.Kind);
            Assert.AreEqual(AltitudeTier.None, bug.Tier, "an ordinary ground target now");
            Assert.AreEqual("silver_bug_wreck", bug.Form);
            foreach (var m in bug.Def.Tiers.Crash.Guns) Assert.IsTrue(bug.MountWorks(m), $"gun {m} awake");
            Assert.AreEqual(bug.Def.Tiers.Crash.DebrisAt.Count, world.PropList.Count(p => p.Def.Id == "crash_debris"), "cover round it");
            Assert.IsTrue(world.PropList.Where(p => p.Def.Id == "crash_debris").All(p => p.Def.BlocksFire && !p.Def.BlocksMovement), "cover to drive over");
            Assert.IsTrue(world.Grid.IsWalkable(under.Position), "the tank under it was put off its ground");
            Assert.AreEqual(3f, bug.ArmourOn(ArmorFace.Front), "its crashed armour");
            // A tank's gun reaches it now (its body or a part).
            var spot = bug.Position;
            var hits = Run(world, 12f).Count(e => e.Kind == SimEventKind.ProjectileImpact && e.Entity == bug.Id && e.DefId == shooter.Weapon.Id);
            Assert.Greater(hits, 0, "a tank's gun hits the fortress");
            Assert.AreEqual(spot, bug.Position, "it never moves again");
        }

        // ------------------------------------------------------------------ the drone seizure

        [Test]
        public void OnlyVeryHardSeizesDronesAndJammersKeepTheirs()
        {
            foreach (var difficulty in new[] { "Normal", "VeryHard" })
            {
                var world = Field(difficulty);
                var bug = world.SpawnVehicle("silver_bug", 1, new Vector2(60f, 60f), 0f);
                // FPV launchers (their drones are rounds): one out in the open, one beside its side's jammer vehicle.
                var open = Tough(world, "fpv_carrier", new Vector2(70f, -60f));
                var covered = Tough(world, "fpv_carrier", new Vector2(-70f, -60f));
                Tough(world, "ew_jammer", new Vector2(-70f, -56f));
                world.Bosses.JumpPhase(bug, 2);
                Run(world, 40f, () => world.Bosses.Hijacked > 0);
                if (difficulty == "Normal")
                {
                    Assert.AreEqual(0, world.Bosses.Hijacked, "no seizure below Very Hard");
                    Assert.AreEqual(0, open.Team);
                    continue;
                }
                Assert.AreEqual(1, open.Team, "a drone out of jammer cover fights for the boss");
                Assert.AreEqual(0, covered.Team, "one under its own jammer is kept");
                Run(world, 7f);
                Assert.AreEqual(0, open.Team, "back after a few seconds");
            }
        }

        // ------------------------------------------------------------------ the words

        [Test]
        public void NoSaucerIsLeftAndEveryNewWordIsThere()
        {
            var bad = new List<string>();
            var words = new[] { "saucer", "đĩa bay", "avrocar", "flying disc" };
            foreach (var (key, (en, vi)) in Strings.Texts.Concat(GuideText.Table).Concat(CampaignText.Table).Concat(UnitText.Table).Concat(BigAttackText.Table).Concat(OrbitalText.Table))
                if (words.Any(w => en.ToLowerInvariant().Contains(w) || vi.ToLowerInvariant().Contains(w))) bad.Add(key);
            var data = File.ReadAllText(Path.Combine(Application.dataPath, "MachineBrigade/Resources/Data/balance.json")).ToLowerInvariant();
            if (words.Any(data.Contains)) bad.Add("balance.json");
            Assert.IsEmpty(bad, "a saucer is left in: " + string.Join(", ", bad));
            var def = C.Vehicle("silver_bug");
            foreach (var old in new[] { "coilgun", "flak", "bay", "shield", "emp", "laser" }) Assert.AreEqual(-1, def.PartIndex(old), "old part " + old);
            foreach (var key in new[] { "tier.orbit", "tier.high", "tier.low", "tier.shift", "tier.ground", "hud.tier", "hud.tier.reach", "hud.tier.none",
                         "guide.tiers", "guide.tiers.rule", "toast.pods", "toast.tier.descend", "unit.drop_pod", "part.fx.stop.thrust", "part.fx.stop.pods" })
                Assert.IsTrue(Strings.Has(key), key);
            foreach (var key in def.Tiers.Radio.Values) Assert.IsTrue(Strings.Has(key), key);
        }
    }
}
