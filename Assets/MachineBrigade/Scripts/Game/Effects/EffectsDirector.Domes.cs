using System.Collections.Generic;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 17 C: the shield carrier's and the shield generator's domes, drawn with prompt 11's shield (the
    /// hex dome of the fortress and the Shield Dome item): exactly the sim's radius, half as high, following a
    /// moving carrier; it rises when the dome is up, ripples where a hit lands on it (the sim's DomeHit), flickers
    /// more as it runs low, and shatters when it breaks (DomeChanged). View only.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private sealed class UnitDome
        {
            public ShieldVisual Shield;
            public float Radius;
            public bool Up;
        }

        private readonly Dictionary<EntityId, UnitDome> _unitDomes = new();
        private readonly List<EntityId> _goneDomes = new();

        /// <summary>This step's rounds a dome took whole: the unit they were aimed at and where they struck the dome.</summary>
        private readonly List<(System.Numerics.Vector2 victim, Vector3 skin)> _domeStruck = new();

        /// <summary>
        /// Where a round bound for <paramref name="victim"/> under a dome (<paramref name="radius"/> across the ground,
        /// <paramref name="height"/> high over <paramref name="centre"/>) crosses its skin: straight above the unit
        /// when it comes down from the sky, else along its line from <paramref name="from"/>; and the skin's outward normal there.
        /// </summary>
        internal static Vector3 DomeSkin(Vector3 centre, float radius, float height, Vector3 victim, Vector3 from, bool above, out Vector3 normal)
        {
            var local = victim - centre;
            Vector3 point;
            var across = new Vector2(local.x, local.z).magnitude / Mathf.Max(0.1f, radius);
            var dir = from - victim;
            if (above || new Vector2(dir.x, dir.z).sqrMagnitude < 0.25f)
                point = new Vector3(local.x, height * Mathf.Sqrt(Mathf.Max(0.04f, 1f - Mathf.Min(1f, across * across))), local.z);
            else
            {
                // Solve |p / (r, h, r)| = 1 for p = local + t * dir, t > 0 (the unit is inside, so one root is).
                dir.Normalize();
                var s = new Vector3(1f / radius, 1f / Mathf.Max(0.1f, height), 1f / radius);
                var p = Vector3.Scale(local, s);
                var d = Vector3.Scale(dir, s);
                var a = Vector3.Dot(d, d);
                var b = 2f * Vector3.Dot(p, d);
                var c = Vector3.Dot(p, p) - 1f;
                var disc = Mathf.Max(0f, b * b - 4f * a * c);
                var t = (-b + Mathf.Sqrt(disc)) / (2f * Mathf.Max(1e-5f, a));
                point = local + dir * Mathf.Max(0f, t);
                point.y = Mathf.Max(0.3f, point.y);
            }
            normal = new Vector3(point.x / (radius * radius), point.y / Mathf.Max(0.01f, height * height), point.z / (radius * radius)).normalized;
            return centre + point;
        }

        /// <summary>A hit on a dome's skin: a white-blue flare on the spot and a spray of sparks thrown off it.</summary>
        private void DomeFlash(Vector3 at, Vector3 normal, float strength)
        {
            if (!_cull.Visible(at, 0.3f)) return;
            _emitters.Charge(at, 2.2f * strength);
            _emitters.Charge(at + normal * 0.3f, 1.4f * strength);
            _muzzle.SparkBurst(at + normal * 0.2f, normal, Mathf.RoundToInt(10 + 8 * strength), 4f, 12f, 0.9f);
        }

        /// <summary>A round a dome took whole this step, landing at <paramref name="at"/>: where it struck the dome instead.</summary>
        private bool DomeTook(System.Numerics.Vector2 at, out Vector3 skin)
        {
            foreach (var (victim, point) in _domeStruck)
                if (System.Numerics.Vector2.DistanceSquared(victim, at) < 1f)
                {
                    skin = point;
                    return true;
                }
            skin = default;
            return false;
        }

        private void DomeEvent(in SimEvent e, ViewRegistry views, float now)
        {
            if (!_unitDomes.TryGetValue(e.Entity, out var dome)) return;
            if (e.Kind == SimEventKind.DomeHit && dome.Up)
            {
                // Test feedback 19P: the round strikes the dome's skin where its path crosses it (from above for a
                // shell or a bomb): the hex ripple and a flash there, and a dome that took all of it bursts the
                // round on its skin instead of on the unit under it.
                var centre = dome.Shield.Transform.position;
                var victim = new Vector3(e.Position.X, 1f, e.Position.Y);
                var skin = DomeSkin(centre, dome.Radius, dome.Radius * ItemDomeHeight, victim, new Vector3(e.Target.X, 1.5f, e.Target.Y), e.Airborne,
                    out var normal);
                var strength = Mathf.Clamp(e.Value / 250f, 0.5f, 1.6f);
                dome.Shield.Hit(skin, now, default, strength);
                DomeFlash(skin, normal, strength);
                if (e.Mount == 1) _domeStruck.Add((e.Position, skin));
            }
            else if (e.Kind == SimEventKind.DomeChanged && e.Value < 0.5f && dome.Up)
            {
                dome.Up = false;
                dome.Shield.Collapse(now);
                Ring(dome.Shield.Transform.position, dome.Radius * 2f, Color.white);
            }
        }

        /// <summary>Every frame: a dome for every unit that has one, where it stands, up or down as the sim says.</summary>
        private void TickUnitDomes(ViewRegistry views, float now)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (view.Def.Dome is not { } def || view.IsWreck) continue;
                var id = view.Sim.Id;
                if (!_unitDomes.TryGetValue(id, out var dome))
                {
                    var shield = new ShieldVisual("Unit Dome " + view.Def.Id, _root, ShieldVisual.Shape.Dome, def.Radius);
                    shield.Transform.localScale = new Vector3(def.Radius, def.Radius * ItemDomeHeight, def.Radius);
                    shield.SetSide(view.Team == views.PlayerTeam);
                    dome = new UnitDome { Shield = shield, Radius = def.Radius };
                    _unitDomes[id] = dome;
                }
                dome.Shield.Transform.position = new Vector3(view.Position.x, 0.05f, view.Position.z);
                var up = view.Sim.IsAlive && view.Sim.DomeUp;
                if (up && !dome.Up)
                {
                    dome.Up = true;
                    dome.Shield.Raise(now);
                }
                else if (!up && dome.Up)
                {
                    dome.Up = false;
                    dome.Shield.Collapse(now);
                }
                if (dome.Up) dome.Shield.Flicker = Mathf.Clamp01((0.4f - view.Sim.DomeShare) * 1.8f);
                dome.Shield.Tick(now);
            }
            _goneDomes.Clear();
            foreach (var (id, dome) in _unitDomes)
                if (!views.TryGet(id, out var v) || v.IsWreck || !v.Sim.IsAlive)
                {
                    if (dome.Up)
                    {
                        dome.Up = false;
                        dome.Shield.Collapse(now);
                    }
                    if (!dome.Shield.Tick(now)) _goneDomes.Add(id);
                }
            foreach (var id in _goneDomes)
            {
                Object.Destroy(_unitDomes[id].Shield.Transform.gameObject);
                _unitDomes.Remove(id);
            }
        }
    }
}
