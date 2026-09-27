using System.Collections.Generic;
using System.Text.RegularExpressions;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// How a weapon is named and drawn in unit details: a kind (main gun, machine gun,
    /// autocannon, howitzer, mortar, rockets, anti-tank or anti-air missile, flamethrower, bombs,
    /// kamikaze drones) with its calibre when the weapon's id carries one, what it can hit, and
    /// whether it runs out of rounds. Worked out from the weapon's data, so new weapons need no
    /// new strings.
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

        private static readonly Regex Calibre = new(@"(\d{2,3})");

        /// <summary>Every weapon a vehicle carries, main gun first.</summary>
        public static List<Line> Of(VehicleDef def)
        {
            var lines = new List<Line>(def.Mounts.Count);
            foreach (var mount in def.Mounts) lines.Add(Describe(mount.Weapon));
            return lines;
        }

        public static Line Describe(WeaponDef w)
        {
            var id = w.Id;
            var (kind, icon) = Kind(w);
            var name = Strings.Get("wpn." + kind);
            var calibre = Calibre.Match(id);
            if (calibre.Success && int.Parse(calibre.Value) >= 20 && kind is "gun" or "autocannon" or "howitzer" or "mortar" or "rockets")
                name += " " + calibre.Value + " mm";
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
                    return w.Indirect || id.Contains("howitzer") ? ("howitzer", "artillery") : ("gun", "cannon");
            }
        }
    }
}
