using System;
using MachineBrigade.Game.Match;
using UnityEngine;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// The soundtrack (our own compositions, see Tools/music): the menu theme, one of three battle
    /// tracks, the siege track for fortress battles, the boss track while a boss is on the field,
    /// and a short stinger on the result. Tracks cross-fade over two seconds; the music keeps
    /// playing under the pause screen, at its own volume under the sound effects.
    /// <para>
    /// There is one player for the whole session (test feedback 11D: tracks were heard on top of
    /// each other). It lives across scene loads, so the menu theme carries on when the menu is
    /// rebuilt and a battle cross-fades from it instead of a second player starting. It has two
    /// decks, so two tracks overlap only while one fades into the other, and a deck still fading
    /// is cut before a third track starts. A scene asks for its mood with
    /// <see cref="Play(Mood,int)"/>; the In action range ducks it with <see cref="Duck"/>.
    /// </para>
    /// </summary>
    public sealed class MusicDirector : IDisposable
    {
        public enum Mood
        {
            Menu,
            Battle,
            Siege,
            Boss,
            None,
        }

        /// <summary>The music sits this far under the effects (the effects carry the battle).</summary>
        private const float Bus = 0.55f;

        private const float FadeSeconds = 2f;

        /// <summary>How fast a duck comes and goes (share of the level per second).</summary>
        private const float DuckSpeed = 1.6f;

        private static MusicDirector _current;

        private readonly GameObject _root;
        private readonly AudioSource[] _decks = new AudioSource[2];
        private readonly string[] _tracks = new string[2];
        private readonly float[] _levels = new float[2];
        private readonly AudioSource _stinger;
        private string _battle = "battle_1";
        private int _live;
        private Mood _mood = Mood.None;
        private Mood _base;
        private bool _boss;
        private float _duck = 1f, _duckTarget = 1f;

        /// <summary>The session's player, if one has started.</summary>
        public static MusicDirector Current => _current != null && _current._root != null ? _current : null;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => _current = null;

        /// <summary>
        /// A scene's soundtrack: the session's one player (made on first use) moves to this mood,
        /// cross-fading from whatever was playing. The same track carries on untouched; a battle
        /// draws its track from <paramref name="seed"/>. The boss track and any duck are reset.
        /// </summary>
        public static MusicDirector Play(Mood mood, int seed)
        {
            var music = Current ?? (_current = new MusicDirector());
            music._battle = "battle_" + (1 + (int)((uint)seed % 3u));
            music._base = mood;
            music._boss = false;
            music._duckTarget = 1f;
            music.Switch(mood);
            return music;
        }

        private MusicDirector()
        {
            // Nothing else may be left playing music: a player from an earlier session goes for good.
            foreach (var old in UnityEngine.Object.FindObjectsByType<MusicHost>())
                if (old != null) UnityEngine.Object.Destroy(old.gameObject);
            _root = new GameObject("Music");
            UnityEngine.Object.DontDestroyOnLoad(_root);
            _root.AddComponent<MusicHost>().Owner = this;
            for (var i = 0; i < _decks.Length; i++)
            {
                var deck = _root.AddComponent<AudioSource>();
                deck.loop = true;
                deck.playOnAwake = false;
                deck.spatialBlend = 0f;
                deck.ignoreListenerPause = true;
                deck.volume = 0f;
                deck.priority = 0;
                _decks[i] = deck;
            }
            _stinger = _root.AddComponent<AudioSource>();
            _stinger.playOnAwake = false;
            _stinger.spatialBlend = 0f;
            _stinger.ignoreListenerPause = true;
            _stinger.priority = 0;
        }

        /// <summary>A boss is on the field: its track until it falls, then back to the battle.</summary>
        public bool Boss
        {
            set
            {
                if (_boss == value) return;
                _boss = value;
                Switch(value ? Mood.Boss : _base);
            }
        }

        /// <summary>The track playing (or fading in), null for none: for checks.</summary>
        public string Track => _tracks[_live];

        /// <summary>
        /// Holds the music at a share of its level (1: full) while something else carries the sound,
        /// such as the detail page's In action range; eased in and out.
        /// </summary>
        public void Duck(float level) => _duckTarget = Mathf.Clamp01(level);

        /// <summary>The battle is over: the music fades and the victory or defeat stinger plays.</summary>
        public void Result(bool won)
        {
            Switch(Mood.None);
            var clip = Resources.Load<AudioClip>("Audio/Music/" + (won ? "victory" : "defeat"));
            if (clip == null) return;
            _stinger.Stop();
            _stinger.clip = clip;
            _stinger.loop = false;
            _stinger.volume = Bus * MatchSettings.MusicVolume;
            _stinger.Play();
        }

        private void Switch(Mood mood)
        {
            var name = mood switch
            {
                Mood.Menu => "menu",
                Mood.Battle => _battle,
                Mood.Siege => "siege",
                Mood.Boss => "boss",
                _ => null,
            };
            _mood = mood;
            // The track already playing carries on (a rebuilt menu keeps its theme where it was).
            if (name == _tracks[_live] && (name == null || _decks[_live].isPlaying)) return;
            // A new track: the last battle's result stinger stops.
            if (name != null && _stinger.isPlaying) _stinger.Stop();
            var clip = name != null ? Resources.Load<AudioClip>("Audio/Music/" + name) : null;
            // The other deck takes the new track and fades in; the live one fades out. A deck still
            // fading from an earlier change is cut first, so never more than two tracks sound.
            _live = 1 - _live;
            var deck = _decks[_live];
            deck.Stop();
            deck.clip = clip;
            deck.volume = 0f;
            _tracks[_live] = clip != null ? name : null;
            _levels[_live] = 0f;
            if (clip != null) deck.Play();
        }

        /// <summary>Loudness of each track against the menu theme's (they are mastered alike, but differ in density).</summary>
        private float Trim => _mood switch
        {
            Mood.Siege => 0.92f,
            Mood.Boss => 0.81f,
            Mood.Battle => _battle == "battle_1" ? 0.88f : 0.85f,
            _ => 1f,
        };

        /// <summary>Per frame, in real time (the player's own host calls it): the cross-fade and the duck.</summary>
        private void Tick(float dt)
        {
            // After a scene load the first delta is the whole load: step as one frame.
            dt = Mathf.Min(dt, 0.1f);
            var step = dt / FadeSeconds;
            _duck = Mathf.MoveTowards(_duck, _duckTarget, dt * DuckSpeed);
            var volume = Bus * MatchSettings.MusicVolume * Trim * _duck;
            for (var i = 0; i < _decks.Length; i++)
            {
                var want = i == _live && _decks[i].clip != null ? 1f : 0f;
                _levels[i] = Mathf.MoveTowards(_levels[i], want, step);
                _decks[i].volume = _levels[i] * volume;
                if (_levels[i] <= 0f && i != _live && _decks[i].isPlaying)
                {
                    _decks[i].Stop();
                    _tracks[i] = null;
                }
            }
        }

        /// <summary>Kept for the scene's clean-up: the player outlives the scene (see <see cref="Play(Mood,int)"/>).</summary>
        public void Dispose()
        {
        }

        /// <summary>Drives the player every frame in real time, whichever scene is up.</summary>
        private sealed class MusicHost : MonoBehaviour
        {
            public MusicDirector Owner;

            private void Update() => Owner?.Tick(Time.unscaledDeltaTime);

            private void OnDestroy()
            {
                if (_current == Owner) _current = null;
            }
        }
    }
}
