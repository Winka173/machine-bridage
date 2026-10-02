#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 34 L1: one weapon family of balance.json's "weaponFamilyTable": a calibre class for guns ("152-155 mm",
    /// "120 mm HE") or the real weapon for the rest. <see cref="Tier"/> is the prompt's T0-T5 (warnings, later effects and
    /// sounds); <see cref="Variants"/> the variants a weapon of the family may name, each with its reason; the boss numbers
    /// (a round's damage, core, edge) are what Tools/balance/p34_boss_families.py writes onto the boss weapons (null: the
    /// prompt's table has none).
    /// </summary>
    public sealed class WeaponFamilyInfo
    {
        public WeaponFamilyInfo(string id, string name, int tier)
        {
            Id = id;
            Name = name;
            Tier = Math.Clamp(tier, 0, 5);
        }

        public string Id { get; }
        public string Name { get; }
        public int Tier { get; }
        public IReadOnlyDictionary<string, string> Variants { get; internal set; } = new Dictionary<string, string>();
        public float? BossDamage { get; internal set; }
        public float BossCore { get; internal set; }
        public float BossEdge { get; internal set; }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>Prompt 34 L1: the weapon's family ("weaponFamilyId"; the same real weapon is always the same family), or null.</summary>
        public string? WeaponFamilyId { get; internal set; }

        /// <summary>Prompt 34 L1: its variant inside the family ("weaponVariantId": another round or fire mode), or null.</summary>
        public string? WeaponVariantId { get; internal set; }

        /// <summary>Prompt 34 L1: the family's tier, T0 (up to 14.5 mm) to T5 (406 mm and the super weapons); -1 without a family.</summary>
        public int Tier { get; internal set; } = -1;

        /// <summary>Prompt 34 L1: a T5 blast's edge may reach this far (the 406 mm's 24 m, the 800 mm's 28 m); T0-T4 keep <see cref="MaxEdge"/>.</summary>
        public const float MaxEdgeT5 = 28f;

        // ------------------------------------------------------------------------------------------------ L3 warnings

        /// <summary>Prompt 34 L3: how fast a vehicle gets out of a blast's core (m/s), for the warning time.</summary>
        public const float EscapeSpeed = 4.5f;

        /// <summary>Prompt 34 L3: no warning lasts longer than this.</summary>
        public const float MaxWarning = 6f;

        /// <summary>
        /// Prompt 34 L3: the warning a T4+ round must give before it lands, by escape time: max(the tier's floor, 0.5 s + core /
        /// 4.5 m/s), at most 6 s. Floors: T4 2.5 s, the 406 mm 3.5 s, the 800 mm and the other T5 super weapons 4 s. 0 below T4.
        /// </summary>
        public static float EscapeWarning(int tier, string? familyId, float core)
        {
            if (tier < 4) return 0f;
            var floor = familyId == "cal_406" ? 3.5f : tier >= 5 ? 4f : 2.5f;
            return MathF.Min(MaxWarning, MathF.Max(floor, 0.5f + MathF.Max(0f, core) / EscapeSpeed));
        }

        /// <summary>Prompt 34 L3: this round's escape warning (0 below T4).</summary>
        public float WarnSeconds => EscapeWarning(Tier, WeaponFamilyId, SplashRadius);

        /// <summary>Prompt 34 L3: the ring a warning draws: the blast's edge when it has two layers, else its core.</summary>
        public float WarnRadius => SplashEdge > SplashRadius ? SplashEdge : SplashRadius;

        // ------------------------------------------------------------------------------------------------ L4 barrels

        /// <summary>Prompt 34 L4: the gun's barrels (data "barrels", 1); each has its own muzzle on the model where it has them.</summary>
        public int Barrels { get; internal set; } = 1;

        /// <summary>
        /// Prompt 34 L4: data "salvoMode": "SIMULTANEOUS" fires every barrel in the same tick each trigger pull (one volley; the
        /// view staggers the flashes); "RIPPLE" (the default) fires one round a pull, a salvo's rounds one after another.
        /// </summary>
        public bool Simultaneous { get; internal set; }

        /// <summary>Prompt 34 L4: rounds one trigger pull fires at once: every barrel of a simultaneous gun, else one.</summary>
        public int RoundsPerPull => Simultaneous ? Math.Max(1, Barrels) : 1;

        /// <summary>Prompt 34 L4: the view's gap between the flashes of one volley's barrels (0.05-0.1 s in the prompt).</summary>
        public const float BarrelGap = 0.07f;
    }
}
