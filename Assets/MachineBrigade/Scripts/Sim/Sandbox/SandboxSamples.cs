#nullable enable
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>
    /// The player version's five sample scenarios (prompt 21 F.7), on the flat test range. Each is a lesson in one
    /// line: a flank shot, anti-air against a strike, eight vehicles on Behemoth, guns against towers, artillery
    /// against a rush. The player version fits them to what the player has (a sample's units they lack are
    /// replaced like an imported code's).
    /// </summary>
    public static class SandboxSamples
    {
        /// <summary>The samples' ids, in the order the list shows them (text keys "sandbox.sample.&lt;id&gt;").</summary>
        public static readonly string[] Ids = { "flank", "airdefence", "behemoth", "towers", "artillery" };

        public static SandboxScenario Get(string id)
        {
            var s = new SandboxScenario { Name = id, Map = SandboxMaps.FlatId, Seed = 21, Limit = 180f };
            s.Sides[0].Ai = SandboxAi.Combat;
            s.Sides[1].Ai = SandboxAi.Combat;
            switch (id)
            {
                case "flank":
                    // Two tanks face a heavy tank head on; two more come round its side.
                    Add(s, "main_battle_tank", 0, -8f, -40f, 0f);
                    Add(s, "main_battle_tank", 0, 8f, -40f, 0f);
                    Add(s, "main_battle_tank", 0, -45f, 5f, 90f);
                    Add(s, "main_battle_tank", 0, -45f, 15f, 90f);
                    Add(s, "heavy_tank", 1, 0f, 10f, 180f);
                    Add(s, "heavy_tank", 1, 12f, 10f, 180f);
                    break;
                case "airdefence":
                    // A column of anti-air vehicles under attack jets and helicopters.
                    for (var i = 0; i < 3; i++) Add(s, "aa_vehicle", 0, -12f + i * 12f, -30f, 0f);
                    Add(s, "ifv", 0, 0f, -42f, 0f);
                    for (var i = 0; i < 3; i++) Add(s, "attack_jet", 1, -20f + i * 20f, 70f, 180f);
                    Add(s, "attack_helicopter", 1, -10f, 55f, 180f);
                    Add(s, "attack_helicopter", 1, 10f, 55f, 180f);
                    break;
                case "behemoth":
                    // Eight vehicles against Behemoth, its escorts sent home.
                    string[] eight = { "heavy_tank", "heavy_tank", "tank_destroyer", "tank_destroyer", "main_battle_tank", "main_battle_tank", "mlrs", "artillery" };
                    for (var i = 0; i < eight.Length; i++) Add(s, eight[i], 0, -35f + i * 10f, -50f - (i >= 6 ? 20f : 0f), 0f);
                    var boss = Add(s, "behemoth", 1, 0f, 50f, 180f);
                    boss.Boss = new SandboxBossState { NoEscorts = true };
                    s.Limit = 300f;
                    break;
                case "towers":
                    // A tank platoon against a small tower line (towers stand anywhere on the test range).
                    Add(s, "gun_turret", 1, -15f, 30f, 180f);
                    Add(s, "aa_turret", 1, 0f, 36f, 180f);
                    Add(s, "mg_bunker", 1, 15f, 30f, 180f);
                    for (var i = 0; i < 4; i++) Add(s, i < 2 ? "main_battle_tank" : "light_tank", 0, -15f + i * 10f, -40f, 0f);
                    break;
                default:
                    // Artillery and a guard against a light rush.
                    Add(s, "artillery", 0, -10f, -70f, 0f);
                    Add(s, "mlrs", 0, 10f, -70f, 0f);
                    Add(s, "ifv", 0, 0f, -55f, 0f);
                    for (var i = 0; i < 5; i++) Add(s, i % 2 == 0 ? "armored_car" : "scout_jeep", 1, -24f + i * 12f, 60f, 180f);
                    break;
            }
            return s;
        }

        public static IEnumerable<SandboxScenario> All()
        {
            foreach (var id in Ids) yield return Get(id);
        }

        private static SandboxUnit Add(SandboxScenario s, string def, int team, float x, float y, float heading)
        {
            var u = new SandboxUnit { Def = def, Team = team, Heading = heading, Position = new Vector2(x, y) };
            s.Units.Add(u);
            return u;
        }
    }
}
