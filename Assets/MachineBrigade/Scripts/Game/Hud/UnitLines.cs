using System;
using System.Collections.Generic;
using System.Globalization;
using MachineBrigade.Sim.Abilities;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 13 G: a unit's ammunition and behaviour lines, worked out from its data (weapons, stores,
    /// reloads, flags, skills, auras, modules), never written by hand, so they stay true after every
    /// balance pass. The detail screen shows them (the weapons tab, the guide tab's Behaviour) and the
    /// design document exports them (ExportGameDoc "ammo" and "behavior").
    /// </summary>
    public static class UnitLines
    {
        private static CultureInfo Culture => Strings.Vietnamese ? CultureInfo.GetCultureInfo("vi-VN") : CultureInfo.InvariantCulture;

        private static string N(float value) => value.ToString(value >= 10f || Math.Abs(value - MathF.Round(value)) < 0.05f ? "0" : "0.#", Culture);

        private static string F(string key, params object[] args) => Strings.Format(key, args);

        /// <summary>The weapon's real name and calibre (from the data), else its kind ("Main gun 120 mm").</summary>
        public static string WeaponName(WeaponDef w)
        {
            if (!string.IsNullOrEmpty(w.RealName))
            {
                var name = w.RealName!;
                if (w.Size > 0f && !name.Contains(" mm") && w.Size >= 5f && w.Projectile is ProjectileKind.Bullet or ProjectileKind.Shell)
                    name += " " + N(w.Size) + " mm";
                return name;
            }
            return WeaponInfo.Describe(w).Name;
        }

        /// <summary>The weapons that do damage, main one first.</summary>
        private static IEnumerable<(WeaponDef w, int index)> Armed(VehicleDef def)
        {
            for (var i = 0; i < def.Mounts.Count; i++)
                if (def.Mounts[i].Weapon.Damage > 0f) yield return (def.Mounts[i].Weapon, i);
        }

        /// <summary>One weapon's lines (G.1): name and type, damage, magazine or stores and how they come back, range.</summary>
        public static List<string> Weapon(VehicleDef def, WeaponDef w)
        {
            var lines = new List<string>();
            var targets = w.Targets switch
            {
                TargetLayers.Air => Strings.Get("wpn.air"),
                TargetLayers.All => Strings.Get("wpn.all"),
                _ => Strings.Get("wpn.ground"),
            };
            lines.Add(F("ul.weapon", WeaponName(w), Strings.Get("ul.type." + w.DamageType), targets.ToLower(Culture)));
            lines.Add(w.Burst > 1 ? F("ul.damageBurst", N(w.Damage), w.Burst) : F("ul.damage", N(w.Damage)));
            lines.AddRange(Reload(def, w));
            // Prompt 17 C: the focused laser's ramp, the swarm's own targets.
            if (w.Ramp is { } ramp) lines.Add(F("ul.ramp", N(ramp.From), N(ramp.To), N(ramp.Seconds)));
            if (w.SwarmReach > 0f) lines.Add(F("ul.swarm", N(w.SwarmReach)));
            // Prompt 17 D.6: the heavy tank's gun changes rounds on its own.
            if (w.HeRound is { } he) lines.Add(F("ul.heRound", N(he.Damage), N(he.SplashRadius)));
            var range = w.MinRange > 0f ? F("ul.rangeMin", N(w.Range), N(w.MinRange)) : F("ul.range", N(w.Range));
            lines.Add(w.SplashRadius > 0.5f ? F("ul.splash", range, N(w.SplashRadius)) : range);
            return lines;
        }

        /// <summary>How the weapon's rounds come back: stores on the field, a magazine, shots reloaded in place, or never out.</summary>
        private static List<string> Reload(VehicleDef def, WeaponDef w)
        {
            var lines = new List<string>();
            var load = def.LoadOf(w);
            if (load > 0)
            {
                var noun = Strings.Get(w.Projectile switch
                {
                    ProjectileKind.Bomb => "ul.noun.Bomb",
                    ProjectileKind.Missile => "ul.noun.Missile",
                    ProjectileKind.Rocket => "ul.noun.Rocket",
                    ProjectileKind.Drone => "ul.noun.Drone",
                    _ => "ul.noun.other",
                });
                lines.Add(F("ul.stores", load, noun));
                lines.Add(F("ul.storesRefill", N(def.RearmTime)));
                lines.Add(def.FixedWing
                    ? F("ul.storesFaster", N(SupplyRules.PadRate), N(SupplyRules.HqRate))
                    : F("ul.storesCarrier", N(SupplyRules.PadRate), N(SupplyRules.HqRate), N(SupplyRules.CarrierRate)));
                return lines;
            }
            if (w.Clip > 0)
            {
                lines.Add(F("ul.clip", w.Clip, N(w.ClipReload)));
                return lines;
            }
            if (w.Ammo > 0)
            {
                lines.Add(F(w.Burst > 1 ? "ul.salvos" : "ul.shots", w.Ammo, N(w.MagazineReload)));
                return lines;
            }
            lines.Add(Strings.Get("ul.endless"));
            return lines;
        }

        /// <summary>Every weapon's lines together (the design document's "ammo").</summary>
        public static List<string> Ammo(Catalog catalog, VehicleDef def)
        {
            var lines = new List<string>();
            foreach (var (w, _) in Armed(def)) lines.AddRange(Weapon(def, w));
            if (def.Utility is { } u) lines.AddRange(Module(u));
            return lines;
        }

        private static bool HasStores(VehicleDef def)
        {
            foreach (var (w, _) in Armed(def))
                if (def.LoadOf(w) > 0) return true;
            return false;
        }

        private static bool Launcher(VehicleDef def)
        {
            if (def.Flying || def.Static) return false;
            foreach (var (w, _) in Armed(def))
                if (w.Ammo > 0 && w.Clip <= 0) return true;
            return false;
        }

        /// <summary>
        /// The Behaviour lines (G.2): how it moves and engages, what it does after firing, what it goes for
        /// first, when and where it pulls out, and its skills and auras with when they fire.
        /// </summary>
        public static List<string> Behaviour(Catalog catalog, VehicleDef def)
        {
            var lines = new List<string>();
            var w = def.Weapon;
            var armed = w.Damage > 0f;
            var bomber = def.Flying && def.FixedWing && w.Projectile == ProjectileKind.Bomb;
            // How it moves and engages.
            if (def.Static) lines.Add(Strings.Get(armed ? "ul.move.static" : "ul.move.building"));
            else if (def.Kamikaze) lines.Add(Strings.Get("ul.move.kamikaze"));
            else if (def.Orbit) lines.Add(Strings.Get("ul.move.orbit"));
            else if (bomber) lines.Add(Strings.Get("ul.move.bomber"));
            else if (def.Flying && def.FixedWing && def.Interceptor) lines.Add(Strings.Get("ul.move.interceptor"));
            else if (def.Flying && def.FixedWing) lines.Add(Strings.Get("ul.move.strike"));
            else if (def.Flying) lines.Add(Strings.Get("ul.move.hover"));
            else if (!armed || def.Class == UnitClass.Support) lines.Add(Strings.Get("ul.move.support"));
            else if (w.MinRange > 0f) lines.Add(F("ul.move.artillery", N(w.MinRange), N(w.Range)));
            else
            {
                if (def.Standoff) lines.Add(Strings.Get("ul.move.standoff"));
                lines.Add(Strings.Get(def.FiresWhileMoving ? "ul.move.onTheMove" : "ul.move.stops"));
            }
            // After firing.
            if (def.Scoot is { } scoot) lines.Add(F("ul.after.scoot", scoot.Shots, N(scoot.Min), N(scoot.Max)));
            if (def.Flying && def.FixedWing && !def.Kamikaze && !def.Orbit) lines.Add(Strings.Get("ul.after.pass"));
            if (armed && w.Clip > 1 && !def.Static) lines.Add(F("ul.after.clip", w.Clip));
            // Target priority.
            if (bomber) lines.Add(Strings.Get("ul.target.bomber"));
            else if (def.Interceptor || def.Class == UnitClass.AntiAir && w.Targets == TargetLayers.Air) lines.Add(Strings.Get("ul.target.air"));
            else if (def.StrongVs is { Count: > 0 } strong)
            {
                var names = new List<string>();
                foreach (var c in strong) names.Add(Strings.Get("class." + c));
                lines.Add(F("ul.target.strong", string.Join(", ", names)));
            }
            // When it pulls out, and where to.
            if (HasStores(def)) lines.Add(Strings.Get(bomber ? "ul.leave.bomber" : "ul.leave.stores"));
            if (def.Flying && !def.Kamikaze && !def.Boss && !def.Drone) lines.Add(Strings.Get("ul.leave.hurt"));
            if (Launcher(def)) lines.Add(Strings.Get("ul.leave.launcher"));
            // Skills, auras and what it does for its side.
            foreach (var s in def.Skills)
            {
                var when = Strings.Format("ul.when." + s.Trigger, N(s.Cooldown), N(s.Threshold * 100f));
                lines.Add(F("ul.skill", Strings.Get("ul.skill." + s.Kind), when));
            }
            if (def.Aps is { } aps)
            {
                // Prompt 20 L.1: interceptor missiles reloaded whole, and only rounds lobbed from afar (the Iron Dome).
                if (aps.Reload > 0f) lines.Add(F("ul.apsMagazine", N(aps.Radius), aps.Charges, N(aps.Reload)));
                else lines.Add(F("ul.aps", N(aps.Radius), aps.Charges, N(aps.Recharge)));
                if (!aps.Direct) lines.Add(Strings.Get("ul.apsLobbed"));
                else if (aps.Rockets) lines.Add(Strings.Get("ul.apsRockets"));
                if (aps.Shells > 0f) lines.Add(F("ul.apsShells", N(aps.Shells * 100f)));
            }
            if (def.Jammer > 0f) lines.Add(F("ul.jammer", N(def.Jammer)));
            if (def.RepairAura is { } repair) lines.Add(F("ul.repairAura", N(repair.Radius), N(repair.Rate * 100f)));
            if (def.RearmAura is { } rearm) lines.Add(F("ul.rearmAura", N(rearm.Radius), N(rearm.Rate)));
            if (def.AirRearm is { } air) lines.Add(F("ul.airRearm", N(air.Radius), N(air.Rate)));
            if (def.Mines is { } mines) lines.Add(F("ul.mines", N(mines.Interval), mines.Max));
            if (def.CounterBattery is { } radar) lines.Add(F("ul.counterBattery", N(radar.Range)));
            if (def.Stealth) lines.Add(F("ul.stealth", N(VehicleDef.StealthSight * 100f)));
            if (def.Hidden != null) lines.Add(Strings.Get("ul.hidden"));
            // Prompt 17 C.
            if (def.Dome is { } dome) lines.Add(F("ul.dome", N(dome.Radius), N(dome.Hp), N(dome.Recharge)));
            if (def.Deploy is { } dep)
            {
                lines.Add(F("ul.deploy", N(dep.Seconds), dep.FrontUp, N(dep.Range)));
                lines.Add(F("ul.deploy.arc", N(dep.Arc * 180f / MathF.PI)));
            }
            if (def.Wingman is { } wing)
            {
                lines.Add(F("ul.wingman", N(wing.Follow)));
                lines.Add(F("ul.wingman.decoy", N(wing.Pull * 100f), N(wing.Decoy)));
            }
            if (def.AirCapFree) lines.Add(F("ul.airCapFree", def.MaxPerSide));
            if (def.Sead) lines.Add(Strings.Get("ul.sead"));
            if (def.Relay is { } relay) lines.Add(F("ul.relay", N(relay.Income), N(relay.Second), N(relay.Quiet)));
            return lines;
        }

        /// <summary>A base module's service (G.4): the landing pad's rearm and mending, the hangar's aircraft, the depot's reload.</summary>
        /// <param name="all">False: only the aircraft lines (the detail screen lists the rest its own way).</param>
        public static IEnumerable<string> Module(UtilityDef u, bool all = true)
        {
            if (u.AirRepair > 0f) yield return F("ul.pad", N(u.AirReach), N(SupplyRules.PadRate * MathF.Max(1f, u.AirRearm)), N(u.AirRepair * 100f));
            if (u.AirCap > 0) yield return F("ul.airCap", u.AirCap);
            if (!all) yield break;
            if (u.Rearm > 1f) yield return F("ul.moduleRearm", N(u.Rearm));
            if (u.Repair > 0f) yield return Strings.Get("ul.moduleRepair");
            if (u.Supply > 0) yield return F("ul.moduleSupply", u.Supply);
        }
    }
}
