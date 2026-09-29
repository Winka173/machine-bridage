#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 22 E (DECISIONS 22E): a boss's duel mode, for a mission where the player has aircraft only (Morrigan in
    /// chapter 10). In a duel the boss flies without escorts, uses the duel's big attack, and now and then goes dark:
    /// it breaks off, holds its fire and flares for <see cref="VanishSeconds"/>, so its stealth hides it again.
    /// </summary>
    public sealed class DuelDef
    {
        /// <summary>The duel's big attack id (null: its own).</summary>
        public string? BigAttackId { get; internal set; }

        public BigAttackDef? BigAttack { get; internal set; }

        /// <summary>Its escorts come along in a duel too (Morrigan's do not).</summary>
        public bool Escorts { get; internal set; }

        /// <summary>It goes dark each time its health falls through one of these shares (0.75 and 0.4 ...).</summary>
        public float[] VanishAt { get; internal set; } = Array.Empty<float>();

        /// <summary>... and every this many seconds of the duel besides (0: only at the marks).</summary>
        public float VanishEvery { get; internal set; }

        /// <summary>Seconds it stays dark (no fire, stealth hides it beyond close range).</summary>
        public float VanishSeconds { get; internal set; } = 5f;
    }

    public sealed partial class VehicleDef
    {
        /// <summary>Prompt 22 E: its duel mode, or null.</summary>
        public DuelDef? Duel { get; internal set; }

        /// <summary>
        /// Prompt 22 E: a scripted story unit (Mara's Behemoth): only a mission places it, on the side it names; it is
        /// never a card, never bought, never unlocked, and never drawn for a deck or the Sandbox.
        /// </summary>
        public bool StoryOnly { get; internal set; }
    }

    public sealed partial class Catalog
    {
        private static void ParseP22(JsonObject v, VehicleDef def)
        {
            def.StoryOnly = v.Bool("storyOnly", false);
            if (def.StoryOnly) def.Card = false;
            if (!v.Has("duel")) return;
            var d = v.Object("duel");
            def.Duel = new DuelDef
            {
                BigAttackId = d.Has("bigAttack") ? d.String("bigAttack") : null,
                Escorts = d.Bool("escorts", false),
                VanishAt = d.Has("vanishAt") ? ToArray(d.FloatArray("vanishAt")) : Array.Empty<float>(),
                VanishEvery = MathF.Max(0f, d.Float("vanishEvery", 0f)),
                VanishSeconds = MathF.Max(0.5f, d.Float("vanishSeconds", 5f)),
            };
        }

        private static float[] ToArray(System.Collections.Generic.IReadOnlyList<float> list)
        {
            var a = new float[list.Count];
            for (var i = 0; i < a.Length; i++) a[i] = Math.Clamp(list[i], 0f, 1f);
            return a;
        }

        /// <summary>A duel's big attack is resolved and checked like the boss's own (its parts must be the boss's).</summary>
        private void FinishP22()
        {
            foreach (var v in _vehicles.Values)
            {
                if (v.StoryOnly && v.Boss) throw new FormatException($"{v.Id}: a story unit is no boss.");
                if (v.Duel is not { BigAttackId: { } id } duel) continue;
                if (!BigAttacks.TryGetValue(id, out var attack)) throw new FormatException($"{v.Id}.duel.bigAttack: unknown big attack '{id}'.");
                foreach (var s in attack.Strikes)
                    foreach (var p in s.Parts)
                        if (v.PartIndex(p) < 0) throw new FormatException($"{v.Id}.duel.bigAttack {id}: the boss has no part '{p}'.");
                duel.BigAttack = attack;
            }
        }
    }
}
