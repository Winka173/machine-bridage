using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// What fire support looks like: red telegraphs on the ground, the strike jet screaming over
    /// with bombs falling from it, the cruise missile diving in, smoke clouds and repair sparkle.
    /// Impacts themselves are explosions played by <see cref="EffectsDirector"/>.
    /// </summary>
    internal sealed class StrikeEffects
    {
        private const float JetAltitude = 24f;
        private const float BombFall = 0.8f;

        private sealed class Telegraph
        {
            public Transform Ring;
            public Transform Line;
            public float Start, End, Radius;
            public bool Active;
        }

        private sealed class Jet
        {
            public GameObject Root;
            public Vector3 From, To;
            public float Start, Duration, NextPuff;
            public bool Active;
        }

        private readonly Catalog _catalog;
        private readonly ModelLibrary _models;
        private readonly Emitters _emitters;
        private readonly ProjectilePool _projectiles;
        private readonly List<Telegraph> _telegraphs = new();
        private readonly List<Jet> _jets = new();
        private readonly List<(float at, Vector3 from, Vector3 to)> _bombs = new();
        private readonly List<(ParticleSystem system, float until)> _smoke = new();
        private readonly Transform _root;
        private readonly MaterialLibrary _materials;
        private readonly bool _hasJet, _hasBomb, _hasCruise;

        public StrikeEffects(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Emitters emitters,
            ProjectilePool projectiles, Transform parent)
        {
            _catalog = catalog;
            _materials = materials;
            _models = models;
            _emitters = emitters;
            _projectiles = projectiles;
            _root = new GameObject("Strikes").transform;
            _root.SetParent(parent, false);
            _hasJet = models.Has("strike_jet");
            _hasBomb = models.Has("bomb");
            _hasCruise = models.Has("cruise_missile");

            for (var i = 0; i < 6; i++)
            {
                var t = new Telegraph
                {
                    Ring = VehicleView.CreateMesh("Strike Ring", _root, meshes.ThinRing, materials.StrikeWarning, false),
                    Line = VehicleView.CreateMesh("Strike Line", _root, meshes.Quad, materials.StrikeWarning, false),
                };
                t.Ring.gameObject.SetActive(false);
                t.Line.gameObject.SetActive(false);
                _telegraphs.Add(t);
            }
        }

        public void Consume(in SimEvent e, float now)
        {
            if (e.DefId == null && e.Kind != SimEventKind.SmokeDeployed) return;
            switch (e.Kind)
            {
                case SimEventKind.StrikeWarning:
                    if (!_catalog.TryGetSupport(e.DefId, out var support)) return;
                    ShowTelegraph(support, Ground(e.Position), Ground(e.Target), now, e.Value);
                    if (support.Kind == SupportKind.Airstrike) ScheduleBombs(support, Ground(e.Position), Ground(e.Target), now + e.Value);
                    break;

                case SimEventKind.AircraftPass:
                    if (!_catalog.TryGetSupport(e.DefId, out var pass)) return;
                    if (pass.Kind == SupportKind.CruiseMissile) LaunchCruise(e, now);
                    else LaunchJet(e, now);
                    break;

                case SimEventKind.SmokeDeployed:
                    SpawnSmoke(Ground(e.Position), e.Value, e.Target.X, now);
                    break;
            }
        }

        public void Tick(float now)
        {
            foreach (var t in _telegraphs)
            {
                if (!t.Active) continue;
                if (now >= t.End)
                {
                    t.Active = false;
                    t.Ring.gameObject.SetActive(false);
                    t.Line.gameObject.SetActive(false);
                    continue;
                }
                // Pulse faster as the impact nears.
                var left = t.End - now;
                var pulse = 1f + 0.08f * Mathf.Sin(now * Mathf.Lerp(18f, 6f, Mathf.Clamp01(left / 3f)));
                t.Ring.localScale = Vector3.one * t.Radius * pulse;
            }

            foreach (var jet in _jets)
            {
                if (!jet.Active) continue;
                var k = (now - jet.Start) / jet.Duration;
                if (k >= 1f)
                {
                    jet.Active = false;
                    jet.Root.SetActive(false);
                    continue;
                }
                var p = Vector3.Lerp(jet.From, jet.To, k);
                jet.Root.transform.position = p;
                jet.Root.transform.rotation = Quaternion.LookRotation(jet.To - jet.From) * Quaternion.Euler(0f, 0f, Mathf.Sin(k * 6f) * 6f);
                if (now >= jet.NextPuff)
                {
                    jet.NextPuff = now + 0.03f;
                    var right = jet.Root.transform.right;
                    _emitters.Trail(p + right * 4.5f - jet.Root.transform.forward * 2f, 0.45f);
                    _emitters.Trail(p - right * 4.5f - jet.Root.transform.forward * 2f, 0.45f);
                    _emitters.Motor(p - jet.Root.transform.forward * 5.5f, jet.Root.transform.forward, 1.6f);
                }
            }

            for (var i = _bombs.Count - 1; i >= 0; i--)
            {
                var (at, from, to) = _bombs[i];
                if (now < at) continue;
                _bombs.RemoveAt(i);
                if (_hasBomb) _projectiles.Launch(_models.Merged("bomb"), from, to, BombFall, 0f, 0f, now);
            }

            for (var i = _smoke.Count - 1; i >= 0; i--)
            {
                var (system, until) = _smoke[i];
                if (now < until) continue;
                var emission = system.emission;
                emission.enabled = false;
                if (now > until + 6f)
                {
                    Object.Destroy(system.gameObject);
                    _smoke.RemoveAt(i);
                }
            }
        }

        private void ShowTelegraph(SupportDef support, Vector3 point, Vector3 end, float now, float delay)
        {
            var t = _telegraphs.Find(x => !x.Active) ?? _telegraphs[0];
            t.Active = true;
            t.Start = now;
            t.End = now + delay + (support.Kind is SupportKind.Barrage or SupportKind.Airstrike ? support.Duration : 0.2f);
            if (support.IsLine)
            {
                var direction = end - point;
                var mid = (point + end) * 0.5f;
                t.Line.gameObject.SetActive(true);
                t.Line.position = mid + Vector3.up * 0.12f;
                t.Line.rotation = Quaternion.LookRotation(Vector3.down, direction.normalized);
                t.Line.localScale = new Vector3(support.Radius * 2f + 2f, direction.magnitude, 1f);
                t.Radius = support.Radius + 1f;
                t.Ring.gameObject.SetActive(false);
            }
            else
            {
                t.Radius = support.Radius;
                t.Ring.gameObject.SetActive(true);
                t.Ring.position = point + Vector3.up * 0.12f;
                t.Ring.localScale = Vector3.one * support.Radius;
                t.Line.gameObject.SetActive(false);
            }
        }

        private void ScheduleBombs(SupportDef support, Vector3 start, Vector3 end, float firstImpact)
        {
            var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
            for (var i = 0; i < support.Count; i++)
            {
                var along = support.Count > 1 ? i / (float)(support.Count - 1) : 0.5f;
                var target = Vector3.Lerp(start, end, along);
                var release = target - (end - start).normalized * 14f + Vector3.up * JetAltitude;
                _bombs.Add((firstImpact + i * interval - BombFall, release, target));
            }
        }

        private void LaunchJet(in SimEvent e, float now)
        {
            if (!_hasJet) return;
            var jet = _jets.Find(j => !j.Active);
            if (jet == null)
            {
                jet = new Jet { Root = _models.Spawn("strike_jet", e.Team, _root).Root };
                _jets.Add(jet);
            }
            jet.Root.SetActive(true);
            jet.From = Ground(e.Position) + Vector3.up * JetAltitude;
            jet.To = Ground(e.Target) + Vector3.up * JetAltitude;
            jet.Start = now;
            jet.Duration = Mathf.Max(0.5f, e.Value);
            jet.NextPuff = now;
            jet.Active = true;
        }

        private void LaunchCruise(in SimEvent e, float now)
        {
            var from = Ground(e.Position) + Vector3.up * 40f;
            var to = Ground(e.Target);
            if (_hasCruise) _projectiles.Launch(_models.Merged("cruise_missile"), from, to, e.Value, 4f, 1.2f, now);
        }

        private void SpawnSmoke(Vector3 at, float radius, float seconds, float now)
        {
            var ps = PB.Create(_root, "Smoke Screen", _materials.Smoke);
            ps.transform.position = at;
            var main = ps.main;
            main.loop = true;
            main.duration = 2f;
            main.maxParticles = 220;
            PB.Basics(ps, new Vector2(5f, 8f), new Vector2(0.2f, 0.8f), new Vector2(5f, 8f));
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = radius * 0.8f;
            shape.rotation = new Vector3(90f, 0f, 0f);
            PB.Colors(ps, PB.Plume(0.72f, 0.82f, 0.75f));
            PB.Grow(ps, 0.6f, 1.6f);
            PB.Rise(ps, 0.2f, 0.6f);
            var emission = ps.emission;
            emission.enabled = true;
            emission.rateOverTime = 26f;
            ps.Play();
            _smoke.Add((ps, now + seconds));
        }

        private static Vector3 Ground(System.Numerics.Vector2 p) => new Vector3(p.X, 0f, p.Y);
    }
}
