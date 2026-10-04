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
    /// The Army tab, four tabs: Deck, Towers &amp; modules, Equipment, Base.
    /// E3, Deck: the eight vehicles and two supports as full cards; beside them the deck's overview
    /// (how many, the average cost) and its role cover (tank killers, anti-air, artillery, repair,
    /// recon; what is missing in the warning colour), the commander for the next battle; then the
    /// branch filter chips with the sort button apart, and the collection as cards.
    /// E3b, Towers &amp; modules (test feedback 2, DECISIONS 12E): the base's towers by size and its
    /// utility modules as cards (render, rank, size, the upgrade mark), beside the vehicles, since
    /// both level up and wear gear; a tap opens the same detail page as a vehicle's, where the rank,
    /// the branch and the three gear slots are changed. The Base tab still places them.
    /// E5, Equipment: the branch, its seven slots as gear cards; picking a slot lists at once what
    /// fits it with its change against what is worn; picking a piece shows its lines and actions.
    /// E6, Base: <see cref="BaseScreen"/>.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        /// <summary>The Army page's tabs, in their order (play-test 14: Commander and HQ have their own).</summary>
        private enum ArmyView
        {
            Deck,
            Commander,
            Towers,
            Equipment,
            Base,
            Hq,
            Outpost,
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

        private enum CardSort
        {
            Cost,
            Level,
            Name,
        }

        private VisualElement _deckView, _gearView, _deckRow, _deckOverview, _collection, _gearSlots, _gearList, _gearInfo, _gearDetails, _towersView, _towersBody;
        private KitTabs _armyTabs;
        private KitSortButton _sortButton;
        private readonly List<(KitChip chip, CardFilter filter)> _filterChips = new();
        private readonly List<(KitChip chip, GearBranch branch)> _branchChips = new();
        private ArmyView _armyView = ArmyView.Deck;
        private CardFilter _filter = CardFilter.All;
        private CardSort _sort = CardSort.Cost;
        private GearQuery.Sort _gearSort = GearQuery.Sort.Rarity;
        private GearBranch _branch = GearBranch.Armor;
        private GearItem _gearSelected;
        private GearSlot? _slotFilter;
        private BaseScreen _base;
        private OutpostScreen _outpost;

        private void BuildArmyPage()
        {
            var page = TabPage(Tab.Army, "fc-page--opaque fc-army");
            _armyTabs = new KitTabs(new[] { Strings.Get("army.deck"), Strings.Get("army.commander"), Strings.Get("army.towers"), Strings.Get("army.equipment"), Strings.Get("army.base"),
                Strings.Get("army.hq"), Strings.Get("army.outpost") }, 0, i =>
            {
                _armyView = (ArmyView)i;
                Refresh();
            });
            page.Add(_armyTabs);

            // Deck and collection ---------------------------------------------------------------------
            _deckView = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            var deckBody = Kit.Box("fc-page__body");
            var deckStrip = Kit.Scroll(ScrollViewMode.Horizontal, "fc-army__deck-strip");
            _deckRow = deckStrip.contentContainer;
            deckBody.Add(deckStrip);
            _deckOverview = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-army__overview");
            deckBody.Add(_deckOverview);
            var chips = new List<VisualElement>();
            foreach (CardFilter filter in Enum.GetValues(typeof(CardFilter)))
            {
                var f = filter;
                var chip = filter == CardFilter.All
                    ? new KitChip(Strings.Get("filter.all"), true, () => SetFilter(f))
                    : KitChip.Branch(BranchOf(filter), false, () => SetFilter(f));
                _filterChips.Add((chip, filter));
                chips.Add(chip);
            }
            _sortButton = new KitSortButton(SortName(_sort), PickSort);
            deckBody.Add(new KitChipRow(chips, _sortButton));
            _collection = Kit.Box("fc-army__collection");
            deckBody.Add(_collection);
            _deckView.Add(deckBody);
            page.Add(_deckView);

            // Play-test 14: the Commander and HQ tabs.
            BuildCommandViews(page);

            // Towers and modules ------------------------------------------------------------------------
            _towersView = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _towersBody = Kit.Box("fc-page__body");
            _towersView.Add(_towersBody);
            page.Add(_towersView);

            // Equipment ---------------------------------------------------------------------------------
            _gearView = Kit.Box("fc-army__gear");
            var gearLeft = Kit.Scroll(ScrollViewMode.Vertical, "fc-army__gear-left");
            var left = Kit.Box("fc-page__body");
            var branches = new List<VisualElement>();
            foreach (GearBranch branch in Enum.GetValues(typeof(GearBranch)))
            {
                var b = branch;
                var chip = KitChip.Branch(KitOf(branch), branch == _branch, () =>
                {
                    _branch = b;
                    _gearSelected = null;
                    Refresh();
                });
                _branchChips.Add((chip, branch));
                branches.Add(chip);
            }
            left.Add(new KitChipRow(branches));
            _gearSlots = Kit.Box("fc-army__slots");
            left.Add(_gearSlots);
            gearLeft.Add(left);
            _gearView.Add(gearLeft);
            // Play-test 10 (DECISIONS "PT10 gear menu"): the picked piece's head and its buttons stay pinned at the top;
            // its long lines and the list share one scroll view under them. The whole piece's page used to sit above
            // the list unscrolled, so a long one pushed its buttons and the list off the panel.
            var gearRight = Kit.Box(KitPanel.SurfaceClass + " fc-army__gear-right", PickingMode.Position);
            _gearInfo = Kit.Box("fc-army__gear-info");
            gearRight.Add(_gearInfo);
            var listScroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-army__gear-list");
            _gearDetails = Kit.Box("fc-army__gear-details");
            listScroll.Add(_gearDetails);
            _gearList = Kit.Box("fc-army__gear-items");
            listScroll.Add(_gearList);
            gearRight.Add(listScroll);
            _gearView.Add(gearRight);
            page.Add(_gearView);

            // Base ---------------------------------------------------------------------------------------
            _base = new BaseScreen(_catalog, (text, warn) => Note(text, warn), Refresh)
            {
                OpenDetail = OpenDetail,
                OpenHq = () =>
                {
                    _armyView = ArmyView.Hq;
                    Refresh();
                },
            };
            _base.Root.AddToClassList("fc-army__base");
            page.Add(_base.Root);

            // Outpost (prompt 14 H: its own tab beside the base) ---------------------------------------------
            _outpost = new OutpostScreen(_catalog, (text, warn) => Note(text, warn)) { OpenDetail = OpenDetail };
            _outpost.Root.AddToClassList("fc-army__base");
            page.Add(_outpost.Root);
        }

        private static KitBranch BranchOf(CardFilter filter) => filter switch
        {
            CardFilter.Armor => KitBranch.Armor,
            CardFilter.Light => KitBranch.Light,
            CardFilter.Artillery => KitBranch.Artillery,
            CardFilter.Air => KitBranch.Air,
            _ => KitBranch.Support,
        };

        private static KitBranch KitOf(GearBranch branch) => branch switch
        {
            GearBranch.Armor => KitBranch.Armor,
            GearBranch.Artillery => KitBranch.Artillery,
            GearBranch.Air => KitBranch.Air,
            _ => KitBranch.Light,
        };

        private void SetFilter(CardFilter filter)
        {
            _filter = filter;
            Refresh();
        }

        private static string SortName(CardSort sort) => Strings.Get("army.sort." + sort.ToString().ToLowerInvariant());

        private void PickSort()
        {
            var options = new List<KitOption>();
            foreach (CardSort s in Enum.GetValues(typeof(CardSort))) options.Add(new KitOption(SortName(s)));
            new KitDropdown(Strings.Get("army.sortTitle"), options, (int)_sort, i => Set(() =>
            {
                _sort = (CardSort)i;
                _sortButton.Value = SortName(_sort);
            })) { name = "sort-picker" }.OpenIn(Root);
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

        private void RefreshArmy()
        {
            if (_armyTabs == null) return;
            _armyTabs.Select((int)_armyView, false);
            _deckView.style.display = _armyView == ArmyView.Deck ? DisplayStyle.Flex : DisplayStyle.None;
            _gearView.style.display = _armyView == ArmyView.Equipment ? DisplayStyle.Flex : DisplayStyle.None;
            _towersView.style.display = _armyView == ArmyView.Towers ? DisplayStyle.Flex : DisplayStyle.None;
            _commandView.style.display = _armyView == ArmyView.Commander ? DisplayStyle.Flex : DisplayStyle.None;
            _hqView.style.display = _armyView == ArmyView.Hq ? DisplayStyle.Flex : DisplayStyle.None;
            var onBase = _tab == Tab.Army && _armyView == ArmyView.Base && _overlays.Count == 0;
            _base.Root.style.display = _armyView == ArmyView.Base ? DisplayStyle.Flex : DisplayStyle.None;
            _outpost.Root.style.display = _armyView == ArmyView.Outpost ? DisplayStyle.Flex : DisplayStyle.None;
            // Leaving the base (another view, tab or page) lets a drag or a pick go (changes are saved as they are made).
            if (!onBase) _base.Leave();
            if (!(_tab == Tab.Army && _armyView == ArmyView.Outpost && _overlays.Count == 0)) _outpost.Leave();
            if (_tab != Tab.Army) return;
            if (_armyView == ArmyView.Deck) RefreshDeck();
            else if (_armyView == ArmyView.Towers) RefreshTowers();
            else if (_armyView == ArmyView.Commander) RefreshCommand();
            else if (_armyView == ArmyView.Hq) RefreshHq();
            else if (_armyView == ArmyView.Equipment) RefreshGear();
            else if (_armyView == ArmyView.Outpost) _outpost.Refresh();
            else _base.Refresh();
        }

        // ------------------------------------------------------------------ E3b: towers and modules

        /// <summary>The base's towers by size, then its utility modules, as cards; a tap opens the structure's detail page.</summary>
        private void RefreshTowers()
        {
            _towersBody.Clear();
            _towersBody.Add(Kit.Body2(Strings.Get("army.towersHint")));
            var structures = Structures();
            foreach (SlotSize size in System.Enum.GetValues(typeof(SlotSize)))
            {
                var towers = structures.Where(id => _catalog.Vehicles[id].Fort is { Kind: not FortKind.Utility } fort && fort.Size == size).ToList();
                if (towers.Count > 0) TowerSection(Strings.Format("army.towerSize", SizeWord(size)), towers);
            }
            var modules = structures.Where(id => _catalog.Vehicles[id].Fort is { Kind: FortKind.Utility }).ToList();
            if (modules.Count > 0) TowerSection(Strings.Get("army.modules"), modules);
        }

        private void TowerSection(string title, List<string> ids)
        {
            _towersBody.Add(Kit.Text(Kit.Caps(title), "fc-caption fc-mt-4 fc-mb-2"));
            var grid = Kit.Box("fc-army__grid");
            foreach (var id in ids) grid.Add(TowerCard(id));
            _towersBody.Add(grid);
        }

        /// <summary>A tower's or module's card: its render, name and rank, its own line icon in the corner (TowerIcons), the upgrade mark when it can rank up.</summary>
        private VisualElement TowerCard(string id)
        {
            var def = _catalog.Vehicles[id];
            var data = VehicleCardData.From(def);
            data.Cp = 0;
            data.Combat = true;
            return new KitVehicleCard(data, () => OpenDetail(id));
        }

        // ------------------------------------------------------------------ E3: the deck

        private void RefreshDeck()
        {
            _deckRow.Clear();
            foreach (var id in MatchSettings.DeckLayout(false)) _deckRow.Add(DeckCard(id, false, compact: true, showLevel: true, combat: true, removable: true));
            _deckRow.Add(Kit.Box("fc-deck-divider"));
            foreach (var id in MatchSettings.DeckLayout(true)) _deckRow.Add(DeckCard(id, true, compact: true, showLevel: true, combat: true, removable: true));

            // The overview band: how many and how dear, the role cover; the commander's row under it.
            _deckOverview.Clear();
            var summary = Kit.Box("fc-army__overview-part");
            summary.Add(Kit.Text(Kit.Caps(Strings.Get("army.overview")), "fc-panel-title fc-mb-2"));
            var costs = MatchSettings.DeckVehicles.Select(CostOf).ToList();
            summary.Add(Kit.Body(Strings.Format("army.summary", ("vehicles", MatchSettings.DeckVehicles.Count), ("vehicleSlots", MatchSettings.DeckVehicleSlots),
                ("supports", MatchSettings.DeckSupports.Count), ("supportSlots", MatchSettings.DeckSupportSlots), ("average", costs.Count > 0 ? costs.Average().ToString("0.0", Strings.Culture) : "-"))));
            // Prompt 15 E7: the five shields, lit where the deck has a weapon that pierces that armour well.
            var deckDefs = MatchSettings.DeckVehicles.Select(v => _catalog.Vehicles.TryGetValue(v, out var d) ? d : null).Where(d => d != null).ToList();
            summary.Add(Kit.Text(Kit.Caps(Strings.Get("combat.armourCover")), "fc-caption fc-mt-3 fc-mb-1"));
            summary.Add(KitCombat.CoverShields(level => KitCombat.Covers(deckDefs, level), "cover.deck"));
            _deckOverview.Add(summary);
            var cover = Kit.Box("fc-army__overview-part fc-grow");
            cover.Add(Kit.Text(Kit.Caps(Strings.Get("army.roles")), "fc-caption fc-mb-2"));
            var roles = Kit.Box("fc-row fc-row--wrap");
            foreach (var (key, icon, has) in DeckRoles.Of(_catalog, MatchSettings.DeckVehicles, MatchSettings.DeckSupports).Rows)
                roles.Add(Tag(has ? icon : "info", Strings.Get(key), has ? "fc-tag--ok" : "fc-tag--missing"));
            cover.Add(roles);
            _deckOverview.Add(cover);

            foreach (var (chip, filter) in _filterChips) chip.Selected = filter == _filter;
            _sortButton.Value = SortName(_sort);
            BuildCollection();
        }

        /// <summary>The collection: owned cards (sorted), then the locked ones with where they unlock.</summary>
        private void BuildCollection()
        {
            _collection.Clear();
            var all = MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(Passes).ToList();
            var owned = all.Where(PlayerProfile.IsUnlocked).ToList();
            owned = _sort switch
            {
                CardSort.Level => owned.OrderByDescending(PlayerProfile.Rank).ThenBy(CostOf).ToList(),
                CardSort.Name => owned.OrderBy(Strings.Card, StringComparer.CurrentCulture).ToList(),
                _ => owned.OrderBy(IsSupport).ThenBy(CostOf).ToList(),
            };
            var grid = Kit.Box("fc-army__grid");
            foreach (var id in owned) grid.Add(CollectionCard(id));
            _collection.Add(grid);
            var locked = all.Where(id => !PlayerProfile.IsUnlocked(id)).ToList();
            if (locked.Count == 0) return;
            _collection.Add(Kit.Caption(Strings.Format("army.locked", locked.Count)));
            var lockedGrid = Kit.Box("fc-army__grid fc-mt-2");
            foreach (var id in locked) lockedGrid.Add(CollectionCard(id));
            _collection.Add(lockedGrid);
        }

        private VisualElement CollectionCard(string id)
        {
            var data = CardData(id);
            data.Combat = true;
            var card = new KitVehicleCard(data, () => CardTapped(id)) { name = "collection-card-" + id };
            card.Chosen = MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id);
            return card;
        }

        /// <summary>A card tapped: its name and what can be done with it (details, into or out of the deck).</summary>
        private void CardTapped(string id)
        {
            var unlocked = PlayerProfile.IsUnlocked(id);
            var inDeck = MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id);
            VisualElement scrim = null;
            var details = new KitButton(ButtonTier.Secondary, Strings.Get("army.info"), () =>
            {
                scrim?.RemoveFromHierarchy();
                OpenDetail(id);
            }, "info");
            var buttons = new List<VisualElement> { details };
            if (unlocked)
                buttons.Add(new KitButton(ButtonTier.Primary, Strings.Get(inDeck ? "army.remove" : "army.use"), () =>
                {
                    scrim?.RemoveFromHierarchy();
                    ToggleInDeck(id);
                }, "deck"));
            scrim = KitDialog.Present(Root, KitDialog.Build(Strings.Card(id), unlocked ? Strings.Get("army.cardHint") : LockReason(id), buttons.ToArray()));
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

        // ------------------------------------------------------------------ E5: equipment

        private void RefreshGear()
        {
            foreach (var (chip, branch) in _branchChips) chip.Selected = branch == _branch;
            _gearSlots.Clear();
            _gearSlots.Add(Kit.Text(GearText.BranchClasses(_branch), "fc-small fc-mb-3"));
            var grid = Kit.Box("fc-army__grid");
            for (var s = 0; s < Gear.Slots; s++)
            {
                var slot = (GearSlot)s;
                var item = PlayerProfile.Equipped(_branch, slot);
                var cell = Kit.Box("fc-army__slot");
                cell.Add(Kit.Caption(GearText.SlotName(slot)));
                VisualElement card;
                if (item != null)
                {
                    var data = GearCardData.From(item);
                    data.Equipped = true;
                    card = new KitGearCard(data, () => PickSlot(slot));
                }
                else
                {
                    card = Kit.Tappable("fc-gcard fc-gcard--empty", () => PickSlot(slot));
                    var art = Kit.Box("fc-gcard__art");
                    var picture = Kit.Box("fc-gcard__picture");
                    if (GearArt.Picture(SlotPictureName(slot)) is { } tex) picture.style.backgroundImage = Background.FromTexture2D(tex);
                    art.Add(picture);
                    card.Add(art);
                    var body = Kit.Box("fc-gcard__body");
                    body.Add(Kit.Text(Strings.Get("gear.empty"), "fc-gcard__stat"));
                    card.Add(body);
                }
                card.EnableInClassList("fc-gcard--chosen", _slotFilter == slot);
                cell.Add(card);
                grid.Add(cell);
            }
            _gearSlots.Add(grid);
            _gearSlots.Add(Kit.Text(Kit.Caps(Strings.Get("gear.setsTitle")), "fc-caption fc-mt-3 fc-mb-2"));
            _gearSlots.Add(SetChips(_branch));
            // Gear targets 04/10 (owner): the bonus the loadout cap cuts off ("+3% fire rate over cap").
            var overCap = Gear.OverCap(PlayerProfile.Loadout(_branch), GearCatalog.StatCap);
            if (overCap.Count > 0)
            {
                _gearSlots.Add(Kit.Text(Kit.Caps(Strings.Get("gear.overCapTitle")), "fc-caption fc-mt-3 fc-mb-2"));
                foreach (var (stat, lost) in overCap) _gearSlots.Add(Kit.Text(GearText.OverCapLine(stat, lost), "fc-small fc-danger-text"));
            }
            _gearSlots.Add(KitButton.Danger(Strings.Get("gear.mergeAll"),
                new KitConfirm(Strings.Get("gear.mergeAllTitle"), Strings.Get("gear.mergeAllBody"), Strings.Get("gear.merge")), () =>
                {
                    var merges = PlayerProfile.MergeAll();
                    Note(merges > 0 ? Strings.Format("gear.merged", merges) : Strings.Get("gear.nothingToMerge"), merges == 0);
                    Refresh();
                }, "upgrade"));
            FillGearList();
            GearInfo();
        }

        private static string SlotPictureName(GearSlot slot) => slot switch
        {
            GearSlot.Special => "reactivearmor",
            GearSlot.Optics => "veterancrew",
            _ => slot.ToString().ToLowerInvariant(),
        };

        private void PickSlot(GearSlot slot)
        {
            _slotFilter = _slotFilter == slot ? null : slot;
            _gearSelected = _slotFilter != null ? PlayerProfile.Equipped(_branch, slot) : null;
            Refresh();
        }

        /// <summary>The pieces that fit the picked slot (or all), sorted, each with its change against the worn one.</summary>
        private void FillGearList()
        {
            _gearList.Clear();
            var head = Kit.Box("fc-row fc-row--spread fc-mb-2");
            head.Add(Kit.Text(Kit.Caps(_slotFilter is { } s ? GearText.SlotName(s) : Strings.Get("gear.inventory")), "fc-panel-title fc-row-text"));
            head.Add(new KitSortButton(GearQuery.SortName(_gearSort), () =>
            {
                var options = new List<KitOption>();
                foreach (GearQuery.Sort sort in Enum.GetValues(typeof(GearQuery.Sort))) options.Add(new KitOption(GearQuery.SortName(sort)));
                new KitDropdown(Strings.Get("army.sortTitle"), options, (int)_gearSort, i => Set(() => _gearSort = (GearQuery.Sort)i)).OpenIn(Root);
            }));
            _gearList.Add(head);
            var items = GearQuery.Sorted(GearQuery.Filter(PlayerProfile.VehicleGearOwned, _slotFilter), _gearSort);
            if (items.Count == 0)
            {
                _gearList.Add(Kit.Body2(Strings.Get(_slotFilter == null ? "gear.none" : "gear.noneForSlot")));
                return;
            }
            var grid = Kit.Box("fc-army__grid");
            foreach (var item in items)
            {
                var g = item;
                var worn = PlayerProfile.Equipped(_branch, item.Slot);
                var data = GearCardData.From(item, worn);
                data.Equipped = PlayerProfile.IsEquipped(item);
                var card = new KitGearCard(data, () =>
                {
                    _gearSelected = g;
                    Refresh();
                }) { Chosen = item == _gearSelected };
                // A piece that does nothing for this branch is dimmed (prompt 8 I.1).
                card.EnableInClassList("fc-gcard--unfit", !Gear.FitsBranch(item, _branch));
                grid.Add(card);
            }
            _gearList.Add(grid);
        }

        /// <summary>
        /// The picked piece: pinned, its card, names and what can be done with it; in the scroll view above the list,
        /// its lines against the worn one.
        /// </summary>
        private void GearInfo()
        {
            _gearInfo.Clear();
            _gearDetails.Clear();
            var item = _gearSelected != null ? PlayerProfile.FindGear(_gearSelected.id) : null;
            if (item == null)
            {
                _gearInfo.Add(Kit.Body2(Strings.Get(_slotFilter == null ? "gear.pick" : "gear.pickFor2")));
                return;
            }
            var head = Kit.Box("fc-row fc-row--top");
            var data = GearCardData.From(item);
            data.Equipped = PlayerProfile.IsEquipped(item);
            head.Add(new KitGearCard(data));
            var names = Kit.Box("fc-row-text fc-grow");
            names.Add(Kit.Text(Kit.Caps(GearText.Name(item)), "fc-panel-title fc-rarity-text-" + item.rarity));
            names.Add(Kit.Small(Strings.Format("gear.detail", ("rarity", Strings.Get("rarity." + item.Rarity.ToString().ToLowerInvariant())), ("level", item.level),
                ("total", Gear.LevelCap[item.rarity]), ("item", StatText(item)))));
            var brand = GearCatalog.Brand(item.brand);
            names.Add(Kit.Small(GearText.SlotName(item.Slot) + (brand != null ? "  ·  " + GearText.BrandName(brand) : "")));
            var partners = PlayerProfile.GearOwned.Count(g => g != item && Gear.CanMerge(g, item));
            names.Add(Kit.Small(item.rarity < (int)Rarity.Legendary ? Strings.Format("gear.mergeHint", partners + 1) : Strings.Get("gear.top")));
            head.Add(names);
            _gearInfo.Add(head);
            var current = PlayerProfile.Equipped(_branch, item.Slot);
            var fits = Gear.FitsBranch(item, _branch);
            if (current != null && current != item)
            {
                _gearDetails.Add(Kit.Text(Kit.Caps(Strings.Get("kit.preview.compare")), "fc-caption"));
                _gearDetails.Add(new KitCompareRow(GearText.SlotName(item.Slot), StatText(current), StatText(item),
                    Math.Sign(Gear.Value(item) - Gear.Value(current))));
            }
            _gearDetails.Add(GearLines(item));
            _gearDetails.Add(Kit.Text(GearText.FitLine(item), fits ? "fc-small" : "fc-small fc-danger-text"));
            // Prompt 29 L5: a module for hardware few cards carry (Trophy, the heat decoys) names the vehicles it works on.
            if (GearText.HardwareLine(item, _branch) is { Length: > 0 } hardware) _gearDetails.Add(Kit.Small(hardware));
            // The buttons under the names, beside the card, so they are always on screen.
            var actions = Kit.Box("fc-row fc-row--wrap fc-mt-2 fc-gap-2");
            var equipped = current == item;
            var equip = new KitButton(ButtonTier.Secondary, Strings.Get(equipped ? "gear.unequip" : "gear.equipShort"), () =>
            {
                if (equipped) PlayerProfile.Unequip(_branch, item.Slot);
                else if (!PlayerProfile.Equip(_branch, item))
                    Note(Strings.Format("gear.notForBranch", Strings.Get("gear.branch." + _branch.ToString().ToLowerInvariant())), true);
                Refresh();
            }, equipped ? "close" : "check");
            if (!equipped && !fits) equip.Disable(Strings.Get("gear.unfitShort"));
            actions.Add(equip);
            var cost = Gear.LevelCost(item);
            if (cost > 0)
            {
                var level = new KitButton(ButtonTier.Secondary, Strings.Get("gear.levelUpShort"), () =>
                {
                    if (!PlayerProfile.TryLevelGear(item)) Note(Strings.Get("arsenal.needCoins"), true);
                    Refresh();
                }, "upgrade");
                if (PlayerProfile.Coins < cost) level.Disable(Strings.Format("kit.sample.coinsShort", Kit.Count(cost - PlayerProfile.Coins)));
                else level.Label = Strings.Format("gear.levelUp", Kit.Count(cost));
                actions.Add(level);
            }
            if (partners >= 2)
                actions.Add(new KitButton(ButtonTier.Secondary, Strings.Get("gear.merge"), () =>
                {
                    if (PlayerProfile.TryMerge(item) is { } merged)
                    {
                        _gearSelected = merged;
                        Note(Strings.Format("gear.mergedInto", GearText.Name(merged)));
                    }
                    Refresh();
                }, "upgrade"));
            names.Add(actions);
        }

        /// <summary>A piece's main effect in a few characters: "+8% dmg", "-5% taken", "Smoke 8 m", or a module's name.</summary>
        private static string StatText(GearItem item) => GearCardData.ShortStat(item);

        /// <summary>A piece's affix lines: main stat, implicit, drawback, sub-stats with their roll bars, the trait and the brand.</summary>
        private static VisualElement GearLines(GearItem item)
        {
            var box = Kit.Box("fc-gear-lines");
            if (item.Slot == GearSlot.Special)
            {
                box.Add(Kit.Body(GearText.ModuleEffect(item)));
                return box;
            }
            foreach (var line in Gear.Lines(item))
            {
                var row = Kit.Box("fc-gear-line");
                var cls = line.Kind switch
                {
                    Gear.LineKind.Main => "fc-body",
                    Gear.LineKind.Penalty => "fc-body fc-danger-text",
                    _ => "fc-body-2",
                };
                row.Add(Kit.Text(GearText.Line(line), cls + " fc-row-text"));
                // The Division's roll bar: where the sub-stat landed between its worst and best roll.
                if (line.Quality >= 0f)
                {
                    var bar = new KitProgress(Mathf.Lerp(0.08f, 1f, line.Quality));
                    bar.AddToClassList("fc-gear-line__roll");
                    row.Add(bar);
                }
                box.Add(row);
            }
            if (Gear.BaseOf(item) is { } baseType && GearText.BaseNote(baseType) is { Length: > 0 } note) box.Add(Kit.Body2(note));
            var trait = GearText.TraitLine(item);
            if (trait.Length > 0) box.Add(Kit.Body(trait));
            else if (item.rarity < (int)Rarity.Epic) box.Add(Kit.Small(Strings.Get("gear.traitAtEpic")));
            var brand = GearCatalog.Brand(item.brand);
            if (brand != null) box.Add(Kit.Small(GearText.BrandName(brand) + "  ·  " + GearText.BrandBonuses(brand)));
            return box;
        }

        /// <summary>The loadout's set chips ("Ironclad 2/4"): a filled chip once the two-piece bonus is on.</summary>
        private static VisualElement SetChips(GearBranch branch)
        {
            var row = Kit.Box("fc-row fc-row--wrap");
            var chips = PlayerProfile.SetChips(branch);
            if (chips.Count == 0)
            {
                row.Add(Kit.Small(Strings.Get("gear.setNone")));
                return row;
            }
            foreach (var chip in chips)
            {
                var tag = Tag(chip.FourPiece ? "star" : chip.TwoPiece ? "check" : null, GearText.Chip(chip), chip.TwoPiece ? "fc-tag--ok" : null);
                tag.tooltip = GearText.BrandBonuses(chip.Brand);
                row.Add(tag);
            }
            return row;
        }

    }
}
