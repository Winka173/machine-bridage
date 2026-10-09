#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Boss design workbook 09/10: balance.json "bossDesign", one row per boss or variant id, laid over the raw entry before the
    /// templates are built, so the workbook's numbers sit in one block and are easy to tune. Row keys (all optional):
    /// "hp", "gunNerf" {damage, rate}, "newGunDps" (copied onto the entry); "set" {key: value} (top-level keys replaced, an object
    /// merged one level; null removes the key); "unpart" [ids] (parts taken off, their mounts stay: the radar parts); "tune"
    /// {part id: {fields}}; "add" [parts] (library "use" parts; a variant gets them through its variant.add); "drop" [ids]
    /// (parts and the mounts only they carried, as "dropParts" / variant.drop); "keep" [ids] (a variant's keep list).
    /// A row naming no entry is an error.
    /// </summary>
    internal static partial class BossTemplates
    {
        private static void ApplyDesign(JsonObject root, List<JsonObject> entries)
        {
            var design = Raw(root, "bossDesign");
            if (design.Count == 0) return;
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var e in entries)
            {
                var raw = e.Raw;
                if (!raw.TryGetValue("id", out var idv) || idv is not string id || !design.TryGetValue(id, out var rowv)) continue;
                if (rowv is not Dictionary<string, object?> row) throw new FormatException($"bossDesign.{id}: an object is expected.");
                seen.Add(id);
                Design(raw, row, $"bossDesign.{id}");
            }
            foreach (var key in design.Keys)
                if (!seen.Contains(key) && !key.StartsWith("_", StringComparison.Ordinal)) throw new FormatException($"bossDesign.{key}: no vehicle entry of that id.");
        }

        private static void Design(Dictionary<string, object?> raw, Dictionary<string, object?> row, string path)
        {
            var variant = raw.ContainsKey("variantOf");
            Dictionary<string, object?> Rules()
            {
                if (!raw.TryGetValue("variant", out var v) || v is not Dictionary<string, object?> rules) raw["variant"] = rules = new Dictionary<string, object?>();
                return rules;
            }
            List<object?> ListOf(Dictionary<string, object?> d, string key)
            {
                if (!d.TryGetValue(key, out var l) || l is not List<object?> list) d[key] = list = new List<object?>();
                return list;
            }
            foreach (var pair in row)
            {
                var value = pair.Value;
                switch (pair.Key)
                {
                    case "hp":
                    case "gunNerf":
                    case "newGunDps":
                        raw[pair.Key] = Clone(value);
                        break;
                    case "set":
                        if (value is not Dictionary<string, object?> set) throw new FormatException($"{path}.set: an object is expected.");
                        foreach (var kv in set)
                        {
                            if (kv.Value == null) { if (variant) raw[kv.Key] = null; else raw.Remove(kv.Key); }
                            else if (kv.Value is Dictionary<string, object?> sub && raw.TryGetValue(kv.Key, out var under) && under is Dictionary<string, object?> ud) raw[kv.Key] = Merge(ud, sub);
                            else raw[kv.Key] = Clone(kv.Value);
                        }
                        break;
                    case "unpart":
                        if (variant) throw new FormatException($"{path}.unpart: a variant takes it from its parent's row.");
                        if (raw.TryGetValue("parts", out var pl) && pl is List<object?> parts && value is List<object?> ids)
                        {
                            var gone = Strings(ids);
                            parts.RemoveAll(o => o is Dictionary<string, object?> pd && pd.TryGetValue("id", out var pid) && pid is string ps && gone.Contains(ps));
                        }
                        break;
                    case "tune":
                        if (value is not Dictionary<string, object?> tune) throw new FormatException($"{path}.tune: an object is expected.");
                        if (variant)
                        {
                            var rules = Rules();
                            rules["tune"] = rules.TryGetValue("tune", out var old) && old is Dictionary<string, object?> od ? MergeTune(od, tune) : Clone(tune);
                        }
                        else if (raw.TryGetValue("parts", out var pl2) && pl2 is List<object?> parts2)
                        {
                            foreach (var kv in tune)
                            {
                                var found = false;
                                foreach (var o in parts2)
                                    if (o is Dictionary<string, object?> part && part.TryGetValue("id", out var pid) && pid as string == kv.Key && kv.Value is Dictionary<string, object?> fields)
                                    {
                                        foreach (var f in fields) part[f.Key] = Clone(f.Value);
                                        found = true;
                                    }
                                if (!found) throw new FormatException($"{path}.tune.{kv.Key}: no such part.");
                            }
                        }
                        break;
                    case "add":
                        if (value is not List<object?> add) throw new FormatException($"{path}.add: a list is expected.");
                        foreach (var a in add) ListOf(variant ? Rules() : raw, variant ? "add" : "parts").Add(Clone(a));
                        break;
                    case "drop":
                        if (value is not List<object?> drop) throw new FormatException($"{path}.drop: a list is expected.");
                        foreach (var a in drop) ListOf(variant ? Rules() : raw, variant ? "drop" : "dropParts").Add(a);
                        break;
                    case "keep":
                        if (!variant) throw new FormatException($"{path}.keep: only a variant keeps parts.");
                        Rules()["keep"] = Clone(value);
                        break;
                    case "note":
                        break;
                    default:
                        throw new FormatException($"{path}.{pair.Key}: unknown design key.");
                }
            }
        }

        private static Dictionary<string, object?> MergeTune(Dictionary<string, object?> under, Dictionary<string, object?> over)
        {
            var d = Copy(under);
            foreach (var kv in over)
                d[kv.Key] = kv.Value is Dictionary<string, object?> f && d.TryGetValue(kv.Key, out var u) && u is Dictionary<string, object?> uf ? Merge(uf, f) : Clone(kv.Value);
            return d;
        }
    }
}
