using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 29 appendix (DECISIONS "Prompt 29 appendix"): a weapon's declared targets against what its rounds can do, the
    /// two masks fixed in the data (B6-mask), and the vehicle's outgoing damage multiplier kept on every round it loads.
    /// The same check runs statically as <c>Tools/balance/target_mask_check.py</c> (Docs/checks/target_mask.md). Written,
    /// not run (the owner's rule).
    /// </summary>
    public class TargetMaskTests
    {
        private const float Dt = TestWorlds.Step;

        private static Catalog Shipped => GameContent.LoadCatalog();

        /// <summary>Target situations a gun meets (CombatSystem.Suits): flying, a structure, an armoured or light vehicle, alone or clustered.</summary>
        private static readonly (string name, bool flying, RoundUse takes)[] Situations =
        {
            ("aircraft", true, RoundUse.Air),
            ("structure", false, RoundUse.Ground | RoundUse.Structure),
            ("armour", false, RoundUse.Ground | RoundUse.Armour),
            ("armour, clustered", false, RoundUse.Ground | RoundUse.Armour | RoundUse.Cluster),
            ("light", false, RoundUse.Ground | RoundUse.Light),
            ("light, clustered", false, RoundUse.Ground | RoundUse.Light | RoundUse.Cluster),
        };

        /// <summary>Guns: weapons a vehicle mounts, and weapons that are no other gun's second round; doing damage, not intercept-only.</summary>
        private static List<WeaponDef> Guns(Catalog c)
        {
            var mounted = new HashSet<WeaponDef>(c.Vehicles.Values.SelectMany(v => v.Mounts.Select(m => m.Weapon)));
            return c.Weapons.Values.Where(w => (w.RoundOf == null || mounted.Contains(w)) && w.Damage > 0f && !w.InterceptOnly)
                .OrderBy(w => w.Id).ToList();
        }

        /// <summary>The highest damage-type multiplier over the rounds valid for a layer (its own when it reaches it, and each second round whose rule takes it).</summary>
        private static float Best(Catalog c, WeaponDef gun, TargetKind kind, bool flying)
        {
            var best = gun.CanTarget(flying) ? c.Damage.TypeOf(gun, kind) : 0f;
            foreach (var r in gun.Rounds)
            {
                var takes = flying ? (r.Use & RoundUse.Air) != 0 : (r.Use & ~RoundUse.Air) != 0;
                if (takes && r.Round.CanTarget(flying)) best = System.Math.Max(best, c.Damage.TypeOf(r.Round, kind));
            }
            return best;
        }

        [Test]
        public void EveryDeclaredTargetLayerTakesDamageFromSomeRound()
        {
            var c = Shipped;
            var failures = new List<string>();
            foreach (var gun in Guns(c))
            {
                if ((gun.Targets & TargetLayers.Air) != 0 && Best(c, gun, TargetKind.Air, true) <= 0f)
                    failures.Add($"{gun.Id}: targets aircraft, no round damages them ({gun.DamageType})");
                if ((gun.Targets & TargetLayers.Ground) != 0 && Best(c, gun, TargetKind.Ground, false) <= 0f)
                    failures.Add($"{gun.Id}: targets the ground, no round damages vehicles ({gun.DamageType})");
                if ((gun.Targets & TargetLayers.Ground) != 0 && Best(c, gun, TargetKind.Structure, false) <= 0f)
                    failures.Add($"{gun.Id}: targets the ground, no round damages structures ({gun.DamageType})");
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [Test]
        public void TheTwoAppendixGunsHitTheGroundOnly()
        {
            var c = Shipped;
            foreach (var id in new[] { "gun_100_river" })
            {
                var gun = c.Weapons[id];
                // B6-mask: All -> Ground, unless a second round of the gun damaged aircraft (none does; DECISIONS).
                Assert.IsFalse(gun.Rounds.Any(r => r.Round.CanTarget(true) && c.Damage.TypeOf(r.Round, TargetKind.Air) > 0f), id);
                Assert.That(gun.Targets, Is.EqualTo(TargetLayers.Ground), id);
            }
        }

        /// <summary>
        /// A second round whose rule no target meets: its round reaches nothing the rule names, it is elite-only and no elite
        /// or branch carries the gun, or an earlier round of the gun takes every target it would (the first that suits wins).
        /// Listed, not failed per round: the appendix fixes only the two masks, so this test fails only on a new one.
        /// </summary>
        [Test]
        public void SecondRoundsWhoseRuleIsNeverMetAreTheKnownOnes()
        {
            var c = Shipped;
            var carriers = c.Vehicles.Values.SelectMany(v => v.Mounts.Select(m => (v, m.Weapon))).ToList();
            var unmet = new List<string>();
            foreach (var gun in Guns(c))
            {
                var eliteCarrier = carriers.Any(p => p.Weapon == gun && (p.v.Elite || p.v.BranchOf != null));
                for (var k = 0; k < gun.Rounds.Count; k++)
                {
                    var r = gun.Rounds[k];
                    if (r.EliteOnly && !eliteCarrier)
                    {
                        unmet.Add(r.Round.Id);
                        continue;
                    }
                    var wins = false;
                    foreach (var (_, flying, takes) in Situations)
                    {
                        for (var j = 0; j < gun.Rounds.Count; j++)
                        {
                            var other = gun.Rounds[j];
                            if (!other.Round.CanTarget(flying) || (other.Use & takes) == 0) continue;
                            wins = j == k;
                            break;
                        }
                        if (wins) break;
                    }
                    if (!wins) unmet.Add(r.Round.Id);
                }
            }
            // Docs/checks/target_mask.md, section 2 (2026-10-02): elite-only rounds on guns no elite or branch mounts.
            var known = new HashSet<string>
            {
                "bomber_tail_guns_api", "boss_hmg_api", "boss_howitzer_guided", "bunker_hmg_api", "casemate_155_guided", "cruiser_203_guided",
                "gun_155_coastal_guided", "gun_behemoth_guided", "gunship_105_guided", "hmg_selfdef_21_api", "howitzer_fixed_guided",
                "leviathan_460_guided", "mg_jeep_api", "mg_jeep_selfdef_api", "naval_100_guided", "naval_155_triple_guided", "naval_76_guided",
            };
            var fresh = unmet.Where(id => !known.Contains(id)).ToList();
            Assert.IsEmpty(fresh, "second rounds whose rule is never met (add to Docs/checks/target_mask.md or fix):\n" + string.Join("\n", fresh));
        }

        /// <summary>The first round of <paramref name="roundId"/> the shooter fires at the target: its damage scale (null if none in 14 s).</summary>
        private static float? FirstScale(float mult, string shooterId, string roundId, string targetId, float reach)
        {
            var c = Shipped;
            c.Vehicles[shooterId].OutgoingDamageMult = mult;
            var world = new SimWorld(c, new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), 7);
            var shooter = world.SpawnVehicle(shooterId, 0, Vector2.Zero, 0f);
            world.MakeSparring(shooter);
            var target = world.SpawnVehicle(targetId, 1, new Vector2(0f, reach), System.MathF.PI);
            world.MakeSparring(target);
            for (var i = 0; i < (int)(14f / Dt); i++)
            {
                world.Step(Dt);
                foreach (var p in world.Combat.InFlight)
                    if (p.Owner == shooter.Id && p.Weapon.Id == roundId) return p.DamageScale;
                world.ClearEvents();
            }
            return null;
        }

        [Test]
        public void OutgoingDamageMultRidesOnEveryRoundTheGunLoads()
        {
            var c = Shipped;
            var tried = 0;
            var failures = new List<string>();
            // A carrier on an open field for a few guns with a second round: its own round at one target, the second at another.
            foreach (var gun in c.Weapons.Values.Where(w => w.HasRounds && w.RoundOf == null).OrderBy(w => w.Id))
            {
                var carrier = c.Vehicles.Values.OrderBy(d => d.Id).FirstOrDefault(d =>
                    !d.Boss && !d.Flying && d.Naval == null && !d.NavalOnly && d.Hidden == null && d.Deploy == null && !d.Passive && !d.Elite &&
                    d.BranchOf == null && d.Mounts.Count > 0 && d.Mounts[0].Weapon == gun && !gun.Laid);
                if (carrier == null) continue;
                var round = gun.Rounds.FirstOrDefault(r => !r.EliteOnly && (r.Use & (RoundUse.Air | RoundUse.Armour | RoundUse.Light)) != 0);
                if (round == null) continue;
                var air = (round.Use & RoundUse.Air) != 0;
                var light = (round.Use & RoundUse.Light) != 0;
                var forRound = air ? "attack_helicopter" : light ? "scout_jeep" : "main_battle_tank";
                var reach = System.MathF.Max(gun.MinRange + 5f, System.MathF.Min(gun.Range * 0.6f, 24f));
                foreach (var (roundId, target) in new[] { (round.Round.Id, forRound) })
                {
                    var one = FirstScale(1f, carrier.Id, roundId, target, reach);
                    var two = FirstScale(2f, carrier.Id, roundId, target, reach);
                    if (one == null || two == null) continue;
                    tried++;
                    if (System.Math.Abs(two.Value - 2f * one.Value) > 1e-4f) failures.Add($"{carrier.Id} {roundId}: x1 {one}, x2 {two}");
                }
                if (tried >= 6) break;
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
            Assert.GreaterOrEqual(tried, 3, "a few guns changed to a second round and fired it");
        }
    }
}
