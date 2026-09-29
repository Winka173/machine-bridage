using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.UIElements;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Under the boss bar (prompt 9 D): a small icon for each of the boss's parts, by what it is, with a
    /// thin health bar; a broken part greyed and crossed out, the ordered part ringed. Tapping an icon
    /// orders every unit in reach at that part (tapping it again cancels). Self-contained; on the kit's
    /// tokens (Screens.uss, "fc-boss-parts"): each icon is a full touch target (Field Command 2.0, G).
    /// </summary>
    internal sealed class BossPartsRow
    {
        private sealed class Cell
        {
            public VisualElement Root, Fill;
            public int ShownFill = -1;
            public bool ShownBroken, ShownFocus;
        }

        private readonly List<Cell> _cells = new();
        private string _shownDef;
        private EntityId _boss;
        private bool _mini;

        /// <summary>
        /// The compact boss bar's closed look (prompt 11 A4): small icons that only show each part's state;
        /// they take no taps (the bar opens on a tap), so they are not touch targets.
        /// </summary>
        public bool Mini
        {
            get => _mini;
            set
            {
                _mini = value;
                Root.EnableInClassList("fc-boss-parts--mini", value);
                foreach (var cell in _cells) cell.Root.pickingMode = value ? PickingMode.Ignore : PickingMode.Position;
            }
        }

        public BossPartsRow()
        {
            Root = Kit.Box("fc-boss-parts");
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        /// <summary>An icon was tapped: the boss and the part's index.</summary>
        public event Action<EntityId, int> Tapped;

        /// <summary>The icon for a kind of part (the HUD's line icons).</summary>
        internal static string IconFor(string kind) => kind switch
        {
            "maingun" or "gun" or "turret" or "cannon" => "cannon",
            "flak" => "aa",
            "missiles" => "missile",
            "rockets" => "mlrs",
            "thermo" => "thermo",
            "railgun" => "railgun",
            "coilgun" => "bolt",
            "laser" => "laser",
            "shield" => "shield",
            "flamer" => "flame",
            "launcher" or "bay" or "uav" or "hangar" => "drone",
            "sam" => "sam",
            "emp" => "jammer",
            "howitzer" => "artillery",
            "mortar" => "mortar",
            "minigun" => "mg",
            "rotor" => "helicopter",
            "fan" => "wind",
            "ramp" => "reinforce",
            "antenna" => "command",
            "station" => "crosshair",
            "radar" => "cbradar",
            // Prompt 16 E.
            "aps" => "shield",
            "ciws" => "aa",
            "fuel" => "flame",
            "ew" => "jammer",
            _ => "gear",
        };

        /// <summary>Shows the boss's parts (null hides the row); <paramref name="focused"/> is the ordered part, or -1.</summary>
        public void Set(Vehicle boss, int focused)
        {
            if (boss == null || !boss.HasParts)
            {
                Root.style.display = DisplayStyle.None;
                _shownDef = null;
                return;
            }
            _boss = boss.Id;
            Show(boss.Def, boss.PartCount, boss.PartShare, boss.IsPartBroken, focused);
        }

        /// <summary>The row for a boss's parts without a battle (the screenshots): each part's share of health and whether it is broken.</summary>
        internal void Preview(MachineBrigade.Sim.Content.VehicleDef def, IReadOnlyList<float> shares, IReadOnlyList<bool> broken, int focused)
        {
            Show(def, def.Parts.Count, i => i < shares.Count ? shares[i] : 1f, i => i < broken.Count && broken[i], focused);
        }

        private void Show(MachineBrigade.Sim.Content.VehicleDef def, int count, Func<int, float> share, Func<int, bool> isBroken, int focused)
        {
            if (_shownDef != def.Id || _cells.Count != count) Build(def, count);
            Root.style.display = DisplayStyle.Flex;
            for (var i = 0; i < _cells.Count; i++)
            {
                var cell = _cells[i];
                var broken = isBroken(i);
                var fill = broken ? 0 : Mathf.RoundToInt(Mathf.Clamp01(share(i)) * 100f);
                if (fill != cell.ShownFill)
                {
                    cell.ShownFill = fill;
                    cell.Fill.style.width = Length.Percent(fill);
                }
                if (broken != cell.ShownBroken)
                {
                    cell.ShownBroken = broken;
                    cell.Root.EnableInClassList("fc-boss-part--broken", broken);
                }
                var focus = i == focused;
                if (focus != cell.ShownFocus)
                {
                    cell.ShownFocus = focus;
                    cell.Root.EnableInClassList("fc-boss-part--focused", focus);
                }
            }
        }

        private void Build(MachineBrigade.Sim.Content.VehicleDef def, int count)
        {
            Root.Clear();
            _cells.Clear();
            _shownDef = def.Id;
            for (var i = 0; i < count; i++)
            {
                var index = i;
                var part = def.Parts[i];
                var cell = Kit.Box("fc-boss-part", _mini ? PickingMode.Ignore : PickingMode.Position);
                cell.Add(Kit.Icon(IconFor(part.Kind), "fc-boss-part__icon"));
                var track = Kit.Box("fc-boss-part__track");
                var fill = Kit.Box("fc-boss-part__fill");
                track.Add(fill);
                cell.Add(track);
                // The cross over a broken part (two thin bars, shown by the "broken" class).
                cell.Add(Kit.Box("fc-boss-part__cross"));
                cell.Add(Kit.Box("fc-boss-part__cross fc-boss-part__cross--flip"));
                cell.tooltip = Strings.Get("part." + part.Kind);
                cell.AddManipulator(new Tap(() => Tapped?.Invoke(_boss, index)));
                Root.Add(cell);
                _cells.Add(new Cell { Root = cell, Fill = fill });
            }
        }
    }
}
