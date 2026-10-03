#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Fix prompt L4 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): munitions in flight, by the rules A-G of the prompt, on the
    /// Sim tick and from its seeded generator only.
    /// <list type="bullet">
    /// <item>A guided round (missile, drone, guided rocket, guided bomb or shell) lands on its target wherever it drove: it
    /// cannot be outrun. It misses only by an APS, a jammer (at launch), its one launch roll (<see cref="Projectile.Failed"/>),
    /// a sight-guided missile's shooter dying or losing sight on the way (<see cref="Divert.Sight"/>), its target getting out
    /// of its reach (<see cref="Divert.Reach"/>), and for an IR missile a flare (<see cref="Divert.Flare"/>).</item>
    /// <item>Flares: one roll per IR missile, on the first tick its aircraft's flares burn while it flies; a decoyed missile
    /// flies on to the flare and bursts beside it (an air burst with its effect and sound). Radar-guided families, guns and
    /// lasers are never decoyed.</item>
    /// <item>Unguided rockets, shells, mortars and bombs (not a free-falling stick, which falls where the drop puts it)
    /// lead a moving ground target: they aim where it will be after the round's flight (at most
    /// <see cref="MunitionRules.LeadCap"/> s of its motion), then scatter as before. A target that turns or brakes after
    /// the shot can still get partly clear, as the prompt wants.</item>
    /// <item>Every round lands on its launch-time travel at the latest (its own flight limit, rule G); a guided one is
    /// diverted the tick its reason happens and the view is told (<see cref="SimEventKind.RoundDiverted"/>).</item>
    /// </list>
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>Whether a round homes on its target at impact (rule A): guided, or a steered rocket, bomb or shell.</summary>
        internal static bool Homes(WeaponDef w) => w.Guided || w.GuidedRocket || w.GuidedBomb || w.GuidedShell;

        /// <summary>Rule D: the unguided rounds that lead a moving target (a free-falling stick falls where its drop puts it).</summary>
        internal static bool Leads(WeaponDef w, bool freeFall) =>
            !freeFall && !Homes(w) && !w.Beam && w.DamageType != DamageType.Energy &&
            (w.Projectile == ProjectileKind.Rocket || w.Projectile == ProjectileKind.Bomb || (w.Projectile == ProjectileKind.Shell && w.Indirect));

        /// <summary>
        /// Rule D: where a moving ground vehicle will be when a round from <paramref name="shooter"/> gets there (two passes of
        /// its flight against its speed along its heading, the lead capped at <paramref name="cap"/> s). Its position when it
        /// is not moving, flies or is a fixed defence.
        /// </summary>
        internal static Vector2 LeadPoint(Vehicle shooter, Vehicle target, WeaponDef weapon, float cap)
        {
            if (!target.IsMoving || target.Flying || target.Def.Static || cap <= 0f) return target.Position;
            var velocity = SimMath.Forward(target.Heading) * target.Speed;
            var at = target.Position;
            for (var pass = 0; pass < 2; pass++)
            {
                var distance = Vector2.Distance(shooter.Position, at);
                var flight = weapon.Projectile == ProjectileKind.Bomb && shooter.Flying && !BayStick(weapon)
                    ? MathF.Max(0.8f, distance / MathF.Max(8f, shooter.Speed))
                    : distance / MathF.Max(1f, weapon.ProjectileSpeed);
                at = target.Position + velocity * MathF.Min(cap, flight);
            }
            return at;
        }

        /// <summary>Rule C: an IR missile (not a radar-guided family) that flares can pull off; data flareEligible overrides.</summary>
        internal static bool FlareTakes(WeaponDef w, MunitionRules rules)
        {
            if (!w.Guided || w.FlareEligible == false) return false;
            if (w.FlareEligible == true) return true;
            return w.Projectile == ProjectileKind.Missile && !rules.IsRadarGuided(w);
        }

        /// <summary>
        /// Every tick, before the rounds land: each guided round still on its target checks the rules that take it off in
        /// flight (flares, a sight-guided missile's lost sight, its reach). Rounds from equipment (no launch time) meet the
        /// flares only.
        /// </summary>
        private void GuideRounds()
        {
            var rules = _world.Catalog.Munitions;
            var now = _world.Time;
            for (var i = 0; i < _projectiles.Count; i++)
            {
                var p = _projectiles[i];
                if (p.Diverted != Entities.Divert.None || p.Jammed || p.Failed || !Homes(p.Weapon)) continue;
                if (!_world.TryGetTarget(p.Target, out var target) || !target.IsAlive) continue;
                var weapon = p.Weapon;
                // C: one roll per IR missile on the first tick its aircraft's flares burn while it flies.
                if (!p.FlareRolled && p.TargetFlying && target is Vehicle flyer && flyer.FlaresUntil > now && FlareTakes(weapon, rules))
                {
                    p.FlareRolled = true;
                    if (_world.Random.NextDouble() < rules.FlareDecoyChance * (1f - weapon.FlareResist))
                    {
                        DivertRound(p, Entities.Divert.Flare, FlarePoint(flyer, rules));
                        continue;
                    }
                }
                // Rounds from equipment (no launch time) have no shooter's sight or reach of their own.
                if (double.IsPositiveInfinity(p.LaunchedAt)) continue;
                // A: a sight-guided missile flies on its shooter's sight: dead, in smoke or behind a wall, it is lost.
                if (weapon.Projectile == ProjectileKind.Missile && rules.IsSightGuided(weapon) && LostSight(p, target))
                {
                    DivertRound(p, Entities.Divert.Sight, target.Position + p.Miss);
                    continue;
                }
                // A, G: out of its reach (it would run out of fuel chasing): it self-destructs at the end of it.
                var reach = weapon.Range * MathF.Max(1f, p.Shooter?.RangeFactor ?? 1f) * rules.ReachScale;
                var away = target.Position - p.Origin;
                if (reach > 0f && away.LengthSquared() > reach * reach)
                    DivertRound(p, Entities.Divert.Reach, p.Origin + Vector2.Normalize(away) * reach);
            }
        }

        private void DivertRound(Projectile p, Entities.Divert why, Vector2 at)
        {
            p.Diverted = why;
            p.DivertAt = _world.ClampToMap(at);
            _world.Emit(SimEvent.Diverted(p, p.DivertAt, (int)why));
        }

        /// <summary>
        /// Where a decoyed missile meets its flare: behind the aircraft and to one side (seeded), <see cref="MunitionRules.FlareOffset"/>
        /// out, so its burst is outside its own fuze and clear of the aircraft.
        /// </summary>
        private Vector2 FlarePoint(Vehicle flyer, MunitionRules rules)
        {
            var back = -SimMath.Forward(flyer.Heading);
            var side = new Vector2(back.Y, -back.X) * (_world.Random.NextDouble() < 0.5 ? -1f : 1f);
            var reach = rules.FlareOffset + flyer.Radius;
            return flyer.Position + Vector2.Normalize(back * 0.8f + side * 0.6f) * reach;
        }

        /// <summary>
        /// Rule A: the shooter of a sight-guided missile has lost it: it is dead, it or its target is in smoke, or (both on the
        /// ground) a wall now stands between them.
        /// </summary>
        private bool LostSight(Projectile p, IDamageable target)
        {
            var shooter = p.Shooter;
            if (shooter == null || !shooter.IsAlive) return true;
            if (_world.Strikes.InSmoke(target.Position) || _world.Strikes.InSmoke(shooter.Position)) return true;
            if (shooter.Flying || p.TargetFlying || target is not Vehicle) return false;
            return _world.Cover.TryFirstHit(shooter.Position, target.Position, shooter.Radius, target.Radius, null, out _);
        }
    }
}
