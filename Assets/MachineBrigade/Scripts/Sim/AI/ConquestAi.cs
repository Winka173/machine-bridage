#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
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

    /// <summary>The commander's general intent.</summary>
    public enum CommanderStance
    {
        /// <summary>Take neutral and enemy objectives.</summary>
        Attack,

        /// <summary>Hold what we have: go where our objectives are threatened.</summary>
        Defend,
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

        private readonly IObjectiveMode? _mode;
        private readonly int _team;
        private readonly int _enemyTeam;
        private readonly AiDifficulty _difficulty;
        private readonly Random _random;
        private readonly TacticalAi _tactics;
        private float _timer;

        /// <summary>Last seen hold on each point (1 = fully ours), to notice points being drained.</summary>
        private readonly Dictionary<string, float> _lastHold = new();

        /// <summary>Buy vehicles from the deck automatically.</summary>
        public bool AutoDeploy { get; set; } = true;

        /// <summary>Call fire support automatically.</summary>
        public bool AutoStrike { get; set; } = true;

        public CommanderStance Stance { get; set; } = CommanderStance.Attack;

        /// <summary>Objective id the army should concentrate on; null lets the commander choose.</summary>
        public string? FocusPoint { get; set; }

        /// <summary>
        /// Where the mission wants the army (a convoy to guard, a boss to hunt); checked after
        /// <see cref="FocusPoint"/> and before the objectives.
        /// </summary>
        public Func<SimWorld, Vector2?>? Goal { get; set; }

        /// <summary>How far from <see cref="Goal"/> the army may chase (see <see cref="TacticalAi.Leash"/>).</summary>
        public float? Leash
        {
            get => _tactics.Leash;
            set => _tactics.Leash = value;
        }

        /// <summary>A structure to knock down (see <see cref="TacticalAi.Demolish"/>).</summary>
        public Func<SimWorld, EntityId>? Demolish
        {
            get => _tactics.Demolish;
            set => _tactics.Demolish = value;
        }

        /// <summary>Where to hold when there are no objectives (Survival).</summary>
        public Vector2? DefendPoint { get; set; }

        /// <param name="mode">
        /// The objectives to fight over; null for modes without them: the army holds
        /// <see cref="DefendPoint"/>, or hunts the enemy when there is none.
        /// </param>
        public ConquestAi(IObjectiveMode? mode, int team, int enemyTeam, AiDifficulty difficulty = AiDifficulty.Normal, int seed = 11)
        {
            _mode = mode;
            _team = team;
            _enemyTeam = enemyTeam;
            _difficulty = difficulty;
            _random = new Random(seed);
            _tactics = new TacticalAi(team, enemyTeam, seed) { Objective = ChooseObjective, FallBackTo = SafePoint };
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
            if (AutoStrike && TryStrike(world, economy)) return;
            if (AutoDeploy) TryDeploy(world, economy);
        }

        /// <summary>
        /// Neutral and enemy points are worth taking, contested ones are worth defending; nearer
        /// ones score higher. Null once every point is ours and quiet (push the enemy instead).
        /// </summary>
        private Vector2? ChooseObjective(SimWorld world)
        {
            if (FocusPoint != null && _mode != null)
                foreach (var point in _mode.Points)
                    if (point.Def.Id == FocusPoint) return point.Def.Position;
            if (Goal != null && Goal(world) is { } goal) return goal;
            if (_mode == null || _mode.Points.Count == 0) return DefendPoint;
            var front = Centre(world, out var any);
            if (!any) world.TryGetRally(_team, out front);
            ObjectiveState? best = null;
            var bestScore = float.MinValue;
            var defend = Stance == CommanderStance.Defend;
            foreach (var point in _mode.Points)
            {
                float score;
                if (defend)
                {
                    // Our points first, threatened ones most; take new ground only when we hold nothing.
                    score = point.Owner == _team ? 3f : point.Owner == -1 ? 1f : 0.5f;
                    if (point.Contested || (point.Owner == _team && point.Progress * (_team == 0 ? 1f : -1f) < 0.99f)) score += 2f;
                }
                else
                {
                    // Our points only matter when threatened: being drained (even by a lone scout
                    // the capture rules do not count as contesting) or with enemies closing in.
                    var ours = point.Owner == _team;
                    var threatened = point.Contested || (ours && (Draining(point) || EnemyNear(world, point)));
                    score = ours ? 0f : point.Owner == _enemyTeam ? 2.2f : 3f;
                    if (point.Contested) score += 1.5f;
                    if (ours) score += threatened ? 2.5f : -2f;
                }
                score -= Vector2.Distance(front, point.Def.Position) / 60f;
                if (score <= bestScore) continue;
                best = point;
                bestScore = score;
            }
            return best != null && bestScore > -1.5f ? best.Def.Position : null;
        }

        /// <summary>
        /// Outmatched at the front: the point we hold that lies between the front and home,
        /// nearest the front, where the army can dig in and meet the attack together.
        /// </summary>
        private Vector2? SafePoint(SimWorld world, Vector2 front)
        {
            if (_mode == null || !world.TryGetRally(_team, out var home)) return null;
            Vector2? best = null;
            var bestDistance = float.MaxValue;
            var frontToHome = Vector2.Distance(front, home);
            foreach (var point in _mode.Points)
            {
                if (point.Owner != _team) continue;
                var p = point.Def.Position;
                var distance = Vector2.Distance(front, p);
                if (distance < 15f || Vector2.Distance(p, home) > frontToHome) continue;
                if (distance >= bestDistance) continue;
                best = p;
                bestDistance = distance;
            }
            return best;
        }

        private bool Draining(ObjectiveState point)
        {
            var hold = point.Progress * (_team == 0 ? 1f : -1f);
            var draining = _lastHold.TryGetValue(point.Def.Id, out var before) && hold < before - 0.001f;
            _lastHold[point.Def.Id] = hold;
            return draining;
        }

        private bool EnemyNear(SimWorld world, ObjectiveState point)
        {
            var reach = point.Def.Radius + 8f;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _enemyTeam && !v.Flying && v.IsVisibleTo(_team) &&
                    Vector2.Distance(v.Position, point.Def.Position) < reach) return true;
            return false;
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

            var foundCluster = FindCluster(out var cluster, out var size);
            // A boss is worth the biggest strike on its own.
            foreach (var e in _tactics.KnownEnemies)
                if (e.Def.Boss && !e.Flying)
                {
                    cluster = e.Position;
                    size = ClusterSize + 2;
                    foundCluster = true;
                    break;
                }
            if (!foundCluster) return false;
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
            string? best = null, bestAffordable = null;
            var bestScore = float.MinValue;
            var bestAffordableScore = float.MinValue;
            CountEnemies(out var air, out var heavy, out var light);
            CountOwn(world, out var ownAa, out var ownArtillery, out var ownAir, out var ownTotal);
            var neutral = 0;
            if (_mode != null)
                foreach (var p in _mode.Points)
                    if (p.Owner != _team) neutral++;
            var owned = new Dictionary<string, int>();
            foreach (var v in world.Vehicles)
                if (v.IsAlive && v.Team == _team) owned[v.Def.Id] = owned.TryGetValue(v.Def.Id, out var n) ? n + 1 : 1;

            foreach (var id in cards)
            {
                var def = world.Catalog.Vehicles[id];
                // Bosses and mission trucks cost nothing and are never bought.
                if (def.Boss || def.CpCost <= 0) continue;
                if (economy.ArmyCp + def.CpCost > economy.ArmyCap) continue;
                var score = 1f + (float)_random.NextDouble() * (_difficulty == AiDifficulty.Easy ? 3f : 0.8f);
                if (_difficulty != AiDifficulty.Easy)
                {
                    var main = def.Weapon;
                    if (CanHitAir(def)) score += air * 2.2f - ownAa * 1.5f;
                    if (main.DamageType == DamageType.ArmorPiercing) score += heavy * 0.6f;
                    if (main.DamageType is DamageType.Kinetic or DamageType.Fire) score += light * 0.5f;
                    // Keep about a fifth of the army in the air: aircraft are fast, hit hard and
                    // make the enemy spend on anti-air.
                    if (def.Flying) score += (ownAir * 5 < ownTotal + 3 ? 1.8f : -1.2f) + heavy * 0.35f - air * 0.25f;
                    if (main.MinRange > 0f) score += ownArtillery * 5 < ownTotal ? 1.2f : -2f;
                    score += def.CaptureRate * neutral * 0.35f;
                }
                // A mixed army: each copy already fielded makes another less attractive.
                if (owned.TryGetValue(id, out var copies)) score -= copies * 0.45f;
                // Bigger vehicles are worth saving for (except on Easy, which spends as it earns).
                if (_difficulty != AiDifficulty.Easy) score += def.CpCost * 0.22f;
                if (score > bestScore)
                {
                    best = id;
                    bestScore = score;
                }
                if (def.CpCost <= economy.Cp && score > bestAffordableScore)
                {
                    bestAffordable = id;
                    bestAffordableScore = score;
                }
            }
            if (best == null) return;
            var bestCost = world.Catalog.Vehicles[best].CpCost;
            if (bestCost <= economy.Cp)
            {
                world.Submit(Command.Deploy(_team, best));
                return;
            }
            // Save up for the best card, unless the army is thin or CP is about to overflow.
            if (bestAffordable != null && (ownTotal < 4 || economy.Cp >= economy.Bank - 3f || _difficulty == AiDifficulty.Easy))
                world.Submit(Command.Deploy(_team, bestAffordable));
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
            // Scripted convoys are left to direct fire: a column of trucks would draw every strike.
            foreach (var e in _tactics.KnownEnemies)
            {
                if (e.Flying || e.Scripted) continue;
                var around = 0;
                var sum = Vector2.Zero;
                foreach (var other in _tactics.KnownEnemies)
                {
                    if (other.Flying || other.Scripted || Vector2.Distance(other.Position, e.Position) > ClusterRadius) continue;
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

        private void CountOwn(SimWorld world, out int aa, out int artillery, out int air, out int total)
        {
            aa = artillery = air = total = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _team) continue;
                total++;
                if (v.Def.Flying) air++;
                else if (CanHitAir(v.Def)) aa++;
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
