using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21B): a boss's file, the boss wiki's facts read from the data: its rank, the chapters it
    /// is fought in, its general, its numbers (no equipment, no level: a boss is no card), its parts with their armour
    /// and health, its big attack and its escorts. The menu's boss page (the detail page of a boss) is built from it,
    /// and the Sandbox, which runs in a battle with no menu, shows the same file in a dialog. On prompt 10's kit.
    /// </summary>
    internal static class BossFile
    {
        public static string Rank(VehicleDef boss) =>
            Strings.Get(boss.RankDef?.Label ?? (boss.MiniBoss ? "boss.rank.mini" : "boss.rank.main"));

        /// <summary>The chapters switched on that fight it (their main or a mini slot).</summary>
        public static List<int> Chapters(VehicleDef boss) =>
            Campaign.Chapters.Where(c => Campaign.ChapterEnabled(c.Number) && (c.Main == boss.Id || c.Minis.Contains(boss.Id))).Select(c => c.Number).ToList();

        /// <summary>The rank and chapter tags, and the general's portrait, name and call sign.</summary>
        public static void Head(VisualElement into, VehicleDef boss)
        {
            var head = Kit.Box("fc-row fc-row--wrap");
            head.Add(Tag(boss.MiniBoss ? "elite" : "skull", Rank(boss)));
            var chapters = Chapters(boss);
            if (chapters.Count > 0) head.Add(Tag("campaign", Strings.Format("guide.boss.chapters", string.Join(", ", chapters.Select(Campaign.ChapterShort)))));
            into.Add(head);
            if (boss.General is not { } general || !Strings.Has($"char.{general}.name")) return;
            var row = Kit.Box("fc-row fc-mt-2");
            row.Add(Portraits.Element(general, "fc-portrait"));
            var text = Kit.Box("fc-dossier__text");
            text.Add(Kit.Text(Kit.Caps(Strings.Format("guide.boss.general", Strings.Get($"char.{general}.name"))), "fc-panel-title"));
            if (Strings.Has($"char.{general}.role")) text.Add(Kit.Caption(Strings.Get($"char.{general}.role")));
            row.Add(text);
            into.Add(row);
        }

        /// <summary>Its numbers as they are in a battle at campaign strength, and its armour on each face.</summary>
        public static void Numbers(VisualElement into, Catalog catalog, VehicleDef boss)
        {
            into.Add(Caption("guide.boss.numbers"));
            foreach (var stat in UnitStats.For(catalog, boss, VehicleBoost.None))
                into.Add(Line(Strings.Get(stat.Key) + ": " + Strings.Num(stat.Value, stat.Format)));
            into.Add(Line(Armour(boss.Armour)));
        }

        public static string Armour(ArmourLevels a) =>
            Strings.Format("guide.boss.armour", ("front", a.Front), ("side", a.Side), ("rear", a.Rear), ("top", a.Top));

        /// <summary>A part's armour and health ("armour 3 · 1,200 health").</summary>
        public static string PartStats(VehicleDef boss, BossPartDef part) =>
            Strings.Format("guide.boss.partStats", ("armour", part.ArmourOn(boss)), ("hp", Strings.Num((int)part.Hp)));

        /// <summary>Each kind of part once, with how many, its armour and health.</summary>
        public static void Parts(VisualElement into, VehicleDef boss)
        {
            if (boss.Parts.Count == 0) return;
            into.Add(Caption("guide.parts"));
            foreach (var group in boss.Parts.GroupBy(p => (p.Kind, p.ArmourOn(boss), p.Hp)))
            {
                var name = Strings.Get("part." + group.Key.Kind);
                var count = group.Count();
                into.Add(Line((count > 1 ? name + " ×" + count : name) + " · " + PartStats(boss, group.First())));
            }
        }

        /// <summary>Its big attack: the name and its numbers.</summary>
        public static void BigAttack(VisualElement into, VehicleDef boss)
        {
            if (boss.BigAttack is not { } big) return;
            into.Add(Caption("guide.bigattack"));
            into.Add(Line(Strings.Get(big.NameKey) + " · " + MenuScreen.BigAttackStats(big)));
        }

        /// <summary>Who comes with it: the wave that arrives with it, and the waves at its phase changes.</summary>
        public static void Escorts(VisualElement into, Catalog catalog, VehicleDef boss)
        {
            into.Add(Caption("guide.boss.escorts"));
            if (!catalog.Escorts.TryGetValue(boss.Id, out var escorts) || escorts.Arrive == null && escorts.Phases.Count == 0)
            {
                into.Add(Line(Strings.Get("guide.boss.escorts.none")));
                return;
            }
            if (escorts.Arrive is { } arrive && arrive.Units.Count > 0) into.Add(Line(Strings.Format("guide.boss.escorts.arrive", Units(arrive))));
            if (escorts.Phases.Count > 0) into.Add(Line(Strings.Format("guide.boss.escorts.phases", escorts.Phases.Count)));
        }

        /// <summary>A wave's units by name, each once with how many ("Light tank ×2, Anti-air vehicle").</summary>
        private static string Units(EscortWaveDef wave) =>
            string.Join(", ", wave.Units.GroupBy(u => u.Unit).Select(g => g.Count() > 1 ? Strings.Short(g.Key) + " ×" + g.Count() : Strings.Short(g.Key)));

        /// <summary>The whole file on one card: for the Sandbox, where no menu page can open.</summary>
        public static VisualElement Card(Catalog catalog, VehicleDef boss, System.Action close)
        {
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog fc-boss-file", PickingMode.Position);
            card.Add(Kit.Text(Kit.Caps(Strings.Card(boss.Id)), "fc-panel-title fc-dialog__title"));
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-boss-file__scroll");
            Head(scroll, boss);
            Numbers(scroll, catalog, boss);
            Parts(scroll, boss);
            BigAttack(scroll, boss);
            Escorts(scroll, catalog, boss);
            card.Add(scroll);
            var buttons = Kit.Box("fc-dialog__buttons");
            buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("guide.boss.close"), close, "close"));
            card.Add(buttons);
            return card;
        }

        /// <summary>Opens <see cref="Card"/> over the screen <paramref name="anchor"/> is on.</summary>
        public static VisualElement Show(VisualElement anchor, Catalog catalog, VehicleDef boss)
        {
            VisualElement scrim = null;
            scrim = KitDialog.Present(anchor, Card(catalog, boss, () => scrim?.RemoveFromHierarchy()));
            return scrim;
        }

        private static VisualElement Caption(string key) => Kit.Text(Kit.Caps(Strings.Get(key)), "fc-caption fc-mt-4");

        private static VisualElement Line(string text) => Kit.Text(text, "fc-body fc-mt-2");

        private static VisualElement Tag(string icon, string text)
        {
            var tag = Kit.Box("fc-tag");
            if (icon != null) tag.Add(Kit.Icon(icon));
            tag.Add(Kit.Text(text, "fc-small"));
            return tag;
        }
    }
}
