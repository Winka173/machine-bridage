#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Fix prompt L4 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): how munitions behave in flight, balance.json
    /// "munitionRules" (lane B's own block: the weapons' numbers stay in "weapons"). Families are weaponFamilyIds.
    /// </summary>
    public sealed class MunitionRules
    {
        /// <summary>Rule C: the share of IR missiles one flare release pulls off, times (1 - the weapon's flareResist); one roll per missile.</summary>
        public float FlareDecoyChance { get; internal set; } = 0.35f;

        /// <summary>Rule C: how far behind and beside the aircraft a decoyed missile meets its flare (m); always past the fuze.</summary>
        public float FlareOffset { get; internal set; } = 10f;

        /// <summary>Rule B: an anti-air missile's proximity fuze (m, the prompt's 6-8 m): it bursts this close to what it chases.</summary>
        public float ProximityFuze { get; internal set; } = 7f;

        /// <summary>Rules A, G: a guided round self-destructs once its target is farther than its range x this from where it left.</summary>
        public float ReachScale { get; internal set; } = 1.3f;

        /// <summary>Rule D: an unguided round leads its target by at most this many seconds of the target's motion.</summary>
        public float LeadCap { get; internal set; } = 3f;

        /// <summary>Rule C: missile families with radar (or radio-command) guidance: flares do nothing to them.</summary>
        public IReadOnlyCollection<string> RadarGuided { get; internal set; } = Array.Empty<string>();

        /// <summary>Rule A: missile families steered by their shooter's sight (wire, beam, laser): they lose their target when the shooter dies or loses sight.</summary>
        public IReadOnlyCollection<string> SightGuided { get; internal set; } = Array.Empty<string>();

        /// <summary>The view: flares a release puts out, by aircraft size (fighters and attack jets, helicopters, big aircraft), min and max.</summary>
        public (int min, int max) FlaresFighter { get; internal set; } = (4, 6);
        public (int min, int max) FlaresHelicopter { get; internal set; } = (4, 8);
        public (int min, int max) FlaresLarge { get; internal set; } = (8, 16);

        /// <summary>The view: how long one flare burns (s), min and max.</summary>
        public (float min, float max) FlareBurn { get; internal set; } = (3f, 4f);

        public bool IsRadarGuided(WeaponDef w) => w.WeaponFamilyId != null && Contains(RadarGuided, w.WeaponFamilyId);

        public bool IsSightGuided(WeaponDef w) => w.WeaponFamilyId != null && Contains(SightGuided, w.WeaponFamilyId);

        private static bool Contains(IReadOnlyCollection<string> set, string id) =>
            set is HashSet<string> hash ? hash.Contains(id) : new List<string>(set).Contains(id);

        internal static MunitionRules Parse(JsonObject o)
        {
            var r = new MunitionRules
            {
                FlareDecoyChance = Math.Clamp(o.Float("flareDecoyChance", 0.35f), 0f, 1f),
                ProximityFuze = Math.Clamp(o.Float("proximityFuze", 7f), 1f, 20f),
                ReachScale = Math.Max(1f, o.Float("reachScale", 1.3f)),
                LeadCap = Math.Max(0f, o.Float("leadCap", 3f)),
                RadarGuided = o.Has("radarGuided") ? new HashSet<string>(o.StringArray("radarGuided")) : new HashSet<string>(),
                SightGuided = o.Has("sightGuided") ? new HashSet<string>(o.StringArray("sightGuided")) : new HashSet<string>(),
            };
            // A decoyed missile bursts outside its own fuze (else it would burst on the aircraft it lost).
            r.FlareOffset = Math.Max(r.ProximityFuze + 2f, o.Float("flareOffset", 10f));
            if (o.Has("flareRelease"))
            {
                var f = o.Object("flareRelease");
                r.FlaresFighter = Pair(f, "fighter", r.FlaresFighter);
                r.FlaresHelicopter = Pair(f, "helicopter", r.FlaresHelicopter);
                r.FlaresLarge = Pair(f, "large", r.FlaresLarge);
            }
            if (o.Has("flareBurn"))
            {
                var b = o.FloatArray("flareBurn");
                if (b.Count != 2 || b[0] <= 0f || b[1] < b[0]) throw new FormatException($"{o.Path}.flareBurn: [min, max] seconds.");
                r.FlareBurn = (b[0], b[1]);
            }
            return r;
        }

        private static (int min, int max) Pair(JsonObject o, string key, (int min, int max) fallback)
        {
            if (!o.Has(key)) return fallback;
            var a = o.FloatArray(key);
            if (a.Count != 2 || a[0] < 1f || a[1] < a[0]) throw new FormatException($"{o.Path}.{key}: [min, max] flares.");
            return ((int)a[0], (int)a[1]);
        }
    }

    /// <summary>
    /// Fix prompt L5 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): which rounds warn and for how long, balance.json
    /// "warningRules". The Sim reads the time (a warned round stays in the air at least that long); the view reads the rest.
    /// </summary>
    public sealed class WarningRules
    {
        /// <summary>The rules every weapon's <see cref="WeaponDef.WarnSeconds"/> uses: the last catalog loaded (all load the same data).</summary>
        public static WarningRules Shared { get; internal set; } = new();

        /// <summary>Warned: guns from this calibre (mm), bombs from this weight (kg), rockets from this calibre (mm).</summary>
        public float GunMinMm { get; internal set; } = 203f;
        public float BombMinKg { get; internal set; } = 400f;
        public float RocketMinMm { get; internal set; } = 300f;

        /// <summary>The warning's floor (s): 203-240 mm and the other T4, the 406 mm, the 800 mm and the super weapons.</summary>
        public float FloorT4 { get; internal set; } = 2.5f;
        public float Floor406 { get; internal set; } = 3.5f;
        public float FloorT5 { get; internal set; } = 4f;

        /// <summary>The escape term: base + core / escape speed (s, m/s).</summary>
        public float Base { get; internal set; } = 0.5f;
        public float EscapeSpeed { get; internal set; } = 4.5f;

        /// <summary>No warning is longer (s).</summary>
        public float Cap { get; internal set; } = 6f;

        /// <summary>The view: rings shown at once at most (super weapons on top of these, always).</summary>
        public int MaxShown { get; internal set; } = 6;

        /// <summary>
        /// Play-test 13 (lane C), data "normalFire": whether a weapon's ordinary fire warns at all. False (the owner's rule):
        /// a gun fires and its shell lands at once, with no ring and no added flight; only the bosses' big attacks, the super
        /// weapons' strikes, the supports and a bomber's stick warn (their own systems). <see cref="IsBig"/> still sorts the
        /// big rounds (the preview's ring time, the export).
        /// </summary>
        public bool NormalFire { get; internal set; }

        /// <summary>The view: one shooter's rounds fired within this (s) whose rings touch are one ring round them all.</summary>
        public float SalvoMerge { get; internal set; } = 0.6f;

        /// <summary>The view: a ring fades in over this (s).</summary>
        public float FadeIn { get; internal set; } = 0.4f;

        /// <summary>The warning a round of <paramref name="tier"/> (family <paramref name="familyId"/>, core m) must give: 0 below T4.</summary>
        public float Seconds(int tier, string? familyId, float core)
        {
            if (tier < 4) return 0f;
            var floor = familyId == "cal_406" ? Floor406 : tier >= 5 ? FloorT5 : FloorT4;
            return MathF.Min(Cap, MathF.Max(floor, Base + MathF.Max(0f, core) / MathF.Max(0.1f, EscapeSpeed)));
        }

        /// <summary>
        /// Whether a round fired by a mount warns (a ring on its fall point, its flight held to the warning): only when
        /// <see cref="NormalFire"/> is on and the round is a big one (<see cref="IsBig"/>). Off by the owner's rule (play-test 13).
        /// </summary>
        public bool Warns(WeaponDef w) => NormalFire && IsBig(w);

        /// <summary>
        /// Whether a round is a big one the rules would warn of: never a guided one (it chases its target and has no fall
        /// point) nor a beam; else its tier (T4+: 203 mm and up, the 400 kg bombs, the Smerch) or, for a weapon with no
        /// family, its size by kind.
        /// </summary>
        public bool IsBig(WeaponDef w)
        {
            if (w.Guided || w.GuidedRocket || w.Beam || w.Laid || w.SplashRadius <= 0f) return false;
            if (w.Tier >= 0) return w.Tier >= 4;
            return w.Projectile switch
            {
                ProjectileKind.Shell => w.Size >= GunMinMm,
                ProjectileKind.Bomb => w.Size >= BombMinKg,
                ProjectileKind.Rocket => w.Size >= RocketMinMm,
                _ => false,
            };
        }

        internal static WarningRules Parse(JsonObject o) => new()
        {
            GunMinMm = o.Float("gunMinMm", 203f),
            BombMinKg = o.Float("bombMinKg", 400f),
            RocketMinMm = o.Float("rocketMinMm", 300f),
            FloorT4 = o.Float("floorT4", 2.5f),
            Floor406 = o.Float("floor406", 3.5f),
            FloorT5 = o.Float("floorT5", 4f),
            Base = o.Float("base", 0.5f),
            EscapeSpeed = Math.Max(0.1f, o.Float("escapeSpeed", 4.5f)),
            Cap = Math.Max(0.5f, o.Float("cap", 6f)),
            MaxShown = Math.Max(1, o.Int("maxShown", 6)),
            NormalFire = o.Bool("normalFire", false),
            SalvoMerge = Math.Max(0f, o.Float("salvoMergeSeconds", 0.6f)),
            FadeIn = Math.Max(0f, o.Float("fadeIn", 0.4f)),
        };
    }

    public sealed partial class Catalog
    {
        /// <summary>Fix prompt L4: balance.json "munitionRules" (defaults without it).</summary>
        public MunitionRules Munitions { get; internal set; } = new();

        /// <summary>Fix prompt L5: balance.json "warningRules" (defaults without it).</summary>
        public WarningRules Warnings { get; internal set; } = new();

        /// <summary>Fix prompt L4 / L5: reads lane B's rule blocks (called once the catalog is built).</summary>
        private void FinishFixRules(JsonObject root)
        {
            if (root.Has("munitionRules")) Munitions = MunitionRules.Parse(root.Object("munitionRules"));
            if (root.Has("warningRules")) Warnings = WarningRules.Parse(root.Object("warningRules"));
            WarningRules.Shared = Warnings;
        }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>
        /// Fix prompt L4 rule A: a guided rocket (the laser-guided APKWS: variant "guided", or data "guided": true on a rocket)
        /// homes on its target like a missile; it stays a rocket for every other rule (APS, its look).
        /// </summary>
        public bool GuidedRocket => Projectile == ProjectileKind.Rocket && (Steered || WeaponVariantId == "guided");
    }
}
