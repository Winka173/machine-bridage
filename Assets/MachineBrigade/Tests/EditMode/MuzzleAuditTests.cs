using System.Collections.Generic;
using System.Linq;
using System.Text;
using MachineBrigade.Editor;
using MachineBrigade.Game.Match;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Every weapon's muzzle against its own barrel, tube or pod in the model files, through the
    /// game's own mapping (MuzzleGeometryAudit, DECISIONS 13E). The owner's play-test list must be
    /// right on every mount; anything else the audit finds wrong must be on the known list below,
    /// with why, so a new or re-exported model, a slot mapping or a launcher change that puts a
    /// muzzle off its barrel fails here. Fixing one of the known ones fails too, until it is
    /// taken off the list (the list stays the truth). Docs/muzzle-audit.md is the full table
    /// (-executeMethod MachineBrigade.Editor.MuzzleGeometryAudit.Report).
    /// </summary>
    public class MuzzleAuditTests
    {
        /// <summary>The vehicles the owner saw wrong (play tests 2 and 3), and the tanks, all mounts right.</summary>
        private static readonly string[] OwnersList =
        {
            "armored_car", "rocket_technical", "main_battle_tank", "light_tank", "heavy_tank", "twin_tank", "elite_mbt", "elite_heavy_tank",
            "turtle_tank", "wheeled_gun", "tank_destroyer", "flame_tank", "mortar_carrier", "thermobaric_launcher", "mlrs", "artillery",
            "ifv", "heavy_rocket_artillery", "atgm_carrier", "attack_helicopter", "scout_heli",
        };

        /// <summary>
        /// Mounts still off their barrel in the model files (vehicle, or vehicle_hd for the high-detail
        /// variant, and mount index), mostly bosses and aircraft whose Blender builds place the muzzle
        /// empty away from the drawn gun or draw no gun at all: the Blender lane's list (DECISIONS 13E).
        /// </summary>
        private static readonly Dictionary<string, string> Known = new()
        {
            ["aa_turret m0"] = "twin_30_flak: flash 6 deg off the barrel",
            ["aa_turret.flak m0"] = "flak_quad: flash 6 deg off the barrel",
            ["aa_turret.sam m0"] = "sam_long: no barrel, tube or pod round its line",
            ["aa_turret.sam m1"] = "hmg_roof: no barrel, tube or pod round its line",
            ["ammo_carrier m0"] = "hmg_roof: no muzzle of its own (no Muzzle_main)",
            ["armored_train m1"] = "boss_rockets: 0.42 m off the barrel's middle",
            ["attack_jet m0"] = "jet_cannon: 0.40 m ahead of the open end",
            ["ballistic_launcher m0"] = "ballistic_missile: no barrel, tube or pod round its line",
            ["behemoth m2"] = "boss_flak: 1.48 m ahead of the open end",
            ["behemoth m3"] = "boss_flak: 1.48 m ahead of the open end",
            ["behemoth m4"] = "boss_missiles: 0.20 m off the barrel's middle",
            ["behemoth m5"] = "boss_missiles: 0.20 m off the barrel's middle",
            ["behemoth_inferno m2"] = "boss_flak: 1.48 m ahead of the open end",
            ["behemoth_tempest m0"] = "boss_railgun: 0.38 m ahead of the open end",
            ["drone_mothership m2"] = "boss_flak: no barrel, tube or pod round its line",
            ["drone_mothership m3"] = "boss_flak: no barrel, tube or pod round its line",
            ["elite_attack_jet m0"] = "jet_cannon: 0.40 m ahead of the open end",
            ["elite_grad m0"] = "grad_cluster: 0.09 m inside",
            ["elite_mlrs m0"] = "mlrs_elite: flash 22 deg off the barrel",
            ["fighter_jet m0"] = "air_to_air: 1.00 m ahead of the open end",
            ["fortress_bastion m1"] = "autocannon_40: no barrel, tube or pod round its line",
            ["fortress_bastion m2"] = "autocannon_40: no barrel, tube or pod round its line",
            ["fortress_bastion m3"] = "autocannon_40: no barrel, tube or pod round its line",
            ["fortress_bastion m4"] = "autocannon_40: no barrel, tube or pod round its line",
            ["fortress_hive m3"] = "boss_flak: no barrel, tube or pod round its line",
            ["fortress_hive m4"] = "boss_flak: no barrel, tube or pod round its line",
            ["gunship_heli m0"] = "gunship_rockets: no barrel, tube or pod round its line",
            ["gunship_heli m2"] = "heli_atgm: no barrel, tube or pod round its line",
            ["heavy_aa m0"] = "twin_30_flak: no barrel, tube or pod round its line",
            ["heavy_aa m1"] = "sam: 0.17 m off the barrel's middle",
            ["heavy_bomber m1"] = "bomber_tail_guns: 0.77 m ahead of the open end",
            ["heavy_bomber m2"] = "air_cruise_missile: no barrel, tube or pod round its line",
            ["mega_gunship m0"] = "gunship_rockets: 0.62 m ahead of the open end",
            ["mega_gunship m1"] = "boss_heli_gun: 0.18 m ahead of the open end",
            ["mega_gunship m2"] = "boss_heli_gun: 0.18 m ahead of the open end",
            ["mega_gunship m6"] = "gunship_rockets: 0.62 m ahead of the open end",
            ["mobile_fortress m1"] = "boss_rockets: no barrel, tube or pod round its line",
            ["mobile_fortress m2"] = "boss_rockets: no barrel, tube or pod round its line",
            ["mobile_fortress m3"] = "boss_flak: 1.18 m ahead of the open end",
            ["mobile_fortress m4"] = "boss_flak: 1.18 m ahead of the open end",
            ["mobile_fortress m5"] = "boss_missiles: no barrel, tube or pod round its line",
            ["sam_launcher m0"] = "sam_long: flash 17 deg off the barrel",
            ["silver_bug m0"] = "saucer_laser: 0.05 m off the barrel's middle",
            ["silver_bug m1"] = "coilgun: 0.52 m ahead of the open end",
            ["silver_bug m2"] = "boss_flak: no barrel, tube or pod round its line",
            ["sky_fortress m1"] = "gunship_40mm: flash 7 deg off the barrel",
            ["sky_fortress m2"] = "gunship_40mm: flash 7 deg off the barrel",
            ["sky_fortress m4"] = "griffin: 0.18 m ahead of the open end",
            ["sky_gunship m0"] = "gunship_105: flash 7 deg off the barrel",
            ["sky_gunship m1"] = "gunship_40mm: flash 7 deg off the barrel",
            ["sky_gunship m3"] = "griffin: flash 7 deg off the barrel",
            ["stealth_bomber m1"] = "jassm: Standoff_nose",
            ["strike_drone m0"] = "drone_missile: 0.62 m ahead of the open end",
            ["supply_truck m0"] = "mg_jeep: no muzzle of its own (no Muzzle_main)",
            ["attack_jet_hd m0"] = "jet_cannon: 0.40 m ahead of the open end",
            ["elite_attack_jet_hd m0"] = "jet_cannon: 0.40 m ahead of the open end",
            ["fighter_jet_hd m0"] = "air_to_air: 1.00 m ahead of the open end",
            ["sky_gunship_hd m0"] = "gunship_105: flash 7 deg off the barrel",
            ["sky_gunship_hd m1"] = "gunship_40mm: flash 7 deg off the barrel",
            ["sky_gunship_hd m3"] = "griffin: flash 7 deg off the barrel",
        };

        [Test]
        public void EveryMuzzleSitsOnItsOwnBarrel()
        {
            var catalog = GameContent.LoadCatalog();
            var rows = MuzzleGeometryAudit.Run(catalog);
            var hd = MuzzleGeometryAudit.Run(catalog, highDetail: true);
            var all = rows.Select(r => (key: $"{r.Vehicle} m{r.Mount}", r)).Concat(hd.Select(r => (key: $"{r.Vehicle}_hd m{r.Mount}", r))).ToList();
            var wrong = all.Where(x => !x.r.Ok).ToList();
            var log = new StringBuilder();
            foreach (var (key, r) in wrong)
                log.Append($"{key} {r.Slot} {r.Weapon} [{r.Node}] ahead {r.AheadOfTip:0.00} off {r.OffAxis:0.00} axis {r.AxisAngle:0.0}: {r.Note}").Append('\n');
            var firing = rows.Count(r => r.Verdict != "n/a");
            Debug.Log($"MUZZLE AUDIT {firing} firing mounts, {rows.Count(r => !r.Ok)} wrong (known {Known.Count(k => !k.Key.Contains("_hd "))}); " +
                      $"high detail {hd.Count(r => r.Verdict != "n/a")} mounts, {hd.Count(r => !r.Ok)} wrong" + System.Environment.NewLine + log);
            Assert.Greater(firing, 250, "the audit reached every armed vehicle");

            foreach (var id in OwnersList)
            {
                var mounts = rows.Where(r => r.Vehicle == id && r.Verdict != "n/a").ToList();
                Assert.IsNotEmpty(mounts, id);
                foreach (var r in mounts)
                    Assert.IsTrue(r.Ok, $"{id} mount {r.Mount} ({r.Weapon}) off its barrel: {r.Note}");
            }
            var unexpected = wrong.Where(x => !Known.ContainsKey(x.key)).Select(x => $"{x.key} {x.r.Weapon}: {x.r.Note}").ToList();
            Assert.IsEmpty(unexpected, "muzzles off their barrels: " + string.Join(" | ", unexpected));
            var nowRight = Known.Keys.Where(k => !wrong.Any(x => x.key == k)).ToList();
            Assert.IsEmpty(nowRight, "now right, take them off the known list: " + string.Join(", ", nowRight));
        }

        /// <summary>
        /// A raised box of tubes launches from its tilted face, spread across that face and along its
        /// tubes: the MLRS's pod, raised 21 degrees, and the rocket technical's (DECISIONS 13E).
        /// </summary>
        [Test]
        public void TiltedLauncherFacesLaunchAlongTheirTubes()
        {
            var catalog = GameContent.LoadCatalog();
            var rows = MuzzleGeometryAudit.Run(catalog, new[] { "mlrs", "rocket_technical", "thermobaric_launcher", "sam_launcher", "mortar_carrier" });
            foreach (var r in rows.Where(r => r.Mount == 0))
            {
                Debug.Log($"TILTED {r.Vehicle} {r.Weapon} [{r.Node}] points {r.Points} ahead {r.AheadOfTip:0.00} axis {r.AxisAngle:0.0}: {r.Note}");
                if (r.Vehicle == "sam_launcher") continue; // known: its missile box is drawn 14 degrees off its muzzle's line
                Assert.IsTrue(r.Ok, $"{r.Vehicle}: {r.Note}");
                Assert.Less(r.AxisAngle, MuzzleGeometryAudit.Angle, r.Vehicle);
            }
        }
    }
}
