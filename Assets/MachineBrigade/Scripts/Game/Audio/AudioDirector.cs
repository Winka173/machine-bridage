using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Views;
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
        private enum Sound
        {
            MachineGun, Autocannon, Cannon, HeavyCannon, Howitzer, Launch, Flak, Flame,
            ExplosionSmall, ExplosionLarge, ExplosionHuge, Collapse, Jet,
        }

        private const int Voices = 24;

        private readonly GameObject _root;
        private readonly RtsCamera _camera;
        private readonly Catalog _catalog;
        private readonly int _playerTeam;
        private readonly AudioSource[] _voices = new AudioSource[Voices];
        private readonly AudioSource _ambient, _rotor, _ui, _rain;
        private readonly AudioClip[] _thunder;
        private readonly List<float> _thunderAt = new();
        private readonly AudioClip _warning, _captured, _lost;
        private readonly Dictionary<Sound, AudioClip[]> _clips = new();
        private readonly Dictionary<Sound, float> _lastPlayed = new();
        private readonly List<AudioClip> _owned = new();
        private readonly System.Random _rng = new(5);
        private int _next;

        public AudioDirector(RtsCamera camera, Transform parent, Catalog catalog, int playerTeam)
        {
            _camera = camera;
            _catalog = catalog;
            _playerTeam = playerTeam;
            _root = new GameObject("Audio");
            _root.transform.SetParent(parent, false);

            _clips[Sound.MachineGun] = Make(i => SoundSynth.MachineGun(100 + i), 3);
            _clips[Sound.Autocannon] = Make(i => SoundSynth.Cannon(150 + i, 0.35f), 3);
            _clips[Sound.Cannon] = Make(i => SoundSynth.Cannon(200 + i, 0.8f), 3);
            _clips[Sound.HeavyCannon] = Make(i => SoundSynth.Cannon(300 + i, 1.2f), 3);
            _clips[Sound.Howitzer] = Make(i => SoundSynth.Cannon(400 + i, 1.6f), 2);
            _clips[Sound.Launch] = Make(i => SoundSynth.Launch(450 + i), 3);
            _clips[Sound.Flak] = Make(i => SoundSynth.Flak(470 + i), 3);
            _clips[Sound.Flame] = Make(i => SoundSynth.Flame(490 + i), 2);
            _clips[Sound.ExplosionSmall] = Make(i => SoundSynth.Explosion(500 + i, 0.25f), 3);
            _clips[Sound.ExplosionLarge] = Make(i => SoundSynth.Explosion(600 + i, 0.65f), 3);
            _clips[Sound.ExplosionHuge] = Make(i => SoundSynth.Explosion(700 + i, 1f), 2);
            _clips[Sound.Collapse] = Make(i => SoundSynth.Collapse(800 + i), 2);
            _clips[Sound.Jet] = Make(i => SoundSynth.JetPass(900 + i), 2);
            _warning = Own(SoundSynth.Warning());
            _captured = Own(SoundSynth.Chime(true));
            _lost = Own(SoundSynth.Chime(false));

            for (var i = 0; i < Voices; i++) _voices[i] = NewSource($"Voice {i}");
            _ambient = NewSource("Wind");
            _ambient.clip = Own(SoundSynth.Wind(9));
            _ambient.loop = true;
            _ambient.volume = 0.16f;
            _ambient.Play();
            _rotor = NewSource("Rotors");
            _rotor.clip = Own(SoundSynth.Rotor(3));
            _rotor.loop = true;
            _rotor.volume = 0f;
            _rotor.Play();
            _rain = NewSource("Rain");
            _rain.clip = Own(SoundSynth.Rain(12));
            _rain.loop = true;
            _rain.volume = 0f;
            _thunder = Make(i => SoundSynth.Thunder(40 + i), 2);
            _ui = NewSource("UI");
            _ui.clip = Own(SoundSynth.Click());
        }

        /// <summary>Extra wind for rain and storms.</summary>
        public float AmbientLevel
        {
            set => _ambient.volume = value;
        }

        /// <summary>Rain loop level (0 = dry).</summary>
        public float RainLevel
        {
            set
            {
                _rain.volume = value;
                if (value > 0f && !_rain.isPlaying) _rain.Play();
                else if (value <= 0f && _rain.isPlaying) _rain.Stop();
            }
        }

        /// <summary>Thunder after a lightning flash, delayed by the distance of the strike.</summary>
        public void Thunder(float delay) => _thunderAt.Add(Time.unscaledTime + delay);

        public void Consume(IReadOnlyList<SimEvent> events)
        {
            foreach (var e in events)
            {
                switch (e.Kind)
                {
                    case SimEventKind.WeaponFired:
                        var weapon = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var w) ? w : null;
                        var sound = WeaponSound(weapon);
                        var light = sound is Sound.MachineGun or Sound.Autocannon or Sound.Flak;
                        Play(sound, e.Position, light ? 0.5f : 0.8f, light ? 0.08f : 0.05f);
                        break;
                    case SimEventKind.ProjectileImpact when e.Tier >= ExplosionTier.Medium:
                        Play(e.Tier >= ExplosionTier.Large ? Sound.ExplosionLarge : Sound.ExplosionSmall, e.Position, 0.7f, 0.05f);
                        break;
                    case SimEventKind.Explosion:
                        Play(e.Tier >= ExplosionTier.Huge ? Sound.ExplosionHuge : Sound.ExplosionLarge, e.Position, 1f, 0.03f);
                        break;
                    case SimEventKind.StrikeImpact:
                        Play(e.Tier >= ExplosionTier.Huge ? Sound.ExplosionHuge : Sound.ExplosionLarge, e.Position, 1f, 0.02f);
                        break;
                    case SimEventKind.AircraftPass:
                        Play(Sound.Jet, e.Target, 1f, 0.5f, reachBonus: 80f);
                        break;
                    case SimEventKind.StrikeWarning when _playerTeam >= 0 && e.Team != _playerTeam:
                        _ui.PlayOneShot(_warning, 0.6f);
                        break;
                    case SimEventKind.PointCaptured when _playerTeam >= 0:
                        if (e.Team == _playerTeam) _ui.PlayOneShot(_captured, 0.5f);
                        else if (e.Team >= 0) _ui.PlayOneShot(_lost, 0.5f);
                        break;
                    case SimEventKind.DeploymentQueued when e.Team == _playerTeam:
                        _ui.PlayOneShot(_ui.clip, 0.5f);
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

        /// <summary>Per frame: helicopter rotors get louder as aircraft come near the view.</summary>
        public void Tick(ViewRegistry views)
        {
            var nearest = float.MaxValue;
            foreach (var view in views.All)
                if (view.Flying) nearest = Mathf.Min(nearest, Vector3.Distance(view.Position, _camera.Focus));
            var reach = _camera.Zoom * 2.6f + 30f;
            var target = nearest < float.MaxValue ? Mathf.Clamp01(1f - nearest / reach) * 0.55f : 0f;
            _rotor.volume = Mathf.MoveTowards(_rotor.volume, target, Time.unscaledDeltaTime * 0.8f);
            for (var i = _thunderAt.Count - 1; i >= 0; i--)
            {
                if (Time.unscaledTime < _thunderAt[i]) continue;
                _thunderAt.RemoveAt(i);
                _ui.PlayOneShot(_thunder[_rng.Next(_thunder.Length)], 0.9f);
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

        private static Sound WeaponSound(WeaponDef weapon)
        {
            if (weapon == null) return Sound.Cannon;
            switch (weapon.Projectile)
            {
                case ProjectileKind.Missile:
                case ProjectileKind.Rocket:
                    return Sound.Launch;
                case ProjectileKind.Flame:
                    return Sound.Flame;
                case ProjectileKind.Bullet:
                    return weapon.DamageType == DamageType.Flak ? Sound.Flak : weapon.Damage >= 20f ? Sound.Autocannon : Sound.MachineGun;
            }
            if (weapon.MinRange > 0f) return Sound.Howitzer;
            return weapon.Damage >= 100f ? Sound.HeavyCannon : Sound.Cannon;
        }

        private void Play(Sound sound, System.Numerics.Vector2 at, float volume, float cooldown, float reachBonus = 0f)
        {
            var now = Time.unscaledTime;
            if (_lastPlayed.TryGetValue(sound, out var last) && now - last < cooldown) return;
            _lastPlayed[sound] = now;

            var world = new Vector3(at.X, 0f, at.Y);
            var focus = _camera.Focus;
            var distance = Vector3.Distance(world, focus);
            var reach = _camera.Zoom * 2.6f + 30f + reachBonus;
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
