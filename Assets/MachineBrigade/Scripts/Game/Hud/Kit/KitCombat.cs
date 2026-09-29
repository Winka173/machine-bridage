using System;
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 15 D-E: the armour and weapon icons as kit parts. An armour icon (the level's shield, wing or brick
    /// shield), a weapon chip (the form's icon with its damage-type mark in the corner), the card row (armour and at
    /// most two chips, "+N" for the rest), the armour diagram, the effectiveness table, the generated strong / weak
    /// lines, the five-shield cover row and the enemy tooltip's verdict marks. Sizes and colours are USS (the
    /// "prompt 15" blocks of Tokens.uss); nothing here sets a colour or a size.
    /// </summary>
    public static class KitCombat
    {
        public const string RowClass = "fc-crow";

        // ---------------------------------------------------------------- icons and chips

        public static IconElement ArmourIcon(int level, ArmourKind kind, int face = -1, bool large = false)
        {
            var icon = Kit.Icon(CombatIcons.Armour(level, kind), "fc-cicon" + (large ? " fc-cicon--large" : ""));
            icon.tooltip = CombatIcons.ArmourTip(level, kind, face);
            return icon;
        }

        /// <summary>One weapon: its form, its damage-type mark in the corner (none for kinetic), and on the detail page the extra marks after it.</summary>
        public static VisualElement Chip(WeaponFacts w, bool large = false, bool extras = false)
        {
            var chip = Kit.Box("fc-wchip" + (large ? " fc-wchip--large" : ""));
            chip.Add(Kit.Icon(CombatIcons.Form(w.Form) ?? "w_mg_heavy", "fc-wchip__form"));
            var mark = CombatIcons.Mark(w);
            if (mark != null)
            {
                var badge = Kit.Box("fc-wchip__mark");
                badge.Add(Kit.Icon(mark, "fc-wchip__mark-icon", 2f));
                chip.Add(badge);
            }
            chip.tooltip = CombatIcons.WeaponTip(w);
            if (!extras) return chip;
            var group = Kit.Box("fc-row fc-wchip-group");
            group.Add(chip);
            foreach (var x in Extras(w)) group.Add(Kit.Icon(x, "fc-xmark" + (large ? " fc-xmark--large" : "")));
            group.tooltip = chip.tooltip;
            return group;
        }

        /// <summary>The detail page's extra marks: top attack, guided, splash.</summary>
        public static IEnumerable<string> Extras(WeaponFacts w)
        {
            if (w.TopAttack) yield return CombatIcons.TopAttack;
            if (w.Guided) yield return CombatIcons.Guided;
            if (w.Splash) yield return CombatIcons.Splash;
        }

        /// <summary>
        /// A card's row (prompt 15 E1): the front armour and the first <paramref name="max"/> weapons, main first, "+N"
        /// for the rest. A card with no weapon shows the armour alone; <paramref name="def"/> null gives an empty row of
        /// the same height, so the cards of a row keep lining up.
        /// </summary>
        public static VisualElement Row(VehicleDef def, int max = 2, string classes = null)
        {
            var row = Kit.Box(RowClass + (classes != null ? " " + classes : ""));
            if (def == null) return row;
            var armour = CombatFacts.Armour(def);
            row.Add(ArmourIcon(armour.Front, armour.Kind, armour.Uniform ? -1 : 0));
            var weapons = CombatFacts.Weapons(def);
            for (var i = 0; i < weapons.Count && i < max; i++) row.Add(Chip(weapons[i]));
            if (weapons.Count > max) row.Add(Kit.Text("+" + (weapons.Count - max), "fc-small fc-crow__more"));
            row.tooltip = RowTip(def);
            return row;
        }

        /// <summary>The row in words, for a tooltip: every weapon, not just the two shown.</summary>
        public static string RowTip(VehicleDef def)
        {
            var armour = CombatFacts.Armour(def);
            var lines = new List<string> { CombatIcons.ArmourTip(armour.Front, armour.Kind, armour.Uniform ? -1 : 0) };
            lines.AddRange(CombatFacts.Weapons(def).Select(w => CombatIcons.WeaponTip(w)));
            return string.Join("\n", lines);
        }

        /// <summary>A tap on <paramref name="target"/> (a full touch target) shows a tooltip in words.</summary>
        public static void TapTip(VisualElement target, Func<string> title, Func<string> text)
        {
            target.pickingMode = PickingMode.Position;
            target.AddManipulator(new Tap(() => KitDialog.Present(target, KitTooltip.Build(title?.Invoke(), text()))));
        }

        // ---------------------------------------------------------------- the detail page

        /// <summary>
        /// The armour by face (E2): the unit seen from above with each face's border as thick as its armour, and a
        /// legend of the four faces with their shields and words. Aircraft and structures whose faces are all alike get
        /// the one icon and "the same on every face".
        /// </summary>
        public static VisualElement Diagram(VehicleDef def)
        {
            var armour = CombatFacts.Armour(def);
            var box = Kit.Box("fc-armour");
            if (armour.Uniform)
            {
                var one = Kit.Box("fc-row fc-armour__line");
                one.Add(ArmourIcon(armour.Front, armour.Kind, -1, true));
                var words = Kit.Box("fc-armour__words");
                words.Add(Kit.Text(CombatIcons.ArmourName(armour.Front, armour.Kind), "fc-body"));
                words.Add(Kit.Text(Strings.Get("armour.faces.same"), "fc-small"));
                one.Add(words);
                box.Add(one);
                return box;
            }
            box.Add(new ArmourDiagram(armour, armour.Kind == ArmourKind.Structure));
            var legend = Kit.Box("fc-armour__legend");
            for (var face = 0; face < 4; face++)
            {
                var line = Kit.Box("fc-row fc-armour__line");
                line.Add(ArmourIcon(armour[face], armour.Kind, face));
                line.Add(Kit.Text(Kit.Caps(Strings.Get("armour.face." + face)) + " · " + CombatIcons.ArmourName(armour[face], armour.Kind), "fc-body fc-row-text"));
                legend.Add(line);
            }
            box.Add(legend);
            return box;
        }

        /// <summary>The columns of the effectiveness table (the sim's <see cref="EffectColumn"/>): armour 0-5 on the ground (5: a boss's plate), aircraft, structures.</summary>
        public static readonly (int level, ArmourKind kind)[] Columns =
        {
            (0, ArmourKind.Ground), (1, ArmourKind.Ground), (2, ArmourKind.Ground), (3, ArmourKind.Ground), (4, ArmourKind.Ground), (5, ArmourKind.Ground),
            (Matchup.AirLevel, ArmourKind.Air), (Matchup.StructureLevel, ArmourKind.Structure),
        };

        private static IconElement ColumnIcon(int column) => ArmourIcon(Columns[column].level, Columns[column].kind);

        /// <summary>
        /// The effectiveness table (E2), made from the data: the shields (and the air and structure icons) head the
        /// columns, each weapon is a row, each cell a bar as long as its real multiplier against that column; with the
        /// numbers on, the cell says it.
        /// </summary>
        public static VisualElement EffectTable(IReadOnlyList<WeaponFacts> weapons)
        {
            var table = Kit.Box("fc-effect");
            var head = Kit.Box("fc-row fc-effect__row fc-effect__head");
            head.Add(Kit.Box("fc-effect__weapon"));
            for (var c = 0; c < Columns.Length; c++)
            {
                var cell = Kit.Box("fc-effect__cell");
                cell.Add(ColumnIcon(c));
                head.Add(cell);
            }
            table.Add(head);
            var scale = 1f;
            foreach (var w in weapons)
                for (var c = 0; c < Columns.Length; c++)
                    scale = Mathf.Max(scale, CombatFacts.Effect(w, (EffectColumn)c));
            foreach (var w in weapons)
            {
                var row = Kit.Box("fc-row fc-effect__row");
                var weapon = Kit.Box("fc-effect__weapon");
                weapon.Add(Chip(w));
                row.Add(weapon);
                for (var c = 0; c < Columns.Length; c++)
                {
                    var (level, kind) = Columns[c];
                    var m = CombatFacts.Effect(w, (EffectColumn)c);
                    var cell = Kit.Box("fc-effect__cell");
                    var track = Kit.Box("fc-effect__track");
                    var bar = Kit.Box("fc-effect__bar");
                    bar.style.width = Length.Percent(Mathf.Clamp01(m / scale) * 100f);
                    track.Add(bar);
                    cell.Add(track);
                    if (MatchSettings.ShowCombatNumbers) cell.Add(Kit.Text(CombatIcons.Times(m), "fc-small fc-effect__num"));
                    cell.tooltip = CombatIcons.WeaponTip(w, false) + "\n" + CombatIcons.ArmourName(level, kind) + " · " +
                                   CombatIcons.VerdictName(CombatFacts.Judge(m));
                    row.Add(cell);
                }
                table.Add(row);
            }
            return table;
        }

        /// <summary>
        /// "Mạnh với / Yếu trước" made from the data (E2): the armour levels and kinds the unit's weapons pierce well,
        /// and the weapon forms (from the whole roster) that pierce this unit's front well, plus top attack when its roof
        /// is thinner.
        /// </summary>
        public static VisualElement StrongWeak(VehicleDef def)
        {
            var box = Kit.Box("fc-strongweak");
            var summary = CombatFacts.Summary(def);
            var strong = Kit.Box("fc-row fc-strongweak__line");
            strong.Add(Kit.Text(Strings.Get("combat.strong"), "fc-body fc-strongweak__label"));
            foreach (var column in summary.StrongVs) strong.Add(ColumnIcon((int)column));
            if (summary.StrongVs.Count == 0) strong.Add(Kit.Text(Strings.Get("combat.nothing"), "fc-body-2 fc-row-text"));
            box.Add(strong);

            var weak = Kit.Box("fc-row fc-strongweak__line");
            weak.Add(Kit.Text(Strings.Get("combat.weak"), "fc-body fc-strongweak__label"));
            foreach (var threat in summary.WeakTo)
            {
                var chip = threat == Threat.TopAttack ? Kit.Icon(CombatIcons.TopAttack, "fc-xmark fc-xmark--large") : Chip(CombatFacts.ThreatChip(threat));
                chip.tooltip = Strings.Get("threat." + threat);
                weak.Add(chip);
            }
            if (summary.WeakTo.Count == 0) weak.Add(Kit.Text(Strings.Get("combat.nothing"), "fc-body-2 fc-row-text"));
            box.Add(weak);
            box.tooltip = Strings.Get("combat.strongweak.tip");
            return box;
        }

        /// <summary>The strong / weak lines in words, for the tap tooltip.</summary>
        public static string StrongWeakTip(VehicleDef def)
        {
            var summary = CombatFacts.Summary(def);
            var strong = summary.StrongVs.Select(c => CombatIcons.ArmourName(Columns[(int)c].level, Columns[(int)c].kind)).ToList();
            var weak = summary.WeakTo.Select(t => Strings.Get("threat." + t)).ToList();
            return Strings.Get("combat.strong") + ": " + (strong.Count > 0 ? string.Join(", ", strong) : Strings.Get("combat.nothing")) + "\n" +
                   Strings.Get("combat.weak") + ": " + (weak.Count > 0 ? string.Join(", ", weak) : Strings.Get("combat.nothing")) + "\n" +
                   Strings.Get("combat.strongweak.tip");
        }

        // ---------------------------------------------------------------- cover and verdicts

        /// <summary>
        /// The five shields of a cover row (E7): lit where <paramref name="covered"/> says the deck or base has a weapon
        /// that pierces that level well, dimmed, struck through and in the warning colour where it has none.
        /// </summary>
        public static VisualElement CoverShields(Func<int, bool> covered, string tipKey)
        {
            var row = Kit.Box("fc-row fc-cover");
            // A deck's cover is against the levels units have (0-4): only bosses carry level 5, and nothing is meant to pierce it well.
            for (var level = 0; level <= ArmourLevels.MaxUnit; level++)
            {
                var has = covered(level);
                var cell = Kit.Box("fc-cover__cell" + (has ? "" : " fc-cover__cell--missing"));
                cell.Add(ArmourIcon(level, ArmourKind.Ground));
                if (!has) cell.Add(Kit.Box("fc-cover__strike"));
                cell.tooltip = CombatIcons.ArmourName(level, ArmourKind.Ground) + " · " + Strings.Get(has ? tipKey + ".has" : tipKey + ".missing");
                row.Add(cell);
            }
            return row;
        }

        /// <summary>Whether any of <paramref name="defs"/>' weapons pierces ground armour <paramref name="level"/> well.</summary>
        public static bool Covers(IEnumerable<VehicleDef> defs, int level) =>
            defs.Any(d => CombatFacts.Weapons(d).Any(w => CombatFacts.Effect(w, (EffectColumn)level) >= CombatFacts.GoodFrom));

        public static IconElement VerdictIcon(Verdict v)
        {
            var icon = Kit.Icon(CombatIcons.Verdict(v), "fc-verdict fc-verdict--" + v.ToString().ToLowerInvariant(), 2.4f);
            icon.tooltip = CombatIcons.VerdictName(v);
            return icon;
        }

        /// <summary>
        /// The enemy tooltip (E5): the enemy's front armour, its name, then each vehicle of our deck with ✓ ~ ✕ by its
        /// main weapon against that front.
        /// </summary>
        public static VisualElement EnemyTip(VehicleDef enemy, IEnumerable<VehicleDef> deck, AltitudeTier tier = AltitudeTier.None)
        {
            var tip = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-enemytip");
            var armour = CombatFacts.Armour(enemy);
            var head = Kit.Box("fc-row fc-enemytip__head");
            head.Add(ArmourIcon(armour.Front, armour.Kind, armour.Uniform ? -1 : 0));
            head.Add(Kit.Text(Strings.Short(enemy.Id), "fc-body fc-row-text"));
            // Prompt 19 B.5: at altitude, ✓ its main weapon reaches the tier, ~ only another of its weapons, ✕ none.
            if (tier != AltitudeTier.None)
                head.Add(Kit.Text("· " + Strings.Get("tier." + tier.ToString().ToLowerInvariant()) + " · " + Strings.Get("hud.tier.reach"), "fc-small fc-row-text"));
            tip.Add(head);
            var grid = Kit.Box("fc-enemytip__grid");
            var reached = 0;
            foreach (var mine in deck)
            {
                var v = tier == AltitudeTier.None ? CombatFacts.Judge(mine, enemy) : TierRules.Verdict(mine, tier) switch
                {
                    2 => Verdict.Good,
                    1 => Verdict.Poor,
                    _ => Verdict.None,
                };
                if (v != Verdict.None) reached++;
                var cell = Kit.Box("fc-row fc-enemytip__cell");
                cell.Add(VerdictIcon(v));
                var name = Strings.Short(mine.Id);
                if (MatchSettings.ShowCombatNumbers) name += " " + CombatIcons.Times(CombatFacts.Against(mine, enemy));
                cell.Add(Kit.Text(name, "fc-small fc-row-text"));
                cell.tooltip = tier != AltitudeTier.None && v == Verdict.Poor ? Strings.Get("hud.tier.partial") : CombatIcons.VerdictName(v);
                grid.Add(cell);
            }
            tip.Add(grid);
            if (tier != AltitudeTier.None && reached == 0) tip.Add(Kit.Text(Strings.Get("hud.tier.none"), "fc-small"));
            return tip;
        }
    }

    /// <summary>
    /// The unit seen from above, front up (prompt 15 D.2): a hull (or a structure's square) whose four borders are as
    /// thick as each face's armour, dashed for none, with the gun pointing at the front. Colour from --icon-color.
    /// </summary>
    public sealed class ArmourDiagram : VisualElement
    {
        private static readonly CustomStyleProperty<Color> IconColor = new("--icon-color");

        /// <summary>Border width in panel px by level: 0 dashed hairline, then 2, 4, 7, 10.</summary>
        public static readonly float[] Widths = { 1.5f, 2f, 4f, 7f, 10f, 13f };

        private readonly ArmourFaces _armour;
        private readonly bool _structure;
        private Color _colour;

        public ArmourDiagram(ArmourFaces armour, bool structure)
        {
            _armour = armour;
            _structure = structure;
            AddToClassList("fc-armour__diagram");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                if (e.customStyle.TryGetValue(IconColor, out var c)) _colour = c;
                MarkDirtyRepaint();
            });
            tooltip = string.Join("\n", Enumerable.Range(0, 4).Select(f => CombatIcons.ArmourTip(armour[f], armour.Kind, f)));
        }

        private void Draw(MeshGenerationContext context)
        {
            var r = contentRect;
            if (r.width <= 0f || r.height <= 0f) return;
            var p = context.painter2D;
            p.strokeColor = _colour;
            p.fillColor = _colour;
            p.lineCap = LineCap.Butt;
            var pad = Widths[ArmourLevels.Max] * 0.5f + 2f;
            var w = _structure ? Mathf.Min(r.width, r.height) - pad * 2f : Mathf.Min(r.width - pad * 2f, (r.height - pad * 2f) * 0.62f);
            var h = _structure ? w : w / 0.62f;
            var x0 = r.center.x - w / 2f;
            var y0 = r.center.y - h / 2f;
            var x1 = x0 + w;
            var y1 = y0 + h;
            Edge(p, new Vector2(x0, y0), new Vector2(x1, y0), _armour.Front);
            Edge(p, new Vector2(x1, y0), new Vector2(x1, y1), _armour.Side);
            Edge(p, new Vector2(x0, y0), new Vector2(x0, y1), _armour.Side);
            Edge(p, new Vector2(x0, y1), new Vector2(x1, y1), _armour.Rear);
            // The roof: the turret (or the structure's gun mount) drawn as thick as the roof's armour.
            var c = new Vector2(r.center.x, r.center.y + (_structure ? 0f : h * 0.08f));
            var radius = w * (_structure ? 0.24f : 0.3f);
            p.lineWidth = ArmourDiagram.Widths[Mathf.Clamp(_armour.Top, 0, ArmourLevels.Max)] * 0.6f + 1.2f;
            p.BeginPath();
            p.Arc(c, radius, Angle.Degrees(0f), Angle.Degrees(360f));
            p.Stroke();
            p.lineWidth = 3f;
            p.lineCap = LineCap.Round;
            p.BeginPath();
            p.MoveTo(new Vector2(c.x, c.y - radius));
            p.LineTo(new Vector2(c.x, y0 - (_structure ? 0f : h * 0.12f)));
            p.Stroke();
        }

        private static void Edge(Painter2D p, Vector2 a, Vector2 b, int level)
        {
            level = Mathf.Clamp(level, 0, ArmourLevels.Max);
            p.lineWidth = Widths[level];
            if (level > 0)
            {
                p.BeginPath();
                p.MoveTo(a);
                p.LineTo(b);
                p.Stroke();
                return;
            }
            var length = Vector2.Distance(a, b);
            var dir = (b - a) / length;
            for (var d = 0f; d < length; d += 9f)
            {
                p.BeginPath();
                p.MoveTo(a + dir * d);
                p.LineTo(a + dir * Mathf.Min(length, d + 5f));
                p.Stroke();
            }
        }
    }
}
