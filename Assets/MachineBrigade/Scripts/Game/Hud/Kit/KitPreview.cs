using System;
using System.Collections.Generic;
using System.Globalization;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The kit's internal preview: every component in every state, in both languages and both
    /// text sizes, and a sample screen composed only of kit parts. Opened by the debug flag
    /// <c>-mb-ui-kit</c> (<c>-mb-ui-kit=cards</c> for a page, <c>-mb-ui-large</c> for Large text)
    /// or by five quick taps on the rank badge in the menu's top bar. The UI checks
    /// (UiLayoutTests) and the screenshot tool (MachineBrigade.Editor.UiShots) build it directly.
    /// </summary>
    public sealed class KitPreview
    {
        public const string DebugFlag = "-mb-ui-kit";

        public enum Page
        {
            Tokens,
            Buttons,
            Controls,
            Cards,
            Feedback,
            Sample,
        }

        private static readonly (Page page, string icon)[] PageIcons =
        {
            (Page.Tokens, "paint"), (Page.Buttons, "play"), (Page.Controls, "settings"), (Page.Cards, "deck"),
            (Page.Feedback, "info"), (Page.Sample, "home"),
        };

        private readonly Catalog _catalog;
        private readonly Action _close;
        private readonly bool _wasVietnamese;
        private readonly VisualElement _safe;

        public KitPreview(Catalog catalog = null, Action close = null, Page page = Page.Buttons, bool? vietnamese = null, bool? large = null)
        {
            _catalog = catalog ?? GameContent.LoadCatalog();
            _close = close;
            _wasVietnamese = Strings.Vietnamese;
            Vietnamese = vietnamese ?? Strings.Vietnamese;
            Large = large ?? MatchSettings.LargeText;
            Current = page;
            Root = Kit.Root("fc-screen fc-preview");
            Root.pickingMode = PickingMode.Position;
            _safe = Kit.Box("fc-safe");
            Root.Add(_safe);
            _safeTracking = KitSafeArea.Track(_safe);
            Build();
        }

        private readonly IVisualElementScheduledItem _safeTracking;

        /// <summary>Fixed safe-area insets in panel pixels instead of the device's (the screenshot tool's notch and punch hole).</summary>
        public void SetSafeInsets(Vector4 insets)
        {
            _safeTracking?.Pause();
            KitSafeArea.Apply(_safe, insets);
        }

        public VisualElement Root { get; }

        /// <summary>The safe-area frame everything sits in (the screenshot tool insets it for a notch or a punch hole).</summary>
        public VisualElement Safe => _safe;

        public Page Current { get; private set; }
        public bool Vietnamese { get; private set; }
        public bool Large { get; private set; }

        public static Page ParsePage(string name) =>
            Enum.TryParse<Page>(name, true, out var page) ? page : Page.Buttons;

        public void Show(Page page) => Rebuild(page, Vietnamese, Large);

        /// <summary>Builds the preview again in the given page, language and text size.</summary>
        public void Rebuild(Page page, bool vietnamese, bool large)
        {
            Current = page;
            Vietnamese = vietnamese;
            Large = large;
            Build();
        }

        public void Close()
        {
            Strings.Vietnamese = _wasVietnamese;
            Root.RemoveFromHierarchy();
            _close?.Invoke();
        }

        private void Build()
        {
            Strings.Vietnamese = Vietnamese;
            Kit.ApplyTextSize(Root, Large);
            _safe.Clear();
            if (Current == Page.Sample)
            {
                _safe.Add(SampleScreen());
                return;
            }
            var column = Kit.Box("fc-preview__column fc-grow");
            column.Add(TopBar());
            var main = Kit.Box("fc-preview__main");
            main.Add(Rail());
            var scroll = Kit.Scroll(ScrollViewMode.Vertical);
            scroll.AddToClassList("fc-preview__content");
            var body = Kit.Box("fc-preview__page");
            switch (Current)
            {
                case Page.Tokens: TokensPage(body); break;
                case Page.Buttons: ButtonsPage(body); break;
                case Page.Controls: ControlsPage(body); break;
                case Page.Cards: CardsPage(body); break;
                default: FeedbackPage(body); break;
            }
            scroll.Add(body);
            main.Add(scroll);
            column.Add(main);
            _safe.Add(column);
        }

        // ------------------------------------------------------------------ chrome

        private VisualElement TopBar()
        {
            var top = Kit.Box("fc-preview__top", PickingMode.Position);
            top.Add(Kit.Text(Kit.Caps(Strings.Get("kit.preview.title")), "fc-title fc-preview__title"));
            var language = Kit.Box("fc-preview__group");
            language.Add(Kit.Caption(Strings.Get("kit.preview.language")));
            language.Add(new KitChip("EN", !Vietnamese, () => Rebuild(Current, false, Large)));
            language.Add(new KitChip("VI", Vietnamese, () => Rebuild(Current, true, Large)));
            top.Add(language);
            var size = Kit.Box("fc-preview__group");
            size.Add(Kit.Caption(Strings.Get("kit.textSize")));
            size.Add(new KitChip(Strings.Get("kit.textNormal"), !Large, () => Rebuild(Current, Vietnamese, false)));
            size.Add(new KitChip(Strings.Get("kit.textLarge"), Large, () => Rebuild(Current, Vietnamese, true)));
            top.Add(size);
            var close = new KitIconButton("close", Strings.Get("kit.preview.close"), Close);
            close.AddToClassList("fc-ml-4");
            top.Add(close);
            return top;
        }

        private VisualElement Rail()
        {
            var rail = Kit.Box("fc-nav", PickingMode.Position);
            foreach (var (page, icon) in PageIcons)
            {
                var p = page;
                rail.Add(new KitNavItem(icon, Strings.Get("kit.preview.page." + page.ToString().ToLowerInvariant()), page == Current, () => Show(p)));
            }
            return rail;
        }

        private static VisualElement Section(VisualElement page, string titleKey)
        {
            var section = Kit.Box("fc-preview__section");
            section.Add(Kit.Text(Kit.Caps(Strings.Get(titleKey)), "fc-panel-title fc-preview__section-title"));
            page.Add(section);
            return section;
        }

        private static VisualElement Row(VisualElement parent)
        {
            var row = Kit.Box("fc-preview__row");
            parent.Add(row);
            return row;
        }

        /// <summary>A documentation specimen: a caption over one component in one state.</summary>
        private static VisualElement Specimen(VisualElement row, string caption, VisualElement component)
        {
            var box = Kit.Box("fc-preview__specimen " + Kit.SpecimenClass);
            box.Add(Kit.Text(caption, "fc-small fc-preview__specimen-label"));
            box.Add(component);
            row.Add(box);
            return box;
        }

        private static string State(string key) => Strings.Get("kit.state." + key);

        // ------------------------------------------------------------------ pages

        private static readonly string[] ColourTokens =
        {
            "fc-bg", "fc-bg-2", "fc-panel", "fc-panel-raised", "fc-panel-selected", "fc-panel-field", "fc-border", "fc-border-strong",
            "fc-text", "fc-text-2", "fc-text-dim", "fc-accent", "fc-accent-press", "fc-coin", "fc-danger", "fc-danger-text",
            "fc-positive", "fc-ally", "fc-enemy",
            "fc-branch-armor", "fc-branch-light", "fc-branch-artillery", "fc-branch-air", "fc-branch-support",
            "fc-rarity-common", "fc-rarity-uncommon", "fc-rarity-rare", "fc-rarity-epic", "fc-rarity-legendary",
        };

        private static readonly (string cls, string name)[] TypeScale =
        {
            ("fc-title", "fc-fs-title"), ("fc-panel-title", "fc-fs-panel-title"), ("fc-body", "fc-fs-body"),
            ("fc-body-2", "fc-fs-body"), ("fc-dim", "fc-fs-body"), ("fc-small", "fc-fs-small"), ("fc-caption", "fc-fs-small"),
            ("fc-number", "fc-fs-number"), ("fc-number-small", "fc-fs-number-small"),
        };

        private void TokensPage(VisualElement page)
        {
            var colours = Section(page, "kit.preview.colours");
            colours.Add(Kit.Small(Strings.Get("kit.preview.contrast")));
            var grid = Row(colours);
            foreach (var token in ColourTokens)
            {
                var swatch = Kit.Box("fc-swatch");
                var ratio = Kit.Text("", "fc-small");
                swatch.Add(new KitSwatch(token, ratio));
                swatch.Add(Kit.Text(token, "fc-small"));
                swatch.Add(ratio);
                grid.Add(swatch);
            }
            var type = Section(page, "kit.preview.type");
            var sample = Strings.Get("kit.preview.typeSample");
            foreach (var (cls, name) in TypeScale)
            {
                var row = Kit.Box("fc-type-row");
                var size = Kit.Text(name, "fc-small fc-type-row__name");
                row.Add(size);
                var text = Kit.Text(cls is "fc-title" or "fc-panel-title" or "fc-caption" ? Kit.Caps(sample) : sample, cls);
                // The size as drawn, once laid out (the token's value at the current text size).
                text.RegisterCallback<GeometryChangedEvent>(_ =>
                    size.text = name + "  " + text.resolvedStyle.fontSize.ToString("0", CultureInfo.InvariantCulture) + " px");
                row.Add(text);
                type.Add(row);
            }
            var primary = Kit.Box("fc-type-row");
            primary.Add(Kit.Text("fc-fs-primary", "fc-small fc-type-row__name"));
            var face = new KitButton(ButtonTier.Primary, Strings.Get("kit.sample.deploy"), null);
            var holder = Kit.Box(Kit.SpecimenClass);
            holder.Add(face);
            primary.Add(holder);
            type.Add(primary);
        }

        private void ButtonsPage(VisualElement page)
        {
            foreach (ButtonTier tier in Enum.GetValues(typeof(ButtonTier)))
            {
                var section = Section(page, "kit.tier." + KitButton.TierName(tier));
                var row = Row(section);
                var t = tier;
                KitButton Make() => t switch
                {
                    ButtonTier.Primary => new KitButton(t, Strings.Get("kit.sample.deploy"), null, "play"),
                    ButtonTier.Secondary => new KitButton(t, Strings.Get("kit.sample.details"), null, "info"),
                    ButtonTier.Claim => new KitButton(t, Strings.Get("kit.sample.claim"), null),
                    ButtonTier.Text => new KitButton(t, Strings.Get("kit.sample.editDeck"), null),
                    _ => KitButton.Danger(Strings.Get("kit.sample.mergeAll"),
                        new KitConfirm(Strings.Get("kit.sample.mergeTitle"), Strings.Get("kit.sample.mergeBody"), Strings.Get("kit.sample.mergeConfirm")), null),
                };
                Specimen(row, State("normal"), Make());
                Specimen(row, State("pressed"), Make().ShowPressed());
                var reason = tier == ButtonTier.Primary || tier == ButtonTier.Claim
                    ? Strings.Format("kit.sample.coinsShort", Kit.Count(320))
                    : Strings.Format("kit.sample.needsHq", 3);
                Specimen(row, State("disabled"), Make().Disable(reason));
                Specimen(row, State("loading"), Make().SetLoading(true));
            }
            var icons = Section(page, "kit.preview.iconButtons");
            var iconRow = Row(icons);
            Specimen(iconRow, State("normal"), new KitIconButton("settings", Strings.Get("kit.sample.settings"), null));
            Specimen(iconRow, State("pressed"), new KitIconButton("retreat", Strings.Get("kit.sample.back"), null).ShowPressed());
            Specimen(iconRow, State("disabled"), new KitIconButton("info", Strings.Get("kit.sample.info"), null).SetDisabled(true));
            Specimen(iconRow, Strings.Get("kit.buyCoins"), new KitCurrency(12450, null));
        }

        private void ControlsPage(VisualElement page)
        {
            var tabs = Section(page, "kit.preview.tabs");
            tabs.Add(new KitTabs(new[] { Strings.Get("kit.sample.deck"), Strings.Get("kit.sample.gear"), Strings.Get("kit.sample.base") }, 0, null));

            var chips = Section(page, "kit.preview.chips");
            var branchChips = new List<VisualElement>();
            var i = 0;
            foreach (KitBranch b in Enum.GetValues(typeof(KitBranch))) branchChips.Add(KitChip.Branch(b, i++ == 1, null));
            chips.Add(new KitChipRow(branchChips, new KitSortButton(GearQuery.SortName(GearQuery.Sort.Level), null)));
            var rarity = new List<VisualElement>();
            foreach (var key in new[] { "kit.sort.rarity", "kit.sort.slot", "kit.sort.brand" })
                rarity.Add(new KitChip(Strings.Get(key), key == "kit.sort.rarity", null));
            chips.Add(new KitChipRow(rarity, new KitSortButton(GearQuery.SortName(GearQuery.Sort.Rarity), null)));

            var dropdowns = Section(page, "kit.preview.dropdowns");
            var dropRow = Row(dropdowns);
            var modes = new List<KitOption>
            {
                new(Strings.Get("kit.sample.modeConquest"), Strings.Get("kit.sample.modeConquestDetail"), CardArt.For("main_battle_tank")),
                new(Strings.Get("kit.sample.modeSiege"), Strings.Get("kit.sample.modeSiegeDetail"), CardArt.For("siege_tank")),
                new(Strings.Get("kit.sample.modeSurvival"), Strings.Get("kit.sample.modeSurvivalDetail"), CardArt.For("heavy_tank")),
            };
            var mode = new KitDropdown(Strings.Get("kit.sample.mode"), modes, 0, null);
            mode.AddToClassList("fc-preview__w-wide");
            dropRow.Add(mode);
            var difficulty = new KitDropdown(Strings.Get("kit.sample.difficulty"),
                new[] { new KitOption(Strings.Get("kit.sample.easy")), new KitOption(Strings.Get("kit.sample.normal")), new KitOption(Strings.Get("kit.sample.hard")) }, 1, null);
            difficulty.AddToClassList("fc-preview__w-narrow");
            dropRow.Add(difficulty);
            var weather = new KitDropdown(Strings.Get("kit.sample.weather"),
                new[] { new KitOption(Strings.Get("kit.sample.clear")), new KitOption(Strings.Get("kit.sample.rain")), new KitOption(Strings.Get("kit.sample.fog")) }, 2, null);
            weather.AddToClassList("fc-preview__w-narrow");
            dropRow.Add(weather);
            var pressedDrop = new KitDropdown(Strings.Get("kit.sample.map"), new[] { new KitOption(Strings.Get("map.greenvale")) }, 0, null);
            pressedDrop.AddToClassList(KitButton.PressedClass);
            pressedDrop.AddToClassList("fc-preview__w-narrow");
            Specimen(dropRow, State("pressed"), pressedDrop);

            var toggles = Section(page, "kit.preview.toggles");
            var toggleRow = Row(toggles);
            var on = new KitToggle(Strings.Get("kit.sample.autoBuy"), true, null);
            on.AddToClassList("fc-preview__w-toggle");
            toggleRow.Add(on);
            var off = new KitToggle(Strings.Get("kit.sample.support"), false, null);
            off.AddToClassList("fc-preview__w-toggle");
            toggleRow.Add(off);

            var nav = Section(page, "kit.preview.nav");
            var rail = Kit.Box("fc-nav fc-preview__nav-row");
            foreach (var (icon, key, selected, dot) in NavItems)
            {
                var item = new KitNavItem(icon, Strings.Get(key), selected, null);
                item.ShowDot(dot);
                rail.Add(item);
            }
            nav.Add(rail);
        }

        private static readonly (string icon, string key, bool selected, bool dot)[] NavItems =
        {
            ("home", "kit.sample.home", true, false), ("campaign", "kit.sample.campaign", false, false),
            ("swords", "kit.sample.operations", false, true), ("tank", "kit.sample.army", false, false), ("shop", "kit.sample.shop", false, false),
        };

        private VehicleCardData Card(string id, int level = 5)
        {
            if (!_catalog.Vehicles.TryGetValue(id, out var def)) return new VehicleCardData { Id = id, Name = Strings.Card(id) };
            return new VehicleCardData
            {
                Id = id,
                Name = Strings.Card(id),
                Branch = KitBranches.Of(def),
                ClassIcon = KitBranches.ClassIcon(def.Class),
                Cp = def.CpCost,
                Level = level,
                Art = CardArt.For(id),
            };
        }

        private void CardsPage(VisualElement page)
        {
            var vehicles = Section(page, "kit.preview.vehicleCards");
            var states = Row(vehicles);
            Specimen(states, State("normal"), new KitVehicleCard(Card("main_battle_tank"), () => { }));
            var chosen = new KitVehicleCard(Card("attack_helicopter", 7), () => { }) { Chosen = true };
            Specimen(states, State("pressed"), chosen);
            var upgrade = Card("mlrs", 3);
            upgrade.CanUpgrade = true;
            Specimen(states, State("upgrade"), new KitVehicleCard(upgrade, () => { }));
            var locked = Card("heavy_rocket_artillery", 1);
            locked.Locked = true;
            locked.UnlockWhere = Strings.Format("kit.unlockChapter", 3);
            Specimen(states, State("locked"), new KitVehicleCard(locked, () => { }));
            Specimen(states, State("longName"), new KitVehicleCard(Card("ground_cruise_missile_vehicle", 2), () => { }));
            var roster = Row(vehicles);
            foreach (var id in new[] { "scout_jeep", "light_tank", "artillery", "aa_vehicle", "fighter_jet", "engineer_vehicle", "elite_mbt", "gun_turret" })
                roster.Add(new KitVehicleCard(Card(id, 4), () => { }));

            var gear = Section(page, "kit.preview.gearCards");
            var gearRow = Row(gear);
            var rng = new System.Random(20260928);
            GearItem worn = null;
            for (var r = 0; r <= 4; r++)
            {
                var item = Gear.Create((Rarity)r, rng, 900 + r, BranchMask.All);
                item.level = 1 + r * 4;
                worn ??= item;
                var data = GearCardData.From(item, r == 0 ? null : worn);
                data.Equipped = r == 0;
                gearRow.Add(new KitGearCard(data, () => { }));
            }
            gear.Add(new KitChipRow(new VisualElement[]
            {
                new KitChip(Strings.Get("kit.sort.slot"), true, null), new KitChip(Strings.Get("kit.sort.rarity"), false, null),
                new KitChip(Strings.Get("kit.sort.brand"), false, null),
            }, new KitSortButton(GearQuery.SortName(GearQuery.Sort.Rarity), null)));
            var compare = Section(page, "kit.preview.compare");
            compare.AddToClassList("fc-preview__w-compare");
            compare.Add(new KitCompareRow(Strings.Get("kit.preview.statDamage"), "+8%", "+12%", 1));
            compare.Add(new KitCompareRow(Strings.Get("kit.preview.statRange"), "+5%", "+3%", -1));
            compare.Add(new KitCompareRow(Strings.Get("kit.preview.statSpeed"), "+4%", "+4%", 0));
        }

        private void FeedbackPage(VisualElement page)
        {
            var progress = Section(page, "kit.preview.progress");
            progress.AddToClassList("fc-preview__w-compare");
            progress.Add(Kit.Small(Strings.Get("kit.preview.progressLabel")));
            progress.Add(new KitProgress(0.45f));
            var ready = Kit.Small(Strings.Get("kit.preview.progressReady"));
            ready.AddToClassList("fc-mt-4");
            progress.Add(ready);
            progress.Add(new KitProgress(1f, true));
            var dots = Row(progress);
            dots.AddToClassList("fc-mt-4");
            var shop = new KitIconButton("shop", Strings.Get("kit.sample.shop"), null);
            KitDot.Attach(shop, true);
            Specimen(dots, Strings.Get("kit.preview.dotFree"), shop);
            var army = new KitNavItem("tank", Strings.Get("kit.sample.army"), false, null);
            army.ShowDot(true);
            Specimen(dots, Strings.Get("kit.preview.dotUpgrade"), army);

            var surfaces = Section(page, "kit.preview.surfaces");
            var row = Row(surfaces);
            var panel = KitPanel.Create(Strings.Get("kit.preview.panelTitle"), out var body);
            panel.AddToClassList("fc-preview__w-panel");
            body.Add(Kit.Body2(Strings.Get("kit.preview.panelBody")));
            row.Add(panel);
            var dialog = KitDialog.Build(Strings.Get("kit.sample.mergeTitle"), Strings.Get("kit.sample.mergeBody"),
                new KitButton(ButtonTier.Secondary, Strings.Get("kit.cancel"), null),
                KitButton.DangerConfirm(Strings.Get("kit.sample.mergeConfirm"), null));
            row.Add(dialog);
            var toasts = Row(surfaces);
            toasts.Add(KitToast.Build(Strings.Get("kit.preview.toastInfo")));
            toasts.Add(KitToast.Build(Strings.Get("kit.preview.toastReward"), ToastKind.Reward));
            toasts.Add(KitToast.Build(Strings.Get("kit.preview.toastAlert"), ToastKind.Alert));
            var tips = Row(surfaces);
            tips.Add(KitTooltip.Build(Strings.Get("kit.preview.tooltipTitle"), Strings.Get("kit.preview.tooltipBody")));
        }

        // ------------------------------------------------------------------ the sample screen

        /// <summary>
        /// A home screen made only of kit parts, as the rebuild will lay it out: the top bar (rank and
        /// XP, coins with the plus, one settings gear), the left rail, the campaign card (all of it a
        /// button) and the daily challenge on the right, the deck along the bottom left, and the mode
        /// dropdowns with the one main button bottom right.
        /// </summary>
        private VisualElement SampleScreen()
        {
            var screen = Kit.Box("fc-sample fc-grow");
            var top = Kit.Box("fc-sample__top", PickingMode.Position);
            var rank = Kit.Box("fc-sample__rank");
            rank.Add(Kit.Icon("rank"));
            var rankText = Kit.Box("");
            rankText.Add(Kit.Text(Kit.Caps(Strings.Format("kit.sample.rank", 12)), "fc-panel-title"));
            var xp = new KitProgress(0.62f);
            xp.AddToClassList("fc-sample__xp");
            rankText.Add(xp);
            rank.Add(rankText);
            top.Add(rank);
            top.Add(new KitCurrency(12450, null));
            var settings = new KitIconButton("settings", Strings.Get("kit.sample.settings"), null);
            settings.AddToClassList("fc-ml-4");
            top.Add(settings);
            var close = new KitIconButton("close", Strings.Get("kit.preview.close"), () => Show(Page.Tokens));
            close.AddToClassList("fc-ml-2");
            top.Add(close);
            screen.Add(top);

            var body = Kit.Box("fc-sample__body");
            var rail = Kit.Box("fc-nav", PickingMode.Position);
            foreach (var (icon, key, selected, dot) in NavItems)
            {
                var item = new KitNavItem(icon, Strings.Get(key), selected, null);
                item.ShowDot(dot);
                rail.Add(item);
            }
            body.Add(rail);

            var left = Kit.Box("fc-sample__column fc-sample__column--end");
            var deckHead = Kit.Box("fc-preview__row fc-preview__row--center");
            deckHead.Add(Kit.Text(Kit.Caps(Strings.Get("kit.sample.deck")), "fc-panel-title"));
            deckHead.Add(new KitButton(ButtonTier.Text, Strings.Get("kit.sample.editDeck"), null));
            left.Add(deckHead);
            left.Add(Kit.Small(Strings.Get("kit.sample.deckShort")));
            var deck = Kit.Scroll(ScrollViewMode.Horizontal);
            deck.AddToClassList("fc-sample__deck");
            foreach (var id in new[] { "main_battle_tank", "attack_helicopter", "mlrs", "aa_vehicle", "tank_destroyer", "ifv", "artillery", "scout_jeep" })
                deck.Add(new KitVehicleCard(Card(id), () => { }, compact: true));
            left.Add(deck);
            body.Add(left);

            // The right column scrolls when the text is large; the mode and the main button stay at the bottom.
            var side = Kit.Box("fc-sample__side");
            var sideScroll = Kit.Scroll(ScrollViewMode.Vertical);
            sideScroll.AddToClassList("fc-sample__side-scroll");
            var campaign = Kit.Tappable(KitPanel.SurfaceClass + " fc-panel", null);
            campaign.Add(Kit.Caption(Strings.Get("kit.sample.campaign")));
            campaign.Add(Kit.Text(Kit.Caps(Strings.Get("kit.sample.campaignCard")), "fc-panel-title"));
            campaign.Add(Kit.Small(Strings.Get("kit.sample.campaignCardBody")));
            var chapter = new KitProgress(6f / 9f);
            chapter.AddToClassList("fc-mt-2");
            campaign.Add(chapter);
            sideScroll.Add(campaign);
            var daily = KitPanel.Create(null, out var dailyBody);
            daily.AddToClassList("fc-mt-3");
            var dailyHead = Kit.Box("fc-preview__row fc-preview__row--center fc-nowrap");
            dailyHead.Add(Kit.Text(Kit.Caps(Strings.Get("kit.sample.daily")), "fc-panel-title fc-row-text"));
            var claim = new KitButton(ButtonTier.Claim, Strings.Get("kit.sample.claim"), null);
            claim.AddToClassList("fc-keep");
            dailyHead.Add(claim);
            dailyBody.Add(dailyHead);
            dailyBody.Add(Kit.Small(Strings.Get("kit.sample.dailyBody")));
            sideScroll.Add(daily);
            side.Add(sideScroll);
            var launch = Kit.Box("fc-mt-3");
            var modeRow = Kit.Box("fc-preview__row fc-nowrap fc-sample__modes");
            var mode = new KitDropdown(Strings.Get("kit.sample.mode"), new[] { new KitOption(Strings.Get("kit.sample.modeConquest")) }, 0, null);
            mode.AddToClassList("fc-grow");
            modeRow.Add(mode);
            var difficulty = new KitDropdown(Strings.Get("kit.sample.difficulty"), new[] { new KitOption(Strings.Get("kit.sample.normal")) }, 0, null);
            difficulty.AddToClassList("fc-grow");
            modeRow.Add(difficulty);
            launch.Add(modeRow);
            var deploy = new KitButton(ButtonTier.Primary, Strings.Get("kit.sample.deploy"), null, "play");
            deploy.AddToClassList("fc-mt-1");
            launch.Add(deploy);
            side.Add(launch);
            body.Add(side);
            screen.Add(body);
            return screen;
        }
    }
}
