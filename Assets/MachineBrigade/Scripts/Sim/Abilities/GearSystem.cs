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
    /// <summary>What a trait-modified shot carries: its damage multiplier, a heavy round's burst and a tandem warhead.</summary>
    internal struct ShotMods
    {
        public float Scale;
        public float ExtraSplash;
        public bool Tandem;

        public static ShotMods Plain => new() { Scale = 1f };
    }

    /// <summary>
    /// Equipment in battle: sets a vehicle up from its <see cref="VehicleBoost"/> (stat lines,
    /// weapon copies, modules), runs the timers and auras of its traits every step, and answers the
    /// hooks the other systems call: a shot leaving (<see cref="Shot"/>), a round striking
    /// (<see cref="OnDirectHit"/>), damage going out and coming in (<see cref="Outgoing"/>,
    /// <see cref="Incoming"/>), a vehicle destroyed (<see cref="OnDeath"/>). Every proc the player
    /// should see is announced as a <see cref="SimEventKind.TraitProc"/>, at most once per vehicle
    /// every two seconds. Everything is deterministic: timers, counters and thresholds, no chance.
    /// </summary>
    internal sealed class GearSystem
    {
        /// <summary>Seconds between two proc words over one vehicle.</summary>
        public const double ProcGap = 2.0;

        private const float AuraInterval = 0.5f;

        private readonly SimWorld _world;
        private readonly List<Vehicle> _guardians = new();
        private readonly List<Vehicle> _radars = new();
        private float _auraTimer;

        private static readonly SkillDef EmpBurst = new("emp_payload", SkillKind.Emp, SkillTrigger.Always, 0f, 0f, 2f, 0f, 10f, 0, null, true);

        public GearSystem(SimWorld world) => _world = world;

        // ================================================================== setup

        /// <summary>Gives a vehicle entering the battle what its equipment carries beyond the plain multipliers.</summary>
        public void Equip(Vehicle v, in VehicleBoost b)
        {
            if (b.Stats == null && b.Traits == null && b.Special < SpecialModule.TrophyAps && b.Special != SpecialModule.SmokeDischarger) return;
            var g = new GearState { SpawnedAt = _world.Time };
            if (b.Stats != null) Array.Copy(b.Stats, g.Stats, Math.Min(b.Stats.Length, g.Stats.Length));
            if (b.Traits != null)
                foreach (var t in b.Traits) g.Add(t);
            v.Gear = g;
            // High-explosive filler on a gun that has no blast: it hits light vehicles harder instead.
            if (v.Def.Weapon.SplashRadius <= 0f && g.Stat(StatId.Splash) > 0f)
                g.Stats[(int)StatId.DamageVsLight] += g.Stat(StatId.Splash) * 0.55f;
            v.TurnFactor = 1f + g.Stat(StatId.TurnRate);
            v.TurretFactor = 1f + g.Stat(StatId.TurretRate);
            v.VisionFactor = 1f + g.Stat(StatId.Vision);
            v.CaptureFactor = 1f + g.Stat(StatId.CaptureRate);
            v.RepairReceived = 1f + g.Stat(StatId.RepairReceived);
            TuneWeapons(v, g);
            if (g.Has(TraitId.ReactiveBlocks)) g.Blocks = (int)g.Trait(TraitId.ReactiveBlocks).A;
            if (g.Has(TraitId.AblativeLayer)) g.Ablative = -1f;
            if (g.Has(TraitId.SetSwarm)) g.Drone = DroneFor(v, g);
            var now = _world.Time;
            switch (v.Special)
            {
                case SpecialModule.TrophyAps:
                {
                    var charges = Math.Max(1, (int)MathF.Round(b.SpecialPower));
                    var recharge = b.SpecialPower2 > 0f ? b.SpecialPower2 : 25f;
                    var own = v.Def.Aps;
                    v.Aps = own == null ? new ApsDef(6f, charges, recharge) : new ApsDef(MathF.Max(6f, own.Radius), own.Charges + charges, MathF.Min(own.Recharge, recharge));
                    v.ApsCharges = v.Aps.Charges;
                    break;
                }
                case SpecialModule.MineDispenser when v.Def.Mines == null && !v.Flying:
                    v.MineLayer = new MineLayerDef(b.SpecialPower2 > 0f ? b.SpecialPower2 : 20f, Math.Max(1, (int)MathF.Round(b.SpecialPower)), MineBlast(g), 2.2f);
                    v.NextMineAt = now + 3.0;
                    break;
                case SpecialModule.DroneEscort:
                    g.Drone ??= DroneFor(v, g);
                    g.ModuleReady = now + 4.0;
                    break;
                case SpecialModule.UplinkBarrage:
                    g.ModuleReady = now + 6.0;
                    break;
            }
        }

        /// <summary>Copies the weapons the equipment changes (the catalog's stay as they are).</summary>
        private static void TuneWeapons(Vehicle v, GearState g)
        {
            for (var i = 0; i < v.Arms.Length; i++)
            {
                var w = v.Arms[i];
                float range = w.Range, cooldown = w.Cooldown, speed = w.ProjectileSpeed, splash = w.SplashRadius, spread = w.Spread, interval = w.BurstInterval;
                var targets = w.Targets;
                var ammo = w.Ammo;
                var reload = w.Reload;
                var cluster = w.Cluster;
                if (i == 0)
                {
                    range *= 1f + g.Stat(StatId.Range);
                    speed *= 1f + g.Stat(StatId.ProjectileSpeed);
                    spread *= MathF.Max(0.1f, 1f - g.Stat(StatId.Spread));
                    if (splash > 0f) splash *= 1f + g.Stat(StatId.Splash);
                    if (w.Burst > 1) interval *= MathF.Max(0.3f, 1f - g.Stat(StatId.SalvoInterval));
                    if (g.Has(TraitId.ClusterWarhead) && w.Indirect)
                    {
                        var count = (int)g.Trait(TraitId.ClusterWarhead).A + (cluster?.Count ?? 0);
                        var bomblet = cluster?.Bomblet ?? new ExplosionDef(MathF.Max(4f, w.Damage * 0.08f), 2.5f, 0f, ExplosionTier.Small);
                        cluster = new ClusterDef(Math.Max(1, count), MathF.Max(6f, cluster?.Radius ?? 0f), bomblet);
                    }
                }
                else
                {
                    if (g.Stat(StatId.SecondaryFireRate) > 0f) cooldown /= 1f + g.Stat(StatId.SecondaryFireRate);
                    if (g.Has(TraitId.SkywardPintle) && w.Projectile == ProjectileKind.Bullet && (targets & TargetLayers.Air) == 0) targets |= TargetLayers.Air;
                }
                if (ammo > 0)
                {
                    var more = g.Stat(StatId.Magazine);
                    if (more > 0f) ammo = Math.Max(ammo + (more >= 0.08f ? 1 : 0), (int)MathF.Round(ammo * (1f + more)));
                    var faster = g.Stat(StatId.MagazineReload) + (g.Has(TraitId.HotSwap) ? g.Trait(TraitId.HotSwap).A : 0f);
                    if (faster > 0f) reload = w.MagazineReload * MathF.Max(0.3f, 1f - faster);
                }
                var changed = range != w.Range || cooldown != w.Cooldown || speed != w.ProjectileSpeed || splash != w.SplashRadius || spread != w.Spread ||
                              interval != w.BurstInterval || targets != w.Targets || ammo != w.Ammo || reload != w.Reload || cluster != w.Cluster;
                if (changed) v.Arms[i] = w.Tuned(range, cooldown, speed, splash, spread, interval, targets, ammo, reload, cluster);
            }
        }

        /// <summary>A Mine Dispenser's charge: three fifths of a mine layer's, or a stock one.</summary>
        private ExplosionDef MineBlast(GearState g)
        {
            ExplosionDef? stock = null;
            foreach (var def in _world.Catalog.Vehicles.Values)
                if (def.Mines != null)
                {
                    stock = def.Mines.Blast;
                    break;
                }
            var damage = (stock?.Damage * 0.6f ?? 260f) * (1f + g.Stat(StatId.SummonPower));
            return new ExplosionDef(damage, MathF.Min(stock?.Radius ?? 4f, 4f), 0f, stock?.Tier ?? ExplosionTier.Large);
        }

        /// <summary>The kamikaze drone this vehicle launches: a catalog drone's look, 60 % of one main-gun shot.</summary>
        private WeaponDef DroneFor(Vehicle v, GearState g)
        {
            var damage = MathF.Max(40f, v.Def.Weapon.Damage * 0.6f) * (1f + g.Stat(StatId.SummonPower));
            WeaponDef? template = null;
            if (_world.Catalog.Weapons.TryGetValue("fpv_swarm", out var fpv)) template = fpv;
            else
                foreach (var w in _world.Catalog.Weapons.Values)
                    if (w.Projectile == ProjectileKind.Drone)
                    {
                        template = w;
                        break;
                    }
            if (template == null)
                return new WeaponDef("gear_drone", DamageType.ArmorPiercing, damage, 1f, 80f, 0f, 26f, 2f, 0f, ExplosionTier.Medium, ProjectileKind.Drone);
            return template.Tuned(80f, 1f, template.ProjectileSpeed, MathF.Min(template.SplashRadius, 2.5f), 0f, template.BurstInterval, TargetLayers.Ground,
                0, 0f, null, damage, 1);
        }

        private static bool Has(Vehicle v, TraitId id) => v.Gear != null && v.Gear.Has(id);

        /// <summary>Crew Drills and the like: trait and module cooldowns are this share of their nominal length.</summary>
        private static float CooldownFactor(GearState g) => MathF.Max(0.5f, 1f - g.Stat(StatId.Cooldowns));

        // ================================================================== procs

        public void Proc(Vehicle v, TraitId id) => Proc(v, GearKeys.Trait(id));

        public void Proc(Vehicle v, SpecialModule module) => Proc(v, GearKeys.Module(module));

        public void Proc(Vehicle v, string key)
        {
            var g = v.Gear;
            if (g == null) return;
            var now = _world.Time;
            if (now - g.LastProcAt < ProcGap) return;
            g.LastProcAt = now;
            _world.Emit(SimEvent.Proc(v, key));
        }

        // ================================================================== every step

        public void Step(float dt)
        {
            var now = _world.Time;
            _auraTimer -= dt;
            var aura = _auraTimer <= 0f;
            if (aura) _auraTimer += AuraInterval;
            _guardians.Clear();
            _radars.Clear();
            var list = _world.VehicleList;
            for (var i = 0; i < list.Count; i++)
            {
                var v = list[i];
                if (!v.IsAlive) continue;
                var speed = 1f - StatusSystem.SlowShare(v, now);
                var fire = 1f;
                v.RangeFactor = 1f;
                if (v.Gear != null) StepGear(v, v.Gear, now, aura, ref speed, ref fire);
                v.SpeedGear = speed;
                v.FireGear = fire;
            }
        }

        private void StepGear(Vehicle v, GearState g, double now, bool aura, ref float speed, ref float fire)
        {
            var stillFor = v.IsMoving ? 0.0 : now - v.StillSince;
            var underFire = now - v.LastHitTime < 1.0;
            var cd = CooldownFactor(g);
            if (g.Has(TraitId.GuardianLink)) _guardians.Add(v);
            if (g.Has(TraitId.CounterBatteryRadar)) _radars.Add(v);

            // ---------------------------------------------------------- fire rate and speed
            if (g.Has(TraitId.HullDownCrew) && stillFor >= 2.0) fire *= 1f + g.Trait(TraitId.HullDownCrew).A;
            if (g.KillFireUntil > now) fire *= 1f + g.Trait(TraitId.KillReload).A;
            if (aura && g.Stat(StatId.TransitSpeed) > 0f)
                g.Calm = _world.FindNearestEnemy(v, v.Def.VisionRange * v.VisionFactor, requireVisible: true) == null;
            if (g.Calm && g.Stat(StatId.TransitSpeed) > 0f) speed *= 1f + g.Stat(StatId.TransitSpeed);
            if (g.ScootUntil > now) speed *= 1f + g.Trait(TraitId.ShootAndScoot).B;
            if (g.HitRunUntil > now) speed *= 1f + g.Trait(TraitId.SetHitAndRun).A;
            if (g.Has(TraitId.RapidDeployment) && now - g.SpawnedAt < g.Trait(TraitId.RapidDeployment).A) speed *= 1.4f;

            // ---------------------------------------------------------- stances
            if (g.Has(TraitId.SiegeAnchor))
            {
                if (g.Anchored && v.HasPath)
                {
                    g.Anchored = false;
                    g.UnanchorUntil = now + 1.0;
                }
                else if (!g.Anchored && !v.HasPath && stillFor >= 3.0 && g.UnanchorUntil <= now)
                {
                    g.Anchored = true;
                    Proc(v, TraitId.SiegeAnchor);
                }
                if (g.Anchored) v.RangeFactor *= 1f + g.Trait(TraitId.SiegeAnchor).B;
                // Dug in, and for a second after the order to move while the anchor comes up: no driving.
                if (g.Anchored || g.UnanchorUntil > now) speed = 0f;
            }
            if (g.Has(TraitId.GhillieMode))
            {
                var quiet = Math.Min(stillFor, now - v.LastFiredAt);
                if (g.Hidden && v.IsMoving) g.Hidden = false;
                else if (!g.Hidden && !v.IsMoving && quiet >= g.Trait(TraitId.GhillieMode).B) g.Hidden = true;
            }

            // ---------------------------------------------------------- defensive timers
            if (g.Has(TraitId.AegisBarrier) && now >= g.Ready[(int)TraitId.AegisBarrier])
            {
                var t = g.Trait(TraitId.AegisBarrier);
                var broken = v.Barrier <= 0f;
                _world.Status.AddBarrier(v, v.MaxHp * t.A);
                g.Ready[(int)TraitId.AegisBarrier] = now + t.B * cd;
                if (broken && now - g.SpawnedAt > 0.5) Proc(v, TraitId.AegisBarrier);
            }
            if (g.Has(TraitId.ReactiveBlocks))
            {
                var t = g.Trait(TraitId.ReactiveBlocks);
                if (g.Blocks < (int)t.A && now >= g.BlockAt)
                {
                    g.Blocks++;
                    g.BlockAt = now + t.B * cd;
                }
            }
            if (underFire && g.Has(TraitId.RapidResponse) && now >= g.Ready[(int)TraitId.RapidResponse])
            {
                var t = g.Trait(TraitId.RapidResponse);
                v.BarrageRate = v.BarrageUntil > now ? MathF.Max(v.BarrageRate, t.A) : t.A;
                v.BarrageUntil = now + 4.0;
                g.Ready[(int)TraitId.RapidResponse] = now + t.B * cd;
                v.RefreshEffects(now);
                Proc(v, TraitId.RapidResponse);
            }
            if (underFire && g.Has(TraitId.NitroDash) && now >= g.Ready[(int)TraitId.NitroDash] && !v.Def.Static)
            {
                var t = g.Trait(TraitId.NitroDash);
                v.OverdriveUntil = now + 3.0;
                v.OverdriveSpeed = MathF.Max(1f, t.A);
                g.Ready[(int)TraitId.NitroDash] = now + t.B * cd;
                v.RefreshEffects(now);
                Proc(v, TraitId.NitroDash);
            }
            if (g.Has(TraitId.AfterburnerReserve) && !g.AfterburnerUsed && v.Flying && v.Hp < v.MaxHp * 0.4f)
            {
                g.AfterburnerUsed = true;
                v.OverdriveUntil = now + 4.0;
                v.OverdriveSpeed = 1f + g.Trait(TraitId.AfterburnerReserve).A;
                v.FlaresUntil = Math.Max(v.FlaresUntil, now + 2.0);
                v.RefreshEffects(now);
                Proc(v, TraitId.AfterburnerReserve);
            }
            if (g.Has(TraitId.EmergencyRepairKit) && v.Hp < v.MaxHp * 0.4f && now >= g.Ready[(int)TraitId.EmergencyRepairKit])
            {
                v.Healing = v.MaxHp * g.Trait(TraitId.EmergencyRepairKit).A / 5f;
                v.HealUntil = now + 5.0;
                g.Ready[(int)TraitId.EmergencyRepairKit] = now + 30.0 * cd;
                Proc(v, TraitId.EmergencyRepairKit);
            }
            if (g.Has(TraitId.DamageControl) && now >= g.Ready[(int)TraitId.DamageControl] && _world.Status.Afflicted(v))
            {
                _world.Status.Cleanse(v, 2f);
                g.Ready[(int)TraitId.DamageControl] = now + g.Trait(TraitId.DamageControl).A * cd;
                Proc(v, TraitId.DamageControl);
            }
            if (g.Has(TraitId.EwJammer) && now >= g.Ready[(int)TraitId.EwJammer]) Jam(v, g, now, cd);
            if (g.Has(TraitId.SetSharedShield) && now >= g.Ready[(int)TraitId.SetSharedShield]) ShareShield(v, g, now);
            if (g.Has(TraitId.SetStrafingRun) && v.Flying && now >= g.Ready[(int)TraitId.SetStrafingRun])
            {
                v.FlaresUntil = Math.Max(v.FlaresUntil, now + 2.0);
                g.Ready[(int)TraitId.SetStrafingRun] = now + g.Trait(TraitId.SetStrafingRun).B;
                v.RefreshEffects(now);
            }

            // ---------------------------------------------------------- auras
            if (aura)
            {
                if (g.Has(TraitId.FieldMechanics)) FieldRepair(v, g.Trait(TraitId.FieldMechanics), now);
                if (g.Has(TraitId.AmmoCarrier)) Buff(v, StatusKind.Rearm, g.Trait(TraitId.AmmoCarrier).A, g.Trait(TraitId.AmmoCarrier).B, now);
                if (v.Special == SpecialModule.RallyHorn) Buff(v, StatusKind.Rally, v.SpecialPower, v.SpecialPower2 > 0f ? v.SpecialPower2 : 12f, now);
            }

            // ---------------------------------------------------------- modules
            switch (v.Special)
            {
                case SpecialModule.SmokeDischarger when v.SpecialPower2 > 0f && v.SmokeUsed && !g.SecondSmokeUsed && v.Hp < v.MaxHp * 0.25f:
                    g.SecondSmokeUsed = true;
                    _world.Strikes.AddSmoke(v.Team, v.Position, v.SpecialPower, 14f);
                    Proc(v, SpecialModule.SmokeDischarger);
                    break;
                case SpecialModule.FlareDispenser when now >= g.ModuleReady && _world.MissileIncoming(v.Id):
                    v.FlaresUntil = Math.Max(v.FlaresUntil, now + v.SpecialPower);
                    g.ModuleReady = now + (v.SpecialPower2 > 0f ? v.SpecialPower2 : 25f) * cd;
                    v.RefreshEffects(now);
                    Proc(v, SpecialModule.FlareDispenser);
                    break;
                case SpecialModule.DroneEscort when now >= g.ModuleReady:
                    g.ModuleReady = LaunchDrones(v, g, Math.Max(1, (int)MathF.Round(v.SpecialPower)))
                        ? now + (v.SpecialPower2 > 0f ? v.SpecialPower2 : 25f) * cd
                        : now + 1.0;
                    break;
                case SpecialModule.AegisDome when !g.DomeUsed && aura:
                    Dome(v, g, now);
                    break;
                case SpecialModule.DecoyLauncher when now >= g.ModuleReady && (_world.MissileIncoming(v.Id) || _world.RoundIncoming(v.Id)):
                    g.DecoyUntil = now + v.SpecialPower;
                    g.DecoyAt = _world.ClampToMap(v.Position - SimMath.Forward(v.Heading) * (v.Def.HullBound + 6f));
                    g.ModuleReady = now + (v.SpecialPower2 > 0f ? v.SpecialPower2 : 35f) * cd;
                    Proc(v, SpecialModule.DecoyLauncher);
                    break;
                case SpecialModule.UplinkBarrage when now >= g.ModuleReady:
                    g.ModuleReady = Barrage(v, Math.Max(1, (int)MathF.Round(v.SpecialPower)))
                        ? now + (v.SpecialPower2 > 0f ? v.SpecialPower2 : 45f) * cd
                        : now + 1.0;
                    break;
            }
        }

        /// <summary>Guided rounds aimed at allies round an EW jammer lose lock for a moment.</summary>
        private void Jam(Vehicle v, GearState g, double now, float cd)
        {
            var t = g.Trait(TraitId.EwJammer);
            var radius = t.C > 0f ? t.C : 12f;
            var threatened = false;
            foreach (var ally in _world.VehicleList)
                if (ally.IsAlive && ally.Team == v.Team && Vector2.DistanceSquared(ally.Position, v.Position) <= radius * radius && _world.MissileIncoming(ally.Id))
                {
                    threatened = true;
                    break;
                }
            if (!threatened) return;
            foreach (var ally in _world.VehicleList)
            {
                if (!ally.IsAlive || ally.Team != v.Team || Vector2.DistanceSquared(ally.Position, v.Position) > radius * radius) continue;
                ref var s = ref ally.Statuses[(int)StatusKind.Jam];
                s.Until = Math.Max(s.Until, now + t.A);
            }
            g.Ready[(int)TraitId.EwJammer] = now + t.B * cd;
            Proc(v, TraitId.EwJammer);
        }

        /// <summary>Aegis Systems' four-piece: a barrier for the weakest ally nearby (itself if alone).</summary>
        private void ShareShield(Vehicle v, GearState g, double now)
        {
            var t = g.Trait(TraitId.SetSharedShield);
            var radius = t.C > 0f ? t.C : 12f;
            Vehicle best = v;
            var bestShare = v.Hp / v.MaxHp;
            foreach (var ally in _world.VehicleList)
            {
                if (!ally.IsAlive || ally.Team != v.Team || ally == v || Vector2.DistanceSquared(ally.Position, v.Position) > radius * radius) continue;
                var share = ally.Hp / ally.MaxHp;
                if (share < bestShare)
                {
                    best = ally;
                    bestShare = share;
                }
            }
            _world.Status.AddBarrier(best, best.MaxHp * t.A);
            g.Ready[(int)TraitId.SetSharedShield] = now + t.B;
            if (now - g.SpawnedAt > 0.5) Proc(v, TraitId.SetSharedShield);
        }

        /// <summary>Field Mechanics: allies round it (not itself) that are out of combat repair a share of their health a second.</summary>
        private void FieldRepair(Vehicle v, GearTrait t, double now)
        {
            var radius = t.B > 0f ? t.B : 12f;
            foreach (var ally in _world.VehicleList)
            {
                if (!ally.IsAlive || ally == v || ally.Team != v.Team || ally.Def.Boss || ally.Hp >= ally.MaxHp) continue;
                if (now - ally.LastHitTime <= 4.0 || Vector2.DistanceSquared(ally.Position, v.Position) > radius * radius) continue;
                var amount = MathF.Min(ally.MaxHp - ally.Hp, ally.MaxHp * t.A * AuraInterval * RepairFactor(ally, now));
                if (amount <= 0f) continue;
                ally.Hp += amount;
                _world.Emit(SimEvent.RepairedBy(ally, amount));
            }
        }

        /// <summary>A buff aura (rally horn, ammunition carrier) on every ally within <paramref name="radius"/>, itself included; the strongest holds.</summary>
        private void Buff(Vehicle v, StatusKind kind, float value, float radius, double now)
        {
            foreach (var ally in _world.VehicleList)
            {
                if (!ally.IsAlive || ally.Team != v.Team || Vector2.DistanceSquared(ally.Position, v.Position) > radius * radius) continue;
                ref var s = ref ally.Statuses[(int)kind];
                s.Value = s.Until > now ? MathF.Max(s.Value, value) : value;
                s.Until = now + AuraInterval + 0.15;
            }
        }

        /// <summary>Repairs on a burning vehicle go at half rate; its equipment may make them go faster.</summary>
        public static float RepairFactor(Vehicle v, double now) =>
            v.RepairReceived * (StatusSystem.Has(v, StatusKind.Burn, now) ? 0.5f : 1f);

        /// <summary>Aegis Dome: once a life, three or more allies under fire round it and all of them (itself too) turn invulnerable.</summary>
        private void Dome(Vehicle v, GearState g, double now)
        {
            const float radius = 10f;
            var pressed = 0;
            foreach (var ally in _world.VehicleList)
                if (ally.IsAlive && ally.Team == v.Team && now - ally.LastHitTime < 1.0 && Vector2.DistanceSquared(ally.Position, v.Position) <= radius * radius)
                    pressed++;
            if (pressed < 3) return;
            g.DomeUsed = true;
            foreach (var ally in _world.VehicleList)
                if (ally.IsAlive && ally.Team == v.Team && Vector2.DistanceSquared(ally.Position, v.Position) <= radius * radius)
                    ally.ImmuneUntil = Math.Max(ally.ImmuneUntil, now + v.SpecialPower);
            Proc(v, SpecialModule.AegisDome);
        }

        /// <summary>Launches drones at the nearest visible ground enemy; false when there is none.</summary>
        private bool LaunchDrones(Vehicle v, GearState g, int count, EntityId skip = default)
        {
            var drone = g.Drone;
            if (drone == null) return false;
            var target = _world.FindNearestEnemy(v, drone.Range, requireVisible: true, layers: TargetLayers.Ground);
            if (target == null) return false;
            for (var k = 0; k < count; k++)
            {
                var origin = v.Position + SimMath.Forward(v.Heading + (k - (count - 1) * 0.5f) * 0.6f) * v.Radius;
                var travel = MathF.Max(0.3f, Vector2.Distance(origin, target.Position) / drone.ProjectileSpeed) + 0.15f * k;
                var p = new Projectile(v.Id, v.Team, drone, target.Position, target.Id, travel) { Origin = origin, Shooter = v, NoProc = true };
                _world.Combat.AddProjectile(p);
                _world.Emit(SimEvent.FiredWith(v, drone, origin, target.Position, travel, target.Id));
            }
            if (v.Special == SpecialModule.DroneEscort) Proc(v, SpecialModule.DroneEscort);
            return true;
        }

        /// <summary>Uplink Barrage: light mortar rounds walk onto its current target.</summary>
        private bool Barrage(Vehicle v, int rounds)
        {
            if (!_world.TryGetTarget(v.Target, out var target) || !target.IsAlive) return false;
            var blast = new ExplosionDef(60f * (1f + (v.Gear?.Stat(StatId.SummonPower) ?? 0f)), 4f, 0f, ExplosionTier.Medium);
            for (var k = 0; k < rounds; k++)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                var reach = 3f * MathF.Sqrt((float)_world.Random.NextDouble());
                var at = target.Position + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach;
                _world.Damage.Queue(at, blast, 1.2 + 0.35 * k, v.Team, v, HitKind.Strike, v.Id);
            }
            Proc(v, SpecialModule.UplinkBarrage);
            return true;
        }

        // ================================================================== shots

        /// <summary>
        /// A round leaves a vehicle's mount: what its traits add to it. <paramref name="pull"/> is
        /// the first round of a trigger pull (salvos count once).
        /// </summary>
        public ShotMods Shot(Vehicle v, int index, EntityId target, Vector2 aimAt, WeaponDef weapon, bool pull)
        {
            var mods = ShotMods.Plain;
            var g = v.Gear;
            if (g == null || index != 0) return mods;
            var now = _world.Time;
            var wasHidden = g.Hidden;
            if (g.Has(TraitId.GhillieMode))
            {
                if (g.Hidden && pull)
                {
                    mods.Scale *= 1f + g.Trait(TraitId.GhillieMode).A;
                    Proc(v, TraitId.GhillieMode);
                }
                g.Hidden = false;
            }
            if (g.Has(TraitId.TandemWarhead) && weapon.Projectile is ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Drone) mods.Tandem = true;
            if (g.Has(TraitId.SetHitAndRun)) g.HitRunUntil = now + 2.0;
            if (g.Has(TraitId.SetDeepStrike) && Vector2.Distance(v.Position, aimAt) > weapon.Range * 0.7f) mods.Scale *= 1f + g.Trait(TraitId.SetDeepStrike).A;
            if (g.Has(TraitId.SetGhostNet) && (wasHidden || _world.Strikes.InSmoke(v.Position))) mods.Scale *= 1f + g.Trait(TraitId.SetGhostNet).A;
            if (g.Has(TraitId.MomentumGun) && target.IsValid && g.StreakTarget == target && g.Streak > 0)
                mods.Scale *= 1f + g.Trait(TraitId.MomentumGun).A * Math.Min(5, g.Streak);
            if (!pull) return mods;

            g.Shots++;
            if (g.Has(TraitId.OpeningSalvo) && target.IsValid && target != g.LastTarget)
            {
                mods.Scale *= 1f + g.Trait(TraitId.OpeningSalvo).A;
                Proc(v, TraitId.OpeningSalvo);
            }
            if (target.IsValid) g.LastTarget = target;
            if (g.Has(TraitId.ShootAndScoot))
            {
                if (!v.IsMoving && now - v.StillSince <= 1.5 && g.ScootShotAt < v.StillSince)
                {
                    mods.Scale *= 1f + g.Trait(TraitId.ShootAndScoot).A;
                    g.ScootShotAt = now;
                    Proc(v, TraitId.ShootAndScoot);
                }
                g.ScootUntil = now + 2.0;
            }
            // Every Nth trigger pull is a heavy round: Overpressure Chamber, Hammerfall's Heavy Round,
            // or both together (every third, not stacking).
            var every = 0;
            var bonus = 0f;
            var key = TraitId.None;
            if (g.Has(TraitId.OverpressureChamber))
            {
                every = Math.Max(2, (int)g.Trait(TraitId.OverpressureChamber).A);
                bonus = 0.5f;
                key = TraitId.OverpressureChamber;
            }
            if (g.Has(TraitId.SetHeavyRound))
            {
                var t = g.Trait(TraitId.SetHeavyRound);
                every = every > 0 ? 3 : Math.Max(2, (int)t.A);
                bonus = MathF.Max(bonus, t.B);
                key = TraitId.SetHeavyRound;
            }
            if (every > 0 && g.Shots % every == 0)
            {
                mods.Scale *= 1f + bonus;
                mods.ExtraSplash = 4f;
                Proc(v, key);
            }
            return mods;
        }

        /// <summary>Extra rounds a trigger pull adds (Twin Feed, Stormfront's Strafing Run) and the damage of each round against a plain one.</summary>
        public int ExtraRounds(Vehicle v, WeaponDef weapon, out float perRound)
        {
            perRound = 1f;
            var g = v.Gear;
            if (g == null) return 0;
            var rounds = weapon.Burst;
            float total = rounds;
            var extra = 0;
            if (g.Has(TraitId.TwinFeed))
            {
                extra++;
                total = rounds * (1f + g.Trait(TraitId.TwinFeed).A);
                Proc(v, TraitId.TwinFeed);
            }
            if (g.Has(TraitId.SetStrafingRun) && ++g.Salvos % Math.Max(2, (int)g.Trait(TraitId.SetStrafingRun).A) == 0)
            {
                extra += rounds;
                total += rounds;
                Proc(v, TraitId.SetStrafingRun);
            }
            if (extra == 0) return 0;
            perRound = total / (rounds + extra);
            return extra;
        }

        /// <summary>Stormfront on a machine gun: every Nth round hits twice as hard instead of a second salvo.</summary>
        public float MachineGunRound(Vehicle v)
        {
            var g = v.Gear;
            if (g == null || !g.Has(TraitId.SetStrafingRun)) return 1f;
            return ++g.Salvos % Math.Max(2, (int)g.Trait(TraitId.SetStrafingRun).A) == 0 ? 2f : 1f;
        }

        /// <summary>Counter-battery radar: enemy artillery firing near a radar is revealed to the radar's side.</summary>
        public void Fired(Vehicle shooter, WeaponDef weapon)
        {
            if (weapon.MinRange <= 0f || _radars.Count == 0) return;
            var now = _world.Time;
            foreach (var radar in _radars)
            {
                if (!radar.IsAlive || radar.Team == shooter.Team || radar.Team < 0 || radar.Team > 30) continue;
                var t = radar.Gear!.Trait(TraitId.CounterBatteryRadar);
                if (Vector2.Distance(radar.Position, shooter.Position) > t.B) continue;
                ref var s = ref shooter.Statuses[(int)StatusKind.Reveal];
                if (s.Until <= now) s.Stacks = 0;
                s.Stacks |= 1 << radar.Team;
                s.Value = MathF.Max(s.Until > now ? s.Value : 0f, t.A);
                s.Until = Math.Max(s.Until, now + t.C);
                Proc(radar, TraitId.CounterBatteryRadar);
            }
        }

        /// <summary>A secondary gun given an anti-aircraft ring (Skyward Pintle) hits aircraft at this share.</summary>
        public float PintleScale(Vehicle v, int index, bool targetFlying)
        {
            if (index == 0 || !targetFlying || v.Gear == null || !v.Gear.Has(TraitId.SkywardPintle)) return 1f;
            return v.Def.Mounts[index].Weapon.CanTarget(true) ? 1f : v.Gear.Trait(TraitId.SkywardPintle).A;
        }

        /// <summary>Spread against its nominal value for this shot (Laser Rangefinder, Gun Stabiliser, Fire-Control Computer; Kestrel's evasion on the target).</summary>
        public float SpreadFactor(Vehicle v, int index, IDamageable? target, float reach)
        {
            var f = 1f;
            var g = v.Gear;
            var moving = target is Vehicle tv && tv.IsMoving;
            if (g != null && index == 0)
            {
                var cut = g.Stat(StatId.SpreadLong) * Math.Clamp(reach, 0f, 1f) + (v.IsMoving ? g.Stat(StatId.SpreadMoving) : 0f);
                if (moving && g.Has(TraitId.FireControlComputer)) cut += g.Trait(TraitId.FireControlComputer).A;
                if (cut > 0f) f *= MathF.Max(0.1f, 1f - cut);
            }
            if (moving && target is Vehicle evader && evader.Gear != null && evader.Gear.HitRunUntil > _world.Time)
                f *= 1f + evader.Gear.Trait(TraitId.SetHitAndRun).B;
            return f;
        }

        /// <summary>Fire-Control Computer: where to aim at a moving target so the shell meets it.</summary>
        public Vector2 Lead(Vehicle v, int index, IDamageable target, Vector2 aimAt, WeaponDef weapon)
        {
            if (index != 0 || v.Gear == null || !v.Gear.Has(TraitId.FireControlComputer) || target is not Vehicle tv || !tv.IsMoving) return aimAt;
            var travel = Vector2.Distance(v.Position, aimAt) / MathF.Max(1f, weapon.ProjectileSpeed);
            return aimAt + SimMath.Forward(tv.Heading) * tv.Speed * travel;
        }

        /// <summary>How far a weapon reaches against this target, against its range: a siege anchor, and a mark for artillery.</summary>
        public float Reach(Vehicle v, IDamageable target, WeaponDef weapon)
        {
            var f = v.RangeFactor;
            if (weapon.MinRange > 0f && target is Vehicle tv)
            {
                ref var mark = ref tv.Statuses[(int)StatusKind.Mark];
                if (mark.Until > _world.Time && mark.Team == v.Team) f *= 1f + mark.Extra;
            }
            return f;
        }

        /// <summary>Ironclad's Bulwark: dug in, it draws the fire of enemies round it.</summary>
        public bool Taunts(Vehicle target, Vehicle shooter) =>
            target.Gear != null && target.Gear.Has(TraitId.SetBulwark) && !target.IsMoving && _world.Time - target.StillSince >= 2.0 &&
            Vector2.DistanceSquared(target.Position, shooter.Position) <= 25f * 25f;

        /// <summary>Hot Swap or an ammunition carrier nearby: the magazine reloads on the move too, and faster.</summary>
        public float ReloadRate(Vehicle v, out bool onTheMove)
        {
            var now = _world.Time;
            onTheMove = Has(v, TraitId.HotSwap);
            ref var rearm = ref v.Statuses[(int)StatusKind.Rearm];
            if (rearm.Until > now)
            {
                onTheMove = true;
                return 1f + rearm.Value;
            }
            return 1f;
        }

        // ================================================================== hits

        /// <summary>A round from a vehicle with equipment struck what it was aimed at.</summary>
        public void OnDirectHit(Projectile p, IDamageable target, float dealt)
        {
            var v = p.Shooter!;
            var g = v.Gear!;
            if (!p.Main) return;
            var weapon = p.Weapon;
            if (target is Vehicle tv)
            {
                if (g.Has(TraitId.MomentumGun))
                {
                    if (g.StreakTarget == tv.Id) g.Streak = Math.Min(5, g.Streak + 1);
                    else
                    {
                        g.StreakTarget = tv.Id;
                        g.Streak = 1;
                    }
                    if (g.Streak == 5) Proc(v, TraitId.MomentumGun);
                }
                if (dealt > 0f && tv.IsAlive)
                {
                    var firestorm = g.Has(TraitId.SetFirestorm);
                    if (g.Has(TraitId.IncendiaryRounds) || (firestorm && weapon.DamageType == DamageType.Fire))
                    {
                        var seconds = weapon.Projectile == ProjectileKind.Flame ? 6f : 4f;
                        var share = g.Has(TraitId.IncendiaryRounds) ? g.Trait(TraitId.IncendiaryRounds).A : 0.1f;
                        _world.Status.Burn(tv, dealt * share * (1f + g.Stat(StatId.BurnDamage)) / seconds, seconds, v.Team, v.Id, firestorm);
                        if (g.Has(TraitId.IncendiaryRounds)) Proc(v, TraitId.IncendiaryRounds);
                    }
                    if (g.Has(TraitId.ShredderRounds))
                    {
                        _world.Status.Shred(tv, g.Trait(TraitId.ShredderRounds).A, 5f);
                        if (tv.Statuses[(int)StatusKind.Shred].Stacks >= 5) Proc(v, TraitId.ShredderRounds);
                    }
                    if (g.Has(TraitId.SuppressionRounds))
                    {
                        _world.Status.Slow(tv, g.Trait(TraitId.SuppressionRounds).A, 2f);
                        Proc(v, TraitId.SuppressionRounds);
                    }
                    if (g.Has(TraitId.LaserDesignator))
                    {
                        var t = g.Trait(TraitId.LaserDesignator);
                        _world.Status.Mark(tv, t.A, t.B, v.Team, 0.1f);
                        Proc(v, TraitId.LaserDesignator);
                    }
                }
            }
            if (g.Has(TraitId.RicochetShells) && target is Vehicle struck && (weapon.Cooldown >= 0.35f || weapon.Burst > 1)) Ricochet(p, v, g, struck);
        }

        /// <summary>Ricochet Shells: the round bounces on to the nearest other enemy close by, at a share of its damage.</summary>
        private void Ricochet(Projectile p, Vehicle v, GearState g, Vehicle struck)
        {
            var t = g.Trait(TraitId.RicochetShells);
            Vehicle? next = null;
            var best = t.B * t.B;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other == struck || other.Team == v.Team || other.Invulnerable || other.Flying != struck.Flying) continue;
                var d = Vector2.DistanceSquared(other.Position, struck.Position);
                if (d > best) continue;
                best = d;
                next = other;
            }
            if (next == null) return;
            var travel = MathF.Max(0.05f, MathF.Sqrt(best) / MathF.Max(1f, p.Weapon.ProjectileSpeed));
            var bounce = new Projectile(p.Owner, p.OwnerTeam, p.Weapon, next.Position, next.Id, travel, next.Flying)
            {
                Origin = struck.Position, DamageScale = p.DamageScale * t.A, Shooter = v, NoProc = true, Tandem = p.Tandem,
            };
            _world.Combat.AddProjectile(bounce);
            Proc(v, TraitId.RicochetShells);
        }

        /// <summary>A round aimed at this vehicle is drawn off: an EW jammer's cover, Spectre's first lost lock, a decoy.</summary>
        public bool Lure(Vehicle v, Projectile p, out Vector2 at)
        {
            at = default;
            var now = _world.Time;
            var weapon = p.Weapon;
            if (weapon.Guided && v.Statuses[(int)StatusKind.Jam].Until > now)
            {
                at = v.Position + p.Miss;
                return true;
            }
            var g = v.Gear;
            if (g == null) return false;
            if (weapon.Guided && g.Has(TraitId.SetGhostNet) && !g.GhostNetUsed)
            {
                g.GhostNetUsed = true;
                at = v.Position + p.Miss;
                Proc(v, TraitId.SetGhostNet);
                return true;
            }
            if (g.DecoyUntil > now && (weapon.Guided || weapon.Indirect))
            {
                at = g.DecoyAt;
                return true;
            }
            return false;
        }

        /// <summary>Damage going out: a multiplier from the attacker's equipment and effects, and marks on the target.</summary>
        public float Outgoing(Vehicle attacker, IDamageable target, in HitInfo hit)
        {
            var m = 1f;
            var now = _world.Time;
            var g = attacker.Gear;
            if (g != null)
            {
                m += target.Armor switch
                {
                    ArmorClass.Light => g.Stat(StatId.DamageVsLight),
                    ArmorClass.Heavy => g.Stat(StatId.DamageVsHeavy),
                    ArmorClass.Air => g.Stat(StatId.DamageVsAir),
                    _ => g.Stat(StatId.DamageVsStructure),
                };
                if (g.Has(TraitId.Executioner) && target is Vehicle && target.Hp < target.MaxHp * 0.3f)
                {
                    m += g.Trait(TraitId.Executioner).A;
                    if (hit.Kind == HitKind.Direct) Proc(attacker, TraitId.Executioner);
                }
                if (g.Has(TraitId.TandemWarhead) && target.Armor == ArmorClass.Heavy && hit.Weapon?.Projectile is ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Drone)
                    m += g.Trait(TraitId.TandemWarhead).A;
                if (g.CrownStacks > 0) m += g.Trait(TraitId.DarkCrown).A * g.CrownStacks;
            }
            if (target is Vehicle victim && hit.Known)
            {
                ref var mark = ref victim.Statuses[(int)StatusKind.Mark];
                if (mark.Until > now && mark.Team == hit.Team) m += mark.Value;
                // Counter-battery: artillery firing on artillery a radar has revealed.
                ref var reveal = ref victim.Statuses[(int)StatusKind.Reveal];
                if (reveal.Until > now && hit.Team >= 0 && hit.Team < 31 && (reveal.Stacks & (1 << hit.Team)) != 0 && (hit.Weapon?.MinRange ?? 0f) > 0f &&
                    victim.Def.Weapon.MinRange > 0f)
                    m += reveal.Value;
            }
            ref var rally = ref attacker.Statuses[(int)StatusKind.Rally];
            if (rally.Until > now) m += rally.Value;
            return m;
        }

        /// <summary>Damage coming in: a multiplier from the victim's resistances, stances and effects (0: the hit bounced).</summary>
        public float Incoming(Vehicle v, DamageType type, in HitInfo hit)
        {
            var now = _world.Time;
            var m = 1f;
            if (hit.Kind != HitKind.Burn)
            {
                ref var shred = ref v.Statuses[(int)StatusKind.Shred];
                if (shred.Until > now && shred.Stacks > 0) m *= 1f + shred.Value * shred.Stacks;
                ref var burn = ref v.Statuses[(int)StatusKind.Burn];
                if (burn.Flag && burn.Until > now) m *= 1.1f;
            }
            var g = v.Gear;
            if (g == null) return m;
            var cut = g.Stat(StatId.ResistKinetic + (int)type) + Adapted(g, type, now);
            if (hit.Kind == HitKind.Burn) return m * (1f - Math.Clamp(cut, 0f, 0.6f));
            var weapon = hit.Weapon;
            if (weapon != null && weapon.Projectile is ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Drone) cut += g.Stat(StatId.ResistRocket);
            if (hit.Indirect) cut += g.Stat(StatId.ResistIndirect);
            if (hit.Kind == HitKind.Mine)
            {
                if (g.Has(TraitId.MineSweep) && now >= g.Ready[(int)TraitId.MineSweep])
                {
                    g.Ready[(int)TraitId.MineSweep] = now + 30.0;
                    Proc(v, TraitId.MineSweep);
                    return 0f;
                }
                cut += g.Stat(StatId.ResistMine);
            }
            if (hit.Kind == HitKind.Direct && !hit.Indirect && g.Stat(StatId.ResistFrontal) > 0f && Frontal(v, hit.Origin)) cut += g.Stat(StatId.ResistFrontal);
            if (g.Anchored) cut += g.Trait(TraitId.SiegeAnchor).A;
            if (g.Has(TraitId.SetBulwark) && !v.IsMoving && now - v.StillSince >= 2.0) cut += g.Trait(TraitId.SetBulwark).A;
            if (g.Has(TraitId.RapidDeployment) && now - g.SpawnedAt < g.Trait(TraitId.RapidDeployment).A) cut += 0.2f;
            m *= 1f - Math.Clamp(cut, 0f, 0.7f);
            if (hit.Kind != HitKind.Direct) return m;

            // Armour traits that work hit by hit.
            if (g.Has(TraitId.ReactiveBlocks) && g.Blocks > 0 && !(hit.Projectile?.Tandem ?? false) &&
                (type == DamageType.ArmorPiercing || weapon?.Projectile is ProjectileKind.Rocket or ProjectileKind.Missile))
            {
                if (g.Blocks >= (int)g.Trait(TraitId.ReactiveBlocks).A) g.BlockAt = now + g.Trait(TraitId.ReactiveBlocks).B * CooldownFactor(g);
                g.Blocks--;
                m *= 0.5f;
                Proc(v, TraitId.ReactiveBlocks);
            }
            if (g.Has(TraitId.AngledGlacis) && type is DamageType.ArmorPiercing or DamageType.Kinetic && !hit.Indirect &&
                ++g.GlacisHits % Math.Max(2, (int)g.Trait(TraitId.AngledGlacis).A) == 0)
            {
                Proc(v, TraitId.AngledGlacis);
                return 0f;
            }
            return m;
        }

        private static float Adapted(GearState g, DamageType type, double now)
        {
            var i = (int)type;
            return g.Has(TraitId.AdaptivePlating) && g.AdaptUntil[i] > now ? g.Adapt[i] * g.Trait(TraitId.AdaptivePlating).A : 0f;
        }

        /// <summary>A hit from within 30 degrees of the nose (Frontal Wedge).</summary>
        private static bool Frontal(Vehicle v, Vector2 from)
        {
            var to = from - v.Position;
            if (to.LengthSquared() < 0.01f) return false;
            return MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(to) - v.Heading)) <= MathF.PI / 6f;
        }

        /// <summary>Ablative Layer: the first share of each life's damage is halved while the layer lasts.</summary>
        public float Soak(Vehicle v, float damage)
        {
            var g = v.Gear!;
            if (!g.Has(TraitId.AblativeLayer)) return damage;
            if (g.Ablative < 0f) g.Ablative = v.MaxHp * g.Trait(TraitId.AblativeLayer).A;
            if (g.Ablative <= 0f) return damage;
            var within = MathF.Min(damage, g.Ablative);
            g.Ablative -= within;
            if (g.Ablative <= 0f) Proc(v, TraitId.AblativeLayer);
            return damage - within * 0.5f;
        }

        /// <summary>Guardian Link: a heavy vehicle nearby takes a share of the damage to a light one.</summary>
        public float Redirect(Vehicle v, float damage, in HitInfo hit)
        {
            if (_guardians.Count == 0 || v.Flying || v.Def.Static || v.Armor != ArmorClass.Light || hit.Kind == HitKind.Redirect) return damage;
            foreach (var guardian in _guardians)
            {
                if (!guardian.IsAlive || guardian == v || guardian.Team != v.Team) continue;
                if (Vector2.DistanceSquared(guardian.Position, v.Position) > 100f) continue;
                var share = damage * guardian.Gear!.Trait(TraitId.GuardianLink).A;
                _world.Damage.TakeOver(guardian, share, hit);
                Proc(guardian, TraitId.GuardianLink);
                return damage - share;
            }
            return damage;
        }

        /// <summary>Unbreakable: the first killing blow of a life leaves it on 1 HP, untouchable for a moment.</summary>
        public bool Survives(Vehicle v)
        {
            var g = v.Gear!;
            if (!g.Has(TraitId.Unbreakable) || g.UnbreakableUsed || v.Dummy) return false;
            g.UnbreakableUsed = true;
            v.ImmuneUntil = _world.Time + g.Trait(TraitId.Unbreakable).A;
            Proc(v, TraitId.Unbreakable);
            return true;
        }

        /// <summary>After a hit landed: Adaptive Plating learns the damage type.</summary>
        public void AfterDamaged(Vehicle v, DamageType type, in HitInfo hit)
        {
            var g = v.Gear!;
            if (!g.Has(TraitId.AdaptivePlating) || hit.Kind is HitKind.Redirect or HitKind.Burn) return;
            var now = _world.Time;
            var i = (int)type;
            g.Adapt[i] = g.AdaptUntil[i] > now ? Math.Min(4, g.Adapt[i] + 1) : 1;
            g.AdaptUntil[i] = now + 6.0;
            if (g.Adapt[i] == 4) Proc(v, TraitId.AdaptivePlating);
        }

        // ================================================================== deaths

        /// <summary>A vehicle was destroyed: its killer's kill traits, its own death traits, and Dark Crowns nearby.</summary>
        public void OnDeath(Vehicle victim, Vehicle? killer)
        {
            var now = _world.Time;
            if (killer?.Gear is { } kg && killer.IsAlive)
            {
                if (kg.Has(TraitId.KillReload))
                {
                    var state = killer.Weapons[0];
                    state.Cooldown = 0f;
                    if (state.Ammo == 0)
                    {
                        state.Ammo = killer.Arms[0].Ammo;
                        state.ReloadLeft = 0f;
                    }
                    kg.KillFireUntil = now + 4.0;
                    Proc(killer, TraitId.KillReload);
                }
                if (kg.Has(TraitId.SalvageTeam))
                {
                    var share = kg.Trait(TraitId.SalvageTeam).A;
                    foreach (var ally in _world.VehicleList)
                    {
                        if (!ally.IsAlive || ally.Team != killer.Team || ally.Hp >= ally.MaxHp) continue;
                        var self = ally == killer;
                        if (!self && Vector2.DistanceSquared(ally.Position, killer.Position) > 100f) continue;
                        var amount = MathF.Min(ally.MaxHp - ally.Hp, ally.MaxHp * share * (self ? 1f : 0.5f) * RepairFactor(ally, now));
                        if (amount <= 0f) continue;
                        ally.Hp += amount;
                        _world.Emit(SimEvent.RepairedBy(ally, amount));
                    }
                    Proc(killer, TraitId.SalvageTeam);
                }
                if (kg.Has(TraitId.SetSwarm) && now >= kg.Ready[(int)TraitId.SetSwarm] && LaunchDrones(killer, kg, 1))
                {
                    kg.Ready[(int)TraitId.SetSwarm] = now + kg.Trait(TraitId.SetSwarm).A;
                    Proc(killer, TraitId.SetSwarm);
                }
            }

            if (victim.Gear is { } g && g.Has(TraitId.VolatileFuelTanks))
            {
                var t = g.Trait(TraitId.VolatileFuelTanks);
                _world.Damage.Queue(victim.Position, new ExplosionDef(victim.MaxHp * t.A, t.B > 0f ? t.B : 8f, 0f, ExplosionTier.Large), 0.15, victim.Team,
                    victim, HitKind.Splash, victim.Id);
                _world.Emit(SimEvent.Proc(victim, GearKeys.Trait(TraitId.VolatileFuelTanks)));
            }
            if (victim.Special == SpecialModule.EmpPayload) EmpPayload(victim, now);

            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v == victim || v.Gear == null || !v.Gear.Has(TraitId.DarkCrown)) continue;
                if (Vector2.DistanceSquared(v.Position, victim.Position) > 25f * 25f) continue;
                var t = v.Gear.Trait(TraitId.DarkCrown);
                v.Gear.CrownStacks = Math.Min(5, v.Gear.CrownStacks + 1);
                v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * t.B);
                Proc(v, TraitId.DarkCrown);
            }

            // Vulcan's Firestorm: the fire on a dying enemy jumps to the nearest of its friends.
            ref var burn = ref victim.Statuses[(int)StatusKind.Burn];
            if (burn.Flag && burn.Until > now)
            {
                Vehicle? next = null;
                var best = 36f;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v == victim || v.Team != victim.Team) continue;
                    var d = Vector2.DistanceSquared(v.Position, victim.Position);
                    if (d > best) continue;
                    best = d;
                    next = v;
                }
                if (next != null) _world.Status.Burn(next, burn.Value, 4f, burn.Team, burn.Source, true);
            }
        }

        /// <summary>EMP Payload: the dying vehicle stuns enemy ground vehicles round it.</summary>
        private void EmpPayload(Vehicle victim, double now)
        {
            var radius = victim.SpecialPower2 > 0f ? victim.SpecialPower2 : 10f;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == victim.Team || other.Team < 0 || other.Flying || other.Def.Boss) continue;
                if (Vector2.Distance(other.Position, victim.Position) > radius + other.Def.HullRadius) continue;
                _world.Status.Stun(other, now + victim.SpecialPower);
                other.ClearPath();
                other.Speed = 0f;
                other.RefreshEffects(now);
            }
            _world.Emit(SimEvent.SkillUsed(victim, EmpBurst));
            _world.Emit(SimEvent.Proc(victim, GearKeys.Module(SpecialModule.EmpPayload)));
        }
    }
}
