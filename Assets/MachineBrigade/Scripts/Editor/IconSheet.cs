// Needs the UI Toolkit test framework package (com.unity.ui.test-framework), like UiShots.
#if MB_UI_TEST_FRAMEWORK
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UIElements;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// The tower and structure line icons (prompt 14 I, <see cref="TowerIcons"/>) on the kit's dark
    /// panel: each at 20, 24 and 48 panel px with its name and what it stands for, the vehicle class
    /// icons above for the stroke and style. Rendered through <see cref="UiShots.Shoot"/> at the
    /// 1280 x 720 reference, so a panel pixel is an image pixel, into Docs/ui-screens/kit-tower-icons.png.
    /// Batch mode with graphics: -executeMethod MachineBrigade.Editor.IconSheet.Towers [-mbShotsDir &lt;folder&gt;].
    /// </summary>
    public static class IconSheet
    {
        [MenuItem("Machine Brigade/Tower Icon Sheet")]
        public static void Towers()
        {
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[IconSheet] needs a graphics device: run the batch without -nographics.");
                return;
            }
            var catalog = GameContent.LoadCatalog();
            var was = Strings.Vietnamese;
            Strings.Vietnamese = false;
            try
            {
                var folder = UiShots.OutputFolder();
                Directory.CreateDirectory(folder);
                var path = Path.Combine(folder, "kit-tower-icons.png");
                File.WriteAllBytes(path, UiShots.Shoot((out Action<Vector4> insets) =>
                {
                    insets = null;
                    return Build(catalog);
                }, new UiShots.Shape("sheet", 1280, 720), false));
                Debug.Log("[IconSheet] wrote " + path);
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        /// <summary>
        /// Prompt 15 D: the armour and weapon icon set at its smallest size (34 panel px, 18.7 pt: the card rows, the
        /// chips, the HUD), each with its Vietnamese words, and sample chips with their corner marks. Written at 16:9
        /// (kit-combat-icons.png, 1920 x 1080) and on the smallest screen, 1280 x 720, one panel pixel an image pixel
        /// (kit-combat-icons-small.png). Batch with graphics: -executeMethod MachineBrigade.Editor.IconSheet.Combat.
        /// </summary>
        [MenuItem("Machine Brigade/Combat Icon Sheet")]
        public static void Combat()
        {
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[IconSheet] needs a graphics device: run the batch without -nographics.");
                return;
            }
            var was = Strings.Vietnamese;
            Strings.Vietnamese = true;
            try
            {
                var folder = UiShots.OutputFolder();
                Directory.CreateDirectory(folder);
                foreach (var (file, shape) in new[] { ("kit-combat-icons.png", new UiShots.Shape("sheet", 1920, 1080)), ("kit-combat-icons-small.png", new UiShots.Shape("sheet-small", 1280, 720)) })
                {
                    var path = Path.Combine(folder, file);
                    File.WriteAllBytes(path, UiShots.Shoot((out Action<Vector4> insets) =>
                    {
                        insets = null;
                        return BuildCombat();
                    }, shape, false));
                    Debug.Log("[IconSheet] wrote " + path);
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        private static VisualElement BuildCombat()
        {
            var root = Kit.Root("fc-screen");
            root.style.paddingLeft = root.style.paddingRight = 24;
            root.style.paddingTop = root.style.paddingBottom = 12;
            root.Add(Kit.Title("Biểu tượng giáp và vũ khí · cỡ nhỏ nhất 18,7 pt"));
            var grid = Kit.Box("");
            grid.style.flexDirection = FlexDirection.Row;
            grid.style.flexWrap = Wrap.Wrap;
            grid.style.marginTop = 6;
            root.Add(grid);

            void Group(string title)
            {
                var cell = Cell();
                cell.Add(Kit.Text(Kit.Caps(title), "fc-caption"));
                grid.Add(cell);
            }

            void Item(VisualElement icon, string words)
            {
                var cell = Cell();
                icon.style.marginRight = 8;
                cell.Add(icon);
                var label = Kit.Text(words, "fc-small");
                label.style.flexShrink = 1;
                cell.Add(label);
                grid.Add(cell);
            }

            IconElement Small(string name, float stroke = 1.8f) => Kit.Icon(name, "fc-cicon", stroke);

            foreach (var kind in new[] { ArmourKind.Ground, ArmourKind.Air, ArmourKind.Structure })
            {
                Group(Strings.Get("legend.kind." + kind.ToString().ToLowerInvariant()));
                for (var level = 0; level < CombatFacts.Levels; level++) Item(Small(CombatIcons.Armour(level, kind)), Strings.Get("armour.level." + level));
            }
            foreach (var (key, forms) in MenuScreen.LegendGroups)
            {
                Group(Strings.Get(key));
                foreach (var form in forms) Item(Small(CombatIcons.Form(form)), CombatIcons.FormName(form));
            }
            Group(Strings.Get("legend.marks"));
            foreach (var type in MenuScreen.DamageOrder)
                if (CombatIcons.Types[type] is { } mark)
                    Item(Small(mark, 2f), CombatIcons.TypeName(type));
            Item(Small(CombatIcons.Thermobaric, 2f), Strings.Get("tag.thermo"));
            Group(Strings.Get("legend.extras").Split('(')[0].Trim());
            Item(Small(CombatIcons.TopAttack, 2f), Strings.Get("tag.top"));
            Item(Small(CombatIcons.Guided, 2f), Strings.Get("tag.guided"));
            Item(Small(CombatIcons.Splash, 2f), Strings.Get("tag.splash"));
            foreach (var v in new[] { Verdict.Good, Verdict.Poor, Verdict.None })
            {
                var icon = KitCombat.VerdictIcon(v);
                icon.AddToClassList("fc-cicon");
                Item(icon, CombatIcons.VerdictName(v));
            }
            Group("Chip");
            foreach (var (form, damage, thermo) in new[]
                     {
                         ("DoubleDart", "Kinetic", false), ("Atgm", "ShapedCharge", false), ("HeShell", "HighExplosive", false), ("RocketBig", "HighExplosive", true),
                         ("Airburst", "Fragmentation", false), ("Flame", "Fire", false), ("Energy", "Energy", false),
                     })
            {
                var w = new WeaponFacts { Form = form, Damage = damage, Thermobaric = thermo };
                Item(KitCombat.Chip(w), CombatIcons.FormName(form));
            }
            return root;
        }

        private static VisualElement Cell()
        {
            var cell = Kit.Box("");
            cell.style.flexDirection = FlexDirection.Row;
            cell.style.alignItems = Align.Center;
            cell.style.width = 154;
            cell.style.height = 54;
            cell.style.paddingRight = 4;
            return cell;
        }

        /// <summary>The structures in sheet order (the HQ, towers by size, modules, the other fixed defences), one entry an icon.</summary>
        private static List<(string icon, List<string> ids)> Groups(Catalog catalog)
        {
            static int Order(VehicleDef v) => v.Fort == null ? 3 : v.Fort.Kind switch { FortKind.Hq => 0, FortKind.Tower => 1, _ => 2 };
            var groups = new List<(string icon, List<string> ids)>();
            foreach (var v in catalog.Vehicles.Values.Where(v => v.BranchOf == null && (v.Fort != null || v.Static))
                         .OrderBy(Order).ThenBy(v => v.Fort?.Size ?? SlotSize.Large).ThenBy(v => v.Id, StringComparer.Ordinal))
            {
                var icon = TowerIcons.For(v.Id) ?? "module";
                var at = groups.FindIndex(g => g.icon == icon);
                if (at < 0) groups.Add((icon, new List<string> { v.Id }));
                else groups[at].ids.Add(v.Id);
            }
            return groups;
        }

        private static IconElement Icon(string name, float size)
        {
            var icon = Kit.Icon(name);
            icon.style.width = icon.style.height = size;
            return icon;
        }

        private static VisualElement Build(Catalog catalog)
        {
            var root = Kit.Root("fc-screen");
            root.style.paddingLeft = root.style.paddingRight = 24;
            root.style.paddingTop = root.style.paddingBottom = 16;
            root.Add(Kit.Title("Tower and structure icons"));

            var reference = Kit.Box("fc-surface fc-panel");
            reference.style.flexDirection = FlexDirection.Row;
            reference.style.alignItems = Align.Center;
            reference.style.marginTop = 8;
            reference.style.paddingLeft = reference.style.paddingRight = 12;
            reference.style.paddingTop = reference.style.paddingBottom = 6;
            reference.Add(Kit.Text("Vehicle class icons, for comparison", "fc-small"));
            foreach (var icon in Enum.GetValues(typeof(UnitClass)).Cast<UnitClass>().Select(MenuScreen.ClassIcon).Distinct())
            {
                var mark = Icon(icon, 24);
                mark.style.marginLeft = 14;
                reference.Add(mark);
            }
            root.Add(reference);

            var panel = Kit.Box("fc-surface fc-panel");
            panel.style.flexDirection = FlexDirection.Row;
            panel.style.flexWrap = Wrap.Wrap;
            panel.style.marginTop = 8;
            panel.style.paddingLeft = panel.style.paddingRight = 8;
            panel.style.paddingTop = panel.style.paddingBottom = 6;
            foreach (var (icon, ids) in Groups(catalog))
            {
                var cell = Kit.Box("");
                cell.style.flexDirection = FlexDirection.Row;
                cell.style.alignItems = Align.Center;
                cell.style.width = 302;
                cell.style.height = 78;
                cell.style.paddingLeft = 6;
                var small = Icon(icon, 20);
                small.style.marginRight = 8;
                cell.Add(small);
                var chip = Icon(icon, 24);
                chip.style.marginRight = 8;
                cell.Add(chip);
                cell.Add(Icon(icon, 48));
                var text = Kit.Box("");
                text.style.marginLeft = 8;
                text.style.flexShrink = 1;
                text.Add(Kit.Text(icon, "fc-body"));
                text.Add(Kit.Text(string.Join(", ", ids.Select(Strings.Card)), "fc-small"));
                cell.Add(text);
                panel.Add(cell);
            }
            root.Add(panel);
            return root;
        }
    }
}
#endif
