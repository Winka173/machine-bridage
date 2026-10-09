// Naval FINAL spec (09/10, Docs/naval/final): the naval regression suite of the headless harness (no Unity). Every matchup of
// prompt section H and spec section 9, 3- and 5-ship formations, a mixed escort group, a narrow lane, a wreck in the lane,
// target selection / salvo overkill and a missile-saturation performance run, on the Sandbox's coastal range (or a narrow
// one-lane sea built here), fixed rosters and seeds. Each row records the QA guide section 1 fields: time to first shot,
// TTK, survivors, damage by source, ammunition (shots by weapon), interceptions, target switches, pathing failures (stuck
// episodes, a ship off the water, reversing, turning past its rate), range keeping, salvo overkill, projectiles in flight
// and step time. Plus a static economy table (no simulation): HP/CP, the main battery's effective DPS/CP against the ship's
// intended prey, salvo alpha/CP, interception value/CP, the time its counter needs to sink it.
//
// Run (the lead; tests need the owner's word): see Docs/naval/final/TEST_PLAN.md.
//   Temp/regress/MachineBrigade.Tests.EditMode.exe naval <balance.json> <tunables.json> <out.tsv>     (MB_SET=duel|aa|shore|capital|ew|budget|formation|lane|wreck|target|perf|all)
//   Temp/regress/MachineBrigade.Tests.EditMode.exe naval-econ <balance.json> <tunables.json> <out.tsv>
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Text;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

