#nullable enable
using System;
using System.Numerics;

namespace MachineBrigade.Sim.Core
{
    /// <summary>
    /// Ground-plane math shared by the simulation. The plane is (X, Y) where Y maps to the
    /// engine's world Z. Headings are radians measured from +Y towards +X, which matches a
    /// Unity yaw rotation, so views can use <c>heading * Rad2Deg</c> directly.
    /// </summary>
    public static class SimMath
    {
        public const float Tau = MathF.PI * 2f;

        public static float HeadingOf(Vector2 direction) => MathF.Atan2(direction.X, direction.Y);

        public static Vector2 Forward(float heading) => new Vector2(MathF.Sin(heading), MathF.Cos(heading));

        /// <summary>Wraps an angle into (-PI, PI].</summary>
        public static float WrapAngle(float angle)
        {
            angle %= Tau;
            if (angle > MathF.PI) angle -= Tau;
            else if (angle <= -MathF.PI) angle += Tau;
            return angle;
        }

        /// <summary>Turns <paramref name="current"/> towards <paramref name="target"/> by at most <paramref name="maxStep"/>.</summary>
        public static float RotateTowards(float current, float target, float maxStep)
        {
            var delta = WrapAngle(target - current);
            if (MathF.Abs(delta) <= maxStep) return WrapAngle(target);
            return WrapAngle(current + MathF.Sign(delta) * maxStep);
        }

        public static float MoveTowards(float current, float target, float maxStep)
        {
            if (MathF.Abs(target - current) <= maxStep) return target;
            return current + MathF.Sign(target - current) * maxStep;
        }

        public static bool IsFinite(Vector2 v) => float.IsFinite(v.X) && float.IsFinite(v.Y);

        public static float Clamp01(float v) => v < 0f ? 0f : v > 1f ? 1f : v;

        public static float DegToRad(float degrees) => degrees * (MathF.PI / 180f);
    }
}
