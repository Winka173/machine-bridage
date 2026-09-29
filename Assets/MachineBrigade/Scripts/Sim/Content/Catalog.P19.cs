#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    public sealed partial class VehicleDef
    {
        /// <summary>Prompt 19 B: its altitude tiers and their fixed schedule (null: an ordinary unit).</summary>
        public TierDef? Tiers { get; internal set; }

        /// <summary>Prompt 19 D: the drop pods it sends down (null: none).</summary>
        public PodDef? Pods { get; internal set; }

        /// <summary>Prompt 19 B.2: the highest tier its anti-air weapons reach (a fighter's: high); None: their own.</summary>
        public AltitudeTier Ceiling { get; internal set; }

        /// <summary>Prompt 19 G.2: the battlefield it is fought on in Boss Rush when the rush's own is another ("launchsite").</summary>
        public string? Arena { get; internal set; }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>Prompt 19 B.2: the highest tier it reaches ("ceiling": a railgun's low, a long-range SAM's high); None: the ordinary rule.</summary>
        public AltitudeTier Ceiling { get; internal set; }
    }

    /// <summary>Prompt 19 (DECISIONS 18A): balance.json "tiers", "pods", "ceiling" and "arena".</summary>
    public sealed partial class Catalog
    {
        private static void ParseWeaponP19(JsonObject w, WeaponDef def) => def.Ceiling = w.Enum("ceiling", AltitudeTier.None);

        private static void ParseP19(JsonObject v, VehicleDef def)
        {
            def.Ceiling = v.Enum("ceiling", AltitudeTier.None);
            if (v.Has("arena")) def.Arena = v.String("arena");
            if (v.Has("tiers")) def.Tiers = Wrap(v.Object("tiers"), () => ParseTiers(v.Object("tiers")));
            if (v.Has("pods")) def.Pods = Wrap(v.Object("pods"), () => ParsePods(v.Object("pods")));
        }

        private static TierDef ParseTiers(JsonObject t)
        {
            var def = new TierDef
            {
                Opening = MathF.Max(0f, t.Float("opening", 0f)),
                Descend = MathF.Max(0.5f, t.Float("descend", 4f)),
                Shift = MathF.Max(0.5f, t.Float("shift", 3.5f)),
                EscortsOnDescend = t.Bool("escortsOnDescend", true),
            };
            if (t.Has("heights"))
            {
                var h = t.Object("heights");
                def.OrbitHeight = MathF.Max(1f, h.Float("orbit", def.OrbitHeight));
                def.HighHeight = MathF.Max(1f, h.Float("high", def.HighHeight));
                def.LowHeight = MathF.Max(1f, h.Float("low", def.LowHeight));
            }
            if (t.Has("marks"))
            {
                var marks = new List<float>(t.FloatArray("marks"));
                for (var i = 0; i < marks.Count; i++)
                    if (marks[i] <= 0f || marks[i] >= 1f || (i > 0 && marks[i] >= marks[i - 1]))
                        throw new FormatException($"{t.Path}.marks: shares of health between 0 and 1, highest first.");
                def.Marks = marks;
            }
            var schedule = new List<IReadOnlyList<TierStepDef>>();
            foreach (var phase in t.Array("schedule"))
            {
                var steps = new List<TierStepDef>();
                foreach (var s in phase.Array("steps"))
                {
                    var tier = s.Enum<AltitudeTier>("tier");
                    if (tier is AltitudeTier.None or AltitudeTier.Orbit) throw new FormatException($"{s.Path}.tier: a schedule keeps to low and high (orbit is the opening's).");
                    steps.Add(new TierStepDef(tier, MathF.Max(1f, s.Float("seconds"))));
                }
                if (steps.Count == 0) throw new FormatException($"{phase.Path}.steps: a phase needs at least one step.");
                schedule.Add(steps);
            }
            if (schedule.Count == 0) throw new FormatException($"{t.Path}.schedule: at least one phase.");
            def.Schedule = schedule;
            if (t.Has("armour"))
            {
                var a = t.Object("armour");
                def.Armour = new TierArmourDef
                {
                    Hull = Math.Clamp(a.Int("hull", 4), 0, ArmourLevels.Max),
                    Belly = Math.Clamp(a.Int("belly", 2), 0, ArmourLevels.Max),
                    Grounded = Math.Clamp(a.Int("grounded", 3), 0, ArmourLevels.Max),
                };
            }
            if (t.Has("crash"))
            {
                var c = t.Object("crash");
                var crash = new CrashDef
                {
                    Fall = MathF.Max(1f, c.Float("fall", 6f)),
                    Damage = MathF.Max(0f, c.Float("damage", 500f)),
                    Radius = MathF.Max(1f, c.Float("radius", 16f)),
                    Form = c.Has("form") ? c.String("form") : null,
                    Warning = c.Has("warning") ? c.String("warning") : null,
                };
                if (c.Has("at"))
                {
                    var at = c.FloatArray("at");
                    crash.At = new Vector2(at.Count > 0 ? at[0] : 0f, at.Count > 1 ? at[1] : 0f);
                }
                if (c.Has("guns"))
                {
                    var guns = new List<int>();
                    foreach (var g in c.FloatArray("guns")) guns.Add((int)g);
                    crash.Guns = guns;
                }
                if (c.Has("debris")) crash.Debris = c.String("debris");
                if (c.Has("debrisAt"))
                {
                    var spots = new List<Vector2>();
                    foreach (var p in c.FloatArrays("debrisAt")) spots.Add(new Vector2(p.Count > 0 ? p[0] : 0f, p.Count > 1 ? p[1] : 0f));
                    crash.DebrisAt = spots;
                }
                def.Crash = crash;
            }
            if (t.Has("hijack"))
            {
                var h = t.Object("hijack");
                def.Hijack = new HijackDef
                {
                    First = MathF.Max(0f, h.Float("first", 10f)),
                    Every = MathF.Max(5f, h.Float("every", 40f)),
                    Warn = MathF.Max(0.5f, h.Float("warn", 4f)),
                    Seconds = MathF.Max(0.5f, h.Float("seconds", 6f)),
                };
                if (h.Has("difficulties")) def.Hijack.Difficulties = h.StringArray("difficulties");
            }
            if (t.Has("radio"))
            {
                var r = t.Object("radio");
                var radio = new Dictionary<string, string>();
                foreach (var key in r.Keys) radio[key] = r.String(key);
                def.Radio = radio;
            }
            return def;
        }

        private static PodDef ParsePods(JsonObject p)
        {
            var def = new PodDef
            {
                Unit = p.Has("unit") ? p.String("unit") : "drop_pod",
                First = MathF.Max(0f, p.Float("first", 4f)),
                Every = MathF.Max(2f, p.Float("every", 14f)),
                Count = Math.Max(1, p.Int("count", 2)),
                Min = Math.Max(1, p.Int("min", 1)),
                PerPod = Math.Max(1, p.Int("perPod", 2)),
                Fall = MathF.Max(1f, p.Float("fall", 6f)),
                Max = Math.Max(1, p.Int("max", 6)),
                Offset = MathF.Max(0f, p.Float("offset", 30f)),
                Spread = MathF.Max(0f, p.Float("spread", 12f)),
                Warning = p.Has("warning") ? p.String("warning") : null,
                Units = p.Has("units") ? p.StringArray("units") : Array.Empty<string>(),
            };
            if (def.Min > def.PerPod) def.Min = def.PerPod;
            if (p.Has("tiers"))
            {
                var tiers = new List<AltitudeTier>();
                foreach (var name in p.StringArray("tiers"))
                    tiers.Add(Enum.TryParse<AltitudeTier>(name, true, out var tier) ? tier : throw new FormatException($"{p.Path}.tiers: unknown tier '{name}'."));
                def.Tiers = tiers;
            }
            if (def.Units.Count == 0) throw new FormatException($"{p.Path}.units: a pod needs something to carry.");
            return def;
        }

        /// <summary>Prompt 19: every tiered boss's pods, crash and warnings checked against the catalog.</summary>
        private void CheckTiers()
        {
            foreach (var def in _vehicles.Values)
            {
                if (def.Pods is { } pods)
                {
                    if (!_vehicles.TryGetValue(pods.Unit, out var pod) || !pod.Flying) throw new FormatException($"{def.Id}.pods.unit: '{pods.Unit}' is not a flying vehicle.");
                    foreach (var u in pods.Units)
                        if (!_vehicles.ContainsKey(u)) throw new FormatException($"{def.Id}.pods.units: unknown vehicle '{u}'.");
                    if (pods.Warning != null && !_supports.ContainsKey(pods.Warning)) throw new FormatException($"{def.Id}.pods.warning: unknown support '{pods.Warning}'.");
                }
                if (def.Tiers?.Crash is not { } crash) continue;
                foreach (var g in crash.Guns)
                    if (g <= 0 || g >= def.Mounts.Count) throw new FormatException($"{def.Id}.tiers.crash.guns: no secondary mount {g}.");
                if (crash.Warning != null && !_supports.ContainsKey(crash.Warning)) throw new FormatException($"{def.Id}.tiers.crash.warning: unknown support '{crash.Warning}'.");
                if (crash.DebrisAt.Count > 0 && !_props.ContainsKey(crash.Debris)) throw new FormatException($"{def.Id}.tiers.crash.debris: unknown prop '{crash.Debris}'.");
                if (!def.Flying) throw new FormatException($"{def.Id}.tiers: only a flying boss crashes.");
            }
        }
    }
}
