using System;
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What a vehicle card shows. Screens fill it from the profile (<see cref="From"/>) or by hand.</summary>
    public sealed class VehicleCardData
    {
        public string Id;
        public string Name;
        public KitBranch Branch;
        public string ClassIcon = "tank";
        public int Cp;
        public int Level = 1;

        /// <summary>Enough blueprints and coins for the next level right now: the only time the upgrade mark shows.</summary>
        public bool CanUpgrade;

        public bool Locked;

        /// <summary>Where a locked card is won ("Unlocks in Chapter 3").</summary>
        public string UnlockWhere;

        /// <summary>The 3D render (Resources/UI/Cards, see <see cref="CardArt"/>); null shows the class icon large instead.</summary>
        public Texture2D Art;

        /// <summary>A card for a vehicle from the catalog, with the player's level, upgrade and lock state.</summary>
        public static VehicleCardData From(VehicleDef def, string unlockWhere = null)
        {
            var locked = !PlayerProfile.IsUnlocked(def.Id);
            return new VehicleCardData
            {
                Id = def.Id,
                Name = Strings.Card(def.Id),
                Branch = KitBranches.Of(def),
                ClassIcon = KitBranches.ClassIcon(def.Class),
                Cp = def.CpCost,
                Level = PlayerProfile.Rank(def.Id),
                CanUpgrade = !locked && PlayerProfile.CanRankUp(def.Id),
                Locked = locked,
                UnlockWhere = locked ? unlockWhere ?? UnlockText(def.Id) : null,
                Art = CardArt.For(def.Id),
            };
        }

        /// <summary>The default unlock line: the campaign mission that wins it, else the shop.</summary>
        public static string UnlockText(string id)
        {
            var mission = Progression.UnlockMission(id);
            return mission != null ? Strings.Format("kit.unlockMission", Campaign.IndexOf(mission.Id) + 1) : Strings.Get("kit.unlockShop");
        }
    }

    /// <summary>
    /// A vehicle card: the 3D render under a 3 px bar in the branch's colour, the class icon, the CP
    /// cost in a dark box in the corner, the full name (it wraps; it is never cut), the level, and
    /// the upgrade mark only when the upgrade is affordable now. A locked card is dimmed to 45 %
    /// and says where it unlocks.
    /// </summary>
    public sealed class KitVehicleCard : VisualElement
    {
        public const string BaseClass = "fc-vcard";

        public KitVehicleCard(VehicleCardData data, Action onClick = null)
        {
            Data = data;
            AddToClassList(BaseClass);
            EnableInClassList("fc-vcard--locked", data.Locked);
            var content = Kit.Box("fc-vcard__content");
            content.Add(Kit.Box("fc-vcard__bar " + KitBranches.ColourClass(data.Branch)));
            var art = Kit.Box("fc-vcard__art");
            if (data.Art != null) art.style.backgroundImage = Background.FromTexture2D(data.Art);
            else art.Add(Kit.Icon(data.ClassIcon, "fc-vcard__fallback"));
            art.Add(Kit.Icon(data.ClassIcon, "fc-vcard__class"));
            var cp = Kit.Box("fc-vcard__cp");
            cp.Add(Kit.Text(data.Cp.ToString(), "fc-vcard__cp-value"));
            cp.Add(Kit.Text("CP", "fc-vcard__cp-unit"));
            art.Add(cp);
            if (data.CanUpgrade && !data.Locked)
            {
                var upgrade = Kit.Box("fc-vcard__upgrade");
                upgrade.Add(Kit.Icon("upgrade", null, 2.2f));
                art.Add(upgrade);
            }
            content.Add(art);
            var body = Kit.Box("fc-vcard__body");
            body.Add(Kit.Text(Kit.Caps(data.Name), "fc-vcard__name"));
            body.Add(Kit.Text(Strings.Format("kit.level", data.Level), "fc-vcard__level"));
            content.Add(body);
            Add(content);
            var lockRow = Kit.Box("fc-vcard__lock");
            lockRow.Add(Kit.Icon("lock"));
            lockRow.Add(Kit.Text(data.UnlockWhere ?? "", "fc-vcard__lock-text"));
            Add(lockRow);
            if (onClick == null) return;
            pickingMode = PickingMode.Position;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                onClick();
            }));
        }

        public VehicleCardData Data { get; }

        public bool Chosen
        {
            get => ClassListContains("fc-vcard--chosen");
            set => EnableInClassList("fc-vcard--chosen", value);
        }
    }

    /// <summary>What a gear card shows: the item type's own picture, the rarity, the short main stat, the level.</summary>
    public sealed class GearCardData
    {
        public string Name;
        public Texture2D Picture;
        public int Rarity;
        public int Level = 1;

        /// <summary>The main stat, short ("+15% heavy vehicles").</summary>
        public string MainStat;

        public bool Equipped;

        /// <summary>The main stat's change against the worn piece ("+3%"), and its sign (1 better, -1 worse, 0 none).</summary>
        public string Compare;

        public int CompareSign;

        public static GearCardData From(GearItem item, GearItem worn = null)
        {
            var data = new GearCardData
            {
                Name = GearText.Name(item),
                Picture = GearArt.PictureFor(item),
                Rarity = Mathf.Clamp(item.rarity, 0, 4),
                Level = item.level,
                MainStat = MainLine(item),
            };
            if (worn != null && worn != item && Gear.MainStat(worn) == Gear.MainStat(item))
            {
                var delta = MainValue(item) - MainValue(worn);
                data.CompareSign = Mathf.Abs(delta) < 1e-4f ? 0 : delta > 0f ? 1 : -1;
                data.Compare = data.CompareSign == 0 ? Strings.Get("kit.same") : (delta > 0f ? "+" : "−") + Mathf.RoundToInt(Mathf.Abs(delta) * 100f) + "%";
            }
            return data;
        }

        private static float MainValue(GearItem item)
        {
            var main = Gear.MainStat(item);
            foreach (var line in Gear.Lines(item))
                if (line.Stat == main && line.Kind != Gear.LineKind.Penalty) return line.Value;
            return 0f;
        }

        private static string MainLine(GearItem item)
        {
            var main = Gear.MainStat(item);
            foreach (var line in Gear.Lines(item))
                if (line.Stat == main) return GearText.Line(line);
            var lines = Gear.Lines(item);
            return lines.Count > 0 ? GearText.Line(lines[0]) : "";
        }
    }

    /// <summary>
    /// A gear card: the item type's own picture in a frame of its rarity colour, the level in the
    /// corner, the name, the short main stat, a check when worn and the change against the worn piece.
    /// </summary>
    public sealed class KitGearCard : VisualElement
    {
        public const string BaseClass = "fc-gcard";

        public KitGearCard(GearCardData data, Action onClick = null)
        {
            Data = data;
            AddToClassList(BaseClass);
            AddToClassList("fc-rarity-" + Mathf.Clamp(data.Rarity, 0, 4));
            var art = Kit.Box("fc-gcard__art");
            var picture = Kit.Box("fc-gcard__picture");
            if (data.Picture != null) picture.style.backgroundImage = Background.FromTexture2D(data.Picture);
            art.Add(picture);
            art.Add(Kit.Text(Strings.Format("kit.levelShort", data.Level), "fc-gcard__level"));
            if (data.Equipped) art.Add(Kit.Icon("check", "fc-gcard__equipped", 2.4f));
            Add(art);
            var body = Kit.Box("fc-gcard__body");
            body.Add(Kit.Text(Kit.Caps(data.Name), "fc-gcard__name"));
            if (!string.IsNullOrEmpty(data.MainStat)) body.Add(Kit.Text(data.MainStat, "fc-gcard__stat"));
            if (!string.IsNullOrEmpty(data.Compare))
                body.Add(Kit.Text(data.Compare, "fc-gcard__compare" + (data.CompareSign > 0 ? " fc-gcard__compare--better" : data.CompareSign < 0 ? " fc-gcard__compare--worse" : "")));
            Add(body);
            if (onClick == null) return;
            pickingMode = PickingMode.Position;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                onClick();
            }));
        }

        public GearCardData Data { get; }

        public bool Chosen
        {
            get => ClassListContains("fc-gcard--chosen");
            set => EnableInClassList("fc-gcard--chosen", value);
        }
    }

    /// <summary>One row of a comparison with the worn piece: the stat, what is worn, this piece, the change.</summary>
    public sealed class KitCompareRow : VisualElement
    {
        public KitCompareRow(string stat, string worn, string candidate, int sign)
        {
            AddToClassList("fc-compare-row");
            Add(Kit.Text(stat, "fc-body-2 fc-compare-row__stat"));
            Add(Kit.Text(worn, "fc-body-2 fc-compare-row__value"));
            Add(Kit.Text(candidate, "fc-body fc-compare-row__value" + (sign > 0 ? " fc-positive-text" : sign < 0 ? " fc-danger-text" : "")));
        }
    }

    /// <summary>Sorting and filtering of gear for the equipment screen: by slot, rarity and brand.</summary>
    public static class GearQuery
    {
        public enum Sort
        {
            Rarity,
            Level,
            Slot,
            Brand,
        }

        public static IEnumerable<GearItem> Filter(IEnumerable<GearItem> items, GearSlot? slot = null, int? rarity = null, int? brand = null) =>
            items.Where(i => (slot == null || i.Slot == slot) && (rarity == null || i.rarity == rarity) && (brand == null || i.brand == brand));

        /// <summary>Best first: rarity, then level, then slot and brand, then id (stable across refreshes).</summary>
        public static List<GearItem> Sorted(IEnumerable<GearItem> items, Sort by)
        {
            var list = items.ToList();
            list.Sort((a, b) =>
            {
                int c = by switch
                {
                    Sort.Level => b.level.CompareTo(a.level),
                    Sort.Slot => a.slot.CompareTo(b.slot),
                    Sort.Brand => a.brand.CompareTo(b.brand),
                    _ => b.rarity.CompareTo(a.rarity),
                };
                if (c == 0) c = b.rarity.CompareTo(a.rarity);
                if (c == 0) c = b.level.CompareTo(a.level);
                if (c == 0) c = a.slot.CompareTo(b.slot);
                if (c == 0) c = a.id.CompareTo(b.id);
                return c;
            });
            return list;
        }

        public static string SortName(Sort by) => Strings.Get("kit.sort." + by.ToString().ToLowerInvariant());
    }
}
