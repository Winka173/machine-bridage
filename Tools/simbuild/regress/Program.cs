// Balance master final (06/10): headless regression harness over the engine-free Sim (no Unity). Ports of the EditMode
// measures (ArmourBalanceMeasure.Run, CombatValueMeasure.PrintPointDefenceValue) plus dumps of the runtime-effective data.
// Usage: Harness <mode> <balance.json> <tunables.json> <out file> [campaign.json]
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.Json;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

static class P
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static Catalog Cat;
    static int[] Seeds = { 1, 2, 3 };

    static int Main(string[] a)
    {
        var mode = a[0];
        SimTunables.Apply(File.ReadAllText(a[2]));
        Cat = Catalog.FromJson(File.ReadAllText(a[1]));
        var outFile = a[3];
        if (a.Length > 4) Console.WriteLine("campaign missions: " + MissionDef.ListFromJson(File.ReadAllText(a[4])).Count);
        var env = Environment.GetEnvironmentVariable("MB_SEEDS");
        if (!string.IsNullOrEmpty(env)) Seeds = env.Split(',').Select(int.Parse).ToArray();
        var sb = new StringBuilder();
        switch (mode)
        {
            case "load": sb.AppendLine($"OK {Cat.Vehicles.Count} vehicles, {Cat.Weapons.Count} weapons, {Cat.Supports.Count} supports"); break;
            case "dump": Dump(sb); break;
            case "ttk": Ttk(sb, Environment.GetEnvironmentVariable("MB_SET") ?? "all"); break;
            case "pd": PointDefence(sb); break;
            case "barrage": Barrage(sb); break;
            case "pressure": Pressure(sb); break;
            case "aps": Aps(sb); Lead(sb); break;
            default: Console.Error.WriteLine("mode?"); return 2;
        }
        File.WriteAllText(outFile, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine(sb.Length > 3000 ? sb.ToString(0, 3000) + "..." : sb.ToString());
        return 0;
    }

    // ------------------------------------------------------------------ dump: runtime-effective values by reflection
    static object Plain(object o, int depth = 0)
    {
        if (o == null) return null;
        var t = o.GetType();
        if (t.IsPrimitive || o is string || t.IsEnum || o is decimal) return t.IsEnum ? o.ToString() : o;
        if (depth > 1) return o.ToString();
        var d = new SortedDictionary<string, object>();
        foreach (var p in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            if (p.GetIndexParameters().Length > 0) continue;
            var pt = p.PropertyType;
            object v;
            try { v = p.GetValue(o); } catch { continue; }
            if (v == null) continue;
            if (pt.IsPrimitive || pt == typeof(string) || pt.IsEnum) d[p.Name] = pt.IsEnum ? v.ToString() : v;
            else if (p.Name is "Armour" or "Cluster" or "Aps") d[p.Name] = Plain(v, depth + 1);
        }
        return d;
    }

    static void Dump(StringBuilder sb)
    {
        var o = new Dictionary<string, object>
        {
            ["weapons"] = Cat.Weapons.ToDictionary(k => k.Key, k => Plain(k.Value)),
            ["vehicles"] = Cat.Vehicles.ToDictionary(k => k.Key, k => Plain(k.Value)),
            ["supports"] = Cat.Supports.ToDictionary(k => k.Key, k => Plain(k.Value)),
        };
        sb.Append(JsonSerializer.Serialize(o, new JsonSerializerOptions { WriteIndented = false }));
    }

    // ------------------------------------------------------------------ TTK (port of ArmourBalanceMeasure.Run)
    sealed class M
    {
        public string Set, Name;
        public string[] S, T;
        public float D = 24f, Limit = 120f;
        public DuelFacing F = DuelFacing.Front;
        public SandboxAi SAi = SandboxAi.Idle, TAi = SandboxAi.Idle;
        public bool Both;
    }

    static string[] N(string id, int n) => Enumerable.Repeat(id, n).ToArray();
    static string[] L(params string[] ids) => ids;

    static readonly M[] Matrix =
    {
        // ground
        new() { Set = "ground", Name = "MBT vs Heavy (front)", S = N("main_battle_tank", 1), T = N("heavy_tank", 1) },
        new() { Set = "ground", Name = "MBT vs Heavy (flank)", S = N("main_battle_tank", 1), T = N("heavy_tank", 1), F = DuelFacing.Side },
        new() { Set = "ground", Name = "Heavy vs MBT (front)", S = N("heavy_tank", 1), T = N("main_battle_tank", 1) },
        new() { Set = "ground", Name = "MBT vs MBT (front)", S = N("main_battle_tank", 1), T = N("main_battle_tank", 1) },
        new() { Set = "ground", Name = "MBT vs MBT duel (both fire)", S = N("main_battle_tank", 1), T = N("main_battle_tank", 1), Both = true },
        new() { Set = "ground", Name = "Heavy vs TD (front)", S = N("heavy_tank", 1), T = N("tank_destroyer", 1) },
        new() { Set = "ground", Name = "TD vs Heavy (front)", S = N("tank_destroyer", 1), T = N("heavy_tank", 1), D = 30f },
        new() { Set = "ground", Name = "Heavy vs TD duel (both fire)", S = N("heavy_tank", 1), T = N("tank_destroyer", 1), D = 30f, Both = true },
        new() { Set = "ground", Name = "TD vs Titan (front)", S = N("tank_destroyer", 1), T = N("titan_tank", 1), D = 30f },
        new() { Set = "ground", Name = "TD vs Titan (flank)", S = N("tank_destroyer", 1), T = N("titan_tank", 1), D = 30f, F = DuelFacing.Side },
        new() { Set = "ground", Name = "Flame Tank assault: 2 flame vs MG bunker", S = N("flame_tank", 2), T = N("mg_bunker", 1), D = 12f },
        new() { Set = "ground", Name = "Flame Tank assault: 2 flame vs 2 IFV", S = N("flame_tank", 2), T = N("ifv", 2), D = 12f },
        new() { Set = "ground", Name = "Flame Tank survives: 2 IFV vs flame tank", S = N("ifv", 2), T = N("flame_tank", 1), D = 20f },
        new() { Set = "ground", Name = "Breacher vs HESCO wall", S = N("armored_bulldozer", 1), T = N("wall_hesco", 1), D = 6f, SAi = SandboxAi.Combat },
        new() { Set = "ground", Name = "Breacher vs T-wall", S = N("armored_bulldozer", 1), T = N("wall_t", 1), D = 6f, SAi = SandboxAi.Combat },
        new() { Set = "ground", Name = "MBT vs bulldozer (breacher survival)", S = N("main_battle_tank", 1), T = N("armored_bulldozer", 1) },
        new() { Set = "ground", Name = "Railgun vs MBT (armour 4)", S = N("railgun_truck", 1), T = N("main_battle_tank", 1), D = 40f },
        new() { Set = "ground", Name = "Railgun vs Titan (armour 5)", S = N("railgun_truck", 1), T = N("titan_tank", 1), D = 40f },
        // air
        new() { Set = "air", Name = "SHORAD (aa_vehicle) vs attack helicopter", S = N("aa_vehicle", 1), T = N("attack_helicopter", 1), D = 30f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "SHORAD (heavy_aa) vs attack helicopter", S = N("heavy_aa", 1), T = N("attack_helicopter", 1), D = 40f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "Attack helicopter vs aa_vehicle", S = N("attack_helicopter", 1), T = N("aa_vehicle", 1), D = 40f },
        new() { Set = "air", Name = "SAM (sam_launcher) vs attack jet", S = N("sam_launcher", 1), T = N("attack_jet", 1), D = 60f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "SAM (long_sam) vs attack jet", S = N("long_sam", 1), T = N("attack_jet", 1), D = 70f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "Fighter vs fighter (AAM)", S = N("fighter_jet", 1), T = N("fighter_jet", 1), D = 60f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "Fighter vs attack helicopter (AAM)", S = N("fighter_jet", 1), T = N("attack_helicopter", 1), D = 60f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "Heavy bomber survival vs long_sam", S = N("long_sam", 1), T = N("heavy_bomber", 1), D = 70f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "Heavy bomber survival vs heavy_aa", S = N("heavy_aa", 1), T = N("heavy_bomber", 1), D = 50f, TAi = SandboxAi.Combat },
        new() { Set = "air", Name = "Sortie: attack jet vs 3 MBT", S = N("attack_jet", 1), T = N("main_battle_tank", 3), D = 70f, Limit = 90f },
        new() { Set = "air", Name = "Sortie: heavy bomber vs 4 IFV", S = N("heavy_bomber", 1), T = N("ifv", 4), D = 70f, Limit = 90f },
        new() { Set = "air", Name = "Sortie: stealth bomber vs gun turret", S = N("stealth_bomber", 1), T = N("gun_turret", 1), D = 70f, Limit = 90f },
        new() { Set = "air", Name = "Sortie: attack helicopter vs 2 MBT", S = N("attack_helicopter", 1), T = N("main_battle_tank", 2), D = 50f, Limit = 90f },
        new() { Set = "air", Name = "Sortie: sky gunship vs 4 armoured cars", S = N("sky_gunship", 1), T = N("armored_car", 4), D = 60f, Limit = 90f },
        // towers and structures
        new() { Set = "tower", Name = "Assault squad (2 MBT + IFV) vs guard tower (small)", S = L("main_battle_tank", "main_battle_tank", "ifv"), T = N("guard_tower", 1) },
        new() { Set = "tower", Name = "Assault squad vs gun turret (medium)", S = L("main_battle_tank", "main_battle_tank", "ifv"), T = N("gun_turret", 1) },
        new() { Set = "tower", Name = "Assault squad vs heavy turret (large)", S = L("main_battle_tank", "main_battle_tank", "ifv"), T = N("heavy_turret", 1) },
        new() { Set = "tower", Name = "Gun turret vs 2 MBT (tower damage)", S = N("gun_turret", 1), T = N("main_battle_tank", 2) },
        new() { Set = "tower", Name = "MG bunker vs 3 armoured cars (tower damage)", S = N("mg_bunker", 1), T = N("armored_car", 3), D = 22f },
        new() { Set = "tower", Name = "Gun turret vs assault squad (both fire)", S = N("gun_turret", 1), T = L("main_battle_tank", "main_battle_tank", "ifv"), Both = true },
        new() { Set = "tower", Name = "Bomber vs gun turret (medium)", S = N("heavy_bomber", 1), T = N("gun_turret", 1), D = 70f },
        new() { Set = "tower", Name = "Bomber vs heavy turret (large)", S = N("heavy_bomber", 1), T = N("heavy_turret", 1), D = 70f },
        new() { Set = "tower", Name = "2 SP howitzers vs gun turret", S = N("artillery", 2), T = N("gun_turret", 1), D = 60f },
        new() { Set = "tower", Name = "Thermobaric launcher vs MG bunker", S = N("thermobaric_launcher", 1), T = N("mg_bunker", 1), D = 40f },
        new() { Set = "tower", Name = "Breacher (bulldozer) vs MG bunker", S = N("armored_bulldozer", 1), T = N("mg_bunker", 1), D = 8f, SAi = SandboxAi.Combat },
        new() { Set = "tower", Name = "Attack jet bombs vs repair bay (utility)", S = N("attack_jet", 1), T = N("repair_bay", 1), D = 70f },
        new() { Set = "tower", Name = "4 MBT + 2 SP howitzers vs HQ", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "main_battle_tank", "artillery", "artillery"), T = N("headquarters", 1), D = 30f, Limit = 240f },
        // fire support
        new() { Set = "fire", Name = "2 mortar carriers vs 4 armoured cars", S = N("mortar_carrier", 2), T = N("armored_car", 4), D = 55f },
        new() { Set = "fire", Name = "AMOS (sp_mortar) vs 4 armoured cars", S = N("sp_mortar", 1), T = N("armored_car", 4), D = 55f },
        new() { Set = "fire", Name = "Siege tank 240 mm vs 4 IFV", S = N("siege_tank", 1), T = N("ifv", 4), D = 55f },
        new() { Set = "fire", Name = "2 SP howitzers vs 4 armoured cars (formation)", S = N("artillery", 2), T = N("armored_car", 4), D = 60f },
        new() { Set = "fire", Name = "2 SP howitzers vs 2 MBT", S = N("artillery", 2), T = N("main_battle_tank", 2), D = 60f },
        new() { Set = "fire", Name = "2 MLRS vs 4 IFV", S = N("mlrs", 2), T = N("ifv", 4), D = 70f },
        new() { Set = "fire", Name = "2 MLRS vs 2 MBT", S = N("mlrs", 2), T = N("main_battle_tank", 2), D = 70f },
        new() { Set = "fire", Name = "Elite MLRS (cluster) vs 4 armoured cars", S = N("elite_mlrs", 1), T = N("armored_car", 4), D = 60f },
        new() { Set = "fire", Name = "Elite Grad (cluster) vs 4 armoured cars", S = N("elite_grad", 1), T = N("armored_car", 4), D = 60f },
        new() { Set = "fire", Name = "TOS vs 4 IFV (unchanged)", S = N("thermobaric_launcher", 1), T = N("ifv", 4), D = 40f },
        new() { Set = "fire", Name = "Counter-battery duel: SP howitzer vs SP howitzer", S = N("artillery", 1), T = N("artillery", 1), D = 80f, Both = true, TAi = SandboxAi.Combat, Limit = 180f },
        new() { Set = "fire", Name = "Counter-battery duel: MLRS vs SP howitzer", S = N("mlrs", 1), T = N("artillery", 1), D = 80f, Both = true, TAi = SandboxAi.Combat, Limit = 180f },
        // bosses (held fire: TTK)
        new() { Set = "boss", Name = "Army vs Behemoth (main)", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "artillery"), T = N("behemoth", 1), D = 40f, Limit = 150f },
        new() { Set = "boss", Name = "Army vs Mobile Fortress (main)", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "artillery"), T = N("mobile_fortress", 1), D = 40f, Limit = 150f },
        new() { Set = "boss", Name = "Army vs Fortress Bastion (main)", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "artillery"), T = N("fortress_bastion", 1), D = 40f, Limit = 150f },
        new() { Set = "boss", Name = "Army vs Behemoth Inferno (mini)", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "artillery"), T = N("behemoth_inferno", 1), D = 40f, Limit = 150f },
        new() { Set = "boss", Name = "Army vs Behemoth Mk0 (mini)", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "artillery"), T = N("behemoth_mk0", 1), D = 40f, Limit = 150f },
        new() { Set = "boss", Name = "Army vs Earth Borer (mini)", S = L("main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "artillery"), T = N("earth_borer", 1), D = 40f, Limit = 150f },
    };

    sealed class R { public double Ttk; public bool Killed; public double Seconds; public int Winner; public int Hits; public float Dealt; }

    static R RunOne(SandboxScenario s, float seconds, bool holdTargets, bool both)
    {
        var world = new SimWorld(Cat, SandboxMaps.Flat(), s.Seed);
        var battle = new SandboxBattle(s, null);
        battle.Setup(world);
        var r = new R();
        var targetHp = 0f;
        foreach (var v in world.Vehicles)
        {
            if (v.Team != 1) continue;
            targetHp += v.MaxHp;
            if (holdTargets) world.HoldFire(v, true);
        }
        double first = -1;
        var dealt = 0f;
        world.HitLog = h =>
        {
            if (h.VictimTeam != 1) return;
            if (first < 0) first = world.Time;
            dealt += h.Dealt;
            r.Hits++;
        };
        var n = (int)MathF.Ceiling(seconds / SandboxLab.Step);
        for (var i = 0; i < n && battle.Result == null; i++)
        {
            battle.Tick(world, SandboxLab.Step);
            world.Step(SandboxLab.Step);
            world.ClearEvents();
        }
        var end = battle.Result != null ? battle.EndedAt : world.Time;
        r.Seconds = end;
        r.Winner = battle.Result is { } won ? won.WinningTeam : -2;
        r.Killed = r.Winner == 0;
        r.Dealt = dealt;
        if (first < 0) r.Ttk = double.PositiveInfinity;
        else if (r.Killed) r.Ttk = end - first;
        else r.Ttk = dealt > 0f ? (end - first) * targetHp / dealt : double.PositiveInfinity;
        return r;
    }

    static void Ttk(StringBuilder sb, string set)
    {
        sb.AppendLine("set\tmatchup\tttk_s\tkilled\twinner_side0_share\tavg_end_s\thits\tdealt");
        foreach (var m in Matrix)
        {
            if (set != "all" && m.Set != set) continue;
            var runs = new List<R>();
            foreach (var seed in Seeds)
            {
                try
                {
                    var s = SandboxLab.DuelScenario(Cat, m.S, m.T, m.D, m.F, seed, m.Limit);
                    s.Sides[0].Ai = m.SAi;
                    s.Sides[1].Ai = m.TAi;
                    if (m.Both) { s.Sides[0].Ai = SandboxAi.Combat; s.Sides[1].Ai = SandboxAi.Combat; }
                    if (m.S.Any(id => Cat.Vehicles.TryGetValue(id, out var d) && (d.Flying || d.Mounts.Any(x => x.Weapon.MinRange > 0f))))
                        s.Sides[0].Ai = SandboxAi.Combat;
                    runs.Add(RunOne(s, m.Limit + 1f, !m.Both, m.Both));
                }
                catch (Exception e) { sb.AppendLine($"{m.Set}\t{m.Name}\tERROR {e.GetType().Name}: {e.Message.Split('\n')[0]}"); break; }
            }
            if (runs.Count == 0) continue;
            var fin = runs.Where(x => !double.IsInfinity(x.Ttk)).Select(x => x.Ttk).ToList();
            var ttk = fin.Count > 0 ? fin.Average() : double.PositiveInfinity;
            var killed = runs.Count(x => x.Killed);
            var mark = killed < runs.Count ? "~" : "";
            sb.AppendLine(string.Join("\t", m.Set, m.Name, double.IsInfinity(ttk) ? "none" : mark + ttk.ToString("0.0", Inv), $"{killed}/{runs.Count}",
                (runs.Count(x => x.Winner == 0) / (double)runs.Count).ToString("0.00", Inv), runs.Average(x => x.Seconds).ToString("0.0", Inv),
                runs.Average(x => x.Hits).ToString("0", Inv), runs.Average(x => x.Dealt).ToString("0", Inv)));
            Console.Error.WriteLine(m.Name);
        }
    }

    // ------------------------------------------------------------------ point defence (port of PrintPointDefenceValue)
    static SimWorld Field(int seed) =>
        new SimWorld(Cat, new MapDefinition("range", 300f,
            new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
            new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

    static void PointDefence(StringBuilder sb)
    {
        sb.AppendLine("fire\tguard\ttanks_hp_lost_45s\tinterceptions\tdiverted_rounds\tshots_fired");
        foreach (var (fire, attackers, dist) in new[]
                 {
                     ("direct (ATGM, heli, FPV)", new[] { "ifv", "ifv", "attack_helicopter", "fpv_carrier", "fpv_carrier" }, 38f),
                     ("lobbed (MLRS, howitzer, mortar, Shahed)", new[] { "mlrs", "artillery", "mortar_carrier", "shahed_truck" }, 70f),
                     ("missiles (TD? no: ATGM tower-free: 2 IFV + light tank + strike drone)", new[] { "ifv", "ifv", "light_tank", "strike_drone" }, 34f),
                 })
            foreach (var guard in new[] { "none", "c_ram", "c_ram.centurion", "c_ram.dome", "iron_beam", "aa_vehicle", "laser_ad_station" })
            {
                float lost = 0f, inter = 0f, div = 0f, shots = 0f;
                foreach (var seed in Seeds)
                {
                    var world = Field(seed + 12);
                    world.RevealAll = true;
                    var tanks = new List<Vehicle>();
                    for (var i = 0; i < 4; i++)
                    {
                        var t = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-18f + i * 12f, 0f), 0f);
                        world.MakeSparring(t);
                        t.HoldFire = true;
                        tanks.Add(t);
                    }
                    if (guard != "none")
                    {
                        var g = world.SpawnVehicle(guard, 0, new Vector2(0f, -8f), 0f);
                        if (g.Def.Static) world.AnchorDefence(g);
                        world.MakeSparring(g);
                    }
                    for (var i = 0; i < attackers.Length; i++)
                    {
                        var at = world.SpawnVehicle(attackers[i], 1, new Vector2(-20f + i * 8f, attackers[i] is "mlrs" or "artillery" or "shahed_truck" or "mortar_carrier" ? dist : 38f), MathF.PI);
                        world.MakeSparring(at);
                        world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Attack, 1, new[] { at.Id }, tanks[i % 4].Position, tanks[i % 4].Id));
                    }
                    var taken = 0f;
                    DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (victim.Team == 0 && tanks.Contains(victim)) taken += amount; };
                    try
                    {
                        for (var t = 0f; t < 45f; t += 0.05f)
                        {
                            world.Step(0.05f);
                            foreach (var e in world.Events)
                            {
                                if (e.Kind == SimEventKind.Intercepted && e.Team == 0) inter++;
                                if (e.Kind == SimEventKind.RoundDiverted) div++;
                                if (e.Kind == SimEventKind.WeaponFired && e.Team == 1) shots++;
                            }
                            world.ClearEvents();
                        }
                    }
                    finally { DamageSystem.DamageLog = null; }
                    lost += taken;
                }
                var k = Seeds.Length;
                sb.AppendLine($"{fire}\t{guard}\t{lost / k:0}\t{inter / k:0.0}\t{div / k:0.0}\t{shots / k:0.0}");
                Console.Error.WriteLine(fire + " " + guard);
            }
        // Flares and jammer: SAMs and AAMs against aircraft that cannot die, 60 s: hits, damage, diverted rounds (flare decoys).
        sb.AppendLine();
        sb.AppendLine("air_defence\ttarget\tdamage_60s\thits\tdiverted\tshots");
        foreach (var (shooter, target, d) in new[]
                 {
                     ("sam_launcher", "attack_helicopter", 45f), ("sam_launcher", "attack_jet", 55f), ("long_sam", "attack_jet", 70f), ("aa_vehicle", "attack_helicopter", 30f),
                     ("manpads_tower", "attack_helicopter", 35f), ("missile_battery", "heavy_bomber", 70f), ("heavy_aa", "fighter_jet", 45f), ("fighter_jet", "attack_helicopter", 50f),
                 })
        {
            foreach (var jam in new[] { false, true })
            {
                float dmg = 0, hits = 0, div = 0, shots = 0;
                foreach (var seed in Seeds)
                {
                    var world = Field(seed + 30);
                    world.RevealAll = true;
                    var s = world.SpawnVehicle(shooter, 0, new Vector2(0f, -10f), 0f);
                    if (s.Def.Static) world.AnchorDefence(s);
                    world.MakeSparring(s);
                    var t = world.SpawnVehicle(target, 1, new Vector2(0f, d), MathF.PI);
                    world.MakeSparring(t);
                    t.HoldFire = true;
                    if (jam) { var j = world.SpawnVehicle("ew_jammer", 1, new Vector2(6f, d - 4f), MathF.PI); world.MakeSparring(j); j.HoldFire = true; }
                    var taken = 0f; var n = 0;
                    DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (victim == t) { taken += amount; n++; } };
                    try
                    {
                        for (var x = 0f; x < 60f; x += 0.05f)
                        {
                            world.Step(0.05f);
                            foreach (var e in world.Events)
                            {
                                if (e.Kind == SimEventKind.RoundDiverted) div++;
                                if (e.Kind == SimEventKind.WeaponFired && e.Team == 0) shots++;
                            }
                            world.ClearEvents();
                        }
                    }
                    finally { DamageSystem.DamageLog = null; }
                    dmg += taken; hits += n;
                }
                var k = Seeds.Length;
                sb.AppendLine($"{shooter}{(jam ? " (+enemy ew_jammer)" : "")}\t{target}\t{dmg / k:0}\t{hits / k:0.0}\t{div / k:0.0}\t{shots / k:0.0}");
                Console.Error.WriteLine(shooter + " " + target + " " + jam);
            }
        }
    }

    // ------------------------------------------------------------------ vehicle APS: 2 undying Titans (APS) under guided fire
    static void Aps(StringBuilder sb)
    {
        sb.AppendLine("aps_target\tattackers\thp_lost_45s\taps_interceptions\tshots");
        foreach (var (name, attackers) in new[]
                 {
                     ("ATGM / missile", new[] { "ifv", "ifv", "light_tank", "strike_drone", "attack_helicopter" }),
                     ("rockets / lobbed", new[] { "mlrs", "rocket_technical", "mortar_carrier" }),
                 })
        {
            float lost = 0, inter = 0, shots = 0;
            foreach (var seed in Seeds)
            {
                var world = Field(seed + 70);
                world.RevealAll = true;
                var tanks = new List<Vehicle>();
                for (var i = 0; i < 2; i++)
                {
                    var t = world.SpawnVehicle("titan_tank", 0, new Vector2(-8f + i * 16f, 0f), 0f);
                    world.MakeSparring(t); t.HoldFire = true; tanks.Add(t);
                }
                for (var i = 0; i < attackers.Length; i++)
                {
                    var lobbed = attackers[i] is "mlrs" or "rocket_technical" or "mortar_carrier";
                    var at = world.SpawnVehicle(attackers[i], 1, new Vector2(-16f + i * 8f, lobbed ? 45f : 32f), MathF.PI);
                    world.MakeSparring(at);
                    world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Attack, 1, new[] { at.Id }, tanks[i % 2].Position, tanks[i % 2].Id));
                }
                var taken = 0f;
                DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (tanks.Contains(victim)) taken += amount; };
                try
                {
                    for (var t = 0f; t < 45f; t += 0.05f)
                    {
                        world.Step(0.05f);
                        foreach (var e in world.Events)
                        {
                            if (e.Kind == SimEventKind.Intercepted && e.Team == 0) inter++;
                            if (e.Kind == SimEventKind.WeaponFired && e.Team == 1) shots++;
                        }
                        world.ClearEvents();
                    }
                }
                finally { DamageSystem.DamageLog = null; }
                lost += taken;
            }
            var k = Seeds.Length;
            sb.AppendLine($"titan_tank x2\t{name}\t{lost / k:0}\t{inter / k:0.0}\t{shots / k:0.0}");
        }
    }

    // ------------------------------------------------------------------ AI lead / intercept: hit share on a crossing target
    static void Lead(StringBuilder sb)
    {
        sb.AppendLine();
        sb.AppendLine("shooter\tmoving_target\tshots\thits\thit_share\tdamage_60s");
        foreach (var (shooter, target, d) in new[]
                 {
                     ("main_battle_tank", "armored_car", 22f), ("ifv", "main_battle_tank", 22f), ("tank_destroyer", "armored_car", 32f), ("light_tank", "main_battle_tank", 28f),
                     ("aa_vehicle", "attack_helicopter", 30f), ("sam_launcher", "attack_helicopter", 45f), ("heavy_aa", "attack_helicopter", 40f), ("atgm_tower", "main_battle_tank", 34f),
                     ("artillery", "armored_car", 60f), ("mortar_carrier", "armored_car", 40f), ("mlrs", "ifv", 70f),
                 })
        {
            float hits = 0, shots = 0, dmg = 0;
            foreach (var seed in Seeds)
            {
                var world = Field(seed + 90);
                world.RevealAll = true;
                var s = world.SpawnVehicle(shooter, 0, new Vector2(0f, -10f), 0f);
                if (s.Def.Static) world.AnchorDefence(s);
                world.MakeSparring(s);
                var t = world.SpawnVehicle(target, 1, new Vector2(-20f, d), MathF.PI / 2);
                world.MakeSparring(t);
                t.HoldFire = true;
                // Crossing: back and forth across the shooter's front.
                var leg = 0;
                var n = 0; var taken = 0f;
                DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (victim == t) { taken += amount; n++; } };
                try
                {
                    for (var x = 0f; x < 60f; x += 0.05f)
                    {
                        if ((int)(x / 12f) != leg || x == 0f)
                        {
                            leg = (int)(x / 12f);
                            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 1, new[] { t.Id }, new Vector2(leg % 2 == 0 ? 20f : -20f, d)));
                        }
                        world.Step(0.05f);
                        foreach (var e in world.Events)
                            if (e.Kind == SimEventKind.WeaponFired && e.Team == 0) shots++;
                        world.ClearEvents();
                    }
                }
                finally { DamageSystem.DamageLog = null; }
                hits += n; dmg += taken;
            }
            var k = Seeds.Length;
            sb.AppendLine($"{shooter}\t{target}\t{shots / k:0.0}\t{hits / k:0.0}\t{(shots > 0 ? hits / shots : 0):0.00}\t{dmg / k:0}");
        }
    }

    // ------------------------------------------------------------------ support barrage value (card vs scripted)
    static void Barrage(StringBuilder sb)
    {
        sb.AppendLine("support\ttargets\tdamage_mean_over_seeds\tseeds");
        var seeds = Enumerable.Range(1, 40).ToArray();
        foreach (var id in new[] { "artillery_barrage", "scripted_barrage", "hq_barrage" })
        {
            if (!Cat.Supports.TryGetValue(id, out var sup)) { sb.AppendLine($"{id}\t(missing)"); continue; }
            foreach (var (name, pos) in new[]
                     {
                         ("1 MBT at the centre", new[] { new Vector2(0, 0) }),
                         ("4 IFV formation (6 m)", new[] { new Vector2(-3, -3), new Vector2(3, -3), new Vector2(-3, 3), new Vector2(3, 3) }),
                         ("4 armoured cars spread (12 m)", new[] { new Vector2(-6, -6), new Vector2(6, -6), new Vector2(-6, 6), new Vector2(6, 6) }),
                     })
            {
                double total = 0;
                foreach (var seed in seeds)
                {
                    var world = Field(seed);
                    var kind = name.Contains("MBT") ? "main_battle_tank" : name.Contains("IFV") ? "ifv" : "armored_car";
                    var vs = pos.Select(p => { var v = world.SpawnVehicle(kind, 1, p, 0f); world.MakeSparring(v); v.HoldFire = true; return v; }).ToList();
                    var taken = 0f;
                    DamageSystem.DamageLog = (by, victim, amount, k, w) => { if (vs.Contains(victim)) taken += amount; };
                    try
                    {
                        world.Strikes.Launch(sup, 0, Vector2.Zero, new Vector2(0, 1));
                        for (var t = 0f; t < 12f; t += 0.05f) { world.Step(0.05f); world.ClearEvents(); }
                    }
                    finally { DamageSystem.DamageLog = null; }
                    total += taken;
                }
                sb.AppendLine($"{id}\t{name}\t{total / seeds.Length:0}\t{seeds.Length}");
            }
        }
    }

    // ------------------------------------------------------------------ boss pressure: damage a boss deals to undying tanks
    static void Pressure(StringBuilder sb)
    {
        sb.AppendLine("boss\tdamage_to_6_undying_MBT_60s\tseeds\tnote");
        foreach (var boss in new[] { "behemoth", "mobile_fortress", "nuke_train", "nyx", "scylla", "leviathan", "moloch", "monster", "kraken", "earth_borer", "behemoth_inferno", "fortress_bastion" })
        {
            double total = 0; var note = "";
            var ok = 0;
            foreach (var seed in Seeds)
            {
                try
                {
                    var world = Field(seed + 50);
                    world.RevealAll = true;
                    var tanks = new List<Vehicle>();
                    for (var i = 0; i < 6; i++)
                    {
                        var t = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-25f + i * 10f, -10f), 0f);
                        world.MakeSparring(t); t.HoldFire = true; tanks.Add(t);
                    }
                    var b = world.SpawnVehicle(boss, 1, new Vector2(0f, 35f), MathF.PI);
                    world.MakeSparring(b);
                    var taken = 0f;
                    DamageSystem.DamageLog = (by, victim, amount, k, w) => { if (tanks.Contains(victim)) taken += amount; };
                    try { for (var t = 0f; t < 60f; t += 0.05f) { world.Step(0.05f); world.ClearEvents(); } }
                    finally { DamageSystem.DamageLog = null; }
                    total += taken; ok++;
                }
                catch (Exception e) { note = e.GetType().Name + ": " + e.Message.Split('\n')[0]; break; }
            }
            sb.AppendLine($"{boss}\t{(ok > 0 ? (total / ok).ToString("0", Inv) : "n/a")}\t{ok}\t{note}");
            Console.Error.WriteLine(boss);
        }
    }
}
