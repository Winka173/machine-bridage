using MachineBrigade.Game.Effects;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// A vehicle's own shield (prompt 11C) in the look every shield shares: a bubble of hex tiles
    /// round its hull while a shield skill (a boss's, an elite's) or the Shield Dome item protects
    /// it, blue on our side and red-orange on the enemy's. Rounds ripple it where they strike; it
    /// flickers as a boss's shield generator is hurt and in the last second before it runs out,
    /// and shatters when it goes. Under a standing item dome of its side, the dome is its shield
    /// and the bubble is not drawn. A gear barrier (Aegis Barrier, Shared Shield) shows for a
    /// moment, fainter, as it takes a hit, and shatters when it breaks. Visual only.
    /// </summary>
    public sealed partial class VehicleView
    {
        private enum ShieldState
        {
            None,
            Shield,
            Barrier,
        }

        private ShieldVisual _shield;
        private ShieldState _shieldState;

        /// <summary>Its boss part that is a shield generator (-1: none; -2: not looked for yet).</summary>
        private int _shieldPart = -2;

        private float _shieldPartShare = 1f, _shieldSurgeUntil = -1f, _shieldEnds = -1f, _barrierSeenUntil = -1f, _lastBarrier;
        private Vector3 _toCamera = Vector3.up;

        /// <summary>It stands under a standing item dome of its side (set by the effects every frame while one stands).</summary>
        public bool ShieldCovered { get; set; }

        /// <summary>Its shield lasts <paramref name="seconds"/> from now (a skill used, an item dome over it): it flickers out at the end.</summary>
        public void ShieldFor(float seconds, float now)
        {
            if (seconds > 0f) _shieldEnds = Mathf.Max(_shieldEnds, now + seconds);
        }

        /// <summary>A round struck it at (x, z): its shield ripples there, on the side the player sees.</summary>
        public void ShieldHit(float x, float z)
        {
            if (_wreck) return;
            var now = FrameTime;
            NoteBarrierHit(now);
            if (_shield == null || !_shield.Standing) return;
            _shield.Hit(new Vector3(x, _shield.Transform.position.y, z), now, _toCamera);
        }

        /// <summary>It lost health with no point to go by (a splash, a burn): a ripple on the side facing the camera.</summary>
        public void ShieldStruck()
        {
            if (_wreck) return;
            var now = FrameTime;
            NoteBarrierHit(now);
            if (_shield == null || !_shield.Standing) return;
            _shield.Hit(_shield.Transform.position + Random.insideUnitSphere * 0.5f, now, _toCamera, 0.7f);
        }

        /// <summary>A hit on a gear barrier with no shield up: the barrier shows for a moment.</summary>
        private void NoteBarrierHit(float now)
        {
            if (!Sim.ShieldUp && Sim.Barrier > 0f) _barrierSeenUntil = now + 0.8f;
        }

        /// <summary>A bubble's three radii round a model's bounds (the model's own units, before its scale): the hull with room to spare.</summary>
        public static Vector3 ShieldRadii(Bounds bounds, float scale)
        {
            var s = Mathf.Max(0.01f, scale);
            var margin = 0.7f / s;
            var radii = new Vector3(bounds.extents.x * 1.15f + margin, bounds.extents.y * 1.2f + margin, bounds.extents.z * 1.15f + margin);
            return Vector3.Max(radii, Vector3.one * (1.4f / s));
        }

        private void AnimateShield(Quaternion cameraRotation)
        {
            var now = FrameTime;
            _toCamera = cameraRotation * Vector3.back;
            var barrier = Sim.Barrier;
            var barrierBroke = _lastBarrier > 0f && barrier <= 0f && !Sim.ShieldUp && Sim.IsAlive;
            _lastBarrier = barrier;
            var want = ShieldCovered ? ShieldState.None
                : Sim.ShieldUp ? ShieldState.Shield
                : barrier > 0f && now < _barrierSeenUntil ? ShieldState.Barrier
                : ShieldState.None;
            if (want != _shieldState)
            {
                if (want != ShieldState.None)
                {
                    _shield ??= MakeShield();
                    _shield.Intensity = want == ShieldState.Barrier ? 0.6f : 1f;
                    _shield.Raise(now, want == ShieldState.Barrier ? 0.08f : 0.4f);
                }
                else if (_shield != null && _shield.Shown)
                {
                    // Covered by a dome, or a barrier's moment over: it fades. A shield that ran
                    // out, or a barrier that broke, shatters.
                    if (ShieldCovered || (_shieldState == ShieldState.Barrier && !barrierBroke)) _shield.Lower(now);
                    else _shield.Collapse(now);
                }
                _shieldState = want;
            }
            else if (barrierBroke && !ShieldCovered)
            {
                // Broken by the blow that just landed, before it was shown: it shows and shatters.
                _shield ??= MakeShield();
                _shield.Intensity = 0.6f;
                _shield.Raise(now, 0f);
                _shield.Collapse(now);
            }
            if (_shield == null) return;
            _shield.Flicker = _shieldState == ShieldState.Shield ? ShieldFlicker(now) : 0f;
            _shield.Tick(now);
        }

        /// <summary>
        /// How much its shield flickers: as its boss's shield generator is hurt (a burst each time
        /// it is hit), and in the last second before the shield runs out.
        /// </summary>
        private float ShieldFlicker(float now)
        {
            if (_shieldPart == -2)
            {
                _shieldPart = -1;
                for (var i = 0; i < Def.Parts.Count; i++)
                    if (Def.Parts[i].Kind == "shield")
                    {
                        _shieldPart = i;
                        break;
                    }
            }
            var flicker = 0f;
            if (_shieldPart >= 0 && _shieldPart < Sim.PartCount)
            {
                var share = Sim.PartShare(_shieldPart);
                if (share < _shieldPartShare - 1e-4f) _shieldSurgeUntil = now + 0.3f;
                _shieldPartShare = share;
                flicker = (1f - share) * 0.75f;
            }
            if (now < _shieldSurgeUntil) flicker = Mathf.Max(flicker, 0.85f);
            if (_shieldEnds > now) flicker = Mathf.Max(flicker, Mathf.Clamp01(1f - (_shieldEnds - now)));
            return flicker;
        }

        private ShieldVisual MakeShield()
        {
            var radii = ShieldRadii(ModelBounds, DrawScale);
            var shield = new ShieldVisual("Shield", _body, ShieldVisual.Shape.Bubble, Mathf.Max(radii.x, radii.z) * DrawScale);
            shield.Transform.localPosition = ModelBounds.center;
            shield.Transform.localScale = radii;
            shield.SetSide(_ours);
            return shield;
        }

        private void HideShield()
        {
            _shield?.Hide();
            _shieldState = ShieldState.None;
        }
    }
}
