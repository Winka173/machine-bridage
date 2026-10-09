using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>Who holds a piece of the front map.</summary>
    public enum FrontState
    {
        /// <summary>Sea, or land no mission is fought near.</summary>
        None,
        Ours,
        Enemy,

        /// <summary>Thorne's army, from the betrayal in chapter 7 until the brigade takes the ground back (chapters 8-9).</summary>
        Betrayed,
    }

    /// <summary>A mission's piece of the front: where it is fought on the coast and who holds it now.</summary>
    public readonly struct FrontSector
    {
        public FrontSector(MissionDef mission, Vector2 at, FrontState state)
        {
            Mission = mission;
            At = at;
            State = state;
        }

        public MissionDef Mission { get; }

        /// <summary>On the map, 0-1 across (west to east) and down (north to south).</summary>
        public Vector2 At { get; }

        public FrontState State { get; }
    }

    /// <summary>
    /// Prompt 22 D.1: the chapter screen's map of the Meridian Coast. Every main mission on the player's path is a piece of
    /// ground near its battlefield; a won mission frees its piece, so the front line (where the brigade's ground meets
    /// Hegemon's) moves with every win. Ground won in an earlier chapter stays ours until a later chapter fights there again
    /// (Varga's counterstrike retakes it when chapter 6 opens). Once Veyra is liberated (c7m10) Thorne's army holds the
    /// ground it stood on with the brigade (Red Rock, Hollow Dam, Iron Harbor, Beacon Bay) until chapters 8 and 9 win it
    /// back. A battlefield where an enemy base or an operation was won shows a flag. Chapters switched off (prompt 20 C)
    /// are not on it. The picture is drawn from this (Hud/FrontMapView); the same save gives the same map.
    /// </summary>
    public static class FrontMap
    {
        /// <summary>The battlefields on the coast (0-1 across and down; the sea is west and north, Helion in the south-east).</summary>
        public static readonly Dictionary<string, Vector2> Sites = new()
        {
            ["landingbeach"] = new Vector2(0.13f, 0.64f), ["greenvale"] = new Vector2(0.22f, 0.55f), ["ashfield"] = new Vector2(0.25f, 0.74f),
            ["dunebreak"] = new Vector2(0.40f, 0.86f), ["redrock"] = new Vector2(0.50f, 0.74f), ["foundry"] = new Vector2(0.36f, 0.62f),
            ["whiteout"] = new Vector2(0.57f, 0.52f), ["frostpeak"] = new Vector2(0.67f, 0.42f), ["rustyard"] = new Vector2(0.30f, 0.40f),
            ["ironport"] = new Vector2(0.23f, 0.27f), ["lighthousebay"] = new Vector2(0.40f, 0.20f), ["junglepass"] = new Vector2(0.63f, 0.64f),
            ["emberridge"] = new Vector2(0.73f, 0.74f), ["hydrodam"] = new Vector2(0.46f, 0.50f), ["swamp"] = new Vector2(0.79f, 0.57f),
            ["borderbridge"] = new Vector2(0.90f, 0.64f), ["metrocity"] = new Vector2(0.54f, 0.29f), ["veyra_old_quarter"] = new Vector2(0.62f, 0.23f),
            ["capital"] = new Vector2(0.69f, 0.17f), ["openpit"] = new Vector2(0.58f, 0.88f), ["coralisles"] = new Vector2(0.445f, 0.06f),
            ["skyhold"] = new Vector2(0.80f, 0.35f), ["orbitalgate"] = new Vector2(0.90f, 0.24f), ["saltflat"] = new Vector2(0.78f, 0.88f),
            ["launchsite"] = new Vector2(0.92f, 0.82f),
        };

        /// <summary>The coast: the land's outline (the sea is outside it), and the Coral Keys.</summary>
        public static readonly Vector2[] Coast =
        {
            new(0.05f, 1.00f), new(0.06f, 0.78f), new(0.09f, 0.62f), new(0.14f, 0.50f), new(0.12f, 0.40f), new(0.16f, 0.31f),
            new(0.18f, 0.22f), new(0.26f, 0.18f), new(0.32f, 0.21f), new(0.37f, 0.14f), new(0.44f, 0.13f), new(0.50f, 0.17f),
            new(0.57f, 0.14f), new(0.64f, 0.10f), new(0.72f, 0.09f), new(0.80f, 0.13f), new(0.88f, 0.08f), new(1.00f, 0.10f),
            new(1.00f, 1.00f),
        };

        public static readonly Vector2[][] Islands =
        {
            new Vector2[] { new(0.41f, 0.05f), new(0.45f, 0.03f), new(0.47f, 0.06f), new(0.44f, 0.09f) },
            new Vector2[] { new(0.48f, 0.08f), new(0.51f, 0.06f), new(0.53f, 0.09f), new(0.50f, 0.11f) },
        };

        /// <summary>Where Thorne's army stood with the brigade: it turns with him in chapter 7.</summary>
        public static readonly string[] ThorneSites = { "redrock", "hydrodam", "ironport", "lighthousebay" };

        /// <summary>The mission of the betrayal (Veyra liberated; Thorne's base turns).</summary>
        public const string BetrayalMission = "c7m10";

        /// <summary>The chapters that win Thorne's ground back.</summary>
        public static readonly int[] RetakeChapters = { 8, 9 };

        /// <summary>The map's width to its height (distances on it are measured in its own proportions).</summary>
        public const float Aspect = 16f / 7f;

        /// <summary>How far a mission's ground reaches from where it is fought.</summary>
        public const float Reach = 0.075f;

        public static bool Betrayed => PlayerProfile.Completed(BetrayalMission);

        /// <summary>The land at a point of the map (the Coral Keys too).</summary>
        public static bool Land(Vector2 p)
        {
            if (Inside(p, Coast)) return true;
            foreach (var island in Islands)
                if (Inside(p, island)) return true;
            return false;
        }

        private static bool Inside(Vector2 p, Vector2[] poly)
        {
            var inside = false;
            for (int i = 0, j = poly.Length - 1; i < poly.Length; j = i++)
                if ((poly[i].y > p.y) != (poly[j].y > p.y) && p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)
                    inside = !inside;
            return inside;
        }

        /// <summary>A chapter's place in the order of play.</summary>
        private static int Order(int chapter)
        {
            var chapters = Campaign.Chapters;
            for (var i = 0; i < chapters.Count; i++)
                if (chapters[i].Number == chapter) return i;
            return chapters.Count;
        }

        /// <summary>Thorne's ground is back once every mission of chapters 8-9 on it is won.</summary>
        private static bool Retaken(string map)
        {
            var any = false;
            foreach (var m in Campaign.All)
            {
                if (m.Map != map || m.Side || !Campaign.OnPath(m) || System.Array.IndexOf(RetakeChapters, m.Chapter) < 0) continue;
                any = true;
                if (!PlayerProfile.Completed(m.Id)) return false;
            }
            return any;
        }

        /// <summary>Every piece of the front, one for each main mission on the player's path in the chapters switched on.</summary>
        public static List<FrontSector> Sectors()
        {
            var list = new List<FrontSector>();
            var perSite = new Dictionary<string, int>();
            var heldSince = new Dictionary<string, int>();
            var betrayed = Betrayed;
            var retaken = new Dictionary<string, bool>();
            foreach (var m in Campaign.All)
            {
                if (m.Side || !Campaign.OnPath(m) || !Sites.TryGetValue(m.Map, out var site) || !Campaign.ChapterEnabled(m.Chapter)) continue;
                perSite.TryGetValue(m.Map, out var k);
                perSite[m.Map] = k + 1;
                // A ring round the battlefield, one piece a mission, in the order they are played there.
                var angle = k * 2.39996f;
                var radius = 0.012f + 0.015f * Mathf.Sqrt(k);
                var at = site + new Vector2(Mathf.Cos(angle) * radius / Aspect, Mathf.Sin(angle) * radius);
                var won = PlayerProfile.Completed(m.Id);
                var order = Order(m.Chapter);
                FrontState state;
                if (won) state = FrontState.Ours;
                // Ground an earlier chapter won stays ours until the fighting comes back to it.
                else state = heldSince.TryGetValue(m.Map, out var since) && since < order && !Campaign.ChapterOpen(m.Chapter) ? FrontState.Ours : FrontState.Enemy;
                if (won && (!heldSince.TryGetValue(m.Map, out var first) || order < first)) heldSince[m.Map] = order;
                if (betrayed && order <= Order(9) && System.Array.IndexOf(ThorneSites, m.Map) >= 0)
                {
                    if (!retaken.TryGetValue(m.Map, out var back)) retaken[m.Map] = back = Retaken(m.Map);
                    var retakenPiece = won && System.Array.IndexOf(RetakeChapters, m.Chapter) >= 0;
                    if (!back && !retakenPiece) state = FrontState.Betrayed;
                }
                list.Add(new FrontSector(m, at, state));
            }
            return list;
        }

        /// <summary>
        /// The map in cells (<paramref name="width"/> across, <paramref name="height"/> down): each piece of land takes the state
        /// of the nearest mission's ground within <see cref="Reach"/>; the rest is None.
        /// </summary>
        public static FrontState[,] Grid(IReadOnlyList<FrontSector> sectors, int width, int height)
        {
            var grid = new FrontState[width, height];
            for (var x = 0; x < width; x++)
                for (var y = 0; y < height; y++)
                {
                    var p = new Vector2((x + 0.5f) / width, (y + 0.5f) / height);
                    if (!Land(p)) continue;
                    var best = Reach * Reach;
                    var state = FrontState.None;
                    foreach (var s in sectors)
                    {
                        var dx = (s.At.x - p.x) * Aspect;
                        var dy = s.At.y - p.y;
                        var d = dx * dx + dy * dy;
                        if (d >= best) continue;
                        best = d;
                        state = s.State;
                    }
                    grid[x, y] = state;
                }
            return grid;
        }

        /// <summary>The front line: the cell edges where the brigade's ground meets the enemy's (0-1 map coordinates).</summary>
        public static List<(Vector2 a, Vector2 b)> FrontLine(FrontState[,] grid)
        {
            var w = grid.GetLength(0);
            var h = grid.GetLength(1);
            var lines = new List<(Vector2, Vector2)>();
            bool Meets(FrontState a, FrontState b) => (a == FrontState.Ours && b is FrontState.Enemy or FrontState.Betrayed) ||
                                                      (b == FrontState.Ours && a is FrontState.Enemy or FrontState.Betrayed);
            for (var x = 0; x < w; x++)
                for (var y = 0; y < h; y++)
                {
                    if (x + 1 < w && Meets(grid[x, y], grid[x + 1, y]))
                        lines.Add((new Vector2((x + 1f) / w, (float)y / h), new Vector2((x + 1f) / w, (y + 1f) / h)));
                    if (y + 1 < h && Meets(grid[x, y], grid[x, y + 1]))
                        lines.Add((new Vector2((float)x / w, (y + 1f) / h), new Vector2((x + 1f) / w, (y + 1f) / h)));
                }
            return lines;
        }

        /// <summary>The battlefields with a flag: an enemy base or an operation won there, on ground the brigade holds now.</summary>
        public static List<string> Flags(IReadOnlyList<FrontSector> sectors)
        {
            var flags = new List<string>();
            foreach (var s in sectors)
            {
                var m = s.Mission;
                if (s.State != FrontState.Ours || !(m.EnemyBase != BaseRole.None || m.Operation) || flags.Contains(m.Map)) continue;
                flags.Add(m.Map);
            }
            // A battlefield some of whose ground is lost again flies no flag.
            flags.RemoveAll(map =>
            {
                foreach (var s in sectors)
                    if (s.Mission.Map == map && s.State == FrontState.Betrayed) return true;
                return false;
            });
            return flags;
        }

        /// <summary>Where a chapter's pin goes: the battlefield of its operation (an interlude's last mission).</summary>
        public static Vector2 PinOf(ChapterDef chapter)
        {
            var op = Campaign.OperationOf(chapter.Number);
            if (op != null && Sites.TryGetValue(op.Map, out var at)) return at;
            foreach (var map in chapter.Maps)
                if (Sites.TryGetValue(map, out at)) return at;
            return new Vector2(0.5f, 0.5f);
        }

        /// <summary>How many pieces are ours (the tests follow the front with it).</summary>
        public static int Count(IReadOnlyList<FrontSector> sectors, FrontState state)
        {
            var n = 0;
            foreach (var s in sectors)
                if (s.State == state) n++;
            return n;
        }
    }
}
