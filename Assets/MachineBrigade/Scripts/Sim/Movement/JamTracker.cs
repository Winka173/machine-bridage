#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>AI MASTER spec 38 / 102: how far a jammed vehicle's recovery has escalated.</summary>
    public enum JamStage
    {
        /// <summary>Stage 0: no problem.</summary>
        None,

        /// <summary>Stage 1 (1.5 s): more separation, looser formation, a side-step.</summary>
        Soft,

        /// <summary>Stage 2 (3 s): a local waypoint 3-6 m off the line, round occupied cells (strategic target kept).</summary>
        LocalReplan,

        /// <summary>Stage 3 (5 s): with a friend in the way, the TrafficCoordinator picks who gives way.</summary>
        Yield,

        /// <summary>Stage 4 (8 s): the corridor is planned again with the jam's cells dear (a way round only under 1.5 x).</summary>
        CorridorReplan,

        /// <summary>Stage 5 (12 s): formation broken; a short reverse only where the vehicle may reverse, else pivot to another local target.</summary>
        Emergency,
    }

    /// <summary>What stage 5 does for a vehicle (spec 38): ships never reverse.</summary>
    public enum EmergencyMove
    {
        /// <summary>A short reverse (a ground vehicle that may reverse, with room behind).</summary>
        ShortReverse,

        /// <summary>Pivot and drive to another local target.</summary>
        PivotAlternate,

        /// <summary>A ship: widen the turn and take another waypoint (never reverse).</summary>
        WidenTurnAlternate,
    }

    /// <summary>
    /// AI MASTER spec 37-38 / 102: the staged jam detector of one vehicle. It counts low-progress time (slower than a
    /// quarter of the desired speed and under 0.25 m/s of route progress) while the vehicle means to move and is not
    /// engaging; time making progress drains it twice as fast. A deliberate wait (making way, queued at a choke, a doorway's
    /// turn) freezes it. The stage follows the time; each stage's action runs once per episode (<see cref="Handled"/>).
    /// Pure state: the movement system feeds it, so a test can drive it directly.
    /// </summary>
    public sealed class JamTracker
    {
        public JamStage Stage { get; private set; }
        public float LowProgressSeconds { get; private set; }

        /// <summary>The highest stage whose action has run in this episode (actions never repeat while the stage wobbles).</summary>
        public JamStage Handled { get; internal set; }

        /// <summary>When the current stage was reached (battle time).</summary>
        public double StageSince { get; private set; } = double.NegativeInfinity;

        /// <summary>Episodes begun (stage 1 reached from none) and the worst stage seen, this battle.</summary>
        public int Episodes { get; private set; }
        public JamStage Worst { get; private set; }

        /// <summary>The last stage action's reason code (JAM_*), for the debug panel.</summary>
        public string Reason { get; internal set; } = "";

        /// <summary>Waiting on purpose at the last look (the accumulator froze).</summary>
        public bool Waiting { get; private set; }

        // The movement system's last sample (position, route left to drive, and the route it measured).
        internal Vector2 SamplePos;
        internal float SampleRemaining = float.NaN;
        internal Vector2 SampleGoal;
        internal int SampleCount = -1;

        /// <summary>The stage that <paramref name="seconds"/> of low progress reach (ai.navigation.jam*S).</summary>
        public static JamStage StageFor(float seconds)
        {
            return seconds >= JamEmergency ? JamStage.Emergency :
                seconds >= JamCorridor ? JamStage.CorridorReplan :
                seconds >= JamYield ? JamStage.Yield :
                seconds >= JamReplan ? JamStage.LocalReplan :
                seconds >= JamSoft ? JamStage.Soft :
                JamStage.None;
        }

        private static float JamSoft => SimTunables.Ai.Navigation.JamSoftS;
        private static float JamReplan => SimTunables.Ai.Navigation.JamReplanS;
        private static float JamYield => SimTunables.Ai.Navigation.JamYieldS;
        private static float JamCorridor => SimTunables.Ai.Navigation.JamCorridorS;
        private static float JamEmergency => SimTunables.Ai.Navigation.JamEmergencyS;

        /// <summary>Whether a sample is low progress (spec 102: actual &lt; 25 % of desired and route progress &lt; 0.25 m/s).</summary>
        public static bool IsLow(float desiredSpeed, float actualSpeed, float progressPerSecond) =>
            actualSpeed < MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.JamTracker.IsLowDesiredSpeedFloor, desiredSpeed) * SimTunables.Ai.Navigation.JamLowSpeedShare &&
            progressPerSecond < SimTunables.Ai.Navigation.JamProgressPerSecond;

        /// <summary>
        /// One look. True when the stage rose (the caller runs that stage's action if it is above <see cref="Handled"/>).
        /// </summary>
        public bool Tick(bool moveIntent, bool engaging, bool waiting, float desiredSpeed, float actualSpeed, float progressPerSecond,
            float dt, double now)
        {
            Waiting = false;
            if (!moveIntent || engaging)
            {
                if (Stage != JamStage.None || LowProgressSeconds > 0f) Reset();
                return false;
            }
            if (waiting)
            {
                Waiting = true;
                return false;
            }
            var low = IsLow(desiredSpeed, actualSpeed, progressPerSecond);
            LowProgressSeconds = low ? LowProgressSeconds + dt : MathF.Max(0f, LowProgressSeconds - dt * SimTunables.Ai.Navigation.JamDecay);
            var stage = StageFor(LowProgressSeconds);
            var rose = stage > Stage;
            if (rose)
            {
                if (Stage == JamStage.None) Episodes++;
                StageSince = now;
                if (stage > Worst) Worst = stage;
            }
            else if (stage < Stage)
            {
                StageSince = now;
            }
            Stage = stage;
            if (Stage == JamStage.None) Handled = JamStage.None;
            return rose;
        }

        /// <summary>A new order, arrival or engagement: the episode is over.</summary>
        public void Reset()
        {
            Stage = JamStage.None;
            Handled = JamStage.None;
            LowProgressSeconds = 0f;
            StageSince = double.NegativeInfinity;
            SampleRemaining = float.NaN;
            SampleCount = -1;
            Waiting = false;
        }

        /// <summary>The reason code of a stage (Part O's JAM_* namespace).</summary>
        public static string Code(JamStage stage) => stage switch
        {
            JamStage.Soft => "JAM_SOFT",
            JamStage.LocalReplan => "JAM_LOCAL_REPLAN",
            JamStage.Yield => "JAM_YIELD",
            JamStage.CorridorReplan => "JAM_CORRIDOR_REPLAN",
            JamStage.Emergency => "JAM_EMERGENCY",
            _ => "JAM_NONE",
        };
    }

    /// <summary>
    /// AI MASTER spec 38 (stage 5), 52, 190: who may reverse. Ships never do (they widen the turn and take another waypoint);
    /// a boss, a train, a fixed defence or an aircraft does not in an unjam either (a boss's own controller decides its rare
    /// reverses, P0-C). Everything else may back up a few metres when there is room behind.
    /// </summary>
    public static class JamPolicy
    {
        public static bool AllowsReverse(Content.VehicleDef def, bool onRail) =>
            def.Naval == null && !def.Boss && !def.Static && !def.Flying && !onRail && def.Frame?.Move != BossMove.Rail;

        public static EmergencyMove Emergency(Content.VehicleDef def, bool onRail, bool roomBehind)
        {
            if (def.Naval != null) return EmergencyMove.WidenTurnAlternate;
            return AllowsReverse(def, onRail) && roomBehind ? EmergencyMove.ShortReverse : EmergencyMove.PivotAlternate;
        }
    }
}
