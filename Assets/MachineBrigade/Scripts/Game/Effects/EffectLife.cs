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
    /// 1     20-40 mm                                0.3 s     0.5-1 s                               10 s
    /// 2     57-105 mm                               0.5 s     1.5-2.5 s                             20 s
    /// 3     120-155 mm, Grad                        0.8 s     3-5 s                                 30 s
    /// 4     203-240 mm, bombs 400 kg+, Smerch       1.2 s     a column 6-10 s drifting on the wind  45 s
    /// 5     406 mm+, super weapons                  1.8 s     a column 10-15 s, high, on the wind   60 s
    /// (play-test 12: the smoke column halved from L6's 1-2 / 3-5 / 6-10 / 12-20 / 25-40 s, "khói đen rất dài")
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
            // Play-test 12: the lingering smoke about half as long (the band order kept, the 406 mm plume capped at 15 s);
            // fireballs and craters unchanged.
            new(0.3f, 0.5f, 1f, 10f),
            new(0.5f, 1.5f, 2.5f, 20f),
            new(0.8f, 3f, 5f, 30f),
            new(1.2f, 6f, 10f, 45f),
            new(1.8f, 10f, 15f, 60f),
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

    /// <summary>
    /// Play-test 14 session 5 ("giảm toàn bộ thời gian các khói, kể cả khói tên lửa, khói cháy nổ, khói sát thương khi nổ chết
    /// (cái này đáng kể nhất) do nó làm chiến trường toàn khói"): every smoke clears sooner, as a share of the life it had. The
    /// fire, the flash, the fireball, sparks and debris are never cut or shrunk; a tank round's impact smoke keeps its own
    /// 0.4 (<see cref="EffectsDirector.TankSmokeLife"/>). View only.
    /// </summary>
    internal static class SmokeTimes
    {
        /// <summary>A missile's or rocket's smoke trail (the motor plume's puffs, the old shell trail).</summary>
        public const float Trail = 0.5f;

        /// <summary>Play-test 14 (lane H), the owner after R2 ("khói của tên lửa ... giảm chiều dài 50%"): a missile's or rocket's
        /// smoke trail half as long again (each puff lives this share on top of <see cref="Trail"/>).</summary>
        public const float TrailLength = 0.5f;

        /// <summary>... and a quarter narrower (each puff this share as wide; the owner's correction: 20-30 %, not half).
        /// The motor's flame, glow and the puffs' spacing are unchanged.</summary>
        public const float TrailWidth = 0.75f;

        /// <summary>A blast's smoke, dust and smoke column, and the smoke it leaves lingering (ImpactSmoke).</summary>
        public const float Blast = 0.5f;

        /// <summary>A vehicle's death: its killing blast's and its death explosion's smoke (the worst of it).</summary>
        public const float Death = 0.35f;

        /// <summary>
        /// Play-test 14 (lane H), the owner after R2 ("khói vẫn quá nhiều khi chết, giảm lượng khói sinh ra 50%"): a death's
        /// smoke, dust and smoke column also emit half their puffs, on top of the shorter <see cref="Death"/> life. The fire,
        /// flash, fireball, sparks and debris keep every particle.
        /// </summary>
        public const float DeathAmount = 0.5f;

        /// <summary>The share of its smoke puffs a blast drawn at smoke life <paramref name="life"/> emits: a death's
        /// (<see cref="Death"/> or shorter) <see cref="DeathAmount"/>, any other all of them.</summary>
        public static float AmountOf(float life) => life <= Death + 0.001f ? DeathAmount : 1f;

        /// <summary>A fire's smoke (a burning hull, a wreck, a ground fire): each puff's life.</summary>
        public const float Fire = 0.5f;

        /// <summary>The smoke a fire (a wreck's above all) smoulders on with after its flames are out: how long it goes on.</summary>
        public const float Smoulder = 0.5f;
    }
}
