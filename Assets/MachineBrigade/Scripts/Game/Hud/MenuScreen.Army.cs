using System;
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Army tab: the battle deck across the top (eight vehicles, two supports, its average cost
    /// and what it lacks), the collection below with filters (Clash Royale's deck screen), and the
    /// equipment loadouts. Tapping a card offers Info or Use; Info opens its detail page.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum ArmyView
        {
            Deck,
            Equipment,
        }

        private enum CardFilter
        {
            All,
            Armor,
            Light,
            Artillery,
            Air,
            Support,
        }

        private VisualElement _deckView, _gearView, _deckSlots, _collection, _gearSlots, _gearGrid, _gearInfo, _popover;
        private Label _deckSummary, _deckWarnings, _popoverText, _gearTotal;
        private VisualElement _popoverInfo, _popoverUse;
        private ArmyView _armyView = ArmyView.Deck;
        private CardFilter _filter = CardFilter.All;
        private bool _sortByRank;
        private string _popoverCard;
        private GearBranch _branch = GearBranch.Armor;
        private GearItem _gearSelected;
        private GearSlot? _slotFilter;
        private readonly List<(VisualElement card, string id)> _collectionCards = new();

        private void BuildArmyPage()
        {
            var page = TabPage(Tab.Army, "army-page opaque");
            var views = UiKit.Box("segments army-views");
            foreach (var (view, icon, key) in new[] { (ArmyView.Deck, "deck", "army.deck"), (ArmyView.Equipment, "gear", "army.equipment") })
                views.Add(Choice(Segment(icon, Strings.Get(key), () =>
                {
                    _armyView = view;
                    HidePopover();
                    Refresh();
                }, view == ArmyView.Equipment), () => _armyView == view));
            page.Add(views);

            // Deck and collection --------------------------------------------------------------
            _deckView = UiKit.Box("army-deck");
            var strip = UiKit.Box("deck-strip");
            _deckSlots = UiKit.Box("deck-slots");
            strip.Add(_deckSlots);
            var summary = UiKit.Box("deck-summary");
            _deckSummary = UiKit.Text("", "deck-summary-text");
            _deckWarnings = UiKit.Text("", "deck-warnings");
            summary.Add(_deckSummary);
            summary.Add(_deckWarnings);
            // The doctrine for the next battle rides with the deck.
            var doctrines = UiKit.Box("doctrine-chips");
            foreach (var doctrine in Doctrine.All)
            {
                var id = doctrine.Id;
                var chip = UiKit.Button("doctrine-chip", () =>
                {
                    if (!Progression.DoctrineOwned(id))
                    {
                        Note(Strings.Format("doctrine.locked", Strings.Get("doctrine." + id), Progression.DoctrinePrice.ToString("N0")), true);
                        return;
                    }
                    MatchSettings.Doctrine = id;
                    MatchSettings.Save();
                    Note(Strings.Get("doctrine." + id + ".info"));
                    Refresh();
                });
                chip.Add(UiKit.Icon(DoctrineIcon(id), UiKit.Ink, 1.7f));
                chip.tooltip = Strings.Get("doctrine." + id);
                doctrines.Add(Choice(chip, () => MatchSettings.Doctrine == id));
            }
            summary.Add(doctrines);
            strip.Add(summary);
            _deckView.Add(strip);

            var filters = UiKit.Box("army-filters");
            foreach (var (filter, icon, key) in new[]
                     {
                         (CardFilter.All, "deck", "filter.all"), (CardFilter.Armor, "heavytank", "gear.branch.armor"),
                         (CardFilter.Light, "armoredcar", "gear.branch.light"), (CardFilter.Artillery, "artillery", "gear.branch.artillery"),
                         (CardFilter.Air, "jet", "gear.branch.air"), (CardFilter.Support, "barrage", "filter.support"),
                     })
            {
                var f = filter;
                filters.Add(Choice(Segment(icon, Strings.Get(key), () =>
                {
                    _filter = f;
                    HidePopover();
                    BuildCollection();
                    Refresh();
                }), () => _filter == f));
            }
            filters.Add(Choice(Segment("upgrade", Strings.Get("filter.byRank"), () =>
            {
                _sortByRank = !_sortByRank;
                BuildCollection();
                Refresh();
            }, true), () => _sortByRank));
            _deckView.Add(filters);
            var scroll = Scroller("army-scroll");
            _collection = scroll.contentContainer;
            _deckView.Add(scroll);
            page.Add(_deckView);

            // Equipment ------------------------------------------------------------------------
            _gearView = UiKit.Box("army-gear");
            var branches = UiKit.Box("gear-branches");
            foreach (GearBranch branch in Enum.GetValues(typeof(GearBranch)))
            {
                var b = branch;
                var button = UiKit.Button("gear-branch", () =>
                {
                    _branch = b;
                    Refresh();
                });
                button.Add(UiKit.Icon(BranchIcon(branch), UiKit.Ink, 1.9f));
                button.Add(UiKit.Text(Strings.Get("gear.branch." + branch.ToString().ToLowerInvariant()), "gear-branch-name"));
                branches.Add(Choice(button, () => _branch == b));
            }
            _gearView.Add(branches);
            var centre = UiKit.Box("gear-centre");
            centre.Add(UiKit.Text(Strings.Get("gear.loadout"), "menu-caps"));
            _gearSlots = UiKit.Box("gear-slots");
            centre.Add(_gearSlots);
            _gearTotal = UiKit.Text("", "gear-total");
            centre.Add(_gearTotal);
            _gearView.Add(centre);
            var inventory = UiKit.Box("gear-inventory");
            _gearInfo = UiKit.Box("gear-info");
            inventory.Add(_gearInfo);
            var tools = UiKit.Box("gear-tools");
            tools.Add(UiKit.Text(Strings.Get("gear.inventory"), "menu-caps"));
            tools.Add(UiKit.WideButton("wide small-wide", "upgrade", Strings.Get("gear.mergeAll"), null, () =>
            {
                var merges = PlayerProfile.MergeAll();
                Note(merges > 0 ? Strings.Format("gear.merged", merges) : Strings.Get("gear.nothingToMerge"), merges == 0);
                Refresh();
            }));
            inventory.Add(tools);
            var gearScroll = Scroller("gear-scroll");
            _gearGrid = gearScroll.contentContainer;
            inventory.Add(gearScroll);
            _gearView.Add(inventory);
            page.Add(_gearView);

            // The card popover: Info or Use.
            _popover = UiKit.Box("card-popover", PickingMode.Position);
            _popoverText = UiKit.Text("", "popover-text");
            _popover.Add(_popoverText);
            var buttons = UiKit.Box("popover-buttons");
            _popoverInfo = UiKit.WideButton("wide popover-button", "info", Strings.Get("army.info"), null, () =>
            {
                var id = _popoverCard;
                HidePopover();
                OpenDetail(id);
            });
            _popoverUse = UiKit.WideButton("wide primary popover-button", "deck", "", null, () =>
            {
                var id = _popoverCard;
                HidePopover();
                ToggleInDeck(id);
            });
            buttons.Add(_popoverInfo);
            buttons.Add(_popoverUse);
            _popover.Add(buttons);
            _popover.style.display = DisplayStyle.None;
            page.Add(_popover);
            BuildCollection();
        }

        private static bool IsSupport(string id) => MatchSettings.AllSupports.Contains(id);

        private bool Passes(string id)
        {
            if (_filter == CardFilter.All) return true;
            if (IsSupport(id)) return _filter == CardFilter.Support;
            if (!_catalog.Vehicles.TryGetValue(id, out var def)) return false;
            return _filter switch
            {
                CardFilter.Armor => Gear.BranchOf(def) == GearBranch.Armor,
                CardFilter.Light => Gear.BranchOf(def) == GearBranch.Light,
                CardFilter.Artillery => Gear.BranchOf(def) == GearBranch.Artillery,
                CardFilter.Air => Gear.BranchOf(def) == GearBranch.Air,
                _ => false,
            };
        }

        private int CostOf(string id) =>
            IsSupport(id) ? _catalog.TryGetSupport(id, out var s) ? s.CpCost : 0 : _catalog.Vehicles.TryGetValue(id, out var v) ? v.CpCost : 0;

        /// <summary>The collection grid: owned cards (sorted), then the locked ones with how to get them.</summary>
        private void BuildCollection()
        {
            _collection.Clear();
            _collectionCards.Clear();
            var all = MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(Passes).ToList();
            var owned = all.Where(PlayerProfile.IsUnlocked).ToList();
            owned = _sortByRank
                ? owned.OrderByDescending(PlayerProfile.Rank).ThenBy(CostOf).ToList()
                : owned.OrderBy(IsSupport).ThenBy(CostOf).ToList();
            var grid = UiKit.Box("collection-grid");
            foreach (var id in owned) grid.Add(CollectionCard(id));
            _collection.Add(grid);
            var locked = all.Where(id => !PlayerProfile.IsUnlocked(id)).ToList();
            if (locked.Count > 0)
            {
                _collection.Add(UiKit.Text(Strings.Format("army.locked", locked.Count), "menu-caps"));
                var lockedGrid = UiKit.Box("collection-grid");
                foreach (var id in locked) lockedGrid.Add(CollectionCard(id));
                _collection.Add(lockedGrid);
            }
        }

        private VisualElement CollectionCard(string id)
        {
            var card = UiKit.Button("unit-card-big", () => CardTapped(id));
            if (IsSupport(id)) card.AddToClassList("support");
            var art = UiKit.Box("unit-card-art");
            art.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Short(id), "unit-card-name"));
            var cost = UiKit.Box("unit-card-cost");
            cost.Add(UiKit.Text(CostOf(id).ToString(), "unit-card-cost-text"));
            card.Add(cost);
            card.Add(UiKit.Text("", "unit-card-rank"));
            // The blueprint bar; ready to rank up, it turns green with the upgrade arrow at its end.
            var foot = UiKit.Box("unit-card-foot");
            var track = UiKit.Box("unit-card-track");
            track.Add(UiKit.Box("unit-card-fill"));
            foot.Add(track);
            var up = UiKit.Box("unit-card-up");
            up.Add(UiKit.Icon("upgrade", UiKit.Ink, 2.4f));
            foot.Add(up);
            card.Add(foot);
            var check = UiKit.Box("unit-card-check");
            check.Add(UiKit.Icon("check", UiKit.Ink, 2.2f));
            card.Add(check);
            var lockBadge = UiKit.Box("unit-card-lock");
            lockBadge.Add(UiKit.Icon("lock", UiKit.Ink, 1.8f));
            card.Add(lockBadge);
            _collectionCards.Add((card, id));
            return card;
        }

        private void RefreshCard(VisualElement card, string id)
        {
            var unlocked = PlayerProfile.IsUnlocked(id);
            var rank = PlayerProfile.Rank(id);
            var need = CardRanks.BlueprintsToNext(rank);
            card.EnableInClassList("locked", !unlocked);
            card.EnableInClassList("in-deck", MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id));
            card.EnableInClassList("upgradable", PlayerProfile.CanRankUp(id));
            card.Q<Label>(className: "unit-card-rank").text = unlocked ? Strings.Format("arsenal.rank", rank) : "";
            var fill = card.Q(className: "unit-card-fill");
            fill.style.width = Length.Percent(need <= 0 ? 100f : Mathf.Clamp01(PlayerProfile.Blueprints(id) / (float)need) * 100f);
        }

        private void CardTapped(string id)
        {
            _popoverCard = id;
            var unlocked = PlayerProfile.IsUnlocked(id);
            var inDeck = MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id);
            _popoverText.text = unlocked ? Strings.Card(id) : LockReason(id);
            _popoverUse.style.display = unlocked ? DisplayStyle.Flex : DisplayStyle.None;
            _popoverUse.Q<Label>(className: "wide-title").text = Strings.Get(inDeck ? "army.remove" : "army.use");
            _popover.style.display = DisplayStyle.Flex;
            _popover.BringToFront();
        }

        private void HidePopover()
        {
            if (_popover != null) _popover.style.display = DisplayStyle.None;
        }

        /// <summary>Puts a card in the deck (the first empty slot) or takes it out of its slot; the others stay where they are.</summary>
        private void ToggleInDeck(string id)
        {
            if (!PlayerProfile.IsUnlocked(id)) return;
            var support = IsSupport(id);
            switch (MatchSettings.ToggleDeckCard(id, support))
            {
                case MatchSettings.DeckChange.Full:
                    Note(Strings.Get(support ? "army.fullSupports" : "army.fullVehicles"), true);
                    return;
                case MatchSettings.DeckChange.LastCard:
                    Note(Strings.Get(support ? "army.lastSupport" : "army.lastVehicle"), true);
                    return;
                case MatchSettings.DeckChange.Removed:
                    Note(Strings.Format("army.removed", Strings.Card(id)));
                    break;
                default:
                    Note(Strings.Format("army.added", Strings.Card(id)));
                    break;
            }
            MatchSettings.Save();
            Refresh();
        }

        private void RefreshArmy()
        {
            _deckView.style.display = _armyView == ArmyView.Deck ? DisplayStyle.Flex : DisplayStyle.None;
            _gearView.style.display = _armyView == ArmyView.Equipment ? DisplayStyle.Flex : DisplayStyle.None;
            if (_armyView == ArmyView.Deck) RefreshDeck();
            else RefreshGear();
        }

        private void RefreshDeck()
        {
            _deckSlots.Clear();
            foreach (var id in MatchSettings.DeckLayout(false)) _deckSlots.Add(DeckSlot(id, false));
            _deckSlots.Add(UiKit.Box("deck-divider"));
            foreach (var id in MatchSettings.DeckLayout(true)) _deckSlots.Add(DeckSlot(id, true));
            var costs = MatchSettings.DeckVehicles.Select(CostOf).ToList();
            _deckSummary.text = Strings.Format("army.summary", MatchSettings.DeckVehicles.Count, MatchSettings.DeckVehicleSlots,
                MatchSettings.DeckSupports.Count, MatchSettings.DeckSupportSlots, costs.Count > 0 ? costs.Average().ToString("0.0") : "-");
            _deckWarnings.text = DeckWarnings();
            foreach (var (card, id) in _collectionCards) RefreshCard(card, id);
        }

        private VisualElement DeckSlot(string id, bool support)
        {
            if (id == null)
            {
                var empty = UiKit.Box(support ? "deck-slot empty support" : "deck-slot empty");
                empty.Add(UiKit.Icon("plus", UiKit.Ink, 2f));
                return empty;
            }
            var slot = UiKit.Button(support ? "deck-slot support" : "deck-slot", () => CardTapped(id));
            slot.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            slot.Add(UiKit.Text(Strings.Format("arsenal.rank", PlayerProfile.Rank(id)), "deck-slot-rank"));
            var cost = UiKit.Box("unit-card-cost");
            cost.Add(UiKit.Text(CostOf(id).ToString(), "unit-card-cost-text"));
            slot.Add(cost);
            return slot;
        }

        /// <summary>What the deck lacks: nothing against aircraft, nothing that kills heavy armour, no artillery.</summary>
        private string DeckWarnings()
        {
            bool air = false, armour = false, artillery = false;
            foreach (var id in MatchSettings.DeckVehicles)
            {
                if (!_catalog.Vehicles.TryGetValue(id, out var def)) continue;
                foreach (var m in def.Mounts)
                    if (m.Weapon.CanTarget(true) && m.Weapon.DamageType == DamageType.Flak) air = true;
                if (def.Class is UnitClass.TankHunter or UnitClass.Heavy or UnitClass.Tank || def.Weapon.DamageType == DamageType.ArmorPiercing) armour = true;
                if (def.Weapon.MinRange > 0f) artillery = true;
            }
            var warnings = new List<string>();
            if (!air) warnings.Add(Strings.Get("army.noAir"));
            if (!armour) warnings.Add(Strings.Get("army.noArmour"));
            if (!artillery) warnings.Add(Strings.Get("army.noArtillery"));
            return warnings.Count == 0 ? Strings.Get("army.balanced") : string.Join("   ", warnings);
        }

        // ------------------------------------------------------------------ equipment

        private void RefreshGear()
        {
            _gearSlots.Clear();
            for (var s = 0; s < Gear.Slots; s++)
            {
                var slot = (GearSlot)s;
                var item = PlayerProfile.Equipped(_branch, slot);
                var tile = UiKit.Button(slot == GearSlot.Special ? "gear-slot2 special" : "gear-slot2", () =>
                {
                    _slotFilter = _slotFilter == slot ? null : slot;
                    _gearSelected = PlayerProfile.Equipped(_branch, slot);
                    Refresh();
                });
                tile.Add(item != null ? GearArt.Tile(item, slot == GearSlot.Special ? 104 : 92) : GearArt.Empty(slot, slot == GearSlot.Special ? 104 : 92));
                tile.Add(UiKit.Text(item != null ? StatText(item) : Strings.Get("gear.slot." + slot.ToString().ToLowerInvariant()), "gear-slot-value"));
                tile.EnableInClassList("chosen", _slotFilter == slot);
                _gearSlots.Add(tile);
            }
            var worn = new List<string>();
            for (var s = 0; s < Gear.Slots; s++)
                if (PlayerProfile.Equipped(_branch, (GearSlot)s) is { } piece)
                    worn.Add(StatText(piece));
            _gearTotal.text = worn.Count == 0 ? Strings.Get("gear.totalNone") : Strings.Format("gear.total", string.Join("  ·  ", worn));
            _gearGrid.Clear();
            var items = PlayerProfile.GearOwned.Where(g => _slotFilter == null || g.Slot == _slotFilter)
                .OrderByDescending(g => g.rarity).ThenBy(g => g.slot).ThenByDescending(g => g.level).ToList();
            if (items.Count == 0) _gearGrid.Add(UiKit.Text(Strings.Get(_slotFilter == null ? "gear.none" : "gear.noneForSlot"), "menu-note"));
            var grid = UiKit.Box("gear-grid2");
            foreach (var item in items)
            {
                var g = item;
                var tile = UiKit.Button("gear-cell", () =>
                {
                    _gearSelected = g;
                    Refresh();
                });
                tile.Add(GearArt.Tile(item, 92));
                tile.EnableInClassList("chosen", item == _gearSelected);
                tile.EnableInClassList("equipped", PlayerProfile.IsEquipped(item));
                grid.Add(tile);
            }
            _gearGrid.Add(grid);
            GearInfo();
        }

        /// <summary>The selected piece: what it does, against what is equipped in its slot now, and what can be done with it.</summary>
        private void GearInfo()
        {
            _gearInfo.Clear();
            var item = _gearSelected != null ? PlayerProfile.FindGear(_gearSelected.id) : null;
            if (item == null)
            {
                _gearInfo.Add(UiKit.Text(Strings.Get(_slotFilter == null ? "gear.pick" : "gear.pickFor2"), "menu-note"));
                return;
            }
            var head = UiKit.Box("gear-info-head");
            head.Add(GearArt.Tile(item, 84, showLevel: false));
            var names = UiKit.Box("gear-info-names");
            var title = UiKit.Text(GearName(item), "gear-info-title");
            title.style.color = GearArt.Colors[item.rarity];
            names.Add(title);
            names.Add(UiKit.Text(Strings.Format("gear.detail", Strings.Get("rarity." + item.Rarity.ToString().ToLowerInvariant()), item.level,
                Gear.LevelCap[item.rarity], StatText(item)), "gear-info-line"));
            var current = PlayerProfile.Equipped(_branch, item.Slot);
            if (current != null && current != item)
                names.Add(UiKit.Text(Strings.Format("gear.compare", StatText(current), StatText(item)), "gear-info-compare"));
            var partners = PlayerProfile.GearOwned.Count(g => g != item && Gear.CanMerge(g, item));
            names.Add(UiKit.Text(item.rarity < (int)Rarity.Legendary ? Strings.Format("gear.mergeHint", partners + 1) : Strings.Get("gear.top"), "gear-info-merge"));
            head.Add(names);
            _gearInfo.Add(head);
            var actions = UiKit.Box("gear-actions");
            var equipped = current == item;
            actions.Add(UiKit.WideButton(equipped ? "wide" : "wide primary", equipped ? "close" : "check",
                equipped ? Strings.Get("gear.unequip") : Strings.Get("gear.equipShort"), null, () =>
                {
                    if (equipped) PlayerProfile.Unequip(_branch, item.Slot);
                    else PlayerProfile.Equip(_branch, item);
                    Refresh();
                }));
            var cost = Gear.LevelCost(item);
            if (cost > 0)
                actions.Add(UiKit.WideButton("wide upgrade-button", "upgrade", Strings.Format("gear.levelUp", cost.ToString("N0")), null, () =>
                {
                    if (!PlayerProfile.TryLevelGear(item)) Note(Strings.Get("arsenal.needCoins"), true);
                    Refresh();
                }));
            if (partners >= 2)
                actions.Add(UiKit.WideButton("wide upgrade-button", "upgrade", Strings.Get("gear.merge"), null, () =>
                {
                    if (PlayerProfile.TryMerge(item) is { } merged)
                    {
                        _gearSelected = merged;
                        Note(Strings.Format("gear.mergedInto", GearName(merged)));
                    }
                    Refresh();
                }));
            _gearInfo.Add(actions);
        }

        private static string BranchIcon(GearBranch branch) => branch switch
        {
            GearBranch.Armor => "heavytank",
            GearBranch.Light => "armoredcar",
            GearBranch.Artillery => "artillery",
            _ => "jet",
        };

        private static string GearName(GearItem item) =>
            item.Slot == GearSlot.Special
                ? Strings.Get("module." + item.Module.ToString().ToLowerInvariant())
                : Strings.Get("gear.name." + item.Slot.ToString().ToLowerInvariant());

        /// <summary>A piece's effect in a few characters: "+8% dmg", "-5% taken", "Smoke 8 m".</summary>
        private static string StatText(GearItem item)
        {
            var v = Gear.Value(item);
            return item.Slot switch
            {
                GearSlot.Weapon => Strings.Format("stat.gear.damage", Pct(v)),
                GearSlot.Loader => Strings.Format("stat.gear.fire", Pct(v)),
                GearSlot.Armor => Strings.Format("stat.gear.hp", Pct(v)),
                GearSlot.Plating => Strings.Format("stat.gear.taken", Pct(v)),
                GearSlot.Engine => Strings.Format("stat.gear.speed", Pct(v)),
                GearSlot.Repair => Strings.Format("stat.gear.repair", (v * 100f).ToString("0.0")),
                _ => item.Module == SpecialModule.SmokeDischarger ? Strings.Format("stat.gear.smoke", Mathf.RoundToInt(v))
                    : item.Module == SpecialModule.AutoRepair ? Strings.Format("stat.gear.repair", (v * 100f).ToString("0.0"))
                    : item.Module == SpecialModule.ReactiveArmor ? Strings.Format("stat.gear.taken", Pct(v))
                    : Strings.Format("stat.gear.crew", Pct(v)),
            };
        }

        private static string Pct(float v) => Mathf.RoundToInt(v * 100f).ToString();
    }
}
