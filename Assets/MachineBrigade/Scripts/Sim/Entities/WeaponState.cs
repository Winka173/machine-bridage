#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Per-mount firing state: its own cooldown, target, aim and salvo progress.</summary>
    internal sealed class WeaponState
    {
        public float Cooldown;

        /// <summary>Prompt 32 L4: this mount's own damage and cadence (a Fortress HQ's added gun, by HQ level); 1: as the data says.</summary>
        public float DamageScale = 1f, RateScale = 1f;

        /// <summary>Artillery walking its fire onto a target: which one, and how many rounds it has put near it.</summary>
        public EntityId BracketTarget;
        public int BracketShots;

        /// <summary>Rounds left, or -1 for a weapon with unlimited ammunition.</summary>
        public int Ammo = -1;

        /// <summary>An aircraft's stores (prompt 13 C): rounds when fully loaded (0: not stores), and the next round coming back.</summary>
        public int Load;

        public float LoadProgress;

        /// <summary>An empty magazine being reloaded in place: seconds still to go (0: not reloading).</summary>
        public float ReloadLeft;
        public EntityId Target;

        /// <summary>World heading of a free mount (pintle gun, chin turret), in radians.</summary>
        public float Heading;

        /// <summary>Shots still to fire in the current salvo, and time until the next one.</summary>
        public int BurstLeft;
        public float BurstTimer;
        public EntityId BurstTarget;
        public System.Numerics.Vector2 BurstAim;

        /// <summary>
        /// The bomb-run fix, pass 2 (DECISIONS "Ném bom rải thảm"): the stick under way, fixed when its first bomb goes: where
        /// bomb 0 lands (before its jitter), the way the stick runs (unit vector), the next bomb's index along it, and how many
        /// bombs this stick drops (its full count, or fewer on few targets).
        /// </summary>
        public System.Numerics.Vector2 StickStart, StickDir;
        public int StickNext, StickBombs;

        /// <summary>The salvo was aimed at an aircraft: later rounds keep bursting in the air.</summary>
        public bool BurstFlying;

        /// <summary>Damage of each round of the salvo under way against a plain round (Twin Feed spreads its bonus over the extra round).</summary>
        public float BurstScale = 1f;

        /// <summary>
        /// Machine guns fire in bursts: rounds left in the current run of fire (0: pausing, or not
        /// started), and whether the gun has fired yet (its first run starts after a random delay).
        /// </summary>
        public int RunLeft;
        public bool Started;

        /// <summary>A charged weapon powering up: seconds still to go (0: not charging).</summary>
        public float ChargeLeft;

        /// <summary>Play-test 8 A (DECISIONS 22Q): when this mount next weighs its target against everything else in reach.</summary>
        public double RetargetAt;

        /// <summary>Sustained fire: rounds left in the magazine (-1: a full one not yet started), and when the last round went.</summary>
        public int ClipLeft = -1;
        public double LastRoundAt = double.NegativeInfinity;

        /// <summary>
        /// Play-test 7 (DECISIONS 22P): when the mount's last round left, and when it last opened fire (a single shot, the
        /// first round of a salvo, a stream or a run): twin barrels open fire apart.
        /// </summary>
        public double FiredAt = double.NegativeInfinity;
        public double OpenedAt = double.NegativeInfinity;

        /// <summary>Prompt 17 C: a ramping weapon (the focused laser): the target it is on, since when, and its last round on it.</summary>
        /// <summary>Play-test 6 (DECISIONS 21F): the last two targets of a swarm's single drones (the next goes to another).</summary>
        public EntityId SwarmLast, SwarmBefore;

        public EntityId RampTarget;
        public double RampSince, RampLastAt = double.NegativeInfinity;

        /// <summary>
        /// Prompt 25 G (DECISIONS 25G): the round in the gun (0 its own, k its k-th second round), the one being loaded
        /// (-1: none) and when it will be in, and when the round now in went in (it stays at least 2 s).
        /// </summary>
        public int Round;
        public int Loading = -1;
        public double SwitchDoneAt;
        public double LoadedAt = double.NegativeInfinity;
    }
}
