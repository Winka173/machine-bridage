using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// How much bigger than its tier's recipe a blast is drawn, by what made it (play-test
    /// feedback, DECISIONS 11A): a tank's round by the tank's class, a bomb by its weight, a
    /// cruise missile or the MOAB as wide as the ground it wrecks. The view's alone: damage and
    /// radii stay the simulation's (balance.json). Passed to <see cref="ExplosionEffect.Play"/>
    /// as its grow factor, which enlarges a blast without blowing its sprites up. The second
    /// play test (DECISIONS 12C) made every blast a tenth bigger on top (<see cref="Bigger"/>),
    /// drone blasts bigger by the drone, and tank rounds linger longer by the tank's class.
    /// </summary>
    internal static class BlastSizes
    {
        /// <summary>Tank rounds: light tanks and wheeled guns, main battle tanks and tank destroyers, heavy, siege and super-heavy tanks.</summary>
        public const float LightTank = 1.3f, MainTank = 1.4f, HeavyTank = 1.5f;

        /// <summary>
        /// Every blast of a bomb, missile, drone or shell a tenth bigger again, multiplied onto
        /// the factors here (second play test, DECISIONS 12C). Bullets and flak (the Small tier)
        /// and falling buildings are not blasts and keep their size.
        /// </summary>
        public const float Bigger = 1.1f;

        /// <summary>
        /// How much longer a tank round's fireball, smoke, dust and embers last, by the same
        /// classes (the flash, sparks and air snap stay as quick): light +20 %, main battle and
        /// tank destroyers +25 %, heavy, siege and super-heavy +30 % (DECISIONS 12C).
        /// </summary>
        public const float LightLife = 1.2f, MainLife = 1.25f, HeavyLife = 1.3f;

        /// <summary>Drone blasts by the drone: small FPVs, the Lancet (and the mothership's drones), the Shahed and strike drones.</summary>
        public const float FpvDrone = 1.2f, LancetDrone = 1.25f, HeavyDrone = 1.3f;

        /// <summary>
        /// How far out the Ultimate recipe's ground shockwave ring reaches at scale 1, in metres:
        /// the ring is drawn at 0.82 of its quad's half size, 16 x 1.6 m (x 1.04 on average) across.
        /// </summary>
        public const float UltimateReach = 0.82f * 16f * 1.6f * 1.04f * 0.5f;

        private enum Class
        {
            Light,
            Main,
            Heavy,
        }

        /// <summary>The class of tank a gun belongs to (others by their damage).</summary>
        private static Class ClassOf(WeaponDef w)
        {
            switch (w.Id)
            {
                case "gun_57mm":
                case "gun_105_wheeled":
                    return Class.Light;
                case "gun_120mm":
                case "gun_125_elite":
                case "gun_105_twin":
                case "gun_105_long":
                case "gun_105_apfsds":
                case "gun_pit_105":
                case "bastion_gun":
                    return Class.Main;
                case "gun_152":
                case "gun_152_heat":
                case "gun_140_twin":
                case "gun_203_siege":
                case "train_gun":
                    return Class.Heavy;
            }
            if (w.Id.StartsWith("turret_gun_120")) return Class.Main;
            return w.Damage < 120f ? Class.Light : w.Damage < 300f ? Class.Main : Class.Heavy;
        }

        /// <summary>A tank gun's round, by the class of tank that fires it (others by their damage).</summary>
        public static float TankShell(WeaponDef w) => ClassOf(w) switch
        {
            Class.Light => LightTank,
            Class.Main => MainTank,
            _ => HeavyTank,
        };

        /// <summary>How much longer a tank gun's round lingers, by the class of tank that fires it.</summary>
        public static float ShellLife(WeaponDef w) => ClassOf(w) switch
        {
            Class.Light => LightLife,
            Class.Main => MainLife,
            _ => HeavyLife,
        };

        /// <summary>A round landing on the ground lingers like a tank's when a tank fired it (the siege tank's 203 mm); others as they were.</summary>
        public static float GroundLife(WeaponDef w) => w != null && w.Id == "gun_203_siege" ? HeavyLife : 1f;

        /// <summary>
        /// A drone's blast by the drone (1 for anything else): FPVs (the carrier's swarm, the
        /// hangars', the airship's) +20 %, the Lancet and the mothership's attack drones +25 %,
        /// the Shahed and the strike drone's missiles +30 % (DECISIONS 12C).
        /// </summary>
        public static float Drone(WeaponDef w)
        {
            if (w == null) return 1f;
            if (w.Id.StartsWith("shahed") || w.Id == "drone_missile") return HeavyDrone;
            if (w.Id.StartsWith("lancet") || w.Id == "mothership_drones") return LancetDrone;
            return w.Projectile == ProjectileKind.Drone ? FpvDrone : 1f;
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
