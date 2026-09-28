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
    /// (the Game layer names it "chapter.&lt;n&gt;.*"). Its missions carry its number.
    /// </summary>
    public sealed class ChapterDef
    {
        public int Number { get; set; }

        /// <summary>The act it belongs to (1-3).</summary>
        public int Act { get; set; }

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
                    Maps = c.Has("maps") ? new List<string>(c.StringArray("maps")) : Array.Empty<string>(),
                    General = c.Has("general") ? c.String("general") : null,
                });
            return list;
        }
    }
}
