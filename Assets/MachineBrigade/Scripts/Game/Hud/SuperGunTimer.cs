using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The fortress super-gun's countdown (Siege, Defend): a chip with the gun's icon, what it is
    /// and the seconds to its next shell, red in the last ten; "destroyed" for a few seconds once it
    /// falls, then gone. In Defend the gun is the player's (mint). Styled in Hud.uss (.gun-timer).
    /// </summary>
    internal sealed class SuperGunTimer
    {
        private const float DownShown = 8f;

        private readonly Label _name, _clock;
        private string _shownName, _shownClock;
        private float _downSince = -1f;
        private bool _shown, _urgent, _down, _ours;

        public SuperGunTimer()
        {
            Root = UiKit.Box("gun-timer");
            Root.Add(UiKit.Icon(TowerIcons.For("super_gun"), UiKit.Ink, 1.8f));
            var text = UiKit.Box("gun-timer-text");
            _name = UiKit.Text("", "gun-timer-name");
            _clock = UiKit.Text("", "gun-timer-clock");
            text.Add(_name);
            text.Add(_clock);
            Root.Add(text);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        /// <param name="seconds">Seconds to the next shell; negative when no gun stands.</param>
        /// <param name="down">The gun was destroyed.</param>
        /// <param name="ours">It is the player's gun (Defend).</param>
        public void Set(float seconds, bool down, bool ours)
        {
            var now = Time.unscaledTime;
            if (down && _downSince < 0f) _downSince = now;
            var show = seconds >= 0f || (down && now - _downSince < DownShown);
            if (show != _shown) Root.style.display = (_shown = show) ? DisplayStyle.Flex : DisplayStyle.None;
            if (!show) return;
            if (ours != _ours) Root.EnableInClassList("ours", _ours = ours);
            if (down != _down) Root.EnableInClassList("down", _down = down);
            var name = Strings.Get(down ? "hud.superGunDown" : ours ? "hud.ourSuperGun" : "hud.superGun");
            if (name != _shownName) _name.text = _shownName = name;
            var clock = down || seconds < 0f ? "" : $"{(int)seconds / 60}:{(int)seconds % 60:00}";
            if (clock != _shownClock)
            {
                _clock.text = _shownClock = clock;
                _clock.style.display = clock.Length > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            }
            var urgent = !down && seconds >= 0f && seconds < 10f;
            if (urgent != _urgent) Root.EnableInClassList("urgent", _urgent = urgent);
        }
    }
}
