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
