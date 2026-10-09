#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Boss design workbook 09/10 (Docs/bosses/design_0910): the data side of the new hardpoints. A boss's "newGunDps" is the DPS
    /// budget of the guns it gains (sheet 03 col L, weapon level: the sustained DPS of the weapon alone, before rank and difficulty
    /// multipliers, the unit sheet 07 and sheet 03 count in). It is split evenly over its mounts flagged "new", and each mount's
    /// damage multiplier is set so the mount adds exactly its share once the boss's gun nerf (damage x rate) has been applied
    /// to every gun, so more guns never mean more DPS.
    /// </summary>
    /// <summary>One fire group's limits (balance.json "bossFireGroups.&lt;group&gt;").</summary>
    public sealed class FireGroupRule
    {
        /// <summary>At most this many mounts of the group are on one target at once (a mount counts for <see cref="Window"/> s after a round).</summary>
        public int MaxAtTarget { get; internal set; } = 99;

        public float Window { get; internal set; } = 3f;

        /// <summary>Two mounts of the group never open fire within this many seconds of each other; each mount has its own gap in the range (stagger).</summary>
        public float GapLo { get; internal set; }

        public float GapHi { get; internal set; }

        public bool Free => MaxAtTarget >= 99 && GapHi <= 0f;

        internal static FireGroupRule Parse(JsonObject o, FireGroupRule d)
        {
            var gap = o.Has("gap") ? o.FloatArray("gap") : null;
            return new FireGroupRule
            {
                MaxAtTarget = o.Int("maxAtTarget", d.MaxAtTarget),
                Window = Math.Max(0.1f, o.Float("window", d.Window)),
                GapLo = gap != null && gap.Count > 0 ? Math.Max(0f, gap[0]) : d.GapLo,
                GapHi = gap != null && gap.Count > 1 ? Math.Max(gap[0], gap[1]) : gap != null && gap.Count == 1 ? gap[0] : d.GapHi,
            };
        }
    }

    /// <summary>
    /// Boss design 09/10, sheet 12: how a boss's many guns share the fight. Main guns go for heavy armour a cluster or two at a
    /// time, secondary guns for vehicles from two to four mounts at a time and out of step, CIWS and flak are independent and
    /// shoot the air, suppression guns are many and light; a heavy blast weapon (a bomb stick, a big shell) never opens fire within
    /// <see cref="HeavyAoeGap"/> s of another of the boss's, or while its big attack is charging or firing. Only a boss with at least
    /// <see cref="MinMounts"/> mounts is held to it (the older, smaller armaments fire as before).
    /// </summary>
    public sealed class FireGroupRules
    {
        public int MinMounts { get; internal set; } = 6;
        public float HeavyAoeRadius { get; internal set; } = 6f;
        public float HeavyAoeGap { get; internal set; } = 5f;

        /// <summary>How many different fire groups (air defence aside) may be on one target at once (0: no limit).</summary>
        public int MaxGroupsAtTarget { get; internal set; } = 2;
        public FireGroupRule Main { get; internal set; } = new FireGroupRule { MaxAtTarget = 2, Window = 4f, GapLo = 1f, GapHi = 2f };
        public FireGroupRule Secondary { get; internal set; } = new FireGroupRule { MaxAtTarget = 4, Window = 3f, GapLo = 0.4f, GapHi = 1.8f };
        public FireGroupRule Ciws { get; internal set; } = new FireGroupRule();
        public FireGroupRule Suppress { get; internal set; } = new FireGroupRule { MaxAtTarget = 5, Window = 2f, GapLo = 0.3f, GapHi = 1.5f };

        internal static FireGroupRules Parse(JsonObject root)
        {
            var r = new FireGroupRules();
            if (!root.Has("bossFireGroups")) return r;
            var o = root.Object("bossFireGroups");
            r.MinMounts = o.Int("minMounts", r.MinMounts);
            r.MaxGroupsAtTarget = o.Int("maxGroupsAtTarget", r.MaxGroupsAtTarget);
            if (o.Has("heavyAoe"))
            {
                var h = o.Object("heavyAoe");
                r.HeavyAoeRadius = h.Float("radius", r.HeavyAoeRadius);
                r.HeavyAoeGap = h.Float("gap", r.HeavyAoeGap);
            }
            if (o.Has("main")) r.Main = FireGroupRule.Parse(o.Object("main"), r.Main);
            if (o.Has("secondary")) r.Secondary = FireGroupRule.Parse(o.Object("secondary"), r.Secondary);
            if (o.Has("ciws")) r.Ciws = FireGroupRule.Parse(o.Object("ciws"), r.Ciws);
            if (o.Has("suppress")) r.Suppress = FireGroupRule.Parse(o.Object("suppress"), r.Suppress);
            return r;
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>Boss design 09/10: the fire group rules (data "bossFireGroups").</summary>
        public FireGroupRules FireGroups { get; internal set; } = new FireGroupRules();

        internal void FinishBossDesign(JsonObject root) => FireGroups = FireGroupRules.Parse(root);

        private static void ScaleNewGuns(VehicleDef def)
        {
            if (def.GunDpsAll > 0f)
            {
                // A new mini boss (sheet 05): every mount is the workbook's; the target is the whole gun DPS.
                var all = 0;
                foreach (var m in def.Mounts)
                    if (m.Weapon.SustainedDps > 0f) all++;
                if (all == 0) return;
                var each = def.GunDpsAll / all;
                var nerfAll = Math.Max(0.05f, def.GunNerfDamage * def.FireScale);
                foreach (var m in def.Mounts)
                {
                    var dps = m.Weapon.SustainedDps;
                    if (dps > 0f) m.DamageScale = Math.Clamp(each / (dps * nerfAll), 0.02f, 4f);
                }
                return;
            }
            if (def.NewGunDps <= 0f) return;
            var n = 0;
            foreach (var m in def.Mounts)
                if (m.NewGun) n++;
            if (n == 0) return;
            var share = def.NewGunDps / n;
            var nerf = Math.Max(0.05f, def.GunNerfDamage * def.FireScale);
            foreach (var m in def.Mounts)
            {
                if (!m.NewGun) continue;
                var dps = m.Weapon.SustainedDps;
                if (dps <= 0f) continue;
                m.DamageScale = Math.Clamp(share / (dps * nerf), 0.02f, 4f);
            }
        }
    }
}
