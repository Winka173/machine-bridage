using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Play-test 14 (Docs/fixes/playtest14_plan.md): a fire support's "Units called" tab. The units a support drops, flies
    /// in or builds are no deck cards of their own: they show here, each with its page. A call the player fills (the
    /// airdropped armour) shows its drop: the units chosen (tap one to take it out), the units that may be added (tap to
    /// add), their total against the cap and the call's price in CP; the drop is saved and used in every battle.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private void UnitsCalled(string id)
        {
            if (!_catalog.TryGetSupport(id, out var support)) return;
            if (support.CallMaxCp <= 0f)
            {
                _detailBody.Add(Kit.Body2(Strings.Get(support.Kind == SupportKind.Tower ? "detail.units.tower" : "detail.units.fixed")));
                var seen = new HashSet<string>();
                foreach (var unit in support.Units)
                    if (seen.Add(unit)) _detailBody.Add(CalledRow(unit, null));
                return;
            }

            var chosen = PlayerProfile.CallUnits(id, support, _catalog);
            var total = CallTotal(chosen);
            _detailBody.Add(Kit.Body2(Strings.Format("detail.units.call", ("cap", Strings.Num(support.CallMaxCp)), ("scale", Strings.Num(support.CallPriceScale)))));
            _detailBody.Add(Kit.Text(Strings.Format("detail.units.total", ("total", Strings.Num(total)), ("cap", Strings.Num(support.CallMaxCp)),
                ("price", support.CallPrice(total))), "fc-panel-title fc-mt-2"));
            _detailBody.Add(Kit.Caption(Strings.Get("detail.units.drop")));
            if (chosen.Count == 0) _detailBody.Add(Kit.Body2(Strings.Get("detail.units.empty")));
            for (var i = 0; i < chosen.Count; i++)
            {
                var index = i;
                _detailBody.Add(CalledRow(chosen[i], new KitButton(ButtonTier.Text, Strings.Get("detail.units.remove"), () =>
                {
                    var list = new List<string>(PlayerProfile.CallUnits(id, support, _catalog));
                    if (index < list.Count) list.RemoveAt(index);
                    PlayerProfile.SetCallUnits(id, list);
                    Refresh();
                }, "minus")));
            }
            _detailBody.Add(Kit.Caption(Strings.Get("detail.units.add")));
            foreach (var unit in support.CallChoices)
            {
                if (!_catalog.Vehicles.TryGetValue(unit, out var def)) continue;
                var pick = unit;
                VisualElement act;
                if (!PlayerProfile.IsUnlocked(unit)) act = Kit.Text(Strings.Get("detail.units.locked"), "fc-small");
                else if (total + def.BaseCp > support.CallMaxCp + 1e-4f) act = Kit.Text(Strings.Get("detail.units.full"), "fc-small");
                else
                    act = new KitButton(ButtonTier.Secondary, Strings.Get("detail.units.addOne"), () =>
                    {
                        var list = new List<string>(PlayerProfile.CallUnits(id, support, _catalog)) { pick };
                        PlayerProfile.SetCallUnits(id, list);
                        Refresh();
                    }, "plus");
                _detailBody.Add(CalledRow(unit, act));
            }
        }

        private float CallTotal(IReadOnlyList<string> units)
        {
            var total = 0f;
            foreach (var u in units)
                if (_catalog.Vehicles.TryGetValue(u, out var def)) total += def.BaseCp;
            return total;
        }

        /// <summary>A called unit's row: its icon, name and CP (a vehicle), its page on a tap of More, and <paramref name="act"/> at its end.</summary>
        private VisualElement CalledRow(string unit, VisualElement act)
        {
            var row = Kit.Box(KitPanel.SurfaceClass + " fc-row fc-mt-1");
            row.Add(Kit.Icon(CardIcons.For(unit), "fc-tactic-icon"));
            var text = Kit.Box("fc-cmdr-row__text");
            text.Add(Kit.Text(Strings.Unit(unit), "fc-body fc-row-text"));
            if (_catalog.Vehicles.TryGetValue(unit, out var def) && def.Fort == null)
                text.Add(Kit.Text(Strings.Format("detail.cpTag", def.BaseCp) + " · " + Strings.Get("class." + def.Class), "fc-small fc-row-text"));
            row.Add(text);
            row.Add(new KitButton(ButtonTier.Text, Strings.Get("detail.units.page"), () => OpenDetail(unit), "info"));
            if (act != null) row.Add(act);
            return row;
        }
    }
}
