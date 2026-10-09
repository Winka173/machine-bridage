#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Prompt 25 F2 batch A (DECISIONS 25F2-A): the balance sheet's new structures and the units' mechanisms that are not a
    /// weapon's: blast walls and troop shelters (cover), inflatable decoys (found out by scouts, radars and scans), the
    /// fire-control centre's linked towers, searchlights and flare towers (light in the dark), barrage balloons (bomb
    /// scatter, helicopters kept out), the visual jammer (enemy sight cut round it), the reconnaissance jet's pass and
    /// the airborne vehicle's parachute drop. Everything reads the simulation's state and clock only (deterministic).
    /// The drone killers (the microwave, interceptor drones) and the targeting weights are CombatSystem.P25A's.
    /// </summary>
    internal sealed partial class FieldWorksSystem
    {
        private readonly SimWorld _world;

        // The works alive this step (rebuilt every step; a handful each, so the queries loop them).
        private readonly List<Vehicle> _walls = new();
        private readonly List<Vehicle> _shelters = new();
        private readonly List<Vehicle> _lights = new();
        private readonly List<Vehicle> _balloons = new();
        private readonly List<Vehicle> _screens = new();
        private readonly List<Vehicle> _centres = new();
        private readonly List<Vehicle> _decoys = new();

        /// <summary>Targets linked towers are firing on this step (team, target): the others gang up on them.</summary>
        private readonly HashSet<(int team, EntityId target)> _linkedTargets = new();

        /// <summary>Ground a side has lit (a flare burning): everything there shows to that side until the time.</summary>
        private readonly List<(int team, Vector2 at, float radius, double until)> _lit = new();

        /// <summary>Paradrop stand-ins falling.</summary>
        private readonly List<Vehicle> _drops = new();

        private double _decoyCheckAt;

        public FieldWorksSystem(SimWorld world) => _world = world;

        /// <summary>
        /// Night, fog or a sandstorm (the game sets it from the weather; a mission's weather shift that takes sight down to
        /// night's counts too): what the searchlights and flare towers are for.
        /// </summary>
        public bool Dark => _dark || _world.WeatherSight <= NightSight + 1e-3f;

        private bool _dark;

        internal void SetDark(bool dark) => _dark = dark;

        /// <summary>The weather table's sight at night (EventDefs: Night 0.75, Fog 0.7, Sandstorm 0.75).</summary>
        private static float NightSight => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.NightSight;

        /// <summary>A unit joins the battle: a high-flying jet takes its altitude tier.</summary>
        internal void Joined(Vehicle v)
        {
            v.SpawnedAt = _world.Time;
            if (v.Def.FlightTier == AltitudeTier.None || !v.Def.Flying) return;
            v.Tier = v.TierFrom = v.TierTo = v.Def.FlightTier;
            v.AltitudeNow = v.Def.Altitude;
        }

        public void Step(float dt)
        {
            var now = _world.Time;
            _walls.Clear();
            _shelters.Clear();
            _lights.Clear();
            _balloons.Clear();
            _screens.Clear();
            _centres.Clear();
            _decoys.Clear();
            _auras.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team < 0) continue;
                var d = v.Def;
                if (d.BlastWall != null) _walls.Add(v);
                if (d.Shelter != null) _shelters.Add(v);
                if (d.Decoy != null) _decoys.Add(v);
                if (d.BaseAura != null) _auras.Add(v);
                // A stunned light, balloon crew, jammer or centre does nothing while it lasts.
                if (v.Stunned) continue;
                if (d.Searchlight != null) _lights.Add(v);
                if (d.Balloon != null) _balloons.Add(v);
                if (d.SightJammer != null) _screens.Add(v);
                if (d.FireControl != null) _centres.Add(v);
                if (d.Flares != null) Flares(v, now);
                if (d.ReconPass != null) PassScan(v, now);
            }
            LinkTowers();
            ApplyBaseAuras();
            if (_decoys.Count > 0 && now >= _decoyCheckAt)
            {
                _decoyCheckAt = now + DecoyCheckSeconds;
                ExposeDecoys();
            }
            for (var i = _lit.Count - 1; i >= 0; i--)
                if (_lit[i].until <= now) _lit.RemoveAt(i);
            StepDrops(now);
        }

        // ================================================================== cover: blast walls and shelters

        /// <summary>
        /// What a hit on <paramref name="victim"/> keeps after its side's cover: a blast wall between a tower and the shooter
        /// takes its share off direct fire (not rounds lobbed or dropped, not top attack); a troop shelter takes its share
        /// off lobbed rounds, bombs and strikes for the vehicles round it (never direct fire). One wall and one shelter count.
        /// </summary>
        internal float CoverFactor(Vehicle victim, DamageType type, in HitInfo hit)
        {
            if (_walls.Count == 0 && _shelters.Count == 0) return 1f;
            var weapon = hit.Weapon;
            var lobbed = hit.Indirect || hit.Kind is HitKind.Strike or HitKind.Mine || weapon is { Projectile: ProjectileKind.Bomb } ||
                         (hit.Kind == HitKind.Splash && weapon == null && hit.Attacker == null);
            var factor = 1f;
            if (_walls.Count > 0 && victim.Def.Fort is { Kind: FortKind.Tower } && victim.Def.BlastWall == null && !lobbed && !hit.Top &&
                !(weapon?.TopAttack ?? false) && hit.Kind is HitKind.Direct or HitKind.Pierce or HitKind.Splash)
            {
                var from = hit.Attacker?.Position ?? hit.Origin;
                var toShooter = from - victim.Position;
                var shooterDistance = toShooter.Length();
                if (shooterDistance > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.CoverFactorShooterDistanceMin)
                    foreach (var wall in _walls)
                    {
                        if (wall.Team != victim.Team) continue;
                        var w = wall.Def.BlastWall!;
                        var toWall = wall.Position - victim.Position;
                        var d = toWall.Length();
                        if (d > w.Radius + wall.Def.HullBound || d >= shooterDistance || d < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.CoverFactorDMax) continue;
                        var cos = Vector2.Dot(toWall, toShooter) / (d * shooterDistance);
                        if (cos < MathF.Cos(w.Cone)) continue;
                        factor *= 1f - w.Cut;
                        break;
                    }
            }
            if (_shelters.Count > 0 && lobbed && !victim.Def.Static && !victim.Flying)
                foreach (var s in _shelters)
                {
                    if (s.Team != victim.Team) continue;
                    var r = s.Def.Shelter!.Radius + s.Def.HullBound;
                    if (Vector2.DistanceSquared(s.Position, victim.Position) > r * r) continue;
                    factor *= 1f - s.Def.Shelter.Cut;
                    break;
                }
            return factor;
        }

        // ================================================================== decoys

        private static double DecoyCheckSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.DecoyCheckSeconds;

        /// <summary>
        /// A decoy is found out by the side of an enemy scout, radar (a counter-battery or air-search radar, a radar module)
        /// or drone that sees it, or of a UAV scan (or a reconnaissance pass) over it; that side stops shooting at it for good.
        /// </summary>
        private void ExposeDecoys()
        {
            foreach (var d in _decoys)
            {
                var scanned = _world.Strikes.ScanMask(d.Position, d.Team);
                var mask = d.DecoyExposedMask | scanned;
                foreach (var e in _world.VehicleList)
                {
                    if (!e.IsAlive || e.Team == d.Team || e.Team < 0 || e.Team > 30 || (mask & (1 << e.Team)) != 0) continue;
                    if (!Unmasks(e.Def) || !d.IsSeenBy(e.Team)) continue;
                    var reach = e.Def.VisionRange * e.VisionFactor + d.Radius;
                    if (e.Def.StillVision > 0f) reach = MathF.Max(reach, e.Def.StillVision * e.VisionFactor + d.Radius);
                    if (Vector2.DistanceSquared(e.Position, d.Position) <= reach * reach) mask |= 1 << e.Team;
                }
                if (mask != d.DecoyExposedMask)
                {
                    d.DecoyExposedMask = mask;
                    _world.Emit(SimEvent.Proc(d, "decoy.exposed"));
                }
            }
        }

        /// <summary>What sees through a decoy: a scout, a radar or a drone.</summary>
        internal static bool Unmasks(VehicleDef def) =>
            def.Class == UnitClass.Scout || def.CounterBattery != null || def.RevealAir > 0f || def.StillVision > 0f || def.ReconPass != null ||
            (def.Drone && def.Flying) || def.Utility is { RevealBase: true } || def.RevealStealth;

        // ================================================================== the fire-control centre

        private void LinkTowers()
        {
            _linkedTargets.Clear();
            foreach (var v in _world.VehicleList)
            {
                v.FireLinked = false;
                v.LinkDamage = 1f;
            }
            if (_centres.Count == 0) return;
            foreach (var t in _world.VehicleList)
            {
                if (!t.IsAlive || t.Def.Fort is not { Kind: FortKind.Tower } || t.Def.Passive || t.Def.Decoy != null) continue;
                var best = 0f;
                foreach (var c in _centres)
                {
                    if (c.Team != t.Team) continue;
                    var r = c.Def.FireControl!.Radius + t.Def.HullBound;
                    if (Vector2.DistanceSquared(c.Position, t.Position) <= r * r) best = MathF.Max(best, c.Def.FireControl.Damage);
                }
                if (best <= 0f) continue;
                t.FireLinked = true;
                t.LinkDamage = 1f + best;
                if (t.Target.IsValid) _linkedTargets.Add((t.Team, t.Target));
            }
        }

        /// <summary>A linked tower of <paramref name="team"/> is firing on <paramref name="target"/>.</summary>
        internal bool LinkedOn(int team, EntityId target) => _linkedTargets.Contains((team, target));

        /// <summary>The fire-control focus of the best centre over this tower (1: none).</summary>
        internal float LinkFocus(Vehicle tower)
        {
            var best = 1f;
            foreach (var c in _centres)
            {
                if (c.Team != tower.Team) continue;
                var r = c.Def.FireControl!.Radius + tower.Def.HullBound;
                if (Vector2.DistanceSquared(c.Position, tower.Position) <= r * r) best = MathF.Max(best, c.Def.FireControl.Focus);
            }
            return best;
        }

        // ================================================================== light, balloons, the visual jammer

        /// <summary>Teams (a mask) that see <paramref name="target"/> by a searchlight or a burning flare of theirs (in the dark only).</summary>
        internal int LitMask(Vehicle target)
        {
            if (!Dark || (_lights.Count == 0 && _lit.Count == 0)) return 0;
            var mask = 0;
            foreach (var l in _lights)
            {
                if (l.Team == target.Team || l.Team > 30) continue;
                var r = l.Def.Searchlight!.Radius + target.Radius;
                if (Vector2.DistanceSquared(l.Position, target.Position) <= r * r) mask |= 1 << l.Team;
            }
            foreach (var (team, at, radius, _) in _lit)
                if (team != target.Team && team is >= 0 and < 31 && Vector2.DistanceSquared(at, target.Position) <= (radius + target.Radius) * (radius + target.Radius))
                    mask |= 1 << team;
            return mask;
        }

        /// <summary>
        /// How much wider a shot scatters: a shooter caught in an enemy searchlight in the dark (dazzled), a bomb dropped from
        /// over or onto an enemy barrage balloon's ground (the aircraft had to climb). 1: neither.
        /// </summary>
        internal float SpreadFactor(Vehicle shooter, WeaponDef weapon, Vector2 aimAt)
        {
            var factor = 1f;
            if (_lights.Count > 0 && Dark)
                foreach (var l in _lights)
                {
                    if (l.Team == shooter.Team) continue;
                    var s = l.Def.Searchlight!;
                    var r = s.Radius + shooter.Radius;
                    if (Vector2.DistanceSquared(l.Position, shooter.Position) > r * r) continue;
                    factor /= 1f - s.Dazzle;
                    break;
                }
            if (_balloons.Count > 0 && shooter.Flying && weapon.Projectile == ProjectileKind.Bomb)
                foreach (var b in _balloons)
                {
                    if (b.Team == shooter.Team) continue;
                    var s = b.Def.Balloon!;
                    if (Vector2.DistanceSquared(b.Position, shooter.Position) > s.Radius * s.Radius &&
                        Vector2.DistanceSquared(b.Position, aimAt) > s.Radius * s.Radius) continue;
                    factor *= 1f + s.Scatter;
                    break;
                }
            return factor;
        }

        /// <summary>A helicopter keeps out of an enemy barrage balloon's ground: pushed back out over its edge at its own speed.</summary>
        internal void KeepOffBalloons(Vehicle v, float dt)
        {
            if (_balloons.Count == 0 || !v.Flying || v.Def.FixedWing || v.IsPod || v.Def.Boss) return;
            foreach (var b in _balloons)
            {
                if (b.Team == v.Team) continue;
                var r = b.Def.Balloon!.Radius;
                var out_ = v.Position - b.Position;
                var d = out_.Length();
                if (d >= r) continue;
                var away = d > 0.01f ? out_ / d : SimMath.Forward(v.Heading + MathF.PI);
                var push = MathF.Min(r - d, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.KeepOffBalloonsSpeedFloor, v.Def.Speed) * dt);
                v.Position = _world.ClampToMap(v.Position + away * push);
            }
        }

        /// <summary>
        /// A spotter's sight of <paramref name="target"/> cut by a visual jammer of the target's side over it (the metres it
        /// still sees from; float.MaxValue: not screened). A scout sees through it.
        /// </summary>
        internal float ScreenedFrom(Vehicle target)
        {
            if (_screens.Count == 0) return float.MaxValue;
            var close = float.MaxValue;
            foreach (var s in _screens)
            {
                if (s.Team != target.Team) continue;
                var j = s.Def.SightJammer!;
                if (Vector2.DistanceSquared(s.Position, target.Position) <= j.Radius * j.Radius) close = MathF.Min(close, j.Close + target.Radius);
            }
            return close;
        }

        /// <summary>A spotter's reach after its own mechanism: a scout's mast up once it has stood still a while.</summary>
        internal float SpotterReach(Vehicle spotter, float reach)
        {
            var d = spotter.Def;
            if (d.StillVision > 0f && !spotter.IsMoving && _world.Time - spotter.StillSince >= d.StillAfter)
                reach *= d.StillVision / MathF.Max(1f, d.VisionRange);
            return reach;
        }

        // ================================================================== flare towers

        private void Flares(Vehicle tower, double now)
        {
            var f = tower.Def.Flares!;
            if (now < tower.WorksNextAt || !Dark) return;
            // The nearest enemy its side sees within reach, else a point out in front.
            Vector2? mark = null;
            var best = float.MaxValue;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == tower.Team || e.Team < 0 || e.Flying || !e.IsVisibleTo(tower.Team)) continue;
                var d2 = Vector2.DistanceSquared(e.Position, tower.Position);
                if (d2 > f.Range * f.Range || d2 >= best) continue;
                best = d2;
                mark = e.Position;
            }
            var at = mark ?? _world.ClampToMap(tower.Position + SimMath.Forward(tower.Heading) * f.Range * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.FlaresForwardScale);
            tower.WorksNextAt = now + f.Every;
            _lit.Add((tower.Team, at, f.Radius, now + FlareRise + f.Seconds));
            tower.TurretHeading = SimMath.HeadingOf(at - tower.Position);
            _world.Emit(SimEvent.FiredWith(tower, tower.Def.Weapon, tower.Position, at, FlareRise, EntityId.None));
        }

        /// <summary>Seconds a flare takes to climb and burst over its mark.</summary>
        private const float FlareRise = 1.2f;

        // ================================================================== the reconnaissance jet

        /// <summary>Every half second of its run the jet leaves a circle of its strip behind it, shown to its side (a scan: stealth and hidden too).</summary>
        private void PassScan(Vehicle jet, double now)
        {
            if (!jet.PassStarted || now < jet.PassNextScan) return;
            var p = jet.Def.ReconPass!;
            jet.PassNextScan = now + PassScanSeconds;
            if (_world.Map.EdgeDistance(jet.Position) > 1f) _world.Strikes.AddScan(jet.Team, jet.Position, p.Width * 0.5f, p.Seconds);
        }

        private static double PassScanSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.PassScanSeconds;

        /// <summary>
        /// The jet's one run: straight across the battlefield at full speed, towards the enemy's camp from where it came
        /// in, and off the far edge, where it leaves the battle. False for everything else.
        /// </summary>
        internal bool FlyPass(Vehicle v, float dt)
        {
            if (v.Def.ReconPass == null || !v.Flying) return false;
            if (!v.PassStarted)
            {
                v.PassStarted = true;
                v.PassHeading = v.Heading;
                foreach (var team in new[] { 0, 1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.N3 })
                    if (team != v.Team && _world.TryGetRally(team, out var enemy))
                    {
                        v.PassHeading = SimMath.HeadingOf(enemy - v.Position);
                        break;
                    }
                v.PassNextScan = _world.Time;
            }
            v.Heading = SimMath.RotateTowards(v.Heading, v.PassHeading, v.Def.TurnRate * dt);
            v.Speed = v.Def.Speed * v.SpeedFactor;
            var next = v.Position + SimMath.Forward(v.Heading) * v.Speed * dt;
            // Off the map: gone (no wreck, no kill; the pass was the card).
            if (!_world.Map.Contains(next) || _world.Map.EdgeDistance(next) < 1f && _world.Time - v.SpawnedAt > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.FlyPassTimeMin)
            {
                v.Hp = 0f;
                _world.Emit(SimEvent.Retired(v));
                return true;
            }
            v.Position = _world.ClampToMap(next);
            return true;
        }

        // ================================================================== the parachute drop

        /// <summary>Whether a side sees a point now: a unit of its within its sight (not through smoke), or a scan of its over it.</summary>
        internal bool SeenBy(int team, Vector2 point)
        {
            if (team is < 0 or > 30) return false;
            if ((_world.Strikes.ScanMask(point, -1) & (1 << team)) != 0) return true;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != team || v.IsPod) continue;
                var reach = SpotterReach(v, v.Def.VisionRange * v.VisionFactor * _world.WeatherSight * _world.StormSight(v.Position));
                if (Vector2.DistanceSquared(v.Position, point) <= reach * reach && !_world.Strikes.Obscures(v.Position, point)) return true;
            }
            return false;
        }

        /// <summary>A point within <paramref name="keepOut"/> of an enemy side's camp (its HQ and drop zone).</summary>
        internal bool NearEnemyBase(int team, Vector2 point, float keepOut)
        {
            foreach (var other in new[] { 0, 1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.N32 })
                if (other != team && _world.TryGetRally(other, out var camp) && Vector2.DistanceSquared(camp, point) < keepOut * keepOut) return true;
            return false;
        }

        /// <summary>
        /// A paid drop begins: the stand-in (the vehicle under its canopies) comes down on <paramref name="at"/> over the
        /// drop's fall, a low-altitude target the whole way; if it survives, the vehicle lands with the health it kept.
        /// </summary>
        internal void StartDrop(int team, string unit, Vector2 at, ParadropDef drop)
        {
            var heading = 0f;
            if (_world.TryGetRally(team, out var home)) heading = SimMath.HeadingOf(at - home);
            var proxy = _world.SpawnVehicle(drop.Proxy, team, at, heading);
            proxy.IsPod = true;
            proxy.Scripted = true;
            proxy.Tier = proxy.TierFrom = proxy.TierTo = AltitudeTier.Low;
            proxy.PodLaunched = _world.Time;
            proxy.PodLands = _world.Time + drop.Fall;
            proxy.PodFrom = drop.Height;
            proxy.AltitudeNow = drop.Height;
            proxy.DropAt = at;
            proxy.DropUnit = unit;
            _drops.Add(proxy);
        }

        /// <summary>Stand-ins falling this step (the economy counts them as vehicles on the way).</summary>
        internal int DropsOf(int team)
        {
            var n = 0;
            foreach (var d in _drops)
                if (d.IsAlive && d.Team == team) n++;
            return n;
        }

        private void StepDrops(double now)
        {
            for (var i = _drops.Count - 1; i >= 0; i--)
            {
                var proxy = _drops[i];
                if (!proxy.IsAlive)
                {
                    _drops.RemoveAt(i);
                    continue;
                }
                var u = (float)Math.Clamp((now - proxy.PodLaunched) / Math.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.StepDropsPodLandsFloor, proxy.PodLands - proxy.PodLaunched), 0.0, 1.0);
                proxy.AltitudeNow = proxy.PodFrom + (DropGround - proxy.PodFrom) * u;
                if (now < proxy.PodLands) continue;
                _drops.RemoveAt(i);
                var share = Math.Clamp(proxy.Hp / MathF.Max(1f, proxy.MaxHp), global::MachineBrigade.Sim.Content.SimTunables.Vehicles.FieldWorksSystem.StepDropsHpMin, 1f);
                if (proxy.DropUnit != null && _world.Catalog.Vehicles.ContainsKey(proxy.DropUnit))
                {
                    var landed = _world.SpawnVehicle(proxy.DropUnit, proxy.Team, proxy.DropAt, proxy.Heading);
                    landed.Hp = landed.MaxHp * share;
                }
                proxy.Hp = 0f;
                _world.Emit(SimEvent.Retired(proxy));
            }
        }

        /// <summary>The stand-in's drawn height as it touches down (the vehicle's hull on the ground).</summary>
        private const float DropGround = 0.5f;
    }
}
