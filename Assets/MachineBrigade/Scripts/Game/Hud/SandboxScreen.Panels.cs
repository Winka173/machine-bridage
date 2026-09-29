using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    internal sealed partial class SandboxScreen
    {
        private IEnumerator _job;
        private readonly List<string> _duelA = new(), _duelB = new();
        private readonly List<SandboxUnit> _duelUnitsA = new(), _duelUnitsB = new();
        private float _duelDistance = 60f;
        private DuelFacing _duelFacing = DuelFacing.Front;
        private string _duelLine = "", _abLine = "";
        private SandboxGear _abA = SandboxGear.None, _abB = SandboxGear.Suggested;

        /// <summary>Long work (a duel over many seeds, A/B) a little each frame, so the screen keeps drawing.</summary>
        public void RunJobs()
        {
            if (_job != null && !_job.MoveNext()) _job = null;
        }

        // ------------------------------------------------------------------ the battle's settings (B.1, B.7, B.8, C.2, C.4-C.6)

        private void BattlePanel(VisualElement body)
        {
            var e = _c.Editor;
            var s = e.Scenario;
            // B.1: every battlefield (its 300 m, long and coastal versions) and the flat test range.
            var maps = new List<string> { SandboxMaps.FlatId };
            var names = new List<string> { Strings.Get("sandbox.map.flat") };
            foreach (var info in MatchSettings.AllMaps)
            {
                if (!MatchSettings.MapAvailable(info.Id)) continue;
                maps.Add(info.Id + "_conquest");
                names.Add(Strings.Get("map." + info.Id));
                if (Resources.Load<TextAsset>("Data/maps/" + info.Id + "_long") == null) continue;
                maps.Add(info.Id + "_long");
                names.Add(SandboxText.Format("sandbox.map.long", ("map", Strings.Get("map." + info.Id))));
            }
            body.Add(Drop(Strings.Get("sandbox.map"), names, Math.Max(0, maps.IndexOf(s.Map)), i =>
            {
                e.Settings(x => x.Map = maps[i]);
                _c.Rebuild(false);
            }));
            var weathers = new[] { "Clear", "Overcast", "Rain", "Storm", "Snow", "Sandstorm", "Fog" };
            var weatherNames = new List<string>();
            foreach (var w in weathers) weatherNames.Add(Strings.Get("menu." + w.ToLowerInvariant()));
            body.Add(Drop(Strings.Get("sandbox.weather"), weatherNames, Math.Max(0, Array.IndexOf(weathers, s.Weather)), i => e.Settings(x => x.Weather = weathers[i])));
            body.Add(new KitToggle(Strings.Get("sandbox.night"), s.Night, on => e.Settings(x => x.Night = on)));
            body.Add(new KitToggle(Strings.Get("sandbox.fog"), s.Fog, on => e.Settings(x => x.Fog = on)));
            var limits = new[] { 0f, 60f, 120f, 180f, 300f, 600f };
            var limitNames = new List<string>();
            foreach (var l in limits) limitNames.Add(l <= 0f ? Strings.Get("sandbox.limit.none") : SandboxText.Format("sandbox.limit", ("seconds", (int)l)));
            body.Add(Drop(Strings.Get("sandbox.limit.label"), limitNames, Math.Max(0, Array.IndexOf(limits, s.Limit)), i => e.Settings(x => x.Limit = limits[i])));
            var diffNames = new List<string>();
            foreach (var d in Difficulties) diffNames.Add(Strings.Get("sandbox.diff." + d));
            body.Add(Drop(Strings.Get("sandbox.boss.difficulty"), diffNames, Math.Max(0, Array.IndexOf(Difficulties, s.Difficulty)), i => e.Settings(x => x.Difficulty = Difficulties[i])));
            // C.6: the seed.
            var seed = new TextField(Strings.Get("sandbox.seed")) { value = s.Seed.ToString() };
            seed.AddToClassList("sb-field");
            seed.isDelayed = true;
            seed.RegisterValueChangedCallback(ev =>
            {
                if (int.TryParse(ev.newValue, out var n)) e.Settings(x => x.Seed = n);
            });
            body.Add(seed);
            body.Add(Kit.Text(Strings.Get("sandbox.seed.hint"), "fc-small sb-hint"));
            for (var team = 0; team < 2; team++)
            {
                var t = team;
                var side = s.Sides[team];
                body.Add(Kit.Text(Kit.Caps(Strings.Get("sandbox.side." + team)), "fc-caption sb-caption sb-side--" + team));
                var ais = (SandboxAi[])Enum.GetValues(typeof(SandboxAi));
                var aiNames = new List<string>();
                foreach (var a in ais) aiNames.Add(Strings.Get("sandbox.ai." + a));
                body.Add(Drop(Strings.Get("sandbox.ai"), aiNames, (int)side.Ai, i => e.Settings(x => x.Sides[t].Ai = ais[i])));
                body.Add(new KitToggle(Strings.Get("sandbox.cp.unlimited"), side.Cp < 0f, on =>
                {
                    e.Settings(x => x.Sides[t].Cp = on ? -1f : 30f);
                    Reopen(BattlePanel);
                }));
                if (side.Cp >= 0f)
                    body.Add(Stepper(SandboxText.Format("sandbox.cp.value", ("cp", (int)side.Cp)), () =>
                    {
                        e.Settings(x => x.Sides[t].Cp = Math.Max(0f, x.Sides[t].Cp - 10f));
                        Reopen(BattlePanel);
                    }, () =>
                    {
                        e.Settings(x => x.Sides[t].Cp = Math.Min(200f, x.Sides[t].Cp + 10f));
                        Reopen(BattlePanel);
                    }));
                body.Add(new KitToggle(Strings.Get("sandbox.cooldowns"), side.Cooldowns, on => e.Settings(x => x.Sides[t].Cooldowns = on)));
                body.Add(new KitToggle(Strings.Get("sandbox.sideImmortal"), side.Immortal, on => e.Settings(x => x.Sides[t].Immortal = on)));
                body.Add(Row(new KitChip(Strings.Get("sandbox.supports.deck"), true, () => e.Settings(x =>
                    {
                        x.Sides[t].Supports.Clear();
                        x.Sides[t].Supports.AddRange(MatchSettings.DeckSupports);
                    })),
                    new KitChip(Strings.Get("sandbox.supports.free"), false, () => e.Settings(x =>
                    {
                        x.Sides[t].Supports.Clear();
                        foreach (var id in MatchSettings.AllSupports)
                            if (_c.World.Catalog.TryGetSupport(id, out _) && (SandboxSession.Internal || PlayerProfile.IsUnlocked(id))) x.Sides[t].Supports.Add(id);
                    }))));
                var bases = (SandboxBase[])Enum.GetValues(typeof(SandboxBase));
                var baseNames = new List<string>();
                foreach (var b in bases) baseNames.Add(Strings.Get("sandbox.base." + b));
                body.Add(Drop(Strings.Get("sandbox.base"), baseNames, (int)side.Base, i => e.Settings(x => x.Sides[t].Base = bases[i])));
            }
            body.Add(Kit.Text(Strings.Get("sandbox.applyOnRun"), "fc-small sb-hint"));
        }

        // ------------------------------------------------------------------ both sides while running (C.4, C.5)

        /// <summary>Each side's CP, cooldowns, immortality and a support to call on the map.</summary>
        private void SidesPanel(VisualElement body)
        {
            for (var team = 0; team < 2; team++)
            {
                var t = team;
                body.Add(Kit.Text(Kit.Caps(Strings.Get("sandbox.side." + team)), "fc-caption sb-caption sb-side--" + team));
                body.Add(new KitToggle(Strings.Get("sandbox.cp.unlimited"), _c.Battle.Unlimited(team), on => _c.Queue(SandboxOp.Side(SandboxOpKind.SideCp, t, on ? -1 : 20))));
                body.Add(new KitToggle(Strings.Get("sandbox.cooldowns"), _c.Battle.CooldownsOn(team), on => _c.Queue(SandboxOp.Side(SandboxOpKind.Cooldowns, t, on ? 1 : 0))));
                body.Add(new KitToggle(Strings.Get("sandbox.sideImmortal"), _c.Battle.SideImmortal(team), on => _c.Queue(SandboxOp.Side(SandboxOpKind.SideImmortal, t, on ? 1 : 0))));
                if (!_c.World.TryGetEconomy(team, out var economy) || economy.Supports.Count == 0) continue;
                body.Add(Caption("sandbox.call"));
                var row = Row();
                foreach (var s in economy.Supports)
                {
                    var support = s;
                    row.Add(Small(Strings.Support(s), () =>
                    {
                        _c.Strike = support;
                        _c.StrikeTeam = t;
                        _c.Picking = SandboxController.Pick.Strike;
                        CloseSheet();
                        Refresh();
                    }));
                }
                body.Add(row);
            }
        }

        // ------------------------------------------------------------------ scenarios (F.1, F.2, F.6, F.7)

        private void ScenariosPanel(VisualElement body)
        {
            var e = _c.Editor;
            var name = new TextField(Strings.Get("sandbox.name")) { value = e.Scenario.Name, isDelayed = true };
            name.AddToClassList("sb-field");
            name.RegisterValueChangedCallback(ev => e.Settings(x => x.Name = string.IsNullOrWhiteSpace(ev.newValue) ? x.Name : ev.newValue.Trim()));
            body.Add(name);
            body.Add(Row(Small(Strings.Get("sandbox.save"), () =>
            {
                Toast(SandboxProfile.SaveSlot(e.Scenario) ? Strings.Get("sandbox.saved") : SandboxText.Format("sandbox.full", ("max", SandboxProfile.MaxSlots)), false);
                Reopen(ScenariosPanel);
            }), Small(Strings.Get("sandbox.code.copy"), () =>
            {
                GUIUtility.systemCopyBuffer = e.Scenario.ToCode();
                Toast(Strings.Get("sandbox.code.copied"));
            })));
            var code = new TextField(Strings.Get("sandbox.code.field"));
            code.AddToClassList("sb-field");
            body.Add(code);
            body.Add(Small(Strings.Get("sandbox.code.paste"), () => OpenCode(string.IsNullOrWhiteSpace(code.value) ? GUIUtility.systemCopyBuffer : code.value)));
            if (!_c.Editing)
                body.Add(Small(Strings.Get("sandbox.replay"), ExportReplay));
            if (SandboxSession.Internal)
                body.Add(Small(Strings.Get("sandbox.test"), SaveAsTest));

            body.Add(Caption("sandbox.samples"));
            foreach (var id in SandboxSamples.Ids)
            {
                var sample = id;
                body.Add(Small(Strings.Get("sandbox.sample." + id), () => Load(SandboxSamples.Get(sample), true)));
            }
            body.Add(Kit.Text(Kit.Caps(SandboxText.Format("sandbox.mine", ("count", SandboxProfile.Slots.Count), ("max", SandboxProfile.MaxSlots))), "fc-caption sb-caption"));
            for (var i = 0; i < SandboxProfile.Slots.Count; i++)
            {
                var slot = i;
                body.Add(Row(Small(SandboxProfile.Slots[i], () => Load(SandboxProfile.LoadSlot(slot), false)), Small(Strings.Get("sandbox.delete"), () =>
                {
                    SandboxProfile.DeleteSlot(slot);
                    Reopen(ScenariosPanel);
                })));
            }
        }

        /// <summary>Opens a scenario (fitted to the player's units, F.7); a different map rebuilds the scene.</summary>
        private void Load(SandboxScenario s, bool fit)
        {
            if (s == null) return;
            var changes = _c.Session.Access.Fit(_c.World.Catalog, s);
            foreach (var (from, to) in changes)
                Toast(to != null ? SandboxText.Format("sandbox.replaced", ("from", Strings.Unit(from)), ("to", Strings.Unit(to)))
                    : SandboxText.Format("sandbox.removed", ("from", Strings.Unit(from))), true);
            _c.Selected.Clear();
            _c.Editor.Load(s);
            CloseSheet();
            if (!_c.Editing || s.Map != SandboxSession.LoadedMap) _c.Rebuild(false);
            else Toast(Strings.Get("sandbox.opened"));
        }

        private void OpenCode(string code)
        {
            try
            {
                Load(SandboxScenario.FromCode(code), true);
            }
            catch (FormatException ex)
            {
                Toast(Strings.Get(ex.Message.Contains("newer") ? "sandbox.code.newer" : "sandbox.code.bad"), true);
            }
        }

        private static string SandboxFolder(string sub)
        {
            var dir = Path.Combine(Application.persistentDataPath, "sandbox", sub);
            Directory.CreateDirectory(dir);
            return dir;
        }

        /// <summary>F.6: the scenario, its seed and the journal of controls, for a bug report (and on the clipboard).</summary>
        private void ExportReplay()
        {
            var json = _c.Battle.ReplayJson();
            var path = Path.Combine(SandboxFolder("replays"), $"replay-{_c.Battle.Scenario.Seed}-{_c.World.Tick}.json");
            File.WriteAllText(path, json);
            GUIUtility.systemCopyBuffer = json;
            Toast(SandboxText.Format("sandbox.replay.saved", ("path", path)));
        }

        /// <summary>
        /// F.2 (internal): the scenario as an automatic test with its pass conditions ("Blue wins within 60 s", "no
        /// vehicle stuck"): in the editor straight into the test suite's folder, in a development build beside the saves.
        /// </summary>
        private void SaveAsTest()
        {
            var s = _c.Editor.Scenario.Clone();
            if (s.Checks.Count == 0)
            {
                s.Checks.Add(new SandboxCheck { Kind = "win", Team = 0, Seconds = s.Limit > 0f ? s.Limit : 60f });
                s.Checks.Add(new SandboxCheck { Kind = "noStuck" });
            }
            var file = new string(Array.FindAll((s.Name.Length > 0 ? s.Name : "scenario").ToCharArray(), ch => char.IsLetterOrDigit(ch) || ch == '_' || ch == '-')) + ".json";
            var dir = Application.isEditor ? Path.Combine(Application.dataPath, "MachineBrigade", "Tests", "EditMode", "Scenarios") : SandboxFolder("tests");
            Directory.CreateDirectory(dir);
            var path = Path.Combine(dir, file);
            File.WriteAllText(path, s.ToJson());
            Toast(SandboxText.Format("sandbox.test.saved", ("path", path)));
        }

        // ------------------------------------------------------------------ the quick duel (F.5)

        private void DuelPanel(VisualElement body)
        {
            body.Add(Small(Strings.Get("sandbox.duel.pick"), () =>
            {
                _duelA.Clear();
                _duelB.Clear();
                _duelUnitsA.Clear();
                _duelUnitsB.Clear();
                if (_c.Editing)
                    foreach (var i in _c.Selected)
                    {
                        var u = _c.Editor.Units[i];
                        (u.Team == 0 ? _duelA : _duelB).Add(u.Def);
                        (u.Team == 0 ? _duelUnitsA : _duelUnitsB).Add(u.Clone());
                    }
                else
                    foreach (var v in _c.SelectedVehicles())
                        (v.Team == 0 ? _duelA : _duelB).Add(v.Def.Id);
                Reopen(DuelPanel);
            }));
            string Names(List<string> ids)
            {
                var names = new List<string>();
                foreach (var id in ids) names.Add(Strings.Short(id));
                return names.Count > 0 ? string.Join(", ", names) : "—";
            }
            body.Add(Kit.Text(SandboxText.Format("sandbox.duel.a", ("units", Names(_duelA))), "fc-body sb-side--0"));
            body.Add(Kit.Text(SandboxText.Format("sandbox.duel.b", ("units", Names(_duelB))), "fc-body sb-side--1"));
            body.Add(Stepper(SandboxText.Format("sandbox.duel.distance", ("metres", (int)_duelDistance)), () =>
            {
                _duelDistance = Math.Max(10f, _duelDistance - 10f);
                Reopen(DuelPanel);
            }, () =>
            {
                _duelDistance = Math.Min(250f, _duelDistance + 10f);
                Reopen(DuelPanel);
            }));
            var facing = Row();
            foreach (DuelFacing f in Enum.GetValues(typeof(DuelFacing)))
            {
                var ff = f;
                facing.Add(new KitChip(Strings.Get("sandbox.duel.facing." + f), f == _duelFacing, () =>
                {
                    _duelFacing = ff;
                    Reopen(DuelPanel);
                }));
            }
            body.Add(facing);
            body.Add(Row(Small(Strings.Get("sandbox.duel.run"), () => StartDuel(1)), Small(SandboxText.Format("sandbox.duel.many", ("seeds", 20)), () => StartDuel(20))));
            body.Add(Kit.Text(_duelLine, "fc-body sb-result"));
        }

        /// <summary>A duel's scenario with the picked units' own rank, equipment, elite, health and ammunition.</summary>
        private SandboxScenario DuelScenario(int seed)
        {
            var s = SandboxLab.DuelScenario(_c.World.Catalog, _duelA, _duelB, _duelDistance, _duelFacing, seed);
            var (a, b) = (0, 0);
            foreach (var u in s.Units)
            {
                var from = u.Team == 0 ? (a < _duelUnitsA.Count ? _duelUnitsA[a++] : null) : (b < _duelUnitsB.Count ? _duelUnitsB[b++] : null);
                if (from == null) continue;
                (u.Rank, u.Gear, u.Elite, u.Hp, u.Ammo) = (from.Rank, from.Gear, from.Elite, from.Hp, from.Ammo);
            }
            return s;
        }

        private void StartDuel(int seeds)
        {
            if (_duelA.Count == 0 || _duelB.Count == 0)
            {
                Toast(Strings.Get("sandbox.duel.need"), true);
                return;
            }
            _job = Duel(seeds);
        }

        private IEnumerator Duel(int seeds)
        {
            var (wa, wb, draws) = (0, 0, 0);
            var first = _c.Editor.Scenario.Seed;
            for (var i = 0; i < seeds; i++)
            {
                var s = DuelScenario(first + i);
                var r = SandboxLab.Run(_c.World.Catalog, SandboxMaps.Flat(), s, s.Limit + 1f, SandboxSession.BoostFor);
                var winner = r.Winner < -1 ? -1 : r.Winner;
                if (winner == 0) wa++;
                else if (winner == 1) wb++;
                else draws++;
                _duelLine = seeds == 1 ? ResultLine(winner, r.Seconds, r.HealthLeft[0], r.HealthLeft[1])
                    : SandboxText.Format("sandbox.duel.rate", ("blue", wa), ("red", wb), ("draws", draws), ("seeds", i + 1));
                if (_sheet.style.display == DisplayStyle.Flex) Reopen(DuelPanel);
                yield return null;
            }
        }

        // ------------------------------------------------------------------ A/B (F.3)

        private void AbPanel(VisualElement body)
        {
            foreach (var which in new[] { 0, 1 })
            {
                var row = Row(Kit.Text(which == 0 ? "A" : "B", "fc-body"));
                foreach (SandboxGear g in Enum.GetValues(typeof(SandboxGear)))
                {
                    var gear = g;
                    row.Add(new KitChip(Strings.Get("sandbox.gear." + g), (which == 0 ? _abA : _abB) == g, () =>
                    {
                        if (which == 0) _abA = gear;
                        else _abB = gear;
                        Reopen(AbPanel);
                    }));
                }
                body.Add(row);
            }
            body.Add(Kit.Text(SandboxText.Format("sandbox.ab.gear", ("a", Strings.Get("sandbox.gear." + _abA)), ("b", Strings.Get("sandbox.gear." + _abB))), "fc-small"));
            body.Add(Small(Strings.Get("sandbox.ab.run"), () => _job = Ab()));
            body.Add(Kit.Text(_abLine, "fc-body sb-result"));
        }

        private IEnumerator Ab()
        {
            var lines = new List<string>();
            foreach (var (label, gear) in new[] { ("A", _abA), ("B", _abB) })
            {
                var s = _c.Editor.Scenario.Clone();
                foreach (var u in s.Units)
                    if (u.Team == 0) u.Gear = gear;
                var r = SandboxLab.Run(_c.World.Catalog, _c.World.Map, s, s.Limit > 0f ? s.Limit + 1f : 120f, SandboxSession.BoostFor);
                lines.Add(SandboxText.Format("sandbox.ab.row", ("label", label), ("line", ResultLine(r.Winner, r.Seconds, r.HealthLeft[0], r.HealthLeft[1]))));
                _abLine = string.Join("\n", lines);
                if (_sheet.style.display == DisplayStyle.Flex) Reopen(AbPanel);
                yield return null;
            }
        }

        // ------------------------------------------------------------------ statistics (F.4)

        private void StatsPanel(VisualElement body)
        {
            void Fill()
            {
                body.Clear();
                var stats = _c.Battle.Stats.Units;
                if (_c.Editing || stats.Count == 0)
                {
                    body.Add(Kit.Text(Strings.Get("sandbox.stats.none"), "fc-small sb-hint"));
                    return;
                }
                var head = Kit.Box("fc-row sb-trow sb-trow--head");
                foreach (var key in new[] { "sandbox.stats.unit", "sandbox.stats.dealt", "sandbox.stats.taken", "sandbox.stats.ttk", "sandbox.stats.alive", "sandbox.stats.pierced", "sandbox.stats.bounced" })
                    head.Add(Kit.Text(Strings.Get(key), "fc-small sb-tcell"));
                body.Add(head);
                var now = _c.World.Time;
                foreach (var u in stats)
                {
                    if (u.DealtTotal <= 0f && u.TakenTotal <= 0f) continue;
                    var row = Kit.Box("fc-row sb-trow");
                    row.Add(Kit.Text(Strings.Short(u.Def), "fc-small sb-tcell sb-side--" + Mathf.Clamp(u.Team, 0, 1)));
                    row.Add(Kit.Text(SandboxText.Number(u.DealtTotal), "fc-small sb-tcell"));
                    row.Add(Kit.Text(SandboxText.Number(u.TakenTotal), "fc-small sb-tcell"));
                    row.Add(Kit.Text(u.TimeToKill >= 0 ? SandboxText.Format("sandbox.seconds", ("seconds", SandboxText.Number(u.TimeToKill, 1))) : "—", "fc-small sb-tcell"));
                    row.Add(Kit.Text(SandboxText.Format("sandbox.seconds", ("seconds", SandboxText.Number(u.Lifetime(now), 0))), "fc-small sb-tcell"));
                    row.Add(Kit.Text((u.Pierced).ToString(), "fc-small sb-tcell"));
                    row.Add(Kit.Text((u.Bounced).ToString(), "fc-small sb-tcell"));
                    body.Add(row);
                    var types = new List<string>();
                    var values = (DamageType[])Enum.GetValues(typeof(DamageType));
                    foreach (var t in values)
                    {
                        var i = (int)t;
                        if (u.Dealt[i] > 0f || u.Taken[i] > 0f)
                            types.Add(Strings.Get("dtype." + t) + " " + SandboxText.Number(u.Dealt[i]) + " / " + SandboxText.Number(u.Taken[i]));
                    }
                    if (types.Count > 0) body.Add(Kit.Text(string.Join(" · ", types), "fc-small sb-types"));
                }
            }
            Fill();
            _sheetRefresh = Fill;
        }

        // ------------------------------------------------------------------ the first-time guide (G.3)

        public void ShowHint()
        {
            var card = Kit.Box(KitPanel.SurfaceClass + " sb-guide", PickingMode.Position);
            card.Add(Kit.Text(Kit.Caps(Strings.Get("sandbox.title")), "fc-panel-title"));
            foreach (var key in new[] { "sandbox.hint.1", "sandbox.hint.2", "sandbox.hint.3" }) card.Add(Kit.Text(Strings.Get(key), "fc-body sb-guide__line"));
            card.Add(Kit.Text(Strings.Get("sandbox.noRewards"), "fc-small sb-hint"));
            card.Add(new KitButton(ButtonTier.Secondary, Strings.Get("sandbox.hint.ok"), () =>
            {
                SandboxProfile.HintSeen = true;
                card.RemoveFromHierarchy();
            }));
            _frame.Add(card);
        }
    }
}
