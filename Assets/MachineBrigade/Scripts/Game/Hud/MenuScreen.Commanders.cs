using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 22 F.4: the commander picker (a full page over the deck screen or the briefing: every commander with its
    /// portrait, call sign, strength, weakness and the deck it suits; a locked one says where it opens), the commander
    /// slot beside the deck and in the briefing, and the dossier's commander and general pages.
    /// Device checks: -mb-commanders opens the picker.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _commanderPage, _commanderBody, _deckCommander;
        private StyleSheet _commanderSheet;

        private void BuildCommanderPage()
        {
            _commanderSheet = Resources.Load<StyleSheet>("UI/Commanders");
            _commanderPage = FullPage("fc-commanders");
            if (_commanderSheet != null) _commanderPage.styleSheets.Add(_commanderSheet);
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _commanderBody = Kit.Box("fc-page__body");
            scroll.Add(_commanderBody);
            _commanderPage.Add(scroll);
            if (DebugFlags.Has("-mb-commanders")) Root.schedule.Execute(OpenCommanders).StartingIn(400);
        }

        /// <summary>Opens the picker.</summary>
        private void OpenCommanders()
        {
            Open(_commanderPage, Strings.Get("cmdr.pickTitle"));
            FillCommanders();
        }

        private void FillCommanders()
        {
            _commanderBody.Clear();
            _commanderBody.Add(Kit.Body2(Strings.Get("cmdr.sub")));
            var chosen = CommanderPick.Chosen;
            var family = (CommanderFamily)(-1);
            foreach (var c in Commanders.All)
            {
                if (c.Family != family)
                {
                    family = c.Family;
                    _commanderBody.Add(Kit.Caption(Strings.Get("cmdr.family." + family)));
                }
                var open = CommanderPick.Unlocked(c);
                var id = c.Id;
                VisualElement act = null;
                if (open && id != chosen)
                    act = new KitButton(ButtonTier.Secondary, Strings.Get("cmdr.choose"), () =>
                    {
                        if (!CommanderPick.Pick(id)) return;
                        Note(Strings.Format("cmdr.yours", ("name", CommanderText.Name(Commanders.Get(id)))));
                        FillCommanders();
                        Refresh();
                    });
                _commanderBody.Add(CommanderRow(c, !open, open && id == chosen, act));
            }
        }

        /// <summary>
        /// A commander's row: portrait, name, call sign, strength, weakness, the deck it suits (a general: its role), and
        /// where it opens while locked; <paramref name="act"/> at its end (a button), or none.
        /// </summary>
        private VisualElement CommanderRow(CommanderDef c, bool locked, bool chosen, VisualElement act)
        {
            var row = Kit.Box(KitPanel.SurfaceClass + " fc-cmdr-row" + (locked ? " fc-cmdr-row--locked" : "") + (chosen ? " fc-cmdr-row--chosen" : "") +
                              (c.IsGeneral ? " fc-cmdr-row--enemy" : ""));
            if (_commanderSheet != null) row.styleSheets.Add(_commanderSheet);
            row.Add(Portraits.Element(c.Portrait, "fc-portrait"));
            var text = Kit.Box("fc-cmdr-row__text");
            text.Add(Kit.Text(Kit.Caps(CommanderText.Name(c)), "fc-panel-title"));
            text.Add(Kit.Small(CommanderText.Call(c) + " · " + (c.IsGeneral ? CommanderText.Role(c) : Strings.Get("cmdr.family." + c.Family))));
            text.Add(Line("cmdr.strength", CommanderText.Strength(c), "fc-cmdr-row__good"));
            text.Add(Line("cmdr.weakness", CommanderText.Weakness(c), "fc-cmdr-row__bad"));
            if (!c.IsGeneral)
            {
                var tags = Kit.Box("fc-cmdr-row__tags");
                tags.Add(Tag("deck", CommanderText.Style(c)));
                if (locked) tags.Add(Tag("lock", CommanderText.Unlock(c), "fc-tag--missing"));
                else if (chosen) tags.Add(Tag("check", Strings.Get("cmdr.chosen"), "fc-tag--ok"));
                text.Add(tags);
            }
            row.Add(text);
            if (act != null)
            {
                act.AddToClassList("fc-cmdr-row__act");
                row.Add(act);
            }
            return row;
        }

        private static VisualElement Line(string label, string body, string modifier)
        {
            var line = Kit.Box("fc-cmdr-row__line " + modifier);
            line.Add(Kit.Text(Strings.Format("cmdr.line", ("label", Strings.Get(label)), ("text", body)), "fc-body-2 fc-row-text"));
            return line;
        }

        /// <summary>
        /// The commander slot beside the deck and in a mission's briefing: the commander's small portrait, name and
        /// strength, and Change (none when the mission sets its own).
        /// </summary>
        private VisualElement CommanderSlot(MissionDef mission = null)
        {
            var forced = CommanderPick.Forced(mission);
            var c = CommanderPick.ForBattle(mission);
            var slot = Kit.Box("fc-cmdr-slot");
            if (_commanderSheet != null) slot.styleSheets.Add(_commanderSheet);
            slot.Add(Portraits.Element(c.Portrait, "fc-portrait"));
            var text = Kit.Box("fc-cmdr-row__text");
            text.Add(Kit.Text(Kit.Caps(Strings.Get("cmdr.title")), "fc-caption"));
            text.Add(Kit.Text(CommanderText.Name(c) + " · " + CommanderText.Call(c), "fc-body fc-row-text"));
            text.Add(Kit.Text(forced ? Strings.Format("cmdr.forced", ("name", CommanderText.Name(c))) : CommanderText.Strength(c), "fc-small fc-row-text"));
            slot.Add(text);
            if (!forced) slot.Add(new KitButton(ButtonTier.Text, Strings.Get("cmdr.change"), OpenCommanders, "people"));
            return slot;
        }

        /// <summary>The briefing's enemy line: the general's name, its strength and weakness (none for an untied mission).</summary>
        private static string GeneralLines(MissionDef mission)
        {
            if (CommanderPick.EnemyFor(mission) is not { } g) return null;
            return Strings.Format("cmdr.line", ("label", Strings.Get("cmdr.strength")), ("text", CommanderText.Strength(g))) + "\n" +
                   Strings.Format("cmdr.line", ("label", Strings.Get("cmdr.weakness")), ("text", CommanderText.Weakness(g)));
        }

        /// <summary>The dossier's commanders tab: a page for each of the player's commanders, then each enemy general (F.4).</summary>
        private void FillCommanderFiles()
        {
            _dossierBody.Add(Kit.Caption(Strings.Get("cmdr.dossier.yours")));
            foreach (var c in Commanders.All)
            {
                var open = _dossierAll || CommanderPick.Unlocked(c);
                var page = CommanderRow(c, !open, false, null);
                var bio = Strings.Has("cmdr." + c.Id + ".bio") ? Strings.Get("cmdr." + c.Id + ".bio") : CommanderText.Role(c);
                page.Q(className: "fc-cmdr-row__text")?.Insert(2, Kit.Text(open ? bio : CommanderText.Unlock(c), "fc-body fc-row-text"));
                _dossierBody.Add(page);
            }
            _dossierBody.Add(Kit.Caption(Strings.Get("cmdr.dossier.generals")));
            foreach (var g in Commanders.Generals)
            {
                var met = _dossierAll || Met(g.General);
                var page = CommanderRow(g, !met, false, null);
                if (!met) page.Q(className: "fc-cmdr-row__text")?.Insert(2, Kit.Text(Strings.Get("cmdr.dossier.notFaced"), "fc-body-2 fc-row-text"));
                _dossierBody.Add(page);
            }
        }
    }
}
