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

        private readonly GameObject _root;
        private readonly AudioSource[] _decks = new AudioSource[2];
        private readonly float[] _levels = new float[2];
        private readonly AudioSource _stinger;
        private readonly string _battle;
        private int _live;
        private Mood _mood = Mood.None;
        private Mood _base;
        private bool _boss;

        public MusicDirector(Transform parent, Mood mood, int seed)
        {
            _root = new GameObject("Music");
            _root.transform.SetParent(parent, false);
            for (var i = 0; i < _decks.Length; i++)
            {
                var deck = _root.AddComponent<AudioSource>();
                deck.loop = true;
                deck.playOnAwake = false;
                deck.spatialBlend = 0f;
                deck.ignoreListenerPause = true;
                deck.volume = 0f;
                _decks[i] = deck;
            }
            _stinger = _root.AddComponent<AudioSource>();
            _stinger.playOnAwake = false;
            _stinger.spatialBlend = 0f;
            _stinger.ignoreListenerPause = true;
            _battle = "battle_" + (1 + (int)((uint)seed % 3u));
            _base = mood;
            Play(mood);
        }

        /// <summary>A boss is on the field: its track until it falls, then back to the battle.</summary>
        public bool Boss
        {
            set
            {
                if (_boss == value) return;
                _boss = value;
                Play(value ? Mood.Boss : _base);
            }
        }

        /// <summary>The battle is over: the music fades and the victory or defeat stinger plays.</summary>
        public void Result(bool won)
        {
            Play(Mood.None);
            var clip = Resources.Load<AudioClip>("Audio/Music/" + (won ? "victory" : "defeat"));
            if (clip == null) return;
            _stinger.volume = Bus * MatchSettings.MusicVolume;
            _stinger.PlayOneShot(clip);
        }

        private void Play(Mood mood)
        {
            if (mood == _mood) return;
            _mood = mood;
            var name = mood switch
            {
                Mood.Menu => "menu",
                Mood.Battle => _battle,
                Mood.Siege => "siege",
                Mood.Boss => "boss",
                _ => null,
            };
            var clip = name != null ? Resources.Load<AudioClip>("Audio/Music/" + name) : null;
            // The other deck takes the new track and fades in; the live one fades out.
            _live = 1 - _live;
            var deck = _decks[_live];
            deck.Stop();
            deck.clip = clip;
            deck.volume = 0f;
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

        /// <summary>Per frame (real time): the cross-fade.</summary>
        public void Tick(float dt)
        {
            var step = dt / FadeSeconds;
            var volume = Bus * MatchSettings.MusicVolume * Trim;
            for (var i = 0; i < _decks.Length; i++)
            {
                var want = i == _live && _decks[i].clip != null ? 1f : 0f;
                _levels[i] = Mathf.MoveTowards(_levels[i], want, step);
                _decks[i].volume = _levels[i] * volume;
                if (_levels[i] <= 0f && i != _live && _decks[i].isPlaying) _decks[i].Stop();
            }
        }

        public void Dispose()
        {
            if (_root != null) UnityEngine.Object.Destroy(_root);
        }
    }
}
