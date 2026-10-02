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
        private readonly VisualElement _row, _fill, _track;
        private readonly Label _text, _extra;
        private int _left = -1, _full = -1;
        private bool _slow;
        private string _shownExtra;

        /// <summary>
        /// Prompt 29 L5: the load of a vehicle's own missile mounts ("missiles" in the data: the copy
        /// <see cref="VehicleDef.ArmOf"/> gives), past the main weapon (the bar shows that one); 0 for none.
        /// </summary>
        public static int MissileLoad(VehicleDef def)
        {
            if (def == null) return 0;
            var n = 0;
            for (var i = 1; i < def.Mounts.Count; i++)
            {
                var shared = def.Mounts[i].Weapon;
                if (shared == null) continue;
                var own = def.ArmOf(shared);
                if (own != shared && own.Ammo > 0) n += own.Ammo;
            }
            return n;
        }

        /// <summary>Prompt 29 L5: "Missiles 3/4 · Flares 2/3" (either half only when the vehicle has it), or null.</summary>
        public static string KitLine(int missilesLeft, int missilesFull, int flaresLeft, int flaresFull)
        {
            string line = null;
            if (missilesFull > 0) line = Strings.Format("hud.kit.missiles", ("left", missilesLeft), ("full", missilesFull));
            if (flaresFull > 0)
            {
                var flares = Strings.Format("hud.kit.flares", ("left", flaresLeft), ("full", flaresFull));
                line = line == null ? flares : line + "  ·  " + flares;
            }
            return line;
        }

        public StoresStrip(VisualElement host)
        {
            _row = Kit.Box("fc-grow");
            _text = Kit.Text("", "fc-small");
            _row.Add(_text);
            _track = Kit.Box("fc-hud__hp");
            _fill = Kit.Box("fc-hud__hp-fill");
            _track.Add(_fill);
            _row.Add(_track);
            // Prompt 29 L5: the missile mount's rounds and the flare charges, one small line under the bar.
            _extra = Kit.Text("", "fc-small");
            _extra.style.display = DisplayStyle.None;
            _row.Add(_extra);
            host.Add(_row);
            _row.style.display = DisplayStyle.None;
        }

        /// <summary>What the selection carries: its stores or shots left, the full load, the kind, and whether they come back slowly.</summary>
        public void Set(int left, int full, ProjectileKind kind, bool slow, VisualElement host, string extra = null)
        {
            var bar = full > 0;
            var show = bar || !string.IsNullOrEmpty(extra);
            _row.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            host.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            _text.style.display = bar ? DisplayStyle.Flex : DisplayStyle.None;
            _track.style.display = bar ? DisplayStyle.Flex : DisplayStyle.None;
            if (extra != _shownExtra)
            {
                _shownExtra = extra;
                _extra.text = extra ?? "";
                _extra.style.display = string.IsNullOrEmpty(extra) ? DisplayStyle.None : DisplayStyle.Flex;
            }
            if (!bar || left == _left && full == _full && slow == _slow) return;
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
            _text.text = Strings.Format(noun, ("left", left), ("full", full));
            var share = (float)left / full;
            _fill.style.width = Length.Percent(share * 100f);
            _fill.EnableInClassList("fc-hud__hp-fill--hurt", share < 0.2f && left > 0);
            _fill.EnableInClassList("fc-hud__hp-fill--critical", left == 0);
            _fill.style.opacity = slow ? 0.55f : 1f;
        }
    }
}
