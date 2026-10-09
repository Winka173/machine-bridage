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
    /// Prompt 25 F2 batch A (DECISIONS 25F2-A): the new units' and structures' part in combat: what they go for (a heavy
    /// flak gun's groups and big aircraft, an interceptor's bombers, the anti-drone weapons' prey, a towed gun's arc,
    /// linked towers ganging up, decoys drawing fire until found out), one drone at a time, salvos that land together,
    /// and the drone killers (the microwave's pulse, the interceptor drones taking drone rounds out of the air).
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>A heavy flak gun weighs a flier this much more for each other enemy flier its burst would reach.</summary>
        internal const float GroupWeight = 0.5f;

        /// <summary>Worth (CP) from which a flier counts as big game (a bomber, a gunship, a drone mothership).</summary>
        internal const float BigAircraft = 12f;

        /// <summary>An unexposed decoy's pull on fire, on top of passing for the tower it mimics.</summary>
        internal const float DecoyBait = 1.5f;

        /// <summary>The prompt 25 F2 batch A target weights for <see cref="Score"/> (0: not a target for this weapon).</summary>
        private float P25Worth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            var f = 1f;
            // A towed gun's traverse: nothing outside its arc.
            if (v.Def.TurretArc > 0f && MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(other.Position - v.Position) - v.Heading)) > v.Def.TurretArc) return 0f;
            // What an anti-drone weapon may take among fliers.
            if (weapon.Prey == Prey.Light)
            {
                if (other.Flying || other.Def.Static || other.Armour.Front > WeaponDef.HeArmourMax) return 0f;
            }
            else if (weapon.Prey != Prey.Any)
            {
                if (!other.Flying) return 0f;
                var ok = other.Def.Drone || (weapon.Prey == Prey.Rotors && !other.Def.FixedWing);
                if (!ok) return 0f;
            }
            if (other.Flying && weapon.GroupPriority)
            {
                var reach = weapon.SplashRadius + global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthSplashRadiusAdd;
                var others = 0;
                foreach (var e in _world.VehicleList)
                    if (e != other && e.IsAlive && e.Flying && e.Team == other.Team && Vector2.DistanceSquared(e.Position, other.Position) <= reach * reach) others++;
                f *= 1f + GroupWeight * others;
                if (Worth(other) >= BigAircraft) f *= 1.5f;
            }
            if (other.Flying && weapon.BigGame) f *= Worth(other) >= BigAircraft || other.Def.Orbit ? 3f : 0.6f;
            // A decoy passes for the tower it mimics (its worth, a gun that shoots back) until this side finds it out.
            if (other.Def.Decoy is { } decoy)
            {
                if (other.DecoyExposedTo(v.Team)) return 0f;
                if (_world.Catalog.Vehicles.TryGetValue(decoy.Mimic, out var mimic))
                    f *= MathF.Sqrt(Math.Clamp(mimic.MaxHp / global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthMaxHpDivisor, global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthMaxHpMin, global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthMaxHpMax) / Math.Clamp(Worth(other), global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthWorthMin, global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthWorthMax)) * (ThreatWeight / global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P25WorthThreatWeightDivisor) * DecoyBait;
            }
            // Linked towers gang up on what another linked tower is on.
            if (v.FireLinked && other.Id != v.Target && _world.Works.LinkedOn(v.Team, other.Id)) f *= _world.Works.LinkFocus(v);
            return f;
        }

        /// <summary>A towed gun's barrel stays within its arc of the front (see <see cref="VehicleDef.TurretArc"/>).</summary>
        private static bool KeepToTurretArc(Vehicle v)
        {
            var arc = v.Def.TurretArc;
            if (arc <= 0f) return false;
            var off = SimMath.WrapAngle(v.TurretHeading - v.Heading);
            if (MathF.Abs(off) > arc) v.TurretHeading = v.Heading + MathF.Sign(off) * arc;
            return true;
        }

        /// <summary>A round of this mount is still in the air (a fibre-optic drone's operator flies one at a time).</summary>
        private bool InFlightFrom(Vehicle v, int index)
        {
            var weapon = v.Arms[index];
            foreach (var p in _projectiles)
                if (p.Owner == v.Id && p.Weapon.Id == weapon.Id && p.TimeLeft > 0f) return true;
            return false;
        }

        /// <summary>
        /// A multiple-rounds-simultaneous-impact salvo (the turreted mortar): the first round's flight sets when the salvo
        /// lands; every later round is laid on a flatter path to arrive then too.
        /// </summary>
        private float MrsiTravel(Vehicle shooter, int index, bool first, float travel)
        {
            if (!shooter.Arms[index].Mrsi) return travel;
            var now = _world.Time;
            if (first || shooter.MrsiLands <= now)
            {
                shooter.MrsiLands = now + travel;
                return travel;
            }
            return MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.MrsiTravelMrsiLandsFloor, (float)(shooter.MrsiLands - now));
        }

        // ================================================================== the drone killers

        /// <summary>The microwave's pulses and the interceptor drones' hunt for drone rounds, before the rounds land.</summary>
        private void StepDroneKillers()
        {
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team < 0 || v.Stunned || v.HoldFire) continue;
                if (v.Def.Microwave is { } mw && now >= v.WorksNextAt) Pulse(v, mw, now);
                if (v.Def.DroneHunt is { } hunt && v.Weapons.Length > 0 && v.Weapons[0].Cooldown <= 0f && v.Weapons[0].Ammo != 0) Hunt(v, hunt);
            }
        }

        /// <summary>
        /// The microwave's pulse: aimed at the nearest enemy drone in its reach (a drone aircraft or a drone round in flight),
        /// it downs every enemy drone in its cone there at once, and does nothing to anything else.
        /// </summary>
        private void Pulse(Vehicle v, MicrowaveDef mw, double now)
        {
            var reach2 = mw.Range * mw.Range;
            Vector2? aim = null;
            var best = float.MaxValue;
            foreach (var e in _world.VehicleList)
            {
                if (!IsEnemyDrone(v, e)) continue;
                var d2 = Vector2.DistanceSquared(e.Position, v.Position);
                if (d2 <= reach2 && d2 < best) (best, aim) = (d2, e.Position);
            }
            foreach (var p in _projectiles)
            {
                if (!IsEnemyDroneRound(v, p)) continue;
                var at = RoundAt(p);
                var d2 = Vector2.DistanceSquared(at, v.Position);
                if (d2 <= reach2 && d2 < best) (best, aim) = (d2, at);
            }
            if (aim is not { } point) return;
            var heading = SimMath.HeadingOf(point - v.Position);
            v.TurretHeading = heading;
            v.WorksNextAt = now + mw.Cooldown;
            bool InCone(Vector2 at) => Vector2.DistanceSquared(at, v.Position) <= reach2 &&
                                       (Vector2.DistanceSquared(at, v.Position) < 1f || MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(at - v.Position) - heading)) <= mw.Arc);
            var weapon = v.Def.Weapon;
            foreach (var e in _world.VehicleList)
            {
                if (!IsEnemyDrone(v, e) || !InCone(e.Position)) continue;
                _world.Damage.Apply(e, e.Hp + 1f, DamageType.Energy, new HitInfo(v, v.Team, null, v.Position, HitKind.Redirect, false));
                _world.Emit(SimEvent.Intercept(v, weapon, e.Position, false));
            }
            for (var i = _projectiles.Count - 1; i >= 0; i--)
            {
                var p = _projectiles[i];
                if (!IsEnemyDroneRound(v, p)) continue;
                var at = RoundAt(p);
                if (!InCone(at)) continue;
                RemoveRound(p);
                _world.Emit(SimEvent.Intercept(v, p.Weapon, at, false));
            }
            _world.Emit(SimEvent.Proc(v, "microwave"));
        }

        /// <summary>
        /// An interceptor drone goes after an enemy drone round flying at anything of ours within its hunt's reach (the one
        /// landing soonest that it can still catch), in place of its next launch at a drone aircraft or a helicopter.
        /// </summary>
        private void Hunt(Vehicle v, DroneHuntDef hunt)
        {
            Projectile? best = null;
            var reach2 = hunt.Reach * hunt.Reach;
            foreach (var p in _projectiles)
            {
                if (!IsEnemyDroneRound(v, p) || p.TimeLeft < HuntCatch) continue;
                var mark = _world.TryGetTarget(p.Target, out var target) && target.IsAlive ? target.Position : p.AimPoint;
                if (Vector2.DistanceSquared(mark, v.Position) > reach2) continue;
                if (best == null || p.TimeLeft < best.TimeLeft) best = p;
            }
            if (best == null) return;
            var at = RoundAt(best);
            var weapon = v.Arms[0];
            var state = v.Weapons[0];
            state.Cooldown = weapon.Cooldown;
            if (state.Ammo > 0) state.Ammo--;
            state.FiredAt = _world.Time;
            v.LastFiredAt = _world.Time;
            v.TurretHeading = SimMath.HeadingOf(at - v.Position);
            RemoveRound(best);
            var flight = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.HuntDistanceFloor, Vector2.Distance(v.Position, at) / MathF.Max(1f, weapon.ProjectileSpeed));
            _world.Emit(SimEvent.FiredWith(v, weapon, v.Position, at, flight, EntityId.None));
            _world.Emit(SimEvent.Intercept(v, best.Weapon, at, false));
        }

        /// <summary>Seconds a drone round must still have to fly for an interceptor drone to catch it.</summary>
        private const float HuntCatch = 0.6f;

        private static bool IsEnemyDrone(Vehicle v, Vehicle e) =>
            e.IsAlive && e.Team != v.Team && e.Team >= 0 && e.Flying && e.Def.Drone && !e.Def.Boss && !e.Invulnerable && e.IsVisibleTo(v.Team);

        private static bool IsEnemyDroneRound(Vehicle v, Projectile p) =>
            p.OwnerTeam != v.Team && p.Weapon.Projectile == ProjectileKind.Drone && !p.Tandem && p.TimeLeft > 0f;
    }
}
