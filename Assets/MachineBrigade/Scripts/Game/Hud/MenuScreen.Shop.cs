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
    /// E9, the shop, in tabs: Deals (the first one free), Crates (with their pictures, what one
    /// holds and the odds a tap away, before anything is bought or opened), Coins (the packs'
    /// pictures), Camouflage, Units (premium cards and early unlocks) and Items. Every tile says
    /// its price, contents and, for crates, its odds; what is bought with the action button
    /// (camouflage, units, items) is picked first, and the page's one main button buys it.
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

        private VisualElement _shopGrid, _shopDock;
        private KitTabs _shopTabs;
        private Label _shopNote;
        private ShopTab _shopTab = ShopTab.Deals;
        private string _shopSelected;

        /// <summary>A skin is being tried on (null: back to the equipped one).</summary>
        public event Action<string> SkinPreviewed;

        private static readonly string[] PremiumCards = { "titan_tank", "heavy_bomber", "stealth_bomber", "ballistic_launcher", "napalm_strike", "gunship_strike" };

        private void BuildShopPage()
        {
            var page = TabPage(Tab.Shop, "fc-page--opaque fc-shop");
            _shopTabs = new KitTabs(new[] { Strings.Get("shop.deals"), Strings.Get("arsenal.crates"), Strings.Get("shop.coins"), Strings.Get("shop.skins"),
                Strings.Get("shop.units"), Strings.Get("shop.items") }, 0, i => OpenShop((ShopTab)i));
            page.Add(_shopTabs);
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            var body = Kit.Box("fc-page__body");
            _shopNote = Kit.Text("", "fc-body-2 fc-mb-3");
            body.Add(_shopNote);
            _shopGrid = Kit.Box("fc-shop__grid");
            body.Add(_shopGrid);
            scroll.Add(body);
            page.Add(scroll);
            _shopDock = Kit.Box("fc-shop__dock");
            page.Add(_shopDock);
        }

        /// <summary>Opens the shop on a section (the coins' plus, "get blueprints").</summary>
        private void OpenShop(ShopTab tab)
        {
            _shopTab = tab;
            _shopSelected = null;
            SkinPreviewed?.Invoke(null);
            if (_tab != Tab.Shop || _overlays.Count > 0) ShowTab(Tab.Shop);
            else Refresh();
        }

        private bool BuysWithAction => _shopTab is ShopTab.Skins or ShopTab.Units or ShopTab.Items;

        private void RefreshShop()
        {
            if (_shopGrid == null || _tab != Tab.Shop) return;
            _shopTabs.Select((int)_shopTab, false);
            _shopNote.text = _shopTab switch
            {
                ShopTab.Items => Strings.Get("shop.itemsNote"),
                ShopTab.Crates => Strings.Get("arsenal.cratesNote") + " " + Strings.Get("arsenal.cratesHint"),
                ShopTab.Deals => Strings.Get("shop.dealsNote"),
                ShopTab.Skins => Strings.Get("shop.skinsNote"),
                _ => "",
            };
            _shopNote.style.display = string.IsNullOrEmpty(_shopNote.text) ? DisplayStyle.None : DisplayStyle.Flex;
            _shopGrid.Clear();
            switch (_shopTab)
            {
                case ShopTab.Deals:
                    _shopGrid.Add(FreeDealTile());
                    _shopGrid.Add(AdCrateTile());
                    _shopGrid.Add(GoldDealTile());
                    break;
                case ShopTab.Crates:
                    foreach (CrateKind kind in Enum.GetValues(typeof(CrateKind))) _shopGrid.Add(CrateTile(kind));
                    break;
                case ShopTab.Coins:
                    var index = 0;
                    foreach (var (id, coins, price) in CoinStore.Packs) _shopGrid.Add(CoinTile(id, coins, price, index++));
                    break;
                case ShopTab.Skins:
                    foreach (var skin in Skins.All) _shopGrid.Add(SkinTile(skin));
                    break;
                case ShopTab.Units:
                    foreach (var id in PremiumCards) _shopGrid.Add(UnitTile(id, premium: true));
                    foreach (var doctrine in Doctrine.All)
                        if (doctrine.Id != "armor") _shopGrid.Add(DoctrineTile(doctrine.Id));
                    foreach (var id in MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports))
                        if (Progression.Route(id) == CardRoute.Campaign) _shopGrid.Add(UnitTile(id, premium: false));
                    break;
                default:
                    foreach (var id in Progression.Items) _shopGrid.Add(ItemTile(id));
                    break;
            }
            FillShopDock();
        }

        /// <summary>A shop tile: a picture, the name, what it holds, and its buttons or its price.</summary>
        private VisualElement ShopTile(string classes, Texture2D picture, string icon, string name, string contents, Action tap = null, bool chosen = false)
        {
            var tile = tap != null ? Kit.Tappable(KitPanel.SurfaceClass + " fc-shop__tile " + classes, tap) : Kit.Box(KitPanel.SurfaceClass + " fc-shop__tile " + classes);
            tile.EnableInClassList("fc-shop__tile--chosen", chosen);
            var art = Kit.Box("fc-shop__art");
            if (picture != null) art.style.backgroundImage = Background.FromTexture2D(picture);
            else if (icon != null) art.Add(Kit.Icon(icon, "fc-shop__art-icon"));
            tile.Add(art);
            var body = Kit.Box("fc-shop__body");
            body.Add(Kit.Text(Kit.Caps(name), "fc-panel-title"));
            if (!string.IsNullOrEmpty(contents)) body.Add(Kit.Small(contents));
            tile.Add(body);
            return tile;
        }

        private static VisualElement PriceLine(int price, string status = null)
        {
            var row = Kit.Box("fc-row fc-shop__price");
            var coin = Kit.Box("fc-currency");
            coin.Add(Kit.Icon("coin"));
            coin.Add(Kit.Text(Kit.Count(price), "fc-currency__value"));
            row.Add(coin);
            if (!string.IsNullOrEmpty(status)) row.Add(Kit.Text(status, "fc-small fc-ml-4"));
            return row;
        }

        private static VisualElement Buttons(VisualElement tile, params VisualElement[] buttons)
        {
            var row = Kit.Box("fc-row fc-row--wrap fc-gap-2 fc-shop__buttons");
            foreach (var b in buttons) row.Add(b);
            tile.Q(className: "fc-shop__body").Add(row);
            return tile;
        }

        // ------------------------------------------------------------------ deals

        private VisualElement FreeDealTile()
        {
            var ready = PlayerProfile.FreeDealReady;
            var tile = ShopTile("", ShopArt.Crate(CrateKind.Battle), "crate", Strings.Get("deal.free"), Strings.Get("crate.battle"));
            var claim = new KitButton(ButtonTier.Claim, Strings.Get("deal.open"), ClaimFreeDeal);
            if (!ready) claim.Disable(Strings.Get("deal.tomorrow"));
            return Buttons(tile, claim);
        }

        private VisualElement AdCrateTile()
        {
            var left = PlayerProfile.AdCratesLeft;
            var wait = PlayerProfile.AdCrateWait;
            var line = left <= 0 ? Strings.Get("crate.adDone")
                : wait > TimeSpan.Zero ? Strings.Format("crate.adWait", ("left", left), ("time", $"{(int)wait.TotalMinutes}:{wait.Seconds:00}"))
                : Strings.Format("crate.adLeft", ("left", left), ("crate", Strings.Get("crate." + DailyCrates.AdCrate(DailyCrates.AdCrates - left).ToString().ToLowerInvariant())));
            var tile = ShopTile("", ShopArt.Crate(CrateKind.Silver), "ad", Strings.Get("crate.ad"), line);
            var watch = new KitButton(ButtonTier.Claim, Strings.Get("crate.watch"), WatchAdCrate, "ad");
            if (left <= 0) watch.Disable(Strings.Get("crate.adDoneShort"));
            else if (wait > TimeSpan.Zero) watch.Disable(Strings.Format("crate.readyIn", $"{(int)wait.TotalMinutes}:{wait.Seconds:00}"));
            return Buttons(tile, watch);
        }

        private VisualElement GoldDealTile()
        {
            var tile = ShopTile("", ShopArt.Crate(CrateKind.Gold), "crate", Strings.Get("deal.gold"),
                PlayerProfile.GoldDealReady
                    ? Strings.Format("deal.goldPrice", ("coins", Kit.Count(PlayerProfile.GoldDealPrice)), ("was", Kit.Count(Crates.CoinPrice[(int)CrateKind.Gold])))
                    : Strings.Get("deal.tomorrow"));
            var buy = new KitButton(ButtonTier.Secondary, Kit.Count(PlayerProfile.GoldDealPrice), BuyGoldDeal, "coin");
            if (!PlayerProfile.GoldDealReady) buy.Disable(Strings.Get("deal.tomorrow"));
            else if (PlayerProfile.Coins < PlayerProfile.GoldDealPrice) buy.Disable(Strings.Format("kit.sample.coinsShort", Kit.Count(PlayerProfile.GoldDealPrice - PlayerProfile.Coins)));
            return Buttons(tile, buy);
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

        // ------------------------------------------------------------------ crates and coins

        private VisualElement CrateTile(CrateKind kind)
        {
            var k = (int)kind;
            var owned = PlayerProfile.CrateCount(kind);
            var contents = Strings.Format("odds.contents", ("coinsMin", Crates.CoinsLow[k]), ("coinsMax", Crates.CoinsHigh[k]), ("prints", Crates.PrintCount[k]), ("cards", Crates.PrintCards[k]), ("rolls", Crates.Rolls[k]));
            var tile = ShopTile("fc-rarity-frame-" + Mathf.Min(4, k + 1), ShopArt.Crate(kind), "crate",
                Strings.Get("crate." + kind.ToString().ToLowerInvariant()), contents);
            var best = Rarity.Legendary;
            while (best > Rarity.Common && Crates.AtLeastOne(kind, best) < 0.001f) best--;
            tile.Q(className: "fc-shop__body").Add(Kit.Small(Strings.Format("shop.bestOdds", ("rarity", Strings.Get("rarity." + best.ToString().ToLowerInvariant())),
                ("percent", (Crates.AtLeastOne(kind, best) * 100f).ToString("0.#", Strings.Culture)))));
            tile.Q(className: "fc-shop__body").Add(Kit.Text(Strings.Format("crate.owned", owned), "fc-body fc-mt-1"));
            var buttons = new List<VisualElement>();
            var open = new KitButton(ButtonTier.Claim, Strings.Get("crate.open"), () => OpenCrate(kind), "crate");
            if (owned <= 0) open.Disable(Strings.Get("crate.noneShort"));
            buttons.Add(open);
            if (Crates.CoinPrice[k] > 0)
            {
                var buy = new KitButton(ButtonTier.Secondary, Kit.Count(Crates.CoinPrice[k]), () => BuyCrate(kind), "coin");
                if (PlayerProfile.Coins < Crates.CoinPrice[k]) buy.Disable(Strings.Format("kit.sample.coinsShort", Kit.Count(Crates.CoinPrice[k] - PlayerProfile.Coins)));
                buttons.Add(buy);
            }
            buttons.Add(new KitButton(ButtonTier.Text, Strings.Get("crate.odds"), () => ShowOdds(kind)));
            return Buttons(tile, buttons.ToArray());
        }

        private VisualElement CoinTile(string id, int coins, string price, int index)
        {
            var pack = id;
            var tile = ShopTile("", ShopArt.CoinPack(index), "coin", Strings.Format("coins.packName", Kit.Count(coins)),
                CoinStore.TestPurchases ? Strings.Format("coins.testPrice", price) : price);
            return Buttons(tile, new KitButton(ButtonTier.Secondary, price, () => CoinStore.Buy(pack, ok =>
            {
                Note(ok ? Strings.Format("coins.bought", Kit.Count(coins)) : Strings.Get("coins.soon"), !ok);
                Refresh();
            })));
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

        /// <summary>The odds: what one crate holds and the chance of every rarity, with the player's pity counters.</summary>
        private void ShowOdds(CrateKind kind)
        {
            var k = (int)kind;
            var body = Kit.Box("");
            body.Add(Kit.Body(Strings.Format("odds.contents", ("coinsMin", Crates.CoinsLow[k]), ("coinsMax", Crates.CoinsHigh[k]), ("prints", Crates.PrintCount[k]), ("cards", Crates.PrintCards[k]), ("rolls", Crates.Rolls[k]))));
            for (var r = 0; r < 5; r++)
            {
                var rarity = (Rarity)r;
                body.Add(Kit.Text(Strings.Format("odds.roll", ("rarity", Strings.Get("rarity." + rarity.ToString().ToLowerInvariant())), ("percent", (Crates.Odds[k][r] * 100f).ToString("0.#", Strings.Culture)),
                    ("atLeastOne", (Crates.AtLeastOne(kind, rarity) * 100f).ToString("0.#", Strings.Culture))), "fc-body fc-mt-2 fc-rarity-text-" + r));
            }
            var tower = Crates.TowerShare[k];
            body.Add(Kit.Body2(Strings.Format("odds.towerShare", ("percent", ((1f - tower) * 100f).ToString("0.#", Strings.Culture)), ("percent2", (tower * 100f).ToString("0.#", Strings.Culture)),
                ("percent3", (Crates.AtLeastOneTower(kind) * 100f).ToString("0.#", Strings.Culture)))));
            if (kind == CrateKind.Gold) body.Add(Kit.Body2(Strings.Get("odds.goldGuaranteed")));
            if (kind == CrateKind.Legendary) body.Add(Kit.Body2(Strings.Get("odds.legendaryGuaranteed")));
            if (Crates.EpicPity[k] > 0)
                body.Add(Kit.Body2(Strings.Format("odds.pityEpic", ("count", Crates.EpicPity[k]), ("yours", Math.Max(1, Crates.EpicPity[k] - PlayerProfile.SinceEpic(kind))))));
            if (Crates.LegendaryPity[k] > 0)
                body.Add(Kit.Body2(Strings.Format("odds.pityLegendary", ("count", Crates.LegendaryPity[k]), ("yours", Math.Max(1, Crates.LegendaryPity[k] - PlayerProfile.SinceLegendary(kind))))));
            body.Add(Kit.Small(Strings.Get("odds.special")));
            body.Add(Kit.Small(Strings.Get("odds.updated")));
            ShowSheet(Strings.Format("odds.title", Strings.Get("crate." + kind.ToString().ToLowerInvariant())), body);
        }

        /// <summary>A scrolling sheet over the screen with a title and one button to close it.</summary>
        private void ShowSheet(string title, VisualElement content)
        {
            VisualElement scrim = null;
            var sheet = Kit.Box(KitPanel.SurfaceClass + " fc-picker fc-sheet", PickingMode.Position);
            sheet.Add(Kit.Text(Kit.Caps(title), "fc-panel-title fc-panel__title"));
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-picker__scroll");
            scroll.Add(content);
            sheet.Add(scroll);
            var row = Kit.Box("fc-dialog__buttons fc-mt-3");
            row.Add(new KitButton(ButtonTier.Secondary, Strings.Get("loot.ok"), () =>
            {
                scrim?.RemoveFromHierarchy();
                Refresh();
            }, "check"));
            sheet.Add(row);
            scrim = KitDialog.Present(Root, sheet);
        }

        /// <summary>What came out of a crate, one line after another (the best last, for the drumroll), equipment as cards.</summary>
        private void ShowLoot(CrateKind kind, Crates.Loot loot)
        {
            var body = Kit.Box("");
            var rows = new List<VisualElement>();
            VisualElement Line(string icon, string text)
            {
                var row = Kit.Box("fc-row fc-mb-2");
                row.Add(Kit.Icon(icon, "fc-rule-icon"));
                row.Add(Kit.Text(text, "fc-body fc-row-text fc-ml-2"));
                body.Add(row);
                rows.Add(row);
                return row;
            }
            Line("coin", Strings.Format("loot.coins", Kit.Count(loot.Coins)));
            foreach (var (card, count) in loot.Blueprints) Line("blueprint", Strings.Format("loot.prints", ("prints", count), ("card", Strings.Card(card))));
            if (loot.Universal > 0) Line("blueprint", Strings.Format("loot.universal", loot.Universal));
            var gear = Kit.Box("fc-row fc-row--wrap fc-row--top fc-mt-2");
            foreach (var item in loot.Gear.OrderBy(g => g.rarity))
            {
                var card = new KitGearCard(GearCardData.From(item));
                gear.Add(card);
                rows.Add(card);
            }
            if (loot.Gear.Count > 0) body.Add(gear);
            // Revealed one by one.
            for (var i = 0; i < rows.Count; i++)
            {
                var row = rows[i];
                row.style.opacity = 0f;
                row.schedule.Execute(() => row.style.opacity = 1f).StartingIn(150 + i * 240);
            }
            ShowSheet(Strings.Get("crate." + kind.ToString().ToLowerInvariant()), body);
        }

        // ------------------------------------------------------------------ camouflage, units, items (bought with the action button)

        private VisualElement SkinTile(Skin skin)
        {
            var tile = ShopTile("", null, null, Strings.Get("skin." + skin.Id), "", () => SelectShop(skin.Id), skin.Id == _shopSelected);
            var art = tile.Q(className: "fc-shop__art");
            art.Add(new KitPaintSample(new[] { skin.Base, skin.Second, skin.Third }, skin.Metallic > 0.6f));
            var owned = PlayerProfile.Owns(skin.Id);
            var equipped = PlayerProfile.EquippedSkin == skin.Id;
            tile.Q(className: "fc-shop__body").Add(PriceLine(skin.Price, equipped ? Strings.Get("shop.equipped") : owned ? Strings.Get("shop.owned") : null));
            return tile;
        }

        private VisualElement UnitTile(string id, bool premium)
        {
            var available = _catalog.Vehicles.ContainsKey(id) || _catalog.TryGetSupport(id, out _);
            var mission = premium ? null : Progression.UnlockMission(id);
            var tile = ShopTile(premium ? "fc-shop__tile--premium" : "", CardArt.For(id), CardIcons.For(id), Strings.Card(id),
                premium ? Strings.Get("shop.premium") : mission != null ? Strings.Format("shop.fromMission", Campaign.Label(mission)) : "",
                () =>
                {
                    if (available) SelectShop(id);
                    else Note(Strings.Format("shop.soon", Strings.Card(id)), true);
                }, id == _shopSelected);
            tile.Q(className: "fc-shop__body").Add(available
                ? PriceLine(Progression.Price(id, _catalog), PlayerProfile.IsUnlocked(id) ? Strings.Get("shop.owned") : null)
                : Kit.Small(Strings.Get("shop.comingSoon")));
            return tile;
        }

        private VisualElement ItemTile(string id)
        {
            // Play-test 5: an item with a picture of its own (the gunship on call) shows it; the others their icon.
            var tile = ShopTile("", CardArt.For(id), CardIcons.For(id), Strings.Support(id), Strings.Get("item." + id + ".info"), () => SelectShop(id), id == _shopSelected);
            tile.Q(className: "fc-shop__body").Add(PriceLine(Progression.ItemPrice(id), Strings.Format("shop.ownedCount", PlayerProfile.ItemCount(id))));
            return tile;
        }

        private VisualElement DoctrineTile(string doctrine)
        {
            var id = "doctrine." + doctrine;
            var tile = ShopTile("", null, DoctrineIcon(doctrine), Strings.Get(id), Strings.Get(id + ".info"), () => SelectShop(id), id == _shopSelected);
            tile.Q(className: "fc-shop__body").Add(PriceLine(Progression.DoctrinePrice, PlayerProfile.Owns(id) ? Strings.Get("shop.owned") : null));
            return tile;
        }

        private static bool IsDoctrine(string id) => id.StartsWith("doctrine.");

        private void SelectShop(string id)
        {
            _shopSelected = id;
            if (_shopTab == ShopTab.Skins) SkinPreviewed?.Invoke(id);
            Refresh();
        }

        private bool IsItemTab => _shopTab == ShopTab.Items;
        private bool IsSkinTab => _shopTab == ShopTab.Skins;

        private bool Owned(string id) => !IsItemTab && (IsSkinTab || IsDoctrine(id) ? PlayerProfile.Owns(id) : PlayerProfile.IsUnlocked(id));

        private int PriceOf(string id) => IsItemTab ? Progression.ItemPrice(id) : IsDoctrine(id) ? Progression.DoctrinePrice
            : IsSkinTab ? Skins.Get(id).Price : Progression.Price(id, _catalog);

        /// <summary>The page's one main button for camouflage, units and items: buy (or use) the picked one.</summary>
        private void FillShopDock()
        {
            _shopDock.Clear();
            _shopDock.style.display = BuysWithAction ? DisplayStyle.Flex : DisplayStyle.None;
            if (!BuysWithAction) return;
            var action = new KitButton(ButtonTier.Primary, Strings.Get("shop.buyShort"), ShopAction, "coin");
            if (_shopSelected == null) action.Disable(Strings.Get("shop.pick"));
            else
            {
                var price = PriceOf(_shopSelected);
                if (Owned(_shopSelected))
                {
                    var equipped = IsSkinTab && PlayerProfile.EquippedSkin == _shopSelected;
                    action.Label = IsSkinTab ? Strings.Get("shop.equip") : Strings.Get("shop.owned");
                    if (!IsSkinTab) action.Disable(Strings.Get("shop.ownedShort"));
                    else if (equipped) action.Disable(Strings.Get("shop.equipped"));
                }
                else if (PlayerProfile.Coins < price) action.Disable(Strings.Format("kit.sample.coinsShort", Kit.Count(price - PlayerProfile.Coins)));
                else action.Label = IsItemTab ? Strings.Format("shop.buyItems", ("count", Progression.ItemPack), ("price", Kit.Count(price))) : Strings.Format("shop.buy", Kit.Count(price));
            }
            _shopDock.Add(action);
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
            }
            else
            {
                Note(Strings.Get("shop.notEnough"), true);
            }
            Refresh();
        }
    }
}
