using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Play-test 14 (Docs/fixes/playtest14_plan.md): two tabs of the Army page of their own.
    /// <list type="bullet">
    /// <item><description>Commander: the commander and the tactic for the next battle (each with Change), and the
    /// commander's starting forces, read only: the roles of its opening squad (balance.json openingSquads) and the cards
    /// of the deck that fill them.</description></item>
    /// <item><description>HQ: the HQ's type (Fortress with ground guns, Fortress with anti-air guns, Garrison, Shield),
    /// the light unit a Garrison calls, the unit each hangar turns out, and the wall lines. Every choice is free and
    /// saved at once (the loadout carries it into battle).</description></item>
    /// </list>
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _commandView, _commandBody, _hqView, _hqBody;

        private void BuildCommandViews(VisualElement page)
        {
            _commandView = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _commandBody = Kit.Box("fc-page__body");
            _commandView.Add(_commandBody);
            page.Add(_commandView);
            _hqView = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _hqBody = Kit.Box("fc-page__body");
            _hqView.Add(_hqBody);
            page.Add(_hqView);
        }

        // ------------------------------------------------------------------ the Commander tab

        private void RefreshCommand()
        {
            _commandBody.Clear();
            var slots = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mb-2");
            slots.Add(CommanderSlot());
            slots.Add(TacticSlot());
            _commandBody.Add(slots);

            var commander = CommanderPick.ForBattle(null);
            var forces = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mb-2");
            forces.Add(Kit.Text(Kit.Caps(Strings.Get("cmdr.forces")), "fc-panel-title"));
            var roles = _catalog.Opening.CommanderRoles(commander?.Id);
            if (roles.Count == 0)
            {
                forces.Add(Kit.Body2(Strings.Get("cmdr.forces.none")));
                _commandBody.Add(forces);
                return;
            }
            forces.Add(Kit.Body2(Strings.Format("cmdr.forces.info", ("share", Mathf.RoundToInt(_catalog.Opening.Share * 100f)))));
            var deck = MatchSettings.DeckVehicles;
            foreach (var role in roles)
            {
                // The card the deck fills this role with (the cheapest of the role, as the battle picks it), or none.
                var picked = OpeningSquads.Pick(_catalog, new[] { role }, deck, float.MaxValue);
                var row = Kit.Box("fc-row fc-mt-1");
                row.Add(Kit.Icon(picked.Count > 0 ? CardIcons.For(picked[0]) : "lock", "fc-tactic-icon"));
                var text = Kit.Box("fc-cmdr-row__text");
                text.Add(Kit.Text(RoleName(role), "fc-body fc-row-text"));
                text.Add(Kit.Text(picked.Count > 0
                    ? Strings.Format("cmdr.forces.card", ("card", Strings.Unit(picked[0])), ("cp", _catalog.Vehicles[picked[0]].BaseCp))
                    : Strings.Get("cmdr.forces.missing"), "fc-small fc-row-text"));
                row.Add(text);
                forces.Add(row);
            }
            _commandBody.Add(forces);
        }

        /// <summary>A role of the opening table in words (its own string, else its candidates' names).</summary>
        private string RoleName(string role)
        {
            if (Strings.Has("opening.role." + role)) return Strings.Get("opening.role." + role);
            if (!_catalog.Opening.Roles.TryGetValue(role, out var r)) return role;
            if (r.MaxCp > 0) return Strings.Format("opening.role.cheap", ("cp", r.MaxCp));
            var names = new List<string>();
            foreach (var id in r.Ids)
                if (_catalog.Vehicles.ContainsKey(id) && names.Count < 3) names.Add(Strings.Unit(id));
            return string.Join(" / ", names);
        }

        // ------------------------------------------------------------------ the HQ tab

        private static int HqLevelNow => Mathf.Clamp(Campaign.HqLevelCap, 1, Campaign.MaxHqLevel);

        private void RefreshHq()
        {
            _hqBody.Clear();
            var rules = _catalog.Base.HqTypes;
            var level = HqLevelNow;

            var types = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mb-2");
            types.Add(Kit.Text(Kit.Caps(Strings.Format("hq.tab.type", ("level", level))), "fc-panel-title"));
            types.Add(HqChoice(HqType.Fortress, HqBranch.Ground, "headquarters.fortress_ground",
                Strings.Format("hq.type.fortress.info", ("branch", Strings.Get("hq.branch.ground")), ("share", Mathf.RoundToInt(rules.FortressScale(level, HqBranch.Ground) * 100f)))));
            types.Add(HqChoice(HqType.Fortress, HqBranch.Air, "headquarters.fortress_air",
                Strings.Format("hq.type.fortress.info", ("branch", Strings.Get("hq.branch.air")), ("share", Mathf.RoundToInt(rules.FortressScale(level, HqBranch.Air) * 100f)))));
            types.Add(HqChoice(HqType.Garrison, HqBranch.Ground, "headquarters",
                Strings.Format("hq.type.garrison.info", ("every", Mathf.RoundToInt(rules.GarrisonEvery(level))), ("cap", rules.GarrisonCap(level)), ("clear", Mathf.RoundToInt(rules.GarrisonClear)))));
            types.Add(HqChoice(HqType.Shield, HqBranch.Ground, "headquarters.shield",
                Strings.Format("hq.type.shield.info", ("share", Mathf.RoundToInt(rules.ShieldScale(level) * 100f)), ("delay", Mathf.RoundToInt(rules.RegenDelay)),
                    ("regen", Strings.Num(rules.Regen(level) * 100f, "0.##")))));
            _hqBody.Add(types);

            // The light unit a Garrison calls.
            var calls = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mb-2");
            calls.Add(Kit.Text(Kit.Caps(Strings.Get("hq.tab.calls")), "fc-panel-title"));
            calls.Add(Kit.Body2(Strings.Get(PlayerProfile.HqType == HqType.Garrison ? "hq.tab.calls.info" : "hq.tab.calls.off")));
            calls.Add(UnitChips(rules.Callable, PlayerProfile.HqUnit, unit =>
            {
                PlayerProfile.HqUnit = unit;
                Refresh();
            }, Strings.Get("hq.tab.mixed")));
            _hqBody.Add(calls);

            // The unit each hangar card turns out.
            foreach (var id in MatchSettings.BaseHangars(_catalog))
            {
                var hangar = _catalog.Vehicles[id].Hangar;
                var panel = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mb-2");
                panel.Add(Kit.Text(Kit.Caps(Strings.Unit(id)), "fc-panel-title"));
                panel.Add(Kit.Body2(PlayerProfile.IsUnlocked(id)
                    ? Strings.Format("ul.hangar", ("units", Strings.Get("hq.tab.pick")), ("seconds", Mathf.RoundToInt(hangar.Every)),
                        ("count", hangar.AliveOf(_catalog.Vehicles.TryGetValue(PlayerProfile.HangarUnit(id) ?? hangar.Units[0], out var pickedDef) ? pickedDef : null)))
                    : Strings.Get("hq.tab.hangarLocked")));
                var hangarId = id;
                panel.Add(UnitChips(hangar.Units, PlayerProfile.HangarUnit(id) ?? hangar.Units[0], unit =>
                {
                    PlayerProfile.SetHangarUnit(hangarId, unit);
                    Refresh();
                }, null));
                _hqBody.Add(panel);
            }

            // The wall lines (moved here from the Base screen's bar).
            var walls = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mb-2");
            walls.Add(Kit.Text(Kit.Caps(Strings.Get("hq.tab.walls")), "fc-panel-title"));
            var wallRules = _catalog.Base.Walls;
            for (var i = 0; i < wallRules.FortressLines && i < PlayerProfile.WallLines; i++)
            {
                var line = i;
                var type = PlayerProfile.WallOf(i);
                var def = wallRules.Of(type);
                var row = new KitButton(ButtonTier.Secondary,
                    Strings.Format("camp.wall", ("line", Strings.Get("wall.line." + (i + 1))), ("type", Strings.Get("wall.type." + WallRules.Key(type)))), () =>
                    {
                        PlayerProfile.NextWallType(line);
                        Refresh();
                    });
                row.AddToClassList("fc-mt-1");
                walls.Add(row);
                if (type != WallType.None)
                    walls.Add(Kit.Text(Strings.Format("wall.type." + WallRules.Key(type) + ".info", ("durability", Strings.Num(def?.Durability ?? 0f, "0.0"))), "fc-small fc-row-text"));
            }
            walls.Add(Kit.Text(Strings.Get("hq.tab.wallsInfo"), "fc-small fc-row-text fc-mt-1"));
            _hqBody.Add(walls);
        }

        /// <summary>One HQ type as a row: its name, what it does at this level, and Choose (or Chosen).</summary>
        private VisualElement HqChoice(HqType type, HqBranch branch, string def, string info)
        {
            var chosen = PlayerProfile.HqType == type && (type != HqType.Fortress || PlayerProfile.HqBranch == branch);
            var row = Kit.Box("fc-row fc-mt-2" + (chosen ? " fc-cmdr-row--chosen" : ""));
            row.Add(Kit.Icon(TowerIcons.For("headquarters") ?? "hq", "fc-tactic-icon"));
            var text = Kit.Box("fc-cmdr-row__text");
            var name = Strings.Get("hq.type." + HqTypeRules.Key(type));
            if (type == HqType.Fortress) name = Strings.Format("hq.tab.fortress", ("type", name), ("branch", Strings.Get(branch == HqBranch.Air ? "hq.branch.air" : "hq.branch.ground")));
            text.Add(Kit.Text(name, "fc-body fc-row-text"));
            text.Add(Kit.Text(info, "fc-small fc-row-text"));
            row.Add(text);
            if (chosen) row.Add(Kit.Text(Strings.Get("hq.tab.chosen"), "fc-small fc-positive-text"));
            else
                row.Add(new KitButton(ButtonTier.Secondary, Strings.Get("cmdr.choose"), () =>
                {
                    PlayerProfile.HqType = type;
                    PlayerProfile.HqBranch = branch;
                    Refresh();
                }));
            return row;
        }

        /// <summary>A row of unit chips: the chosen one lit; a locked unit says so and cannot be picked. <paramref name="none"/>: an extra chip for no choice.</summary>
        private VisualElement UnitChips(IReadOnlyList<string> units, string chosen, System.Action<string> pick, string none)
        {
            var chips = new List<VisualElement>();
            if (none != null) chips.Add(new KitChip(none, string.IsNullOrEmpty(chosen), () => pick(null)));
            foreach (var id in units)
            {
                if (!_catalog.Vehicles.ContainsKey(id)) continue;
                var unit = id;
                var open = PlayerProfile.IsUnlocked(id);
                var chip = new KitChip(open ? Strings.Unit(id) : Strings.Format("hq.tab.locked", ("name", Strings.Unit(id))), id == chosen,
                    () =>
                    {
                        if (open) pick(unit);
                        else Note(Strings.Format("hq.tab.locked", ("name", Strings.Unit(unit))), true);
                    }, CardIcons.For(id));
                chips.Add(chip);
            }
            var row = new KitChipRow(chips);
            row.AddToClassList("fc-mt-1");
            return row;
        }
    }
}
