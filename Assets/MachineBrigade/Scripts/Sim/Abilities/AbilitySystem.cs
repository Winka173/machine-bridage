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
    internal sealed partial class AbilitySystem
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
                if (v.Transforming && now >= v.TransformUntil) CompletePhase(v, now);
                v.RefreshEffects(now);
                // A boss's jamming aura stops with its jammer part (prompt 16).
                if (v.Def.Jammer > 0f && !v.JammerOff) _jammers.Add(v);
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
                // Active protection reloads one interceptor at a time; a launcher reloaded whole (prompt 20 L.1, the
                // Iron Dome) gets all of them back once it has been quiet for its reload time (it restarts at each launch).
                var aps = v.Aps;
                if (aps != null && !v.ApsOff && v.ApsCharges < Math.Min(aps.Charges, v.ApsMax) && (v.ApsReload += dt) >= (aps.Reload > 0f ? aps.Reload : aps.Recharge))
                {
                    v.ApsCharges = aps.Reload > 0f ? Math.Min(aps.Charges, v.ApsMax) : v.ApsCharges + 1;
                    v.ApsReload = 0f;
                }
            }

            _auraTimer -= dt;
            var auraTick = _auraTimer <= 0f;
            if (auraTick) _auraTimer += AuraInterval;
            _skillTimer -= dt;
            var skillTick = _skillTimer <= 0f;
            if (skillTick) _skillTimer += 0.25f;

            if (auraTick)
            {
                CommandAuras();
                BaseModules();
                SlowAuras();
            }
            HideGunPits(now);
            _summons.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                if (skillTick && v.Def.Skills.Count > 0) UseSkills(v, now);
                if (skillTick && v.Def.Scoot != null) Scoot(v, now);
                if (auraTick && v.Def.Breacher) Plough(v);
                if (v.MineLayer != null) LayMines(v, now);
                if (auraTick)
                {
                    RearmAtHome(v);
                    if (v.Def.RepairAura != null || v.Def.RearmAura != null) Support(v);
                    if (v.Def.FortifyAura != null) Fortify(v);
                    // A firing-range target mends itself between volleys.
                    if (v.Unkillable) v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * 0.08f * AuraInterval);
                }
                // Upgrades: self-repair out of combat (sooner with a toolbox, part of it under fire with a
                // combat welder, half while burning), and smoke dischargers at half health.
                if (v.Regen > 0f)
                {
                    var rate = Regenerating(v, now);
                    if (rate > 0f) _world.Gear.Heal(v, v.MaxHp * v.Regen * rate * dt);
                }
                if (v.Special == SpecialModule.SmokeDischarger && !v.SmokeUsed && v.Hp < v.MaxHp * 0.5f)
                {
                    v.SmokeUsed = true;
                    _world.Strikes.AddSmoke(v.Team, v.Position, v.SpecialPower, 14f);
                    _world.Gear.Proc(v, SpecialModule.SmokeDischarger);
                }
                if (v.Healing > 0f && v.HealUntil > now) _world.Gear.Heal(v, v.Healing * GearSystem.RepairFactor(v, now) * dt);
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

        /// <summary>
        /// How fast a vehicle's own repair works now, against its full rate: all of it once not hit
        /// for 4 s (less with a toolbox), a combat welder's share under fire, half while burning.
        /// </summary>
        private static float Regenerating(Vehicle v, double now)
        {
            var g = v.Gear;
            if (g == null) return now - v.LastHitTime > 4.0 ? 1f : 0f;
            var delay = Math.Max(1.0, 4.0 - g.Stat(StatId.RegenDelay));
            var rate = now - v.LastHitTime > delay ? 1f : g.Has(TraitId.CombatWelder) ? g.Trait(TraitId.CombatWelder).A : 0f;
            return rate * GearSystem.RepairFactor(v, now);
        }

        /// <summary>Whether <paramref name="point"/> lies inside a jammer of a team hostile to <paramref name="team"/>.</summary>
        public bool Jammed(Vector2 point, int team)
        {
            foreach (var j in _jammers)
                if (j.IsAlive && j.Team != team && Vector2.DistanceSquared(j.Position, point) < j.Def.Jammer * j.Def.Jammer)
                    return true;
            return false;
        }

        /// <summary>
        /// Prompt 25 F2 batch C (ht05, the ammo resupply drop): instantly fills every weapon of one vehicle, in place
        /// (unlike the slow trickle of <see cref="RearmAtHome"/> and <see cref="Rearm"/> in <see cref="SupplySystem"/>).
        /// </summary>
        public void Resupply(Vehicle v)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var w = v.Weapons[i];
                if (w.Load > 0) { w.Ammo = w.Load; w.LoadProgress = 0f; }
                else if (v.Arms[i].Ammo > 0) { w.Ammo = v.Arms[i].Ammo; w.ReloadLeft = 0f; }
            }
            v.RearmProgress = 0f;
        }

        // ------------------------------------------------------------------ ammunition and support

        private void RearmAtHome(Vehicle v)
        {
            if (!v.NeedsAmmo || !_world.TryGetRally(v.Team, out var home)) return;
            if (Vector2.Distance(v.Position, home) > HomeReach) return;
            var depot = v.Team is 0 or 1 ? _rearmBoost[v.Team] : 1f;
            v.RearmProgress += AuraInterval / HomeRearmSeconds * depot * _world.RearmScaleOf(v);
            TopUp(v);
        }

        private void Support(Vehicle engineer)
        {
            var repair = engineer.Def.RepairAura;
            var rearm = engineer.Def.RearmAura;
            // Mines: an engineer clears the enemy mines it can see round it, one at a time.
            if (repair != null)
                foreach (var m in _mines)
                    if (m.IsAlive && m.Team != engineer.Team && m.IsVisibleTo(engineer.Team) && Vector2.Distance(m.Position, engineer.Position) <= repair.Radius)
                    {
                        m.IsAlive = false;
                        _world.Emit(SimEvent.MineCleared(m));
                        break;
                    }
            foreach (var v in _world.VehicleList)
            {
                // Towers too (at half the rate): an engineer patches up its side's defences.
                if (!v.IsAlive || v.Team != engineer.Team || v.Flying || (v.Def.Static && v.Def.Fort == null)) continue;
                var distance = Vector2.Distance(v.Position, engineer.Position);
                if (repair != null && distance <= repair.Radius + (v.Def.Static ? v.Def.HullBound : 0f) && !v.Def.Boss && v.Hp < v.MaxHp)
                {
                    // Prompt 22 F: Engineer Lind's engineers repair faster.
                    var rate = repair.Rate * (v.Def.Static ? 0.5f : 1f) * _world.RepairScaleOf(engineer.Team);
                    var amount = _world.Gear.Heal(v, v.MaxHp * rate * AuraInterval * GearSystem.RepairFactor(v, _world.Time));
                    _world.Emit(SimEvent.RepairedBy(v, amount));
                }
                if (rearm != null && distance <= rearm.Radius && v.NeedsAmmo && !v.Def.Static)
                {
                    v.RearmProgress += AuraInterval / rearm.Rate * _world.RearmScaleOf(v);
                    TopUp(v);
                }
            }
        }

        /// <summary>
        /// A sapper patches up friendly fixed defences round it: towers, turrets, bunkers. It is
        /// slow (a tower takes minutes), so a defended line can be kept standing but not made
        /// unbreakable; the repair shows over the defence being worked on.
        /// </summary>
        /// <summary>
        /// Gun pits stay down while no enemy on the ground is within their rise distance, and come
        /// up (their next shot an ambush) when one is.
        /// </summary>
        private void HideGunPits(double now)
        {
            foreach (var v in _world.VehicleList)
            {
                var hide = v.Def.Hidden;
                if (hide == null || !v.IsAlive) continue;
                var near = false;
                foreach (var e in _world.VehicleList)
                {
                    if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Def.Static) continue;
                    if (Vector2.DistanceSquared(e.Position, v.Position) <= hide.Rise * hide.Rise) { near = true; break; }
                }
                if (v.Lowered && near && hide.FirstShot > 1f) v.AmbushReady = true;
                v.Lowered = !near;
            }
        }

        /// <summary>Wire round an obstacle: enemy ground vehicles within it move slower.</summary>
        private void SlowAuras()
        {
            foreach (var w in _world.VehicleList)
            {
                var aura = w.Def.SlowAura;
                if (aura == null || !w.IsAlive) continue;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team == w.Team || v.Team < 0 || v.Flying || v.Def.Static) continue;
                    if (Vector2.DistanceSquared(v.Position, w.Position) <= aura.Radius * aura.Radius) _world.Status.Slow(v, aura.Rate, AuraInterval * 2f);
                }
            }
        }

        /// <summary>
        /// A base's utility modules at work (see UtilityDef): the repair bay and the ammunition depot
        /// for vehicles in the base (within the home radius of the HQ), the airfield for aircraft over
        /// it, the logistics station's supply, and the radar's watch over the base.
        /// </summary>
        private void BaseModules()
        {
            _world._radarBases.Clear();
            for (var team = 0; team <= 1; team++)
            {
                var repair = 0f;
                var supply = 0;
                _rearmBoost[team] = 1f;
                var home = _world.Bases.Of(team) is { } b ? b.HqPosition : (Vector2?)null;
                foreach (var m in _world.VehicleList)
                {
                    var u = m.Def.Utility;
                    if (u == null || !m.IsAlive || m.Team != team) continue;
                    repair = MathF.Max(repair, u.Repair);
                    supply += u.Supply;
                    _rearmBoost[team] = MathF.Max(_rearmBoost[team], u.Rearm);
                    if (u.RevealBase && home is { } hq) _world._radarBases.Add((team, hq));
                    if (u.AirRepair > 0f) ServeAircraft(m, u);
                }
                if (_world.TryGetEconomy(team, out var economy)) economy.SupplyBonus = supply;
                if (repair <= 0f || home is not { } at) continue;
                repair *= _world.RepairScaleOf(team);
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != team || v.Flying || v.Def.Static || v.Hp >= v.MaxHp) continue;
                    if (Vector2.DistanceSquared(v.Position, at) > SimWorld.HomeRadius * SimWorld.HomeRadius) continue;
                    v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * repair * AuraInterval);
                }
            }
        }

        /// <summary>An airfield: aircraft over it repair and rearm.</summary>
        private void ServeAircraft(Vehicle field, UtilityDef u)
        {
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != field.Team || !v.Flying) continue;
                if (Vector2.DistanceSquared(v.Position, field.Position) > u.AirReach * u.AirReach) continue;
                if (v.Hp < v.MaxHp) v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * u.AirRepair * AuraInterval);
                if (v.NeedsAmmo)
                {
                    v.RearmProgress += AuraInterval / HomeRearmSeconds * _world.RearmScaleOf(v);
                    TopUp(v);
                }
            }
        }

        /// <summary>A side's reload speed at home from its ammunition depot (1: none).</summary>
        private readonly float[] _rearmBoost = { 1f, 1f };

        /// <summary>Command vehicles: friendly vehicles within reach of one fire faster (the best aura counts, they never add up).</summary>
        private void CommandAuras()
        {
            var list = _world.VehicleList;
            foreach (var v in list)
            {
                v.CommandFire = 1f;
                v.CommandDamage = 1f;
            }
            foreach (var c in list)
            {
                var aura = c.Def.CommandAura;
                // A broken command antenna (prompt 9) takes the aura with it.
                if (aura == null || !c.IsAlive || c.Stunned || c.AuraOff) continue;
                var boost = 1f + aura.FireRate;
                var harder = 1f + aura.Damage;
                foreach (var v in list)
                {
                    if (!v.IsAlive || v == c || v.Team != c.Team || v.Def.Boss) continue;
                    if (Vector2.DistanceSquared(v.Position, c.Position) > aura.Radius * aura.Radius) continue;
                    v.CommandFire = MathF.Max(v.CommandFire, boost);
                    v.CommandDamage = MathF.Max(v.CommandDamage, harder);
                }
            }
        }

        /// <summary>
        /// Scatters a mine owned by a side (a remote minefield): harmless for the first moments,
        /// cleared by itself at <paramref name="expires"/>.
        /// </summary>
        internal void AddMine(int team, Vector2 at, MineLayerDef def, double armedAt, double expires)
        {
            if (!_world.Map.Contains(at) || !_world.Grid.IsWalkable(at)) return;
            var laid = new Mine(new EntityId(_nextMine++), team, EntityId.None, at, def, armedAt) { ExpiresAt = expires };
            _mines.Add(laid);
            _world.Emit(SimEvent.MineLaid(laid));
        }

        private void Fortify(Vehicle sapper)
        {
            var aura = sapper.Def.FortifyAura!;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != sapper.Team || !v.Def.Static || v.Hp >= v.MaxHp) continue;
                if (Vector2.Distance(v.Position, sapper.Position) > aura.Radius + v.Def.HullBound) continue;
                var amount = MathF.Min(v.MaxHp - v.Hp, v.MaxHp * aura.Rate * AuraInterval);
                v.Hp += amount;
                _world.Emit(SimEvent.RepairedBy(v, amount));
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
                    var max = v.Arms[i].Ammo;
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
                var max = v.Arms[i].Ammo;
                if (max > 0 && v.Weapons[i].Ammo > 0 && v.Weapons[i].Ammo < max) return true;
            }
            return false;
        }

        // ------------------------------------------------------------------ mines

        private void LayMines(Vehicle v, double now)
        {
            var def = v.MineLayer!;
            if (v.Flying || now < v.NextMineAt) return;
            // A fixed minefield: its whole field at once, and again each interval for any lost.
            if (def.Spread > 0f)
            {
                LayField(v, def, now);
                return;
            }
            // A Mine Dispenser module drops its mines only on the move.
            if (v.Def.Mines == null && !v.IsMoving) return;
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

        private void LayField(Vehicle v, MineLayerDef def, double now)
        {
            var alive = 0;
            foreach (var m in _mines)
                if (m.IsAlive && m.Layer == v.Id) alive++;
            // The whole field is laid again each interval (the ones set off or cleared come back).
            var wanted = def.Max;
            v.MinesLaid = true;
            v.NextMineAt = now + def.Interval;
            for (var tries = 0; alive < wanted && tries < 40; tries++)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                var r = def.Spread * MathF.Sqrt(0.2f + 0.8f * (float)_world.Random.NextDouble());
                var at = v.Position + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r;
                if (!_world.Map.Contains(at) || !_world.Grid.IsWalkable(at)) continue;
                var clear = true;
                foreach (var m in _mines)
                    if (m.IsAlive && Vector2.DistanceSquared(m.Position, at) < 4f) clear = false;
                if (!clear) continue;
                var laid = new Mine(new EntityId(_nextMine++), v.Team, v.Id, at, def, now + 1.0);
                _mines.Add(laid);
                _world.Emit(SimEvent.MineLaid(laid));
                alive++;
            }
        }

        private void TriggerMines(double now)
        {
            for (var i = _mines.Count - 1; i >= 0; i--)
            {
                var m = _mines[i];
                if (!m.IsAlive || now >= m.ExpiresAt)
                {
                    _mines.RemoveAt(i);
                    continue;
                }
                // A UAV scan shows the mines under it too.
                var mask = (1 << m.Team) | _world.Strikes.ScanMask(m.Position, m.Team);
                var armed = now >= m.ArmedAt;
                var rolled = EntityId.None;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Flying || v.Team == m.Team || v.Team < 0) continue;
                    var distance = Vector2.Distance(v.Position, m.Position);
                    if (distance < MineSpotting) mask |= 1 << v.Team;
                    if (!armed || distance > m.Def.Trigger + v.Def.HullRadius) continue;
                    m.IsAlive = false;
                    if (v.Def.MineProof) rolled = v.Id;
                    break;
                }
                m.VisibleToMask = mask;
                if (m.IsAlive) continue;
                _world.Emit(SimEvent.MineDetonated(m));
                _world.Emit(SimEvent.Exploded(m.Position, m.Def.Blast, m.Id));
                // A mine roller sets it off out in front of the tracks: the roller takes the blast.
                // The blast is a mine's (mine resistances and the mine sweep see it as one).
                // Prompt 15: an anti-tank mine is a shaped charge under the belly (penetration 4, the roof's armour).
                _world.Damage.Splash(m.Position, m.Def.Blast.Radius, m.Def.Blast.Damage, DamageType.ShapedCharge, m.Team, rolled,
                    info: new Combat.HitInfo(null, m.Team, null, m.Position, Combat.HitKind.Mine, false));
                _mines.RemoveAt(i);
            }
        }

        // ------------------------------------------------------------------ boss phases

        /// <summary>A multi-phase boss reached its next mark: it transforms, untouchable, before fighting on.</summary>
        internal void BeginPhase(Vehicle v)
        {
            var phase = v.Def.Phases[v.Phase];
            var now = _world.Time;
            v.Transforming = true;
            v.TransformUntil = now + MathF.Max(0f, phase.Transform);
            v.ImmuneUntil = Math.Max(v.ImmuneUntil, v.TransformUntil);
            _world.Emit(SimEvent.BossPhase(v, v.Phase + 2, true, phase.Radio));
            _world.Emit(SimEvent.Exploded(v.Position, new ExplosionDef(0f, v.Radius * 1.6f, 0f, ExplosionTier.Huge), v.Id));
            if (phase.Transform <= 0f) CompletePhase(v, now);
        }

        private void CompletePhase(Vehicle v, double now)
        {
            var phase = v.Def.Phases[v.Phase];
            v.Phase++;
            v.Transforming = false;
            v.DamageBoost *= phase.Damage;
            v.PhaseSpeed *= phase.Speed;
            v.DamageTaken *= phase.Armor;
            // Prompt 26 B.5: its last phase fires faster.
            v.FireBoost *= phase.FireRate;
            if (phase.Heal > 0f) v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * phase.Heal);
            if (phase.Model != null) v.Form = phase.Model;
            foreach (var skill in phase.Skills) Fire(v, skill, now);
            v.RefreshEffects(now);
            _world.Emit(SimEvent.BossPhase(v, v.Phase + 1, false, null));
        }

        // ------------------------------------------------------------------ skills

        private void UseSkills(Vehicle v, double now)
        {
            var skills = v.Def.Skills;
            for (var i = 0; i < skills.Count; i++)
            {
                var skill = skills[i];
                if (v.SkillReadyAt[i] > now || (skill.Once && v.SkillUsed[i])) continue;
                // A boss's skill on a broken part (a drone hangar's launches) is used no more.
                if (i < v.SkillOff.Length && v.SkillOff[i]) continue;
                if (!Triggered(v, skill, now)) continue;
                v.SkillReadyAt[i] = now + skill.Cooldown * (v.Gear != null ? MathF.Max(0.5f, 1f - v.Gear.Stat(StatId.Cooldowns)) : 1f);
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
            SkillTrigger.PartBroken => _world.Bosses.CanPatch(v),
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
                case SkillKind.Patch:
                    // Prompt 9: a boss's self-repair puts a broken part back instead of healing the body.
                    _world.Bosses.Patch(v, skill.Amount > 0f ? skill.Amount : 0.5f);
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
                        _world.Status.Stun(other, until);
                        other.ClearPath();
                        other.Speed = 0f;
                    }
                    break;
            }
        }
    }
}
