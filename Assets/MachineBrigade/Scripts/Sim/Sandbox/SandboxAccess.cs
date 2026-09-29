#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>
    /// The two versions of the Sandbox (prompt 21 A). The internal build (development and test builds) has everything
    /// from the start. The player's opens once the last chapter switched on is finished, and offers only what the
    /// player has: unlocked vehicles, aircraft, towers and structures (a tower's branch once it is open), the elite
    /// versions of those, and the bosses and mini bosses they have beaten in the campaign or the Boss Hunt (never one
    /// of a chapter switched off), with the ships and escorts that come with them. It has no internal-only overlays and
    /// pays nothing. The game fills in the three questions (unlocked, beaten, switched on); the rules live here.
    /// </summary>
    public sealed class SandboxAccess
    {
        /// <summary>The internal build: no limits at all.</summary>
        public static readonly SandboxAccess Everything = new(true, _ => true, _ => true, _ => true);

        public SandboxAccess(bool internalBuild, Func<string, bool> unlocked, Func<string, bool> beaten, Func<string, bool> bossOn)
        {
            Internal = internalBuild;
            Unlocked = unlocked;
            Beaten = beaten;
            BossOn = bossOn;
        }

        public bool Internal { get; }

        /// <summary>A card the player has (a vehicle, aircraft, tower or a tower's branch).</summary>
        public Func<string, bool> Unlocked { get; }

        /// <summary>A boss or mini boss the player has brought down at least once (campaign or Boss Hunt).</summary>
        public Func<string, bool> Beaten { get; }

        /// <summary>A boss fought in a chapter switched on (or in none).</summary>
        public Func<string, bool> BossOn { get; }

        /// <summary>Internal-only overlays (E.6): hit boxes, routes, stuck vehicles, the AI's buying scores.</summary>
        public bool InternalLayers => Internal;

        /// <summary>Whether <paramref name="def"/> may be placed.</summary>
        public bool Allowed(Catalog catalog, VehicleDef def)
        {
            if (Internal) return true;
            if (def.Boss) return BossOn(def.Id) && Beaten(def.Id);
            if (def.BranchOf != null) return Unlocked(def.BranchOf) && Unlocked(def.Id);
            if (def.Elite) return def.EliteOf != null && Unlocked(def.EliteOf);
            if (Unlocked(def.Id)) return true;
            // Ships and escorts: those of a beaten boss's fleet or guard.
            if (def.Naval != null || !def.Card)
                foreach (var boss in catalog.Vehicles.Values)
                    if (boss.Boss && BossOn(boss.Id) && Beaten(boss.Id) && Escorts(catalog, boss).Contains(def.Id)) return true;
            return false;
        }

        /// <summary>The units that come with a boss: its escort groups' kinds.</summary>
        public static HashSet<string> Escorts(Catalog catalog, VehicleDef boss)
        {
            var set = new HashSet<string>();
            if (!catalog.Escorts.TryGetValue(boss.Id, out var escorts)) return set;
            void Wave(EscortWaveDef? w)
            {
                if (w == null) return;
                foreach (var u in w.Units) set.Add(u.Unit);
            }
            Wave(escorts.Arrive);
            foreach (var w in escorts.Phases) Wave(w);
            return set;
        }

        /// <summary>
        /// A scenario from someone else (a share code, F.7) made fit for this player: every unit they may not place
        /// is replaced by an allowed one in the same role (the same tab and class, the nearest price; a tower by a
        /// tower of its size), or removed when there is none. The notices say what changed ("from → to", "from → ").
        /// </summary>
        public List<(string from, string? to)> Fit(Catalog catalog, SandboxScenario scenario)
        {
            var changes = new List<(string, string?)>();
            if (Internal) return changes;
            var chosen = new Dictionary<string, string?>();
            for (var i = scenario.Units.Count - 1; i >= 0; i--)
            {
                var u = scenario.Units[i];
                if (catalog.Vehicles.TryGetValue(u.Def, out var def) && Allowed(catalog, def)) continue;
                if (!chosen.TryGetValue(u.Def, out var to))
                {
                    to = def != null ? Stand_in(catalog, def) : null;
                    chosen[u.Def] = to;
                    changes.Add((u.Def, to));
                }
                if (to == null) scenario.Units.RemoveAt(i);
                else
                {
                    u.Def = to;
                    u.Elite = u.Elite && catalog.EliteVariant(to) is { } e && Allowed(catalog, catalog.Vehicles[e]);
                    if (catalog.Vehicles[to].Boss) u.Boss ??= new SandboxBossState();
                    else u.Boss = null;
                }
            }
            changes.Reverse();
            foreach (var side in scenario.Sides)
            {
                side.Deck.RemoveAll(id => !catalog.Vehicles.TryGetValue(id, out var d) || !Allowed(catalog, d));
            }
            return changes;
        }

        /// <summary>The allowed unit that plays <paramref name="def"/>'s role most closely, or null.</summary>
        private string? Stand_in(Catalog catalog, VehicleDef def)
        {
            var tab = SandboxRules.TabOf(def);
            VehicleDef? best = null;
            var bestScore = float.MaxValue;
            foreach (var other in catalog.Vehicles.Values)
            {
                if (other.Id == def.Id || !Allowed(catalog, other)) continue;
                var otherTab = SandboxRules.TabOf(other);
                if (otherTab == null) continue;
                // The same tab first (a boss for a boss, a tower for a tower), then the same class, then the nearest price.
                var score = (otherTab == tab ? 0f : 1000f) + (other.Class == def.Class ? 0f : 100f) + MathF.Abs(other.CpCost - def.CpCost);
                if (def.Fort != null && other.Fort != null && other.Fort.Size != def.Fort.Size) score += 50f;
                if (other.Flying != def.Flying) score += 500f;
                if (score < bestScore || (Math.Abs(score - bestScore) < 1e-3f && best != null && string.CompareOrdinal(other.Id, best.Id) < 0))
                {
                    best = other;
                    bestScore = score;
                }
            }
            // Nothing of the same kind at all: better removed than turned into something else entirely.
            return best != null && bestScore < 1000f ? best.Id : null;
        }
    }
}
