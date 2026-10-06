using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    public sealed partial class VehicleView
    {
        /// <summary>Prompt 34 L7: how a shot-down aircraft falls on its show path (WreckClass: fighter, helicopter, big aircraft).</summary>
        public enum FallStyle
        {
            /// <summary>A wing gone: it rolls hard towards it and spirals down, nose falling.</summary>
            Spiral,

            /// <summary>The tail rotor gone: it spins faster and faster as it drops.</summary>
            Spin,

            /// <summary>An engine burning and a wing gone: a long slanting fall, banking over.</summary>
            Slant,
        }

        private bool _planned;
        private Vector3 _planFrom, _planTo;
        private float _planSeconds, _planYaw, _planSide;
        private FallStyle _planStyle;

        /// <summary>
        /// Prompt 34 L7: the Sim's crash plan for this falling wreck (call after <see cref="BecomeWreck"/>): it flies a show
        /// path that reaches the ground exactly at <paramref name="at"/> after <paramref name="seconds"/> (the Sim's crash
        /// blast: DamageSystem.CrashPlan, on the loss event), in its class's way. <paramref name="side"/> is the side it
        /// lost a wing or banks to (-1 left, 1 right).
        /// </summary>
        public void PlanCrash(Vector3 at, float seconds, FallStyle style, float side)
        {
            if (!Flying || _crashStart < 0f || seconds <= 0.05f || Root == null) return;
            _planned = true;
            _planFrom = Root.position;
            _planTo = new Vector3(at.x, 0f, at.z);
            _planSeconds = seconds;
            _planStyle = style;
            _planSide = side < 0f ? -1f : 1f;
            _planYaw = Root.eulerAngles.y;
        }

        /// <summary>
        /// Prompt 34 L7: the model's node named <paramref name="name"/> (or a copy of it: a stable Part_wheel_L, a legacy
        /// name.001), null when it has none: a separable part for the wreck breakup (Part_wheel, Part_wing, Rotor, Tail_rotor ...).
        /// MVA W1-B: through <see cref="RuntimeNodes.Find"/>, so the plain name wins and no Blender suffix is needed.
        /// </summary>
        public Transform FindPart(string name) => _model?.Root == null ? null : RuntimeNodes.Find(_model.Root.transform, name);

        /// <summary>True when this wreck has a crash plan (its fall is the show path, not the free fall).</summary>
        public bool CrashPlanned => _planned;

        /// <summary>The show path at this frame; the last frame puts it on the ground at the plan's point.</summary>
        private void ShowFall()
        {
            var t = Time.time - _crashStart;
            var s = Mathf.Clamp01(t / _planSeconds);
            var flat = new Vector3(_planTo.x - _planFrom.x, 0f, _planTo.z - _planFrom.z);
            var across = flat.sqrMagnitude > 0.01f ? Vector3.Cross(Vector3.up, flat.normalized) : Root.right;
            // Carried on by its momentum, slowing: it covers most of the way early.
            var along = s * (2f - s);
            Vector3 p;
            switch (_planStyle)
            {
                case FallStyle.Spiral:
                {
                    // A tight spiral round its line down, closing to nothing at the ground; the nose drops ever steeper.
                    var r = Mathf.Min(4f, 1.2f + flat.magnitude * 0.08f) * (1f - s);
                    var a = s * Mathf.PI * 2f * 1.6f;
                    p = _planFrom + flat * along + across * (Mathf.Sin(a) * r * _planSide);
                    p.y = _planFrom.y * (1f - Mathf.Pow(s, 1.7f));
                    Root.rotation = Quaternion.Euler(0f, _planYaw + _planSide * Mathf.Rad2Deg * a * 0.25f, 0f);
                    _body.localRotation = Quaternion.Euler(Mathf.Lerp(12f, 60f, s), 0f, -_planSide * (260f * t + 160f * t * t));
                    Spin(1f);
                    break;
                }
                case FallStyle.Spin:
                    p = _planFrom + flat * along;
                    p.y = _planFrom.y * (1f - s * s);
                    // Spinning faster and faster without its tail rotor, tipping over.
                    Root.rotation = Quaternion.Euler(0f, _planYaw + _planSide * (220f * t + 260f * t * t), 0f);
                    _body.localRotation = Quaternion.Euler(Mathf.Min(26f, t * 22f), 0f, _planSide * Mathf.Min(38f, t * 30f));
                    Spin(Mathf.Clamp01(1f - t * 0.6f));
                    break;
                default:
                    // A long slanting fall: nearly straight along its line, banking over to the lost wing.
                    p = _planFrom + flat * (0.6f * s + 0.4f * along);
                    p.y = _planFrom.y * (1f - Mathf.Pow(s, 1.25f));
                    Root.rotation = Quaternion.Euler(0f, _planYaw + _planSide * 18f * s, 0f);
                    _body.localRotation = Quaternion.Euler(Mathf.Lerp(6f, 30f, s), 0f, -_planSide * Mathf.Lerp(5f, 42f, s));
                    Spin(1f);
                    break;
            }
            if (s >= 1f) p = _planTo;
            Root.position = p;
        }
    }
}
