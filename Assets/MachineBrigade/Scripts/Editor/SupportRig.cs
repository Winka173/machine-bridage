using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Fire support without the rest of the match, for <see cref="EffectShots.Supports"/>: each
    /// card's warning, aircraft pass, rounds coming down and impacts replayed on a scene's clock
    /// with StrikeSystem's timings, drawn by the battle's own <see cref="StrikeEffects"/> (and the
    /// impacts by <see cref="BlastRig"/>). Mirrors EffectsDirector for ShellInbound.
    /// </summary>
    internal sealed class SupportRig
    {
        /// <summary>StrikeSystem's lead times: a round is announced this long before it lands; a cruise missile or SEAD jet runs in this long.</summary>
        private const float ShellFall = 0.9f, RunIn = 1.4f, Approach = 70f;

        private readonly BlastRig _blasts;
        private readonly Catalog _catalog;
        private readonly Emitters _emitters;
        private readonly ProjectilePool _projectiles;
        private readonly TracerPool _tracers;
        private readonly StrikeEffects _strikes;

        public SupportRig(BlastRig blasts, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Transform root)
        {
            _blasts = blasts;
            _catalog = GameContent.LoadCatalog();
            _emitters = new Emitters(materials, root);
            _projectiles = new ProjectilePool(root, 96);
            _tracers = new TracerPool(meshes.Box, materials.Tracer, root, 64);
            _strikes = new StrikeEffects(_catalog, materials, meshes, models, _emitters, _projectiles, new SmokeScreens(), root);
        }

        public void Tick(float now, float dt)
        {
            _tracers.Tick(now, _emitters);
            _projectiles.Tick(now, _emitters);
            _emitters.Tick(now, dt);
            _strikes.Tick(now);
        }

        /// <summary>
        /// A scene of support <paramref name="id"/> called on <paramref name="point"/>, its script
        /// set so the first impact falls on the sheet's common start (the called moment is its
        /// delay before). Supports with no direction run along +X, as the simulation's do.
        /// </summary>
        public BlastScene Scene(string id, Vector3 point, float view)
        {
            var s = _catalog.Supports[id];
            var d = s.Delay;
            var run = Vector3.right;
            var scene = new BlastScene(id, point, view, -d);
            var end = s.IsLine ? point + run * s.Length : point;
            scene.At(0f, t => _strikes.Warned(s, 0, point, end, d, t));
            var random = new System.Random(id.GetHashCode());
            float Next() => (float)random.NextDouble();
            Vector3 Around(float reach, float inner = 0f)
            {
                var a = Next() * Mathf.PI * 2f;
                var r = reach * Mathf.Sqrt(inner + (1f - inner) * Next());
                return point + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r;
            }
            switch (s.Kind)
            {
                case SupportKind.Barrage:
                {
                    var interval = s.Count > 1 ? s.Duration / (s.Count - 1) : 0f;
                    for (var k = 0; k < s.Count; k++)
                    {
                        var at = Around(s.Radius);
                        var lands = d + k * interval;
                        scene.At(lands - ShellFall, t => Inbound(s, at, ShellFall, t));
                        scene.At(lands, t => _blasts.Strike(id, s.Tier, s.BlastRadius, at + Vector3.up * 0.3f, t));
                    }
                    break;
                }
                case SupportKind.Airstrike:
                {
                    var speed = s.Length / Mathf.Max(0.2f, s.Duration);
                    var lead = Mathf.Min(Approach + s.Length * 0.2f, speed * Mathf.Max(0.3f, d - 0.1f));
                    var from = point - run * lead;
                    var to = end + run * Approach;
                    scene.At(d - lead / speed, t => _strikes.Passed(s, 0, from, to, Vector3.Distance(from, to) / speed, t));
                    var interval = s.Count > 1 ? s.Duration / (s.Count - 1) : 0f;
                    for (var i = 0; i < s.Count; i++)
                    {
                        var along = s.Count > 1 ? i / (float)(s.Count - 1) : 0.5f;
                        var at = Vector3.Lerp(point, end, along) + new Vector3(-run.z, 0f, run.x) * ((Next() - 0.5f) * s.Radius) + Vector3.up * 0.3f;
                        scene.At(d + i * interval, t => _blasts.Strike(id, s.Tier, s.BlastRadius, at, t));
                    }
                    break;
                }
                case SupportKind.CruiseMissile:
                    if (id != "moab") scene.At(d - RunIn, t => _strikes.Passed(s, 0, point - run * (Approach + 40f), point, RunIn, t));
                    scene.At(d, t => _blasts.Strike(id, s.Tier, s.BlastRadius, point + Vector3.up * 0.3f, t));
                    break;
                case SupportKind.Smoke:
                    for (var k = 0; k < 5; k++)
                    {
                        var angle = k * Mathf.PI * 2f / 4f + 0.8f;
                        var at = k == 0 ? point : point + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * (s.Radius * 0.5f);
                        var seconds = ShellFall + k * 0.08f;
                        scene.At(d - ShellFall, t => Inbound(s, at, seconds, t));
                    }
                    scene.At(d, t => _strikes.DebugSmoke(point, t));
                    break;
                case SupportKind.Minefield:
                    for (var k = 0; k < s.Count; k++)
                    {
                        var at = Around(s.Radius, 0.1f);
                        var seconds = ShellFall + k * 0.06f;
                        scene.At(d - ShellFall, t => Inbound(s, at, seconds, t));
                        scene.At(d, t =>
                        {
                            _blasts.Mark(at, 2.2f, new Color(1.1f, 0.95f, 0.75f, 0.7f));
                            _emitters.Dust(at, 2f);
                        });
                    }
                    break;
                case SupportKind.Sead:
                    scene.At(d - RunIn, t => _strikes.Passed(s, 0, point - run * (Approach + 40f), point + run * Approach, RunIn * 1.6f, t));
                    scene.At(d - ShellFall, t => Inbound(s, point, ShellFall, t));
                    scene.At(d, t => _blasts.Strike(id, s.Tier, s.BlastRadius, point + Vector3.up * 0.3f, t));
                    break;
                case SupportKind.Emp:
                    scene.At(d, t =>
                    {
                        _blasts.Mark(point, s.Radius * 2.2f, new Color(0.45f, 0.8f, 2.6f, 1f));
                        _blasts.Mark(point, s.Radius * 1.4f, new Color(0.9f, 1.4f, 3f, 1f));
                    });
                    break;
                case SupportKind.Repair:
                    for (var k = 0; k < s.Count; k++)
                        scene.At(d + k * 0.5f, t => _emitters.Repair(Around(4f) + Vector3.up));
                    break;
                case SupportKind.Reinforce:
                    scene.At(d, t =>
                    {
                        for (var k = 0; k < s.Units.Count; k++)
                        {
                            var angle = k * Mathf.PI * 2f / Mathf.Max(1, s.Units.Count);
                            var at = point + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * (s.Units.Count > 1 ? 6f : 0f);
                            var view = _blasts.Spawn(s.Units[k], at);
                            view.Root.rotation = Quaternion.Euler(0f, 90f, 0f);
                        }
                    });
                    break;
            }
            return scene;
        }

        /// <summary>A round announced on its way down (ShellInbound), as EffectsDirector draws it.</summary>
        private void Inbound(SupportDef s, Vector3 at, float seconds, float now)
        {
            var land = at + Vector3.up * 0.2f;
            // The guns stand back towards the calling side (-X here).
            var back = Vector3.left;
            var from = land + back * 24f + Vector3.up * 58f;
            if (_strikes.Inbound(s, back, from, land, seconds, now)) return;
            _tracers.Launch(from, land, seconds, 0f, 0.34f, 3.6f, now, 0f, 0.5f);
        }

        /// <summary>The cards on the sheet, in its order, with the half-height of each row's view.</summary>
        public static readonly (string id, float view)[] Cards =
        {
            ("artillery_barrage", 14f), ("remote_mines", 14f), ("airstrike", 24f),
            ("napalm_strike", 24f), ("cluster_strike", 24f), ("air_raid", 28f), ("cruise_missile", 22f), ("moab", 34f), ("emp_blast", 18f),
            ("repair_drop", 11f), ("reinforcements", 14f),
        };

        public static IEnumerable<string> Ids
        {
            get
            {
                foreach (var (id, _) in Cards) yield return id;
            }
        }
    }
}
