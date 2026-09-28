#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Prompt 8's equipment: the proc coefficient every hit line is scaled by, the fixed-effect
    /// modules sized to the vehicle's price, the new base types (flanking and airburst rounds, the
    /// spare magazine, the radar-absorbent coating, the laser warner, the reverse gearbox, the
    /// underbelly armour), the new unique lines (Vengeance, Suppressive Fire, Rearguard) and brands
    /// (Phoenix Recovery, Wolfpack Tactics, Bulwark Engineering), healing with its overheal, and the
    /// rule that no two last stands chain on one blow.
    /// </summary>
    internal sealed partial class GearSystem
    {
        /// <summary>Opening Salvo: how long after switching to a new target its rounds get the bonus.</summary>
        internal const double OpeningWindow = 1.5;

        /// <summary>Cluster Warhead: how many rounds of a salvo carry bomblets.</summary>
        internal const int ClusterRounds = 2;

        /// <summary>After a last stand (Unbreakable, Aegis Dome, an overheal shield taking a killing blow) no other may save it for this long.</summary>
        internal const float LastStandGap = 6f;

        /// <summary>Kill Reload: seconds taken off the main gun's reload.</summary>
        internal const float KillReadySeconds = 2f;

        /// <summary>Volatile Fuel Tanks: the most its blast may do, whatever the hull.</summary>
        internal const float FuelBlastCap = 1500f;

        /// <summary>The seconds between the reference weapon's hits (the proc coefficient is 1 at this interval).</summary>
        internal const float ProcReference = 1.5f;

        /// <summary>
        /// Fixed-effect modules and lines (drone escort, uplink barrage, mine dispenser, EMP payload,
        /// fuel tanks) are sized to the vehicle's price: CP / 7 between 0.4 and 1.3, so a swarm of
        /// cheap vehicles wearing them is not the best use of them.
        /// </summary>
        internal static float ModuleScale(Vehicle v) => Math.Clamp(MathF.Max(v.Def.CpCost, v.Def.ArmyCost) / 7f, 0.4f, 1.3f);

        /// <summary>Seconds between a weapon's rounds (a salvo's rounds counted one by one; a machine gun's pauses between runs counted in).</summary>
        internal static float HitInterval(WeaponDef w)
        {
            var cycle = w.Cooldown + (w.Burst - 1) * w.BurstInterval + w.Charge;
            var interval = cycle / MathF.Max(1, w.Burst);
            // A machine gun fires in runs with pauses (CombatSystem's RunDamage of 1.7).
            if (w.Projectile == ProjectileKind.Bullet && w.Cooldown < 0.35f && w.Burst <= 1) interval *= 1.7f;
            return MathF.Max(0.02f, interval);
        }

        /// <summary>
        /// The proc coefficient (prompt 8 I.3): a hit line's strength per hit, by weapon. Seconds between
        /// the weapon's hits over 1.5 s, between 0.15 (a flak gun, a minigun) and 2.5 (a tank gun, a
        /// railgun, a howitzer): a fast gun earns a stack in several hits, a slow one several stacks in one.
        /// </summary>
        internal static float ProcCoefficient(WeaponDef w) => Math.Clamp(HitInterval(w) / ProcReference, 0.15f, 2.5f);

        /// <summary>Twin Feed on a gun of one or two rounds: the extra damage of every round (the trait's second number; its salvo share times 1.6 in older data).</summary>
        private static float TwinSingle(GearTrait t) => t.B > 0f ? t.B : t.A * 1.6f;

        /// <summary>The share of fire rate suppressive fire takes off now.</summary>
        private static float SuppressedShare(Vehicle v, double now)
        {
            ref var s = ref v.Statuses[(int)StatusKind.Suppressed];
            return s.Until > now ? Math.Clamp(s.Value, 0f, 0.6f) : 0f;
        }

        // ================================================================== every step

        private readonly List<(Vector2 at, int team, float seconds)> _posts = new();

        /// <summary>Bulwark Engineering's temporary machine-gun posts, raised after the step (the vehicle list is read while towers fall).</summary>
        private void RaisePosts()
        {
            if (_posts.Count == 0) return;
            foreach (var (at, team, seconds) in _posts)
            {
                if (!_world.Catalog.Vehicles.ContainsKey(BulwarkPostId)) continue;
                var post = _world.SpawnVehicle(BulwarkPostId, team, at, 0f);
                post.ExpiresAt = _world.Time + seconds;
            }
            _posts.Clear();
        }

        /// <summary>The temporary machine-gun post a Bulwark tower leaves (balance.json).</summary>
        internal const string BulwarkPostId = "bulwark_post";

        private void StepLines(Vehicle v, GearState g, double now, bool aura, ref float speed, ref float fire)
        {
            var cd = CooldownFactor(g);
            // Spare Magazine: an empty launcher gets part of its magazine back at once, once a life.
            var spare = g.Stat(StatId.SpareMagazine);
            if (spare > 0f && !g.SpareUsed && v.Arms[0].Ammo > 0 && v.Weapons[0].Ammo == 0)
            {
                g.SpareUsed = true;
                v.Weapons[0].Ammo = Math.Max(1, (int)MathF.Round(v.Arms[0].Ammo * Math.Clamp(spare, 0f, 1f)));
                v.Weapons[0].ReloadLeft = 0f;
                Proc(v, "spare_magazine");
            }
            // Laser Warning: an anti-tank missile locks on; a smoke screen goes up and the missiles in the air lose the beam.
            var warn = g.Stat(StatId.LaserWarning);
            if (warn > 0f && !v.Flying && now >= g.WarningAt && _world.AtgmIncoming(v.Id))
            {
                g.WarningAt = now + LaserWarningCooldown * cd;
                _world.Strikes.AddSmoke(v.Team, v.Position, warn, 8f);
                ref var jam = ref v.Statuses[(int)StatusKind.Jam];
                jam.Until = Math.Max(jam.Until, now + 1.5);
                Proc(v, "laser_warning");
            }
            if (aura)
            {
                if (g.Has(TraitId.Rearguard)) g.Withdrawing = MovingAway(v);
                if (g.Has(TraitId.SetPackHunt))
                {
                    var t = g.Trait(TraitId.SetPackHunt);
                    g.Pack = Pack(v, t.B > 0f ? t.B : 15f, t.C > 0f ? (int)t.C : 3);
                }
                if (g.Has(TraitId.SetPackFocus))
                {
                    var was = g.PackFocus;
                    g.PackFocus = FocusedBy(v) >= 3;
                    if (g.PackFocus && !was) Proc(v, TraitId.SetPackFocus);
                }
                if (g.Stat(StatId.ReverseSpeed) > 0f && now >= g.BackOffAt) BackOff(v, g, now);
            }
            if (g.PackFocus) fire *= 1f + g.Trait(TraitId.SetPackFocus).A;
        }

        /// <summary>Laser Warning's smoke: once every this many seconds.</summary>
        internal const float LaserWarningCooldown = 20f;

        /// <summary>Rearguard: driving away from the nearest enemy it knows of (reversing counts).</summary>
        private bool MovingAway(Vehicle v)
        {
            if (MathF.Abs(v.Speed) < 0.5f) return false;
            var threat = _world.FindNearestEnemy(v, 70f, requireVisible: true);
            if (threat == null) return false;
            var travel = SimMath.Forward(v.Heading) * MathF.Sign(v.Speed);
            var to = threat.Position - v.Position;
            if (to.LengthSquared() < 0.01f) return false;
            return Vector2.Dot(travel, Vector2.Normalize(to)) < -0.3f;
        }

        /// <summary>Wolfpack: friendly vehicles within <paramref name="radius"/> (not itself), at most <paramref name="max"/>.</summary>
        private int Pack(Vehicle v, float radius, int max)
        {
            var n = 0;
            foreach (var ally in _world.VehicleList)
            {
                if (ally == v || !ally.IsAlive || ally.Team != v.Team || ally.Def.Static) continue;
                if (Vector2.DistanceSquared(ally.Position, v.Position) > radius * radius) continue;
                if (++n >= max) break;
            }
            return n;
        }

        /// <summary>How many friendly vehicles (itself too) are firing at its main weapon's target.</summary>
        private int FocusedBy(Vehicle v)
        {
            if (!v.Target.IsValid) return 0;
            var n = 0;
            foreach (var ally in _world.VehicleList)
                if (ally.IsAlive && ally.Team == v.Team && ally.Target == v.Target) n++;
            return n;
        }

        /// <summary>Reverse Gearbox: an armed enemy on the ground closes inside half its reach, and it backs off, nose on.</summary>
        private void BackOff(Vehicle v, GearState g, double now)
        {
            if (v.Flying || v.Def.Static || v.UnderPlayerControl(now) || v.Stunned) return;
            var reach = MathF.Max(10f, v.Arms[0].Range * 0.45f);
            var threat = _world.FindNearestEnemy(v, reach, requireVisible: true, layers: TargetLayers.Ground, mobileOnly: true);
            if (threat == null || threat.Def.Passive || threat.Def.Weapon.MinRange > 0f) return;
            if (_world.Movement.BackAway(v, threat.Position, 8f))
            {
                g.BackOffAt = now + 4.0;
                Proc(v, "reverse_gearbox");
            }
            else g.BackOffAt = now + 1.0;
        }

        // ================================================================== damage

        /// <summary>What the new lines add to a hit going out (a share, added to the multiplier).</summary>
        private float OutgoingLines(Vehicle attacker, GearState g, IDamageable target, in HitInfo hit)
        {
            var m = 0f;
            var flank = g.Stat(StatId.DamageFlank);
            if (flank > 0f && hit.Kind == HitKind.Direct && !hit.Indirect && target is Vehicle side && DamageSystem.FacingFactor(side, hit.Origin) > 1f)
                m += flank;
            if (target is Vehicle drone && drone.Def.Drone) m += g.Stat(StatId.DamageVsDrone);
            if (g.Has(TraitId.SetPackHunt) && g.Pack > 0) m += g.Trait(TraitId.SetPackHunt).A * g.Pack;
            return m;
        }

        /// <summary>What the new lines take off a hit coming in (a share, added to the cut).</summary>
        private static float IncomingLines(Vehicle v, GearState g, in HitInfo hit)
        {
            var cut = 0f;
            // Underbelly armour: blasts and mines, never a direct hit.
            if (hit.Kind is HitKind.Splash or HitKind.Mine or HitKind.Strike) cut += g.Stat(StatId.ResistBlast);
            if (g.Has(TraitId.Rearguard) && g.Withdrawing) cut += g.Trait(TraitId.Rearguard).A;
            return cut;
        }

        /// <summary>
        /// Airburst Rounds: a share of the rockets, missiles and drones aimed at it are shot down by its
        /// own airburst fire short of it (half its damage bonus against drones). True when this one was.
        /// </summary>
        public bool ShootDown(Projectile p, Vehicle target)
        {
            var g = target.Gear;
            if (g == null || target.Flying || !target.IsAlive || target.Stunned) return false;
            var share = g.Stat(StatId.DamageVsDrone) * 0.5f;
            if (share <= 0f || p.Weapon.Projectile is not (ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Drone)) return false;
            if (_world.Random.NextDouble() >= share) return false;
            var from = p.Origin - target.Position;
            var toward = from.LengthSquared() > 0.01f ? Vector2.Normalize(from) : SimMath.Forward(target.Heading);
            _world.Emit(SimEvent.Intercept(target, p.Weapon, target.Position + toward * (target.Def.HullBound + 3f), false));
            Proc(target, "airburst_rounds");
            return true;
        }

        // ================================================================== deaths

        private void DeathLines(Vehicle victim, double now)
        {
            // Vengeance: friends of the fallen within 15 m hit harder for a while (the best holds; it never stacks).
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v == victim || v.Team != victim.Team || v.Gear == null || !v.Gear.Has(TraitId.Vengeance)) continue;
                var t = v.Gear.Trait(TraitId.Vengeance);
                var reach = t.B > 0f ? t.B : 15f;
                if (Vector2.DistanceSquared(v.Position, victim.Position) > reach * reach) continue;
                ref var s = ref v.Statuses[(int)StatusKind.Avenging];
                s.Value = s.Until > now ? MathF.Max(s.Value, t.A) : t.A;
                s.Until = now + (t.C > 0f ? t.C : 5f);
                Proc(v, TraitId.Vengeance);
            }
            // Bulwark Engineering's four pieces: a fallen tower leaves a machine-gun post for a while.
            if (victim.Def.Static && victim.Gear is { } g && g.Has(TraitId.SetBulwarkPost))
            {
                _posts.Add((victim.Position, victim.Team, g.Trait(TraitId.SetBulwarkPost).A > 0f ? g.Trait(TraitId.SetBulwarkPost).A : 20f));
                _world.Emit(SimEvent.Proc(victim, GearKeys.Trait(TraitId.SetBulwarkPost)));
            }
        }

        // ================================================================== healing

        /// <summary>
        /// Repairs a vehicle by <paramref name="amount"/> (already scaled by what it receives) and returns
        /// what it gained. With Phoenix Recovery's four pieces, what goes past its full health becomes an
        /// overheal shield (at most a share of its health, for a few seconds), unless a last stand has
        /// just saved it.
        /// </summary>
        public float Heal(Vehicle v, float amount)
        {
            if (!v.IsAlive || !(amount > 0f)) return 0f;
            var applied = MathF.Max(0f, MathF.Min(v.MaxHp - v.Hp, amount));
            v.Hp += applied;
            var over = amount - applied;
            var now = _world.Time;
            if (over > 0f && v.Gear is { } g && g.Has(TraitId.SetPhoenix) && v.LastStandUntil <= now)
            {
                var t = g.Trait(TraitId.SetPhoenix);
                ref var s = ref v.Statuses[(int)StatusKind.Overheal];
                var had = s.Until > now ? s.Value : 0f;
                var cap = v.MaxHp * (t.A > 0f ? t.A : 0.1f);
                s.Value = MathF.Min(cap, had + over);
                s.Until = now + (t.B > 0f ? t.B : 8f);
                if (had <= 0f && s.Value > 0f) Proc(v, TraitId.SetPhoenix);
            }
            return applied;
        }

        /// <summary>
        /// What is left of a hit after the overheal shield soaks what it can. A shield that takes part of a
        /// killing blow counts as a last stand: Unbreakable and a dome do not save it from the same blow.
        /// </summary>
        public float AbsorbOverheal(Vehicle v, float damage)
        {
            ref var s = ref v.Statuses[(int)StatusKind.Overheal];
            var now = _world.Time;
            if (s.Until <= now || s.Value <= 0f || damage <= 0f) return damage;
            var soaked = MathF.Min(s.Value, damage);
            s.Value -= soaked;
            if (s.Value <= 0.01f)
            {
                s.Value = 0f;
                s.Until = 0;
            }
            var left = damage - soaked;
            if (damage >= v.Hp && soaked > 0f) v.LastStandUntil = now + LastStandGap;
            return left;
        }

        /// <summary>Hit points left in an overheal shield (for the view).</summary>
        public static float OverhealOf(Vehicle v, double now)
        {
            var s = v.Statuses[(int)StatusKind.Overheal];
            return s.Until > now ? s.Value : 0f;
        }
    }
}
