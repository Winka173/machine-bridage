using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 14 session 5 ("Leviathan: ngủ thì giấu đi, phải có hoạt ảnh tháp súng trồi lên gì đó khi bắt đầu hoạt động"):
    /// the guns a boss wakes with a later phase (the def's <c>WakeMounts</c>: the Leviathan's secondary
    /// turrets) are hidden while they sleep, lowered into the hull, and come up when the phase wakes them: they rise out of
    /// the deck over the first part of <see cref="WakeRiseSeconds"/>, then unfold (open out to full size, ride up a touch and
    /// settle). The mount pivots' local position and scale only (their heading stays the aim's); no model edit, view only (the
    /// Sim wakes them by the same rule, <c>BossSystem</c>: phase at or past the def's wake phase).
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>How long a waking turret takes to come up and unfold (seconds).</summary>
        internal const float WakeRiseSeconds = 1.5f;

        /// <summary>The share of <see cref="WakeRiseSeconds"/> spent rising; the rest unfolds.</summary>
        private const float WakeRiseShare = 0.65f;

        /// <summary>How narrow a turret is while it is in the hull (its width against its own) before it unfolds.</summary>
        private const float WakeFolded = 0.8f;

        private Transform[] _wakePivots;
        private Vector3[] _wakeRest, _wakeScale;
        private float[] _wakeDrop;
        private float _wakeStart = -1f;
        private bool _wakeReady, _wakeDone;

        /// <summary>Hides the sleeping guns, and brings them up when their phase wakes them (call once a frame).</summary>
        private void RaiseWakeMounts()
        {
            if (_wakeDone) return;
            var awake = Def.WakePhase >= 0 && Sim.Phase >= Def.WakePhase;
            if (!_wakeReady)
            {
                SetUpWakeMounts();
                // Drawn once it is already awake (a view rebuilt mid-battle): up at once.
                if (awake) _wakeStart = Time.time - WakeRiseSeconds;
            }
            if (_wakePivots == null)
            {
                _wakeDone = true;
                return;
            }
            if (awake && _wakeStart < 0f) _wakeStart = Time.time;
            var t = _wakeStart < 0f ? 0f : Mathf.Clamp01((Time.time - _wakeStart) / WakeRiseSeconds);
            var rise = Mathf.Clamp01(t / WakeRiseShare);
            rise = 1f - (1f - rise) * (1f - rise) * (1f - rise);
            var unfold = Mathf.Clamp01((t - WakeRiseShare) / (1f - WakeRiseShare));
            var bump = Mathf.Sin(unfold * Mathf.PI);
            for (var i = 0; i < _wakePivots.Length; i++)
            {
                var pivot = _wakePivots[i];
                if (pivot == null) continue;
                var shown = t > 0f;
                if (pivot.gameObject.activeSelf != shown) pivot.gameObject.SetActive(shown);
                if (t >= 1f)
                {
                    pivot.localPosition = _wakeRest[i];
                    pivot.localScale = _wakeScale[i];
                    continue;
                }
                // Up out of the deck, a little past its seat as it unfolds, then settled.
                pivot.localPosition = _wakeRest[i] + Vector3.down * (_wakeDrop[i] * (1f - rise)) + Vector3.up * (_wakeDrop[i] * 0.06f * bump);
                var width = Mathf.Lerp(WakeFolded, 1f, Mathf.SmoothStep(0f, 1f, unfold)) * (1f + 0.04f * bump);
                pivot.localScale = Vector3.Scale(_wakeScale[i], new Vector3(width, 1f, width));
            }
            if (t >= 1f) _wakeDone = true;
        }

        /// <summary>The waking mounts' pivots (not one an awake mount fires from too), their seats and how far they sink.</summary>
        private void SetUpWakeMounts()
        {
            _wakeReady = true;
            var wake = Def.WakeMounts;
            if (wake == null || wake.Count == 0 || _mounts == null) return;
            var pivots = new List<Transform>();
            foreach (var i in wake)
            {
                if (i <= 0 || i >= _mounts.Length) continue;
                var pivot = _mounts[i];
                if (pivot == null || pivot == Root || pivot == _model.Turret || pivots.Contains(pivot)) continue;
                var shared = false;
                for (var j = 0; j < _mounts.Length && !shared; j++)
                    if (_mounts[j] == pivot && !Wakes(j)) shared = true;
                if (!shared) pivots.Add(pivot);
            }
            if (pivots.Count == 0) return;
            _wakePivots = pivots.ToArray();
            _wakeRest = new Vector3[_wakePivots.Length];
            _wakeScale = new Vector3[_wakePivots.Length];
            _wakeDrop = new float[_wakePivots.Length];
            for (var i = 0; i < _wakePivots.Length; i++)
            {
                var pivot = _wakePivots[i];
                _wakeRest[i] = pivot.localPosition;
                _wakeScale[i] = pivot.localScale;
                // Sunk until its top is at its seat (in its parent's frame): wholly inside the hull.
                var frame = pivot.parent != null ? pivot.parent : pivot;
                var top = Measure(pivot, frame).max.y;
                _wakeDrop[i] = Mathf.Max(0.3f, top - pivot.localPosition.y + 0.05f);
            }
        }

        /// <summary>Whether mount <paramref name="index"/> is one the boss wakes with a later phase.</summary>
        private bool Wakes(int index)
        {
            foreach (var i in Def.WakeMounts)
                if (i == index) return true;
            return false;
        }
    }
}
