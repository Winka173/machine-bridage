using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>D.7: an intel file, recovered by a side objective: a side mission won, or a mission won with three stars.</summary>
    public readonly struct IntelFile
    {
        public IntelFile(string id, int chapter, bool threeStars, string mission, string author, bool clue)
        {
            Id = id;
            Chapter = chapter;
            ThreeStars = threeStars;
            Mission = mission;
            Author = author;
            Clue = clue;
        }

        public string Id { get; }
        public int Chapter { get; }

        /// <summary>Recovered by winning <see cref="Mission"/> with three stars (else by winning it: a side mission).</summary>
        public bool ThreeStars { get; }

        public string Mission { get; }

        /// <summary>Whose it is (a portrait id).</summary>
        public string Author { get; }

        /// <summary>D.2: one of the clues about Thorne (chapters 4-6).</summary>
        public bool Clue { get; }
    }

    /// <summary>D.8: one still panel after a chapter: a battlefield's picture ("foundry|rustyard": the first that exists), a render in it, who speaks.</summary>
    public readonly struct ComicPanel
    {
        public ComicPanel(int chapter, int index, string art, string render, string speaker)
        {
            Chapter = chapter;
            Index = index;
            Art = art;
            Render = render;
            Speaker = speaker;
        }

        public int Chapter { get; }
        public int Index { get; }
        public string Art { get; }
        public string Render { get; }
        public string Speaker { get; }
        public string Key => $"comic.{Chapter}.{Index}";
    }

    /// <summary>D.3: a beat of a character's arc, at a mission; the payoff missions are marked.</summary>
    public readonly struct ArcBeat
    {
        public ArcBeat(string who, string mission, bool payoff)
        {
            Who = who;
            Mission = mission;
            Payoff = payoff;
        }

        public string Who { get; }
        public string Mission { get; }
        public bool Payoff { get; }
        public string Key => $"arc.{Who}.{Mission}";
    }

    /// <summary>
    /// Prompt 22 D, the story's mechanics outside the battle: the story choices and what they change later (D.5), the story
    /// loot (D.6), the intel files (D.7), the comic panels (D.8) and the characters' arcs (D.3). The data and words are
    /// Tools/campaign/narrative.py's (Narrative.Data.cs, StoryText.cs); the choices' missions are act9.py's. Nothing here
    /// takes a card or a unit away (D.9), and reading nothing costs nothing in play.
    /// </summary>
    public static partial class Narrative
    {
        // ------------------------------------------------------------------ D.5 choices and their consequences

        /// <summary>The miners freed in chapter 8 bring this much CP to every chapter 9 battle.</summary>
        public static int MinersCp => global::MachineBrigade.Sim.Content.SimTunables.Campaign.Narrative.MinersCp;

        /// <summary>With the Skygate Array's radar burned in chapter 11, the enemy sees this share as far in chapter 12.</summary>
        public static float RadarVision => global::MachineBrigade.Sim.Content.SimTunables.Campaign.Narrative.RadarVision;

        public static float PlayerCpBonus(MissionDef m) =>
            m != null && m.Chapter == 9 && Campaign.Chosen("c8.miners") == "rescue" ? MinersCp : 0f;

        public static float EnemyVision(MissionDef m) =>
            m != null && m.Chapter == 12 && Campaign.Chosen("c11.radar") == "radar" ? RadarVision : 1f;

        /// <summary>What an earlier choice changes in this mission, as text keys and their numbers (the mission's page says so).</summary>
        public static List<(string key, (string name, object value)[] args)> Effects(MissionDef m)
        {
            var list = new List<(string, (string, object)[])>();
            if (PlayerCpBonus(m) > 0f) list.Add(("storyeffect.c8.miners.rescue", new (string, object)[] { ("cp", MinersCp) }));
            if (EnemyVision(m) < 1f) list.Add(("storyeffect.c11.radar.radar", new (string, object)[] { ("share", (int)System.Math.Round((1f - RadarVision) * 100f)) }));
            return list;
        }

        /// <summary>The mission that offers a choice (it carries "storyChoice"), or null in a build without it.</summary>
        public static MissionDef OfferOf(string choice)
        {
            foreach (var m in Campaign.All)
                if (m.StoryChoice == choice) return m;
            return null;
        }

        /// <summary>Who puts a choice to the player (a portrait id).</summary>
        public static string SpeakerOf(string choice)
        {
            foreach (var c in Choices)
                if (c.id == choice) return c.speaker;
            return "khai";
        }

        /// <summary>The first choice whose mission is won and which is still to be made (null: none).</summary>
        public static string Pending
        {
            get
            {
                foreach (var c in Choices)
                    if (OfferOf(c.id) is { } offer && PlayerProfile.Completed(offer.Id) && Campaign.Chosen(c.id) == null && Campaign.OptionsOf(c.id).Count > 0)
                        return c.id;
                return null;
            }
        }

        /// <summary>Makes a choice (once; an option the choice does not have is refused). The save keeps it.</summary>
        public static bool Choose(string choice, string option)
        {
            foreach (var m in Campaign.OptionsOf(choice))
                if (m.Option == option) return PlayerProfile.ChooseStory(choice, option);
            return false;
        }

        /// <summary>The mission an option leads to, or null.</summary>
        public static MissionDef OptionMission(string choice, string option)
        {
            foreach (var m in Campaign.OptionsOf(choice))
                if (m.Option == option) return m;
            return null;
        }

        // ------------------------------------------------------------------ D.6 story loot

        /// <summary>The line that says why the story hands a card out (a text key), or null for a card it does not.</summary>
        public static string LootReason(string card)
        {
            foreach (var (id, _) in Loot)
                if (id == card) return "loot." + card;
            return null;
        }

        // ------------------------------------------------------------------ D.7 intel files

        /// <summary>
        /// A file is recovered once its side objective is met (a side mission won, or its mission won with three stars), or
        /// (prompt 23 E) once a mission event has recovered it: an intercepted convoy carrying it.
        /// </summary>
        public static bool Found(IntelFile f) =>
            PlayerProfile.IntelRecovered(f.Id) || (f.ThreeStars ? PlayerProfile.Stars(f.Mission) >= 3 : PlayerProfile.Completed(f.Mission));

        public static List<IntelFile> IntelOf(int chapter)
        {
            var list = new List<IntelFile>();
            foreach (var f in Intel)
                if (f.Chapter == chapter) list.Add(f);
            return list;
        }

        /// <summary>
        /// Prompt 23 E: the files a battle's reward recovers now: its interceptions' (won or lost) and, for a win, the files its
        /// mission and stars open; none it had already, each once.
        /// </summary>
        public static List<IntelFile> FoundBy(MatchReward reward, bool won)
        {
            var list = won && reward.MissionId != null ? FoundBy(reward.MissionId, reward.Stars) : new List<IntelFile>();
            foreach (var id in reward.Intel)
                foreach (var f in Intel)
                    if (f.Id == id && !Found(f) && !list.Exists(x => x.Id == id)) list.Add(f);
            return list;
        }

        /// <summary>The files a win of <paramref name="missionId"/> with <paramref name="stars"/> stars recovers now (none it had already).</summary>
        public static List<IntelFile> FoundBy(string missionId, int stars)
        {
            var list = new List<IntelFile>();
            foreach (var f in Intel)
                if (f.Mission == missionId && !Found(f) && stars >= (f.ThreeStars ? 3 : 1)) list.Add(f);
            return list;
        }

        // ------------------------------------------------------------------ D.8 comic panels

        public static List<ComicPanel> ComicOf(int chapter)
        {
            var list = new List<ComicPanel>();
            foreach (var p in Comics)
                if (p.Chapter == chapter) list.Add(p);
            return list;
        }

        /// <summary>The first chapter or interlude finished whose panels have not been shown (0: none), in the order of play.</summary>
        public static int ComicPending
        {
            get
            {
                foreach (var c in Campaign.Chapters)
                    if (Campaign.ChapterEnabled(c.Number) && Campaign.ChapterDone(c.Number) && ComicOf(c.Number).Count > 0 &&
                        !PlayerProfile.ChapterSeen(PlayerProfile.ComicSeen(c.Number)))
                        return c.Number;
                return 0;
            }
        }

        // ------------------------------------------------------------------ D.3 arcs

        /// <summary>The characters with an arc, in the order the data gives them.</summary>
        public static List<string> ArcCharacters
        {
            get
            {
                var list = new List<string>();
                foreach (var b in Arcs)
                    if (!list.Contains(b.Who)) list.Add(b.Who);
                return list;
            }
        }

        public static List<ArcBeat> ArcOf(string who)
        {
            var list = new List<ArcBeat>();
            foreach (var b in Arcs)
                if (b.Who == who) list.Add(b);
            return list;
        }

        /// <summary>The payoff beats a mission carries (its page names whose story it ends).</summary>
        public static List<ArcBeat> PayoffsAt(string missionId)
        {
            var list = new List<ArcBeat>();
            foreach (var b in Arcs)
                if (b.Payoff && b.Mission == missionId) list.Add(b);
            return list;
        }
    }
}
