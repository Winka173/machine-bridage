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
        private static float HomeReach => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.HomeReach;

        /// <summary>Seconds per round when re-arming at home.</summary>
        private static float HomeRearmSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.HomeRearmSeconds;

        /// <summary>Auras tick this often (seconds).</summary>
        private static float AuraInterval => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.AuraInterval;

        /// <summary>Enemies see a mine only this close to one of their vehicles.</summary>
        private static float MineSpotting => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.MineSpotting;

        private readonly SimWorld _world;
        private readonly List<Mine> _mines = new();
        private readonly List<Vehicle> _jammers = new();
        private readonly List<(string def, int team, Vector2 at, float heading, int by, string skill)> _summons = new();

        /// <summary>Boss design 09/10: summons called but not yet arrived (their place ringed): arrival time, then the same as a summon.</summary>
        private readonly List<(double due, string def, int team, Vector2 at, float heading, int by, string skill)> _pending = new();

        /// <summary>Boss design 09/10: how often a summon blocked by an enemy standing on its arrival point is tried again before the wave is given up.</summary>
        private readonly Dictionary<(int by, string skill), int> _blocked = new();

        private const int BlockedRetries = 4;
        private const float BlockedRetrySeconds = 2.5f;

        /// <summary>Play-test 14 (lane G): the units each vehicle's capped summon (<see cref="SkillDef.Max"/>) has put up, by skill.</summary>
        private readonly Dictionary<(int by, string skill), List<EntityId>> _summoned = new();
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
                if (v.FlareChargesMax > 0) RechargeFlares(v, now);
                v.RefreshEffects(now);
                // A boss's jamming aura stops with its jammer part (prompt 16).
                if (v.Def.Jammer > 0f && !v.JammerOff) _jammers.Add(v);
                // Standing still (entrenchment counts from here).
                if (Vector2.DistanceSquared(v.Position, v.StillAt) > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.StepDistanceSquaredMin)
                {
                    v.StillAt = v.Position;
                    v.StillSince = now;
                }
                // Home zone: a vehicle left alone for 3 s by its own camp repairs 2 % a second.
                if (_world.HomeZones && !v.Def.Static && v.Hp < v.MaxHp && now - v.LastHitTime > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.StepNowMin &&
                    _world.TryGetRally(v.Team, out var home) && Vector2.DistanceSquared(v.Position, home) < SimWorld.HomeRadius * SimWorld.HomeRadius)
                    v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.StepMaxHpScale * dt);
                // Active protection reloads one interceptor at a time; a launcher reloaded whole (prompt 20 L.1, the
                // Iron Dome) gets all of them back once it has been quiet for its reload time (it restarts at each launch).
                var aps = v.Aps;
                // Play-test 13 (lane C): a vehicle's own APS (one activation takes a whole salvo) reloads ApsRechargeScale slower.
                var apsRecharge = aps == null ? 0f : aps.Reload > 0f ? aps.Reload
                    : v.Def.InterceptionMode == InterceptionMode.SelfAps ? aps.Recharge * SimTunables.Weapons.Countermeasures.ApsRechargeScale : aps.Recharge;
                if (aps != null && !v.ApsOff && v.ApsCharges < Math.Min(aps.Charges, v.ApsMax) && (v.ApsReload += dt * v.ApsRate) >= apsRecharge)
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
            if (skillTick) _skillTimer += global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.StepSkillTimer;

            if (auraTick)
            {
                CommandAuras();
                BaseModules();
                SlowAuras();
            }
            HideGunPits(now);
            _summons.Clear();
            for (var p = _pending.Count - 1; p >= 0; p--)
            {
                if (_pending[p].due > now) continue;
                var due = _pending[p];
                _pending.RemoveAt(p);
                _summons.Add((due.def, due.team, due.at, due.heading, due.by, due.skill));
            }
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
                    if (v.Unkillable) v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.StepMaxHpScale2 * AuraInterval);
                }
                // Upgrades: self-repair out of combat (sooner with a toolbox, part of it under fire with a
                // combat welder, half while burning), and smoke dischargers at half health.
                if (v.Regen > 0f)
                {
                    var rate = Regenerating(v, now);
                    if (rate > 0f) _world.Gear.Heal(v, v.MaxHp * v.Regen * rate * dt);
                }
                if (v.Special == SpecialModule.SmokeDischarger && !v.SmokeUsed && v.Hp < v.MaxHp * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.StepMaxHpScale3)
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
            foreach (var (def, team, at, heading, by, skillId) in _summons)
            {
                var unit = _world.SpawnVehicle(def, team, at, heading);
                if (skillId.Length == 0) continue;
                if (!_summoned.TryGetValue((by, skillId), out var list)) _summoned[(by, skillId)] = list = new List<EntityId>();
                list.Add(unit.Id);
            }

            TriggerMines(now);
        }

        /// <summary>
        /// How fast a vehicle's own repair works now, against its full rate: all of it once not hit
        /// for 4 s (less with a toolbox), a combat welder's share under fire, half while burning.
        /// </summary>
        private static float Regenerating(Vehicle v, double now)
        {
            var g = v.Gear;
            if (g == null) return now - v.LastHitTime > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.RegeneratingNowMin ? 1f : 0f;
            var delay = Math.Max(1.0, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.RegeneratingStatSub - g.Stat(StatId.RegenDelay));
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
                    var rate = repair.Rate * (v.Def.Static ? global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.SupportStaticTrue : 1f) * _world.RepairScaleOf(engineer.Team);
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
            // Prompt 32 L3: rubble of a wall slows every ground vehicle crossing it (only while there is rubble).
            if (_world.HasWalls && _world.Walls.HasRubble)
            {
                var slow = _world.Catalog.Base.Walls.RubbleSlow;
                foreach (var v in _world.VehicleList)
                    if (v.IsAlive && !v.Flying && !v.Def.Static && _world.Walls.InRubble(v.Position)) _world.Status.Slow(v, slow, AuraInterval * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.SlowAurasAuraIntervalScale);
            }
            foreach (var w in _world.VehicleList)
            {
                var aura = w.Def.SlowAura;
                if (aura == null || !w.IsAlive) continue;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team == w.Team || v.Team < 0 || v.Flying || v.Def.Static) continue;
                    if (Vector2.DistanceSquared(v.Position, w.Position) <= aura.Radius * aura.Radius) _world.Status.Slow(v, aura.Rate, AuraInterval * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.SlowAurasAuraIntervalScale);
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
                    v.Weapons[i].ReloadLeft = MathF.Max(0.0001f, v.Weapons[i].ReloadLeft - AuraInterval * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.TopUpAuraIntervalScale); // the reload itself finishes it
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
            if (v.Flying) return;
            if (def.TurnStrip > 0f)
            {
                LayStrip(v, def, now);
                return;
            }
            if (now < v.NextMineAt) return;
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
                if (Vector2.DistanceSquared(m.Position, v.Position) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayMinesDistanceSquaredMax) return;
            }
            if (mine >= def.Max) return;
            // Drop it behind the vehicle, clear of the hull.
            var at = v.Position - SimMath.Forward(v.Heading) * (v.Def.HullHalf + v.Def.HullRadius + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayMinesHullHalfAdd);
            if (!_world.Map.Contains(at) || !_world.Grid.IsWalkable(at)) return;
            var laid = new Mine(new EntityId(_nextMine++), v.Team, v.Id, at, def, now + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayMinesNowAdd);
            _mines.Add(laid);
            _world.Emit(SimEvent.MineLaid(laid));
        }

        /// <summary>
        /// Prompt 26 D.1 (Ixion): a turn of <see cref="MineLayerDef.TurnStrip"/> degrees on the move drops a strip of mines behind it
        /// (Max of them, 2.5 m apart, clear of the hull), each clearing itself after its Life.
        /// </summary>
        private void LayStrip(Vehicle v, MineLayerDef def, double now)
        {
            var delta = MathF.Abs(SimMath.WrapAngle(v.Heading - v.MineHeading));
            v.MineHeading = v.Heading;
            if (!v.IsMoving) return;
            v.MineTurned += delta;
            if (v.MineTurned < def.TurnStrip * (MathF.PI / 180f) || now < v.NextMineAt) return;
            v.MineTurned = 0f;
            v.NextMineAt = now + def.Interval;
            var back = -SimMath.Forward(v.Heading);
            var start = v.Def.HullHalf + v.Def.HullRadius + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayStripHullHalfAdd;
            for (var k = 0; k < def.Max; k++)
            {
                var at = v.Position + back * (start + k * 2.5f);
                if (!_world.Map.Contains(at) || !_world.Grid.IsWalkable(at)) continue;
                var laid = new Mine(new EntityId(_nextMine++), v.Team, v.Id, at, def, now + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayStripNowAdd) { ExpiresAt = def.Life > 0f ? now + def.Life : double.PositiveInfinity };
                _mines.Add(laid);
                _world.Emit(SimEvent.MineLaid(laid));
            }
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
                var r = def.Spread * MathF.Sqrt(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayFieldNextDoubleAdd + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayFieldNextDoubleScale * (float)_world.Random.NextDouble());
                var at = v.Position + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r;
                if (!_world.Map.Contains(at) || !_world.Grid.IsWalkable(at)) continue;
                var clear = true;
                foreach (var m in _mines)
                    if (m.IsAlive && Vector2.DistanceSquared(m.Position, at) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.LayFieldDistanceSquaredMax) clear = false;
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
            _world.Emit(SimEvent.Exploded(v.Position, new ExplosionDef(0f, v.Radius * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.BeginPhaseRadiusScale, 0f, ExplosionTier.Huge), v.Id));
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
            // Boss design 09/10: a summon's first wave comes after its delay, not with the boss.
            if (!v.SkillsArmed)
            {
                v.SkillsArmed = true;
                for (var a = 0; a < skills.Count; a++)
                    if (skills[a].Kind == SkillKind.Summon && skills[a].Delay > 0f) v.SkillReadyAt[a] = Math.Max(v.SkillReadyAt[a], now + skills[a].Delay);
            }
            for (var i = 0; i < skills.Count; i++)
            {
                var skill = skills[i];
                if (v.SkillReadyAt[i] > now || (skill.Once && v.SkillUsed[i])) continue;
                // A boss's skill on a broken part (a drone hangar's launches) is used no more.
                if (i < v.SkillOff.Length && v.SkillOff[i]) continue;
                if (!Triggered(v, skill, now)) continue;
                // Boss design 09/10: a full flight skips the wave and keeps no queue: the next call is a whole cooldown away
                // (play-test 14 made it wait with its cooldown unspent, so the first free slot refilled at once).
                if (skill.Kind == SkillKind.Summon && skill.Max > 0 && SummonedAlive(v, skill) >= skill.Max)
                {
                    v.SkillReadyAt[i] = now + skill.Cooldown;
                    continue;
                }
                // Boss design 09/10: nothing arrives on top of an enemy ground unit; tried again a few times, then the wave is dropped.
                if (skill.Kind == SkillKind.Summon && skill.Safe > 0f)
                {
                    var key = (v.Id.Value, skill.Id);
                    if (!SpawnClear(v, skill))
                    {
                        var tries = _blocked.TryGetValue(key, out var n) ? n : 0;
                        if (tries < BlockedRetries)
                        {
                            _blocked[key] = tries + 1;
                            v.SkillReadyAt[i] = now + BlockedRetrySeconds;
                        }
                        else
                        {
                            _blocked.Remove(key);
                            v.SkillReadyAt[i] = now + skill.Cooldown;
                        }
                        continue;
                    }
                    _blocked.Remove(key);
                }
                // Prompt 29 S06: flares as charges: one is spent, the next can go once this one has burnt.
                if (skill.Kind == SkillKind.Flares && v.FlareChargesMax > 0)
                {
                    if (v.FlareChargesLeft <= 0) continue;
                    if (v.FlareChargesLeft == v.FlareChargesMax) v.FlareRechargeAt = now + FlareRecharge(v, skill);
                    v.FlareChargesLeft--;
                    v.SkillReadyAt[i] = now + MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.UseSkillsDurationFloor, skill.Duration);
                    v.SkillUsed[i] = true;
                    Fire(v, skill, now);
                    v.RefreshEffects(now);
                    _world.Emit(SimEvent.SkillUsed(v, skill));
                    continue;
                }
                v.SkillReadyAt[i] = now + skill.Cooldown * (v.Gear != null ? MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.UseSkillsStatFloor, 1f - v.Gear.Stat(StatId.Cooldowns)) : 1f);
                v.SkillUsed[i] = true;
                Fire(v, skill, now);
                v.RefreshEffects(now);
                _world.Emit(SimEvent.SkillUsed(v, skill));
            }
        }

        /// <summary>Play-test 14 (lane G): how many of <paramref name="v"/>'s units from <paramref name="skill"/> are alive (the dead are dropped).</summary>
        private int SummonedAlive(Vehicle v, SkillDef skill)
        {
            var pending = 0;
            foreach (var p in _pending)
                if (p.by == v.Id.Value && p.skill == skill.Id) pending++;
            if (!_summoned.TryGetValue((v.Id.Value, skill.Id), out var list)) return pending;
            list.RemoveAll(id => !_world.TryGetVehicle(id, out var u) || !u.IsAlive);
            return list.Count + pending;
        }

        /// <summary>
        /// Boss design 09/10: where a summon's units arrive. From the part that carries the skill (a hangar, a flight deck, a gate or a
        /// deployment door: its place on the hull, a little outside it), side by side; with no such part, round the hull as before. A
        /// ground unit is put on open ground; a spot with none is dropped.
        /// </summary>
        private List<Vector2> SpawnPoints(Vehicle v, SkillDef skill, int count)
        {
            var points = new List<Vector2>(count);
            BossPartDef? carrier = null;
            foreach (var part in v.Def.Parts)
                for (var s = 0; s < part.Skills.Count && carrier == null; s++)
                    if (part.Skills[s] == skill.Id) carrier = part;
            var ground = _world.Catalog.Vehicles.TryGetValue(skill.Unit!, out var unit) && !unit.Flying;
            for (var k = 0; k < count; k++)
            {
                Vector2 at;
                if (carrier != null)
                {
                    var forward = SimMath.Forward(v.Heading);
                    var right = new Vector2(forward.Y, -forward.X);
                    var local = carrier.At;
                    var len = local.Length();
                    var outward = len > 0.5f ? local / len : new Vector2(0f, -1f);
                    // Out of the hull by the unit's own length, and the units of one wave side by side.
                    var lateral = new Vector2(-outward.Y, outward.X) * ((k - (count - 1) * 0.5f) * 6f);
                    var spot = local + outward * 6f + lateral;
                    at = v.Position + right * spot.X + forward * spot.Y;
                }
                else
                {
                    var angle = (k + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.FireKAdd) * SimMath.Tau / skill.Count + v.Heading;
                    at = v.Position + SimMath.Forward(angle) * (v.Def.HullBound + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.FireHullBoundAdd);
                }
                at = _world.ClampToMap(at);
                if (ground)
                {
                    if (!_world.Grid.TryNearestWalkable(at, 6, out var open)) continue;
                    at = open;
                }
                points.Add(at);
            }
            return points;
        }

        /// <summary>Boss design 09/10: no enemy ground unit within <see cref="SkillDef.Safe"/> of where this summon would arrive.</summary>
        private bool SpawnClear(Vehicle v, SkillDef skill)
        {
            foreach (var at in SpawnPoints(v, skill, Math.Max(1, skill.Count)))
                foreach (var e in _world.VehicleList)
                {
                    if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying) continue;
                    if (Vector2.DistanceSquared(e.Position, at) < (skill.Safe + e.Radius) * (skill.Safe + e.Radius)) return false;
                }
            return true;
        }

        /// <summary>Seconds for one flare charge: the vehicle's own, else its flare skill's cooldown; the heat-decoy module x0.75.</summary>
        private static float FlareRecharge(Vehicle v, SkillDef skill) =>
            (v.Def.FlareRecharge ?? MathF.Max(1f, skill.Cooldown)) * v.FlareRechargeScale;

        /// <summary>
        /// Prompt 29 S06: flare charges come back one at a time while the aircraft is in its holding pattern, and all at once
        /// when it rearms on a landing pad or over the HQ.
        /// </summary>
        private void RechargeFlares(Vehicle v, double now)
        {
            if (v.FlareChargesMax <= 0 || v.FlareChargesLeft >= v.FlareChargesMax) return;
            if (v.Supply == SupplyState.Holding && v.RearmAt is RearmSite.LandingPad or RearmSite.Headquarters)
            {
                v.FlareChargesLeft = v.FlareChargesMax;
                return;
            }
            if (v.Supply != SupplyState.Holding)
            {
                // Not in the holding pattern: the clock waits (no charge comes back in the fight).
                if (v.FlareRechargeAt < now) v.FlareRechargeAt = now;
                return;
            }
            if (now < v.FlareRechargeAt) return;
            v.FlareChargesLeft++;
            SkillDef? flare = null;
            foreach (var s in v.Def.Skills)
                if (s.Kind == SkillKind.Flares) flare = s;
            v.FlareRechargeAt = now + (flare != null ? FlareRecharge(v, flare) : global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.RechargeFlaresFlareFalse);
        }

        private bool Triggered(Vehicle v, SkillDef skill, double now) => skill.Trigger switch
        {
            SkillTrigger.Always => true,
            SkillTrigger.HpBelow => v.Hp / v.MaxHp < skill.Threshold,
            SkillTrigger.UnderFire => now - v.LastHitTime < 1.0,
            SkillTrigger.EnemyInRange => _world.FindNearestEnemy(v, skill.Radius > 0f ? skill.Radius : v.Def.Weapon.Range,
                requireVisible: true) != null,
            // Play-test 13 (lane C): flares go out on the missile warner's terminal cue, so one cloud meets every missile
            // arriving together (released at launch, a 1.5 s cloud had burnt out before a long shot arrived).
            SkillTrigger.MissileIncoming => skill.Kind == SkillKind.Flares ? _world.FlareCue(v.Id) : _world.MissileIncoming(v.Id),
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
                    _world.Bosses.Patch(v, skill.Amount > 0f ? skill.Amount : global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.FireAmountFalse);
                    break;
                case SkillKind.Shield:
                    v.ShieldUntil = until;
                    v.ShieldAmount = Math.Clamp(skill.Amount, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.FireAmountMax);
                    break;
                case SkillKind.Smoke:
                    _world.Strikes.AddSmoke(v.Team, v.Position, skill.Radius > 0f ? skill.Radius : global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.FireRadiusFalse, skill.Duration);
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
                {
                    // Play-test 14 (lane G): a capped summon only tops its flight up to the cap.
                    var count = skill.Max > 0 ? Math.Min(skill.Count, skill.Max - SummonedAlive(v, skill)) : skill.Count;
                    var points = SpawnPoints(v, skill, count);
                    for (var k = 0; k < points.Count; k++)
                    {
                        var at = points[k];
                        var id = skill.Max > 0 ? skill.Id : "";
                        if (skill.Warn <= 0f)
                        {
                            _summons.Add((skill.Unit!, v.Team, at, v.Heading, v.Id.Value, id));
                            continue;
                        }
                        // The place is ringed for the warning, then the unit arrives (it counts against the cap meanwhile).
                        _pending.Add((now + skill.Warn, skill.Unit!, v.Team, at, v.Heading, v.Id.Value, id));
                        if (_world.Catalog.TryGetSupport(skill.Warning ?? "escort_drop.ifv", out var ring))
                            _world.Emit(SimEvent.StrikeWarning(v.Team, ring, at, at, skill.Warn));
                    }
                    break;
                }
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
