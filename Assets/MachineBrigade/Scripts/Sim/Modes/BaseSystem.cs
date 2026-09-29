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

        /// <summary>
        /// Its next call is free (a Modular tower, the first of its type to fall this battle), and
        /// the wait before it is this share of the usual one (<see cref="FreeWait"/>).
        /// </summary>
        public bool FreeCall { get; internal set; }

        /// <summary>The share of the usual cooldown a free re-drop waits (0: none).</summary>
        public float FreeWait { get; internal set; } = 1f;

        /// <summary>The fortress ring (line) it stands in: 1 the outer line, 2 the walls, 3 the keep; 0 in a camp or an outpost.</summary>
        public int Ring { get; internal set; }

        /// <summary>Its ring is lost to the attacker: it is never flown back in.</summary>
        public bool Lost { get; internal set; }

        /// <summary>How much tougher and harder-hitting a tower raised here is (a fortress's inner lines).</summary>
        internal float HealthScale = 1f, DamageScale = 1f;
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

        /// <summary>Tower types (card ids) whose Modular free re-drop this battle has been used.</summary>
        public HashSet<string> ModularUsed { get; } = new();
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

        /// <summary>
        /// Diagnostics only (the stuck report's batch runs, prompt 12): replaces the loadout a mode
        /// gives a side's camp or fortress (team, the mode's loadout; null keeps it). Never set in play.
        /// </summary>
        public Func<int, BaseLoadout, BaseLoadout?>? LoadoutFor { get; set; }

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
            if (LoadoutFor?.Invoke(team, loadout) is { } swapped) loadout = swapped;
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
            // The hardpoints the HQ level opens: the first so many of each size (the map lists the
            // most important first), each taking the loadout's tower for that slot of that size.
            if (site != null)
            {
                var seen = new int[3];
                var utility = 0;
                for (var i = 0; i < site.Slots.Count; i++)
                {
                    var def = site.Slots[i];
                    if (def.Kind == HardpointKind.Utility)
                    {
                        if (utility++ >= catalog.Base.UtilitySlots(fitted.HqLevel)) continue;
                        var state = new HardpointState(def, i);
                        // A module past rank 7 works as its chosen branch (the landing pad's hangar or service, prompt 13 F.1).
                        if (utility - 1 < fitted.Utilities.Count && !string.IsNullOrEmpty(fitted.Utilities[utility - 1]))
                        {
                            var module = fitted.Utilities[utility - 1];
                            state.Tower = catalog.Vehicles.ContainsKey(fitted.DefFor(module)) ? fitted.DefFor(module) : module;
                        }
                        b.Slots.Add(state);
                        continue;
                    }
                    var k = seen[(int)def.Class]++;
                    if (k >= catalog.Base.Slots(fitted.HqLevel, def.Class)) continue;
                    var slot = new HardpointState(def, i);
                    var list = fitted.Of(def.Class);
                    // A tower past rank 7 fights as its chosen branch (it stays in its tower's slot).
                    if (k < list.Count && !string.IsNullOrEmpty(list[k])) slot.Tower =catalog.Vehicles.ContainsKey(fitted.DefFor(list[k])) ? fitted.DefFor(list[k]) : list[k];
                    b.Slots.Add(slot);
                }
            }
            foreach (var slot in b.Slots)
                if (slot.Tower != null) Raise(b, slot);
            return b;
        }

        /// <summary>
        /// A siege fortress as a side's base: no HQ of its own (the command HQ is a building the mode
        /// watches, at <paramref name="hq"/>), and every hardpoint of every ring filled from the
        /// loadout, its towers over again where the fortress has more hardpoints than the loadout has
        /// towers (<see cref="BaseLoadout.TowerForFortress"/>), each utility module once. A ring's
        /// towers are <paramref name="health"/> and <paramref name="damage"/> times the usual (by
        /// ring, 1 up): the inner lines are the stronger. With <paramref name="manning"/> under 1 only
        /// that share of the outer rings' tower hardpoints is filled. The modules work round the command HQ.
        /// </summary>
        public TeamBase EstablishFortress(int team, BaseLoadout loadout, BaseRole role, Vector2 hq, IReadOnlyList<FortressSlotDef> slots,
            IReadOnlyList<float>? health = null, IReadOnlyList<float>? damage = null, float manning = 1f)
        {
            var catalog = _world.Catalog;
            if (LoadoutFor?.Invoke(team, loadout) is { } swapped) loadout = swapped;
            // Prompt 17 B: the player's own layered base (Defend, Endless on a long battlefield) is laid out as a camp is:
            // the k-th base hardpoint of a size takes the loadout's k-th tower of that size while the HQ level (the long
            // table) opens it; its forward strongpoints repeat the towers. A fortress the AI holds fills every hardpoint.
            var layered = false;
            foreach (var s in slots) layered |= s.Hardpoint.Place != null;
            var exact = layered && role == BaseRole.Defend;
            if (exact && !loadout.Layered)
            {
                loadout = loadout.Clone();
                loadout.Layered = true;
            }
            var fitted = loadout.Fitted(catalog);
            var b = new TeamBase(team, role, fitted) { HqPosition = hq };
            _bases[team] = b;
            var seen = new int[3];
            var forward = new int[3];
            var utility = 0;
            for (var i = 0; i < slots.Count; i++)
            {
                var def = slots[i].Hardpoint;
                var ring = slots[i].Ring;
                string? id;
                if (exact && !def.Forward)
                {
                    if (def.Kind == HardpointKind.Utility)
                    {
                        var u = utility++;
                        if (u >= catalog.Base.UtilitySlots(fitted.HqLevel, true)) continue;
                        id = u < fitted.Utilities.Count && !string.IsNullOrEmpty(fitted.Utilities[u]) ? fitted.Utilities[u] : null;
                    }
                    else
                    {
                        var k = seen[(int)def.Class]++;
                        if (k >= catalog.Base.Slots(fitted.HqLevel, def.Class, true)) continue;
                        var list = fitted.Of(def.Class);
                        id = k < list.Count && !string.IsNullOrEmpty(list[k]) ? list[k] : null;
                    }
                }
                else if (exact)
                    id = fitted.TowerForFortress(def.Class, forward[(int)def.Class]++);
                else
                    id = def.Kind == HardpointKind.Utility ? fitted.UtilityForFortress(utility++) : fitted.TowerForFortress(def.Class, seen[(int)def.Class]++);
                var state = new HardpointState(def, i)
                {
                    Ring = ring, HealthScale = ByRing(health, ring), DamageScale = ByRing(damage, ring),
                };
                // An undermanned fortress (an easier one) leaves some tower hardpoints of its outer rings empty, spread evenly.
                if (def.Kind == HardpointKind.Tower && ring < 3 && manning < 1f && Unmanned(i, manning)) id = null;
                if (id != null && catalog.Vehicles.ContainsKey(fitted.DefFor(id))) id = fitted.DefFor(id);
                if (id != null && catalog.Vehicles.ContainsKey(id)) state.Tower = id;
                b.Slots.Add(state);
            }
            foreach (var slot in b.Slots)
                if (slot.Tower != null) Raise(b, slot);
            return b;
        }

        /// <summary>Whether the <paramref name="index"/>-th hardpoint stays empty when only <paramref name="manning"/> of them are filled (evenly spread).</summary>
        private static bool Unmanned(int index, float manning) => MathF.Floor((index + 1) * manning) == MathF.Floor(index * manning);

        private static float ByRing(IReadOnlyList<float>? scale, int ring) =>
            scale == null || scale.Count == 0 ? 1f : scale[Math.Clamp(ring - 1, 0, scale.Count - 1)];

        /// <summary>A fortress ring has fallen: its hardpoints are never flown back in.</summary>
        public void LoseRing(int team, int ring)
        {
            if (!_bases.TryGetValue(team, out var b)) return;
            foreach (var slot in b.Slots)
                if (slot.Ring == ring) slot.Lost = true;
        }

        /// <summary>A structure's footprint across (metres), as the hardpoint sizes count it.</summary>
        public static float Footprint(VehicleDef def) => MathF.Max(def.Length, def.Width);

        private void Raise(TeamBase b, HardpointState slot)
        {
            var tower = _world.SpawnVehicle(slot.Tower!, b.Team, slot.Def.Position, slot.Def.Facing);
            _world.AnchorDefence(tower);
            if (slot.HealthScale != 1f)
            {
                tower.HpScale *= slot.HealthScale;
                tower.Hp = tower.MaxHp;
            }
            tower.DamageBoost *= slot.DamageScale;
            slot.Structure = tower.Id;
            slot.Down = false;
            slot.LandsAt = double.NaN;
        }

        /// <summary>CP to fly a tower back into this hardpoint (nothing for a Modular tower's free re-drop).</summary>
        public int CostOf(HardpointState slot) =>
            !slot.FreeCall && slot.Tower != null && _world.Catalog.Vehicles.TryGetValue(slot.Tower, out var def) ? _world.Catalog.Base.RebuildCost(def) : 0;

        /// <summary>
        /// Modular (tower equipment): a tower that carries it has just been destroyed. If it is the
        /// first of its type (card) its side has lost this battle, its hardpoint's next call is free
        /// and waits <c>1 - cut</c> of the usual cooldown. Returns whether it was.
        /// </summary>
        internal bool FreeRedrop(Vehicle tower, float cut)
        {
            if (_clearingOutpost || !_bases.TryGetValue(tower.Team, out var b)) return false;
            var slot = SlotOf(b, tower.Id);
            if (slot == null || !b.ModularUsed.Add(tower.Def.CardId)) return false;
            slot.FreeCall = true;
            slot.FreeWait = Math.Clamp(1f - cut, 0f, 1f);
            return true;
        }

        private static HardpointState? SlotOf(TeamBase b, EntityId structure)
        {
            foreach (var s in b.Slots)
                if (s.Structure == structure) return s;
            foreach (var outpost in b.Outposts.Values)
                foreach (var s in outpost)
                    if (s.Structure == structure) return s;
            return null;
        }

        /// <summary>Whether a destroyed tower here can be called back in now.</summary>
        public bool CanCall(HardpointState slot) => slot.Down && !slot.Lost && !slot.Incoming && slot.Tower != null && _world.Time >= slot.ReadyAt;

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
                // Prompt 17 C: no CP relay on an outpost.
                if (!_world.Catalog.Vehicles.TryGetValue(command.DefId, out var pick) || pick.Fort is not { Kind: FortKind.Tower } || pick.Relay != null ||
                    Footprint(pick) > slot.Def.Size + 0.01f)
                    return CommandResult.Rejected(CommandError.UnknownCard);
                slot.Tower = command.DefId;
                slot.Down = true;
            }
            if (!CanCall(slot)) return CommandResult.Rejected(slot.Incoming || slot.Structure.IsValid ? CommandError.InvalidPoint : CommandError.OnCooldown);
            if (!_world.Economy.TrySpend(command.Team, CostOf(slot))) return CommandResult.Rejected(CommandError.NotEnoughCp);
            slot.FreeCall = false;
            slot.FreeWait = 1f;
            var rules = _world.Catalog.Base;
            slot.LandsAt = _world.Time + rules.RebuildDelay;
            slot.ReadyAt = _world.Time + rules.RebuildCooldown(_world.Catalog.Vehicles[slot.Tower!]);
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
            // The slots in the loadout's order, small first, whatever order the map lists them in.
            var hardpoints = new List<HardpointDef>();
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                foreach (var h in point.Value.Outpost)
                    if (h.Class == size) hardpoints.Add(h);
            var slots = new List<HardpointState>();
            var count = Math.Min(hardpoints.Count, _world.Catalog.Base.OutpostSlots);
            for (var i = 0; i < count; i++)
            {
                var slot = new HardpointState(hardpoints[i], i, id) { ReadyAt = _world.Time };
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
                        // Towers going down with a lost outpost never spend a Modular free re-drop.
                        _clearingOutpost = true;
                        foreach (var slot in slots)
                            if (_world.TryGetVehicle(slot.Structure, out var tower) && tower.IsAlive) _world.Damage.Apply(tower, 1e7f, DamageType.HighExplosive);
                        _clearingOutpost = false;
                        continue;
                    }
                    foreach (var slot in slots) Watch(b, slot);
                }
                foreach (var id in _lost) b.Outposts.Remove(id);
            }
        }

        private readonly List<string> _lost = new();
        private bool _clearingOutpost;

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
            var cooldown = slot.Tower != null && _world.Catalog.Vehicles.TryGetValue(slot.Tower, out var def) ? _world.Catalog.Base.RebuildCooldown(def) : 30f;
            // A Modular tower's free re-drop waits only its share of the cooldown, whatever the last call left.
            slot.ReadyAt = slot.FreeCall ? _world.Time + cooldown * slot.FreeWait : Math.Max(slot.ReadyAt, _world.Time + cooldown);
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
