#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Balance pack (lane B, §3): read-only numbers the export needs that the game computes or builds its data by. Nothing
    /// here is called by the battle: these functions only restate the game's rules (the locked pricing rules of
    /// <see cref="SimTunables.Vehicles.PriceRules"/>, the supply curve of <see cref="Economy.TeamEconomy"/>, the opening
    /// squad of <see cref="Modes.OpeningSquads"/>) for ExportGameDoc.
    /// </summary>
    public static class BalancePackFacts
    {
        /// <summary>The price group (1: ≤ 4 CP, 2: 5-8, 3: 9-13, 4: ≥ 14) of a base price.</summary>
        public static int PriceGroup(int baseCp)
        {
            var bounds = SimTunables.Vehicles.PriceRules.GroupMaxCp;
            for (var i = 0; i < bounds.Length; i++)
                if (baseCp <= bounds[i]) return i + 1;
            return bounds.Length + 1;
        }

        /// <summary>The group's price factor (x1.0 / x1.15 / x1.25 / x1.3).</summary>
        public static float PriceFactor(int baseCp)
        {
            var factors = SimTunables.Vehicles.PriceRules.GroupFactor;
            return factors[Math.Min(PriceGroup(baseCp), factors.Length) - 1];
        }

        /// <summary>A price before the group factor times it, rounded half up (the rule the data's prices were built by).</summary>
        public static int GroupedPrice(int oldCp) => SimMath.RoundHalfUp(oldCp * (double)PriceFactor(oldCp));

        /// <summary>
        /// A splash (area) unit for the power bonus HOLD: its main weapon fires indirectly, from a minimum range (artillery,
        /// rockets, cruise and ballistic missiles, lobbed drones), or drops bombs.
        /// </summary>
        public static bool IsSplashUnit(VehicleDef v)
        {
            var w = v.Weapon;
            if (w == null) return false;
            return w.Indirect || w.Glides;
        }

        /// <summary>
        /// The power bonus: min(cap, perCp x (baseCP - from)), never below 0; a splash unit's is 0 while
        /// <see cref="SimTunables.Vehicles.PriceRules.SplashBonus"/> is off (the HOLD).
        /// </summary>
        public static float PowerBonus(int baseCp, bool splash)
        {
            if (splash && !SimTunables.Vehicles.PriceRules.SplashBonus) return 0f;
            var bonus = SimTunables.Vehicles.PriceRules.BonusPerCp * (baseCp - SimTunables.Vehicles.PriceRules.BonusFromCp);
            return Math.Clamp(bonus, 0f, SimTunables.Vehicles.PriceRules.BonusCap);
        }

        /// <summary>The drop time the rule gives a base price (≤ 4 CP: 2.5 s, ≥ 15: 5 s, else 3.5 s).</summary>
        public static float DropTimeByGroup(int baseCp) =>
            baseCp <= SimTunables.Vehicles.PriceRules.DropSmallMaxCp ? SimTunables.Vehicles.PriceRules.DropSmallSeconds
            : baseCp >= SimTunables.Vehicles.PriceRules.DropLargeMinCp ? SimTunables.Vehicles.PriceRules.DropLargeSeconds
            : SimTunables.Vehicles.PriceRules.DropMiddleSeconds;

        /// <summary>
        /// A mode's supply line as the game computes it for a side with no bonus and no commander: the data's army cap
        /// (economy.armyCap), the army cap after the supply and price scales (<see cref="Economy.TeamEconomy.ArmyCap"/>) and the
        /// supply (the army value kept at full income).
        /// </summary>
        public static (int armyCapData, int armyCap, int supply) SupplyLine(Catalog catalog, string? mode)
        {
            var data = catalog.ArmyCapFor(mode);
            var cap = (int)MathF.Round(data * SimTunables.Modes.EconomyRules.SupplyPriceScale * catalog.SupplyScale);
            var supply = (int)Math.Floor(cap * (double)SimTunables.Modes.EconomyRules.SupplyPerArmyCap);
            return (data, cap, supply);
        }

        /// <summary>The round kinds of the interception table (Khac_che chan_*), in its column order.</summary>
        public static readonly string[] RoundKinds =
            { "directMissile", "heavyMissile", "drone", "directRocket", "artilleryRocket", "mortarShell", "artilleryShell", "tankShell", "bomb" };

        /// <summary>A weapon's round kind for the interception table ("other": bullets, flames, beams, which nothing takes).</summary>
        public static string RoundKind(WeaponDef w)
        {
            if (w.Beam || w.DamageType == DamageType.Energy) return "other";
            if (Combat.DamageSystem.IsHeavyMissile(w)) return "heavyMissile";
            switch (w.Projectile)
            {
                case ProjectileKind.Missile: return "directMissile";
                case ProjectileKind.Drone: return "drone";
                case ProjectileKind.Rocket: return w.MinRange > 0f ? "artilleryRocket" : "directRocket";
                case ProjectileKind.Bomb: return "bomb";
                case ProjectileKind.Shell:
                    if (!w.Indirect) return "tankShell";
                    var mortar = (w.Family ?? "").Contains("mortar") || w.Id.Contains("mortar");
                    return mortar ? "mortarShell" : "artilleryShell";
                default: return "other";
            }
        }

        /// <summary>
        /// Whether <paramref name="carrier"/>'s protection system may take <paramref name="w"/>'s round at all, by the static
        /// rules of DamageSystem.TryIntercept (a vehicle's own APS, a point defence, a boss's) and DamageSystem.GunTakes (a gun
        /// point defence with a burst): reach, interceptors left, smoke, stuns and the rolls are left out.
        /// <paramref name="shellShare"/>: the share of lobbed shells it takes (1 for the rest).
        /// </summary>
        public static bool MayIntercept(VehicleDef carrier, WeaponDef w, out float shellShare)
        {
            shellShare = 1f;
            var a = carrier.Aps;
            if (a == null) return false;
            if (a.Burst > 0f)
            {
                if (!Combat.DamageSystem.GunTakes(a, w, out var partial)) return false;
                if (partial) shellShare = a.Shells;
                return true;
            }
            if (w.Beam || w.DamageType == DamageType.Energy || w.Interceptable == false) return false;
            var kind = w.Projectile;
            var direct = w.Guided || w.Glides || (kind == ProjectileKind.Rocket && w.MinRange <= 0f);
            var rocket = kind == ProjectileKind.Rocket;
            var shell = kind == ProjectileKind.Shell && w.Indirect;
            var heavy = Combat.DamageSystem.IsHeavyMissile(w);
            if (!direct && !rocket && !shell && !heavy) return false;
            var lobbed = kind == ProjectileKind.Drone || w.Glides || (w.MinRange > 0f && kind is ProjectileKind.Rocket or ProjectileKind.Missile);
            if (a.Heavy && !heavy) return false;
            if (carrier.InterceptionMode == InterceptionMode.SelfAps && (w.ApsEligible == false || !(direct || kind == ProjectileKind.Drone))) return false;
            if (!a.Heavy && !direct && rocket && !a.Rockets) return false;
            if (!a.Heavy && !a.Direct && direct && !lobbed) return false;
            if (!a.Heavy && !direct && shell)
            {
                if (a.Shells <= 0f) return false;
                shellShare = a.Shells;
            }
            return true;
        }

        /// <summary>
        /// A ground shooter's round flight in seconds over <paramref name="distance"/> (CombatSystem's launch rule: distance /
        /// speed; a warned round lands no sooner than its warning); bombs from aircraft and salvo timing are left out.
        /// </summary>
        public static float FlightSeconds(Catalog catalog, WeaponDef w, float distance)
        {
            if (w.ProjectileSpeed <= 0f) return 0f;
            var travel = distance / w.ProjectileSpeed;
            if (w.WarnSeconds > travel && catalog.Warnings.Warns(w)) travel = w.WarnSeconds;
            return travel;
        }

        /// <summary>
        /// A vehicle's self-defence (Xe / Thap: tu_ve, so_lan, hoi_tu_ve_s): "aps" (its protection system: interceptors and
        /// seconds per interceptor), "flare" (charges and the seconds to get one back) or "none".
        /// </summary>
        public static (string kind, int charges, float rechargeSeconds) SelfDefence(VehicleDef v)
        {
            if (v.Aps is { } aps) return ("aps", aps.Charges, aps.Recharge);
            SkillDef? flare = null;
            foreach (var s in v.Skills)
                if (s.Kind == SkillKind.Flares) flare = s;
            if (v.FlareCharges > 0) return ("flare", v.FlareCharges, v.FlareRecharge ?? flare?.Cooldown ?? 0f);
            if (flare != null) return ("flare", 1, flare.Cooldown);
            return ("none", 0, 0f);
        }

        /// <summary>The upkeep (income share kept) at an army value of <paramref name="armyCp"/> against <paramref name="supply"/>.</summary>
        public static float Upkeep(int armyCp, int supply) => Economy.TeamEconomy.UpkeepFor(armyCp, supply);

        /// <summary>The underdog's income boost for an army of <paramref name="own"/> CP against <paramref name="rival"/>.</summary>
        public static float CatchUp(int own, int rival) => Economy.EconomySystem.CatchUpFor(own, rival);

        /// <summary>A kill's refund share with no odds and no equipment (the base quarter, capped).</summary>
        public static float KillShare() => Economy.EconomySystem.KillShare(1f, 1f);

        /// <summary>
        /// The opening squad a side gets in <paramref name="mode"/> from <paramref name="roles"/> and its deck (empty: every
        /// card), out of a starting CP of <paramref name="startCp"/> (before the mode's scale): the cards, their baseCP and the
        /// share of the scaled starting CP they take (at most <see cref="OpeningRules.Share"/>).
        /// </summary>
        public static (List<string> squad, int cp, float startCp, float share) OpeningSquad(Catalog catalog, string mode,
            IReadOnlyList<string> roles, IReadOnlyList<string> deck, float startCp)
        {
            var start = catalog.Opening.StartCp(mode, startCp);
            var squad = Modes.OpeningSquads.Pick(catalog, roles, deck, start * catalog.Opening.Share);
            var cp = 0;
            foreach (var id in squad) cp += catalog.Vehicles[id].BaseCp;
            return (squad, cp, start, start > 0f ? cp / start : 0f);
        }
    }
}
