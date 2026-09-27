using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// A card's detail page (after World of Tanks Blitz's vehicle screen and Clash Royale's card
    /// info): the vehicle on a turntable on the left with who it beats and who beats it; on the
    /// right its numbers as bars against the roster's best (the equipment's share in blue, the
    /// next rank's in green), its weapons, and its branch's equipment; along the bottom, in the
    /// thumb's reach, the deck toggle and the rank-up with its price.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum DetailTab
        {
            Stats,
            Weapons,
            Equipment,
        }

        private VisualElement _detail, _detailPreview, _detailCounters, _detailBody, _detailDeck, _detailUpgrade, _detailPrintFill;
        private Label _detailRole, _detailPrints, _detailUpgradeTitle;
        private IconElement _detailIcon;
        private DetailTab _detailTab = DetailTab.Stats;
        private string _detailId;
        private List<string> _detailList = new();

        private void BuildDetailPage()
        {
            _detail = FullPage("detail-page");
            var columns = UiKit.Box("detail-columns");

            var left = UiKit.Box("detail-left");
            var stage = UiKit.Box("detail-stage");
            _detailPreview = UiKit.Box("detail-preview");
            stage.Add(_detailPreview);
            _detailIcon = UiKit.Icon("tank", UiKit.Ink, 1.4f);
            _detailIcon.AddToClassList("detail-big-icon");
            stage.Add(_detailIcon);
            var previous = UiKit.Button("detail-arrow left", () => StepDetail(-1));
            previous.Add(UiKit.Icon("arrow", UiKit.Ink, 2.2f));
            stage.Add(previous);
            var next = UiKit.Button("detail-arrow right", () => StepDetail(1));
            next.Add(UiKit.Icon("arrow", UiKit.Ink, 2.2f));
            stage.Add(next);
            left.Add(stage);
            _detailRole = UiKit.Text("", "detail-role");
            left.Add(_detailRole);
            _detailCounters = UiKit.Box("detail-counters");
            left.Add(_detailCounters);
            columns.Add(left);

            var right = UiKit.Box("detail-right");
            var tabs = UiKit.Box("segments detail-tabs");
            foreach (var (tab, icon, key) in new[] { (DetailTab.Stats, "gauge", "detail.stats"), (DetailTab.Weapons, "cannon", "detail.weaponsTab"),
                         (DetailTab.Equipment, "gear", "army.equipment") })
                tabs.Add(Choice(Segment(icon, Strings.Get(key), () =>
                {
                    _detailTab = tab;
                    Refresh();
                }, tab == DetailTab.Equipment), () => _detailTab == tab));
            right.Add(tabs);
            var scroll = Scroller("detail-scroll");
            _detailBody = scroll.contentContainer;
            right.Add(scroll);
            columns.Add(right);
            _detail.Add(columns);

            var dock = UiKit.Box("page-dock detail-dock");
            _detailDeck = UiKit.WideButton("wide deck-toggle", "deck", "", null, () =>
            {
                if (_detailId != null) ToggleInDeck(_detailId);
            });
            dock.Add(_detailDeck);
            var upgradeBox = UiKit.Box("detail-upgrade-box");
            var printRow = UiKit.Box("detail-print-row");
            printRow.Add(UiKit.Icon("blueprint", UiKit.Ink, 1.7f));
            var printTrack = UiKit.Box("detail-print-track");
            _detailPrintFill = UiKit.Box("detail-print-fill");
            printTrack.Add(_detailPrintFill);
            printRow.Add(printTrack);
            _detailPrints = UiKit.Text("", "detail-prints");
            printRow.Add(_detailPrints);
            upgradeBox.Add(printRow);
            _detailUpgrade = UiKit.Button("upgrade-big", UpgradeDetail);
            _detailUpgrade.Add(UiKit.Icon("upgrade", UiKit.Ink, 2f));
            _detailUpgradeTitle = UiKit.Text("", "upgrade-big-text");
            _detailUpgrade.Add(_detailUpgradeTitle);
            upgradeBox.Add(_detailUpgrade);
            dock.Add(upgradeBox);
            _detail.Add(dock);
        }

        /// <summary>Opens a card's detail page; the arrows step through the collection as it is filtered.</summary>
        private void OpenDetail(string id)
        {
            _detailId = id;
            _detailList = MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(Passes).ToList();
            if (!_detailList.Contains(id)) _detailList.Add(id);
            Open(_detail, Strings.Card(id).ToUpperInvariant());
            ShowPreview();
        }

        private void StepDetail(int step)
        {
            if (_detailList.Count == 0 || _detailId == null) return;
            var i = (_detailList.IndexOf(_detailId) + step + _detailList.Count) % _detailList.Count;
            _detailId = _detailList[i];
            if (_overlays.Count > 0 && _overlays.Peek().page == _detail)
            {
                _overlays.Pop();
                _overlays.Push((_detail, Strings.Card(_detailId).ToUpperInvariant()));
                _pageTitle.text = _overlays.Peek().title;
            }
            ShowPreview();
            Refresh();
        }

        private void ShowPreview()
        {
            var vehicle = _detailId != null && _catalog.Vehicles.TryGetValue(_detailId, out var def) ? def : null;
            if (vehicle != null && Preview != null)
            {
                Preview.Show(vehicle.Model, vehicle.Scale);
                _detailPreview.style.backgroundImage = Background.FromRenderTexture(Preview.Texture);
                _detailPreview.style.display = DisplayStyle.Flex;
                _detailIcon.style.display = DisplayStyle.None;
            }
            else
            {
                Preview?.Hide();
                _detailPreview.style.display = DisplayStyle.None;
                _detailIcon.style.display = DisplayStyle.Flex;
                if (_detailId != null) _detailIcon.Name = CardIcons.For(_detailId);
            }
        }

        private void RefreshDetail()
        {
            if (_detailId == null || _detail.style.display == DisplayStyle.None) return;
            var id = _detailId;
            var vehicle = _catalog.Vehicles.TryGetValue(id, out var def) ? def : null;
            var unlocked = PlayerProfile.IsUnlocked(id);
            var rank = PlayerProfile.Rank(id);

            // Left: role and counters.
            _detailRole.text = vehicle != null
                ? Strings.Format("detail.role", Strings.Get("class." + vehicle.Class), Strings.Get("gear.branch." + Gear.BranchOf(vehicle).ToString().ToLowerInvariant()),
                    Strings.Format("arsenal.rank", rank))
                : Strings.Format("detail.roleStrike", Strings.Format("arsenal.rank", rank));
            _detailCounters.Clear();
            if (vehicle != null)
            {
                CounterRow("detail.strongVs", Counters.StrongVs(vehicle.Class), "strong");
                CounterRow("detail.weakVs", Counters.WeakVs(vehicle.Class), "weak");
            }

            // Right: the chosen tab.
            _detailBody.Clear();
            switch (_detailTab)
            {
                case DetailTab.Stats:
                    if (vehicle != null) VehicleStats(vehicle, rank);
                    else StrikeStats(id, rank);
                    break;
                case DetailTab.Weapons:
                    if (vehicle != null) VehicleWeapons(vehicle);
                    else _detailBody.Add(UiKit.Text(Strings.Get("support." + id + ".info"), "detail-note"));
                    break;
                default:
                    if (vehicle != null) DetailEquipment(vehicle);
                    else _detailBody.Add(UiKit.Text(Strings.Get("detail.strikeNoGear"), "detail-note"));
                    break;
            }

            // Bottom: deck toggle and rank-up.
            var inDeck = MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id);
            _detailDeck.style.display = unlocked ? DisplayStyle.Flex : DisplayStyle.None;
            _detailDeck.EnableInClassList("chosen", inDeck);
            _detailDeck.Q<Label>(className: "wide-title").text = Strings.Get(inDeck ? "detail.inDeck" : "detail.addToDeck");
            var need = CardRanks.BlueprintsToNext(rank);
            var have = PlayerProfile.Blueprints(id);
            _detailPrintFill.style.width = Length.Percent(need <= 0 ? 100f : Mathf.Clamp01((float)have / need) * 100f);
            _detailPrints.text = need <= 0 ? "MAX" : $"{have}/{need}";
            _detailUpgrade.EnableInClassList("ready", PlayerProfile.CanRankUp(id));
            _detailUpgrade.EnableInClassList("maxed", rank >= CardRanks.Max);
            _detailUpgradeTitle.text = !unlocked ? LockReasonShort(id)
                : rank >= CardRanks.Max ? Strings.Get("arsenal.maxRank")
                : have + PlayerProfile.UniversalBlueprints < need ? Strings.Get("detail.getPrints")
                : Strings.Format("detail.rankUp", rank + 1, CardRanks.CoinsToNext(rank).ToString("N0"));
        }

        private string LockReasonShort(string id)
        {
            var mission = Progression.UnlockMission(id);
            return mission != null ? Strings.Format("detail.unlockMission", Campaign.IndexOf(mission.Id) + 1) : Strings.Get("detail.unlockShop");
        }

        private void UpgradeDetail()
        {
            var id = _detailId;
            if (id == null) return;
            if (!PlayerProfile.IsUnlocked(id))
            {
                OpenShop(ShopTab.Units);
                return;
            }
            var rank = PlayerProfile.Rank(id);
            if (rank >= CardRanks.Max) return;
            if (PlayerProfile.Blueprints(id) + PlayerProfile.UniversalBlueprints < CardRanks.BlueprintsToNext(rank))
            {
                // Short of blueprints: they come from crates.
                OpenShop(ShopTab.Crates);
                return;
            }
            if (PlayerProfile.TryRankUp(id)) Note(Strings.Format("arsenal.ranked", Strings.Card(id), PlayerProfile.Rank(id)));
            else Note(Strings.Get("arsenal.needCoins"), true);
            Refresh();
        }

        private void CounterRow(string key, IReadOnlyList<UnitClass> classes, string kind)
        {
            if (classes.Count == 0) return;
            var row = UiKit.Box("counter-row " + kind);
            row.Add(UiKit.Text(Strings.Get(key), "counter-label"));
            foreach (var c in classes)
            {
                var chip = UiKit.Box("counter-chip");
                chip.Add(UiKit.Icon(ClassIcon(c), UiKit.Ink, 1.7f));
                chip.Add(UiKit.Text(Strings.Get("class." + c), "counter-name"));
                row.Add(chip);
            }
            _detailCounters.Add(row);
        }

        // ------------------------------------------------------------------ the numbers

        private void VehicleStats(VehicleDef def, int rank)
        {
            var now = PlayerProfile.BoostFor(def);
            // The next rank's gain on top, as a ghost segment (Clash Royale shows the upgrade in green).
            var loadout = PlayerProfile.Loadout(Gear.BranchOf(def)).ToList();
            var next = rank < CardRanks.Max ? Gear.Boost(rank + 1, loadout) : now;
            var stats = UnitStats.For(_catalog, def, now);
            var after = UnitStats.For(_catalog, def, next);
            var plain = UnitStats.For(_catalog, def, VehicleBoost.None);
            for (var i = 0; i < stats.Count; i++) StatRow(stats[i], plain[i].Value, after[i].Boosted);
            // Words for what the bars cannot say.
            var info = UiKit.Box("stat-facts");
            info.Add(Fact("shield", Strings.Format("detail.armour", Strings.Get("armor." + def.Armor.ToString().ToLowerInvariant()))));
            info.Add(Fact("cp", Strings.Format("detail.cost", def.CpCost)));
            if (def.Weapon.Ammo > 0) info.Add(Fact("ammo", Strings.Format("detail.magazine", def.Weapon.Ammo, Mathf.RoundToInt(def.Weapon.MagazineReload))));
            if (def.Weapon.MinRange > 0f) info.Add(Fact("crosshair", Strings.Format("detail.minRange", Mathf.RoundToInt(def.Weapon.MinRange))));
            if (now.Special != SpecialModule.None) info.Add(Fact("star", Strings.Get("module." + now.Special.ToString().ToLowerInvariant())));
            _detailBody.Add(info);
        }

        private VisualElement Fact(string icon, string text)
        {
            var fact = UiKit.Box("stat-fact");
            fact.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
            fact.Add(UiKit.Text(text, "stat-fact-text"));
            return fact;
        }

        /// <summary>
        /// One number: its name and value (with the upgrade in blue), and a bar against the roster's
        /// best, square-rooted so a tank's damage still shows next to a bomber's; the base in white,
        /// the equipment and rank in blue, the next rank as a green ghost.
        /// </summary>
        private void StatRow(UnitStats.Stat stat, float plain, float nextRank)
        {
            var row = UiKit.Box("stat-row");
            var head = UiKit.Box("stat-head");
            head.Add(UiKit.Text(Strings.Get(stat.Key), "stat-name"));
            var value = UiKit.Text(stat.Boosted.ToString(stat.Format), "stat-value");
            head.Add(value);
            var gain = stat.Boosted - plain;
            if (gain > 0f && Shows(gain, stat.Format)) head.Add(UiKit.Text("+" + gain.ToString(stat.Format), "stat-gain"));
            var ahead = nextRank - stat.Boosted;
            if (ahead > 0f && Shows(ahead, stat.Format))
            {
                // What the next rank adds, in green with the upgrade arrow.
                var next = UiKit.Box("stat-next");
                next.Add(UiKit.Icon("upgrade", UiKit.Ink, 2.2f));
                next.Add(UiKit.Text("+" + ahead.ToString(stat.Format), "stat-next-text"));
                head.Add(next);
            }
            row.Add(head);
            var bar = UiKit.Box("stat-bar");
            float Share(float v) => Mathf.Clamp01(Mathf.Sqrt(Mathf.Max(0f, v) / Mathf.Max(0.01f, stat.Best)));
            var ghost = UiKit.Box("stat-bar-next");
            ghost.style.width = Length.Percent(Share(nextRank) * 100f);
            bar.Add(ghost);
            var boosted = UiKit.Box("stat-bar-boost");
            boosted.style.width = Length.Percent(Share(stat.Boosted) * 100f);
            bar.Add(boosted);
            var basePart = UiKit.Box("stat-bar-base");
            basePart.style.width = Length.Percent(Share(plain) * 100f);
            bar.Add(basePart);
            row.Add(bar);
            _detailBody.Add(row);
        }

        /// <summary>A gain worth printing: not one that rounds to nothing in the stat's format.</summary>
        private static bool Shows(float value, string format)
        {
            foreach (var c in value.ToString(format))
                if (c >= '1' && c <= '9') return true;
            return false;
        }

        private void StrikeStats(string id, int rank)
        {
            if (!_catalog.TryGetSupport(id, out var s)) return;
            var boost = 1f + CardRanks.Bonus(rank);
            var nextBoost = 1f + CardRanks.Bonus(Mathf.Min(CardRanks.Max, rank + 1));
            if (s.Damage > 0f && s.Kind is SupportKind.Barrage or SupportKind.Airstrike or SupportKind.CruiseMissile)
            {
                var total = s.Damage * Mathf.Max(1, s.Count);
                StatRow(new UnitStats.Stat("stat.detail.strikeDamage", s.Damage, s.Damage * boost, 4000f, "N0"), s.Damage, s.Damage * nextBoost);
                StatRow(new UnitStats.Stat("stat.detail.strikeTotal", total, total * boost, 12000f, "N0"), total, total * nextBoost);
                StatRow(new UnitStats.Stat("stat.detail.blast", s.BlastRadius, s.BlastRadius, 27f, "0.#"), s.BlastRadius, s.BlastRadius);
            }
            var facts = UiKit.Box("stat-facts");
            facts.Add(Fact("cp", Strings.Format("detail.cost", s.CpCost)));
            facts.Add(Fact("restart", Strings.Format("detail.cooldown", Mathf.RoundToInt(s.Cooldown))));
            if (s.Count > 1) facts.Add(Fact("barrage", Strings.Format("detail.count", s.Count)));
            facts.Add(Fact("info", Strings.Get("support." + id + ".info")));
            _detailBody.Add(facts);
        }

        private void VehicleWeapons(VehicleDef def)
        {
            var mounts = def.Mounts;
            var lines = WeaponInfo.Of(def);
            for (var i = 0; i < lines.Count && i < mounts.Count; i++)
            {
                var w = mounts[i].Weapon;
                var row = UiKit.Box("weapon-row");
                row.Add(UiKit.Icon(lines[i].Icon, UiKit.Ink, 1.7f));
                var text = UiKit.Box("weapon-text");
                text.Add(UiKit.Text(lines[i].Name + (i == 0 ? "  ·  " + Strings.Get("detail.main") : ""), "weapon-name"));
                var burst = w.Burst > 1 ? $" × {w.Burst}" : "";
                text.Add(UiKit.Text(Strings.Format("detail.weaponLine", w.Damage.ToString("N0") + burst, w.Cooldown.ToString("0.#"), Mathf.RoundToInt(w.Range),
                    lines[i].Targets), "weapon-line"));
                if (lines[i].Ammo > 0) text.Add(UiKit.Text(Strings.Format("detail.ammo", lines[i].Ammo), "weapon-line ammo"));
                row.Add(text);
                _detailBody.Add(row);
            }
        }

        /// <summary>The branch's loadout on this vehicle: six slots and the special one; a tap opens the equipment view on that slot.</summary>
        private void DetailEquipment(VehicleDef def)
        {
            var branch = Gear.BranchOf(def);
            _detailBody.Add(UiKit.Text(Strings.Format("detail.sharedGear", Strings.Get("gear.branch." + branch.ToString().ToLowerInvariant())), "detail-note"));
            var slots = UiKit.Box("detail-gear");
            for (var s = 0; s < Gear.Slots; s++)
            {
                var slot = (GearSlot)s;
                var item = PlayerProfile.Equipped(branch, slot);
                var tile = UiKit.Button("gear-slot2", () =>
                {
                    _branch = branch;
                    _slotFilter = slot;
                    _gearSelected = PlayerProfile.Equipped(branch, slot);
                    _armyView = ArmyView.Equipment;
                    ShowTab(Tab.Army);
                });
                tile.Add(item != null ? GearArt.Tile(item, 80) : GearArt.Empty(slot, 80));
                tile.Add(UiKit.Text(item != null ? StatText(item) : Strings.Get("gear.slot." + slot.ToString().ToLowerInvariant()), "gear-slot-value"));
                slots.Add(tile);
            }
            _detailBody.Add(slots);
        }
    }
}
