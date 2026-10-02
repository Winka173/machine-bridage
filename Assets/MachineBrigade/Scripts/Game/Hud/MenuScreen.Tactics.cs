using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 28 H.4, H.11, H.12, H.14: the tactic beside the deck and the commander. The slot shows the tactic the next
    /// battle starts with (the last one picked for that mode, else one that suits the commander); Change opens the
    /// picker: each tactic's core behaviour, when it is strong and weak, what it buys first, its force mix, what it
    /// counters and what counters it, the 1-2 that suit the commander first, and where a locked one opens.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _tacticPage, _tacticBody;
        private GameModeKind _tacticMode;
        private CommanderDef _tacticCommander;
        private MissionDef _tacticMission;

        private void BuildTacticPage()
        {
            _tacticPage = FullPage("fc-commanders");
            if (_commanderSheet != null) _tacticPage.styleSheets.Add(_commanderSheet);
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _tacticBody = Kit.Box("fc-page__body");
            scroll.Add(_tacticBody);
            _tacticPage.Add(scroll);
        }

        /// <summary>The tactic slot beside the commander's: the deck screen (the menu's mode) and a mission's briefing (the campaign).</summary>
        private VisualElement TacticSlot(MissionDef mission = null)
        {
            var mode = mission != null ? GameModeKind.Campaign : MatchSettings.Mode;
            var commander = CommanderPick.ForBattle(mission);
            var data = _catalog.AiData;
            var t = data.Tactic(TacticPick.For(_catalog, mode, commander));
            var slot = Kit.Box("fc-cmdr-slot fc-mt-2");
            if (_commanderSheet != null) slot.styleSheets.Add(_commanderSheet);
            slot.Add(Kit.Icon("flag", "fc-tactic-icon"));
            var text = Kit.Box("fc-cmdr-row__text");
            text.Add(Kit.Text(Kit.Caps(Strings.Get("tactic.title")), "fc-caption"));
            text.Add(Kit.Text(TacticText.Name(t), "fc-body fc-row-text"));
            text.Add(Kit.Text(TacticText.Core(t), "fc-small fc-row-text"));
            slot.Add(text);
            slot.Add(new KitButton(ButtonTier.Text, Strings.Get("tactic.pickTitle"), () => OpenTactics(mode, commander, mission), "flag"));
            return slot;
        }

        private void OpenTactics(GameModeKind mode, CommanderDef commander, MissionDef mission = null)
        {
            _tacticMode = mode;
            _tacticCommander = commander;
            _tacticMission = mission;
            Open(_tacticPage, Strings.Get("tactic.pickTitle"));
            FillTactics();
        }

        private void FillTactics()
        {
            _tacticBody.Clear();
            var data = _catalog.AiData;
            var chosen = data.Tactic(TacticPick.For(_catalog, _tacticMode, _tacticCommander)).Id;
            var suited = TacticPick.Suited(_catalog, _tacticCommander);
            var suitedIds = new HashSet<string>();
            foreach (var s in suited) suitedIds.Add(s.Id);
            // H.12: the ones that suit the commander first, then every tactic in the sheet's order.
            if (suited.Count > 0)
            {
                _tacticBody.Add(Kit.Caption(Strings.Get("tactic.suits") + (_tacticCommander != null ? " · " + CommanderText.Name(_tacticCommander) : "")));
                foreach (var t in suited) _tacticBody.Add(TacticRow(t, chosen, true));
            }
            _tacticBody.Add(Kit.Caption(Strings.Get("tactic.title")));
            foreach (var t in TacticPick.Choices(_catalog))
                if (!suitedIds.Contains(t.Id)) _tacticBody.Add(TacticRow(t, chosen, false));
        }

        private VisualElement TacticRow(TacticDef t, string chosen, bool suited)
        {
            var data = _catalog.AiData;
            var locked = !TacticPick.Unlocked(t);
            // Prompt 28 appendix: a tactic the mode's AI profile forbids is greyed out (the battle would fall back to another).
            var barred = !locked && !TacticPick.ModeAllows(_catalog, _tacticMode, _tacticMission, t.Id);
            var isChosen = t.Id == chosen;
            var row = Kit.Box(KitPanel.SurfaceClass + " fc-cmdr-row" + (locked || barred ? " fc-cmdr-row--locked" : "") + (isChosen ? " fc-cmdr-row--chosen" : ""));
            if (_commanderSheet != null) row.styleSheets.Add(_commanderSheet);
            row.Add(Kit.Icon("flag", "fc-tactic-icon"));
            var text = Kit.Box("fc-cmdr-row__text");
            text.Add(Kit.Text(Kit.Caps(TacticText.Name(t)), "fc-panel-title"));
            text.Add(Kit.Text(TacticText.Core(t), "fc-body-2"));
            text.Add(Line("tactic.strong", TacticText.Strong(t), "fc-cmdr-row__good"));
            text.Add(Line("tactic.weak", TacticText.Weak(t), "fc-cmdr-row__bad"));
            if (t.Prefer.Count > 0)
            {
                var buys = new List<string>();
                foreach (var id in t.Prefer)
                    if (buys.Count < 4) buys.Add(Strings.Card(id));
                text.Add(Kit.Text(Strings.Format("cmdr.line", ("label", Strings.Get("tactic.buys")), ("text", string.Join(", ", buys))), "fc-small fc-row-text fc-mt-1"));
            }
            text.Add(Kit.Text(Strings.Format("cmdr.line", ("label", Strings.Get("tactic.mix")), ("text", MixLine(t))), "fc-small fc-row-text"));
            text.Add(Kit.Text(TacticText.Counters(data, t) + "  ·  " + TacticText.CounteredBy(data, t), "fc-small fc-row-text"));
            var tags = Kit.Box("fc-cmdr-row__tags");
            if (suited) tags.Add(Tag("star", Strings.Get("tactic.suits"), "fc-tag--ok"));
            if (locked) tags.Add(Tag("lock", TacticText.Unlock(t), "fc-tag--missing"));
            else if (barred) tags.Add(Tag("lock", Strings.Get("tactic.notInMode"), "fc-tag--missing"));
            else if (isChosen) tags.Add(Tag("check", Strings.Get("cmdr.chosen"), "fc-tag--ok"));
            if (tags.childCount > 0) text.Add(tags);
            row.Add(text);
            if (!locked && !barred && !isChosen)
            {
                var id = t.Id;
                var act = new KitButton(ButtonTier.Secondary, Strings.Get("cmdr.choose"), () =>
                {
                    TacticPick.Pick(_tacticMode, id);
                    Note(Strings.Format("cmdr.line", ("label", Strings.Get("tactic.title")), ("text", TacticText.Name(t))));
                    FillTactics();
                    Refresh();
                });
                act.AddToClassList("fc-cmdr-row__act");
                row.Add(act);
            }
            return row;
        }

        /// <summary>H.5: the tactic's CP shares, biggest first ("Tanks, heavy 30% · Light, IFVs 20% ...").</summary>
        private static string MixLine(TacticDef t)
        {
            var groups = new List<int>();
            for (var i = 0; i < t.Cp.Length; i++)
                if (t.Cp[i] > 0.001f) groups.Add(i);
            groups.Sort((a, b) => t.Cp[b].CompareTo(t.Cp[a]));
            var parts = new List<string>();
            foreach (var g in groups)
                parts.Add(Strings.Get("tactic.group." + (ForceGroup)g) + " " + UnityEngine.Mathf.RoundToInt(t.Cp[g] * 100f) + "%");
            return parts.Count > 0 ? string.Join(" · ", parts) : "-";
        }

        /// <summary>H.7: the enemy general's favourite tactic, for the briefing.</summary>
        private string GeneralTacticLine(MissionDef mission)
        {
            if (mission?.General == null) return null;
            var data = _catalog.AiData;
            return Strings.Format("tactic.general", ("tactic", TacticText.Name(data.Tactic(data.GeneralTactic(mission.General)))));
        }
    }
}
