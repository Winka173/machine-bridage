using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 14 G: the player's base as three saved plans (<see cref="BasePlan"/>: one loadout by place for every
    /// map, maps set up on their own, the outpost's towers), one of them in use, switched on the Base screen and
    /// in the match setup. Saved in the profile as <see cref="PlanData"/>; the old loadout (one set of sized
    /// lists, version 2) becomes the first plan (see <see cref="MigrateToPlans"/>).
    /// </summary>
    public static partial class PlayerProfile
    {
        /// <summary>How many base plans the player keeps.</summary>
        public const int BasePlanCount = 3;

        [Serializable]
        private sealed class PlanPlace
        {
            public int place;
            public int size;
            public int ordinal;
            public string tower;
        }

        [Serializable]
        private sealed class PlanMap
        {
            public string map;
            public List<string> small = new();
            public List<string> medium = new();
            public List<string> large = new();
            public List<string> utilities = new();
        }

        [Serializable]
        private sealed class PlanData
        {
            public List<PlanPlace> places = new();
            public List<string> outpost = new();
            public List<PlanMap> custom = new();
        }

        private static readonly BasePlan[] Plans = new BasePlan[BasePlanCount];
        private static Data _plansOf;

        /// <summary>The plan in use (0 to <see cref="BasePlanCount"/> - 1).</summary>
        public static int ActiveBasePlan
        {
            get => Mathf.Clamp(D.basePlan, 0, BasePlanCount - 1);
            set
            {
                D.basePlan = Mathf.Clamp(value, 0, BasePlanCount - 1);
                Save();
            }
        }

        /// <summary>A saved plan, live: change it, then <see cref="SaveBasePlans"/>.</summary>
        public static BasePlan BasePlanAt(int index)
        {
            if (_plansOf != D)
            {
                _plansOf = D;
                for (var i = 0; i < BasePlanCount; i++) Plans[i] = null;
            }
            index = Mathf.Clamp(index, 0, BasePlanCount - 1);
            if (Plans[index] != null) return Plans[index];
            while (D.basePlans.Count < BasePlanCount) D.basePlans.Add(D.basePlans.Count > 0 ? Copy(D.basePlans[0]) : new PlanData());
            return Plans[index] = FromData(D.basePlans[index]);
        }

        /// <summary>The plan in use, live.</summary>
        public static BasePlan ActivePlan => BasePlanAt(ActiveBasePlan);

        /// <summary>Writes every plan back to the profile and saves it (the Base screen saves on every change).</summary>
        public static void SaveBasePlans()
        {
            for (var i = 0; i < BasePlanCount; i++)
                if (Plans[i] != null && _plansOf == D) D.basePlans[i] = ToData(Plans[i]);
            D.baseEdited = true;
            Save();
        }

        /// <summary>
        /// The base the player takes onto a map (its id with or without the mode's suffix): the plan in use laid on
        /// the map's camp (or the map's own set-up), at the HQ level the campaign has opened, a card not unlocked yet
        /// leaving its slot empty, each tower as its chosen branch.
        /// </summary>
        public static BaseLoadout BaseLoadoutFor(string mapId) => BaseLoadoutOn(BaseSites.PlanKey(mapId), BaseSites.CampOf(mapId));

        /// <summary>The base on a match's own camp for a side (a siege's attacker camp, a mission's), the plan laid on that camp.</summary>
        public static BaseLoadout BaseLoadoutOn(MapDefinition map, int team)
        {
            var site = map?.BaseOf(team);
            return BaseLoadoutOn(BaseSites.MapKey(map?.Id), site ?? BaseSites.CampOf(BaseSites.MapKey(map?.Id)));
        }

        /// <summary>
        /// Prompt 17 B.5: the player's base on a long battlefield's layered base (Defend, Endless): the plan laid on its
        /// layered hardpoints (or that map's own set-up), the long table's slots open at the player's HQ level.
        /// </summary>
        public static BaseLoadout BaseLoadoutOnLayered(MapDefinition map)
        {
            var site = map?.Fortress?.Site(0);
            return site == null ? BaseLoadout : BaseLoadoutOn(BaseSites.PlanKey(map.Id), site);
        }

        private static BaseLoadout BaseLoadoutOn(string mapKey, BaseSiteDef site)
        {
            var level = Mathf.Clamp(Campaign.HqLevelCap, 1, Campaign.MaxHqLevel);
            var plan = ActivePlan;
            var resolved = site != null ? plan.Resolve(mapKey, site, level) : FallbackLoadout(plan, level);
            // A tower or module not unlocked yet leaves its slot empty (every card is open in a test build).
            static void Owned(List<string> ids)
            {
                for (var i = 0; i < ids.Count; i++)
                    if (!string.IsNullOrEmpty(ids[i]) && !IsUnlocked(ids[i])) ids[i] = BaseLoadout.Empty;
            }
            Owned(resolved.Small);
            Owned(resolved.Medium);
            Owned(resolved.Large);
            resolved.Utilities.RemoveAll(id => !string.IsNullOrEmpty(id) && !IsUnlocked(id));
            foreach (var id in resolved.Towers)
                if (TowerBranch(id) is { } branch) resolved.Branches[id] = branch;
            // A module's rank-7 branch too (the landing pad's, prompt 13 F.1).
            foreach (var id in resolved.Utilities)
                if (!string.IsNullOrEmpty(id) && TowerBranch(id) is { } branch) resolved.Branches[id] = branch;
            return resolved;
        }

        /// <summary>Without a camp to lay it on (a map with none): the plan's towers by size, front places first.</summary>
        private static BaseLoadout FallbackLoadout(BasePlan plan, int level)
        {
            var loadout = new BaseLoadout { HqLevel = level };
            var entries = new List<(PlaceKey key, string id)>();
            foreach (var (k, v) in plan.Places) entries.Add((k, v));
            entries.Sort((a, b) => a.key.Place != b.key.Place ? a.key.Place.CompareTo(b.key.Place) : a.key.Ordinal.CompareTo(b.key.Ordinal));
            foreach (var (key, id) in entries)
                (key.Place == SlotPlace.Utility ? loadout.Utilities : loadout.Of(key.Size)).Add(id);
            loadout.Outpost.Clear();
            loadout.Outpost.AddRange(plan.Outpost);
            return loadout;
        }

        /// <summary>
        /// The base the player takes into battle on the map chosen now (see <see cref="BaseLoadoutFor"/>). Setting it
        /// lays the loadout out as the plan in use, by the places of the current map's camp (tests, old callers).
        /// </summary>
        public static BaseLoadout BaseLoadout
        {
            get => BaseLoadoutFor(MatchSettings.CurrentMap.Id);
            set
            {
                var id = MatchSettings.CurrentMap.Id;
                var site = BaseSites.CampOf(id);
                var plan = ActivePlan;
                plan.Custom.Remove(BaseSites.MapKey(id));
                if (site != null) plan.FromCamp(site, BasePlan.ToAssignment(site, value));
                plan.Outpost.Clear();
                plan.Outpost.AddRange(BaseLayout.ForSaving(value, GameContent.LoadCatalog()).Outpost);
                D.baseLevel = value.HqLevel;
                SaveBasePlans();
            }
        }

        // ------------------------------------------------------------------ the migration (version 2 to 3)

        /// <summary>3: the base is in plans (see <see cref="MigrateToPlans"/>).</summary>
        internal const int PlansVersion = 3;

        /// <summary>
        /// Moves the one sized loadout of version 2 into the plans, once: the first plan is laid out from the map
        /// that holds the most of its towers (the first such map in the list on a tie), and every other map on which
        /// the plan would put a different tower anywhere than the old loadout did keeps the old loadout as its own
        /// set-up, so nothing changes for the player. A profile that never set its base up starts from the default
        /// towers, with no map of its own. The other two plans start as copies of the first.
        /// </summary>
        private static void MigrateToPlans(Data d)
        {
            if (d.baseVersion >= PlansVersion && d.basePlans.Count > 0) return;
            var edited = d.baseEdited || d.baseSmall.Count + d.baseMedium.Count + d.baseLarge.Count > 0;
            var old = new BaseLoadout();
            old.Small.AddRange(edited ? d.baseSmall : new List<string>(DefaultSmall));
            old.Medium.AddRange(edited ? d.baseMedium : new List<string>(DefaultMedium));
            old.Large.AddRange(edited ? d.baseLarge : new List<string>(DefaultLarge));
            old.Utilities.AddRange(d.baseUtilities);
            var plan = PlanFromLoadout(old, edited);
            if (d.baseOutpost.Count > 0)
            {
                plan.Outpost.Clear();
                plan.Outpost.AddRange(d.baseOutpost);
            }
            var data = ToData(plan);
            d.basePlans = new List<PlanData> { data, Copy(data), Copy(data) };
            d.basePlan = 0;
            d.baseVersion = PlansVersion;
        }

        /// <summary>A plan from an old loadout (see <see cref="MigrateToPlans"/>); <paramref name="keepEveryMap"/>: maps it would change set up on their own.</summary>
        internal static BasePlan PlanFromLoadout(BaseLoadout old, bool keepEveryMap)
        {
            var plan = new BasePlan();
            string best = null;
            BaseSiteDef bestSite = null;
            var most = -1;
            foreach (var map in MatchSettings.AllMaps)
            {
                var site = BaseSites.CampOf(map.Id);
                if (site == null) continue;
                var count = 0;
                foreach (var id in BasePlan.ToAssignment(site, old))
                    if (id != null) count++;
                if (count <= most) continue;
                most = count;
                best = map.Id;
                bestSite = site;
            }
            if (bestSite == null) return plan;
            plan.FromCamp(bestSite, BasePlan.ToAssignment(bestSite, old));
            if (!keepEveryMap) return plan;
            foreach (var map in MatchSettings.AllMaps)
            {
                if (map.Id == best) continue;
                var site = BaseSites.CampOf(map.Id);
                if (site == null) continue;
                var was = BasePlan.ToAssignment(site, old);
                var now = plan.Assign(site, out _);
                var same = true;
                for (var i = 0; i < was.Length; i++) same &= was[i] == now[i];
                if (!same) plan.Custom[map.Id] = BasePlan.FromAssignment(site, was, 1);
            }
            return plan;
        }

        // ------------------------------------------------------------------ saved form

        private static BasePlan FromData(PlanData data)
        {
            var plan = new BasePlan();
            foreach (var p in data.places)
                if (!string.IsNullOrEmpty(p.tower)) plan.Places[new PlaceKey((SlotPlace)p.place, (SlotSize)p.size, p.ordinal)] = p.tower;
            if (data.outpost.Count > 0)
            {
                plan.Outpost.Clear();
                plan.Outpost.AddRange(data.outpost);
            }
            foreach (var m in data.custom)
            {
                if (string.IsNullOrEmpty(m.map)) continue;
                var loadout = new BaseLoadout();
                loadout.Small.AddRange(m.small);
                loadout.Medium.AddRange(m.medium);
                loadout.Large.AddRange(m.large);
                loadout.Utilities.AddRange(m.utilities);
                plan.Custom[m.map] = loadout;
            }
            return plan;
        }

        private static PlanData ToData(BasePlan plan)
        {
            var data = new PlanData();
            var keys = new List<PlaceKey>(plan.Places.Keys);
            keys.Sort((a, b) => a.Place != b.Place ? a.Place.CompareTo(b.Place) : a.Size != b.Size ? a.Size.CompareTo(b.Size) : a.Ordinal.CompareTo(b.Ordinal));
            foreach (var k in keys)
                data.places.Add(new PlanPlace { place = (int)k.Place, size = (int)k.Size, ordinal = k.Ordinal, tower = plan.Places[k] });
            data.outpost.AddRange(plan.Outpost);
            var maps = new List<string>(plan.Custom.Keys);
            maps.Sort(string.CompareOrdinal);
            foreach (var id in maps)
            {
                var l = plan.Custom[id];
                data.custom.Add(new PlanMap
                {
                    map = id, small = new List<string>(l.Small), medium = new List<string>(l.Medium), large = new List<string>(l.Large),
                    utilities = new List<string>(l.Utilities),
                });
            }
            return data;
        }

        private static PlanData Copy(PlanData data) => JsonUtility.FromJson<PlanData>(JsonUtility.ToJson(data));
    }

    /// <summary>Each map's player camp (team 0 of its Conquest variant), loaded once: what the plans are laid on.</summary>
    public static class BaseSites
    {
        private static readonly Dictionary<string, BaseSiteDef> Camps = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            Camps.Clear();
            Layered.Clear();
        }

        /// <summary>A long battlefield's file and plan suffix (prompt 17): "ashfield_long".</summary>
        public const string LongSuffix = "_long";

        /// <summary>A map's id without the mode's suffix ("ashfield_conquest" and "ashfield_long" are "ashfield").</summary>
        public static string MapKey(string mapId)
        {
            if (string.IsNullOrEmpty(mapId)) return mapId;
            foreach (var suffix in new[] { "_conquest", "_sandbox", "_siege", LongSuffix })
                if (mapId.EndsWith(suffix, StringComparison.Ordinal)) return mapId.Substring(0, mapId.Length - suffix.Length);
            return mapId;
        }

        /// <summary>Whether an id names a long battlefield ("ashfield_long").</summary>
        public static bool IsLong(string mapId) => !string.IsNullOrEmpty(mapId) && mapId.EndsWith(LongSuffix, StringComparison.Ordinal);

        /// <summary>
        /// The key a plan's own set-up and the Base screen use for a map: the map's key ("ashfield"), and for a long
        /// battlefield's layered base the long one ("ashfield_long"): the two are different bases.
        /// </summary>
        public static string PlanKey(string mapId) => IsLong(mapId) ? MapKey(mapId) + LongSuffix : MapKey(mapId);

        /// <summary>Whether a map has a long battlefield (a layered base for Siege, Defend, Endless and the weekly fortress).</summary>
        public static bool HasLong(string mapId) => LongOf(mapId) != null;

        private static readonly Dictionary<string, BaseSiteDef> Layered = new();

        /// <summary>A map's long battlefield's layered base as a camp (prompt 17 B.5; null when it has none).</summary>
        public static BaseSiteDef LongOf(string mapId)
        {
            var key = MapKey(mapId);
            if (string.IsNullOrEmpty(key)) return null;
            if (Layered.TryGetValue(key, out var site)) return site;
            try
            {
                site = Resources.Load<TextAsset>("Data/maps/" + key + LongSuffix) != null ? GameContent.LoadMap(key + LongSuffix)?.Fortress?.Site(0) : null;
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[BaseSites] No long battlefield for {key}: {e.Message}");
                site = null;
            }
            Layered[key] = site;
            return site;
        }

        /// <summary>The player's camp on a map (null when it has none); on a long battlefield's id, its layered base.</summary>
        public static BaseSiteDef CampOf(string mapId)
        {
            if (IsLong(mapId)) return LongOf(mapId);
            var key = MapKey(mapId);
            if (string.IsNullOrEmpty(key)) return null;
            if (Camps.TryGetValue(key, out var site)) return site;
            try
            {
                site = GameContent.LoadMap(key + "_conquest")?.BaseOf(0);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[BaseSites] No conquest camp for {key}: {e.Message}");
                site = null;
            }
            Camps[key] = site;
            return site;
        }
    }
}
