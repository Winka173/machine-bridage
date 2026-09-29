using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 8 A (DECISIONS 22Q): an aircraft whose loan is up (the fire support's sky gunship, an escort) no longer
    /// vanishes where it was. It rolls out of its turn and flies straight on the way it was going, opening the throttle
    /// and climbing, propellers and rotors still turning, until it is well past the edge of the map; then the view is
    /// removed. The sim has already let it go (no wreck, no kill, nothing fires at it): this is the view's alone.
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>How long a departing aircraft is flown before its view is removed (it is far off the map by then).</summary>
        public const float DepartSeconds = 10f;

        private float _departStart = -1f, _departSpeed, _departBank;
        private Vector3 _departHeading;

        /// <summary>Starts flying the aircraft off (its heading the way it was moving, else the way it faces).</summary>
        public void Depart(float now)
        {
            var velocity = (_currentPosition - _previousPosition) * 20f;
            velocity.y = 0f;
            var facing = Root.forward;
            facing.y = 0f;
            _departHeading = velocity.sqrMagnitude > 1f ? velocity.normalized : facing.sqrMagnitude > 1e-4f ? facing.normalized : Vector3.forward;
            _departSpeed = Mathf.Max(10f, Def.Speed, velocity.magnitude);
            _departBank = _bank;
            _departStart = now;
        }

        /// <summary>One frame of the departure; false once it is over (the caller removes the view).</summary>
        public bool Departing(float now, float dt)
        {
            if (_departStart < 0f || Root == null) return false;
            var t = now - _departStart;
            if (t >= DepartSeconds) return false;
            // Full throttle over three seconds, a steady climb, and out of the bank it was holding in its orbit.
            var speed = _departSpeed * (1f + 0.7f * Mathf.Clamp01(t / 3f));
            Root.position += (_departHeading * speed + Vector3.up * 2.5f) * dt;
            Root.rotation = Quaternion.RotateTowards(Root.rotation, Quaternion.LookRotation(_departHeading, Vector3.up), 40f * dt);
            _departBank = Mathf.MoveTowards(_departBank, 0f, 20f * dt);
            _body.localRotation = Quaternion.Euler(-4f * Mathf.Clamp01(t / 2f), 0f, _departBank);
            Spin(1f);
            return true;
        }
    }
}
