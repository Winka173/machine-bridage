#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// An enemy general of the story campaign, as the AI plays them: the signature deck (used when
    /// a mission names no deck of its own), the fire support they call, their base's style and the
    /// HQ level of their own base in a duel. Portrait and lines are text keys in the Game layer
    /// ("general.&lt;id&gt;.*").
    /// </summary>
    public sealed class GeneralDef
    {
        public string Id { get; set; } = "";
        public IReadOnlyList<string> Deck { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> Supports { get; set; } = Array.Empty<string>();

        /// <summary>The base style (balance.json base.ai.styles).</summary>
        public string Style { get; set; } = "default";

        /// <summary>The stance the general fights in when a mission does not say.</summary>
        public string Stance { get; set; } = "Attack";

        public static IReadOnlyList<GeneralDef> ListFromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "campaign");
            var list = new List<GeneralDef>();
            if (!root.Has("generals")) return list;
            foreach (var g in root.Array("generals"))
                list.Add(new GeneralDef
                {
                    Id = g.String("id"),
                    Deck = g.Has("deck") ? new List<string>(g.StringArray("deck")) : Array.Empty<string>(),
                    Supports = g.Has("supports") ? new List<string>(g.StringArray("supports")) : Array.Empty<string>(),
                    Style = g.Has("style") ? g.String("style") : "default",
                    Stance = g.Has("stance") ? g.String("stance") : "Attack",
                });
            return list;
        }
    }

    /// <summary>
    /// A chapter of the story campaign: its act, its battlefields, and what finishing it opens
    /// (the Game layer names it "chapter.&lt;n&gt;.*"). Its missions carry its number. Prompt 22: an
    /// interlude is a chapter too, numbered after the twelve (13-15) and played after the chapter
    /// before it in campaign.json's order; it goes with that chapter's act.
    /// </summary>
    public sealed class ChapterDef
    {
        public int Number { get; set; }

        /// <summary>Prompt 22: 0 for one of the twelve chapters, 1-3 for an interlude (its own number).</summary>
        public int Interlude { get; set; }

        public bool IsInterlude => Interlude > 0;

        /// <summary>Its number as the screens show it: "4", or an interlude's Roman numeral ("II").</summary>
        public string Short => Interlude > 0 ? Roman(Interlude) : Number.ToString();

        public static string Roman(int n) => n switch { 1 => "I", 2 => "II", 3 => "III", 4 => "IV", 5 => "V", _ => n.ToString() };

        /// <summary>The act it belongs to (1-4).</summary>
        public int Act { get; set; }

        /// <summary>
        /// Prompt 20: its main boss and mini bosses (boss ids; a boss not built yet is fought as the
        /// stand-in its missions name as the fallback).
        /// </summary>
        public string? Main { get; set; }

        public IReadOnlyList<string> Minis { get; set; } = Array.Empty<string>();

        public IReadOnlyList<string> Maps { get; set; } = Array.Empty<string>();

        /// <summary>The general the chapter is fought against (a portrait on its card; null: none).</summary>
        public string? General { get; set; }

        public static IReadOnlyList<ChapterDef> ListFromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "campaign");
            var list = new List<ChapterDef>();
            if (!root.Has("chapters")) return list;
            foreach (var c in root.Array("chapters"))
                list.Add(new ChapterDef
                {
                    Number = c.Int("number", list.Count + 1),
                    Act = c.Int("act", 1),
                    Interlude = c.Int("interlude", 0),
                    Maps = c.Has("maps") ? new List<string>(c.StringArray("maps")) : Array.Empty<string>(),
                    General = c.Has("general") ? c.String("general") : null,
                    Main = c.Has("main") ? c.String("main") : null,
                    Minis = c.Has("minis") ? new List<string>(c.StringArray("minis")) : Array.Empty<string>(),
                });
            return list;
        }
    }

    /// <summary>
    /// Prompt 20: what campaign.json says besides its chapters and missions: where the nine-chapter
    /// campaign's missions went (a save made before moves its stars with them), and the pay scale a
    /// shorter release uses (by the last act switched on).
    /// </summary>
    public sealed class CampaignMeta
    {
        /// <summary>Old mission id to new (all moved at once, never one after another).</summary>
        public IReadOnlyDictionary<string, string> Moves { get; set; } = new Dictionary<string, string>();

        /// <summary>Old chapter number (an opening card seen) to new; 10 was the old epilogue's mark.</summary>
        public IReadOnlyDictionary<int, int> ChaptersSeen { get; set; } = new Dictionary<int, int>();

        /// <summary>The old campaign's HQ-level missions (old ids) and the level each opened.</summary>
        public IReadOnlyDictionary<string, int> OldHq { get; set; } = new Dictionary<string, int>();

        /// <summary>
        /// Prompt 22 B: where the twelve-chapter campaign's missions went when the chapters grew to 9-18
        /// missions and the interludes came in (a save of campaign version 3; old id to new, all at once).
        /// </summary>
        public IReadOnlyDictionary<string, string> Moves22 { get; set; } = new Dictionary<string, string>();

        /// <summary>Last act switched on to the pay scale of every mission (absent: 1).</summary>
        public IReadOnlyDictionary<int, float> PayScale { get; set; } = new Dictionary<int, float>();

        public static CampaignMeta FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "campaign");
            var meta = new CampaignMeta();
            if (root.Has("migration"))
            {
                var m = root.Object("migration");
                var moves = new Dictionary<string, string>();
                if (m.Has("moves"))
                {
                    var o = m.Object("moves");
                    foreach (var k in o.Keys) moves[k] = o.String(k);
                }
                var seen = new Dictionary<int, int>();
                if (m.Has("chaptersSeen"))
                {
                    var o = m.Object("chaptersSeen");
                    foreach (var k in o.Keys) seen[int.Parse(k)] = o.Int(k, 0);
                }
                var hq = new Dictionary<string, int>();
                if (m.Has("hq"))
                {
                    var o = m.Object("hq");
                    foreach (var k in o.Keys) hq[k] = o.Int(k, 0);
                }
                meta.Moves = moves;
                meta.ChaptersSeen = seen;
                meta.OldHq = hq;
            }
            if (root.Has("migration22") && root.Object("migration22").Has("moves"))
            {
                var o = root.Object("migration22").Object("moves");
                var moves = new Dictionary<string, string>();
                foreach (var k in o.Keys) moves[k] = o.String(k);
                meta.Moves22 = moves;
            }
            if (root.Has("economy") && root.Object("economy").Has("payScale"))
            {
                var o = root.Object("economy").Object("payScale");
                var pay = new Dictionary<int, float>();
                foreach (var k in o.Keys) pay[int.Parse(k)] = o.Float(k);
                meta.PayScale = pay;
            }
            return meta;
        }
    }

    /// <summary>
    /// Prompt 20 C: which parts of the story campaign a build ships (Resources/Data/release.json, or a
    /// remote config once the game has one): the acts switched on, single chapters switched off, and
    /// whether a switched-off chapter shows as a locked "Coming soon" card or not at all. Internal and
    /// test builds switch everything on.
    /// </summary>
    public sealed class CampaignRelease
    {
        public HashSet<int> Acts { get; } = new();

        public HashSet<int> ChaptersOff { get; } = new();

        /// <summary>A switched-off chapter shows as "Coming soon" (true) or is hidden (false).</summary>
        public bool ComingSoon { get; set; } = true;

        public bool On(ChapterDef chapter) => Acts.Contains(chapter.Act) && !ChaptersOff.Contains(chapter.Number);

        /// <summary>Every act on (the internal and test builds).</summary>
        public static CampaignRelease Everything() => UpTo(4);

        /// <summary>Acts I to <paramref name="lastAct"/> on.</summary>
        public static CampaignRelease UpTo(int lastAct, bool comingSoon = true)
        {
            var r = new CampaignRelease { ComingSoon = comingSoon };
            for (var a = 1; a <= lastAct; a++) r.Acts.Add(a);
            return r;
        }

        /// <summary>{ "acts": [1, 2], "chaptersOff": [6], "switchedOff": "comingSoon" | "hidden" }.</summary>
        public static CampaignRelease FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "release");
            var r = new CampaignRelease();
            if (root.Has("acts"))
                foreach (var a in root.FloatArray("acts")) r.Acts.Add((int)a);
            else
                for (var a = 1; a <= 4; a++) r.Acts.Add(a);
            if (root.Has("chaptersOff"))
                foreach (var c in root.FloatArray("chaptersOff")) r.ChaptersOff.Add((int)c);
            r.ComingSoon = !root.Has("switchedOff") || root.String("switchedOff") != "hidden";
            return r;
        }
    }
}
