#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 31 L1: a unit the mission places on the player's side (Mara's Behemoth, Hawk's aircraft), driven by the allied
    /// AI under the player's Attack / Defend order; it takes no card slot. campaign.json fixedDeck.placedAllies[]. Spawned
    /// from prompt 31 L4 on (c6m03 first).
    /// </summary>
    public sealed class PlacedAllyDef
    {
        public string Def { get; set; } = "";
        public Vector2 Position { get; set; }
        public float Heading { get; set; }

        /// <summary>Its own name (a text key's last part: "behemoth_mara"); null: the unit's.</summary>
        public string? Name { get; set; }

        /// <summary>The def it stands in as until <see cref="Def"/> exists (a boss slot still being modelled).</summary>
        public string? Fallback { get; set; }

        /// <summary>The mission is lost when it falls (c6m03, c10m12).</summary>
        public bool LossIfDestroyed { get; set; }

        /// <summary>
        /// Prompt 31 L4: it is the mission's escorted convoy itself (c6m03: Mara's Behemoth is the Escort's convoy), so it is not
        /// spawned again: the escort rules drive it, and it holds while the player's general order is Defend.
        /// </summary>
        public bool Convoy { get; set; }

        /// <summary>The def the battle spawns: <see cref="Def"/>, else <see cref="Fallback"/> (null: neither is in the catalog).</summary>
        public string? SpawnDef(Catalog catalog) =>
            catalog.Vehicles.ContainsKey(Def) ? Def : Fallback != null && catalog.Vehicles.ContainsKey(Fallback) ? Fallback : null;

        internal static PlacedAllyDef Parse(JsonObject o) => new()
        {
            Def = o.String("def"),
            Position = new Vector2(o.Float("x", 0f), o.Float("z", 0f)),
            Heading = SimMath.DegToRad(o.Float("heading", 0f)),
            Name = o.OptionalString("name"),
            Fallback = o.OptionalString("fallback"),
            LossIfDestroyed = o.Bool("lossIfDestroyed", false),
            Convoy = o.Bool("convoy", false),
        };
    }

    /// <summary>
    /// Prompt 31 L1 (DECISIONS "Prompt 31 L0/L1/L2"): the deck the game hands out for a mission (sheet "Màn bộ bài game";
    /// campaign.json "fixedDeck", written by Tools/campaign/fixed_decks.py). Exactly <see cref="VehicleSlots"/> buyable vehicle
    /// cards and <see cref="SupportSlots"/> support cards; the player cannot change it. Its cards fight at the main deck's rank
    /// curve for that point of the campaign plus <see cref="RankBonus"/>, with no equipment (the Game layer, MissionDecks).
    /// A loaned card is usable in this mission only and never unlocked by it. The mission's objective is its own; the special
    /// rules change how it plays, and ride on the mission type's AI profile as flags (SimWorld.AddProfileFlags).
    /// </summary>
    public sealed class FixedDeckDef
    {
        public const int VehicleSlots = 8;
        public const int SupportSlots = 2;

        /// <summary>At most this many loaned cards a mission (c1m01, the first battle, has four: DECISIONS).</summary>
        public const int MaxLoaned = 2;

        public IReadOnlyList<string> Vehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> Supports { get; set; } = Array.Empty<string>();
        public IReadOnlyList<PlacedAllyDef> PlacedAllies { get; set; } = Array.Empty<PlacedAllyDef>();

        /// <summary>The deck's cards the player has not unlocked by this mission ("Loaned for this mission").</summary>
        public IReadOnlyList<string> Loaned { get; set; } = Array.Empty<string>();

        /// <summary>The mission's own rules (ids of fixed_decks.RULES; the text is "fixeddeck.rule.&lt;id&gt;").</summary>
        public IReadOnlyList<string> SpecialRules { get; set; } = Array.Empty<string>();

        /// <summary>The sheet's state: "MAKE_FIRST", "MAKE_LATER", or "READY" (MB_FINAL F3: the ten later decks, their rules made).</summary>
        public string Status { get; set; } = "MAKE_FIRST";

        /// <summary>Ranks above the campaign's curve the deck's cards fight at (i3m03, Crown's elite armour: 1).</summary>
        public int RankBonus { get; set; }

        /// <summary>Seconds the mission's boss waits on its route before it moves (c4m05: the trap is laid first).</summary>
        public float PrepSeconds { get; set; }

        public bool IsLoaned(string cardId)
        {
            foreach (var id in Loaned)
                if (id == cardId) return true;
            return false;
        }

        public bool HasRule(string rule)
        {
            foreach (var r in SpecialRules)
                if (r == rule) return true;
            return false;
        }

        /// <summary>The flags the special rules add to the mission type's AI profile ("rule:&lt;id&gt;").</summary>
        public IEnumerable<string> AiFlags
        {
            get
            {
                foreach (var r in SpecialRules) yield return "rule:" + r;
            }
        }

        internal static FixedDeckDef Parse(JsonObject o)
        {
            var allies = new List<PlacedAllyDef>();
            foreach (var a in o.Array("placedAllies")) allies.Add(PlacedAllyDef.Parse(a));
            return new FixedDeckDef
            {
                Vehicles = o.Has("vehicleIds") ? o.StringArray("vehicleIds") : Array.Empty<string>(),
                Supports = o.Has("supportIds") ? o.StringArray("supportIds") : Array.Empty<string>(),
                PlacedAllies = allies,
                Loaned = o.Has("loanedCards") ? o.StringArray("loanedCards") : Array.Empty<string>(),
                SpecialRules = o.Has("specialRules") ? o.StringArray("specialRules") : Array.Empty<string>(),
                Status = o.OptionalString("status") ?? "MAKE_FIRST",
                RankBonus = o.Int("rankBonus", 0),
                PrepSeconds = o.Float("prepSeconds", 0f),
            };
        }
    }
}
