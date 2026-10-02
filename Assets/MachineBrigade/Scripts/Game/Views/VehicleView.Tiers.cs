using UnityEngine;

namespace MachineBrigade.Game.Views
{
    public sealed partial class VehicleView
    {
        /// <summary>
        /// Prompt 34 L5: the hull rocks away from a big blast at <paramref name="from"/> (a light vehicle near a T4+ round
        /// landing), or squats back from its own shot (T3+, <paramref name="from"/> ahead of the muzzle): view only, by
        /// <paramref name="degrees"/>, dying away as a heavy hit's jolt does. Aircraft, wrecks and fixed defences do not rock.
        /// </summary>
        public void Rock(Vector3 from, float degrees)
        {
            if (degrees <= 0f || Flying || _wreck || Def.Static || Root == null) return;
            var towards = Root.InverseTransformDirection(from - Root.position);
            towards.y = 0f;
            if (towards.sqrMagnitude < 1e-4f) towards = Vector3.forward;
            towards.Normalize();
            // The top tips away from the push: a blast ahead lifts the nose, one to the right leans the hull left.
            var rock = new Vector2(-towards.z, towards.x) * Mathf.Min(degrees, 6f);
            // A bigger rock already under way is not cut short by a smaller one.
            if (Jolt().sqrMagnitude > rock.sqrMagnitude) return;
            _jolt = rock;
            _joltTime = Time.time;
        }
    }
}
