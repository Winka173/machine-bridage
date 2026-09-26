#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Sim.AI
{
    public enum AiDifficulty
    {
        Easy,
        Normal,
        Hard,
    }

    /// <summary>
    /// The Conquest opponent: <see cref="TacticalAi"/> fights the battle, and this layer spends
    /// Command Points and picks objectives (game plan section 9). It counter-picks against what it
    /// has seen, shells clusters of three or more vehicles, repairs damaged groups and heads for
    /// the objective that is worth most. Difficulty changes how often it decides and how well it
    /// picks; it never gets free units or CP.
    /// </summary>
    public sealed class ConquestAi
    {
        private const int ClusterSize = 3;
        private const float ClusterRadius = 9f;

        private readonly ConquestMode _mode;
        private readonly int _team;
        private readonly int _enemyTeam;
        private readonly AiDifficulty _difficulty;
        private readonly Random _random;
        private readonly TacticalAi _tactics;
        private float _timer;

        public ConquestAi(ConquestMode mode, int team, int enemyTeam, AiDifficulty difficulty = AiDifficulty.Normal, int seed = 11)
        {
            _mode = mode;
            _team = team;
            _enemyTeam = enemyTeam;
            _difficulty = difficulty;
            _random = new Random(seed);
            _tactics = new TacticalAi(team, enemyTeam, seed) { Objective = ChooseObjective };
        }

        private float Interval => _difficulty switch
        {
            AiDifficulty.Easy => 2.2f,
            AiDifficulty.Hard => 0.6f,
            _ => 1.1f,
        };

        public void Tick(SimWorld world, float dt)
        {
            _tactics.Tick(world, dt);
            _timer -= dt;
            if (_timer > 0f || world.IsOver) return;
            _timer = Interval;
            if (!world.TryGetEconomy(_team, out var economy)) return;
            if (TryStrike(world, economy)) return;
            TryDeploy(world, economy);
        }

        /// <summary>
        /// Neutral and enemy points are worth taking, contested ones are worth defending; nearer
        /// ones score higher. Null once every point is ours and quiet (push the enemy instead).
        /// </summary>
        private Vector2? ChooseObjective(SimWorld world)
        {
            if (_mode.Points.Count == 0) return null;
            var front = Centre(world, out var any);
            if (!any) world.TryGetRally(_team, out front);
            ObjectiveState? best = null;
            var bestScore = float.MinValue;
            foreach (var point in _mode.Points)
            {
                var score = point.Owner == _team ? 0f : point.Owner == _enemyTeam ? 2.2f : 3f;
                if (point.Contested) score += 1.5f;
                if (point.Owner == _team && !point.Contested) score -= 2f;
                score -= Vector2.Distance(front, point.Def.Position) / 60f;
                if (score <= bestScore) continue;
                best = point;
                bestScore = score;
            }
            return best != null && bestScore > -1.5f ? best.Def.Position : null;
        }

        private bool TryStrike(SimWorld world, TeamEconomy economy)
        {
            if (_difficulty == AiDifficulty.Easy && _random.NextDouble() < 0.6) return false;
            var supports = Cards(world, economy.Supports, world.Catalog.Supports.Keys);
            // Repair a battered group first.
            if (FindDamagedGroup(world, out var hurt))
                foreach (var id in supports)
                {
                    var s = world.Catalog.Supports[id];
                    if (s.Kind == SupportKind.Repair && Ready(world, economy, s) &&
                        world.Submit(Command.Strike(_team, id, hurt)).Accepted) return true;
                }

            if (!FindCluster(out var cluster, out var size)) return false;
            SupportDef? pick = null;
            foreach (var id in supports)
            {
                var s = world.Catalog.Supports[id];
                if (s.Kind is SupportKind.Repair or SupportKind.Smoke || !Ready(world, economy, s)) continue;
                // Save the big one for big targets.
                if (s.Kind == SupportKind.CruiseMissile && size < ClusterSize + 1) continue;
                if (pick == null || s.CpCost > pick.CpCost) pick = s;
            }
            if (pick == null) return false;
            world.TryGetRally(_team, out var home);
            var along = cluster - home;
            along = along.LengthSquared() > 1f ? Vector2.Normalize(along) : Vector2.UnitX;
            var start = pick.IsLine ? cluster - along * (pick.Length * 0.5f) : cluster;
            return world.Submit(Command.Strike(_team, pick.Id, world.ClampToMap(start), start + along)).Accepted;
        }

        private void TryDeploy(SimWorld world, TeamEconomy economy)
        {
            var cards = Cards(world, economy.Vehicles, world.Catalog.Vehicles.Keys);
            string? best = null;
            var bestScore = float.MinValue;
            CountEnemies(out var air, out var heavy, out var light);
            CountOwn(world, out var ownAa, out var ownArtillery, out var ownTotal);
            var neutral = 0;
            foreach (var p in _mode.Points)
                if (p.Owner != _team) neutral++;

            foreach (var id in cards)
            {
                var def = world.Catalog.Vehicles[id];
                if (def.CpCost > economy.Cp || economy.ArmyCp + def.CpCost > economy.ArmyCap) continue;
                var score = 1f + (float)_random.NextDouble() * (_difficulty == AiDifficulty.Easy ? 3f : 0.8f);
                if (_difficulty != AiDifficulty.Easy)
                {
                    var main = def.Weapon;
                    if (CanHitAir(def)) score += air * 2.2f - ownAa * 1.5f;
                    if (main.DamageType == DamageType.ArmorPiercing) score += heavy * 0.6f;
                    if (main.DamageType is DamageType.Kinetic or DamageType.Fire) score += light * 0.5f;
                    if (def.Flying) score += heavy * 0.35f - air * 0.3f;
                    if (main.MinRange > 0f) score += ownArtillery * 5 < ownTotal ? 1.2f : -2f;
                    score += def.CaptureRate * neutral * 0.35f;
                }
                // Spend efficiently: prefer cards that use most of what we can afford.
                score += def.CpCost / MathF.Max(6f, economy.Cp) * 0.8f;
                if (score <= bestScore) continue;
                best = id;
                bestScore = score;
            }
            if (best != null) world.Submit(Command.Deploy(_team, best));
        }

        private static bool CanHitAir(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.CanTarget(true) && m.Weapon.DamageType == DamageType.Flak) return true;
            return false;
        }

        private static bool Ready(SimWorld world, TeamEconomy economy, SupportDef s) =>
            economy.Cp >= s.CpCost && economy.CooldownLeft(s.Id, world.Time) <= 0f;

        private static IEnumerable<string> Cards(SimWorld world, IReadOnlyList<string> deck, IEnumerable<string> all) =>
            deck.Count > 0 ? deck : all;

        private bool FindCluster(out Vector2 centre, out int size)
        {
            centre = default;
            size = 0;
            foreach (var e in _tactics.KnownEnemies)
            {
                if (e.Flying) continue;
                var around = 0;
                var sum = Vector2.Zero;
                foreach (var other in _tactics.KnownEnemies)
                {
                    if (other.Flying || Vector2.Distance(other.Position, e.Position) > ClusterRadius) continue;
                    around++;
                    sum += other.Position;
                }
                if (around < ClusterSize || around <= size) continue;
                size = around;
                centre = sum / around;
            }
            return size >= ClusterSize;
        }

        private bool FindDamagedGroup(SimWorld world, out Vector2 centre)
        {
            centre = default;
            var best = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _team || v.Hp / v.MaxHp > 0.5f) continue;
                var near = 0;
                var sum = Vector2.Zero;
                foreach (var other in world.Vehicles)
                {
                    if (!other.IsAlive || other.Team != _team || other.Hp / other.MaxHp > 0.6f ||
                        Vector2.Distance(other.Position, v.Position) > 10f) continue;
                    near++;
                    sum += other.Position;
                }
                if (near < 2 || near <= best) continue;
                best = near;
                centre = sum / near;
            }
            return best >= 2;
        }

        private void CountEnemies(out int air, out int heavy, out int light)
        {
            air = heavy = light = 0;
            foreach (var e in _tactics.KnownEnemies)
            {
                if (e.Flying) air++;
                else if (e.Armor == ArmorClass.Heavy) heavy++;
                else light++;
            }
        }

        private void CountOwn(SimWorld world, out int aa, out int artillery, out int total)
        {
            aa = artillery = total = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _team) continue;
                total++;
                if (CanHitAir(v.Def)) aa++;
                if (v.Def.Weapon.MinRange > 0f) artillery++;
            }
        }

        private Vector2 Centre(SimWorld world, out bool any)
        {
            var sum = Vector2.Zero;
            var count = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _team || v.Flying) continue;
                sum += v.Position;
                count++;
            }
            any = count > 0;
            return any ? sum / count : Vector2.Zero;
        }
    }
}
