using System.Collections.Generic;
using System.Linq;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 15 E8: the icon legend, a page of its own opened from the detail page's Guide tab and from Settings:
    /// every armour icon, the armour diagram, every weapon form, the damage-type marks, the extra marks, the enemy
    /// tooltip's verdicts, and the counter table (which defence stops which damage type).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _legend;

        /// <summary>The forms in the legend's groups, penetration growing in the kinetic one.</summary>
        internal static readonly (string key, string[] forms)[] LegendGroups =
        {
            ("legend.kinetic", new[] { "BulletSmall", "BulletBig", "BeltedAutocannon", "Dart", "DoubleDart", "Rail" }),
            ("legend.shells", new[] { "HeShell", "MortarBomb", "Airburst", "Grenade", "SuperShell" }),
            ("legend.rockets", new[] { "RocketSmall", "RocketBig", "Atgm", "Sam", "Cruise", "Ballistic" }),
            ("legend.bombs", new[] { "Bomb", "GuidedBomb", "Cluster", "HeavyBomb", "Napalm" }),
            ("legend.drones", new[] { "Fpv", "Shahed", "Lancet" }),
            ("legend.other", new[] { "Flame", "Energy", "Blade", "Drill", "CarBomb" }),
        };

        /// <summary>The counter table: rows are defences, columns the six damage types; "block", "cut", "part" or empty.</summary>
        internal static readonly (string defence, string[] cells)[] CounterTable =
        {
            // Kinetic, ShapedCharge, HighExplosive, Fire, Fragmentation, Energy
            ("era", new[] { "", "cut", "", "", "", "" }),
            ("cage", new[] { "", "cut", "", "", "", "" }),
            ("aps", new[] { "", "block", "part", "", "", "" }),
            ("flares", new[] { "", "", "", "", "part", "" }),
            ("smoke", new[] { "", "", "", "", "", "block" }),
        };

        internal static readonly string[] DamageOrder = { "Kinetic", "ShapedCharge", "HighExplosive", "Fire", "Fragmentation", "Energy" };

        private void BuildLegendPage()
        {
            _legend = FullPage("fc-legend-page");
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _legend.Add(scroll);
            var body = Kit.Box("fc-page__body fc-legend");
            scroll.Add(body);

            // Armour: the three families, filling up like a battery.
            var armour = Section(body, "legend.armour");
            armour.Add(Kit.Text(Strings.Get("legend.armour.info"), "fc-body-2 fc-mb-2"));
            foreach (var kind in new[] { ArmourKind.Ground, ArmourKind.Air, ArmourKind.Structure })
            {
                var row = Kit.Box("fc-legend__grid");
                for (var level = 0; level < CombatFacts.Levels; level++)
                    row.Add(LegendItem(KitCombat.ArmourIcon(level, kind, -1, true), CombatIcons.ArmourName(level, kind)));
                armour.Add(Kit.Text(Kit.Caps(Strings.Get("legend.kind." + kind.ToString().ToLowerInvariant())), "fc-caption fc-mt-2"));
                armour.Add(row);
            }

            var faces = Section(body, "armour.faces");
            faces.Add(Kit.Text(Strings.Get("legend.faces.info"), "fc-body-2 fc-mb-2"));
            if (_catalog.Vehicles.TryGetValue("main_battle_tank", out var sample)) faces.Add(KitCombat.Diagram(sample));

            var forms = Section(body, "legend.forms");
            forms.Add(Kit.Text(Strings.Get("legend.forms.info"), "fc-body-2 fc-mb-2"));
            foreach (var (key, list) in LegendGroups)
            {
                forms.Add(Kit.Text(Kit.Caps(Strings.Get(key)), "fc-caption fc-mt-2"));
                var grid = Kit.Box("fc-legend__grid");
                foreach (var form in list)
                {
                    var icon = Kit.Icon(CombatIcons.Form(form), "fc-cicon fc-cicon--large");
                    grid.Add(LegendItem(icon, CombatIcons.FormName(form)));
                }
                forms.Add(grid);
            }

            var marks = Section(body, "legend.marks");
            marks.Add(Kit.Text(Strings.Get("legend.marks.info"), "fc-body-2 fc-mb-2"));
            var markGrid = Kit.Box("fc-legend__grid");
            foreach (var type in DamageOrder)
            {
                var mark = CombatIcons.Types[type];
                if (mark == null) continue;
                markGrid.Add(LegendItem(Kit.Icon(mark, "fc-cicon fc-cicon--large", 2f), CombatIcons.TypeName(type)));
            }
            markGrid.Add(LegendItem(Kit.Icon(CombatIcons.Thermobaric, "fc-cicon fc-cicon--large", 2f), Strings.Get("tag.thermo")));
            marks.Add(markGrid);
            marks.Add(Kit.Text(Strings.Get("legend.kineticNoMark"), "fc-small fc-mt-1"));

            var extras = Section(body, "legend.extras");
            var extraGrid = Kit.Box("fc-legend__grid");
            extraGrid.Add(LegendItem(Kit.Icon(CombatIcons.TopAttack, "fc-cicon fc-cicon--large", 2f), Strings.Get("tag.top")));
            extraGrid.Add(LegendItem(Kit.Icon(CombatIcons.Guided, "fc-cicon fc-cicon--large", 2f), Strings.Get("tag.guided")));
            extraGrid.Add(LegendItem(Kit.Icon(CombatIcons.Splash, "fc-cicon fc-cicon--large", 2f), Strings.Get("tag.splash")));
            extras.Add(extraGrid);

            var verdicts = Section(body, "legend.verdicts");
            verdicts.Add(Kit.Text(Strings.Get("legend.verdicts.info"), "fc-body-2 fc-mb-2"));
            var verdictGrid = Kit.Box("fc-legend__grid");
            foreach (var v in new[] { Verdict.Good, Verdict.Poor, Verdict.None })
            {
                var icon = KitCombat.VerdictIcon(v);
                icon.AddToClassList("fc-cicon");
                verdictGrid.Add(LegendItem(icon, CombatIcons.VerdictName(v)));
            }
            verdicts.Add(verdictGrid);

            // The counter table: which defence stops which damage type.
            var counters = Section(body, "legend.counters");
            counters.Add(Kit.Text(Strings.Get("legend.counters.info"), "fc-body-2 fc-mb-2"));
            var table = Kit.Box("fc-legend__table");
            var head = Kit.Box("fc-row fc-legend__trow");
            head.Add(Kit.Box("fc-legend__tdef"));
            foreach (var type in DamageOrder)
            {
                var cell = Kit.Box("fc-legend__tcell");
                var mark = CombatIcons.Types[type];
                cell.Add(mark != null ? Kit.Icon(mark, "fc-cicon", 2f) : Kit.Icon(CombatIcons.Form("BulletBig"), "fc-cicon"));
                cell.Add(Kit.Text(CombatIcons.TypeName(type), "fc-small fc-legend__tname"));
                head.Add(cell);
            }
            table.Add(head);
            foreach (var (defence, cells) in CounterTable)
            {
                var row = Kit.Box("fc-row fc-legend__trow");
                var name = Kit.Box("fc-legend__tdef");
                name.Add(Kit.Text(Strings.Get("defence." + defence), "fc-body fc-row-text"));
                row.Add(name);
                foreach (var c in cells)
                {
                    var cell = Kit.Box("fc-legend__tcell");
                    if (c.Length > 0) cell.Add(Kit.Text(Strings.Get("counter.cell." + c), "fc-small fc-legend__tvalue fc-legend__tvalue--" + c));
                    row.Add(cell);
                }
                table.Add(row);
            }
            counters.Add(table);
            counters.Add(Kit.Text(Strings.Get("legend.counters.note"), "fc-small fc-mt-2"));
        }

        private static VisualElement LegendItem(VisualElement icon, string words)
        {
            var item = Kit.Box("fc-legend__item");
            item.Add(icon);
            item.Add(Kit.Text(words, "fc-small fc-legend__words"));
            item.tooltip = words;
            return item;
        }

        private void OpenLegend() => Open(_legend, Strings.Get("combat.legend"));
    }
}
