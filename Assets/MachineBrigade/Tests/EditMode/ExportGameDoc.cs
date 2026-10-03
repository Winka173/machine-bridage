using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using AudioCode = MachineBrigade.Game.Audio;
using FxCode = MachineBrigade.Game.Effects;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Writes the game's own numbers (vehicles and their weapons with damage per second against each
    /// armour, fire support, towers, bosses, equipment, rank and crate economy, modes, campaign) to
    /// one JSON file for the design document (Tools/docs/build_doc.py). Runs only with the
    /// environment variable MB_EXPORT set to the output path.
    /// </summary>
    public partial class ExportGameDoc
    {
        [Test, Category("Export")]
        public void ExportTheGameForTheDesignDocument()
        {
            var path = Environment.GetEnvironmentVariable("MB_EXPORT");
            if (string.IsNullOrEmpty(path)) Assert.Ignore("design document export: set MB_EXPORT to the output path");
            var wasVietnamese = Strings.Vietnamese;
            Strings.Vietnamese = Environment.GetEnvironmentVariable("MB_EXPORT_LANG") != "en";
            try
            {
                var catalog = GameContent.LoadCatalog();
                var doc = new Dictionary<string, object>
                {
                    ["language"] = Strings.Vietnamese ? "vi" : "en",
                    ["damageTable"] = DamageTable(catalog),
                    ["vehicles"] = catalog.Vehicles.Values.Where(v => !v.Static && !v.Boss && !v.Elite && v.Card).OrderBy(v => v.CpCost).ThenBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    // Vehicles that are no card (the Gunship item's AC-130): with the items, not the deck.
                    ["itemVehicles"] = catalog.Vehicles.Values.Where(v => !v.Static && !v.Boss && !v.Elite && !v.Card).OrderBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    ["elites"] = catalog.Vehicles.Values.Where(v => v.Elite).OrderBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    ["bosses"] = catalog.Vehicles.Values.Where(v => v.Boss).OrderBy(v => v.MaxHp).Select(v => Vehicle(catalog, v)).ToList(),
                    ["towers"] = catalog.Vehicles.Values.Where(v => v.Static).OrderBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    ["supports"] = catalog.Supports.Values.OrderBy(s => s.CpCost).Select(s => Support(catalog, s)).ToList(),
                    ["gear"] = Gear(),
                    ["economy"] = Economy(),
                    ["modes"] = Modes(),
                    // Map props (buildings, walls, gates, obstacles) with their plain fields.
                    ["props"] = catalog.Props.Values.OrderBy(p => p.Id).Select(p => (object)new Dictionary<string, object>
                    {
                        ["id"] = p.Id, ["name"] = Text("prop." + p.Id), ["raw"] = Raw(p),
                    }).ToList(),
                    // Every model's measured size in metres (x across, y up, z along), before a def's own scale.
                    ["modelSizes"] = ModelSizes(catalog),
                    // Boss Rush's kinds in order (each draws one variant), for the modes table.
                    ["bossRushKinds"] = MachineBrigade.Sim.Modes.BossRushRules.Kinds.Select(k => (object)k.ToList()).ToList(),
                    ["campaign"] = Campaign.All.Select(Mission).ToList(),
                    ["maps"] = MatchSettings.AllMaps.Select(m => (object)new Dictionary<string, object>
                    {
                        ["id"] = m.Id, ["name"] = Strings.Get("map." + m.Id), ["sub"] = Text("map." + m.Id + ".sub"), ["theme"] = m.Theme,
                    }).ToList(),
                    ["chapters"] = Campaign.Chapters.Select(c => (object)new Dictionary<string, object>
                    {
                        ["number"] = c.Number, ["act"] = c.Act, ["title"] = Text("chapter." + c.Number + ".title"), ["summary"] = Text("chapter." + c.Number + ".summary"),
                        ["maps"] = c.Maps.Select(id => Strings.Get("map." + id)).ToList(), ["general"] = c.General ?? "",
                        ["missions"] = Campaign.All.Count(m => m.Chapter == c.Number),
                    }).ToList(),
                    ["characters"] = new[] { "khai", "mai", "dieuhau", "linh", "hung", "varga", "orlov", "kessler", "sen", "quaden", "aurel" }
                        .Select(id => (object)new Dictionary<string, object>
                        {
                            ["id"] = id, ["name"] = Text("char." + id + ".name"), ["role"] = Text("char." + id + ".role"), ["bio"] = Text("char." + id + ".bio"),
                        }).ToList(),
                    ["timeline"] = Enumerable.Range(0, 20).Select(i => Text("timeline." + i)).Where(s => s.Length > 0).Cast<object>().ToList(),
                    // Prompt 22 F: the player's commanders and the generals' passives, as the game words them.
                    ["commanders"] = Commanders.All.Concat(Commanders.Generals).Select(c => (object)new Dictionary<string, object>
                    {
                        ["id"] = c.Id, ["name"] = CommanderText.Name(c), ["call"] = Text("cmdr." + c.Id + ".call"), ["role"] = CommanderText.Role(c),
                        ["style"] = CommanderText.Style(c), ["strength"] = CommanderText.Strength(c), ["weakness"] = CommanderText.Weakness(c),
                        ["unlock"] = c.IsGeneral ? "" : CommanderText.Unlock(c), ["family"] = c.Family.ToString(), ["general"] = c.General ?? "",
                    }).ToList(),
                    // Every boss's general by id, with the name the story gives them.
                    ["bossGenerals"] = catalog.Vehicles.Values.Where(v => v.Boss && !string.IsNullOrEmpty(v.General)).Select(v => v.General!).Distinct()
                        .ToDictionary(g => g, g => (object)(Text("char." + g + ".name") is { Length: > 0 } n ? n : Text("name." + g))),
                    ["generals"] = Campaign.Generals.Select(g => (object)new Dictionary<string, object>
                    {
                        ["id"] = g.Id, ["name"] = Text("char." + g.Id + ".name"), ["style"] = g.Style, ["stance"] = g.Stance,
                        ["deck"] = g.Deck.Select(Strings.Card).ToList(), ["supports"] = g.Supports.Select(Strings.Support).ToList(),
                        ["elitesPrefer"] = catalog.Generals.TryGetValue(g.Id, out var rules) ? rules.ElitePrefer.ToList() : new List<string>(),
                    }).ToList(),
                    ["base"] = BaseData(catalog),
                    ["operations"] = OperationsData(),
                    // Prompt 26 E (DECISIONS 26E): the Boss Hunt's rules, tiers and combat supports.
                    ["hunt"] = HuntData(),
                    // Full fix L10 (lane C, DECISIONS "Sửa lỗi tổng hợp L9.7/L10 (lane C)"): the warning and munition rules, the
                    // effects by tier and the audio mix, as the code holds them (the design document's sections 10 and C / D).
                    ["fixDoc"] = FixDoc(catalog),
                    // Balance pack (lane B, §3; ExportGameDoc.Pack.cs): the NEED_CODE_CHECK cells' values from the game's code.
                    ["balancePack"] = BalancePack(catalog),
                };
                File.WriteAllText(path, Json(doc), new UTF8Encoding(false));
            }
            finally
            {
                Strings.Vietnamese = wasVietnamese;
            }
        }

        /// <summary>Prompt 26 E: the Boss Hunt's rule texts (as the game words them), the week's and the full hunt's counts, the supports and the tiers.</summary>
        private static object HuntData()
        {
            var week = MachineBrigade.Game.Match.BossHunts.ThisWeek;
            var full = MachineBrigade.Game.Match.BossHunts.Full;
            var mains = MachineBrigade.Game.Match.BossHunts.MainsIn(week);
            var rush = new MachineBrigade.Sim.Modes.BossRushRules();
            return new Dictionary<string, object>
            {
                ["weeklyRules"] = Strings.Format("hunt.weekly.rules", ("count", week.Count), ("minis", week.Count - mains), ("mains", mains),
                    ("minutes", (int)Math.Round(BossHunts.WeeklyMinutes))),
                ["fullRules"] = Strings.Format("hunt.full.rules", full.Count),
                ["weekly"] = week.Count, ["weeklyMains"] = mains, ["full"] = full.Count, ["fullMains"] = MachineBrigade.Game.Match.BossHunts.MainsIn(full),
                ["miniSeconds"] = rush.MiniSeconds, ["mainSeconds"] = rush.MainSeconds, ["cap"] = MachineBrigade.Sim.Modes.HuntSupports.Cap,
                ["weeklyStep"] = MachineBrigade.Sim.Modes.BossHunt.WeeklyStep, ["fullFrom"] = MachineBrigade.Sim.Modes.BossHunt.FullFrom,
                ["fullTo"] = MachineBrigade.Sim.Modes.BossHunt.FullTo,
                ["supports"] = MachineBrigade.Sim.Modes.HuntSupports.All.Select(x => (object)new Dictionary<string, object>
                {
                    ["id"] = x.Id, ["name"] = Text("hunt.support." + x.Id), ["info"] = Text("hunt.support." + x.Id + ".info"), ["strength"] = x.Strength,
                }).ToList(),
            };
        }

        /// <summary>
        /// Full fix L10 (lane C, DECISIONS "Sửa lỗi tổng hợp L9.7/L10 (lane C)"): what the design document's sections 10e-10h, C and D
        /// read from the code rather than from balance.json: the warning rules (data warningRules, with the defaults), the munition
        /// rules (munitionRules, the flare release), the effects by tier T0-T5 (TierFx's firing look, EffectLife's lifetimes, the
        /// camera shake, the full-detail caps and the distance detail) and the audio mix (groups, voices, priorities, compressor,
        /// limiter, falloff, the metal cap). Read only; nothing here changes a value.
        /// </summary>
        private static object FixDoc(Catalog catalog)
        {
            var tiers = new List<object>();
            for (var t = 0; t <= FxCode.TierFx.Top; t++)
            {
                var fire = FxCode.TierFx.FireOf(t);
                var life = FxCode.EffectLife.Of(t);
                var cap = FxCode.TierFx.FullCap(t);
                tiers.Add(new Dictionary<string, object>
                {
                    ["tier"] = t,
                    ["flash"] = fire.Flash, ["flashLife"] = fire.FlashLife, ["puffs"] = fire.Puffs, ["puffSize"] = fire.PuffSize,
                    ["puffLifeMin"] = fire.PuffLife.x, ["puffLifeMax"] = fire.PuffLife.y, ["pressure"] = fire.Pressure,
                    ["dustRing"] = fire.DustRing, ["water"] = fire.Water, ["light"] = fire.Light, ["squat"] = fire.Squat,
                    ["fireballLife"] = life.Fireball, ["smokeMin"] = life.SmokeMin, ["smokeMax"] = life.SmokeMax, ["crater"] = life.Crater,
                    ["shake"] = FxCode.TierFx.ShakeAt(t), ["shotShake"] = FxCode.TierFx.ShakeAt(t) * FxCode.TierFx.ShotShare,
                    ["fullCap"] = cap == int.MaxValue ? -1 : cap, ["busy"] = FxCode.TierFx.Busy(t), ["weight"] = FxCode.TierFx.Weight(t),
                    ["nominalCore"] = FxCode.TierFx.NominalCore(t), ["extra"] = FxCode.TierFx.Extra(t),
                });
            }
            var effects = new Dictionary<string, object>
            {
                ["tiers"] = tiers,
                ["shakeFalloff"] = FxCode.TierFx.ShakeFalloff, ["shakeReach"] = FxCode.TierFx.ShakeReach, ["shakeCap"] = FxCode.TierFx.ShakeCap,
                ["shotShare"] = FxCode.TierFx.ShotShare, ["nearView"] = FxCode.TierFx.NearView, ["midView"] = FxCode.TierFx.MidView,
                ["reducedShare"] = FxCode.TierFx.ReducedShare, ["weightCap"] = FxCode.TierFx.WeightCap,
            };
            var m = catalog.Munitions;
            var munitions = Raw(m);
            munitions["flaresFighter"] = new List<object> { m.FlaresFighter.min, m.FlaresFighter.max };
            munitions["flaresHelicopter"] = new List<object> { m.FlaresHelicopter.min, m.FlaresHelicopter.max };
            munitions["flaresLarge"] = new List<object> { m.FlaresLarge.min, m.FlaresLarge.max };
            munitions["flareBurn"] = new List<object> { m.FlareBurn.min, m.FlareBurn.max };
            munitions["radarGuided"] = m.RadarGuided.OrderBy(x => x, StringComparer.Ordinal).Cast<object>().ToList();
            munitions["sightGuided"] = m.SightGuided.OrderBy(x => x, StringComparer.Ordinal).Cast<object>().ToList();
            var sizes = new List<object>();
            foreach (AudioCode.SizeClass size in Enum.GetValues(typeof(AudioCode.SizeClass)))
                sizes.Add(new Dictionary<string, object> { ["size"] = size.ToString(), ["carry"] = AudioCode.SoundLibrary.Carry(size) });
            var audio = new Dictionary<string, object>
            {
                ["groups"] = Enum.GetNames(typeof(AudioCode.AudioGroup)).Cast<object>().ToList(),
                ["effectVoices"] = AudioCode.AudioDirector.EffectVoices, ["offScreenGain"] = AudioCode.AudioDirector.OffScreenGain,
                ["clusterRadius"] = AudioCode.AudioDirector.ClusterRadius, ["clusterWindow"] = AudioCode.AudioDirector.ClusterWindow,
                ["clusterFrom"] = AudioCode.AudioDirector.ClusterFrom, ["nearShare"] = AudioCode.AudioDirector.NearShare,
                ["compressorAttack"] = AudioCode.AudioDirector.CompressorAttack, ["compressorRelease"] = AudioCode.AudioDirector.CompressorRelease,
                ["compressorThreshold"] = AudioCode.SoundLibrary.CompressorThreshold, ["compressorRatio"] = AudioCode.SoundLibrary.CompressorRatio,
                ["limiterCeiling"] = AudioCode.SoundLibrary.LimiterCeiling, ["refDistance"] = AudioCode.SoundLibrary.RefDistance,
                ["heightShare"] = AudioCode.SoundLibrary.HeightShare,
                ["metalPerSecond"] = AudioCode.MetalCap.PerSecond, ["metalBurst"] = AudioCode.MetalCap.Burst, ["metalMinGap"] = AudioCode.MetalCap.MinGap,
                ["priorities"] = new Dictionary<string, object>
                {
                    ["Warning"] = AudioCode.SoundPriority.Warning, ["Boss"] = AudioCode.SoundPriority.Boss,
                    ["NearBlast"] = AudioCode.SoundPriority.NearBlast, ["NearShot"] = AudioCode.SoundPriority.NearShot,
                    ["FarBlast"] = AudioCode.SoundPriority.FarBlast, ["FarShot"] = AudioCode.SoundPriority.FarShot,
                    ["SmallArms"] = AudioCode.SoundPriority.SmallArms, ["Ambient"] = AudioCode.SoundPriority.Ambient,
                },
                ["sizes"] = sizes,
            };
            return new Dictionary<string, object>
            {
                ["warningRules"] = Raw(catalog.Warnings), ["munitionRules"] = munitions, ["effects"] = effects, ["audio"] = audio,
            };
        }

        private static string Text(string key) => Strings.Has(key) ? Strings.Get(key) : "";

        /// <summary>
        /// Prompt 15: the damage-type table (a row per type: ground, air, structure), the penetration row (a level
        /// or more above the armour, level, one, two and three under) and the thermobaric tag's structure multiplier.
        /// </summary>
        private static object DamageTable(Catalog catalog)
        {
            var table = new Dictionary<string, object>();
            foreach (DamageType d in Enum.GetValues(typeof(DamageType)))
            {
                var row = new Dictionary<string, object>();
                foreach (TargetKind k in Enum.GetValues(typeof(TargetKind))) row[k.ToString()] = catalog.Damage.Type(d, k);
                row["name"] = Text("ul.type." + d);
                table[d.ToString()] = row;
            }
            table["penetration"] = Enumerable.Range(0, MachineBrigade.Sim.Content.DamageTable.PenetrationSteps).Select(i => (object)catalog.Damage.PenetrationStep(i)).ToList();
            table["thermobaric"] = catalog.Damage.ThermobaricStructure;
            return table;
        }

        /// <summary>A mode's subtitle as the menus show it: Boss Rush's has the number of bosses filled in.</summary>
        private static string ModeSub(GameModeKind kind, string key) =>
            kind == GameModeKind.BossRush ? Strings.Format(key + "Sub", BossHunts.ThisWeek.Count) : Text(key + "Sub");

        [Test]
        public void EveryUnitHasArmourLevelsAndEveryWeaponAPenetrationAndAForm()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var v in catalog.Vehicles.Values)
            {
                foreach (var level in new[] { v.Armour.Front, v.Armour.Side, v.Armour.Rear, v.Armour.Top })
                    Assert.That(level, Is.InRange(0, v.Boss ? ArmourLevels.Max : ArmourLevels.MaxUnit), v.Id + ": an armour level 0-4 on every face (a boss's to 5)");
                foreach (var p in v.Parts)
                    Assert.That(p.ArmourOn(v), Is.InRange(0, ArmourLevels.Max), v.Id + " " + p.Id + ": the part's armour level");
                foreach (var m in v.Mounts)
                {
                    if (m.Weapon.Damage <= 0f) continue;
                    Assert.That(m.Weapon.Penetration, Is.InRange(0, 4), m.Weapon.Id + ": a penetration 0-4");
                    Assert.AreNotEqual(WeaponForm.None, m.Weapon.Form, m.Weapon.Id + " on " + v.Id + ": a weapon form");
                }
            }
        }

        [Test]
        public void NoModeLineKeepsAPlaceholder()
        {
            foreach (var vietnamese in new[] { true, false })
            {
                var was = Strings.Vietnamese;
                Strings.Vietnamese = vietnamese;
                try
                {
                    foreach (Dictionary<string, object> m in (IEnumerable)Modes())
                        foreach (var field in new[] { "name", "sub" })
                            StringAssert.DoesNotContain("{", (string)m[field], m["id"] + " " + field + (vietnamese ? " (vi)" : " (en)"));
                }
                finally
                {
                    Strings.Vietnamese = was;
                }
            }
        }

        /// <summary>The bounds of every model a vehicle, tower, boss, prop or round uses, measured from its prefab.</summary>
        private static Dictionary<string, object> ModelSizes(Catalog catalog)
        {
            var ids = new HashSet<string>();
            foreach (var v in catalog.Vehicles.Values)
            {
                if (!string.IsNullOrEmpty(v.Model)) ids.Add(v.Model);
                foreach (var m in v.Mounts)
                {
                    if (!string.IsNullOrEmpty(m.ProjectileModel)) ids.Add(m.ProjectileModel);
                    if (!string.IsNullOrEmpty(m.Weapon.ProjectileModel)) ids.Add(m.Weapon.ProjectileModel);
                }
            }
            foreach (var p in catalog.Props.Values) ids.Add(p.Id);
            foreach (var p in catalog.Props.Values)
                foreach (var prop in p.GetType().GetProperties())
                    if (prop.Name == "Model" && prop.GetValue(p) is string model && model.Length > 0) ids.Add(model);
            var sizes = new Dictionary<string, object>();
            foreach (var id in ids.OrderBy(i => i))
            {
                var prefab = UnityEngine.Resources.Load<UnityEngine.GameObject>("Models/" + id);
                if (prefab == null) continue;
                var go = UnityEngine.Object.Instantiate(prefab);
                try
                {
                    var renderers = go.GetComponentsInChildren<UnityEngine.Renderer>(true);
                    if (renderers.Length == 0) continue;
                    var b = renderers[0].bounds;
                    foreach (var r in renderers) b.Encapsulate(r.bounds);
                    sizes[id] = new List<object> { b.size.x, b.size.y, b.size.z };
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(go);
                }
            }
            return sizes;
        }

        /// <summary>A definition's public numbers, flags, enums and strings, by property name, for the document.</summary>
        private static Dictionary<string, object> Raw(object o)
        {
            var d = new Dictionary<string, object>();
            foreach (var p in o.GetType().GetProperties(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance))
            {
                if (p.GetIndexParameters().Length > 0) continue;
                var t = Nullable.GetUnderlyingType(p.PropertyType) ?? p.PropertyType;
                if (!(t.IsPrimitive || t.IsEnum || t == typeof(string))) continue;
                try
                {
                    var value = p.GetValue(o);
                    if (value == null) continue;
                    d[p.Name] = t.IsEnum ? value.ToString() : value;
                }
                catch (Exception)
                {
                    // A property that throws for this def (not set) is left out.
                }
            }
            return d;
        }

        /// <summary>A unit's armour by face (prompt 15 A).</summary>
        private static object Armour(ArmourLevels a) => new Dictionary<string, object>
        {
            ["front"] = a.Front, ["side"] = a.Side, ["rear"] = a.Rear, ["top"] = a.Top,
        };

        private static object Vehicle(Catalog catalog, VehicleDef v)
        {
            var weapons = new List<object>();
            var dps = new Dictionary<string, float>();
            foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass))) dps[a.ToString()] = 0f;
            foreach (var m in v.Mounts)
            {
                var w = m.Weapon;
                if (w.Damage <= 0f) continue;
                // Prompt 13 A.1: over a whole load (salvos, magazines and their change, a launcher's reload).
                var raw = MachineBrigade.Sim.Combat.FirePower.Sustained(w, v);
                // Full fix L10 item 9: "Main gun" only on the first mount (a secondary without a real name reads "Gun").
                var mainMount = ReferenceEquals(m, v.Mounts[0]);
                var weaponName = string.IsNullOrEmpty(w.RealName) ? WeaponInfo.Describe(w, mainMount).Name : UnitLines.WeaponName(w);
                weapons.Add(new Dictionary<string, object>
                {
                    ["id"] = w.Id, ["name"] = weaponName, ["slot"] = m.Slot, ["type"] = w.DamageType.ToString(), ["damage"] = w.Damage, ["burst"] = w.Burst,
                    // Full fix L10 (lane C): the mount (first or not, how it aims, its own arc in degrees), the warning and the
                    // sound the round plays, for the design document's full weapon table (section A) and its audio section.
                    ["mainMount"] = mainMount, ["aim"] = m.Aim.ToString(),
                    ["arcCentreDeg"] = m.ArcCentre * 180f / MathF.PI, ["arcHalfDeg"] = m.ArcHalf * 180f / MathF.PI,
                    ["tier"] = w.Tier, ["variantId"] = w.WeaponVariantId ?? "", ["warns"] = catalog.Warnings.Warns(w),
                    ["warnSeconds"] = w.WarnSeconds, ["warnRadius"] = w.WarnRadius, ["burstInterval"] = w.BurstInterval,
                    ["roundsPerPull"] = w.RoundsPerPull, ["barrelGap"] = WeaponDef.BarrelGap,
                    ["soundSize"] = MachineBrigade.Game.Audio.SoundLibrary.SizeOf(w).ToString(),
                    ["shotBank"] = MachineBrigade.Game.Audio.SoundLibrary.ShotBank(w) ?? "",
                    ["blastBank"] = MachineBrigade.Game.Audio.SoundLibrary.BlastBank(w) ?? "",
                    ["cooldown"] = w.Cooldown, ["range"] = w.Range, ["minRange"] = w.MinRange, ["splash"] = w.SplashRadius,
                    ["targets"] = w.Targets.ToString(), ["dps"] = raw, ["projectile"] = w.Projectile.ToString(),
                    ["clip"] = w.Clip, ["clipReload"] = w.ClipReload, ["speed"] = w.ProjectileSpeed,
                    // Prompt 15: penetration, the round's form, its tags, and its effect on each armour level, aircraft and structures.
                    ["pen"] = w.Penetration, ["form"] = w.Form.ToString(), ["topAttack"] = Armour_StrikesTop(w), ["guided"] = w.Guided,
                    ["splashes"] = w.Splashes, ["thermobaric"] = w.Thermobaric, ["real"] = w.RealName ?? "",
                    // Full fix L2 / L3: the display calibre, warhead, power, energy; the barrels, the full cycle, its rounds, the family.
                    ["caliberMm"] = w.CaliberMm, ["warheadKg"] = w.WarheadKg, ["powerKw"] = w.PowerKw, ["energyMj"] = w.EnergyMj,
                    ["barrels"] = w.Barrels, ["simultaneous"] = w.Simultaneous, ["cycle"] = w.CycleSeconds, ["roundsPerCycle"] = w.RoundsPerCycle,
                    ["familyId"] = w.WeaponFamilyId ?? "",
                    ["effect"] = Matchup.EffectRow(catalog.Damage, w).Select(x => (object)x).ToList(),
                    // Prompt 25 F1 (DECISIONS 25E): the DPS against aircraft (a boss's weaponDamage is the ground's only), the
                    // DPS by armour level 0-5, on aircraft and on structures, the flight to the longest reach, the round's length.
                    ["dpsAir"] = MachineBrigade.Sim.Combat.FirePower.SustainedAir(w, v),
                    ["dpsVsLevel"] = DpsByLevel(catalog, w, v, raw),
                    ["flightTime"] = w.ProjectileSpeed > 0f ? w.Range / w.ProjectileSpeed : 0f, ["roundLength"] = w.RoundLength,
                    // Every plain number, flag and name the weapon carries (rates, magazines, reloads, ceilings...).
                    ["raw"] = Raw(w),
                    // Prompt 25 G (DECISIONS 25G): the second rounds this gun loads, and (prompt 26 B.3) a boss blast's core and edge.
                    ["roundOf"] = w.RoundOf?.Id ?? "", ["roundKind"] = w.RoundKind ?? "", ["switchSeconds"] = w.SwitchSeconds(null),
                    ["secondRounds"] = w.Rounds.Select(r => (object)new Dictionary<string, object>
                    {
                        ["id"] = r.Round.Id, ["name"] = UnitLines.WeaponName(r.Round), ["kind"] = UnitLines.RoundWord(r.Round), ["type"] = r.Round.DamageType.ToString(),
                        ["pen"] = r.Round.Penetration, ["damage"] = r.Round.Damage, ["splash"] = r.Round.SplashRadius, ["use"] = UnitLines.UseWords(r),
                        ["elite"] = r.EliteOnly, ["switch"] = w.SwitchSeconds(r), ["speed"] = r.Round.ProjectileSpeed,
                    }).ToList(),
                    ["splashEdge"] = w.SplashEdge, ["edgeShare"] = w.EdgeShare,
                    ["bonuses"] = w.Bonuses.Select(b => (object)new Dictionary<string, object>
                    {
                        ["mult"] = b.Mult, ["class"] = b.Class?.ToString() ?? "", ["armor"] = b.Armor?.ToString() ?? "", ["still"] = b.StillFor, ["flank"] = b.Flank,
                    }).ToList(),
                });
                foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass)))
                {
                    var air = a == ArmorClass.Air;
                    if (!w.CanTarget(air)) continue;
                    // A bonus on an armour class alone counts in (a bunker-buster on structures); ones that
                    // depend on the target's class, standing still or a flank are listed with the weapon.
                    var bonus = 1f;
                    foreach (var b in w.Bonuses)
                        if (b.Armor == a && b.Class == null && b.StillFor <= 0f && !b.Flank) bonus *= b.Mult;
                    // Prompt 25 C1: a boss's own weapon damage is the ground's only.
                    var paper = air ? MachineBrigade.Sim.Combat.FirePower.SustainedAir(w, v) : raw;
                    dps[a.ToString()] += paper * Matchup.ClassEffect(catalog.Damage, w, a) * bonus;
                }
            }
            return new Dictionary<string, object>
            {
                ["id"] = v.Id, ["name"] = Strings.Card(v.Id), ["short"] = Strings.Short(v.Id), ["note"] = Text("note." + v.Id), ["guide"] = Text("guide." + v.Id),
                ["rounds"] = v.Mounts.Select(m => m.ProjectileModel ?? m.Weapon.ProjectileModel ?? "").ToList(),
                ["class"] = v.Class.ToString(), ["armor"] = v.Armor.ToString(), ["hp"] = v.MaxHp, ["speed"] = v.Speed, ["cost"] = v.CpCost,
                // Play-test 8: how a card is had (starter, premium, campaign) and its price in coins.
                ["route"] = Progression.Route(v.Id).ToString(), ["coins"] = v.Boss || v.Elite ? 0 : Progression.Price(v.Id, catalog),
                // Prompt 15: armour by face, the kind of target, and the strong / weak summary.
                ["armour"] = Armour(v.Armour), ["kind"] = v.Kind.ToString(),
                ["strongVs"] = Matchup.Summary(catalog.Damage, v).StrongVs.Select(c => (object)c.ToString()).ToList(),
                ["weakTo"] = Matchup.Summary(catalog.Damage, v).WeakTo.Select(t => (object)t.ToString()).ToList(),
                ["vision"] = v.VisionRange, ["flying"] = v.Flying, ["model"] = v.Model, ["weapons"] = weapons, ["dpsVs"] = dps,
                ["raw"] = Raw(v),
                ["skills"] = v.Skills.Select(s => s.Id).ToList(), ["death"] = v.DeathExplosion?.Damage ?? 0f,
                ["deathRadius"] = v.DeathExplosion?.Radius ?? 0f,
                // Prompt 13 G: the generated lines, as the detail screen shows them.
                ["behavior"] = UnitLines.Behaviour(catalog, v), ["ammo"] = UnitLines.Ammo(catalog, v),
                ["phases"] = v.Phases.Select(p => (object)p.At).ToList(),
                ["phaseData"] = v.Phases.Select(p => (object)new Dictionary<string, object>
                {
                    ["at"] = p.At, ["heal"] = p.Heal, ["damage"] = p.Damage, ["speed"] = p.Speed, ["armor"] = p.Armor, ["fireRate"] = p.FireRate,
                }).ToList(),
                ["general"] = v.General ?? "",
                ["parts"] = v.Parts.Select(p => (object)new Dictionary<string, object>
                {
                    ["id"] = p.Id, ["kind"] = p.Kind, ["name"] = Text("part." + p.Kind), ["hp"] = p.Hp, ["breakDamage"] = p.BreakDamage,
                    ["armour"] = p.ArmourOn(v),
                    ["effects"] = MenuScreen.PartEffects(v, p), ["radio"] = p.Radio != null,
                }).ToList(),
                ["partLock"] = v.PartLock != null ? Text("part." + v.PartLock.Kind) + " ×" + v.PartLock.Count : "",
                ["partPatch"] = v.Skills.Any(k => k.Kind == SkillKind.Patch), ["partTip"] = Text("guide.parts.tip." + v.Id),
                ["size"] = v.Fort?.Size.ToString() ?? "", ["bossFile"] = Text("bossfile." + v.Id),
                // Prompt 25 F1 (DECISIONS 25E): the description (the Guide card's how and strong / weak lines), the unlock,
                // the model's size from the data (modelSize) and a main boss's super weapon.
                ["description"] = Description(Text("guide." + v.Id)), ["unlock"] = Unlock(catalog, v),
                ["modelSize"] = v.ModelLength > 0f ? new List<object> { v.ModelLength, v.ModelWidth, v.ModelHeight } : new List<object>(),
                ["superWeapon"] = SuperWeapon(v),
            };
        }

        /// <summary>A weapon's sustained DPS against armour levels 0-5, aircraft and structures (its effect row; an armour-class bonus counts in).</summary>
        private static List<object> DpsByLevel(Catalog catalog, WeaponDef w, VehicleDef v, float sustained)
        {
            var row = Matchup.EffectRow(catalog.Damage, w);
            var air = MachineBrigade.Sim.Combat.FirePower.SustainedAir(w, v);
            var list = new List<object>();
            for (var c = 0; c < row.Length; c++)
            {
                var armor = c == row.Length - 2 ? ArmorClass.Air : c == row.Length - 1 ? ArmorClass.Structure : c >= 3 ? ArmorClass.Heavy : ArmorClass.Light;
                var bonus = 1f;
                foreach (var b in w.Bonuses)
                    if (b.Armor == armor && b.Class == null && b.StillFor <= 0f && !b.Flank) bonus *= b.Mult;
                list.Add((armor == ArmorClass.Air ? air : sustained) * row[c] * bonus);
            }
            return list;
        }

        /// <summary>A Guide card's how-it-fights and strong / weak lines, without their labels and highlights.</summary>
        private static string Description(string guide)
        {
            var lines = guide.Split('\n').Skip(1).Select(l => l.Replace("[[", "").Replace("]]", "").Trim()).Where(l => l.Length > 0).Take(2)
                .Select(l => l.IndexOf(": ", StringComparison.Ordinal) is var i and > 0 and < 16 ? l.Substring(i + 2) : l);
            return string.Join(" ", lines);
        }

        /// <summary>How a card is had (prompt 25 D2): its route, the mission that opens it, its early price, story loot.</summary>
        private static object Unlock(Catalog catalog, VehicleDef v)
        {
            if (v.Boss || v.Elite) return new Dictionary<string, object>();
            var m = Progression.UnlockMission(v.Id);
            return new Dictionary<string, object>
            {
                ["route"] = Progression.Route(v.Id).ToString(), ["mission"] = m?.Id ?? "", ["missionName"] = m != null ? Text("mission." + m.Id + ".name") : "",
                ["chapter"] = m?.Chapter ?? 0, ["index"] = m != null ? Campaign.IndexOf(m.Id) + 1 : 0,
                ["storyLoot"] = Progression.IsStoryLoot(v.Id), ["earlyBuy"] = Progression.CanBuyEarly(v.Id), ["price"] = Progression.Price(v.Id, catalog),
            };
        }

        /// <summary>A main boss's super weapon (prompt 25 C1) with the Guide's words; empty for every other unit.</summary>
        private static object SuperWeapon(VehicleDef v)
        {
            var a = v.BigAttack;
            if (!v.Boss || a == null) return new Dictionary<string, object>();
            return new Dictionary<string, object>
            {
                ["id"] = a.Id, ["name"] = Text(a.NameKey), ["how"] = Text(a.GuideKey("how")), ["dodge"] = Text(a.GuideKey("dodge")),
                ["stop"] = Text(a.GuideKey("stop")), ["warn"] = a.Warn, ["cooldown"] = a.Cooldown,
                ["strikes"] = a.Strikes.Select(s => (object)new Dictionary<string, object>
                {
                    ["shape"] = s.Shape.ToString(), ["count"] = s.Count, ["damage"] = s.Damage, ["type"] = s.Type.ToString(), ["pen"] = s.Pen,
                    ["radius"] = s.Radius, ["length"] = s.Length, ["width"] = s.Width,
                }).ToList(),
            };
        }

        private static object Support(Catalog catalog, SupportDef s) => new Dictionary<string, object>
        {
            ["id"] = s.Id, ["name"] = Strings.Support(s.Id), ["info"] = Text("support." + s.Id + ".info"), ["kind"] = s.Kind.ToString(), ["guide"] = Text("guide." + s.Id),
            ["cost"] = s.CpCost, ["consumable"] = s.Consumable, ["eventOnly"] = s.EventOnly, ["route"] = Progression.Route(s.Id).ToString(),
            ["coins"] = Progression.IsItem(s.Id) ? Progression.ItemPrice(s.Id) : Progression.Price(s.Id, catalog),
            ["cooldown"] = s.Cooldown, ["damage"] = s.Damage, ["radius"] = s.Radius, ["count"] = s.Count,
            ["duration"] = s.Duration, ["type"] = s.DamageType.ToString(), ["pen"] = s.Penetration, ["thermobaric"] = s.Thermobaric,
        };

        /// <summary>Its rounds strike the roof (a top attack, or anything lobbed or dropped).</summary>
        private static bool Armour_StrikesTop(WeaponDef w) => MachineBrigade.Sim.Content.Armour.StrikesTop(w);

        private static object Gear()
        {
            var bases = GearCatalog.Bases.Select(b => (object)new Dictionary<string, object>
            {
                ["id"] = b.Id, ["name"] = Text("gear.base." + b.Id), ["slot"] = b.Slot.ToString(), ["implicit"] = b.Implicit.ToString(),
                ["implicitName"] = b.Implicit == StatId.Count ? GearText.BaseNote(b) : GearText.Line(b.Implicit, b.Top[b.Top.Length - 1]), ["top"] = b.Top,
                ["lines"] = b.Implicit == StatId.Count ? new List<string>() : b.Top.Select(v => GearText.Line(b.Implicit, v)).ToList(),
                ["penaltyLine"] = b.TradeOff && b.PenaltyTop != null ? GearText.Line(b.Penalty, b.PenaltyTop[b.PenaltyTop.Length - 1], true) : "",
                ["tradeOff"] = b.TradeOff, ["penalty"] = b.TradeOff ? b.Penalty.ToString() : "", ["minRarity"] = b.MinRarity,
            }).ToList();
            var traits = GearCatalog.Traits.Select(t => (object)new Dictionary<string, object>
            {
                ["id"] = t.Id.ToString(), ["key"] = t.Key, ["name"] = Text("trait." + t.Key), ["effect"] = GearText.TraitEffect(t.At(Rarity.Legendary)),
                ["effectEpic"] = GearText.TraitEffect(t.At(Rarity.Epic)), ["effectLegendary"] = GearText.TraitEffect(t.At(Rarity.Legendary)),
                ["slot"] = t.Slot.ToString(), ["epic"] = t.Epic, ["legendary"] = t.Legendary,
            }).ToList();
            var modules = GearCatalog.Modules.Select(m => (object)new Dictionary<string, object>
            {
                ["id"] = m.Module.ToString(), ["key"] = m.Key, ["name"] = Text("special." + m.Key),
                ["effect"] = GearText.ModuleEffect(m.Module, Rarity.Legendary),
                ["effectEpic"] = GearText.ModuleEffect(m.Module, Rarity.Epic), ["effectLegendary"] = GearText.ModuleEffect(m.Module, Rarity.Legendary),
                ["epic"] = m.Epic, ["legendary"] = m.Legendary,
            }).ToList();
            var brands = new List<object>();
            for (var i = 1; i <= GearCatalog.Brands.Length; i++)
            {
                var b = GearCatalog.Brand(i);
                brands.Add(new Dictionary<string, object> { ["index"] = i, ["name"] = GearText.BrandName(b), ["bonuses"] = GearText.BrandBonuses(b) });
            }
            return new Dictionary<string, object>
            {
                ["rarities"] = new[] { "Common", "Uncommon", "Rare", "Epic", "Legendary" }, ["levelCap"] = Game.Match.Gear.LevelCap,
                ["caps"] = Game.Match.Gear.Cap, ["bases"] = bases, ["traits"] = traits, ["modules"] = modules, ["brands"] = brands,
            };
        }

        private static object Economy() => new Dictionary<string, object>
        {
            ["rankCoins"] = Enumerable.Range(1, CardRanks.Max - 1).Select(CardRanks.CoinsToNext).ToList(),
            ["rankPrints"] = Enumerable.Range(1, CardRanks.Max - 1).Select(CardRanks.BlueprintsToNext).ToList(),
            ["rankBonus"] = Enumerable.Range(1, CardRanks.Max).Select(CardRanks.Bonus).ToList(),
            ["rankCut"] = Enumerable.Range(1, CardRanks.Max).Select(CardRanks.CutBasisPoints).ToList(),
            ["callCost"] = new[] { 4, 6, 8, 10, 12, 14, 16, 20, 22 }.Select(c => (object)new Dictionary<string, object>
            {
                ["cost"] = c, ["rank7"] = CardRanks.CallCost(c, 7), ["rank9"] = CardRanks.CallCost(c, 9),
            }).ToList(),
            ["bossKinds"] = MachineBrigade.Sim.Modes.BossRushRules.Kinds.Select(k => (object)k.ToList()).ToList(),
            ["itemPack"] = Progression.ItemPack,
            ["crateCoinPrice"] = Crates.CoinPrice, ["crateRolls"] = Crates.Rolls, ["crateOdds"] = Crates.Odds,
            ["crateCoinsLow"] = Crates.CoinsLow, ["crateCoinsHigh"] = Crates.CoinsHigh,
            ["coinPacks"] = CoinStore.Packs.Select(p => (object)new Dictionary<string, object> { ["id"] = p.id, ["coins"] = p.coins, ["price"] = p.price }).ToList(),
        };

        private static object Modes()
        {
            var list = new List<object>();
            foreach (GameModeKind kind in Enum.GetValues(typeof(GameModeKind)))
            {
                var key = kind switch
                {
                    GameModeKind.KingOfTheHill => "mode.hill", GameModeKind.BossRush => "mode.bossrush", _ => "mode." + kind.ToString().ToLowerInvariant(),
                };
                list.Add(new Dictionary<string, object>
                {
                    ["id"] = kind.ToString(), ["name"] = Text(key), ["sub"] = ModeSub(kind, key), ["toast"] = Text(key + ".toast"),
                });
            }
            return list;
        }

        private static object Mission(MissionDef m) => new Dictionary<string, object>
        {
            ["id"] = m.Id, ["name"] = Text("mission." + m.Id + ".name"), ["brief"] = Text("mission." + m.Id + ".brief"), ["map"] = m.Map,
            ["mapName"] = Strings.Get("map." + m.Map), ["variant"] = m.Variant,
            ["goal"] = m.Goal.ToString(), ["goalName"] = Text("goal." + m.Goal.ToString().ToLowerInvariant()), ["weather"] = m.Weather,
            ["difficulty"] = m.Difficulty, ["coins"] = m.RewardCoins, ["xp"] = m.RewardXp, ["unlocks"] = m.Unlocks.Select(Strings.Card).ToList(),
            ["timeLimit"] = m.TimeLimit, ["boss"] = m.Boss != null ? Strings.Card(m.Boss.Def) : "",
            ["chapter"] = m.Chapter, ["side"] = m.Side, ["general"] = m.General ?? "", ["operation"] = m.Operation, ["replay"] = m.Replay,
            ["hqLevel"] = m.HqLevel, ["legacy"] = m.Legacy ?? "",
            ["stages"] = m.Stages.Select(s => (object)new Dictionary<string, object>
            {
                ["id"] = s.Id, ["goal"] = s.Mission.Goal.ToString(), ["goalName"] = Text("goal." + s.Mission.Goal.ToString().ToLowerInvariant()),
                ["title"] = Text("stage." + m.Id + "." + s.Id), ["cp"] = s.Cp, ["choices"] = s.Choices.Select(c => Text("choice." + m.Id + "." + c.Key)).ToList(),
                ["events"] = s.Events.Select(e => e.Kind.ToString()).Distinct().ToList(),
            }).ToList(),
            ["ally"] = m.Ally != null,
        };

        private static object BaseData(Catalog catalog)
        {
            var rules = catalog.Base;
            var levels = Enumerable.Range(1, 5).Select(l => (object)new Dictionary<string, object>
            {
                ["level"] = l, ["small"] = rules.Slots(l, SlotSize.Small), ["medium"] = rules.Slots(l, SlotSize.Medium),
                ["large"] = rules.Slots(l, SlotSize.Large), ["utility"] = rules.UtilitySlots(l),
            }).ToList();
            var towers = TowerCards.All(catalog).Select(id =>
            {
                var def = catalog.Vehicles[id];
                return (object)new Dictionary<string, object>
                {
                    ["id"] = id, ["name"] = Strings.Card(id), ["size"] = def.Fort?.Size.ToString() ?? "", ["hp"] = def.MaxHp,
                    ["rebuildCp"] = rules.RebuildCost(def), ["rebuildSeconds"] = rules.RebuildCooldown(def), ["guide"] = Text("guide." + id),
                    ["branches"] = TowerCards.Branches(catalog, id).Select(b => (object)new Dictionary<string, object>
                    {
                        ["id"] = b, ["name"] = Text("branch." + b), ["info"] = Text("branch." + b + ".info"),
                    }).ToList(),
                };
            }).ToList();
            var modules = catalog.Vehicles.Values.Where(v => v.Fort is { Kind: FortKind.Utility }).OrderBy(v => v.Id).Select(v => (object)new Dictionary<string, object>
            {
                ["id"] = v.Id, ["name"] = Strings.Card(v.Id), ["guide"] = Text("guide." + v.Id),
            }).ToList();
            return new Dictionary<string, object> { ["levels"] = levels, ["towers"] = towers, ["modules"] = modules };
        }

        private static object OperationsData()
        {
            var data = Operations.Data;
            return new Dictionary<string, object>
            {
                ["tiers"] = data.Tiers.Select((t, i) => (object)new Dictionary<string, object>
                {
                    ["id"] = t.Id, ["name"] = Text("tier." + i), ["enemy"] = t.Enemy, ["playerIncome"] = t.PlayerIncome, ["supports"] = t.Supports, ["score"] = t.Score,
                }).ToList(),
                ["scoring"] = new Dictionary<string, object>
                {
                    ["win"] = data.Scoring.Win, ["time"] = data.Scoring.Time, ["par"] = data.Scoring.Par, ["losses"] = data.Scoring.Losses,
                    ["lossesAtZero"] = data.Scoring.LossesAtZero, ["hq"] = data.Scoring.Hq,
                },
                ["weekly"] = new Dictionary<string, object> { ["fortress"] = data.WeeklyFortressReward, ["operation"] = data.WeeklyOperationReward },
                ["mutators"] = data.Mutators.Select(m => (object)new Dictionary<string, object>
                {
                    ["id"] = m.Id, ["name"] = Text("mutator." + m.Id), ["info"] = Text("mutator." + m.Id + ".info"), ["score"] = m.Score,
                }).ToList(),
                ["replayable"] = Operations.Replayable.Select(m => Text("mission." + m.Id + ".name")).Cast<object>().ToList(),
                ["rotation"] = data.Rotation(Math.Max(1, Operations.Big.Count)).Select(e => (object)new Dictionary<string, object>
                {
                    ["operation"] = Operations.Big.Count > 0 ? Text("mission." + Operations.Big[e.operation].Id + ".name") : "",
                    ["a"] = Text("mutator." + e.a.Id), ["b"] = Text("mutator." + e.b.Id),
                }).ToList(),
            };
        }

        // A small JSON writer (dictionaries, lists, arrays, strings, numbers, booleans).
        private static string Json(object value)
        {
            var sb = new StringBuilder();
            Write(sb, value, 0);
            return sb.ToString();
        }

        private static void Write(StringBuilder sb, object value, int depth)
        {
            switch (value)
            {
                case null:
                    sb.Append("null");
                    break;
                case string s:
                    sb.Append('"');
                    foreach (var c in s)
                        sb.Append(c switch { '"' => "\\\"", '\\' => "\\\\", '\n' => "\\n", '\r' => "", '\t' => "\\t", _ => c.ToString() });
                    sb.Append('"');
                    break;
                case bool b:
                    sb.Append(b ? "true" : "false");
                    break;
                case float f:
                    sb.Append(float.IsFinite(f) ? Math.Round(f, 4).ToString(CultureInfo.InvariantCulture) : "0");
                    break;
                case double d:
                    sb.Append(double.IsFinite(d) ? Math.Round(d, 4).ToString(CultureInfo.InvariantCulture) : "0");
                    break;
                case int i:
                    sb.Append(i.ToString(CultureInfo.InvariantCulture));
                    break;
                case IDictionary dict:
                    sb.Append('{');
                    var first = true;
                    foreach (DictionaryEntry e in dict)
                    {
                        if (!first) sb.Append(',');
                        first = false;
                        sb.Append('\n').Append(' ', depth * 2 + 2);
                        Write(sb, e.Key.ToString(), depth + 1);
                        sb.Append(": ");
                        Write(sb, e.Value, depth + 1);
                    }
                    sb.Append('\n').Append(' ', depth * 2).Append('}');
                    break;
                case IEnumerable list:
                    sb.Append('[');
                    var firstItem = true;
                    foreach (var item in list)
                    {
                        if (!firstItem) sb.Append(", ");
                        firstItem = false;
                        Write(sb, item, depth + 1);
                    }
                    sb.Append(']');
                    break;
                default:
                    Write(sb, value.ToString(), depth);
                    break;
            }
        }
    }
}
