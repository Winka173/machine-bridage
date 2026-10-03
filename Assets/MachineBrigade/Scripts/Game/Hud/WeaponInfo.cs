using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// How a weapon is named and drawn in unit details: a kind (main gun, machine gun,
    /// autocannon, howitzer, mortar, rockets, anti-tank or anti-air missile, flamethrower, bombs,
    /// kamikaze drones, laser, railgun) with its calibre, warhead, power or energy from the data's own
    /// fields (full fix L2: never the digits of the id, which read "26 mm" on every prompt 26 weapon),
    /// what it can hit, and whether it runs out of rounds. "Main gun" is the main mount's only; a gun
    /// on another mount is a "Gun". Worked out from the weapon's data, so new weapons need no new strings.
    /// </summary>
    public static class WeaponInfo
    {
        public readonly struct Line
        {
            public Line(string icon, string name, string targets, int ammo)
            {
                Icon = icon;
                Name = name;
                Targets = targets;
                Ammo = ammo;
            }

            public string Icon { get; }
            public string Name { get; }

            /// <summary>What it can hit, already worded ("Ground", "Air", "Ground + air").</summary>
            public string Targets { get; }

            /// <summary>Rounds carried, 0 for unlimited.</summary>
            public int Ammo { get; }
        }

        /// <summary>Every weapon a vehicle carries, main gun first (only the first mount is the "Main gun").</summary>
        public static List<Line> Of(VehicleDef def)
        {
            var lines = new List<Line>(def.Mounts.Count);
            for (var i = 0; i < def.Mounts.Count; i++) lines.Add(Describe(def.Mounts[i].Weapon, i == 0));
            return lines;
        }

        /// <summary>
        /// Full fix L2: the weapon's size in words from its data: "152 mm" (guns, rockets), "warhead 400 kg" (missiles,
        /// bombs, drones), "300 kW" (lasers), "64 MJ" (railguns); empty for a flamethrower or a close-in tool.
        /// </summary>
        public static string Spec(WeaponDef w)
        {
            var c = Strings.Culture;
            if (w.CaliberMm > 0f) return w.CaliberMm.ToString("0.##", c) + " mm";
            if (w.WarheadKg > 0f) return Strings.Format("wpn.warhead", ("kg", w.WarheadKg.ToString("0.##", c)));
            if (w.PowerKw > 0f) return w.PowerKw.ToString("0.##", c) + " kW";
            if (w.EnergyMj > 0f) return w.EnergyMj.ToString("0.##", c) + " MJ";
            return "";
        }

        public static Line Describe(WeaponDef w) => Describe(w, true);

        /// <summary>A weapon's line; <paramref name="main"/> is false for any mount but the first ("Gun", not "Main gun").</summary>
        public static Line Describe(WeaponDef w, bool main)
        {
            var (kind, icon) = Kind(w);
            if (kind == "gun" && !main) kind = "cannon";
            var name = Strings.Get("wpn." + kind);
            var spec = Spec(w);
            if (spec.Length > 0) name += " " + spec;
            var targets = w.Targets switch
            {
                TargetLayers.Air => Strings.Get("wpn.air"),
                TargetLayers.All => Strings.Get("wpn.all"),
                _ => Strings.Get("wpn.ground"),
            };
            return new Line(icon, name, targets, w.Ammo);
        }

        private static (string kind, string icon) Kind(WeaponDef w)
        {
            var id = w.Id;
            // Full fix L2: a laser, a railgun and a close-in tool are their own kinds (a laser was a "machine gun", a drill a "main gun").
            if (w.Melee || w.Family == "melee") return ("melee", "swords");
            if (w.Family == "laser" || w.PowerKw > 0f) return ("laser", "laser");
            if (w.Family == "railgun" || w.EnergyMj > 0f) return ("railgun", "railgun");
            switch (w.Projectile)
            {
                case ProjectileKind.Flame:
                    return ("flame", "flame");
                case ProjectileKind.Bomb:
                    return (id.Contains("guided") ? "guidedbomb" : "bombs", "bomb");
                case ProjectileKind.Drone:
                    return ("drones", "drone");
                case ProjectileKind.Missile:
                    if (id.Contains("ballistic")) return ("ballistic", "missile");
                    return w.Targets == TargetLayers.Air ? ("sam", "aa") : ("atgm", "missile");
                case ProjectileKind.Rocket:
                    if (id.Contains("thermobaric")) return ("thermobaric", "barrage");
                    return w.Indirect ? ("rockets", "barrage") : ("rocketpod", "barrage");
                case ProjectileKind.Bullet:
                    if (id.Contains("autocannon") || id.Contains("flak") || id.Contains("gunship_25") || id.Contains("gunship_40") ||
                        id.Contains("fighter_cannon") || id.Contains("jet_cannon") || id.Contains("heli_gun"))
                        return ("autocannon", "cannon");
                    if (id.Contains("agl")) return ("grenades", "mortar");
                    if (id.Contains("hmg") || id.Contains("minigun") || id.Contains("gatling") || id.Contains("gau") || id.Contains("tail_guns"))
                        return ("hmg", "mg");
                    return ("mg", "mg");
                default:
                    if (id.Contains("mortar")) return ("mortar", "mortar");
                    return w.LobbedLook || id.Contains("howitzer") ? ("howitzer", "artillery") : ("gun", "cannon");
            }
        }
    }
}
