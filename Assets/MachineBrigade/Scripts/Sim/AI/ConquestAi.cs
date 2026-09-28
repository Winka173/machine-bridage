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
        /// <summary>
        /// Take ground: the weakest-held enemy or neutral point in reach, the army advancing in
        /// bounds, flanking, and pulling back to regroup when outmatched.
        /// </summary>
        Attack,

        /// <summary>
        /// Hold ground: the army stands on our point facing the enemy (the one under threat, else
        /// the one nearest them), chases only a short way off it, never falls back, and digs in:
        /// vehicles that stop go hull-down and take less damage (see <see cref="SimWorld.Entrench"/>).
        /// </summary>
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

        /// <summary>
        /// The army's intended mix by value (front line, fast, artillery, anti-air, aircraft); what
        /// is furthest below its share is bought first, before counters adjust it. Null picks a
        /// mix for the stance (a siege attacker brings more artillery).
        /// </summary>
        public float[]? RoleMix { get; set; }

        /// <summary>A mix for a siege attacker: guns to break the fortress from outside its reach.</summary>
        public static readonly float[] SiegeMix = { 0.35f, 0.08f, 0.30f, 0.12f, 0.15f };

        private static readonly float[] AttackMix = { 0.45f, 0.15f, 0.15f, 0.10f, 0.15f };
        private static readonly float[] DefendMix = { 0.50f, 0.12f, 0.15f, 0.18f, 0.05f };

        private enum Role { Front, Fast, Artillery, AntiAir, Air }

        private static Role RoleOf(VehicleDef def) =>
            def.Flying ? Role.Air
            : def.Weapon.MinRange > 0f ? Role.Artillery
            : def.Class == UnitClass.AntiAir || (CanHitAir(def) && def.Armor != ArmorClass.Heavy) ? Role.AntiAir
            : def.Speed >= 11f ? Role.Fast
            : Role.Front;

        private readonly float[] _have = new float[5];

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

        /// <summary>Enemy buildings to shoot up when nothing military is in reach (see <see cref="TacticalAi.Plunder"/>).</summary>
        public Func<SimWorld, IReadOnlyList<EntityId>>? Plunder
        {
            get => _tactics.Plunder;
            set => _tactics.Plunder = value;
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
            _tactics = new TacticalAi(team, enemyTeam, seed) { Objective = ChooseObjective, FallBackTo = SafePoint, Facing = Threat };
        }

        /// <summary>How far off the point it holds a defending army chases.</summary>
        private const float HoldReach = 26f;

        /// <summary>Which way the threat lies from the point being held: the enemy seen nearest it, else their camp.</summary>
        private Vector2? Threat(SimWorld world)
        {
            if (_holding is not { } held) return null;
            Vector2? nearest = null;
            var best = float.MaxValue;
            foreach (var e in _tactics.KnownEnemies)
            {
                if (e.Flying || e.Def.Static) continue;
                var d = Vector2.DistanceSquared(e.Position, held);
                if (d >= best) continue;
                best = d;
                nearest = e.Position;
            }
            var to = nearest ?? (world.TryGetRally(_enemyTeam, out var camp) ? camp : held + Vector2.UnitX);
            var along = to - held;
            return along.LengthSquared() > 1f ? Vector2.Normalize(along) : Vector2.UnitX;
        }

        /// <summary>The point the army is holding this decision (Defend), or null.</summary>
        private Vector2? _holding;

        private float Interval => _difficulty switch
        {
            AiDifficulty.Easy => 2.2f,
            AiDifficulty.Hard => 0.6f,
            _ => 1.1f,
        };

        public void Tick(SimWorld world, float dt)
        {
            var defend = Stance == CommanderStance.Defend;
            world.Entrench(_team, defend);
            _tactics.HoldLeash = defend && _holding != null ? HoldReach : null;
            _tactics.Tick(world, dt);
            _timer -= dt;
            if (_timer > 0f || world.IsOver) return;
            _timer = Interval;
            if (!world.TryGetEconomy(_team, out var economy)) return;
            if (AutoDeploy && TryRebuild(world, economy)) return;
            if (AutoStrike && TryStrike(world, economy)) return;
            if (AutoDeploy) TryDeploy(world, economy);
        }

        /// <summary>
        /// Flies a destroyed tower back into its hardpoint, the front one first, once the army has
        /// some body (a side with next to nothing on the field buys vehicles first) and the CP
        /// left over still buys a vehicle soon; sets a marked point up as an outpost the same way.
        /// </summary>
        private bool TryRebuild(SimWorld world, TeamEconomy economy)
        {
            var bases = world.Bases;
            if (bases.Of(_team) is not { } ours) return false;
            var callable = bases.Callable(_team);
            if (callable.Count > 0 && economy.ArmyCp >= 12)
            {
                var slot = callable[0];
                var cost = bases.CostOf(slot);
                if (economy.Cp >= cost + 4f && world.Submit(new Command(CommandType.CallTower, _team, Array.Empty<EntityId>(), slot.Def.Position)).Accepted)
                    return true;
            }
            // Outposts on marked points we hold: set up, then their towers.
            if (_mode == null || bases.OutpostPoints.Count == 0) return false;
            foreach (var point in _mode.Points)
            {
                if (point.Owner != _team || !bases.OutpostPoints.Contains(point.Def.Id) || point.Def.Outpost.Count == 0) continue;
                if (!ours.Outposts.TryGetValue(point.Def.Id, out var slots))
                {
                    if (economy.Cp >= world.Catalog.Base.OutpostCp + 6f &&
                        world.Submit(new Command(CommandType.Outpost, _team, Array.Empty<EntityId>(), defId: point.Def.Id)).Accepted) return true;
                    // Held and not yet set up: with an army on the field, save up for it rather
                    // than spend every CP as it comes in (it never reached the price otherwise).
                    if (economy.ArmyCp >= 16) return true;
                    continue;
                }
                for (var i = 0; i < slots.Count; i++)
                {
                    if (slots[i].Tower != null) continue;
                    var tower = ours.Loadout.Outpost.Count > 0 ? ours.Loadout.Outpost[i % ours.Loadout.Outpost.Count] : "guard_tower";
                    // A tower that does not fit the slot gives way to one of the loadout's that does.
                    if (world.Catalog.Vehicles.TryGetValue(tower, out var wanted) && wanted.Fort is { } fort && !fort.Fits(slots[i].Def.Class))
                    {
                        tower = "guard_tower";
                        foreach (var other in ours.Loadout.Outpost)
                            if (world.Catalog.Vehicles.TryGetValue(other, out var o) && o.Fort is { } f && f.Fits(slots[i].Def.Class))
                            {
                                tower = other;
                                break;
                            }
                    }
                    if (!world.Catalog.Vehicles.TryGetValue(tower, out var def)) continue;
                    if (economy.Cp < world.Catalog.Base.RebuildCost(def) + 4f) return false;
                    if (world.Submit(new Command(CommandType.CallTower, _team, Array.Empty<EntityId>(), slots[i].Def.Position, defId: tower)).Accepted) return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Neutral and enemy points are worth taking, contested ones are worth defending; nearer
        /// ones score higher. Null once every point is ours and quiet (push the enemy instead).
        /// </summary>
        private Vector2? ChooseObjective(SimWorld world)
        {
            _holding = null;
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
            world.TryGetRally(_enemyTeam, out var enemyCamp);
            var ownPower = ArmyPower(world);
            // Where they are thin only matters with a choice to make: the last point is attacked however hard it is held.
            var choices = 0;
            foreach (var point in _mode.Points)
                if (!point.Locked && point.Owner != _team) choices++;
            foreach (var point in _mode.Points)
            {
                if (point.Locked) continue;
                float score;
                if (defend)
                {
                    // Our points first, threatened ones most, then the one nearest the enemy (the
                    // front); take new ground only when we hold nothing.
                    var ours = point.Owner == _team;
                    score = ours ? 3f : point.Owner == -1 ? 1f : 0.5f;
                    if (point.Contested || (ours && (point.Progress * (_team == 0 ? 1f : -1f) < 0.99f || EnemyNear(world, point)))) score += 2f;
                    if (ours) score -= Vector2.Distance(point.Def.Position, enemyCamp) / 120f;
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
                    // Go where they are thin: every enemy seen dug in round a point (towers and
                    // defences included) counts against it, relative to our own strength.
                    else if (choices > 1) score -= MathF.Min(2f, Guard(point) / MathF.Max(3f, ownPower)) * 1.2f;
                }
                score -= Vector2.Distance(front, point.Def.Position) / 60f;
                if (score <= bestScore) continue;
                best = point;
                bestScore = score;
            }
            if (best == null || bestScore <= -1.5f) return null;
            if (defend && best.Owner == _team) _holding = best.Def.Position;
            return best.Def.Position;
        }

        /// <summary>Strength of the enemies seen round a point (a guess from what is in sight).</summary>
        private float Guard(ObjectiveState point)
        {
            var reach = point.Def.Radius + 18f;
            var total = 0f;
            foreach (var e in _tactics.KnownEnemies)
                if (!e.Flying && Vector2.Distance(e.Position, point.Def.Position) < reach) total += e.Def.Power * (e.Hp / e.MaxHp);
            return total;
        }

        private float ArmyPower(SimWorld world)
        {
            var total = 0f;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _team && !v.Def.Static && !v.Scripted) total += v.Def.Power * (v.Hp / v.MaxHp);
            return total;
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

            // The new supports first, each where it is worth its CP.
            if (TryUtilityStrike(world, economy, supports)) return true;

            var foundCluster = FindCluster(world, out var cluster, out var size);
            // A boss is worth the biggest strike on its own: aimed at its far side from our own
            // vehicles fighting it, so the bombs are not seen falling on them.
            foreach (var e in _tactics.KnownEnemies)
                if (e.Def.Boss && !e.Flying)
                {
                    cluster = e.Position;
                    if (OwnCentroid(world, e.Position, e.Radius + 16f, out var own))
                    {
                        var away = e.Position - own;
                        if (away.LengthSquared() > 0.01f) cluster = e.Position + Vector2.Normalize(away) * (e.Radius + 3f);
                    }
                    size = ClusterSize + 2;
                    foundCluster = true;
                    break;
                }
            if (!foundCluster) return false;
            SupportDef? pick = null;
            foreach (var id in supports)
            {
                var s = world.Catalog.Supports[id];
                if (s.Kind is SupportKind.Repair or SupportKind.Smoke or SupportKind.Scan or SupportKind.Minefield or SupportKind.Tower or SupportKind.Sead ||
                    !Ready(world, economy, s)) continue;
                // Save the big one for big targets.
                if (s.Kind == SupportKind.CruiseMissile && size < ClusterSize + 1) continue;
                if (pick == null || s.CpCost > pick.CpCost) pick = s;
            }
            if (pick == null) return false;
            world.TryGetRally(_team, out var home);
            var along = cluster - home;
            along = along.LengthSquared() > 1f ? Vector2.Normalize(along) : Vector2.UnitX;
            if (pick.IsLine)
            {
                // A bombing run is laid along a line clear of our own vehicles: the direction from
                // home first, then turned until it is clear; none clear, no run.
                if (!ClearRun(world, cluster, along, pick, out along)) return false;
            }
            else if (OwnWithin(world, cluster, pick.Radius + StrikeMargin) && !Boss(cluster)) return false;
            var start = pick.IsLine ? cluster - along * (pick.Length * 0.5f) : cluster;
            return world.Submit(Command.Strike(_team, pick.Id, world.ClampToMap(start), start + along)).Accepted;
        }

        /// <summary>
        /// The supports that are not blasts on a cluster:
        /// SEAD on enemy air defence when we fly aircraft (or have them in the deck);
        /// a field tower on a point we hold that the enemy is coming for;
        /// remote mines across the way of an enemy group closing on our line;
        /// a UAV scan over where the army is about to fight, or over stealth that hurt us.
        /// </summary>
        private bool TryUtilityStrike(SimWorld world, TeamEconomy economy, IEnumerable<string> supports)
        {
            foreach (var id in supports)
            {
                var s = world.Catalog.Supports[id];
                if (!Ready(world, economy, s)) continue;
                switch (s.Kind)
                {
                    case SupportKind.Sead when FlyingOrWillFly(world, economy):
                        foreach (var e in _tactics.KnownEnemies)
                        {
                            if (!e.IsAlive || e.Flying || !MachineBrigade.Sim.Strikes.StrikeSystem.IsAirDefence(e.Def) || world.InEnemyHome(e.Position, _team)) continue;
                            if (world.Submit(Command.Strike(_team, id, e.Position)).Accepted) return true;
                        }
                        break;

                    case SupportKind.Tower when _mode != null:
                        foreach (var p in _mode.Points)
                        {
                            if (p.Owner != _team) continue;
                            var threat = 0;
                            foreach (var e in _tactics.KnownEnemies)
                                if (e.IsAlive && !e.Flying && !e.Def.Static && Vector2.Distance(e.Position, p.Def.Position) < 45f) threat++;
                            if (threat < 2) continue;
                            world.TryGetRally(_team, out var home);
                            var back = home - p.Def.Position;
                            var at = world.ClampToMap(p.Def.Position + (back.LengthSquared() > 1f ? Vector2.Normalize(back) : Vector2.Zero) * 5f);
                            if (world.Submit(Command.Strike(_team, id, at, at + (p.Def.Position - home))).Accepted) return true;
                        }
                        break;

                    case SupportKind.Minefield:
                        if (FindCluster(world, out var group, out _) && OwnCentroid(world, group, 55f, out var line))
                        {
                            var gap = Vector2.Distance(group, line);
                            if (gap < 22f) break;
                            var at = group + Vector2.Normalize(line - group) * MathF.Min(14f, gap * 0.4f);
                            if (OwnWithin(world, at, s.Radius + 3f)) break;
                            if (world.Submit(Command.Strike(_team, id, world.ClampToMap(at))).Accepted) return true;
                        }
                        break;

                    case SupportKind.Scan:
                        if (ScanTarget(world, out var look) && world.Submit(Command.Strike(_team, id, look)).Accepted) return true;
                        break;
                }
            }
            return false;
        }

        /// <summary>The enemy's known towers by what they are good at, and the furthest reach among its cannon towers.</summary>
        private (int cannon, int machineGun, int antiAir) ReadBase(out float cannonReach)
        {
            int cannon = 0, mg = 0, aa = 0;
            cannonReach = 0f;
            foreach (var e in _tactics.KnownEnemies)
            {
                if (!e.IsAlive || !e.Def.Static || e.Def.Fort is not { Kind: FortKind.Tower } || e.Def.Passive) continue;
                var w = e.Def.Weapon;
                if (MachineBrigade.Sim.Strikes.StrikeSystem.IsAirDefence(e.Def) || w.Targets == TargetLayers.Air) aa++;
                else if (w.DamageType == DamageType.Kinetic || w.Projectile == ProjectileKind.Bullet) mg++;
                else if (w.MinRange <= 0f && w.Projectile == ProjectileKind.Shell)
                {
                    cannon++;
                    cannonReach = MathF.Max(cannonReach, w.Range);
                }
            }
            return (cannon, mg, aa);
        }

        /// <summary>
        /// What a card is worth against the enemy's base (supplement 5): against cannon towers (slow
        /// turrets, long reloads, nothing for aircraft) fast light vehicles, drones and artillery
        /// that outranges them; against machine-gun towers heavy armour; against a base full of
        /// anti-air fewer aircraft and more artillery. Nothing when no towers are known.
        /// </summary>
        private static float BaseCounter(VehicleDef def, (int cannon, int machineGun, int antiAir) towers, float cannonReach)
        {
            var total = towers.cannon + towers.machineGun + towers.antiAir;
            if (total == 0) return 0f;
            float Share(int n) => n / (float)total;
            var score = 0f;
            var drones = def.Drone;
            foreach (var m in def.Mounts) drones |= m.Weapon.Projectile == ProjectileKind.Drone;
            if (towers.cannon >= 2)
            {
                if (def.Speed >= 11f && def.Armor == ArmorClass.Light) score += 1.6f * Share(towers.cannon);
                if (drones) score += 1.6f * Share(towers.cannon);
                if (def.Weapon.MinRange > 0f && def.Weapon.Range > cannonReach + 5f) score += 1.4f * Share(towers.cannon);
            }
            if (towers.machineGun >= 2 && def.Armor == ArmorClass.Heavy && !def.Flying) score += 1.8f * Share(towers.machineGun);
            if (towers.antiAir >= 2)
            {
                if (def.Flying) score -= 2.2f * Share(towers.antiAir);
                if (def.Weapon.MinRange > 0f) score += 1.2f * Share(towers.antiAir);
            }
            return score;
        }

        /// <summary>Aircraft up, or in the deck with the CP to call one soon.</summary>
        private bool FlyingOrWillFly(SimWorld world, TeamEconomy economy)
        {
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _team && v.Flying) return true;
            foreach (var id in economy.Vehicles)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Flying && economy.Cp >= def.CpCost * 0.6f) return true;
            return false;
        }

        /// <summary>
        /// Where a scan pays: our vehicle hit in the last seconds by nothing we can see (stealth,
        /// a hidden gun), else the objective our army is closing on while no enemy there is seen.
        /// </summary>
        private bool ScanTarget(SimWorld world, out Vector2 at)
        {
            at = default;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Flying || world.Time - v.LastHitTime > 2.0) continue;
                if (!world.TryGetVehicle(v.LastAttacker, out var shooter) || !shooter.IsAlive || shooter.IsVisibleTo(_team)) continue;
                at = world.ClampToMap(v.Position + (shooter.Position - v.Position) * 0.6f);
                return true;
            }
            if (_mode == null || !OwnCentroid(world, world.ClampToMap(Vector2.Zero), 1000f, out var army)) return false;
            foreach (var p in _mode.Points)
            {
                if (p.Owner == _team) continue;
                var d = Vector2.Distance(p.Def.Position, army);
                if (d > 45f || d < 12f) continue;
                var seen = false;
                foreach (var e in _tactics.KnownEnemies)
                    if (e.IsAlive && Vector2.Distance(e.Position, p.Def.Position) < 25f) seen = true;
                if (seen) continue;
                at = p.Def.Position;
                return true;
            }
            return false;
        }

        /// <summary>Room left round a strike's blast before our own vehicles count as under it.</summary>
        private const float StrikeMargin = 5f;

        private bool Boss(Vector2 at)
        {
            foreach (var e in _tactics.KnownEnemies)
                if (e.Def.Boss && Vector2.Distance(e.Position, at) < e.Radius + 8f) return true;
            return false;
        }

        /// <summary>Any of our own ground vehicles within reach of a point (aircraft fly above the blasts).</summary>
        private bool OwnWithin(SimWorld world, Vector2 at, float reach)
        {
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _team && !v.Flying && Vector2.Distance(v.Position, at) < reach + v.Radius) return true;
            return false;
        }

        private bool OwnCentroid(SimWorld world, Vector2 at, float reach, out Vector2 centre)
        {
            centre = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Flying || Vector2.Distance(v.Position, at) > reach) continue;
                centre += v.Position;
                n++;
            }
            if (n == 0) return false;
            centre /= n;
            return true;
        }

        /// <summary>A direction for a bombing run over <paramref name="centre"/> that stays clear of our own vehicles.</summary>
        private bool ClearRun(SimWorld world, Vector2 centre, Vector2 preferred, SupportDef strike, out Vector2 direction)
        {
            var reach = strike.Radius + StrikeMargin;
            for (var turn = 0; turn < 8; turn++)
            {
                // 0, +45, -45, +90, -90, +135, -135, 180 degrees from the preferred direction.
                var angle = (turn + 1) / 2 * (MathF.PI / 4f) * (turn % 2 == 1 ? 1f : -1f);
                direction = SimMath.Rotate(preferred, angle);
                var clear = true;
                for (var s = -4; s <= 4 && clear; s++)
                    if (OwnWithin(world, centre + direction * (strike.Length * 0.5f * s / 4f), reach)) clear = false;
                if (clear) return true;
            }
            direction = preferred;
            return false;
        }

        private void TryDeploy(SimWorld world, TeamEconomy economy)
        {
            var cards = Cards(world, economy.Vehicles, world.Catalog.Vehicles.Keys);
            var airFull = world.Economy.AircraftCount(_team) >= TeamEconomy.MaxAircraft;
            string? best = null, bestAffordable = null;
            var bestScore = float.MinValue;
            var bestAffordableScore = float.MinValue;
            CountEnemies(out var air, out var heavy, out var light);
            CountOwn(world, out var ownAa, out var ownArtillery, out var ownAir, out var ownTotal);
            var enemy = EnemyMix();
            var answer = OwnAnswers(world);
            var enemyGuns = 0;
            foreach (var e in _tactics.KnownEnemies)
                if (e.IsAlive && !e.Def.Static && e.Def.Weapon.MinRange > 0f) enemyGuns++;
            var towers = ReadBase(out var towerReach);
            var neutral = 0;
            if (_mode != null)
                foreach (var p in _mode.Points)
                    if (p.Owner != _team) neutral++;
            var owned = new Dictionary<string, int>();
            var capturers = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _team) continue;
                owned[v.Def.Id] = owned.TryGetValue(v.Def.Id, out var n) ? n + 1 : 1;
                if (!v.Flying && v.Def.CaptureRate > 0f && !v.Def.Static) capturers++;
            }
            // A structure to bring down (a fortress HQ, a demolition target) wants high explosive.
            var demolishing = Demolish != null && world.TryGetProp(Demolish(world), out var building) && building.IsAlive;
            // How the army's value is split between the roles now (deliveries on the way included).
            Array.Clear(_have, 0, _have.Length);
            var armyValue = 0f;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Def.Static || v.Scripted) continue;
                _have[(int)RoleOf(v.Def)] += v.Def.CpCost;
                armyValue += v.Def.CpCost;
            }
            var mix = RoleMix ?? (Stance == CommanderStance.Defend ? DefendMix : AttackMix);

            foreach (var id in cards)
            {
                var def = world.Catalog.Vehicles[id];
                // Bosses and mission trucks cost nothing and are never bought.
                if (def.Boss || def.CpCost <= 0) continue;
                if (economy.VehicleCount >= TeamEconomy.MaxVehicles) continue;
                if (def.MaxPerSide > 0 && world.Economy.Fielded(_team, id) >= def.MaxPerSide) continue;
                if (def.Flying && airFull) continue;
                var score = 1f + (float)_random.NextDouble() * (_difficulty == AiDifficulty.Easy ? 3f : 0.8f);
                if (_difficulty != AiDifficulty.Easy)
                {
                    var main = def.Weapon;
                    score += CounterScore(def, enemy, answer);
                    // Keep about a seventh of the army in the air: aircraft are fast and hit hard,
                    // but dear, and anti-air is what they are for.
                    if (def.Flying) score += (ownAir * 7 < ownTotal + 2 ? 1.2f : -2f) + heavy * 0.25f - air * 0.3f;
                    // An interceptor with no enemy aircraft to hunt is dead weight (a fighter sent at a ground boss dies for nothing).
                    if (def.Flying && def.Weapon.Targets == TargetLayers.Air && air <= 0) score -= 2.5f;
                    if (main.MinRange > 0f) score += ownArtillery * 5 < ownTotal ? 1.2f : -2f;
                    score += def.CaptureRate * neutral * 0.35f;
                    // Enough anti-air for the enemy's aircraft, not a car park of it.
                    if (def.Class == UnitClass.AntiAir) score -= MathF.Max(0f, ownAa - air * 0.7f - 1f) * 1.2f;
                    // Points are taken on the ground: keep a core of vehicles that can capture.
                    if (neutral > 0 && capturers < 4) score += def.Flying || def.CaptureRate <= 0f ? -2.5f : 1.2f;
                    if (demolishing)
                    {
                        if (main.DamageType == DamageType.HighExplosive) score += 1.6f;
                        if (def.Class == UnitClass.AntiAir) score -= 1.5f;
                    }
                    score += BaseCounter(def, towers, towerReach);
                    // A command vehicle pays once there is an army round it to lead.
                    if (def.CommandAura != null) score += ownTotal >= 5 ? 1.4f : -2f;
                    // A counter-battery radar only where the enemy has guns to find.
                    if (def.CounterBattery != null) score += enemyGuns > 0 ? MathF.Min(2.4f, enemyGuns * 0.8f) - 0.6f : -2.5f;
                }
                // The role furthest below its share of the army comes first (OpenRA's and 0 A.D.'s
                // unit-share quotas): an army of one kind is easy to counter.
                if (_difficulty != AiDifficulty.Easy && armyValue > 0f)
                    score += (mix[(int)RoleOf(def)] - _have[(int)RoleOf(def)] / armyValue) * 5f;
                // A mixed army: each copy already fielded makes another less attractive.
                if (owned.TryGetValue(id, out var copies)) score -= copies * 0.45f;
                // Bigger vehicles are worth saving for (except on Easy, which spends as it earns).
                if (_difficulty != AiDifficulty.Easy) score += def.CpCost * 0.22f;
                if (score > bestScore)
                {
                    best = id;
                    bestScore = score;
                }
                if (economy.CostOf(id, def.CpCost) <= economy.Cp && score > bestAffordableScore)
                {
                    bestAffordable = id;
                    bestAffordableScore = score;
                }
            }
            if (best == null) return;
            var bestCost = economy.CostOf(best, world.Catalog.Vehicles[best].CpCost);
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

        private static IEnumerable<string> Cards(SimWorld world, IReadOnlyList<string> deck, IEnumerable<string> all)
        {
            if (deck.Count > 0) return deck;
            // Items are bought with coins by the player; the AI never has any.
            var cards = new List<string>();
            foreach (var id in all)
                if (!world.Catalog.TryGetSupport(id, out var support) || !(support.Consumable || support.EventOnly)) cards.Add(id);
            return cards;
        }

        private bool FindCluster(SimWorld world, out Vector2 centre, out int size)
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
                // Never a cluster our own vehicles are fighting in: the bombs would fall on them too.
                if (OwnWithin(world, sum / around, ClusterRadius + StrikeMargin)) continue;
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

        /// <summary>The value (CP) of what the enemy fields that the AI has seen, by kind.</summary>
        private struct Mix
        {
            public float Air, Heavy, Light, Artillery, AntiAir, Total;
        }

        private Mix EnemyMix()
        {
            var mix = new Mix();
            foreach (var e in _tactics.KnownEnemies)
            {
                if (e.Def.Static) continue;
                // A boss weighs as much as a small army of its kind.
                var value = e.Def.Boss ? 30f : MathF.Max(1f, e.Def.CpCost);
                if (e.Flying) mix.Air += value;
                else if (e.Def.Weapon.MinRange > 0f) mix.Artillery += value;
                else if (e.Armor == ArmorClass.Heavy) mix.Heavy += value;
                else mix.Light += value;
                if (CanHitAir(e.Def)) mix.AntiAir += value;
                mix.Total += value;
            }
            return mix;
        }

        /// <summary>The value (CP) of our own vehicles that answer each kind of enemy: anti-air (fighters included), anti-armour, anti-light, and hunters fast enough to catch artillery.</summary>
        private Mix OwnAnswers(SimWorld world)
        {
            var mix = new Mix();
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Def.Static || v.Scripted) continue;
                var value = MathF.Max(1f, v.Def.CpCost);
                if (CanHitAir(v.Def)) mix.Air += value;
                if (KillsArmour(v.Def)) mix.Heavy += value;
                if (v.Def.Weapon.DamageType is DamageType.Kinetic or DamageType.Fire or DamageType.HighExplosive && v.Def.Weapon.MinRange <= 0f)
                    mix.Light += value;
                if (v.Def.Flying || v.Def.Speed >= 11f) mix.Artillery += value;
                mix.Total += value;
            }
            return mix;
        }

        private static bool KillsArmour(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.DamageType == DamageType.ArmorPiercing && m.Weapon.CanTarget(false)) return true;
            return false;
        }

        /// <summary>
        /// How much a vehicle answers what the enemy fields, against what we already have for it: a
        /// kind of enemy worth a third of its army wants about a third of ours able to kill it. Lots
        /// of enemy aircraft: anti-air and fighters; none: no anti-air. Heavy armour: guns and missiles
        /// that pierce it. Light vehicles: machine guns, flame and blast. Artillery: aircraft and fast
        /// raiders. An enemy thick with anti-air: fewer aircraft of our own.
        /// </summary>
        private static float CounterScore(VehicleDef def, Mix enemy, Mix own)
        {
            if (enemy.Total <= 0f) return 0f;
            var ours = MathF.Max(8f, own.Total);
            float Short(float theirs, float answering) => theirs / enemy.Total - answering / ours * 0.85f;
            var score = 0f;
            var antiAir = CanHitAir(def);
            if (antiAir)
            {
                score += Short(enemy.Air, own.Air) * 8f;
                // The first answer to aircraft matters most.
                if (enemy.Air > 0f && own.Air <= 0f) score += 2f;
                // No aircraft over there: a dedicated anti-air vehicle is dead weight.
                if (enemy.Air <= 0f && def.Class == UnitClass.AntiAir) score -= 2.5f;
            }
            if (KillsArmour(def)) score += Short(enemy.Heavy, own.Heavy) * 6f;
            if (def.Weapon.DamageType is DamageType.Kinetic or DamageType.Fire or DamageType.HighExplosive && def.Weapon.MinRange <= 0f)
                score += Short(enemy.Light, own.Light) * 4f;
            if (def.Flying || def.Speed >= 11f) score += Short(enemy.Artillery, own.Artillery) * 4f;
            if (def.Flying && !antiAir) score -= enemy.AntiAir / enemy.Total * 4f;
            return score;
        }

        private void CountEnemies(out int air, out int heavy, out int light)
        {
            air = heavy = light = 0;
            foreach (var e in _tactics.KnownEnemies)
            {
                if (e.Def.Static) continue;
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
                if (!v.IsAlive || v.Team != _team || v.Def.Static) continue;
                total++;
                if (v.Def.Flying) air++;
                // Fighters answer aircraft as well as anti-air vehicles do.
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
