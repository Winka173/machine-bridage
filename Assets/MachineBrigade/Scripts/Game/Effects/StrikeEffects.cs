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

        /// <summary>Red target marks on the ground: one for an area strike, one per bomb for an airstrike.</summary>
        private sealed class Telegraph
        {
            public GroundMark[] Rings;
            public int Used;
            public float Start, Impact, End, Radius;
            public bool Active;
            public Color Edge = WarningColor, Fill = WarningFill;
        }

        private static readonly Color WarningColor = new(2.4f, 0.32f, 0.18f, 0.95f);
        private static readonly Color WarningFill = new(2.6f, 0.9f, 0.3f, 1f);

        // Support that harms no one where it lands is marked in its own colours: a scan's circle
        // in radar cyan, a tower's drop point in white.
        private static readonly Color ScanColor = new(0.3f, 1.6f, 2.2f, 0.8f);
        private static readonly Color ScanFill = new(0.4f, 1.2f, 1.6f, 0.5f);
        private static readonly Color DropColor = new(1.8f, 1.8f, 1.7f, 0.85f);

        /// <summary>A UAV scan's drone: flies in, then circles the mark until the scan ends.</summary>
        private sealed class ScanDrone
        {
            public GameObject Root;
            public Vector3 From, Centre;
            public float Arrive, End, Radius;
            public bool Active;
        }

        private readonly List<ScanDrone> _drones = new();
        private const float DroneAltitude = 22f;

        private const int RingsPerTelegraph = 10;

        private sealed class Jet
        {
            public GameObject Root;
            public string Model;
            public Transform Bombs;
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
        private readonly SmokeScreens _screens;
        private readonly Transform _root;
        private readonly MaterialLibrary _materials;
        private readonly bool _hasJet, _hasBomb, _hasCruise;

        public StrikeEffects(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Emitters emitters,
            ProjectilePool projectiles, SmokeScreens screens, Transform parent)
        {
            _screens = screens;
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
                var t = new Telegraph { Rings = new GroundMark[RingsPerTelegraph] };
                for (var r = 0; r < RingsPerTelegraph; r++)
                {
                    t.Rings[r] = new GroundMark("Strike Mark", _root, meshes, materials, GroundMark.Style.Strike);
                    t.Rings[r].Visible = false;
                }
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
                    else if (pass.Kind == SupportKind.Scan) LaunchScanDrone(e, pass, now);
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
                    foreach (var ring in t.Rings) ring.Visible = false;
                    continue;
                }
                // The fill sweeps round until impact; the mark beats faster as it nears.
                var progress = Mathf.Clamp01((now - t.Start) / Mathf.Max(0.1f, t.Impact - t.Start));
                var urgency = Mathf.Clamp01(1f - (t.Impact - now) / 2f);
                var breathe = 1f + 0.05f * Mathf.Sin(now * Mathf.Lerp(6f, 20f, urgency));
                for (var r = 0; r < t.Used; r++)
                {
                    t.Rings[r].Set(t.Edge, t.Fill, progress, urgency);
                    t.Rings[r].Transform.localScale = Vector3.one * t.Radius * breathe;
                }
            }

            foreach (var d in _drones)
            {
                if (!d.Active) continue;
                if (now >= d.End)
                {
                    d.Active = false;
                    d.Root.SetActive(false);
                    continue;
                }
                Vector3 p, ahead;
                if (now < d.Arrive)
                {
                    // Flying in to the start of its circle.
                    var entry = d.Centre + Vector3.back * d.Radius;
                    p = Vector3.Lerp(d.From, entry, Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(d.Arrive - 3f, d.Arrive, now)));
                    ahead = entry - d.From;
                }
                else
                {
                    // A slow circle (about 16 s a lap), banked into the turn.
                    var a = (now - d.Arrive) * 0.4f;
                    p = d.Centre + new Vector3(-Mathf.Sin(a), 0f, -Mathf.Cos(a)) * d.Radius;
                    ahead = new Vector3(-Mathf.Cos(a), 0f, Mathf.Sin(a));
                }
                d.Root.transform.position = p;
                if (ahead.sqrMagnitude > 1e-4f) d.Root.transform.rotation = Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, 0f, now < d.Arrive ? 0f : 14f);
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
                    // Vapour off the wingtips and a hot exhaust, sized to the aircraft as drawn.
                    var scale = jet.Root.transform.localScale.x;
                    var right = jet.Root.transform.right * 4.5f * scale;
                    var back = jet.Root.transform.forward;
                    _emitters.Contrail(p + right - back * 2f * scale, 0.4f, 1.2f);
                    _emitters.Contrail(p - right - back * 2f * scale, 0.4f, 1.2f);
                    _emitters.Afterburner(p - back * 5.5f * scale, back, 1.4f);
                    _emitters.Contrail(p - back * 6.5f * scale, 0.5f, 1.4f);
                }
            }

            for (var i = _bombs.Count - 1; i >= 0; i--)
            {
                var (at, from, to) = _bombs[i];
                if (now < at) continue;
                _bombs.RemoveAt(i);
                if (_hasBomb) _projectiles.Launch(_models.Merged("bomb"), from, to, BombFall, 0f, 0f, now);
                // The bombs leave the wings as they fall.
                foreach (var jet in _jets)
                    if (jet.Active && jet.Bombs != null) jet.Bombs.gameObject.SetActive(false);
            }

            for (var i = _smoke.Count - 1; i >= 0; i--)
            {
                var (system, until) = _smoke[i];
                if (now < until) continue;
                var emission = system.emission;
                emission.enabled = false;
                if (now > until + 9f)
                {
                    _screens?.Remove(system.transform.position);
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
            t.Impact = now + delay;
            t.End = now + delay + (support.Kind is SupportKind.Barrage or SupportKind.Airstrike ? support.Duration : 0.2f);
            foreach (var ring in t.Rings) ring.Visible = false;
            if (support.IsLine)
            {
                // One ring per bomb, where it will land.
                t.Used = Mathf.Min(support.Count, RingsPerTelegraph);
                t.Radius = support.BlastRadius;
                for (var i = 0; i < t.Used; i++)
                {
                    var along = t.Used > 1 ? i / (float)(t.Used - 1) : 0.5f;
                    t.Rings[i].Transform.position = Vector3.Lerp(point, end, along) + Vector3.up * 0.1f;
                    t.Rings[i].Transform.localScale = Vector3.one * t.Radius;
                    t.Rings[i].Visible = true;
                }
                return;
            }
            t.Used = 1;
            // A loaned aircraft only needs its arrival point marked, not the ground it may cover.
            t.Radius = support.Kind == SupportKind.Escort ? Mathf.Min(support.Radius, 5f) : support.Radius;
            (t.Edge, t.Fill) = support.Kind switch
            {
                SupportKind.Scan => (ScanColor, ScanFill),
                SupportKind.Tower => (DropColor, DropColor),
                _ => (WarningColor, WarningFill),
            };
            // A scan's circle stays up while the drone watches it.
            if (support.Kind == SupportKind.Scan) t.End = now + delay + support.Duration;
            t.Rings[0].Transform.position = point + Vector3.up * 0.1f;
            t.Rings[0].Transform.localScale = Vector3.one * t.Radius;
            t.Rings[0].Visible = true;
        }

        private void ScheduleBombs(SupportDef support, Vector3 start, Vector3 end, float firstImpact)
        {
            var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
            // Each bomb leaves the aircraft one fall-time before it lands and keeps the aircraft's
            // speed on the way down, so it drops out from under the aircraft and lands as it passes.
            var speed = support.Length / Mathf.Max(0.2f, support.Duration);
            for (var i = 0; i < support.Count; i++)
            {
                var along = support.Count > 1 ? i / (float)(support.Count - 1) : 0.5f;
                var target = Vector3.Lerp(start, end, along);
                var release = target - (end - start).normalized * (speed * BombFall) + Vector3.up * JetAltitude;
                _bombs.Add((firstImpact + i * interval - BombFall, release, target));
            }
        }

        private void LaunchJet(in SimEvent e, float now)
        {
            if (!_hasJet) return;
            const string model = "strike_jet";
            var jet = _jets.Find(j => !j.Active && j.Model == model);
            if (jet == null)
            {
                jet = new Jet { Root = _models.Spawn(model, e.Team, _root).Root, Model = model };
                var twin = model == "heavy_bomber" ? "heavy_bomber" : "attack_jet";
                if (_catalog.Vehicles.TryGetValue(twin, out var sized)) jet.Root.transform.localScale = Vector3.one * sized.Scale;
                foreach (var t in jet.Root.GetComponentsInChildren<Transform>(true))
                    if (t.name.StartsWith("Bombs")) jet.Bombs = t;
                _jets.Add(jet);
            }
            jet.Root.SetActive(true);
            if (jet.Bombs != null) jet.Bombs.gameObject.SetActive(true);
            jet.From = Ground(e.Position) + Vector3.up * JetAltitude;
            jet.To = Ground(e.Target) + Vector3.up * JetAltitude;
            jet.Start = now;
            jet.Duration = Mathf.Max(0.5f, e.Value);
            jet.NextPuff = now;
            jet.Active = true;
        }

        private void LaunchScanDrone(in SimEvent e, SupportDef scan, float now)
        {
            if (!_models.Has("recon_drone")) return;
            var d = _drones.Find(x => !x.Active);
            if (d == null)
            {
                d = new ScanDrone { Root = _models.Spawn("recon_drone", e.Team, _root).Root };
                if (_catalog.Vehicles.TryGetValue("recon_drone", out var sized)) d.Root.transform.localScale = Vector3.one * sized.Scale;
                _drones.Add(d);
            }
            d.Root.SetActive(true);
            d.Centre = Ground(e.Target) + Vector3.up * DroneAltitude;
            d.From = Ground(e.Position) + Vector3.up * DroneAltitude;
            d.Radius = Mathf.Clamp(scan.Radius * 0.55f, 8f, 20f);
            d.Arrive = now + Mathf.Max(0.3f, e.Value);
            d.End = d.Arrive + scan.Duration + 0.5f;
            d.Active = true;
        }

        private void LaunchCruise(in SimEvent e, float now)
        {
            var from = Ground(e.Position) + Vector3.up * 40f;
            var to = Ground(e.Target);
            if (_hasCruise) _projectiles.Launch(_models.Merged("cruise_missile"), from, to, e.Value, 4f, 1.2f, now);
        }

        /// <summary>Device check (<c>-mb-smokescreen</c>): a smoke screen with no strike behind it.</summary>
        internal void DebugSmoke(Vector3 at, float now) => SpawnSmoke(at, 12f, 12f, now);

        private void SpawnSmoke(Vector3 at, float radius, float seconds, float now)
        {
            // Billowing smoke sheets on their own queue (FxQueue.Screen): whatever burns inside or
            // behind the screen shows through it only as a glow.
            var ps = PB.Create(_root, "Smoke Screen", FxMaterials.Shared.ScreenSmoke);
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
            PB.Flipbook(ps, loop: false, tilt: 25f, from: 0.08f, to: 0.92f);
            PB.Colors(ps, PB.Plume(0.72f, 0.82f, 0.75f));
            PB.Grow(ps, 0.6f, 1.6f);
            PB.Rise(ps, 0.2f, 0.6f);
            _screens?.Add(at, radius * 0.8f + 4f);
            var emission = ps.emission;
            emission.enabled = true;
            emission.rateOverTime = 26f;
            ps.Play();
            _smoke.Add((ps, now + seconds));
        }

        private static Vector3 Ground(System.Numerics.Vector2 p) => new Vector3(p.X, 0f, p.Y);
    }
}
