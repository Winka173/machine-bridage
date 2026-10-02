using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    internal sealed partial class ExplosionEffect
    {
        /// <summary>
        /// Prompt 34 L5 (DECISIONS "Prompt 34 L5/L6/L7"): a round's blast REDRAWN for its tier, played on top of the blast
        /// its round always had (that one is never cut or shrunk). Each tier is designed at its own size, not a scaled
        /// copy: more and wider quads, its own smoke column, debris, embers and dust skirts, timed for that tier.
        /// <list type="bullet">
        /// <item>T2 (57-105 mm): a small hot fireball, a puff of dust and a scatter of earth.</item>
        /// <item>T3 (120-155 mm, Grad): a medium fireball, a dust column and a small crater glow.</item>
        /// <item>T4 (203-240 mm, 400 kg bombs, Smerch): a large fireball that rolls up, a tall smoke column, fragments and
        /// burning debris thrown wide, two dust skirts and a big crater glow.</item>
        /// <item>T5 (406 mm, super weapons): a very large fireball, a column that spreads into a small mushroom cap, debris
        /// thrown far, three dust skirts and a crater that glows a long time.</item>
        /// </list>
        /// The shockwave rings are not in these recipes: they are drawn by EffectsDirector.Tiers exactly on the blast's
        /// core and edge (a recipe's ring would grow with the recipe). Sizes are for the tier's nominal core
        /// (<see cref="TierFx.NominalCore"/>); the director plays them at core / nominal, between 0.8 and 1.6.
        /// T0 and T1 have no overlay: their sparks, dust and flak bursts are the Small recipe and FlakBursts.
        /// </summary>
        public static ExplosionEffect CreateTier(int tier, BlastLayers l)
        {
            var e = new ExplosionEffect(l);
            switch (tier)
            {
                case 2:
                    e.Fireball(1, new Vector2(3.6f, 4.6f), new Vector2(0.8f, 1.05f), 0.45f, hot: true);
                    e.Dust(2, new Vector2(2.6f, 3.6f));
                    e.Dirt(10, new Vector2(4f, 9f));
                    e.Debris(5, new Vector2(4f, 9f));
                    e.Embers(6, 0.8f);
                    e.Smoke(2, new Vector2(3.4f, 4.6f), new Vector2(3f, 4.2f), 0.35f);
                    break;

                case 3:
                    e.Fireball(1, new Vector2(5f, 6.2f), new Vector2(0.7f, 0.9f), 0.4f, hot: true);
                    e.Fireball(3, new Vector2(5.5f, 7.5f), new Vector2(1.1f, 1.45f), 1.2f);
                    e.Fireball(2, new Vector2(4.5f, 6f), new Vector2(0.95f, 1.2f), 1.8f, 0.14f);
                    e.Dust(4, new Vector2(4f, 5.5f));
                    e.Dirt(24, new Vector2(5f, 12f));
                    e.Debris(14, new Vector2(6f, 13f));
                    e.BurningDebris(4, new Vector2(6f, 12f));
                    e.Embers(18, 1f);
                    e.DustRing(14f, 12);
                    // The dust column: five billows climbing out of the crater.
                    e.Column(5, new Vector2(4.6f, 6f), new Vector2(7f, 9f), 0.35f, 1.4f);
                    e.CraterGlow(4.5f, 3.5f);
                    e._chunks = new ChunkThrower.Recipe(earth: 8, wreckage: 0, burning: 1, new Vector2(6f, 12f), 0.9f);
                    break;

                default: // T4 and up (T5 is redrawn in its own commit)
                    e.Flash(14f);
                    e.Fireball(2, new Vector2(9f, 11.5f), new Vector2(0.85f, 1.1f), 0.8f, hot: true);
                    e.Fireball(4, new Vector2(8f, 10.5f), new Vector2(1.35f, 1.75f), 2.4f);
                    e.Fireball(3, new Vector2(7f, 9f), new Vector2(1.2f, 1.5f), 3f, 0.15f);
                    e.Fireball(2, new Vector2(6f, 8f), new Vector2(1.1f, 1.4f), 3.4f, 0.32f);
                    e.Secondaries(9f, 3.4f, 0.22f, 0.5f, 0.8f, 1.15f);
                    e.Smoke(8, new Vector2(7f, 10f), new Vector2(6f, 9f));
                    e.Sparks(80, new Vector2(10f, 26f), 0.22f);
                    e.Debris(30, new Vector2(9f, 20f));
                    e.BurningDebris(12, new Vector2(9f, 18f));
                    e.Dirt(30, new Vector2(6f, 15f));
                    e.Embers(40, 1.4f);
                    e.GroundLight(28f, 1f, 0.4f);
                    e.DustRing(28f, 24);
                    e.OuterDust(30f, 16);
                    // A tall smoke column: eight billows, each 2.4 m above the last.
                    e.Column(8, new Vector2(6.5f, 8.5f), new Vector2(10f, 13f), 0.5f, 2.4f);
                    e.CraterGlow(8f, 6f);
                    e._chunks = new ChunkThrower.Recipe(earth: 16, wreckage: 4, burning: 4, new Vector2(9f, 18f), 1.2f);
                    break;

            }
            return e;
        }

        /// <summary>
        /// Prompt 34 L5: the ground round a T3+ gun as it fires (<see cref="TierFx.Fire"/>): the dust its muzzle blast lifts
        /// in a ring round the vehicle or tower (T3 8 m, T4 16 m, T5 26 m across, T5 with a second, wider skirt) and the
        /// flash's light on the ground. Played at the ground under the muzzle.
        /// </summary>
        public static ExplosionEffect CreateTierFire(int tier, BlastLayers l)
        {
            var e = new ExplosionEffect(l);
            var look = TierFx.FireOf(tier);
            e.DustRing(look.DustRing, tier >= 5 ? 28 : tier >= 4 ? 18 : 10);
            if (tier >= 5) e.OuterDust(look.DustRing * 1.25f, 18);
            e.Dust(tier - 1, new Vector2(2.4f, 3.4f) * (0.5f + 0.25f * tier));
            e.GroundLight(look.Light, tier >= 5 ? 1f : tier >= 4 ? 0.8f : 0.55f, 0.18f + 0.04f * tier);
            return e;
        }
    }
}
