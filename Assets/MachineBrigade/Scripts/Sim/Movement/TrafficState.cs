#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// A vehicle's part in the traffic rules (see MovementSystem.Traffic): whether it is making way
    /// for someone, waiting for someone to make way, queued behind a hull it cannot pass, backing
    /// out of a narrow passage, and what it has asked of whom. Only the movement system writes it;
    /// the tactical AI reads and books firing spots through it.
    /// </summary>
    internal sealed class TrafficState
    {
        /// <summary>Since when it has stood (no route, or crawling slower than a parked hull); +inf while it drives.</summary>
        public double ParkedSince = double.PositiveInfinity;

        /// <summary>The order it had when the traffic state last looked; a new order cancels any yield or reverse.</summary>
        public Order OrderSeen;

        // ------------------------------------------------------------ requests to make way (posted one step, served the next)
        public EntityId PendingYield;
        public int PendingPriority;
        public int PendingDepth;
        public Vector2 PendingDir;

        // ------------------------------------------------------------ making way
        /// <summary>The mover it is making way for (none when it is not yielding).</summary>
        public EntityId YieldingTo;

        public Vector2 YieldOrigin;
        public Vector2 YieldSpot;
        public Vector2 YieldDir;
        public double YieldUntil = double.NegativeInfinity;
        public double YieldArrivedAt = double.PositiveInfinity;
        public double YieldCooldownUntil = double.NegativeInfinity;

        /// <summary>The order the yield interrupted, and whether it was on its way somewhere (to take it up again after).</summary>
        public Order OrderAtYield;
        public bool ResumeHadPath;

        /// <summary>How many times it has made way this battle (tests and tuning).</summary>
        public int Yields;

        // ------------------------------------------------------------ the mover's side
        public EntityId LastBlocker;
        public double LastBlockerTime = double.NegativeInfinity;

        /// <summary>The hull ahead agreed to make way: crawl behind it instead of swerving (since <see cref="WaitStarted"/>).</summary>
        public bool WaitingOnYield;
        public double WaitStarted = double.PositiveInfinity;

        /// <summary>Asked again with more weight after getting nowhere (up to twice per stretch of being stuck).</summary>
        public int YieldEscalations;
        public int TrafficBoost;

        // ------------------------------------------------------------ routing round hulls
        public double LastCostRepath = double.NegativeInfinity;

        /// <summary>A route planned round parked hulls is kept until then (hysteresis), for a goal near <see cref="CostGoal"/>.</summary>
        public double CostPathUntil = double.NegativeInfinity;
        public Vector2 CostGoal;

        /// <summary>No way round the hull ahead (a single gate): wait behind it until then instead of ramming it.</summary>
        public EntityId QueueBehind;
        public double QueueUntil = double.NegativeInfinity;

        /// <summary>Stepping off the route or out of a doorway to hold fire position (until then).</summary>
        public double OffLaneUntil = double.NegativeInfinity;

        /// <summary>Stopped short of a doorway held by traffic the other way (since <see cref="GateWaitStarted"/>).</summary>
        public bool WaitingForGate;
        public double GateWaitStarted = double.PositiveInfinity;

        /// <summary>
        /// Waiting its turn beside a doorway, off the route (0: not): which doorway (numbered by the
        /// lane map build <see cref="GateWaitBuild"/>) and which way it wants through.
        /// </summary>
        public int GateWaitId;
        public int GateWaitWay;
        public int GateWaitBuild;

        // ------------------------------------------------------------ head-on in a narrow passage
        /// <summary>Met this friend head-on in a doorway this step (resolved at the start of the next).</summary>
        public EntityId HeadOn;

        public double ReverseUntil = double.NegativeInfinity;
        public float ReverseLeft;

        /// <summary>Whom it is backing out for (none for a plain back-off when wedged).</summary>
        public EntityId ReverseFor;

        /// <summary>Backing away from an enemy (the Reverse Gearbox): the nose kept towards this point.</summary>
        public bool ReverseFacing;
        public System.Numerics.Vector2 ReverseFace;

        /// <summary>Waits where it is until then (after backing out of a doorway).</summary>
        public double HoldUntil = double.NegativeInfinity;

        public bool Reversing(double now) => now < ReverseUntil;

        // ------------------------------------------------------------ firing-spot booking (see LaneMap.Reserve)
        public bool HasReservation;
        public Vector2 ReservedAt;

        // ------------------------------------------------------------ route failures and the safety net (prompt 12)
        /// <summary>When a route search last failed for it (no way to the goal found), and to where.</summary>
        public double PathFailedAt = double.NegativeInfinity;
        public Vector2 PathFailedGoal;

        /// <summary>When the stuck rules last gave up on its route, and where it was going (its commander usually sends it again).</summary>
        public double GaveUpAt = double.NegativeInfinity;
        public Vector2 GaveUpGoal;

        /// <summary>The safety net's watch: where it last made headway and since when (see MovementSystem.Rescue).</summary>
        public Vector2 RescueAnchor;
        public double RescueSince = double.NaN;

        /// <summary>Drives through its own side's hulls until then (the safety net's first rung).</summary>
        public double GhostUntil = double.NegativeInfinity;

        /// <summary>How many times the safety net has had to step in for it (the stuck report counts them).</summary>
        public int Rescues;

        // ------------------------------------------------------------ AI MASTER P0-D + P1 (lane B): jam stages, traffic
        /// <summary>Spec 37-38: the staged jam detector.</summary>
        public readonly JamTracker Jam = new();

        /// <summary>Stuck windows in a row without progress (DetectStuck), for the give-up rule under the jam stages.</summary>
        public int NoProgressWindows;

        /// <summary>Spec 32: the right of way, held until then (2 s).</summary>
        public int RightOfWay = TrafficSteering.PriorityCombat;
        public double RightOfWayUntil = double.NegativeInfinity;

        /// <summary>The squad's right of way for its members (70 main effort, 40 reinforcement, 30 scouts; 0: none), and its task (debug).</summary>
        public int SquadPriority;
        public string TaskLabel = "";

        /// <summary>Spec 28: the shared corridor it follows (0: its own route); spec 86: driving through a passage in a column.</summary>
        public int CorridorId;
        public bool InColumn;

        /// <summary>Spec 188: the first passage on its route within the prediction window (0: none).</summary>
        public int NextPassage;

        /// <summary>Spec 95: the velocity it wanted and the one avoidance left it, and ORCA-lite's turn (kept between looks).</summary>
        public Vector2 DesiredVelocity;
        public Vector2 SafeVelocity;
        public float OrcaTurn;

        /// <summary>Stage 1: formation loosened until then; stage 5: out of its formation until then.</summary>
        public double LoosenUntil = double.NegativeInfinity;
        public double FormationBreakUntil = double.NegativeInfinity;

        /// <summary>Spec 185: when its current order came, and whether its anomaly was already logged.</summary>
        public double OrderAt = double.NegativeInfinity;
        public bool AnomalyLogged;

        /// <summary>A yield request posted by the coordinator (stage 3, deadlock, boss corridor): served even if not askable.</summary>
        public bool PendingForced;
    }
}
