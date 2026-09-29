#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// The tower-branch rework (DECISIONS 19T): a shield generator's "tower shields" branch. Every tower of its side
    /// within <see cref="Radius"/> carries a small shield of its own (<see cref="Hp"/>, scaled like the emitter's
    /// health), back at full <see cref="Recharge"/> seconds after its last hit. Energy goes through; a tower under a
    /// dome (a generator's or a shield carrier's) is covered by the dome only: they never add up.
    /// </summary>
    public sealed class WardDef
    {
        public float Radius { get; internal set; } = 25f;
        public float Hp { get; internal set; } = 700f;
        public float Recharge { get; internal set; } = 6f;
    }

    /// <summary>
    /// The CP relay's "loot depot" branch: no steady income; every enemy vehicle destroyed within
    /// <see cref="Radius"/> pays its side <see cref="Share"/> of the victim's price, on top of the kill's own refund
    /// but never past the kill cap (prompt 8 I.6's 45 %). One depot pays a kill, the nearest.
    /// </summary>
    public sealed class LootDef
    {
        public float Radius { get; internal set; } = 40f;
        public float Share { get; internal set; } = 0.2f;
    }

    public sealed partial class VehicleDef
    {
        /// <summary>Tower shields over its side's towers (null: none).</summary>
        public WardDef? Wards { get; internal set; }

        /// <summary>A loot depot (null: none).</summary>
        public LootDef? Loot { get; internal set; }

        /// <summary>Enemy aircraft within this many metres are seen by its side (the Patriot's long-range radar; 0: none).</summary>
        public float RevealAir { get; internal set; }

        /// <summary>
        /// The art id of a tower branch (the art branch's "&lt;tower&gt;_a" / "&lt;tower&gt;_b", keyed by the spec's A/B order):
        /// its model and icon when the art has them, else the tower's own (null: no art of its own).
        /// </summary>
        public string? Art { get; internal set; }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>
        /// The round a dual-purpose gun loads for a target in the air ("air": another weapon's id; the 57 mm's air-burst
        /// fragmentation round), fired at the gun's own cadence; null: one round only.
        /// </summary>
        public WeaponDef? AirRound { get; internal set; }
    }

    public sealed partial class Catalog
    {
        private static void ParseBranchRework(JsonObject v, VehicleDef def)
        {
            if (v.Has("wards"))
            {
                var w = v.Object("wards");
                def.Wards = new WardDef
                {
                    Radius = Math.Max(1f, w.Float("radius", 25f)), Hp = Math.Max(1f, w.Float("hp", 700f)), Recharge = Math.Max(0.5f, w.Float("recharge", 6f)),
                };
            }
            if (v.Has("loot"))
            {
                var l = v.Object("loot");
                def.Loot = new LootDef { Radius = Math.Max(1f, l.Float("radius", 40f)), Share = Math.Clamp(l.Float("share", 0.2f), 0f, 1f) };
            }
            def.RevealAir = Math.Max(0f, v.Float("revealAir", 0f));
            if (v.Has("art")) def.Art = v.String("art");
        }

        /// <summary>A gun's air-burst round ("air": another weapon's id), once every weapon is read.</summary>
        private static void ResolveAirRounds(IEnumerable<JsonObject> raw, Dictionary<string, WeaponDef> weapons)
        {
            foreach (var w in raw)
            {
                if (!w.Has("air")) continue;
                var id = w.String("air");
                if (!weapons.TryGetValue(id, out var air)) throw new FormatException($"{w.Path}.air: unknown weapon '{id}'.");
                if (air.AirRound != null || !air.CanTarget(true)) throw new FormatException($"{w.Path}.air: the round must hit aircraft and have no air round of its own.");
                weapons[w.String("id")].AirRound = air;
            }
        }
    }
}
