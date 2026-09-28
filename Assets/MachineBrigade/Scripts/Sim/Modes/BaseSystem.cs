#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>One hardpoint in play: what stands in it (or stood, before it was knocked down), and when it can be flown back in.</summary>
    public sealed class HardpointState
    {
        internal HardpointState(HardpointDef def, int index, string? pointId = null)
        {
            Def = def;
            Index = index;
            PointId = pointId;
        }

        public HardpointDef Def { get; }

        /// <summary>Its place in the camp's list (outposts: in the outpost's).</summary>
        public int Index { get; }

        /// <summary>The capture point of an outpost's hardpoint; null in the camp.</summary>
        public string? PointId { get; }

        /// <summary>The tower (or module) the loadout put here; null for an empty hardpoint.</summary>
        public string? Tower { get; internal set; }

        /// <summary>The structure standing in it now (None while it is down or empty).</summary>
        public EntityId Structure { get; internal set; }

        /// <summary>It had a structure that was destroyed (and not yet flown back in).</summary>
        public bool Down { get; internal set; }

        /// <summary>When it can be called back in (after it went down, or after the last call).</summary>
        public double ReadyAt { get; internal set; }

        /// <summary>A replacement is on its way down: when it lands (NaN: none).</summary>
        public double LandsAt { get; internal set; } = double.NaN;

        public bool Incoming => !double.IsNaN(LandsAt);
    }

    /// <summary>A side's base in the battle: its role, its HQ, its hardpoints and its outposts.</summary>
    public sealed class TeamBase
    {
        internal TeamBase(int team, BaseRole role, BaseLoadout loadout)
        {
            Team = team;
            Role = role;
            Loadout = loadout;
        }

        public int Team { get; }
        public BaseRole Role { get; }
        public BaseLoadout Loadout { get; }
        public EntityId Hq { get; internal set; }
        public Vector2 HqPosition { get; internal set; }

        public List<HardpointState> Slots { get; } = new();

        /// <summary>Outposts set up on captured points, by point id.</summary>
        public Dictionary<string, List<HardpointState>> Outposts { get; } = new();

        /// <summary>The HQ was destroyed (only a Target or Defend base can be).</summary>
        public bool HqFallen { get; internal set; }
    }

    /// <summary>
    /// Bases as a loadout (both sides): each side's HQ stands in its camp with the drop zone round
    /// it, its towers in the camp's hardpoints (map data) as its loadout lists them, front ones
    /// first. Towers can be destroyed; a destroyed tower can be flown back in during the battle for
    /// CP (points x 1 CP) once its cooldown is over. Whether the HQ itself can fall depends on the
    /// mode (<see cref="BaseRole"/>). In the campaign, a captured point marked as an outpost can
    /// be set up as one: 1-2 hardpoints for towers flown in with CP, and a second drop zone.
    /// </summary>
    public sealed class BaseSystem
    {
        private readonly SimWorld _world;
        private readonly Dictionary<int, TeamBase> _bases = new();
        private readonly List<HardpointState> _scratch = new();

        public BaseSystem(SimWorld world) => _world = world;

        public TeamBase? Of(int team) => _bases.TryGetValue(team, out var b) ? b : null;

        public BaseRole RoleOf(int team) => _bases.TryGetValue(team, out var b) ? b.Role : BaseRole.None;

        public IEnumerable<TeamBase> All => _bases.Values;

        /// <summary>Who owns a capture point (set by the mode; -1 neutral), for outposts.</summary>
        public Func<string, int>? PointOwner { get; set; }

        /// <summary>The capture points that may be set up as outposts (a campaign mission's list; empty: none).</summary>
        public HashSet<string> OutpostPoints { get; } = new();

        /// <summary>
        /// Extra forward drop zones a side has now (a command vehicle standing still), nearest the
        /// enemy first; null for none.
        /// </summary>
        public Func<int, Vector2?>? ForwardZone { get; set; }

        /// <summary>
        /// A side with no camp of its own (a campaign mission) that can still set up outposts: a
        /// base with no HQ and no hardpoints. Leaves an existing base alone.
        /// </summary>
        public TeamBase Ensure(int team, BaseLoadout loadout)
        {
            if (_bases.TryGetValue(team, out var existing)) return existing;
            var b = new TeamBase(team, BaseRole.None, loadout.Fitted(_world.Catalog));
            _world.TryGetRally(team, out var rally);
            b.HqPosition = rally;
            _bases[team] = b;
            return b;
        }

        /// <summary>
        /// Sets a side's base up: its HQ at the camp's spot in the map data (or behind its rally
        /// point on a map without one) and the loadout's towers in the hardpoints, front first,
        /// each where it fits. An Anchor HQ cannot be destroyed.
        /// </summary>
        public TeamBase Establish(int team, BaseLoadout loadout, BaseRole role, int? siteTeam = null)
        {
            var catalog = _world.Catalog;
            var fitted = loadout.Fitted(catalog);
            var b = new TeamBase(team, role, fitted);
            _bases[team] = b;
            // The camp in the map data (a siege's attacker camp is the map's side 0, whichever side attacks).
            var site = _world.Map.BaseOf(siteTeam ?? team);
            _world.TryGetRally(team, out var rally);
            var away = rally.LengthSquared() > 1f ? Vector2.Normalize(rally) : -Vector2.UnitX;
            var hqAt = site?.Hq ?? _world.ClampToMap(rally + away * 12f);
            var heading = site?.Heading ?? SimMath.HeadingOf(-away);
            if (catalog.Vehicles.ContainsKey(catalog.Base.HqId))
            {
                var hq = _world.SpawnVehicle(catalog.Base.HqId, team, hqAt, heading);
                hq.Invulnerable = role == BaseRole.Anchor;
                _world.AnchorDefence(hq);
                b.Hq = hq.Id;
            }
            b.HqPosition = hqAt;
            if (site != null)
                for (var i = 0; i < site.Slots.Count; i++)
                    b.Slots.Add(new HardpointState(site.Slots[i], i));
            // The towers, in order, each into the first free hardpoint of its kind it fits.
            Assign(b, fitted.Towers, HardpointKind.Tower);
            Assign(b, fitted.Utilities, HardpointKind.Utility);
            foreach (var slot in b.Slots)
                if (slot.Tower != null) Raise(b, slot);
            return b;
        }

        private void Assign(TeamBase b, List<string> ids, HardpointKind kind)
        {
            foreach (var id in ids)
            {
                var def = _world.Catalog.Vehicles[id];
                foreach (var slot in b.Slots)
                {
                    if (slot.Tower != null || slot.Def.Kind != kind || Footprint(def) > slot.Def.Size + 0.01f) continue;
                    slot.Tower = id;
                    break;
                }
            }
        }

        /// <summary>A structure's footprint across (metres), as the hardpoint sizes count it.</summary>
        public static float Footprint(VehicleDef def) => MathF.Max(def.Length, def.Width);

        private void Raise(TeamBase b, HardpointState slot)
        {
            var tower = _world.SpawnVehicle(slot.Tower!, b.Team, slot.Def.Position, slot.Def.Facing);
            _world.AnchorDefence(tower);
            slot.Structure = tower.Id;
            slot.Down = false;
            slot.LandsAt = double.NaN;
        }

        /// <summary>CP to fly a tower back into this hardpoint.</summary>
        public int CostOf(HardpointState slot) =>
            slot.Tower != null && _world.Catalog.Vehicles.TryGetValue(slot.Tower, out var def) ? _world.Catalog.Base.RebuildCost(def) : 0;

        /// <summary>Whether a destroyed tower here can be called back in now.</summary>
        public bool CanCall(HardpointState slot) => slot.Down && !slot.Incoming && slot.Tower != null && _world.Time >= slot.ReadyAt;

        /// <summary>The destroyed hardpoints of a side that can be called back in now, front first (camp, then outposts).</summary>
        public IReadOnlyList<HardpointState> Callable(int team)
        {
            _scratch.Clear();
            if (!_bases.TryGetValue(team, out var b)) return _scratch;
            foreach (var slot in b.Slots)
                if (CanCall(slot)) _scratch.Add(slot);
            foreach (var outpost in b.Outposts.Values)
                foreach (var slot in outpost)
                    if (CanCall(slot)) _scratch.Add(slot);
            return _scratch;
        }

        /// <summary>
        /// Flies a tower into a hardpoint (Command.Point: the hardpoint's position): a destroyed
        /// one back in, or an outpost's empty one (Command.DefId may pick the tower for an outpost
        /// hardpoint from the loadout's outpost list). Costs CP; the tower lands after a short delay.
        /// </summary>
        public CommandResult CallTower(Command command)
        {
            if (!_bases.TryGetValue(command.Team, out var b)) return CommandResult.Rejected(CommandError.NotAvailable);
            var slot = Nearest(b, command.Point);
            if (slot == null) return CommandResult.Rejected(CommandError.InvalidPoint);
            if (slot.PointId != null && command.DefId != null && slot.Tower == null)
            {
                if (!_world.Catalog.Vehicles.TryGetValue(command.DefId, out var pick) || pick.Fort is not { Kind: FortKind.Tower } ||
                    Footprint(pick) > slot.Def.Size + 0.01f)
                    return CommandResult.Rejected(CommandError.UnknownCard);
                slot.Tower = command.DefId;
                slot.Down = true;
            }
            if (!CanCall(slot)) return CommandResult.Rejected(slot.Incoming || slot.Structure.IsValid ? CommandError.InvalidPoint : CommandError.OnCooldown);
            if (!_world.Economy.TrySpend(command.Team, CostOf(slot))) return CommandResult.Rejected(CommandError.NotEnoughCp);
            var rules = _world.Catalog.Base;
            slot.LandsAt = _world.Time + rules.RebuildDelay;
            slot.ReadyAt = _world.Time + rules.RebuildCooldown;
            _world.Emit(SimEvent.DeploymentQueued(command.Team, slot.Tower!, slot.Def.Position, SimMath.Forward(slot.Def.Facing), rules.RebuildDelay));
            return CommandResult.Ok;
        }

        private static HardpointState? Nearest(TeamBase b, Vector2 at)
        {
            HardpointState? best = null;
            var bestD = 8f * 8f;
            void Look(HardpointState s)
            {
                var d = Vector2.DistanceSquared(s.Def.Position, at);
                if (d >= bestD) return;
                bestD = d;
                best = s;
            }
            foreach (var s in b.Slots) Look(s);
            foreach (var outpost in b.Outposts.Values)
                foreach (var s in outpost) Look(s);
            return best;
        }

        /// <summary>
        /// Sets a captured point up as an outpost (Command.DefId: the point): it must be one the
        /// mission marks, held by the side, with hardpoints in the map data. Costs CP; its
        /// hardpoints can then take towers, and it becomes a second drop zone.
        /// </summary>
        public CommandResult SetUpOutpost(Command command)
        {
            if (!_bases.TryGetValue(command.Team, out var b) || command.DefId == null) return CommandResult.Rejected(CommandError.NotAvailable);
            var id = command.DefId;
            if (!OutpostPoints.Contains(id) || b.Outposts.ContainsKey(id)) return CommandResult.Rejected(CommandError.InvalidPoint);
            if (PointOwner == null || PointOwner(id) != command.Team) return CommandResult.Rejected(CommandError.InvalidPoint);
            CapturePointDef? point = null;
            foreach (var p in _world.Map.Points)
                if (p.Id == id) point = p;
            if (point == null || point.Value.Outpost.Count == 0) return CommandResult.Rejected(CommandError.InvalidPoint);
            if (!_world.Economy.TrySpend(command.Team, _world.Catalog.Base.OutpostCp)) return CommandResult.Rejected(CommandError.NotEnoughCp);
            var slots = new List<HardpointState>();
            var count = Math.Min(point.Value.Outpost.Count, _world.Catalog.Base.OutpostSlots);
            for (var i = 0; i < count; i++)
            {
                var slot = new HardpointState(point.Value.Outpost[i], i, id) { ReadyAt = _world.Time };
                slots.Add(slot);
            }
            b.Outposts[id] = slots;
            _world.Emit(SimEvent.Alert(point.Value.Position, command.Team == 0 ? "alert.outpost.ours" : "alert.outpost.theirs"));
            return CommandResult.Ok;
        }

        /// <summary>
        /// Where a side's bought vehicles land: its most forward outpost (nearest the enemy), a
        /// forward zone of its own (a command vehicle), else its rally point.
        /// </summary>
        public bool TryGetDropZone(int team, out Vector2 zone)
        {
            if (!_world.TryGetRally(team, out zone)) return false;
            var enemy = _world.TryGetRally(1 - team, out var e) ? e : -zone;
            var best = Vector2.Distance(zone, enemy);
            if (ForwardZone?.Invoke(team) is { } forward && Vector2.Distance(forward, enemy) < best)
            {
                zone = forward;
                best = Vector2.Distance(forward, enemy);
            }
            // A command vehicle that has stood still long enough: deliveries land beside it (on its home side).
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != team || v.Def.ForwardDrop <= 0f || v.IsMoving || v.Stunned) continue;
                if (_world.Time - v.StillSince < v.Def.ForwardDrop) continue;
                var back = zone - v.Position;
                var spot = _world.ClampToMap(v.Position + (back.LengthSquared() > 1f ? Vector2.Normalize(back) : Vector2.Zero) * 7f);
                var d = Vector2.Distance(spot, enemy);
                if (d >= best) continue;
                best = d;
                zone = spot;
            }
            if (!_bases.TryGetValue(team, out var b)) return true;
            foreach (var (id, _) in b.Outposts)
                foreach (var p in _world.Map.Points)
                {
                    if (p.Id != id) continue;
                    var d = Vector2.Distance(p.Position, enemy);
                    if (d >= best) continue;
                    best = d;
                    zone = p.Position;
                }
            return true;
        }

        public void Step()
        {
            foreach (var b in _bases.Values)
            {
                if (b.Hq.IsValid && !b.HqFallen && (!_world.TryGetVehicle(b.Hq, out var hq) || !hq.IsAlive)) b.HqFallen = true;
                foreach (var slot in b.Slots) Watch(b, slot);
                // An outpost lost with its point: its towers go with it.
                _lost.Clear();
                foreach (var (id, slots) in b.Outposts)
                {
                    if (PointOwner != null && PointOwner(id) != b.Team)
                    {
                        _lost.Add(id);
                        foreach (var slot in slots)
                            if (_world.TryGetVehicle(slot.Structure, out var tower) && tower.IsAlive) _world.Damage.Apply(tower, 1e7f, DamageType.HighExplosive);
                        continue;
                    }
                    foreach (var slot in slots) Watch(b, slot);
                }
                foreach (var id in _lost) b.Outposts.Remove(id);
            }
        }

        private readonly List<string> _lost = new();

        private void Watch(TeamBase b, HardpointState slot)
        {
            if (slot.Incoming && _world.Time >= slot.LandsAt)
            {
                Raise(b, slot);
                return;
            }
            if (!slot.Structure.IsValid || (_world.TryGetVehicle(slot.Structure, out var tower) && tower.IsAlive)) return;
            // Knocked down: it can be called back in once the cooldown is over.
            slot.Structure = EntityId.None;
            slot.Down = true;
            slot.ReadyAt = Math.Max(slot.ReadyAt, _world.Time + _world.Catalog.Base.RebuildCooldown);
        }

        /// <summary>Every tower standing in a side's base (camp and outposts).</summary>
        public IEnumerable<Vehicle> Towers(int team)
        {
            if (!_bases.TryGetValue(team, out var b)) yield break;
            foreach (var slot in b.Slots)
                if (_world.TryGetVehicle(slot.Structure, out var t) && t.IsAlive) yield return t;
            foreach (var outpost in b.Outposts.Values)
                foreach (var slot in outpost)
                    if (_world.TryGetVehicle(slot.Structure, out var t) && t.IsAlive) yield return t;
        }
    }
}
