using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fix prompt L6 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): how long a blast's parts last, by its round's size band
    /// (the prompt's table; the band is the weapon's tier, T0-T5, or for a round with no family, a strike or a cook-off, its
    /// explosion tier). View only.
    /// <code>
    /// band  rounds                                  fireball  smoke / dust                          crater, scorch
    /// 0     up to 14.5 mm                           0.2 s     0.5 s                                 none
    /// 1     20-40 mm                                0.3 s     1-2 s                                 10 s
    /// 2     57-105 mm                               0.5 s     3-5 s                                 20 s
    /// 3     120-155 mm, Grad                        0.8 s     6-10 s                                30 s
    /// 4     203-240 mm, bombs 400 kg+, Smerch       1.2 s     a column 12-20 s drifting on the wind 45 s
    /// 5     406 mm+, super weapons                  1.8 s     a column 25-40 s, high, on the wind   60 s
    /// </code>
    /// A blast's own recipe (ExplosionEffect, never cut or shrunk) draws the fireball and its first smoke; the lingering
    /// smoke and dust after it are <see cref="ImpactSmoke"/>'s, the craters <see cref="DecalPool"/>'s.
    /// </summary>
    internal static class EffectLife
    {
        public readonly struct Band
        {
            public Band(float fireball, float smokeMin, float smokeMax, float crater)
            {
                Fireball = fireball;
                SmokeMin = smokeMin;
                SmokeMax = smokeMax;
                Crater = crater;
            }

            /// <summary>The fireball's life (s).</summary>
            public float Fireball { get; }

            /// <summary>The smoke and dust's life (s), min and max.</summary>
            public float SmokeMin { get; }
            public float SmokeMax { get; }

            /// <summary>The crater's or scorch mark's life (s; 0: none).</summary>
            public float Crater { get; }
        }

        public const int Top = 5;

        public static readonly Band[] Bands =
        {
            new(0.2f, 0.5f, 0.5f, 0f),
            new(0.3f, 1f, 2f, 10f),
            new(0.5f, 3f, 5f, 20f),
            new(0.8f, 6f, 10f, 30f),
            new(1.2f, 12f, 20f, 45f),
            new(1.8f, 25f, 40f, 60f),
        };

        /// <summary>A round's band: its tier, else its explosion tier's (Small 1, Medium 2, Large 3, Huge 4, Ultimate 5).</summary>
        public static int BandOf(WeaponDef round, ExplosionTier tier) =>
            round != null && round.Tier >= 0 ? Mathf.Clamp(round.Tier, 0, Top) : BandOf(tier);

        /// <summary>A blast's band by its explosion tier alone (a strike, a cook-off, a bomblet).</summary>
        public static int BandOf(ExplosionTier tier) => tier switch
        {
            ExplosionTier.Small => 1,
            ExplosionTier.Medium => 2,
            ExplosionTier.Large => 3,
            ExplosionTier.Huge => 4,
            _ => 5,
        };

        public static Band Of(int band) => Bands[Mathf.Clamp(band, 0, Top)];

        /// <summary>A crater's life for the band (0: none).</summary>
        public static float Crater(int band) => Of(band).Crater;
    }
}
