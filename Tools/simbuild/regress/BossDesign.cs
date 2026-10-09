// Boss design 09/10: static catalog report of every boss (mounts, parts, skills, phases) for the mapping and the checks.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using MachineBrigade.Sim.Content;

static class BossDesign
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    public static void Dump(Catalog cat, StringBuilder sb)
    {
        foreach (var v in cat.Vehicles.Values.Where(x => x.Boss).OrderBy(x => x.Id, StringComparer.Ordinal))
        {
            sb.AppendLine($"BOSS {v.Id} rank={v.RankDef?.Id} hp={v.MaxHp.ToString("0", Inv)} mounts={v.Mounts.Count} parts={v.Parts.Count} wdmg={v.WeaponDamage.ToString("0.###", Inv)} phases=[{string.Join(",", v.Phases.Select(p => p.At.ToString("0.##", Inv)))}] skills=[{string.Join(",", v.Skills.Select(s => s.Id))}]");
            for (var i = 0; i < v.Mounts.Count; i++)
            {
                var m = v.Mounts[i];
                sb.AppendLine($"  M{i} {m.Weapon.Id} slot={m.Slot} aim={m.Aim} dps={m.Weapon.SustainedDps.ToString("0.#", Inv)}");
            }
            foreach (var p in v.Parts)
                sb.AppendLine($"  P {p.Id} kind={p.Kind} hp={p.Hp.ToString("0.###", Inv)} mounts=[{string.Join(",", p.Mounts)}] skills=[{string.Join(",", p.Skills)}] stops=[{string.Join(",", p.Stops)}]");
        }
    }
}
