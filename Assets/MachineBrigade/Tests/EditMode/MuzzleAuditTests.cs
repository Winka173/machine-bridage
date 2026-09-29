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
            "ifv", "heavy_rocket_artillery", "attack_helicopter", "scout_heli",
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
            ["ballistic_launcher m0"] = "ballistic_missile: no barrel, tube or pod round its line",
            ["elite_mlrs m0"] = "mlrs_elite: flash 22 deg off the barrel",
            ["heavy_bomber m2"] = "air_cruise_missile: no barrel, tube or pod round its line",
            ["mobile_fortress m2"] = "boss_rockets: no barrel, tube or pod round its line",
            ["mobile_fortress m5"] = "boss_missiles: no barrel, tube or pod round its line",
            ["silver_bug m0"] = "saucer_laser: 0.05 m off the barrel's middle",
            ["silver_bug m1"] = "coilgun: 0.52 m ahead of the open end",
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
                Assert.IsTrue(r.Ok, $"{r.Vehicle}: {r.Note}");
                Assert.Less(r.AxisAngle, MuzzleGeometryAudit.Angle, r.Vehicle);
            }
        }
    }
}
