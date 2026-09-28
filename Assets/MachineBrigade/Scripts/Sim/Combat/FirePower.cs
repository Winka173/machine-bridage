#nullable enable
using System;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Prompt 13 A.1: what a weapon can deliver over time on paper, counting everything that stops
    /// it firing: a salvo's rounds and its cooldown, a magazine and its change, and a launcher's
    /// rounds per load and its reload. The design document's damage table and the detail screen's
    /// damage a second both read it. It is still the weapon firing whenever it can: flying to the
    /// target, looping round, turning and holding out of reach are what the combat-value
    /// measurement adds (CombatValueMeasure).
    /// </summary>
    public static class FirePower
    {
        /// <summary>Damage of one trigger pull: the salvo, or a whole magazine.</summary>
        public static float Volley(WeaponDef w) => w.Damage * Math.Max(1, w.RoundsPerCycle);

        /// <summary>
        /// Damage a second over a whole load, before damage tables and bonuses: the rounds of a load
        /// over the time to fire them plus the time to reload them (a launcher standing still).
        /// </summary>
        public static float Sustained(WeaponDef w, VehicleDef? carrier = null)
        {
            if (w.Damage <= 0f) return 0f;
            var cycle = MathF.Max(0.05f, w.CycleSeconds);
            var perCycle = Volley(w);
            // A launcher's magazine (trigger pulls per load), reloaded in place.
            if (w.Ammo > 0) return perCycle * w.Ammo / (cycle * w.Ammo + w.MagazineReload);
            return perCycle / cycle;
        }

        /// <summary>Seconds of fire one full load lasts (0 for unlimited weapons).</summary>
        public static float LoadSeconds(WeaponDef w) => w.Ammo > 0 ? MathF.Max(0.05f, w.CycleSeconds) * w.Ammo : 0f;
    }
}
