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
    /// </summary>
    internal sealed class ProjectilePool
    {
        private const float TrailSpacing = 0.55f;

        private sealed class Shot
        {
            public Transform Transform;
            public MeshFilter Filter;
            public MeshRenderer Renderer;
            public Vector3 From, To;
            public Func<Vector3?> Homing;
            public float Start, Duration, Arc, Trail, PuffT, PuffStep, Wobble, Boost;
            public bool Flame, Active;
        }

        private readonly List<Shot> _shots = new();
        private int _next;

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
        /// <param name="boost">0: flies at one speed. Up to 1: leaves slowly and speeds up (a missile's launch and boost), arriving on time.</param>
        /// <param name="scale">How big the model is drawn.</param>
        public void Launch(ChunkModel model, Vector3 from, Vector3 to, float duration, float arc, float trail, float now,
            Func<Vector3?> homing = null, float wobble = 0f, float delay = 0f, float boost = 0f, float scale = 1f)
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
            shot.Start = now + delay;
            shot.Duration = Mathf.Max(0.05f, duration);
            shot.Arc = arc;
            shot.Trail = trail;
            shot.Wobble = wobble;
            shot.Boost = Mathf.Clamp01(boost);
            shot.Transform.localScale = Vector3.one * scale;
            shot.Flame = trail > 0f;
            shot.PuffT = 0f;
            shot.PuffStep = TrailSpacing / Mathf.Max(1f, Vector3.Distance(from, to) + arc);
            shot.Active = true;
            shot.Transform.gameObject.SetActive(delay <= 0f);
            Place(shot, 0f);
        }

        public void Tick(float now, Emitters emitters)
        {
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
                if (shot.Trail <= 0f) continue;
                while (shot.PuffT + shot.PuffStep <= t)
                {
                    shot.PuffT += shot.PuffStep;
                    emitters.Trail(PositionAt(shot, shot.PuffT), shot.Trail);
                }
                emitters.Motor(shot.Transform.position - shot.Transform.forward * 0.6f, shot.Transform.forward, shot.Trail);
            }
        }

        private static Vector3 PositionAt(Shot shot, float t)
        {
            // A boosted missile covers its path as (1-b)t + b t^2: slow off the rail, fastest at the end.
            if (shot.Boost > 0f) t = (1f - shot.Boost) * t + shot.Boost * t * t;
            var p = Vector3.Lerp(shot.From, shot.To, t) + Vector3.up * (shot.Arc * 4f * t * (1f - t));
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
