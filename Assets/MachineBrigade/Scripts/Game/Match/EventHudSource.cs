using System.Collections.Generic;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 23 F (DECISIONS 23F): what the event system tells the HUD's event markers, read by the runner a few times a
    /// second (<see cref="MatchRunner.EventHudSource"/>). A thin adapter on the game side, so the markers do not depend on
    /// the simulation's event fields; the lead fills it from 23A's names at the merge:
    /// <list type="bullet">
    /// <item><see cref="Accord"/>: <c>unit.Accord</c>.</item>
    /// <item><see cref="General"/>: <c>unit.General</c>.</item>
    /// <item><see cref="Arrows"/>: <c>EventState.Arrows</c>: direction <c>-inward</c>, <c>At</c> the point, the warning's time left.</item>
    /// <item><see cref="SideObjectives"/>: <c>EventState</c>'s side objectives (<c>SecondsLeft</c>, <c>Count</c>, <c>Needed</c>).</item>
    /// </list>
    /// </summary>
    public interface IEventHudSource
    {
        /// <summary>F.4: one of the Meridian Accord's reinforcements (the allied AI's, not the player's).</summary>
        bool Accord(Vehicle unit);

        /// <summary>F.5: the enemy general in this unit (a general's id, "varga"), or null; a def's own general needs no answer.</summary>
        string General(Vehicle unit);

        /// <summary>F.2: the directions reinforcements are coming from now, each with its warning's time left.</summary>
        void Arrows(List<EventArrow> into);

        /// <summary>F.3: the side objectives running, and those just ended (kept a moment so their outcome is seen).</summary>
        void SideObjectives(List<SideObjectiveInfo> into);
    }

    /// <summary>F.2: one direction reinforcements come from.</summary>
    public struct EventArrow
    {
        /// <summary>On the ground: x east, y north.</summary>
        public System.Numerics.Vector2 Direction;

        /// <summary>The warning's time left, in battle seconds.</summary>
        public float SecondsLeft;

        /// <summary>The enemy's (red); otherwise the Accord's (sky blue).</summary>
        public bool Enemy;

        /// <summary>Where they come in (23A: the arrow's point), or null: the minimap's arrow stands there.</summary>
        public System.Numerics.Vector2? At;
    }

    public enum SideObjectiveOutcome
    {
        Running,
        Succeeded,
        Failed,
    }

    /// <summary>F.3: a side objective as the mission bar shows it.</summary>
    public struct SideObjectiveInfo
    {
        public string Id;

        /// <summary>What to do: a text key (or a text).</summary>
        public string Text;

        /// <summary>Battle seconds left (0 or less: no clock).</summary>
        public float SecondsLeft;

        /// <summary>Done so far and needed ("2/5"); <see cref="Needed"/> 0: no count.</summary>
        public int Count, Needed;

        public SideObjectiveOutcome Outcome;
    }
}
