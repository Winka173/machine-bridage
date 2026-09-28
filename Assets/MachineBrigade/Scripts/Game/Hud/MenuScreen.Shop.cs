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
    /// The Shop tab, sectioned down a rail on the left as mobile shops are (Clash Royale, Brawl
    /// Stars): today's deals (the first one free), crates (their odds one tap away, before anything
    /// is bought or opened), gems, army skins, premium units and early unlocks, and single-use
    /// items. The currency pills' + buttons open the matching section.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum ShopTab
        {
            Deals,
            Crates,
            Coins,
            Skins,
            Units,
            Items,
        }

        private VisualElement _shopGrid, _shopAction, _lootPanel, _lootList;
        private Label _shopNote, _lootTitle;
        private ShopTab _shopTab = ShopTab.Deals;
        private string _shopSelected;
        private readonly List<(VisualElement card, string id)> _shopCards = new();
        private readonly List<(CrateKind kind, Label count, VisualElement open)> _crateCounts = new();
        private Label _adCrateLabel, _freeDealLabel, _goldDealLabel;

        /// <summary>A skin is being tried on (null: back to the equipped one).</summary>
        public event Action<string> SkinPreviewed;

        private static readonly string[] PremiumCards = { "titan_tank", "heavy_bomber", "stealth_bomber", "siege_tank", "ballistic_launcher", "heavy_attack_heli", "napalm_strike" };

        private void BuildShopPage()
        {
            var page = TabPage(Tab.Shop, "shop-page opaque");
            var rail = UiKit.Box("shop-rail");
            foreach (var (tab, icon, key) in new[]
                     {
                         (ShopTab.Deals, "star", "shop.deals"), (ShopTab.Crates, "crate", "arsenal.crates"), (ShopTab.Coins, "coin", "shop.coins"),
                         (ShopTab.Skins, "paint", "shop.skins"), (ShopTab.Units, "tank", "shop.units"), (ShopTab.Items, "bomb", "shop.items"),
                     })
            {
                var t = tab;
                var button = UiKit.Button("rail-button", () => OpenShop(t));
                button.Add(UiKit.Icon(icon, UiKit.Ink, 1.9f));
                button.Add(UiKit.Text(Strings.Get(key), "rail-label"));
                rail.Add(Choice(button, () => _shopTab == t));
            }
            page.Add(rail);
            var main = UiKit.Box("shop-main");
            _shopNote = UiKit.Text("", "menu-note");
            main.Add(_shopNote);
            var scroll = Scroller("shop-scroll");
            _shopGrid = scroll.contentContainer;
            main.Add(scroll);
            var dock = UiKit.Box("shop-dock");
            _shopAction = UiKit.WideButton("wide primary big shop-buy", "coin", "", null, ShopAction);
            dock.Add(_shopAction);
            main.Add(dock);
            page.Add(main);
            BuildLootPanel();
            BuildShopGrid();
        }

        /// <summary>Opens the Shop tab on a section (the currency pills' + buttons, "get blueprints").</summary>
        private void OpenShop(ShopTab tab)
        {
            _shopTab = tab;
            _shopSelected = null;
            SkinPreviewed?.Invoke(null);
            BuildShopGrid();
            if (_tab != Tab.Shop || _overlays.Count > 0) ShowTab(Tab.Shop);
            else Refresh();
        }

        private void BuildShopGrid()
        {
            _shopGrid.Clear();
            _shopCards.Clear();
            _crateCounts.Clear();
            _adCrateLabel = _freeDealLabel = _goldDealLabel = null;
            _shopNote.text = _shopTab switch
            {
                ShopTab.Items => Strings.Get("shop.itemsNote"),
                ShopTab.Crates => Strings.Get("arsenal.cratesNote") + " " + Strings.Get("arsenal.cratesHint"),
                ShopTab.Deals => Strings.Get("shop.dealsNote"),
                _ => "",
            };
            _shopNote.style.display = string.IsNullOrEmpty(_shopNote.text) ? DisplayStyle.None : DisplayStyle.Flex;
            var grid = UiKit.Box("shop-grid");
            switch (_shopTab)
            {
                case ShopTab.Deals:
                    grid.Add(DealCard("free", "crate", Strings.Get("deal.free"), Strings.Get("crate.battle"), out _freeDealLabel, ClaimFreeDeal));
                    grid.Add(DealCard("ad", "ad", Strings.Get("crate.ad"), "", out _adCrateLabel, WatchAdCrate));
                    grid.Add(DealCard("gold", "crate", Strings.Get("deal.gold"), Strings.Get("crate.gold"), out _goldDealLabel, BuyGoldDeal));
                    break;
                case ShopTab.Crates:
                    foreach (CrateKind kind in Enum.GetValues(typeof(CrateKind))) grid.Add(CrateTile(kind));
                    break;
                case ShopTab.Coins:
                    foreach (var (id, coins, price) in CoinStore.Packs) grid.Add(CoinCard(id, coins, price));
                    break;
                case ShopTab.Skins:
                    foreach (var skin in Skins.All) grid.Add(SkinCard(skin));
                    break;
                case ShopTab.Units:
                    foreach (var id in PremiumCards) grid.Add(UnitCard(id, premium: true));
                    foreach (var doctrine in Doctrine.All)
                        if (doctrine.Id != "armor") grid.Add(DoctrineCard(doctrine.Id));
                    foreach (var id in MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports))
                        if (Progression.Route(id) == CardRoute.Campaign) grid.Add(UnitCard(id, premium: false));
                    break;
                default:
                    foreach (var id in Progression.Items) grid.Add(ItemCard(id));
                    break;
            }
            _shopGrid.Add(grid);
        }

        private bool BuysWithAction => _shopTab is ShopTab.Skins or ShopTab.Units or ShopTab.Items;

        // ------------------------------------------------------------------ deals

        private static VisualElement DealCard(string kind, string icon, string title, string sub, out Label status, Action act)
        {
            var card = UiKit.Button("shop-card deal-card " + kind, act);
            var art = UiKit.Box("deal-art");
            art.Add(UiKit.Icon(icon, UiKit.Ink, 1.8f));
            card.Add(art);
            card.Add(UiKit.Text(title, "shop-name"));
            if (!string.IsNullOrEmpty(sub)) card.Add(UiKit.Text(sub, "shop-sub"));
            status = UiKit.Text("", "deal-status");
            card.Add(status);
            return card;
        }

        private void ClaimFreeDeal()
        {
            if (!PlayerProfile.TryClaimFreeDeal())
            {
                Note(Strings.Get("deal.comeBack"), true);
                return;
            }
            OpenCrate(CrateKind.Battle);
        }

        private void BuyGoldDeal()
        {
            if (!PlayerProfile.GoldDealReady)
            {
                Note(Strings.Get("deal.comeBack"), true);
                return;
            }
            if (!PlayerProfile.TryBuyGoldDeal())
            {
                Note(Strings.Get("arsenal.needCoins"), true);
                return;
            }
            OpenCrate(CrateKind.Gold);
        }

        // ------------------------------------------------------------------ crates and gems

        private VisualElement CrateTile(CrateKind kind)
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
            var odds = UiKit.Button("crate-odds", () => ShowOdds(k));
            odds.Add(UiKit.Icon("info", UiKit.Ink, 1.8f));
            top.Add(odds);
            tile.Add(top);
            var buttons = UiKit.Box("crate-buttons");
            var open = CrateButton("primary", "crate", Strings.Get("crate.open"), () => OpenCrate(k));
            buttons.Add(open);
            if (Crates.CoinPrice[(int)kind] > 0)
                buttons.Add(CrateButton("", "coin", Crates.CoinPrice[(int)kind].ToString("N0"), () => BuyCrate(k)));
            tile.Add(buttons);
            _crateCounts.Add((kind, count, open));
            return tile;
        }

        private VisualElement CoinCard(string id, int coins, string price)
        {
            var pack = id;
            var card = UiKit.Button("shop-card coin-card", () => CoinStore.Buy(pack, ok =>
            {
                Note(ok ? Strings.Format("coins.bought", coins.ToString("N0")) : Strings.Get("coins.soon"), !ok);
                Refresh();
            }));
            card.Add(UiKit.Icon("coin", UiKit.Ink, 1.8f));
            card.Add(UiKit.Text(coins.ToString("N0"), "shop-name"));
            card.Add(UiKit.Text(CoinStore.TestPurchases ? price + "  ·  TEST" : price, "shop-sub"));
            return card;
        }

        private static VisualElement CrateButton(string extra, string icon, string text, Action onClick)
        {
            var button = UiKit.Button("crate-button " + extra, onClick);
            button.Add(UiKit.Icon(icon, UiKit.Ink, 1.7f));
            button.Add(UiKit.Text(text, "crate-button-text"));
            return button;
        }

        private void OpenCrate(CrateKind kind)
        {
            var loot = PlayerProfile.OpenCrate(kind);
            if (loot == null)
            {
                Note(Strings.Get("crate.noneLeft"), true);
                return;
            }
            ShowLoot(kind, loot);
            Refresh();
        }

        private void BuyCrate(CrateKind kind)
        {
            if (PlayerProfile.TryBuyCrate(kind)) Note(Strings.Format("crate.bought", Strings.Get("crate." + kind.ToString().ToLowerInvariant())));
            else Note(Strings.Get("arsenal.needCoins"), true);
            Refresh();
        }

        private void WatchAdCrate()
        {
            if (PlayerProfile.AdCratesLeft <= 0 || PlayerProfile.AdCrateWait > TimeSpan.Zero)
            {
                Note(Strings.Get(PlayerProfile.AdCratesLeft <= 0 ? "crate.adDone" : "crate.adCooldown"), true);
                return;
            }
            if (!Ads.Rewarded.Ready)
            {
                Note(Strings.Get("crate.adUnavailable"), true);
                return;
            }
            Ads.Rewarded.Show(watched =>
            {
                if (watched && PlayerProfile.GrantAdCrate() is { } kind) OpenCrate(kind);
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
                    (Crates.AtLeastOne(kind, rarity) * 100f).ToString("0.#")), GearArt.Colors[r]);
            }
            // Which kind of equipment each roll is: vehicle or tower, at the same rarity odds.
            var tower = Crates.TowerShare[k];
            Line(Strings.Format("odds.towerShare", ((1f - tower) * 100f).ToString("0.#"), (tower * 100f).ToString("0.#"),
                (Crates.AtLeastOneTower(kind) * 100f).ToString("0.#")), null);
            if (kind == CrateKind.Gold) Line(Strings.Get("odds.goldGuaranteed"), null);
            if (kind == CrateKind.Legendary) Line(Strings.Get("odds.legendaryGuaranteed"), null);
            if (Crates.EpicPity[k] > 0)
                Line(Strings.Format("odds.pityEpic", Crates.EpicPity[k], Math.Max(1, Crates.EpicPity[k] - PlayerProfile.SinceEpic(kind))), null);
            if (Crates.LegendaryPity[k] > 0)
                Line(Strings.Format("odds.pityLegendary", Crates.LegendaryPity[k], Math.Max(1, Crates.LegendaryPity[k] - PlayerProfile.SinceLegendary(kind))), null);
            Line(Strings.Get("odds.special"), null);
            Line(Strings.Get("odds.updated"), null);
            _lootPanel.style.display = DisplayStyle.Flex;
            _lootPanel.BringToFront();
        }

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
                Refresh();
            }));
            _lootPanel.Add(card);
            _lootPanel.style.display = DisplayStyle.None;
            Root.Add(_lootPanel);
        }

        /// <summary>What came out of a crate, one line after another (the best last, for the drumroll), equipment with its picture.</summary>
        private void ShowLoot(CrateKind kind, Crates.Loot loot)
        {
            _lootList.Clear();
            _lootTitle.text = Strings.Get("crate." + kind.ToString().ToLowerInvariant());
            var gear = UiKit.Box("loot-gear");
            _lootList.Add(gear);
            var rows = new List<VisualElement> { Line(Strings.Format("loot.coins", loot.Coins.ToString("N0")), null, "coin") };
            foreach (var (card, count) in loot.Blueprints) rows.Add(Line(Strings.Format("loot.prints", count, Strings.Card(card)), null, "blueprint"));
            if (loot.Universal > 0) rows.Add(Line(Strings.Format("loot.universal", loot.Universal), null, "blueprint"));
            foreach (var item in loot.Gear.OrderBy(g => g.rarity))
            {
                var cell = UiKit.Box("loot-gear-cell");
                cell.Add(GearArt.Tile(item, 96));
                var name = UiKit.Text(GearName(item), "loot-gear-name");
                name.style.color = GearArt.Colors[item.rarity];
                cell.Add(name);
                cell.Add(UiKit.Text(StatText(item), "loot-gear-stat"));
                gear.Add(cell);
                rows.Add(cell);
            }
            gear.style.display = loot.Gear.Count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            for (var i = 0; i < rows.Count; i++)
            {
                var row = rows[i];
                // Revealed one by one.
                row.style.opacity = 0f;
                row.schedule.Execute(() => row.style.opacity = 1f).StartingIn(150 + i * 240);
            }
            _lootPanel.style.display = DisplayStyle.Flex;
            _lootPanel.BringToFront();
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

        // ------------------------------------------------------------------ skins, units, items (bought with the action button)

        private VisualElement SkinCard(Skin skin)
        {
            var card = UiKit.Button("shop-card skin-card", () => SelectShop(skin.Id));
            var swatch = UiKit.Box("skin-swatch");
            foreach (var colour in new[] { skin.Base, skin.Second, skin.Third, skin.Base })
            {
                var band = UiKit.Box("skin-band");
                band.style.backgroundColor = colour;
                swatch.Add(band);
            }
            if (skin.Metallic > 0.6f) swatch.AddToClassList("metal");
            card.Add(swatch);
            card.Add(UiKit.Text(Strings.Get("skin." + skin.Id), "shop-name"));
            card.Add(PriceTag(skin.Price));
            _shopCards.Add((card, skin.Id));
            return card;
        }

        private VisualElement UnitCard(string id, bool premium)
        {
            var available = _catalog.Vehicles.ContainsKey(id) || _catalog.TryGetSupport(id, out _);
            var card = UiKit.Button("shop-card unit-card", () =>
            {
                if (available) SelectShop(id);
                else Note(Strings.Format("shop.soon", Strings.Card(id)), true);
            });
            card.EnableInClassList("soon", !available);
            var art = UiKit.Box("unit-art" + (premium ? " premium" : ""));
            art.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Card(id), "shop-name"));
            if (!premium)
            {
                var mission = Progression.UnlockMission(id);
                card.Add(UiKit.Text(mission != null ? Strings.Format("shop.fromMission", Campaign.Label(mission)) : "", "shop-sub"));
            }
            card.Add(available ? PriceTag(Progression.Price(id, _catalog)) : UiKit.Text(Strings.Get("shop.comingSoon"), "shop-soon"));
            _shopCards.Add((card, id));
            return card;
        }

        private VisualElement ItemCard(string id)
        {
            var card = UiKit.Button("shop-card unit-card", () =>
            {
                SelectShop(id);
                Note(Strings.Get("item." + id + ".info"));
            });
            var art = UiKit.Box("unit-art premium");
            art.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Support(id), "shop-name"));
            card.Add(UiKit.Text(Strings.Format("shop.ownedCount", PlayerProfile.ItemCount(id)), "shop-sub item-owned"));
            card.Add(PriceTag(Progression.ItemPrice(id)));
            _shopCards.Add((card, id));
            return card;
        }

        private VisualElement DoctrineCard(string doctrine)
        {
            var id = "doctrine." + doctrine;
            var card = UiKit.Button("shop-card unit-card", () =>
            {
                SelectShop(id);
                Note(Strings.Get(id + ".info"));
            });
            var art = UiKit.Box("unit-art premium");
            art.Add(UiKit.Icon(DoctrineIcon(doctrine), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Get(id), "shop-name"));
            card.Add(UiKit.Text(Strings.Get("doctrine.title"), "shop-sub"));
            card.Add(PriceTag(Progression.DoctrinePrice));
            _shopCards.Add((card, id));
            return card;
        }

        private static bool IsDoctrine(string id) => id.StartsWith("doctrine.");

        private static VisualElement PriceTag(int price)
        {
            var tag = UiKit.Box("price-tag");
            tag.Add(UiKit.Icon("coin", UiKit.Ink, 1.8f));
            tag.Add(UiKit.Text(price.ToString("N0"), "price-value"));
            tag.Add(UiKit.Text("", "price-status"));
            return tag;
        }

        private void SelectShop(string id)
        {
            _shopSelected = id;
            if (_shopTab == ShopTab.Skins) SkinPreviewed?.Invoke(id);
            Refresh();
        }

        private bool IsItemTab => _shopTab == ShopTab.Items;
        private bool IsSkinTab => _shopTab == ShopTab.Skins;

        private bool Owned(string id) => IsItemTab ? false : IsSkinTab || IsDoctrine(id) ? PlayerProfile.Owns(id) : PlayerProfile.IsUnlocked(id);

        private int PriceOf(string id) => IsItemTab ? Progression.ItemPrice(id) : IsDoctrine(id) ? Progression.DoctrinePrice
            : IsSkinTab ? Skins.Get(id).Price : Progression.Price(id, _catalog);

        private void RefreshShop()
        {
            foreach (var (kind, count, open) in _crateCounts)
            {
                count.text = Strings.Format("crate.owned", PlayerProfile.CrateCount(kind));
                // Nothing to open: the button greys (a tap still says why).
                open.EnableInClassList("empty", PlayerProfile.CrateCount(kind) <= 0);
            }
            if (_adCrateLabel != null)
            {
                var left = PlayerProfile.AdCratesLeft;
                var wait = PlayerProfile.AdCrateWait;
                _adCrateLabel.text = left <= 0 ? Strings.Get("crate.adDone")
                    : wait > TimeSpan.Zero ? Strings.Format("crate.adWait", left, $"{(int)wait.TotalMinutes}:{wait.Seconds:00}")
                    : Strings.Format("crate.adLeft", left, Strings.Get("crate." + DailyCrates.AdCrate(DailyCrates.AdCrates - left).ToString().ToLowerInvariant()));
            }
            if (_freeDealLabel != null) _freeDealLabel.text = Strings.Get(PlayerProfile.FreeDealReady ? "deal.claim" : "deal.tomorrow");
            if (_goldDealLabel != null)
                _goldDealLabel.text = PlayerProfile.GoldDealReady
                    ? Strings.Format("deal.goldPrice", PlayerProfile.GoldDealPrice.ToString("N0"), Crates.CoinPrice[(int)CrateKind.Gold].ToString("N0"))
                    : Strings.Get("deal.tomorrow");
            foreach (var (card, id) in _shopCards)
            {
                var owned = Owned(id);
                var equipped = IsSkinTab && PlayerProfile.EquippedSkin == id;
                card.EnableInClassList("chosen", id == _shopSelected);
                card.EnableInClassList("owned", owned);
                card.EnableInClassList("equipped", equipped);
                var status = card.Q<Label>(className: "price-status");
                if (status != null) status.text = equipped ? Strings.Get("shop.equipped") : owned ? Strings.Get("shop.owned") : "";
                var count = card.Q<Label>(className: "item-owned");
                if (count != null) count.text = Strings.Format("shop.ownedCount", PlayerProfile.ItemCount(id));
            }
            _shopAction.parent.style.display = BuysWithAction ? DisplayStyle.Flex : DisplayStyle.None;
            if (!BuysWithAction) return;
            var title = _shopAction.Q<Label>(className: "wide-title");
            if (_shopSelected == null)
            {
                title.text = Strings.Get("shop.pick");
                _shopAction.EnableInClassList("disabled", true);
                return;
            }
            var price = PriceOf(_shopSelected);
            var have = Owned(_shopSelected);
            var enough = PlayerProfile.Coins >= price;
            if (have)
            {
                var equipped = IsSkinTab && PlayerProfile.EquippedSkin == _shopSelected;
                title.text = IsSkinTab ? Strings.Get(equipped ? "shop.equipped" : "shop.equip") : Strings.Get("shop.owned");
                _shopAction.EnableInClassList("disabled", !IsSkinTab || equipped);
            }
            else if (IsItemTab)
            {
                title.text = enough ? Strings.Format("shop.buyItems", Progression.ItemPack, price.ToString("N0"))
                    : Strings.Format("shop.short", (price - PlayerProfile.Coins).ToString("N0"));
                _shopAction.EnableInClassList("disabled", !enough);
            }
            else
            {
                title.text = enough ? Strings.Format("shop.buy", price.ToString("N0")) : Strings.Format("shop.short", (price - PlayerProfile.Coins).ToString("N0"));
                _shopAction.EnableInClassList("disabled", !enough);
            }
        }

        private void ShopAction()
        {
            if (_shopSelected == null) return;
            var id = _shopSelected;
            if (IsItemTab)
            {
                Note(PlayerProfile.TryBuyItems(id, Progression.ItemPack, PriceOf(id))
                    ? Strings.Format("shop.bought", Strings.Support(id)) : Strings.Get("shop.notEnough"));
                Refresh();
                return;
            }
            if (Owned(id))
            {
                if (IsSkinTab) PlayerProfile.Equip(id);
            }
            else if (PlayerProfile.TryBuy(id, PriceOf(id)))
            {
                if (IsSkinTab) PlayerProfile.Equip(id);
                Note(Strings.Format("shop.bought", IsSkinTab ? Strings.Get("skin." + id) : IsDoctrine(id) ? Strings.Get(id) : Strings.Card(id)));
                BuildCollection();
            }
            else
            {
                Note(Strings.Get("shop.notEnough"), true);
            }
            Refresh();
        }
    }
}
