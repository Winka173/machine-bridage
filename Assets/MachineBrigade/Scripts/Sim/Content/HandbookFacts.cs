#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 32 L8: the rules' numbers the ammunition handbook quotes that live in code rather than in the data (the
    /// code reads them from here, so the handbook and the game cannot drift apart), and the handbook's worked example
    /// (balance.json "handbook").
    /// </summary>
    public static class HandbookFacts
    {
        /// <summary>The most of a shaped charge's damage a reactive-armour module takes off (a tandem warhead goes through).</summary>
        public const float ReactiveCap = 0.8f;
    }

    /// <summary>Prompt 32 L8: the handbook's worked example: one shot of the shooter's main weapon on the target's front and side.</summary>
    public sealed class HandbookDef
    {
        public string ExampleShooter { get; internal set; } = "ifv";
        public string ExampleTarget { get; internal set; } = "main_battle_tank";

        internal static HandbookDef Parse(JsonObject root)
        {
            var h = new HandbookDef();
            if (!root.Has("handbook")) return h;
            var o = root.Object("handbook");
            h.ExampleShooter = o.OptionalString("exampleShooter") ?? h.ExampleShooter;
            h.ExampleTarget = o.OptionalString("exampleTarget") ?? h.ExampleTarget;
            return h;
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>Prompt 32 L8: the ammunition handbook's worked example.</summary>
        public HandbookDef Handbook { get; internal set; } = new();
    }
}
