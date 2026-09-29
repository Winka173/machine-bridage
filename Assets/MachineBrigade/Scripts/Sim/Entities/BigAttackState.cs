#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Where a big attack is in its cycle.</summary>
    public enum BigStage
    {
        /// <summary>Cooling down (or waiting for a target, or for a part to be patched).</summary>
        Ready,

        /// <summary>The warning: its zones shown, its parts charging; breaking them now cancels it.</summary>
        Charging,

        /// <summary>Its rounds landing, its missiles and drones in flight, its beam sweeping.</summary>
        Firing,
    }

    /// <summary>
    /// One zone of a big attack's warning, exactly its shape: a circle (<see cref="Radius"/>) or a rectangle along
    /// <see cref="Axis"/> (<see cref="HalfLength"/> by <see cref="HalfWidth"/>), landing at <see cref="Due"/>. The
    /// view draws it; units dodge the harmful ones.
    /// </summary>
    public readonly struct BigZone
    {
        public BigZone(Vector2 centre, float radius, double due, bool harmful, float pad = 0f)
        {
            Pad = pad;
            Centre = centre;
            Radius = radius;
            Axis = Vector2.UnitY;
            HalfLength = HalfWidth = 0f;
            Due = due;
            Harmful = harmful;
            Rect = false;
        }

        public BigZone(Vector2 centre, Vector2 axis, float halfLength, float halfWidth, double due, bool harmful, float pad = 0f)
        {
            Pad = pad;
            Centre = centre;
            Axis = axis;
            HalfLength = halfLength;
            HalfWidth = halfWidth;
            Radius = 0f;
            Due = due;
            Harmful = harmful;
            Rect = true;
        }

        public Vector2 Centre { get; }
        public float Radius { get; }

        /// <summary>A rectangle (a strip, a line, a sweep) rather than a circle.</summary>
        public bool Rect { get; }

        public Vector2 Axis { get; }
        public float HalfLength { get; }
        public float HalfWidth { get; }

        /// <summary>When it lands (sim seconds).</summary>
        public double Due { get; }

        public bool Harmful { get; }

        /// <summary>Metres past its edge a round landing on the edge still reaches (its blast): a dodger clears them too.</summary>
        public float Pad { get; }

        /// <summary>The same zone landing <paramref name="seconds"/> later (an EMP delayed it).</summary>
        public BigZone Later(double seconds) => Rect
            ? new BigZone(Centre, Axis, HalfLength, HalfWidth, Due + seconds, Harmful, Pad)
            : new BigZone(Centre, Radius, Due + seconds, Harmful, Pad);

        /// <summary>Whether a unit of radius <paramref name="pad"/> at <paramref name="p"/> is inside.</summary>
        public bool Contains(Vector2 p, float pad)
        {
            var d = p - Centre;
            if (!Rect) return d.LengthSquared() <= (Radius + pad) * (Radius + pad);
            var along = Vector2.Dot(d, Axis);
            var across = Vector2.Dot(d, new Vector2(Axis.Y, -Axis.X));
            return System.MathF.Abs(along) <= HalfLength + pad && System.MathF.Abs(across) <= HalfWidth + pad;
        }

        /// <summary>The nearest point <paramref name="margin"/> metres outside it from <paramref name="p"/>, and the other way out.</summary>
        public (Vector2 best, Vector2 other) Exits(Vector2 p, float margin, Vector2 fallback)
        {
            var d = p - Centre;
            if (!Rect)
            {
                var dir = d.LengthSquared() > 0.01f ? Vector2.Normalize(d) : fallback;
                return (Centre + dir * (Radius + margin), Centre - dir * (Radius + margin));
            }
            var across = new Vector2(Axis.Y, -Axis.X);
            var a = Vector2.Dot(d, Axis);
            var b = Vector2.Dot(d, across);
            var side = b >= 0f ? 1f : -1f;
            var lateral = Centre + Axis * a + across * side * (HalfWidth + margin);
            var lateralOther = Centre + Axis * a - across * side * (HalfWidth + margin);
            var end = a >= 0f ? 1f : -1f;
            var longitudinal = Centre + across * b + Axis * end * (HalfLength + margin);
            var toLateral = HalfWidth + margin - System.MathF.Abs(b);
            var toEnd = HalfLength + margin - System.MathF.Abs(a);
            return toLateral <= toEnd ? (lateral, lateralOther) : (longitudinal, lateral);
        }
    }

    /// <summary>
    /// A boss's big attack as it runs (prompt 18): its stage, its timings (sim seconds) and its warning's zones. The
    /// simulation runs it (BossSystem.BigAttacks); the boss bar, the zones and the charge glow read it.
    /// </summary>
    public sealed class BigAttackState
    {
        public BigAttackState(BigAttackDef def, IReadOnlyList<int> parts)
        {
            Def = def;
            Parts = parts;
        }

        public BigAttackDef Def { get; }

        /// <summary>The indices of the boss's parts that carry it (they flash on the bar while it charges).</summary>
        public IReadOnlyList<int> Parts { get; }

        public BigStage Stage { get; internal set; }

        /// <summary>When the next one may begin, and when the last began (the cooldown ring).</summary>
        public double Next { get; internal set; }

        public double LastStart { get; internal set; }

        /// <summary>The warning's start and when it lands.</summary>
        public double WarnStart { get; internal set; }

        public double FireAt { get; internal set; }

        /// <summary>The sim's clock at its last step (for the view's countdowns).</summary>
        public double Now { get; internal set; }

        internal readonly List<BigZone> ZoneList = new();

        public IReadOnlyList<BigZone> Zones => ZoneList;

        /// <summary>How far the cooldown has come (1: ready), or the charge while it warns.</summary>
        public float Ready => Stage != BigStage.Ready ? 1f : Next <= LastStart ? 1f : (float)System.Math.Clamp((Now - LastStart) / (Next - LastStart), 0.0, 1.0);

        /// <summary>Seconds left of the warning (0 outside it).</summary>
        public float WarnLeft => Stage == BigStage.Charging ? (float)System.Math.Max(0.0, FireAt - Now) : 0f;

        // ------------------------------------------------------------ the sim's own

        internal Vector2 Aim;
        internal Vector2 Origin;
        internal Vector2 Axis = Vector2.UnitY;
        internal Vector2 Forward = Vector2.UnitY;
        internal bool Blind;
        internal bool WasStunned;
        internal float HpAtFire;
        internal double EndsAt;
        internal double BuffUntil;
        internal float SweepDone = -1f;
        internal readonly HashSet<EntityId> Swept = new();
        internal readonly List<Vehicle> Dropped = new();
        internal int ShotDown;

        /// <summary>Rounds, drones and missiles its last firing sent (the tests count them).</summary>
        internal int Rounds;

        /// <summary>Its landing points planned with the warning (a walking barrage, a missile volley's targets).</summary>
        internal readonly List<(Vector2 at, double due)> Points = new();
    }
}
