using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L5 (DECISIONS "Prompt 34 L5/L6/L7"): how a round's tier (WeaponDef.Tier, T0-T5, from its weapon family)
    /// is drawn when it fires and when it lands, how much of that detail a blast gets by its distance from the view and by
    /// how many big blasts are already going, and how hard it shakes the camera. View only: nothing here reads or changes
    /// the simulation beyond the weapon's data.
    /// <para>The prompt's table: T0 a small flash, sparks and dust; T1 a small flash and thin smoke, flak bursting in the
    /// air; T2 a medium flash, short smoke and the barrel's recoil, a small fireball; T3 a big flash, long smoke, the hull
    /// squatting and a dust ring, a medium fireball, a dust column and a small crater; T4 a very big lasting flash, long
    /// rolling smoke, a wide dust ring and the air's pressure wave, a large fireball, a tall column, the shockwave,
    /// fragments, a big crater, light vehicles near it rocked, a light shake; T5 a huge flash lighting the scene, very long
    /// smoke, a water or dust wave spreading wide, a very large fireball, a small mushroom cloud, two shockwave rings, far
    /// fragments, a very big lasting crater, a strong shake.</para>
    /// </summary>
    internal static class TierFx
    {
        /// <summary>The highest tier.</summary>
        public const int Top = 5;

        /// <summary>A weapon's tier, -1 without one (no family: support strikes, the game's staged blasts).</summary>
        public static int Of(WeaponDef weapon) => weapon == null ? -1 : Mathf.Min(Top, Looks.TryGetValue(weapon.Id, out var look) ? look.Tier : weapon.Tier);

        /// <summary>
        /// Play-test 14 (lane L, owner 04/10: "các tàu / thuyền mini boss tôi thấy bắn nổ hơi to (các vũ khí mới thêm vào như tên
        /// lửa)"): the boss weapons added on 04/10 drawn like the same-calibre weapons elsewhere, not by their family's tier
        /// alone. The view's only (the Sim's tier and every number stay): <see cref="Of"/> takes <c>Tier</c>, and a blast's
        /// overlay is drawn for at most <c>Core</c> m (-1: its own radius; its rings stay on the real radius).
        /// <list type="bullet">
        /// <item>Kh-35U (145 kg), NSM (125 kg real) and Club-S (200 kg): T3, the Maverick's band (57 kg, T3) rather than the
        /// strike jets' 400-450 kg cruise missiles (T4); a Kh-29L (320 kg) is the lightest T4 in the game.</item>
        /// <item>Spike NLOS: an ATGM's blast (the Kornet's, the Hellfire's: T2 at its nominal size), with no splash since MB_FINAL
        /// zones (an ATGM's direct hit, as theirs; it was 3.5 m).</item>
        /// </list>
        /// The Tomahawk (450 kg) keeps T4 (with a Large blast, the Kh-29L's look); the guns already match their calibres.
        /// </summary>
        private static readonly Dictionary<string, (int Tier, float Core)> Looks = new()
        {
            ["scylla_kh35"] = (3, -1f),
            ["pt14_hp_nsm"] = (3, -1f),
            ["hydra_club_s"] = (3, -1f),
            ["pt14_co_spike"] = (2, 0f),
        };

        /// <summary>
        /// Play-test 14 (lane L, owner 04/10: "các vũ khí lớn các boss sao không có hiệu ứng bắn"): how much bigger a boss's shot
        /// is drawn at its muzzle (the weapon's flash, its tier's firing look, the pressure and water rings): 1 for anyone else.
        /// The recipes are sized for a vehicle's guns (a 120 mm tank gun's flash: a 5 m core) and took no calibre, so a 406 mm,
        /// a 203 mm and a 155 mm all flashed as a tank gun does; on a 50-90 m hull, framed from far enough to see it whole,
        /// that is a speck for a tenth of a second, and a boss's gun shakes nothing (play-test 12): its big guns read as not
        /// firing at all. A gun's muzzle blast grows with its bore (the fireball goes with the cube root of the charge, the
        /// charge with the bore cubed), so a shell or bullet's look by its calibre against the 120 mm design; and a boss by its
        /// bulk (its radius over 7 m, at most 1.5: ships and the space ships 1.4-1.5). Missiles and rockets by the bulk alone.
        /// At least 1 (nothing drawn smaller than before), at most 3 (the 406 mm).
        /// </summary>
        public static float BossMuzzle(MachineBrigade.Game.Views.VehicleView shooter, WeaponDef weapon)
        {
            if (shooter == null || shooter.Def == null || !shooter.Def.Boss || weapon == null) return 1f;
            var bulk = Mathf.Clamp(shooter.Def.Radius / 7f, 1f, 1.5f);
            var calibre = weapon.CaliberMm > 0f ? weapon.CaliberMm : weapon.Size;
            var bore = weapon.Projectile is ProjectileKind.Shell or ProjectileKind.Bullet && calibre > 0f ? calibre / DesignCalibre : 1f;
            return Mathf.Clamp(bore * bulk, 1f, MaxBossMuzzle);
        }

        /// <summary>The calibre the firing recipes are drawn for (a main battle tank's gun, mm), and the most a boss's shot grows.</summary>
        public const float DesignCalibre = 120f, MaxBossMuzzle = 3f;

        /// <summary>The core radius a round's tier overlay is drawn for: its own, capped by its look (<see cref="Looks"/>).</summary>
        public static float CoreOf(WeaponDef weapon, float core) =>
            weapon != null && Looks.TryGetValue(weapon.Id, out var look) && look.Core >= 0f ? Mathf.Min(core, look.Core) : core;

        /// <summary>The core radius each tier's overlay is designed at (m): its overlay is played at core / this.</summary>
        public static float NominalCore(int tier) => tier switch
        {
            <= 2 => 2.5f,
            3 => 5f,
            4 => 9f,
            _ => 14f,
        };

        /// <summary>The overlay's size for a round of <paramref name="core"/> m: never under 0.8 or over 1.6 of the design.</summary>
        public static float OverlayScale(int tier, float core) => core > 0f ? Mathf.Clamp(core / NominalCore(tier), 0.8f, 1.6f) : 1f;

        /// <summary>
        /// The round's own extras (the thermobaric round's second fireball, a HEAT warhead's flash, an AP round's sparks)
        /// grown by its tier: 1 to T2, then 15 % a tier (T5: 1.45).
        /// </summary>
        public static float Extra(int tier) => tier <= 2 ? 1f : 1f + 0.15f * (tier - 2);

        // ---------------------------------------------------------------------------------------------- detail by distance

        /// <summary>How much of a tier's overlay a blast or shot gets.</summary>
        public enum Detail
        {
            /// <summary>Near the view: everything.</summary>
            Full,

            /// <summary>Middle distance: fewer particles and fragments (<see cref="ReducedShare"/>), no thrown chunks.</summary>
            Reduced,

            /// <summary>Far: the flash and the rings only (the blast its round always had still plays whole).</summary>
            Far,
        }

        /// <summary>A view distance under this is near (full detail), under <see cref="MidView"/> middle.</summary>
        public const float NearView = 70f, MidView = 140f;

        /// <summary>The share of an overlay's particles at middle distance.</summary>
        public const float ReducedShare = 0.45f;

        /// <summary>
        /// The view distance of a point <paramref name="distance"/> m from the camera's focus: the top-down camera is
        /// orthographic, so a zoomed-out view (a bigger <paramref name="zoom"/>, its half height in metres) draws
        /// everything smaller and counts as farther.
        /// </summary>
        public static float ViewDistance(float distance, float zoom) => Mathf.Max(0f, distance) + Mathf.Max(0f, zoom) * 1.2f;

        public static Detail DetailAt(float distance, float zoom)
        {
            var d = ViewDistance(distance, zoom);
            return d < NearView ? Detail.Full : d < MidView ? Detail.Reduced : Detail.Far;
        }

        /// <summary>The particle share of a detail level (0: no overlay particles).</summary>
        public static float ShareOf(Detail detail) => detail switch
        {
            Detail.Full => 1f,
            Detail.Reduced => ReducedShare,
            _ => 0f,
        };

        // ------------------------------------------------------------------------------------------------ bomb sticks

        /// <summary>
        /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): a stick from this many bombs draws its far bombs lighter,
        /// and from <see cref="LongStick"/> its farthest with the flash and rings only.
        /// </summary>
        public const int StickFrom = 6, LongStick = 12;

        /// <summary>A stick's bomb this near the view's focus (m) keeps its detail; the far ones of a long stick past <see cref="NearView"/>.</summary>
        public const float StickNear = 35f;

        /// <summary>
        /// The detail of a stick's bomb <paramref name="distance"/> m from the view's focus that wanted <paramref name="wanted"/>
        /// (<paramref name="bombs"/> in its stick): the near ones as they are, so the chain reads bomb by bomb where the player
        /// looks; one level less farther out on a stick of <see cref="StickFrom"/>+; only the flash and the rings past
        /// <see cref="NearView"/> on a stick of <see cref="LongStick"/>+ (a 20-bomb carpet). The round's own blast always plays
        /// whole: this is the tier overlay and the lingering smoke only, never a smaller fire or blast.
        /// </summary>
        public static Detail StickDetail(Detail wanted, int bombs, float distance)
        {
            if (bombs < StickFrom || wanted == Detail.Far || distance < StickNear) return wanted;
            return bombs >= LongStick && distance >= NearView ? Detail.Far : Lower(wanted);
        }

        /// <summary>One level less detail (a blast over its tier's cap).</summary>
        public static Detail Lower(Detail detail) => detail == Detail.Full ? Detail.Reduced : Detail.Far;

        // ------------------------------------------------------------------------------------------------- concurrency

        /// <summary>Blasts drawn in full detail at once at most: T5 1, T4 3, T3 6 (the prompt's 1, 2-3 and 4-6).</summary>
        public static int FullCap(int tier) => tier >= 5 ? 1 : tier == 4 ? 3 : tier == 3 ? 6 : int.MaxValue;

        /// <summary>
        /// A full-detail blast's weight against <see cref="WeightCap"/>: with a T5 going, two T4 and three T3 more fit; a
        /// third T4 only without the T5. So the prompt's "lower events step down" holds across tiers too.
        /// </summary>
        public static float Weight(int tier) => tier >= 5 ? 6f : tier == 4 ? 3f : tier == 3 ? 1f : 0f;

        public const float WeightCap = 12f;

        /// <summary>How long a full-detail blast counts as going (its heavy particles' time on screen), seconds.</summary>
        public static float Busy(int tier) => tier >= 5 ? 6f : tier == 4 ? 4f : 2.5f;

        // ------------------------------------------------------------------------------------------------ camera shake

        /// <summary>Shake at the blast for T4 (light) and T5 (strong); none below T4 (the prompt's table).</summary>
        public static float ShakeAt(int tier) => tier >= 5 ? 0.6f : tier == 4 ? 0.22f : 0f;

        /// <summary>A shot shakes less than its round's landing (the muzzle's blast is the smaller one).</summary>
        public const float ShotShare = 0.5f;

        /// <summary>The shake halves this far from the view's focus (m), and stops beyond <see cref="ShakeReach"/>.</summary>
        public const float ShakeFalloff = 25f, ShakeReach = 90f;

        /// <summary>The most trauma the tier shakes add up to at once (the camera's own cap is 1).</summary>
        public const float ShakeCap = 0.65f;

        /// <summary>
        /// The trauma a T4+ blast (or shot, <paramref name="shot"/>) adds: only on screen, only within
        /// <see cref="ShakeReach"/> of the view's focus, falling off with distance. The setting (MatchSettings.ScreenShake)
        /// and the cap are applied by the camera (RtsCamera.AddTierTrauma).
        /// </summary>
        public static float Shake(int tier, float distance, bool onScreen, bool shot = false)
        {
            var at = ShakeAt(tier) * (shot ? ShotShare : 1f);
            if (at <= 0f || !onScreen || distance > ShakeReach) return 0f;
            return at / (1f + Mathf.Max(0f, distance) / ShakeFalloff);
        }

        // ----------------------------------------------------------------------------------------------- firing look

        /// <summary>A tier's look when it fires, on top of the muzzle flash its weapon always had.</summary>
        public readonly struct Muzzle
        {
            public Muzzle(float flash, float flashLife, int puffs, float puffSize, Vector2 puffLife, float pressure, float dustRing,
                float water, float light, float squat)
            {
                Flash = flash;
                FlashLife = flashLife;
                Puffs = puffs;
                PuffSize = puffSize;
                PuffLife = puffLife;
                Pressure = pressure;
                DustRing = dustRing;
                Water = water;
                Light = light;
                Squat = squat;
            }

            /// <summary>The extra flash core's size (m; 0: none) and how long it burns (s).</summary>
            public float Flash { get; }
            public float FlashLife { get; }

            /// <summary>Gun smoke puffs blown out of the muzzle, their size (m) and life (s): long and slow to clear at T3+.</summary>
            public int Puffs { get; }
            public float PuffSize { get; }
            public Vector2 PuffLife { get; }

            /// <summary>The pressure wave's ring round the muzzle (m across; 0: none).</summary>
            public float Pressure { get; }

            /// <summary>The dust ring blown up round the vehicle or tower (m across; 0: none).</summary>
            public float DustRing { get; }

            /// <summary>A ship's pressure wave on the water (m across; 0: none).</summary>
            public float Water { get; }

            /// <summary>The light the flash throws on the ground round it (m across; 0: none).</summary>
            public float Light { get; }

            /// <summary>How far the hull squats back on its springs (degrees; 0: not at all).</summary>
            public float Squat { get; }
        }

        /// <summary>T0-T5 at fire. T0 adds nothing (its machine-gun flicker is its look).</summary>
        public static readonly Muzzle[] Fire =
        {
            new(0f, 0f, 0, 0f, Vector2.zero, 0f, 0f, 0f, 0f, 0f),
            new(0f, 0f, 2, 0.6f, new Vector2(1.2f, 1.8f), 0f, 0f, 0f, 0f, 0f),
            new(1.2f, 0.1f, 4, 1.1f, new Vector2(1.8f, 2.6f), 0f, 0f, 0f, 0f, 0f),
            new(2.4f, 0.16f, 10, 1.7f, new Vector2(3.5f, 5f), 0f, 8f, 0f, 9f, 1.6f),
            new(3.6f, 0.24f, 16, 2.4f, new Vector2(5f, 7f), 7f, 16f, 12f, 16f, 2.4f),
            new(5f, 0.34f, 24, 3.2f, new Vector2(7f, 10f), 12f, 26f, 22f, 28f, 3.2f),
        };

        public static Muzzle FireOf(int tier) => Fire[Mathf.Clamp(tier, 0, Top)];
    }

    /// <summary>
    /// Prompt 34 L5: the big blasts drawn in full detail now, so that at most <see cref="TierFx.FullCap"/> of a tier (and
    /// <see cref="TierFx.WeightCap"/> in all) are; any over that is drawn one level down (<see cref="TierFx.Lower"/>).
    /// </summary>
    internal sealed class TierBudget
    {
        private readonly List<(int tier, float until)> _busy = new();

        /// <summary>The detail a T<paramref name="tier"/> blast gets that wanted <paramref name="wanted"/>; a full one is counted.</summary>
        public TierFx.Detail Admit(int tier, TierFx.Detail wanted, float now)
        {
            if (tier < 3 || wanted != TierFx.Detail.Full) return wanted;
            Prune(now);
            var same = 0;
            var weight = 0f;
            foreach (var (t, _) in _busy)
            {
                if (t == tier) same++;
                weight += TierFx.Weight(t);
            }
            if (same >= TierFx.FullCap(tier) || weight + TierFx.Weight(tier) > TierFx.WeightCap) return TierFx.Lower(wanted);
            _busy.Add((tier, now + TierFx.Busy(tier)));
            return wanted;
        }

        /// <summary>Full-detail blasts of a tier still going at <paramref name="now"/>.</summary>
        public int Active(int tier, float now)
        {
            Prune(now);
            var n = 0;
            foreach (var (t, _) in _busy)
                if (t == tier) n++;
            return n;
        }

        public void Clear() => _busy.Clear();

        private void Prune(float now)
        {
            for (var i = _busy.Count - 1; i >= 0; i--)
                if (_busy[i].until <= now) _busy.RemoveAt(i);
        }
    }
}
