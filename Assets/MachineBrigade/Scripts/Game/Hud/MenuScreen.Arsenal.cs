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
    /// The arsenal: card ranks (coins and blueprints), equipment loadouts for each branch of the
    /// army (six slots and a special one, white to gold), and crates (open, buy with coins or
    /// gems, one for watching an ad, the odds and pity counters on show before anything is
    /// bought or opened).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum ArsenalTab
        {
            Cards,
            Gear,
            Crates,
        }

        private VisualElement _arsenal, _arsenalBody, _arsenalDetail, _arsenalAction, _arsenalAction2, _lootPanel, _lootList;
        private Label _arsenalNote;
        private ArsenalTab _arsenalTab = ArsenalTab.Cards;
        private string _rankCard;
        private GearBranch _branch = GearBranch.Armor;
        private GearItem _gearSelected;
        private Action _action, _action2;

        private static readonly Color[] RarityColors =
        {
            new(0.86f, 0.87f, 0.88f), new(0.45f, 0.82f, 0.42f), new(0.35f, 0.62f, 0.98f), new(0.72f, 0.45f, 0.95f), new(0.98f, 0.76f, 0.25f),
        };

        private static readonly string[] SlotIcons = { "cannon", "ammo", "shield", "edges", "move", "repair", "star" };

        private void BuildArsenalPage()
        {
            _arsenal = UiKit.Box("menu-panel wide-panel", PickingMode.Position);
            _arsenal.Add(Brand());
            var head = UiKit.Box("shop-head");
            var tabs = UiKit.Box("segments shop-tabs");
            foreach (var (tab, icon, key) in new[] { (ArsenalTab.Cards, "upgrade", "arsenal.cards"), (ArsenalTab.Gear, "gear", "arsenal.gear"),
                         (ArsenalTab.Crates, "crate", "arsenal.crates") })
                tabs.Add(Choice(Segment(icon, Strings.Get(key), () =>
                {
                    _arsenalTab = tab;
                    BuildArsenal();
                    Refresh();
                }, tab == ArsenalTab.Crates), () => _arsenalTab == tab));
            head.Add(tabs);
            _arsenal.Add(head);
            // The selected card's or piece's details: a fixed pane, so selecting never moves the grid.
            _arsenalDetail = UiKit.Box("card-detail arsenal-detail");
            _arsenal.Add(_arsenalDetail);
            var scroll = Scroller("shop-scroll");
            _arsenalNote = UiKit.Text("", "menu-note");
            scroll.contentContainer.Add(_arsenalNote);
            _arsenalBody = UiKit.Box("arsenal-body");
            scroll.contentContainer.Add(_arsenalBody);
            _arsenal.Add(scroll);
            var dock = UiKit.Box("menu-actions dock-row");
            _arsenalAction = UiKit.WideButton("wide primary big", "upgrade", "", null, () => _action?.Invoke());
            _arsenalAction2 = UiKit.WideButton("wide", "gear", "", null, () => _action2?.Invoke());
            dock.Add(_arsenalAction);
            dock.Add(_arsenalAction2);
            dock.Add(UiKit.WideButton("wide back-button", "retreat", Strings.Get("menu.back"), null, () => Show(_main)));
            _arsenal.Add(dock);
            Root.Add(_arsenal);
            BuildLootPanel();
            BuildArsenal();
        }

        private void BuildArsenal()
        {
            _arsenalBody.Clear();
            switch (_arsenalTab)
            {
                case ArsenalTab.Cards:
                    _arsenalNote.text = Strings.Get("arsenal.cardsNote");
                    _rankCards.Clear();
                    var grid = UiKit.Box("shop-grid");
                    foreach (var id in MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports))
                        if (PlayerProfile.IsUnlocked(id)) grid.Add(RankCard(id));
                    _arsenalBody.Add(grid);
                    break;
                case ArsenalTab.Gear:
                    _arsenalNote.text = Strings.Get("arsenal.gearNote");
                    BuildGearTab();
                    break;
                default:
                    _arsenalNote.text = Strings.Get("arsenal.cratesNote");
                    BuildCratesTab();
                    break;
            }
        }

        // ------------------------------------------------------------------ cards

        private readonly List<(VisualElement card, string id, Label rank, VisualElement fill)> _rankCards = new();

        private VisualElement RankCard(string id)
        {
            var card = UiKit.Button("shop-card unit-card rank-card", () =>
            {
                _rankCard = id;
                Refresh();
            });
            var art = UiKit.Box("unit-art");
            art.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Card(id), "shop-name"));
            var rank = UiKit.Text("", "rank-badge");
            card.Add(rank);
            var track = UiKit.Box("print-track");
            var fill = UiKit.Box("print-fill");
            track.Add(fill);
            card.Add(track);
            _rankCards.Add((card, id, rank, fill));
            return card;
        }

        private void RefreshRankCards()
        {
            foreach (var (card, id, rank, fill) in _rankCards)
            {
                var r = PlayerProfile.Rank(id);
                rank.text = Strings.Format("arsenal.rank", r);
                var need = CardRanks.BlueprintsToNext(r);
                fill.style.width = Length.Percent(need <= 0 ? 100f : Mathf.Clamp01(PlayerProfile.Blueprints(id) / (float)need) * 100f);
                card.EnableInClassList("chosen", id == _rankCard);
                card.EnableInClassList("ready", PlayerProfile.CanRankUp(id));
            }
        }

        private void CardDetail()
        {
            _arsenalDetail.Clear();
            if (_rankCard == null)
            {
                DetailHint("arsenal.pickCard");
                SetActions(null, null, null, null);
                return;
            }
            var rank = PlayerProfile.Rank(_rankCard);
            var head = UiKit.Box("detail-head");
            head.Add(UiKit.Icon(CardIcons.For(_rankCard), UiKit.Ink, 1.7f));
            var names = UiKit.Box("detail-names");
            names.Add(UiKit.Text(Strings.Card(_rankCard) + "  ·  " + Strings.Format("arsenal.rank", rank), "detail-title"));
            var vehicle = _catalog.Vehicles.ContainsKey(_rankCard);
            var now = Mathf.RoundToInt(CardRanks.Bonus(rank) * 100f);
            names.Add(UiKit.Text(Strings.Format(vehicle ? "arsenal.bonusVehicle" : "arsenal.bonusStrike", now), "detail-empty"));
            if (rank < CardRanks.Max)
            {
                var next = Mathf.RoundToInt(CardRanks.Bonus(rank + 1) * 100f);
                names.Add(UiKit.Text(Strings.Format("arsenal.nextRank", rank + 1, next, PlayerProfile.Blueprints(_rankCard),
                    CardRanks.BlueprintsToNext(rank), PlayerProfile.UniversalBlueprints), "detail-counter"));
            }
            head.Add(names);
            _arsenalDetail.Add(head);
            if (rank >= CardRanks.Max)
            {
                SetActions(Strings.Get("arsenal.maxRank"), null, null, null);
                return;
            }
            var id = _rankCard;
            SetActions(Strings.Format("arsenal.rankUp", CardRanks.CoinsToNext(rank).ToString("N0")), () =>
            {
                if (PlayerProfile.TryRankUp(id)) Toast(Strings.Format("arsenal.ranked", Strings.Card(id), PlayerProfile.Rank(id)));
                else Toast(Strings.Get(PlayerProfile.Coins < CardRanks.CoinsToNext(PlayerProfile.Rank(id)) ? "arsenal.needCoins" : "arsenal.needPrints"), true);
                Refresh();
            }, null, null, PlayerProfile.CanRankUp(id));
        }

        // ------------------------------------------------------------------ equipment

        private readonly List<(VisualElement tile, GearSlot slot)> _slotTiles = new();
        private readonly List<(VisualElement tile, GearItem item)> _gearTiles = new();

        private void BuildGearTab()
        {
            _slotTiles.Clear();
            _gearTiles.Clear();
            var branches = UiKit.Box("segments branch-row");
            var all = (GearBranch[])Enum.GetValues(typeof(GearBranch));
            for (var i = 0; i < all.Length; i++)
            {
                var branch = all[i];
                branches.Add(Choice(Segment(BranchIcon(branch), Strings.Get("gear.branch." + branch.ToString().ToLowerInvariant()), () =>
                {
                    _branch = branch;
                    Refresh();
                }, i == all.Length - 1), () => _branch == branch));
            }
            _arsenalBody.Add(branches);
            var slots = UiKit.Box("gear-slots");
            for (var s = 0; s < Gear.Slots; s++)
            {
                var slot = (GearSlot)s;
                var tile = UiKit.Button(slot == GearSlot.Special ? "gear-slot special" : "gear-slot", () =>
                {
                    _gearSelected = PlayerProfile.Equipped(_branch, slot);
                    _slotFilter = slot;
                    Refresh();
                });
                tile.Add(UiKit.Icon(SlotIcons[s], UiKit.Ink, 1.7f));
                tile.Add(UiKit.Text("", "gear-slot-value"));
                slots.Add(tile);
                _slotTiles.Add((tile, slot));
            }
            _arsenalBody.Add(slots);
            var tools = UiKit.Box("gear-tools");
            tools.Add(UiKit.Text(Strings.Get("gear.inventory"), "menu-caps"));
            tools.Add(UiKit.WideButton("wide small-wide", "upgrade", Strings.Get("gear.mergeAll"), null, () =>
            {
                var merges = PlayerProfile.MergeAll();
                Toast(merges > 0 ? Strings.Format("gear.merged", merges) : Strings.Get("gear.nothingToMerge"), merges == 0);
                BuildArsenal();
                Refresh();
            }));
            _arsenalBody.Add(tools);
            var grid = UiKit.Box("gear-grid");
            var items = PlayerProfile.GearOwned.OrderByDescending(g => g.rarity).ThenBy(g => g.slot).ThenByDescending(g => g.level).ToList();
            if (items.Count == 0) _arsenalBody.Add(UiKit.Text(Strings.Get("gear.none"), "menu-note"));
            foreach (var item in items)
            {
                var tile = UiKit.Button("gear-tile", () =>
                {
                    _gearSelected = item;
                    Refresh();
                });
                tile.style.borderTopColor = tile.style.borderBottomColor = tile.style.borderLeftColor = tile.style.borderRightColor = RarityColors[item.rarity];
                tile.Add(UiKit.Icon(SlotIcons[item.slot], RarityColors[item.rarity], 1.7f));
                tile.Add(UiKit.Text(Strings.Format("gear.level", item.level), "gear-tile-level"));
                grid.Add(tile);
                _gearTiles.Add((tile, item));
            }
            _arsenalBody.Add(grid);
        }

        private GearSlot? _slotFilter;

        private void RefreshGear()
        {
            foreach (var (tile, slot) in _slotTiles)
            {
                var item = PlayerProfile.Equipped(_branch, slot);
                var colour = item != null ? RarityColors[item.rarity] : new Color(0.3f, 0.33f, 0.35f);
                tile.style.borderTopColor = tile.style.borderBottomColor = tile.style.borderLeftColor = tile.style.borderRightColor = colour;
                tile.Q<Label>().text = item != null ? StatText(item) : Strings.Get("gear.slot." + slot.ToString().ToLowerInvariant());
                tile.EnableInClassList("chosen", _slotFilter == slot);
            }
            foreach (var (tile, item) in _gearTiles)
            {
                tile.EnableInClassList("chosen", item == _gearSelected);
                tile.EnableInClassList("equipped", PlayerProfile.IsEquipped(item));
                tile.style.display = _slotFilter == null || item.Slot == _slotFilter ? DisplayStyle.Flex : DisplayStyle.None;
            }
        }

        private void GearDetail()
        {
            _arsenalDetail.Clear();
            var item = _gearSelected;
            if (item == null || PlayerProfile.FindGear(item.id) == null)
            {
                _gearSelected = null;
                DetailHint(_slotFilter != null ? "gear.pickFor" : "gear.pick", _slotFilter != null ? Strings.Get("gear.slot." + _slotFilter.Value.ToString().ToLowerInvariant()) : null);
                SetActions(_slotFilter != null ? Strings.Get("gear.showAll") : null, () =>
                {
                    _slotFilter = null;
                    Refresh();
                }, null, null);
                return;
            }
            var head = UiKit.Box("detail-head");
            head.Add(UiKit.Icon(SlotIcons[item.slot], RarityColors[item.rarity], 1.7f));
            var names = UiKit.Box("detail-names");
            var title = UiKit.Text(GearName(item), "detail-title");
            title.style.color = RarityColors[item.rarity];
            names.Add(title);
            names.Add(UiKit.Text(Strings.Format("gear.detail", Strings.Get("rarity." + item.Rarity.ToString().ToLowerInvariant()), item.level,
                Gear.LevelCap[item.rarity], StatText(item)), "detail-empty"));
            var partners = PlayerProfile.GearOwned.Count(g => g != item && Gear.CanMerge(g, item));
            names.Add(UiKit.Text(item.rarity < (int)Rarity.Legendary ? Strings.Format("gear.mergeHint", partners + 1) : Strings.Get("gear.top"), "detail-counter"));
            head.Add(names);
            _arsenalDetail.Add(head);
            var equipped = PlayerProfile.Equipped(_branch, item.Slot) == item;
            var cost = Gear.LevelCost(item);
            SetActions(equipped ? Strings.Get("gear.unequip") : Strings.Format("gear.equip", Strings.Get("gear.branch." + _branch.ToString().ToLowerInvariant())), () =>
            {
                if (equipped) PlayerProfile.Unequip(_branch, item.Slot);
                else PlayerProfile.Equip(_branch, item);
                Refresh();
            }, cost > 0 ? Strings.Format("gear.levelUp", cost.ToString("N0")) : partners >= 2 ? Strings.Get("gear.merge") : null, () =>
            {
                if (cost > 0)
                {
                    if (!PlayerProfile.TryLevelGear(item)) Toast(Strings.Get("arsenal.needCoins"), true);
                }
                else if (PlayerProfile.TryMerge(item) is { } merged)
                {
                    _gearSelected = merged;
                    Toast(Strings.Format("gear.mergedInto", GearName(merged)));
                    BuildArsenal();
                }
                Refresh();
            });
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

        /// <summary>A piece's effect in a few characters: "+8% DMG", "-5% taken", "Smoke 8 m".</summary>
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

        // ------------------------------------------------------------------ crates

        private readonly List<(CrateKind kind, Label count)> _crateCounts = new();
        private Label _adCrateLabel;

        private void BuildCratesTab()
        {
            _crateCounts.Clear();
            var grid = UiKit.Box("crate-grid");
            foreach (CrateKind kind in Enum.GetValues(typeof(CrateKind)))
            {
                var k = kind;
                var tile = UiKit.Box("crate-tile " + kind.ToString().ToLowerInvariant());
                var top = UiKit.Box("crate-top");
                top.Add(UiKit.Icon("crate", UiKit.Ink, 1.8f));
                var texts = UiKit.Box("crate-texts");
                texts.Add(UiKit.Text(Strings.Get("crate." + kind.ToString().ToLowerInvariant()), "crate-name"));
                var count = UiKit.Text("", "crate-count");
                texts.Add(count);
                top.Add(texts);
                tile.Add(top);
                var buttons = UiKit.Box("crate-buttons");
                buttons.Add(CrateButton("primary", "crate", Strings.Get("crate.open"), () => OpenCrate(k)));
                if (Crates.CoinPrice[(int)kind] > 0)
                    buttons.Add(CrateButton("", "coin", Crates.CoinPrice[(int)kind].ToString("N0"), () => BuyCrate(k, false)));
                if (Crates.GemPrice[(int)kind] > 0)
                    buttons.Add(CrateButton("", "gem", Crates.GemPrice[(int)kind].ToString("N0"), () => BuyCrate(k, true)));
                buttons.Add(CrateButton("", "info", Strings.Get("crate.odds"), () => ShowOdds(k)));
                tile.Add(buttons);
                grid.Add(tile);
                _crateCounts.Add((kind, count));
            }
            _arsenalBody.Add(grid);

            // A crate for an ad, three a day.
            var ad = UiKit.Box("crate-tile ad-crate");
            var adTop = UiKit.Box("crate-top");
            adTop.Add(UiKit.Icon("ad", UiKit.Ink, 1.8f));
            var adTexts = UiKit.Box("crate-texts");
            adTexts.Add(UiKit.Text(Strings.Get("crate.ad"), "crate-name"));
            _adCrateLabel = UiKit.Text("", "crate-count");
            adTexts.Add(_adCrateLabel);
            adTop.Add(adTexts);
            ad.Add(adTop);
            var adButtons = UiKit.Box("crate-buttons");
            adButtons.Add(CrateButton("primary", "ad", Strings.Get("crate.watch"), WatchAdCrate));
            ad.Add(adButtons);
            _arsenalBody.Add(ad);

            // Gems (the premium currency): packs for real money once the store is connected.
            _arsenalBody.Add(UiKit.Text(Strings.Get(GemStore.TestPurchases ? "gems.titleTest" : "gems.title"), "menu-caps"));
            var packs = UiKit.Box("gem-grid");
            foreach (var (id, gems, price) in GemStore.Packs)
            {
                var pack = id;
                var tile = UiKit.Button("shop-card gem-card", () => GemStore.Buy(pack, ok =>
                {
                    Toast(ok ? Strings.Format("gems.bought", gems.ToString("N0")) : Strings.Get("gems.soon"), !ok);
                    Refresh();
                }));
                tile.Add(UiKit.Icon("gem", UiKit.Ink, 1.8f));
                tile.Add(UiKit.Text(gems.ToString("N0"), "shop-name"));
                tile.Add(UiKit.Text(price, "shop-sub"));
                packs.Add(tile);
            }
            _arsenalBody.Add(packs);
        }

        private static VisualElement CrateButton(string extra, string icon, string text, Action onClick)
        {
            var button = UiKit.Button("crate-button " + extra, onClick);
            button.Add(UiKit.Icon(icon, UiKit.Ink, 1.7f));
            button.Add(UiKit.Text(text, "crate-button-text"));
            return button;
        }

        private void RefreshCrates()
        {
            foreach (var (kind, count) in _crateCounts)
                count.text = Strings.Format("crate.owned", PlayerProfile.CrateCount(kind));
            if (_adCrateLabel != null)
            {
                var left = PlayerProfile.AdCratesLeft;
                var wait = PlayerProfile.AdCrateWait;
                _adCrateLabel.text = left <= 0 ? Strings.Get("crate.adDone")
                    : wait > TimeSpan.Zero ? Strings.Format("crate.adWait", left, $"{(int)wait.TotalMinutes}:{wait.Seconds:00}")
                    : Strings.Format("crate.adLeft", left, Strings.Get("crate." + DailyCrates.AdCrate(DailyCrates.AdCrates - left).ToString().ToLowerInvariant()));
            }
        }

        private void OpenCrate(CrateKind kind)
        {
            var loot = PlayerProfile.OpenCrate(kind);
            if (loot == null)
            {
                Toast(Strings.Get("crate.noneLeft"), true);
                return;
            }
            ShowLoot(kind, loot);
            Refresh();
        }

        private void BuyCrate(CrateKind kind, bool gems)
        {
            if (PlayerProfile.TryBuyCrate(kind, gems)) Toast(Strings.Format("crate.bought", Strings.Get("crate." + kind.ToString().ToLowerInvariant())));
            else Toast(Strings.Get(gems ? "gems.notEnough" : "arsenal.needCoins"), true);
            Refresh();
        }

        private void WatchAdCrate()
        {
            if (PlayerProfile.AdCratesLeft <= 0 || PlayerProfile.AdCrateWait > TimeSpan.Zero)
            {
                Toast(Strings.Get(PlayerProfile.AdCratesLeft <= 0 ? "crate.adDone" : "crate.adCooldown"), true);
                return;
            }
            if (!Ads.Rewarded.Ready)
            {
                Toast(Strings.Get("crate.adUnavailable"), true);
                return;
            }
            Ads.Rewarded.Show(watched =>
            {
                if (watched && PlayerProfile.GrantAdCrate() is { } kind)
                    Toast(Strings.Format("crate.bought", Strings.Get("crate." + kind.ToString().ToLowerInvariant())));
                Refresh();
            });
        }

        /// <summary>The odds screen: what one crate holds and the chance of every rarity, with the player's pity counters.</summary>
        private void ShowOdds(CrateKind kind)
        {
            var k = (int)kind;
            _lootList.Clear();
            _lootTitle.text = Strings.Format("odds.title", Strings.Get("crate." + kind.ToString().ToLowerInvariant()));
            Line(Strings.Format("odds.contents", Crates.CoinsLow[k], Crates.CoinsHigh[k], Crates.PrintCount[k], Crates.PrintCards[k], Crates.Rolls[k]), null);
            for (var r = 0; r < 5; r++)
            {
                var rarity = (Rarity)r;
                Line(Strings.Format("odds.roll", Strings.Get("rarity." + rarity.ToString().ToLowerInvariant()), (Crates.Odds[k][r] * 100f).ToString("0.#"),
                    (Crates.AtLeastOne(kind, rarity) * 100f).ToString("0.#")), RarityColors[r]);
            }
            if (kind == CrateKind.Gold) Line(Strings.Get("odds.goldGuaranteed"), null);
            if (kind == CrateKind.Legendary) Line(Strings.Get("odds.legendaryGuaranteed"), null);
            if (Crates.EpicPity[k] > 0)
                Line(Strings.Format("odds.pityEpic", Crates.EpicPity[k], Math.Max(1, Crates.EpicPity[k] - PlayerProfile.SinceEpic(kind))), null);
            if (Crates.LegendaryPity[k] > 0)
                Line(Strings.Format("odds.pityLegendary", Crates.LegendaryPity[k], Math.Max(1, Crates.LegendaryPity[k] - PlayerProfile.SinceLegendary(kind))), null);
            Line(Strings.Get("odds.special"), null);
            Line(Strings.Get("odds.updated"), null);
            _lootPanel.style.display = DisplayStyle.Flex;
        }

        // ------------------------------------------------------------------ the loot card

        private Label _lootTitle;

        private void BuildLootPanel()
        {
            _lootPanel = UiKit.Box("overlay loot-overlay", PickingMode.Position);
            var card = UiKit.Box("loot-card", PickingMode.Position);
            _lootTitle = UiKit.Text("", "loot-title");
            card.Add(_lootTitle);
            var scroll = Scroller("loot-scroll");
            _lootList = scroll.contentContainer;
            card.Add(scroll);
            card.Add(UiKit.WideButton("wide primary", "check", Strings.Get("loot.ok"), null, () =>
            {
                _lootPanel.style.display = DisplayStyle.None;
                BuildArsenal();
                Refresh();
            }));
            _lootPanel.Add(card);
            _lootPanel.style.display = DisplayStyle.None;
            Root.Add(_lootPanel);
        }

        /// <summary>What came out of a crate, one line after another (the best last, for the drumroll).</summary>
        private void ShowLoot(CrateKind kind, Crates.Loot loot)
        {
            _lootList.Clear();
            _lootTitle.text = Strings.Format("loot.title", Strings.Get("crate." + kind.ToString().ToLowerInvariant()));
            var lines = new List<(string text, Color? colour, string icon)>
            {
                (Strings.Format("loot.coins", loot.Coins.ToString("N0")), null, "coin"),
            };
            foreach (var (card, count) in loot.Blueprints) lines.Add((Strings.Format("loot.prints", count, Strings.Card(card)), null, "blueprint"));
            if (loot.Universal > 0) lines.Add((Strings.Format("loot.universal", loot.Universal), null, "blueprint"));
            foreach (var item in loot.Gear.OrderBy(g => g.rarity))
                lines.Add((Strings.Get("rarity." + item.Rarity.ToString().ToLowerInvariant()) + "  ·  " + GearName(item) + "  ·  " + StatText(item),
                    RarityColors[item.rarity], SlotIcons[item.slot]));
            for (var i = 0; i < lines.Count; i++)
            {
                var row = Line(lines[i].text, lines[i].colour, lines[i].icon);
                // Revealed one by one.
                row.style.opacity = 0f;
                row.schedule.Execute(() => row.style.opacity = 1f).StartingIn(180 + i * 260);
            }
            _lootPanel.style.display = DisplayStyle.Flex;
        }

        private VisualElement Line(string text, Color? colour, string icon = null)
        {
            var row = UiKit.Box("loot-row");
            if (icon != null) row.Add(UiKit.Icon(icon, colour ?? UiKit.Ink, 1.6f));
            var label = UiKit.Text(text, "loot-text");
            if (colour is { } c) label.style.color = c;
            row.Add(label);
            _lootList.Add(row);
            return row;
        }

        // ------------------------------------------------------------------ shared

        private void RefreshArsenal()
        {
            if (_arsenal == null || _arsenal.style.display == DisplayStyle.None) return;
            switch (_arsenalTab)
            {
                case ArsenalTab.Cards:
                    RefreshRankCards();
                    CardDetail();
                    break;
                case ArsenalTab.Gear:
                    RefreshGear();
                    GearDetail();
                    break;
                default:
                    RefreshCrates();
                    _arsenalDetail.Clear();
                    DetailHint("arsenal.cratesHint");
                    SetActions(null, null, null, null);
                    break;
            }
        }

        private void DetailHint(string key, string arg = null)
        {
            var head = UiKit.Box("detail-head");
            head.Add(UiKit.Icon("info", UiKit.Ink, 1.7f));
            var names = UiKit.Box("detail-names");
            names.Add(UiKit.Text(arg != null ? Strings.Format(key, arg) : Strings.Get(key), "detail-empty"));
            head.Add(names);
            _arsenalDetail.Add(head);
        }

        private void SetActions(string first, Action firstAction, string second, Action secondAction, bool firstReady = true)
        {
            _action = firstAction;
            _action2 = secondAction;
            _arsenalAction.style.display = first != null ? DisplayStyle.Flex : DisplayStyle.None;
            _arsenalAction2.style.display = second != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (first != null) _arsenalAction.Q<Label>(className: "wide-title").text = first;
            if (second != null) _arsenalAction2.Q<Label>(className: "wide-title").text = second;
            _arsenalAction.EnableInClassList("disabled", !firstReady);
        }

        private void Toast(string text, bool warn = false)
        {
            _arsenalNote.text = text;
            _arsenalNote.EnableInClassList("warn", warn);
        }
    }
}
