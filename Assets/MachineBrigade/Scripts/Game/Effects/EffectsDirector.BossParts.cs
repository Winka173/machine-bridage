using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fire and smoke at a boss's breaks (prompt 9 C), all of it the view's alone: the simulation
    /// never sees it (no smoke zone, nothing that blocks sight or aim).
    /// <list type="bullet">
    /// <item>A part under half its health smokes thinly and sparks; under a quarter the smoke
    /// thickens and a small fire starts.</item>
    /// <item>A part breaking: a blast by what it is (guns and ammunition a big blast and debris, energy
    /// parts a flash, a blue shock ring and arcs, engines a fireball), then fire and a black smoke
    /// column there until the battle ends; energy parts keep arcing, a flying boss's broken engines
    /// trail long smoke.</item>
    /// <item>The body burns too: two small fires under two thirds of its health, a big one and thick
    /// smoke under a third.</item>
    /// <item>The fires ride on the boss (on the part's turret, where it has one), so they follow it and
    /// its smoke streams out behind a boss on the move. Play-test 6 (DECISIONS 21H): they burn as a burning
    /// vehicle does (HullFire: tongues, glow, sparks, flare-ups and black smoke), no longer as ground fire.</item>
    /// <item>At most <see cref="FireBudget.Cap"/> fire points per boss (<see cref="FireBudget.LowCap"/>
    /// on Low): nearby ones are merged. Low also emits half the smoke and no arcs; High throws debris.</item>
    /// <item>When the boss dies every fire flares up before the death blasts, and the wreck burns on.</item>
    /// </list>
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private sealed class BossFx
        {
            public VehicleView View;
            public readonly List<(Transform point, int fire, float size)> Fires = new();
            public int Signature = int.MinValue;
            public float PuffAt;
            public float ArcAt;
            public float FireAt;
            public int Beat;
        }

        private readonly Dictionary<EntityId, BossFx> _bossFx = new();

        /// <summary>Bosses whose part just broke: the sim's blast event that follows is drawn here instead, at the part.</summary>
        private readonly HashSet<EntityId> _partBlasts = new();

        private static readonly Color ArcBlue = new(0.55f, 1.4f, 2.6f, 1f);

        private static bool Low => MatchSettings.Tier == GraphicsQuality.Low;

        /// <summary>A boss's fire point's flames against a burning tank's (its fire sizes run 0.35 to 1.4).</summary>
        private const float PartFireSize = 2.2f;

        /// <summary>A part broke (its PartBroken event): the blast by what it is, at the part itself.</summary>
        private void PartBroke(in SimEvent e, ViewRegistry views, float now)
        {
            _partBlasts.Add(e.Entity);
            if (!views.TryGet(e.Entity, out var view) || e.Mount < 0 || e.Mount >= view.Def.Parts.Count) return;
            var part = view.Def.Parts[e.Mount];
            var at = view.PartWorld(e.Mount);
            switch (part.Fx)
            {
                case "energy":
                    Pop(_pop, at, now);
                    Ring(at, Mathf.Max(5f, part.Radius * 3f), ArcBlue * 1.2f);
                    Flash?.Invoke(0.06f / (1f + Vector3.Distance(at, _camera.Focus) / 40f));
                    Shake(at, 0.35f);
                    _muzzle.SparkBurst(at, Vector3.up, Low ? 10 : 26, 5f, 14f);
                    if (!Low) Arcs(at, part.Radius * 1.5f, 10);
                    break;
                case "engine":
                    Explode(ExplosionTier.Large, at, now, 0.9f);
                    for (var i = 0; i < 4; i++) _emitters.DamageSmoke(at + Random.insideUnitSphere * part.Radius, part.Radius * 1.2f, 0.05f);
                    break;
                default:
                    Explode(ExplosionTier.Huge, at, now, 0.75f);
                    _muzzle.SparkBurst(at, Vector3.up, Low ? 8 : 20, 6f, 16f);
                    // The High setting throws real debris off a gun or an ammunition store going up.
                    if (MatchSettings.HighQuality) _layers.Chunks.Throw(new ChunkThrower.Recipe(0, 8, 3, new Vector2(5f, 12f), 0.6f), at, 1f, now);
                    break;
            }
        }

        /// <summary>A self-repair put a part back: a shower of welding sparks (its fire goes out on the next rebuild).</summary>
        private void PartBack(in SimEvent e, ViewRegistry views)
        {
            if (!views.TryGet(e.Entity, out var view) || e.Mount < 0 || e.Mount >= view.Def.Parts.Count) return;
            var at = view.PartWorld(e.Mount);
            _muzzle.SparkBurst(at, Vector3.up, 30, 3f, 8f);
            _emitters.Repair(at);
        }

        /// <summary>Per frame: every boss's fire points kept up to date, and its smoke, sparks, arcs and trails.</summary>
        private void TickBossParts(ViewRegistry views, float now, float dt)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (!view.Def.Boss || view.IsWreck || !view.Sim.IsAlive) continue;
                if (!_bossFx.TryGetValue(view.Id, out var fx)) _bossFx[view.Id] = fx = new BossFx { View = view };
                var signature = Signature(view);
                if (signature != fx.Signature)
                {
                    fx.Signature = signature;
                    Rebuild(fx, now);
                }
                if (!_cull.Visible(view.Position, 0.3f)) continue;
                if (now >= fx.FireAt)
                {
                    // Play-test 6 (DECISIONS 21H): the part fires burn as a burning vehicle's (HullFire), riding the boss.
                    fx.FireAt = now + HullFire.Next;
                    var velocity = view.Root.forward * view.Speed;
                    foreach (var (point, _, size) in fx.Fires)
                        if (point != null) _hullFire.FeedPoint(point.position, size * PartFireSize, Mathf.Clamp01(size), velocity, fx.Beat++);
                }
                Trails(view);
                if (now < fx.PuffAt) continue;
                fx.PuffAt = now + (Low ? 0.45f : 0.22f);
                Puffs(view);
                if (!Low && now >= fx.ArcAt)
                {
                    fx.ArcAt = now + Random.Range(0.25f, 0.7f);
                    for (var p = 0; p < view.Def.Parts.Count; p++)
                        if (view.Sim.IsPartBroken(p) && view.Def.Parts[p].Fx == "energy") Arcs(view.PartWorld(p), view.Def.Parts[p].Radius, 4);
                }
            }
        }

        /// <summary>What decides a boss's fire points: its broken parts, its parts under a quarter, its body's stage, the quality.</summary>
        private static int Signature(VehicleView view)
        {
            var sim = view.Sim;
            var s = 17;
            for (var p = 0; p < sim.PartCount; p++)
                s = s * 3 + (sim.IsPartBroken(p) ? 2 : sim.PartShare(p) < 0.25f ? 1 : 0);
            var health = sim.MaxHp > 0f ? sim.Hp / sim.MaxHp : 1f;
            s = s * 3 + (health < 0.33f ? 2 : health < 0.66f ? 1 : 0);
            return s * 2 + (Low ? 1 : 0);
        }

        /// <summary>The fire points again: every broken part and every part under a quarter, the body's fires, merged down to the cap.</summary>
        private void Rebuild(BossFx fx, float now)
        {
            var view = fx.View;
            var sim = view.Sim;
            var anchors = new List<Transform>();
            var points = new List<FireBudget.Point>();
            int AnchorOf(Transform t)
            {
                var k = anchors.IndexOf(t);
                if (k >= 0) return k;
                anchors.Add(t);
                return anchors.Count - 1;
            }
            for (var p = 0; p < sim.PartCount; p++)
            {
                var part = view.Def.Parts[p];
                if (sim.IsPartBroken(p)) points.Add(new FireBudget.Point(view.PartWorld(p), part.Fx == "engine" ? 0.9f : 0.8f, AnchorOf(view.PartAnchor(p))));
                else if (sim.PartShare(p) < 0.25f) points.Add(new FireBudget.Point(view.PartWorld(p), 0.35f, AnchorOf(view.PartAnchor(p))));
            }
            var health = sim.MaxHp > 0f ? sim.Hp / sim.MaxHp : 1f;
            var model = view.ModelRoot;
            var r = view.Def.Radius / Mathf.Max(0.1f, view.Def.Scale);
            var top = view.Top * 0.6f / Mathf.Max(0.1f, view.Def.Scale);
            if (health < 0.66f)
            {
                points.Add(new FireBudget.Point(model.TransformPoint(new Vector3(r * 0.3f, top, r * 0.2f)), 0.5f, AnchorOf(model)));
                points.Add(new FireBudget.Point(model.TransformPoint(new Vector3(-r * 0.28f, top, -r * 0.3f)), 0.5f, AnchorOf(model)));
            }
            if (health < 0.33f) points.Add(new FireBudget.Point(model.TransformPoint(new Vector3(0f, top, -r * 0.1f)), 1.4f, AnchorOf(model)));

            var merged = FireBudget.Merge(points, Low ? FireBudget.LowCap : FireBudget.Cap);
            foreach (var (point, _, _) in fx.Fires)
                if (point != null) Object.Destroy(point.gameObject);
            fx.Fires.Clear();
            foreach (var m in merged)
            {
                var anchor = anchors[m.Anchor];
                if (anchor == null) continue;
                var point = new GameObject("Boss fire").transform;
                point.SetParent(anchor, false);
                point.position = m.At;
                // Burns until the battle is over (or the part is patched, or the boss dies): fed in TickBossParts.
                fx.Fires.Add((point, -1, m.Size));
            }
        }

        /// <summary>Thin smoke and sparks off hurt parts, thick smoke off parts about to go and off a body under a third.</summary>
        private void Puffs(VehicleView view)
        {
            var sim = view.Sim;
            for (var p = 0; p < sim.PartCount; p++)
            {
                if (sim.IsPartBroken(p)) continue;
                var share = sim.PartShare(p);
                if (share >= 0.5f) continue;
                var at = view.PartWorld(p) + Vector3.up * 0.3f;
                var size = Mathf.Clamp(view.Def.Parts[p].Radius * 0.6f, 0.6f, 2f);
                _emitters.DamageSmoke(at, share < 0.25f ? size * 1.4f : size * 0.8f, share < 0.25f ? 0.15f : 0.7f);
                if (Random.value < (share < 0.25f ? 0.5f : 0.3f))
                    _layers.Sparks.Emit(new ParticleSystem.EmitParams
                    {
                        position = at, velocity = Vector3.up * 4f + Random.insideUnitSphere * 3f, startSize = 0.12f,
                        startLifetime = 0.6f, applyShapeToPosition = false,
                    }, Low ? 2 : 5);
            }
            var health = sim.MaxHp > 0f ? sim.Hp / sim.MaxHp : 1f;
            if (health < 0.33f)
                _emitters.DamageSmoke(view.Position + Vector3.up * view.Top, view.Def.Radius * 0.9f, 0.05f);
        }

        /// <summary>A flying or fast boss's broken engines trail long black smoke.</summary>
        private void Trails(VehicleView view)
        {
            if (!view.Flying && view.Speed < 4f) return;
            var sim = view.Sim;
            for (var p = 0; p < sim.PartCount; p++)
            {
                if (!sim.IsPartBroken(p) || view.Def.Parts[p].Fx != "engine") continue;
                if (Low && Random.value < 0.5f) continue;
                _emitters.DamageSmoke(view.PartWorld(p), Mathf.Clamp(view.Def.Parts[p].Radius, 1f, 2.5f), 0.08f);
            }
        }

        /// <summary>A few jagged electric arcs round an energy part: glow points along a zigzag, blue sparks at its ends.</summary>
        private void Arcs(Vector3 at, float reach, int points)
        {
            var end = at + Random.insideUnitSphere * Mathf.Max(1f, reach);
            var previous = at;
            for (var k = 1; k <= points; k++)
            {
                var t = k / (float)points;
                var p = Vector3.Lerp(at, end, t) + Random.insideUnitSphere * 0.35f;
                _emitters.Charge(p, 0.35f);
                _emitters.Charge((p + previous) * 0.5f, 0.25f);
                previous = p;
            }
            _layers.Sparks.Emit(new ParticleSystem.EmitParams
            {
                position = end, velocity = Random.insideUnitSphere * 4f, startSize = 0.1f, startLifetime = 0.35f,
                startColor = new Color(0.6f, 0.85f, 1f, 1f), applyShapeToPosition = false,
            }, 4);
        }

        /// <summary>A boss died: every fire flares up before its death blasts, then the wreck burns on for a while.</summary>
        private void BossPartsDied(VehicleView view, float now)
        {
            if (!_bossFx.TryGetValue(view.Id, out var fx)) return;
            _bossFx.Remove(view.Id);
            foreach (var (point, _, size) in fx.Fires)
            {
                if (point == null) continue;
                _hullFire.FeedPoint(point.position, size * PartFireSize * 1.8f, 1f, Vector3.zero, 0);
                var at = point.position;
                Explode(ExplosionTier.Medium, at, now, 0.8f + size * 0.3f, flash: false);
                _fires.Ignite(at, size * 1.5f, Random.Range(25f, 35f), now, view.Root);
            }
        }

        /// <summary>The fire points of a boss now (for tests and the budget check): how many, and none past the cap.</summary>
        internal int BossFirePoints(EntityId boss) => _bossFx.TryGetValue(boss, out var fx) ? fx.Fires.Count : 0;
    }
}
