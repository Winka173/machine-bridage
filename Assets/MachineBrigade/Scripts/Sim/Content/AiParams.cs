#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// One tunable AI or economy parameter (prompt 28 L.1): its starting value, the range a sweep tries, what the
    /// sweep measures and why it is tuned. Nothing here is final; the sweep (L.3) picks the values.
    /// </summary>
    public readonly struct AiParam
    {
        public AiParam(float value, float min, float max, string metric, string reason)
        {
            Value = value;
            Min = min;
            Max = max;
            Metric = metric;
            Reason = reason;
        }

        public float Value { get; }
        public float Min { get; }
        public float Max { get; }
        public string Metric { get; }
        public string Reason { get; }

        public AiParam With(float value) => new(value, Min, Max, Metric, Reason);
    }

    public sealed partial class Catalog
    {
        /// <summary>The AI and economy parameters of prompt 28 (balance.json "ai").</summary>
        public AiParams Ai { get; internal set; } = new();
    }

    /// <summary>
    /// The AI parameter frame (prompt 28 L): balance.json "ai", generated from the research sheet by
    /// Tools/ai/import_ai_xlsx.py. Parameters are addressed "section.key" ("params.switchMargin",
    /// "economy.escalation.2"); a missing one reads as its sheet starting value, so old data still plays.
    /// </summary>
    public sealed class AiParams
    {
        private readonly SortedDictionary<string, AiParam> _all;

        private AiParams(SortedDictionary<string, AiParam> all) => _all = all;

        public AiParams() : this(new SortedDictionary<string, AiParam>(StringComparer.Ordinal)) { }

        /// <summary>Every parameter's key, in ordinal order (a stable order for the sweep and for replays).</summary>
        public IEnumerable<string> Keys => _all.Keys;

        public bool Has(string key) => _all.ContainsKey(key);

        public AiParam Param(string key) =>
            _all.TryGetValue(key, out var p) ? p : throw new KeyNotFoundException($"ai.{key}: no such parameter.");

        public float Get(string key, float fallback) => _all.TryGetValue(key, out var p) ? p.Value : fallback;

        /// <summary>A copy with one value replaced (the sweep tool's run; the range and notes stay).</summary>
        public AiParams With(string key, float value)
        {
            var copy = new SortedDictionary<string, AiParam>(_all, StringComparer.Ordinal);
            copy[key] = Param(key).With(value);
            return new AiParams(copy);
        }


        // World Model (A.1, M.1).
        public float WorldRate => Get("world.rate", 2f);
        public float WorldCell => Get("world.cell", 10f);

        // The sheet "Tham số AI".
        public float AttackThreshold => Get("params.attackThreshold", 1.2f);
        public float FallbackRatio => Get("params.fallbackRatio", 0.6f);
        public float SwitchMargin => Get("params.switchMargin", 8f);
        public float MinCommit => Get("params.minCommit", 4f);
        public float IdleReassess => Get("params.idleReassess", 5f);
        public float StuckTime => Get("params.stuckTime", 3f);
        public float EmergencyCooldown => Get("params.emergencyCooldown", 25f);
        public float OverwhelmRatio => Get("params.overwhelmRatio", 2f);
        /// <summary>Confidence lost per second since an enemy was last seen (0.06: about half left after 8 s).</summary>
        public float ConfidenceDecay => Get("params.confidenceDecay", 0.06f);
        public float SplashSpread => Get("params.splashSpread", 1f);
        public float ReactionDelay => Get("params.reactionDelay", 0.8f);
        public float FlankWeight => Get("params.flankWeight", 1f);
        public float FocusWeight => Get("params.focusWeight", 1f);
        public float Cohesion => Get("params.cohesion", 1f);
        public float ArtilleryPrep => Get("params.artilleryPrep", 0f);
        public float AirAaLimit => Get("params.airAaLimit", 1f);
        public float HoldFire => Get("params.holdFire", 0f);
        public float MainEffort => Get("params.mainEffort", 0.5f);
        public float CpSaving => Get("params.cpSaving", 0f);
        public float TacticCooldown => Get("params.tacticCooldown", 50f);
        public float TacticTransition => Get("params.tacticTransition", 5f);

        internal static AiParams Parse(JsonObject ai)
        {
            var all = new SortedDictionary<string, AiParam>(StringComparer.Ordinal);
            foreach (var section in ai.Raw)
            {
                if (section.Value == null) continue;
                var entries = new JsonObject(section.Value, "balance.ai." + section.Key);
                foreach (var entry in entries.Raw)
                {
                    var key = section.Key + "." + entry.Key;
                    if (entry.Value is List<object?> list)
                    {
                        var i = 0;
                        foreach (var item in list)
                        {
                            var o = new JsonObject(item, $"balance.ai.{key}[{i}]");
                            all[key + "." + i] = Read(o);
                            i++;
                        }
                    }
                    else
                    {
                        all[key] = Read(new JsonObject(entry.Value, "balance.ai." + key));
                    }
                }
            }
            return new AiParams(all);
        }

        private static AiParam Read(JsonObject o)
        {
            var value = o.Float("value");
            var min = o.Float("min", value);
            var max = o.Float("max", value);
            if (min > max) throw new FormatException($"{o.Path}: min {min} > max {max}.");
            return new AiParam(value, min, max, o.OptionalString("metric") ?? "", o.OptionalString("reason") ?? "");
        }
    }
}
