#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>The unit picker's tabs (prompt 21 B.3).</summary>
    public enum SandboxTab
    {
        Vehicles,
        Air,
        Towers,
        Bosses,
        MiniBosses,
        Elites,
        Ships,
    }

    /// <summary>Formations for placing several at once (prompt 21 B.5).</summary>
    public enum SandboxFormation
    {
        Line,
        Column,
        Cluster,
        Arc,
    }

    /// <summary>Why a placement was refused (prompt 21 B.4, B.10).</summary>
    public enum SandboxRefusal
    {
        None,
        Unknown,
        OffMap,
        NotOnSea,
        NoSea,
        NotOnHardpoint,
        HardpointTaken,
        CapReached,
        Locked,
    }

    /// <summary>
    /// The Sandbox's placement rules and picker (prompt 21 B): which tab a unit is in, where it may stand (aircraft
    /// at their flying height, ships on a sea lane, towers on a hardpoint or anywhere on the flat test map and in the
    /// internal build), the rotation step, formations and the unit ceiling. Pure functions of the scenario and the
    /// catalog, so tests use them as the screen does.
    /// </summary>
    public static class SandboxRules
    {
        /// <summary>The rotation step (B.4): about 15 degrees unless free rotation is on.</summary>
        public const float RotationStep = 15f;

        /// <summary>The starting ceiling per side (B.10): 64 ground vehicles and 12 aircraft.</summary>
        public static int VehicleCap => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.VehicleCap;
        public static int AircraftCap => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.AircraftCap;

        /// <summary>A tap this close to a free hardpoint snaps the tower onto it.</summary>
        public const float HardpointSnap = 8f;

        /// <summary>Positions are kept to the centimetre so a scenario saved and read back is the same scenario.</summary>
        public static float Round(float v) => MathF.Round(v * 100f) / 100f;

        /// <summary>An angle in [0, 360).</summary>
        public static float Normalise(float degrees)
        {
            degrees %= 360f;
            if (degrees < 0f) degrees += 360f;
            return MathF.Round(degrees * 10f) / 10f % 360f;
        }

        /// <summary>A heading snapped to the rotation step (or kept to a tenth of a degree when <paramref name="free"/>).</summary>
        public static float Snap(float degrees, bool free) => free ? Normalise(degrees) : Normalise(MathF.Round(degrees / RotationStep) * RotationStep);

        /// <summary>The heading (degrees, 0 north, clockwise) from a unit to where the drag is (B.4).</summary>
        public static float HeadingTowards(Vector2 from, Vector2 to, bool free) =>
            Vector2.DistanceSquared(from, to) < 1e-6f ? 0f : Snap(Core.SimMath.HeadingOf(to - from) * 180f / MathF.PI, free);

        /// <summary>The tab a unit is picked from; null for what is never placed by hand (a tower's branch, a drone).</summary>
        public static SandboxTab? TabOf(VehicleDef def)
        {
            if (def.BranchOf != null || def.Drone) return null;
            if (def.Boss) return def.MiniBoss ? SandboxTab.MiniBosses : SandboxTab.Bosses;
            if (def.Naval != null) return SandboxTab.Ships;
            if (def.Elite) return SandboxTab.Elites;
            if (def.Static || def.Fort != null) return SandboxTab.Towers;
            return def.Flying ? SandboxTab.Air : SandboxTab.Vehicles;
        }

        /// <summary>Counts against the aircraft ceiling (else the vehicle ceiling; towers count against neither).</summary>
        public static bool IsAircraft(VehicleDef def) => def.Flying;

        public static bool IsTower(VehicleDef def) => def.Static || def.Fort != null;

        /// <summary>A tower's rank-7 branches (tower branches, DECISIONS 19T): the defs that fight as it, in id order.</summary>
        public static List<string> Branches(Catalog catalog, string towerId)
        {
            var list = new List<string>();
            foreach (var def in catalog.Vehicles.Values)
                if (def.BranchOf == towerId) list.Add(def.Id);
            list.Sort(StringComparer.Ordinal);
            return list;
        }

        /// <summary>The rank from which a tower's branch may be chosen (the tower cards' own rule).</summary>
        public const int BranchRank = Modes.TowerCards.BranchRank;

        /// <summary>The highest card rank (the game's CardRanks.Max).</summary>
        public static int MaxRank => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.MaxRank;

        /// <summary>
        /// The picker's list for a tab (B.3), filtered: a name that contains <paramref name="search"/> (by
        /// <paramref name="name"/>, the language's name), a branch, an armour level (the front's, 0-4) and a damage
        /// type of the main weapon; <paramref name="allowed"/> the player version's limits (null: everything).
        /// Sorted by price then id, so the list is the same everywhere.
        /// </summary>
        public static List<VehicleDef> Palette(Catalog catalog, SandboxTab tab, Func<string, string>? name = null, string? search = null,
            ArmyBranch? branch = null, int? armour = null, DamageType? damage = null, Func<VehicleDef, bool>? allowed = null)
        {
            var list = new List<VehicleDef>();
            var needle = string.IsNullOrWhiteSpace(search) ? null : search!.Trim();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (TabOf(def) != tab) continue;
                if (allowed != null && !allowed(def)) continue;
                if (branch != null && def.Branch != branch) continue;
                if (armour != null && def.Armour.Front != armour) continue;
                if (damage != null && def.Weapon.DamageType != damage) continue;
                if (needle != null)
                {
                    var shown = name?.Invoke(def.Id) ?? def.Id;
                    if (shown.IndexOf(needle, StringComparison.OrdinalIgnoreCase) < 0 && def.Id.IndexOf(needle, StringComparison.OrdinalIgnoreCase) < 0) continue;
                }
                list.Add(def);
            }
            list.Sort((a, b) => a.CpCost != b.CpCost ? a.CpCost.CompareTo(b.CpCost) : string.CompareOrdinal(a.Id, b.Id));
            return list;
        }

        /// <summary>
        /// Where a unit of <paramref name="def"/> tapped at <paramref name="at"/> goes (B.4), or why it cannot: a ship
        /// onto the nearest sea lane; a tower onto the nearest free hardpoint that takes its size (anywhere on the flat
        /// test map, or with <paramref name="anywhere"/>, the internal build); everything else where it was tapped.
        /// <paramref name="heading"/> becomes a hardpoint's facing for a tower snapped onto one.
        /// </summary>
        public static SandboxRefusal Place(MapDefinition map, VehicleDef def, IReadOnlyList<SandboxUnit> placed, Vector2 at, bool anywhere,
            out Vector2 spot, ref float heading, Catalog? catalog = null, int skip = -1)
        {
            spot = at;
            if (!map.Contains(at)) return SandboxRefusal.OffMap;
            if (def.Naval != null)
            {
                if (map.Sea is not { } sea) return SandboxRefusal.NoSea;
                if (!sea.IsSea(at, 2f)) return SandboxRefusal.NotOnSea;
                var f = sea.Frame(at);
                SeaLaneDef? best = null;
                foreach (var lane in sea.Lanes)
                    if (best == null || MathF.Abs(lane.W - f.Y) < MathF.Abs(best.W - f.Y)) best = lane;
                if (best != null) spot = sea.At(Math.Clamp(f.X, -best.Patrol, best.Patrol), best.W);
                if (!map.Contains(spot)) spot = at;
                return SandboxRefusal.None;
            }
            if (IsTower(def) && !anywhere && !SandboxMaps.IsFlat(map.Id))
            {
                HardpointDef? chosen = null;
                var bestDistance = HardpointSnap;
                foreach (var site in map.Bases)
                    foreach (var slot in site.Slots)
                    {
                        if (slot.Kind != HardpointKind.Tower && def.Fort?.Kind == FortKind.Tower) continue;
                        if (def.Fort != null && !def.Fort.Fits(slot.Class)) continue;
                        var d = Vector2.Distance(slot.Position, at);
                        if (d >= bestDistance) continue;
                        bestDistance = d;
                        chosen = slot;
                    }
                if (chosen is not { } hp) return SandboxRefusal.NotOnHardpoint;
                for (var i = 0; i < placed.Count; i++)
                {
                    if (i == skip || catalog == null || !catalog.Vehicles.TryGetValue(placed[i].Def, out var other) || !IsTower(other)) continue;
                    if (Vector2.Distance(placed[i].Position, hp.Position) < 1f) return SandboxRefusal.HardpointTaken;
                }
                spot = hp.Position;
                heading = Normalise(hp.Facing);
            }
            return SandboxRefusal.None;
        }

        /// <summary>A side's units against the ceiling: ground vehicles, aircraft.</summary>
        public static (int vehicles, int aircraft) Count(Catalog catalog, IReadOnlyList<SandboxUnit> units, int team)
        {
            var (v, a) = (0, 0);
            foreach (var u in units)
            {
                if (u.Team != team || !catalog.Vehicles.TryGetValue(u.Def, out var def) || IsTower(def)) continue;
                if (IsAircraft(def)) a++;
                else v++;
            }
            return (v, a);
        }

        /// <summary>Whether one more of <paramref name="def"/> would go past the ceiling (a warning in the internal build, a stop in the player's).</summary>
        public static bool OverCap(Catalog catalog, IReadOnlyList<SandboxUnit> units, int team, VehicleDef def, int adding = 1)
        {
            if (IsTower(def)) return false;
            var (v, a) = Count(catalog, units, team);
            return IsAircraft(def) ? a + adding > AircraftCap : v + adding > VehicleCap;
        }

        /// <summary>
        /// The places of <paramref name="count"/> units in a formation round <paramref name="centre"/> facing
        /// <paramref name="heading"/> (degrees), <paramref name="spacing"/> metres apart (B.5).
        /// </summary>
        public static List<Vector2> Formation(SandboxFormation shape, int count, Vector2 centre, float heading, float spacing)
        {
            var list = new List<Vector2>();
            count = Math.Max(1, count);
            var forward = Core.SimMath.Forward(heading * MathF.PI / 180f);
            var right = new Vector2(forward.Y, -forward.X);
            switch (shape)
            {
                case SandboxFormation.Line:
                    for (var i = 0; i < count; i++) list.Add(centre + right * ((i - (count - 1) * 0.5f) * spacing));
                    break;
                case SandboxFormation.Column:
                    for (var i = 0; i < count; i++) list.Add(centre - forward * ((i - (count - 1) * 0.5f) * spacing));
                    break;
                case SandboxFormation.Cluster:
                {
                    var side = (int)MathF.Ceiling(MathF.Sqrt(count));
                    for (var i = 0; i < count; i++)
                    {
                        var (row, col) = (i / side, i % side);
                        list.Add(centre + right * ((col - (side - 1) * 0.5f) * spacing) - forward * ((row - (side - 1) * 0.5f) * spacing));
                    }
                    break;
                }
                case SandboxFormation.Arc:
                {
                    // A half circle bowed towards the heading, wide enough for the spacing.
                    var radius = MathF.Max(spacing, spacing * (count - 1) / MathF.PI);
                    for (var i = 0; i < count; i++)
                    {
                        var t = count == 1 ? global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.FormationCountTrue : i / (float)(count - 1);
                        var a = (t - 0.5f) * MathF.PI;
                        list.Add(centre + right * (MathF.Sin(a) * radius) + forward * ((MathF.Cos(a) - global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.FormationCosSub) * radius));
                    }
                    break;
                }
            }
            for (var i = 0; i < list.Count; i++) list[i] = new Vector2(Round(list[i].X), Round(list[i].Y));
            return list;
        }

        /// <summary>The spacing that keeps a formation's hulls apart.</summary>
        public static float Spacing(VehicleDef def) => MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.SpacingHullBoundFloor, def.HullBound * global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.SpacingHullBoundScale + global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxRules.SpacingHullBoundAdd);
    }
}
