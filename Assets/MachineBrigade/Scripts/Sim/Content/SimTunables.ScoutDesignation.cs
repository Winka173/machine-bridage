#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Scout Target Designation (10/10, DECISIONS "No Fog of War + scout Target Designation"): the numbers of the mark.
    /// Defaults are the owner's starting values; tunables.json (vehicles.scoutDesignation.*) overrides them at catalog load.
    /// Per-scout ranges are vehicle data (balance.json "designationRange").
    /// </summary>
    public static partial class SimTunables
    {
        public static partial class Vehicles
        {
            public static partial class ScoutDesignation
            {
                /// <summary>Extra direct damage a marked target takes from the marking side (0.10 = +10 %).</summary>
                public static float DamageBonus = 0.10f;

                /// <summary>The same against a boss (+5 %).</summary>
                public static float BossDamageBonus = 0.05f;

                /// <summary>How long a mark lasts unless refreshed (s; 5 s = 100 ticks).</summary>
                public static float MarkSeconds = 5f;

                /// <summary>How often a scout re-picks and refreshes its target (s; 2 s = 40 ticks).</summary>
                public static float RetargetSeconds = 2f;

                /// <summary>Targets one scout keeps marked (only 1 is supported; the value is clamped to 1).</summary>
                public static int MaxTargetsPerScout = 1;

                /// <summary>Allies' target-score multiplier for a marked target (inside the existing scoring only).</summary>
                public static float MarkedPriorityMultiplier = 1.10f;

                /// <summary>A scout drops its target for a new one only when the new one scores this many times higher.</summary>
                public static float SwitchMargin = 1.35f;

                /// <summary>Scout pick weights: the enemy is aiming at a friend / long-range fire / a gun that threatens an aircraft scout / heavy or elite / support / the rest.</summary>
                public static float WeightThreat = 3f, WeightArtillery = 2.5f, WeightAirDefence = 3f, WeightHeavy = 2f, WeightSupport = 1.5f, WeightOther = 1f;

                /// <summary>A target at the edge of the scout's range scores this share less than one beside it.</summary>
                public static float RangeFalloff = 0.25f;

                /// <summary>false: one bonus however many scouts mark it. true: the bonus is added once per distinct scout.</summary>
                public static bool Stacking;

                /// <summary>A scout also gains from its own mark (false).</summary>
                public static bool ApplyToSelf;

                /// <summary>Damage groups the bonus covers: the direct component (true), blast damage (false), burning (false).</summary>
                public static bool AffectsDirect = true, AffectsSplash, AffectsDamageOverTime;
            }
        }

        private static IEnumerable<Entry> ScoutDesignationEntries()
        {
            const string k = "vehicles.scoutDesignation.";
            yield return new Entry(k + "damageBonus", "share", () => Vehicles.ScoutDesignation.DamageBonus, v => Vehicles.ScoutDesignation.DamageBonus = (float)v);
            yield return new Entry(k + "bossDamageBonus", "share", () => Vehicles.ScoutDesignation.BossDamageBonus, v => Vehicles.ScoutDesignation.BossDamageBonus = (float)v);
            yield return new Entry(k + "markSeconds", "s", () => Vehicles.ScoutDesignation.MarkSeconds, v => Vehicles.ScoutDesignation.MarkSeconds = (float)v);
            yield return new Entry(k + "retargetSeconds", "s", () => Vehicles.ScoutDesignation.RetargetSeconds, v => Vehicles.ScoutDesignation.RetargetSeconds = (float)v);
            yield return new Entry(k + "maxTargetsPerScout", "count", () => Vehicles.ScoutDesignation.MaxTargetsPerScout,
                v => Vehicles.ScoutDesignation.MaxTargetsPerScout = (int)Math.Round(v));
            yield return new Entry(k + "markedPriorityMultiplier", "x", () => Vehicles.ScoutDesignation.MarkedPriorityMultiplier,
                v => Vehicles.ScoutDesignation.MarkedPriorityMultiplier = (float)v);
            yield return new Entry(k + "switchMargin", "x", () => Vehicles.ScoutDesignation.SwitchMargin, v => Vehicles.ScoutDesignation.SwitchMargin = (float)v);
            yield return new Entry(k + "weightThreat", "score", () => Vehicles.ScoutDesignation.WeightThreat, v => Vehicles.ScoutDesignation.WeightThreat = (float)v);
            yield return new Entry(k + "weightArtillery", "score", () => Vehicles.ScoutDesignation.WeightArtillery, v => Vehicles.ScoutDesignation.WeightArtillery = (float)v);
            yield return new Entry(k + "weightAirDefence", "score", () => Vehicles.ScoutDesignation.WeightAirDefence, v => Vehicles.ScoutDesignation.WeightAirDefence = (float)v);
            yield return new Entry(k + "weightHeavy", "score", () => Vehicles.ScoutDesignation.WeightHeavy, v => Vehicles.ScoutDesignation.WeightHeavy = (float)v);
            yield return new Entry(k + "weightSupport", "score", () => Vehicles.ScoutDesignation.WeightSupport, v => Vehicles.ScoutDesignation.WeightSupport = (float)v);
            yield return new Entry(k + "weightOther", "score", () => Vehicles.ScoutDesignation.WeightOther, v => Vehicles.ScoutDesignation.WeightOther = (float)v);
            yield return new Entry(k + "rangeFalloff", "share", () => Vehicles.ScoutDesignation.RangeFalloff, v => Vehicles.ScoutDesignation.RangeFalloff = (float)v);
            yield return new Entry(k + "stacking", "flag", () => Vehicles.ScoutDesignation.Stacking ? 1 : 0, v => Vehicles.ScoutDesignation.Stacking = v != 0, flag: true);
            yield return new Entry(k + "applyToSelf", "flag", () => Vehicles.ScoutDesignation.ApplyToSelf ? 1 : 0, v => Vehicles.ScoutDesignation.ApplyToSelf = v != 0, flag: true);
            yield return new Entry(k + "affectsDirectDamage", "flag", () => Vehicles.ScoutDesignation.AffectsDirect ? 1 : 0, v => Vehicles.ScoutDesignation.AffectsDirect = v != 0, flag: true);
            yield return new Entry(k + "affectsSplashDamage", "flag", () => Vehicles.ScoutDesignation.AffectsSplash ? 1 : 0, v => Vehicles.ScoutDesignation.AffectsSplash = v != 0, flag: true);
            yield return new Entry(k + "affectsDamageOverTime", "flag", () => Vehicles.ScoutDesignation.AffectsDamageOverTime ? 1 : 0,
                v => Vehicles.ScoutDesignation.AffectsDamageOverTime = v != 0, flag: true);
        }
    }
}
