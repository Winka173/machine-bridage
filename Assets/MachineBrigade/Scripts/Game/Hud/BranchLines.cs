using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The tower-branch rework (DECISIONS 19T, D): what sets a tower's two rank-7 branches apart, worked out from their data
    /// (reach, what they hit, their mechanism: interceptors, dome or tower shields, loot, radar, counter-battery, fire over
    /// walls, mines, jamming), and the side-by-side picker the Base screen and the detail page share: each branch's render,
    /// icon, role line, when to pick it and the facts where it differs from the other, never only percentages.
    /// </summary>
    public static class BranchLines
    {
        private static string N(float v) => v.ToString(v >= 10f || Math.Abs(v - MathF.Round(v)) < 0.05f ? "0" : "0.#", Strings.Culture);

        /// <summary>A branch's facts, from its data.</summary>
        public static List<string> Facts(VehicleDef def)
        {
            var facts = new List<string>();
            var weapons = def.Mounts.Select(m => m.Weapon).Where(w => w.Damage > 0f).ToList();
            if (weapons.Count > 0)
            {
                facts.Add(Strings.Format("branch.range", N(weapons.Max(w => w.Range))));
                bool ground = weapons.Any(w => w.CanTarget(false)), air = weapons.Any(w => w.CanTarget(true));
                facts.Add(Strings.Format("branch.targets", Strings.Get(ground && air ? "branch.targets.all" : air ? "branch.targets.air" : "branch.targets.ground")));
                if (weapons.Any(w => w.Indirect && w.MinRange > 0f)) facts.Add(Strings.Get("branch.mech.overWalls"));
            }
            else if (def.Mines == null && def.Dome == null && def.Wards == null && def.Relay == null && def.Loot == null && def.Aps == null && def.Jammer <= 0f)
                facts.Add(Strings.Format("branch.targets", Strings.Get("branch.targets.none")));
            if (def.Aps is { } aps)
                facts.Add(Strings.Format("branch.mech.intercepts", Strings.Get(aps.Heavy ? "branch.mech.heavy" : !aps.Direct ? "branch.mech.lobbed" : "branch.mech.direct")) +
                          $" · {aps.Charges} · {N(aps.Radius)} m");
            if (def.Dome is { } dome) facts.Add(Strings.Format("branch.mech.dome", ("metres", N(dome.Radius)), ("count", N(dome.Hp))));
            if (def.Wards is { } wards) facts.Add(Strings.Format("branch.mech.wards", ("metres", N(wards.Radius)), ("health", N(wards.Hp)), ("seconds", N(wards.Recharge))));
            if (def.Loot is { } loot) facts.Add(Strings.Format("branch.mech.loot", ("percent", N(loot.Share * 100f)), ("metres", N(loot.Radius))));
            if (def.Relay is { } relay) facts.Add(Strings.Format("branch.mech.relay", N(relay.Income)));
            if (def.RevealAir > 0f) facts.Add(Strings.Format("branch.mech.revealAir", N(def.RevealAir)));
            if (def.CounterBattery is { } cb) facts.Add(Strings.Format("branch.mech.counterBattery", N(cb.Range)));
            if (def.Mines is { } mines) facts.Add(Strings.Format("branch.mech.mines", ("count", mines.Max), ("damage", N(mines.Blast.Damage))));
            if (def.Jammer > 0f) facts.Add(Strings.Format("branch.mech.jammer", N(def.Jammer)));
            facts.Add(Strings.Format("branch.mech.hp", N(def.MaxHp)));
            return facts;
        }

        /// <summary>The facts of <paramref name="def"/> the other branch does not share (what the picker shows).</summary>
        public static List<string> Differences(VehicleDef def, VehicleDef other)
        {
            var theirs = new HashSet<string>(Facts(other));
            var mine = Facts(def).Where(f => !theirs.Contains(f)).ToList();
            return mine.Count > 0 ? mine : Facts(def);
        }

        /// <summary>Its "when to pick it" line.</summary>
        public static string When(string branchId) => Strings.Has("branch." + branchId + ".when") ? Strings.Format("branch.when", Strings.Get("branch." + branchId + ".when")) : "";

        /// <summary>
        /// The picker: the tower's branches side by side, each tappable (<paramref name="choose"/>), the chosen one marked,
        /// all locked under rank 7.
        /// </summary>
        public static VisualElement Picker(Catalog catalog, string towerId, string chosen, bool locked, Action<string> choose)
        {
            var branches = Sim.Modes.TowerCards.Branches(catalog, towerId);
            // Side by side; stacked in Large text (Screens.uss), where a long English word no longer fits half the panel.
            var row = Kit.Box("fc-row fc-base__branch-pair");
            row.style.alignItems = Align.Stretch;
            for (var i = 0; i < branches.Count; i++)
            {
                var id = branches[i];
                var def = catalog.Vehicles[id];
                var other = catalog.Vehicles[branches[(i + 1) % branches.Count]];
                var card = Kit.Tappable(KitPanel.SurfaceClass + " fc-base__branch", () => choose(id));
                // Equal halves side by side, stacked in Large text: the sizes are in Screens.uss (.fc-base__branch-pair).
                if (i > 0) card.AddToClassList("fc-base__branch--next");
                card.EnableInClassList("fc-base__branch--locked", locked);
                card.EnableInClassList("fc-base__branch--chosen", id == chosen);
                // Its render (the branch's own once the card renders exist, the tower's until then).
                var render = CardArt.For(id) ?? CardArt.For(towerId);
                if (render != null)
                {
                    var art = Kit.Box("fc-base__branch-art");
                    art.style.height = 72f;
                    art.style.backgroundImage = Background.FromTexture2D(render);
                    art.style.unityBackgroundScaleMode = ScaleMode.ScaleToFit;
                    card.Add(art);
                }
                var head = Kit.Box("fc-row");
                if (TowerIcons.For(id) is { } icon) head.Add(Kit.Icon(icon));
                // The short name in the narrow card (prompt 21 K2: English names run longer); "In use" on its own line.
                head.Add(Kit.Text(Kit.Caps(Strings.Short(id)), "fc-panel-title fc-row-text"));
                if (locked) head.Add(Kit.Icon("lock", "fc-base__branch-lock"));
                card.Add(head);
                if (!locked && id == chosen) card.Add(Kit.Text(Kit.Caps(Strings.Get("camp.current")), "fc-caption fc-base__branch-tag fc-base__branch-tag--line"));
                card.Add(Kit.Text(Strings.Get("branch." + id + ".info"), "fc-small"));
                if (When(id) is { Length: > 0 } when) card.Add(Kit.Text(when, "fc-small fc-base__note"));
                foreach (var fact in Differences(def, other)) card.Add(Kit.Text("· " + fact, "fc-small"));
                row.Add(card);
            }
            return row;
        }
    }
}
