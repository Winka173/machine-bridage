using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// A boss's Guide tab (prompt 9 D): its parts and what breaking each does, read from the data, with
    /// the general rule, its lock or self-repair if it has one, and a tip for fighting it part by part.
    /// Kept apart from MenuScreen.Detail.cs so the two change independently. On the kit's text styles (Field Command 2.0).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private void BossPartsGuide(VehicleDef def)
        {
            if (def.Parts.Count == 0) return;
            _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("guide.parts")), "fc-caption fc-mt-4"));
            _detailBody.Add(Kit.Text(Strings.Get("guide.parts.rule"), "fc-body fc-mt-2"));
            if (def.PartLock != null)
                _detailBody.Add(Kit.Text(Strings.Format("guide.parts.lock", Strings.Get("part." + def.PartLock.Kind)), "fc-body fc-mt-2"));
            foreach (var skill in def.Skills)
                if (skill.Kind == SkillKind.Patch)
                {
                    _detailBody.Add(Kit.Text(Strings.Get("guide.parts.patch"), "fc-body fc-mt-2"));
                    break;
                }
            // One line a kind of part and what it does ("flak gun ×2: its guns fall silent").
            var order = new List<string>();
            var counts = new Dictionary<string, int>();
            foreach (var part in def.Parts)
            {
                var line = Strings.Get("part." + part.Kind) + "\u0001" + PartEffects(def, part);
                if (!counts.ContainsKey(line))
                {
                    order.Add(line);
                    counts[line] = 0;
                }
                counts[line]++;
            }
            foreach (var line in order)
            {
                var bits = line.Split('\u0001');
                var name = counts[line] > 1 ? bits[0] + " ×" + counts[line] : bits[0];
                var label = Kit.Text(Strings.Highlight("[[" + name + "]]") + " " + bits[1], "fc-body fc-mt-2");
                label.enableRichText = true;
                _detailBody.Add(label);
            }
            if (Strings.Has("guide.parts.tip." + def.Id))
            {
                var tip = Kit.Text(Strings.Highlight(Strings.Get("guide.parts.tip." + def.Id)), "fc-body fc-mt-2");
                tip.enableRichText = true;
                _detailBody.Add(tip);
            }
            BigAttackGuide(def);
        }

        /// <summary>
        /// Prompt 18 D.4: the boss's big attack: its name, how it works, how to get out of it, how to stop it and who it
        /// is for, with its numbers from the data (prompt 13's rule: nothing typed twice).
        /// </summary>
        private void BigAttackGuide(VehicleDef def)
        {
            if (def.BigAttack is not { } big) return;
            _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("guide.bigattack")), "fc-caption fc-mt-4"));
            var name = Kit.Text(Strings.Highlight("[[" + Strings.Get(big.NameKey) + "]]") + " · " + BigAttackStats(big), "fc-body fc-mt-2");
            name.enableRichText = true;
            _detailBody.Add(name);
            foreach (var line in new[] { "how", "dodge", "stop" })
            {
                var key = big.GuideKey(line);
                if (!Strings.Has(key)) continue;
                var label = Kit.Text(Strings.Highlight("[[" + Strings.Get("guide.bigattack." + line) + "]]") + " " + Strings.Get(key), "fc-body fc-mt-2");
                label.enableRichText = true;
                _detailBody.Add(label);
            }
            var target = Kit.Text(Strings.Highlight("[[" + Strings.Get("guide.bigattack.target") + "]]") + " " + Strings.Get("guide.bigattack.target." + big.Target), "fc-body fc-mt-2");
            target.enableRichText = true;
            _detailBody.Add(target);
            _detailBody.Add(Kit.Text(Strings.Get("guide.bigattack.rule"), "fc-body fc-mt-2"));
        }

        /// <summary>A big attack's numbers in words: each strike's rounds, damage, type and penetration, its warning and cooldown.</summary>
        internal static string BigAttackStats(BigAttackDef big)
        {
            var hits = new List<string>();
            foreach (var s in big.Strikes)
                switch (s.Shape)
                {
                    case BigShape.Drop:
                        hits.Add(Strings.Format("guide.bigattack.drop", s.Units.Count));
                        break;
                    case BigShape.Buff:
                        hits.Add(Strings.Format("guide.bigattack.buff", Mathf.RoundToInt(s.Damage * 100f), Mathf.RoundToInt(s.FireRate * 100f),
                            Mathf.RoundToInt(s.Seconds), Mathf.RoundToInt(s.Reach)));
                        break;
                    default:
                        hits.Add(Strings.Format("guide.bigattack.hits", s.FullCount, Mathf.RoundToInt(s.Damage), Strings.Get("dtype." + s.Type).ToLowerInvariant(), s.Pen));
                        break;
                }
            return Strings.Format("guide.bigattack.stats", string.Join(" + ", hits), big.Warn.ToString("0.#"), Mathf.RoundToInt(big.Cooldown));
        }

        /// <summary>What breaking a part does, in words, from its data.</summary>
        internal static string PartEffects(VehicleDef def, BossPartDef part)
        {
            var bits = new List<string>();
            if (part.Mounts.Count > 0) bits.Add(Strings.Get("part.fx.guns"));
            foreach (var id in part.Skills)
                foreach (var skill in def.Skills)
                {
                    if (skill.Id != id) continue;
                    var key = "part.fx.skill." + skill.Kind;
                    var text = Strings.Get(Strings.Has(key) ? key : "part.fx.skill.Other");
                    if (!bits.Contains(text)) bits.Add(text);
                }
            foreach (var stop in part.Stops) bits.Add(Strings.Get("part.fx.stop." + stop));
            if (part.Speed < 1f) bits.Add(Strings.Format("part.fx.speed", Mathf.RoundToInt((1f - part.Speed) * 100f)));
            if (part.Turn < 1f) bits.Add(Strings.Format("part.fx.turn", Mathf.RoundToInt((1f - part.Turn) * 100f)));
            if (part.Cadence > 1f) bits.Add(Strings.Format("part.fx.cadence", Mathf.RoundToInt((1f - 1f / part.Cadence) * 100f)));
            if (part.Spread > 1f) bits.Add(Strings.Get("part.fx.spread"));
            // Prompt 18: the part that fires its big attack.
            if (def.BigAttack != null && def.BigAttack.UsesPart(part.Id)) bits.Add(Strings.Get("part.fx.bigattack"));
            if (bits.Count == 0) bits.Add(Strings.Get("part.fx.none"));
            return string.Join("; ", bits);
        }
    }
}
