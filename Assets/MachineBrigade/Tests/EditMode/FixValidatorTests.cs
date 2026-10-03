using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using NUnit.Framework;
using UnityEngine;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Full fix prompt L9 (DECISIONS "Sửa lỗi tổng hợp L9"): the validators for items 1-6 and 8 that run in the build, each the
    /// twin of a check in <c>Tools/balance/fix_validate.py</c> (which also reads the GLBs and the audio analyser). Item 7 (models)
    /// was added by lane C (the script's "models" block). Written, not run (the owner's rule of 30/09); compile-checked by the lead.
    /// Item 3's source figures (the real rates) live in Python: the test reads <c>Docs/checks/fix_validate.json</c> that the script
    /// writes (every used weapon's rounds a cycle and cycle, the audit's flags, the recorded reason) and fails when the
    /// catalog's numbers no longer match it, which means the script must be rerun. Item 8 reads <c>Docs/audio/metrics.json</c>
    /// the same way (the clips' numbers are in the OGG files, not in the build), checking it is current by the clip names.
    /// </summary>
    public class FixValidatorTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        private static string Root(params string[] parts) =>
            Path.GetFullPath(Path.Combine(new[] { Application.dataPath, ".." }.Concat(parts).ToArray()));

        private static Dictionary<string, object> Json(string path)
        {
            Assert.IsTrue(File.Exists(path), path + " is missing: run the Python tool that writes it (Tools/balance/fix_validate.py, Tools/sfx/analyze_sfx.py)");
            return (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(path));
        }

        private static float Num(object o) => Convert.ToSingle(o, System.Globalization.CultureInfo.InvariantCulture);

        // ------------------------------------------------------------------------------------------------ 1: calibre / warhead

        private static readonly HashSet<string> GunFamilies = new HashSet<string>
            { "mg", "autocannon", "tank_gun", "howitzer", "mortar", "naval_gun", "grenade", "recoilless", "rocket" };

        private static readonly HashSet<string> WarheadFamilies = new HashSet<string>
            { "atgm", "aa_missile", "missile", "cruise", "cruise_missile", "ballistic", "bomb", "drone" };

        [Test]
        public void Item1_TheCardsCalibreOrWarheadIsData_NoFieldMixesMmAndKg()
        {
            foreach (var w in C.Weapons.Values)
            {
                var fields = (w.CaliberMm > 0f ? 1 : 0) + (w.WarheadKg > 0f ? 1 : 0) + (w.PowerKw > 0f ? 1 : 0) + (w.EnergyMj > 0f ? 1 : 0);
                Assert.That(fields, Is.LessThanOrEqualTo(1), w.Id + ": one display field at most (mm and kg never mixed)");
                var spec = WeaponInfo.Spec(w);
                Assert.That(spec.Contains(" mm") && spec.Contains(" kg"), Is.False, w.Id + ": the card prints mm and kg together: " + spec);
                if (w.CaliberMm > 0f) Assert.That(spec, Does.EndWith(" mm"), w.Id);
                if (w.WarheadKg > 0f) Assert.That(spec, Does.Contain(" kg"), w.Id);
                if (w.CaliberMm <= 0f) Assert.That(spec, Does.Not.Contain(" mm"), w.Id + ": no calibre on a weapon whose data has none");
                if (w.Family != null && GunFamilies.Contains(w.Family) && w.Size > 0f)
                    Assert.That(w.CaliberMm, Is.EqualTo(w.Size), w.Id + ": a gun's calibre is its round size");
                if (w.Family != null && WarheadFamilies.Contains(w.Family) && w.Size > 0f)
                {
                    Assert.That(w.WarheadKg, Is.GreaterThan(0f), w.Id + ": a missile, bomb or drone has its warhead");
                    Assert.That(w.CaliberMm, Is.EqualTo(0f), w.Id + ": and no calibre");
                }
                if (w.Family == "laser") Assert.That(w.PowerKw, Is.GreaterThan(0f), w.Id);
            }
        }

        // ------------------------------------------------------------------------------------------------ 2: one family, one round

        [Test]
        public void Item2_BossWeaponsOfOneFamilyAndVariantFireTheSameRound()
        {
            var c = C;
            var shared = new HashSet<string>(c.Vehicles.Values.Where(v => !v.Boss).SelectMany(v => v.Mounts.Select(m => m.Weapon.Id)));
            shared.Add("autocannon_40");    // Gungnir's own 40 mm guns, frozen (DECISIONS L3)
            var groups = new Dictionary<string, List<WeaponDef>>();
            foreach (var boss in c.Vehicles.Values.Where(v => v.Boss))
                foreach (var m in boss.Mounts)
                {
                    var w = m.Weapon;
                    if (w.WeaponFamilyId == null || w.Damage <= 0f || shared.Contains(w.Id)) continue;
                    var key = w.WeaponFamilyId + "/" + (w.WeaponVariantId ?? "-");
                    if (!groups.TryGetValue(key, out var list)) groups[key] = list = new List<WeaponDef>();
                    if (!list.Contains(w)) list.Add(w);
                }
            Assert.Greater(groups.Count, 20, "the boss weapons have families");
            var failures = new List<string>();
            foreach (var kv in groups)
            {
                var first = kv.Value[0];
                foreach (var w in kv.Value.Skip(1))
                    if (Mathf.Abs(w.Damage - first.Damage) > 1e-3f || Mathf.Abs(w.SplashRadius - first.SplashRadius) > 1e-3f ||
                        Mathf.Abs(w.SplashEdge - first.SplashEdge) > 1e-3f || Mathf.Abs(w.ProjectileSpeed - first.ProjectileSpeed) > 1e-3f)
                        failures.Add($"{kv.Key}: {first.Id} {first.Damage}/{first.SplashRadius}/{first.SplashEdge}/{first.ProjectileSpeed} against " +
                                     $"{w.Id} {w.Damage}/{w.SplashRadius}/{w.SplashEdge}/{w.ProjectileSpeed}");
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [Test]
        public void Item2_EveryVariantInUseHasItsReason()
        {
            var c = C;
            foreach (var w in c.Weapons.Values.Where(x => x.WeaponVariantId != null))
            {
                Assert.That(w.WeaponFamilyId, Is.Not.Null, w.Id + ": a variant without a family");
                Assert.IsTrue(c.WeaponFamilyTable.TryGetValue(w.WeaponFamilyId, out var family), w.Id + ": family " + w.WeaponFamilyId);
                Assert.IsTrue(family.Variants.TryGetValue(w.WeaponVariantId, out var reason) && !string.IsNullOrWhiteSpace(reason),
                    w.Id + ": variant " + w.WeaponVariantId + " has no reason in weaponFamilyTable");
            }
        }

        // ------------------------------------------------------------------------------------------------ 3: rates against the source

        [Test]
        public void Item3_NoWeaponIsTooFastOrTooSlowAgainstTheSource_ExceptTheRecordedList()
        {
            var c = C;
            var file = Json(Root("Docs", "checks", "fix_validate.json"));
            var weapons = (Dictionary<string, object>)file["weapons"];
            Assert.Greater(weapons.Count, 150, "the check covers every weapon a unit carries");
            var stale = new List<string>();
            var unrecorded = new List<string>();
            foreach (var kv in weapons)
            {
                var row = (Dictionary<string, object>)kv.Value;
                if (!c.Weapons.TryGetValue(kv.Key, out var w)) { stale.Add(kv.Key + ": no longer a weapon"); continue; }
                var cycle = Num(row["cycle"]);
                if (w.RoundsPerCycle != (int)Num(row["n"]) || Mathf.Abs(w.CycleSeconds - cycle) > 0.005f * Mathf.Max(1f, cycle))
                    stale.Add($"{kv.Key}: {w.RoundsPerCycle} rounds / {w.CycleSeconds:0.###} s now, {(int)Num(row["n"])} / {cycle:0.###} s when checked");
                var flags = (List<object>)row["flags"];
                if (flags.Count > 0 && string.IsNullOrEmpty((string)row["reason"]))
                    unrecorded.Add($"{kv.Key}: {string.Join(", ", flags)} with no recorded reason");
            }
            Assert.IsEmpty(stale, "the rates changed since Tools/balance/fix_validate.py ran: rerun it\n" + string.Join("\n", stale));
            Assert.IsEmpty(unrecorded, string.Join("\n", unrecorded));
        }

        // ------------------------------------------------------------------------------------------------ 4: declared targets

        private static float BestAgainst(Catalog c, WeaponDef gun, TargetKind kind, bool flying)
        {
            var best = gun.CanTarget(flying) ? c.Damage.TypeOf(gun, kind) : 0f;
            foreach (var r in gun.Rounds)
            {
                var takes = flying ? (r.Use & RoundUse.Air) != 0 : (r.Use & ~RoundUse.Air) != 0;
                if (takes && r.Round.CanTarget(flying)) best = Math.Max(best, c.Damage.TypeOf(r.Round, kind));
            }
            return best;
        }

        [Test]
        public void Item4_EveryDeclaredTargetHasARoundThatCanDamageIt()
        {
            var c = C;
            var mounted = new HashSet<WeaponDef>(c.Vehicles.Values.SelectMany(v => v.Mounts.Select(m => m.Weapon)));
            var failures = new List<string>();
            foreach (var gun in c.Weapons.Values.Where(w => (w.RoundOf == null || mounted.Contains(w)) && w.Damage > 0f && !w.InterceptOnly).OrderBy(w => w.Id))
            {
                if ((gun.Targets & TargetLayers.Air) != 0 && BestAgainst(c, gun, TargetKind.Air, true) <= 0f)
                    failures.Add($"{gun.Id}: shoots aircraft, no round of it can damage them ({gun.DamageType})");
                if ((gun.Targets & TargetLayers.Ground) != 0 && BestAgainst(c, gun, TargetKind.Ground, false) <= 0f)
                    failures.Add($"{gun.Id}: shoots the ground, no round of it can damage vehicles ({gun.DamageType})");
                if ((gun.Targets & TargetLayers.Ground) != 0 && BestAgainst(c, gun, TargetKind.Structure, false) <= 0f)
                    failures.Add($"{gun.Id}: shoots the ground, no round of it can damage structures ({gun.DamageType})");
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        // ------------------------------------------------------------------------------------------------ 5: warnings and rings

        [Test]
        public void Item5_BigWeaponsWarnAtLeastTheEscapeFormula_AndTheRingIsTheDamageArea()
        {
            var c = C;
            var rules = c.Warnings;
            // The block holds the prompt's formula: floors 2.5 / 3.5 / 4 s, 0.5 s + core / 4.5 m/s, at most 6 s.
            Assert.That(rules.FloorT4, Is.GreaterThanOrEqualTo(2.5f));
            Assert.That(rules.Floor406, Is.GreaterThanOrEqualTo(3.5f));
            Assert.That(rules.FloorT5, Is.GreaterThanOrEqualTo(4f));
            Assert.That(rules.Base, Is.GreaterThanOrEqualTo(0.5f));
            Assert.That(rules.EscapeSpeed, Is.LessThanOrEqualTo(4.5f));
            Assert.That(rules.Cap, Is.InRange(4f, 6f));
            var failures = new List<string>();
            var warned = 0;
            foreach (var w in c.Weapons.Values.OrderBy(x => x.Id))
            {
                var big = (w.Projectile == ProjectileKind.Shell && w.CaliberMm >= rules.GunMinMm) ||
                          (w.Projectile == ProjectileKind.Rocket && w.CaliberMm >= rules.RocketMinMm) ||
                          (w.Projectile == ProjectileKind.Bomb && w.WarheadKg >= rules.BombMinKg);
                var fires = !(w.Guided || w.GuidedRocket || w.Beam || w.Laid) && w.SplashRadius > 0f;
                // Play-test 13 (lane C): the big rounds the rules sort (IsBig); ordinary fire itself no longer warns.
                var warns = rules.IsBig(w);
                if (big && fires && !warns) failures.Add($"{w.Id}: {w.CaliberMm:0.#} mm / {w.WarheadKg:0.#} kg but no warning (tier {w.Tier})");
                if (!warns) continue;
                warned++;
                var floor = w.WeaponFamilyId == "cal_406" ? 3.5f : w.Tier >= 5 ? 4f : 2.5f;
                var need = Math.Min(6f, Math.Max(floor, 0.5f + w.SplashRadius / 4.5f));
                if (w.WarnSeconds < need - 1e-3f) failures.Add($"{w.Id}: warns {w.WarnSeconds:0.##} s, the escape formula needs {need:0.##} s");
                if (w.WarnSeconds > 6f + 1e-3f) failures.Add($"{w.Id}: warns {w.WarnSeconds:0.##} s, over the 6 s cap");
                var area = Math.Max(w.SplashRadius, w.SplashEdge);
                if (Mathf.Abs(w.WarnRadius - area) > 1e-3f || w.WarnRadius < w.SplashRadius || w.WarnRadius <= 0f)
                    failures.Add($"{w.Id}: ring {w.WarnRadius:0.##} m, damage area {area:0.##} m");
                if (w.SplashEdge > 0f && w.SplashEdge < w.SplashRadius) failures.Add($"{w.Id}: edge {w.SplashEdge:0.##} m under its core {w.SplashRadius:0.##} m");
            }
            Assert.Greater(warned, 20, "the warned rounds were reached");
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        // ------------------------------------------------------------------------------------------------ 6: muzzles and flare mounts

        /// <summary>A GLB's nodes (name, children), read from its JSON chunk, or null when the model has no file.</summary>
        private static List<(string name, int[] children)> Nodes(string model)
        {
            var path = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Models", model + ".glb");
            if (!File.Exists(path)) return null;
            var bytes = File.ReadAllBytes(path);
            var length = BitConverter.ToInt32(bytes, 12);
            var json = (Dictionary<string, object>)MiniJson.Parse(Encoding.UTF8.GetString(bytes, 20, length));
            var nodes = (List<object>)json["nodes"];
            var list = new List<(string, int[])>();
            foreach (var o in nodes)
            {
                var node = (Dictionary<string, object>)o;
                var name = node.TryGetValue("name", out var n) ? (string)n : "";
                var kids = node.TryGetValue("children", out var k) ? ((List<object>)k).Select(x => (int)Num(x)).ToArray() : new int[0];
                list.Add((name, kids));
            }
            return list;
        }

        /// <summary>The model a vehicle draws: its own file, else its original's, parent's or tower's (a variant is its parent scaled).</summary>
        private static string ModelOf(Catalog c, VehicleDef v)
        {
            for (var depth = 0; v != null && depth < 6; depth++)
            {
                if (File.Exists(Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Models", v.Model + ".glb"))) return v.Model;
                var parent = v.EliteOf ?? v.VariantOf ?? v.BranchOf ?? (v.Id.Contains(".") ? v.Id.Substring(0, v.Id.IndexOf('.')) : null);
                if (parent == null || !c.Vehicles.TryGetValue(parent, out var next)) return v.Model;
                v = next;
            }
            return v?.Model;
        }

        /// <summary>A launch cell and rocket box with no barrels: one muzzle each (Tools/balance/p34_barrels.KNOWN_MISSING).</summary>
        private static readonly HashSet<string> NoBarrels = new HashSet<string> { "kraken" };

        [Test]
        public void Item6_EveryBarrelThatFiresTogetherHasItsMuzzle()
        {
            var c = C;
            var failures = new List<string>();
            var checkedUnits = 0;
            foreach (var v in c.Vehicles.Values.OrderBy(x => x.Id))
            {
                var guns = v.Mounts.Select(m => m.Weapon).Where(w => w.Simultaneous && w.Barrels > 1).Distinct().ToList();
                if (guns.Count == 0 || NoBarrels.Contains(v.Id)) continue;
                var model = ModelOf(c, v);
                if (NoBarrels.Contains(model)) continue;
                var nodes = Nodes(model);
                if (nodes == null) { failures.Add($"{v.Id}: model '{model}' is not built"); continue; }
                checkedUnits++;
                // A muzzle node holds one Muzzle_b<k>_ child per barrel of its gun.
                var best = 0;
                foreach (var (name, kids) in nodes)
                    if (name.StartsWith("Muzzle_", StringComparison.Ordinal))
                        best = Math.Max(best, kids.Count(k => Regex.IsMatch(nodes[k].name, @"^Muzzle_b\d+_")));
                foreach (var g in guns)
                    if (best < g.Barrels) failures.Add($"{v.Id}: {g.Id} fires {g.Barrels} barrels together, '{model}' has a Muzzle_* node with {best} barrel muzzles at most");
            }
            Assert.Greater(checkedUnits, 10, "the units with barrels firing together were reached");
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        /// <summary>Flare units whose model is not yet built with Mount_Flare_* points: the list stays the truth (fixing one fails here).</summary>
        private static readonly Dictionary<string, string> FlareKnownMissing = new Dictionary<string, string>
        {
            // Play-test 14 deleted Stymphalos, the one unit listed here.
        };

        [Test]
        public void Item6_EveryFlareUnitHasTwoMountFlareNodes()
        {
            var c = C;
            var failures = new List<string>();
            var units = 0;
            foreach (var v in c.Vehicles.Values.OrderBy(x => x.Id))
            {
                if (v.FlareCharges <= 0 && !v.Skills.Any(s => s.Kind == SkillKind.Flares)) continue;
                units++;
                var model = ModelOf(c, v);
                var nodes = Nodes(model);
                if (nodes == null) { failures.Add($"{v.Id}: model '{model}' is not built"); continue; }
                var count = nodes.Count(n => n.name.StartsWith("Mount_Flare_", StringComparison.Ordinal));
                var known = FlareKnownMissing.ContainsKey(v.Id) || FlareKnownMissing.ContainsKey(model);
                if (count >= 2 && known) failures.Add($"{v.Id}: now has {count} Mount_Flare_* points, take it off the known list");
                else if (count < 2 && !known) failures.Add($"{v.Id}: model '{model}' has {count} Mount_Flare_* nodes (needs 2 or more)");
                // The high-detail twin, where there is one, keeps them too.
                var hd = Nodes(model + "_hd");
                if (hd != null && !known && hd.Count(n => n.name.StartsWith("Mount_Flare_", StringComparison.Ordinal)) < 2)
                    failures.Add($"{v.Id}: '{model}_hd' has fewer than 2 Mount_Flare_* nodes");
            }
            Assert.Greater(units, 15, "the flare units were reached");
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [Test]
        public void Item6_TheFlaresSpawnFromTheMountFlareNodes()
        {
            var scripts = Path.Combine(Application.dataPath, "MachineBrigade", "Scripts");
            var view = File.ReadAllText(Path.Combine(scripts, "Game", "Views", "VehicleView.FxPoints.cs"));
            var release = File.ReadAllText(Path.Combine(scripts, "Game", "Effects", "EffectsDirector.Munitions.cs"));
            StringAssert.Contains("FlareMounts() ?? FxPoints(", view, "the view reads the Mount_Flare_* nodes first");
            StringAssert.Contains("IsFlareMount", view, "and finds them by the model library's name rule");
            StringAssert.Contains(".FlarePoints", release, "the release fans its flares from the view's points");
            Assert.That(ModelLibrary_IsFlareMount("Mount_Flare_L"), Is.True);
            Assert.That(ModelLibrary_IsFlareMount("Mount_Flare"), Is.False, "a bare Mount_Flare would read as a weapon mount's pivot");
        }

        private static bool ModelLibrary_IsFlareMount(string name) => MachineBrigade.Game.Rendering.ModelLibrary.IsFlareMount(name);

        // ------------------------------------------------------------------------------------------------ 7: models

        /// <summary>
        /// Item 7 (DECISIONS "Sửa lỗi tổng hợp L9.7/L10 (lane C)"): the model check lives in Python (the pass 8 scorer reads node
        /// names, triangles and ModelScan's LOD1 counts); the test reads the "models" block of fix_validate.json, which must cover
        /// every model a unit draws and hold no failure. Over budget is information only (the owner's rule of 02/10).
        /// </summary>
        [Test]
        public void Item7_EveryModelHasItsPartsAndLod_OverBudgetIsInfoOnly()
        {
            var file = Json(Root("Docs", "checks", "fix_validate.json"));
            Assert.IsTrue(file.ContainsKey("models"), "no models block: run python Tools/balance/fix_validate.py 7");
            var models = (Dictionary<string, object>)file["models"];
            var grades = (Dictionary<string, object>)models["grades"];
            var c = C;
            var unseen = new SortedSet<string>(StringComparer.Ordinal);
            foreach (var v in c.Vehicles.Values)
            {
                var model = ModelOf(c, v);
                if (string.IsNullOrEmpty(model)) continue;
                if (!File.Exists(Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Models", model + ".glb"))) continue;
                if (!grades.ContainsKey(model)) unseen.Add(model + " (" + v.Id + ")");
            }
            Assert.IsEmpty(unseen, "models the check never saw: rerun python Tools/balance/fix_validate.py 7\n" + string.Join("\n", unseen));
            var failures = ((List<object>)models["failures"]).Select(o => (string)o).ToList();
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        // ------------------------------------------------------------------------------------------------ 8: audio

        [Test]
        public void Item8_NoKengOutsideTheArmourHitGroup_AndTheSizeTableRises()
        {
            var metrics = Json(Root("Docs", "audio", "metrics.json"));
            var clips = (Dictionary<string, object>)metrics["clips"];
            // The numbers are current: the same clips as the files in the build (Music aside).
            var audio = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Audio");
            var files = Directory.GetFiles(audio, "*.ogg", SearchOption.AllDirectories)
                .Select(p => p.Substring(audio.Length + 1).Replace('\\', '/')).Where(p => !p.StartsWith("Music/")).OrderBy(p => p, StringComparer.Ordinal).ToList();
            var analysed = clips.Keys.OrderBy(p => p, StringComparer.Ordinal).ToList();
            CollectionAssert.AreEqual(files, analysed, "Docs/audio/metrics.json is out of date: rerun python Tools/sfx/analyze_sfx.py");
            Assert.IsEmpty((List<object>)metrics["keng_outside_armour"], "a clip outside the armour-hit group rings like a bell");
            // The per-size table rises (louder, deeper, longer), for the shots and for the blasts: recomputed here from the rows.
            var rows = ((List<object>)metrics["sizes"]).Cast<Dictionary<string, object>>().ToList();
            var bad = new List<string>();
            foreach (var role in new[] { "shot", "blast" })
            {
                Dictionary<string, object> prev = null;
                string prevSize = null;
                foreach (var row in rows)
                {
                    if (!row.TryGetValue(role, out var cur)) continue;
                    var now = (Dictionary<string, object>)cur;
                    if (prev != null)
                        foreach (var key in new[] { "lufs_mmax", "sub150", "tail" })
                            if (Num(now[key]) <= Num(prev[key])) bad.Add($"{role} {key}: {prevSize} {Num(prev[key])} -> {row["size"]} {Num(now[key])}");
                    prev = now;
                    prevSize = (string)row["size"];
                }
            }
            Assert.IsEmpty(bad, "the per-size audio table does not rise:\n" + string.Join("\n", bad));
            Assert.IsEmpty((List<object>)metrics["not_rising"]);
        }
    }
}
