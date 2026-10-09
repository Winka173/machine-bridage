#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Boss design workbook 09/10 (Docs/bosses/design_0910): the rules the catalog's bosses must keep, as a static check over the loaded
    /// <see cref="Catalog"/> (CatalogCheck, the headless harness and the EditMode tests call it). It returns one line per breach; an empty
    /// list means the data follows the workbook. It reads no balance numbers of its own except the workbook's fixed facts (the mount counts of
    /// the two carriers, the six new minis); every other rule is structural.
    /// </summary>
    public static class BossDesignRules
    {
        /// <summary>The six new mini bosses of sheet 05 and the mount count each is to have.</summary>
        public static readonly IReadOnlyDictionary<string, int> NewMinis = new Dictionary<string, int>
        {
            ["roc_gunship"] = 8, ["daedalus_assault"] = 7, ["icarus_interceptor"] = 7, ["matriarch_flak"] = 6, ["jotunn_artillery"] = 7, ["bastion_aa"] = 7,
        };

        public static List<string> Check(Catalog catalog)
        {
            var errors = new List<string>();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (!def.Boss) continue;
                var id = def.Id;
                // One phase mark at 50 %, once; no phase buffs stacked on top.
                if (def.Phases.Count > 1) errors.Add($"{id}: {def.Phases.Count} phases (one allowed)");
                foreach (var p in def.Phases)
                {
                    if (Math.Abs(p.At - 0.5f) > 1e-4f) errors.Add($"{id}: phase mark {p.At} (0.5 only)");
                    if (p.Damage != 1f || p.FireRate != 1f || p.Speed != 1f || p.Armor != 1f) errors.Add($"{id}: the phase carries a stat buff (damage/fireRate/speed/armor)");
                }
                if (def.Tiers != null)
                {
                    if (def.Tiers.Marks.Count > 1) errors.Add($"{id}: {def.Tiers.Marks.Count} tier marks (one allowed)");
                    foreach (var m in def.Tiers.Marks)
                        if (Math.Abs(m - 0.5f) > 1e-4f) errors.Add($"{id}: tier mark {m} (0.5 only)");
                    if (def.Tiers.Crash != null) errors.Add($"{id}: a crash phase (no second phase)");
                }
                // No health-threshold buff skills.
                foreach (var s in def.Skills)
                    if (s.Trigger == SkillTrigger.HpBelow && s.Kind != SkillKind.Summon) errors.Add($"{id}: skill {s.Id} triggers below a health mark (a second phase)");
                // No destructible radar or command tower.
                foreach (var part in def.Parts)
                {
                    if (part.Kind == "radar" || part.Kind == "tower" || part.Kind == "command" || part.Kind == "commandtower") errors.Add($"{id}: part {part.Id} is a {part.Kind}");
                    foreach (var stop in part.Stops)
                        if (stop == "radar") errors.Add($"{id}: part {part.Id} stops the radar mechanism");
                }
                // Periodic summons: cap, delay and cooldown; carried by a part (a module to break).
                foreach (var s in def.Skills)
                {
                    if (s.Kind != SkillKind.Summon) continue;
                    if (s.Max <= 0) errors.Add($"{id}: summon {s.Id} has no cap (max)");
                    if (s.Cooldown <= 0f) errors.Add($"{id}: summon {s.Id} has no cooldown");
                    if (s.Delay <= 0f) errors.Add($"{id}: summon {s.Id} has no first-wave delay");
                    var carried = false;
                    foreach (var part in def.Parts)
                        foreach (var k in part.Skills)
                            carried |= k == s.Id;
                    if (!carried) errors.Add($"{id}: summon {s.Id} is carried by no part (nothing to break)");
                }
                // A boss with pods has a pod bay to break.
                if (def.Pods != null)
                {
                    var bay = false;
                    foreach (var part in def.Parts)
                        foreach (var stop in part.Stops)
                            bay |= stop == "pods";
                    if (!bay && def.Pods.Max > 2) errors.Add($"{id}: pods with a live cap of {def.Pods.Max} (the workbook allows at most 2-3)");
                }
                // New hardpoints: every mount flagged new has a part carrying it, and the budget exists.
                var newMounts = 0;
                for (var i = 0; i < def.Mounts.Count; i++)
                {
                    if (!def.Mounts[i].NewGun) continue;
                    newMounts++;
                    var carried = false;
                    foreach (var part in def.Parts)
                        foreach (var m in part.Mounts)
                            carried |= m == i;
                    if (!carried) errors.Add($"{id}: new mount {i} is on no part");
                }
                if (newMounts > 0 && def.NewGunDps <= 0f && def.GunDpsAll <= 0f) errors.Add($"{id}: new mounts without a DPS budget");
            }
            // The two carriers: Kraken has 13 hardpoints, Leviathan 22, Kraken fewer.
            if (catalog.Vehicles.TryGetValue("kraken", out var kraken) && catalog.Vehicles.TryGetValue("leviathan", out var leviathan))
            {
                if (kraken.Mounts.Count != 13) errors.Add($"kraken: {kraken.Mounts.Count} mounts (13)");
                if (leviathan.Mounts.Count != 22) errors.Add($"leviathan: {leviathan.Mounts.Count} mounts (22)");
                if (kraken.Mounts.Count >= leviathan.Mounts.Count) errors.Add("kraken must have fewer gun mounts than leviathan");
                var deck = false;
                foreach (var part in kraken.Parts)
                    if (part.Kind == "flightdeck" && part.Skills.Count > 0) deck = true;
                if (!deck) errors.Add("kraken: its flight deck carries no launch skill");
            }
            else errors.Add("kraken / leviathan missing");
            // The six new minis.
            foreach (var pair in NewMinis)
            {
                if (!catalog.Vehicles.TryGetValue(pair.Key, out var mini)) { errors.Add($"{pair.Key}: not in the catalog"); continue; }
                if (!mini.Boss || mini.Rank != BossRank.Mini) errors.Add($"{pair.Key}: not a mini boss");
                if (mini.Mounts.Count != pair.Value) errors.Add($"{pair.Key}: {mini.Mounts.Count} mounts ({pair.Value})");
                if (mini.GunDpsAll <= 0f) errors.Add($"{pair.Key}: no DPS budget");
            }
            return errors;
        }
    }
}
