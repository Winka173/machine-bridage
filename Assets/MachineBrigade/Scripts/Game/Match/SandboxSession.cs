using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 21: the Sandbox as the match runner plays it. The scenario (<see cref="Scenario"/>) is the truth; the
    /// battle is built from it every time the scene loads, so running it, resetting it or running it again from
    /// its seed always starts from the same state (C.6-C.7). While <see cref="Editing"/> the battle stands still and
    /// the editor's changes are mirrored onto the field; <see cref="Run"/> and <see cref="Reset"/> rebuild the scene
    /// from the scenario. Nothing is paid, counted or recorded (A.2): no reward, no daily progress, no items used,
    /// and the battle is tagged "Sandbox" for any telemetry (<see cref="TelemetryTag"/>) so balance data leaves it out.
    /// </summary>
    internal sealed class SandboxSession : ModeSession
    {
        /// <summary>The tag a Sandbox battle carries for telemetry; balance telemetry must drop tagged battles.</summary>
        public const string TelemetryTag = "sandbox";

        /// <summary>The scenario the next Sandbox scene builds (null: the last one, or a new one).</summary>
        public static SandboxScenario Scenario { get; set; }

        /// <summary>The next scene starts running at once (Run, a reset while running) instead of in set-up.</summary>
        public static bool RunOnLoad { get; set; }

        /// <summary>The internal build (the editor, development builds): every unit and tool (A.1).</summary>
        public static bool Internal => (Application.isEditor || Debug.isDebugBuild) && !DebugFlags.Has("-mb-sandbox-player");

        /// <summary>The player version is open: the last chapter switched on is finished (A.2).</summary>
        public static bool Open => Internal || BossHunts.FullOpen;

        /// <summary>The map file the scene was built on (a scenario on another map rebuilds the scene).</summary>
        public static string LoadedMap { get; private set; }

        public SandboxBattle Battle { get; private set; }

        public bool Editing { get; set; }

        public SandboxAccess Access { get; private set; }

        public override HudSpec Hud => new() { Mode = HudMode.Waves, HintKey = "sandbox.place.hint", StartHint = false, Compact = true };
        public override string Kicker => Strings.Get("sandbox.title");
        public override string Subtitle => Strings.Get("sandbox.sub");
        public override string StartToast => Strings.Get("sandbox.noRewards");

        /// <summary>The map a scenario plays on: the flat test range or a battlefield's file.</summary>
        public static MapDefinition LoadMap(SandboxScenario s)
        {
            if (SandboxMaps.IsFlat(s.Map)) return SandboxMaps.Flat();
            try
            {
                return GameContent.LoadMap(s.Map);
            }
            catch (System.Exception)
            {
                s.Map = SandboxMaps.FlatId;
                return SandboxMaps.Flat();
            }
        }

        /// <summary>The weather the scenario asks for (night is the game's night weather).</summary>
        public static WeatherKind WeatherOf(SandboxScenario s) =>
            s.Night ? WeatherKind.Night : System.Enum.TryParse<WeatherKind>(s.Weather, out var w) && w != WeatherKind.Random ? w : WeatherKind.Clear;

        /// <summary>The player's limits (A.2), or none in the internal build.</summary>
        public static SandboxAccess MakeAccess() =>
            Internal ? SandboxAccess.Everything : new SandboxAccess(false, PlayerProfile.IsUnlocked, SandboxProfile.Beaten, Campaign.BossEnabled);

        /// <summary>A fresh scenario: the flat test range, both sides fighting, the player's own deck's supports.</summary>
        public static SandboxScenario NewScenario()
        {
            var s = new SandboxScenario { Name = SandboxText.Format("sandbox.name.default", ("number", SandboxProfile.Slots.Count + 1)) };
            foreach (var side in s.Sides) side.Supports.AddRange(MatchSettings.DeckSupports);
            return s;
        }

        protected override void Build(SimWorld world, int seed)
        {
            Scenario ??= NewScenario();
            Access = MakeAccess();
            LoadedMap = Scenario.Map;
            Editing = !RunOnLoad;
            RunOnLoad = false;
            Battle = new SandboxBattle(Scenario, BoostFor)
            {
                PlayerBase = team => PlayerProfile.BaseLoadoutOn(world.Map, team),
                TraceBuying = Internal,
            };
            Mode = Battle;
            Battle.Setup(world);
        }

        /// <summary>
        /// A unit's rank and equipment as the game's gear rules make them (B.6): none; the suggested set for its
        /// branch (<see cref="SandboxGearKit"/>); or the player's own loadout. A tower's equipment is its tower gear.
        /// </summary>
        internal static VehicleBoost? BoostFor(SandboxUnit unit, VehicleDef def)
        {
            if (unit.Rank <= 1 && unit.Gear == SandboxGear.None) return null;
            if (def.Fort != null)
            {
                var gear = unit.Gear == SandboxGear.Player ? PlayerProfile.TowerGear(def.CardId) : System.Array.Empty<GearItem>();
                return Gear.TowerBoost(unit.Rank, gear, unit.Gear == SandboxGear.Player ? PlayerProfile.BaseBrandCounts() : null);
            }
            IEnumerable<GearItem> loadout = unit.Gear switch
            {
                SandboxGear.Suggested => SandboxGearKit.Suggested(def),
                SandboxGear.Player => PlayerProfile.Loadout(Gear.BranchOf(def)),
                _ => System.Array.Empty<GearItem>(),
            };
            return Gear.Boost(unit.Rank, loadout);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps) =>
            hud.SetStats(world.CountAlive(PlayerTeam), world.CountAlive(EnemyTeam), 0, 0f, fps);

        /// <summary>Never a result card (the Sandbox shows its own statistics) and never a reward.</summary>
        public override MatchOutcome Outcome(SimWorld world, int kills, int losses) => null;
    }

    /// <summary>
    /// The suggested equipment for a branch (B.6): one Epic piece for each vehicle slot, rolled from a seed made of
    /// the unit's id, so it is the same set on every device and in every run.
    /// </summary>
    internal static class SandboxGearKit
    {
        private static readonly Dictionary<string, List<GearItem>> Cache = new();

        public static List<GearItem> Suggested(VehicleDef def)
        {
            if (Cache.TryGetValue(def.Id, out var kit)) return kit;
            kit = new List<GearItem>();
            var branch = Gear.BranchOf(def);
            var mask = Gear.DeckMask(new[] { def.CardId });
            var seed = 17;
            foreach (var ch in def.CardId) seed = unchecked(seed * 31 + ch);
            for (var slot = 0; slot < Gear.NormalSlots; slot++)
            {
                var rng = new System.Random(unchecked(seed * 7 + slot));
                var item = new GearItem { id = -1 - slot, slot = slot, rarity = (int)Rarity.Epic, level = 10, seed = rng.Next(1, int.MaxValue) };
                if ((GearSlot)slot == GearSlot.Special)
                {
                    var module = Gear.PickModule(rng, mask);
                    item.special = (int)module;
                    item.baseType = GearKeys.Module(module);
                }
                else
                {
                    item.baseType = Gear.PickBase((GearSlot)slot, Rarity.Epic, rng, mask)?.Id ?? "";
                    item.brand = 1 + rng.Next(GearCatalog.VehicleBrandCount);
                    Gear.FillSubs(item, rng);
                    Gear.RollTrait(item, rng, mask);
                }
                if (Gear.FitsBranch(item, branch) || Gear.MakeFit(item, branch)) kit.Add(item);
            }
            Cache[def.Id] = kit;
            return kit;
        }
    }

    /// <summary>
    /// What the Sandbox keeps between sessions (PlayerPrefs "mb.sandbox"): the player's saved scenarios (at most
    /// <see cref="MaxSlots"/>, F.7), the bosses they have beaten (A.2: campaign and Boss Hunt), and whether its short
    /// guide has been shown (G.3). Kept apart from the profile: the Sandbox never touches coins, cards or records.
    /// </summary>
    internal static class SandboxProfile
    {
        public const int MaxSlots = 20;
        private const string Key = "mb.sandbox";

        [System.Serializable]
        private sealed class Data
        {
            public List<string> beaten = new();
            public List<string> names = new();
            public List<string> scenarios = new();
            public bool hintSeen;
        }

        private static Data _data;

        private static Data D
        {
            get
            {
                if (_data != null) return _data;
                try
                {
                    _data = JsonUtility.FromJson<Data>(PlayerPrefs.GetString(Key, "{}")) ?? new Data();
                }
                catch (System.Exception)
                {
                    _data = new Data();
                }
                return _data;
            }
        }

        private static void Save()
        {
            PlayerPrefs.SetString(Key, JsonUtility.ToJson(D));
            PlayerPrefs.Save();
        }

        /// <summary>Forgets what was read (tests).</summary>
        internal static void Reload() => _data = null;

        public static bool HintSeen
        {
            get => D.hintSeen;
            set
            {
                D.hintSeen = value;
                Save();
            }
        }

        /// <summary>A boss or mini boss brought down in the campaign or the Boss Hunt (the runner calls it).</summary>
        public static void MarkBeaten(string bossId)
        {
            if (string.IsNullOrEmpty(bossId) || D.beaten.Contains(bossId)) return;
            D.beaten.Add(bossId);
            Save();
        }

        /// <summary>Beaten: recorded, or the boss of a campaign mission already won (before the Sandbox kept a list).</summary>
        public static bool Beaten(string bossId)
        {
            if (D.beaten.Contains(bossId)) return true;
            foreach (var m in Campaign.Everything)
            {
                if (!PlayerProfile.Completed(m.Id)) continue;
                foreach (var b in Campaign.BossesOf(m))
                    if (b.Def == bossId) return true;
            }
            return false;
        }

        public static IReadOnlyList<string> Slots => D.names;

        public static SandboxScenario LoadSlot(int i) => i >= 0 && i < D.scenarios.Count ? SandboxScenario.FromJson(D.scenarios[i]) : null;

        /// <summary>Saves over the slot with the scenario's name, or into a new one; false when all <see cref="MaxSlots"/> are taken.</summary>
        public static bool SaveSlot(SandboxScenario s)
        {
            var i = D.names.IndexOf(s.Name);
            if (i < 0)
            {
                if (D.names.Count >= MaxSlots) return false;
                D.names.Add(s.Name);
                D.scenarios.Add(s.ToJson());
            }
            else D.scenarios[i] = s.ToJson();
            Save();
            return true;
        }

        public static void DeleteSlot(int i)
        {
            if (i < 0 || i >= D.names.Count) return;
            D.names.RemoveAt(i);
            D.scenarios.RemoveAt(i);
            Save();
        }
    }
}
