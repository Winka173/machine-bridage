#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// The only place hit points change. Resolves impacts, splash and delayed explosions,
    /// and announces each destruction exactly once, which is what makes chain reactions
    /// terminate: an entity can only start one explosion. Equipment hooks in here: what a hit
    /// does to its target (<see cref="Abilities.GearSystem.Outgoing"/>), what a vehicle's
    /// resistances, barrier and armour traits take off (<see cref="Abilities.GearSystem.Incoming"/>),
    /// and what happens when a vehicle is destroyed.
    /// </summary>
    internal sealed class DamageSystem
    {
        /// <summary>Damage at the edge of a blast, relative to the centre.</summary>
        private const float EdgeFalloff = 0.25f;

        private readonly SimWorld _world;
        private readonly List<PendingExplosion> _pending = new();

        public DamageSystem(SimWorld world) => _world = world;

        public int PendingCount => _pending.Count;

        public void ResolveImpact(Projectile p)
        {
            var weapon = p.Weapon;
            var hit = EntityId.None;
            var at = p.AimPoint;
            if (!p.Tandem && TryIntercept(p)) return;
            var info = HitInfo.Of(p, HitKind.Direct);
            if (_world.TryGetTarget(p.Target, out var target) && target.IsAlive)
            {
                // Guided missiles follow their target (unless flares decoy them or a jammer scrambles
                // them); everything else lands where it was aimed.
                // Flares pull a missile off about one time in three (radar-guided missiles mostly see through them).
                var decoyed = weapon.Guided && ((target is Vehicle { FlaresUp: true } && _world.Random.NextDouble() < FlareDecoy) || p.Jammed || p.Failed);
                // Equipment that turns a round away: an EW jammer's cover, a decoy, a first missile losing lock.
                var lure = default(Vector2);
                var lured = !decoyed && target is Vehicle guarded && _world.Gear.Lure(guarded, p, out lure);
                if (lured) at = lure;
                else
                {
                    if (weapon.Guided && !decoyed) at = target.Position;
                    if (decoyed) at = target.Position + p.Miss;
                }
                if (!decoyed && !lured && Vector2.Distance(target.Position, at) <= target.Radius + 0.5f)
                {
                    // Blame first, so a killing blow is credited to this shooter.
                    if (target is Vehicle victim) Blame(victim, p.Owner, p.OwnerTeam);
                    var facing = target is Vehicle struck && !weapon.Indirect ? FacingFactor(struck, p.Origin) : 1f;
                    // A kamikaze drone's damage partly stopped by a turtle tank's shed.
                    if (weapon.Projectile == ProjectileKind.Drone && target is Vehicle shed) facing *= shed.Def.DroneArmor;
                    var dealt = Apply(target, weapon.Damage * p.DamageScale * facing, weapon.DamageType, info);
                    hit = target.Id;
                    if (!p.NoProc && p.Shooter?.Gear != null) _world.Gear.OnDirectHit(p, target, dealt);
                }
            }

            if (weapon.Pierce && !p.TargetFlying) PierceLine(p, at, hit);

            // Every blast is a little different: its reach varies by up to 15 %.
            if (weapon.SplashRadius > 0f)
                Splash(at, weapon.SplashRadius * (0.85f + 0.3f * (float)_world.Random.NextDouble()), weapon.Damage * p.DamageScale,
                    weapon.DamageType, p.OwnerTeam, hit, p.Owner, p.TargetFlying, info.As(HitKind.Splash));
            // A heavy round from equipment bursts round its target too, at half its weight.
            if (p.ExtraSplash > 0f)
                Splash(at, p.ExtraSplash, weapon.Damage * p.DamageScale * 0.5f, weapon.DamageType, p.OwnerTeam, hit, p.Owner, p.TargetFlying,
                    info.As(HitKind.Splash));

            _world.Emit(SimEvent.Impact(weapon, at, hit, p.OwnerTeam, p.TargetFlying));
            if (weapon.Cluster != null && !p.TargetFlying) Scatter(weapon.Cluster, at, p.OwnerTeam, p.DamageScale, p.Shooter);
        }

        /// <summary>
        /// Armour by facing, after Company of Heroes and Wargame: a hull is thickest in front. A
        /// direct-fire hit from the side does 1.25x, from behind 1.6x (within 50 degrees of the
        /// nose counts as the front, within 50 of the tail as the rear). Aircraft and fixed
        /// defences are the same all round, and artillery, bombs and drones strike from above.
        /// </summary>
        internal static float FacingFactor(Vehicle target, Vector2 from)
        {
            if (target.Flying || target.Def.Static || target.Armor is not (ArmorClass.Heavy or ArmorClass.Light)) return 1f;
            var toShooter = from - target.Position;
            if (toShooter.LengthSquared() < 0.01f) return 1f;
            var off = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(toShooter) - target.Heading));
            return off <= FrontArc ? 1f : off >= MathF.PI - RearArc ? RearFactor : SideFactor;
        }

        /// <summary>A weapon's own bonus against this target (see <see cref="DamageBonus"/>): the best bonus that applies times the worst penalty.</summary>
        internal static float BonusFor(WeaponDef weapon, Vehicle attacker, IDamageable target, double now)
        {
            var bonuses = weapon.Bonuses;
            var best = 1f;
            var worst = 1f;
            var vehicle = target as Vehicle;
            // A light tower's anti-air gun: +25 % on helicopters and drones.
            if (vehicle != null && vehicle.Flying && attacker.Def.Fort is { Size: SlotSize.Small } && weapon.CanTarget(true) &&
                (vehicle.Def.Class == UnitClass.Helicopter || vehicle.Def.Drone))
                best = LightTowerAirBonus;
            // Engineers breach obstacles three times as fast.
            if (vehicle != null && vehicle.Def.Obstacle && attacker.Def.RepairAura != null) best = MathF.Max(best, EngineerBreach);
            for (var i = 0; i < bonuses.Count; i++)
            {
                var b = bonuses[i];
                if (b.Class is { } c && (vehicle == null || vehicle.Def.Class != c)) continue;
                if (b.Armor is { } a && target.Armor != a) continue;
                // Standing still: a vehicle parked a while (a fixed defence does not count).
                if (b.StillFor > 0f && (vehicle == null || vehicle.Def.Static || vehicle.IsMoving || now - vehicle.StillSince < b.StillFor)) continue;
                if (b.Flank && (vehicle == null || FacingFactor(vehicle, attacker.Position) <= 1f)) continue;
                if (b.Mult >= 1f) best = MathF.Max(best, b.Mult);
                else worst = MathF.Min(worst, b.Mult);
            }
            return best * worst;
        }

        internal const float LightTowerAirBonus = 1.25f;
        internal const float EngineerBreach = 3f;

        internal const float SideFactor = 1.25f;
        internal const float RearFactor = 1.6f;
        private static readonly float FrontArc = SimMath.DegToRad(50f);
        private static readonly float RearArc = SimMath.DegToRad(50f);

        /// <summary>A cluster round opens over the impact: its bomblets land round it and go off one after another.</summary>
        private void Scatter(ClusterDef cluster, Vector2 at, int team, float damageScale, Vehicle? attacker)
        {
            var rng = _world.Random;
            var blast = damageScale == 1f ? cluster.Bomblet
                : new ExplosionDef(cluster.Bomblet.Damage * damageScale, cluster.Bomblet.Radius, 0f, cluster.Bomblet.Tier);
            for (var k = 0; k < cluster.Count; k++)
            {
                var angle = (float)rng.NextDouble() * SimMath.Tau;
                var reach = cluster.Radius * MathF.Sqrt(0.15f + 0.85f * (float)rng.NextDouble());
                var spot = at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach;
                _pending.Add(new PendingExplosion(_world.Time + 0.12 + 0.06 * k + 0.1 * rng.NextDouble(), spot, blast, EntityId.None, team, attacker, HitKind.Splash));
            }
        }

        /// <summary>
        /// An active protection system of the target's side shoots the round down short of its
        /// mark: missiles, drones and direct-fire rockets only (not shells, bullets, bombs or
        /// artillery rockets), aimed within the system's reach, while it has an interceptor.
        /// </summary>
        private bool TryIntercept(Projectile p)
        {
            var weapon = p.Weapon;
            var kind = weapon.Projectile;
            if (p.TargetFlying) return false;
            // Every system takes missiles, drones and direct-fire rockets; a point-defence laser
            // artillery rockets too, a C-RAM a share of the shells.
            var direct = weapon.Guided || (kind == ProjectileKind.Rocket && weapon.MinRange <= 0f);
            var rocket = kind == ProjectileKind.Rocket;
            var shell = kind == ProjectileKind.Shell && weapon.Indirect;
            if (!direct && !rocket && !shell) return false;
            var mark = _world.TryGetTarget(p.Target, out var target) && target.IsAlive ? target.Position : p.AimPoint;
            foreach (var v in _world.VehicleList)
            {
                var aps = v.Aps;
                if (aps == null || !v.IsAlive || v.Team == p.OwnerTeam || v.ApsCharges <= 0 || v.Stunned) continue;
                if (Vector2.DistanceSquared(v.Position, mark) > aps.Radius * aps.Radius) continue;
                if (!direct && rocket && !aps.Rockets) continue;
                if (!direct && shell && (aps.Shells <= 0f || _world.Random.NextDouble() >= aps.Shells)) continue;
                v.ApsCharges--;
                v.ApsLeft = !v.ApsLeft;
                // The interceptor meets the round a few metres out, on the side it came from.
                var from = _world.TryGetVehicle(p.Owner, out var shooter) ? shooter.Position : mark + SimMath.Forward(v.Heading) * 10f;
                var toward = from - v.Position;
                toward = toward.LengthSquared() > 0.01f ? Vector2.Normalize(toward) : SimMath.Forward(v.Heading);
                _world.Emit(SimEvent.Intercept(v, weapon, v.Position + toward * (v.Def.HullBound + 3f), v.ApsLeft));
                return true;
            }
            return false;
        }

        /// <summary>
        /// Area damage with linear falloff. Weapon splash spares the shooter's team; blasts
        /// from <see cref="Teams.Environment"/> (cook-offs, fuel) hurt everyone.
        /// </summary>
        public void Splash(Vector2 at, float radius, float damage, DamageType type, int sourceTeam, EntityId exclude,
            EntityId attacker = default, bool airborne = false, in HitInfo info = default)
        {
            foreach (var v in _world.VehicleList)
            {
                // A blast on the ground cannot reach aircraft, and an airburst does not reach the ground.
                if (!v.IsAlive || v.Id == exclude || v.Flying != airborne) continue;
                if (sourceTeam != Teams.Environment && v.Team == sourceTeam) continue;
                if (Reaches(v, at, radius)) Blame(v, attacker, sourceTeam);
                ApplyFalloff(v, at, radius, damage, type, info);
            }
            if (airborne) return;
            foreach (var prop in _world.PropList)
            {
                if (!prop.IsAlive || prop.Id == exclude) continue;
                ApplyFalloff(prop, at, radius, damage, type, info);
            }
        }

        /// <summary>
        /// Remembers who hit a vehicle: the shooter lets idle vehicles turn on their attacker, the
        /// team decides who is paid for the kill. Blasts from the environment credit nobody.
        /// </summary>
        private void Blame(Vehicle victim, EntityId attacker, int team)
        {
            victim.LastAttackerTeam = team >= 0 ? team : -1;
            victim.LastHitTime = _world.Time;
            if (attacker.IsValid) victim.LastAttacker = attacker;
        }

        /// <summary>A fire burning on a vehicle does its share of damage this step (credited to whoever lit it).</summary>
        internal void Burn(Vehicle v, float amount, Vehicle? lighter, int team, EntityId source)
        {
            Blame(v, source, team);
            Apply(v, amount, DamageType.Fire, new HitInfo(lighter, team, null, v.Position, HitKind.Burn, false));
        }

        /// <summary>Deals damage (after the damage table, equipment and armour); returns what the target actually lost.</summary>
        public float Apply(IDamageable target, float amount, DamageType type, in HitInfo hit = default)
        {
            if (!target.IsAlive || !(amount > 0f)) return 0f;
            if (target is Prop { Invulnerable: true } || target is Vehicle { Invulnerable: true }) return 0f;
            var raw = hit.Kind is HitKind.Burn or HitKind.Redirect;
            var damage = raw ? amount : amount * _world.Catalog.Damage.Multiplier(type, target.Armor);
            if (!(damage > 0f)) return 0f;
            if (hit.Attacker != null && !raw) damage *= _world.Gear.Outgoing(hit.Attacker, target, hit);
            if (hit.Attacker != null && hit.Weapon != null && !raw) damage *= BonusFor(hit.Weapon, hit.Attacker, target, _world.Time);
            // A gun pit down in its hole takes much less.
            if (target is Vehicle { Lowered: true } pit && pit.Def.Hidden is { } hide) damage *= 1f - hide.Cut;

            switch (target)
            {
                case Vehicle vehicle:
                    return HitVehicle(vehicle, damage, type, hit);
                case Prop prop:
                    prop.Hp = MathF.Max(0f, prop.Hp - damage);
                    _world.Emit(SimEvent.Damage(prop, damage));
                    if (!prop.IsAlive) OnPropDestroyed(prop);
                    return damage;
            }
            return 0f;
        }

        private float HitVehicle(Vehicle vehicle, float damage, DamageType type, in HitInfo hit)
        {
            var now = _world.Time;
            if (vehicle.ImmuneUntil > now) return 0f;
            if (hit.Kind == HitKind.Burn)
            {
                damage *= _world.Gear.Incoming(vehicle, type, hit);
            }
            else if (hit.Kind != HitKind.Redirect)
            {
                damage *= vehicle.DamageTaken;
                if (vehicle.ShieldUp) damage *= 1f - vehicle.ShieldAmount;
                if (vehicle.GraceUntil > now) damage *= 0.2f;
                // Hull-down only shields from direct fire: shells, rockets and bombs from above still land.
                if (type is DamageType.Kinetic or DamageType.ArmorPiercing && _world.IsEntrenched(vehicle))
                    damage *= 1f - SimWorld.EntrenchReduction;
                damage *= _world.Gear.Incoming(vehicle, type, hit);
                if (!(damage > 0f)) return 0f;
                if (!(hit.Projectile?.Tandem ?? false)) damage = _world.Status.Absorb(vehicle, damage);
                if (vehicle.Gear != null) damage = _world.Gear.Soak(vehicle, damage);
                damage = _world.Gear.Redirect(vehicle, damage, hit);
            }
            if (!(damage > 0f)) return 0f;
            // Unbreakable: a killing blow once a life leaves it on a sliver, briefly untouchable.
            if (damage >= vehicle.Hp && vehicle.Gear != null && damage < 1e6f && _world.Gear.Survives(vehicle)) damage = MathF.Max(0f, vehicle.Hp - 1f);
            // A multi-phase boss stops at its next phase's mark (what goes past it is lost) and transforms.
            var phaseReached = false;
            if (vehicle.Phase < vehicle.Def.Phases.Count && !vehicle.Transforming)
            {
                var mark = vehicle.Def.Phases[vehicle.Phase].At * vehicle.MaxHp;
                if (vehicle.Hp > mark && vehicle.Hp - damage <= mark)
                {
                    damage = vehicle.Hp - mark;
                    phaseReached = true;
                }
            }
            vehicle.Hp = MathF.Max(0f, vehicle.Hp - damage);
            if (phaseReached) _world.Abilities.BeginPhase(vehicle);
            // A firing-range target takes the hit (its bar shows it) but never goes down.
            if (vehicle.Dummy) vehicle.Hp = MathF.Max(vehicle.Hp, vehicle.MaxHp * 0.25f);
            _world.Emit(SimEvent.Damage(vehicle, damage));
            if (vehicle.Gear != null) _world.Gear.AfterDamaged(vehicle, type, hit);
            if (!vehicle.IsAlive) OnVehicleDestroyed(vehicle, hit);
            return damage;
        }

        /// <summary>Takes hit points off a vehicle directly (a guardian's share of an ally's hit): its own plating counts, nothing else.</summary>
        internal void TakeOver(Vehicle guardian, float damage, in HitInfo hit)
        {
            Apply(guardian, damage * guardian.DamageTaken, DamageType.Kinetic, hit.As(HitKind.Redirect));
        }

        /// <summary>Detonates every explosion that has come due; new ones may be queued as a result.</summary>
        public void Step()
        {
            var i = 0;
            while (i < _pending.Count)
            {
                var pending = _pending[i];
                if (pending.Due > _world.Time)
                {
                    i++;
                    continue;
                }
                _pending.RemoveAt(i);
                _world.Emit(SimEvent.Exploded(pending.Position, pending.Explosion, pending.Source));
                var info = pending.Kind == HitKind.None ? default
                    : new HitInfo(pending.Attacker, pending.Team, null, pending.Position, pending.Kind, true);
                Splash(pending.Position, pending.Explosion.Radius, pending.Explosion.Damage, DamageType.HighExplosive,
                    pending.Team, EntityId.None, pending.Attacker?.Id ?? default, false, info);
            }
        }

        /// <summary>A blast from equipment (Volatile Fuel Tanks, Uplink Barrage) that spares its own side, after <paramref name="delay"/> seconds.</summary>
        internal void Queue(Vector2 at, ExplosionDef blast, double delay, int team, Vehicle? attacker, HitKind kind, EntityId source = default) =>
            _pending.Add(new PendingExplosion(_world.Time + delay, at, blast, source, team, attacker, kind));

        private static bool Reaches(IDamageable target, Vector2 at, float radius) =>
            Vector2.Distance(target.Position, at) - target.Radius <= radius;

        private void ApplyFalloff(IDamageable target, Vector2 at, float radius, float damage, DamageType type, in HitInfo info)
        {
            var edgeDistance = MathF.Max(0f, Vector2.Distance(target.Position, at) - target.Radius);
            if (edgeDistance > radius) return;
            var scale = 1f - (1f - EdgeFalloff) * SimMath.Clamp01(edgeDistance / radius);
            Apply(target, damage * scale, type, info);
        }

        /// <summary>
        /// A car bomb goes off: the blast (its weapon's damage and splash) hurts the enemy and
        /// spares its own side, and the car is gone.
        /// </summary>
        internal void Detonate(Vehicle car, WeaponDef charge)
        {
            if (!car.IsAlive) return;
            _pending.Add(new PendingExplosion(_world.Time, car.Position,
                new ExplosionDef(charge.Damage, MathF.Max(1f, charge.SplashRadius), 0f, charge.ImpactTier), car.Id, car.Team));
            car.Detonated = true;
            Apply(car, car.Hp + car.MaxHp, DamageType.HighExplosive);
            car.Hp = 0f;
        }

        /// <summary>
        /// A railgun slug goes on through everything on its line: every enemy ground vehicle within
        /// a hull's width of it takes the full hit (the one it was aimed at already has).
        /// </summary>
        private void PierceLine(Projectile p, Vector2 to, EntityId struck)
        {
            var from = p.Origin;
            var line = to - from;
            var length = line.Length();
            if (length < 0.1f) return;
            var along = line / length;
            var info = HitInfo.Of(p, HitKind.Pierce);
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Team == p.OwnerTeam || v.Id == struck || v.Id == p.Owner) continue;
                var offset = v.Position - from;
                var t = Vector2.Dot(offset, along);
                if (t < 0f || t > length + 12f) continue;
                if ((offset - along * t).Length() > v.Radius + 1.2f) continue;
                Blame(v, p.Owner, p.OwnerTeam);
                Apply(v, p.Weapon.Damage * p.DamageScale, p.Weapon.DamageType, info);
                PierceVictims++;
            }
        }

        /// <summary>Vehicles hit by a piercing round beyond the one it was aimed at, over the battle (balance measurements).</summary>
        internal int PierceVictims { get; private set; }

        /// <summary>Chance a guided missile at an aircraft with its flares out is decoyed.</summary>
        private const double FlareDecoy = 0.35;

        private void OnVehicleDestroyed(Vehicle vehicle, in HitInfo hit)
        {
            var speed = vehicle.Speed;
            vehicle.ClearPath();
            vehicle.Speed = 0f;
            // Who gets the kill: the vehicle whose round it was, else whoever hit it last (recently).
            var killer = hit.Attacker;
            if (killer == null && vehicle.LastAttacker.IsValid && _world.Time - vehicle.LastHitTime <= 10.0 &&
                _world.TryGetVehicle(vehicle.LastAttacker, out var last)) killer = last;
            if (killer != null && killer.Team == vehicle.Team) killer = null;
            _world.Emit(SimEvent.VehicleLost(vehicle));
            _world.Economy.OnVehicleDestroyed(vehicle, killer);
            if (vehicle.Def.DeathExplosion != null && !vehicle.Detonated) Schedule(vehicle.Position, vehicle.Def.DeathExplosion, vehicle.Id);
            if (vehicle.Def.Flying) ScheduleCrash(vehicle, speed);
            _world.Gear.OnDeath(vehicle, killer);
        }

        /// <summary>
        /// A shot-down aircraft comes down where its momentum carries it, as its wreck falls on
        /// screen (VehicleView: a fall under 11 m/s² for aeroplanes, 7 for helicopters, the drift
        /// fading as it goes), and crushes whatever is under it, either side's: a blast sized by
        /// how heavy it was.
        /// </summary>
        private void ScheduleCrash(Vehicle vehicle, float speed)
        {
            var def = vehicle.Def;
            var fall = MathF.Sqrt(2f * def.Altitude / (def.FixedWing ? 11f : 7f));
            var fade = def.FixedWing ? 0.35f : 0.5f;
            var glide = MathF.Min(fall, 1f / fade);
            var carry = 0.8f * speed * (glide - 0.5f * fade * glide * glide);
            var forward = SimMath.Forward(vehicle.Heading);
            var at = _world.ClampToMap(vehicle.Position + forward * carry);
            _pending.Add(new PendingExplosion(_world.Time + fall, at, CrashBlast(def), vehicle.Id));
        }

        /// <summary>The blast of an aircraft hitting the ground: 8 % of its health as damage, wider for heavier aircraft.</summary>
        public static ExplosionDef CrashBlast(VehicleDef def) =>
            new(Math.Clamp(def.MaxHp * 0.08f, 60f, 450f), Math.Clamp(3.5f + def.MaxHp / 800f, 4f, 10f), 0f,
                def.MaxHp > 3000f ? ExplosionTier.Huge : ExplosionTier.Large);

        /// <summary>A hull drives over a tree, bush or fence: it goes down the way the hull was going.</summary>
        internal void Crush(Prop prop, Vector2 direction)
        {
            if (!prop.IsAlive || prop.Invulnerable) return;
            prop.Hp = 0f;
            if (prop.Def.BlocksFire) _world.Cover.Remove(prop);
            _world.Emit(SimEvent.PropCrushed(prop, direction));
        }

        private void OnPropDestroyed(Prop prop)
        {
            if (prop.Def.BlocksMovement)
                _world.Grid.RemoveBlocker(prop.Position, prop.Width, prop.Depth, SimWorld.ObstacleClearance);
            if (prop.Def.BlocksFire) _world.Cover.Remove(prop);
            _world.Emit(SimEvent.PropLost(prop));
            if (prop.Def.Explosion != null) Schedule(prop.Position, prop.Def.Explosion, prop.Id);
        }

        private void Schedule(Vector2 position, ExplosionDef explosion, EntityId source) =>
            _pending.Add(new PendingExplosion(_world.Time + explosion.Delay, position, explosion, source));

        private readonly struct PendingExplosion
        {
            public PendingExplosion(double due, Vector2 position, ExplosionDef explosion, EntityId source, int team = Teams.Environment,
                Vehicle? attacker = null, HitKind kind = HitKind.None)
            {
                Team = team;
                Due = due;
                Position = position;
                Explosion = explosion;
                Source = source;
                Attacker = attacker;
                Kind = kind;
            }

            public double Due { get; }
            public Vector2 Position { get; }
            public ExplosionDef Explosion { get; }
            public EntityId Source { get; }

            /// <summary>Whose blast it is (a cluster bomblet spares its own side); the environment's hurts everyone.</summary>
            public int Team { get; }

            /// <summary>The vehicle whose round or equipment it is (its hit effects and kill credit), if any.</summary>
            public Vehicle? Attacker { get; }

            public HitKind Kind { get; }
        }
    }
}
