using System.Collections.Generic;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fix prompt L4 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"), the view of munitions in flight. A guided round the Sim
    /// takes off its target (<see cref="SimEventKind.RoundDiverted"/>) turns onto where it now goes off and bursts there
    /// with its effect and sound: a missile a flare decoyed chases a burning flare and blows up beside it, it does not
    /// vanish. A flare release fans its flares from the model's Mount_Flare points (else its dispensers, else under the
    /// hull): 4-6 for a fighter or attack jet, 4-8 for a helicopter, 8-16 for a big aircraft in "angel wings", each a very
    /// bright point on a thick white smoke trail burning 3-4 s on a falling curve, launched along its tube with the
    /// aircraft's speed, its light on the hull. One release is one decoy in the Sim whatever is drawn.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        /// <summary>Where an air burst of a diverted round is due, at what height (its impact event carries no height).</summary>
        private readonly List<(System.Numerics.Vector2 at, float height, float until)> _decoyBursts = new();

        private void RoundDiverted(in SimEvent e, ViewRegistry views, float now)
        {
            var height = 0.4f;
            if (e.Airborne)
                height = views.TryGet(e.Other, out var chased) && chased.Flying ? Mathf.Max(2.5f, chased.Altitude - 1.5f) : 12f;
            var to = new Vector3(e.Position.X, height, e.Position.Y);
            _projectiles.Divert(e.Other, to, e.Value, now);
            if (!e.Airborne) return;
            _decoyBursts.Add((e.Position, height, now + e.Value + 2f));
            if (_decoyBursts.Count > 64) _decoyBursts.RemoveAt(0);
            // The flare it chases, burning where it meets it (the release's own flares fall from the tubes).
            if (e.Mount == (int)MachineBrigade.Sim.Entities.Divert.Flare && _cull.Visible(to, 0.3f))
                _emitters.LoneFlare(to, e.Value + 0.6f, Vector3.down * 1.2f);
        }

        /// <summary>The height a diverted round's air burst at <paramref name="at"/> is drawn at, when one is due there.</summary>
        private bool DecoyHeight(System.Numerics.Vector2 at, float now, out float height)
        {
            height = 0f;
            for (var i = _decoyBursts.Count - 1; i >= 0; i--)
            {
                var d = _decoyBursts[i];
                if (d.until < now)
                {
                    _decoyBursts.RemoveAt(i);
                    continue;
                }
                if (System.Numerics.Vector2.DistanceSquared(d.at, at) > 0.5f) continue;
                height = d.height;
                _decoyBursts.RemoveAt(i);
                return true;
            }
            return false;
        }

        /// <summary>How many flares one release of <paramref name="flyer"/> puts out: by its size (data munitionRules.flareRelease).</summary>
        internal static (int min, int max) FlareCount(VehicleView flyer, MunitionRules rules) =>
            flyer.Def.Class == UnitClass.Helicopter ? rules.FlaresHelicopter : Large(flyer) ? rules.FlaresLarge : rules.FlaresFighter;

        /// <summary>A big aircraft (a bomber, a tanker, a gunship, a carrier): its release is the "angel wings".</summary>
        private static bool Large(VehicleView flyer) =>
            flyer.Def.Class != UnitClass.Helicopter && (flyer.Sim.Radius >= 4f || flyer.Def.Boss);

        /// <summary>A flare release: the flares shared out over the model's flare points, both sides at once.</summary>
        private void FlareSalvo(VehicleView flyer)
        {
            var rules = _catalog.Munitions;
            var (least, most) = FlareCount(flyer, rules);
            var total = Random.Range(least, most + 1);
            var scale = Mathf.Clamp(flyer.Sim.Radius / 3.2f, 0.8f, 1.6f);
            var root = flyer.Root;
            if (root == null) return;
            var carrier = root.forward * flyer.Speed;
            var wings = Large(flyer);
            var points = flyer.FlarePoints;
            var live = 0;
            for (var i = 0; i < points.Count; i++)
                if (points[i] != null) live++;
            if (live == 0)
            {
                // No flare points on the model: from under both sides of the hull.
                var below = flyer.Position - root.up * 0.3f - root.forward * flyer.Sim.Radius * 0.2f;
                for (var s = -1; s <= 1; s += 2)
                    _emitters.Flares(below + root.right * (s * flyer.Sim.Radius * 0.3f), FlareLook(root, s, wings), scale,
                        s < 0 ? total / 2 : total - total / 2, carrier, rules.FlareBurn.min, rules.FlareBurn.max);
            }
            else
            {
                var k = 0;
                for (var i = 0; i < points.Count; i++)
                {
                    var point = points[i];
                    if (point == null) continue;
                    // Shared out evenly, the first points taking the odd ones.
                    var n = total / live + (k < total % live ? 1 : 0);
                    k++;
                    if (n <= 0) continue;
                    var side = root.InverseTransformPoint(point.position).x;
                    // A point on the centre line (the tail root) throws to alternate sides.
                    var s = Mathf.Abs(side) < 0.05f ? (k % 2 == 0 ? 1 : -1) : side < 0f ? -1 : 1;
                    _emitters.Flares(point.position, FlareLook(root, s, wings), scale, n, carrier, rules.FlareBurn.min, rules.FlareBurn.max);
                }
            }
            // The burst of light on the hull.
            _night.Flash(flyer.Position - root.up * 0.6f, 5f * scale);
        }

        /// <summary>The way a side's flares leave: down and out (an "angel wings" release out and up first, then curving down).</summary>
        private static Vector3 FlareLook(Transform root, int side, bool wings) =>
            wings ? root.right * side + root.up * 0.55f - root.forward * 0.25f : root.right * side - root.up * 1.2f - root.forward * 0.3f;
    }
}
