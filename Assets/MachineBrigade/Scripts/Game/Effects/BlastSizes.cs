using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// How much bigger than its tier's recipe a blast is drawn, by what made it (play-test
    /// feedback, DECISIONS 11A): a tank's round by the tank's class, a bomb by its weight, a
    /// cruise missile or the MOAB as wide as the ground it wrecks. The view's alone: damage and
    /// radii stay the simulation's (balance.json). Passed to <see cref="ExplosionEffect.Play"/>
    /// as its grow factor, which enlarges a blast without blowing its sprites up.
    /// </summary>
    internal static class BlastSizes
    {
        /// <summary>Tank rounds: light tanks and wheeled guns, main battle tanks and tank destroyers, heavy, siege and super-heavy tanks.</summary>
        public const float LightTank = 1.3f, MainTank = 1.4f, HeavyTank = 1.5f;

        /// <summary>
        /// How far out the Ultimate recipe's ground shockwave ring reaches at scale 1, in metres:
        /// the ring is drawn at 0.82 of its quad's half size, 16 x 1.6 m (x 1.04 on average) across.
        /// </summary>
        public const float UltimateReach = 0.82f * 16f * 1.6f * 1.04f * 0.5f;

        /// <summary>A tank gun's round, by the class of tank that fires it (others by their damage).</summary>
        public static float TankShell(WeaponDef w)
        {
            switch (w.Id)
            {
                case "gun_57mm":
                case "gun_105_wheeled":
                    return LightTank;
                case "gun_120mm":
                case "gun_125_elite":
                case "gun_105_twin":
                case "gun_105_long":
                case "gun_105_apfsds":
                case "gun_pit_105":
                case "bastion_gun":
                    return MainTank;
                case "gun_152":
                case "gun_152_heat":
                case "gun_140_twin":
                case "gun_203_siege":
                case "train_gun":
                    return HeavyTank;
            }
            if (w.Id.StartsWith("turret_gun_120")) return MainTank;
            return w.Damage < 120f ? LightTank : w.Damage < 300f ? MainTank : HeavyTank;
        }

        /// <summary>A bomb, by weapon or fire-support id: small guided bombs and bomblets least, the heavy iron bombs most.</summary>
        public static float Bomb(string id) => id switch
        {
            "guided_bomb" => 1.3f, // GBU-12, a small guided bomb
            "cluster_strike" => 1.3f, // bomblets
            "napalm_strike" => 1.3f, // canisters: the fire is the napalm's own
            "bomber_payload" => 1.45f, // carpet bombing, a dozen at a time
            "jet_bombs" => 1.5f, // FAB-500
            "stealth_payload" => 1.5f, // JDAM
            "airstrike" or "air_raid" => 1.5f, // Mk 84s off the strike jet
            _ => 1.4f,
        };

        /// <summary>A round landing on the ground: bombs by weight, the siege tank's 203 mm shell as a heavy tank's; others as they were.</summary>
        public static float Ground(WeaponDef w)
        {
            if (w == null) return 1f;
            if (w.Projectile == ProjectileKind.Bomb) return Bomb(w.Id);
            return w.Id == "gun_203_siege" ? HeavyTank : 1f;
        }

        /// <summary>A fire-support strike: bombing runs by their bombs; barrages and the rest as they were.</summary>
        public static float Strike(SupportDef s) => s != null && s.Kind == SupportKind.Airstrike ? Bomb(s.Id) : 1f;

        /// <summary>The grow factor that makes an Ultimate blast's shockwave reach <paramref name="blastRadius"/>.</summary>
        public static float Reach(float blastRadius) => Mathf.Max(1f, blastRadius / UltimateReach);
    }
}
