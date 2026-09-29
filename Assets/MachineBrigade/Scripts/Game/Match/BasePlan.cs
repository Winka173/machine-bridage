using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 14 G: where a camp's hardpoint stands, named the same way on every map, so one loadout can be
    /// laid out once and fit all twenty camps. Worked out from the camp's own geometry (the HQ, the way it
    /// faces the enemy, each slot's distance and bearing from it): <see cref="SlotPlaces"/>.
    /// </summary>
    public enum SlotPlace
    {
        /// <summary>The front slots furthest out, facing the enemy's way in (cổng).</summary>
        Gate,

        /// <summary>The rest of the outer ring: the flanks (vòng ngoài).</summary>
        Outer,

        /// <summary>Between the outer ring and the HQ (vòng trong).</summary>
        Inner,

        /// <summary>Close round the HQ (cạnh HQ).</summary>
        HqSide,

        /// <summary>Behind the HQ, away from the front (phía sau).</summary>
        Rear,

        /// <summary>A utility module's hardpoint (tiện ích).</summary>
        Utility,

        // Prompt 17 B.5: a long battlefield's layered base (its hardpoints carry these in the map data).

        /// <summary>Behind the outer wall's gates (cổng ngoài).</summary>
        OuterGate,

        /// <summary>Along the outer wall, by its sally ports (tường ngoài).</summary>
        OuterWall,

        /// <summary>The yard between the two walls (sân trong).</summary>
        Yard,

        /// <summary>Behind the inner wall, the keep's (tường trong).</summary>
        InnerWall,
    }

    /// <summary>A place in a loadout by position: the place, the slot's size, and which of the camp's slots of that place and size (left to right).</summary>
    public readonly struct PlaceKey : IEquatable<PlaceKey>
    {
        public PlaceKey(SlotPlace place, SlotSize size, int ordinal)
        {
            Place = place;
            Size = size;
            Ordinal = ordinal;
        }

        public SlotPlace Place { get; }
        public SlotSize Size { get; }
        public int Ordinal { get; }

        public bool Equals(PlaceKey other) => Place == other.Place && Size == other.Size && Ordinal == other.Ordinal;
        public override bool Equals(object obj) => obj is PlaceKey other && Equals(other);
        public override int GetHashCode() => ((int)Place * 5 + (int)Size) * 97 + Ordinal;
        public override string ToString() => $"{Place} {Size} {Ordinal}";
    }

    /// <summary>
    /// The places of a camp's hardpoints. A slot's distance from the HQ is measured against the camp's
    /// furthest tower slot, its bearing against the way the HQ faces: close to the HQ it is beside the HQ;
    /// more than 110 degrees round, at the rear; out at the edge and within 40 degrees of the front, at the
    /// gate; out at the edge otherwise, on the outer ring; the rest on the inner ring. Slots of the same place
    /// and size are numbered from left to right as the camp faces the enemy.
    /// </summary>
    public static class SlotPlaces
    {
        /// <summary>A slot this close to the HQ (a share of the furthest tower slot's distance) is beside it.</summary>
        public const float HqSide = 0.4f;

        /// <summary>A slot this far out (a share of the furthest) is on the outer ring or at the gate.</summary>
        public const float OuterRing = 0.7f;

        /// <summary>A slot this close to the front (degrees off the HQ's facing) out on the ring is at the gate.</summary>
        public const float GateCone = 40f;

        /// <summary>A slot this far round (degrees off the facing) is at the rear.</summary>
        public const float RearCone = 110f;

        /// <summary>Places only a layered base has (prompt 17): a camp ignores a plan's towers for them, and the other way round.</summary>
        public static bool LongOnly(SlotPlace place) => place is SlotPlace.OuterGate or SlotPlace.OuterWall or SlotPlace.Yard or SlotPlace.InnerWall;

        /// <summary>Places only a camp has.</summary>
        public static bool CampOnly(SlotPlace place) => place is SlotPlace.Gate or SlotPlace.Outer or SlotPlace.Inner or SlotPlace.Rear;

        /// <summary>A layered base's place from the map data's label (null: work it out as on a camp).</summary>
        public static SlotPlace? FromLabel(string label) => label switch
        {
            "outer_gate" => SlotPlace.OuterGate,
            "outer_wall" => SlotPlace.OuterWall,
            "yard" => SlotPlace.Yard,
            "inner_wall" => SlotPlace.InnerWall,
            "hq_side" => SlotPlace.HqSide,
            _ => null,
        };

        /// <summary>Every hardpoint's place key, in the camp's slot order.</summary>
        public static PlaceKey[] Keys(BaseSiteDef site)
        {
            var n = site.Slots.Count;
            var places = new SlotPlace[n];
            var bearings = new float[n];
            var front = new Vector2(MathF.Sin(site.Heading), MathF.Cos(site.Heading));
            var furthest = 1f;
            foreach (var s in site.Slots)
                if (s.Kind == HardpointKind.Tower) furthest = MathF.Max(furthest, Vector2.Distance(s.Position, site.Hq));
            for (var i = 0; i < n; i++)
            {
                var s = site.Slots[i];
                var offset = s.Position - site.Hq;
                var distance = offset.Length();
                var along = Vector2.Dot(offset, front);
                var across = offset.X * front.Y - offset.Y * front.X;
                var angle = distance < 0.01f ? 0f : MathF.Acos(Math.Clamp(along / distance, -1f, 1f)) * 180f / MathF.PI;
                bearings[i] = MathF.Atan2(across, along);
                var r = distance / furthest;
                // A layered base names its places in the map data (B.5).
                if (s.Kind != HardpointKind.Utility && s.Place != null && FromLabel(s.Place) is { } labelled)
                {
                    places[i] = labelled;
                    continue;
                }
                places[i] = s.Kind == HardpointKind.Utility ? SlotPlace.Utility
                    : r < HqSide ? SlotPlace.HqSide
                    : angle > RearCone ? SlotPlace.Rear
                    : r >= OuterRing && angle <= GateCone ? SlotPlace.Gate
                    : r >= OuterRing ? SlotPlace.Outer
                    : SlotPlace.Inner;
            }
            var keys = new PlaceKey[n];
            for (var i = 0; i < n; i++)
            {
                var ordinal = 0;
                for (var j = 0; j < n; j++)
                {
                    if (j == i || places[j] != places[i] || site.Slots[j].Class != site.Slots[i].Class) continue;
                    if (bearings[j] < bearings[i] || (bearings[j] == bearings[i] && j < i)) ordinal++;
                }
                keys[i] = new PlaceKey(places[i], site.Slots[i].Class, ordinal);
            }
            return keys;
        }

        /// <summary>How far apart two places are, for putting a tower whose place a map lacks into the nearest one.</summary>
        internal static int Distance(SlotPlace a, SlotPlace b) => Math.Abs(Rank(a) - Rank(b));

        private static int Rank(SlotPlace place) => place switch
        {
            SlotPlace.OuterGate => -1,
            SlotPlace.OuterWall => 0,
            SlotPlace.Gate => 0,
            SlotPlace.Outer => 1,
            SlotPlace.Yard => 1,
            SlotPlace.Inner => 2,
            SlotPlace.InnerWall => 2,
            SlotPlace.HqSide => 3,
            SlotPlace.Rear => 4,
            _ => 10,
        };

        /// <summary>
        /// The camp place a layered base's place borrows its towers from while the plan has none of its own for the
        /// long battlefields: the gate's for the outer gate, the outer ring's for the outer wall, the inner ring's for the
        /// yard and the inner wall (prompt 17 B.5).
        /// </summary>
        internal static SlotPlace Counterpart(SlotPlace place) => place switch
        {
            SlotPlace.OuterGate => SlotPlace.Gate,
            SlotPlace.OuterWall => SlotPlace.Outer,
            SlotPlace.Yard => SlotPlace.Inner,
            SlotPlace.InnerWall => SlotPlace.Inner,
            _ => place,
        };
    }

    /// <summary>
    /// Prompt 14 G: one base loadout for every map. The player lays out the towers (and modules) by place;
    /// each map takes the tower of each of its slots from the slot's place key (<see cref="Resolve"/>). A tower
    /// whose place a map does not have goes into the nearest free slot of the same size there, and the map is
    /// marked (a warning dot on the map picker); a map can also be set up on its own (<see cref="Custom"/>:
    /// "Chỉnh riêng cho map này"), in its slots' order like the old loadout. The outpost's two towers are the
    /// plan's too. The HQ level and the towers' branches are the profile's, not a plan's.
    /// </summary>
    public sealed class BasePlan
    {
        /// <summary>The tower or module wanted at each place (a place missing: nothing there).</summary>
        public Dictionary<PlaceKey, string> Places { get; } = new();

        /// <summary>The outpost's small slot's tower, then its medium slot's.</summary>
        public List<string> Outpost { get; } = new(BaseLayout.DefaultOutpost);

        /// <summary>Maps set up on their own: the map id and its loadout, in that map's slot order.</summary>
        public Dictionary<string, BaseLoadout> Custom { get; } = new();

        public BasePlan Clone()
        {
            var copy = new BasePlan();
            foreach (var (k, v) in Places) copy.Places[k] = v;
            copy.Outpost.Clear();
            copy.Outpost.AddRange(Outpost);
            foreach (var (k, v) in Custom) copy.Custom[k] = v.Clone();
            return copy;
        }

        /// <summary>
        /// The loadout a map fights with: its own when it is set up on its own, else the plan laid on its camp. The
        /// lists are in the camp's slot order (the i-th small slot takes Small[i]), as the simulation raises them.
        /// </summary>
        public BaseLoadout Resolve(string mapId, BaseSiteDef site, int hqLevel)
        {
            if (mapId != null && Custom.TryGetValue(mapId, out var own))
            {
                var loadout = own.Clone();
                loadout.HqLevel = hqLevel;
                loadout.Layered = site != null && site.Layered;
                loadout.Outpost.Clear();
                loadout.Outpost.AddRange(Outpost);
                return loadout;
            }
            var laid = FromAssignment(site, Assign(site, out _), hqLevel);
            laid.Outpost.Clear();
            laid.Outpost.AddRange(Outpost);
            return laid;
        }

        /// <summary>Whether the plan does not fit this map exactly (a tower moved to the nearest slot, or left out): its warning dot.</summary>
        public bool Misfits(string mapId, BaseSiteDef site)
        {
            if (site == null || (mapId != null && Custom.ContainsKey(mapId))) return false;
            Assign(site, out var misfit);
            return misfit;
        }

        /// <summary>
        /// The plan on a camp: each hardpoint's tower (null: empty), in slot order. A slot takes its own place's
        /// tower; the plan's towers left over (the map has fewer slots of that place and size) go, in place order,
        /// into the nearest free slot of the same size and kind (the nearest place first, then the nearest in line).
        /// </summary>
        public string[] Assign(BaseSiteDef site, out bool misfit)
        {
            misfit = false;
            var keys = SlotPlaces.Keys(site);
            var towers = new string[keys.Length];
            var used = new HashSet<PlaceKey>();
            var places = site.Layered && !HasLong ? Borrowed(site, keys) : Places;
            for (var i = 0; i < keys.Length; i++)
                if (places.TryGetValue(keys[i], out var id) && !string.IsNullOrEmpty(id))
                {
                    towers[i] = id;
                    used.Add(keys[i]);
                }
            var left = new List<(PlaceKey key, string id)>();
            // (A camp leaves the long battlefields' places alone, and a layered base every place but its own: B.5.)
            foreach (var (key, id) in places)
                if (!string.IsNullOrEmpty(id) && !used.Contains(key) && SlotPlaces.LongOnly(key.Place) == site.Layered) left.Add((key, id));
            left.Sort((a, b) => a.key.Place != b.key.Place ? a.key.Place.CompareTo(b.key.Place)
                : a.key.Size != b.key.Size ? a.key.Size.CompareTo(b.key.Size) : a.key.Ordinal.CompareTo(b.key.Ordinal));
            var ownKeyed = new HashSet<PlaceKey>(places.Keys);
            foreach (var (key, id) in left)
            {
                misfit = true;
                var best = -1;
                var bestScore = int.MaxValue;
                for (var i = 0; i < keys.Length; i++)
                {
                    if (towers[i] != null || keys[i].Size != key.Size || (keys[i].Place == SlotPlace.Utility) != (key.Place == SlotPlace.Utility)) continue;
                    // A slot whose own place the plan speaks for is kept for that (even if empty on purpose).
                    if (ownKeyed.Contains(keys[i])) continue;
                    var score = SlotPlaces.Distance(keys[i].Place, key.Place) * 100 + Math.Abs(keys[i].Ordinal - key.Ordinal) * 10 + (i > 9 ? 9 : i);
                    if (score < bestScore)
                    {
                        bestScore = score;
                        best = i;
                    }
                }
                if (best >= 0) towers[best] = id;
            }
            return towers;
        }

        /// <summary>Whether the plan has towers of its own for a layered base's places (else it borrows the camps', <see cref="Borrowed"/>).</summary>
        public bool HasLong
        {
            get
            {
                foreach (var key in Places.Keys)
                    if (SlotPlaces.LongOnly(key.Place)) return true;
                return false;
            }
        }

        /// <summary>
        /// The plan as a layered base reads it while the player has laid none of the long battlefields' places out
        /// (prompt 17 B.5): each long place takes the towers of its camp counterpart (<see cref="SlotPlaces.Counterpart"/>)
        /// of the same size, in order and over again, then any of that size; the places both kinds share (beside the HQ,
        /// the utility slots) are the plan's own.
        /// </summary>
        internal Dictionary<PlaceKey, string> Borrowed(BaseSiteDef site, PlaceKey[] keys)
        {
            var result = new Dictionary<PlaceKey, string>();
            foreach (var (k, v) in Places)
                if (!SlotPlaces.LongOnly(k.Place)) result[k] = v;
            List<string> Towers(Func<PlaceKey, bool> which)
            {
                var list = new List<(PlaceKey key, string id)>();
                foreach (var (k, v) in Places)
                    if (!string.IsNullOrEmpty(v) && which(k)) list.Add((k, v));
                list.Sort((a, b) => SlotPlaces.Distance(a.key.Place, SlotPlace.Gate) != SlotPlaces.Distance(b.key.Place, SlotPlace.Gate)
                    ? SlotPlaces.Distance(a.key.Place, SlotPlace.Gate).CompareTo(SlotPlaces.Distance(b.key.Place, SlotPlace.Gate))
                    : a.key.Ordinal.CompareTo(b.key.Ordinal));
                return list.ConvertAll(e => e.id);
            }
            var seen = new Dictionary<(SlotPlace, SlotSize), int>();
            foreach (var key in keys)
            {
                if (!SlotPlaces.LongOnly(key.Place)) continue;
                var from = SlotPlaces.Counterpart(key.Place);
                var own = Towers(k => k.Place == from && k.Size == key.Size);
                if (own.Count == 0) own = Towers(k => SlotPlaces.CampOnly(k.Place) && k.Size == key.Size);
                if (own.Count == 0) continue;
                seen.TryGetValue((key.Place, key.Size), out var n);
                seen[(key.Place, key.Size)] = n + 1;
                result[key] = own[n % own.Count];
            }
            return result;
        }

        /// <summary>Lays the borrowed towers (<see cref="Borrowed"/>) into the plan as its own long places: the first edit on a layered base.</summary>
        private void OwnLong(BaseSiteDef site)
        {
            if (!site.Layered || HasLong) return;
            var keys = SlotPlaces.Keys(site);
            foreach (var (k, v) in Borrowed(site, keys))
                if (SlotPlaces.LongOnly(k.Place)) Places[k] = v;
        }

        /// <summary>A camp's towers (in slot order) as a loadout's sized lists, in the camp's slot order.</summary>
        public static BaseLoadout FromAssignment(BaseSiteDef site, IReadOnlyList<string> towers, int hqLevel)
        {
            var loadout = new BaseLoadout { HqLevel = hqLevel, Layered = site.Layered };
            for (var i = 0; i < site.Slots.Count; i++)
            {
                var slot = site.Slots[i];
                var list = slot.Kind == HardpointKind.Utility ? loadout.Utilities : loadout.Of(slot.Class);
                list.Add(towers[i] ?? BaseLoadout.Empty);
            }
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize))) TrimGaps(loadout.Of(size));
            TrimGaps(loadout.Utilities);
            return loadout;
        }

        /// <summary>Drops the empty entries at the end of a list (they mean nothing there).</summary>
        private static void TrimGaps(List<string> list)
        {
            while (list.Count > 0 && string.IsNullOrEmpty(list[list.Count - 1])) list.RemoveAt(list.Count - 1);
        }

        /// <summary>A loadout's towers on a camp (the i-th small slot takes Small[i]), in slot order.</summary>
        public static string[] ToAssignment(BaseSiteDef site, BaseLoadout loadout)
        {
            var towers = new string[site.Slots.Count];
            var seen = new int[3];
            var utility = 0;
            for (var i = 0; i < site.Slots.Count; i++)
            {
                var slot = site.Slots[i];
                var list = slot.Kind == HardpointKind.Utility ? loadout.Utilities : loadout.Of(slot.Class);
                var k = slot.Kind == HardpointKind.Utility ? utility++ : seen[(int)slot.Class]++;
                towers[i] = k < list.Count && !string.IsNullOrEmpty(list[k]) ? list[k] : null;
            }
            return towers;
        }

        /// <summary>What stands at a hardpoint of a map (null: empty), the map's own set-up first.</summary>
        public string At(string mapId, BaseSiteDef site, int hardpoint)
        {
            if (mapId != null && Custom.TryGetValue(mapId, out var own)) return ToAssignment(site, own)[hardpoint];
            return Assign(site, out _)[hardpoint];
        }

        /// <summary>
        /// Puts a card at a hardpoint of a map (null clears it): into the map's own set-up when it has one, else
        /// into the plan at the slot's place, for every map.
        /// </summary>
        public void Set(string mapId, BaseSiteDef site, int hardpoint, string id)
        {
            if (mapId != null && Custom.TryGetValue(mapId, out var own))
            {
                var towers = ToAssignment(site, own);
                towers[hardpoint] = string.IsNullOrEmpty(id) ? null : id;
                var level = own.HqLevel;
                Custom[mapId] = FromAssignment(site, towers, level);
                return;
            }
            OwnLong(site);
            var key = SlotPlaces.Keys(site)[hardpoint];
            // A tower the plan had put here from a place this map lacks moves off with the edit: the slot now speaks for its own place.
            if (string.IsNullOrEmpty(id)) Places.Remove(key);
            else Places[key] = id;
        }

        /// <summary>Sets a map up on its own (a copy of what it has now), or back on the plan.</summary>
        public void SetCustom(string mapId, BaseSiteDef site, bool own, int hqLevel)
        {
            if (own)
            {
                if (!Custom.ContainsKey(mapId)) Custom[mapId] = FromAssignment(site, Assign(site, out _), hqLevel);
            }
            else Custom.Remove(mapId);
        }

        /// <summary>Lays the plan out from a camp's towers (in slot order): every slot's place takes its tower (Auto-arrange, the migration).</summary>
        public void FromCamp(BaseSiteDef site, IReadOnlyList<string> towers)
        {
            var keys = SlotPlaces.Keys(site);
            // Laying out one kind of base keeps the other kind's own places (prompt 17 B.5): a camp's Auto-arrange
            // keeps the long battlefields' places, a layered base's keeps the camps'.
            if (site.Layered)
            {
                foreach (var k in new List<PlaceKey>(Places.Keys))
                    if (SlotPlaces.LongOnly(k.Place)) Places.Remove(k);
                foreach (var k in keys) Places.Remove(k);
            }
            else
                foreach (var k in new List<PlaceKey>(Places.Keys))
                    if (!SlotPlaces.LongOnly(k.Place)) Places.Remove(k);
            for (var i = 0; i < keys.Length; i++)
                if (!string.IsNullOrEmpty(towers[i])) Places[keys[i]] = towers[i];
        }
    }
}
