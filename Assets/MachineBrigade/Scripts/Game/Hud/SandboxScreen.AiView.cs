using System;
using System.Collections.Generic;
using System.Text;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Economy;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 28 J (internal build only): the AI viewer sheet. One small texture a layer (influence, a threat kind,
    /// information age, front and chokepoints, events), repainted only when the World Model has refreshed (its 2 Hz);
    /// then the general's tactic and "VÌ SAO", actual against target force shares, upkeep and CP income, the events, each
    /// squad's task, state, action, formation and tactic with the decision-churn warning, and "VÌ SAO" for the selected
    /// unit and its squad. It reads <see cref="WorldModel.Peek"/>, so looking never changes when the AI refreshes.
    /// </summary>
    internal sealed partial class SandboxScreen
    {
        private enum AiMap
        {
            Influence,
            ThreatAir,
            ThreatTank,
            ThreatArtillery,
            ThreatSplash,
            Confidence,
            Front,
            Events,
        }

        private int _aiSide;
        private AiMap _aiMap;
        private readonly Dictionary<AiMap, Texture2D> _aiTextures = new();
        private readonly Dictionary<AiMap, (int side, double at)> _aiPainted = new();
        private Color32[] _aiPixels;

        private void AiViewPanel(VisualElement body)
        {
            void Fill()
            {
                body.Clear();
                var sides = Kit.Box("fc-row sb-wrap");
                for (var team = 0; team < 2; team++)
                {
                    var t = team;
                    sides.Add(new KitChip(Strings.Get("sandbox.side." + team), _aiSide == team, () =>
                    {
                        _aiSide = t;
                        Fill();
                    }));
                }
                body.Add(sides);
                var layers = Kit.Box("fc-row sb-wrap");
                foreach (AiMap m in Enum.GetValues(typeof(AiMap)))
                {
                    var map = m;
                    layers.Add(new KitChip(MapName(m), _aiMap == m, () =>
                    {
                        _aiMap = map;
                        Fill();
                    }));
                }
                body.Add(layers);

                var world = _c.World;
                var intel = world.Intel.Peek(_aiSide);
                if (intel == null)
                {
                    body.Add(Kit.Text(Strings.Get("sandbox.stats.none"), "fc-small sb-hint"));
                    return;
                }
                var image = Kit.Box("sb-aiview__map");
                image.style.width = 300;
                image.style.height = Mathf.Clamp(300f * intel.Rows / Mathf.Max(1, intel.Columns), 60f, 420f);
                image.style.backgroundImage = Background.FromTexture2D(Paint(intel));
                image.style.marginTop = 4;
                image.style.marginBottom = 4;
                body.Add(image);
                body.Add(Kit.Text(Legend(_aiMap), "fc-small sb-hint"));

                world.AiCommanders.TryGetValue(_aiSide, out var general);
                world.TryGetEconomy(_aiSide, out var economy);
                if (general != null)
                {
                    body.Add(Caption("tactic.title"));
                    var line = TacticText.Name(general.CurrentTactic);
                    if (general.InTransition) line += " · " + Strings.Get("tactic.transition");
                    body.Add(Kit.Text(line, "fc-body-2"));
                    WhyLines(body, world.AiLog.Latest(AiLayer.Commander, _aiSide, 0));
                    if (economy != null) body.Add(Kit.Text(ForceShares(general, economy, intel), "fc-small sb-hint"));
                }
                if (economy != null)
                {
                    body.Add(Caption("aiview.layer.economy"));
                    body.Add(Kit.Text(Strings.Format("upkeep.factor", ("factor", economy.ArmyFactor.ToString("0.00", Kit.Culture))) +
                                      " · " + economy.Earning.ToString("0.00", Kit.Culture) + " CP/s · " +
                                      Strings.Format("aiview.pressure", ("tier", world.PressureTier)), "fc-small sb-hint"));
                }

                body.Add(Caption("aiview.layer.events"));
                var shown = 0;
                foreach (var e in intel.Events)
                {
                    if (shown++ >= 6) break;
                    body.Add(Kit.Text($"{e.Kind} p{e.Priority:0} c{e.Confidence:0.00} · {e.Reason}", "fc-small sb-hint"));
                }
                if (shown == 0) body.Add(Kit.Text("-", "fc-small sb-hint"));

                if (general != null)
                {
                    body.Add(Caption("aiview.layer.squads"));
                    var now = world.Time;
                    foreach (var s in general.Squads.Squads)
                    {
                        var tactic = TacticText.Name(general.TacticFor(s));
                        var text = $"#{s.Id} ({s.Members.Count}) {s.Task.Kind} · {Word("squad.state." + s.State)} · {Word("squad.action." + s.Action)} · {s.Formation} · {tactic}";
                        var row = Kit.Text(text, "fc-small sb-hint");
                        if (world.AiLog.Churning(_aiSide, s.Id, now))
                        {
                            row.text += "  ⚠ " + Strings.Get("aiview.churn");
                            row.AddToClassList("fc-danger-text");
                        }
                        body.Add(row);
                    }
                }

                // "VÌ SAO" for the selected unit and its squad.
                foreach (var v in _c.SelectedVehicles())
                {
                    body.Add(Caption("aiview.why"));
                    body.Add(Kit.Text(Strings.Unit(v.Def.Id) + " #" + v.Id.Value, "fc-body-2"));
                    WhyLines(body, world.AiLog.Latest(AiLayer.Unit, v.Team, v.Id.Value));
                    if (world.AiCommanders.TryGetValue(v.Team, out var own))
                        foreach (var s in own.Squads.Squads)
                            if (Contains(s.Members, v.Id))
                            {
                                body.Add(Kit.Text(Strings.Get("tactic.squad") + " #" + s.Id, "fc-body-2"));
                                WhyLines(body, world.AiLog.Latest(AiLayer.Squad, v.Team, s.Id));
                            }
                    break;
                }
            }
            Fill();
            _sheetRefresh = Fill;
        }

        private static bool Contains(IReadOnlyList<MachineBrigade.Sim.Core.EntityId> list, MachineBrigade.Sim.Core.EntityId id)
        {
            foreach (var x in list)
                if (x == id) return true;
            return false;
        }

        private static string Word(string key) => Strings.Has(key) ? Strings.Get(key) : key.Substring(key.LastIndexOf('.') + 1);

        /// <summary>J.2: the choice, its score, its biggest plus and minus factors, and the runner-up.</summary>
        private static void WhyLines(VisualElement body, Why why)
        {
            if (why == null)
            {
                body.Add(Kit.Text("-", "fc-small sb-hint"));
                return;
            }
            var b = new StringBuilder();
            if (!string.IsNullOrEmpty(why.Context)) b.Append(why.Context).Append(" · ");
            b.Append(why.Choice).Append(' ').Append(why.Score.ToString("0", Kit.Culture));
            foreach (var f in why.Plus) b.Append("\n  +").Append(f.Points.ToString("0", Kit.Culture)).Append(' ').Append(Word(f.Key));
            foreach (var f in why.Minus) b.Append("\n  ").Append(f.Points.ToString("0", Kit.Culture)).Append(' ').Append(Word(f.Key));
            if (why.RunnerUp != null)
                b.Append('\n').Append(Strings.Format("aiview.runnerUp", ("action", why.RunnerUp), ("score", why.RunnerUpScore.ToString("0", Kit.Culture))));
            foreach (var e in why.Events) b.Append("\n  · ").Append(e);
            body.Add(Kit.Text(b.ToString(), "fc-small sb-hint"));
        }

        /// <summary>H.5: CP spent per group against the tactic's target shares for this deck (MISMATCH moves included).</summary>
        private string ForceShares(AiCommander general, TeamEconomy economy, TeamIntel intel)
        {
            var target = (float[])general.CurrentTactic.Cp.Clone();
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.Mismatch && e.Need is { } need) target[(int)need] += 0.15f * e.Confidence;
            var present = new bool[target.Length];
            foreach (var id in economy.Vehicles)
                if (_c.World.Catalog.Vehicles.TryGetValue(id, out var d) && TeamIntel.GroupOf(d) is { } g) present[(int)g] = true;
            var sum = 0f;
            for (var i = 0; i < target.Length; i++)
            {
                if (!present[i]) target[i] = 0f;
                sum += target[i];
            }
            var spent = 0f;
            foreach (var x in general.Spent) spent += x;
            var parts = new List<string>();
            for (var i = 0; i < target.Length && i < general.Spent.Count; i++)
            {
                if (target[i] <= 0f && general.Spent[i] <= 0f) continue;
                var have = spent > 0f ? general.Spent[i] / spent : 0f;
                var want = sum > 0f ? target[i] / sum : 0f;
                parts.Add($"{(ForceGroup)i} {Mathf.RoundToInt(have * 100f)}/{Mathf.RoundToInt(want * 100f)}%");
            }
            return Strings.Get("tactic.mix") + ": " + (parts.Count > 0 ? string.Join(" · ", parts) : "-");
        }

        private static string MapName(AiMap m) => m switch
        {
            AiMap.Influence => Strings.Get("aiview.layer.influence"),
            AiMap.ThreatAir => Strings.Get("aiview.layer.threat") + " AA",
            AiMap.ThreatTank => Strings.Get("aiview.layer.threat") + " AT",
            AiMap.ThreatArtillery => Strings.Get("aiview.layer.threat") + " ART",
            AiMap.ThreatSplash => Strings.Get("aiview.layer.threat") + " AOE",
            AiMap.Confidence => Strings.Get("aiview.layer.confidence"),
            AiMap.Front => Strings.Get("aiview.layer.front"),
            _ => Strings.Get("aiview.layer.events"),
        };

        private static string Legend(AiMap m) => m switch
        {
            AiMap.Influence => Strings.Get("aiview.legend.influence"),
            AiMap.Confidence => Strings.Get("aiview.legend.confidence"),
            AiMap.Front => Strings.Get("aiview.legend.front"),
            AiMap.Events => Strings.Get("aiview.legend.events"),
            _ => Strings.Get("aiview.legend.threat"),
        };

        /// <summary>The layer's texture, repainted only when the side's picture has refreshed since (or another side is shown).</summary>
        private Texture2D Paint(TeamIntel intel)
        {
            int w = intel.Columns, h = intel.Rows, n = w * h;
            if (!_aiTextures.TryGetValue(_aiMap, out var tex) || tex == null || tex.width != w || tex.height != h)
            {
                tex = new Texture2D(w, h, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp, name = "AI view " + _aiMap };
                _aiTextures[_aiMap] = tex;
                _aiPainted.Remove(_aiMap);
            }
            if (_aiPainted.TryGetValue(_aiMap, out var last) && last.side == _aiSide && last.at == intel.UpdatedAt) return tex;
            _aiPainted[_aiMap] = (_aiSide, intel.UpdatedAt);
            if (_aiPixels == null || _aiPixels.Length != n) _aiPixels = new Color32[n];
            var px = _aiPixels;
            var bg = new Color32(24, 28, 32, 255);
            for (var i = 0; i < n; i++) px[i] = bg;
            var now = _c.World.Time;
            switch (_aiMap)
            {
                case AiMap.Influence:
                {
                    var max = 0.01f;
                    for (var i = 0; i < n; i++) max = Mathf.Max(max, Mathf.Max(intel.Own[i], intel.Enemy[i]));
                    for (var i = 0; i < n; i++)
                    {
                        var own = intel.Own[i] / max;
                        var enemy = intel.Enemy[i] / max;
                        px[i] = new Color32((byte)(24 + 220 * Mathf.Clamp01(enemy)), (byte)(28 + 60 * Mathf.Clamp01(Mathf.Min(own, enemy))), (byte)(32 + 220 * Mathf.Clamp01(own)), 255);
                    }
                    break;
                }
                case AiMap.Confidence:
                    for (var i = 0; i < n; i++)
                    {
                        var seen = intel.Seen[i];
                        if (double.IsNegativeInfinity(seen)) continue;
                        var c = Mathf.Clamp01(1f - (float)(now - seen) * intel.ConfidenceDecay);
                        px[i] = new Color32((byte)(40 + 60 * c), (byte)(50 + 200 * c), (byte)(40 + 80 * c), 255);
                    }
                    break;
                case AiMap.Front:
                    foreach (var i in intel.Contested) px[i] = new Color32(200, 200, 200, 255);
                    foreach (var i in intel.Front) px[i] = new Color32(240, 200, 40, 255);
                    foreach (var i in intel.Chokepoints) px[i] = new Color32(220, 60, 220, 255);
                    break;
                case AiMap.Events:
                    foreach (var z in intel.Warnings) Disc(intel, px, z.Centre, z.Radius, new Color32(255, 90, 40, 255));
                    foreach (var e in intel.Events) Disc(intel, px, e.Centre, Mathf.Max(e.Radius, intel.Cell), EventColour(e.Kind));
                    foreach (var g in intel.EnemyGroups) Disc(intel, px, g.Centre, intel.Cell, new Color32(255, 40, 40, (byte)(80 + 175 * g.Confidence)));
                    break;
                default:
                {
                    var k = _aiMap switch { AiMap.ThreatAir => 0, AiMap.ThreatTank => 1, AiMap.ThreatArtillery => 2, _ => 3 };
                    var layer = intel.Threat[k];
                    var max = 0.01f;
                    for (var i = 0; i < n; i++) max = Mathf.Max(max, layer[i]);
                    for (var i = 0; i < n; i++)
                    {
                        var v = Mathf.Clamp01(layer[i] / max);
                        if (v > 0f) px[i] = new Color32((byte)(40 + 215 * v), (byte)(30 + 120 * v), 30, 255);
                    }
                    break;
                }
            }
            tex.SetPixels32(px);
            tex.Apply(false);
            return tex;
        }

        private static Color32 EventColour(IntelEventKind kind) => kind switch
        {
            IntelEventKind.Threat => new Color32(230, 70, 60, 255),
            IntelEventKind.Opportunity => new Color32(80, 210, 110, 255),
            IntelEventKind.Window => new Color32(90, 160, 240, 255),
            IntelEventKind.Mismatch => new Color32(240, 200, 60, 255),
            _ => new Color32(200, 120, 240, 255),
        };

        private static void Disc(TeamIntel intel, Color32[] px, System.Numerics.Vector2 centre, float radius, Color32 colour)
        {
            var r = Mathf.Max(0, Mathf.CeilToInt(radius / intel.Cell));
            var c = intel.CellIndex(centre);
            int cx = c % intel.Columns, cy = c / intel.Columns;
            for (var y = Math.Max(0, cy - r); y <= Math.Min(intel.Rows - 1, cy + r); y++)
                for (var x = Math.Max(0, cx - r); x <= Math.Min(intel.Columns - 1, cx + r); x++)
                    if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r) px[y * intel.Columns + x] = colour;
        }
    }
}
