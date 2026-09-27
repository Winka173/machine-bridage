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
    /// Plays the battle's sounds from simulation events: recorded clips from Resources/Audio (see
    /// CREDITS.md there), with the synthesised ones in <see cref="SoundSynth"/> standing in for
    /// any category that has none. Sounds are panned by their position on screen and fade with
    /// distance from the camera focus, which suits the top-down view better than true 3D audio.
    /// The mix follows the usual game-audio rules (Wwise and FMOD voice management, Battlefield's
    /// distance treatment):
    /// <list type="bullet">
    /// <item>each category keeps a few variants, never the same one twice running, with a little
    /// pitch spread;</item>
    /// <item>each category has a voice limit and a short cooldown, so a machine-gun duel cannot
    /// flood the mixer, and when all voices are busy the least important, quietest one is cut
    /// (a rifle round never cuts a big blast);</item>
    /// <item>far sounds are muffled (a low-pass filter closes with distance), and big blasts far
    /// off arrive a moment late, at the speed of sound;</item>
    /// <item>a big blast ducks the small arms for a moment, so it lands clean;</item>
    /// <item>loops (wind, rain, rotors, jet engines, fires burning near the view, boss drums)
    /// fade with what is near the view.</item>
    /// </list>
    /// </summary>
    public sealed class AudioDirector : IDisposable
    {
        private enum Sound
        {
            MachineGun, Autocannon, Cannon, HeavyCannon, Howitzer, Rocket, Missile, Flak, Flame,
            ExplosionSmall, ExplosionMedium, ExplosionLarge, ExplosionHuge, Collapse, Debris, Impact, Jet, Whistle,
        }

        /// <summary>One category: its clips and how it is mixed.</summary>
        private sealed class Bank
        {
            public AudioClip[] Clips;
            public float Volume;
            public int MaxVoices;
            public float Cooldown;
            public int Priority;
            public float Pitch = 1f;
            public float PitchSpread = 0.08f;

            /// <summary>Ducked by big blasts.</summary>
            public bool Light;

            /// <summary>Arrives late when far off (speed of sound).</summary>
            public bool Delayed;

            public float LastPlayed = -10f;
            private int _last = -1;

            public AudioClip Next(System.Random rng)
            {
                if (Clips.Length == 1) return Clips[0];
                var i = rng.Next(Clips.Length - 1);
                if (_last >= 0 && i >= _last) i++;
                _last = i;
                return Clips[i];
            }
        }

        private sealed class Voice
        {
            public AudioSource Source;
            public AudioLowPassFilter Filter;
            public Bank Bank;
            public float Level;
            public float Started;
        }

        private const int Voices = 32;
        private const float SpeedOfSound = 343f;

        private readonly GameObject _root;
        private readonly RtsCamera _camera;
        private readonly Catalog _catalog;
        private readonly int _playerTeam;
        private readonly Voice[] _voices = new Voice[Voices];
        private readonly AudioSource _ambient, _rotor, _jetLoop, _ui, _rain, _fire, _drums;
        private readonly AudioClip[] _thunder, _clicks;
        private readonly List<float> _thunderAt = new();
        private readonly AudioClip _captured, _lost, _siren;
        private readonly Dictionary<Sound, Bank> _banks = new();
        private readonly List<AudioClip> _owned = new();
        private readonly List<(float at, Sound sound, System.Numerics.Vector2 where, float volume)> _delayed = new();
        private readonly List<(Vector3 at, float until)> _fires = new();
        private readonly System.Random _rng = new(5);
        private float _duckUntil;
        private float _drumsTarget;

        public AudioDirector(RtsCamera camera, Transform parent, Catalog catalog, int playerTeam)
        {
            _camera = camera;
            _catalog = catalog;
            _playerTeam = playerTeam;
            _root = new GameObject("Audio");
            _root.transform.SetParent(parent, false);

            // Category, recorded clips (else synthesised), level, voices, cooldown, priority.
            Add(Sound.MachineGun, "mg", i => SoundSynth.MachineGun(100 + i), 0.42f, 4, 0.07f, 1, light: true);
            Add(Sound.Autocannon, "autocannon", i => SoundSynth.Cannon(150 + i, 0.35f), 0.45f, 3, 0.08f, 2, light: true);
            Add(Sound.Cannon, "cannon", i => SoundSynth.Cannon(200 + i, 0.8f), 0.72f, 4, 0.05f, 3);
            Add(Sound.HeavyCannon, "heavy_cannon", i => SoundSynth.Cannon(300 + i, 1.2f), 0.82f, 3, 0.06f, 4, pitch: 1.08f);
            Add(Sound.Howitzer, "heavy_cannon", i => SoundSynth.Cannon(400 + i, 1.6f), 0.9f, 3, 0.08f, 4, pitch: 0.9f);
            Add(Sound.Rocket, "rocket_launch", i => SoundSynth.Launch(450 + i), 0.55f, 4, 0.06f, 3);
            Add(Sound.Missile, "missile_launch", i => SoundSynth.Launch(460 + i, 1.4f), 0.6f, 3, 0.1f, 3);
            Add(Sound.Flak, "flak", i => SoundSynth.Flak(470 + i), 0.5f, 3, 0.08f, 2, light: true);
            Add(Sound.Flame, "flame", i => SoundSynth.Flame(490 + i), 0.55f, 2, 0.25f, 2);
            Add(Sound.ExplosionSmall, "explosion_small", i => SoundSynth.Explosion(500 + i, 0.25f), 0.55f, 4, 0.05f, 2, delayed: true);
            Add(Sound.ExplosionMedium, "explosion_medium", i => SoundSynth.Explosion(550 + i, 0.45f), 0.72f, 4, 0.05f, 3, delayed: true);
            Add(Sound.ExplosionLarge, "explosion_large", i => SoundSynth.Explosion(600 + i, 0.65f), 0.88f, 3, 0.04f, 4, delayed: true);
            Add(Sound.ExplosionHuge, "explosion_huge", i => SoundSynth.Explosion(700 + i, 1f), 1f, 2, 0.1f, 5, delayed: true);
            Add(Sound.Collapse, "collapse", i => SoundSynth.Collapse(800 + i), 0.85f, 2, 0.3f, 4);
            Add(Sound.Debris, "debris", i => SoundSynth.Collapse(850 + i), 0.45f, 2, 0.12f, 1);
            Add(Sound.Impact, "impact_metal", i => SoundSynth.MachineGun(860 + i, 1), 0.28f, 3, 0.1f, 0, light: true);
            Add(Sound.Jet, "jet_pass", i => SoundSynth.JetPass(900 + i), 0.9f, 2, 0.5f, 4);
            // Incoming shells whistle down onto where they land: the warning is in the world, where
            // the danger is, not a beep from the interface (Company of Heroes and Men of War do the same).
            Add(Sound.Whistle, "whistle", i => SoundSynth.Whistle(950 + i), 0.5f, 3, 0.22f, 3);
            // Points taken and lost come over the radio: a squelch and two soft notes.
            _captured = Own(SoundSynth.Radio(true));
            _lost = Own(SoundSynth.Radio(false));
            _siren = Recorded("siren")?[0];

            for (var i = 0; i < Voices; i++)
            {
                var source = NewSource($"Voice {i}");
                var filter = source.gameObject.AddComponent<AudioLowPassFilter>();
                filter.cutoffFrequency = 22000f;
                _voices[i] = new Voice { Source = source, Filter = filter };
            }
            _ambient = Loop("Wind", "wind_loop", () => SoundSynth.Wind(9));
            _ambient.volume = 0.16f;
            _ambient.Play();
            _rotor = Loop("Rotors", "rotor_loop", () => SoundSynth.Rotor(3));
            _rotor.volume = 0f;
            _rotor.Play();
            // Aeroplanes overhead; the synthesised stand-in is the jet pass, slowed and looped.
            _jetLoop = Loop("Jet Engines", "jet_loop", () => SoundSynth.JetPass(77));
            if (Recorded("jet_loop") == null) _jetLoop.pitch = 0.8f;
            _jetLoop.volume = 0f;
            _rain = Loop("Rain", "rain_loop", () => SoundSynth.Rain(12));
            _rain.volume = 0f;
            _fire = Loop("Fires", "fire_loop", () => SoundSynth.Flame(95));
            _fire.volume = 0f;
            _thunder = Recorded("thunder") ?? Make(i => SoundSynth.Thunder(40 + i), 2);
            _drums = Loop("War Drums", "drums_loop", () => SoundSynth.WarDrums(21));
            _drums.volume = 0f;
            _ui = NewSource("UI");
            _clicks = Recorded("click") ?? new[] { Own(SoundSynth.Click()) };
            _ui.clip = _clicks[0];
            // Menu clicks still sound while the game (and every other source) is paused.
            _ui.ignoreListenerPause = true;
        }

        /// <summary>War drums while a boss is on the field; they fade in and out.</summary>
        public bool BossMusic
        {
            set => _drumsTarget = value ? 0.45f : 0f;
        }

        /// <summary>Extra wind for rain and storms.</summary>
        public float AmbientLevel
        {
            get => _ambient.volume;
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
                        // Bombs are released silently; the blast is the sound.
                        if (weapon != null && weapon.Projectile == ProjectileKind.Bomb) break;
                        Play(WeaponSound(weapon), e.Position, 1f);
                        // Heavy shells on a long flight whistle down onto where they are aimed.
                        if (weapon != null && weapon.MinRange > 0f && weapon.Projectile == ProjectileKind.Shell && e.Value > WhistleLead + 0.2f)
                            Schedule(Sound.Whistle, e.Target, 0.7f, e.Value - WhistleLead);
                        break;
                    case SimEventKind.ProjectileImpact:
                        if (e.Tier >= ExplosionTier.Medium) Play(Blast(e.Tier), e.Position, e.Tier >= ExplosionTier.Huge ? 1f : 0.85f);
                        else Play(Sound.Impact, e.Position, 1f);
                        break;
                    case SimEventKind.Intercepted:
                        Play(Sound.Impact, e.Position, 1f);
                        Play(Sound.ExplosionSmall, e.Position, 0.6f);
                        break;
                    case SimEventKind.Explosion:
                        Play(e.Tier <= ExplosionTier.Small ? Sound.ExplosionSmall : Blast(e.Tier < ExplosionTier.Large ? ExplosionTier.Large : e.Tier),
                            e.Position, 1f);
                        break;
                    case SimEventKind.StrikeImpact:
                        Play(Blast(e.Tier < ExplosionTier.Large ? ExplosionTier.Large : e.Tier), e.Position, 1f);
                        break;
                    case SimEventKind.AircraftPass:
                        Play(Sound.Jet, e.Target, 1f, reachBonus: 80f);
                        break;
                    case SimEventKind.StrikeWarning:
                        // A barrage or a missile whistles down in the last second before it lands
                        // (aircraft strikes announce themselves with their engines; smoke and repairs are quiet).
                        if (_catalog.TryGetSupport(e.DefId, out var strike) && strike.Kind is SupportKind.Barrage or SupportKind.CruiseMissile)
                        {
                            Schedule(Sound.Whistle, e.Position, 1f, e.Value - WhistleLead);
                            // A long barrage keeps coming down: a second whistle halfway through.
                            if (strike.Duration > 1.5f) Schedule(Sound.Whistle, e.Position, 0.85f, e.Value + strike.Duration * 0.5f - WhistleLead);
                        }
                        break;
                    case SimEventKind.FortressAlert when _playerTeam >= 0 && _siren != null:
                        // The fortress's own alarm: heard as far as the fortress is near the view.
                        var alarm = Vector3.Distance(new Vector3(e.Position.X, 0f, e.Position.Y), _camera.Focus);
                        if (alarm < 120f) _ui.PlayOneShot(_siren, 0.28f * (1f - alarm / 120f) + 0.06f);
                        break;
                    case SimEventKind.StageCleared when _playerTeam >= 0:
                        _ui.PlayOneShot(_captured, 0.6f);
                        break;
                    case SimEventKind.PointCaptured when _playerTeam >= 0:
                        if (e.Team == _playerTeam) _ui.PlayOneShot(_captured, 0.5f);
                        else if (e.Team >= 0) _ui.PlayOneShot(_lost, 0.5f);
                        break;
                    case SimEventKind.VehicleDestroyed:
                        Play(Sound.ExplosionLarge, e.Position, 0.9f);
                        Play(Sound.Debris, e.Position, 0.8f);
                        Burn(e.Position, 25f);
                        break;
                    case SimEventKind.PropDestroyed:
                        if (e.Value >= 3f)
                        {
                            Play(Sound.Collapse, e.Position, 0.9f);
                            Burn(e.Position, 30f);
                        }
                        else Play(Sound.Debris, e.Position, 0.7f);
                        break;
                }
            }
        }

        /// <summary>Per frame: loops follow what is near the view, late sounds arrive, ducking eases off.</summary>
        public void Tick(ViewRegistry views)
        {
            var now = Time.unscaledTime;
            if (!Mathf.Approximately(_drums.volume, _drumsTarget))
            {
                _drums.volume = Mathf.MoveTowards(_drums.volume, _drumsTarget, Time.unscaledDeltaTime * 0.25f);
                if (_drums.volume > 0f && !_drums.isPlaying) _drums.Play();
                if (_drums.volume <= 0f && _drums.isPlaying) _drums.Stop();
            }
            // Helicopters drive the rotor loop, aeroplanes the jet loop.
            var nearest = float.MaxValue;
            var nearestJet = float.MaxValue;
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (!view.Flying) continue;
                var distance = Vector3.Distance(view.Position, _camera.Focus);
                if (view.Def.FixedWing) nearestJet = Mathf.Min(nearestJet, distance);
                else nearest = Mathf.Min(nearest, distance);
            }
            var reach = Reach(0f);
            var target = nearest < float.MaxValue ? Mathf.Clamp01(1f - nearest / reach) * 0.5f : 0f;
            _rotor.volume = Mathf.MoveTowards(_rotor.volume, target, Time.unscaledDeltaTime * 0.8f);
            var jetTarget = nearestJet < float.MaxValue ? Mathf.Clamp01(1f - nearestJet / (reach + 20f)) * 0.4f : 0f;
            _jetLoop.volume = Mathf.MoveTowards(_jetLoop.volume, jetTarget, Time.unscaledDeltaTime * 0.8f);
            if (_jetLoop.volume > 0f && !_jetLoop.isPlaying) _jetLoop.Play();
            else if (_jetLoop.volume <= 0f && _jetLoop.isPlaying) _jetLoop.Stop();

            // Fires burning near the view crackle; each dies down over its last few seconds.
            var fire = 0f;
            for (var i = _fires.Count - 1; i >= 0; i--)
            {
                var (at, until) = _fires[i];
                if (now > until)
                {
                    _fires.RemoveAt(i);
                    continue;
                }
                var near = Mathf.Clamp01(1f - Vector3.Distance(at, _camera.Focus) / reach);
                fire += near * near * Mathf.Clamp01((until - now) / 6f);
            }
            var fireTarget = Mathf.Min(0.55f, fire * 0.3f);
            _fire.volume = Mathf.MoveTowards(_fire.volume, fireTarget, Time.unscaledDeltaTime * 0.5f);
            if (_fire.volume > 0f && !_fire.isPlaying) _fire.Play();
            else if (_fire.volume <= 0f && _fire.isPlaying) _fire.Stop();

            for (var i = _thunderAt.Count - 1; i >= 0; i--)
            {
                if (now < _thunderAt[i]) continue;
                _thunderAt.RemoveAt(i);
                _ui.PlayOneShot(_thunder[_rng.Next(_thunder.Length)], 0.85f);
            }
            for (var i = _delayed.Count - 1; i >= 0; i--)
            {
                var d = _delayed[i];
                if (now < d.at) continue;
                _delayed.RemoveAt(i);
                Start(d.sound, d.where, d.volume);
            }
            for (var i = _scheduled.Count - 1; i >= 0; i--)
            {
                var s = _scheduled[i];
                if (now < s.at) continue;
                _scheduled.RemoveAt(i);
                Play(s.sound, s.where, s.volume);
            }
            // Small arms come back up after a big blast.
            var duck = Duck(now);
            foreach (var v in _voices)
                if (v.Bank != null && v.Bank.Light && v.Source.isPlaying) v.Source.volume = v.Level * duck;
        }

        /// <summary>UI feedback; call from button handlers.</summary>
        public void Click() => _ui.PlayOneShot(_clicks[_rng.Next(_clicks.Length)], 0.35f);

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            foreach (var clip in _owned)
                if (clip != null) Object.Destroy(clip);
        }

        private static Sound Blast(ExplosionTier tier) =>
            tier >= ExplosionTier.Huge ? Sound.ExplosionHuge : tier >= ExplosionTier.Large ? Sound.ExplosionLarge : Sound.ExplosionMedium;

        private static Sound WeaponSound(WeaponDef weapon)
        {
            if (weapon == null) return Sound.Cannon;
            switch (weapon.Projectile)
            {
                case ProjectileKind.Missile:
                    return Sound.Missile;
                case ProjectileKind.Rocket:
                case ProjectileKind.Drone:
                    return Sound.Rocket;
                case ProjectileKind.Flame:
                    return Sound.Flame;
                case ProjectileKind.Bullet:
                    return weapon.DamageType == DamageType.Flak ? Sound.Flak : weapon.Damage >= 20f ? Sound.Autocannon : Sound.MachineGun;
            }
            if (weapon.MinRange > 0f) return Sound.Howitzer;
            return weapon.Damage >= 100f ? Sound.HeavyCannon : Sound.Cannon;
        }

        private float Reach(float bonus) => _camera.Zoom * 2.6f + 30f + bonus;

        private static float DuckLevel(float left) => Mathf.Lerp(1f, 0.5f, Mathf.Clamp01(left / 0.35f));

        private float Duck(float now) => now < _duckUntil ? DuckLevel(_duckUntil - now) : 1f;

        /// <summary>How long before a shell lands its whistle starts (the clip's length, less the cut at the end).</summary>
        private const float WhistleLead = 1.15f;

        /// <summary>Sounds due later (a whistle timed to a landing), played through the usual limits when due.</summary>
        private readonly List<(float at, Sound sound, System.Numerics.Vector2 where, float volume)> _scheduled = new();

        private void Schedule(Sound sound, System.Numerics.Vector2 at, float volume, float delay)
        {
            if (_scheduled.Count > 24) return;
            _scheduled.Add((Time.unscaledTime + Mathf.Max(0f, delay), sound, at, volume));
        }

        private void Burn(System.Numerics.Vector2 at, float seconds) =>
            _fires.Add((new Vector3(at.X, 0f, at.Y), Time.unscaledTime + seconds));

        private void Play(Sound sound, System.Numerics.Vector2 at, float volume, float reachBonus = 0f)
        {
            var bank = _banks[sound];
            var now = Time.unscaledTime;
            if (now - bank.LastPlayed < bank.Cooldown) return;
            var distance = Vector3.Distance(new Vector3(at.X, 0f, at.Y), _camera.Focus);
            if (distance >= Reach(reachBonus) * 0.98f) return;
            bank.LastPlayed = now;
            // Big blasts far off arrive a moment after the flash (capped: a few tenths at most).
            var delay = bank.Delayed ? Mathf.Min(0.3f, Mathf.Max(0f, distance - 30f) / SpeedOfSound) : 0f;
            if (delay > 0.02f) _delayed.Add((now + delay, sound, at, volume));
            else Start(sound, at, volume, reachBonus);
        }

        private void Start(Sound sound, System.Numerics.Vector2 at, float volume, float reachBonus = 0f)
        {
            var bank = _banks[sound];
            var now = Time.unscaledTime;
            var world = new Vector3(at.X, 0f, at.Y);
            var distance = Vector3.Distance(world, _camera.Focus);
            var reach = Reach(reachBonus);
            var attenuation = Mathf.Clamp01(1f - distance / reach);
            if (attenuation <= 0.02f) return;
            var level = bank.Volume * volume * attenuation * attenuation;

            var voice = PickVoice(bank, level);
            if (voice == null) return;
            if (bank.Priority >= 4) _duckUntil = now + 0.35f;
            var screen = _camera.Camera.WorldToViewportPoint(world);
            voice.Bank = bank;
            voice.Level = level;
            voice.Started = now;
            voice.Source.clip = bank.Next(_rng);
            voice.Source.volume = bank.Light ? level * Duck(now) : level;
            voice.Source.panStereo = Mathf.Clamp((screen.x - 0.5f) * 1.4f, -0.9f, 0.9f);
            voice.Source.pitch = bank.Pitch * (1f + ((float)_rng.NextDouble() - 0.5f) * bank.PitchSpread);
            // Far sounds lose their top end.
            var far = Mathf.Pow(Mathf.Clamp01(distance / reach), 0.8f);
            voice.Filter.cutoffFrequency = Mathf.Lerp(22000f, 2200f, far);
            voice.Source.Play();
        }

        /// <summary>
        /// A voice for a new sound: its category's oldest once the category is at its limit, else a
        /// free one, else the least important and quietest playing one that matters no more than
        /// the new sound. Null drops the new sound.
        /// </summary>
        private Voice PickVoice(Bank bank, float level)
        {
            Voice oldest = null, free = null, weakest = null;
            var playing = 0;
            foreach (var v in _voices)
            {
                if (!v.Source.isPlaying || v.Bank == null)
                {
                    free ??= v;
                    continue;
                }
                if (v.Bank == bank)
                {
                    playing++;
                    if (oldest == null || v.Started < oldest.Started) oldest = v;
                }
                if (v.Bank.Priority > bank.Priority || (v.Bank.Priority == bank.Priority && v.Level > level)) continue;
                if (weakest == null || v.Bank.Priority < weakest.Bank.Priority ||
                    (v.Bank.Priority == weakest.Bank.Priority && v.Level < weakest.Level)) weakest = v;
            }
            if (playing >= bank.MaxVoices) return oldest;
            return free ?? weakest;
        }

        private void Add(Sound sound, string folder, Func<int, AudioClip> synth, float volume, int voices, float cooldown, int priority,
            float pitch = 1f, bool light = false, bool delayed = false)
        {
            _banks[sound] = new Bank
            {
                Clips = Recorded(folder) ?? Make(synth, 3), Volume = volume, MaxVoices = voices, Cooldown = cooldown, Priority = priority,
                Pitch = pitch, Light = light, Delayed = delayed,
            };
        }

        /// <summary>The recorded clips of a category (Resources/Audio/folder/folder_1, _2...), or null if there are none.</summary>
        private static AudioClip[] Recorded(string folder)
        {
            var clips = Resources.LoadAll<AudioClip>("Audio/" + folder);
            if (clips == null || clips.Length == 0) return null;
            Array.Sort(clips, (a, b) => string.CompareOrdinal(a.name, b.name));
            return clips;
        }

        private AudioSource Loop(string name, string folder, Func<AudioClip> synth)
        {
            var source = NewSource(name);
            source.clip = Recorded(folder)?[0] ?? Own(synth());
            source.loop = true;
            return source;
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
