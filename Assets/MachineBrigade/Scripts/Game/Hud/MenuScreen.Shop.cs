using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The shop: army skins, premium units and strikes, and early unlocks of campaign cards, all
    /// for coins. Picking a skin previews it on the battle behind the menu.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum ShopTab
        {
            Skins,
            Premium,
            Items,
            Unlocks,
        }

        private VisualElement _shop, _shopGrid, _shopAction;
        private Label _shopNote;
        private ShopTab _tab = ShopTab.Skins;
        private string _shopSelected;
        private readonly List<(VisualElement card, string id)> _shopCards = new();

        /// <summary>A skin is being tried on (null: back to the equipped one).</summary>
        public event Action<string> SkinPreviewed;

        private static readonly string[] PremiumCards = { "titan_tank", "heavy_bomber", "sky_gunship", "stealth_bomber", "napalm_strike", "carpet_bombing" };

        private void BuildShopPage()
        {
            _shop = UiKit.Box("menu-panel wide-panel", PickingMode.Position);
            _shop.Add(Brand());
            var tabs = UiKit.Box("segments shop-tabs");
            foreach (var (tab, icon, key) in new[] { (ShopTab.Skins, "paint", "shop.skins"), (ShopTab.Premium, "star", "shop.premium"),
                         (ShopTab.Items, "bomb", "shop.items"), (ShopTab.Unlocks, "lock", "shop.unlocks") })
                tabs.Add(Choice(Segment(icon, Strings.Get(key), () =>
                {
                    _tab = tab;
                    _shopSelected = null;
                    SkinPreviewed?.Invoke(null);
                    BuildShopGrid();
                    Refresh();
                }, tab == ShopTab.Unlocks), () => _tab == tab));
            var head = UiKit.Box("shop-head");
            head.Add(tabs);
            _shop.Add(head);
            var scroll = Scroller("shop-scroll");
            _shopNote = UiKit.Text("", "menu-note");
            scroll.contentContainer.Add(_shopNote);
            _shopGrid = UiKit.Box("shop-grid");
            scroll.contentContainer.Add(_shopGrid);
            _shop.Add(scroll);
            var dock = UiKit.Box("menu-actions dock-row");
            _shopAction = UiKit.WideButton("wide primary big", "coin", "", null, ShopAction);
            dock.Add(_shopAction);
            dock.Add(UiKit.WideButton("wide back-button", "retreat", Strings.Get("menu.back"), null, () =>
            {
                SkinPreviewed?.Invoke(null);
                _shopSelected = null;
                Show(_main);
            }));
            _shop.Add(dock);
            Root.Add(_shop);
            BuildShopGrid();
        }

        /// <summary>The line above the grid (how items work, what a card is, what was bought); hidden when empty.</summary>
        private void SetShopNote(string text)
        {
            _shopNote.text = text;
            _shopNote.style.display = string.IsNullOrEmpty(text) ? DisplayStyle.None : DisplayStyle.Flex;
        }

        private void BuildShopGrid()
        {
            _shopGrid.Clear();
            _shopCards.Clear();
            // Only the items tab has a note (how items are used); the other tabs drop it.
            SetShopNote(_tab == ShopTab.Items ? Strings.Get("shop.itemsNote") : "");
            switch (_tab)
            {
                case ShopTab.Skins:
                    foreach (var skin in Skins.All) _shopGrid.Add(SkinCard(skin));
                    break;
                case ShopTab.Premium:
                    foreach (var id in PremiumCards) _shopGrid.Add(UnitCard(id, premium: true));
                    foreach (var doctrine in MachineBrigade.Sim.Content.Doctrine.All)
                        if (doctrine.Id != "armor") _shopGrid.Add(DoctrineCard(doctrine.Id));
                    break;
                case ShopTab.Items:
                    foreach (var id in Progression.Items) _shopGrid.Add(ItemCard(id));
                    break;
                default:
                    foreach (var id in MatchSettings.AllVehicles)
                        if (Progression.Route(id) == CardRoute.Campaign) _shopGrid.Add(UnitCard(id, premium: false));
                    foreach (var id in MatchSettings.AllSupports)
                        if (Progression.Route(id) == CardRoute.Campaign) _shopGrid.Add(UnitCard(id, premium: false));
                    break;
            }
        }

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
                else SetShopNote(Strings.Format("shop.soon", Strings.Card(id)));
            });
            card.EnableInClassList("soon", !available);
            var art = UiKit.Box("unit-art" + (premium ? " premium" : ""));
            art.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Card(id), "shop-name"));
            if (!premium)
            {
                var mission = Progression.UnlockMission(id);
                card.Add(UiKit.Text(mission != null ? Strings.Format("shop.fromMission", Campaign.IndexOf(mission.Id) + 1) : "", "shop-sub"));
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
                SetShopNote(Strings.Get("item." + id + ".info"));
            });
            var art = UiKit.Box("unit-art premium");
            art.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Support(id), "shop-name"));
            card.Add(UiKit.Text(Strings.Format("shop.owned", PlayerProfile.ItemCount(id)), "shop-sub item-owned"));
            card.Add(PriceTag(Progression.ItemPrice(id)));
            _shopCards.Add((card, id));
            return card;
        }

        private bool IsItemTab => _tab == ShopTab.Items;

        private VisualElement DoctrineCard(string doctrine)
        {
            var id = "doctrine." + doctrine;
            var card = UiKit.Button("shop-card unit-card", () =>
            {
                SelectShop(id);
                SetShopNote(Strings.Get(id + ".info"));
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
            if (_tab == ShopTab.Skins) SkinPreviewed?.Invoke(id);
            Refresh();
        }

        private bool IsSkinTab => _tab == ShopTab.Skins;

        private bool Owned(string id) => IsItemTab ? false : IsSkinTab || IsDoctrine(id) ? PlayerProfile.Owns(id) : PlayerProfile.IsUnlocked(id);

        private int PriceOf(string id) => IsItemTab ? Progression.ItemPrice(id) : IsDoctrine(id) ? Progression.DoctrinePrice
            : IsSkinTab ? Skins.Get(id).Price : Progression.Price(id, _catalog);

        private void RefreshShop()
        {
            if (_shop == null) return;
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
                if (count != null) count.text = Strings.Format("shop.owned", PlayerProfile.ItemCount(id));
            }
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
                SetShopNote(PlayerProfile.TryBuyItems(id, Progression.ItemPack, PriceOf(id))
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
                SetShopNote(Strings.Format("shop.bought", IsSkinTab ? Strings.Get("skin." + id) : IsDoctrine(id) ? Strings.Get(id) : Strings.Card(id)));
            }
            else
            {
                SetShopNote(Strings.Get("shop.notEnough"));
            }
            Refresh();
        }
    }
}
