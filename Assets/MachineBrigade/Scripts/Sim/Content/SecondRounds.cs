#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 25 G (DECISIONS 25G): the targets a gun loads one of its second rounds for (data "for").</summary>
    [Flags]
    public enum RoundUse
    {
        None = 0,

        /// <summary>Aircraft and drones (anything flying, or on an altitude tier).</summary>
        Air = 1,

        /// <summary>Anything on the ground: vehicles, fixed defences, walls and buildings.</summary>
        Ground = 2,

        /// <summary>A ground vehicle (not a structure) of front armour 2 or more.</summary>
        Armour = 4,

        /// <summary>A ground vehicle (not a structure) of front armour 1 or less.</summary>
        Light = 8,

        /// <summary>A fixed defence, the structure armour class, a wall or a building.</summary>
        Structure = 16,

        /// <summary>A ground vehicle with at least two more of its side inside the round's blast (4 m at least).</summary>
        Cluster = 32,

        /// <summary>Every target.</summary>
        Any = Air | Ground,
    }

    /// <summary>
    /// Prompt 25 G: a gun's second round ("đạn thay thế"): a weapon of its own (its damage type, penetration, damage, blast,
    /// form) that the gun loads for the targets its rule names, keeping its own round for everything else. The gun's
    /// cadence, reach, magazine and speed stay the gun's; only the round's own figures change.
    /// </summary>
    public sealed class SecondRound
    {
        public SecondRound(WeaponDef round, RoundUse use, bool eliteOnly, float switchSeconds)
        {
            Round = round;
            Use = use;
            EliteOnly = eliteOnly;
            SwitchSeconds = switchSeconds;
        }

        public WeaponDef Round { get; }

        /// <summary>What it is loaded for.</summary>
        public RoundUse Use { get; }

        /// <summary>Only an elite or a rank-7 branch carries it (the sheet's "cho bản tinh nhuệ", "cho nhánh hạng 7").</summary>
        public bool EliteOnly { get; }

        /// <summary>Seconds to change to it, from the data ("switch"); 0 takes the gun's (<see cref="WeaponDef.SwitchSeconds"/>).</summary>
        public float SwitchSeconds { get; }

        /// <summary>Whether a vehicle of this definition carries the round (an elite-only round on an elite or a rank-7 branch).</summary>
        public bool CarriedBy(VehicleDef? def) => !EliteOnly || (def != null && (def.Elite || def.BranchOf != null));
    }

    public sealed partial class WeaponDef
    {
        /// <summary>A switch between rounds takes at least this long (the owner's 0.5 s).</summary>
        public const float MinSwitchSeconds = 0.5f;

        /// <summary>A loaded round stays in at least this long, so a gun never flickers between rounds.</summary>
        public const float RoundHoldSeconds = 2f;

        private static readonly IReadOnlyList<SecondRound> NoRounds = System.Array.Empty<SecondRound>();

        /// <summary>Prompt 25 G: the second rounds this gun can load, in the data's order (the first that suits a target wins).</summary>
        public IReadOnlyList<SecondRound> Rounds { get; internal set; } = NoRounds;

        /// <summary>This gun has a second round.</summary>
        public bool HasRounds => Rounds.Count > 0;

        /// <summary>For a second round: the gun it is loaded in (null for a gun's own round).</summary>
        public WeaponDef? RoundOf { get; internal set; }

        /// <summary>The round's kind in the data ("flak", "ap", "he", "guided", "api"; null: the gun's own, see the UI's word for it).</summary>
        public string? RoundKind { get; internal set; }

        /// <summary>
        /// Prompt 25 G: a guided shell (the Excalibur, the Krasnopol; data "guided" on a shell): no scatter, and it comes down on
        /// its target where it is when it lands.
        /// </summary>
        public bool GuidedShell => Projectile == ProjectileKind.Shell && Steered;

        /// <summary>
        /// Prompt 25 G: an air-burst (flak) round of an autocannon: fragmentation, its proximity fuse bursting it by its target
        /// (its blast is the fragments' reach). The view flies it as the flak round and bursts it as flak; the C-RAM's
        /// intercepting rounds are not flak.
        /// </summary>
        public bool Flak => Family == "autocannon" && DamageType == DamageType.Fragmentation && !InterceptOnly;

        /// <summary>
        /// Seconds this gun takes to change rounds: its reload (a magazine gun's magazine change, else the time between
        /// its shots or salvos), at least <see cref="MinSwitchSeconds"/>; a round's own "switch" overrides.
        /// </summary>
        public float SwitchSeconds(SecondRound? to)
        {
            if (to != null && to.SwitchSeconds > 0f) return to.SwitchSeconds;
            var reload = Clip > 0 ? ClipReload : Cooldown;
            return MathF.Max(MinSwitchSeconds, reload);
        }

        /// <summary>The round at an index of the loaded-round state: 0 the gun's own, k its k-th second round.</summary>
        public WeaponDef RoundAt(int index) => index > 0 && index <= Rounds.Count ? Rounds[index - 1].Round : this;

        /// <summary>Whether this gun, with the rounds a vehicle of <paramref name="carrier"/> carries, can hit the layer at all.</summary>
        public bool CanEngage(bool flying, VehicleDef? carrier)
        {
            if (CanTarget(flying)) return true;
            if (InterceptOnly) return false;
            foreach (var r in Rounds)
                if (r.CarriedBy(carrier) && r.Round.CanTarget(flying)) return true;
            return false;
        }

        /// <summary>Every round a vehicle of <paramref name="carrier"/> loads in this gun, its own first.</summary>
        public IEnumerable<WeaponDef> RoundsCarried(VehicleDef? carrier)
        {
            yield return this;
            foreach (var r in Rounds)
                if (r.CarriedBy(carrier)) yield return r.Round;
        }

        /// <summary>
        /// The round a gun loads against a typical unit of a broad class (the effect tables by class, the design document):
        /// the first second round whose rule takes that class, else its own. No elite-only round, no cluster.
        /// </summary>
        public WeaponDef RoundForClass(ArmorClass armor)
        {
            foreach (var r in Rounds)
            {
                if (r.EliteOnly) continue;
                var u = r.Use;
                var fits = armor switch
                {
                    ArmorClass.Air => (u & RoundUse.Air) != 0,
                    ArmorClass.Structure => (u & (RoundUse.Ground | RoundUse.Structure)) != 0,
                    ArmorClass.Heavy => (u & (RoundUse.Ground | RoundUse.Armour)) != 0,
                    _ => (u & (RoundUse.Ground | RoundUse.Light)) != 0,
                };
                if (fits && r.Round.CanTarget(armor == ArmorClass.Air)) return r.Round;
            }
            return this;
        }

        /// <summary>Data "for": the rule's words.</summary>
        internal static RoundUse ParseUse(IEnumerable<string> words, string path)
        {
            var use = RoundUse.None;
            foreach (var w in words)
                use |= w switch
                {
                    "air" => RoundUse.Air,
                    "ground" => RoundUse.Ground,
                    "armour" => RoundUse.Armour,
                    "light" => RoundUse.Light,
                    "structure" => RoundUse.Structure,
                    "cluster" => RoundUse.Cluster,
                    "any" => RoundUse.Any,
                    _ => throw new FormatException($"{path}.for: unknown target '{w}' (air, ground, armour, light, structure, cluster, any)."),
                };
            if (use == RoundUse.None) throw new FormatException($"{path}.for: name what the round is loaded for.");
            return use;
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>Prompt 25 G: the second rounds' own weapon entries ("secondRounds.rounds"), none when the data has none.</summary>
        private static IEnumerable<JsonObject> SecondRoundEntries(JsonObject root)
        {
            if (!root.Has("secondRounds")) yield break;
            var block = root.Object("secondRounds");
            if (!block.Has("rounds")) yield break;
            foreach (var r in block.Array("rounds")) yield return r;
        }

        /// <summary>Prompt 25 G: the second rounds' weapon families ("secondRounds.families"), read with prompt 25 A3's.</summary>
        private static IEnumerable<JsonObject> SecondRoundFamilies(JsonObject root)
        {
            if (!root.Has("secondRounds")) yield break;
            var block = root.Object("secondRounds");
            if (!block.Has("families")) yield break;
            foreach (var f in block.Array("families")) yield return f;
        }

        /// <summary>
        /// A second round inherits its gun's line, but not what makes the gun a gun of several rounds (its own "he" and "air"
        /// links) and not its "roundOf" chain: applied to every entry after its inheritance is resolved.
        /// </summary>
        private static JsonObject StripRoundLinks(JsonObject w) => w.Has("roundOf") ? w.Without("he", "air") : w;

        /// <summary>
        /// Prompt 25 G: every gun's second rounds once all the weapons are read. Prompt 17 D.6's "he" (a structure, a fixed
        /// defence or a light vehicle) and the tower-branch "air" (aircraft) are second rounds too, read first; then the
        /// "secondRounds" block's, in their order.
        /// </summary>
        private static void ResolveSecondRounds(IEnumerable<JsonObject> raw, Dictionary<string, WeaponDef> weapons)
        {
            var lists = new Dictionary<WeaponDef, List<SecondRound>>();
            void Add(WeaponDef gun, SecondRound round)
            {
                if (!lists.TryGetValue(gun, out var list)) lists[gun] = list = new List<SecondRound>();
                if (list.Exists(r => r.Round == round.Round)) return;
                list.Add(round);
                round.Round.RoundOf ??= gun;
            }
            foreach (var gun in weapons.Values)
            {
                if (gun.HeRound is { } he) Add(gun, new SecondRound(he, RoundUse.Light | RoundUse.Structure, false, 0f));
                if (gun.AirRound is { } air) Add(gun, new SecondRound(air, RoundUse.Air, false, 0f));
            }
            foreach (var r in raw)
            {
                if (!r.Has("roundOf")) continue;
                var id = r.String("roundOf");
                if (!weapons.TryGetValue(id, out var gun)) throw new FormatException($"{r.Path}.roundOf: unknown weapon '{id}'.");
                var round = weapons[r.String("id")];
                if (gun == round || gun.RoundOf != null) throw new FormatException($"{r.Path}.roundOf: a gun's own round, not another second round.");
                if (round.Clip > 0 && gun.Clip == 0) throw new FormatException($"{r.Path}: a magazine round in a gun without one.");
                round.RoundKind = r.Has("round") ? r.String("round") : null;
                var use = WeaponDef.ParseUse(r.StringArray("for"), r.Path);
                Add(gun, new SecondRound(round, use, r.Bool("elite", false), Math.Max(0f, r.Float("switch", 0f))));
            }
            foreach (var pair in lists) pair.Key.Rounds = pair.Value;
        }
    }
}
