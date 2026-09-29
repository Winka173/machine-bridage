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

        /// <summary>
        /// Test feedback 19P: a seamless 2 s laser-beam hum: a low sawtooth drone with its octave, a bright
        /// shimmer fluttering over it and a faint crackle of burning, every partial a whole number of cycles
        /// over the loop so it joins without a click.
        /// </summary>
        public static AudioClip BeamLoop(int seed)
        {
            var rng = new Random(seed);
            const float length = 2f;
            var data = new float[(int)(Rate * length)];
            var hiss = new OnePole(0.5f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var hum = Saw(110f * t) * 0.32f + Saw(220f * t + 0.3f) * 0.16f + Mathf.Sin(2f * Mathf.PI * 55f * t) * 0.22f;
                // The shimmer's pitch wanders (4 Hz and 7 Hz), the way a power supply sings under load.
                var shimmer = Mathf.Sin(2f * Mathf.PI * (1760f * t + 3f * Mathf.Sin(2f * Mathf.PI * 4f * t))) *
                              (0.07f + 0.05f * Mathf.Sin(2f * Mathf.PI * 7f * t));
                var noise = Noise(rng);
                var crackle = (noise - hiss.Next(noise)) * (rng.NextDouble() < 0.004 ? 0.9f : 0.05f);
                data[i] = hum * (0.85f + 0.15f * Mathf.Sin(2f * Mathf.PI * 3f * t)) + shimmer + crackle;
            }
            return Finish($"beam_loop_{seed}", data, 0.55f);
        }

        /// <summary>A beam igniting: a rising whine from 300 Hz to 2.4 kHz over a quarter second, a zap, the hum swelling under it.</summary>
        public static AudioClip BeamStart(int seed)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * 0.45f)];
            var phase = 0f;
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var rise = Mathf.Clamp01(t / 0.25f);
                phase += (300f + 2100f * rise * rise) / Rate;
                var whine = Mathf.Sin(2f * Mathf.PI * phase) * 0.35f * Env(t, 0.02f, 0.3f);
                var zap = Noise(rng) * Mathf.Exp(-Mathf.Abs(t - 0.24f) * 90f) * 0.6f;
                var hum = Saw(110f * t) * 0.25f * Mathf.Clamp01((t - 0.2f) * 8f);
                data[i] = whine + zap + hum * Mathf.Clamp01((0.45f - t) * 8f);
            }
            return Finish($"beam_start_{seed}", data, 0.6f);
        }

        /// <summary>
        /// An FPV drone lifting off its rack: the high buzz of four small props (a detuned sawtooth pair near
        /// 190 Hz with a fast warble), climbing in pitch as it throttles up, fading as it flies off.
        /// </summary>
        public static AudioClip DroneBuzz(int seed)
        {
            var rng = new Random(seed);
            var data = new float[(int)(Rate * 1.3f)];
            var p1 = (float)rng.NextDouble();
            var p2 = (float)rng.NextDouble();
            var baseFreq = 170f + 40f * (float)rng.NextDouble();
            var hiss = new OnePole(0.3f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var throttle = 1f + 0.45f * Mathf.Clamp01(t / 0.35f) + 0.05f * Mathf.Sin(2f * Mathf.PI * 11f * t);
                p1 += baseFreq * throttle / Rate;
                p2 += baseFreq * 1.013f * throttle / Rate;
                var props = (Saw(p1) + Saw(p2)) * 0.28f * (0.8f + 0.2f * Mathf.Sin(2f * Mathf.PI * 37f * t));
                var noise = Noise(rng);
                var air = (noise - hiss.Next(noise)) * 0.12f;
                data[i] = (props + air) * Env(t, 0.06f, 0.75f);
            }
            return Finish($"drone_buzz_{seed}", data, 0.55f);
        }

        /// <summary>A sawtooth in -1..1 at <paramref name="cycles"/> (the phase in whole cycles).</summary>
        private static float Saw(float cycles) => 2f * (cycles - Mathf.Floor(cycles)) - 1f;

        /// <summary>Incoming-strike alarm: two short falling tones.</summary>
        /// <summary>
        /// A seamless 9.6 s war-drum loop at 100 bpm for boss fights: a deep kick on every beat,
        /// taiko toms answering, a low droning bass that swells each bar, and a metal clang every
        /// second bar.
        /// </summary>
        public static AudioClip WarDrums(int seed)
        {
            var rng = new Random(seed);
            const float beat = 0.6f;
            var length = beat * 16f;
            var data = new float[(int)(Rate * length)];
            for (var b = 0; b < 16; b++)
            {
                var start = (int)(Rate * b * beat);
                // Kick: a sine that drops from 90 to 42 Hz.
                for (var i = 0; start + i < data.Length && i < Rate * 0.5f; i++)
                {
                    var t = i / (float)Rate;
                    var freq = 42f + 48f * Mathf.Exp(-t * 18f);
                    data[start + i] += Mathf.Sin(2f * Mathf.PI * freq * t) * Env(t, 0.002f, 0.16f) * 0.9f;
                }
                // Toms on the off-beats, higher on the last beat of each bar.
                var tomAt = start + (int)(Rate * beat * 0.5f);
                var tomFreq = b % 4 == 3 ? 150f : 110f;
                for (var i = 0; tomAt + i < data.Length && i < Rate * 0.35f; i++)
                {
                    var t = i / (float)Rate;
                    data[tomAt + i] += (Mathf.Sin(2f * Mathf.PI * tomFreq * t * (1f - t * 0.3f)) + Noise(rng) * 0.25f) *
                                       Env(t, 0.003f, 0.09f) * 0.45f;
                }
                // A metal clang every second bar.
                if (b % 8 == 0)
                    for (var i = 0; start + i < data.Length && i < Rate * 0.9f; i++)
                    {
                        var t = i / (float)Rate;
                        data[start + i] += (Mathf.Sin(2f * Mathf.PI * 587f * t) + 0.6f * Mathf.Sin(2f * Mathf.PI * 911f * t) +
                                            0.4f * Mathf.Sin(2f * Mathf.PI * 1433f * t)) * Env(t, 0.001f, 0.35f) * 0.18f;
                    }
            }
            // Droning bass under it all, swelling with each bar and fading to zero at the loop point.
            var low = new OnePole(0.03f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var bar = t / (beat * 4f) % 1f;
                var swell = 0.35f + 0.65f * Mathf.Sin(bar * Mathf.PI);
                var saw = 2f * (55f * t % 1f) - 1f;
                data[i] += low.Next(saw) * swell * 0.55f;
            }
            return Finish("war_drums", data, 0.6f);
        }

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

        /// <summary>
        /// An incoming shell's whistle: a falling tone with a breathy edge, swelling as it comes
        /// down and cut off at the moment it lands (the blast is its own sound).
        /// </summary>
        public static AudioClip Whistle(int seed)
        {
            var rng = new Random(seed);
            const float length = 1.25f;
            var data = new float[(int)(Rate * length)];
            var high = 1450f + 350f * (float)rng.NextDouble();
            var low = 480f + 160f * (float)rng.NextDouble();
            var air = new OnePole(0.45f);
            var phase = 0f;
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var k = t / length;
                var frequency = Mathf.Lerp(high, low, k * k * 0.55f + k * 0.45f);
                phase += 2f * Mathf.PI * frequency / Rate;
                var tone = Mathf.Sin(phase) + 0.22f * Mathf.Sin(phase * 2f + 0.4f);
                var breath = air.Next(Noise(rng)) * 0.3f;
                var swell = 0.12f + 0.88f * k * k;
                var cut = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.93f, 1f, k));
                data[i] = (tone * 0.55f + breath) * swell * cut;
            }
            return Finish($"whistle_{seed}", data, 0.7f);
        }

        /// <summary>
        /// A radio report: the squelch of the handset keying, two soft notes through a radio's
        /// narrow band (rising for good news, falling for bad), and the squelch letting go.
        /// </summary>
        public static AudioClip Radio(bool good)
        {
            var rng = new Random(good ? 61 : 67);
            var notes = good ? new[] { 660f, 880f } : new[] { 587f, 440f };
            const float length = 0.66f;
            var data = new float[(int)(Rate * length)];
            var band = new OnePole(0.32f);
            var floor = new OnePole(0.04f);
            for (var i = 0; i < data.Length; i++)
            {
                var t = i / (float)Rate;
                var noise = Noise(rng);
                var squelch = noise * (Env(t, 0.002f, 0.035f) * 0.55f + (t > 0.55f ? Env(t - 0.55f, 0.002f, 0.04f) * 0.4f : 0f));
                var tone = 0f;
                for (var n = 0; n < notes.Length; n++)
                {
                    var start = 0.08f + n * 0.17f;
                    if (t < start) continue;
                    var local = t - start;
                    tone += (Mathf.Sin(2f * Mathf.PI * notes[n] * local) + 0.3f * Mathf.Sin(4f * Mathf.PI * notes[n] * local)) * Env(local, 0.01f, 0.16f);
                }
                // A crude band-pass: a radio has no deep bass and no sparkle.
                var x = band.Next(squelch + tone * 0.4f);
                data[i] = x - floor.Next(x);
            }
            return Finish(good ? "radio_good" : "radio_bad", data, 0.6f);
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
