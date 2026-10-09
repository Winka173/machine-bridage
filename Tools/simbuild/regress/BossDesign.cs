// Boss design 09/10: static catalog report of every boss (mounts, parts, skills, phases, DPS budget) and the headless smoke of the workbook's rules.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Numerics;
using System.Text;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

static class BossDesign
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    public static void Dump(Catalog cat, StringBuilder sb)
    {
        foreach (var v in cat.Vehicles.Values.Where(x => x.Boss).OrderBy(x => x.Id, StringComparer.Ordinal))
        {
            double oldDps = 0, newDps = 0;
            foreach (var m in v.Mounts)
            {
                if (m.NewGun) newDps += m.Weapon.SustainedDps * m.DamageScale;
                else oldDps += m.Weapon.SustainedDps;
            }
            var nerf = v.GunNerfDamage * v.FireScale;
            sb.AppendLine($"BOSS {v.Id} rank={v.RankDef?.Id} hp={v.MaxHp.ToString("0", Inv)} mounts={v.Mounts.Count} new={v.Mounts.Count(m => m.NewGun)} parts={v.Parts.Count} wdmg={v.WeaponDamage.ToString("0.###", Inv)} nerf={nerf.ToString("0.###", Inv)} dpsOldPaper={oldDps.ToString("0.#", Inv)} dpsOldAfter={(oldDps * nerf).ToString("0.#", Inv)} dpsNewAfter={(newDps * nerf).ToString("0.#", Inv)} dpsAll={AllDps(v).ToString("0.#", Inv)} phases=[{string.Join(",", v.Phases.Select(p => p.At.ToString("0.##", Inv)))}] skills=[{string.Join(",", v.Skills.Select(s => s.Id))}]");
            for (var i = 0; i < v.Mounts.Count; i++)
            {
                var m = v.Mounts[i];
                sb.AppendLine($"  M{i} {m.Weapon.Id} slot={m.Slot} aim={m.Aim} new={(m.NewGun ? 1 : 0)} scale={m.DamageScale.ToString("0.###", Inv)} dps={m.Weapon.SustainedDps.ToString("0.#", Inv)}");
            }
            foreach (var p in v.Parts)
                sb.AppendLine($"  P {p.Id} kind={p.Kind} hp={p.Hp.ToString("0.###", Inv)} mounts=[{string.Join(",", p.Mounts)}] skills=[{string.Join(",", p.Skills)}] stops=[{string.Join(",", p.Stops)}]");
        }
    }

    /// <summary>The weapon-level DPS of all mounts after the gun nerf and each mount's own scale (what sheet 03 / 05 count).</summary>
    static double AllDps(VehicleDef v)
    {
        var nerf = v.GunNerfDamage * v.FireScale;
        double d = 0;
        foreach (var m in v.Mounts) d += m.Weapon.SustainedDps * m.DamageScale * nerf;
        return d;
    }

    // ------------------------------------------------------------------ headless smoke (09/10): spawn every boss, step it, check the workbook's rules
    public static void Smoke(Catalog cat, StringBuilder sb)
    {
        var bosses = cat.Vehicles.Values.Where(v => v.Boss).OrderBy(v => v.Id, StringComparer.Ordinal).ToList();
        var failures = 0;
        foreach (var def in bosses)
        {
            var problems = new List<string>();
            var note = "";
            try { note = RunBoss(cat, def, problems); }
            catch (Exception e) { problems.Add("EXCEPTION " + e.GetType().Name + ": " + e.Message.Split('\n')[0]); }
            if (problems.Count > 0) failures++;
            sb.AppendLine($"{def.Id}\t{(problems.Count == 0 ? "ok" : "FAIL " + string.Join("; ", problems))}\t{note}");
        }
        sb.AppendLine($"bosses {bosses.Count}, failures {failures}");
    }

    static bool IsSummoner(VehicleDef d) => d.Skills.Any(s => s.Kind == SkillKind.Summon) || d.Pods != null || d.Factory != null;

    static string RunBoss(Catalog cat, VehicleDef def, List<string> problems)
    {
        var map = new MapDefinition("range", 300f,
            new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
            new List<PropPlacement>(), new List<UnitPlacement>());
        var world = new SimWorld(cat, map, seed: 7);
        world.RevealAll = true;
        var boss = world.SpawnVehicle(def.Id, 1, new Vector2(0f, 60f), MathF.PI);
        for (var i = 0; i < 6; i++)
        {
            var t = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-33f + i * 13f, 0f), 0f);
            world.MakeSparring(t);
            t.HoldFire = true;
        }
        var summoner = IsSummoner(def);
        var total = summoner ? 360f : 90f;
        // The units the boss's own summons make (escorts, pods in flight and the boss itself are not counted).
        var kinds = new HashSet<string>();
        var cap = 0;
        var minDelay = float.MaxValue;
        foreach (var s in def.Skills)
            if (s.Kind == SkillKind.Summon) { kinds.Add(s.Unit); cap += s.Max; minDelay = Math.Min(minDelay, s.Delay); }
        if (def.Pods != null)
        {
            foreach (var u in def.Pods.Units) kinds.Add(u);
            cap += def.Pods.Max;
            minDelay = Math.Min(minDelay, def.Pods.First);
        }
        if (def.Factory != null)
        {
            for (var p = 0; p < 4; p++)
                foreach (var u in def.Factory.UnitsFor(p)) kinds.Add(u);
            cap += def.Factory.Cap;
            minDelay = Math.Min(minDelay, def.Factory.First);
        }
        // The big attacks that land units (Daedalus's mass drop, Moloch's dump) are capped at 2 in the data.
        if (def.Id == "daedalus" || def.Id == "moloch") cap += 2;
        // Parts that carry the summons (and the pod bays, the workshop doors): broken once the first wave is out.
        var breakers = new List<int>();
        for (var i = 0; i < def.Parts.Count; i++)
        {
            var p = def.Parts[i];
            var carries = false;
            foreach (var k in p.Skills)
                foreach (var s in def.Skills)
                    carries |= s.Id == k && s.Kind == SkillKind.Summon;
            if (carries || p.Stops.Contains("pods") || p.Stops.Contains("factory")) breakers.Add(i);
        }
        var begins = 0;
        var maxLive = 0;
        double firstSeen = -1;
        double brokeAt = -1;
        HashSet<int> seenBefore = null;
        var afterBreakNew = 0;
        var newKinds = new List<string>();
        var step = 0.05f;
        var n = (int)(total / step);
        var healed = false;
        var hit = false;
        for (var k = 0; k < n; k++)
        {
            var now = world.Time;
            if (!hit && now >= 45.0)
            {
                hit = true;
                // The mark: just above 50 %, then one blow across it (or the health set under it where the body takes none).
                boss.Hp = boss.MaxHp * 0.52f;
                var before = boss.Hp;
                world.Damage.Apply(boss, boss.MaxHp * 0.20f, DamageType.Kinetic, new HitInfo(null, 0, null, boss.Position, HitKind.Direct, false));
                if (boss.Hp >= before - 1f) boss.Hp = boss.MaxHp * 0.49f;
            }
            if (hit && !healed && now >= 70.0)
            {
                healed = true;
                boss.Hp = boss.MaxHp * 0.9f;   // a heal back above the mark...
                world.Step(step);
                world.ClearEvents();
                boss.Hp = boss.MaxHp * 0.45f;  // ...and under it again: no second phase
            }
            world.Step(step);
            foreach (var e in world.Events)
                if (e.Kind == SimEventKind.BossPhase && e.Entity == boss.Id && e.Mount == 1) begins++;
            world.ClearEvents();
            if (!boss.IsAlive) { problems.Add("the boss died with nobody shooting it"); break; }
            if (summoner && k % 20 == 0)
            {
                var live = 0;
                var ids = new HashSet<int>();
                var byId = new Dictionary<int, string>();
                foreach (var v in world.Vehicles)
                {
                    if (!v.IsAlive || v.Team != 1 || v.Id == boss.Id || v.IsEscort || v.IsPod || !kinds.Contains(v.Def.Id)) continue;
                    live++;
                    ids.Add(v.Id.Value);
                    byId[v.Id.Value] = v.Def.Id + "@" + world.Time.ToString("0", Inv);
                }
                maxLive = Math.Max(maxLive, live);
                if (live > 0 && firstSeen < 0) firstSeen = now;
                if (brokeAt < 0 && firstSeen >= 0 && now >= firstSeen + 3.0 && breakers.Count > 0)
                {
                    foreach (var i in breakers) world.Bosses.Break(boss, i);
                    brokeAt = now;
                    seenBefore = ids;
                }
                else if (brokeAt >= 0)
                {
                    foreach (var id in ids)
                        if (!seenBefore.Contains(id)) { afterBreakNew++; seenBefore.Add(id); newKinds.Add(byId[id]); }
                }
            }
        }
        var phaseAtEnd = def.Tiers != null ? boss.TierPhase : boss.Phase;
        // The phase: exactly once, at the mark, never again.
        if (begins > 1) problems.Add($"phase began {begins} times");
        if (def.Tiers == null && begins != 1) problems.Add($"phase began {begins} times (1 expected)");
        if (phaseAtEnd != 1) problems.Add($"phase counter {phaseAtEnd} at the end (1 expected)");
        if (summoner)
        {
            if (maxLive > cap) problems.Add($"{maxLive} summoned units alive at once, cap {cap}");
            if (minDelay < float.MaxValue && firstSeen >= 0 && firstSeen < minDelay - 1.0) problems.Add($"first unit at {firstSeen:0.0} s, delay {minDelay:0} s");
            if (afterBreakNew > 0) problems.Add($"{afterBreakNew} new units after the carrying parts broke");
        }
        return $"phase={phaseAtEnd} begins={begins} maxLive={maxLive} cap={cap} firstSeen={(firstSeen < 0 ? "-" : firstSeen.ToString("0.0", Inv))} brokeAt={(brokeAt < 0 ? "-" : brokeAt.ToString("0", Inv))} newAfterBreak={afterBreakNew}{(newKinds.Count > 0 ? " [" + string.Join(",", newKinds) + "]" : "")}";
    }
}
