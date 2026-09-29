using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 13 C.9: the selection panel's ammunition bar, under the health bar (in
    /// <see cref="BattleHud.SelectionExtras"/>): the bombs, missiles or rockets left of the full load
    /// ("Rockets 14/22"), or a launcher's salvos, filling as they come back. Dim while the stores come
    /// back at the slow rate; the bar turns yellow under 20 % and red when empty.
    /// </summary>
    public sealed class StoresStrip
    {
        private readonly VisualElement _row, _fill;
        private readonly Label _text;
        private int _left = -1, _full = -1;
        private bool _slow;

        public StoresStrip(VisualElement host)
        {
            _row = Kit.Box("fc-grow");
            _text = Kit.Text("", "fc-small");
            _row.Add(_text);
            var track = Kit.Box("fc-hud__hp");
            _fill = Kit.Box("fc-hud__hp-fill");
            track.Add(_fill);
            _row.Add(track);
            host.Add(_row);
            _row.style.display = DisplayStyle.None;
        }

        /// <summary>What the selection carries: its stores or shots left, the full load, the kind, and whether they come back slowly.</summary>
        public void Set(int left, int full, ProjectileKind kind, bool slow, VisualElement host)
        {
            var show = full > 0;
            _row.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            host.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            if (!show || left == _left && full == _full && slow == _slow) return;
            _left = left;
            _full = full;
            _slow = slow;
            var noun = kind switch
            {
                ProjectileKind.Bomb => "hud.stores.bombs",
                ProjectileKind.Missile => "hud.stores.missiles",
                ProjectileKind.Rocket => "hud.stores.rockets",
                _ => "hud.stores.rounds",
            };
            _text.text = Strings.Format(noun, left, full);
            var share = (float)left / full;
            _fill.style.width = Length.Percent(share * 100f);
            _fill.EnableInClassList("fc-hud__hp-fill--hurt", share < 0.2f && left > 0);
            _fill.EnableInClassList("fc-hud__hp-fill--critical", left == 0);
            _fill.style.opacity = slow ? 0.55f : 1f;
        }
    }
}
