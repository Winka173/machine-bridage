using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Missiles, rockets and bombs drawn as real models. Each flies for its simulated travel time,
    /// with a burning motor and a smoke trail; guided missiles bend towards their target's current
    /// position every frame, so what the player sees lands where the simulation scores the hit.
    /// A missile or rocket with a <see cref="Plume"/> burns a flame cone and leaves a lingering
    /// smoke trail from its tail (<see cref="MotorPlumes"/>); a boosted one leaves the rail slowly,
    /// speeds up hard and then cruises (<see cref="Progress"/>).
    /// </summary>
    internal sealed class ProjectilePool
    {
        private const float TrailSpacing = 0.55f;

        /// <summary>A boosted munition's speed as it leaves the rail, as a share of its cruise speed.</summary>
        internal const float RailSpeed = 0.2f;

        private sealed class Shot
        {
            public Transform Transform;
            public MeshFilter Filter;
            public MeshRenderer Renderer;
            public Vector3 From, To;

            /// <summary>The middle point of a bent path (see <see cref="Launch"/>'s control), used when Bent.</summary>
            public Vector3 Mid;
            public bool Bent;
            public Func<Vector3?> Homing;
            public float Start, Duration, Arc, Trail, PuffT, PuffStep, Wobble, Boost;
            public bool Flame, Active;

            /// <summary>The motor's flame (metres at cruise) and smoke puff size, and when it burns out (share of the flight); 0 length for none.</summary>
            public float PlumeLength, PlumeWidth, PlumeSmoke, Burn;

            /// <summary>Metres between the motor's smoke puffs on High.</summary>
            public float PuffSpacing;

            /// <summary>The model's tail along its length (local metres; negative: behind the pivot).</summary>
            public float Tail;
        }

        private readonly List<Shot> _shots = new();
        private int _next;
        private float _last = float.NaN;

        public ProjectilePool(Transform parent, int capacity)
        {
            var root = new GameObject("Projectiles").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < capacity; i++)
            {
                var go = new GameObject("Projectile");
                go.transform.SetParent(root, false);
                var shot = new Shot
                {
                    Transform = go.transform,
                    Filter = go.AddComponent<MeshFilter>(),
                    Renderer = go.AddComponent<MeshRenderer>(),
                };
                shot.Renderer.shadowCastingMode = ShadowCastingMode.Off;
                shot.Renderer.receiveShadows = false;
                go.SetActive(false);
                _shots.Add(shot);
            }
        }

        /// <param name="homing">Current aim point of a guided missile, or null once its target is gone.</param>
        /// <param name="arc">Peak height of the flight path above the straight line.</param>
        /// <param name="trail">Smoke puff size; 0 for none.</param>
        /// <param name="boost">
        /// 0: flies at one speed. Up to 1: leaves the rail slowly, speeds up hard over the first
        /// <see cref="BoostShare"/> of the flight and then cruises (a missile's launch, boost and
        /// sustainer), arriving on time.
        /// </param>
        /// <param name="scale">How big the model is drawn.</param>
        /// <param name="control">
        /// A lobbed round's path through this point instead of the plain arc (a quadratic curve
        /// from <paramref name="from"/> to <paramref name="to"/>): set along the barrel, the round
        /// leaves down its barrel and bends onto where it lands, its trail on the same curve.
        /// </param>
        /// <param name="plume">
        /// The motor's flame and smoke, in lengths of the model as drawn: with one, the flame cone
        /// burns from the model's tail and the smoke trail leaves the tip of the flame (in place of
        /// <paramref name="trail"/>'s puffs); without one, the old small motor puff where there is a trail.
        /// </param>
        public void Launch(ChunkModel model, Vector3 from, Vector3 to, float duration, float arc, float trail, float now,
            Func<Vector3?> homing = null, float wobble = 0f, float delay = 0f, float boost = 0f, float scale = 1f, Vector3? control = null,
            Plume plume = default)
        {
            // A free slot if there is one, so a missile in flight does not teleport.
            var shot = _shots[_next];
            for (var k = 0; k < _shots.Count && shot.Active; k++)
            {
                _next = (_next + 1) % _shots.Count;
                shot = _shots[_next];
            }
            _next = (_next + 1) % _shots.Count;
            shot.Filter.sharedMesh = model.Mesh;
            shot.Renderer.sharedMaterials = model.Materials;
            shot.From = from;
            shot.To = to;
            shot.Homing = homing;
            shot.Bent = control.HasValue;
            shot.Mid = control ?? Vector3.zero;
            shot.Start = now + delay;
            shot.Duration = Mathf.Max(0.05f, duration);
            shot.Arc = arc;
            shot.Trail = trail;
            shot.Wobble = wobble;
            shot.Boost = Mathf.Clamp01(boost);
            shot.Transform.localScale = Vector3.one * scale;
            var bounds = model.Mesh != null ? model.Mesh.bounds : new Bounds(Vector3.zero, Vector3.one);
            shot.Tail = bounds.min.z;
            var drawn = bounds.size.z * scale;
            shot.PlumeLength = plume.Burns ? plume.Length * drawn : 0f;
            shot.PlumeWidth = plume.Width * drawn;
            shot.PlumeSmoke = plume.Smoke * shot.PlumeWidth;
            shot.Burn = plume.Burns ? plume.Burn : 0f;
            shot.Flame = plume.Burns || trail > 0f;
            shot.PuffT = 0f;
            shot.PuffSpacing = Mathf.Max(0.15f, shot.PlumeSmoke * plume.Puffs);
            shot.PuffStep = TrailSpacing / Mathf.Max(1f, Vector3.Distance(from, to) + arc);
            shot.Active = true;
            shot.Transform.gameObject.SetActive(delay <= 0f);
            Place(shot, 0f);
        }

        public void Tick(float now, Emitters emitters)
        {
            var dt = float.IsNaN(_last) || now <= _last ? 1f / 30f : Mathf.Min(0.1f, now - _last);
            _last = now;
            var plumes = emitters.Plumes;
            plumes.Frame();
            foreach (var shot in _shots)
            {
                if (!shot.Active || now < shot.Start) continue;
                if (!shot.Transform.gameObject.activeSelf) shot.Transform.gameObject.SetActive(true);
                var t = (now - shot.Start) / shot.Duration;
                if (t >= 1f)
                {
                    shot.Active = false;
                    shot.Transform.gameObject.SetActive(false);
                    continue;
                }
                if (shot.Homing != null)
                {
                    var aim = shot.Homing();
                    if (aim.HasValue) shot.To = Vector3.Lerp(shot.To, aim.Value, 0.35f);
                }
                Place(shot, t);
                var forward = shot.Transform.forward;
                if (shot.PlumeLength > 0f)
                {
                    if (t > shot.Burn) continue;
                    var nozzle = shot.Transform.TransformPoint(new Vector3(0f, 0f, shot.Tail));
                    var speed = SpeedAt(shot.Boost, t);
                    // The flame flies with the missile, so its cone stays on the tail.
                    var velocity = (PositionAt(shot, Mathf.Min(1f, t + dt / shot.Duration)) - shot.Transform.position) / dt;
                    if (velocity.sqrMagnitude < 0.25f) velocity = forward * 0.5f;
                    plumes.Burn(nozzle, forward, velocity, shot.PlumeLength, shot.PlumeWidth, speed, dt);
                    // The smoke leaves the tip of the flame: puffs only where the flame has passed.
                    var path = Mathf.Max(1f, Vector3.Distance(shot.From, shot.To) + shot.Arc);
                    var behind = (shot.PlumeLength * 0.7f - shot.Tail * shot.Transform.localScale.z) / path;
                    var step = shot.PuffSpacing * plumes.SmokeSpacing / path;
                    while (shot.PuffT + step <= t - behind)
                    {
                        shot.PuffT += step;
                        plumes.Smoke(PositionAt(shot, shot.PuffT), -forward, shot.PlumeSmoke);
                    }
                    continue;
                }
                if (shot.Trail <= 0f) continue;
                while (shot.PuffT + shot.PuffStep <= t)
                {
                    shot.PuffT += shot.PuffStep;
                    emitters.Trail(PositionAt(shot, shot.PuffT), shot.Trail);
                }
                emitters.Motor(shot.Transform.position - forward * 0.6f, forward, shot.Trail);
            }
        }

        /// <summary>Share of the flight the boost takes, at full boost.</summary>
        internal const float BoostShare = 0.35f;

        /// <summary>
        /// How far along its path a munition is at <paramref name="t"/> (share of its flight time).
        /// Boosted: it leaves the rail at <see cref="RailSpeed"/> of its cruise speed, speeds up
        /// evenly to cruise over the first <c>boost x BoostShare</c> of the flight, then cruises,
        /// arriving at the end of its flight (the simulation's travel time).
        /// </summary>
        internal static float Progress(float boost, float t)
        {
            var tb = Mathf.Clamp01(boost) * BoostShare;
            if (tb <= 0f) return t;
            var cruise = 1f / (1f - tb * (1f - RailSpeed) * 0.5f);
            if (t >= tb) return cruise * (tb * (1f + RailSpeed) * 0.5f + (t - tb));
            return cruise * (RailSpeed * t + (1f - RailSpeed) * t * t / (2f * tb));
        }

        /// <summary>A boosted munition's speed at <paramref name="t"/> as a share of its cruise speed (1 when not boosted).</summary>
        internal static float SpeedAt(float boost, float t)
        {
            var tb = Mathf.Clamp01(boost) * BoostShare;
            return tb <= 0f || t >= tb ? 1f : RailSpeed + (1f - RailSpeed) * t / tb;
        }

        private static Vector3 PositionAt(Shot shot, float t)
        {
            t = Progress(shot.Boost, t);
            var p = shot.Bent
                ? Vector3.Lerp(Vector3.Lerp(shot.From, shot.Mid, t), Vector3.Lerp(shot.Mid, shot.To, t), t)
                : Vector3.Lerp(shot.From, shot.To, t) + Vector3.up * (shot.Arc * 4f * t * (1f - t));
            if (shot.Wobble > 0f)
            {
                // Unguided rockets corkscrew a little as they leave the tube.
                var side = Vector3.Cross(Vector3.up, (shot.To - shot.From).normalized);
                p += side * (Mathf.Sin(t * 19f + shot.Start * 7f) * shot.Wobble * (1f - t));
            }
            return p;
        }

        private static void Place(Shot shot, float t)
        {
            var here = PositionAt(shot, t);
            var ahead = PositionAt(shot, Mathf.Min(1f, t + 0.02f));
            shot.Transform.position = here;
            var direction = ahead - here;
            if (direction.sqrMagnitude < 1e-6f) direction = shot.To - shot.From;
            // Models point their nose along -Z after import (Blender -Y front arrives as Unity +Z), so look along +Z.
            if (direction.sqrMagnitude > 1e-6f) shot.Transform.rotation = Quaternion.LookRotation(direction);
        }
    }
}
