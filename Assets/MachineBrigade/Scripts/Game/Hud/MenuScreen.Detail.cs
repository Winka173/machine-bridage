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
        private string _detailId;
        private List<string> _detailList = new();

        private void BuildDetailPage()
        {
            _detail = FullPage("fc-detail");
            _detailLeft = Kit.Box("fc-detail__left");
            var leftScroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-detail__left-scroll");
            _detailLeftBody = Kit.Box("fc-detail__left-body");
            leftScroll.Add(_detailLeftBody);
            _detailLeft.Add(leftScroll);
            _detailStage = Kit.Box("fc-detail__stage");
            _detailArt = Kit.Box("fc-detail__art");
            _detailStage.Add(_detailArt);
            _detailPreview = Kit.Box("fc-detail__preview");
            _detailStage.Add(_detailPreview);
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
            _detailList = IsStructure(id) ? Structures() : MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(Passes).ToList();
            if (!_detailList.Contains(id)) _detailList.Add(id);
            Open(_detail, Strings.Get(IsStructure(id) ? "detail.structureTitle" : "detail.title"));
            ShowPreview();
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
                else Preview.Show(vehicle.Model, vehicle.Scale);
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
                _detailTags.Add(Tag("shield", Strings.Format("detail.armour", Strings.Get("armor." + vehicle.Armor.ToString().ToLowerInvariant()))));
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
                _detailTags.Add(Tag("shield", Strings.Format("detail.armour", Strings.Get("armor." + vehicle.Armor.ToString().ToLowerInvariant()))));
            }
            else _detailTags.Add(Tag(CardIcons.For(id), Strings.Get("detail.strikeTag")));
            if (!structure) _detailTags.Add(Tag("cp", Strings.Format("detail.cpTag", CostOf(id))));
            _detailTags.Add(Tag("upgrade", Strings.Format("kit.level", rank)));
            _detailCounters.Clear();
            if (vehicle != null && !module)
            {
                CounterRow("detail.strongVs", Counters.StrongVs(vehicle));
                CounterRow("detail.weakVs", Counters.WeakVs(vehicle.Class));
            }

            // Right: the chosen tab.
            _detailBody.Clear();
            switch (_detailTab)
            {
                case DetailTab.Stats:
                    if (vehicle != null) VehicleStats(vehicle, rank);
                    else StrikeStats(id, rank);
                    if (module) ModuleFacts(vehicle);
                    break;
                case DetailTab.Guide:
                    Guide(id);
                    break;
                case DetailTab.Weapons:
                    if (module) _detailBody.Add(Kit.Body2(Strings.Get("detail.moduleNoWeapons")));
                    else if (vehicle != null) VehicleWeapons(vehicle);
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
            var prints = Kit.Box("fc-detail__prints");
            var need = CardRanks.BlueprintsToNext(rank);
            var have = PlayerProfile.Blueprints(id) + PlayerProfile.UniversalBlueprints;
            var enough = need > 0 && have >= need;
            var head = Kit.Box("fc-row fc-row--wrap");
            head.Add(Kit.Icon("blueprint", "fc-rule-icon"));
            head.Add(Kit.Text(need <= 0 ? Strings.Get("arsenal.maxRank") : Strings.Format("detail.prints", have, need), "fc-body fc-row-text fc-ml-2"));
            if (enough) head.Add(Kit.Text(Strings.Get("detail.enoughPrints"), "fc-small fc-positive-text fc-ml-2"));
            prints.Add(head);
            prints.Add(new KitProgress(need <= 0 ? 1f : Mathf.Clamp01((float)have / need), enough));
            if (unlocked && rank < CardRanks.Max)
                prints.Add(Kit.Small(Strings.Format("detail.nextLevel", rank + 1, Kit.Count(CardRanks.CoinsToNext(rank)))));
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
            }
            // The enemy's elite versions of this card (prompt 8 H.6): each with its own entry and skills.
            foreach (var elite in _catalog.Vehicles.Values)
            {
                if (!elite.Elite || elite.EliteOf != id || !Strings.Has("guide." + elite.Id)) continue;
                _detailBody.Add(Kit.Text(Kit.Caps(Strings.Get("detail.eliteVersion")), "fc-caption fc-mt-4"));
                GuideLines(Strings.Get("guide." + elite.Id));
            }
            // A boss's parts and what breaking each does (prompt 9).
            if (_catalog.Vehicles.TryGetValue(id, out var boss) && boss.Parts.Count > 0) BossPartsGuide(boss);
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
            if (PlayerProfile.TryRankUp(id)) Note(Strings.Format("arsenal.ranked", Strings.Card(id), PlayerProfile.Rank(id)));
            else Note(Strings.Get("arsenal.needCoins"), true);
            Refresh();
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
                ? Strings.Format("detail.costCut", price, def.CpCost, CardRanks.CutBasisPoints(rank) / 100)
                : Strings.Format("detail.cost", def.CpCost)));
            if (def.Weapon.Ammo > 0) facts.Add(Rule("ammo", Strings.Format("detail.magazine", def.Weapon.Ammo, Mathf.RoundToInt(def.Weapon.MagazineReload))));
            if (def.Weapon.MinRange > 0f) facts.Add(Rule("crosshair", Strings.Format("detail.minRange", Mathf.RoundToInt(def.Weapon.MinRange))));
            if (now.Special != SpecialModule.None) facts.Add(Rule("star", Strings.Get("special." + GearKeys.Module(now.Special))));
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

        private void VehicleWeapons(VehicleDef def)
        {
            var mounts = def.Mounts;
            var lines = WeaponInfo.Of(def);
            for (var i = 0; i < lines.Count && i < mounts.Count; i++)
            {
                var w = mounts[i].Weapon;
                var row = Kit.Box(KitPanel.SurfaceClass + " fc-weapon");
                row.Add(Kit.Icon(lines[i].Icon, "fc-weapon__icon"));
                var text = Kit.Box("fc-row-text fc-grow");
                text.Add(Kit.Text(Kit.Caps(lines[i].Name + (i == 0 ? "  ·  " + Strings.Get("detail.main") : "")), "fc-panel-title"));
                var burst = w.RoundsPerCycle > 1 ? $" × {w.RoundsPerCycle}" : "";
                // A magazine gun: its rounds, then the magazine change.
                var pause = w.Clip > 0 ? w.ClipReload : w.Cooldown;
                text.Add(Kit.Body2(Strings.Format("detail.weaponLine", w.Damage.ToString("N0") + burst, pause.ToString("0.#"), Mathf.RoundToInt(w.Range),
                    lines[i].Targets)));
                if (lines[i].Ammo > 0) text.Add(Kit.Small(Strings.Format("detail.ammo", lines[i].Ammo)));
                // Prompt 13 G.1: every figure (real name and calibre, rounds, magazine or stores and how they
                // come back, faster sites, range), behind "More".
                if (_weaponsMore && w.Damage > 0f)
                    foreach (var line in UnitLines.Weapon(def, w)) text.Add(Kit.Small(line));
                row.Add(text);
                _detailBody.Add(row);
            }
            _detailBody.Add(new KitButton(ButtonTier.Text, Strings.Get(_weaponsMore ? "detail.less" : "detail.more"), () =>
            {
                _weaponsMore = !_weaponsMore;
                RefreshDetail();
            }));
        }

        /// <summary>The weapons tab shows every figure (prompt 13 G.5: "More").</summary>
        private bool _weaponsMore;

        /// <summary>What a utility module does for the base, from its data (repairs, reloads, aircraft, supply, radar).</summary>
        private void ModuleFacts(VehicleDef def)
        {
            if (def.Utility is not { } u) return;
            var facts = Kit.Box("fc-mt-3");
            facts.Add(Kit.Text(Kit.Caps(Strings.Get("detail.moduleDoes")), "fc-caption fc-mb-2"));
            if (u.Repair > 0f) facts.Add(Rule("repair", Strings.Format("detail.module.repair", (u.Repair * 100f).ToString("0.#", Kit.Culture))));
            if (u.Rearm > 1f) facts.Add(Rule("ammo", Strings.Format("detail.module.rearm", u.Rearm.ToString("0.#", Kit.Culture))));
            if (u.AirRepair > 0f) facts.Add(Rule("helicopter", Strings.Format("detail.module.air", (u.AirRepair * 100f).ToString("0.#", Kit.Culture), Mathf.RoundToInt(u.AirReach))));
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
                    _detailBody.Add(Kit.Body2(rank < TowerCards.BranchRank ? Strings.Format("camp.branchLocked", TowerCards.BranchRank, rank)
                        : (chosen == null ? Strings.Get("camp.branchFree") : Strings.Format("camp.branchSwap", PlayerProfile.BranchSwapCoins.ToString("N0")))
                          + " " + Strings.Get("detail.branchTap")));
                    foreach (var b in branches)
                    {
                        var branchId = b;
                        var row = Kit.Tappable(KitPanel.SurfaceClass + " fc-weapon" + (b == chosen ? " fc-weapon--chosen" : ""), () => ChooseTowerBranch(card, branchId));
                        row.Add(Kit.Icon(b == chosen ? "check" : rank < TowerCards.BranchRank ? "lock" : "upgrade", "fc-weapon__icon"));
                        var text = Kit.Box("fc-row-text fc-grow");
                        text.Add(Kit.Text(Kit.Caps(Strings.Branch(b)), "fc-panel-title"));
                        text.Add(Kit.Body2(Strings.Get("branch." + b + ".info")));
                        row.Add(text);
                        _detailBody.Add(row);
                    }
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
            if (chosen == null)
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
                Strings.Format("camp.branchConfirm", Strings.Card(card), Strings.Branch(branchId), PlayerProfile.BranchSwapCoins.ToString("N0")), cancel, change));
        }

        private void ApplyTowerBranch(string card, string branchId)
        {
            if (!PlayerProfile.TryChooseBranch(card, branchId))
            {
                Note(Strings.Get("arsenal.needCoins"), true);
                return;
            }
            Note(Strings.Format("camp.branchChosen", Strings.Card(card), Strings.Branch(branchId)));
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
                options.Add(new KitOption(GearText.Name(piece), Strings.Format("gear.detail", Strings.Get("rarity." + piece.Rarity.ToString().ToLowerInvariant()),
                    piece.level, Gear.LevelCap[piece.rarity], GearCardData.ShortStat(piece))));
            }
            new KitDropdown(GearText.TowerSlotName(slot), options, chosen, i =>
            {
                if (i == 0)
                {
                    if (worn == null) return;
                    PlayerProfile.UnequipTower(card, slot);
                    Note(Strings.Format("camp.gearRemoved", GearText.TowerSlotName(slot), Strings.Card(card)));
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
                if (item != null) cell.Add(new KitGearCard(GearCardData.From(item), GoToSlot));
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
