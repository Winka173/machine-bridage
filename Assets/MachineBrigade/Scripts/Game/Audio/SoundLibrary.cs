using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// Fix pass L7: the size classes of the sound library (Resources/Audio/sfx, Tools/sfx/build_sfx.py), in the order the
    /// sounds rise: louder, deeper, longer (Docs/audio/metrics.md).
    /// </summary>
    internal enum SizeClass
    {
        /// <summary>Up to 14.5 mm (T0).</summary>
        S0,

        /// <summary>20-40 mm (T1).</summary>
        S1,

        /// <summary>57-105 mm (T2).</summary>
        S2,

        /// <summary>120-155 mm (T3).</summary>
        S3,

        /// <summary>203-240 mm (T4).</summary>
        S4,

        /// <summary>Bombs.</summary>
        Bomb,

        /// <summary>Big rockets and missiles (T4+) and the 406 mm.</summary>
        S406,

        /// <summary>Super weapons: the other T5 (the 800 mm, the railguns of the bosses).</summary>
        Super,
    }

    /// <summary>Fix pass L7: what a round without a blast struck, as it sounds.</summary>
    internal enum HitSurface
    {
        /// <summary>The ground: earth.</summary>
        Ground,

        /// <summary>A building, a wall, a fixed defence: concrete.</summary>
        Concrete,

        /// <summary>A kinetic round on armour it does not pierce: metal (the only metal sound; rate-capped).</summary>
        Metal,

        /// <summary>A round that goes through (or a soft target, an aircraft's skin): a heavy, dull impact.</summary>
        Pierced,
    }

    /// <summary>The mix's four groups (prompt "Hiệu ứng / Nhạc / Thoại / Giao diện"), each under the master volume.</summary>
    internal enum AudioGroup
    {
        Effects,
        Music,
        Dialogue,
        UI,
    }

    /// <summary>
    /// Fix pass L7: the sound library's rules, kept free of Unity objects so the tests read them: a weapon's size class, the
    /// bank its shot and its landing play, what a hit struck, the match-wide metal rate cap, the camera-distance falloff and
    /// the Effects compressor's gain.
    /// </summary>
    internal static class SoundLibrary
    {
        /// <summary>The library's folder under Resources/Audio.</summary>
        public const string Folder = "sfx/";

        // ------------------------------------------------------------------------------------------------ sizes

        /// <summary>A weapon's size class: bombs; big rockets and missiles (T4+) and the 406 mm; the other T5 super; else its tier.</summary>
        public static SizeClass SizeOf(WeaponDef weapon)
        {
            if (weapon == null) return SizeClass.S2;
            if (weapon.Projectile == ProjectileKind.Bomb) return SizeClass.Bomb;
            var tier = weapon.Tier;
            if (tier >= 5) return weapon.WeaponFamilyId == "cal_406" ? SizeClass.S406 : SizeClass.Super;
            if (tier >= 4 && weapon.Projectile is ProjectileKind.Rocket or ProjectileKind.Missile) return SizeClass.S406;
            if (tier < 0)
            {
                // No family: by the round's weight and blast, as the old banks did.
                if (weapon.Projectile == ProjectileKind.Bullet) return weapon.RoundWeight >= 20f ? SizeClass.S1 : SizeClass.S0;
                return weapon.SplashRadius >= 8f ? SizeClass.S4 : weapon.Damage >= 100f ? SizeClass.S3 : SizeClass.S2;
            }
            return (SizeClass)Mathf.Clamp(tier, 0, 4);
        }

        /// <summary>How much farther a size carries (m) over the camera's hearing reach.</summary>
        public static float Carry(SizeClass size) => 12f * (int)size;

        /// <summary>The library's suffix of a size ("s0" .. "s4", "s406"; bombs and super weapons have their own names).</summary>
        private static string Suffix(SizeClass size) => size switch
        {
            SizeClass.S406 => "s406",
            SizeClass.Bomb => "s4",
            SizeClass.Super => "super",
            _ => "s" + (int)size,
        };

        // ------------------------------------------------------------------------------------------------ banks

        /// <summary>The bank a shot plays (null: the old categories: flamethrowers, drones, beams; bombs drop silently).</summary>
        public static string ShotBank(WeaponDef weapon)
        {
            if (weapon == null || weapon.Beam) return null;
            var size = SizeOf(weapon);
            switch (weapon.Projectile)
            {
                case ProjectileKind.Rocket:
                case ProjectileKind.Missile:
                    return size <= SizeClass.S1 ? null : size == SizeClass.S2 ? "launch_s2" : size == SizeClass.S3 ? "launch_s3" : "launch_big";
                case ProjectileKind.Flame:
                case ProjectileKind.Drone:
                case ProjectileKind.Bomb:
                    return null;
                default:
                    return size == SizeClass.Super ? "shot_super" : "shot_" + Suffix(size);
            }
        }

        /// <summary>
        /// The blast a round's landing plays, by size and round: thermobaric, HEAT, an air burst (fragmentation, or any blast
        /// in the air), else high explosive. Null for a round without a blast (a kinetic round: <see cref="HitBank"/>), fire
        /// and energy (the old categories).
        /// </summary>
        public static string BlastBank(WeaponDef round, bool airborne = false)
        {
            if (round == null || round.Beam) return null;
            if (round.DamageType is DamageType.Fire or DamageType.Energy) return null;
            if (round.DamageType == DamageType.Kinetic && round.SplashRadius <= 0f) return null;
            var size = SizeOf(round);
            if (round.Thermobaric || round.WeaponVariantId == "thermobaric" || round.Id.StartsWith("thermobaric"))
                return size >= SizeClass.S4 ? "blast_thermo_s4" : "blast_thermo_s3";
            if (round.DamageType == DamageType.ShapedCharge) return size >= SizeClass.S3 ? "blast_heat_s3" : "blast_heat_s2";
            if (round.DamageType == DamageType.Fragmentation || airborne)
                return size <= SizeClass.S1 ? "blast_air_s1" : size == SizeClass.S2 ? "blast_air_s2" : "blast_air_s3";
            return size switch
            {
                SizeClass.S0 or SizeClass.S1 => "blast_he_s1",
                SizeClass.Bomb => "blast_bomb",
                SizeClass.Super => "blast_super",
                _ => "blast_he_" + Suffix(size),
            };
        }

        /// <summary>The bank a round without a blast plays on what it struck: light up to 40 mm, heavy from 57 mm.</summary>
        public static string HitBank(HitSurface surface, SizeClass size)
        {
            var heavy = size >= SizeClass.S2;
            return surface switch
            {
                HitSurface.Metal => heavy ? "hit_metal_heavy" : "hit_metal_light",
                HitSurface.Pierced => heavy ? "hit_pen_heavy" : "hit_pen_light",
                HitSurface.Concrete => heavy ? "hit_concrete_heavy" : "hit_concrete_light",
                _ => heavy ? "hit_ground_heavy" : "hit_ground_light",
            };
        }

        /// <summary>A round of <paramref name="penetration"/> goes through a face of <paramref name="armour"/>: level with it or better (the Sim's ✓, step 2 or under).</summary>
        public static bool Penetrates(float penetration, float armour) => penetration >= armour - 0.01f;

        /// <summary>
        /// What a round without a blast struck, as it sounds. Metal only for a kinetic round on an armoured vehicle's face it
        /// does not pierce; a pierced face, an aircraft or an unarmoured target is a heavy impact; a building or a fixed
        /// defence concrete; nothing the ground.
        /// </summary>
        public static HitSurface SurfaceOf(bool struck, bool vehicle, bool structure, bool flying, bool kinetic, float penetration, float armour)
        {
            if (!struck) return HitSurface.Ground;
            if (!vehicle || structure) return HitSurface.Concrete;
            if (flying || armour <= 0f) return HitSurface.Pierced;
            return kinetic && !Penetrates(penetration, armour) ? HitSurface.Metal : HitSurface.Pierced;
        }

        // ------------------------------------------------------------------------------------------------ the mix

        /// <summary>Where the camera-distance falloff starts (m): nearer than this a sound is at full level.</summary>
        public const float RefDistance = 25f;

        /// <summary>How much of the camera's height counts in its distance to a sound.</summary>
        public const float HeightShare = 0.5f;

        /// <summary>
        /// The camera-distance falloff: a soft inverse-distance curve (-4.2 dB a doubling, as a top-down view wants: the
        /// whole screen stays audible) on the distance from the camera (ground distance and a share of its height), times an
        /// edge fade to nothing at the hearing reach. 0-1, falling with distance and with height.
        /// </summary>
        public static float Falloff(float ground, float height, float reach)
        {
            if (reach <= 0f) return 0f;
            var d = Mathf.Sqrt(ground * ground + height * HeightShare * height * HeightShare);
            var near = Mathf.Pow(RefDistance / Mathf.Max(RefDistance, d), 0.7f);
            var edge = Mathf.Clamp01(1f - ground / reach);
            return near * edge * edge * (3f - 2f * edge);
        }

        /// <summary>The Effects compressor: from this summed RMS of the effect voices (linear) it turns the group down.</summary>
        public const float CompressorThreshold = 0.3f;

        /// <summary>The compressor's ratio over its threshold.</summary>
        public const float CompressorRatio = 3f;

        /// <summary>The compressor's gain for a summed level (1 under the threshold; the ratio over it).</summary>
        public static float CompressorGain(float level)
        {
            if (level <= CompressorThreshold) return 1f;
            var over = level / CompressorThreshold;
            return Mathf.Pow(over, 1f / CompressorRatio - 1f);
        }

        /// <summary>The output limiter's ceiling (linear, -1 dBFS).</summary>
        public const float LimiterCeiling = 0.89f;

        /// <summary>A group's volume under the master (Settings): effects, music, dialogue; the interface at full.</summary>
        public static float Gain(AudioGroup group) => group switch
        {
            AudioGroup.Effects => MatchSettings.EffectsVolume,
            AudioGroup.Music => MatchSettings.MusicVolume,
            AudioGroup.Dialogue => MatchSettings.DialogueVolume,
            _ => 1f,
        };

        /// <summary>Parses envelopes.txt: "clip v0 v1 ..." (RMS x1000 at 50 Hz) into linear RMS by clip name.</summary>
        public static Dictionary<string, float[]> ParseEnvelopes(string text)
        {
            var map = new Dictionary<string, float[]>();
            if (string.IsNullOrEmpty(text)) return map;
            foreach (var raw in text.Split('\n'))
            {
                var line = raw.Trim();
                if (line.Length == 0 || line[0] == '#') continue;
                var parts = line.Split(' ');
                var values = new float[parts.Length - 1];
                for (var i = 1; i < parts.Length; i++)
                    values[i - 1] = int.TryParse(parts[i], out var v) ? v / 1000f : 0f;
                map[parts[0]] = values;
            }
            return map;
        }

        /// <summary>The envelopes' rate (Hz).</summary>
        public const int EnvelopeRate = 50;
    }

    /// <summary>
    /// Fix pass L7: the match-wide rate cap on metal hits: a bucket of <see cref="Burst"/> refilled at <see cref="PerSecond"/>,
    /// and never two within <see cref="MinGap"/>. A hit over the cap plays nothing (the sound of a run of glancing rounds is
    /// the first few).
    /// </summary>
    internal sealed class MetalCap
    {
        public const float PerSecond = 2.5f;
        public const float Burst = 3f;
        public const float MinGap = 0.12f;

        private float _tokens = Burst;
        private float _last = -100f;
        private float _at = -100f;

        /// <summary>True (and one taken) when a metal hit may play at <paramref name="now"/> (s).</summary>
        public bool TryTake(float now)
        {
            if (_at > -100f) _tokens = Math.Min(Burst, _tokens + (now - _at) * PerSecond);
            _at = now;
            if (now - _last < MinGap || _tokens < 1f) return false;
            _tokens -= 1f;
            _last = now;
            return true;
        }
    }
}
