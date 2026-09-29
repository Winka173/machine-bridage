using System;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Army tab's Outpost view (prompt 14 H, split from the Base screen): the outpost's two slots, a small and a
    /// medium one, on a drawing of a captured point; the tower tray (small and medium towers); and in a few lines
    /// how an outpost works. The two towers belong to the base plan in use; an outpost always flies in with two, so
    /// a slot is replaced, never emptied. A card is tapped and then its slot (or the slot first, then the card).
    /// </summary>
    internal sealed class OutpostScreen
    {
        private readonly Catalog _catalog;
        private readonly Action<string, bool> _note;
        private readonly TowerTray _tray;
        private readonly (VisualElement target, SlotFace face)[] _slots = new (VisualElement, SlotFace)[2];
        private readonly VisualElement _info;
        private string _armed;
        private int _picked = -1;

        public OutpostScreen(Catalog catalog, Action<string, bool> note)
        {
            _catalog = catalog;
            _note = note ?? ((_, _) => { });
            Root = Kit.Box("fc-base fc-outpost", PickingMode.Position);
            var body = Kit.Box("fc-base__body");
            _tray = new TowerTray(catalog, new[] { TowerTray.Tab.Small, TowerTray.Tab.Medium }, TapTower);
            _tray.Changed += Refresh;
            _tray.Root.AddToClassList("fc-base__tray");
            body.Add(_tray.Root);

            var centre = Kit.Box(KitPanel.SurfaceClass + " fc-outpost__site");
            centre.Add(Kit.Caption(Strings.Get("camp.outpost")));
            var ring = Kit.Box("fc-outpost__ring");
            for (var i = 0; i < 2; i++)
            {
                var index = i;
                var target = Kit.Tappable("fc-base-slot fc-outpost__slot fc-base-slot--" + (i == 0 ? "small" : "medium"), () => TapSlot(index));
                var face = new SlotFace(false);
                target.Add(face);
                ring.Add(target);
                _slots[i] = (target, face);
            }
            centre.Add(ring);
            centre.Add(Kit.Text(Strings.Get("camp.outpostInfo"), "fc-small fc-outpost__caption"));
            body.Add(centre);

            var panel = Kit.Box(KitPanel.SurfaceClass + " fc-base__panel", PickingMode.Position);
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-base__panel-scroll");
            _info = scroll.contentContainer;
            panel.Add(scroll);
            body.Add(panel);
            Root.Add(body);
            Refresh();
        }

        public VisualElement Root { get; }

        /// <summary>A structure's detail page asked for: set by the menu.</summary>
        internal Action<string> OpenDetail { get; set; }

        private static BasePlan Plan => PlayerProfile.ActivePlan;

        private static LoadoutSlot SlotOf(int index) => LoadoutSlot.Outpost(index);

        internal string TowerAt(int index) => index < Plan.Outpost.Count ? Plan.Outpost[index] : BaseLayout.DefaultOutpost[index];

        internal void TapTower(string id)
        {
            if (!PlayerProfile.IsUnlocked(id))
            {
                _note(VehicleCardData.UnlockText(id), true);
                return;
            }
            if (_picked >= 0)
            {
                Put(_picked, id);
                return;
            }
            _armed = _armed == id ? null : id;
            Refresh();
        }

        internal void TapSlot(int index)
        {
            if (_armed != null)
            {
                Put(index, _armed);
                return;
            }
            _picked = _picked == index ? -1 : index;
            _tray.Shown = index == 0 ? TowerTray.Tab.Small : TowerTray.Tab.Medium;
            Refresh();
        }

        private void Put(int index, string id)
        {
            if (!BaseLayout.Fits(_catalog, id, SlotOf(index)))
            {
                _note(Strings.Format("camp.tooBig", Strings.Card(id), Strings.Get(index == 0 ? "camp.size.small" : "camp.size.medium").ToLowerInvariant()), true);
                return;
            }
            while (Plan.Outpost.Count < 2) Plan.Outpost.Add(BaseLayout.DefaultOutpost[Plan.Outpost.Count]);
            Plan.Outpost[index] = id;
            PlayerProfile.SaveBasePlans();
            _armed = null;
            _picked = index;
            _note(Strings.Format("camp.placed", Strings.Card(id)) + " " + Strings.Get("camp.saved"), false);
            Refresh();
        }

        public void Leave()
        {
            _armed = null;
            _picked = -1;
        }

        public bool Back()
        {
            if (_armed == null && _picked < 0) return false;
            Leave();
            Refresh();
            return true;
        }

        public void Refresh()
        {
            for (var i = 0; i < 2; i++)
            {
                var (target, face) = _slots[i];
                var tower = TowerAt(i);
                target.EnableInClassList("fc-base-slot--filled", tower != null);
                var lit = _armed != null && BaseLayout.Fits(_catalog, _armed, SlotOf(i));
                target.EnableInClassList("fc-base-slot--lit", lit);
                target.EnableInClassList("fc-base-slot--dim", _armed != null && !lit);
                target.EnableInClassList("fc-base-slot--picked", _picked == i);
                var render = tower != null ? CardArt.For(tower) : null;
                face.Art.style.backgroundImage = render != null ? new StyleBackground(render) : new StyleBackground(StyleKeyword.None);
                face.Word.text = Strings.Get(i == 0 ? "camp.size.small" : "camp.size.medium");
                face.Lock.style.display = DisplayStyle.None;
                face.Branch.style.display = tower != null && PlayerProfile.TowerBranch(tower) != null ? DisplayStyle.Flex : DisplayStyle.None;
                face.Rank = tower != null ? PlayerProfile.Rank(tower) : 0;
                target.tooltip = tower != null ? Strings.Card(tower) : "";
            }
            var picked = _picked;
            _tray.Refresh(_armed, id => (TowerAt(0) == id ? 1 : 0) + (TowerAt(1) == id ? 1 : 0),
                picked >= 0 ? id => BaseLayout.Fits(_catalog, id, SlotOf(picked)) : null);
            _info.Clear();
            _info.Add(Kit.Text(Kit.Caps(Strings.Get("camp.outpostHowTitle")), "fc-panel-title"));
            _info.Add(Kit.Text(Strings.Get("camp.outpostHow"), "fc-body-2 fc-mt-2"));
            if (picked >= 0 && TowerAt(picked) is { } id && _catalog.Vehicles.ContainsKey(id))
            {
                _info.Add(Kit.Text(Kit.Caps(Strings.Card(id)), "fc-panel-title fc-mt-4"));
                _info.Add(Kit.Text(Strings.Format("camp.cardLine", Strings.Get(picked == 0 ? "camp.size.small" : "camp.size.medium"), PlayerProfile.Rank(id)), "fc-small"));
                _info.Add(Kit.Text(Strings.Get("camp.outpostKeep"), "fc-small fc-mt-2"));
                if (OpenDetail != null) _info.Add(new KitButton(ButtonTier.Text, Strings.Get("army.info"), () => OpenDetail(id), "info"));
            }
        }
    }
}
