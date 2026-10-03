using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.AI;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    public enum GameModeKind
    {
        Conquest,
        Survival,
        Deathmatch,
        KingOfTheHill,
        Assault,

        /// <summary>A campaign mission (<see cref="MatchSettings.Mission"/>).</summary>
        Campaign,

        /// <summary>Break into an enemy fortress and level its command HQ.</summary>
        Siege,

        /// <summary>The bosses one after another.</summary>
        BossRush,

        /// <summary>Hold three sectors against the enemy's Breakthrough.</summary>
        Defend,

        /// <summary>This week's fortress: a siege whose broken rings stay broken all week.</summary>
        Weekly,

        /// <summary>The player's fortress against waves that never stop, until the HQ falls.</summary>
        Endless,

        /// <summary>Prompt 21: the Sandbox (a battle set up by hand; no rewards).</summary>
        Sandbox,

        /// <summary>Prompt 32 L7: Showdown, base against base: destroy the enemy HQ (12 minutes, then the HQ lead or sudden death).</summary>
        Showdown,
    }

    public enum WeatherKind
    {
        Clear,
        Overcast,
        Rain,
        Storm,
        Random,
        Snow,
        Sandstorm,
        Fog,
        Night,
    }

    /// <summary>A battlefield the menu offers: data files are Data/maps/{Id}_conquest and {Id}_sandbox.</summary>
    public readonly struct MapInfo
    {
        public MapInfo(string id, string theme, string icon, WeatherKind[] weathers)
        {
            Id = id;
            Theme = theme;
            Icon = icon;
            Weathers = weathers;
        }

        public string Id { get; }

        /// <summary>temperate, desert, snow or harbor: picks ground, scenery and palettes.</summary>
        public string Theme { get; }

        public string Icon { get; }

        /// <summary>The weather Random draws from on this map (first entries most often).</summary>
        public WeatherKind[] Weathers { get; }
    }

    /// <summary>Graphics setting; Auto picks a tier from the device.</summary>
    public enum GraphicsQuality
    {
        Auto,
        Low,
        Medium,
        High,

        /// <summary>The player changed individual options (see <see cref="MatchSettings.Options"/>).</summary>
        Custom,
    }

    public enum LanguageChoice
    {
        Auto,
        English,
        Vietnamese,
    }

    /// <summary>Text size (Settings: Normal / Large, vi Thường / Lớn): which type scale the UI kit uses (Tokens.uss).</summary>
    public enum TextSize
    {
        Normal,
        Large,
    }

    /// <summary>
    /// What the next match should be (chosen in the menu) and the player's settings. The match
    /// choice lives for the session; settings and the deck are saved with PlayerPrefs, so they
    /// survive restarts. Scene reloads read from here, which keeps every match a clean restart.
    /// </summary>
    public static class MatchSettings
    {
        public const int DeckVehicleSlots = 8;
        public const int DeckSupportSlots = 2;

        /// <summary>Saved-deck format: 2 since decks hold 8 vehicles.</summary>
        private const int DeckVersion = 3;

        public static readonly string[] AllVehicles =
        {
            "scout_jeep", "armored_car", "rocket_technical", "light_tank", "main_battle_tank", "heavy_tank",
            "tank_destroyer", "flame_tank", "mortar_carrier", "artillery", "mlrs", "aa_vehicle", "sam_launcher",
            "scout_heli", "attack_helicopter", "gunship_heli", "strike_drone", "attack_jet",
            "ifv", "thermobaric_launcher", "heavy_aa", "titan_tank",
            "heavy_bomber", "stealth_bomber",
            // Play-test 7 (DECISIONS 22P): the AC-130 is an aircraft card again (its support card is gone).
            "sky_gunship",
            "twin_tank", "siege_tank", "heavy_rocket_artillery", "ballistic_launcher",
            // Prompt 17 D: the ATGM carrier, A-10, Ka-52 and sapper were folded into other cards (CardMerges).
            "engineer_vehicle", "ew_jammer", "fpv_carrier", "mine_layer", "ammo_carrier",
            "fighter_jet", "recon_drone",
            "vbied", "zu23_technical", "smoke_carrier", "lancet_truck", "shahed_truck", "iron_beam", "railgun_truck",
            "turtle_tank", "bmpt",
            "command_vehicle", "wheeled_gun", "counter_battery_radar", "long_sam",
            "armored_bulldozer",
            // Prompt 17 C.
            "stealth_fighter", "wingman_drone", "laser_tank", "shield_carrier", "bunker_vehicle", "swarm_carrier",
            // Prompt 25 F2 batch A (DECISIONS 25F2-A): the balance sheet's new vehicles.
            "aa_gun_vehicle",
            "shorad_vehicle",
            "microwave_vehicle",
            "nlos_atgm_vehicle",
            "radar_atgm_vehicle",
            "recoilless_jeep",
            "airborne_vehicle",
            "wheeled_howitzer",
            "sp_mortar",
            "glide_bomber",
            "recon_jet",
            "interceptor_jet",
            "radar_scout",
            "fibre_fpv_carrier",
            "interceptor_drone_vehicle",
            // (batch A cards: new entries above)
            // Prompt 25 F2 batch B (DECISIONS 25F2-B): the 26 non-tower Thấp-priority items (dx23 not in this pass;
            // the six towers are base-slot cards, not here).
            "aa_57mm_vehicle",
            "mine_rocket_truck",
            "prop_attack_plane",
            "light_attack_heli",
            "next_gen_tank",
            "demolition_line_vehicle",
            "combat_wreck_car",
            "drone_hijack_vehicle",
            "river_patrol_boat",
            "river_gunboat",
            "coastal_ashm_vehicle",
            "auto_loader_howitzer",
            "amphib_light_vehicle",
            "airborne_light_tank",
            "stealth_naval_strike",
            "twin_rotor_gunship",
            "ground_drone_carrier",
            "mobile_repair_vehicle",
            "radar_support_vehicle",
            "towed_at_gun",
            "dazzler_vehicle",
            "ground_cruise_missile_vehicle",
            "aerial_tanker",
            "heavy_lift_helicopter",
            "gps_jammer_vehicle",
            // (batch B cards: new entries above)
        };

        public static readonly string[] AllSupports =
            { "artillery_barrage", "airstrike", "cruise_missile", "smoke_screen", "repair_drop", "napalm_strike",
              "uav_scan", "remote_mines", "field_tower", "sead_strike",
              // Prompt 25 F2 batch C (DECISIONS 25F2-C): new support cards.
              "glide_bomb_strike", "guided_shell_strike", "cluster_at_strike", "uav_loiter_strike_support", "ammo_resupply",
              "jam_storm", "illum_flare_strike", "decoy_paradrop", "instant_counter_battery", "drone_intercept_strike",
              "chaff_strike" };

        // A new player's deck: the starter cards (the rest are won in the campaign or bought).
        private static readonly string[] DefaultVehicles = Progression.StarterVehicles;
        private static readonly string[] DefaultSupports = Progression.StarterSupports;

        /// <summary>The campaign mission to play when <see cref="Mode"/> is Campaign.</summary>
        public static string Mission { get; set; } = "c1m01";

        private static bool _loaded;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _loaded = false;
            InMatch = false;
        }

        /// <summary>False shows the menu over an AI-versus-AI battle; true plays the chosen match.</summary>
        public static bool InMatch { get; set; }

        /// <summary>A saved difficulty's number back as the difficulty (anything unknown: Normal).</summary>
        internal static AiDifficulty DifficultyFromSave(int saved) =>
            System.Enum.IsDefined(typeof(AiDifficulty), saved) ? (AiDifficulty)saved : AiDifficulty.Normal;

        /// <summary>The tier the next campaign mission is fought at (0 normal, 1 hard, 2 very hard); not saved.</summary>

        public static int MissionTier { get; set; }

        /// <summary>An Operations battle (its tier, mutators, week), or null for a campaign mission.</summary>
        internal static OperationRun Run { get; set; }


        public static GameModeKind Mode { get; set; } = GameModeKind.Conquest;

        public static readonly MapInfo[] AllMaps =
        {
            new("ashfield", "temperate", "pine",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Fog, WeatherKind.Night }),
            new("dunebreak", "desert", "dune",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Sandstorm, WeatherKind.Overcast, WeatherKind.Night }),
            new("frostpeak", "snow", "snow",
                new[] { WeatherKind.Snow, WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Fog, WeatherKind.Night }),
            new("ironport", "harbor", "anchor",
                new[] { WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Fog, WeatherKind.Night }),
            new("redrock", "desert", "dune",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Sandstorm, WeatherKind.Night }),
            new("whiteout", "snow", "snow",
                new[] { WeatherKind.Snow, WeatherKind.Snow, WeatherKind.Fog, WeatherKind.Clear, WeatherKind.Night }),
            new("greenvale", "temperate", "pine",
                new[] { WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Fog, WeatherKind.Night }),
            new("rustyard", "harbor", "anchor",
                new[] { WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Night }),
            // Lava glows best in the dark: night comes up as often as a clear day.
            new("emberridge", "volcanic", "flame",
                new[] { WeatherKind.Night, WeatherKind.Night, WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Fog, WeatherKind.Storm }),
            new("junglepass", "jungle", "pine",
                new[] { WeatherKind.Clear, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Storm, WeatherKind.Overcast, WeatherKind.Night }),
            new("skyhold", "temperate", "jet",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Night }),
            // A city at night: lit windows, street lamps and burning buses.
            new("metrocity", "urban", "home",
                new[] { WeatherKind.Night, WeatherKind.Night, WeatherKind.Clear, WeatherKind.Rain, WeatherKind.Overcast, WeatherKind.Fog, WeatherKind.Storm }),
            // Round 4M: four battlefields for the campaign, four for skirmish (all in the rotation).
            // A landing at dawn: overcast and fog come up as often as a clear day.
            new("landingbeach", "temperate", "anchor",
                new[] { WeatherKind.Overcast, WeatherKind.Fog, WeatherKind.Clear, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Night }),
            new("hydrodam", "temperate", "bolt",
                new[] { WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Storm, WeatherKind.Night }),
            new("capital", "urban", "crown",
                new[] { WeatherKind.Clear, WeatherKind.Night, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Storm }),
            // A launch goes at night under the floodlights as often as by day.
            new("launchsite", "desert", "missile",
                new[] { WeatherKind.Clear, WeatherKind.Night, WeatherKind.Clear, WeatherKind.Sandstorm, WeatherKind.Night }),
            // The flats are for long sight lines: mostly clear.
            new("saltflat", "desert", "dune",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Sandstorm, WeatherKind.Night }),
            new("borderbridge", "temperate", "flag",
                new[] { WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Storm, WeatherKind.Night }),
            new("swamp", "jungle", "fog",
                new[] { WeatherKind.Fog, WeatherKind.Rain, WeatherKind.Overcast, WeatherKind.Storm, WeatherKind.Clear, WeatherKind.Night }),
            new("coralisles", "desert", "sun",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Storm, WeatherKind.Overcast, WeatherKind.Night }),
            // Prompt 16: a rocky coast on the sea (Leviathan's battlefield), in the skirmish rotation too.
            new("lighthousebay", "temperate", "anchor",
                new[] { WeatherKind.Overcast, WeatherKind.Clear, WeatherKind.Fog, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Night }),
            // Prompt 20 M: a terraced open-pit mine (the excavator's battlefield); dust storms blow off the spoil heaps.
            new("openpit", "desert", "gear",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Sandstorm, WeatherKind.Overcast, WeatherKind.Night }),
            // A snowbound spaceport: snow and night launches under the floodlights.
            new("orbitalgate", "snow", "globe",
                new[] { WeatherKind.Snow, WeatherKind.Clear, WeatherKind.Night, WeatherKind.Overcast, WeatherKind.Fog, WeatherKind.Night }),
            // Prompt 22 E: Hegemon's old tank works (indoor lanes: rain on the roofs, smoke and night shifts) and the
            // capital's old town.
            new("foundry", "urban", "gear",
                new[] { WeatherKind.Overcast, WeatherKind.Clear, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Night, WeatherKind.Night }),
            new("veyra_old_quarter", "urban", "tower",
                new[] { WeatherKind.Clear, WeatherKind.Night, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Fog, WeatherKind.Storm }),
        };

        public static string Map { get; set; } = "ashfield";

        public static MapInfo CurrentMap
        {
            get
            {
                foreach (var map in AllMaps)
                    if (map.Id == Map && MapAvailable(map.Id)) return map;
                return AllMaps[0];
            }
        }

        public static bool MapAvailable(string id) => Resources.Load<TextAsset>("Data/maps/" + id + "_conquest") != null;
        public static AiDifficulty Difficulty { get; set; } = AiDifficulty.Normal;
        public static WeatherKind Weather { get; set; } = WeatherKind.Random;

        public static List<string> DeckVehicles { get; } = new(DefaultVehicles);
        public static List<string> DeckSupports { get; } = new(DefaultSupports);

        // Where each card sits in the deck on screen (null: an empty slot). Taking a card out
        // leaves its slot empty instead of sliding the others along, which read as the wrong
        // card leaving.
        private static readonly string[] VehicleLayout = new string[DeckVehicleSlots];
        private static readonly string[] SupportLayout = new string[DeckSupportSlots];

        /// <summary>The deck's slots as the player sees them, reconciled with the deck list.</summary>
        public static string[] DeckLayout(bool supports)
        {
            var deck = supports ? DeckSupports : DeckVehicles;
            var layout = supports ? SupportLayout : VehicleLayout;
            for (var i = 0; i < layout.Length; i++)
                if (layout[i] != null && (!deck.Contains(layout[i]) || Array.IndexOf(layout, layout[i]) != i)) layout[i] = null;
            foreach (var id in deck)
            {
                if (Array.IndexOf(layout, id) >= 0) continue;
                var free = Array.IndexOf(layout, null);
                if (free >= 0) layout[free] = id;
            }
            return layout;
        }

        /// <summary>
        /// Puts a card in the deck's first empty slot or takes it out of its slot. The last card
        /// of a kind stays (an empty deck means "anything" to the simulation).
        /// </summary>
        public static DeckChange ToggleDeckCard(string id, bool supports)
        {
            var deck = supports ? DeckSupports : DeckVehicles;
            var layout = DeckLayout(supports);
            var at = Array.IndexOf(layout, id);
            if (at >= 0)
            {
                if (deck.Count <= 1) return DeckChange.LastCard;
                layout[at] = null;
            }
            else
            {
                var free = Array.IndexOf(layout, null);
                if (free < 0) return DeckChange.Full;
                layout[free] = id;
            }
            deck.Clear();
            foreach (var card in layout)
                if (card != null) deck.Add(card);
            return at >= 0 ? DeckChange.Removed : DeckChange.Added;
        }

        public enum DeckChange
        {
            Added,
            Removed,
            Full,
            LastCard,
        }

        public static float Volume { get; set; } = 0.8f;

        /// <summary>The soundtrack's own level (0 turns it off), under the master volume.</summary>
        public static float MusicVolume { get; set; } = 0.7f;

        /// <summary>Prompt 34 L6: the battle's sounds (shots, blasts, wrecks, engines, warnings) under the master volume.</summary>
        public static float EffectsVolume { get; set; } = 1f;

        /// <summary>Prompt 34 L6: the radio and spoken lines under the master volume.</summary>
        public static float DialogueVolume { get; set; } = 1f;
        public static GraphicsQuality Graphics { get; set; } = GraphicsQuality.Auto;

        /// <summary>
        /// The tier in force: the player's choice, or one picked from the device (memory and CPU
        /// cores, the usual proxies for GPU class on Android). Explosions and fires are never cut;
        /// tiers change resolution, anti-aliasing, shadows, bloom and far scenery.
        /// </summary>
        public static GraphicsQuality Tier => Graphics is GraphicsQuality.Auto or GraphicsQuality.Custom ? DetectTier() : Graphics;

        private static GraphicsOptions _custom;

        /// <summary>The graphics options in force: the preset's, or the player's own under Custom.</summary>
        public static GraphicsOptions Options => Graphics == GraphicsQuality.Custom && _custom != null ? _custom : GraphicsOptions.For(Tier);

        /// <summary>Changes one option: the current values become the Custom set.</summary>
        public static void Customise(System.Action<GraphicsOptions> change)
        {
            var options = Options.Copy();
            change(options);
            _custom = options;
            Graphics = GraphicsQuality.Custom;
        }

        public static bool HighQuality => Options.MaxEffects;

        /// <summary>Screen shake: 0 off, 1 low, 2 full.</summary>
        public static int ScreenShake { get; set; } = 2;

        public static float ShakeScale => ScreenShake switch { 0 => 0f, 1 => 0.35f, _ => 1f };

        /// <summary>
        /// Fix prompt L5: the warning rings (Effects/WarningGate): 0 Full (at most six, the most threatening first), 1 Important
        /// only (super weapons and the rings over our units), 2 Off (super weapons still shown).
        /// </summary>
        public static int WarningRings { get; set; }

        /// <summary>Short vibrations on the heaviest moments.</summary>
        public static bool Haptics { get; set; } = true;

        /// <summary>Blue against orange instead of green against red, for red-green colour blindness.</summary>
        public static bool ColorBlind { get; set; }

        /// <summary>Where a save before DECISIONS 23D kept its doctrine choice: deleted on load, never read.</summary>
        internal const string OldDoctrineKey = "mb.doctrine";

        internal static void DropOldDoctrineChoice() => PlayerPrefs.DeleteKey(OldDoctrineKey);

        /// <summary>Slow motion and letterbox for a second on the biggest blasts.</summary>
        public static bool CinematicMoments { get; set; } = true;

        /// <summary>Prompt 23 H.7: Settings, In-battle dialogue (Full, Important only, Off; story lines always show).</summary>
        public static DialogueSetting Dialogue { get; set; } = DialogueSetting.Full;

        /// <summary>Camera drag speed: 0 slow, 1 normal, 2 fast.</summary>
        public static int CameraSpeed { get; set; } = 1;

        public static float PanScale => CameraSpeed switch { 0 => 0.7f, 2 => 1.45f, _ => 1f };

        /// <summary>Battery saver: 0 off, 1 on, 2 automatic (on when the battery is low and not charging).</summary>
        public static int BatterySaver { get; set; } = 2;

        /// <summary>
        /// True while saving battery: 30 fps and 85% resolution. Effects are untouched. The
        /// automatic mode starts it under 20% charge while unplugged.
        /// </summary>
        public static bool SavingBattery => BatterySaver == 1 || (BatterySaver == 2 && SystemInfo.batteryLevel >= 0f &&
            SystemInfo.batteryLevel < 0.2f && SystemInfo.batteryStatus == BatteryStatus.Discharging);

        /// <summary>Brightness in percent (80 to 120).</summary>
        public static int Brightness { get; set; } = 100;

        /// <summary>Interface size: 0 small, 1 normal, 2 large.</summary>
        public static int UiSize { get; set; } = 1;

        public static float UiScale => UiSize switch { 0 => 0.9f, 2 => 1.1f, _ => 1f };

        /// <summary>Text size: Large switches every kit screen to the larger type scale (Kit.ApplyTextSize).</summary>
        public static TextSize TextSize { get; set; } = TextSize.Normal;

        public static bool LargeText => TextSize == TextSize.Large;

        public static GraphicsQuality DetectTier()
        {
            if (!Application.isMobilePlatform) return GraphicsQuality.High;
            var memory = SystemInfo.systemMemorySize;
            var cores = SystemInfo.processorCount;
            if (memory >= 7000 && cores >= 8) return GraphicsQuality.High;
            if (memory >= 3500 && cores >= 6) return GraphicsQuality.Medium;
            return GraphicsQuality.Low;
        }
        public static bool ShowFps { get; set; }

        /// <summary>Prompt 28 B.7: the battle HUD's AI hint line (Settings, saved as mb.aiHints, on by default).</summary>
        public static bool AiHints { get; set; } = true;

        /// <summary>Prompt 13 C.9: the ammunition icons over units: 0 every unit (the default), 1 aircraft and helicopters only.</summary>
        public static int AmmoIcons { get; set; }
        public static LanguageChoice Language { get; set; } = LanguageChoice.Auto;

        /// <summary>The commander AI buys vehicles from the deck.</summary>
        public static bool AutoDeploy { get; set; } = true;

        /// <summary>The commander AI calls fire support.</summary>
        public static bool AutoStrike { get; set; } = true;

        /// <summary>
        /// The compact battle HUD (prompt 11 A: a smaller minimap, icon toggles, a lower card tray, a
        /// collapsible boss bar); off shows the full HUD. On by default.
        /// </summary>
        public static bool CompactHud { get; set; } = true;

        /// <summary>
        /// Settings > "Hiện số chi tiết" (prompt 15 D.9, saved as mb.showNumbers, off by default): the armour and
        /// weapon tooltips and the detail page add the armour and penetration levels and the multipliers.
        /// </summary>
        public static bool ShowCombatNumbers { get; set; }

        /// <summary>How many matches the standing hint ("your army fights on its own · tap A B C") is shown for.</summary>
        public const int StartHintMatches = 3;

        /// <summary>Matches played with the standing hint so far (saved as mb.hintMatches).</summary>
        public static int HintMatchesSeen { get; private set; }

        /// <summary>The standing hint still shows: only in the player's first few matches.</summary>
        public static bool ShowStartHint => HintMatchesSeen < StartHintMatches;

        /// <summary>A real match began (not the menu's lobby battle): counts towards the standing hint's matches.</summary>
        public static void CountHintMatch()
        {
            if (!ShowStartHint) return;
            HintMatchesSeen++;
            try
            {
                PlayerPrefs.SetInt("mb.hintMatches", HintMatchesSeen);
                PlayerPrefs.Save();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[MatchSettings] Could not save the hint count: {e.Message}");
            }
        }

        public static void Load()
        {
            if (_loaded) return;
            _loaded = true;
            try
            {
                Volume = PlayerPrefs.GetFloat("mb.volume", Volume);
                MusicVolume = PlayerPrefs.GetFloat("mb.music", MusicVolume);
                EffectsVolume = Mathf.Clamp01(PlayerPrefs.GetFloat("mb.effects", EffectsVolume));
                DialogueVolume = Mathf.Clamp01(PlayerPrefs.GetFloat("mb.dialogue", DialogueVolume));
                Graphics = (GraphicsQuality)Mathf.Clamp(PlayerPrefs.GetInt("mb.graphics", 0), 0, 4);
                if (Graphics == GraphicsQuality.Custom) _custom = GraphicsOptions.Load("mb.gfx.", GraphicsOptions.For(DetectTier()));
                // Reduced motion (older saves) became the low screen-shake setting.
                ScreenShake = Mathf.Clamp(PlayerPrefs.GetInt("mb.shake", PlayerPrefs.GetInt("mb.reducedMotion", 0) == 1 ? 1 : 2), 0, 2);
                CameraSpeed = Mathf.Clamp(PlayerPrefs.GetInt("mb.cameraSpeed", 1), 0, 2);
                WarningRings = Mathf.Clamp(PlayerPrefs.GetInt("mb.warnings", 0), 0, 2);
                CinematicMoments = PlayerPrefs.GetInt("mb.cinematic", 1) == 1;
                Dialogue = (DialogueSetting)Mathf.Clamp(PlayerPrefs.GetInt("mb.dialogue", 0), 0, 2);
                // DECISIONS 23D: the doctrines are the commanders' now; an old save's doctrine choice is dropped, never read.
                DropOldDoctrineChoice();
                Haptics = PlayerPrefs.GetInt("mb.haptics", 1) == 1;
                ColorBlind = PlayerPrefs.GetInt("mb.colorblind", 0) == 1;
                MachineBrigade.Game.Rendering.TeamColors.Palette = ColorBlind ? 1 : 0;
                UiSize = Mathf.Clamp(PlayerPrefs.GetInt("mb.uiSize", 1), 0, 2);
                TextSize = (TextSize)Mathf.Clamp(PlayerPrefs.GetInt("mb.textSize", 0), 0, 1);
                BatterySaver = Mathf.Clamp(PlayerPrefs.GetInt("mb.battery", 2), 0, 2);
                Brightness = Mathf.Clamp(PlayerPrefs.GetInt("mb.brightness", 100), 80, 120);
                Map = PlayerPrefs.GetString("mb.map", Map);
                ShowFps = PlayerPrefs.GetInt("mb.fps", 0) == 1;
                AiHints = PlayerPrefs.GetInt("mb.aiHints", 1) == 1;
                AmmoIcons = Mathf.Clamp(PlayerPrefs.GetInt("mb.ammoIcons", 0), 0, 1);
                Language = (LanguageChoice)PlayerPrefs.GetInt("mb.language", 0);
                // Saved as its number: Easy 0, Normal 1, Hard 2 as before; Very Hard (3) came after them (prompt 13 I).
                Difficulty = DifficultyFromSave(PlayerPrefs.GetInt("mb.difficulty", (int)AiDifficulty.Normal));
                Weather = (WeatherKind)PlayerPrefs.GetInt("mb.weather", (int)WeatherKind.Random);
                var savedMode = (GameModeKind)PlayerPrefs.GetInt("mb.mode", 0);
                Mode = System.Enum.IsDefined(typeof(GameModeKind), savedMode) && savedMode != GameModeKind.Campaign ? savedMode : GameModeKind.Conquest;
                Mission = PlayerPrefs.GetString("mb.mission", Mission);
                AutoDeploy = PlayerPrefs.GetInt("mb.autoDeploy", 1) == 1;
                AutoStrike = PlayerPrefs.GetInt("mb.autoStrike", 1) == 1;
                CompactHud = PlayerPrefs.GetInt("mb.compactHud", 1) == 1;
                ShowCombatNumbers = PlayerPrefs.GetInt("mb.showNumbers", 0) == 1;
                HintMatchesSeen = Mathf.Max(0, PlayerPrefs.GetInt("mb.hintMatches", 0));
                ReadDeck("mb.deck.vehicles", DeckVehicles, AllVehicles, DefaultVehicles, DeckVehicleSlots, VehicleLayout);
                ReadDeck("mb.deck.supports", DeckSupports, AllSupports, DefaultSupports, DeckSupportSlots, SupportLayout);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[MatchSettings] Could not read settings: {e.Message}");
            }
            ApplyLanguage();
        }

        /// <summary>Checks that tap through the screens turn saving off, so they never write the player's saved settings.</summary>
        internal static bool SaveSuspended { get; set; }

        public static void Save()
        {
            if (SaveSuspended) return;
            // An empty deck would mean "anything" to the simulation; refill it instead.
            if (DeckVehicles.Count == 0) DeckVehicles.AddRange(DefaultVehicles);
            if (DeckSupports.Count == 0) DeckSupports.AddRange(DefaultSupports);
            try
            {
                PlayerPrefs.SetFloat("mb.volume", Volume);
                PlayerPrefs.SetFloat("mb.music", MusicVolume);
                PlayerPrefs.SetFloat("mb.effects", EffectsVolume);
                PlayerPrefs.SetFloat("mb.dialogue", DialogueVolume);
                PlayerPrefs.SetInt("mb.graphics", (int)Graphics);
                if (Graphics == GraphicsQuality.Custom) _custom?.Save("mb.gfx.");
                PlayerPrefs.SetInt("mb.shake", ScreenShake);
                PlayerPrefs.SetInt("mb.cameraSpeed", CameraSpeed);
                PlayerPrefs.SetInt("mb.warnings", WarningRings);
                PlayerPrefs.SetInt("mb.cinematic", CinematicMoments ? 1 : 0);
                PlayerPrefs.SetInt("mb.dialogue", (int)Dialogue);
                PlayerPrefs.SetInt("mb.haptics", Haptics ? 1 : 0);
                PlayerPrefs.SetInt("mb.colorblind", ColorBlind ? 1 : 0);
                MachineBrigade.Game.Rendering.TeamColors.Palette = ColorBlind ? 1 : 0;
                PlayerPrefs.SetInt("mb.uiSize", UiSize);
                PlayerPrefs.SetInt("mb.textSize", (int)TextSize);
                PlayerPrefs.SetInt("mb.battery", BatterySaver);
                PlayerPrefs.SetInt("mb.brightness", Brightness);
                PlayerPrefs.SetString("mb.map", Map);
                PlayerPrefs.SetInt("mb.fps", ShowFps ? 1 : 0);
                PlayerPrefs.SetInt("mb.aiHints", AiHints ? 1 : 0);
                PlayerPrefs.SetInt("mb.ammoIcons", AmmoIcons);
                PlayerPrefs.SetInt("mb.language", (int)Language);
                PlayerPrefs.SetInt("mb.difficulty", (int)Difficulty);
                PlayerPrefs.SetInt("mb.weather", (int)Weather);
                // Campaign runs are started from the campaign page, never restored as the menu's mode.
                PlayerPrefs.SetInt("mb.mode", Mode == GameModeKind.Campaign ? 0 : (int)Mode);
                PlayerPrefs.SetString("mb.mission", Mission);
                PlayerPrefs.SetInt("mb.autoDeploy", AutoDeploy ? 1 : 0);
                PlayerPrefs.SetInt("mb.autoStrike", AutoStrike ? 1 : 0);
                PlayerPrefs.SetInt("mb.compactHud", CompactHud ? 1 : 0);
                PlayerPrefs.SetInt("mb.showNumbers", ShowCombatNumbers ? 1 : 0);
                // Saved slot by slot, empty slots as blanks, so the layout comes back as it was.
                PlayerPrefs.SetString("mb.deck.vehicles", string.Join(",", Array.ConvertAll(DeckLayout(false), c => c ?? "")));
                PlayerPrefs.SetString("mb.deck.supports", string.Join(",", Array.ConvertAll(DeckLayout(true), c => c ?? "")));
                PlayerPrefs.SetInt("mb.deck.version", DeckVersion);
                PlayerPrefs.Save();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[MatchSettings] Could not save settings: {e.Message}");
            }
            ApplyLanguage();
        }

        /// <summary>Picks the weather for this match, resolving Random.</summary>
        public static WeatherKind ResolveWeather(int seed)
        {
            if (Weather != WeatherKind.Random) return Weather;
            var choices = CurrentMap.Weathers;
            return choices[new System.Random(seed).Next(choices.Length)];
        }

        public static void ApplyLanguage()
        {
            Strings.Vietnamese = Language switch
            {
                LanguageChoice.English => false,
                LanguageChoice.Vietnamese => true,
                _ => Application.systemLanguage == SystemLanguage.Vietnamese,
            };
            // Device checks of text lengths in each language: -mb-en, -mb-vi.
            if (DebugFlags.Has("-mb-en")) Strings.Vietnamese = false;
            else if (DebugFlags.Has("-mb-vi")) Strings.Vietnamese = true;
        }

        private static void ReadDeck(string key, List<string> deck, string[] all, string[] defaults, int slots, string[] layout)
        {
            var saved = PlayerPrefs.GetString(key, "");
            if (string.IsNullOrEmpty(saved)) return;
            Array.Clear(layout, 0, layout.Length);
            // Merged cards come back as the card they became (once: a second copy is dropped).
            var positions = Array.ConvertAll(saved.Split(','), CardMerges.Resolve);
            for (var i = 0; i < positions.Length && i < layout.Length; i++)
                if (Array.IndexOf(all, positions[i]) >= 0 && PlayerProfile.IsUnlocked(positions[i]) && Array.IndexOf(layout, positions[i]) < 0) layout[i] = positions[i];
            var cards = new List<string>();
            foreach (var id in positions)
                if (Array.IndexOf(all, id) >= 0 && PlayerProfile.IsUnlocked(id) && !cards.Contains(id) && cards.Count < slots) cards.Add(id);
            // Decks saved before the deck grew to 8 vehicles are topped up from the defaults once;
            // a deck the player deliberately left short stays as it is.
            if (PlayerPrefs.GetInt("mb.deck.version", 1) < DeckVersion || cards.Count == 0)
                foreach (var id in defaults)
                    if (cards.Count < slots && !cards.Contains(id)) cards.Add(id);
            deck.Clear();
            deck.AddRange(cards);
        }
    }
}
