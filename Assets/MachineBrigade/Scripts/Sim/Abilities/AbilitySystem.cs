#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Everything vehicles do besides driving and shooting:
    /// <list type="bullet">
    /// <item>limited ammunition, restocked at home and by engineers;</item>
    /// <item>support auras (engineers repair and re-arm, jammers scramble guided weapons);</item>
    /// <item>mines, laid by mine layers and set off by enemy ground vehicles;</item>
    /// <item>skills of elite units and bosses (shield, repair, smoke, overdrive, barrage, flares,
    /// summons, EMP), used automatically when their trigger is met.</item>
    /// </list>
    /// </summary>
    internal sealed class AbilitySystem
    {
        /// <summary>Supply at home: within this distance of the team's rally point, vehicles re-arm.</summary>
        private const float HomeReach = 20f;

        /// <summary>Seconds per round when re-arming at home.</summary>
        private const float HomeRearmSeconds = 3f;

        /// <summary>Auras tick this often (seconds).</summary>
        private const float AuraInterval = 0.5f;

        /// <summary>Enemies see a mine only this close to one of their vehicles.</summary>
        private const float MineSpotting = 9f;

        private readonly SimWorld _world;
        private readonly List<Mine> _mines = new();
        private readonly List<Vehicle> _jammers = new();
        private readonly List<(string def, int team, Vector2 at, float heading)> _summons = new();
        private float _auraTimer;

        /// <summary>Skill triggers are checked four times a second: each may search for enemies.</summary>
        private float _skillTimer;
        private int _nextMine = 1;

        public AbilitySystem(SimWorld world) => _world = world;

        public IReadOnlyList<Mine> Mines => _mines;

        public void Step(float dt)
        {
            var now = _world.Time;
            _jammers.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                v.RefreshEffects(now);
                if (v.Def.Jammer > 0f) _jammers.Add(v);
                // Standing still (entrenchment counts from here).
                if (Vector2.DistanceSquared(v.Position, v.StillAt) > 0.04f)
                {
                    v.StillAt = v.Position;
                    v.StillSince = now;
                }
                // Home zone: a vehicle left alone for 3 s by its own camp repairs 2 % a second.
                if (_world.HomeZones && !v.Def.Static && v.Hp < v.MaxHp && now - v.LastHitTime > 3.0 &&
                    _world.TryGetRally(v.Team, out var home) && Vector2.DistanceSquared(v.Position, home) < SimWorld.HomeRadius * SimWorld.HomeRadius)
                    v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * 0.02f * dt);
                // Active protection reloads one interceptor at a time.
                var aps = v.Def.Aps;
                if (aps != null && v.ApsCharges < aps.Charges && (v.ApsReload += dt) >= aps.Recharge)
                {
                    v.ApsCharges++;
                    v.ApsReload = 0f;
                }
            }

            _auraTimer -= dt;
            var auraTick = _auraTimer <= 0f;
            if (auraTick) _auraTimer += AuraInterval;
            _skillTimer -= dt;
            var skillTick = _skillTimer <= 0f;
            if (skillTick) _skillTimer += 0.25f;

            _summons.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                if (skillTick && v.Def.Skills.Count > 0) UseSkills(v, now);
                if (v.Def.Mines != null) LayMines(v, now);
                if (auraTick)
                {
                    RearmAtHome(v);
                    if (v.Def.RepairAura != null || v.Def.RearmAura != null) Support(v);
                }
                // Upgrades: self-repair out of combat, and smoke dischargers at half health.
                if (v.Regen > 0f && v.Hp < v.MaxHp && now - v.LastHitTime > 4.0) v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * v.Regen * dt);
                if (v.Special == SpecialModule.SmokeDischarger && !v.SmokeUsed && v.Hp < v.MaxHp * 0.5f)
                {
                    v.SmokeUsed = true;
                    _world.Strikes.AddSmoke(v.Team, v.Position, v.SpecialPower, 14f);
                }
                if (v.Healing > 0f && v.HealUntil > now)
                {
                    var amount = MathF.Min(v.MaxHp - v.Hp, v.Healing * dt);
                    if (amount > 0f) v.Hp += amount;
                }
            }
            // Loaned escorts fly home when their time is up (no wreck, no kill).
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.ExpiresAt <= now)
                {
                    v.Hp = 0f;
                    _world.Emit(SimEvent.Retired(v));
                }
            // Summons join after the loop so the vehicle list is not changed while it is read.
            foreach (var (def, team, at, heading) in _summons) _world.SpawnVehicle(def, team, at, heading);

            TriggerMines(now);
        }

        /// <summary>Whether <paramref name="point"/> lies inside a jammer of a team hostile to <paramref name="team"/>.</summary>
        public bool Jammed(Vector2 point, int team)
        {
            foreach (var j in _jammers)
                if (j.IsAlive && j.Team != team && Vector2.DistanceSquared(j.Position, point) < j.Def.Jammer * j.Def.Jammer)
                    return true;
            return false;
        }

        // ------------------------------------------------------------------ ammunition and support

        private void RearmAtHome(Vehicle v)
        {
            if (!v.NeedsAmmo || !_world.TryGetRally(v.Team, out var home)) return;
            if (Vector2.Distance(v.Position, home) > HomeReach) return;
            v.RearmProgress += AuraInterval / HomeRearmSeconds;
            TopUp(v);
        }

        private void Support(Vehicle engineer)
        {
            var repair = engineer.Def.RepairAura;
            var rearm = engineer.Def.RearmAura;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != engineer.Team || v.Flying || v.Def.Static) continue;
                var distance = Vector2.Distance(v.Position, engineer.Position);
                if (repair != null && distance <= repair.Radius && !v.Def.Boss && v.Hp < v.MaxHp)
                {
                    var amount = MathF.Min(v.MaxHp - v.Hp, v.MaxHp * repair.Rate * AuraInterval);
                    v.Hp += amount;
                    _world.Emit(SimEvent.RepairedBy(v, amount));
                }
                if (rearm != null && distance <= rearm.Radius && v.NeedsAmmo)
                {
                    v.RearmProgress += AuraInterval / rearm.Rate;
                    TopUp(v);
                }
            }
        }

        /// <summary>
        /// Hands out whole rounds to part-empty magazines as the re-arm progress fills; an empty
        /// one being reloaded in place goes three times as fast instead (the whole magazine comes
        /// back at once, so it never trickles back one round at a time and runs dry again).
        /// </summary>
        private static void TopUp(Vehicle v)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
                if (v.Weapons[i].Ammo == 0 && v.Weapons[i].ReloadLeft > 0f)
                    v.Weapons[i].ReloadLeft = MathF.Max(0.0001f, v.Weapons[i].ReloadLeft - AuraInterval * 2f); // the reload itself finishes it
            while (v.RearmProgress >= 1f && PartEmpty(v))
            {
                v.RearmProgress -= 1f;
                for (var i = 0; i < v.Weapons.Length; i++)
                {
                    var max = v.Def.Mounts[i].Weapon.Ammo;
                    if (max > 0 && v.Weapons[i].Ammo > 0 && v.Weapons[i].Ammo < max) v.Weapons[i].Ammo++;
                }
            }
            if (!PartEmpty(v)) v.RearmProgress = 0f;
        }

        /// <summary>Some limited weapon has rounds left but is not full (empty ones reload in place).</summary>
        private static bool PartEmpty(Vehicle v)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var max = v.Def.Mounts[i].Weapon.Ammo;
                if (max > 0 && v.Weapons[i].Ammo > 0 && v.Weapons[i].Ammo < max) return true;
            }
            return false;
        }

        // ------------------------------------------------------------------ mines

        private void LayMines(Vehicle v, double now)
        {
            var def = v.Def.Mines!;
            if (v.Flying || now < v.NextMineAt) return;
            v.NextMineAt = now + def.Interval;
            var mine = 0;
            foreach (var m in _mines)
            {
                if (!m.IsAlive || m.Layer != v.Id) continue;
                mine++;
                // Spread them out: no two within a few metres.
                if (Vector2.DistanceSquared(m.Position, v.Position) < 25f) return;
            }
            if (mine >= def.Max) return;
            // Drop it behind the vehicle, clear of the hull.
            var at = v.Position - SimMath.Forward(v.Heading) * (v.Def.HullHalf + v.Def.HullRadius + 0.8f);
            if (!_world.Map.Contains(at) || !_world.Grid.IsWalkable(at)) return;
            var laid = new Mine(new EntityId(_nextMine++), v.Team, v.Id, at, def, now + 2.0);
            _mines.Add(laid);
            _world.Emit(SimEvent.MineLaid(laid));
        }

        private void TriggerMines(double now)
        {
            for (var i = _mines.Count - 1; i >= 0; i--)
            {
                var m = _mines[i];
                if (!m.IsAlive)
                {
                    _mines.RemoveAt(i);
                    continue;
                }
                var mask = 1 << m.Team;
                var armed = now >= m.ArmedAt;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Flying || v.Team == m.Team || v.Team < 0) continue;
                    var distance = Vector2.Distance(v.Position, m.Position);
                    if (distance < MineSpotting) mask |= 1 << v.Team;
                    if (!armed || distance > m.Def.Trigger + v.Def.HullRadius) continue;
                    m.IsAlive = false;
                    break;
                }
                m.VisibleToMask = mask;
                if (m.IsAlive) continue;
                _world.Emit(SimEvent.MineDetonated(m));
                _world.Emit(SimEvent.Exploded(m.Position, m.Def.Blast, m.Id));
                _world.Damage.Splash(m.Position, m.Def.Blast.Radius, m.Def.Blast.Damage, DamageType.ArmorPiercing, m.Team, EntityId.None);
                _mines.RemoveAt(i);
            }
        }

        // ------------------------------------------------------------------ skills

        private void UseSkills(Vehicle v, double now)
        {
            var skills = v.Def.Skills;
            for (var i = 0; i < skills.Count; i++)
            {
                var skill = skills[i];
                if (v.SkillReadyAt[i] > now || (skill.Once && v.SkillUsed[i])) continue;
                if (!Triggered(v, skill, now)) continue;
                v.SkillReadyAt[i] = now + skill.Cooldown;
                v.SkillUsed[i] = true;
                Fire(v, skill, now);
                v.RefreshEffects(now);
                _world.Emit(SimEvent.SkillUsed(v, skill));
            }
        }

        private bool Triggered(Vehicle v, SkillDef skill, double now) => skill.Trigger switch
        {
            SkillTrigger.Always => true,
            SkillTrigger.HpBelow => v.Hp / v.MaxHp < skill.Threshold,
            SkillTrigger.UnderFire => now - v.LastHitTime < 1.0,
            SkillTrigger.EnemyInRange => _world.FindNearestEnemy(v, skill.Radius > 0f ? skill.Radius : v.Def.Weapon.Range,
                requireVisible: true) != null,
            SkillTrigger.MissileIncoming => _world.MissileIncoming(v.Id),
            _ => false,
        };

        private void Fire(Vehicle v, SkillDef skill, double now)
        {
            var until = now + skill.Duration;
            switch (skill.Kind)
            {
                case SkillKind.Repair:
                    v.Healing = skill.Duration > 0f ? v.MaxHp * skill.Amount / skill.Duration : 0f;
                    v.HealUntil = until;
                    if (skill.Duration <= 0f) v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * skill.Amount);
                    break;
                case SkillKind.Shield:
                    v.ShieldUntil = until;
                    v.ShieldAmount = Math.Clamp(skill.Amount, 0f, 0.95f);
                    break;
                case SkillKind.Smoke:
                    _world.Strikes.AddSmoke(v.Team, v.Position, skill.Radius > 0f ? skill.Radius : 8f, skill.Duration);
                    break;
                case SkillKind.Overdrive:
                    v.OverdriveUntil = until;
                    v.OverdriveSpeed = MathF.Max(1f, skill.Amount);
                    break;
                case SkillKind.Barrage:
                    v.BarrageUntil = until;
                    v.BarrageRate = MathF.Max(1f, skill.Amount);
                    break;
                case SkillKind.Flares:
                    v.FlaresUntil = until;
                    break;
                case SkillKind.Summon:
                    for (var k = 0; k < skill.Count; k++)
                    {
                        var angle = (k + 0.5f) * SimMath.Tau / skill.Count + v.Heading;
                        var at = _world.ClampToMap(v.Position + SimMath.Forward(angle) * (v.Def.HullBound + 5f));
                        _summons.Add((skill.Unit!, v.Team, at, v.Heading));
                    }
                    break;
                case SkillKind.Emp:
                    foreach (var other in _world.VehicleList)
                    {
                        if (!other.IsAlive || other.Team == v.Team || other.Team < 0 || other.Flying || other.Def.Boss) continue;
                        if (Vector2.Distance(other.Position, v.Position) > skill.Radius + other.Def.HullRadius) continue;
                        other.StunnedUntil = Math.Max(other.StunnedUntil, until);
                        other.ClearPath();
                        other.Speed = 0f;
                    }
                    break;
            }
        }
    }
}
