#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 20 E (DECISIONS 19E): the boss templates, so a new boss is mostly data. Before the vehicles are
    /// parsed, every boss entry in balance.json is built from:
    /// <list type="bullet">
    /// <item>its body frame ("frame", balance.json "bossFrames": tracked, wheeled, train, ship, submarine,
    /// aircraft, spacecraft): the frame's "defaults" go under the entry (an object field such as "tiers",
    /// "naval" or "burrow" merged one level deep, the entry's keys winning; a null removes one);</item>
    /// <item>the shared part and weapon library (a part with "use", balance.json "bossParts"): the library
    /// part's fields under the entry's; a library part with a "weapon" and no "mounts" adds its own weapon
    /// mount (slot, aim, arc) to the boss and carries it;</item>
    /// <item>"dropParts": parts left off with the mounts only they carried and the skills only they drove
    /// (a mini boss's lighter armament, prompt 20 G.3); their model nodes are hidden
    /// ("hiddenNodes");</item>
    /// <item>"size": the prompt 20 resize (F.1, G.2): the model, the hull, the hit radius, the parts'
    /// positions and radii, the attached models, the landing ramp and the death blast together;</item>
    /// <item>a variant ("variantOf" a boss, with "variant": size, keep, drop, tune, tint, mark, name): the
    /// parent's built data (its model too), cut down to the parts it keeps, resized, the entry's own fields
    /// on top. Its phases, radio line, big attack and variant fields are its own;</item>
    /// <item>its rank ("rank": main or mini, balance.json "bossRanks"): a mini's health share, weapon and
    /// big-attack scaling, and each rank's default phases for a boss with none of its own (not a tiered
    /// boss: its tier marks are its phases).</item>
    /// </list>
    /// Big attacks may inherit another ("from"), their strikes merged by index. Nothing here touches the
    /// sim: the result is ordinary vehicle data, parsed as before.
    /// </summary>
    internal static class BossTemplates
    {
        /// <summary>Keys a variant never takes from its parent.</summary>
        private static readonly string[] NotInherited =
        {
            "id", "rank", "variantOf", "variant", "phases", "radioSpawn", "bigAttack", "bigAttackScale", "damageScale", "weaponDamage", "mountWeapons",
            "size", "dropParts", "tint", "mark", "variantName", "hiddenNodes",
        };

        /// <summary>Every vehicle entry, bosses built from their templates, in data order.</summary>
        public static List<JsonObject> Expand(JsonObject root, IEnumerable<JsonObject> vehicles)
        {
            var frames = Raw(root, "bossFrames");
            var library = Raw(root, "bossParts");
            var ranks = Raw(root, "bossRanks");
            var entries = new List<JsonObject>(vehicles);
            var built = new Dictionary<string, object?>[entries.Count];
            var beforeRank = new Dictionary<string, Dictionary<string, object?>>();
            // Bosses and variants first without their variants' parents; then the variants.
            for (var pass = 0; pass < 2; pass++)
                for (var i = 0; i < entries.Count; i++)
                {
                    var raw = entries[i].Raw;
                    var variant = raw.TryGetValue("variantOf", out var parentId) && parentId is string;
                    if (variant != (pass == 1)) continue;
                    if (!variant && !IsTemplated(raw))
                    {
                        built[i] = raw;
                        continue;
                    }
                    var path = entries[i].Path;
                    Dictionary<string, object?> d;
                    if (variant)
                    {
                        var parent = (string)parentId!;
                        if (!beforeRank.TryGetValue(parent, out var from)) throw new FormatException($"{path}.variantOf: '{parent}' is no boss built before it.");
                        d = Variant(from, raw, parent, path);
                    }
                    else
                    {
                        d = Build(Copy(raw), frames, library, path);
                        if (d.ContainsKey("dropParts") && d["dropParts"] is List<object?> drop)
                        {
                            var dropped = Strings(drop);
                            Strip(d, id => !dropped.Contains(id));
                        }
                        Resize(d, Number(d, "size", 1f));
                    }
                    MountWeapons(d, path);
                    if (d.TryGetValue("id", out var idValue) && idValue is string id) beforeRank[id] = Copy(d);
                    Rank(d, ranks, path);
                    built[i] = d;
                }
            var result = new List<JsonObject>(entries.Count);
            for (var i = 0; i < entries.Count; i++) result.Add(new JsonObject(built[i], entries[i].Path));
            return result;
        }

        /// <summary>A boss entry, or one naming a frame, a rank or a library part.</summary>
        private static bool IsTemplated(Dictionary<string, object?> raw) =>
            raw.TryGetValue("boss", out var boss) && boss is true || raw.ContainsKey("frame") || raw.ContainsKey("rank");

        // ================================================================== frame and part library

        private static Dictionary<string, object?> Build(Dictionary<string, object?> d, Dictionary<string, object?> frames, Dictionary<string, object?> library, string path)
        {
            if (d.TryGetValue("frame", out var f) && f is string frameId)
            {
                if (!frames.TryGetValue(frameId, out var frame) || frame is not Dictionary<string, object?> fd) throw new FormatException($"{path}.frame: unknown body frame '{frameId}'.");
                if (fd.TryGetValue("defaults", out var defaults) && defaults is Dictionary<string, object?> dd) d = Merge(dd, d);
            }
            if (d.TryGetValue("parts", out var p) && p is List<object?> parts)
            {
                var secondary = d.TryGetValue("secondary", out var s) && s is List<object?> list ? new List<object?>(list) : new List<object?>();
                for (var k = 0; k < parts.Count; k++)
                {
                    if (parts[k] is not Dictionary<string, object?> part || !part.TryGetValue("use", out var u) || u is not string use) continue;
                    if (!library.TryGetValue(use, out var lib) || lib is not Dictionary<string, object?> ld) throw new FormatException($"{path}.parts[{k}].use: unknown library part '{use}'.");
                    var merged = Merge(ld, part);
                    merged.Remove("use");
                    if (merged.TryGetValue("weapon", out var w) && w is string weapon)
                    {
                        if (!merged.ContainsKey("mounts"))
                        {
                            var mount = new Dictionary<string, object?> { ["weapon"] = weapon };
                            foreach (var key in new[] { "slot", "aim", "arc", "model" })
                                if (merged.TryGetValue(key, out var value) && value != null) mount[key] = value;
                            if (!mount.ContainsKey("slot")) mount["slot"] = "gun";
                            secondary.Add(mount);
                            merged["mounts"] = new List<object?> { (double)secondary.Count };
                        }
                        foreach (var key in new[] { "weapon", "slot", "aim", "arc", "model" }) merged.Remove(key);
                    }
                    parts[k] = merged;
                }
                if (secondary.Count > 0) d["secondary"] = secondary;
            }
            return d;
        }

        /// <summary>
        /// Prompt 26 B.7: "mountWeapons" {"mount index": "weapon id"} on a boss swaps the weapon on those mounts of the boss as built
        /// (0 the main weapon, then the secondary list), after its parts and variants are cut down and before its variants are
        /// cut from it, so a variant takes the swapped weapons with the mounts it keeps (and may swap its own).
        /// </summary>
        private static void MountWeapons(Dictionary<string, object?> d, string path)
        {
            if (!d.TryGetValue("mountWeapons", out var mw) || mw is not Dictionary<string, object?> swaps) return;
            d.Remove("mountWeapons");
            var secondary = d.TryGetValue("secondary", out var s) && s is List<object?> list ? list : new List<object?>();
            foreach (var pair in swaps)
            {
                if (!int.TryParse(pair.Key, out var index) || index < 0 || index > secondary.Count || pair.Value is not string weapon)
                    throw new FormatException($"{path}.mountWeapons: '{pair.Key}' is no mount of this boss ({1 + secondary.Count}), or its weapon is no id.");
                if (index == 0) d["weapon"] = weapon;
                else if (secondary[index - 1] is Dictionary<string, object?> mount) mount["weapon"] = weapon;
            }
        }

        /// <summary>The parts <paramref name="keep"/> says stay, and the mounts and skills that only the others carried gone.</summary>
        private static void Strip(Dictionary<string, object?> d, Func<string, bool> keep)
        {
            if (!d.TryGetValue("parts", out var p) || p is not List<object?> parts) return;
            var secondary = d.TryGetValue("secondary", out var s) && s is List<object?> list ? list : new List<object?>();
            var mounts = 1 + secondary.Count;
            var kept = new List<object?>();
            var keptMounts = new HashSet<int>();
            var droppedMounts = new HashSet<int>();
            var keptSkills = new HashSet<string>();
            var droppedSkills = new HashSet<string>();
            var hidden = d.TryGetValue("hiddenNodes", out var h) && h is List<object?> hl ? new List<object?>(hl) : new List<object?>();
            foreach (var o in parts)
            {
                if (o is not Dictionary<string, object?> part) continue;
                var id = part.TryGetValue("id", out var i) && i is string pid ? pid : "";
                var stays = keep(id);
                if (stays) kept.Add(part);
                // A dropped weapon is not drawn; a dropped engine or bay stays on the model (only no longer a part).
                else if (part.TryGetValue("node", out var node) && node is string n && part.TryGetValue("mounts", out var pm) && pm is List<object?> { Count: > 0 }) hidden.Add(n);
                foreach (var m in Ints(part, "mounts")) (stays ? keptMounts : droppedMounts).Add(m);
                if (part.TryGetValue("skills", out var sk) && sk is List<object?> skills)
                    foreach (var name in Strings(skills)) (stays ? keptSkills : droppedSkills).Add(name);
            }
            if (kept.Count == parts.Count) return;
            // Old mount index to new (-1: gone). A mount on no part stays.
            var gone = new bool[mounts];
            for (var m = 0; m < mounts; m++) gone[m] = droppedMounts.Contains(m) && !keptMounts.Contains(m);
            var order = new List<int>();
            for (var m = 0; m < mounts; m++)
                if (!gone[m]) order.Add(m);
            if (order.Count == 0) throw new FormatException($"{d["id"]}: a boss needs one weapon left after dropping parts.");
            if (gone[0])
            {
                // The main weapon gone: the first mount left is the main one now.
                var promoted = (Dictionary<string, object?>)secondary[order[0] - 1]!;
                d["weapon"] = promoted["weapon"];
                d["mainSlot"] = promoted.TryGetValue("slot", out var slot) ? slot : "main";
                if (promoted.TryGetValue("aim", out var aim) && aim != null) d["mainAim"] = aim;
                else d.Remove("mainAim");
                if (promoted.TryGetValue("model", out var model) && model != null) d["mainModel"] = model;
                else d.Remove("mainModel");
            }
            var remap = new Dictionary<int, int>();
            for (var k = 0; k < order.Count; k++) remap[order[k]] = k;
            var newSecondary = new List<object?>();
            for (var k = 1; k < order.Count; k++) newSecondary.Add(secondary[order[k] - 1]);
            d["secondary"] = newSecondary;
            foreach (var o in kept)
            {
                var part = (Dictionary<string, object?>)o!;
                foreach (var key in new[] { "mounts", "affects" })
                {
                    if (!part.ContainsKey(key)) continue;
                    var list2 = new List<object?>();
                    foreach (var m in Ints(part, key))
                        if (remap.TryGetValue(m, out var n)) list2.Add((double)n);
                    part[key] = list2;
                }
            }
            if (d.TryGetValue("tiers", out var t) && t is Dictionary<string, object?> tiers && tiers.TryGetValue("crash", out var c) && c is Dictionary<string, object?> crash)
            {
                var guns = new List<object?>();
                foreach (var m in Ints(crash, "guns"))
                    if (remap.TryGetValue(m, out var n)) guns.Add((double)n);
                crash["guns"] = guns;
            }
            // Prompt 26 B.5: the mounts that wake in the second phase follow the others.
            if (d.TryGetValue("wake", out var wk) && wk is Dictionary<string, object?> wake)
            {
                var woken = new List<object?>();
                foreach (var m in Ints(wake, "mounts"))
                    if (remap.TryGetValue(m, out var n)) woken.Add((double)n);
                wake["mounts"] = woken;
            }
            if (d.TryGetValue("skills", out var ks) && ks is List<object?> own)
            {
                var left = new List<object?>();
                foreach (var name in Strings(own))
                    if (!droppedSkills.Contains(name) || keptSkills.Contains(name)) left.Add(name);
                d["skills"] = left;
            }
            d["parts"] = kept;
            if (hidden.Count > 0) d["hiddenNodes"] = hidden;
        }

        /// <summary>Resizes a boss: the model and hull ("scale"), the hit radius, its parts, attachments, ramp and death blast.</summary>
        private static void Resize(Dictionary<string, object?> d, float size)
        {
            if (MathF.Abs(size - 1f) < 1e-4f) return;
            d["scale"] = (double)(Number(d, "scale", 1f) * size);
            if (d.ContainsKey("radius")) d["radius"] = (double)(Number(d, "radius", 1f) * size);
            if (d.TryGetValue("parts", out var p) && p is List<object?> parts)
                foreach (var o in parts)
                {
                    if (o is not Dictionary<string, object?> part) continue;
                    if (part.TryGetValue("at", out var at) && at is List<object?> xyz) part["at"] = Scaled(xyz, size);
                    part["radius"] = (double)(Number(part, "radius", 2f) * size);
                }
            if (d.TryGetValue("attach", out var a) && a is List<object?> attach)
                foreach (var o in attach)
                    if (o is Dictionary<string, object?> m && m.TryGetValue("at", out var at) && at is List<object?> xyz) m["at"] = Scaled(xyz, size);
            if (d.TryGetValue("landing", out var l) && l is Dictionary<string, object?> landing && landing.TryGetValue("ramp", out var r) && r is List<object?> ramp)
                landing["ramp"] = Scaled(ramp, size);
            if (d.TryGetValue("deathExplosion", out var e) && e is Dictionary<string, object?> blast)
                blast["radius"] = (double)(Number(blast, "radius", 6f) * MathF.Sqrt(size));
        }

        private static List<object?> Scaled(List<object?> xyz, float size)
        {
            var list = new List<object?>(xyz.Count);
            foreach (var v in xyz) list.Add(v is double x ? x * size : v);
            return list;
        }

        // ================================================================== variants

        /// <summary>A mini boss from a boss's data (prompt 20 E.5): its parts cut down, resized, recoloured, its own fields on top.</summary>
        private static Dictionary<string, object?> Variant(Dictionary<string, object?> parent, Dictionary<string, object?> own, string parentId, string path)
        {
            var d = Copy(parent);
            foreach (var key in NotInherited) d.Remove(key);
            // It is drawn with its parent's model.
            if (!d.ContainsKey("model")) d["model"] = parentId;
            var rules = own.TryGetValue("variant", out var v) && v is Dictionary<string, object?> vd ? vd : new Dictionary<string, object?>();
            if (rules.TryGetValue("keep", out var k) && k is List<object?> keepList)
            {
                var keep = Strings(keepList);
                foreach (var id in keep)
                    if (!HasPart(d, id)) throw new FormatException($"{path}.variant.keep: '{parentId}' has no part '{id}'.");
                Strip(d, id => keep.Contains(id));
            }
            if (rules.TryGetValue("drop", out var dr) && dr is List<object?> dropList)
            {
                var drop = Strings(dropList);
                Strip(d, id => !drop.Contains(id));
            }
            // Part by part changes (a thinner hull's parts, a hardened one).
            if (rules.TryGetValue("tune", out var t) && t is Dictionary<string, object?> tune && d.TryGetValue("parts", out var p) && p is List<object?> parts)
                for (var i = 0; i < parts.Count; i++)
                    if (parts[i] is Dictionary<string, object?> part && part.TryGetValue("id", out var pid) && pid is string id && tune.TryGetValue(id, out var over) && over is Dictionary<string, object?> od)
                        parts[i] = Merge(part, od);
            Resize(d, Number(rules, "size", 0.7f));
            // Its own fields over its parent's (the whole value: a list or an object it names is its own).
            foreach (var pair in own)
            {
                if (pair.Key is "variant") continue;
                if (pair.Value is Dictionary<string, object?> sub && d.TryGetValue(pair.Key, out var under) && under is Dictionary<string, object?> ud) d[pair.Key] = Merge(ud, sub);
                else d[pair.Key] = Clone(pair.Value);
            }
            if (rules.TryGetValue("tint", out var tint) && tint != null) d["tint"] = Clone(tint);
            if (rules.TryGetValue("mark", out var mark) && mark != null) d["mark"] = mark;
            if (rules.TryGetValue("name", out var name) && name != null) d["variantName"] = name;
            d["variantOf"] = parentId;
            d["boss"] = true;
            if (!d.ContainsKey("rank")) d["rank"] = "mini";
            return d;
        }

        private static bool HasPart(Dictionary<string, object?> d, string id)
        {
            if (!d.TryGetValue("parts", out var p) || p is not List<object?> parts) return false;
            foreach (var o in parts)
                if (o is Dictionary<string, object?> part && part.TryGetValue("id", out var pid) && pid as string == id) return true;
            return false;
        }

        // ================================================================== ranks

        private static void Rank(Dictionary<string, object?> d, Dictionary<string, object?> ranks, string path)
        {
            if (!(d.TryGetValue("boss", out var boss) && boss is true)) return;
            var rank = d.TryGetValue("rank", out var r) && r is string name ? name : "main";
            d["rank"] = rank;
            if (!ranks.TryGetValue(rank, out var rr) || rr is not Dictionary<string, object?> rules)
            {
                if (ranks.Count > 0) throw new FormatException($"{path}.rank: unknown boss rank '{rank}'.");
                return;
            }
            if (rules.TryGetValue("hp", out var hp) && hp is double share && d.TryGetValue("hp", out var h) && h is double own) d["hp"] = own * share;
            foreach (var key in new[] { "damageScale", "bigAttackScale" })
                if (!d.ContainsKey(key) && rules.TryGetValue(key, out var value) && value != null) d[key] = Clone(value);
            // Prompt 26 A.5: the breakable parts' health comes on top of the body's, about a third of it in all.
            if (rules.TryGetValue("partsShare", out var ps) && ps is double partsShare && d.TryGetValue("parts", out var pl) && pl is List<object?> partList)
            {
                var sum = 0.0;
                foreach (var o in partList)
                    if (o is Dictionary<string, object?> part && part.TryGetValue("hp", out var ph) && ph is double phv) sum += phv;
                if (sum > 0.0)
                    foreach (var o in partList)
                        if (o is Dictionary<string, object?> part && part.TryGetValue("hp", out var ph) && ph is double phv)
                            part["hp"] = Math.Round(Math.Max(0.004, phv * partsShare / sum), 4);
            }
            var tiered = d.TryGetValue("tiers", out var t) && t != null;
            if (!d.ContainsKey("phases") && !tiered && rules.TryGetValue("phases", out var phases) && phases != null) d["phases"] = Clone(phases);
        }

        // ================================================================== big attacks

        /// <summary>The big attacks, an entry with "from" built on the one it names (its strikes merged by index).</summary>
        public static List<JsonObject> BigAttacks(JsonObject root)
        {
            var entries = new List<JsonObject>(root.Array("bigAttacks"));
            var byId = new Dictionary<string, Dictionary<string, object?>>();
            foreach (var e in entries)
                if (e.Raw.TryGetValue("id", out var id) && id is string s) byId[s] = e.Raw;
            Dictionary<string, object?> Resolve(Dictionary<string, object?> e, string path, int depth)
            {
                if (!e.TryGetValue("from", out var f) || f is not string from) return e;
                if (depth > 3 || !byId.TryGetValue(from, out var parent)) throw new FormatException($"{path}.from: unknown big attack '{from}'.");
                var baseDef = Copy(Resolve(parent, path, depth + 1));
                foreach (var pair in e)
                {
                    if (pair.Key is "from") continue;
                    if (pair.Key == "strikes" && pair.Value is List<object?> strikes && baseDef.TryGetValue("strikes", out var bs) && bs is List<object?> baseStrikes)
                    {
                        for (var i = 0; i < strikes.Count; i++)
                        {
                            if (strikes[i] is not Dictionary<string, object?> sd) continue;
                            if (i < baseStrikes.Count && baseStrikes[i] is Dictionary<string, object?> under) baseStrikes[i] = Merge(under, sd);
                            else baseStrikes.Add(Copy(sd));
                        }
                        continue;
                    }
                    baseDef[pair.Key] = Clone(pair.Value);
                }
                return baseDef;
            }
            var result = new List<JsonObject>(entries.Count);
            foreach (var e in entries) result.Add(new JsonObject(Resolve(e.Raw, e.Path, 0), e.Path));
            return result;
        }

        // ================================================================== escort templates

        /// <summary>
        /// The escort tables: each entry with "template" built on that general's (balance.json "escortTemplates"), and
        /// a boss with no entry given its general's (a new boss needs none of its own).
        /// </summary>
        public static List<JsonObject> Escorts(JsonObject root, IEnumerable<VehicleDef> bosses, IReadOnlyDictionary<string, VehicleDef>? vehicles = null)
        {
            var built = EscortTables(root, bosses);
            if (vehicles == null) return built;
            // Play-test 14: an escort keeps to its boss's domain (a ground boss ground vehicles, a ship boats, an aircraft
            // aircraft); a unit of another domain in its table stands down for the domain's unit of its role
            // (balance.json escortRules.domains), so Nyx never brings tanks out to sea.
            var domains = root.Has("escortRules") && root.Object("escortRules").Has("domains") ? root.Object("escortRules").Object("domains").Raw : null;
            if (domains == null) return built;
            var result = new List<JsonObject>();
            foreach (var e in built)
            {
                var raw = e.Raw;
                if (raw.TryGetValue("boss", out var b) && b is string boss && vehicles.TryGetValue(boss, out var bossDef) &&
                    domains.TryGetValue(Domain(bossDef), out var dv) && dv is Dictionary<string, object?> table)
                {
                    raw = Copy(raw);
                    KeepDomain(raw, Domain(bossDef), table, vehicles);
                }
                result.Add(new JsonObject(raw, e.Path));
            }
            return result;
        }

        /// <summary>Play-test 14: a unit's domain: "sea" (a ship), "air" (it flies) or "ground".</summary>
        internal static string Domain(VehicleDef def) => def.Naval != null || def.NavalOnly ? "sea" : def.Flying ? "air" : "ground";

        /// <summary>Every "unit" in the table of another domain than <paramref name="domain"/> becomes the domain's unit of its role.</summary>
        private static void KeepDomain(Dictionary<string, object?> raw, string domain, Dictionary<string, object?> table,
            IReadOnlyDictionary<string, VehicleDef> vehicles)
        {
            if (raw.TryGetValue("unit", out var u) && u is string unit && vehicles.TryGetValue(unit, out var def) && Domain(def) != domain)
            {
                var role = raw.TryGetValue("role", out var r) && r is string roleName ? roleName.ToLowerInvariant() : "guard";
                var swap = table.TryGetValue(role, out var s) && s is string byRole ? byRole : table.TryGetValue("default", out var d) && d is string fallback ? fallback : null;
                // "unit:role": the stand-in takes another role (a jammer's place in the air is air cover).
                string? newRole = null;
                if (swap != null && swap.IndexOf(':') > 0)
                {
                    newRole = swap.Substring(swap.IndexOf(':') + 1);
                    swap = swap.Substring(0, swap.IndexOf(':'));
                }
                if (swap != null && vehicles.ContainsKey(swap))
                {
                    raw["unit"] = swap;
                    raw.Remove("elite");
                    if (newRole != null) raw["role"] = newRole;
                }
            }
            foreach (var key in new List<string>(raw.Keys))
            {
                if (key == "fleet") continue;
                switch (raw[key])
                {
                    case Dictionary<string, object?> child:
                        raw[key] = child = Copy(child);
                        KeepDomain(child, domain, table, vehicles);
                        break;
                    case List<object?> list:
                        var copy = new List<object?>(list.Count);
                        foreach (var item in list)
                        {
                            if (item is Dictionary<string, object?> c)
                            {
                                var cc = Copy(c);
                                KeepDomain(cc, domain, table, vehicles);
                                copy.Add(cc);
                            }
                            else copy.Add(item);
                        }
                        raw[key] = copy;
                        break;
                }
            }
        }

        private static List<JsonObject> EscortTables(JsonObject root, IEnumerable<VehicleDef> bosses)
        {
            var templates = Raw(root, "escortTemplates");
            var result = new List<JsonObject>();
            var listed = new HashSet<string>();
            foreach (var e in root.Array("escorts"))
            {
                var raw = e.Raw;
                if (raw.TryGetValue("boss", out var b) && b is string boss) listed.Add(boss);
                if (raw.TryGetValue("template", out var t) && t is string name)
                {
                    if (!templates.TryGetValue(name, out var tv) || tv is not Dictionary<string, object?> td) throw new FormatException($"{e.Path}.template: no escort template '{name}'.");
                    raw = Merge(td, raw);
                }
                result.Add(new JsonObject(raw, e.Path));
            }
            foreach (var def in bosses)
            {
                // A ship sails with its own fleet ("fleet"), never with ground escorts beside it at sea.
                if (listed.Contains(def.Id) || def.Naval != null || def.General == null || !templates.TryGetValue(def.General, out var tv) || tv is not Dictionary<string, object?> td) continue;
                var raw = Copy(td);
                raw["boss"] = def.Id;
                result.Add(new JsonObject(raw, $"balance.escortTemplates.{def.General}"));
            }
            return result;
        }

        // ================================================================== helpers

        private static Dictionary<string, object?> Raw(JsonObject root, string key) =>
            root.Has(key) ? root.Object(key).Raw : new Dictionary<string, object?>();

        /// <summary><paramref name="over"/>'s fields on a copy of <paramref name="under"/>'s, objects merged one level deep.</summary>
        internal static Dictionary<string, object?> Merge(Dictionary<string, object?> under, Dictionary<string, object?> over)
        {
            var d = Copy(under);
            foreach (var pair in over)
            {
                if (pair.Value is Dictionary<string, object?> sub && d.TryGetValue(pair.Key, out var u) && u is Dictionary<string, object?> ud)
                {
                    var m = Copy(ud);
                    foreach (var inner in sub) m[inner.Key] = Clone(inner.Value);
                    d[pair.Key] = m;
                }
                else d[pair.Key] = Clone(pair.Value);
            }
            return d;
        }

        internal static Dictionary<string, object?> Copy(Dictionary<string, object?> d)
        {
            var c = new Dictionary<string, object?>(d.Count);
            foreach (var pair in d) c[pair.Key] = Clone(pair.Value);
            return c;
        }

        private static object? Clone(object? value) => value switch
        {
            Dictionary<string, object?> d => Copy(d),
            List<object?> l => l.ConvertAll(Clone),
            _ => value,
        };

        private static float Number(Dictionary<string, object?> d, string key, float fallback) =>
            d.TryGetValue(key, out var v) && v is double x ? (float)x : fallback;

        private static IEnumerable<int> Ints(Dictionary<string, object?> d, string key)
        {
            if (!d.TryGetValue(key, out var v) || v is not List<object?> list) yield break;
            foreach (var x in list)
                if (x is double n) yield return (int)Math.Round(n);
        }

        private static HashSet<string> Strings(List<object?> list)
        {
            var set = new HashSet<string>();
            foreach (var x in list)
                if (x is string s) set.Add(s);
            return set;
        }
    }
}
