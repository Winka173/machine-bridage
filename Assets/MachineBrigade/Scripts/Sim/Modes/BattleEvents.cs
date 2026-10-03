#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Things that happen to a battle rather than in it, so no two matches play alike: supply
    /// crates parachuted into the middle for either side to grab, and bomber raids that hit
    /// whatever is fighting below, friend and foe alike. Deterministic from the seed.
    /// </summary>
    public sealed partial class BattleEvents
    {
        /// <summary>Prompt 30 L6: the contested drop is announced (and marked) 15 s before it lands (5 s before).</summary>
        private static float CrateFall => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.CrateFall;
        private static float CrateLife => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.CrateLife;
        private static float ClaimReach => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.ClaimReach;
        private static float ClaimSeconds => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.ClaimSeconds;
        private static float CrateCp => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.CrateCp;
        private static float CrateRepair => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.CrateRepair;
        private const string RaidSupport = "air_raid";

        private readonly Random _random;
        private readonly bool _raids;
        private double _nextCrate;
        private double _nextRaid;
        private int _nextId = 1;

        public BattleEvents(int seed, bool raids = true)
        {
            _random = new Random(seed * 7919 + 13);
            _raids = raids;
            _nextCrate = 45 + _random.NextDouble() * 30;
            _nextRaid = 80 + _random.NextDouble() * 45;
        }

        public void Tick(SimWorld world, float dt)
        {
            if (world.IsOver) return;
            var now = world.Time;
            if (now >= _nextCrate)
            {
                _nextCrate = now + 70 + _random.NextDouble() * 40;
                DropCrate(world, now);
            }
            if (_raids && now >= _nextRaid)
            {
                // No fight worth bombing yet: look again shortly.
                _nextRaid = Raid(world) ? now + 120 + _random.NextDouble() * 70 : now + 20;
            }
            UpdateCrates(world, dt, now);
            // Prompt 28 I.6: rising pressure on a battle standing still.
            if (Escalation) Escalate(world, now);
        }

        private void DropCrate(SimWorld world, double now)
        {
            // Prompt 30 L6: between the two armies (else the middle band), open ground, well away from both rally points.
            var a = ArmyCentre(world, 0);
            var b = ArmyCentre(world, 1);
            var middle = a != null && b != null ? (a.Value + b.Value) * 0.5f : world.Map.Centre;
            for (var attempt = 0; attempt < 20; attempt++)
            {
                var map = world.Map;
                var spread = attempt < 10 ? 0.1f : 0.225f;
                var at = (attempt < 10 ? middle : map.Centre) + new Vector2((float)(_random.NextDouble() * 2 - 1) * map.Width * spread,
                    (float)(_random.NextDouble() * 2 - 1) * map.Length * spread);
                if (!world.Grid.IsWalkable(at)) continue;
                var clear = true;
                foreach (var team in world.Map.Teams)
                    if (Vector2.Distance(team.Rally, at) < 40f) clear = false;
                if (!clear) continue;
                var crate = new Crate(new EntityId(_nextId++), at, now + CrateFall, now + CrateFall + CrateLife);
                world.CrateList.Add(crate);
                world.Announce(SimEvent.CrateIncoming(crate, CrateFall));
                return;
            }
        }

        private static void UpdateCrates(SimWorld world, float dt, double now)
        {
            var crates = world.CrateList;
            for (var i = crates.Count - 1; i >= 0; i--)
            {
                var crate = crates[i];
                if (now < crate.LandsAt) continue;
                if (now > crate.ExpiresAt)
                {
                    crate.IsAlive = false;
                    crates.RemoveAt(i);
                    continue;
                }
                // Who is standing on it? Contested ground claims nothing.
                var holder = -1;
                var contested = false;
                foreach (var v in world.VehicleList)
                {
                    if (!v.IsAlive || v.Flying || v.Team < 0) continue;
                    if (Vector2.Distance(v.Position, crate.Position) > ClaimReach + v.Def.HullRadius) continue;
                    if (holder < 0) holder = v.Team;
                    else if (holder != v.Team) contested = true;
                }
                if (holder < 0 || contested)
                {
                    crate.Claim = MathF.Max(0f, crate.Claim - dt / ClaimSeconds);
                    continue;
                }
                if (holder != crate.Holder) crate.Claim = 0f;
                crate.Holder = holder;
                crate.Claim += dt / ClaimSeconds;
                if (crate.Claim < 1f) continue;

                crate.IsAlive = false;
                crates.RemoveAt(i);
                if (world.TryGetEconomy(holder, out var economy)) economy.Cp = MathF.Min(economy.Bank, economy.Cp + CrateCp);
                foreach (var v in world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != holder || v.Def.Boss || Vector2.Distance(v.Position, crate.Position) > 25f) continue;
                    var amount = world.Gear.Heal(v, v.MaxHp * CrateRepair);
                    if (amount <= 0f) continue;
                    world.Announce(SimEvent.RepairedBy(v, amount));
                }
                world.Announce(SimEvent.CrateClaimed(crate, holder));
            }
        }

        /// <summary>A bomber run across the busiest fight: the centre of the biggest clash between the armies.</summary>
        private bool Raid(SimWorld world)
        {
            if (!world.Catalog.TryGetSupport(RaidSupport, out var support)) return true;
            Vector2? best = null;
            var bestScore = 0;
            foreach (var a in world.VehicleList)
            {
                if (!a.IsAlive || a.Flying || a.Team != 0) continue;
                var score = 0;
                foreach (var b in world.VehicleList)
                    if (b.IsAlive && !b.Flying && b.Team == 1 && Vector2.Distance(a.Position, b.Position) < 35f) score++;
                if (score <= bestScore) continue;
                bestScore = score;
                best = a.Position;
            }
            if (best == null)
            {
                // No clash yet: the raid finds the biggest group of vehicles on the ground instead.
                var most = 2;
                foreach (var a in world.VehicleList)
                {
                    if (!a.IsAlive || a.Flying || a.Team < 0 || a.Def.Static) continue;
                    var count = 0;
                    foreach (var b in world.VehicleList)
                        if (b.IsAlive && !b.Flying && b.Team >= 0 && Vector2.Distance(a.Position, b.Position) < 25f) count++;
                    if (count <= most) continue;
                    most = count;
                    best = a.Position;
                }
            }
            if (best == null) return false;
            var angle = (float)(_random.NextDouble() * SimMath.Tau);
            var along = new Vector2(MathF.Cos(angle), MathF.Sin(angle));
            var start = best.Value - along * (support.Length * 0.5f);
            world.Strikes.Launch(support, Teams.Environment, start, start + along);
            return true;
        }
    }
}
