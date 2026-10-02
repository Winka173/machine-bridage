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
    /// Fix pass L7 (Docs/audio/diagnosis.md, DECISIONS "Sửa lỗi tổng hợp L7"): the shots, blasts and hits come from the
    /// library by size (Resources/Audio/sfx, AudioDirector.P34 and <see cref="SoundLibrary"/>), the hits by what they
    /// struck (metal only on armour not pierced, rate-capped); the mix has its four groups, an Effects compressor, the
    /// output limiter (<see cref="EffectsLimiter"/>) and a camera-distance falloff.
    /// </summary>
    public sealed partial class AudioDirector : IDisposable
    {
        private enum Sound
        {
            MachineGun, Autocannon, Cannon, HeavyCannon, Howitzer, Rocket, Missile, Flak, Flame,
            ExplosionSmall, ExplosionMedium, ExplosionLarge, ExplosionHuge, Collapse, Debris, Impact, Jet, Whistle,
            Drone, BeamStart,
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

            /// <summary>
            /// Play-test 12 (the rapid-fire bursts): at its voice limit the bank does not cut its oldest voice mid-burst; a new
            /// sound takes the quietest one only when it is twice as loud, else it is dropped (no stutter, no clicks).
            /// </summary>
            public bool NoSteal;

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

            /// <summary>Prompt 34 L6: what this sound counts for when the voices run out (<see cref="SoundPriority"/>, 1-7).</summary>
            public int Priority;
        }

        private const int Voices = 32;
        private const float SpeedOfSound = 343f;

        private readonly GameObject _root;
        private readonly RtsCamera _camera;
        private readonly Catalog _catalog;
        private readonly int _playerTeam;
        private readonly Voice[] _voices = new Voice[Voices];
        private readonly AudioSource _ambient, _rotor, _jetLoop, _ui, _rain, _fire, _drums, _beam;

        /// <summary>
        /// Test feedback 19P: a laser's held beam is one continuous hum while it burns (a loop), not a machine gun's
        /// clatter for each of its 0.1 s shots: until when the nearest beam burns, how loud, and where from.
        /// </summary>
        private float _beamUntil, _beamLevel, _beamPan;
        private readonly AudioClip[] _thunder, _clicks;
        private readonly List<float> _thunderAt = new();
        private readonly AudioClip _captured, _lost, _siren;

        /// <summary>
        /// Prompt 25 C1 (DECISIONS 25C): each main boss's super weapon has its own warning, a synthesised alarm in place of
        /// the siren: by its big attack's id. Distinct in pitch, rhythm, sweep and timbre, so the player learns which is
        /// coming by ear: the Behemoth's low horn, the missile train's rising wail, Icarus's electronic chirps, Typhon's
        /// sonar pings...
        /// </summary>
        internal static readonly Dictionary<string, SoundSynth.SuperCue> SuperCues = new()
        {
            ["behemoth_barrage"] = new(2501, 196f, 2, 0.55f, 0.18f, -0.18f, 0.7f, 0.35f),
            ["fortress_203_barrage"] = new(2502, 330f, 3, 0.3f, 0.12f, 0f, 1f, 0.15f),
            ["carrier_heavy_bomb"] = new(2503, 900f, 1, 1.3f, 0.1f, -0.55f, 0.2f, 0.25f),
            ["doomsday_missile"] = new(2504, 440f, 2, 0.8f, 0.1f, 0.6f, 0.35f, 0.1f),
            ["bug_rod_rain"] = new(2505, 1250f, 5, 0.09f, 0.07f, 0.12f, 0f, 0f),
            ["bastion_420_shell"] = new(2506, 140f, 1, 1.1f, 0.1f, -0.1f, 0.8f, 0.6f),
            ["airship_carpet"] = new(2507, 520f, 6, 0.1f, 0.06f, 0f, 1f, 0.1f),
            ["leviathan_volley"] = new(2508, 165f, 2, 0.7f, 0.2f, 0f, 0.45f, 0.7f),
            ["moloch_factory_dump"] = new(2509, 620f, 4, 0.22f, 0.04f, 0f, 1f, 0.2f, 0.72f),
            ["daedalus_mass_drop"] = new(2510, 700f, 3, 0.2f, 0.08f, 0.45f, 0.1f, 0.05f),
            ["kronos_bucket_sweep"] = new(2511, 250f, 4, 0.18f, 0.08f, -0.05f, 0.6f, 0.9f),
            ["typhon_underwater_launch"] = new(2512, 1480f, 2, 0.35f, 0.45f, -0.02f, 0f, 0f),
        };

        private readonly Dictionary<string, AudioClip> _superCues = new();
        private readonly Dictionary<Sound, Bank> _banks = new();
        private readonly List<AudioClip> _owned = new();
        private readonly List<(float at, Bank bank, System.Numerics.Vector2 where, float volume, int priority)> _delayed = new();
        private readonly List<(Vector3 at, float until)> _fires = new();
        private readonly System.Random _rng = new(5);
        private float _duckUntil;
        private float _drumsTarget;

        /// <summary>
        /// The menu's lobby (no player side): its battle is not heard at all, no guns, blasts,
        /// rotors or fires, only a soft wind (test feedback 11D). The detail page's In action range
        /// is heard through <see cref="ConsumeRange"/>, a little under a battle's level.
        /// </summary>
        private readonly bool _lobby;

        /// <summary>The lobby's wind against a battle's.</summary>
        private const float LobbyAmbience = 0.45f;

        /// <summary>A thunderclap's level (0.85 before play-test 6, when the storm drowned the music).</summary>
        internal const float ThunderLevel = 0.55f;

        /// <summary>The In action range's shots and blasts against a battle's (the menu music is ducked under them).</summary>
        public const float RangeGain = 0.6f;

        /// <summary>The events being played are the In action range's (see <see cref="ConsumeRange"/>).</summary>
        private bool _ranging;

        /// <summary>
        /// Somewhere else to listen from, while the detail page's In action range plays: its look
        /// point, its camera (for left and right) and how far it hears. Null: the battlefield camera.
        /// </summary>
        public Vector3? FocusOverride { get; set; }
        public Camera ViewOverride { get; set; }
        public float ReachOverride { get; set; }

        private Vector3 Focus => FocusOverride ?? _camera.Focus;
        private Camera View => ViewOverride != null ? ViewOverride : _camera.Camera;

        public AudioDirector(RtsCamera camera, Transform parent, Catalog catalog, int playerTeam)
        {
            _camera = camera;
            _catalog = catalog;
            _playerTeam = playerTeam;
            _lobby = playerTeam < 0;
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
            Add(Sound.Impact, "sfx/hit_ground_light", i => SoundSynth.MachineGun(860 + i, 1), 0.28f, 3, 0.1f, 0, light: true);
            Add(Sound.Jet, "jet_pass", i => SoundSynth.JetPass(900 + i), 0.9f, 2, 0.5f, 4);
            // Incoming shells whistle down onto where they land: the warning is in the world, where
            // the danger is, not a beep from the interface (Company of Heroes and Men of War do the same).
            Add(Sound.Whistle, "sfx/warn_whistle", i => SoundSynth.Whistle(950 + i), 0.5f, 3, 0.22f, SoundPriority.Warning);
            // Test feedback 19P: an FPV drone leaves its rack with a buzz of props, not a rocket's roar; a beam
            // ignites with a rising whine before its hum takes over.
            Add(Sound.Drone, "drone_buzz", i => SoundSynth.DroneBuzz(970 + i), 0.5f, 4, 0.12f, 2, light: true);
            Add(Sound.BeamStart, "beam_start", i => SoundSynth.BeamStart(980 + i), 0.6f, 2, 0.3f, 3);
            // Points taken and lost come over the radio: a squelch and two soft notes.
            _captured = Own(SoundSynth.Radio(true));
            _lost = Own(SoundSynth.Radio(false));
            _siren = Recorded("siren")?[0];
            foreach (var (id, cue) in SuperCues) _superCues[id] = Own(SoundSynth.SuperWarning("super_" + id, cue));
            // Prompt 34 L6: the tiered banks (Resources/Audio/p34, Tools/sfx/build_sfx.py); the naval and rail ones load with their units.
            AddTierBanks();

            for (var i = 0; i < Voices; i++)
            {
                var source = NewSource($"Voice {i}");
                var filter = source.gameObject.AddComponent<AudioLowPassFilter>();
                filter.cutoffFrequency = 22000f;
                _voices[i] = new Voice { Source = source, Filter = filter };
            }
            _ambient = Loop("Wind", "wind_loop", () => SoundSynth.Wind(9));
            // Play-test 6: the wind sits under the music (0.16 before).
            _ambient.volume = _lobby ? 0.1f * LobbyAmbience : 0.1f;
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
            _beam = Loop("Laser Beams", "beam_loop", () => SoundSynth.BeamLoop(31));
            _beam.volume = 0f;
            _ui = NewSource("UI");
            _clicks = Recorded("click") ?? new[] { Own(SoundSynth.Click()) };
            _ui.clip = _clicks[0];
            // Menu clicks still sound while the game (and every other source) is paused.
            _ui.ignoreListenerPause = true;
            Preload();
        }

        /// <summary>
        /// Decompresses every clip now, behind the loading curtain. The recorded effects are set to
        /// load on first play, which decoded each one on the main thread the first time it sounded:
        /// a stall in the first seconds of a battle or of the In action range (test feedback 11D).
        /// </summary>
        private void Preload()
        {
            foreach (var bank in _banks.Values)
                foreach (var clip in bank.Clips)
                    Load(clip);
            foreach (var bank in _tierBanks.Values)
                foreach (var clip in bank.Clips)
                    Load(clip);
            foreach (var clip in _thunder) Load(clip);
            foreach (var clip in _clicks) Load(clip);
            Load(_siren);
            foreach (var source in new[] { _ambient, _rotor, _jetLoop, _rain, _fire, _drums, _beam })
                Load(source.clip);
        }

        private static void Load(AudioClip clip)
        {
            if (clip != null && clip.loadState == AudioDataLoadState.Unloaded) clip.LoadAudioData();
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
            set => _ambient.volume = (_lobby ? value * LobbyAmbience : value) * Fx;
        }

        /// <summary>Rain loop level (0 = dry).</summary>
        public float RainLevel
        {
            set
            {
                _rain.volume = value * Fx;
                if (value > 0f && !_rain.isPlaying) _rain.Play();
                else if (value <= 0f && _rain.isPlaying) _rain.Stop();
            }
        }

        /// <summary>Thunder after a lightning flash, delayed by the distance of the strike.</summary>
        public void Thunder(float delay) => _thunderAt.Add(Time.unscaledTime + delay);

        /// <summary>The battle's events: its shots, blasts and radio chimes (none in the menu's lobby).</summary>
        public void Consume(IReadOnlyList<SimEvent> events)
        {
            if (_lobby) return;
            Play(events);
        }

        /// <summary>The detail page's In action range: its own shots and blasts, at <see cref="RangeGain"/>.</summary>
        public void ConsumeRange(IReadOnlyList<SimEvent> events)
        {
            _ranging = true;
            try
            {
                Play(events);
            }
            finally
            {
                _ranging = false;
            }
        }

        private void Play(IReadOnlyList<SimEvent> events)
        {
            foreach (var e in events)
            {
                switch (e.Kind)
                {
                    case SimEventKind.WeaponFired:
                        var weapon = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var w) ? w : null;
                        // Bombs are released silently; the blast is the sound.
                        if (weapon != null && weapon.Projectile == ProjectileKind.Bomb) break;
                        if (weapon != null && weapon.Beam)
                        {
                            Beam(weapon, e.Position);
                            break;
                        }
                        // Prompt 34 L6: by tier and round, small arms as clusters, at the 7-step priority.
                        Shot(e, weapon);
                        // Play-test 12: a missile or a rocket hisses in just before it lands.
                        Incoming(e, weapon);
                        // Heavy shells on a long flight whistle down onto where they are aimed.
                        if (weapon != null && weapon.MinRange > 0f && weapon.Projectile == ProjectileKind.Shell && e.Value > WhistleLead + 0.2f)
                            Whistle(e.Target, 0.7f, e.Value - WhistleLead, SoundLibrary.SizeOf(weapon) >= SizeClass.S406);
                        break;
                    case SimEventKind.ProjectileImpact:
                        // A beam's burn is in its hum: no ping for each of its shots.
                        if (e.Tier < ExplosionTier.Medium && e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var burnt) && burnt.Beam) break;
                        if (Landed(e)) break;
                        if (e.Tier >= ExplosionTier.Medium) Play(Blast(e.Tier), e.Position, e.Tier >= ExplosionTier.Huge ? 1f : 0.85f);
                        else Play(Sound.Impact, e.Position, 1f);
                        break;
                    case SimEventKind.Intercepted:
                        // Fix pass L7: an interception is a burst in the air, not a metal ping.
                        if (_tierBanks.TryGetValue("blast_air_s1", out var burst)) Play(burst, e.Position, 1f, 10f, SoundPriority.FarBlast);
                        else Play(Sound.ExplosionSmall, e.Position, 0.6f);
                        break;
                    case SimEventKind.SkillUsed when e.Skill == SkillKind.Flares:
                        Flared(e);
                        break;
                    case SimEventKind.Explosion:
                        if (Exploded(e)) break;
                        if (TierBlast(e.Tier, e.Position)) break;
                        Play(e.Tier <= ExplosionTier.Small ? Sound.ExplosionSmall : Blast(e.Tier < ExplosionTier.Large ? ExplosionTier.Large : e.Tier),
                            e.Position, 1f);
                        break;
                    case SimEventKind.StrikeImpact:
                        if (TierBlast(e.Tier < ExplosionTier.Large ? ExplosionTier.Large : e.Tier, e.Position)) break;
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
                    // Prompt 18 A.3: a boss's big attack begins: the alarm (heard wherever the view is) and the whistle as it lands.
                    case SimEventKind.BigAttack when e.Mount == 0 && _playerTeam >= 0:
                        // Prompt 25 C1: a super weapon's own warning, else the siren.
                        if (e.DefId != null && _superCues.TryGetValue(e.DefId, out var cue)) _ui.PlayOneShot(cue, 0.36f * Fx);
                        else if (_siren != null) _ui.PlayOneShot(_siren, 0.32f * Fx);
                        MusicDirector.Current?.Alert();
                        Whistle(e.Position, 1f, e.Value - WhistleLead, true);
                        break;
                    case SimEventKind.FortressAlert when _playerTeam >= 0 && _siren != null:
                        // The fortress's own alarm: heard as far as the fortress is near the view.
                        var alarm = Vector3.Distance(new Vector3(e.Position.X, 0f, e.Position.Y), Focus);
                        if (alarm < 120f)
                        {
                            _ui.PlayOneShot(_siren, (0.28f * (1f - alarm / 120f) + 0.06f) * Fx);
                            MusicDirector.Current?.Alert();
                        }
                        break;
                    case SimEventKind.StageCleared when _playerTeam >= 0:
                        _ui.PlayOneShot(_captured, 0.6f * Talk);
                        break;
                    case SimEventKind.PointCaptured when _playerTeam >= 0:
                        if (e.Team == _playerTeam) _ui.PlayOneShot(_captured, 0.5f * Talk);
                        else if (e.Team >= 0) _ui.PlayOneShot(_lost, 0.5f * Talk);
                        break;
                    case SimEventKind.VehicleDestroyed:
                        Burn(e.Position, 25f);
                        // Prompt 34 L6: the wreck by its class (and an aircraft's fall); the old blast where there is no clip.
                        if (Wrecked(e)) break;
                        Play(Sound.ExplosionLarge, e.Position, 0.9f);
                        Play(Sound.Debris, e.Position, 0.8f);
                        break;
                    case SimEventKind.VehicleSpawned:
                        Spawned(e);
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
            _views = views;
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
                var distance = Vector3.Distance(view.Position, Focus);
                if (view.Def.FixedWing) nearestJet = Mathf.Min(nearestJet, distance);
                else nearest = Mathf.Min(nearest, distance);
            }
            var reach = Reach(0f);
            // The lobby's aircraft and fires are not heard (its views are the lobby battle's).
            if (_lobby) nearest = nearestJet = float.MaxValue;
            var target = nearest < float.MaxValue ? Mathf.Clamp01(1f - nearest / reach) * 0.5f * Fx : 0f;
            _rotor.volume = Mathf.MoveTowards(_rotor.volume, target, Time.unscaledDeltaTime * 0.8f);
            var jetTarget = nearestJet < float.MaxValue ? Mathf.Clamp01(1f - nearestJet / (reach + 20f)) * 0.4f * Fx : 0f;
            _jetLoop.volume = Mathf.MoveTowards(_jetLoop.volume, jetTarget, Time.unscaledDeltaTime * 0.8f);
            if (_jetLoop.volume > 0f && !_jetLoop.isPlaying) _jetLoop.Play();
            else if (_jetLoop.volume <= 0f && _jetLoop.isPlaying) _jetLoop.Stop();

            // A laser's beam hums while it burns, swelling in fast and dying away in a moment after its last shot.
            var beamTarget = now < _beamUntil ? _beamLevel * Fx : 0f;
            _beam.volume = Mathf.MoveTowards(_beam.volume, beamTarget, Time.unscaledDeltaTime * (beamTarget > _beam.volume ? 6f : 2.5f));
            _beam.panStereo = _beamPan;
            if (_beam.volume > 0f && !_beam.isPlaying) _beam.Play();
            else if (_beam.volume <= 0f && _beam.isPlaying) _beam.Stop();

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
                var near = Mathf.Clamp01(1f - Vector3.Distance(at, Focus) / reach);
                fire += near * near * Mathf.Clamp01((until - now) / 6f);
            }
            // A boss's broken parts burn on as it moves (prompt 9): a low crackle that follows it.
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (!view.Def.Boss || view.IsWreck || !view.Sim.IsAlive || view.Sim.BrokenParts == 0) continue;
                var near = Mathf.Clamp01(1f - Vector3.Distance(view.Position, Focus) / reach);
                fire += near * near * Mathf.Min(1f, 0.25f * view.Sim.BrokenParts);
            }
            var fireTarget = _lobby ? 0f : Mathf.Min(0.55f, fire * 0.3f) * Fx;
            _fire.volume = Mathf.MoveTowards(_fire.volume, fireTarget, Time.unscaledDeltaTime * 0.5f);
            if (_fire.volume > 0f && !_fire.isPlaying) _fire.Play();
            else if (_fire.volume <= 0f && _fire.isPlaying) _fire.Stop();

            for (var i = _thunderAt.Count - 1; i >= 0; i--)
            {
                if (now < _thunderAt[i]) continue;
                _thunderAt.RemoveAt(i);
                _ui.PlayOneShot(_thunder[_rng.Next(_thunder.Length)], ThunderLevel * Fx);
            }
            for (var i = _delayed.Count - 1; i >= 0; i--)
            {
                var d = _delayed[i];
                if (now < d.at) continue;
                _delayed.RemoveAt(i);
                Start(d.bank, d.where, d.volume, 0f, d.priority);
            }
            for (var i = _scheduled.Count - 1; i >= 0; i--)
            {
                var s = _scheduled[i];
                if (now < s.at) continue;
                _scheduled.RemoveAt(i);
                Play(s.bank, s.where, s.volume, 0f, s.priority);
            }
            TickTiers(views, now);
            // Fix pass L7: the Effects compressor's gain on every effect voice; small arms come back up after a big blast.
            Compress(Time.unscaledDeltaTime);
            var duck = Duck(now);
            foreach (var v in _voices)
                if (v.Bank != null && v.Source.isPlaying) v.Source.volume = v.Level * (v.Bank.Light ? duck : 1f) * _busGain;
        }

        /// <summary>Prompt 34 L9: the voices playing now, of 32 (the stress scene's count).</summary>
        internal int BusyVoices
        {
            get
            {
                var n = 0;
                foreach (var v in _voices)
                    if (v != null && v.Source != null && v.Source.isPlaying) n++;
                return n;
            }
        }

        /// <summary>UI feedback; call from button handlers.</summary>
        public void Click() => _ui.PlayOneShot(_clicks[_rng.Next(_clicks.Length)], 0.35f * Ui);

        public void Dispose()
        {
            DetachLimiter();
            if (_root != null) Object.Destroy(_root);
            foreach (var clip in _owned)
                if (clip != null) Object.Destroy(clip);
        }

        /// <summary>
        /// A laser's shot: it keeps the beam's hum going for a little over the gap to its next shot, as loud as the
        /// nearest beam burning; a beam that starts after a pause ignites with a whine first.
        /// </summary>
        private void Beam(WeaponDef weapon, System.Numerics.Vector2 at)
        {
            var now = Time.unscaledTime;
            var world = new Vector3(at.X, 0f, at.Y);
            var attenuation = Mathf.Clamp01(1f - Vector3.Distance(world, Focus) / Reach(10f));
            if (attenuation <= 0.02f) return;
            // Point-defence lasers are thinner beams than the tank's focused one.
            var level = (weapon.Targets == TargetLayers.Air ? 0.4f : 0.55f) * attenuation * attenuation * (_ranging ? RangeGain : 1f);
            if (now >= _beamUntil + 0.2f) Play(Sound.BeamStart, at, weapon.Targets == TargetLayers.Air ? 0.7f : 1f);
            if (now >= _beamUntil || level >= _beamLevel)
            {
                _beamLevel = level;
                _beamPan = Mathf.Clamp((View.WorldToViewportPoint(world).x - 0.5f) * 1.4f, -0.9f, 0.9f);
            }
            _beamUntil = Mathf.Max(_beamUntil, now + Mathf.Max(0.12f, weapon.Cooldown) * 1.8f + 0.08f);
        }

        /// <summary>Fix pass L7: a blast known only by its tier (a strike, a cook-off, a mine) from the library: HE by size. False: none built.</summary>
        private bool TierBlast(ExplosionTier tier, System.Numerics.Vector2 at)
        {
            var size = tier >= ExplosionTier.Ultimate ? SizeClass.S406 : tier >= ExplosionTier.Huge ? SizeClass.S4 : tier >= ExplosionTier.Large ? SizeClass.S3
                : tier >= ExplosionTier.Medium ? SizeClass.S2 : SizeClass.S1;
            var name = size == SizeClass.S406 ? "blast_he_s406" : "blast_he_s" + (int)size;
            if (!_tierBanks.TryGetValue(name, out var bank)) return false;
            Play(bank, at, 1f, SoundLibrary.Carry(size), SoundPriority.For(size, false, true, Near(at)));
            return true;
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
                    return Sound.Rocket;
                case ProjectileKind.Drone:
                    // A quadcopter buzzes off; a winged drone (a Lancet, a Shahed) is thrown off its rail by a booster.
                    return weapon.ProjectileModel is null or "fpv_drone" ? Sound.Drone : Sound.Rocket;
                case ProjectileKind.Flame:
                    return Sound.Flame;
                case ProjectileKind.Bullet:
                    // Flak rounds, and the point-defence laser (it sounded as flak before prompt 15 made it energy).
                    return weapon.DamageType == DamageType.Fragmentation || (weapon.Beam && weapon.Targets == TargetLayers.Air) ? Sound.Flak
                        : weapon.RoundWeight >= 20f ? Sound.Autocannon : Sound.MachineGun;
            }
            if (weapon.MinRange > 0f) return Sound.Howitzer;
            return weapon.Damage >= 100f ? Sound.HeavyCannon : Sound.Cannon;
        }

        private float Reach(float bonus) => (ReachOverride > 0f ? ReachOverride : _camera.Zoom * 2.6f + 30f) + bonus;

        private static float DuckLevel(float left) => Mathf.Lerp(1f, 0.5f, Mathf.Clamp01(left / 0.35f));

        private float Duck(float now) => now < _duckUntil ? DuckLevel(_duckUntil - now) : 1f;

        /// <summary>How long before a shell lands its whistle starts (the clip's length, less the cut at the end).</summary>
        private const float WhistleLead = 1.15f;

        /// <summary>Sounds due later (a whistle timed to a landing), played through the usual limits when due.</summary>
        private readonly List<(float at, Bank bank, System.Numerics.Vector2 where, float volume, int priority)> _scheduled = new();

        private void Schedule(Sound sound, System.Numerics.Vector2 at, float volume, float delay) =>
            Schedule(_banks[sound], at, volume, delay, -1);

        private void Schedule(Bank bank, System.Numerics.Vector2 at, float volume, float delay, int priority)
        {
            if (_scheduled.Count > 24) return;
            if (_ranging) volume *= RangeGain;
            _scheduled.Add((Time.unscaledTime + Mathf.Max(0f, delay), bank, at, volume, priority));
        }

        private void Burn(System.Numerics.Vector2 at, float seconds) =>
            _fires.Add((new Vector3(at.X, 0f, at.Y), Time.unscaledTime + seconds));

        private void Play(Sound sound, System.Numerics.Vector2 at, float volume, float reachBonus = 0f) =>
            Play(_banks[sound], at, volume, reachBonus, -1);

        /// <summary>
        /// Plays a bank's next clip at <paramref name="at"/>: through its cooldown, its reach and (far off, for big blasts)
        /// the speed of sound. <paramref name="priority"/> is the 7-step priority it plays at (-1: the bank's own).
        /// </summary>
        private void Play(Bank bank, System.Numerics.Vector2 at, float volume, float reachBonus, int priority, float pitch = 1f)
        {
            if (_ranging) volume *= RangeGain;
            var now = Time.unscaledTime;
            if (now - bank.LastPlayed < bank.Cooldown) return;
            var distance = Vector3.Distance(new Vector3(at.X, 0f, at.Y), Focus);
            if (distance >= Reach(reachBonus) * 0.98f) return;
            bank.LastPlayed = now;
            // Big blasts far off arrive a moment after the flash (capped: a few tenths at most).
            var delay = bank.Delayed ? Mathf.Min(0.3f, Mathf.Max(0f, distance - 30f) / SpeedOfSound) : 0f;
            if (delay > 0.02f) _delayed.Add((now + delay, bank, at, volume, priority));
            else Start(bank, at, volume, reachBonus, priority, pitch);
        }

        private void Start(Bank bank, System.Numerics.Vector2 at, float volume, float reachBonus, int priority, float pitch = 1f)
        {
            var now = Time.unscaledTime;
            var world = new Vector3(at.X, 0f, at.Y);
            var distance = Vector3.Distance(world, Focus);
            var reach = Reach(reachBonus);
            var attenuation = Mathf.Clamp01(1f - distance / reach);
            if (attenuation <= 0.02f) return;
            var screen = View.WorldToViewportPoint(world);
            // Prompt 34 L6: a source off the screen is a little quieter; the effects' own volume (settings) on top.
            var offScreen = screen.x < 0f || screen.x > 1f || screen.y < 0f || screen.y > 1f || screen.z < 0f;
            // Fix pass L7: the camera-distance falloff (ground distance and the camera's height), in place of (1 - d / reach)^2.
            var height = Mathf.Max(0f, View.transform.position.y);
            var level = bank.Volume * volume * SoundLibrary.Falloff(distance, height, reach) * (offScreen ? OffScreenGain : 1f) * Fx;
            if (level <= 0.001f) return;
            if (priority < 0) priority = bank.Priority;

            var voice = PickVoice(bank, level, priority);
            if (voice == null) return;
            if (priority >= SoundPriority.NearBlast) _duckUntil = now + 0.35f;
            voice.Priority = priority;
            voice.Bank = bank;
            voice.Level = level;
            voice.Started = now;
            voice.Source.clip = bank.Next(_rng);
            voice.Source.volume = (bank.Light ? level * Duck(now) : level) * _busGain;
            voice.Source.panStereo = Mathf.Clamp((screen.x - 0.5f) * 1.4f, -0.9f, 0.9f);
            voice.Source.pitch = bank.Pitch * pitch * (1f + ((float)_rng.NextDouble() - 0.5f) * bank.PitchSpread);
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
        private Voice PickVoice(Bank bank, float level, int priority)
        {
            Voice oldest = null, free = null, weakest = null, quietest = null;
            var playing = 0;
            var busy = 0;
            foreach (var v in _voices)
            {
                if (!v.Source.isPlaying || v.Bank == null)
                {
                    free ??= v;
                    continue;
                }
                busy++;
                if (v.Bank == bank)
                {
                    playing++;
                    if (oldest == null || v.Started < oldest.Started) oldest = v;
                    if (quietest == null || v.Level < quietest.Level) quietest = v;
                }
                if (v.Priority > priority || (v.Priority == priority && v.Level > level)) continue;
                if (weakest == null || v.Priority < weakest.Priority || (v.Priority == weakest.Priority && v.Level < weakest.Level)) weakest = v;
            }
            if (playing >= bank.MaxVoices)
            {
                if (!bank.NoSteal) return oldest;
                return quietest != null && quietest.Level * 2f < level ? quietest : null;
            }
            // Prompt 34 L6: about 24 effect voices at once before the least important is cut; the pool's last 8 are kept
            // for the warnings and the T5 / boss sounds.
            if (busy >= EffectVoices && priority < SoundPriority.Boss) return weakest;
            return free ?? weakest;
        }

        private void Add(Sound sound, string folder, Func<int, AudioClip> synth, float volume, int voices, float cooldown, int priority,
            float pitch = 1f, bool light = false, bool delayed = false)
        {
            _banks[sound] = new Bank
            {
                Clips = Recorded(folder) ?? Make(synth, 3), Volume = volume, MaxVoices = voices, Cooldown = cooldown,
                Priority = SoundPriority.Steps(priority),
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
