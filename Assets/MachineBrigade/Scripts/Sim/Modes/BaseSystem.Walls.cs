#nullable enable
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    public sealed partial class TeamBase
    {
        /// <summary>Prompt 32 L3: the base's wall lines (outer first); empty with no wall in the loadout or on the map.</summary>
        public List<WallLine> Walls { get; } = new();
    }

    /// <summary>
    /// Prompt 32 L3: a base's walls, built as the base is set up (<see cref="WallSystem.Build"/>), before its towers stand.
    /// A gun wall takes one of the base's own small slots, never a free one: the last small slot the HQ level opens that
    /// holds a tower; that tower stands on the line's gun segment (next to the gate) instead of its hardpoint, is flown back
    /// in there by the usual rules, and comes down with its segment. With no small tower in the base the gun wall stands
    /// without one.
    /// </summary>
    public sealed partial class BaseSystem
    {
        private void BuildWalls(TeamBase b, string owner)
        {
            var lines = _world.Map.WallsOf(owner);
            if (lines.Count == 0) return;
            var built = _world.Walls.Build(b.Team, lines, b.Loadout, b.HqPosition);
            b.Walls.AddRange(built);
            foreach (var line in built)
            {
                if (line.Type != WallType.GunWall) continue;
                WallSegment? gun = null;
                foreach (var s in line.Segments)
                    if (s.Def.Gun) gun = s;
                if (gun == null) continue;
                for (var i = b.Slots.Count - 1; i >= 0; i--)
                {
                    var slot = b.Slots[i];
                    if (slot.Def.Kind != HardpointKind.Tower || slot.Def.Class != SlotSize.Small || slot.Tower == null || slot.OnWall || slot.Def.Forward) continue;
                    var def = new HardpointDef(gun.Center, HardpointKind.Tower, slot.Def.Size, gun.Def.Facing, SlotSize.Small, slot.Def.Place);
                    var moved = new HardpointState(def, slot.Index, slot.PointId)
                    {
                        Tower = slot.Tower, Ring = slot.Ring, Lost = slot.Lost, OnWall = true,
                        HealthScale = slot.HealthScale, DamageScale = slot.DamageScale,
                    };
                    b.Slots[i] = moved;
                    line.Gun = moved;
                    break;
                }
            }
        }
    }
}
