#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>The bomb-run fix (DECISIONS "Ném bom rải thảm"): how a bomb weapon lays its bombs (data "stick.mode").</summary>
    public enum StickMode
    {
        /// <summary>One point: a guided bomb, or a single bomb (its scatter only).</summary>
        Point,

        /// <summary>A stick: the bombs walk along a line, one spacing apart.</summary>
        Stick,

        /// <summary>Another shape (reserved; laid as a point today).</summary>
        Pattern,
    }

    /// <summary>Which way a stick is laid (data "stick.heading").</summary>
    public enum StickHeading
    {
        /// <summary>Along the way the aircraft comes in.</summary>
        Approach,

        /// <summary>Along the target cluster's main axis when it is within 45 degrees of the approach, else the approach.</summary>
        Axis,
    }

    /// <summary>Where the aim sits on the stick (data "stick.anchor").</summary>
    public enum StickAnchor
    {
        /// <summary>The stick starts at the aim.</summary>
        Start,

        /// <summary>The stick's middle is on the aim (the bomb nearest the key target falls mid-stick).</summary>
        Center,
    }

    /// <summary>How the bombs leave the carrier (data "stick.drop").</summary>
    public enum StickDrop
    {
        /// <summary>Falling free from an aircraft flying over: the stick starts where the first bomb's fall puts it.</summary>
        Overfly,

        /// <summary>A boss's bomb bay: the stick is laid round its aim (the boss stands off; the bay ripples at its interval).</summary>
        Bay,
    }

    /// <summary>The warning a stick shows (data "stick.warnShape"; the view draws it in pass 3).</summary>
    public enum StickWarn
    {
        None,
        Ring,
        StickRect,
    }

    /// <summary>
    /// The bomb-run fix, pass 1 (DECISIONS "Ném bom rải thảm"): a bomb weapon's stick parameters (balance.json weapons[*].stick).
    /// Only <see cref="Mode"/>, <see cref="Bombs"/>, <see cref="Spacing"/>, <see cref="Interval"/>, <see cref="Heading"/>,
    /// <see cref="Anchor"/>, <see cref="Drop"/>, the jitters, <see cref="MinTargets"/>, <see cref="Safety"/> and
    /// <see cref="StraightTime"/> drive the Sim; the rest (lead, overlap, width, bay-open time, warning shape) are the sheet's
    /// numbers for the view and the export, checked against their formulas on load.
    /// </summary>
    public sealed class StickDef
    {
        public StickMode Mode { get; internal set; }
        public int Bombs { get; internal set; }
        public float Spacing { get; internal set; }
        public float Length { get; internal set; }
        public float Interval { get; internal set; }
        public float ReleaseSpeed { get; internal set; }
        public float FallTime { get; internal set; }
        public float Lead { get; internal set; }
        public StickHeading Heading { get; internal set; }
        public StickAnchor Anchor { get; internal set; }
        public StickDrop Drop { get; internal set; }
        public float JitterAcross { get; internal set; }
        public float JitterAlong { get; internal set; }
        public float Overlap { get; internal set; }
        public float Width { get; internal set; }
        public int MinTargets { get; internal set; }
        public float Safety { get; internal set; }
        public float StraightTime { get; internal set; }
        public float Exit { get; internal set; }
        public float BayOpen { get; internal set; }
        public StickWarn Warn { get; internal set; }

        /// <summary>A real stick (more than one bomb laid along a line).</summary>
        public bool Laid => Mode == StickMode.Stick && Bombs > 1;

        /// <summary>The bombs a stick drops on fewer targets than <see cref="MinTargets"/>: max(2, ceil(n / 3)), never more than n.</summary>
        public int Reduced => Math.Min(Bombs, Math.Max(2, (Bombs + 2) / 3));
    }

    public sealed partial class WeaponDef
    {
        /// <summary>The bomb-run fix: the stick parameters (data "stick"), or null for a weapon that drops no bombs.</summary>
        public StickDef? Stick { get; internal set; }

        /// <summary>The weapon lays a real stick (pass 2: every bomb on its own point along the line).</summary>
        public bool LaysStick => Stick is { Laid: true };

        /// <summary>Seconds between two rounds of a salvo: a stick's release interval (spacing / release speed), else the data's.</summary>
        public float SalvoGap => Stick is { Laid: true } s ? s.Interval : BurstInterval;
    }

    public sealed partial class Catalog
    {
        /// <summary>Tolerance of the derived stick numbers against their formulas (length, interval, lead, overlap, width).</summary>
        private const float StickTolerance = 0.02f;

        /// <summary>The bomb-run fix, pass 1: reads weapons[*].stick (enum words may be written with underscores: STICK_RECT).</summary>
        private static void ParseWeaponStick(JsonObject w, WeaponDef def)
        {
            if (!w.Has("stick")) return;
            var s = w.Object("stick");
            var stick = new StickDef
            {
                Mode = Loose(s, "mode", StickMode.Stick),
                Bombs = Math.Max(1, s.Int("bombs", def.Burst)),
                Spacing = MathF.Max(0f, s.Float("spacing", 0f)),
                ReleaseSpeed = MathF.Max(0f, s.Float("releaseSpeed", 0f)),
                FallTime = MathF.Max(0f, s.Float("fallTime", 1.2f)),
                Heading = Loose(s, "heading", StickHeading.Approach),
                Anchor = Loose(s, "anchor", StickAnchor.Center),
                Drop = Loose(s, "drop", StickDrop.Overfly),
                JitterAcross = MathF.Max(0f, s.Float("jitterAcross", 0.25f * def.SplashRadius)),
                MinTargets = Math.Max(0, s.Int("minTargets", 0)),
                Safety = MathF.Max(0f, s.Float("safety", MathF.Max(def.SplashRadius, 8f))),
                Exit = MathF.Max(0f, s.Float("exit", 0f)),
                BayOpen = MathF.Max(0f, s.Float("bayOpen", 0f)),
                Warn = Loose(s, "warnShape", StickWarn.None),
            };
            stick.JitterAlong = MathF.Max(0f, s.Float("jitterAlong", 0.15f * stick.Spacing));
            var length = (stick.Bombs - 1) * stick.Spacing;
            stick.Length = MathF.Max(0f, s.Float("length", length));
            stick.Interval = MathF.Max(0f, s.Float("interval", stick.ReleaseSpeed > 0f ? stick.Spacing / stick.ReleaseSpeed : def.BurstInterval));
            stick.Lead = MathF.Max(0f, s.Float("lead", stick.Drop == StickDrop.Bay ? 0f : stick.ReleaseSpeed * stick.FallTime));
            stick.Overlap = MathF.Max(0f, s.Float("overlap", stick.Spacing > 0f ? def.SplashRadius / stick.Spacing : 0f));
            stick.Width = MathF.Max(0f, s.Float("width", 2f * def.WarnRadius + 2f * stick.JitterAcross));
            stick.StraightTime = MathF.Max(0f, s.Float("straightTime", 0f));
            if (stick.Mode == StickMode.Stick)
            {
                if (stick.Bombs != def.Burst) throw new FormatException($"{s.Path}.bombs: {stick.Bombs}, the weapon's burst is {def.Burst} (the fix keeps the bombs per pass).");
                if (stick.Bombs > 1 && (stick.Spacing <= 0f || stick.ReleaseSpeed <= 0f))
                    throw new FormatException($"{s.Path}: a stick of {stick.Bombs} bombs needs a spacing and a releaseSpeed.");
                Near(s, "length", stick.Length, length);
                if (stick.Bombs > 1) Near(s, "interval", stick.Interval, stick.Spacing / stick.ReleaseSpeed);
                if (stick.Spacing > 0f) Near(s, "overlap", stick.Overlap, def.SplashRadius / stick.Spacing);
                Near(s, "width", stick.Width, 2f * def.WarnRadius + 2f * stick.JitterAcross);
            }
            def.Stick = stick;
        }

        /// <summary>A derived stick number within <see cref="StickTolerance"/> of its formula (0.05 absolute for small numbers).</summary>
        private static void Near(JsonObject s, string key, float value, float formula)
        {
            if (MathF.Abs(value - formula) > MathF.Max(0.05f, MathF.Abs(formula) * StickTolerance))
                throw new FormatException($"{s.Path}.{key}: {value}, its formula gives {formula}.");
        }

        /// <summary>An enum word, case and underscores ignored ("STICK_RECT" reads as StickRect).</summary>
        private static TEnum Loose<TEnum>(JsonObject s, string key, TEnum fallback) where TEnum : struct, Enum
        {
            if (!s.Has(key)) return fallback;
            var word = s.String(key).Replace("_", "");
            return Enum.TryParse<TEnum>(word, true, out var e) && Enum.IsDefined(typeof(TEnum), e)
                ? e
                : throw new FormatException($"{s.Path}.{key}: one of {string.Join(", ", Enum.GetNames(typeof(TEnum)))}.");
        }
    }
}
