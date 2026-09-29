#nullable enable
using System;
using System.Numerics;

namespace MachineBrigade.Sim.Economy
{
    /// <summary>
    /// Prompt 13 H.12: help for the side falling behind, once a match (Conquest, Deathmatch, King of
    /// the Hill, Assault; each mode sets its own). After <see cref="After"/> seconds, when one side's
    /// army on the field is worth <see cref="Ratio"/> times the other's or more, the weaker side's income
    /// goes up by <see cref="Income"/> for the rest of the match and it is flown one free reinforcement:
    /// two or three vehicles of its deck's average price. No health or damage is added. Both sides are told.
    /// </summary>
    public sealed class UnderdogRules
    {
        public float After { get; set; } = 240f;
        public float Ratio { get; set; } = 1.6f;
        public float Income { get; set; } = 1.25f;

        /// <summary>The smallest army the stronger side must have for the odds to count (the opening, a wiped board).</summary>
        public int MinimumArmy { get; set; } = 14;
    }

    internal sealed partial class EconomySystem
    {
        /// <summary>The mode's help for the side falling behind (null: none).</summary>
        public UnderdogRules? Underdog { get; set; }

        /// <summary>The side that got it (-1: nobody yet).</summary>
        public int UnderdogTeam { get; private set; } = -1;

        private void StepUnderdog()
        {
            if (Underdog is not { } rules || UnderdogTeam >= 0 || _world.Time < rules.After || _teams.Count != 2) return;
            if (!_teams.TryGetValue(0, out var a) || !_teams.TryGetValue(1, out var b)) return;
            var strong = a.ArmyCp >= b.ArmyCp ? a : b;
            var weak = strong == a ? b : a;
            if (strong.ArmyCp < rules.MinimumArmy || strong.ArmyCp < rules.Ratio * Math.Max(1, weak.ArmyCp)) return;
            UnderdogTeam = weak.Team;
            // The drop: the deck's vehicle nearest its average price, three of them for a cheap deck, two for a dear one.
            string? pick = null;
            var sum = 0f;
            var n = 0;
            foreach (var id in weak.Vehicles)
                if (_world.Catalog.Vehicles.TryGetValue(id, out var def) && def.CpCost > 0 && !def.Flying && def.Card)
                {
                    sum += def.CpCost;
                    n++;
                }
            if (n > 0)
            {
                var average = sum / n;
                var best = float.MaxValue;
                foreach (var id in weak.Vehicles)
                {
                    if (!_world.Catalog.Vehicles.TryGetValue(id, out var def) || def.CpCost <= 0 || def.Flying || !def.Card) continue;
                    var gap = MathF.Abs(def.CpCost - average);
                    if (gap >= best) continue;
                    best = gap;
                    pick = id;
                }
                if (pick != null && _world.Bases.TryGetDropZone(weak.Team, out var zone))
                {
                    var count = average <= 6f ? 3 : 2;
                    for (var i = 0; i < count; i++) Airlift(weak.Team, pick, zone);
                }
            }
            var at = _world.Bases.TryGetDropZone(weak.Team, out var told) ? told : Vector2.Zero;
            // The player's side hears it as help; the enemy getting it as a warning.
            _world.Emit(Events.SimEvent.Alert(at, weak.Team == 0 ? "assist.us" : "assist.them", bad: weak.Team != 0));
        }
    }
}
