using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 23 H in a battle: every character's line (the campaign's lines through <see cref="RadioDirector"/>, the
    /// Radio events of the other modes, a boss's general at a phase, the commander's first words, the reports of a broken
    /// part or an elite) goes to one <see cref="DialogueDirector"/>, which the HUD's subtitle shows. Its clock stops under
    /// the pause. A story moment slows the battle through Unity's time scale, which only changes how many fixed steps run
    /// each second: the simulation, its command journal and its replays see the same steps (H.8). Kept apart from
    /// MatchRunner.cs so the two change independently.
    /// </summary>
    public sealed partial class MatchRunner
    {
        private DialogueDirector _dialogue;
        private double _dialogueClock;

        /// <summary>
        /// The battle's dialogue (null in the menu): the event system says its lines here or through a Radio event
        /// (<see cref="DialogueRules.FromEvent"/>); a general's name label asks <see cref="DialogueDirector.IsSpeaking(string)"/> (H.9).
        /// </summary>
        internal DialogueDirector Dialogue => _dialogue;

        /// <summary>The mission's enemy general (null outside the campaign).</summary>
        private string DialogueGeneral => (_session as MissionSession)?.Def.General;

        private void StartDialogue()
        {
            if (_menu) return;
            _dialogue = new DialogueDirector { Setting = MatchSettings.Dialogue };
            _dialogue.Shown += line => _hud?.ShowLine(line);
            _dialogue.Hidden += () => _hud?.HideLine();
        }

        private void WireDialogue()
        {
            if (_hud != null && _dialogue != null) _hud.DialogueLog = () => _dialogue.Log;
        }

        /// <summary>A line for the dialogue, now.</summary>
        internal DialogueOutcome Say(in DialogueLine line) => _dialogue?.Say(line, _dialogueClock) ?? DialogueOutcome.Dropped;

        /// <summary>A line by its key: the speaker (the key's, or a prefix in its text) and side worked out, the priority the key's unless given.</summary>
        internal DialogueOutcome Say(string key, DialoguePriority? priority = null, int team = 0, bool moment = false, EntityId unit = default,
            object arg = null, string speaker = null) =>
            Say(DialogueRules.Line(key, priority, DialogueGeneral, team, moment, unit, arg, speaker));

        /// <summary>Every frame: the dialogue's clock (stopped under the pause and the result), whether a boss is on the field, the next line.</summary>
        private void TickDialogue()
        {
            if (_dialogue == null) return;
            if (!_paused && !_resultShown) _dialogueClock += Time.unscaledDeltaTime;
            if (Time.frameCount % 15 == 0) _dialogue.BossBattle = BossOnField();
            _dialogue.Tick(_dialogueClock);
        }

        /// <summary>H.8: the battle's pace while a story moment plays (1 otherwise).</summary>
        private float DialogueTimeScale => _dialogue?.TimeScale(_dialogueClock) ?? 1f;
    }
}
