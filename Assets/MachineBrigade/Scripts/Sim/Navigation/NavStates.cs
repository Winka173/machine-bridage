#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>One rectangle of ground a state closes (axis-aligned; grown by <see cref="Clearance"/> on every side, as a building's).</summary>
    public readonly struct NavBlock
    {
        public NavBlock(Vector2 center, float width, float depth, float clearance = SimWorld.ObstacleClearance)
        {
            Center = center;
            Width = width;
            Depth = depth;
            Clearance = clearance;
        }

        public Vector2 Center { get; }
        public float Width { get; }
        public float Depth { get; }
        public float Clearance { get; }

        /// <summary>The corners of the closed ground (with the clearance).</summary>
        public Vector2 Min => Center - new Vector2(Width * 0.5f + Clearance, Depth * 0.5f + Clearance);

        public Vector2 Max => Center + new Vector2(Width * 0.5f + Clearance, Depth * 0.5f + Clearance);
    }

    /// <summary>One named state of a site: the ground it closes (none: the site is open in this state).</summary>
    public sealed class NavStateDef
    {
        public NavStateDef(string name, IReadOnlyList<NavBlock>? blocks = null)
        {
            Name = name;
            Blocks = blocks ?? Array.Empty<NavBlock>();
        }

        public string Name { get; }
        public IReadOnlyList<NavBlock> Blocks { get; }
    }

    /// <summary>
    /// A switchable piece of ground (a factory gate, a shoal, a bridge, a wall segment of prompt 32): two or more named states,
    /// one of them in force at a time; <see cref="Initial"/> is in force when the battle loads.
    /// </summary>
    public sealed class NavSiteDef
    {
        public NavSiteDef(string id, IReadOnlyList<NavStateDef> states, string? initial = null)
        {
            if (string.IsNullOrEmpty(id)) throw new ArgumentException("A nav site needs an id.");
            if (states == null || states.Count < 2) throw new ArgumentException($"Nav site {id}: two or more states.");
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (var s in states)
                if (!names.Add(s.Name)) throw new ArgumentException($"Nav site {id}: state {s.Name} twice.");
            Id = id;
            States = states;
            Initial = initial ?? states[0].Name;
            if (!names.Contains(Initial)) throw new ArgumentException($"Nav site {id}: no state {Initial} to start in.");
        }

        public string Id { get; }
        public IReadOnlyList<NavStateDef> States { get; }
        public string Initial { get; }

        public int IndexOf(string name)
        {
            for (var i = 0; i < States.Count; i++)
                if (States[i].Name == name) return i;
            return -1;
        }
    }

    /// <summary>A site as the battle holds it: the state in force, the switch waiting for its tick, which states passed the checks.</summary>
    public sealed class NavSite
    {
        internal NavSite(NavSiteDef def, int index)
        {
            Def = def;
            Index = index;
            Active = def.IndexOf(def.Initial);
            Valid = new bool[def.States.Count];
            for (var i = 0; i < Valid.Length; i++) Valid[i] = true;
            Refusals = new string?[def.States.Count];
        }

        public NavSiteDef Def { get; }
        public string Id => Def.Id;
        internal int Index { get; }

        /// <summary>The state in force (its index in <see cref="NavSiteDef.States"/>).</summary>
        public int Active { get; internal set; }

        public string ActiveName => Def.States[Active].Name;

        /// <summary>The state a switch waits to bring in (-1: none) and the tick it comes in at.</summary>
        public int Pending { get; internal set; } = -1;

        public long PendingTick { get; internal set; }

        /// <summary>The tick of the last switch (-1: none yet).</summary>
        public long SwitchedAt { get; internal set; } = -1;

        internal readonly bool[] Valid;
        internal readonly string?[] Refusals;

        /// <summary>Whether the state passed the load-time checks (the anchors joined, no ground sealed off).</summary>
        public bool IsValid(int state) => state >= 0 && state < Valid.Length && Valid[state];

        /// <summary>Why a state was refused at load (null: it was not).</summary>
        public string? Refusal(int state) => state >= 0 && state < Refusals.Length ? Refusals[state] : null;
    }

    /// <summary>
    /// Prompt 31 L3 (DECISIONS "Prompt 31 L3"): the battlefield's prebuilt ground states. A site's states are all built when
    /// the battle loads (<see cref="Define"/>, before the first step) and checked once (<see cref="Validate"/>): with every
    /// other site as it stands, each state must keep the anchors (the rallies, the objectives) joined by a route and must not
    /// seal off open ground of theirs (a pocket bigger than <see cref="PocketCells"/>), or it is refused and never comes in.
    /// A switch only comes in at a tick boundary (<see cref="Schedule"/> names the tick; <see cref="Step"/> runs first thing in
    /// <see cref="SimWorld.Step"/>), in site order, so a battle and its replay switch on the same step. Ground it closes goes
    /// through <see cref="NavGrid.AddBlocker"/> (routes planned over it are planned again, the lanes rebuilt), and any ground
    /// vehicle left on closed ground, or cut off from the open battlefield it stood on, is put on the nearest open ground of
    /// the main region and plans its route again: a switch never traps a vehicle. The states in force are in the battle's
    /// fingerprint (<see cref="Mix"/>), so a checkpoint's replay restores them; <see cref="Snapshot"/> and
    /// <see cref="Restore"/> carry them for any other load.
    /// </summary>
    public sealed class NavStates
    {
        /// <summary>Open cells a state may cut off from the anchors' ground (slivers along a wall's clearance); more is sealing.</summary>
        public const int PocketCells = 6;

        private readonly NavGrid _grid;
        private readonly List<NavSite> _sites = new();
        private readonly Dictionary<string, NavSite> _byId = new(StringComparer.Ordinal);

        public NavStates(NavGrid grid) => _grid = grid;

        public IReadOnlyList<NavSite> Sites => _sites;

        /// <summary>The battle has stepped: no more sites may be defined.</summary>
        public bool Locked { get; private set; }

        /// <summary>Switches carried out so far.</summary>
        public int Switches { get; private set; }

        /// <summary>Vehicles put off ground a switch closed (tests and the stuck report).</summary>
        public int Displaced { get; private set; }

        /// <summary>Builds a site at load and puts its initial state in force. Throws once the battle has stepped.</summary>
        public NavSite Define(NavSiteDef def)
        {
            if (Locked) throw new InvalidOperationException($"Nav site {def.Id}: sites are built when the battle loads, not during it.");
            if (_byId.ContainsKey(def.Id)) throw new ArgumentException($"Nav site {def.Id} twice.");
            var site = new NavSite(def, _sites.Count);
            _sites.Add(site);
            _byId[def.Id] = site;
            foreach (var b in def.States[site.Active].Blocks) _grid.Mark(b, +1);
            return site;
        }

        public bool TryGet(string id, out NavSite site) => _byId.TryGetValue(id, out site!);

        /// <summary>The name of the state in force at a site (null: no such site).</summary>
        public string? ActiveOf(string id) => _byId.TryGetValue(id, out var s) ? s.ActiveName : null;

        /// <summary>Whether a site has the state and it passed the checks.</summary>
        public bool CanSwitch(string id, string state) => _byId.TryGetValue(id, out var s) && s.IsValid(s.Def.IndexOf(state));

        /// <summary>
        /// Asks for a site to go to a state at <paramref name="tick"/> (at least the next step's). False for an unknown site or
        /// state, or one refused at load. A later request for the same site replaces the waiting one; asking for the state in
        /// force cancels it.
        /// </summary>
        public bool Schedule(string id, string state, long tick, long now)
        {
            if (!_byId.TryGetValue(id, out var site)) return false;
            var index = site.Def.IndexOf(state);
            if (!site.IsValid(index)) return false;
            if (index == site.Active)
            {
                site.Pending = -1;
                return true;
            }
            site.Pending = index;
            site.PendingTick = Math.Max(tick, now + 1);
            return true;
        }

        /// <summary>
        /// The load-time check of every state of every site (the others as they stand). Returns the refusals (empty: all
        /// good); a refused state is marked and never comes in. <paramref name="anchors"/>: the points that must stay joined.
        /// </summary>
        public IReadOnlyList<string> Validate(IReadOnlyList<Vector2> anchors)
        {
            var problems = new List<string>();
            if (_sites.Count == 0) return problems;
            var n = _grid.Width * _grid.Height;
            var baseLabels = new int[n];
            var home = new int[anchors.Count];
            foreach (var site in _sites)
            {
                Labels(baseLabels);
                for (var k = 0; k < anchors.Count; k++) home[k] = AnchorRegion(anchors[k]);
                var main = anchors.Count > 0 && home[0] > 0 ? home[0] : _grid.MainRegion;
                for (var state = 0; state < site.Def.States.Count; state++)
                {
                    if (state == site.Active) continue;
                    Swap(site, site.Active, state, false);
                    var reason = Check(site, state, baseLabels, main, anchors, home);
                    Swap(site, state, site.Active, false);
                    if (reason == null) continue;
                    site.Valid[state] = false;
                    site.Refusals[state] = reason;
                    problems.Add($"nav site {site.Id} state {site.Def.States[state].Name}: {reason}");
                }
            }
            return problems;
        }

        private string? Check(NavSite site, int state, int[] baseLabels, int main, IReadOnlyList<Vector2> anchors, int[] home)
        {
            var now = new int[anchors.Count];
            for (var k = 0; k < anchors.Count; k++) now[k] = AnchorRegion(anchors[k]);
            for (var k = 0; k < anchors.Count; k++)
                for (var j = k + 1; j < anchors.Count; j++)
                    if (home[k] > 0 && home[k] == home[j] && now[k] != now[j])
                        return $"cuts ({anchors[k].X:0}, {anchors[k].Y:0}) off from ({anchors[j].X:0}, {anchors[j].Y:0})";
            var target = anchors.Count > 0 && now[0] > 0 ? now[0] : _grid.MainRegion;
            var sealedCells = new Dictionary<int, int>();
            for (var y = 0; y < _grid.Height; y++)
            for (var x = 0; x < _grid.Width; x++)
            {
                var i = _grid.Index(x, y);
                if (baseLabels[i] != main) continue;
                var r = _grid.RegionOf(x, y);
                if (r == 0 || r == target) continue;
                sealedCells[r] = sealedCells.TryGetValue(r, out var c) ? c + 1 : 1;
            }
            var total = 0;
            foreach (var kv in sealedCells)
                if (kv.Value > PocketCells) total += kv.Value;
            return total > 0 ? $"seals off {total} open cells" : null;
        }

        private void Labels(int[] into)
        {
            for (var y = 0; y < _grid.Height; y++)
            for (var x = 0; x < _grid.Width; x++)
                into[_grid.Index(x, y)] = _grid.RegionOf(x, y);
        }

        private int AnchorRegion(Vector2 p)
        {
            var r = _grid.RegionOf(p);
            if (r > 0) return r;
            return _grid.TryNearestWalkable(p, 5, out var open) ? _grid.RegionOf(open) : 0;
        }

        /// <summary>Takes one state's ground out and another's in; <paramref name="closing"/>: through AddBlocker (routes replanned).</summary>
        private void Swap(NavSite site, int from, int to, bool closing)
        {
            foreach (var b in site.Def.States[from].Blocks) _grid.Mark(b, -1);
            foreach (var b in site.Def.States[to].Blocks)
            {
                if (closing) _grid.AddBlocker(b.Center, b.Width, b.Depth, b.Clearance);
                else _grid.Mark(b, +1);
            }
        }

        /// <summary>First thing in a step: every switch due by this tick comes in (site order), and nobody is left trapped.</summary>
        internal void Step(SimWorld world)
        {
            Locked = true;
            foreach (var site in _sites)
            {
                if (site.Pending < 0 || site.PendingTick > world.Tick) continue;
                var to = site.Pending;
                site.Pending = -1;
                Switch(world, site, to);
            }
        }

        private readonly List<(Vehicle v, bool main)> _ground = new();

        private void Switch(SimWorld world, NavSite site, int to)
        {
            var mainBefore = _grid.MainRegion;
            _ground.Clear();
            foreach (var v in world.VehicleList)
                if (v.IsAlive && !v.Flying && !v.Def.Static && v.Def.Naval == null)
                    _ground.Add((v, _grid.RegionOf(v.Position) == mainBefore));
            Swap(site, site.Active, to, true);
            site.Active = to;
            site.SwitchedAt = world.Tick;
            Switches++;
            var main = _grid.MainRegion;
            foreach (var (v, wasMain) in _ground)
            {
                var region = _grid.RegionOf(v.Position);
                if (region != 0 && (region == main || !wasMain)) continue;
                if (!_grid.TryNearestInRegion(v.Position, main, 24, out var open)) continue;
                v.Position = open;
                v.Speed = 0f;
                Displaced++;
                Vehicle.PathTrace?.Invoke(v, "Put off ground a prebuilt state closed");
                if (v.HasPath) world.PathTo(v, v.PathGoal);
            }
        }

        /// <summary>The states in force (site id, state name), in site order: what a load needs.</summary>
        public IReadOnlyList<(string site, string state)> Snapshot()
        {
            var list = new List<(string, string)>();
            foreach (var s in _sites) list.Add((s.Id, s.ActiveName));
            return list;
        }

        /// <summary>
        /// A load: puts each named site straight into its state (no check of the vehicles: they are restored with it), and
        /// drops waiting switches. Unknown sites and states are skipped.
        /// </summary>
        public void Restore(IReadOnlyList<(string site, string state)> states)
        {
            foreach (var (id, name) in states)
            {
                if (!_byId.TryGetValue(id, out var site)) continue;
                var index = site.Def.IndexOf(name);
                site.Pending = -1;
                if (index < 0 || index == site.Active) continue;
                Swap(site, site.Active, index, true);
                site.Active = index;
            }
        }

        internal void Mix(Action<long> mix)
        {
            if (_sites.Count == 0) return;
            mix(Switches);
            foreach (var s in _sites) mix(s.Active * 1000 + s.Pending + 1);
        }
    }
}
