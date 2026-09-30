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
        private static CultureInfo Culture => Strings.Culture;

        private static string N(float value) => value.ToString(value >= 10f || Math.Abs(value - MathF.Round(value)) < 0.05f ? "0" : "0.#", Culture);

        private static string F(string key, object value) => Strings.Format(key, value);

        private static string F(string key, params (string name, object value)[] args) => Strings.Format(key, args);

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
            lines.Add(F("ul.weapon", ("weapon", WeaponName(w)), ("type", Strings.Get("ul.type." + w.DamageType)), ("targets", targets.ToLower(Culture))));
            lines.Add(w.Burst > 1 ? F("ul.damageBurst", ("damage", N(w.Damage)), ("count", w.Burst)) : F("ul.damage", N(w.Damage)));
            lines.AddRange(Reload(def, w));
            // Prompt 17 C: the focused laser's ramp, the swarm's own targets.
            if (w.Ramp is { } ramp) lines.Add(F("ul.ramp", ("from", N(ramp.From)), ("to", N(ramp.To)), ("seconds", N(ramp.Seconds))));
            if (w.SwarmReach > 0f) lines.Add(F("ul.swarm", N(w.SwarmReach)));
            // Prompt 17 D.6: the heavy tank's gun changes rounds on its own.
            if (w.HeRound is { } he) lines.Add(F("ul.heRound", ("damage", N(he.Damage)), ("metres", N(he.SplashRadius))));
            var range = w.MinRange > 0f ? F("ul.rangeMin", ("metres", N(w.Range)), ("minimum", N(w.MinRange))) : F("ul.range", N(w.Range));
            lines.Add(w.SplashRadius > 0.5f ? F("ul.splash", ("range", range), ("metres", N(w.SplashRadius))) : range);
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
                lines.Add(F("ul.stores", ("count", load), ("noun", noun)));
                lines.Add(F("ul.storesRefill", N(def.RearmTime)));
                lines.Add(def.FixedWing
                    ? F("ul.storesFaster", ("pad", N(SupplyRules.PadRate)), ("hq", N(SupplyRules.HqRate)))
                    : F("ul.storesCarrier", ("pad", N(SupplyRules.PadRate)), ("hq", N(SupplyRules.HqRate)), ("times", N(SupplyRules.CarrierRate))));
                return lines;
            }
            if (w.Clip > 0)
            {
                lines.Add(F("ul.clip", ("count", w.Clip), ("seconds", N(w.ClipReload))));
                return lines;
            }
            if (w.Ammo > 0)
            {
                lines.Add(F(w.Burst > 1 ? "ul.salvos" : "ul.shots", ("count", w.Ammo), ("seconds", N(w.MagazineReload))));
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
            else if (w.MinRange > 0f) lines.Add(F("ul.move.artillery", ("minimum", N(w.MinRange)), ("maximum", N(w.Range))));
            else
            {
                if (def.Standoff) lines.Add(Strings.Get("ul.move.standoff"));
                lines.Add(Strings.Get(def.FiresWhileMoving ? "ul.move.onTheMove" : "ul.move.stops"));
            }
            // After firing.
            if (def.Scoot is { } scoot) lines.Add(F("ul.after.scoot", ("count", scoot.Shots), ("minimum", N(scoot.Min)), ("maximum", N(scoot.Max))));
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
                var when = Strings.Format("ul.when." + s.Trigger, ("seconds", N(s.Cooldown)), ("percent", N(s.Threshold * 100f)));
                lines.Add(F("ul.skill", ("skill", Strings.Get("ul.skill." + s.Kind)), ("when", when)));
            }
            if (def.Aps is { } aps)
            {
                // Prompt 20 L.1: interceptor missiles reloaded whole, and only rounds lobbed from afar (the Iron Dome).
                if (aps.Reload > 0f) lines.Add(F("ul.apsMagazine", ("metres", N(aps.Radius)), ("charges", aps.Charges), ("seconds", N(aps.Reload))));
                else lines.Add(F("ul.aps", ("metres", N(aps.Radius)), ("charges", aps.Charges), ("seconds", N(aps.Recharge))));
                if (!aps.Direct) lines.Add(Strings.Get("ul.apsLobbed"));
                else if (aps.Rockets) lines.Add(Strings.Get("ul.apsRockets"));
                if (aps.Shells > 0f) lines.Add(F("ul.apsShells", N(aps.Shells * 100f)));
            }
            if (def.Jammer > 0f) lines.Add(F("ul.jammer", N(def.Jammer)));
            if (def.RepairAura is { } repair) lines.Add(F("ul.repairAura", ("metres", N(repair.Radius)), ("percent", N(repair.Rate * 100f))));
            if (def.RearmAura is { } rearm) lines.Add(F("ul.rearmAura", ("metres", N(rearm.Radius)), ("seconds", N(rearm.Rate))));
            if (def.AirRearm is { } air) lines.Add(F("ul.airRearm", ("metres", N(air.Radius)), ("count", N(air.Rate))));
            if (def.Mines is { } mines) lines.Add(F("ul.mines", ("seconds", N(mines.Interval)), ("count", mines.Max)));
            if (def.CounterBattery is { } radar) lines.Add(F("ul.counterBattery", N(radar.Range)));
            if (def.Stealth) lines.Add(F("ul.stealth", N(VehicleDef.StealthSight * 100f)));
            if (def.Hidden != null) lines.Add(Strings.Get("ul.hidden"));
            // Prompt 17 C.
            if (def.Dome is { } dome) lines.Add(F("ul.dome", ("metres", N(dome.Radius)), ("health", N(dome.Hp)), ("seconds", N(dome.Recharge))));
            // Play-test 5 (DECISIONS 20W): the siege tank's two modes.
            if (def.Deploy is { Siege: true } siege)
            {
                lines.Add(F("ul.siege", ("seconds", N(siege.Seconds))));
                lines.Add(Strings.Get("ul.siege.tank"));
            }
            else if (def.Deploy is { } dep)
            {
                lines.Add(F("ul.deploy", ("seconds", N(dep.Seconds)), ("amount", dep.FrontUp), ("times", N(dep.Range))));
                lines.Add(F("ul.deploy.arc", N(dep.Arc * 180f / MathF.PI)));
            }
            if (def.Wingman is { } wing)
            {
                lines.Add(F("ul.wingman", N(wing.Follow)));
                lines.Add(F("ul.wingman.decoy", ("percent", N(wing.Pull * 100f)), ("metres", N(wing.Decoy))));
            }
            if (def.AirCapFree) lines.Add(F("ul.airCapFree", def.MaxPerSide));
            if (def.Sead) lines.Add(Strings.Get("ul.sead"));
            if (def.Relay is { } relay) lines.Add(F("ul.relay", ("cp", N(relay.Income)), ("cpSecond", N(relay.Second)), ("seconds", N(relay.Quiet))));
            // Prompt 25 F2 batch A (DECISIONS 25F2-A): the new units' and structures' mechanisms.
            if (def.BlastWall is { } wall) lines.Add(F("ul.blastWall", ("metres", N(wall.Radius)), ("percent", N(wall.Cut * 100f))));
            if (def.Decoy != null) lines.Add(Strings.Get("ul.decoy"));
            if (def.FireControl is { } fc) lines.Add(F("ul.fireControl", ("metres", N(fc.Radius)), ("percent", N(fc.Damage * 100f))));
            if (def.Searchlight is { } light) lines.Add(F("ul.searchlight", ("metres", N(light.Radius)), ("percent", N(light.Dazzle * 100f))));
            if (def.Balloon is { } balloon) lines.Add(F("ul.balloon", ("metres", N(balloon.Radius)), ("percent", N(balloon.Scatter * 100f))));
            if (def.SightJammer is { } screen) lines.Add(F("ul.sightJammer", ("metres", N(screen.Radius)), ("close", N(screen.Close))));
            if (def.Shelter is { } shelter) lines.Add(F("ul.shelter", ("metres", N(shelter.Radius)), ("percent", N(shelter.Cut * 100f))));
            if (def.Flares is { } flares) lines.Add(F("ul.flares", ("seconds", N(flares.Every)), ("metres", N(flares.Radius)), ("range", N(flares.Range))));
            if (def.Microwave is { } mw) lines.Add(F("ul.microwave", ("metres", N(mw.Range)), ("degrees", N(mw.Arc * 360f / MathF.PI)), ("seconds", N(mw.Cooldown))));
            if (def.DroneHunt is { } hunt) lines.Add(F("ul.droneHunt", N(hunt.Reach)));
            if (def.Paradrop is { } drop) lines.Add(F("ul.paradrop", N(drop.Fall)));
            if (def.ReconPass is { } pass) lines.Add(F("ul.reconPass", ("metres", N(pass.Width)), ("seconds", N(pass.Seconds))));
            if (def.TurretArc > 0f) lines.Add(F("ul.turretArc", N(def.TurretArc * 360f / MathF.PI)));
            if (def.SmokeSight) lines.Add(Strings.Get("ul.smokeSight"));
            if (def.StillVision > 0f) lines.Add(F("ul.stillVision", ("metres", N(def.StillVision)), ("seconds", N(def.StillAfter))));
            if (def.GlideRelease) lines.Add(Strings.Get("ul.glideRelease"));
            if (def.FlightTier == AltitudeTier.High) lines.Add(Strings.Get("ul.flightHigh"));
            foreach (var (arm, _) in Armed(def))
            {
                if (arm.GroundRange > 0f) lines.Add(F("ul.groundRange", ("air", N(arm.Range)), ("ground", N(arm.GroundRange))));
                if (arm.GroupPriority) lines.Add(Strings.Get("ul.groupPriority"));
                if (arm.BigGame) lines.Add(Strings.Get("ul.bigGame"));
                if (arm.JamProof) lines.Add(Strings.Get("ul.jamProof"));
                if (arm.OneAtATime) lines.Add(Strings.Get("ul.oneAtATime"));
                if (arm.Mrsi) lines.Add(F("ul.mrsi", arm.Burst));
                if (arm.Glides) lines.Add(Strings.Get("ul.glides"));
                if (arm.Lofted) lines.Add(Strings.Get("ul.lofted"));
                if (arm.Prey != Prey.Any) lines.Add(Strings.Get("ul.prey." + arm.Prey));
            }
            return lines;
        }

        /// <summary>A base module's service (G.4): the landing pad's rearm and mending, the hangar's aircraft, the depot's reload.</summary>
        /// <param name="all">False: only the aircraft lines (the detail screen lists the rest its own way).</param>
        public static IEnumerable<string> Module(UtilityDef u, bool all = true)
        {
            if (u.AirRepair > 0f) yield return F("ul.pad", ("metres", N(u.AirReach)), ("count", N(SupplyRules.PadRate * MathF.Max(1f, u.AirRearm))), ("percent", N(u.AirRepair * 100f)));
            if (u.AirCap > 0) yield return F("ul.airCap", u.AirCap);
            if (!all) yield break;
            if (u.Rearm > 1f) yield return F("ul.moduleRearm", N(u.Rearm));
            if (u.Repair > 0f) yield return Strings.Get("ul.moduleRepair");
            if (u.Supply > 0) yield return F("ul.moduleSupply", u.Supply);
        }
    }
}
