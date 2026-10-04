using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    internal sealed partial class MuzzleFx
    {
        /// <summary>
        /// Prompt 34 L5: a tier's firing look on top of the weapon's own flash (<see cref="Fire"/>), redrawn bigger and longer
        /// by tier (<see cref="TierFx.Fire"/>): a larger flash core that burns longer, a long tongue, a muzzle fireball at T3+
        /// that rolls into smoke, and gun smoke blown out along the barrel that drifts and clears slowly. The pressure wave,
        /// the dust ring, the water wave and the ground light need the blast layers and are drawn by EffectsDirector.Tiers.
        /// <paramref name="share"/> is the distance's share (<see cref="TierFx.ShareOf"/>): fewer puffs far off.
        /// Play-test 14 (lane L): <paramref name="scale"/> grows the look (a boss's gun by its calibre and bulk,
        /// <see cref="TierFx.BossMuzzle"/>): the flash, its tongues and fireballs by it, the smoke and the dust by its square
        /// root (a 406 mm's T5 smoke would otherwise bury its ship), as many of each.
        /// </summary>
        public void TierShot(int tier, Vector3 from, Vector3 direction, float now, Anchor anchor, float? groundY, float share = 1f,
            float scale = 1f)
        {
            if (tier <= 0) return;
            var look = TierFx.FireOf(tier);
            scale = Mathf.Max(1f, scale);
            var flash = look.Flash * scale;
            var dir = direction.sqrMagnitude > 1e-4f ? direction.normalized : Vector3.forward;
            _anchor = anchor;
            _now = now;
            if (look.Flash > 0f)
            {
                // The core sits ahead of the tip, a little further the bigger it is; the tongue reaches out with it.
                Core(from + dir * (0.35f * flash), flash * 0.9f, flash * 1.1f, look.FlashLife * 0.85f, look.FlashLife * 1.15f);
                Tongue(from, dir, tier >= 4 ? 3 : tier >= 3 ? 2 : 1, flash * 0.42f, look.FlashLife * 1.1f);
            }
            if (tier >= 3)
            {
                // Big guns belch fireballs that roll into smoke, more and bigger by tier.
                var balls = tier - 2;
                for (var k = 0; k < balls; k++)
                    _fireball.Emit(new ParticleSystem.EmitParams
                    {
                        position = from + dir * (flash * (0.3f + 0.25f * k)),
                        velocity = (dir + Random.insideUnitSphere * 0.15f) * (4f + 2f * tier) * Mathf.Sqrt(scale),
                        startSize = flash * Random.Range(0.85f, 1.1f),
                        startLifetime = Random.Range(0.45f, 0.6f) + 0.08f * tier,
                        applyShapeToPosition = false,
                    }, 1);
                Sparks(from, dir, 4 * tier, 6f, 16f, (1f + 0.2f * tier) * Mathf.Sqrt(scale));
            }
            // Gun smoke: blown out along the barrel, braked by the air, then drifting and clearing slowly.
            var puffs = Mathf.Max(look.Puffs > 0 ? 1 : 0, Mathf.RoundToInt(look.Puffs * share));
            if (puffs > 0)
                Puffs(from, dir, puffs, new Vector2(1.5f, 4f + tier), new Vector2(look.PuffSize * 0.8f, look.PuffSize * 1.2f), look.PuffLife,
                    Mathf.Sqrt(scale));
            // The muzzle's blast lifts dust off the ground under it (T3+).
            if (tier >= 3 && groundY.HasValue && share > 0f)
                Dust(from, groundY.Value, dir, Mathf.RoundToInt((4 + 3 * tier) * share), (0.6f + 0.2f * tier) * Mathf.Sqrt(scale));
            _anchor = default;
        }

        /// <summary>Prompt 34 L5: spray blown off the water by a ship's big guns: pale puffs racing out low over the sea.</summary>
        public void WaterSpray(Vector3 centre, float radius, int count)
        {
            for (var i = 0; i < count; i++)
            {
                var a = Random.value * Mathf.PI * 2f;
                var outward = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                Emit(_smoke, centre + outward * (radius * Random.Range(0.2f, 0.5f)) + Vector3.up * 0.3f,
                    outward * Random.Range(6f, 12f) + Vector3.up * Random.Range(0.3f, 1.2f), Random.Range(1.4f, 2.4f), Random.Range(1.4f, 2.4f));
            }
        }
    }
}
