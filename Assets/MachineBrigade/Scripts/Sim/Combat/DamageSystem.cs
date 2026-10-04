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
        /// <summary>Damage at the edge of a blast, relative to the centre (tunables weapons.damageRules.edgeFalloff).</summary>
        internal static float EdgeFalloff => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageRules.EdgeFalloff;

        private readonly SimWorld _world;
        private readonly List<PendingExplosion> _pending = new();

        /// <summary>Toppling walls: when each one's ground opens (see <see cref="PropDef.Collapse"/>).</summary>
        private readonly List<(double due, Prop prop)> _collapsing = new();

        public DamageSystem(SimWorld world) => _world = world;

        public int PendingCount => _pending.Count;

        /// <summary>
        /// Measurements only (never set in play, like <see cref="Entities.Vehicle.PathTrace"/>): told of
        /// every hit point a vehicle loses, with who dealt it, how and with what (the equipment lab
        /// attributes damage to the vehicle that dealt it).
        /// </summary>
        internal static Action<Vehicle?, Vehicle, float, HitKind, WeaponDef?>? DamageLog;

        /// <summary>The last hit's penetration multiplier and the face it struck (prompt 21: the Sandbox's hit report).</summary>
        private float _lastPen = 1f;
        private ArmorFace _lastFace;

        public void ResolveImpact(Projectile p)
        {
            var weapon = p.Weapon;
            var hit = EntityId.None;
            var at = p.AimPoint;
            // Prompt 17 C: a swarm drone whose target is gone strikes another round where it arrives.
            if (weapon.SwarmReach > 0f) RetargetSwarm(p);
            if (!p.Tandem && TryIntercept(p)) return;
            // Airburst Rounds: the target's own airburst fire takes down some of what is flying at it.
            if (!p.Tandem && !p.TargetFlying && p.Target.IsValid && _world.TryGetVehicle(p.Target, out var shooting) && shooting.Gear != null &&
                _world.Gear.ShootDown(p, shooting)) return;
            var info = HitInfo.Of(p, HitKind.Direct);
            // Fix prompt L4: a guided round taken off its target in flight (a flare, its shooter's lost sight, out of reach,
            // CombatSystem.GuideRounds) goes off where it was diverted to, its target or not still there: no direct hit.
            if (p.Diverted != Divert.None)
            {
                at = p.DivertAt;
                Burst(p, weapon, at, hit, info);
                return;
            }
            if (_world.TryGetTarget(p.Target, out var target) && target.IsAlive)
            {
                // Guided missiles follow their target (unless a jammer scrambles them or the launch roll lost the lock: the
                // flares are rolled in flight now, fix prompt L4); everything else lands where it was aimed.
                // Prompt 15 C: a jammer or a lost lock takes any guided round.
                var decoyed = weapon.Guided && (p.Jammed || p.Failed);
                // Equipment that turns a round away: an EW jammer's cover, a decoy, a first missile losing lock.
                var lure = default(Vector2);
                var lured = !decoyed && target is Vehicle guarded && _world.Gear.Lure(guarded, p, out lure);
                if (lured) at = lure;
                else
                {
                    // Play-test 8 A: a steered bomb (the SDB, the JDAM) glides onto its target too.
                    // Prompt 25 G: so does a guided shell (the Excalibur, the Krasnopol).
                    // Fix prompt L4 rule A: and a guided rocket (the APKWS).
                    if (CombatSystem.Homes(weapon) && !decoyed) at = p.Part >= 0 && target is Vehicle aimedBoss ? aimedBoss.PartPosition(p.Part) : target.Position;
                    if (decoyed) at = target.Position + p.Miss;
                }
                // A round aimed at a boss's part strikes it only if it lands on it; else it strikes the body.
                if (p.Part >= 0 && target is Vehicle partBoss && (partBoss.IsPartBroken(p.Part) ||
                    Vector2.Distance(partBoss.PartPosition(p.Part), at) > partBoss.Def.Parts[p.Part].Radius + 1.5f)) p.Part = -1;
                // A part may stand out past the hull's round footprint (a hovercraft's fans, a train's locomotive): landing on it is a hit.
                if (!decoyed && !lured && (p.Part >= 0 || Vector2.Distance(target.Position, at) <= target.Radius + 0.5f))
                {
                    // Blame first, so a killing blow is credited to this shooter.
                    if (target is Vehicle victim) Blame(victim, p.Owner, p.OwnerTeam);
                    // The face it strikes and that face's armour are worked out in Apply (prompt 15).
                    // A kamikaze drone's damage partly stopped by a turtle tank's shed.
                    var shedCut = weapon.Projectile == ProjectileKind.Drone && target is Vehicle shed ? shed.Def.DroneArmor : 1f;
                    var dealt = Apply(target, weapon.Damage * p.DamageScale * shedCut, weapon.DamageType, info);
                    hit = target.Id;
                    if (!p.NoProc && p.Shooter?.Gear != null) _world.Gear.OnDirectHit(p, target, dealt);
                }
            }

            // Play-test 6 (DECISIONS 21F): a round fired straight at a big target (a boss, a big ship, a large aircraft or
            // structure) bursts where it meets its hull or the struck part's edge, not in its middle; one that comes down
            // from above (lobbed, dropped, a diving drone or a top attack) still bursts on the roof. The damage and the face
            // struck are as before: the face is the one turned to the shooter, on whose line the contact point lies.
            if (hit.IsValid && !weapon.Indirect && !weapon.TopAttack && _world.TryGetVehicle(hit, out var struck))
                at = p.Part >= 0 && p.Part < struck.Def.Parts.Count
                    ? HullContact.On(struck.PartPosition(p.Part), 0f, 0f, struck.Def.Parts[p.Part].Radius, p.Origin)
                    : HullContact.On(struck.Def, struck.Position, struck.Heading, p.Origin);

            if (weapon.Pierce && !p.TargetFlying && !p.Bounce) PierceLine(p, at, hit);
            Burst(p, weapon, at, hit, info);
        }

        /// <summary>A round going off at <paramref name="at"/> (struck <paramref name="hit"/>, none for a miss): its blast, the impact event and its bomblets.</summary>
        private void Burst(Projectile p, WeaponDef weapon, Vector2 at, EntityId hit, in HitInfo info)
        {
            // Every blast is a little different: its reach varies by up to 15 %. A ricochet strikes its target only.
            if (weapon.SplashRadius > 0f && !p.Bounce)
            {
                // Prompt 26 B.3: a boss weapon's blast has two layers, the core at full damage and the edge twice as wide at 40 %,
                // both fixed (the ordinary blast's reach varies by up to 15 %).
                if (weapon.SplashEdge > 0f)
                    Splash(at, weapon.SplashRadius, weapon.Damage * p.DamageScale, weapon.DamageType, p.OwnerTeam, hit, p.Owner, p.TargetFlying,
                        info.As(HitKind.Splash), weapon.SplashEdge, weapon.EdgeShare);
                else
                    Splash(at, weapon.SplashRadius * (0.85f + 0.3f * (float)_world.Random.NextDouble()), weapon.Damage * p.DamageScale,
                        weapon.DamageType, p.OwnerTeam, hit, p.Owner, p.TargetFlying, info.As(HitKind.Splash));
            }
            // A heavy round from equipment bursts round its target too, at half its weight.
            if (p.ExtraSplash > 0f)
                Splash(at, p.ExtraSplash, weapon.Damage * p.DamageScale * 0.5f, weapon.DamageType, p.OwnerTeam, hit, p.Owner, p.TargetFlying,
                    info.As(HitKind.Splash));

            _world.Emit(SimEvent.Impact(weapon, at, hit, p.OwnerTeam, p.TargetFlying));
            if (weapon.Cluster != null && !p.TargetFlying && !p.NoCluster) Scatter(weapon.Cluster, at, p.OwnerTeam, p.DamageScale, p.Shooter);
        }

        /// <summary>
        /// Prompt 15 A.2: the face a direct-fire round from <paramref name="from"/> strikes (within 40 degrees of
        /// the nose the front, DECISIONS 20X; within 50 of the tail the rear; else the side). Aircraft are the same
        /// all round and count as the front; a fixed defence's faces follow its heading (a bunker's embrasured front).
        /// </summary>
        internal static ArmorFace FaceFrom(Vehicle target, Vector2 from) =>
            target.Flying ? ArmorFace.Front : Armour.FaceFrom(target.Position, target.Heading, from);

        /// <summary>
        /// An aeroplane fires down on its target in its dive: its direct fire strikes the roof. A helicopter fires
        /// from low and stand-off, at the face turned to it.
        /// </summary>
        internal static bool FromAbove(Vehicle? shooter) => shooter != null && shooter.Flying && shooter.Def.FixedWing;

        /// <summary>A direct-fire hit from <paramref name="from"/> takes the vehicle in the side or the rear (flanking rounds, the wheeled gun's bonus).</summary>
        internal static bool Flanked(Vehicle target, Vector2 from) =>
            !target.Flying && !target.Def.Static && FaceFrom(target, from) != ArmorFace.Front;

        /// <summary>
        /// Prompt 15 B.3: the face a hit strikes. Rounds that come down on the roof (top-attack weapons, bomblets,
        /// everything lobbed or dropped, called strikes, a mine under the belly, an aeroplane's guns and rockets in
        /// its dive) strike the top; a direct hit the face turned to the shooter; a blast the face turned to it.
        /// </summary>
        internal static ArmorFace FaceOf(IDamageable target, in HitInfo hit)
        {
            if (target is not Vehicle v || v.Flying) return ArmorFace.Front;
            if (hit.Top || (hit.Weapon != null && Armour.StrikesTop(hit.Weapon)) || hit.Kind is HitKind.Strike or HitKind.Mine) return ArmorFace.Top;
            if (hit.Kind is HitKind.Direct or HitKind.Pierce && FromAbove(hit.Attacker)) return ArmorFace.Top;
            if (hit.Kind == HitKind.Splash || hit.HasBlast) return hit.HasBlast ? FaceFrom(v, hit.Blast) : ArmorFace.Top;
            return hit.Kind is HitKind.Direct or HitKind.Pierce ? FaceFrom(v, hit.Origin) : ArmorFace.Front;
        }

        /// <summary>
        /// Prompt 15 B.5: what a hit's damage is multiplied by before equipment and bonuses: the armour multiplier
        /// (the round's penetration, with the shooter's equipment, against the armour of the face it strikes; a blast's
        /// fragments pierce as a heavy machine gun against vehicles; a boss part has its own armour) times the damage type
        /// against the target's kind. Combat final 04/10: a top-attack weapon's hit on a ground target or a structure meets
        /// the roof's armour (a boss part's own) through the top attack table only; every other hit the direct table.
        /// </summary>
        internal float HitMultiplier(IDamageable target, DamageType type, in HitInfo hit)
        {
            var table = _world.Catalog.Damage;
            var weapon = hit.Weapon != null && hit.Weapon.DamageType == type ? hit.Weapon : null;
            var kind = target.Kind;
            // Damage that says nothing of its round (no weapon, no penetration, no kind: a scripted blow) meets
            // the damage type's table only; everything else meets armour.
            var known = weapon != null || hit.Pen >= 0f || hit.Kind != HitKind.None;
            var pen = weapon != null ? weapon.Penetration : hit.Pen >= 0f ? hit.Pen : Armour.DefaultPenetration(type);
            if (hit.Attacker != null) pen += hit.Attacker.PenetrationUp;
            // A blast's fragments (a round's splash, a called strike, a cook-off) pierce as a heavy machine gun against vehicles.
            if (hit.Kind is HitKind.Splash or HitKind.Strike || (hit.HasBlast && weapon == null)) pen = Armour.SplashPenetration(pen, kind);
            float armour;
            var face = ArmorFace.Front;
            // Combat final 04/10: the weapon's topAttack flag picks the top attack table (never on an aircraft).
            var topAttack = weapon is { TopAttack: true } && kind != TargetKind.Air;
            if (target is Vehicle v)
            {
                var part = v.HasParts && hit.Kind == HitKind.Direct && hit.Projectile is { Part: >= 0 } shot && !v.IsPartBroken(shot.Part) ? shot.Part : -1;
                _lastFace = face = part >= 0 ? ArmorFace.Front : FaceOf(v, hit);
                armour = part >= 0 ? v.Def.Parts[part].ArmourOn(v.Def) : v.ArmourOn(_lastFace);
                if (part < 0 && face != ArmorFace.Top) topAttack = false;
            }
            else armour = target.Armour[topAttack ? ArmorFace.Top : ArmorFace.Front];
            // The thermobaric tag replaces high explosive's structure value (not on top of it).
            var typeMult = weapon != null ? table.TypeOf(weapon, kind) : table.TypeOf(type, kind, hit.Thermo);
            // DECISIONS 20X: a direct-table round overmatches a face it meets side on, not the roof and not an aircraft;
            // a top attack reads its own table against the roof (DamageTable.ArmourMultiplier: one table, never both).
            _lastPen = known ? table.ArmourMultiplier(pen, armour, kind, face == ArmorFace.Top, topAttack) : 1f;
            // Prompt 26 A.5: a ground boss struck on its side or its rear (not on a part) takes half as much again.
            var flank = target is Vehicle flanked && flanked.Def.Boss && !flanked.Flying && (face == ArmorFace.Side || face == ArmorFace.Rear) ? BossFlankBonus : 1f;
            return _lastPen * typeMult * flank;
        }

        /// <summary>
        /// What one of a weapon's rounds is expected to do, as a multiplier, to a target from <paramref name="from"/>
        /// (targeting and the overkill check): penetration against the face it would strike, times the damage type.
        /// </summary>
        internal float Estimate(WeaponDef weapon, Vehicle shooter, IDamageable target)
        {
            var table = _world.Catalog.Damage;
            var face = target is Vehicle v
                ? v.Flying ? ArmorFace.Front : Armour.StrikesTop(weapon) || FromAbove(shooter) ? ArmorFace.Top : FaceFrom(v, shooter.Position)
                : ArmorFace.Front;
            var topAttack = weapon.TopAttack && target.Kind != TargetKind.Air && (target is not Vehicle || face == ArmorFace.Top);
            var armour = target is Vehicle tv ? tv.ArmourOn(face) : target.Armour[topAttack ? ArmorFace.Top : ArmorFace.Front];
            return table.ArmourMultiplier(weapon.Penetration + shooter.PenetrationUp, armour, target.Kind, face == ArmorFace.Top, topAttack) *
                   table.TypeOf(weapon, target.Kind);
        }

        /// <summary>Whether a hit is thermobaric (its weapon, or a thermobaric strike).</summary>
        private static bool Thermobaric(in HitInfo hit) => hit.Thermo || (hit.Weapon?.Thermobaric ?? false);

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
            // Engineers (and the armoured bulldozer) breach obstacles three times as fast.
            if (vehicle != null && vehicle.Def.Obstacle && !vehicle.Def.Wall && (attacker.Def.RepairAura != null || attacker.Def.Breacher)) best = MathF.Max(best, EngineerBreach);
            // Prompt 32 L3: the wall breakers (bulldozer, engineer vehicle, line charge) hit walls 1.5 times as hard (walls only).
            if (vehicle != null && vehicle.Def.Wall && attacker.Def.WallBreaker) best = MathF.Max(best, attacker.Def.WallBreakerScale);
            for (var i = 0; i < bonuses.Count; i++)
            {
                var b = bonuses[i];
                if (b.Class is { } c && (vehicle == null || vehicle.Def.Class != c)) continue;
                if (b.Armor is { } a && target.Armor != a) continue;
                // Standing still: a vehicle parked a while (a fixed defence does not count).
                if (b.StillFor > 0f && (vehicle == null || vehicle.Def.Static || vehicle.IsMoving || now - vehicle.StillSince < b.StillFor)) continue;
                if (b.Flank && (vehicle == null || !Flanked(vehicle, attacker.Position))) continue;
                if (b.Mult >= 1f) best = MathF.Max(best, b.Mult);
                else worst = MathF.Min(worst, b.Mult);
            }
            return best * worst;
        }

        /// <summary>Prompt 26 A.5: what a ground boss takes from a hit on its side or rear, over the front's.</summary>
        internal const float BossFlankBonus = 1.5f;

        internal const float LightTowerAirBonus = 1.25f;
        internal static float EngineerBreach => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageSystem.EngineerBreach;


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
                _pending.Add(new PendingExplosion(_world.Time + 0.12 + 0.06 * k + 0.1 * rng.NextDouble(), spot, blast, EntityId.None, team, attacker, HitKind.Splash,
                    cluster.Penetration));
            }
        }

        /// <summary>Prompt 17 C: a swarm drone arriving over a target that is gone takes the nearest enemy on the ground its side sees within the swarm's reach.</summary>
        private void RetargetSwarm(Projectile p)
        {
            if (_world.TryGetTarget(p.Target, out var aimed) && aimed.IsAlive) return;
            Vehicle? best = null;
            var bestD2 = p.Weapon.SwarmReach * p.Weapon.SwarmReach;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Team == p.OwnerTeam || v.Team < 0 || v.Invulnerable || v.Def.Untargetable || !v.IsVisibleTo(p.OwnerTeam)) continue;
                var d2 = Vector2.DistanceSquared(v.Position, p.AimPoint);
                if (d2 >= bestD2) continue;
                best = v;
                bestD2 = d2;
            }
            if (best != null) p.Target = best.Id;
        }

        /// <summary>
        /// An active protection system of the target's side shoots the round down short of its
        /// mark: missiles, drones and direct-fire rockets only (not shells, bullets, bombs or
        /// artillery rockets), aimed within the system's reach, while it has an interceptor.
        /// Prompt 20 L.1: interceptor missiles that take no direct fire (the Iron Dome) take only
        /// rounds lobbed from afar: drones, artillery rockets, long-range missiles and shells.
        /// </summary>
        /// <summary>A cruise or ballistic missile (its family, or a missile fired from a minimum range).</summary>
        internal static bool IsHeavyMissile(WeaponDef weapon) =>
            weapon.Family is "cruise" or "ballistic" || (weapon.Projectile == ProjectileKind.Missile && weapon.MinRange > 0f);

        /// <summary>
        /// Play-test 5 (DECISIONS 20W): the rounds a gun point defence (<see cref="ApsDef.Burst"/>) may take, by the same
        /// rules as <see cref="TryIntercept"/>; <paramref name="shell"/>: only its share of them (the caller rolls).
        /// </summary>
        internal static bool GunTakes(ApsDef aps, WeaponDef weapon, out bool shell)
        {
            var kind = weapon.Projectile;
            shell = false;
            // Prompt 29 S05: flagged rounds no point-defence gun takes.
            if (weapon.Interceptable == false || weapon.CiwsEligible == false) return false;
            if (weapon.Beam || weapon.DamageType == DamageType.Energy) return false;
            // Prompt 25 F2 batch A: a glide bomb is taken like a guided round lobbed from afar.
            var direct = weapon.Guided || weapon.Glides || (kind == ProjectileKind.Rocket && weapon.MinRange <= 0f);
            var rocket = kind == ProjectileKind.Rocket;
            var lobbedShell = kind == ProjectileKind.Shell && weapon.Indirect;
            var heavy = IsHeavyMissile(weapon);
            if (!direct && !rocket && !lobbedShell && !heavy) return false;
            var lobbed = kind == ProjectileKind.Drone || weapon.Glides || (weapon.MinRange > 0f && kind is ProjectileKind.Rocket or ProjectileKind.Missile);
            if (aps.Heavy) return heavy;
            if (!direct && rocket && !aps.Rockets) return false;
            if (!aps.Direct && direct && !lobbed) return false;
            if (!direct && lobbedShell)
            {
                if (aps.Shells <= 0f) return false;
                shell = true;
            }
            return true;
        }

        private bool TryIntercept(Projectile p)
        {
            var weapon = p.Weapon;
            var kind = weapon.Projectile;
            // Prompt 19 C.1: in the air only a tiered craft's own point defence guards it (its lasers take the SAMs and
            // fighters' missiles flying at it); nothing else intercepts a round aimed at an aircraft.
            var guarded = EntityId.None;
            if (p.TargetFlying)
            {
                if (!_world.TryGetVehicle(p.Target, out var craft) || craft.Def.Tiers == null || craft.Aps == null) return false;
                guarded = craft.Id;
            }
            // Every system takes missiles, drones and direct-fire rockets; a point-defence laser
            // artillery rockets too, a C-RAM a share of the shells.
            // Prompt 15 C: never a beam (energy hits at once) nor a bullet.
            if (weapon.Beam || weapon.DamageType == DamageType.Energy) return false;
            // Prompt 29 S05: a round flagged never interceptable (Gungnir's rail round) goes through everything.
            if (weapon.Interceptable == false) return false;
            var direct = weapon.Guided || weapon.Glides || (kind == ProjectileKind.Rocket && weapon.MinRange <= 0f);
            var rocket = kind == ProjectileKind.Rocket;
            var shell = kind == ProjectileKind.Shell && weapon.Indirect;
            if (!direct && !rocket && !shell && !IsHeavyMissile(weapon)) return false;
            // Lobbed from afar: a drone, or a rocket or missile with a minimum range (artillery, a ballistic missile).
            var lobbed = kind == ProjectileKind.Drone || weapon.Glides || (weapon.MinRange > 0f && kind is ProjectileKind.Rocket or ProjectileKind.Missile);
            // A heavy missile (cruise or ballistic): the only thing a PAC-3's interceptors take (DECISIONS 19T).
            var heavy = IsHeavyMissile(weapon);
            var mark = _world.TryGetTarget(p.Target, out var target) && target.IsAlive ? target.Position : p.AimPoint;
            // Prompt 32 L4, the point-defence stacking rule: a round is offered to ONE system only, the nearest that may take
            // it and has an interceptor left (ties by id); there is no second try on the same round, and a round a gun point
            // defence has engaged or let through is not offered again. Systems that overlap add reach and interceptors,
            // never a second chance. A dome takes what comes through (DomeSystem).
            if (p.PdPassed || p.EngagedBy.IsValid) return false;
            Vehicle? v = null;
            var bestD = float.MaxValue;
            foreach (var c in _world.VehicleList)
            {
                var a = c.Aps;
                // A boss's protection system stops with its parts (prompt 16: the Behemoth's, the Tempest's laser, the hovercraft's CIWS).
                // Play-test 13 (lane C): a vehicle APS activation still open takes this round too, charges left or not.
                var volleyOpen = c.Def.InterceptionMode == InterceptionMode.SelfAps && c.ApsVolleyUntil >= _world.Time;
                if (a == null || !c.IsAlive || c.Team == p.OwnerTeam || (c.ApsCharges <= 0 && !volleyOpen) || c.Stunned || c.ApsOff) continue;
                // Play-test 5: a gun point defence (the C-RAM) takes rounds in flight with a burst, never as they land.
                if (a.Burst > 0f) continue;
                if (guarded.IsValid && c.Id != guarded) continue;
                var d2 = Vector2.DistanceSquared(c.Position, mark);
                if (d2 > a.Radius * a.Radius) continue;
                // Prompt 15 C.6: a point-defence laser is an energy weapon: smoke round it or its mark blinds it.
                if (a.Laser && (_world.Strikes.InSmoke(c.Position) || _world.Strikes.InSmoke(mark))) continue;
                if (a.Heavy && !heavy) continue;
                // Prompt 29 S07 (D7): a vehicle's own APS takes guided missiles, drones and direct-fire rockets only, and
                // never a round flagged apsEligible=false.
                if (c.Def.InterceptionMode == InterceptionMode.SelfAps &&
                    (weapon.ApsEligible == false || !(direct || kind == ProjectileKind.Drone))) continue;
                if (!a.Heavy && !direct && rocket && !a.Rockets) continue;
                if (!a.Heavy && !a.Direct && direct && !lobbed) continue;
                if (!a.Heavy && !direct && shell && a.Shells <= 0f) continue;
                if (v != null && (d2 > bestD || (d2 == bestD && c.Id.Value > v.Id.Value))) continue;
                v = c;
                bestD = d2;
            }
            if (v == null) return false;
            var aps = v.Aps!;
            p.PdPassed = true;
            // Its share of the shells: one roll, by the one system the round was offered to.
            if (!aps.Heavy && !direct && shell && _world.Random.NextDouble() >= aps.Shells) return false;
            // Prompt 16: a ship's CIWS with its fire-control radar broken misses now and then.
            if (v.ApsMiss > 0f && _world.Random.NextDouble() < v.ApsMiss)
            {
                v.ApsCharges--;
                if (aps.Reload > 0f) v.ApsReload = 0f;
                return false;
            }
            // Play-test 13 (lane C): a vehicle's hard-kill APS fires one activation at everything arriving together (a Trophy
            // or Afganit volley): the first round spends the charge and opens the activation; rounds reaching the vehicle
            // within ApsVolleySeconds join it free. To balance it, its interceptors come back ApsRechargeScale times slower
            // (AbilitySystem): the real systems' weak point is the reload, not the kill.
            var selfAps = v.Def.InterceptionMode == InterceptionMode.SelfAps;
            var joins = selfAps && v.ApsVolleyUntil >= _world.Time;
            if (!joins)
            {
                v.ApsCharges--;
                // A launcher reloaded whole starts its reload again at every launch.
                if (aps.Reload > 0f) v.ApsReload = 0f;
                v.ApsLeft = !v.ApsLeft;
                if (selfAps) v.ApsVolleyUntil = _world.Time + SimTunables.Weapons.Countermeasures.ApsVolleySeconds;
            }
            // The interceptor meets the round a few metres out, on the side it came from; an
            // interceptor missile flies out and meets it short of its mark.
            var from = _world.TryGetVehicle(p.Owner, out var shooter) ? shooter.Position : mark + SimMath.Forward(v.Heading) * 10f;
            if (aps.Missiles)
            {
                var back = from - mark;
                var meet = back.LengthSquared() > 0.01f ? mark + Vector2.Normalize(back) * MathF.Min(10f, back.Length() * 0.5f) : mark;
                _world.Emit(SimEvent.Intercept(v, weapon, meet, v.ApsLeft));
                return true;
            }
            var toward = from - v.Position;
            toward = toward.LengthSquared() > 0.01f ? Vector2.Normalize(toward) : SimMath.Forward(v.Heading);
            _world.Emit(SimEvent.Intercept(v, weapon, v.Position + toward * (v.Def.HullBound + 3f), v.ApsLeft));
            return true;
        }

        /// <summary>
        /// Area damage with linear falloff. Weapon splash spares the shooter's team; blasts
        /// from <see cref="Teams.Environment"/> (cook-offs, fuel) hurt everyone.
        /// </summary>
        public void Splash(Vector2 at, float radius, float damage, DamageType type, int sourceTeam, EntityId exclude,
            EntityId attacker = default, bool airborne = false, in HitInfo info = default, float edgeRadius = 0f, float edgeShare = 0.4f)
        {
            // Prompt 26 B.3: a two-layer blast: full damage within the core (radius), edgeShare of it out to edgeRadius.
            var reach = edgeRadius > radius ? edgeRadius : radius;
            foreach (var v in _world.VehicleList)
            {
                // A blast on the ground cannot reach aircraft, and an airburst does not reach the ground.
                if (!v.IsAlive || v.Id == exclude || v.Flying != airborne) continue;
                if (sourceTeam != Teams.Environment && v.Team == sourceTeam) continue;
                if (Reaches(v, at, reach)) Blame(v, attacker, sourceTeam);
                ApplyFalloff(v, at, radius, damage, type, info.At(at), edgeRadius, edgeShare);
            }
            if (airborne) return;
            foreach (var prop in _world.PropList)
            {
                if (!prop.IsAlive || prop.Id == exclude) continue;
                ApplyFalloff(prop, at, radius, damage, type, info.At(at), edgeRadius, edgeShare);
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
            // Prompt 28 appendix: a ceasefire faction takes nothing from another side's fire, strikes or splash.
            if (_world.Ceasefire(hit.Team, target.Team)) return 0f;
            // Prompt 31 L4: the same for one vehicle of a ceasefire faction (a sworn column on a side that still fights).
            if (target is Vehicle { Sworn: true } sworn && hit.Team != sworn.Team) return 0f;
            // Recon: the first hit between the player and the enemy is the alarm.
            if (!_world.Alarm && target is Vehicle && target.Team is 0 or 1 && hit.Team is 0 or 1 && hit.Team != target.Team) _world.RaiseAlarm();
            var raw = hit.Kind is HitKind.Burn or HitKind.Redirect;
            var damage = raw ? amount : amount * HitMultiplier(target, type, hit);
            // Prompt 21 E.2 / F.4: the Sandbox's hit report (null in play: nothing is worked out for it).
            var report = _world.HitLog != null && target is Vehicle;
            var penShare = raw ? 1f : _lastPen;
            var face = _lastFace;
            if (!(damage > 0f))
            {
                if (report) _world.ReportHit((Vehicle)target, 0f, type, face, penShare, hit);
                return 0f;
            }
            // Prompt 15 C.6: a beam through smoke (round the target or the shooter) is mostly scattered.
            if (!raw && type == DamageType.Energy && (_world.Strikes.InSmoke(target.Position) ||
                (hit.Attacker != null && _world.Strikes.InSmoke(hit.Attacker.Position)))) damage *= 1f - SmokeEnergyCut;
            if (hit.Attacker != null && !raw) damage *= _world.Gear.Outgoing(hit.Attacker, target, hit);
            // Prompt 22 F: the attacking side's commander (Titan's wounded, Captain Kerr's exposed targets).
            if (!raw) damage *= _world.CommanderOutgoing(hit.Attacker, hit.Team, target);
            if (hit.Attacker != null && hit.Weapon != null && !raw) damage *= BonusFor(hit.Weapon, hit.Attacker, target, _world.Time);
            // Play-test 6 (DECISIONS 21G): a boss's air defence hits aircraft harder (its rank's airDamage).
            if (!raw && hit.Attacker is { Def: { RankDef: { } firing } } && target is Vehicle { Flying: true }) damage *= firing.AirDamage;
            // A gun pit down in its hole takes much less (a thermobaric blast reaches half into it).
            if (target is Vehicle { Lowered: true } pit && pit.Def.Hidden is { } hide) damage *= 1f - hide.Cut * (Thermobaric(hit) ? 0.5f : 1f);

            switch (target)
            {
                case Vehicle vehicle:
                {
                    var dealt = HitVehicle(vehicle, damage, type, hit);
                    if (report) _world.ReportHit(vehicle, dealt, type, face, penShare, hit);
                    // Prompt 15 C.4: fire burns on: a share of what got through, over a few seconds (fires add up).
                    if (type == DamageType.Fire && dealt > 0f && vehicle.IsAlive && hit.Kind is HitKind.Direct or HitKind.Splash or HitKind.Strike)
                        _world.Status.Burn(vehicle, dealt * FireAfterburn / FireBurnSeconds, FireBurnSeconds, hit.Team, hit.Attacker?.Id ?? default, stack: true);
                    return dealt;
                }
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
                // A belly plate (the armoured bulldozer's) takes part of a mine's blast.
                if (hit.Kind == HitKind.Mine) damage *= vehicle.Def.MineArmor;
                if (vehicle.ShieldUp) damage *= 1f - vehicle.ShieldAmount;
                if (vehicle.GraceUntil > now) damage *= 0.2f;
                // Hull-down only shields from direct fire: shells, rockets and bombs from above still land.
                if (type is DamageType.Kinetic or DamageType.ShapedCharge && !hit.Indirect && _world.IsEntrenched(vehicle))
                    damage *= 1f - SimWorld.EntrenchReduction;
                // Prompt 25 F2 batch A: a blast wall before a tower, a troop shelter over the vehicles round it.
                damage *= _world.Works.CoverFactor(vehicle, type, hit);
                damage *= _world.Gear.Incoming(vehicle, type, hit);
                if (!(damage > 0f)) return 0f;
                // Prompt 17 C: a shield dome over it takes the hit first (not energy, not a mine; one dome at a time).
                damage = _world.Domes.Absorb(vehicle, damage, type, hit);
                if (!(damage > 0f)) return 0f;
                if (!(hit.Projectile?.Tandem ?? false)) damage = _world.Status.Absorb(vehicle, damage);
                damage = _world.Gear.AbsorbOverheal(vehicle, damage);
                if (vehicle.Gear != null) damage = _world.Gear.Soak(vehicle, damage);
                damage = _world.Gear.Redirect(vehicle, damage, hit);
            }
            if (!(damage > 0f)) return 0f;
            // A boss's parts: a direct hit on one hurts the part; the body is shut while its lock holds;
            // a boring boss just out of the ground takes more.
            if (vehicle.ExposedUntil > now) damage *= vehicle.Def.Burrow?.ExposedTaken ?? 1f;
            // Prompt 18: a big attack that exposes it (the Spectre low and slow, the carrier's bomb doors open).
            damage *= vehicle.BigTaken;
            // Play-test 6 (DECISIONS 21G): a boss takes a share of strikes and bombs, and only so much of them in a window.
            if (vehicle.Def.RankDef is { } rank && StrikeLike(hit)) damage = CapStrike(vehicle, damage, rank, now);
            if (vehicle.HasParts)
            {
                var part = hit.Kind == HitKind.Direct && hit.Projectile is { Part: >= 0 } shot && !vehicle.IsPartBroken(shot.Part) ? shot.Part : -1;
                if (part >= 0)
                {
                    var lost = _world.Bosses.DamagePart(vehicle, part, damage, hit);
                    if (lost > 0f) _world.Emit(SimEvent.Damage(vehicle, lost));
                    return lost;
                }
                if (vehicle.BodyLocked && hit.Kind != HitKind.Redirect) return 0f;
            }
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
            // Prompt 32 L7: Showdown's anti-snipe on an HQ (and its sudden-death count of the damage the HQs take).
            if (_world.HqDamageRule != null && vehicle.Def.Static && vehicle.Def.Fort == null && !vehicle.Def.Wall) damage = _world.HqDamageRule(vehicle, hit, damage);
            if (!(damage > 0f)) return 0f;
            vehicle.Hp = MathF.Max(0f, vehicle.Hp - damage);
            DamageLog?.Invoke(hit.Attacker, vehicle, damage, hit.Kind, hit.Weapon);
            if (phaseReached) _world.Abilities.BeginPhase(vehicle);
            // A firing-range target takes the hit (its bar shows it) but never goes down.
            if (vehicle.Unkillable) vehicle.Hp = MathF.Max(vehicle.Hp, vehicle.MaxHp * 0.25f);
            _world.Emit(SimEvent.Damage(vehicle, damage));
            if (vehicle.Gear != null) _world.Gear.AfterDamaged(vehicle, type, hit);
            if (!vehicle.IsAlive) OnVehicleDestroyed(vehicle, hit);
            return damage;
        }

        /// <summary>Play-test 6: a called strike, or a bomb (its blast too), or a strike's bomblet.</summary>
        internal static bool StrikeLike(in HitInfo hit) =>
            hit.Kind == HitKind.Strike || hit.Weapon is { Projectile: ProjectileKind.Bomb } || (hit.Kind == HitKind.Splash && hit.Weapon == null && hit.Attacker == null);

        /// <summary>
        /// Play-test 6 (DECISIONS 21G): a boss's rank takes its share of a strike or a bomb; within its window at most its
        /// cap of its health goes that way, and past the cap only a fifth (by default) gets through.
        /// </summary>
        internal static float CapStrike(Vehicle boss, float damage, BossRankDef rank, double now)
        {
            damage *= rank.StrikeTaken;
            if (rank.StrikeCap <= 0f || !(damage > 0f)) return damage;
            if (now - boss.StrikeWindowAt > rank.StrikeWindow)
            {
                boss.StrikeWindowAt = now;
                boss.StrikeWindowTaken = 0f;
            }
            var room = MathF.Max(0f, rank.StrikeCap * boss.MaxHp - boss.StrikeWindowTaken);
            if (damage > room) damage = room + (damage - room) * rank.StrikeOver;
            boss.StrikeWindowTaken += damage;
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
            for (var k = _collapsing.Count - 1; k >= 0; k--)
            {
                var (due, fallen) = _collapsing[k];
                if (due > _world.Time) continue;
                _collapsing.RemoveAt(k);
                _world.Grid.RemoveBlocker(fallen.Position, fallen.Width, fallen.Depth, SimWorld.ObstacleClearance);
                _world.RebuildLanesNow();
            }
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
                // Prompt 15 B.3: a bomblet comes down on the roof with its own penetration; any other blast (a
                // cook-off, a fuel tank, equipment's) throws fragments at the face turned to it.
                info = pending.Pen >= 0f ? info.WithPen(pending.Pen, pending.Top) : info.WithPen(Armour.FragmentPenetration, top: false);
                Splash(pending.Position, pending.Explosion.Radius, pending.Explosion.Damage, DamageType.HighExplosive,
                    pending.Team, EntityId.None, pending.Attacker?.Id ?? default, false, info, pending.Explosion.Edge, pending.Explosion.EdgeShare);
            }
        }

        /// <summary>A blast from equipment (Volatile Fuel Tanks, Uplink Barrage) that spares its own side, after <paramref name="delay"/> seconds.</summary>
        internal void Queue(Vector2 at, ExplosionDef blast, double delay, int team, Vehicle? attacker, HitKind kind, EntityId source = default) =>
            _pending.Add(new PendingExplosion(_world.Time + delay, at, blast, source, team, attacker, kind));

        private static bool Reaches(IDamageable target, Vector2 at, float radius) =>
            Vector2.Distance(target.Position, at) - target.Radius <= radius;

        private void ApplyFalloff(IDamageable target, Vector2 at, float radius, float damage, DamageType type, in HitInfo info,
            float edgeRadius = 0f, float edgeShare = 0.4f)
        {
            var edgeDistance = MathF.Max(0f, Vector2.Distance(target.Position, at) - target.Radius);
            // Prompt 26 B.3: two flat layers, no falloff inside either: the core at full damage, the edge at its share.
            if (edgeRadius > radius)
            {
                if (edgeDistance > edgeRadius) return;
                Apply(target, edgeDistance <= radius ? damage : damage * edgeShare, type, info);
                return;
            }
            if (edgeDistance > radius) return;
            // Prompt 15 C.3: a thermobaric blast's pressure falls off half as much.
            var edge = Thermobaric(info) ? (1f + EdgeFalloff) * 0.5f : EdgeFalloff;
            var scale = 1f - (1f - edge) * SimMath.Clamp01(edgeDistance / radius);
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
                new ExplosionDef(charge.Damage, MathF.Max(1f, charge.SplashRadius), 0f, charge.ImpactTier), car.Id, car.Team,
                pen: charge.Penetration, top: false));
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
            // Prompt 26 B.7: a slug that goes through at most PierceMax vehicles in all (the one aimed at counts): the nearest first.
            var capped = p.Weapon.PierceMax > 0;
            if (capped) _pierced.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Team == p.OwnerTeam || v.Id == struck || v.Id == p.Owner) continue;
                var offset = v.Position - from;
                var t = Vector2.Dot(offset, along);
                if (t < 0f || t > length + 12f) continue;
                if ((offset - along * t).Length() > v.Radius + 1.2f) continue;
                if (capped)
                {
                    _pierced.Add((t, v));
                    continue;
                }
                Blame(v, p.Owner, p.OwnerTeam);
                Apply(v, p.Weapon.Damage * p.DamageScale, p.Weapon.DamageType, info);
                PierceVictims++;
            }
            if (!capped) return;
            _pierced.Sort((a, b) => a.t != b.t ? a.t.CompareTo(b.t) : a.v.Id.Value.CompareTo(b.v.Id.Value));
            var room = p.Weapon.PierceMax - (struck.IsValid ? 1 : 0);
            for (var k = 0; k < _pierced.Count && k < room; k++)
            {
                var hit = _pierced[k].v;
                Blame(hit, p.Owner, p.OwnerTeam);
                Apply(hit, p.Weapon.Damage * p.DamageScale, p.Weapon.DamageType, info);
                PierceVictims++;
            }
        }

        private readonly List<(float t, Vehicle v)> _pierced = new();

        /// <summary>Vehicles hit by a piercing round beyond the one it was aimed at, over the battle (balance measurements).</summary>
        internal int PierceVictims { get; private set; }

        /// <summary>Prompt 15 C.4: the share of a fire hit's damage that burns on afterwards, and over how long.</summary>
        internal static float FireAfterburn => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageSystem.FireAfterburn;
        internal static float FireBurnSeconds => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageSystem.FireBurnSeconds;

        /// <summary>Prompt 15 C.6: the share of a beam's damage smoke scatters.</summary>
        internal static float SmokeEnergyCut => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageSystem.SmokeEnergyCut;

        private void OnVehicleDestroyed(Vehicle vehicle, in HitInfo hit)
        {
            // Prompt 32 L3: a wall segment turns to rubble (its ground opens at the next tick).
            if (vehicle.Def.Wall) _world.Walls.OnDestroyed(vehicle);
            var speed = vehicle.Speed;
            vehicle.ClearPath();
            vehicle.Speed = 0f;
            // Play-test 14 (lane J): its burning hulk (a ship going down) stays solid where it stopped until it is gone.
            _world.Wrecks.Add(vehicle, _world.Time);
            // Who gets the kill: the vehicle whose round it was, else whoever hit it last (recently).
            var killer = hit.Attacker;
            if (killer == null && vehicle.LastAttacker.IsValid && _world.Time - vehicle.LastHitTime <= 10.0 &&
                _world.TryGetVehicle(vehicle.LastAttacker, out var last)) killer = last;
            if (killer != null && killer.Team == vehicle.Team) killer = null;
            // Prompt 34 L7: an aircraft's crash is planned now (where and when it hits the ground) and told to the view on the
            // loss event, so its wreck can fly a show path that lands on that point at that time.
            var crash = vehicle.Flying ? CrashPlan(vehicle, speed) : default;
            _world.Emit(vehicle.Flying ? SimEvent.VehicleLost(vehicle, crash.At, crash.Fall) : SimEvent.VehicleLost(vehicle));
            // Prompt 19 E.7: a tiered boss's last radio line.
            if (vehicle.Def.Tiers?.RadioFor("down") is { } down) _world.Emit(SimEvent.RadioMessage(down, vehicle.Team));
            _world.Economy.OnVehicleDestroyed(vehicle, killer);
            if (vehicle.Def.DeathExplosion != null && !vehicle.Detonated) Schedule(vehicle.Position, vehicle.Def.DeathExplosion, vehicle.Id);
            if (vehicle.Flying) ScheduleCrash(vehicle, crash);
            _world.Gear.OnDeath(vehicle, killer);
        }

        /// <summary>
        /// A shot-down aircraft comes down where its momentum carries it, as its wreck falls on
        /// screen (VehicleView: a fall under 11 m/s² for aeroplanes, 7 for helicopters, the drift
        /// fading as it goes), and crushes whatever is under it, either side's: a blast sized by
        /// how heavy it was.
        /// </summary>
        private void ScheduleCrash(Vehicle vehicle, (Vector2 At, float Fall) crash) =>
            _pending.Add(new PendingExplosion(_world.Time + crash.Fall, crash.At, CrashBlast(vehicle.Def), vehicle.Id));

        /// <summary>
        /// Prompt 34 L7: where and after how long a shot-down aircraft hits the ground (the same numbers as before: a fall
        /// under 11 m/s² for aeroplanes and 7 for helicopters, carried on by its momentum, the drift fading).
        /// </summary>
        internal (Vector2 At, float Fall) CrashPlan(Vehicle vehicle, float speed)
        {
            var def = vehicle.Def;
            var fall = MathF.Sqrt(2f * MathF.Max(1f, vehicle.Height) / (def.FixedWing ? 11f : 7f));
            var fade = def.FixedWing ? 0.35f : 0.5f;
            var glide = MathF.Min(fall, 1f / fade);
            var carry = 0.8f * speed * (glide - 0.5f * fade * glide * glide);
            var forward = SimMath.Forward(vehicle.Heading);
            return (_world.ClampToMap(vehicle.Position + forward * carry), fall);
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
            // A wall that topples opens its ground once it is down (see PropDef.Collapse).
            if (prop.Def.BlocksMovement && prop.Def.Collapse > 0f) _collapsing.Add((_world.Time + prop.Def.Collapse, prop));
            else if (prop.Def.BlocksMovement)
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
                Vehicle? attacker = null, HitKind kind = HitKind.None, float pen = -1f, bool top = true)
            {
                Pen = pen;
                Top = top;
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

            /// <summary>A bomblet's penetration (it comes down on the roof), a car bomb's charge's; -1 for an ordinary blast.</summary>
            public float Pen { get; }

            /// <summary>It comes down on the roof (a bomblet), else it strikes the face turned to it.</summary>
            public bool Top { get; }
        }
    }
}