static class NavalSuite
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    /// <summary>Default seeds (MB_SEEDS overrides): several per matchup, fixed for regression.</summary>
    static int[] Seeds = { 1, 2, 3, 4, 5 };

    const float Step = SandboxLab.Step;

    // ------------------------------------------------------------------ the matrix

    sealed class Row
    {
        public string Set, Name, Expect = "-";
        public string[] A, B;
        public float Gap = 90f, Limit = 150f;
        public bool Narrow, HoldA, HoldB, Wreck;
        /// <summary>Health of side B's units, percent (the wreck bait, the nearly-dead patrol boat).</summary>
        public int[] HpB;
        /// <summary>Equal-CP fill: each side's list repeated while its CP stays within this (0: the lists as given).</summary>
        public int Budget;
        public string Note = "";
    }

    static string[] N(string id, int n) => Enumerable.Repeat(id, n).ToArray();
    static string[] L(params string[] ids) => ids;

    static readonly Row[] Matrix =
    {
        // ---- duels (prompt H, spec 9): both sides on their own patrol lanes, fighting AI
        new() { Set = "duel", Name = "hover_gunboat x2 vs torpedo_boat x2", A = N("hover_gunboat", 2), B = N("torpedo_boat", 2), Expect = "A", Note = "OWNER DECISION: hover_gunboat is not a sea unit (no naval block; the sea's water blocks it, it is pushed ashore) and the torpedo boat is navalOnly" },
        new() { Set = "duel", Name = "river_patrol_boat x2 vs torpedo_boat x2", A = N("river_patrol_boat", 2), B = N("torpedo_boat", 2), Expect = "A", Note = "OWNER DECISION: river_patrol_boat is a ground-domain river craft (no naval block), it cannot enter the sea" },
        new() { Set = "duel", Name = "sea_corvette vs ashm_corvette (close 40 m)", A = N("sea_corvette", 1), B = N("ashm_corvette", 1), Gap = 40f, Expect = "A", Note = "AShM corvette loses close" },
        new() { Set = "duel", Name = "sea_corvette vs ashm_corvette (long 130 m)", A = N("sea_corvette", 1), B = N("ashm_corvette", 1), Gap = 130f, Expect = "B", Note = "AShM corvette wins at standoff" },
        new() { Set = "duel", Name = "ashm_corvette vs sea_corvette + ciws_escort_craft", A = N("ashm_corvette", 1), B = L("sea_corvette", "ciws_escort_craft"), Gap = 120f, Expect = "B", Note = "a lone AShM corvette loses to a CIWS-protected group" },
        new() { Set = "duel", Name = "frigate vs sea_corvette", A = N("frigate", 1), B = N("sea_corvette", 1), Expect = "A" },
        new() { Set = "duel", Name = "missile_frigate vs frigate (long 130 m)", A = N("missile_frigate", 1), B = N("frigate", 1), Gap = 130f, Expect = "A" },
        new() { Set = "duel", Name = "destroyer vs frigate", A = N("destroyer", 1), B = N("frigate", 1), Expect = "A" },
        new() { Set = "duel", Name = "gun_destroyer vs missile_destroyer (close 40 m)", A = N("gun_destroyer", 1), B = N("missile_destroyer", 1), Gap = 40f, Expect = "A" },
        new() { Set = "duel", Name = "gun_destroyer vs missile_destroyer (long 135 m)", A = N("gun_destroyer", 1), B = N("missile_destroyer", 1), Gap = 135f, Expect = "B" },
        new() { Set = "duel", Name = "sea_cruiser.gun vs destroyer", A = N("sea_cruiser.gun", 1), B = N("destroyer", 1), Expect = "A" },
        new() { Set = "duel", Name = "sea_cruiser (anchor) vs destroyer", A = N("sea_cruiser", 1), B = N("destroyer", 1), Expect = "-", Note = "anchor niche: fleet escort, cp 0" },
        new() { Set = "duel", Name = "sea_cruiser.missile vs destroyer (long)", A = N("sea_cruiser.missile", 1), B = N("destroyer", 1), Gap = 130f, Expect = "A" },
        new() { Set = "duel", Name = "battlecruiser vs sea_cruiser.gun", A = N("battlecruiser", 1), B = N("sea_cruiser.gun", 1), Expect = "A" },
        new() { Set = "duel", Name = "battlecruiser vs sea_cruiser.missile", A = N("battlecruiser", 1), B = N("sea_cruiser.missile", 1), Expect = "A" },
        new() { Set = "duel", Name = "naval_monitor vs destroyer", A = N("naval_monitor", 1), B = N("destroyer", 1), Gap = 60f, Expect = "-", Note = "monitor strong vs medium ships close, weak at standoff" },
        new() { Set = "duel", Name = "naval_monitor vs missile_destroyer (long)", A = N("naval_monitor", 1), B = N("missile_destroyer", 1), Gap = 135f, Expect = "B" },
        new() { Set = "duel", Name = "torpedo_boat x2 vs destroyer", A = N("torpedo_boat", 2), B = N("destroyer", 1), Gap = 60f, Expect = "A", Note = "glass cannon vs capital" },
        new() { Set = "duel", Name = "aa_frigate vs missile_frigate (surface duel)", A = N("aa_frigate", 1), B = N("missile_frigate", 1), Gap = 120f, Expect = "B" },
        new() { Set = "duel", Name = "aa_destroyer vs gun_destroyer (isolated)", A = N("aa_destroyer", 1), B = N("gun_destroyer", 1), Expect = "B" },
        new() { Set = "duel", Name = "ew_corvette vs ashm_corvette (equal CP)", A = N("ew_corvette", 1), B = N("ashm_corvette", 1), Expect = "B", Note = "EW loses a duel" },
        new() { Set = "duel", Name = "ciws_escort_craft vs sea_corvette", A = N("ciws_escort_craft", 1), B = N("sea_corvette", 1), Expect = "B" },
        new() { Set = "duel", Name = "missile_boat x2 vs frigate (anchor niche)", A = N("missile_boat", 2), B = N("frigate", 1), Expect = "-" },
        new() { Set = "duel", Name = "river_gunboat vs torpedo_boat (anchor niche)", A = N("river_gunboat", 1), B = N("torpedo_boat", 1), Gap = 60f, Expect = "A" },
        // ---- AA ships against aircraft and a cruise missile (the ship is side A, the air side B attacks it)
        new() { Set = "aa", Name = "aa_corvette vs scout_heli", A = N("aa_corvette", 1), B = N("scout_heli", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_corvette vs attack_helicopter", A = N("aa_corvette", 1), B = N("attack_helicopter", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_corvette vs fighter_jet", A = N("aa_corvette", 1), B = N("fighter_jet", 1), Expect = "-" },
        new() { Set = "aa", Name = "aa_corvette vs attack_jet", A = N("aa_corvette", 1), B = N("attack_jet", 1), Expect = "-" },
        new() { Set = "aa", Name = "aa_corvette vs cruise missile (ground launcher)", A = N("aa_corvette", 1), B = N("ground_cruise_missile_vehicle", 1), Gap = 160f, Expect = "-", Note = "record interceptions" },
        new() { Set = "aa", Name = "aa_frigate vs scout_heli", A = N("aa_frigate", 1), B = N("scout_heli", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_frigate vs attack_helicopter", A = N("aa_frigate", 1), B = N("attack_helicopter", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_frigate vs fighter_jet", A = N("aa_frigate", 1), B = N("fighter_jet", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_frigate vs attack_jet", A = N("aa_frigate", 1), B = N("attack_jet", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_frigate vs cruise missile (ground launcher)", A = N("aa_frigate", 1), B = N("ground_cruise_missile_vehicle", 1), Gap = 160f, Expect = "-" },
        new() { Set = "aa", Name = "aa_destroyer vs scout_heli", A = N("aa_destroyer", 1), B = N("scout_heli", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_destroyer vs attack_helicopter", A = N("aa_destroyer", 1), B = N("attack_helicopter", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_destroyer vs fighter_jet", A = N("aa_destroyer", 1), B = N("fighter_jet", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_destroyer vs attack_jet", A = N("aa_destroyer", 1), B = N("attack_jet", 1), Expect = "A" },
        new() { Set = "aa", Name = "aa_destroyer vs cruise missile (ground launcher)", A = N("aa_destroyer", 1), B = N("ground_cruise_missile_vehicle", 1), Gap = 160f, Expect = "-" },
        new() { Set = "aa", Name = "frigate (no SAM) vs attack_helicopter (control)", A = N("frigate", 1), B = N("attack_helicopter", 1), Expect = "-" },
        // ---- shore fire: towers / structures on the shore, a moving ship
        new() { Set = "shore", Name = "rocket_artillery_ship vs gun_turret (shore tower)", A = N("rocket_artillery_ship", 1), B = N("gun_turret", 1), Gap = 80f, Expect = "A" },
        new() { Set = "shore", Name = "rocket_artillery_ship vs repair_bay (structure)", A = N("rocket_artillery_ship", 1), B = N("repair_bay", 1), Gap = 80f, Expect = "A" },
        new() { Set = "shore", Name = "rocket_artillery_ship vs sea_corvette (moving ship)", A = N("rocket_artillery_ship", 1), B = N("sea_corvette", 1), Gap = 90f, Expect = "-" },
        new() { Set = "shore", Name = "rocket_artillery_ship vs torpedo_boat (closing craft)", A = N("rocket_artillery_ship", 1), B = N("torpedo_boat", 1), Gap = 60f, Expect = "B" },
        new() { Set = "shore", Name = "naval_monitor vs gun_turret (medium tower)", A = N("naval_monitor", 1), B = N("gun_turret", 1), Gap = 50f, Expect = "A" },
        new() { Set = "shore", Name = "naval_monitor vs repair_bay (structure)", A = N("naval_monitor", 1), B = N("repair_bay", 1), Gap = 50f, Expect = "A" },
        new() { Set = "shore", Name = "gun_destroyer vs gun_turret (shore bombardment)", A = N("gun_destroyer", 1), B = N("gun_turret", 1), Gap = 70f, Expect = "A" },
        // ---- capitals against concentrated fire
        new() { Set = "capital", Name = "battleship vs ashm_corvette x3 (concentrated AShM)", A = N("battleship", 1), B = N("ashm_corvette", 3), Gap = 130f, Limit = 180f, Expect = "-" },
        new() { Set = "capital", Name = "battleship vs missile_destroyer x2 (AShM salvo)", A = N("battleship", 1), B = N("missile_destroyer", 2), Gap = 130f, Limit = 180f, Expect = "B" },
        new() { Set = "capital", Name = "battleship vs torpedo_boat x3 (torpedo)", A = N("battleship", 1), B = N("torpedo_boat", 3), Gap = 70f, Limit = 180f, Expect = "-" },
        new() { Set = "capital", Name = "battleship vs gun_destroyer x2 (heavy gun)", A = N("battleship", 1), B = N("gun_destroyer", 2), Limit = 180f, Expect = "A" },
        new() { Set = "capital", Name = "battleship vs sea_cruiser.gun (heavy gun)", A = N("battleship", 1), B = N("sea_cruiser.gun", 1), Limit = 180f, Expect = "A" },
        new() { Set = "capital", Name = "battleship vs battlecruiser", A = N("battleship", 1), B = N("battlecruiser", 1), Limit = 180f, Expect = "A" },
        // ---- EW: the same protected group with and without the EW corvette, under the same AShM attack
        new() { Set = "ew", Name = "frigate + aa_frigate + ew_corvette vs missile_frigate x2", A = L("frigate", "aa_frigate", "ew_corvette"), B = N("missile_frigate", 2), Gap = 130f, Limit = 180f, Expect = "-", Note = "compare A's damage taken with the next row" },
        new() { Set = "ew", Name = "frigate + aa_frigate (no EW) vs missile_frigate x2", A = L("frigate", "aa_frigate"), B = N("missile_frigate", 2), Gap = 130f, Limit = 180f, Expect = "-" },
        new() { Set = "ew", Name = "destroyer + ew_corvette vs ashm_corvette x3", A = L("destroyer", "ew_corvette"), B = N("ashm_corvette", 3), Gap = 130f, Limit = 180f, Expect = "-" },
        new() { Set = "ew", Name = "destroyer (no EW) vs ashm_corvette x3", A = L("destroyer"), B = N("ashm_corvette", 3), Gap = 130f, Limit = 180f, Expect = "-" },
        // ---- equal CP budget (both sides CP-costed)
        new() { Set = "budget", Name = "36 CP: missile_frigate vs frigate", A = N("missile_frigate", 1), B = N("frigate", 1), Budget = 36, Gap = 130f, Limit = 180f, Expect = "A" },
        new() { Set = "budget", Name = "42 CP: destroyer vs frigate", A = N("destroyer", 1), B = N("frigate", 1), Budget = 42, Limit = 180f, Expect = "-" },
        new() { Set = "budget", Name = "30 CP: gun_destroyer vs missile_destroyer (close)", A = N("gun_destroyer", 1), B = N("missile_destroyer", 1), Budget = 30, Gap = 40f, Limit = 180f, Expect = "A" },
        new() { Set = "budget", Name = "30 CP: gun_destroyer vs missile_destroyer (long)", A = N("gun_destroyer", 1), B = N("missile_destroyer", 1), Budget = 30, Gap = 135f, Limit = 180f, Expect = "B" },
        new() { Set = "budget", Name = "28 CP: torpedo_boat vs destroyer", A = N("torpedo_boat", 1), B = N("destroyer", 1), Budget = 28, Gap = 60f, Limit = 180f, Expect = "A" },
        new() { Set = "budget", Name = "46 CP: battleship vs ashm_corvette", A = N("battleship", 1), B = N("ashm_corvette", 1), Budget = 46, Gap = 130f, Limit = 180f, Expect = "-" },
        new() { Set = "budget", Name = "36 CP: sea_cruiser.gun vs frigate", A = N("sea_cruiser.gun", 1), B = N("frigate", 1), Budget = 36, Limit = 180f, Expect = "-" },
        new() { Set = "budget", Name = "36 CP: river_gunboat vs frigate (anchor niche)", A = N("river_gunboat", 1), B = N("frigate", 1), Budget = 36, Limit = 180f, Expect = "-" },
        // ---- formations
        new() { Set = "formation", Name = "3 ships: destroyer + frigate + aa_frigate vs missile_destroyer + frigate + ashm_corvette", A = L("destroyer", "frigate", "aa_frigate"), B = L("missile_destroyer", "frigate", "ashm_corvette"), Gap = 110f, Limit = 180f },
        new() { Set = "formation", Name = "5 ships: destroyer + 2 frigate + aa_frigate + ciws_escort_craft vs missile_destroyer + gun_destroyer + missile_frigate + ashm_corvette + torpedo_boat",
            A = L("destroyer", "frigate", "frigate", "aa_frigate", "ciws_escort_craft"), B = L("missile_destroyer", "gun_destroyer", "missile_frigate", "ashm_corvette", "torpedo_boat"), Gap = 110f, Limit = 200f },
        new() { Set = "formation", Name = "mixed escort: battleship + aa_destroyer + ciws_escort_craft + ew_corvette vs missile_destroyer x2 + missile_frigate + torpedo_boat x2",
            A = L("battleship", "aa_destroyer", "ciws_escort_craft", "ew_corvette"), B = L("missile_destroyer", "missile_destroyer", "missile_frigate", "torpedo_boat", "torpedo_boat"), Gap = 130f, Limit = 200f },
        // ---- narrow lane: one 22 m channel, every ship in it
        new() { Set = "lane", Name = "narrow lane: destroyer + frigate + frigate vs gun_destroyer + frigate + sea_corvette", A = L("destroyer", "frigate", "frigate"), B = L("gun_destroyer", "frigate", "sea_corvette"), Narrow = true, Gap = 100f, Limit = 180f },
        new() { Set = "lane", Name = "narrow lane: battleship + ciws_escort_craft vs destroyer x2", A = L("battleship", "ciws_escort_craft"), B = N("destroyer", 2), Narrow = true, Gap = 100f, Limit = 180f },
        // ---- wreck obstruction: a ship sunk in the near lane ahead of a column on the same lane
        new() { Set = "wreck", Name = "wreck in the lane: frigate + gun_destroyer + naval_monitor past a sunk sea_corvette", A = L("frigate", "gun_destroyer", "naval_monitor"), B = L("sea_corvette"), HpB = new[] { 2 }, HoldB = true, Wreck = true, Gap = 50f, Limit = 120f },
        new() { Set = "wreck", Name = "wreck in the narrow lane: destroyer + frigate past a sunk destroyer", A = L("destroyer", "frigate"), B = L("destroyer"), HpB = new[] { 2 }, HoldB = true, Wreck = true, Narrow = true, Gap = 60f, Limit = 120f },
        // ---- target selection / salvo overkill: a nearly-dead cheap boat next to a worthwhile ship
        new() { Set = "target", Name = "battleship vs river_patrol_boat (5 % HP) + destroyer", A = N("battleship", 1), B = L("river_patrol_boat", "destroyer"), HpB = new[] { 5, 100 }, Gap = 80f, Limit = 120f, Note = "main battery should prefer the destroyer" },
        new() { Set = "target", Name = "missile_destroyer vs torpedo_boat (10 % HP) + frigate", A = N("missile_destroyer", 1), B = L("torpedo_boat", "frigate"), HpB = new[] { 10, 100 }, Gap = 120f, Limit = 120f },
        new() { Set = "target", Name = "missile_destroyer x2 vs frigate (salvo overkill)", A = N("missile_destroyer", 2), B = N("frigate", 1), Gap = 120f, Limit = 90f, Note = "second salvo held while the first is in flight" },
        new() { Set = "target", Name = "torpedo_boat x3 vs frigate (torpedo overkill)", A = N("torpedo_boat", 3), B = N("frigate", 1), Gap = 60f, Limit = 90f },
        // ---- performance under missile saturation
        new() { Set = "perf", Name = "saturation: missile_destroyer x6 + missile_frigate x4 vs battleship + aa_destroyer x2 + ciws_escort_craft x2",
            A = L("battleship", "aa_destroyer", "aa_destroyer", "ciws_escort_craft", "ciws_escort_craft"), B = L("missile_destroyer", "missile_destroyer", "missile_destroyer", "missile_destroyer", "missile_destroyer", "missile_destroyer", "missile_frigate", "missile_frigate", "missile_frigate", "missile_frigate"),
            Gap = 135f, Limit = 120f },
    };

    // ------------------------------------------------------------------ maps

    /// <summary>The narrow lane: the coastal range with a 22 m channel at its east edge, one lane (near = mid = far).</summary>
    static MapDefinition Narrow()
    {
        var teams = new[] { new TeamStart(0, new Vector2(-56f, -56f)), new TeamStart(1, new Vector2(56f, 56f)) };
        var half = SandboxMaps.FlatSize * 0.5f;
        const float shore = 128f;
        var water = new List<PropPlacement>();
        for (var x = shore + SandboxMaps.WaterTile * 0.5f; x < half; x += SandboxMaps.WaterTile)
            for (var z = -half + SandboxMaps.WaterTile * 0.5f; z < half; z += SandboxMaps.WaterTile)
                water.Add(new PropPlacement("river_water", new Vector2(x, z), 0));
        var lanes = new List<SeaLaneDef>
        {
            new() { Id = "near", W = 139f, Patrol = 110f, End = 146f },
            new() { Id = "mid", W = 139f, Patrol = 110f, End = 146f },
            new() { Id = "far", W = 139f, Patrol = 110f, End = 146f },
        };
        var landings = new List<SeaLandingDef> { new() { At = new Vector2(shore + 1f, 0f), Inland = new Vector2(shore - 20f, 0f) } };
        var piers = new[] { new Vector2(shore - 4f, 0f) };
        var sea = SeaDef.Straight(new Vector2(0f, 1f), shore, -half, half, lanes, landings, piers, new Vector2(half - 4f, 0f));
        return new MapDefinition("naval_narrow", SandboxMaps.FlatSize, teams, water, Array.Empty<UnitPlacement>(), theme: "temperate") { Sea = sea };
    }

    static float LaneX(VehicleDef def, bool narrow)
    {
        if (narrow) return 139f;
        var lane = def.Naval?.Patrol;
        return lane == "far" ? SandboxMaps.LaneX[2] : lane == "mid" ? SandboxMaps.LaneX[1] : SandboxMaps.LaneX[0];
    }

    /// <summary>Where a unit of this kind starts: ships (and boats) on their lane, towers on the shore, aircraft and land units inland.</summary>
    static float ColumnX(VehicleDef def, bool narrow)
    {
        var shore = narrow ? 128f : SandboxMaps.Shore;
        if (def.Naval != null || def.Id.Contains("boat") || def.Id.Contains("gunboat")) return LaneX(def, narrow);
        if (def.Static) return shore - 8f;
        if (def.Flying) return shore - 50f;
        return shore - 70f;
    }

    static string[] Fill(string[] list, int budget)
    {
        if (budget <= 0) return list;
        var cost = list.Sum(id => Cat.Vehicles[id].CpCost);
        if (cost <= 0) return list;
        var outList = new List<string>();
        var total = 0;
        for (var i = 0; ; i++)
        {
            var id = list[i % list.Length];
            var cp = Cat.Vehicles[id].CpCost;
            if (total + cp > budget) break;
            outList.Add(id);
            total += cp;
        }
        return outList.Count > 0 ? outList.ToArray() : list;
    }

    static Catalog Cat;

    static readonly bool Trace = Environment.GetEnvironmentVariable("MB_TRACE") == "1";

    /// <summary>MB_ROW=text: only the matrix rows whose name contains it (diagnosis).</summary>
    static readonly string RowFilter = Environment.GetEnvironmentVariable("MB_ROW") ?? "";

    // ------------------------------------------------------------------ one run

    sealed class RunStats
    {
        public int Winner = -2;
        public double End, FirstShotA = -1, FirstShotB = -1, FirstHitOnLoser = -1, TimeToRangeA = -1, TimeToRangeB = -1;
        public int AliveA, AliveB, StartA, StartB;
        public float HpA, HpB;
        public readonly Dictionary<string, float> Damage = new();
        public readonly Dictionary<string, int> Shots = new();
        public int InterceptA, InterceptB, Switches, Stuck, OffWater, Reverse, TurnOver;
        public double RangeSumA, RangeSumB;
        public int RangeNA, RangeNB;
        public int BigSalvos, OverkillSalvos, CheapSalvos;
        public int PeakProjectiles;
        public double StepMsSum, StepMsMax;
        public int Steps;
        public float MinWreckClearance = float.PositiveInfinity;
        public ulong Hash;
        public string FirstMainTarget = "";
    }

    static RunStats RunOne(Row row, string[] a, string[] b, int seed)
    {
        var map = row.Narrow ? Narrow() : SandboxMaps.Coast();
        var s = new SandboxScenario { Name = row.Name, Map = SandboxMaps.CoastId, Seed = seed, Fog = false, Limit = row.Limit };
        s.Sides[0].Ai = SandboxAi.Combat;
        s.Sides[1].Ai = SandboxAi.Combat;
        var used = new Dictionary<(int team, float x), int>();
        void Put(string id, int team, int index)
        {
            var def = Cat.Vehicles[id];
            var x = ColumnX(def, row.Narrow);
            var k = used.TryGetValue((team, x), out var c) ? c : 0;
            used[(team, x)] = k + 1;
            var spacing = MathF.Max(16f, def.Length * 0.6f + 6f);
            var z = team == 0 ? -row.Gap * 0.5f - k * spacing : row.Gap * 0.5f + k * spacing;
            var hp = team == 1 && row.HpB != null && index < row.HpB.Length ? row.HpB[index] : 100;
            s.Units.Add(new SandboxUnit { Def = id, Team = team, Heading = team == 0 ? 0f : 180f, Position = new Vector2(x, z), Hp = hp });
        }
        for (var i = 0; i < a.Length; i++) Put(a[i], 0, i);
        for (var i = 0; i < b.Length; i++) Put(b[i], 1, i);
        // The wreck test keeps a held, immortal marker far up the lane so the battle runs on after the bait sinks.
        if (row.Wreck) s.Units.Add(new SandboxUnit { Def = "missile_boat", Team = 1, Heading = 180f, Position = new Vector2(row.Narrow ? 139f : SandboxMaps.LaneX[2], 140f), Immortal = true });

        var world = new SimWorld(Cat, map, seed);
        var battle = new SandboxBattle(s, null);
        battle.Setup(world);
        var r = new RunStats();
        var mine = new List<Vehicle>();
        for (var i = 0; i < battle.Spawned.Count; i++)
        {
            if (!world.TryGetVehicle(new EntityId(battle.Spawned[i]), out var v)) continue;
            var marker = row.Wreck && i == s.Units.Count - 1;
            if (marker || (row.HoldB && v.Team == 1) || (row.HoldA && v.Team == 0)) world.HoldFire(v, true);
            if (!marker) mine.Add(v);
        }
        r.StartA = mine.Count(v => v.Team == 0);
        r.StartB = mine.Count(v => v.Team == 1);
        var lastTarget = new Dictionary<EntityId, EntityId>();
        var lastHeading = new Dictionary<EntityId, float>();
        double firstHitA = -1, firstHitB = -1;
        DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
        {
            var side = by?.Team ?? -1;
            var key = (side == 0 ? "A:" : side == 1 ? "B:" : "?:") + (weapon?.Id ?? kind.ToString());
            r.Damage[key] = (r.Damage.TryGetValue(key, out var d) ? d : 0f) + amount;
            if (victim.Team == 0 && firstHitA < 0) firstHitA = world.Time;
            if (victim.Team == 1 && firstHitB < 0) firstHitB = world.Time;
        };
        var sw = new Stopwatch();
        var steps = (int)MathF.Ceiling((row.Limit + 3f) / Step);
        var sea = world.Map.Sea;
        try
        {
            for (var i = 0; i < steps && battle.Result == null; i++)
            {
                sw.Restart();
                battle.Tick(world, Step);
                world.Step(Step);
                sw.Stop();
                var ms = sw.Elapsed.TotalMilliseconds;
                r.StepMsSum += ms;
                r.StepMsMax = Math.Max(r.StepMsMax, ms);
                r.Steps++;
                r.PeakProjectiles = Math.Max(r.PeakProjectiles, world.Combat.InFlight.Count);
                foreach (var e in world.Events)
                {
                    if (e.Kind == SimEventKind.WeaponFired)
                    {
                        if (e.Team == 0 && r.FirstShotA < 0) r.FirstShotA = world.Time;
                        if (e.Team == 1 && r.FirstShotB < 0) r.FirstShotB = world.Time;
                        if (Trace && e.Mount == 0) Console.Error.WriteLine($"  t={world.Time:0.0} FIRE {e.Team}#{e.Entity.Value} {e.DefId}");
                        var key = (e.Team == 0 ? "A:" : "B:") + (e.DefId ?? "?");
                        r.Shots[key] = (r.Shots.TryGetValue(key, out var n) ? n : 0) + 1;
                        if (e.Mount == 0 && world.TryGetVehicle(e.Entity, out var shooter) && CombatRoleDoctrine.NavalSalvo(shooter.Def, shooter.Def.Weapon) &&
                            world.TryGetVehicle(shooter.Target, out var tgt))
                        {
                            r.BigSalvos++;
                            if (r.FirstMainTarget == "" && shooter.Team == 0) r.FirstMainTarget = tgt.Def.Id;
                            var w = shooter.Def.Weapon;
                            var alpha = w.Damage * Math.Max(1, w.Burst) * w.RoundsPerPull;
                            if (world.Combat.Committed(tgt.Id) - alpha > MathF.Max(1f, tgt.Hp) * 1.15f) r.OverkillSalvos++;
                            if (tgt.Def.CpCost < SimTunables.Ai.RoleDoctrine.NavalSalvoMinWorth && tgt.Def.Class is UnitClass.Light or UnitClass.Scout) r.CheapSalvos++;
                        }
                    }
                    else if (e.Kind == SimEventKind.Intercepted)
                    {
                        if (e.Team == 0) r.InterceptA++;
                        else if (e.Team == 1) r.InterceptB++;
                    }
                }
                world.ClearEvents();
                // MB_TRACE=1: every unit's place, order, target and health each second (diagnosis, stderr).
                if (Trace && world.Tick % 20 == 0)
                    foreach (var v in mine)
                    {
                        if (!v.IsAlive) continue;
                        var tgt = world.TryGetVehicle(v.Target, out var tv) ? $"{tv.Def.Id}@{Vector2.Distance(tv.Position, v.Position):0}" : "-";
                        Console.Error.WriteLine($"  t={world.Time:0} {v.Team}:{v.Def.Id}#{v.Id.Value} p=({v.Position.X:0},{v.Position.Y:0}) v={v.Speed:0.0} hp={v.Hp:0} ord={v.Order.Kind}({v.Order.Point.X:0},{v.Order.Point.Y:0}) tgt={tgt} scr={v.Scripted} cd0={v.Weapons[0].Cooldown:0.0} ammo0={v.Weapons[0].Ammo} los={(tv != null ? world.Combat.HasLineOfFire(v, tv, v.Def.Weapon) : false)} mh={SimMath.WrapAngle((v.MountHeading(0) - v.Heading)) * 57.3f:0}");
                    }
                // Per-unit samples every 0.5 s: target switches, range keeping, pathing.
                if (world.Tick % 10 != 0) continue;
                foreach (var v in mine)
                {
                    if (!v.IsAlive) continue;
                    if (v.Target.IsValid && lastTarget.TryGetValue(v.Id, out var was) && was.IsValid && was != v.Target) r.Switches++;
                    lastTarget[v.Id] = v.Target;
                    var main = v.Def.Weapon;
                    var nearest = float.MaxValue;
                    foreach (var o in mine)
                        if (o.IsAlive && o.Team != v.Team) nearest = MathF.Min(nearest, Vector2.Distance(o.Position, v.Position) - o.Radius);
                    if (main.Range > 0f && nearest <= main.Range)
                    {
                        if (v.Team == 0 && r.TimeToRangeA < 0) r.TimeToRangeA = world.Time;
                        if (v.Team == 1 && r.TimeToRangeB < 0) r.TimeToRangeB = world.Time;
                    }
                    if (v.Def.Naval != null && main.Range > 0f && world.TryGetVehicle(v.Target, out var t) && t.IsAlive)
                    {
                        var ratio = Vector2.Distance(t.Position, v.Position) / main.Range;
                        if (v.Team == 0) { r.RangeSumA += ratio; r.RangeNA++; }
                        else { r.RangeSumB += ratio; r.RangeNB++; }
                    }
                    if (v.Def.Naval == null) continue;
                    if (sea != null && !sea.IsSea(v.Position)) r.OffWater++;
                    if (v.Speed < -0.1f) r.Reverse++;
                    if (lastHeading.TryGetValue(v.Id, out var h0))
                    {
                        var turned = MathF.Abs(MathF.IEEERemainder(v.Heading - h0, MathF.PI * 2f));
                        if (turned > v.Def.TurnRate * v.TurnFactor * Step * 10f * 1.25f + 0.02f) r.TurnOver++;
                    }
                    lastHeading[v.Id] = v.Heading;
                    if (row.Wreck)
                        foreach (var wr in world.Wrecks.List)
                            if (wr.Naval && wr.Id != v.Id)
                                r.MinWreckClearance = MathF.Min(r.MinWreckClearance, Vector2.Distance(wr.Position, v.Position) - wr.Bound - v.Def.HullRadius);
                }
            }
        }
        finally { DamageSystem.DamageLog = null; }
        r.Winner = battle.Result is { } won ? won.WinningTeam : -2;
        r.End = battle.Result != null ? battle.EndedAt : world.Time;
        r.AliveA = mine.Count(v => v.Team == 0 && v.IsAlive);
        r.AliveB = mine.Count(v => v.Team == 1 && v.IsAlive);
        r.HpA = SandboxBattle.HealthShare(world, 0);
        r.HpB = SandboxBattle.HealthShare(world, 1);
        r.FirstHitOnLoser = r.Winner == 0 ? firstHitB : r.Winner == 1 ? firstHitA : -1;
        r.Stuck = battle.Stuck?.CountOver(battle.Stuck.Threshold) ?? 0;
        r.Hash = world.StateHash();
        return r;
    }

    // ------------------------------------------------------------------ the suite

    static string F(double v, string f = "0.0") => double.IsNaN(v) || double.IsInfinity(v) || v < 0 ? "-" : v.ToString(f, Inv);

    public static void Run(Catalog cat, StringBuilder sb, string set)
    {
        Cat = cat;
        var env = Environment.GetEnvironmentVariable("MB_SEEDS");
        if (!string.IsNullOrEmpty(env)) Seeds = env.Split(',').Select(int.Parse).ToArray();
        sb.AppendLine(string.Join("\t", "set", "matchup", "sideA", "sideB", "cpA", "cpB", "seeds", "expect", "winA", "winB", "draw", "verdict",
            "first_shot_A_s", "first_shot_B_s", "time_to_range_A_s", "time_to_range_B_s", "ttk_s", "end_s", "survivors_A", "survivors_B", "hp_left_A", "hp_left_B",
            "damage_by_source", "shots_by_weapon", "intercepts_A", "intercepts_B", "target_switches", "stuck", "off_water", "reverse", "turn_over_rate",
            "range_ratio_A", "range_ratio_B", "big_salvos", "overkill_salvos", "cheap_target_salvos", "first_main_target_A", "wreck_clearance_m",
            "peak_projectiles", "step_ms_avg", "step_ms_max", "hash_seed1", "note"));
        foreach (var row in Matrix)
        {
            if (set != "all" && row.Set != set) continue;
            if (RowFilter != "" && !row.Name.Contains(RowFilter)) continue;
            var a = Fill(row.A, row.Budget);
            var b = Fill(row.B, row.Budget);
            var missing = a.Concat(b).Where(id => !Cat.Vehicles.ContainsKey(id)).Distinct().ToList();
            if (missing.Count > 0) { sb.AppendLine($"{row.Set}\t{row.Name}\tMISSING {string.Join(",", missing)}"); continue; }
            var runs = new List<RunStats>();
            foreach (var seed in Seeds)
            {
                try { runs.Add(RunOne(row, a, b, seed)); }
                catch (Exception e) { sb.AppendLine($"{row.Set}\t{row.Name}\tERROR seed {seed} {e.GetType().Name}: {e.Message.Split('\n')[0]}"); break; }
            }
            if (runs.Count == 0) continue;
            var k = (double)runs.Count;
            int winA = runs.Count(x => x.Winner == 0), winB = runs.Count(x => x.Winner == 1);
            int draw = runs.Count - winA - winB;
            var verdict = row.Expect == "-" ? "record" : (row.Expect == "A" ? winA : winB) * 2 > runs.Count ? "as_expected" : "UNEXPECTED";
            string Top(Dictionary<string, float> d) => string.Join(" ", d.OrderByDescending(p => p.Value).Take(6).Select(p => $"{p.Key}={p.Value / k:0}"));
            var dmg = new Dictionary<string, float>();
            var shots = new Dictionary<string, float>();
            foreach (var x in runs)
            {
                foreach (var p in x.Damage) dmg[p.Key] = (dmg.TryGetValue(p.Key, out var v) ? v : 0f) + p.Value;
                foreach (var p in x.Shots) shots[p.Key] = (shots.TryGetValue(p.Key, out var v) ? v : 0f) + p.Value;
            }
            double Avg(Func<RunStats, double> f, bool positiveOnly = true)
            {
                var vals = runs.Select(f).Where(v => !positiveOnly || v >= 0).ToList();
                return vals.Count > 0 ? vals.Average() : -1;
            }
            var ttk = Avg(x => x.Winner >= 0 && x.FirstHitOnLoser >= 0 ? x.End - x.FirstHitOnLoser : -1);
            var cpA = a.Sum(id => Cat.Vehicles[id].CpCost);
            var cpB = b.Sum(id => Cat.Vehicles[id].CpCost);
            sb.AppendLine(string.Join("\t", row.Set, row.Name, string.Join("+", a), string.Join("+", b), cpA, cpB, runs.Count, row.Expect, winA, winB, draw, verdict,
                F(Avg(x => x.FirstShotA)), F(Avg(x => x.FirstShotB)), F(Avg(x => x.TimeToRangeA)), F(Avg(x => x.TimeToRangeB)), F(ttk), F(Avg(x => x.End)),
                F(Avg(x => x.AliveA), "0.0"), F(Avg(x => x.AliveB), "0.0"), F(Avg(x => x.HpA), "0.00"), F(Avg(x => x.HpB), "0.00"),
                Top(dmg), Top(shots), F(Avg(x => x.InterceptA)), F(Avg(x => x.InterceptB)), F(Avg(x => x.Switches)),
                F(Avg(x => x.Stuck)), F(Avg(x => x.OffWater)), F(Avg(x => x.Reverse)), F(Avg(x => x.TurnOver)),
                F(Avg(x => x.RangeNA > 0 ? x.RangeSumA / x.RangeNA : -1), "0.00"), F(Avg(x => x.RangeNB > 0 ? x.RangeSumB / x.RangeNB : -1), "0.00"),
                F(Avg(x => x.BigSalvos)), F(Avg(x => x.OverkillSalvos)), F(Avg(x => x.CheapSalvos)),
                runs[0].FirstMainTarget == "" ? "-" : runs[0].FirstMainTarget,
                F(Avg(x => float.IsInfinity(x.MinWreckClearance) ? -1 : Math.Max(0, x.MinWreckClearance)), "0.0"),
                runs.Max(x => x.PeakProjectiles), F(Avg(x => x.Steps > 0 ? x.StepMsSum / x.Steps : -1), "0.000"), F(runs.Max(x => x.StepMsMax), "0.0"),
                runs[0].Hash.ToString("x16"), row.Note));
            Console.Error.WriteLine(row.Name);
        }
    }

    // ------------------------------------------------------------------ the static economy table (no simulation)

    /// <summary>Intended prey and explicit counter per ship (spec sections 4-5): the prey sets the effective-DPS row, the counter the lifetime.</summary>
    static readonly (string ship, string prey, string counter)[] Roles =
    {
        ("river_patrol_boat", "torpedo_boat", "river_gunboat"), ("river_gunboat", "river_patrol_boat", "frigate"), ("hover_gunboat", "torpedo_boat", "sea_corvette"),
        ("missile_boat", "sea_corvette", "hover_gunboat"), ("sea_corvette", "ashm_corvette", "frigate"), ("sea_cruiser", "destroyer", "missile_destroyer"),
        ("torpedo_boat", "destroyer", "hover_gunboat"), ("ciws_escort_craft", "strike_drone", "sea_corvette"), ("ashm_corvette", "frigate", "sea_corvette"),
        ("aa_corvette", "attack_helicopter", "ashm_corvette"), ("ew_corvette", "missile_boat", "frigate"), ("frigate", "sea_corvette", "destroyer"),
        ("missile_frigate", "frigate", "gun_destroyer"), ("aa_frigate", "attack_jet", "missile_frigate"), ("rocket_artillery_ship", "gun_turret", "torpedo_boat"),
        ("naval_monitor", "gun_turret", "missile_destroyer"), ("destroyer", "frigate", "sea_cruiser.gun"), ("gun_destroyer", "frigate", "missile_destroyer"),
        ("missile_destroyer", "destroyer", "gun_destroyer"), ("aa_destroyer", "attack_jet", "gun_destroyer"), ("sea_cruiser.gun", "destroyer", "missile_destroyer"),
        ("sea_cruiser.missile", "destroyer", "battlecruiser"), ("battlecruiser", "sea_cruiser.gun", "battleship"), ("battleship", "battlecruiser", "missile_destroyer"),
    };

    static TargetKind KindOf(VehicleDef d) => d.Static ? TargetKind.Structure : d.Flying ? TargetKind.Air : TargetKind.Ground;

    /// <summary>The main battery: every mount carrying the main weapon (the battleship's three turrets).</summary>
    static int MainMounts(VehicleDef d) => Math.Max(1, d.Mounts.Count(m => m.Weapon.Id == d.Weapon.Id));

    static double Alpha(WeaponDef w) => w.Damage * Math.Max(1, w.Burst) * w.RoundsPerPull;

    /// <summary>Sustained rounds of damage a second: a burst every cooldown (after its last round), a clip and its reload.</summary>
    static double Dps(WeaponDef w)
    {
        if (w.Damage <= 0f) return 0;
        if (w.Clip > 0) return w.Clip * w.Damage * w.RoundsPerPull / (w.Clip * Math.Max(0.001, w.Cooldown) + w.ClipReload);
        var cycle = Math.Max(0.05, w.Cooldown + (Math.Max(1, w.Burst) - 1) * w.BurstInterval);
        return Alpha(w) / cycle;
    }

    static double EffDps(VehicleDef shooter, VehicleDef target)
    {
        var w = shooter.Weapon;
        if (!w.CanTarget(target.Flying)) return 0;
        if (shooter.NavalOnly && target.Naval == null) return 0;
        var mult = Cat.Damage.Effective(w, target.Armour.Front, KindOf(target));
        return Dps(w) * MainMounts(shooter) * mult;
    }

    public static void Economy(Catalog cat, StringBuilder sb)
    {
        Cat = cat;
        sb.AppendLine(string.Join("\t", "ship", "cp", "hp", "armour_F", "speed", "primary", "main_mounts", "pen", "alpha", "alpha_per_cp", "dps_raw", "hp_per_cp",
            "prey", "prey_armour_F", "eff_mult_vs_prey", "eff_dps_vs_prey", "eff_dps_per_cp", "aps_charges", "aps_recharge_s", "intercepts_per_min", "intercepts_per_min_per_cp",
            "counter", "counter_eff_dps", "lifetime_vs_counter_s", "secondary"));
        foreach (var (ship, prey, counter) in Roles)
        {
            if (!Cat.Vehicles.TryGetValue(ship, out var d)) { sb.AppendLine(ship + "\tMISSING"); continue; }
            var w = d.Weapon;
            var p = Cat.Vehicles.TryGetValue(prey, out var pd) ? pd : null;
            var c = Cat.Vehicles.TryGetValue(counter, out var cd) ? cd : null;
            var cp = d.CpCost;
            var alpha = Alpha(w) * MainMounts(d);
            var eff = p != null ? EffDps(d, p) : 0;
            var mult = p != null && w.CanTarget(p.Flying) ? Cat.Damage.Effective(w, p.Armour.Front, KindOf(p)) : 0;
            var perMin = d.Aps != null ? d.Aps.Charges + (d.Aps.Recharge > 0 ? 60.0 / d.Aps.Recharge : 0) : 0;
            var ceff = c != null ? EffDps(c, d) : 0;
            string PerCp(double v) => cp > 0 ? (v / cp).ToString("0.00", Inv) : "n/a (cp 0)";
            var sec = string.Join(",", d.Mounts.Skip(1).Where(m => m.Weapon.Id != w.Id).Select(m => m.Weapon.Id).Distinct());
            sb.AppendLine(string.Join("\t", ship, cp, d.MaxHp.ToString("0", Inv), d.Armour.Front, d.Speed.ToString("0.0", Inv), w.Id, MainMounts(d), w.Penetration,
                alpha.ToString("0", Inv), PerCp(alpha), (Dps(w) * MainMounts(d)).ToString("0.0", Inv), PerCp(d.MaxHp),
                prey, p?.Armour.Front.ToString() ?? "-", mult.ToString("0.00", Inv), eff.ToString("0.0", Inv), PerCp(eff),
                d.Aps?.Charges.ToString() ?? "-", d.Aps?.Recharge.ToString("0.0", Inv) ?? "-", perMin.ToString("0.0", Inv), PerCp(perMin),
                counter, ceff.ToString("0.0", Inv), ceff > 0 ? (d.MaxHp / ceff).ToString("0", Inv) : "inf", sec));
        }
    }
}
