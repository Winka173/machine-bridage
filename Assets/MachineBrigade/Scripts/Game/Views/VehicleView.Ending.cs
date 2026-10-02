using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 30 L3 (lead UI pass 2026-10-02): the match-end presentation's poses, the view's alone (the Sim is frozen from
    /// the resolve on). After a win the enemy's surviving vehicles turn away and drive (or fly) off towards the edge of the
    /// battlefield, and our turrets swing round onto the last target. Both run on the scaled clock, so the ending's slow
    /// motion slows them too, and both stop after <see cref="EndRunSeconds"/> (the results panel is up by then).
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>How long a retreating vehicle keeps going.</summary>
        private const float EndRunSeconds = 10f;

        private float _endStart = -1f, _endYaw = float.NaN, _endSpeed;
        private Vector3 _endRetreat, _endOffset, _endAim;
        private bool _endRetreating, _endAiming;

        /// <summary>Drives this vehicle off along <paramref name="direction"/> (ground plane) during the ending.</summary>
        public void EndRetreat(Vector3 direction, float now)
        {
            direction.y = 0f;
            if (direction.sqrMagnitude < 1e-4f || Def.Static) return;
            _endRetreat = direction.normalized;
            _endRetreating = true;
            _endStart = now;
            _endYaw = float.NaN;
            _endSpeed = 0f;
            _endOffset = Vector3.zero;
        }

        /// <summary>Swings this vehicle's turret onto <paramref name="target"/> during the ending.</summary>
        public void EndAim(Vector3 target, float now)
        {
            if (_model.Turret == null) return;
            _endAim = target;
            _endAiming = true;
            if (_endStart < 0f) _endStart = now;
        }

        /// <summary>Back to the sim's pose (the battle goes on: Endless).</summary>
        public void EndPoseClear()
        {
            _endStart = -1f;
            _endRetreating = _endAiming = false;
            _endOffset = Vector3.zero;
            _endYaw = float.NaN;
        }

        /// <summary>From <see cref="Render"/> after the hull is placed: the retreat's offset and heading.</summary>
        private void EndPoseHull(float hull)
        {
            if (!_endRetreating || _endStart < 0f) return;
            var t = Time.time - _endStart;
            if (float.IsNaN(_endYaw)) _endYaw = hull;
            var dt = Time.deltaTime;
            // A beat, then it turns away and picks up speed over 1.5 s.
            if (t > 0.4f && t < EndRunSeconds && dt > 0f)
            {
                var away = Mathf.Atan2(_endRetreat.x, _endRetreat.z) * Mathf.Rad2Deg;
                _endYaw = Mathf.MoveTowardsAngle(_endYaw, away, (Flying ? 70f : 110f) * dt);
                var top = Mathf.Clamp(Def.Speed, Flying ? 10f : 3f, Flying ? 40f : 14f);
                _endSpeed = Mathf.MoveTowards(_endSpeed, top, top / 1.5f * dt);
                // It moves the way it faces (a tracked hull turns before it goes).
                var facing = Quaternion.Euler(0f, _endYaw, 0f) * Vector3.forward;
                var lined = Mathf.Clamp01(Vector3.Dot(facing, _endRetreat) * 0.5f + 0.5f);
                _endOffset += facing * (_endSpeed * (Flying ? 1f : 0.35f + 0.65f * lined) * dt);
            }
            Root.position += _endOffset;
            Root.rotation = Quaternion.Euler(0f, _endYaw, 0f);
        }

        /// <summary>From <see cref="Render"/> after the turret is set: it eases round onto the ending's target.</summary>
        private void EndPoseTurret()
        {
            if (!_endAiming || _endStart < 0f || _model.Turret == null) return;
            var t = Time.time - _endStart;
            var to = _endAim - Root.position;
            to.y = 0f;
            if (to.sqrMagnitude < 1f) return;
            var bearing = Mathf.Atan2(to.x, to.z) * Mathf.Rad2Deg;
            var local = Mathf.DeltaAngle(Root.eulerAngles.y, bearing);
            var weight = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01((t - 0.2f) / 1.2f));
            var now = _model.Turret.localEulerAngles.y;
            _model.Turret.localRotation = Quaternion.Euler(0f, Mathf.LerpAngle(now, local, weight), 0f);
        }
    }
}
