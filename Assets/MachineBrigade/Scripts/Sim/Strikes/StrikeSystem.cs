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
        }

        private readonly SimWorld _world;
        private readonly List<Strike> _strikes = new();
        private readonly List<SmokeZone> _smoke = new();

        public StrikeSystem(SimWorld world) => _world = world;

        public IReadOnlyList<SmokeZone> Smoke => _smoke;

        public CommandResult Call(Command command)
        {
            if (command.DefId == null || !_world.Catalog.TryGetSupport(command.DefId, out var support))
                return CommandResult.Rejected(CommandError.UnknownCard);
            if (!SimMath.IsFinite(command.Point)) return CommandResult.Rejected(CommandError.InvalidPoint);
            if (!_world.Map.Contains(command.Point)) return CommandResult.Rejected(CommandError.OutOfBounds);

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
                if (!_world.Economy.TrySpend(command.Team, support.CpCost)) return CommandResult.Rejected(CommandError.NotEnoughCp);
            }
            if (economy != null) economy.ReadyAt[support.Id] = _world.Time + support.Cooldown;

            Launch(support, command.Team, command.Point, command.Point2);
            return CommandResult.Ok;
        }

        /// <summary>Starts a strike with no deck, CP or cooldown checks (battle events call bombers this way).</summary>
        internal void Launch(SupportDef support, int team, Vector2 point, Vector2 towards)
        {
            var direction = towards - point;
            direction = direction.LengthSquared() > 0.01f ? Vector2.Normalize(direction) : Vector2.UnitX;
            var strike = new Strike
            {
                Support = support, Team = team, Point = point, Direction = direction,
                Start = _world.Time + support.Delay, Scatter = team >= 0 && _world.Abilities.Jammed(point, team) ? 2.2f : 1f,
            };
            _strikes.Add(strike);
            var end = support.IsLine ? point + direction * support.Length : point;
            _world.Emit(SimEvent.StrikeWarning(team, support, point, end, support.Delay));
        }

        public void Step()
        {
            var now = _world.Time;
            for (var i = _smoke.Count - 1; i >= 0; i--)
                if (_smoke[i].Until <= now) _smoke.RemoveAt(i);

            for (var i = _strikes.Count - 1; i >= 0; i--)
            {
                var strike = _strikes[i];
                if (Advance(strike, now)) _strikes.RemoveAt(i);
            }
        }

        /// <summary>A vehicle's own smoke dischargers (a skill), announced like a smoke strike.</summary>
        public void AddSmoke(int team, Vector2 at, float radius, float seconds)
        {
            _smoke.Add(new SmokeZone(at, radius, _world.Time + seconds));
            _world.Emit(SimEvent.SmokeDeployed(team, at, radius, seconds));
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
                    if (now < s.Start) return false;
                    var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
                    while (s.Done < support.Count && now >= s.Start + s.Done * interval)
                    {
                        var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                        var r = support.Radius * MathF.Sqrt((float)_world.Random.NextDouble());
                        Blast(s, s.Point + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r);
                        s.Done++;
                    }
                    return s.Done >= support.Count;
                }

                case SupportKind.Airstrike:
                {
                    var end = s.Point + s.Direction * support.Length;
                    if (!s.Announced && now >= s.Start - RunIn)
                    {
                        // The jet crosses the whole map along the bomb line.
                        var from = s.Point - s.Direction * (Approach + support.Length * 0.2f);
                        var to = end + s.Direction * Approach;
                        var speed = support.Length / MathF.Max(0.2f, support.Duration);
                        _world.Emit(SimEvent.AircraftPass(s.Team, support, from, to, Vector2.Distance(from, to) / speed));
                        s.Announced = true;
                    }
                    if (now < s.Start) return false;
                    var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
                    while (s.Done < support.Count && now >= s.Start + s.Done * interval)
                    {
                        var along = support.Count > 1 ? s.Done / (float)(support.Count - 1) : 0.5f;
                        var side = new Vector2(-s.Direction.Y, s.Direction.X) * (((float)_world.Random.NextDouble() - 0.5f) * support.Radius);
                        Blast(s, Vector2.Lerp(s.Point, end, along) + side);
                        s.Done++;
                    }
                    return s.Done >= support.Count;
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
                    Blast(s, s.Point);
                    return true;
                }

                case SupportKind.Smoke:
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
                        v.StunnedUntil = Math.Max(v.StunnedUntil, now + support.Duration);
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
                        if (support.Kind == SupportKind.Escort) unit.ExpiresAt = now + support.Duration;
                    }
                    return true;
                }

                default:
                    return true;
            }
        }

        private void Blast(Strike s, Vector2 at)
        {
            var support = s.Support;
            if (s.Scatter > 1f)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                var off = (s.Scatter - 1f) * MathF.Max(6f, support.Radius) * MathF.Sqrt((float)_world.Random.NextDouble());
                at += new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * off;
            }
            at = _world.ClampToMap(at);
            _world.Emit(SimEvent.StrikeImpact(s.Team, support, at));
            _world.Damage.Splash(at, support.BlastRadius, support.Damage, support.DamageType, s.Team, EntityId.None);
        }

        private void Heal(Strike s)
        {
            var support = s.Support;
            var fraction = support.Damage / support.Count;
            foreach (var v in _world.VehicleList)
            {
                // Bosses cannot be patched up in the field: a 40% heal would undo minutes of fighting.
                if (!v.IsAlive || v.Team != s.Team || v.Def.Boss || Vector2.Distance(v.Position, s.Point) > support.Radius + v.Radius) continue;
                var amount = MathF.Min(v.MaxHp - v.Hp, v.MaxHp * fraction);
                if (amount <= 0f) continue;
                v.Hp += amount;
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
