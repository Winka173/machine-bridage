#nullable enable
using System;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Prompt 13 A.1: what a weapon can deliver over time on paper, counting everything that stops
    /// it firing: a salvo's rounds and its cooldown, a magazine and its change, a launcher's rounds
    /// per load and its reload, and an aircraft's stores per full load and the time to take them on
    /// again at the holding pattern's full rate. The design document's damage table and the detail
    /// screen's damage a second both read it. It is still the weapon firing whenever it can: flying
    /// to the target, looping round, turning and holding out of reach are what the combat-value
    /// measurement adds (CombatValueMeasure).
    /// </summary>
    public static class FirePower
    {
        /// <summary>Damage of one trigger pull: the salvo, or a whole magazine.</summary>
        public static float Volley(WeaponDef w) => w.Damage * Math.Max(1, w.RoundsPerCycle);

        /// <summary>
        /// Damage a second over a whole load, before damage tables and bonuses: the rounds of a load
        /// over the time to fire them plus the time to reload them (a launcher standing still; an
        /// aircraft's stores at the holding pattern's full rate: <paramref name="carrier"/>'s rearm time).
        /// </summary>
        public static float Sustained(WeaponDef w, VehicleDef? carrier = null) =>
            // Prompt 25 C1: a boss's own weapon damage on the ground, on what the combat system fires (not a weapon the boss
            // system lays).
            OnPaper(w, carrier) * (carrier != null && !w.Laid ? carrier.WeaponDamage : 1f);

        /// <summary>Prompt 25 C1: <see cref="Sustained"/> at aircraft (a boss's own weapon damage is the ground's only).</summary>
        public static float SustainedAir(WeaponDef w, VehicleDef? carrier = null) => OnPaper(w, carrier);

        private static float OnPaper(WeaponDef w, VehicleDef? carrier)
        {
            if (w.Damage <= 0f) return 0f;
            var cycle = MathF.Max(0.05f, w.CycleSeconds);
            var perCycle = Volley(w);
            // An aircraft's stores: the whole load fired, then taken on again.
            var load = carrier?.LoadOf(w) ?? 0;
            if (load > 0)
            {
                var pulls = MathF.Max(1f, MathF.Ceiling(load / (float)Math.Max(1, w.Burst)));
                return w.Damage * load / (cycle * pulls + MathF.Max(0f, carrier!.RearmTime));
            }
            // A launcher's magazine (trigger pulls per load), reloaded in place.
            if (w.Ammo > 0) return perCycle * w.Ammo / (cycle * w.Ammo + w.MagazineReload);
            return perCycle / cycle;
        }

        /// <summary>Seconds of fire one full load lasts (0 for unlimited weapons).</summary>
        public static float LoadSeconds(WeaponDef w, VehicleDef? carrier = null)
        {
            var load = carrier?.LoadOf(w) ?? 0;
            if (load > 0) return MathF.Max(0.05f, w.CycleSeconds) * MathF.Ceiling(load / (float)Math.Max(1, w.Burst));
            return w.Ammo > 0 ? MathF.Max(0.05f, w.CycleSeconds) * w.Ammo : 0f;
        }
    }
}
