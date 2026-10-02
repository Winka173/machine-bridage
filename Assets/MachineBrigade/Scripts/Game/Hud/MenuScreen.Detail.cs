using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// E4, a card's detail page. On the left the vehicle on its turntable (the card's render until
    /// the turntable is up), its full name and, under it, the tags: armour, branch with its class
    /// icon, cost; who it beats and who beats it. On the right the same five tabs for every card
    /// (Stats, Guide, Weapons, In action, Equipment). Every stat bar carries a mark at its class's
    /// average, and the two gains are told apart and labelled: what the equipment adds, and what
    /// the next level would. Along the bottom the blueprints (have / need, "Enough to level up"),
    /// the deck toggle and the level-up, the page's one main button. Towers and the base's utility
    /// modules have the same page (the owner's request): the model, the numbers, the weapons, the
    /// guide, the rank; a tower's Equipment tab is its branches and its three gear slots, a module's
    /// numbers are what it does for the base.
    /// The In action tab turns the page into a theatre (test feedback 2, DECISIONS 12E): the preview
    /// leaves the left column and fills the space under the tabs; the name with the arrows, the
    /// weapons, the deck toggle and the dock stand in a narrower column beside it. The arrows are
    /// small faces beside the name, off the picture, in both layouts.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum DetailTab
        {
            Stats,
            Guide,
            Weapons,
            Firing,
            Equipment,
        }

        private VisualElement _detail, _detailPreview, _detailArt, _detailTags, _detailCounters, _detailBody, _detailDock, _detailDeck;
        private VisualElement _detailStage, _detailLeft, _detailLeftBody, _detailRight, _detailScroll;
        private bool _detailTheatre;
        private Label _detailName;
        private KitTabs _detailTabs;
        private DetailTab _detailTab = DetailTab.Stats;

        private Label _detailReadout;

        /// <summary>The range's readout, while the In action tab shows one.</summary>
        private void ShowReadout()
        {
            var text = _detailTab == DetailTab.Firing && _detailPreview.style.display != DisplayStyle.None ? Preview?.RangeReadout : null;
            _detailReadout.style.display = string.IsNullOrEmpty(text) ? DisplayStyle.None : DisplayStyle.Flex;
            if (string.IsNullOrEmpty(text)) return;
            _detailReadout.text = text;
            _detailReadout.EnableInClassList("fc-detail__readout--alert", Preview.RangeAlert);
        }
        private string _detailId;
        private List<string> _detailList = new();

        private void BuildDetailPage()
        {
            _detail = FullPage("fc-detail");
            _detailLeft = Kit.Box("fc-detail__left");
            var leftScroll = _detailLeftScroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-detail__left-scroll");
            _detailLeftBody = Kit.Box("fc-detail__left-body");
            leftScroll.Add(_detailLeftBody);
            _detailLeft.Add(leftScroll);
            _detailStage = Kit.Box("fc-detail__stage");
            _detailArt = Kit.Box("fc-detail__art");
            _detailStage.Add(_detailArt);
            _detailPreview = Kit.Box("fc-detail__preview");
            _detailStage.Add(_detailPreview);
            // Test feedback 19P: what a tower on the In action range is doing, as a line over the picture.
            _detailReadout = Kit.Text("", "fc-detail__readout");
            _detailReadout.pickingMode = PickingMode.Ignore;
            _detailReadout.style.display = DisplayStyle.None;
            _detailStage.Add(_detailReadout);
            _detailReadout.schedule.Execute(ShowReadout).Every(200);
            // The texture follows the stage's shape and size (the theatre is much bigger than the turntable's box).
            _detailStage.RegisterCallback<GeometryChangedEvent>(_ => FitPreview());
            _detailLeftBody.Add(_detailStage);
            // The name, and beside it the arrows through the collection: small faces in full touch targets, off the picture.
            var head = Kit.Box("fc-row fc-detail__head");
            _detailName = Kit.Text("", "fc-title fc-row-text fc-grow");
            head.Add(_detailName);
            var previous = new KitIconButton("arrow", Strings.Get("detail.previous"), () => StepDetail(-1), plain: true);
            previous.AddToClassList("fc-detail__previous");
            head.Add(previous);
            head.Add(new KitIconButton("arrow", Strings.Get("detail.next"), () => StepDetail(1), plain: true));
            _detailLeftBody.Add(head);
            _detailTags = Kit.Box("fc-row fc-row--wrap fc-mt-2 fc-detail__tags");
            _detailLeftBody.Add(_detailTags);
            _detailDeck = Kit.Box("fc-mt-3");
            _detailLeftBody.Add(_detailDeck);
            _detailCounters = Kit.Box("fc-mt-3 fc-detail__counters");
            _detailLeftBody.Add(_detailCounters);
            _detail.Add(_detailLeft);

            var right = _detailRight = Kit.Box("fc-detail__right");
            _detailTabs = new KitTabs(new[] { Strings.Get("detail.stats"), Strings.Get("detail.guide"), Strings.Get("detail.weaponsTab"),
                Strings.Get("detail.firing"), Strings.Get("army.equipment") }, 0, i =>
            {
                _detailTab = (DetailTab)i;
                ShowPreview();
                Refresh();
            });
            right.Add(_detailTabs);
            _detailScroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll fc-detail__body-scroll");
            _detailBody = Kit.Box("fc-page__body");
            _detailScroll.Add(_detailBody);
            right.Add(_detailScroll);
            _detailDock = Kit.Box("fc-detail__dock");
            right.Add(_detailDock);
            _detail.Add(right);
        }

        /// <summary>
        /// The In action tab's theatre, or the other tabs' two columns: the stage, the tab's body and
        /// the dock move between the columns (the same elements, so Refresh fills them either way).
        /// </summary>
        private void ArrangeDetail()
        {
            var theatre = _detailTab == DetailTab.Firing;
            if (theatre == _detailTheatre) return;
            _detailTheatre = theatre;
            _detail.EnableInClassList("fc-detail--theatre", theatre);
            if (theatre)
            {
                _detailRight.Insert(_detailRight.IndexOf(_detailScroll), _detailStage);
                _detailLeftBody.Insert(_detailLeftBody.IndexOf(_detailDeck), _detailBody);
                _detailLeft.Add(_detailDock);
            }
            else
            {
                _detailLeftBody.Insert(0, _detailStage);
                _detailScroll.Add(_detailBody);
                _detailRight.Add(_detailDock);
            }
        }

        /// <summary>Sizes the preview's texture to the stage on screen (its shape, about its pixels, within the preview's caps).</summary>
        private void FitPreview()
        {
            if (Preview == null || _detailStage.panel == null) return;
            var box = _detailStage.layout.size;
            var panel = _detailStage.panel.visualTree.layout.size;
            if (box.x < 2f || box.y < 2f || panel.x < 2f || float.IsNaN(box.x)) return;
            var scale = Screen.width / panel.x;
            if (Preview.Fit(box.x * scale, box.y * scale)) _detailPreview.style.backgroundImage = Background.FromRenderTexture(Preview.Texture);
        }

        /// <summary>A slot size as a word inside a sentence ("nhỏ" in Vietnamese; English keeps its capital at the start).</summary>
        private static string SizeWord(SlotSize size)
        {
            var word = Strings.Get("camp.size." + size.ToString().ToLowerInvariant());
            return Strings.Vietnamese ? word.ToLowerInvariant() : word;
        }

        /// <summary>A base structure: a tower, a tower's branch, or a utility module.</summary>
        private bool IsStructure(string id) => id != null && _catalog.Vehicles.TryGetValue(id, out var def) && def.Fort != null;

        /// <summary>The base's structures in the base screen's order: the towers, then the utility modules.</summary>
        private List<string> Structures() =>
            TowerCards.All(_catalog).OrderBy(t => _catalog.Vehicles[t].Fort.Size).ThenBy(t => t, System.StringComparer.Ordinal)
                .Concat(_catalog.Vehicles.Values.Where(d => d.Fort is { Kind: FortKind.Utility } && d.BranchOf == null).Select(d => d.Id).OrderBy(t => t, System.StringComparer.Ordinal))
                .ToList();

        /// <summary>Opens a card's detail page; the arrows step through the collection as it is filtered (a structure: through the base's).</summary>
        private void OpenDetail(string id)
        {
            _detailId = id;
            _detailList = IsStructure(id) ? Structures() : IsBoss(id) ? Bosses() : MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(Passes).ToList();
            if (!_detailList.Contains(id)) _detailList.Add(id);
            Open(_detail, Strings.Get(IsStructure(id) ? "detail.structureTitle" : "detail.title"));
            ShowPreview();
        }

        /// <summary>A boss (its detail page is a Guide page: no deck, level or blueprints).</summary>
        private bool IsBoss(string id) => id != null && _catalog.Vehicles.TryGetValue(id, out var def) && def.Boss;

        /// <summary>Prompt 20 O.3: the bosses in story order (the chapters switched on), then the rest by id: a boss page's arrows.</summary>
        private List<string> Bosses()
        {
            var list = BossHunts.Story.Select(b => b.Id).ToList();
            foreach (var def in _catalog.Vehicles.Values.Where(d => d.Boss && !d.Elite && Strings.Has("unit." + d.Id)).OrderBy(d => d.Id, System.StringComparer.Ordinal))
                if (!list.Contains(def.Id)) list.Add(def.Id);
            return list;
        }

        /// <summary>Prompt 20 O.3: a boss's Guide page (from the dossier, the Boss Hunt's list, a variant's link).</summary>
        private void OpenBossGuide(string id)
        {
            _detailTab = DetailTab.Guide;
            OpenDetail(id);
            Refresh();
        }

        private void StepDetail(int step)
        {
            if (_detailList.Count == 0 || _detailId == null) return;
            var i = (_detailList.IndexOf(_detailId) + step + _detailList.Count) % _detailList.Count;
            _detailId = _detailList[i];
            ShowPreview();
            Refresh();
        }

        private void ShowPreview()
        {
            var vehicle = _detailId != null && _catalog.Vehicles.TryGetValue(_detailId, out var def) ? def : null;
            ArrangeDetail();
            FitPreview();
            _detailArt.style.backgroundImage = _detailId != null && CardArt.For(_detailId) is { } art ? Background.FromTexture2D(art) : new StyleBackground(StyleKeyword.None);
            // A fire support's In action tab: the support called on a range.
            if (vehicle == null && _detailId != null && Preview != null && _detailTab == DetailTab.Firing && _catalog.TryGetSupport(_detailId, out _))
            {
                Preview.ShowRange(_detailId);
                _detailPreview.style.backgroundImage = Background.FromRenderTexture(Preview.Texture);
                _detailPreview.style.display = DisplayStyle.Flex;
                _detailArt.style.display = DisplayStyle.None;
                return;
            }
            if (vehicle != null && Preview != null)
            {
                // The In action tab shows it firing on a range; the others turn it on its stand.
                if (_detailTab == DetailTab.Firing) Preview.ShowRange(vehicle.Id);
                else Preview.Show(Rendering.TowerArt.ModelFor(vehicle, id => Resources.Load<GameObject>("Models/" + id) != null), vehicle.Scale, vehicle);
                _detailPreview.style.backgroundImage = Background.FromRenderTexture(Preview.Texture);
                _detailPreview.style.display = DisplayStyle.Flex;
                _detailArt.style.display = DisplayStyle.None;
            }
            else
            {
                Preview?.Hide();
                _detailPreview.style.display = DisplayStyle.None;
                _detailArt.style.display = DisplayStyle.Flex;
            }
        }

        private void RefreshDetail()
        {
            if (_detailId == null || _detail.style.display == DisplayStyle.None) return;
            var id = _detailId;
            var vehicle = _catalog.Vehicles.TryGetValue(id, out var def) ? def : null;
            var structure = vehicle?.Fort != null;
            var module = vehicle?.Fort is { Kind: FortKind.Utility };
            // Every tower and module stands in the base from the start: nothing to unlock.
            var unlocked = structure || PlayerProfile.IsUnlocked(id);
            var rank = PlayerProfile.Rank(structure ? vehicle.CardId : id);
            // A boss is no card (play-test 6, DECISIONS 21B): its page has no Equipment tab.
            var bossPage = IsBoss(id);
            _detailTabs.Tabs[(int)DetailTab.Equipment].style.display = bossPage ? DisplayStyle.None : DisplayStyle.Flex;
            if (bossPage && _detailTab == DetailTab.Equipment) _detailTab = DetailTab.Guide;
            _detailTabs.Select((int)_detailTab, false);
            ArrangeDetail();

            // Left: the name, the tags under it, the counters.
            _detailName.text = Kit.Caps(Strings.Card(id));
            _detailTags.Clear();
            if (structure)
            {
                _detailTags.Add(Tag(module ? "module" : BaseScreen.SizeIcon(vehicle.Fort.Size), module
                    ? Strings.Get("camp.utility")
                    : Strings.Format("detail.towerSize", SizeWord(vehicle.Fort.Size))));
                _detailTags.Add(ArmourTag(vehicle));
                if (!module && PlayerProfile.TowerBranch(vehicle.CardId) is { } chosen) _detailTags.Add(Tag("upgrade", Strings.Branch(chosen)));
            }
            else if (vehicle != null)
            {
                var branch = KitBranches.Of(vehicle);
                var branchTag = Kit.Box("fc-tag");
                branchTag.Add(Kit.Box("fc-chip__swatch " + KitBranches.ColourClass(branch)));
                branchTag.Add(Kit.Icon(KitBranches.ClassIcon(vehicle.Class)));
                branchTag.Add(Kit.Text(KitBranches.Name(branch) + " · " + Strings.Get("class." + vehicle.Class), "fc-small"));
                _detailTags.Add(branchTag);
                _detailTags.Add(ArmourTag(vehicle));
            }
            else _detailTags.Add(Tag(CardIcons.For(id), Strings.Get("detail.strikeTag")));
            var boss = vehicle is { Boss: true };
            if (!structure && !boss) _detailTags.Add(Tag("cp", Strings.Format("detail.cpTag", CostOf(id))));
            if (boss) _detailTags.Add(Tag(vehicle.MiniBoss ? "elite" : "skull", Strings.Get(vehicle.RankDef?.Label ?? (vehicle.MiniBoss ? "boss.rank.mini" : "boss.rank.main"))));
            else _detailTags.Add(Tag("upgrade", Strings.Format("kit.level", rank)));
            _detailCounters.Clear();
            if (vehicle != null) CombatBlock(vehicle, module);

            // Right: the chosen tab.
            _detailBody.Clear();
            switch (_detailTab)
            {
                case DetailTab.Stats:
                    if (bossPage) BossStats(vehicle);
                    else if (vehicle != null) VehicleStats(vehicle, rank);
                    else StrikeStats(id, rank);
                    if (module) ModuleFacts(vehicle);
                    break;
                case DetailTab.Guide:
                    Guide(id);
                    break;
                case DetailTab.Weapons:
                    if (module) _detailBody.Add(Kit.Body2(Strings.Get("detail.moduleNoWeapons")));
                    else if (vehicle != null) VehicleWeapons(vehicle, true);
                    else _detailBody.Add(Kit.Body(Strings.Get("support." + id + ".info")));
                    break;
                case DetailTab.Firing:
                    _detailBody.Add(Kit.Body2(Strings.Get(module ? "detail.moduleNoFiring" : vehicle != null ? "detail.firingNote" : "detail.firingStrike")));
                    if (vehicle != null && !module) VehicleWeapons(vehicle);
                    break;
                default:
                    if (structure) StructureEquipment(vehicle, module);
                    else if (vehicle != null) DetailEquipment(vehicle);
                    else _detailBody.Add(Kit.Body2(Strings.Get("detail.strikeNoGear")));
                    break;
            }
            FillDetailDock(id, unlocked, rank);
        }

        /// <summary>The bottom: blueprints have / need, the deck toggle, the level-up (the one main button).</summary>
        private void FillDetailDock(string id, bool unlocked, int rank)
        {
            _detailDock.Clear();
            // A boss is no card: nothing to level up or put in the deck.
            if (IsBoss(id))
            {
                _detailDeck.Clear();
                return;
            }
            var prints = Kit.Box("fc-detail__prints");
            var need = CardRanks.BlueprintsToNext(rank);
            var have = PlayerProfile.Blueprints(id) + PlayerProfile.UniversalBlueprints;
            var enough = need > 0 && have >= need;
            var head = Kit.Box("fc-row fc-row--wrap");
            head.Add(Kit.Icon("blueprint", "fc-rule-icon"));
            head.Add(Kit.Text(need <= 0 ? Strings.Get("arsenal.maxRank") : Strings.Format("detail.prints", ("have", have), ("need", need)), "fc-body fc-row-text fc-ml-2"));
            if (enough) head.Add(Kit.Text(Strings.Get("detail.enoughPrints"), "fc-small fc-positive-text fc-ml-2"));
            prints.Add(head);
            prints.Add(new KitProgress(need <= 0 ? 1f : Mathf.Clamp01((float)have / need), enough));
            if (unlocked && rank < CardRanks.Max)
                prints.Add(Kit.Small(Strings.Format("detail.nextLevel", ("level", rank + 1), ("coins", Kit.Count(CardRanks.CoinsToNext(rank))))));
            _detailDock.Add(prints);

            _detailDeck.Clear();
            var inDeck = MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id);
            // A structure goes in the base, not the deck: the button opens the base screen with it picked.
            if (IsStructure(id)) _detailDeck.Add(new KitButton(ButtonTier.Secondary, Strings.Get("detail.toBase"), () => OpenInBase(id), "hq"));
            else if (unlocked)
                _detailDeck.Add(new KitButton(ButtonTier.Secondary, Strings.Get(inDeck ? "army.remove" : "detail.addToDeck"), () => ToggleInDeck(id), "deck"));
            var upgrade = new KitButton(ButtonTier.Primary, Strings.Get("detail.levelUp"), UpgradeDetail, "upgrade");
            if (!unlocked) upgrade.Disable(LockReasonShort(id));
            else if (rank >= CardRanks.Max) upgrade.Disable(Strings.Get("arsenal.maxRank"));
            else if (!enough) upgrade.Disable(Strings.Format("detail.printsShort", need - have));
            else if (PlayerProfile.Coins < CardRanks.CoinsToNext(rank))
                upgrade.Disable(Strings.Format("kit.sample.coinsShort", Kit.Count(CardRanks.CoinsToNext(rank) - PlayerProfile.Coins)));
            _detailDock.Add(upgrade);
        }

        /// <summary>
        /// The Guide tab: the unit's role, how it fights, what it beats and fears, and a tip, one
        /// block each, key words in bold; the real vehicle it is based on underneath.
        /// </summary>
        private void Guide(string id)
        {
            // Prompt 15 E8: the legend of the armour and weapon icons, from every guide.
            _detailBody.Add(new KitButton(ButtonTier.Text, Strings.Get("combat.legend.open"), OpenLegend, "info"));
            // Prompt 20 O.5: the battlefields' guide (the dossier's tab).
            _detailBody.Add(new KitButton(ButtonTier.Text, Strings.Get("guide.maps.open"), OpenBattlefields, "globe"));
            if (_catalog.Vehicles.TryGetValue(id, out var bossDef) && bossDef.Boss)
            {
                BossFacts(bossDef);
                BossFile.Escorts(_detailBody, _catalog, bossDef);
            }
            if (Strings.Has("note." + id))
            {
                _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("detail.notes")), "fc-caption fc-mb-2"));
                _detailBody.Add(Kit.Body(Strings.Get("note." + id)));
            }
            if (Strings.Has("guide." + id)) GuideLines(Strings.Get("guide." + id));
            // Prompt 13 G.2: how it behaves, worked out from its data.
            if (_catalog.Vehicles.TryGetValue(id, out var unit))
            {
                var behaviour = UnitLines.Behaviour(_catalog, unit);
                if (behaviour.Count > 0)
                {
                    _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("detail.behaviour")), "fc-caption fc-mt-4 fc-mb-2"));
                    foreach (var line in behaviour) _detailBody.Add(Kit.Body("· " + line));
                }
                if (unit.Flying || unit.Weapon.Ammo > 0 && !unit.Static) AmmoIconTable();
            }
            // The tower-branch rework (D.3): each rank-7 branch's page: its role, when to pick it, what sets it apart, its behaviour.
            var towerBranches = TowerCards.Branches(_catalog, id);
            if (towerBranches.Count > 0)
            {
                _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("detail.branches")), "fc-caption fc-mt-4 fc-mb-2"));
                for (var i = 0; i < towerBranches.Count; i++)
                {
                    var b = _catalog.Vehicles[towerBranches[i]];
                    var other = _catalog.Vehicles[towerBranches[(i + 1) % towerBranches.Count]];
                    _detailBody.Add(Kit.Text(Kit.Caps(Strings.Branch(b.Id)), "fc-panel-title fc-mt-2"));
                    _detailBody.Add(Kit.Body(Strings.Get("branch." + b.Id + ".info")));
                    if (BranchLines.When(b.Id) is { Length: > 0 } when) _detailBody.Add(Kit.Body(when));
                    foreach (var fact in BranchLines.Differences(b, other)) _detailBody.Add(Kit.Body("· " + fact));
                    foreach (var line in UnitLines.Behaviour(_catalog, b)) _detailBody.Add(Kit.Body2("· " + line));
                }
            }
            // The enemy's elite versions of this card (prompt 8 H.6): each with its own entry and skills.
            foreach (var elite in _catalog.Vehicles.Values)
            {
                if (!elite.Elite || elite.EliteOf != id || !Strings.Has("guide." + elite.Id)) continue;
                _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("detail.eliteVersion")), "fc-caption fc-mt-4"));
                GuideLines(Strings.Get("guide." + elite.Id));
            }
            // A boss's parts and what breaking each does (prompt 9), its altitude tiers and its big attack.
            if (_catalog.Vehicles.TryGetValue(id, out var boss) && boss.Boss)
            {
                BossPartsGuide(boss);
                TiersGuide(boss);
                BigAttackGuide(boss);
            }
        }

        /// <summary>
        /// Prompt 20 O.3: a boss's Guide header: its rank, the chapters it is fought in, its general (portrait, name, call
        /// sign and naming theme), the main boss it is a variant of and its own variants, each a link to that boss's page.
        /// </summary>
        private void BossFacts(VehicleDef boss)
        {
            var box = Kit.Box(KitPanel.SurfaceClass + " fc-boss-facts fc-mt-2");
            BossFile.Head(box, boss);
            if (boss.VariantOf is { } parent && _catalog.Vehicles.ContainsKey(parent))
                box.Add(new KitButton(ButtonTier.Text, Strings.Format("guide.boss.variantOf", Strings.Unit(parent)), () => OpenBossGuide(parent), "arrow"));
            var variants = _catalog.Vehicles.Values.Where(v => v.VariantOf == boss.Id).OrderBy(v => v.Id, System.StringComparer.Ordinal).ToList();
            if (variants.Count > 0)
            {
                box.Add(Kit.Text(Kit.Caps(Strings.Get("guide.boss.variants")), "fc-caption fc-mt-2"));
                foreach (var v in variants)
                {
                    var vid = v.Id;
                    box.Add(new KitButton(ButtonTier.Text, Strings.Unit(vid), () => OpenBossGuide(vid), "arrow"));
                }
            }
            _detailBody.Add(box);
        }

        /// <summary>Prompt 13 C.9: what the ammunition icons over units mean, with their colours.</summary>
        private void AmmoIconTable()
        {
            _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("detail.ammoIcons")), "fc-caption fc-mt-4 fc-mb-2"));
            foreach (var (key, colour) in new[]
                     {
                         ("icons.low", new Color(1f, 0.8f, 0.22f)), ("icons.empty", new Color(1f, 0.26f, 0.18f)),
                         ("icons.leaving", new Color(0.62f, 0.66f, 0.7f)), ("icons.rearming", new Color(0.36f, 0.9f, 0.5f)),
                         ("icons.full", new Color(0.6f, 1f, 0.7f)),
                     })
            {
                var row = Kit.Box("fc-row fc-mt-2");
                var swatch = new VisualElement();
                swatch.style.width = 12f;
                swatch.style.height = 12f;
                swatch.style.flexShrink = 0f;
                swatch.style.marginRight = 8f;
                swatch.style.backgroundColor = colour;
                row.Add(swatch);
                row.Add(Kit.Body(Strings.Get(key)));
                _detailBody.Add(row);
            }
            _detailBody.Add(Kit.Small(Strings.Get("icons.enemy")));
        }

        private void GuideLines(string text)
        {
            var lines = text.Split('\n');
            for (var i = 0; i < lines.Length; i++)
            {
                var line = Strings.Highlight(lines[i].Trim());
                if (line.Length == 0) continue;
                var label = Kit.Text(line, i == 0 ? "fc-panel-title fc-mt-3" : "fc-body fc-mt-2");
                label.enableRichText = true;
                _detailBody.Add(label);
            }
        }

        private string LockReasonShort(string id)
        {
            var mission = Progression.UnlockMission(id);
            return mission != null ? Strings.Format("detail.unlockMission", Campaign.Label(mission)) : Strings.Get("detail.unlockShop");
        }

        private void UpgradeDetail()
        {
            var id = _detailId;
            if (id == null) return;
            // A tower's branch shares its card's rank.
            if (_catalog.Vehicles.TryGetValue(id, out var structure) && structure.Fort != null) id = structure.CardId;
            if (PlayerProfile.TryRankUp(id)) Note(Strings.Format("arsenal.ranked", ("card", Strings.Card(id)), ("rank", PlayerProfile.Rank(id))));
            else Note(Strings.Get("arsenal.needCoins"), true);
            Refresh();
        }

        /// <summary>The armour tag under the name (prompt 15): the front's shield and its words.</summary>
        private static VisualElement ArmourTag(VehicleDef def)
        {
            var armour = CombatFacts.Armour(def);
            var tag = Kit.Box("fc-tag");
            tag.Add(Kit.Icon(CombatIcons.Armour(armour.Front, armour.Kind)));
            tag.Add(Kit.Text(CombatIcons.ArmourTip(armour.Front, armour.Kind, armour.Uniform ? -1 : 0), "fc-small"));
            return tag;
        }

        /// <summary>
        /// Prompt 15 E2 on the left: the armour by face, then "Strong against / Weak to" made from the armour and
        /// penetration levels and the damage types (a module has the armour only). A tap on either explains it in words.
        /// </summary>
        private void CombatBlock(VehicleDef def, bool module)
        {
            _detailCounters.Add(Kit.Caption(Strings.Get("armour.faces")));
            var diagram = Kit.Box("fc-detail__armour fc-mt-1");
            diagram.Add(KitCombat.Diagram(def));
            var armour = CombatFacts.Armour(def);
            KitCombat.TapTip(diagram, () => Strings.Get("armour.faces"),
                () => string.Join("\n", Enumerable.Range(0, 4).Select(f => CombatIcons.ArmourTip(armour[f], armour.Kind, f))));
            _detailCounters.Add(diagram);
            if (module) return;
            var lines = KitCombat.StrongWeak(def);
            lines.AddToClassList("fc-detail__strongweak");
            KitCombat.TapTip(lines, () => Strings.Get("combat.strong") + " / " + Strings.Get("combat.weak"), () => KitCombat.StrongWeakTip(def));
            _detailCounters.Add(lines);
        }

        private ScrollView _detailLeftScroll;

        /// <summary>The screenshots and checks: scroll the left column (the armour) or the tab's body (the effectiveness table) to its end once laid out.</summary>
        private void DebugScrollDetail(bool left)
        {
            var scroll = left ? _detailLeftScroll : (ScrollView)_detailScroll;
            void End(GeometryChangedEvent e)
            {
                var room = scroll.contentContainer.layout.height - scroll.contentViewport.layout.height;
                if (room > 0f) scroll.scrollOffset = new Vector2(0f, room);
            }
            scroll.contentContainer.RegisterCallback<GeometryChangedEvent>(End);
        }

        private void CounterRow(string key, IReadOnlyList<UnitClass> classes)
        {
            if (classes.Count == 0) return;
            _detailCounters.Add(Kit.Caption(Strings.Get(key)));
            var row = Kit.Box("fc-row fc-row--wrap fc-mt-1");
            foreach (var c in classes) row.Add(Tag(ClassIcon(c), Strings.Get("class." + c)));
            _detailCounters.Add(row);
        }

        // ------------------------------------------------------------------ the numbers

        private void VehicleStats(VehicleDef def, int rank)
        {
            var now = PlayerProfile.BoostFor(def);
            VehicleBoost next, rankOnly;
            if (def.Fort != null)
            {
                // A tower: its card's rank and its type's three pieces, under the tower caps.
                var pieces = PlayerProfile.TowerGear(def.CardId).ToList();
                var brands = PlayerProfile.BaseBrandCounts();
                next = rank < CardRanks.Max ? Gear.TowerBoost(rank + 1, pieces, brands) : now;
                rankOnly = Gear.TowerBoost(rank, new List<GearItem>(), brands);
            }
            else
            {
                var loadout = PlayerProfile.Loadout(Gear.BranchOf(def)).ToList();
                next = rank < CardRanks.Max ? Gear.Boost(rank + 1, loadout) : now;
                rankOnly = Gear.Boost(rank, new List<GearItem>());
            }
            var stats = UnitStats.For(_catalog, def, now);
            var after = UnitStats.For(_catalog, def, next);
            var plain = UnitStats.For(_catalog, def, rankOnly);
            var average = ClassAverage(def);
            // The legend: what each part of a bar is.
            var legend = Kit.Box("fc-row fc-row--wrap fc-mb-3");
            legend.Add(Legend("fc-statbar__base", Strings.Get("detail.legendBase")));
            legend.Add(Legend("fc-statbar__boost", Strings.Get("detail.legendGear")));
            legend.Add(Legend("fc-statbar__next", Strings.Get("detail.legendNext")));
            legend.Add(Legend("fc-statbar__avg", def.Fort is { Kind: FortKind.Utility } ? Strings.Get("detail.legendModules") : def.Fort != null
                ? Strings.Format("detail.legendTowers", SizeWord(def.Fort.Size).ToLowerInvariant())
                : Strings.Format("detail.legendAverage", Strings.Get("class." + def.Class))));
            _detailBody.Add(legend);
            for (var i = 0; i < stats.Count; i++)
            {
                // A structure does not move, and a utility module does not shoot: those rows would only say 0.
                var key = stats[i].Key;
                if (def.Fort != null && key == "stat.detail.speed") continue;
                if (def.Fort is { Kind: FortKind.Utility } && key is "stat.detail.volley" or "stat.detail.dps" or "stat.detail.range") continue;
                StatRow(stats[i], plain[i].Boosted, after[i].Boosted, average.TryGetValue(key, out var avg) ? avg : -1f);
            }
            var facts = Kit.Box("fc-mt-3");
            var price = CardRanks.CallCost(def.CpCost, rank);
            if (def.Fort == null) facts.Add(Rule("cp", price < def.CpCost
                ? Strings.Format("detail.costCut", ("cp", price), ("was", def.CpCost), ("percent", CardRanks.CutBasisPoints(rank) / 100))
                : Strings.Format("detail.cost", def.CpCost)));
            if (def.Weapon.Ammo > 0) facts.Add(Rule("ammo", Strings.Format("detail.magazine", ("count", def.Weapon.Ammo), ("seconds", Mathf.RoundToInt(def.Weapon.MagazineReload)))));
            if (def.Weapon.MinRange > 0f) facts.Add(Rule("crosshair", Strings.Format("detail.minRange", Mathf.RoundToInt(def.Weapon.MinRange))));
            if (now.Special != SpecialModule.None) facts.Add(Rule("star", Strings.Get("special." + GearKeys.Module(now.Special))));
            _detailBody.Add(facts);
        }

        /// <summary>
        /// Play-test 6 (DECISIONS 21B): a boss's numbers at campaign strength, without the card's equipment, next level
        /// and cost (a boss is no card), and its armour on each face.
        /// </summary>
        private void BossStats(VehicleDef def)
        {
            _detailBody.Add(Kit.Body2(Strings.Get("guide.boss.noCard")));
            foreach (var stat in UnitStats.For(_catalog, def, VehicleBoost.None)) StatRow(stat, stat.Boosted, stat.Boosted, -1f);
            var facts = Kit.Box("fc-mt-3");
            facts.Add(Rule("shield", BossFile.Armour(def.Armour)));
            if (def.Parts.Count > 0) facts.Add(Rule("crosshair", Strings.Format("guide.boss.partCount", def.Parts.Count)));
            if (def.Weapon.Ammo > 0) facts.Add(Rule("ammo", Strings.Format("detail.magazine", ("count", def.Weapon.Ammo), ("seconds", Mathf.RoundToInt(def.Weapon.MagazineReload)))));
            _detailBody.Add(facts);
        }

        private static VisualElement Legend(string swatch, string text)
        {
            var item = Kit.Box("fc-row fc-legend");
            item.Add(Kit.Box("fc-legend__swatch " + swatch));
            item.Add(Kit.Text(text, "fc-small"));
            return item;
        }

        /// <summary>Each stat's average over the fieldable vehicles of the same class (a tower: the towers of its size), unboosted.</summary>
        private Dictionary<string, float> ClassAverage(VehicleDef def)
        {
            var sums = new Dictionary<string, (float sum, int count)>();
            IEnumerable<string> pool = def.Fort != null ? Structures() : MatchSettings.AllVehicles;
            foreach (var id in pool)
            {
                if (!_catalog.Vehicles.TryGetValue(id, out var other)) continue;
                if (def.Fort != null ? other.Fort == null || other.Fort.Kind != def.Fort.Kind || other.Fort.Size != def.Fort.Size : other.Class != def.Class) continue;
                foreach (var s in UnitStats.For(_catalog, other, VehicleBoost.None))
                {
                    sums.TryGetValue(s.Key, out var acc);
                    sums[s.Key] = (acc.sum + s.Value, acc.count + 1);
                }
            }
            var result = new Dictionary<string, float>();
            foreach (var (key, (sum, count)) in sums)
                if (count > 0) result[key] = sum / count;
            return result;
        }

        /// <summary>
        /// One number: its name and value, the equipment's gain and the next level's gain told apart,
        /// and a bar against the roster's best (square-rooted, so a tank's damage still shows next to a
        /// bomber's) with a mark at the class average.
        /// </summary>
        private void StatRow(UnitStats.Stat stat, float withoutGear, float nextLevel, float average)
        {
            var row = Kit.Box("fc-stat");
            var head = Kit.Box("fc-row fc-row--wrap");
            head.Add(Kit.Text(Strings.Get(stat.Key), "fc-body fc-stat__name"));
            head.Add(Kit.Text(stat.Boosted.ToString(stat.Format), "fc-number-small"));
            var gear = stat.Boosted - withoutGear;
            if (Shows(gear, stat.Format)) head.Add(Kit.Text(Strings.Format("detail.fromGear", Signed(gear, stat.Format)), "fc-small fc-stat__gain"));
            var ahead = nextLevel - stat.Boosted;
            if (Shows(ahead, stat.Format)) head.Add(Kit.Text(Strings.Format("detail.fromNext", Signed(ahead, stat.Format)), "fc-small fc-positive-text fc-stat__gain"));
            row.Add(head);
            var bar = Kit.Box("fc-statbar");
            float Share(float v) => Mathf.Clamp01(Mathf.Sqrt(Mathf.Max(0f, v) / Mathf.Max(0.01f, stat.Best)));
            var ghost = Kit.Box("fc-statbar__next");
            ghost.style.width = Length.Percent(Share(nextLevel) * 100f);
            bar.Add(ghost);
            var boosted = Kit.Box("fc-statbar__boost");
            boosted.style.width = Length.Percent(Share(stat.Boosted) * 100f);
            bar.Add(boosted);
            var basePart = Kit.Box("fc-statbar__base");
            basePart.style.width = Length.Percent(Share(withoutGear) * 100f);
            bar.Add(basePart);
            if (average >= 0f)
            {
                var mark = Kit.Box("fc-statbar__avg");
                mark.style.left = Length.Percent(Share(average) * 100f);
                bar.Add(mark);
            }
            row.Add(bar);
            _detailBody.Add(row);
        }

        private static string Signed(float value, string format) => (value >= 0f ? "+" : "−") + Mathf.Abs(value).ToString(format);

        /// <summary>A gain worth printing: not one that rounds to nothing in the stat's format.</summary>
        private static bool Shows(float value, string format)
        {
            if (value <= 0f) return false;
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
                StatRow(new UnitStats.Stat("stat.detail.strikeDamage", s.Damage, s.Damage * boost, 4000f, "N0"), s.Damage * boost, s.Damage * nextBoost, -1f);
                StatRow(new UnitStats.Stat("stat.detail.strikeTotal", total, total * boost, 12000f, "N0"), total * boost, total * nextBoost, -1f);
                StatRow(new UnitStats.Stat("stat.detail.blast", s.BlastRadius, s.BlastRadius, 27f, "0.#"), s.BlastRadius, s.BlastRadius, -1f);
            }
            var facts = Kit.Box("fc-mt-3");
            facts.Add(Rule("cp", Strings.Format("detail.cost", s.CpCost)));
            facts.Add(Rule("restart", Strings.Format("detail.cooldown", Mathf.RoundToInt(s.Cooldown))));
            if (s.Count > 1) facts.Add(Rule("barrage", Strings.Format("detail.count", s.Count)));
            facts.Add(Rule("info", Strings.Get("support." + id + ".info")));
            _detailBody.Add(facts);
        }

        private void VehicleWeapons(VehicleDef def, bool table = false)
        {
            // Prompt 32 L8: small chips for the handbook's marks (top attack, second round, airburst, guided, structure and wall
            // breakers); a tap opens the right entry of the ammunition handbook. The main card keeps its marks.
            var chips = AmmoHandbook.Chips(_catalog, def);
            if (chips.Count > 0)
            {
                var strip = Kit.Box("fc-hb__chips");
                strip.style.flexDirection = FlexDirection.Row;
                strip.style.flexWrap = Wrap.Wrap;
                foreach (var (key, entry) in chips)
                {
                    var target = entry;
                    strip.Add(new KitChip(Strings.Get(key), false, () => OpenHandbook(target)));
                }
                _detailBody.Add(strip);
            }
            var mounts = def.Mounts;
            var lines = WeaponInfo.Of(def);
            for (var i = 0; i < lines.Count && i < mounts.Count; i++)
            {
                var w = mounts[i].Weapon;
                var row = Kit.Box(KitPanel.SurfaceClass + " fc-weapon");
                // Prompt 15 E2: the weapon's chip (its form, the damage-type mark, the extra marks) beside its name; a tap says it in words.
                var facts = CombatFacts.Of(w, def);
                if (facts != null)
                {
                    var chip = KitCombat.Chip(facts, large: true, extras: true);
                    chip.AddToClassList("fc-weapon__chip");
                    var weaponName = lines[i].Name;
                    KitCombat.TapTip(row, () => weaponName, () => CombatIcons.WeaponTip(facts));
                    row.Add(chip);
                }
                else row.Add(Kit.Icon(lines[i].Icon, "fc-weapon__icon"));
                var text = Kit.Box("fc-row-text fc-grow");
                text.Add(Kit.Text(Kit.Caps(lines[i].Name + (i == 0 ? "  ·  " + Strings.Get("detail.main") : "")), "fc-panel-title"));
                // Full fix L3: the full cycle (the salvo or magazine fired off plus its reload), never the pause alone:
                // "salvo N · cycle X s" for a salvo or a magazine, "every X s" for a single shot.
                var cycle = w.CycleSeconds.ToString(w.CycleSeconds >= 10f ? "0" : "0.#", Strings.Culture);
                var dmg = w.Damage.ToString("N0", Strings.Culture);
                text.Add(Kit.Body2(w.RoundsPerCycle > 1
                    ? Strings.Format("detail.weaponLineSalvo", ("damage", dmg), ("count", w.RoundsPerCycle), ("seconds", cycle), ("metres", Mathf.RoundToInt(w.Range)),
                        ("targets", lines[i].Targets))
                    : Strings.Format("detail.weaponLine", ("damage", dmg), ("seconds", cycle), ("metres", Mathf.RoundToInt(w.Range)), ("targets", lines[i].Targets))));
                if (w.Damage > 0f) text.Add(Kit.Small(WeaponFacts(def, w)));
                if (lines[i].Ammo > 0) text.Add(Kit.Small(Strings.Format("detail.ammo", lines[i].Ammo)));
                // Prompt 13 G.1: every figure (real name and calibre, rounds, magazine or stores and how they
                // come back, faster sites, range), behind "More".
                if (_weaponsMore && w.Damage > 0f)
                    foreach (var line in UnitLines.Weapon(def, w)) text.Add(Kit.Small(line));
                // Prompt 25 G: a gun of two rounds lists both, each with its figures and what it is loaded for.
                if (CombatFacts.SecondRounds(w, def) > 0) text.Add(RoundsOf(def, w));
                row.Add(text);
                _detailBody.Add(row);
            }
            // Prompt 25 G: the table has a row for each round of a gun of two rounds.
            var weapons = CombatFacts.Rounds(def);
            if (table && weapons.Count > 0)
            {
                // Prompt 15 E2: the effectiveness table, made from the data.
                var panel = Kit.Box(KitPanel.SurfaceClass + " fc-panel fc-mt-2 fc-detail__effect");
                panel.Add(Kit.Text(Kit.Caps(Strings.Get("combat.effect")), "fc-panel-title"));
                panel.Add(KitCombat.EffectTable(weapons));
                KitCombat.TapTip(panel, () => Strings.Get("combat.effect"), () => Strings.Get("combat.effect.tip"));
                _detailBody.Add(panel);
            }
            _detailBody.Add(new KitButton(ButtonTier.Text, Strings.Get(_weaponsMore ? "detail.less" : "detail.more"), () =>
            {
                _weaponsMore = !_weaponsMore;
                RefreshDetail();
            }));
        }

        /// <summary>
        /// Prompt 25 G (DECISIONS 25G): a gun's rounds under its line: the ammo switch and "switches on its own", then its own
        /// round and each second round its carrier loads: the chip, the round's kind, damage type, penetration, damage and
        /// blast, and what the gun loads it for (its own: everything else).
        /// </summary>
        private static VisualElement RoundsOf(VehicleDef def, WeaponDef gun)
        {
            var box = Kit.Box("fc-rounds");
            var head = Kit.Box("fc-rounds__head");
            head.Add(Kit.Icon("ammoswap", "fc-rounds__icon"));
            head.Add(Kit.Text(Strings.Get("detail.rounds"), "fc-small"));
            box.Add(head);
            box.Add(RoundRow(gun, Strings.Format("detail.roundMain", ("name", UnitLines.RoundWord(gun))), Strings.Format("detail.roundFor",
                ("targets", Strings.Get("round.for.rest"))), def));
            foreach (var r in gun.Rounds)
                if (r.CarriedBy(def))
                    box.Add(RoundRow(r.Round, UnitLines.RoundWord(r.Round), Strings.Format("detail.roundSwitch", ("targets", UnitLines.UseWords(r)),
                        ("seconds", gun.SwitchSeconds(r).ToString("0.#", Strings.Culture))), def));
            return box;
        }

        private static VisualElement RoundRow(WeaponDef round, string name, string use, VehicleDef def)
        {
            var row = Kit.Box("fc-round");
            var facts = CombatFacts.Of(round);
            if (facts != null) row.Add(KitCombat.Chip(facts));
            var text = Kit.Box("fc-row-text fc-grow");
            text.Add(Kit.Body2(name));
            text.Add(Kit.Small(UnitLines.RoundFigures(round)));
            text.Add(Kit.Small(use));
            row.Add(text);
            return row;
        }

        /// <summary>The weapons tab shows every figure (prompt 13 G.5: "More").</summary>
        private bool _weaponsMore;

        /// <summary>
        /// Full fix L3: a weapon's sustained damage a second on this carrier (a cycle's rounds over the cycle, every barrel,
        /// a launcher's reload, the boss's own weapon damage), its barrels fired together, a blast's core and edge.
        /// </summary>
        internal static string WeaponFacts(VehicleDef def, WeaponDef w)
        {
            var parts = new List<string>
            {
                Strings.Format("detail.sustained", ("dps", MachineBrigade.Sim.Combat.FirePower.Sustained(w, def).ToString("N0", Strings.Culture))),
            };
            if (w.Simultaneous && w.Barrels > 1) parts.Add(Strings.Format("detail.barrels", ("count", w.Barrels)));
            if (w.SplashRadius > 0.5f && w.SplashEdge > w.SplashRadius)
                parts.Add(Strings.Format("detail.coreEdge", ("core", w.SplashRadius.ToString("0.#", Strings.Culture)), ("edge", w.SplashEdge.ToString("0.#", Strings.Culture))));
            else if (w.SplashRadius > 0.5f) parts.Add(Strings.Format("detail.core", ("core", w.SplashRadius.ToString("0.#", Strings.Culture))));
            return string.Join("  ·  ", parts);
        }

        /// <summary>What a utility module does for the base, from its data (repairs, reloads, aircraft, supply, radar).</summary>
        private void ModuleFacts(VehicleDef def)
        {
            if (def.Utility is not { } u) return;
            var facts = Kit.Box("fc-mt-3");
            facts.Add(Kit.Text(Kit.Caps(Strings.Get("detail.moduleDoes")), "fc-caption fc-mb-2"));
            if (u.Repair > 0f) facts.Add(Rule("repair", Strings.Format("detail.module.repair", (u.Repair * 100f).ToString("0.#", Kit.Culture))));
            if (u.Rearm > 1f) facts.Add(Rule("ammo", Strings.Format("detail.module.rearm", u.Rearm.ToString("0.#", Kit.Culture))));
            if (u.AirRepair > 0f) facts.Add(Rule("helicopter", Strings.Format("detail.module.air", ("percent", (u.AirRepair * 100f).ToString("0.#", Kit.Culture)), ("metres", Mathf.RoundToInt(u.AirReach)))));
            // Prompt 13 G.4: the landing pad's stores rate, a hangar's aircraft.
            foreach (var line in UnitLines.Module(u, false)) facts.Add(Rule("ammo", line));
            if (u.Supply > 0) facts.Add(Rule("people", Strings.Format("detail.module.supply", u.Supply)));
            if (u.RevealBase) facts.Add(Rule("eye", Strings.Get("detail.module.radar")));
            _detailBody.Add(facts);
        }

        /// <summary>
        /// A structure's Equipment tab: a tower's branches (what each does, which is chosen, the rank
        /// they open at) and its type's three gear slots with what they wear; a module's note. Both are
        /// changed right here (DECISIONS 12E): a tap on a branch chooses it (a change asks first, it
        /// costs coins), a tap on a slot lists the bag's pieces that fit it. The base screen, which the
        /// button under them opens with the structure picked, changes them too.
        /// </summary>
        private void StructureEquipment(VehicleDef def, bool module)
        {
            var card = def.CardId;
            if (!module)
            {
                var branches = TowerCards.Branches(_catalog, card);
                var rank = PlayerProfile.Rank(card);
                var chosen = PlayerProfile.TowerBranch(card);
                _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("camp.branch")), "fc-caption fc-mb-2"));
                if (branches.Count == 0) _detailBody.Add(Kit.Body2(Strings.Get("camp.branchNone")));
                else
                {
                    _detailBody.Add(Kit.Body2(rank < TowerCards.BranchRank ? Strings.Format("camp.branchLocked", ("rank", TowerCards.BranchRank), ("rank2", rank))
                        : (chosen == null ? Strings.Get("camp.branchFree") : PlayerProfile.FreeBranchSwap(card) ? Strings.Get("camp.branchFreeSwap")
                            : Strings.Format("camp.branchSwap", PlayerProfile.BranchSwapCoins.ToString("N0", Strings.Culture)))
                          + " " + Strings.Get("detail.branchTap")));
                    // The tower-branch rework (D.1): both branches side by side, from their data.
                    _detailBody.Add(BranchLines.Picker(_catalog, card, chosen, rank < TowerCards.BranchRank, b => ChooseTowerBranch(card, b)));
                }
                _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("camp.gear")), "fc-caption fc-mt-4 fc-mb-2"));
                _detailBody.Add(Kit.Body2(Strings.Get("detail.gearTap")));
                var grid = Kit.Box("fc-army__grid fc-mt-2");
                for (var i = 0; i < BaseScreen.GearSlots.Length; i++)
                {
                    var cell = Kit.Box("fc-army__slot");
                    var slot = BaseScreen.TowerSlotOf(i);
                    cell.Add(Kit.Caption(GearText.TowerSlotName(slot)));
                    var item = BaseScreen.TowerGearIn(card, i);
                    if (item != null) cell.Add(new KitGearCard(GearCardData.From(item), () => PickTowerGear(card, slot)));
                    else
                    {
                        var empty = Kit.Tappable("fc-gcard fc-gcard--empty", () => PickTowerGear(card, slot));
                        var body = Kit.Box("fc-gcard__body");
                        body.Add(Kit.Text(Strings.Get("gear.empty"), "fc-gcard__stat"));
                        empty.Add(body);
                        cell.Add(empty);
                    }
                    grid.Add(cell);
                }
                _detailBody.Add(grid);
            }
            else _detailBody.Add(Kit.Body2(Strings.Get("detail.moduleNoGear")));
        }

        /// <summary>A tower's branch from its detail page: rank 7 first; the first choice is free, a change asks before it spends coins.</summary>
        private void ChooseTowerBranch(string card, string branchId)
        {
            if (PlayerProfile.Rank(card) < TowerCards.BranchRank)
            {
                Note(Strings.Format("camp.branchNeedRank", TowerCards.BranchRank), true);
                return;
            }
            var chosen = PlayerProfile.TowerBranch(card);
            if (chosen == branchId) return;
            if (chosen == null || PlayerProfile.FreeBranchSwap(card))
            {
                ApplyTowerBranch(card, branchId);
                return;
            }
            VisualElement scrim = null;
            var change = new KitButton(ButtonTier.Primary, Strings.Get("camp.change"), () =>
            {
                scrim?.RemoveFromHierarchy();
                ApplyTowerBranch(card, branchId);
            }, "upgrade");
            var cancel = new KitButton(ButtonTier.Secondary, Strings.Get("camp.cancel"), () => scrim?.RemoveFromHierarchy());
            scrim = KitDialog.Present(Root, KitDialog.Build(Strings.Branch(branchId),
                Strings.Format("camp.branchConfirm", ("card", Strings.Card(card)), ("branch", Strings.Branch(branchId)), ("coins", PlayerProfile.BranchSwapCoins.ToString("N0", Strings.Culture))), cancel, change));
        }

        private void ApplyTowerBranch(string card, string branchId)
        {
            if (!PlayerProfile.TryChooseBranch(card, branchId))
            {
                Note(Strings.Get("arsenal.needCoins"), true);
                return;
            }
            Note(Strings.Format("camp.branchChosen", ("card", Strings.Card(card)), ("branch", Strings.Branch(branchId))));
            Refresh();
        }

        /// <summary>One of a tower type's gear slots from its detail page: the bag's pieces that fit it (the worn one ticked), or take it off.</summary>
        private void PickTowerGear(string card, GearSlot slot)
        {
            var worn = PlayerProfile.TowerEquipped(card, slot);
            var pieces = PlayerProfile.TowerGearFor(card, slot);
            if (pieces.Count == 0 && worn == null)
            {
                Note(Strings.Get("camp.gearNoPieces"), true);
                return;
            }
            // The first row takes the worn piece off (or leaves the slot empty): nothing is ticked by mistake.
            var options = new List<KitOption> { new(Strings.Get(worn != null ? "camp.gearOff" : "camp.empty")) };
            var chosen = 0;
            foreach (var piece in pieces)
            {
                if (piece == worn) chosen = options.Count;
                options.Add(new KitOption(GearText.Name(piece), Strings.Format("gear.detail", ("rarity", Strings.Get("rarity." + piece.Rarity.ToString().ToLowerInvariant())),
                    ("level", piece.level), ("total", Gear.LevelCap[piece.rarity]), ("item", GearCardData.ShortStat(piece)))));
            }
            new KitDropdown(GearText.TowerSlotName(slot), options, chosen, i =>
            {
                if (i == 0)
                {
                    if (worn == null) return;
                    PlayerProfile.UnequipTower(card, slot);
                    Note(Strings.Format("camp.gearRemoved", ("slot", GearText.TowerSlotName(slot)), ("card", Strings.Card(card))));
                }
                else if (PlayerProfile.EquipTower(card, pieces[i - 1])) Note(Strings.Format("camp.gearWorn", Strings.Card(card)));
                Refresh();
            }, thumbnail: false) { name = "tower-gear-picker" }.OpenIn(Root);
        }

        /// <summary>The base screen with a structure picked (its Gear tab when asked), from its detail page.</summary>
        private void OpenInBase(string id, bool gear = false)
        {
            CloseTop();
            _armyView = ArmyView.Base;
            ShowTab(Tab.Army);
            _base.Pick(id, gear);
        }

        /// <summary>The branch's loadout on this vehicle: the seven slots as gear cards; a tap opens the equipment tab on that slot.</summary>
        private void DetailEquipment(VehicleDef def)
        {
            var branch = Gear.BranchOf(def);
            _detailBody.Add(Kit.Body2(Strings.Format("detail.sharedGear", Strings.Get("gear.branch." + branch.ToString().ToLowerInvariant()))));
            var grid = Kit.Box("fc-army__grid fc-mt-3");
            for (var s = 0; s < Gear.Slots; s++)
            {
                var slot = (GearSlot)s;
                var item = PlayerProfile.Equipped(branch, slot);
                void GoToSlot()
                {
                    _branch = branch;
                    _slotFilter = slot;
                    _gearSelected = PlayerProfile.Equipped(branch, slot);
                    _armyView = ArmyView.Equipment;
                    ShowTab(Tab.Army);
                }
                var cell = Kit.Box("fc-army__slot");
                cell.Add(Kit.Caption(GearText.SlotName(slot)));
                if (item != null)
                {
                    var card = new KitGearCard(GearCardData.From(item), GoToSlot);
                    // Prompt 29 L5: the branch's Trophy or heat decoys on a vehicle without an APS mount or flares do nothing here.
                    var idle = !VehicleFit.WorksOn(item, def);
                    card.EnableInClassList("fc-gcard--unfit", idle);
                    cell.Add(card);
                    if (idle) cell.Add(Kit.Text(Strings.Get("gear.idleHere"), "fc-small fc-danger-text"));
                }
                else
                {
                    var empty = Kit.Tappable("fc-gcard fc-gcard--empty", GoToSlot);
                    var body = Kit.Box("fc-gcard__body");
                    body.Add(Kit.Text(Strings.Get("gear.empty"), "fc-gcard__stat"));
                    empty.Add(body);
                    cell.Add(empty);
                }
                grid.Add(cell);
            }
            _detailBody.Add(grid);
            _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("gear.setsTitle")), "fc-caption fc-mt-3 fc-mb-2"));
            _detailBody.Add(SetChips(branch));
        }
    }
}
