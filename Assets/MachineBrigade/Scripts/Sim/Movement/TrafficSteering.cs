#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// AI MASTER spec 32, 34-36, 87: the pure maths of local steering: right-of-way priorities, the deterministic ORCA-lite
    /// avoidance (predict 1.5 s ahead, lateral avoidance split by priority), the passing side fixed per pair by a hash, and
    /// the dynamic minimum separation. No state, no randomness: the same inputs give the same answer on every machine.
    /// </summary>
    public static class TrafficSteering
    {
        // ------------------------------------------------------------------ spec 32: right of way

        public const int PriorityBoss = 100, PriorityInChoke = 90, PriorityHeavy = 80, PriorityNewSpawn = 75, PriorityMainEffort = 70,
            PriorityArtilleryMove = 60, PriorityCombat = 50, PriorityReinforcement = 40, PriorityScout = 30;

        // ------------------------------------------------------------------ spec 36: passing side

        /// <summary>A fixed hash of an unordered pair of ids (min, max), the same on every machine.</summary>
        public static uint PairHash(int idA, int idB)
        {
            unchecked
            {
                var lo = (uint)Math.Min(idA, idB);
                var hi = (uint)Math.Max(idA, idB);
                var h = 2166136261u;
                h = (h ^ lo) * 16777619u;
                h = (h ^ hi) * 16777619u;
                h ^= h >> 15;
                h *= 2246822519u;
                h ^= h >> 13;
                return h;
            }
        }

        /// <summary>
        /// The hand both of a pair steer to when they pass (+1: each to its own right, -1: each to its own left): fixed by
        /// the pair's hash, so the same pair always passes the same way and never wobbles left-right-left.
        /// </summary>
        public static int PassingSide(int idA, int idB) => (PairHash(idA, idB) & 1u) == 0u ? 1 : -1;

        // ------------------------------------------------------------------ spec 87: minimum separation

        /// <summary>radiusA + radiusB + 0.5 m; x1.5 under a splash threat (1.3-1.8); x0.85 in a travel column.</summary>
        public static float MinSeparation(float radiusA, float radiusB, bool splashThreat, bool travelColumn)
        {
            var d = radiusA + radiusB + SimTunables.Ai.Navigation.SeparationPad;
            if (splashThreat) d *= SimTunables.Ai.Navigation.SeparationSplash;
            if (travelColumn) d *= SimTunables.Ai.Navigation.SeparationColumn;
            return d;
        }

        // ------------------------------------------------------------------ spec 35: ORCA-lite

        /// <summary>Share of the avoidance this unit takes: lower right of way 70-100 %, higher 0-30 %, equal half.</summary>
        public static float Responsibility(int selfPriority, int otherPriority)
        {
            if (selfPriority == otherPriority) return 0.5f;
            return selfPriority < otherPriority ? SimTunables.Ai.Navigation.OrcaLowShare : SimTunables.Ai.Navigation.OrcaHighShare;
        }

        /// <summary>
        /// Whether two discs (combined radius <paramref name="combined"/>) come within it in the next <paramref name="horizon"/>
        /// seconds: <paramref name="relPos"/> = other - self, <paramref name="relVel"/> = selfVel - otherVel. Gives the time of
        /// closest approach and the miss distance then.
        /// </summary>
        public static bool WillOverlap(Vector2 relPos, Vector2 relVel, float combined, float horizon, out float time, out float miss)
        {
            var speed2 = relVel.LengthSquared();
            time = speed2 > 1e-6f ? Math.Clamp(Vector2.Dot(relPos, relVel) / speed2, 0f, horizon) : 0f;
            miss = Vector2.Distance(relPos, relVel * time);
            return miss < combined;
        }

        /// <summary>
        /// The lateral avoidance one unit takes for one neighbour: zero unless they would overlap within the horizon; then
        /// its right-hand vector (relative to its own velocity) times the pair's passing side (oncoming pairs always keep
        /// right, as the movement system's head-on rule), weighted by responsibility, urgency (sooner is stronger) and depth.
        /// </summary>
        public static Vector2 Avoid(Vector2 selfPos, Vector2 selfVel, float selfRadius, int selfPriority, int selfId,
            Vector2 otherPos, Vector2 otherVel, float otherRadius, int otherPriority, int otherId,
            float horizon, float combined, int pairSide)
        {
            var relPos = otherPos - selfPos;
            var relVel = selfVel - otherVel;
            if (!WillOverlap(relPos, relVel, combined, horizon, out var time, out var miss)) return Vector2.Zero;
            var speed = selfVel.Length();
            var forward = speed > 1e-3f ? selfVel / speed : (relPos.LengthSquared() > 1e-6f ? Vector2.Normalize(relPos) : Vector2.UnitY);
            var right = new Vector2(forward.Y, -forward.X);
            var otherSpeed = otherVel.Length();
            var oncoming = otherSpeed > 1e-3f && Vector2.Dot(forward, otherVel / otherSpeed) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.TrafficSteering.AvoidDotMax;
            var side = oncoming ? 1 : pairSide;
            var urgency = horizon > 1e-3f ? 1f - time / horizon : 1f;
            var depth = Math.Clamp((combined - miss) / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.TrafficSteering.AvoidCombinedFloor, combined), 0f, 1f);
            return right * (side * Responsibility(selfPriority, otherPriority) * MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.TrafficSteering.AvoidUrgencyFloor, urgency) * MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.TrafficSteering.AvoidDepthFloor, depth));
        }

        /// <summary>The heading change (radians, + is to the right) for a summed lateral avoidance, at most <paramref name="maxTurn"/>.</summary>
        public static float TurnFor(Vector2 avoidance, Vector2 forward, float maxTurn)
        {
            var right = new Vector2(forward.Y, -forward.X);
            var lateral = Vector2.Dot(avoidance, right);
            return Math.Clamp(lateral, -1f, 1f) * maxTurn;
        }
    }
}
