#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>
    /// Setting up a Sandbox battle (prompt 21 B): placing (one or a formation), turning, moving, copying and removing
    /// units, changing them one or many at a time, both sides' settings, and undo and redo of all of it. Every change
    /// keeps a copy of the scenario from before it, so undo gives back exactly what was there. The editor only
    /// changes the scenario; the screen builds the battle from it.
    /// </summary>
    public sealed class SandboxEditor
    {
        /// <summary>Changes remembered for undo.</summary>
        public const int UndoDepth = 100;

        private readonly Stack<string> _undo = new(), _redo = new();
        private readonly Catalog _catalog;
        private readonly Func<VehicleDef, bool>? _allowed;

        public SandboxEditor(Catalog catalog, MapDefinition map, SandboxScenario scenario, bool internalBuild, Func<VehicleDef, bool>? allowed = null)
        {
            _catalog = catalog;
            Map = map;
            Scenario = scenario;
            Internal = internalBuild;
            _allowed = internalBuild ? null : allowed;
        }

        public SandboxScenario Scenario { get; private set; }
        public MapDefinition Map { get; set; }

        /// <summary>The internal build: every unit, towers anywhere, the ceiling only a warning.</summary>
        public bool Internal { get; }

        /// <summary>Turning by any angle instead of the 15-degree step (B.4).</summary>
        public bool FreeRotation { get; set; }

        /// <summary>The side new units go to (B.2).</summary>
        public int Team { get; set; }

        /// <summary>The scenario changed (a placement, an undo, a setting).</summary>
        public event Action? Changed;

        public bool CanUndo => _undo.Count > 0;
        public bool CanRedo => _redo.Count > 0;

        /// <summary>The last placement went past the ceiling (the internal build only warns, B.10).</summary>
        public bool OverCapWarning { get; private set; }

        public IReadOnlyList<SandboxUnit> Units => Scenario.Units;

        private void Remember()
        {
            _undo.Push(Scenario.ToJson());
            if (_undo.Count > UndoDepth)
            {
                var keep = new List<string>(_undo);
                keep.RemoveAt(keep.Count - 1);
                _undo.Clear();
                for (var i = keep.Count - 1; i >= 0; i--) _undo.Push(keep[i]);
            }
            _redo.Clear();
        }

        private void Done() => Changed?.Invoke();

        public bool Undo()
        {
            if (_undo.Count == 0) return false;
            _redo.Push(Scenario.ToJson());
            Scenario = SandboxScenario.FromJson(_undo.Pop());
            Done();
            return true;
        }

        public bool Redo()
        {
            if (_redo.Count == 0) return false;
            _undo.Push(Scenario.ToJson());
            Scenario = SandboxScenario.FromJson(_redo.Pop());
            Done();
            return true;
        }

        /// <summary>A scenario opened in place of this one (a file, a code, a sample): undo goes back to what was here.</summary>
        public void Load(SandboxScenario scenario)
        {
            Remember();
            Scenario = scenario;
            Done();
        }

        /// <summary>The unit may be placed at all (the player version's limits; everything in the internal build).</summary>
        public bool Allowed(VehicleDef def) => _allowed == null || _allowed(def);

        private SandboxRefusal Check(VehicleDef def, int adding)
        {
            OverCapWarning = false;
            if (!Allowed(def)) return SandboxRefusal.Locked;
            if (SandboxRules.OverCap(_catalog, Scenario.Units, Team, def, adding))
            {
                if (!Internal) return SandboxRefusal.CapReached;
                OverCapWarning = true;
            }
            return SandboxRefusal.None;
        }

        /// <summary>A unit placed where tapped (B.4), facing <paramref name="heading"/>; <paramref name="index"/> is its place in the list.</summary>
        public SandboxRefusal Place(string defId, Vector2 at, float heading, out int index)
        {
            index = -1;
            if (!_catalog.Vehicles.TryGetValue(defId, out var def)) return SandboxRefusal.Unknown;
            var refusal = Check(def, 1);
            if (refusal != SandboxRefusal.None) return refusal;
            heading = SandboxRules.Snap(heading, FreeRotation);
            refusal = SandboxRules.Place(Map, def, Scenario.Units, at, Internal, out var spot, ref heading, _catalog);
            if (refusal != SandboxRefusal.None) return refusal;
            Remember();
            var unit = new SandboxUnit { Def = defId, Team = Team, Heading = heading, Position = spot };
            if (def.Boss) unit.Boss = new SandboxBossState();
            Scenario.Units.Add(unit);
            index = Scenario.Units.Count - 1;
            Done();
            return SandboxRefusal.None;
        }

        /// <summary>
        /// <paramref name="count"/> units in a formation round <paramref name="at"/>, all facing <paramref name="heading"/>
        /// (B.5); the ones that cannot stand (off the map, off the sea) are left out. The indices of those placed.
        /// </summary>
        public SandboxRefusal PlaceFormation(string defId, Vector2 at, float heading, SandboxFormation shape, int count, out List<int> placed)
        {
            placed = new List<int>();
            if (!_catalog.Vehicles.TryGetValue(defId, out var def)) return SandboxRefusal.Unknown;
            count = Math.Clamp(count, 1, 32);
            var refusal = Check(def, count);
            if (refusal != SandboxRefusal.None) return refusal;
            heading = SandboxRules.Snap(heading, FreeRotation);
            var spots = SandboxRules.Formation(shape, count, at, heading, SandboxRules.Spacing(def));
            var units = new List<SandboxUnit>();
            var last = SandboxRefusal.None;
            foreach (var p in spots)
            {
                var h = heading;
                var why = SandboxRules.Place(Map, def, Scenario.Units, p, Internal, out var spot, ref h, _catalog);
                if (why != SandboxRefusal.None)
                {
                    last = why;
                    continue;
                }
                // Towers snapped onto hardpoints never share one.
                if (SandboxRules.IsTower(def) && units.Exists(u => Vector2.Distance(u.Position, spot) < 1f)) continue;
                var unit = new SandboxUnit { Def = defId, Team = Team, Heading = h, Position = spot };
                if (def.Boss) unit.Boss = new SandboxBossState();
                units.Add(unit);
            }
            if (units.Count == 0) return last == SandboxRefusal.None ? SandboxRefusal.OffMap : last;
            Remember();
            foreach (var u in units)
            {
                Scenario.Units.Add(u);
                placed.Add(Scenario.Units.Count - 1);
            }
            Done();
            return SandboxRefusal.None;
        }

        private IEnumerable<SandboxUnit> Pick(IEnumerable<int> indices)
        {
            var seen = new HashSet<int>();
            foreach (var i in indices)
                if (i >= 0 && i < Scenario.Units.Count && seen.Add(i)) yield return Scenario.Units[i];
        }

        /// <summary>The units turned to face <paramref name="heading"/> (snapped unless free rotation is on).</summary>
        public void Rotate(IEnumerable<int> indices, float heading)
        {
            var list = new List<SandboxUnit>(Pick(indices));
            if (list.Count == 0) return;
            heading = SandboxRules.Snap(heading, FreeRotation);
            Remember();
            foreach (var u in list) u.Heading = heading;
            Done();
        }

        /// <summary>The units turned by <paramref name="degrees"/> each.</summary>
        public void RotateBy(IEnumerable<int> indices, float degrees)
        {
            var list = new List<SandboxUnit>(Pick(indices));
            if (list.Count == 0) return;
            Remember();
            foreach (var u in list) u.Heading = SandboxRules.Snap(u.Heading + degrees, FreeRotation);
            Done();
        }

        /// <summary>
        /// The units moved together so the first stands at <paramref name="to"/> (their places round it kept); each is
        /// checked as a placement (a ship stays on the sea, a tower on a free hardpoint). False when none could move.
        /// </summary>
        public bool Move(IReadOnlyList<int> indices, Vector2 to)
        {
            var list = new List<int>();
            foreach (var i in indices)
                if (i >= 0 && i < Scenario.Units.Count && !list.Contains(i)) list.Add(i);
            if (list.Count == 0) return false;
            var delta = to - Scenario.Units[list[0]].Position;
            var moves = new List<(SandboxUnit unit, Vector2 spot, float heading)>();
            foreach (var i in list)
            {
                var u = Scenario.Units[i];
                if (!_catalog.Vehicles.TryGetValue(u.Def, out var def)) continue;
                var h = u.Heading;
                if (SandboxRules.Place(Map, def, Scenario.Units, u.Position + delta, Internal, out var spot, ref h, _catalog, skip: i) != SandboxRefusal.None) continue;
                moves.Add((u, spot, h));
            }
            if (moves.Count == 0) return false;
            Remember();
            foreach (var (u, spot, h) in moves)
            {
                u.Position = spot;
                u.Heading = h;
            }
            Done();
            return true;
        }

        /// <summary>Copies of the units, <paramref name="offset"/> away (B.9); the copies' indices.</summary>
        public List<int> Copy(IEnumerable<int> indices, Vector2 offset)
        {
            var added = new List<int>();
            var copies = new List<SandboxUnit>();
            foreach (var u in Pick(indices))
            {
                if (!_catalog.Vehicles.TryGetValue(u.Def, out var def) || !Allowed(def)) continue;
                var copy = u.Clone();
                var h = copy.Heading;
                if (SandboxRules.Place(Map, def, Scenario.Units, u.Position + offset, Internal, out var spot, ref h, _catalog) != SandboxRefusal.None) continue;
                if (!Internal && SandboxRules.OverCap(_catalog, Scenario.Units, u.Team, def, 1 + copies.FindAll(c => c.Team == u.Team).Count)) continue;
                copy.Position = spot;
                copy.Heading = h;
                copies.Add(copy);
            }
            if (copies.Count == 0) return added;
            Remember();
            foreach (var c in copies)
            {
                Scenario.Units.Add(c);
                added.Add(Scenario.Units.Count - 1);
            }
            Done();
            return added;
        }

        /// <summary>The units taken off the field (B.9).</summary>
        public void Delete(IEnumerable<int> indices)
        {
            var remove = new List<int>();
            foreach (var i in indices)
                if (i >= 0 && i < Scenario.Units.Count && !remove.Contains(i)) remove.Add(i);
            if (remove.Count == 0) return;
            Remember();
            remove.Sort();
            for (var k = remove.Count - 1; k >= 0; k--) Scenario.Units.RemoveAt(remove[k]);
            Done();
        }

        /// <summary>
        /// A change to the units (B.6: rank, equipment, elite, health, ammunition, a boss's state), one or many at a
        /// time. A tower under rank 7 loses its branch (tower branches open at rank 7).
        /// </summary>
        public void Edit(IEnumerable<int> indices, Action<SandboxUnit> change)
        {
            var list = new List<SandboxUnit>(Pick(indices));
            if (list.Count == 0) return;
            Remember();
            foreach (var u in list)
            {
                change(u);
                u.Rank = Math.Clamp(u.Rank, 1, SandboxRules.MaxRank);
                u.Hp = Math.Clamp(u.Hp, 1, 100);
                u.Ammo = Math.Clamp(u.Ammo, 0, 100);
                if (_catalog.Vehicles.TryGetValue(u.Def, out var def) && def.BranchOf != null && u.Rank < SandboxRules.BranchRank) u.Def = def.BranchOf;
                if (_catalog.Vehicles.TryGetValue(u.Def, out def) && def.Boss) u.Boss ??= new SandboxBossState();
            }
            Done();
        }

        /// <summary>
        /// A tower's rank-7 branch (null: the tower itself): the unit fights as the branch's def. Refused (false) under
        /// rank 7 or for a branch that is not this tower's.
        /// </summary>
        public bool SetBranch(int index, string? branch)
        {
            if (index < 0 || index >= Scenario.Units.Count) return false;
            var u = Scenario.Units[index];
            if (!_catalog.Vehicles.TryGetValue(u.Def, out var def)) return false;
            var tower = def.BranchOf ?? def.Id;
            if (branch == null)
            {
                if (u.Def == tower) return true;
                Edit(new[] { index }, x => x.Def = tower);
                return true;
            }
            if (u.Rank < SandboxRules.BranchRank || !SandboxRules.Branches(_catalog, tower).Contains(branch)) return false;
            if (_catalog.Vehicles.TryGetValue(branch, out var b) && !Allowed(b)) return false;
            Edit(new[] { index }, x => x.Def = branch);
            return true;
        }

        /// <summary>A change to the battle's settings (map, weather, sides, seed...).</summary>
        public void Settings(Action<SandboxScenario> change)
        {
            Remember();
            change(Scenario);
            Done();
        }

        /// <summary>The unit nearest <paramref name="at"/> within <paramref name="reach"/> metres (a tap), or -1.</summary>
        public int NearestUnit(Vector2 at, float reach)
        {
            var best = -1;
            var bestD = reach * reach;
            for (var i = 0; i < Scenario.Units.Count; i++)
            {
                var d = Vector2.DistanceSquared(Scenario.Units[i].Position, at);
                if (d >= bestD) continue;
                bestD = d;
                best = i;
            }
            return best;
        }
    }
}
