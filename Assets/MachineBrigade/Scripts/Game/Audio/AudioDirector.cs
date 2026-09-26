using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// Plays the battle's sounds from simulation events. Sounds are panned by their position on
    /// screen and fade with distance from the camera focus, which suits the top-down view better
    /// than true 3D audio. Each sound type has a short cooldown so a machine-gun duel cannot
    /// flood the mixer, and a fixed pool of sources bounds the cost.
    /// </summary>
    public sealed class AudioDirector : IDisposable
    {
        private enum Sound { MachineGun, Cannon, HeavyCannon, Howitzer, ExplosionSmall, ExplosionLarge, ExplosionHuge, Collapse }

        private const int Voices = 20;

        private readonly GameObject _root;
        private readonly RtsCamera _camera;
        private readonly AudioSource[] _voices = new AudioSource[Voices];
        private readonly AudioSource _ambient;
        private readonly AudioSource _ui;
        private readonly Dictionary<Sound, AudioClip[]> _clips = new();
        private readonly Dictionary<Sound, float> _lastPlayed = new();
        private readonly List<AudioClip> _owned = new();
        private readonly System.Random _rng = new(5);
        private int _next;

        public AudioDirector(RtsCamera camera, Transform parent)
        {
            _camera = camera;
            _root = new GameObject("Audio");
            _root.transform.SetParent(parent, false);

            _clips[Sound.MachineGun] = Make(i => SoundSynth.MachineGun(100 + i), 3);
            _clips[Sound.Cannon] = Make(i => SoundSynth.Cannon(200 + i, 0.8f), 3);
            _clips[Sound.HeavyCannon] = Make(i => SoundSynth.Cannon(300 + i, 1.2f), 3);
            _clips[Sound.Howitzer] = Make(i => SoundSynth.Cannon(400 + i, 1.6f), 2);
            _clips[Sound.ExplosionSmall] = Make(i => SoundSynth.Explosion(500 + i, 0.25f), 3);
            _clips[Sound.ExplosionLarge] = Make(i => SoundSynth.Explosion(600 + i, 0.65f), 3);
            _clips[Sound.ExplosionHuge] = Make(i => SoundSynth.Explosion(700 + i, 1f), 2);
            _clips[Sound.Collapse] = Make(i => SoundSynth.Collapse(800 + i), 2);

            for (var i = 0; i < Voices; i++) _voices[i] = NewSource($"Voice {i}");
            _ambient = NewSource("Wind");
            _ambient.clip = Own(SoundSynth.Wind(9));
            _ambient.loop = true;
            _ambient.volume = 0.16f;
            _ambient.Play();
            _ui = NewSource("UI");
            _ui.clip = Own(SoundSynth.Click());
        }

        public void Consume(IReadOnlyList<SimEvent> events)
        {
            foreach (var e in events)
            {
                switch (e.Kind)
                {
                    case SimEventKind.WeaponFired:
                        var sound = e.DefId switch
                        {
                            "mg_jeep" => Sound.MachineGun,
                            "gun_120mm" => Sound.HeavyCannon,
                            "howitzer" => Sound.Howitzer,
                            _ => Sound.Cannon,
                        };
                        Play(sound, e.Position, sound == Sound.MachineGun ? 0.55f : 0.8f, sound == Sound.MachineGun ? 0.09f : 0.05f);
                        break;
                    case SimEventKind.ProjectileImpact when e.Tier >= ExplosionTier.Medium:
                        Play(e.Tier >= ExplosionTier.Large ? Sound.ExplosionLarge : Sound.ExplosionSmall, e.Position, 0.7f, 0.05f);
                        break;
                    case SimEventKind.Explosion:
                        Play(e.Tier >= ExplosionTier.Huge ? Sound.ExplosionHuge : Sound.ExplosionLarge, e.Position, 1f, 0.03f);
                        break;
                    case SimEventKind.VehicleDestroyed:
                        Play(Sound.ExplosionLarge, e.Position, 0.9f, 0.03f);
                        break;
                    case SimEventKind.PropDestroyed:
                        if (e.Value >= 3f) Play(Sound.Collapse, e.Position, 0.9f, 0.2f);
                        break;
                }
            }
        }

        /// <summary>UI feedback; call from button handlers.</summary>
        public void Click() => _ui.PlayOneShot(_ui.clip, 0.35f);

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            foreach (var clip in _owned)
                if (clip != null) Object.Destroy(clip);
        }

        private void Play(Sound sound, System.Numerics.Vector2 at, float volume, float cooldown)
        {
            var now = Time.unscaledTime;
            if (_lastPlayed.TryGetValue(sound, out var last) && now - last < cooldown) return;
            _lastPlayed[sound] = now;

            var world = new Vector3(at.X, 0f, at.Y);
            var focus = _camera.Focus;
            var distance = Vector3.Distance(world, focus);
            var reach = _camera.Zoom * 2.6f + 30f;
            var attenuation = Mathf.Clamp01(1f - distance / reach);
            if (attenuation <= 0.02f) return;

            var screen = _camera.Camera.WorldToViewportPoint(world);
            var voice = _voices[_next];
            _next = (_next + 1) % _voices.Length;
            var clips = _clips[sound];
            voice.clip = clips[_rng.Next(clips.Length)];
            voice.volume = volume * attenuation * attenuation;
            voice.panStereo = Mathf.Clamp((screen.x - 0.5f) * 1.4f, -0.9f, 0.9f);
            voice.pitch = 0.92f + (float)_rng.NextDouble() * 0.16f;
            voice.Play();
        }

        private AudioClip[] Make(Func<int, AudioClip> create, int variants)
        {
            var clips = new AudioClip[variants];
            for (var i = 0; i < variants; i++) clips[i] = Own(create(i));
            return clips;
        }

        private AudioClip Own(AudioClip clip)
        {
            _owned.Add(clip);
            return clip;
        }

        private AudioSource NewSource(string name)
        {
            var go = new GameObject(name);
            go.transform.SetParent(_root.transform, false);
            var source = go.AddComponent<AudioSource>();
            source.playOnAwake = false;
            source.spatialBlend = 0f;
            return source;
        }
    }
}
