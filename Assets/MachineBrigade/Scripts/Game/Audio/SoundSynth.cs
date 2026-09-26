using System;
using UnityEngine;
using Random = System.Random;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// Procedural sound effects: every clip is synthesised from filtered noise and decaying
    /// oscillators at startup, so the game ships without audio files. Each recipe takes a seed
    /// so several variants of the same sound can be made.
    /// </summary>
    public static class SoundSynth
    {
        public const int Rate = 22050;

        /// <summary>Tank gun: a sharp crack, a heavy low boom and a rolling tail.</summary>
        public static AudioClip Cannon(int seed, float weight = 1f)
        {
            var rng = new Random(seed);
            var length = 1.1f + 0.5f * weight;
            var data = new float[(int)(Rate * length)];
            var low = new OnePole(0.06f);
            var body = new OnePole(0.25f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var crack = noise * Env(t, 0.001f, 0.035f) * 0.9f;
                var boom = low.Next(noise) * 3.2f * Env(t, 0.004f, 0.28f * weight);
                var sub = Mathf.Sin(2f * Mathf.PI * (48f + 30f * Mathf.Exp(-t * 18f)) * t) * Env(t, 0.003f, 0.22f * weight) * 0.8f;
                var tail = body.Next(noise) * 0.35f * Env(t, 0.05f, 0.6f * weight);
                data[i] = crack + boom + sub + tail;
            }
            return Finish($"cannon_{seed}", data, 0.9f);
        }

        /// <summary>Machine-gun burst: a few rapid, bright clicks.</summary>
        public static AudioClip MachineGun(int seed, int rounds = 3)
        {
            var rng = new Random(seed);
            const float spacing = 0.065f;
            var data = new float[(int)(Rate * (spacing * rounds + 0.25f))];
            var band = new OnePole(0.35f);
            var low = new OnePole(0.08f);
            for (var r = 0; r < rounds; r++)
            {
                var start = (int)(Rate * (r * spacing + rng.NextDouble() * 0.008));
                for (var i = 0; i < Rate * 0.18f && start + i < data.Length; i++)
                {
                    var t = i / (float)Rate;
                    var noise = Noise(rng);
                    var bright = (noise - band.Next(noise)) * Env(t, 0.0005f, 0.02f);
                    var thump = low.Next(noise) * 2f * Env(t, 0.001f, 0.05f);
                    data[start + i] += (bright * 0.8f + thump) * (0.85f + 0.3f * (float)rng.NextDouble());
                }
            }
            return Finish($"mg_{seed}", data, 0.7f);
        }

        /// <summary>Explosion: dense low roar, a pressure thump and scattered crackle.</summary>
        public static AudioClip Explosion(int seed, float size)
        {
            var rng = new Random(seed);
            var length = 1.2f + 1.6f * size;
            var data = new float[(int)(Rate * length)];
            var roar = new OnePole(0.03f + 0.02f * (1f - size));
            var mid = new OnePole(0.12f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var body = roar.Next(noise) * 5f * Env(t, 0.006f, 0.35f + 0.6f * size);
                var thump = Mathf.Sin(2f * Mathf.PI * (38f + 50f * Mathf.Exp(-t * 10f)) * t) * Env(t, 0.004f, 0.3f + 0.3f * size);
                var grit = mid.Next(noise) * 0.9f * Env(t, 0.002f, 0.12f + 0.2f * size);
                var crackle = rng.NextDouble() < 0.0025 * (1f - t / length) ? (float)(rng.NextDouble() * 2 - 1) * 0.6f : 0f;
                data[i] = body + thump * (0.8f + 0.4f * size) + grit + crackle;
            }
            return Finish($"explosion_{seed}", data, 0.95f);
        }

        /// <summary>Tumbling debris and falling masonry after a building collapses.</summary>
        public static AudioClip Collapse(int seed)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * 2.4f)];
            var low = new OnePole(0.05f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var rumble = low.Next(noise) * 3f * Env(t, 0.05f, 1.1f);
                var knock = rng.NextDouble() < 0.004 * Mathf.Exp(-t * 1.2f) ? (float)(rng.NextDouble() * 2 - 1) : 0f;
                data[i] = rumble + knock * 0.7f;
            }
            return Finish($"collapse_{seed}", data, 0.8f);
        }

        /// <summary>Soft, looping wind bed with slow gusts.</summary>
        public static AudioClip Wind(int seed)
        {
            var rng = new Random(seed);
            var data = new float[Rate * 8];
            var low = new OnePole(0.015f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var gust = 0.6f + 0.4f * Mathf.Sin(t * Mathf.PI * 2f / 8f) * Mathf.Sin(t * 0.9f + 1f);
                data[i] = low.Next(Noise(rng)) * 4f * gust;
            }
            // Cross-fade the ends so the loop has no click.
            const int fade = Rate / 2;
            for (var i = 0; i < fade; i++)
            {
                var k = i / (float)fade;
                data[i] = data[i] * k + data[data.Length - fade + i] * (1f - k);
            }
            Array.Resize(ref data, data.Length - fade);
            return Finish($"wind_{seed}", data, 0.5f);
        }

        /// <summary>Missile or rocket leaving its tube: an ignition pop and a rising, fading whoosh.</summary>
        public static AudioClip Launch(int seed, float length = 1.1f)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * length)];
            var band = new OnePole(0.25f);
            var low = new OnePole(0.05f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var pop = low.Next(noise) * 2.5f * Env(t, 0.002f, 0.06f);
                // The hiss brightens as the motor speeds away, then fades with distance.
                var hiss = (noise - band.Next(noise) * (1f - Mathf.Clamp01(t * 2f))) * Env(t, 0.03f, length * 0.45f) * 0.8f;
                data[i] = pop + hiss;
            }
            return Finish($"launch_{seed}", data, 0.8f);
        }

        /// <summary>Anti-aircraft gun: a hard crack with a short mid-range thump.</summary>
        public static AudioClip Flak(int seed)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * 0.45f)];
            var mid = new OnePole(0.15f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                data[i] = noise * Env(t, 0.0005f, 0.012f) * 1.1f + mid.Next(noise) * 2.2f * Env(t, 0.002f, 0.07f);
            }
            return Finish($"flak_{seed}", data, 0.75f);
        }

        /// <summary>Flamethrower gout: a rough roar of band-limited noise.</summary>
        public static AudioClip Flame(int seed)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * 0.55f)];
            var low = new OnePole(0.09f);
            var high = new OnePole(0.4f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var roar = (high.Next(noise) - low.Next(noise)) * (0.7f + 0.3f * Mathf.Sin(t * 90f));
                data[i] = roar * Env(t, 0.03f, 0.25f);
            }
            return Finish($"flame_{seed}", data, 0.6f);
        }

        /// <summary>Strike jet screaming overhead: a roar that swells and drops in pitch as it passes.</summary>
        public static AudioClip JetPass(int seed)
        {
            var rng = new Random(seed);
            var length = 3.2f;
            var data = new float[(int)(Rate * length)];
            var low = new OnePole(0.04f);
            var band = new OnePole(0.2f);
            var phase = 0f;
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var near = Mathf.Exp(-Mathf.Pow((t - 1.3f) / 0.55f, 2f));
                var freq = Mathf.Lerp(900f, 420f, Mathf.Clamp01((t - 0.9f) / 0.9f));
                phase += 2f * Mathf.PI * freq / Rate;
                var whine = Mathf.Sin(phase) * 0.15f;
                var roar = low.Next(noise) * 3f + (noise - band.Next(noise)) * 0.5f;
                data[i] = (roar + whine) * (0.15f + near) * Mathf.Clamp01(t * 3f) * Mathf.Clamp01((length - t) * 2f);
            }
            return Finish($"jet_{seed}", data, 0.85f);
        }

        /// <summary>Helicopter rotor loop: blade slap at about 18 Hz over a turbine hum.</summary>
        public static AudioClip Rotor(int seed)
        {
            var rng = new Random(seed);
            const float slap = 18f;
            var data = new float[(int)(Rate * 2f / slap) * (int)slap];
            var low = new OnePole(0.06f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var beat = t * slap % 1f;
                var thump = Mathf.Exp(-beat * 14f);
                data[i] = low.Next(Noise(rng)) * 3f * (0.3f + thump) + Mathf.Sin(2f * Mathf.PI * 170f * t) * 0.05f;
            }
            return Finish($"rotor_{seed}", data, 0.55f);
        }

        /// <summary>Incoming-strike alarm: two short falling tones.</summary>
        public static AudioClip Warning()
        {
            var data = new float[(int)(Rate * 0.7f)];
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var first = t < 0.3f;
                var local = first ? t : t - 0.35f;
                if (!first && t < 0.35f) continue;
                var freq = (first ? 880f : 660f) - local * 200f;
                data[i] = Mathf.Sign(Mathf.Sin(2f * Mathf.PI * freq * t)) * 0.4f * Env(local, 0.005f, 0.12f);
            }
            return Finish("warning", data, 0.45f);
        }

        /// <summary>Radio chime: rising notes for good news (captured), falling for bad (lost).</summary>
        public static AudioClip Chime(bool rising)
        {
            var notes = rising ? new[] { 523f, 659f, 784f } : new[] { 587f, 466f, 349f };
            var data = new float[(int)(Rate * 0.75f)];
            for (var n = 0; n < notes.Length; n++)
            {
                var start = (int)(Rate * n * 0.12f);
                for (var i = 0; start + i < data.Length; i++)
                {
                    var t = i / (float)Rate;
                    data[start + i] += (Mathf.Sin(2f * Mathf.PI * notes[n] * t) + 0.3f * Mathf.Sin(4f * Mathf.PI * notes[n] * t)) *
                                       Env(t, 0.004f, 0.22f) * 0.5f;
                }
            }
            return Finish(rising ? "chime_up" : "chime_down", data, 0.45f);
        }

        /// <summary>Rain loop: bright hiss with scattered droplet ticks.</summary>
        public static AudioClip Rain(int seed)
        {
            var rng = new Random(seed);
            var data = new float[Rate * 4];
            var low = new OnePole(0.2f);
            for (var i = 0; i < data.Length; i++)
            {
                var noise = Noise(rng);
                var hiss = (noise - low.Next(noise)) * 0.6f;
                var drop = rng.NextDouble() < 0.004 ? (float)(rng.NextDouble() * 2 - 1) * 0.8f : 0f;
                data[i] = hiss + drop;
            }
            const int fade = Rate / 4;
            for (var i = 0; i < fade; i++)
            {
                var k = i / (float)fade;
                data[i] = data[i] * k + data[data.Length - fade + i] * (1f - k);
            }
            Array.Resize(ref data, data.Length - fade);
            return Finish($"rain_{seed}", data, 0.45f);
        }

        /// <summary>Thunder: a crack, then a long rolling rumble.</summary>
        public static AudioClip Thunder(int seed)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * 4.5f)];
            var low = new OnePole(0.02f);
            var mid = new OnePole(0.1f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var roll = 0.6f + 0.4f * Mathf.Sin(t * 5.3f) * Mathf.Sin(t * 2.1f + 1f);
                data[i] = mid.Next(noise) * 1.6f * Env(t, 0.005f, 0.25f) + low.Next(noise) * 6f * Env(t, 0.25f, 1.6f) * roll;
            }
            return Finish($"thunder_{seed}", data, 0.9f);
        }

        /// <summary>Short UI tick.</summary>
        public static AudioClip Click()
        {
            var data = new float[(int)(Rate * 0.05f)];
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                data[i] = Mathf.Sin(2f * Mathf.PI * 1800f * t) * Env(t, 0.0005f, 0.012f);
            }
            return Finish("click", data, 0.5f);
        }

        private static float Noise(Random rng) => (float)(rng.NextDouble() * 2 - 1);

        /// <summary>Linear attack then exponential decay (decay is the time constant).</summary>
        private static float Env(float t, float attack, float decay) =>
            t < attack ? t / attack : Mathf.Exp(-(t - attack) / Mathf.Max(decay, 1e-4f));

        private static AudioClip Finish(string name, float[] data, float peak)
        {
            var max = 1e-5f;
            foreach (var v in data) max = Mathf.Max(max, Mathf.Abs(v));
            var gain = peak / max;
            for (var i = 0; i < data.Length; i++) data[i] = (float)Math.Tanh(data[i] * gain * 1.2f); // soft clip
            var clip = AudioClip.Create(name, data.Length, 1, Rate, false);
            clip.SetData(data, 0);
            return clip;
        }

        /// <summary>One-pole low-pass filter; alpha near 0 keeps only the lows.</summary>
        private struct OnePole
        {
            private readonly float _alpha;
            private float _state;

            public OnePole(float alpha)
            {
                _alpha = alpha;
                _state = 0f;
            }

            public float Next(float input)
            {
                _state += _alpha * (input - _state);
                return _state;
            }
        }
    }
}
