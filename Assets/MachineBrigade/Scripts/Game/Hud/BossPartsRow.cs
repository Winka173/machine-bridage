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
    /// orders every unit in reach at that part (tapping it again cancels). Self-contained and styled in
    /// Hud.uss ("boss-parts"), so the HUD's rebuild can move it as a whole.
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

        public BossPartsRow()
        {
            Root = UiKit.Box("boss-parts");
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
            if (_shownDef != boss.Def.Id || _cells.Count != boss.PartCount) Build(boss);
            Root.style.display = DisplayStyle.Flex;
            for (var i = 0; i < _cells.Count; i++)
            {
                var cell = _cells[i];
                var broken = boss.IsPartBroken(i);
                var fill = broken ? 0 : Mathf.RoundToInt(Mathf.Clamp01(boss.PartShare(i)) * 100f);
                if (fill != cell.ShownFill)
                {
                    cell.ShownFill = fill;
                    cell.Fill.style.width = Length.Percent(fill);
                }
                if (broken != cell.ShownBroken)
                {
                    cell.ShownBroken = broken;
                    cell.Root.EnableInClassList("broken", broken);
                }
                var focus = i == focused;
                if (focus != cell.ShownFocus)
                {
                    cell.ShownFocus = focus;
                    cell.Root.EnableInClassList("focused", focus);
                }
            }
        }

        private void Build(Vehicle boss)
        {
            Root.Clear();
            _cells.Clear();
            _shownDef = boss.Def.Id;
            for (var i = 0; i < boss.PartCount; i++)
            {
                var index = i;
                var part = boss.Def.Parts[i];
                var cell = UiKit.Box("boss-part", PickingMode.Position);
                cell.Add(UiKit.Icon(IconFor(part.Kind), UiKit.Ink, 1.8f));
                var track = UiKit.Box("boss-part-track");
                var fill = UiKit.Box("boss-part-fill");
                track.Add(fill);
                cell.Add(track);
                // The cross over a broken part (two thin bars, shown by the "broken" class).
                cell.Add(UiKit.Box("boss-part-cross"));
                cell.Add(UiKit.Box("boss-part-cross flip"));
                cell.tooltip = Strings.Get("part." + part.Kind);
                cell.AddManipulator(new Tap(() => Tapped?.Invoke(_boss, index)));
                Root.Add(cell);
                _cells.Add(new Cell { Root = cell, Fill = fill });
            }
        }
    }
}
