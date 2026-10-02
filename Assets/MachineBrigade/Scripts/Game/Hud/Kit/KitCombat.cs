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
            // Prompt 25 G: a gun of two rounds wears the ammo switch in its top corner (the card, the detail page, the rows).
            if (w.Rounds > 0)
            {
                var swap = Kit.Box("fc-wchip__swap");
                swap.Add(Kit.Icon("ammoswap", "fc-wchip__swap-icon", 2f));
                chip.Add(swap);
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
            box.Add(new ArmourDiagram(armour, ArmourDiagram.ShapeOf(def, armour.Kind)));
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
    /// The unit seen from above, front up (prompt 15 D.2): its outline, each face's part of it as thick as that face's
    /// armour, dashed for none, and its roof (a turret, a ship's superstructure, a cockpit) as thick as the roof's armour.
    /// Play-test 8 A (DECISIONS 22Q): each unit's own outline (a ship's pointed bow, sides and transom; an aircraft's nose,
    /// wings and tail; a helicopter's cabin and boom; a vehicle without a turret its hull and cab; a structure's square),
    /// no longer a tank for every unit. Colour from --icon-color.
    /// </summary>
    public sealed class ArmourDiagram : VisualElement
    {
        /// <summary>The outline drawn: whose shape the faces are marked on.</summary>
        public enum Shape
        {
            Tank,
            Hull,
            Structure,
            Ship,
            Aircraft,
            Helicopter,
        }

        private static readonly CustomStyleProperty<Color> IconColor = new("--icon-color");

        /// <summary>Border width in panel px by level: 0 dashed hairline, then 2, 4, 7, 10.</summary>
        public static readonly float[] Widths = { 1.5f, 2f, 4f, 7f, 10f, 13f };

        private readonly ArmourFaces _armour;
        private readonly Shape _shape;
        private Color _colour;

        public ArmourDiagram(ArmourFaces armour, bool structure) : this(armour, structure ? Shape.Structure : Shape.Tank) { }

        public ArmourDiagram(ArmourFaces armour, Shape shape)
        {
            _armour = armour;
            _shape = shape;
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

        /// <summary>The outline drawn for a unit.</summary>
        public Shape Outline => _shape;

        /// <summary>The unit's own outline: a ship, an aeroplane, a helicopter, a structure, a turreted vehicle or a turretless one.</summary>
        public static Shape ShapeOf(VehicleDef def, ArmourKind kind)
        {
            if (def == null) return kind == ArmourKind.Structure ? Shape.Structure : Shape.Tank;
            if (def.Naval != null) return Shape.Ship;
            if (def.Flying) return def.FixedWing ? Shape.Aircraft : Shape.Helicopter;
            if (kind == ArmourKind.Structure || def.Static) return Shape.Structure;
            return def.Mounts.Count > 0 && def.Mounts[0].Aim == MountAim.Turret ? Shape.Tank : Shape.Hull;
        }

        /// <summary>The outline's width against its height (front to rear).</summary>
        private static float Aspect(Shape shape) => shape switch
        {
            Shape.Structure => 1f,
            Shape.Ship => 0.34f,
            Shape.Aircraft => 0.95f,
            Shape.Helicopter => 0.5f,
            _ => 0.62f,
        };

        private void Draw(MeshGenerationContext context)
        {
            var r = contentRect;
            if (r.width <= 0f || r.height <= 0f) return;
            var p = context.painter2D;
            p.strokeColor = _colour;
            p.fillColor = _colour;
            p.lineCap = LineCap.Butt;
            var pad = Widths[ArmourLevels.Max] * 0.5f + 2f;
            var aspect = Aspect(_shape);
            var w = Mathf.Min(r.width - pad * 2f, (r.height - pad * 2f) * aspect);
            var h = w / aspect;
            var x0 = r.center.x - w / 2f;
            var y0 = r.center.y - h / 2f;
            // A point in the outline's own frame: u across (0 left, 1 right), v front to rear (0 front, 1 rear).
            Vector2 At(float u, float v) => new(x0 + u * w, y0 + v * h);
            switch (_shape)
            {
                case Shape.Ship:
                    // The bow comes to a point; long sides; a transom stern with bevelled corners; the superstructure
                    // amidships and a gun forward, pointing over the bow.
                    Line(p, _armour.Front, At(0f, 0.26f), At(0.5f, 0f), At(1f, 0.26f));
                    Line(p, _armour.Side, At(0f, 0.26f), At(0f, 0.92f));
                    Line(p, _armour.Side, At(1f, 0.26f), At(1f, 0.92f));
                    Line(p, _armour.Rear, At(0f, 0.92f), At(0.18f, 1f), At(0.82f, 1f), At(1f, 0.92f));
                    Roof(p, Rect(At(0.24f, 0.46f), At(0.76f, 0.72f)));
                    Gun(p, At(0.5f, 0.34f), w * 0.16f, At(0.5f, 0.12f));
                    break;

                case Shape.Aircraft:
                    // The nose; the fuselage's sides with the swept wings and the tailplane; the tail; the cockpit on the roof.
                    Line(p, _armour.Front, At(0.44f, 0.16f), At(0.5f, 0f), At(0.56f, 0.16f));
                    Line(p, _armour.Side, At(0.44f, 0.16f), At(0.44f, 0.36f), At(0f, 0.6f), At(0f, 0.68f), At(0.44f, 0.6f), At(0.44f, 0.84f),
                        At(0.24f, 0.96f));
                    Line(p, _armour.Side, At(0.56f, 0.16f), At(0.56f, 0.36f), At(1f, 0.6f), At(1f, 0.68f), At(0.56f, 0.6f), At(0.56f, 0.84f),
                        At(0.76f, 0.96f));
                    Line(p, _armour.Rear, At(0.24f, 0.96f), At(0.24f, 1f), At(0.76f, 1f), At(0.76f, 0.96f));
                    Roof(p, Ellipse(At(0.5f, 0.27f), w * 0.045f, h * 0.07f));
                    break;

                case Shape.Helicopter:
                    // The rounded nose; the cabin's sides narrowing to the tail boom; the tail's stabiliser; the rotor head on the roof.
                    Line(p, _armour.Front, Arc(At(0.5f, 0.2f), w * 0.3f, h * 0.17f));
                    Line(p, _armour.Side, At(0.2f, 0.2f), At(0.2f, 0.52f), At(0.44f, 0.64f), At(0.44f, 0.96f), At(0.2f, 0.96f));
                    Line(p, _armour.Side, At(0.8f, 0.2f), At(0.8f, 0.52f), At(0.56f, 0.64f), At(0.56f, 0.96f), At(0.8f, 0.96f));
                    Line(p, _armour.Rear, At(0.2f, 0.96f), At(0.2f, 1f), At(0.8f, 1f), At(0.8f, 0.96f));
                    Roof(p, Ellipse(At(0.5f, 0.36f), w * 0.16f, w * 0.16f));
                    Rotor(p, At(0.5f, 0.36f), w * 0.5f);
                    break;

                case Shape.Structure:
                    Line(p, _armour.Front, At(0f, 0f), At(1f, 0f));
                    Line(p, _armour.Side, At(1f, 0f), At(1f, 1f));
                    Line(p, _armour.Side, At(0f, 0f), At(0f, 1f));
                    Line(p, _armour.Rear, At(0f, 1f), At(1f, 1f));
                    Gun(p, At(0.5f, 0.5f), w * 0.24f, At(0.5f, 0f));
                    break;

                case Shape.Hull:
                    // A vehicle without a turret: its hull, and the cab (or the fighting compartment) forward on the roof.
                    Line(p, _armour.Front, At(0f, 0f), At(1f, 0f));
                    Line(p, _armour.Side, At(1f, 0f), At(1f, 1f));
                    Line(p, _armour.Side, At(0f, 0f), At(0f, 1f));
                    Line(p, _armour.Rear, At(0f, 1f), At(1f, 1f));
                    Roof(p, Rect(At(0.18f, 0.12f), At(0.82f, 0.42f)));
                    break;

                default:
                    // A turreted vehicle: the hull, the turret on the roof, the gun pointing at the front.
                    Line(p, _armour.Front, At(0f, 0f), At(1f, 0f));
                    Line(p, _armour.Side, At(1f, 0f), At(1f, 1f));
                    Line(p, _armour.Side, At(0f, 0f), At(0f, 1f));
                    Line(p, _armour.Rear, At(0f, 1f), At(1f, 1f));
                    Gun(p, At(0.5f, 0.58f), w * 0.3f, At(0.5f, -0.12f));
                    break;
            }
        }

        /// <summary>The roof's outline (a closed path), as thick as the roof's armour.</summary>
        private void Roof(Painter2D p, Vector2[] outline)
        {
            p.lineWidth = Widths[Mathf.Clamp(_armour.Top, 0, ArmourLevels.Max)] * 0.6f + 1.2f;
            p.lineCap = LineCap.Butt;
            p.BeginPath();
            p.MoveTo(outline[0]);
            for (var i = 1; i < outline.Length; i++) p.LineTo(outline[i]);
            p.ClosePath();
            p.Stroke();
        }

        /// <summary>A turret (the roof, as thick as its armour) and its gun out to <paramref name="muzzle"/>.</summary>
        private void Gun(Painter2D p, Vector2 centre, float radius, Vector2 muzzle)
        {
            p.lineWidth = Widths[Mathf.Clamp(_armour.Top, 0, ArmourLevels.Max)] * 0.6f + 1.2f;
            p.BeginPath();
            p.Arc(centre, radius, Angle.Degrees(0f), Angle.Degrees(360f));
            p.Stroke();
            p.lineWidth = 3f;
            p.lineCap = LineCap.Round;
            p.BeginPath();
            p.MoveTo(new Vector2(centre.x, centre.y - radius));
            p.LineTo(muzzle);
            p.Stroke();
            p.lineCap = LineCap.Butt;
        }

        /// <summary>A helicopter's two rotor blades, a hairline across the roof (not armour).</summary>
        private static void Rotor(Painter2D p, Vector2 centre, float reach)
        {
            p.lineWidth = 1.5f;
            p.lineCap = LineCap.Round;
            var d = new Vector2(0.72f, 0.69f) * reach;
            p.BeginPath();
            p.MoveTo(centre - d);
            p.LineTo(centre + d);
            p.MoveTo(centre + new Vector2(-d.x, d.y));
            p.LineTo(centre + new Vector2(d.x, -d.y));
            p.Stroke();
            p.lineCap = LineCap.Butt;
        }

        private static Vector2[] Rect(Vector2 a, Vector2 b) => new[] { a, new Vector2(b.x, a.y), b, new Vector2(a.x, b.y) };

        private static Vector2[] Ellipse(Vector2 centre, float rx, float ry)
        {
            var points = new Vector2[20];
            for (var i = 0; i < points.Length; i++)
            {
                var a = i * Mathf.PI * 2f / points.Length;
                points[i] = centre + new Vector2(Mathf.Cos(a) * rx, Mathf.Sin(a) * ry);
            }
            return points;
        }

        /// <summary>The front half of an ellipse, left to right over the top (a helicopter's nose).</summary>
        private static Vector2[] Arc(Vector2 centre, float rx, float ry)
        {
            var points = new Vector2[11];
            for (var i = 0; i < points.Length; i++)
            {
                var a = Mathf.PI + i * Mathf.PI / (points.Length - 1);
                points[i] = centre + new Vector2(Mathf.Cos(a) * rx, Mathf.Sin(a) * ry);
            }
            return points;
        }

        /// <summary>One face's part of the outline, as thick as its armour (dashed for none).</summary>
        private static void Line(Painter2D p, int level, params Vector2[] points)
        {
            for (var i = 1; i < points.Length; i++) Edge(p, points[i - 1], points[i], level);
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
