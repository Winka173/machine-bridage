using System;
using System.Globalization;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Field Command 2.0: the UI kit's shared builders. Every component is styled by the classes
    /// of Resources/UI/Tokens.uss (the one theme file) and sets no colour or font size in code;
    /// C# decides structure, text and state classes only. Labels wrap and are never cut with an
    /// ellipsis; every tappable element is at least a touch target (82 panel px: 72 px at the 1400 px reference, 44 pt).
    /// </summary>
    public static class Kit
    {
        /// <summary>The class every kit screen root carries: fonts, text colour and the component rules hang off it.</summary>
        public const string RootClass = "fc-root";

        /// <summary>The Large text size's class (see <see cref="MatchSettings.TextSize"/>).</summary>
        public const string LargeTextClass = "fc-text-large";

        /// <summary>Marks a documentation specimen in the kit preview (exempt from the one-primary-per-screen count).</summary>
        public const string SpecimenClass = "fc-specimen";

        /// <summary>
        /// The brief's reference width (its sizes are given at 1400 px) in panel pixels: the panel
        /// is authored at 1280 x 720 and scales with the height on phones, so a 19.5:9 phone, the
        /// class the reference describes, is 1560 panel px wide.
        /// </summary>
        public const float PanelPxPerReferencePx = 1560f / 1400f;

        /// <summary>The smallest tap target in panel pixels: 72 px at the 1400 px reference (44 pt).</summary>
        public const float TouchTarget = 72f * PanelPxPerReferencePx;

        /// <summary>A kit screen's root: the fonts, text colour and text size.</summary>
        public static VisualElement Root(string classes = null)
        {
            var root = Box(RootClass + (classes != null ? " " + classes : ""), PickingMode.Ignore);
            ApplyTextSize(root);
            return root;
        }

        /// <summary>Applies the player's text size (Settings: Normal / Large) to a kit root.</summary>
        public static void ApplyTextSize(VisualElement root) => ApplyTextSize(root, MatchSettings.LargeText);

        public static void ApplyTextSize(VisualElement root, bool large) => root.EnableInClassList(LargeTextClass, large);

        public static VisualElement Box(string classes, PickingMode picking = PickingMode.Ignore)
        {
            var element = new VisualElement { pickingMode = picking };
            UiKit.AddClasses(element, classes);
            return element;
        }

        /// <summary>A label that wraps (the kit never cuts text).</summary>
        public static Label Text(string text, string classes)
        {
            var label = new Label(text ?? "") { pickingMode = PickingMode.Ignore };
            label.AddToClassList("fc-text");
            UiKit.AddClasses(label, classes);
            return label;
        }

        public static Label Title(string text) => Text(Caps(text), "fc-title");
        public static Label PanelTitle(string text) => Text(Caps(text), "fc-panel-title");
        public static Label Body(string text) => Text(text, "fc-body");
        public static Label Body2(string text) => Text(text, "fc-body-2");
        public static Label Dim(string text) => Text(text, "fc-dim");
        public static Label Small(string text) => Text(text, "fc-small");
        public static Label Caption(string text) => Text(Caps(text), "fc-caption");
        public static Label Number(string text) => Text(text, "fc-number");

        /// <summary>A kit icon: stroke vector, coloured by the stylesheet's --icon-color (never by code).</summary>
        public static IconElement Icon(string name, string classes = null, float stroke = 1.8f)
        {
            var icon = new IconElement(name, stroke);
            // Kit icons do not carry the old HUD's "icon" class: its colour rule would win over the kit's.
            icon.RemoveFromClassList("icon");
            icon.AddToClassList("fc-icon");
            UiKit.AddClasses(icon, classes);
            return icon;
        }

        /// <summary>Anything tappable in the kit: a tap handler (see <see cref="Tap"/>) and the UI click sound.</summary>
        public static VisualElement Tappable(string classes, Action onTap)
        {
            var element = UiKit.Button(classes, onTap);
            return element;
        }

        /// <summary>Uppercase for the condensed display labels (USS has no text-transform); Vietnamese capitals keep their marks.</summary>
        public static string Caps(string text) => string.IsNullOrEmpty(text) ? text ?? "" : text.ToUpper(Culture);

        /// <summary>A count with the language's digit grouping (12,450 / 12.450).</summary>
        public static string Count(int value) => value.ToString("N0", Culture);

        private static CultureInfo Culture => Strings.Vietnamese ? Vietnamese : CultureInfo.InvariantCulture;

        private static readonly CultureInfo Vietnamese = new("vi-VN");

        /// <summary>The kit root an element belongs to (dialogs, pickers and toasts open there), else its panel's root.</summary>
        public static VisualElement HostOf(VisualElement element)
        {
            VisualElement host = null;
            for (var e = element; e != null; e = e.hierarchy.parent)
                if (e.ClassListContains(RootClass)) host = e;
            return host ?? element?.panel?.visualTree;
        }
    }

    /// <summary>The five vehicle branches of the brief, each with its colour token (never shown without the class icon).</summary>
    public enum KitBranch
    {
        Armor,
        Light,
        Artillery,
        Air,
        Support,
    }

    public static class KitBranches
    {
        public static KitBranch Of(VehicleDef def) => Gear.BranchOf(def) switch
        {
            GearBranch.Armor => KitBranch.Armor,
            GearBranch.Artillery => KitBranch.Artillery,
            GearBranch.Air => KitBranch.Air,
            _ => def.Class == UnitClass.Support ? KitBranch.Support : KitBranch.Light,
        };

        /// <summary>The class that paints an element in the branch's colour (a swatch or a bar).</summary>
        public static string ColourClass(KitBranch branch) => "fc-branch--" + branch.ToString().ToLowerInvariant();

        public static string Name(KitBranch branch) => Strings.Get("kit.branch." + branch.ToString().ToLowerInvariant());

        /// <summary>The branch's line icon (filter chips): its most typical class.</summary>
        public static string Icon(KitBranch branch) => branch switch
        {
            KitBranch.Armor => "tank",
            KitBranch.Light => "armoredcar",
            KitBranch.Artillery => "artillery",
            KitBranch.Air => "helicopter",
            _ => "repair",
        };

        /// <summary>A vehicle class's single-colour line icon, for small places (chips, the minimap, tags).</summary>
        public static string ClassIcon(UnitClass unitClass) => MenuScreen.ClassIcon(unitClass);
    }
}
