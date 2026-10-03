#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>A mode with capture points the commander AI can fight over.</summary>
    public interface IObjectiveMode
    {
        IReadOnlyList<ObjectiveState> Points { get; }
    }

    /// <summary>
    /// The capture rules every point-based mode shares: vehicles inside the circle push the point
    /// towards their side at their capture rate, both sides present freezes it, an unattended
    /// point drifts back to its owner, and ownership flips only at a full hold.
    /// </summary>
    public static class PointCapture
    {
        public const int TeamA = 0;
        public const int TeamB = 1;

        public static void Tick(SimWorld world, ObjectiveState point, float dt, float captureSeconds)
        {
            // Prompt 22 F: the battle has capture points (Flag's weakness is for a battle without them).
            world.PointsInPlay = true;
            var power0 = 0f;
            var power1 = 0f;
            var r = point.Def.Radius;
            foreach (var v in world.VehicleList)
            {
                // Aircraft cannot hold ground, except a helicopter that carries troops (the Mi-24's capture rate).
                if (!v.IsAlive || (v.Flying && (v.Def.FixedWing || v.Def.CaptureRate <= 0f)) ||
                    Vector2.DistanceSquared(v.Position, point.Def.Position) > r * r) continue;
                if (v.Team == TeamA) power0 += v.CaptureRate;
                else if (v.Team == TeamB) power1 += v.CaptureRate;
            }

            point.Contested = power0 > 0f && power1 > 0f;
            var before = point.Owner;
            if (!point.Contested && (power0 > 0f || power1 > 0f))
            {
                var push = (power0 - power1) * dt / captureSeconds;
                point.Progress = Math.Clamp(point.Progress + push, -1f, 1f);
            }
            else if (!point.Contested)
            {
                // Unattended points drift back to their owner's full hold (or to neutral).
                var rest = point.Owner == TeamA ? 1f : point.Owner == TeamB ? -1f : 0f;
                point.Progress = SimMath.MoveTowards(point.Progress, rest, dt / (captureSeconds * 3f));
            }

            // Ownership flips only at a full hold; crossing zero neutralises the point first.
            if (point.Progress >= 1f) point.Owner = TeamA;
            else if (point.Progress <= -1f) point.Owner = TeamB;
            else if ((point.Owner == TeamA && point.Progress <= 0f) || (point.Owner == TeamB && point.Progress >= 0f))
                point.Owner = -1;
            if (point.Owner != before) world.Announce(SimEvent.Captured(point.Def.Id, point.Def.Position, point.Owner));
        }

        /// <summary>Starts a point fully held by <paramref name="team"/>.</summary>
        public static void Own(ObjectiveState point, int team)
        {
            point.Owner = team;
            point.Progress = team == TeamA ? 1f : team == TeamB ? -1f : 0f;
        }

        public static int Held(IReadOnlyList<ObjectiveState> points, int team)
        {
            var count = 0;
            foreach (var p in points)
                if (p.Owner == team) count++;
            return count;
        }
    }

    /// <summary>
    /// Notices vehicles that are gone since the last look and books them to their side: how many
    /// each side lost and what they cost. Destroyed and removed vehicles count the same.
    /// </summary>
    /// <summary>
    /// Spawn protection for the capture modes, after LoL's Nexus Obelisk and Dota's fountain: each
    /// side's camp gets two indestructible bastions (twin guns and flak, reaching 40 m, air and
    /// ground) and a home zone (see <see cref="SimWorld.HomeZones"/>), so a winning army cannot
    /// camp the losing side's spawn and a match cannot be steamrolled to its last vehicle.
    /// </summary>
    public static class BaseDefences
    {
        public const string Bastion = "spawn_bastion";

        public static void Build(SimWorld world, params int[] teams) => Build(world, null, teams);

        /// <summary>
        /// Each side's base (see <see cref="BaseSystem"/>): its HQ with the drop zone round it
        /// (standing in for the old pair of bastions) and its loadout's towers in the camp's
        /// hardpoints, plus the home zone. A setup names each side's loadout and role (an Anchor HQ
        /// cannot fall); without one each side gets a bare, unbreakable HQ.
        /// </summary>
        public static void Build(SimWorld world, BaseSetup? setup, params int[] teams)
        {
            world.HomeZones = true;
            if (world.Catalog.Vehicles.ContainsKey(world.Catalog.Base.HqId))
            {
                foreach (var team in teams)
                {
                    var role = setup?.Role(team) ?? BaseRole.Anchor;
                    if (role == BaseRole.None) continue;
                    world.Bases.Establish(team, setup?.Loadout(team) ?? BaseLoadout.HqOnly(), role);
                }
                return;
            }
            if (!world.Catalog.Vehicles.ContainsKey(Bastion)) return;
            foreach (var team in teams)
            {
                if (!world.TryGetRally(team, out var rally)) continue;
                var toward = rally.LengthSquared() > 1f ? Vector2.Normalize(-rally) : Vector2.UnitX;
                var side = new Vector2(-toward.Y, toward.X);
                foreach (var s in new[] { -1f, 1f })
                {
                    var bastion = world.SpawnVehicle(Bastion, team, rally + toward * 10f + side * (18f * s), SimMath.HeadingOf(toward));
                    bastion.Invulnerable = true;
                    world.AnchorDefence(bastion);
                }
            }
        }
    }

    /// <summary>
    /// Watchtowers on the capture points. Two kinds, after how other games guard their objectives:
    /// <list type="bullet">
    /// <item><b>Neutral</b> (Conquest, King of the Hill): each point has a tower that belongs to no
    /// side and fires on every side, like Warcraft III's creep camps guarding expansions or the
    /// hostile mercenaries of Sins of a Solar Empire: whoever wants the point has to pay for it,
    /// and the side that breaks the tower opens the point for the other side too. A tower that is
    /// knocked down stands again after <see cref="RespawnSeconds"/>, like a MOBA jungle camp, so
    /// the points never go quiet.</item>
    /// <item><b>Holder</b> (Assault): the defender's sectors are dug in with its own towers, as in
    /// Battlefield's Breakthrough; a sector the attacker takes gets the attacker's tower after
    /// <see cref="BuildSeconds"/>, and a tower knocked down while its side still holds the point is
    /// rebuilt after <see cref="RebuildSeconds"/>.</item>
    /// </list>
    /// Each side's camp is guarded by its own bastions (see <see cref="BaseDefences"/>).
    /// </summary>
    public sealed class Outposts
    {
        /// <summary>A point's watchtower: a guard tower, with twice the health while it is neutral.</summary>
        public const string Tower = "guard_tower";

        private static float NeutralHealth => global::MachineBrigade.Sim.Content.SimTunables.Modes.Outposts.NeutralHealth;
        public static float BuildSeconds => global::MachineBrigade.Sim.Content.SimTunables.Modes.Outposts.BuildSeconds;
        public static float RebuildSeconds => global::MachineBrigade.Sim.Content.SimTunables.Modes.Outposts.RebuildSeconds;
        public static float RespawnSeconds => global::MachineBrigade.Sim.Content.SimTunables.Modes.Outposts.RespawnSeconds;

        private sealed class Site
        {
            public ObjectiveState Point = null!;
            public Vector2 Spot;
            public float Heading;
            public EntityId Tower;
            public int Team = -1;
            public int Pending = -1;
            public double BuildAt;
        }

        private readonly List<Site> _sites = new();
        private readonly bool _neutral;

        /// <param name="neutral">Towers hostile to every side (else each belongs to the point's holder).</param>
        /// <param name="built">Holder towers: points already held get their tower at once (a defender dug in).</param>
        public Outposts(SimWorld world, IReadOnlyList<ObjectiveState> points, bool neutral = false, bool built = false)
        {
            _neutral = neutral;
            if (!world.Catalog.Vehicles.ContainsKey(Tower)) return;
            // Towers stand to the side of the line between the camps, off the approach lanes.
            var across = Vector2.UnitX;
            if (world.TryGetRally(0, out var a) && world.TryGetRally(1, out var b) && Vector2.DistanceSquared(a, b) > 1f)
            {
                var along = Vector2.Normalize(b - a);
                across = new Vector2(-along.Y, along.X);
            }
            foreach (var point in points)
            {
                var site = new Site { Point = point, Spot = SpotFor(world, point, across) };
                site.Heading = SimMath.HeadingOf(point.Def.Position - site.Spot);
                _sites.Add(site);
                if (neutral) Raise(world, site, Teams.Hostile);
                else if (built && point.Owner >= 0) Raise(world, site, point.Owner);
            }
        }

        public void Tick(SimWorld world)
        {
            foreach (var site in _sites)
            {
                if (_neutral) TickNeutral(world, site);
                else TickHolder(world, site);
            }
        }

        private static void TickNeutral(SimWorld world, Site site)
        {
            if (world.TryGetVehicle(site.Tower, out var tower) && tower.IsAlive) return;
            if (site.Tower.IsValid)
            {
                site.Tower = default;
                site.BuildAt = world.Time + RespawnSeconds;
            }
            // It goes up again once nobody is standing on its footing.
            if (world.Time < site.BuildAt) return;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && !v.Flying && Vector2.DistanceSquared(v.Position, site.Spot) < 36f) return;
            Raise(world, site, Teams.Hostile);
        }

        private static void TickHolder(SimWorld world, Site site)
        {
            var owner = site.Point.Owner;
            var standing = world.TryGetVehicle(site.Tower, out var tower) && tower.IsAlive;
            if (standing && site.Team != owner)
            {
                // The point fell: its tower goes up with it.
                world.Damage.Apply(tower!, 1e7f, DamageType.HighExplosive);
                standing = false;
            }
            if (!standing && site.Tower.IsValid)
            {
                // Lost while the point is still held: rebuilt after a while.
                if (site.Team == owner && owner >= 0)
                {
                    site.Pending = owner;
                    site.BuildAt = world.Time + RebuildSeconds;
                }
                site.Tower = default;
                site.Team = -1;
            }
            if (standing || owner < 0)
            {
                if (owner < 0) site.Pending = -1;
                return;
            }
            if (site.Pending != owner)
            {
                site.Pending = owner;
                site.BuildAt = world.Time + BuildSeconds;
            }
            else if (world.Time >= site.BuildAt) Raise(world, site, owner);
        }

        /// <summary>The tower standing at a point, if any.</summary>
        public bool TryGetTower(SimWorld world, ObjectiveState point, out Vehicle tower)
        {
            foreach (var site in _sites)
                if (site.Point == point && world.TryGetVehicle(site.Tower, out tower!) && tower.IsAlive) return true;
            tower = null!;
            return false;
        }

        private static void Raise(SimWorld world, Site site, int team)
        {
            var tower = world.SpawnVehicle(Tower, team, site.Spot, site.Heading);
            if (team == Teams.Hostile)
            {
                tower.HpScale *= NeutralHealth;
                tower.Hp = tower.MaxHp;
            }
            world.AnchorDefence(tower);
            site.Tower = tower.Id;
            site.Team = team;
            site.Pending = -1;
        }

        /// <summary>Just outside the circle, on open ground with room round it, to one side of the lane.</summary>
        private static Vector2 SpotFor(SimWorld world, ObjectiveState point, Vector2 across)
        {
            var centre = point.Def.Position;
            var reach = point.Def.Radius + 3f;
            var start = MathF.Atan2(across.Y, across.X);
            for (var ring = 0; ring < 3; ring++)
                for (var i = 0; i < 16; i++)
                {
                    // Alternate sides of the lane, working round from square across it.
                    var step = (i + 1) / 2 * (i % 2 == 0 ? 1 : -1);
                    var angle = start + (i % 4 < 2 ? 0f : MathF.PI) + step * (MathF.PI / 8f);
                    var at = centre + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (reach + ring * 3f);
                    if (Open(world, at, 3f)) return at;
                }
            return centre + across * reach;
        }

        private static bool Open(SimWorld world, Vector2 at, float room)
        {
            if (!world.Map.Contains(at)) return false;
            for (var dx = -1; dx <= 1; dx++)
                for (var dy = -1; dy <= 1; dy++)
                    if (!world.Grid.IsWalkable(at + new Vector2(dx, dy) * room)) return false;
            return true;
        }
    }

    public sealed class KillLedger
    {
        private readonly Dictionary<EntityId, (int team, int cost, bool air, int baseCp)> _alive = new();
        private readonly int[] _lostBase = new int[2], _lostScore = new int[2];

        /// <summary>Prompt 30 L4: what one loss scores at most (Deathmatch: min(baseCP, 18)); 0: no cap.</summary>
        public int ScoreCap { get; set; }

        /// <summary>The base CP (no card-rank discount) the side has lost (Operations' losses, Endless's board).</summary>
        public int LostBaseCp(int team) => team is 0 or 1 ? _lostBase[team] : 0;

        /// <summary>The score the other side made from this side's losses: min(baseCP, <see cref="ScoreCap"/>) each.</summary>
        public int LostScore(int team) => team is 0 or 1 ? _lostScore[team] : 0;
        private readonly int[] _airLosses = new int[2];
        private readonly List<EntityId> _gone = new();
        private readonly HashSet<EntityId> _seen = new();
        private readonly int[] _losses = new int[2];
        private readonly int[] _lostCp = new int[2];

        /// <summary>Called for every loss: its team and CP cost.</summary>
        public event Action<int, int>? Lost;

        public int Losses(int team) => team is 0 or 1 ? _losses[team] : 0;

        public int LostCp(int team) => team is 0 or 1 ? _lostCp[team] : 0;

        /// <summary>Aircraft the other side lost.</summary>
        public int AirKills(int team) => team is 0 or 1 ? _airLosses[1 - team] : 0;

        /// <summary>Vehicles the other side lost.</summary>
        public int Kills(int team) => Losses(1 - team);

        /// <summary>Vehicles excluded from the count (a scripted convoy, a boss counted on its own).</summary>
        public Func<Vehicle, bool>? Ignore { get; set; }

        public void Update(SimWorld world)
        {
            _seen.Clear();
            foreach (var v in world.VehicleList)
            {
                // Prompt 32 L4: a Garrison HQ's squads score nothing (no Deathmatch points).
                if (!v.IsAlive || v.Team < 0 || v.Team > 1 || v.Garrison || v.Def.Wall || (Ignore != null && Ignore(v))) continue;
                _seen.Add(v.Id);
                if (!_alive.ContainsKey(v.Id)) _alive[v.Id] = (v.Team, v.Def.ArmyCost, v.Def.Flying, v.Def.BaseCp);
            }
            _gone.Clear();
            foreach (var id in _alive.Keys)
                if (!_seen.Contains(id)) _gone.Add(id);
            foreach (var id in _gone)
            {
                var (team, cost, air, baseCp) = _alive[id];
                _losses[team]++;
                _lostBase[team] += baseCp;
                _lostScore[team] += ScoreCap > 0 ? Math.Min(baseCp, ScoreCap) : baseCp;
                if (air) _airLosses[team]++;
                _lostCp[team] += cost;
                Lost?.Invoke(team, cost);
                _alive.Remove(id);
            }
        }
    }

    /// <summary>Command Points, deck and income for one side of a mode.</summary>
    /// <summary>The two sides' bases for a mode: each side's loadout and its role (by team).</summary>
    public sealed class BaseSetup
    {
        private readonly BaseLoadout?[] _loadouts = new BaseLoadout?[2];
        private readonly BaseRole[] _roles = { BaseRole.Anchor, BaseRole.Anchor };

        public BaseSetup Set(int team, BaseLoadout? loadout, BaseRole role)
        {
            if (team is < 0 or > 1) return this;
            _loadouts[team] = loadout;
            _roles[team] = role;
            return this;
        }

        public BaseLoadout? Loadout(int team) => team is 0 or 1 ? _loadouts[team] : null;

        public BaseRole Role(int team) => team is 0 or 1 ? _roles[team] : BaseRole.None;
    }

    public sealed class SideSetup
    {
        public float StartCp { get; set; } = 14f;

        /// <summary>CP per second.</summary>
        public float Income { get; set; } = 1f;

        /// <summary>The army supply in CP (upkeep above 1.5x it); 0: the data's for the mode.</summary>
        public int ArmyCap { get; set; }

        /// <summary>Most CP the side can hold unspent (a start or a bounty above it is not lost).</summary>
        public float Bank { get; set; } = 30f;

        public IReadOnlyList<string> Vehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> Supports { get; set; } = Array.Empty<string>();

        internal Economy.TeamEconomy Build(int team) =>
            new(team, StartCp, income: Income, bank: MathF.Max(Bank, StartCp), armyCap: ArmyCap, vehicles: Vehicles, supports: Supports);
    }
}
