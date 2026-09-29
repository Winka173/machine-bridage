#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// The tower-branch rework (DECISIONS 19T, A.5): how the AI picks a tower's rank-7 branch, by the deck it will face and
    /// its own loadout. Each branch is scored on paper: its guns' damage a second against the deck's cards (by their armour,
    /// aircraft for flyers, the damage table and penetration), plus what its mechanism is worth against that deck (the
    /// interceptors against what the deck fires, a dome against area fire, tower shields against focused fire, the loot
    /// depot against a swarm of cheap vehicles, the radar against aircraft, counter-battery against artillery, mines by
    /// the deck's armour, jamming, obstacles); a general's style weighs branches it likes ("tower.branch" in its
    /// weights). Deterministic: no draws.
    /// </summary>
    public static class BranchChoice
    {
        /// <summary>What a deck brings, as shares of its cards.</summary>
        public sealed class Threat
        {
            public float Air, Heavy, Light, Artillery, Drones, Straight, HeavyMissiles, Stealth;
            public readonly List<VehicleDef> Cards = new();
        }

        public static Threat Of(Catalog catalog, IEnumerable<string> deck)
        {
            var t = new Threat();
            foreach (var id in deck)
            {
                if (!catalog.Vehicles.TryGetValue(id, out var c) || c.Static) continue;
                t.Cards.Add(c);
                var w = c.Weapon;
                if (c.Flying) t.Air++;
                else if (c.Armor == ArmorClass.Heavy) t.Heavy++;
                else t.Light++;
                if (w.Damage > 0f && w.Projectile == ProjectileKind.Drone) t.Drones++;
                else if (w.Damage > 0f && !c.Flying && w.MinRange > 0f && w.CanTarget(false)) t.Artillery++;
                else if (w.Damage > 0f && (w.Guided || w.Projectile == ProjectileKind.Rocket)) t.Straight++;
                foreach (var m in c.Mounts)
                    if (DamageSystem.IsHeavyMissile(m.Weapon)) { t.HeavyMissiles++; break; }
                if (c.Stealth) t.Stealth++;
            }
            var n = Math.Max(1, t.Cards.Count);
            t.Air /= n; t.Heavy /= n; t.Light /= n; t.Artillery /= n; t.Drones /= n; t.Straight /= n; t.HeavyMissiles /= n; t.Stealth /= n;
            return t;
        }

        /// <summary>A branch's worth against the threat, in its guns' hundreds of damage a second.</summary>
        public static float Score(Catalog catalog, VehicleDef b, Threat t, int towers)
        {
            var score = 0f;
            // Its guns against the deck's cards.
            if (t.Cards.Count > 0)
            {
                var dps = 0f;
                foreach (var card in t.Cards)
                {
                    var armor = card.Flying ? ArmorClass.Air : card.Armor;
                    foreach (var m in b.Mounts)
                        if (m.Weapon.Damage > 0f) dps += FirePower.Sustained(m.Weapon, b) * Matchup.ClassEffect(catalog.Damage, m.Weapon, armor);
                }
                score += dps / t.Cards.Count / 100f;
                // Mines under the deck's vehicles (the blast on the roof of what drives over it).
                if (b.Mines is { } mines)
                {
                    var hit = 0f;
                    foreach (var card in t.Cards)
                        if (!card.Flying) hit += mines.Max * mines.Blast.Damage * (card.Armor == ArmorClass.Heavy ? 0.6f : 1f) / MathF.Max(1f, mines.Interval);
                    score += hit / t.Cards.Count / 100f;
                }
            }
            if (b.Aps is { } aps)
                score += (aps.Heavy ? 3f * t.HeavyMissiles : !aps.Direct ? 2f * (t.Artillery + t.Drones) : 2f * t.Straight) + aps.Charges * 0.02f;
            if (b.Dome != null) score += 1f + 1.5f * (t.Artillery + t.Drones);
            if (b.Wards != null) score += 1f + 1.5f * (t.Heavy + t.Straight) + MathF.Min(1f, towers / 10f);
            if (b.Relay != null) score += 1f;
            if (b.Loot != null) score += 0.6f + 1.2f * t.Light;
            if (b.RevealAir > 0f) score += 2f * t.Air + t.Stealth;
            if (b.CounterBattery != null) score += 2f * t.Artillery;
            if (b.Jammer > 0f) score += b.Jammer / 30f * 1.5f * (t.Drones + t.Straight);
            if (b.Obstacle) score += b.SlowAura != null ? 1f + t.Light : 1f + t.Heavy;
            if (b.TowerRangeAura != null) score += 0.3f + 2f * t.Stealth + (towers >= 6 ? 0.3f : 0f);
            return score;
        }

        private static Catalog? _refFor;
        private static Threat? _reference;

        /// <summary>
        /// What "a deck like any other" brings: the decks the commanders draw by roles (Normal and Hard, 16 seeds each), all
        /// their cards together; each branch's score is read against its score here, so the choice follows how this deck
        /// differs from the usual one.
        /// </summary>
        private static Threat Reference(Catalog catalog)
        {
            if (_refFor == catalog && _reference != null) return _reference;
            var pool = new List<string>();
            foreach (var v in catalog.Vehicles.Values)
                if (v.Card && v.CpCost > 0 && !v.Boss && !v.Static && !v.Elite) pool.Add(v.Id);
            pool.Sort(string.CompareOrdinal);
            var all = new List<string>();
            foreach (var difficulty in new[] { AI.AiDifficulty.Normal, AI.AiDifficulty.Hard })
                for (var seed = 1; seed <= 16; seed++)
                    all.AddRange(AI.ConquestAi.PickDeck(catalog, pool, difficulty, seed));
            _reference = Of(catalog, all);
            _refFor = catalog;
            return _reference;
        }

        /// <summary>
        /// The branch the AI takes for a tower (null: it has none): the one this deck suits best against how it does
        /// against the whole roster (so a branch is taken where it shines, not only where its numbers are bigger).
        /// </summary>
        public static string? Pick(Catalog catalog, string tower, Threat t, int towers, IReadOnlyDictionary<string, float>? style = null)
        {
            string? pick = null;
            var best = float.MinValue;
            var reference = Reference(catalog);
            foreach (var id in TowerCards.Branches(catalog, tower))
            {
                var def = catalog.Vehicles[id];
                var s = (Score(catalog, def, t, towers) + 0.1f) / (Score(catalog, def, reference, towers) + 0.1f);
                if (style != null && style.TryGetValue(id, out var bias)) s *= bias;
                if (s <= best) continue;
                pick = id;
                best = s;
            }
            return pick;
        }
    }
}
