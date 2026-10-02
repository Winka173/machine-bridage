#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Ships at sea (prompt 16 B, C), on a battlefield with a sea (<see cref="SeaDef"/>). Ships never touch
    /// the ground's grid: they are steered here in the coast's frame (u along the coast, w out to sea), on
    /// the map's sea lanes.
    /// <list type="bullet">
    /// <item>The flagship (Leviathan) patrols its phase's lane: the far one in phase 1, the near one in
    /// phase 2; in its last phase it runs for the farther end of the far lane, and gets away there
    /// (<see cref="Vehicle.Escaped"/>, the mission lost). Its main turrets lay salvos on the shore, marked
    /// ahead and sweeping along it (a group of enemies near the sweep draws them; from phase 2 the
    /// biggest group in reach); its launch cells fire cruise missiles (and a volley at the enemy's base when
    /// the last phase begins); its well deck sends landing craft to the beaches in phase 2; aircraft fly
    /// in off the sea when a phase begins. Its point defence (APS) is its CIWS parts', strongest in phase 2,
    /// off once both are broken and missing now and then once its radar is.</item>
    /// <item>Escorts keep station on it (abeam on the shore side, inside its length, or along its lane) and
    /// screen it from the shore when it runs; their own CIWS covers it while they are close. Attack boats wait
    /// on the mid lane (the near one while escorts abeam of a flagship on the far lane hold the mid one), dash
    /// in to a pier head, fire and run back out. Landing craft run up on a beach, land their vehicles and go
    /// back.</item>
    /// <item>The coast: its abandoned coastal batteries are taken by a side's ground vehicles holding them
    /// alone; then their guns fire on ships (only). The lighthouse's holder sees the sea.</item>
    /// </list>
    /// Deterministic: everything runs in vehicle-list order off the world's clock and random stream, and
    /// draws random numbers only when a ship is on the field.
    /// </summary>
    internal sealed class NavalSystem
    {
        /// <summary>A coastal battery's gun (a fixed defence that fires on ships only).</summary>
        internal const string BatteryGun = "coastal_battery";

        private const float CaptureRadius = 11f;
        private const float LighthouseRadius = 14f;

        private readonly SimWorld _world;
        private readonly List<(string def, int team, Vector2 at, float heading, EntityId flagship, int landing, string[] cargo, Vector2? station)> _spawns = new();
        private readonly List<(int team, float progress, int progressTeam, EntityId gun, double rebuildAt)> _batteries = new();
        private (int team, float progress, int progressTeam) _lighthouse = (-1, 0f, -1);

        public NavalSystem(SimWorld world)
        {
            _world = world;
            if (world.Map.Sea is { } sea)
                foreach (var _ in sea.Batteries) _batteries.Add((-1, 0f, -1, EntityId.None, 0.0));
            Refresh();
        }

        public NavalRules Rules { get; } = new();

        private SeaDef? Sea => _world.Map.Sea;

        // ================================================================== joining

        /// <summary>A vehicle joined: a ship is put on the water, scripted (no commander moves it), and a flagship's fleet sails with it.</summary>
        public void Joined(Vehicle v)
        {
            var naval = v.Def.Naval;
            if (naval == null || Sea is not { } sea) return;
            v.Scripted = true;
            v.Position = OnWater(sea, v.Position, 4f);
            var f = sea.Frame(v.Position);
            v.NavalDir = f.X <= 0f ? 1 : -1;
            v.Heading = SimMath.HeadingOf(sea.Along * v.NavalDir);
            if (naval.Role != NavalRole.Flagship) return;
            Rules.Flagship = v.Id;
            var now = _world.Time;
            if (v.Def.Salvo is { } salvo) v.SalvoNext = now + salvo.First;
            if (v.Def.Cruise is { } cruise) v.CruiseNext = now + cruise.First;
            v.CraftNext = double.PositiveInfinity;
            v.NavalLane = naval.LaneFor(0);
            // DECISIONS 20Y: its main turrets start trained out to the beam, towards the shore.
            for (var i = 0; i < v.Def.Parts.Count; i++)
                if (v.Def.Parts[i].Kind == "maingun")
                    for (var k = 0; k < v.Def.Parts[i].Mounts.Count; k++) Lay(v, v.Def.Parts[i].Mounts[k], SimMath.HeadingOf(-sea.Out));
            // Its fleet: escorts abeam (or ahead and astern), attack boats out on their lane (the modes' extras on
            // top, on the last escort entry; Boss Rush a share of it).
            var escorts = 0;
            var lastEscort = -1;
            var escortCount = 0;
            for (var e = 0; e < v.Def.Fleet.Count; e++)
                if ((_world.Catalog.Vehicle(v.Def.Fleet[e].Unit).Naval?.Role ?? NavalRole.Escort) == NavalRole.Escort)
                {
                    lastEscort = e;
                    escortCount += v.Def.Fleet[e].Count;
                }
            // A share of the fleet (Boss Rush's half) is taken over all its escorts, the first entries first.
            var escortsLeft = Math.Max(0, (int)MathF.Round(escortCount * Rules.FleetShare));
            for (var e = 0; e < v.Def.Fleet.Count; e++)
            {
                var ship = v.Def.Fleet[e];
                var def = _world.Catalog.Vehicle(ship.Unit);
                var role = def.Naval?.Role ?? NavalRole.Escort;
                var extra = role == NavalRole.Escort ? (e == lastEscort ? Rules.ExtraEscorts : 0) : role == NavalRole.Raider ? Rules.ExtraRaiders : 0;
                var share = role == NavalRole.Escort ? Math.Min(ship.Count, escortsLeft) : Math.Max(0, (int)MathF.Round(ship.Count * Rules.FleetShare));
                if (role == NavalRole.Escort) escortsLeft -= share;
                var count = share + extra;
                for (var k = 0; k < count; k++)
                {
                    Vector2? station = null;
                    Vector2 at;
                    if (role == NavalRole.Escort && ship.Beside)
                    {
                        var s = StationOf(ship, k);
                        station = s;
                        at = sea.At(f.X + s.X, (sea.Lane(v.NavalLane)?.W ?? f.Y) + s.Y);
                    }
                    else
                    {
                        var along = role == NavalRole.Escort ? (escorts++ % 2 == 0 ? 1f : -1f) * (ship.Station + 8f * (k / 2)) : (k - (count - 1) * 0.5f) * 22f;
                        var lane = role == NavalRole.Raider ? sea.Lane(RaiderLane(v)) : sea.Lane(v.NavalLane);
                        at = sea.At(f.X + along * v.NavalDir, lane?.W ?? f.Y);
                    }
                    _spawns.Add((ship.Unit, v.Team, at, v.Heading, v.Id, -1, Array.Empty<string>(), station));
                }
            }
        }

        /// <summary>
        /// DECISIONS 20Y: the k-th escort of a fleet entry kept abeam: its place along the flagship's line (the entry's
        /// "at", mirrored for every other ship) and beside it (the entry's "abeam", a row further out for each one after).
        /// </summary>
        private static Vector2 StationOf(FleetShipDef ship, int k) =>
            new(ship.Station * (k % 2 == 0 ? 1f : -1f), ship.Abeam + 11f * k * (ship.Abeam < 0f ? -1f : 1f));

        /// <summary>Whether a flagship's escorts keep station abeam (they hold the lane inshore of it).</summary>
        private static bool EscortsBeside(VehicleDef def)
        {
            for (var i = 0; i < def.Fleet.Count; i++)
                if (def.Fleet[i].Beside) return true;
            return false;
        }

        /// <summary>
        /// Where a flagship's attack boats wait: the mid lane, or the near one while it sails the far lane with its
        /// escorts abeam inshore of it (they are on the mid lane then).
        /// </summary>
        private string RaiderLane(Vehicle flag) =>
            flag.NavalLane == "far" && EscortsBeside(flag.Def) && Sea?.Lane("near") != null ? "near" : "mid";

        /// <summary>
        /// Trains a gun the naval system lays (a main turret) on a heading, inside its own firing arc (DECISIONS 20Y:
        /// an aft turret never swings forward across the superstructure).
        /// </summary>
        private static void Lay(Vehicle v, int m, float heading)
        {
            var mount = v.Def.Mounts[m];
            if (mount.ArcHalf > 0f)
            {
                var centre = v.Heading + mount.ArcCentre;
                heading = centre + Math.Clamp(SimMath.WrapAngle(heading - centre), -mount.ArcHalf, mount.ArcHalf);
            }
            v.Weapons[m].Heading = heading;
        }

        // ================================================================== the step

        public void Step(float dt)
        {
            var sea = Sea;
            if (sea == null) return;
            var now = _world.Time;
            if (_batteries.Count > 0 && _world.Tick % 5 == 0) Batteries(sea, dt * 5f, now);
            if (sea.Lighthouse != null && _world.Tick % 5 == 0) Lighthouse(sea, dt * 5f);
            var flagshipAlive = false;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Def.Naval is not { } naval || v.Escaped) continue;
                // Its CIWS all broken: no more point defence; its radar broken: it misses now and then.
                if (v.ApsOff) v.Aps = null;
                v.ApsMiss = v.RadarOff ? 0.35f : 0f;
                switch (naval.Role)
                {
                    case NavalRole.Flagship:
                        flagshipAlive = true;
                        Flagship(v, naval, sea, now);
                        break;
                    case NavalRole.Escort:
                        Escort(v, naval, sea);
                        break;
                    case NavalRole.Raider:
                        Raider(v, naval, sea, now);
                        break;
                    case NavalRole.Lander:
                        Lander(v, sea, now);
                        break;
                }
                // Prompt 20 J.4: a submarine under water is the boss system's to move.
                if (v.Burrow == Vehicle.BurrowState.Surface) Sail(v, naval, sea, dt);
            }
            // The flagship went down this step: its magazines go up along the hull, its general signs off.
            if (!flagshipAlive && Rules.Flagship.IsValid && _world.TryGetVehicle(Rules.Flagship, out var sunk) && !sunk.IsAlive)
                Sunk(sunk);
            if (!flagshipAlive && Rules.Flagship.IsValid && !_world.TryGetVehicle(Rules.Flagship, out _)) Rules.Flagship = EntityId.None;
            foreach (var (def, team, at, heading, flagship, landing, cargo, station) in _spawns)
            {
                var ship = _world.SpawnVehicle(def, team, at, heading);
                ship.Flagship = flagship;
                ship.LandingIndex = landing;
                ship.Cargo = cargo;
                if (station is { } s)
                {
                    ship.StationAt = s;
                    ship.OnStation = true;
                }
            }
            _spawns.Clear();
            Refresh();
        }

        private void Refresh()
        {
            Rules.BatteryList.Clear();
            if (Sea is not { } sea) return;
            for (var i = 0; i < _batteries.Count && i < sea.Batteries.Count; i++)
            {
                var b = _batteries[i];
                Rules.BatteryList.Add(new BatteryState(sea.Batteries[i].Id, sea.Batteries[i].At, b.team, b.progress, b.progressTeam, b.gun));
            }
        }

        // ================================================================== steering

        /// <summary>Turns towards its goal and sails on, never onto the land (a landing craft onto its beach).</summary>
        private void Sail(Vehicle v, NavalDef naval, SeaDef sea, float dt)
        {
            var goal = sea.At(v.NavalGoal.X, v.NavalGoal.Y);
            var to = goal - v.Position;
            var distance = to.Length();
            var speed = v.Def.Speed * v.SpeedFactor * (v.Escaping ? naval.EscapeSpeed : 1f);
            if (v.Stunned || v.Landing || distance < 0.8f)
            {
                v.Speed = MathF.Max(0f, v.Speed - v.Def.Speed * dt);
                return;
            }
            var desired = SimMath.HeadingOf(to);
            v.Heading = SimMath.RotateTowards(v.Heading, desired, v.Def.TurnRate * v.TurnFactor * dt);
            var alignment = MathF.Max(0.25f, Vector2.Dot(SimMath.Forward(v.Heading), to / distance));
            // Slows to a stop at its goal (a landing craft on the sand, a boat holding off a pier).
            var target = speed * alignment * MathF.Min(1f, distance / 8f + 0.2f);
            v.Speed += Math.Clamp(target - v.Speed, -v.Def.Speed * dt, v.Def.Speed * 0.5f * dt);
            var next = v.Position + SimMath.Forward(v.Heading) * v.Speed * dt;
            // The waterline: a ship keeps its hull's half-width off it (a lander may ground on the sand).
            var margin = naval.Role == NavalRole.Lander ? -1f : v.Def.HullRadius * 0.6f + 1f;
            v.Position = OnWater(sea, next, margin, v.Escaping);
        }

        /// <summary>A point on the water: pushed out past the waterline by <paramref name="margin"/> metres, inside the map unless it is sailing off.</summary>
        private Vector2 OnWater(SeaDef sea, Vector2 p, float margin, bool leaving = false)
        {
            var f = sea.Frame(p);
            var shore = sea.ShoreAt(f.X);
            if (f.Y < shore + margin) f.Y = shore + margin;
            var q = sea.At(f.X, f.Y);
            if (leaving) return q;
            var limit = _world.Map.HalfSize - 2f;
            return new Vector2(Math.Clamp(q.X, -limit, limit), Math.Clamp(q.Y, -limit, limit));
        }

        // ================================================================== the flagship

        private void Flagship(Vehicle v, NavalDef naval, SeaDef sea, double now)
        {
            var phase = v.Phase;
            if (phase != v.NavalPhaseSeen) PhaseBegins(v, naval, sea, phase, now);
            var f = sea.Frame(v.Position);
            // DECISIONS 20Y: its laid guns with arcs stay inside them as it turns about.
            for (var i = 0; i < v.Def.Parts.Count; i++)
            {
                if (v.Def.Parts[i].Kind != "maingun") continue;
                var laid = v.Def.Parts[i].Mounts;
                for (var k = 0; k < laid.Count; k++)
                    if (v.Def.Mounts[laid[k]].ArcHalf > 0f) Lay(v, laid[k], v.Weapons[laid[k]].Heading);
            }
            if (v.Escaping)
            {
                // Out along the far lane to the edge of the battlefield at its end: it gets away there once its
                // clock (set as the run began, the turn about included) is out, or later if it was slowed.
                var far = sea.Lane("far")!;
                var endU = v.NavalDir * far.End;
                v.NavalGoal = new Vector2(endU, far.W);
                var left = MathF.Abs(endU - f.X) + MathF.Abs(far.W - f.Y);
                var pace = MathF.Max(0.3f, v.Def.Speed * v.SpeedFactor * naval.EscapeSpeed);
                if (double.IsNaN(v.EscapeDeadline))
                {
                    var turn = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(sea.At(endU, far.W) - v.Position) - v.Heading));
                    v.EscapeDeadline = now + left / pace + turn / MathF.Max(0.01f, v.Def.TurnRate * v.TurnFactor);
                }
                v.EscapeSeconds = MathF.Max((float)(v.EscapeDeadline - now), left / pace);
                if (MathF.Abs(f.X) >= far.End - 3f && now >= v.EscapeDeadline)
                {
                    v.Escaped = true;
                    v.Invulnerable = true;
                    v.HoldFire = true;
                    v.EscapeSeconds = 0f;
                    Rules.Escapes++;
                    _world.Emit(SimEvent.RadioMessage("radio.kessler.leviathan.escaped", v.Team));
                }
            }
            else
            {
                // Prompt 20 J.5: a skimmer's passes, in along the near lane, then out on the far one.
                if (naval.PassIn > 0f)
                {
                    if (now >= v.PassUntil)
                    {
                        v.PassIn = !v.PassIn;
                        v.PassUntil = now + (v.PassIn ? naval.PassIn : naval.PassOut);
                    }
                    v.NavalLane = v.PassIn ? "near" : "far";
                    if (sea.Lane(v.NavalLane) == null) v.NavalLane = naval.LaneFor(phase);
                }
                // Patrol: along its lane to the end of its stretch, then about.
                var lane = sea.Lane(v.NavalLane)!;
                var turnU = v.NavalDir * lane.Patrol;
                if ((f.X - turnU) * v.NavalDir > -4f) v.NavalDir = -v.NavalDir;
                v.NavalGoal = new Vector2(v.NavalDir * lane.Patrol, lane.W);
            }
            // Prompt 20 J.4: a submarine fires nothing under water.
            if (v.Transforming || v.HoldFire || v.Burrow != Vehicle.BurrowState.Surface) return;
            if (v.Def.Salvo is { } salvo && now >= v.SalvoNext) Salvo(v, salvo, sea, now);
            if (v.Def.Cruise is { } cruise && phase >= cruise.Phase && now >= v.CruiseNext && !v.CruiseOff)
            {
                v.CruiseNext = now + cruise.Every * v.PartCadence;
                if (BiggestGroup(v, float.MaxValue, out var aim) > 0) Cruise(v, cruise, aim);
            }
            if (v.Def.Craft is { } craft && phase >= craft.Phase && now >= v.CraftNext && !v.CraftOff && v.CraftLaunched < craft.Max && sea.Landings.Count > 0)
            {
                v.CraftNext = now + craft.Every * v.PartCadence;
                LaunchCraft(v, craft, sea);
            }
        }

        /// <summary>A new phase: its lane, its point defence, its aircraft; the last phase's run, smoke and volley.</summary>
        private void PhaseBegins(Vehicle v, NavalDef naval, SeaDef sea, int phase, double now)
        {
            v.NavalPhaseSeen = phase;
            v.NavalLane = naval.LaneFor(phase);
            // Phase 2 (index 1) is its point defence at its most: more interceptors, faster.
            if (v.Def.Aps is { } own)
                v.Aps = phase == 1 ? new ApsDef(own.Radius, own.Charges + 2, own.Recharge * 0.6f) { Rockets = own.Rockets, Shells = own.Shells } : own;
            v.ApsCharges = Math.Min(v.ApsCharges, v.Aps?.Charges ?? 0);
            // The interceptors its standing CIWS hold (part 2's cap) follow the new system.
            BossSystem.Recompute(v);
            if (v.ApsOff) v.Aps = null;
            if (v.Def.Craft is { } craft && phase >= craft.Phase && double.IsPositiveInfinity(v.CraftNext)) v.CraftNext = now + craft.First;
            if (v.Def.Cruise is { } cruise && phase == cruise.Phase) v.CruiseNext = Math.Max(v.CruiseNext, now + cruise.First * 0.5);
            foreach (var wave in v.Def.AirWaves)
            {
                if (wave.Phase != phase) continue;
                for (var k = 0; k < wave.Units.Count; k++)
                {
                    var side = (k - (wave.Units.Count - 1) * 0.5f) * 18f;
                    var at = sea.AirEntry + sea.Along * side;
                    _spawns.Add((wave.Units[k], v.Team, at, SimMath.HeadingOf(-sea.Out), EntityId.None, -1, Array.Empty<string>(), null));
                }
            }
            if (naval.EscapePhase < 0 || phase < naval.EscapePhase || v.Escaping) return;
            // The last phase: it runs for the farther end of the far lane behind smoke, its escorts
            // screening it, and empties its launch cells at the enemy's base.
            v.Escaping = true;
            var f = sea.Frame(v.Position);
            v.NavalDir = f.X >= 0f ? -1 : 1;
            if (MathF.Abs(f.X) < 1f) v.NavalDir = 1;
            _world.Strikes.AddSmoke(v.Team, v.Position, 20f, 22f);
            _world.Strikes.AddSmoke(v.Team, v.Position - sea.Out * 18f, 16f, 18f);
            _world.Emit(SimEvent.RadioMessage("radio.kessler.leviathan.run", v.Team));
            if (v.Def.Cruise is { } final && !v.CruiseOff)
                foreach (var aim in BaseTargets(v, final.Final)) Cruise(v, final, aim);
        }

        /// <summary>
        /// A salvo from each standing main turret: its shells along the shore round the aim point, marked
        /// ahead. Phase 1 sweeps the shore the way it sails (a group of enemies near the sweep draws it);
        /// later phases shell the biggest group of enemies in reach. A broken fire-control radar spreads them.
        /// </summary>
        private void Salvo(Vehicle v, SalvoDef salvo, SeaDef sea, double now)
        {
            v.SalvoNext = now + salvo.Every * v.PartCadence;
            var parts = v.Def.Parts;
            var f = sea.Frame(v.Position);
            if (!v.SweepSet)
            {
                v.SweepU = f.X;
                v.SweepSet = true;
            }
            v.SweepU += v.NavalDir * salvo.Sweep;
            if (MathF.Abs(v.SweepU - f.X) > salvo.Range * 0.7f) v.SweepU = f.X;
            var sweep = sea.At(v.SweepU, sea.ShoreAt(v.SweepU) - 8f);
            Vector2 aim;
            if (v.Phase >= 1 && BiggestGroup(v, salvo.Range, out var group) > 0) aim = group;
            else if (BiggestGroup(v, salvo.Range, out var near, sweep, 24f) > 0) aim = near;
            else aim = sweep;
            if (Vector2.Distance(aim, v.Position) > salvo.Range) return;
            var blind = v.RadarOff;
            var scatter = 3.5f * (blind ? salvo.BlindScatter : 1f);
            var spread = salvo.Spread * (blind ? salvo.BlindScatter : 1f);
            var warning = salvo.Warning != null && _world.Catalog.TryGetSupport(salvo.Warning, out var w) ? w : null;
            var gun = salvo.Weapon != null && _world.Catalog.Weapons.TryGetValue(salvo.Weapon, out var g) ? g : null;
            // DECISIONS 20Y: the salvo's shells lie in one line along the shore across every standing turret's
            // (Leviathan's: one gun a turret, a ripple), each turret flashing once a shell.
            var total = 0;
            for (var i = 0; i < parts.Count; i++)
                if (parts[i].Kind == "maingun" && !v.IsPartBroken(i)) total += salvo.Shells;
            var j = 0;
            // Prompt 34 L4: a turret whose barrels fire together lands its shells together (the ripple runs turret by turret).
            var together = gun is { Simultaneous: true };
            var turret = -1;
            for (var i = 0; i < parts.Count; i++)
            {
                if (parts[i].Kind != "maingun" || v.IsPartBroken(i)) continue;
                turret++;
                for (var s = 0; s < salvo.Shells; s++, j++)
                {
                    var along = total > 1 ? (j - (total - 1) * 0.5f) * spread / (total - 1) : 0f;
                    var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                    var reach = scatter * MathF.Sqrt((float)_world.Random.NextDouble());
                    var at = _world.ClampToMap(aim + sea.Along * along + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach);
                    if (warning != null) _world.Emit(SimEvent.StrikeWarning(v.Team, warning, at, at, salvo.Warn));
                    _world.Damage.Queue(at, salvo.Blast(ExplosionTier.Huge), salvo.Warn + 0.15 * (together ? turret : j), v.Team, v,
                        HitKind.Strike, v.Id);
                }
                // The turret swings to its aim (inside its arc) and fires (its muzzle flash and the shells' flight).
                var mounts = parts[i].Mounts;
                if (mounts.Count == 0) continue;
                var m = mounts[0];
                Lay(v, m, SimMath.HeadingOf(aim - v.Position));
                if (gun != null)
                    for (var s = 0; s < salvo.Shells; s++) _world.Emit(SimEvent.Fired(v, m, v.PartPosition(i), aim, salvo.Warn, EntityId.None));
            }
            v.LastFiredAt = now;
        }

        /// <summary>A cruise missile from the launch cells at a spot, marked ahead.</summary>
        private void Cruise(Vehicle v, CruiseDef cruise, Vector2 aim)
        {
            var origin = v.Position;
            for (var i = 0; i < v.Def.Parts.Count; i++)
                if (v.Def.Parts[i].Kind == "vls") origin = v.PartPosition(i);
            var scatter = v.RadarOff ? 6f : 2f;
            var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
            var at = _world.ClampToMap(aim + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * scatter * (float)_world.Random.NextDouble());
            if (cruise.Warning != null && _world.Catalog.TryGetSupport(cruise.Warning, out var warning))
                _world.Emit(SimEvent.StrikeWarning(v.Team, warning, at, at, cruise.Warn));
            if (cruise.Weapon != null && _world.Catalog.Weapons.TryGetValue(cruise.Weapon, out var missile))
                _world.Emit(SimEvent.FiredWith(v, missile, origin, at, cruise.Warn, EntityId.None));
            _world.Damage.Queue(at, ExplosionDef.TwoLayer(cruise.Damage, cruise.Radius, ExplosionTier.Ultimate), cruise.Warn, v.Team, v, HitKind.Strike, v.Id);
        }

        /// <summary>The enemy's base for the last volley: its HQ and its biggest towers (else its biggest groups).</summary>
        private List<Vector2> BaseTargets(Vehicle v, int count)
        {
            var list = new List<Vector2>();
            var enemy = v.Team == 0 ? 1 : 0;
            if (_world.Bases.Of(enemy) is { HqFallen: false } camp) list.Add(camp.HqPosition);
            foreach (var o in _world.VehicleList)
            {
                if (list.Count >= count) break;
                if (o.IsAlive && o.Team == enemy && o.Def.Static && o.Def.Fort != null && !o.Def.Obstacle) list.Add(o.Position);
            }
            if (list.Count < count && BiggestGroup(v, float.MaxValue, out var group) > 0)
                while (list.Count < count) list.Add(group);
            return list;
        }

        /// <summary>A landing craft out of the well deck, for the next beach, with the next vehicles.</summary>
        private void LaunchCraft(Vehicle v, CraftDef craft, SeaDef sea)
        {
            var cargo = new string[craft.Per];
            for (var k = 0; k < craft.Per; k++)
                cargo[k] = craft.Carries.Count > 0 ? craft.Carries[(v.CraftLaunched * craft.Per + k) % craft.Carries.Count] : "main_battle_tank";
            var landing = v.CraftLaunched % sea.Landings.Count;
            // Launched from the stern, out of the well deck (a part of kind "welldeck", else behind the ship).
            var at = v.Position - SimMath.Forward(v.Heading) * v.Def.HullRadius;
            for (var i = 0; i < v.Def.Parts.Count; i++)
                if (v.Def.Parts[i].Kind == "welldeck") at = v.PartPosition(i) - SimMath.Forward(v.Heading) * 4f;
            _spawns.Add((craft.Unit, v.Team, at, v.Heading, v.Id, landing, cargo, null));
            v.CraftLaunched++;
        }

        // ================================================================== the fleet

        private void Escort(Vehicle v, NavalDef naval, SeaDef sea)
        {
            if (_world.TryGetVehicle(v.Flagship, out var flag) && flag.IsAlive && !flag.Escaped)
            {
                var ff = sea.Frame(flag.Position);
                v.NavalDir = flag.NavalDir;
                if (v.OnStation)
                {
                    // DECISIONS 20Y: abeam of it on its station (inside its length, on the shore side), a little
                    // further in while it runs.
                    var w = flag.Escaping ? ff.Y : sea.Lane(flag.NavalLane)?.W ?? ff.Y;
                    v.NavalGoal = new Vector2(ff.X + v.StationAt.X + flag.NavalDir * 4f, w + v.StationAt.Y * (flag.Escaping ? 1.25f : 1f));
                    return;
                }
                var station = naval.Station == 0f ? 24f : naval.Station;
                var side = (v.Id.Value & 1) == 0 ? 1f : -1f;
                // Screening the run: between it and the shore, a little ahead or astern.
                if (flag.Escaping) v.NavalGoal = new Vector2(ff.X + side * station * 0.45f + flag.NavalDir * 6f, ff.Y - 15f);
                else
                {
                    var lane = sea.Lane(flag.NavalLane);
                    v.NavalGoal = new Vector2(ff.X + side * station + flag.NavalDir * 4f, lane?.W ?? ff.Y);
                }
                return;
            }
            // Its flagship gone: it patrols the near lane on its own.
            Patrol(v, sea, "near");
        }

        private void Patrol(Vehicle v, SeaDef sea, string laneId)
        {
            var lane = sea.Lane(laneId)!;
            var f = sea.Frame(v.Position);
            if ((f.X - v.NavalDir * lane.Patrol) * v.NavalDir > -4f) v.NavalDir = -v.NavalDir;
            v.NavalGoal = new Vector2(v.NavalDir * lane.Patrol, lane.W);
        }

        /// <summary>An attack boat: out on the mid lane by its flagship, then a dash to the nearest pier head, a hold there firing, and back out.</summary>
        private void Raider(Vehicle v, NavalDef naval, SeaDef sea, double now)
        {
            var f = sea.Frame(v.Position);
            if (now >= v.DashUntil)
            {
                v.DashStage = (v.DashStage + 1) % 3;
                v.DashUntil = now + v.DashStage switch { 0 => naval.DashEvery, 1 => 40.0, _ => naval.DashHold };
                if (v.DashStage == 0 && _world.Random.NextDouble() < 0.5) v.NavalDir = -v.NavalDir;
            }
            switch (v.DashStage)
            {
                case 0:
                {
                    // Out on its lane, near its flagship (or on its own patrol on the mid lane).
                    var withFlag = _world.TryGetVehicle(v.Flagship, out var flag) && flag.IsAlive && !flag.Escaped;
                    var lane = sea.Lane(withFlag ? RaiderLane(flag) : "mid")!;
                    var u = withFlag
                        ? sea.Frame(flag.Position).X + ((v.Id.Value % 3) - 1) * 20f
                        : Math.Clamp(f.X + v.NavalDir * 20f, -lane.Patrol, lane.Patrol);
                    v.NavalGoal = new Vector2(u, lane.W);
                    return;
                }
                case 1:
                {
                    // In: to just off the pier head nearest it; the hold starts when it gets there.
                    var pier = sea.Frame(sea.Approach(v.Position));
                    v.NavalGoal = new Vector2(pier.X, MathF.Max(pier.Y + naval.DashW * 0.3f, sea.ShoreAt(pier.X) + 8f));
                    if (Vector2.Distance(sea.At(v.NavalGoal.X, v.NavalGoal.Y), v.Position) < 6f)
                    {
                        v.DashStage = 2;
                        v.DashUntil = now + naval.DashHold;
                    }
                    return;
                }
                default:
                    return;
            }
        }

        /// <summary>A landing craft: onto its beach, its vehicles off, back to its ship (and gone).</summary>
        private void Lander(Vehicle v, SeaDef sea, double now)
        {
            if (v.LandingIndex < 0 || v.LandingIndex >= sea.Landings.Count) v.LandingIndex = 0;
            var beach = sea.Landings[v.LandingIndex];
            if (!v.Unloaded)
            {
                var goal = sea.Frame(beach.At);
                v.NavalGoal = goal;
                if (double.IsPositiveInfinity(v.UnloadAt) && Vector2.Distance(v.Position, beach.At) < 5f)
                {
                    v.UnloadAt = now + 3.0;
                    v.Landing = true;
                }
                if (now < v.UnloadAt) return;
                v.Unloaded = true;
                v.Landing = false;
                var inland = beach.Inland;
                var across = Vector2.Normalize(new Vector2(-(inland - beach.At).Y, (inland - beach.At).X));
                for (var k = 0; k < v.Cargo.Length; k++)
                    _spawns.Add((v.Cargo[k], v.Team, inland + across * ((k - (v.Cargo.Length - 1) * 0.5f) * 6f), SimMath.HeadingOf(inland - beach.At),
                        EntityId.None, -1, Array.Empty<string>(), null));
                _world.Emit(SimEvent.Landed(v, inland, v.Cargo.Length));
                return;
            }
            // Back out to its ship; alongside, it is hoisted in (it leaves the field).
            var home = _world.TryGetVehicle(v.Flagship, out var flag) && flag.IsAlive ? flag.Position : sea.At(sea.Frame(v.Position).X, sea.Lane("far")!.W);
            v.NavalGoal = sea.Frame(home);
            if (Vector2.Distance(v.Position, home) < 10f + (flag?.Def.HullRadius ?? 0f))
            {
                v.Hp = 0f;
                _world.Emit(SimEvent.Retired(v));
            }
        }

        // ================================================================== going down

        /// <summary>The flagship sank: its magazines cook off along the hull, one after another, and its general signs off.</summary>
        private void Sunk(Vehicle v)
        {
            Rules.Flagship = EntityId.None;
            var forward = SimMath.Forward(v.Heading);
            for (var k = 0; k < 5; k++)
            {
                var at = v.Position + forward * ((k - 2) * v.Def.HullRadius * 0.55f);
                _world.Damage.Queue(at, new ExplosionDef(0f, 9f + 2f * (k % 2), 0f, ExplosionTier.Ultimate), 0.8 + 0.7 * k, v.Team, null, HitKind.Strike, v.Id);
            }
            // Prompt 20: each ship boss's own sign-off (Leviathan's is Kessler's line).
            var line = v.Def.Id != "leviathan" && v.Def.RadioSpawn != null ? v.Def.RadioSpawn + ".sunk" : "radio.kessler.leviathan.sunk";
            _world.Emit(SimEvent.RadioMessage(line, v.Team));
        }

        // ================================================================== the coast

        /// <summary>The coastal batteries: taken by a side's ground vehicles holding one alone; a destroyed gun's battery stands abandoned again a while later.</summary>
        private void Batteries(SeaDef sea, float dt, double now)
        {
            for (var i = 0; i < _batteries.Count; i++)
            {
                var (team, progress, progressTeam, gun, rebuildAt) = _batteries[i];
                var def = sea.Batteries[i];
                if (team >= 0)
                {
                    if (_world.TryGetVehicle(gun, out var g) && g.IsAlive)
                    {
                        // A side that takes the ground from its holder takes the gun.
                        var (holder, _) = Holder(def.At, CaptureRadius);
                        if (holder >= 0 && holder != team)
                        {
                            progress = progressTeam == holder ? progress + dt / Rules.CaptureSeconds : dt / Rules.CaptureSeconds;
                            progressTeam = holder;
                            if (progress >= 1f)
                            {
                                _world.Defect(g, holder);
                                team = holder;
                                progress = 0f;
                                progressTeam = -1;
                                _world.Emit(SimEvent.RadioMessage(holder == 0 ? "radio.naval.battery.ours" : "radio.naval.battery.theirs", holder));
                            }
                        }
                        else if (holder < 0) progress = 0f;
                        _batteries[i] = (team, progress, progressTeam, gun, rebuildAt);
                        continue;
                    }
                    // Its gun was destroyed: abandoned, and usable again after a while.
                    _batteries[i] = (-1, 0f, -1, EntityId.None, now + Rules.RebuildSeconds);
                    continue;
                }
                if (now < rebuildAt) continue;
                var (side, _) = Holder(def.At, CaptureRadius);
                if (side < 0)
                {
                    _batteries[i] = (-1, 0f, -1, EntityId.None, rebuildAt);
                    continue;
                }
                progress = progressTeam == side ? progress + dt / Rules.CaptureSeconds : dt / Rules.CaptureSeconds;
                progressTeam = side;
                if (progress < 1f)
                {
                    _batteries[i] = (-1, progress, progressTeam, EntityId.None, rebuildAt);
                    continue;
                }
                var gunDef = _world.Catalog.Vehicles.ContainsKey(BatteryGun) ? BatteryGun : "heavy_turret";
                var raised = _world.SpawnVehicle(gunDef, side, def.At, SimMath.DegToRad(def.Heading));
                _batteries[i] = (side, 0f, -1, raised.Id, 0.0);
                _world.Emit(SimEvent.RadioMessage(side == 0 ? "radio.naval.battery.ours" : "radio.naval.battery.theirs", side));
            }
        }

        /// <summary>The lighthouse: held by whoever holds its point (the mode's), else by a side's ground vehicles holding it alone.</summary>
        private void Lighthouse(SeaDef sea, float dt)
        {
            if (_world.Bases.PointOwner is { } owner)
            {
                Rules.LighthouseOwner = owner(sea.Lighthouse!);
                return;
            }
            var (side, _) = Holder(sea.Lamp, LighthouseRadius);
            var (team, progress, progressTeam) = _lighthouse;
            if (side >= 0 && side != team)
            {
                progress = progressTeam == side ? progress + dt / Rules.CaptureSeconds : dt / Rules.CaptureSeconds;
                progressTeam = side;
                if (progress >= 1f)
                {
                    team = side;
                    progress = 0f;
                    _world.Emit(SimEvent.RadioMessage(side == 0 ? "radio.naval.lighthouse.ours" : "radio.naval.lighthouse.theirs", side));
                }
            }
            else if (side < 0) progress = 0f;
            _lighthouse = (team, progress, progressTeam);
            Rules.LighthouseOwner = team;
        }

        /// <summary>The one side with ground vehicles within <paramref name="radius"/> of a spot (-1: nobody, or both).</summary>
        private (int team, int count) Holder(Vector2 at, float radius)
        {
            var team = -1;
            var count = 0;
            foreach (var o in _world.VehicleList)
            {
                if (!o.IsAlive || o.Team < 0 || o.Flying || o.Def.Static || o.Def.Naval != null) continue;
                if (Vector2.DistanceSquared(o.Position, at) > radius * radius) continue;
                if (team >= 0 && o.Team != team) return (-1, 0);
                team = o.Team;
                count++;
            }
            return (team, count);
        }

        /// <summary>
        /// The enemy's ground vehicles round their densest spot within <paramref name="range"/> of the ship
        /// (and within <paramref name="radius"/> of <paramref name="near"/> when one is given): how many, and where.
        /// </summary>
        private int BiggestGroup(Vehicle v, float range, out Vector2 centre, Vector2? near = null, float radius = 0f)
        {
            centre = v.Position;
            var best = 0f;
            var count = 0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Def.Naval != null) continue;
                if (range < float.MaxValue && Vector2.DistanceSquared(e.Position, v.Position) > range * range) continue;
                if (near is { } n && Vector2.DistanceSquared(e.Position, n) > radius * radius) continue;
                var weight = 0f;
                var k = 0;
                var sum = Vector2.Zero;
                foreach (var o in _world.VehicleList)
                {
                    if (!o.IsAlive || o.Team != e.Team || o.Flying || o.Def.Naval != null) continue;
                    if (Vector2.DistanceSquared(o.Position, e.Position) > 15f * 15f) continue;
                    weight += MathF.Max(1f, o.Def.CpCost);
                    k++;
                    sum += o.Position;
                }
                if (weight <= best) continue;
                best = weight;
                count = k;
                centre = sum / k;
            }
            return count;
        }

        /// <summary>The sea's state into the battle's fingerprint.</summary>
        internal void Mix(Action<long> mix)
        {
            foreach (var b in _batteries) mix(b.team * 1000 + (long)MathF.Round(b.progress * 100f));
            mix(Rules.LighthouseOwner);
            mix(Rules.Escapes);
        }
    }
}
