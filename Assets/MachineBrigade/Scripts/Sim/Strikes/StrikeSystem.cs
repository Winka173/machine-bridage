#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Strikes
{
    /// <summary>A cloud that blocks sight through it until it disperses.</summary>
    internal readonly struct SmokeZone
    {
        public SmokeZone(Vector2 centre, float radius, double until)
        {
            Centre = centre;
            Radius = radius;
            Until = until;
        }

        public Vector2 Centre { get; }
        public float Radius { get; }
        public double Until { get; }
    }

    /// <summary>
    /// Fire support (game plan section 5): barrages, airstrikes, cruise missiles, smoke and repair.
    /// Every strike is announced with a telegraph and lands after its delay, so the other side can
    /// scatter. Damage goes through the same splash rules as weapons and spares the caller's team.
    /// </summary>
    internal sealed class StrikeSystem
    {
        /// <summary>Strike aircraft enter this far outside the map edge.</summary>
        private const float Approach = 70f;

        /// <summary>Seconds from the aircraft appearing to its first bomb.</summary>
        private const float RunIn = 1.4f;

        private sealed class Strike
        {
            public SupportDef Support = null!;
            public int Team;
            public Vector2 Point, Direction;
            public double Start;
            public int Done;
            public bool Announced;

            /// <summary>Spread multiplier: fire support called into an enemy jammer's bubble lands wide.</summary>
            public float Scatter = 1f;

            /// <summary>An airstrike's bomb line, bombs and seconds over it (longer from the card's rank: see SupportDef.LineRank).</summary>
            public float Length, Duration;
            public int Count;

            /// <summary>Where each round of a barrage lands, aimed a moment before it does (so it can be seen coming down).</summary>
            public readonly List<Vector2> Planned = new();

            /// <summary>A SEAD strike's quarry, picked as its missile fires (none: nothing in reach).</summary>
            public EntityId Victim = EntityId.None;
            public bool Aimed;
        }

        /// <summary>Seconds a fire-support round is seen falling before it lands.</summary>
        private const float ShellFall = 0.9f;

        private readonly SimWorld _world;
        private readonly List<Strike> _strikes = new();
        private readonly List<SmokeZone> _smoke = new();

        /// <summary>A UAV over a circle: everything in it shows to Team until Until.</summary>
        private readonly struct ScanZone
        {
            public ScanZone(Vector2 centre, float radius, double until, int team)
            {
                Centre = centre;
                Radius = radius;
                Until = until;
                Team = team;
            }

            public Vector2 Centre { get; }
            public float Radius { get; }
            public double Until { get; }
            public int Team { get; }
        }

        private readonly List<ScanZone> _scans = new();
        private readonly Dictionary<string, MineLayerDef> _mineDefs = new();

        /// <summary>The teams (a mask) whose UAV scan covers a point, other than <paramref name="owner"/>'s own.</summary>
        public int ScanMask(Vector2 at, int owner)
        {
            var mask = 0;
            foreach (var z in _scans)
                if (z.Team != owner && z.Team >= 0 && z.Team < 31 && Vector2.DistanceSquared(z.Centre, at) <= z.Radius * z.Radius) mask |= 1 << z.Team;
            return mask;
        }

        public StrikeSystem(SimWorld world) => _world = world;

        public IReadOnlyList<SmokeZone> Smoke => _smoke;

        public CommandResult Call(Command command)
        {
            if (command.DefId == null || !_world.Catalog.TryGetSupport(command.DefId, out var support))
                return CommandResult.Rejected(CommandError.UnknownCard);
            if (!SimMath.IsFinite(command.Point)) return CommandResult.Rejected(CommandError.InvalidPoint);
            if (!_world.Map.Contains(command.Point)) return CommandResult.Rejected(CommandError.OutOfBounds);
            // Home zones: no strikes on the enemy's camp (and never a tower dropped into it).
            if (_world.InEnemyHome(command.Point, command.Team)) return CommandResult.Rejected(CommandError.InvalidPoint);
            if (support.Kind == SupportKind.Tower && (_world.InEnemyCamp(command.Point, command.Team) || !_world.Grid.IsWalkable(command.Point)))
                return CommandResult.Rejected(CommandError.InvalidPoint);

            var economy = _world.Economy.TryGet(command.Team, out var e) ? e : null;
            if (support.Consumable)
            {
                // Items are not in the deck and cost no CP, but each use spends one.
                if (economy == null || economy.ItemCount(support.Id) <= 0) return CommandResult.Rejected(CommandError.UnknownCard);
                if (economy.CooldownLeft(support.Id, _world.Time) > 0f) return CommandResult.Rejected(CommandError.OnCooldown);
                economy.Items[support.Id] = economy.ItemCount(support.Id) - 1;
            }
            else
            {
                if (economy != null && economy.Supports.Count > 0 && !Contains(economy.Supports, support.Id))
                    return CommandResult.Rejected(CommandError.UnknownCard);
                if (economy != null && economy.CooldownLeft(support.Id, _world.Time) > 0f) return CommandResult.Rejected(CommandError.OnCooldown);
                if (!_world.Economy.TrySpend(command.Team, economy?.PriceOf(support.Id, support.CpCost) ?? support.CpCost))
                    return CommandResult.Rejected(CommandError.NotEnoughCp);
            }
            if (economy != null) economy.ReadyAt[support.Id] = _world.Time + support.Cooldown * (economy.Commander?.StrikeCooldown ?? 1f) * economy.StrikeScale;

            Launch(support, command.Team, command.Point, command.Point2);
            _world.CountStrike(command.Team);
            return CommandResult.Ok;
        }

        /// <summary>Starts a strike with no deck, CP or cooldown checks (battle events call bombers this way).</summary>
        internal void Launch(SupportDef support, int team, Vector2 point, Vector2 towards)
        {
            var direction = towards - point;
            direction = direction.LengthSquared() > 0.01f ? Vector2.Normalize(direction) : Vector2.UnitX;
            // Play-test 6: a dropped tower comes down on open ground near the mark, clear of what stands there.
            if (support.Kind == SupportKind.Tower && TowerOf(support, team) is { } dropped && _world.Catalog.Vehicles.TryGetValue(dropped, out var droppedDef))
                point = _world.ClearSpot(droppedDef, point, team);
            var line = support.LineRank > 0 && _world.StrikeRank(team, support.Id) >= support.LineRank ? support.LineScale : 1f;
            var strike = new Strike
            {
                Support = support, Team = team, Point = point, Direction = direction,
                Start = _world.Time + support.Delay, Scatter = team >= 0 && _world.Abilities.Jammed(point, team) ? 2.2f : 1f,
                Length = support.Length * line, Duration = support.Duration * line, Count = (int)MathF.Round(support.Count * line),
            };
            _strikes.Add(strike);
            var end = support.IsLine ? point + direction * strike.Length : point;
            _world.Emit(SimEvent.StrikeWarning(team, support, point, end, support.Delay));
            if (support.Kind == SupportKind.Tower && TowerOf(support, team) is { } tower)
                _world.Emit(SimEvent.DeploymentQueued(team, tower, point, -direction, support.Delay));
        }

        public void Step()
        {
            var now = _world.Time;
            for (var i = _smoke.Count - 1; i >= 0; i--)
                if (_smoke[i].Until <= now) _smoke.RemoveAt(i);
            for (var i = _scans.Count - 1; i >= 0; i--)
                if (_scans[i].Until <= now) _scans.RemoveAt(i);

            for (var i = _strikes.Count - 1; i >= 0; i--)
            {
                var strike = _strikes[i];
                if (Advance(strike, now)) _strikes.RemoveAt(i);
            }
        }

        /// <summary>Prompt 23 D.6: a side sees everything round a spot for a while (Nadia's report), as under a UAV scan.</summary>
        internal void AddScan(int team, Vector2 at, float radius, float seconds) => _scans.Add(new ScanZone(at, radius, _world.Time + seconds, team));

        /// <summary>A vehicle's own smoke dischargers (a skill), announced like a smoke strike.</summary>
        public void AddSmoke(int team, Vector2 at, float radius, float seconds)
        {
            _smoke.Add(new SmokeZone(at, radius, _world.Time + seconds));
            _world.Emit(SimEvent.SmokeDeployed(team, at, radius, seconds));
        }

        /// <summary>Whether a point lies inside a smoke cloud.</summary>
        public bool InSmoke(Vector2 at)
        {
            foreach (var zone in _smoke)
                if (Vector2.DistanceSquared(zone.Centre, at) < zone.Radius * zone.Radius) return true;
            return false;
        }

        /// <summary>Whether sight between two points is cut by smoke (either end inside a cloud, beyond arm's length).</summary>
        public bool Obscures(Vector2 from, Vector2 to)
        {
            if (_smoke.Count == 0) return false;
            if (Vector2.DistanceSquared(from, to) < 36f) return false;
            foreach (var zone in _smoke)
            {
                var r2 = zone.Radius * zone.Radius;
                if (Vector2.DistanceSquared(zone.Centre, from) < r2 || Vector2.DistanceSquared(zone.Centre, to) < r2) return true;
                // The line of sight passes through the cloud.
                var d = to - from;
                var t = Math.Clamp(Vector2.Dot(zone.Centre - from, d) / d.LengthSquared(), 0f, 1f);
                if (Vector2.DistanceSquared(zone.Centre, from + d * t) < r2 * 0.6f) return true;
            }
            return false;
        }

        /// <summary>Runs one strike forward; returns true when it has finished.</summary>
        private bool Advance(Strike s, double now)
        {
            var support = s.Support;
            switch (support.Kind)
            {
                case SupportKind.Barrage:
                {
                    var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
                    // Each round is aimed a moment before it lands and announced, so the shell can be
                    // seen coming down out of the sky onto the very spot it hits.
                    while (s.Planned.Count < support.Count && now >= s.Start + s.Planned.Count * interval - ShellFall)
                    {
                        var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                        var r = support.Radius * MathF.Sqrt((float)_world.Random.NextDouble());
                        var at = Scattered(s, s.Point + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r);
                        var lands = s.Start + s.Planned.Count * interval;
                        s.Planned.Add(at);
                        _world.Emit(SimEvent.ShellInbound(s.Team, support, at, FireFrom(s), (float)Math.Max(0.15, lands - now)));
                    }
                    if (now < s.Start) return false;
                    while (s.Done < support.Count && now >= s.Start + s.Done * interval)
                    {
                        Land(s, s.Planned[s.Done]);
                        s.Done++;
                    }
                    return s.Done >= support.Count;
                }

                case SupportKind.Airstrike:
                {
                    var end = s.Point + s.Direction * s.Length;
                    // The aircraft flies the bomb line at the speed the bombs walk along it, and is
                    // over each bomb as it lands (bombs keep its forward speed as they fall): it
                    // comes in from far enough back to be seen, but never later than the first bomb.
                    var speed = s.Length / MathF.Max(0.2f, s.Duration);
                    var lead = MathF.Min(Approach + s.Length * 0.2f, speed * MathF.Max(0.3f, support.Delay - 0.1f));
                    if (!s.Announced && now >= s.Start - lead / speed)
                    {
                        var from = s.Point - s.Direction * lead;
                        var to = end + s.Direction * Approach;
                        _world.Emit(SimEvent.AircraftPass(s.Team, support, from, to, Vector2.Distance(from, to) / speed));
                        s.Announced = true;
                    }
                    if (now < s.Start) return false;
                    var interval = s.Count > 1 ? s.Duration / (s.Count - 1) : 0f;
                    while (s.Done < s.Count && now >= s.Start + s.Done * interval)
                    {
                        var along = s.Count > 1 ? s.Done / (float)(s.Count - 1) : 0.5f;
                        var side = new Vector2(-s.Direction.Y, s.Direction.X) * (((float)_world.Random.NextDouble() - 0.5f) * support.Radius);
                        Blast(s, Vector2.Lerp(s.Point, end, along) + side);
                        s.Done++;
                    }
                    return s.Done >= s.Count;
                }

                case SupportKind.CruiseMissile:
                {
                    if (!s.Announced && now >= s.Start - RunIn)
                    {
                        var from = s.Point - s.Direction * (Approach + 40f);
                        _world.Emit(SimEvent.AircraftPass(s.Team, support, from, s.Point, RunIn));
                        s.Announced = true;
                    }
                    if (now < s.Start) return false;
                    // The tower-branch rework: an enemy PAC-3 over the mark shoots the cruise missile down (items are bombs, not missiles).
                    if (!support.Consumable && ShotDown(s)) return true;
                    Blast(s, s.Point);
                    return true;
                }

                case SupportKind.Smoke:
                    // The smoke shells come down first: one on the mark and four round it.
                    if (!s.Announced && now >= s.Start - ShellFall)
                    {
                        s.Announced = true;
                        for (var k = 0; k < 5; k++)
                        {
                            var angle = k * SimMath.Tau / 4f + 0.8f;
                            var at = k == 0 ? s.Point : s.Point + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (support.Radius * 0.5f);
                            _world.Emit(SimEvent.ShellInbound(s.Team, support, _world.ClampToMap(at), FireFrom(s),
                                (float)Math.Max(0.15, s.Start - now + k * 0.08)));
                        }
                    }
                    if (now < s.Start) return false;
                    _smoke.Add(new SmokeZone(s.Point, support.Radius, now + support.Duration));
                    _world.Emit(SimEvent.SmokeDeployed(s.Team, s.Point, support.Radius, support.Duration));
                    return true;

                case SupportKind.Repair:
                {
                    if (now < s.Start) return false;
                    var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
                    while (s.Done < support.Count && now >= s.Start + s.Done * interval)
                    {
                        Heal(s);
                        s.Done++;
                    }
                    return s.Done >= support.Count;
                }

                case SupportKind.Emp:
                    if (now < s.Start) return false;
                    _world.Emit(SimEvent.StrikeImpact(s.Team, support, s.Point));
                    foreach (var v in _world.VehicleList)
                    {
                        if (!v.IsAlive || v.Team == s.Team || v.Team < 0 || v.Flying || v.Def.Boss) continue;
                        if (Vector2.Distance(v.Position, s.Point) > support.Radius + v.Def.HullRadius) continue;
                        var knocked = _world.Gear.StunSeconds(v, support.Duration);
                        if (knocked <= 0f) continue;
                        v.StunnedUntil = Math.Max(v.StunnedUntil, now + knocked);
                        v.ClearPath();
                        v.Speed = 0f;
                    }
                    return true;

                case SupportKind.ShieldDome:
                    if (now < s.Start) return false;
                    _world.Emit(SimEvent.StrikeImpact(s.Team, support, s.Point));
                    foreach (var v in _world.VehicleList)
                    {
                        if (!v.IsAlive || v.Team != s.Team || Vector2.Distance(v.Position, s.Point) > support.Radius + v.Radius) continue;
                        v.ShieldUntil = Math.Max(v.ShieldUntil, now + support.Duration);
                        v.ShieldAmount = Math.Clamp(support.Damage, 0f, 0.9f);
                        v.RefreshEffects(now);
                    }
                    return true;

                case SupportKind.Reinforce:
                case SupportKind.Escort:
                {
                    if (now < s.Start) return false;
                    _world.Emit(SimEvent.StrikeImpact(s.Team, support, s.Point));
                    var units = support.Units;
                    for (var k = 0; k < units.Count; k++)
                    {
                        var angle = k * SimMath.Tau / Math.Max(1, units.Count);
                        var at = s.Point + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (units.Count > 1 ? 6f : 0f);
                        var unit = _world.SpawnVehicle(units[k], s.Team, _world.ClampToMap(at), SimMath.HeadingOf(s.Direction));
                        if (support.Kind == SupportKind.Escort)
                        {
                            unit.ExpiresAt = now + support.Duration;
                            // It works over the spot it was called to (it used to wander off after targets 60 m away).
                            unit.GuardPoint = _world.ClampToMap(s.Point);
                            unit.PostRadius = MathF.Max(support.Radius, 12f);
                        }
                    }
                    return true;
                }

                case SupportKind.Scan:
                    // The drone arrives over the point and circles it for the scan's length.
                    if (!s.Announced && now >= s.Start - RunIn)
                    {
                        var from = s.Point - s.Direction * (Approach + 30f);
                        _world.Emit(SimEvent.AircraftPass(s.Team, support, from, s.Point, RunIn));
                        s.Announced = true;
                    }
                    if (now < s.Start) return false;
                    _scans.Add(new ScanZone(s.Point, support.Radius, now + support.Duration, s.Team));
                    _world.Emit(SimEvent.StrikeImpact(s.Team, support, s.Point));
                    return true;

                case SupportKind.Minefield:
                {
                    // Rocket-scattered mines: each comes down on its spot, then lies armed.
                    while (s.Planned.Count < support.Count)
                    {
                        var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                        var r = support.Radius * MathF.Sqrt(0.1f + 0.9f * (float)_world.Random.NextDouble());
                        s.Planned.Add(_world.ClampToMap(s.Point + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r));
                    }
                    if (!s.Announced && now >= s.Start - ShellFall)
                    {
                        s.Announced = true;
                        for (var k = 0; k < s.Planned.Count; k++)
                            _world.Emit(SimEvent.ShellInbound(s.Team, support, s.Planned[k], FireFrom(s), (float)Math.Max(0.15, s.Start - now + k * 0.06)));
                    }
                    if (now < s.Start) return false;
                    var def = MinesOf(support);
                    foreach (var at in s.Planned)
                    {
                        _world.Emit(SimEvent.StrikeImpact(s.Team, support, at));
                        _world.Abilities.AddMine(s.Team, at, def, now + 1.0, now + support.Duration);
                    }
                    return true;
                }

                case SupportKind.Tower:
                {
                    if (now < s.Start) return false;
                    _world.Emit(SimEvent.StrikeImpact(s.Team, support, s.Point));
                    if (TowerOf(support, s.Team) is not { } id) return true;
                    var tower = _world.SpawnVehicle(id, s.Team, s.Point, SimMath.HeadingOf(-s.Direction));
                    tower.ExpiresAt = now + support.Duration;
                    return true;
                }

                case SupportKind.Sead:
                {
                    // The jet runs in, and its anti-radiation missile homes on the nearest enemy
                    // air-defence radar: picked as it fires, followed to where it is when it hits.
                    if (!s.Announced && now >= s.Start - RunIn)
                    {
                        var from = s.Point - s.Direction * (Approach + 40f);
                        _world.Emit(SimEvent.AircraftPass(s.Team, support, from, s.Point + s.Direction * Approach, RunIn * 1.6f));
                        s.Announced = true;
                    }
                    if (!s.Aimed && now >= s.Start - ShellFall)
                    {
                        s.Aimed = true;
                        s.Victim = NearestAirDefence(s.Point, s.Team, support.Radius);
                        var aim = _world.TryGetVehicle(s.Victim, out var marked) ? marked.Position : s.Point;
                        _world.Emit(SimEvent.ShellInbound(s.Team, support, aim, FireFrom(s), (float)Math.Max(0.15, s.Start - now)));
                    }
                    if (now < s.Start) return false;
                    if (_world.TryGetVehicle(s.Victim, out var radar) && radar.IsAlive)
                    {
                        _world.Emit(SimEvent.StrikeImpact(s.Team, support, radar.Position));
                        var damage = support.Damage * _world.StrikeDamage(s.Team, support.Id);
                        _world.Damage.Apply(radar, damage, support.DamageType, new Combat.HitInfo(null, s.Team, null, radar.Position, Combat.HitKind.Strike, true)
                            .WithPen(support.Penetration, top: true, support.Thermobaric));
                        var knocked = radar.IsAlive ? _world.Gear.StunSeconds(radar, support.Duration) : 0f;
                        if (knocked > 0f)
                        {
                            radar.StunnedUntil = Math.Max(radar.StunnedUntil, now + knocked);
                            radar.ClearPath();
                            radar.Speed = 0f;
                        }
                    }
                    else Land(s, s.Point);
                    return true;
                }

                default:
                    return true;
            }
        }

        /// <summary>The tower a Tower drop brings for this side: the better one from its card rank.</summary>
        private string? TowerOf(SupportDef support, int team)
        {
            var units = support.Units;
            if (units.Count == 0) return null;
            var better = support.UnitRank > 0 && units.Count > 1 && _world.StrikeRank(team, support.Id) >= support.UnitRank;
            var id = better ? units[1] : units[0];
            return _world.Catalog.Vehicles.ContainsKey(id) ? id : units[0];
        }

        private MineLayerDef MinesOf(SupportDef support)
        {
            if (_mineDefs.TryGetValue(support.Id, out var def)) return def;
            def = new MineLayerDef(1f, Math.Max(1, support.Count), new ExplosionDef(support.Damage, MathF.Max(1f, support.BlastRadius), 0f, support.Tier), 2.2f);
            _mineDefs[support.Id] = def;
            return def;
        }

        /// <summary>The enemy air defence (an anti-air vehicle, or a fixed defence with an anti-air weapon) nearest a point within reach.</summary>
        private EntityId NearestAirDefence(Vector2 at, int team, float reach)
        {
            var best = EntityId.None;
            var bestD = reach * reach;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team == team || v.Team < 0 || v.Flying || v.Def.Boss) continue;
                if (!IsAirDefence(v.Def)) continue;
                var d = Vector2.DistanceSquared(v.Position, at);
                if (d > bestD) continue;
                bestD = d;
                best = v.Id;
            }
            return best;
        }

        /// <summary>A vehicle or tower whose job is shooting aircraft down (not a tank whose machine gun can).</summary>
        internal static bool IsAirDefence(VehicleDef def)
        {
            if (def.Class == UnitClass.AntiAir) return true;
            if (!def.Static) return false;
            foreach (var m in def.Mounts)
                if (m.Weapon.Targets == TargetLayers.Air || (m.Weapon.CanTarget(true) && m.Weapon.Projectile == ProjectileKind.Missile)) return true;
            return false;
        }

        private void Blast(Strike s, Vector2 at) => Land(s, Scattered(s, at));

        /// <summary>A cruise-missile strike met over its mark by an enemy heavy-missile interceptor (the PAC-3) with one left.</summary>
        private bool ShotDown(Strike s)
        {
            foreach (var v in _world.VehicleList)
            {
                var aps = v.Aps;
                if (aps == null || !aps.Heavy || !v.IsAlive || v.Team == s.Team || v.Team < 0 || v.ApsCharges <= 0 || v.Stunned || v.ApsOff) continue;
                if (Vector2.DistanceSquared(v.Position, s.Point) > aps.Radius * aps.Radius) continue;
                v.ApsCharges--;
                if (aps.Reload > 0f) v.ApsReload = 0f;
                _world.Emit(SimEvent.Intercept(v, v.Def.Weapon, s.Point, v.ApsLeft = !v.ApsLeft));
                return true;
            }
            return false;
        }

        /// <summary>Fire support called into an enemy jammer's bubble lands wide.</summary>
        private Vector2 Scattered(Strike s, Vector2 at)
        {
            var support = s.Support;
            if (s.Scatter > 1f)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                var off = (s.Scatter - 1f) * MathF.Max(6f, support.Radius) * MathF.Sqrt((float)_world.Random.NextDouble());
                at += new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * off;
            }
            return _world.ClampToMap(at);
        }

        private void Land(Strike s, Vector2 at)
        {
            var support = s.Support;
            _world.Emit(SimEvent.StrikeImpact(s.Team, support, at));
            _world.Damage.Splash(at, support.BlastRadius, support.Damage * _world.StrikeDamage(s.Team, support.Id), support.DamageType, s.Team, EntityId.None,
                info: new Combat.HitInfo(null, s.Team, null, at, Combat.HitKind.Strike, true).WithPen(support.Penetration, top: true, support.Thermobaric));
        }

        /// <summary>The side the rounds come from: the calling side's camp, else back along the strike.</summary>
        private Vector2 FireFrom(Strike s)
        {
            if (_world.TryGetRally(s.Team, out var home) && Vector2.DistanceSquared(home, s.Point) > 1f) return Vector2.Normalize(home - s.Point);
            return s.Direction.LengthSquared() > 0.01f ? -Vector2.Normalize(s.Direction) : Vector2.UnitY;
        }

        private void Heal(Strike s)
        {
            var support = s.Support;
            var fraction = support.Damage / support.Count;
            foreach (var v in _world.VehicleList)
            {
                // Bosses cannot be patched up in the field: a 40% heal would undo minutes of fighting.
                if (!v.IsAlive || v.Team != s.Team || v.Def.Boss || Vector2.Distance(v.Position, s.Point) > support.Radius + v.Radius) continue;
                var amount = _world.Gear.Heal(v, v.MaxHp * fraction * Abilities.GearSystem.RepairFactor(v, _world.Time));
                if (amount <= 0f) continue;
                _world.Emit(SimEvent.RepairedBy(v, amount));
            }
        }

        private static bool Contains(IReadOnlyList<string> list, string id)
        {
            foreach (var item in list)
                if (item == id) return true;
            return false;
        }
    }
}
