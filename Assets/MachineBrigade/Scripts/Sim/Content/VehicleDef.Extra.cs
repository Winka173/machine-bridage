#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 8's vehicle data: the equipment branch, the breacher's and the SP gun's mechanisms, the
    /// elite's army cost, and the new bosses' parts, lock, boring, landings, emplacements and attached
    /// models. Kept apart from Definitions.cs so the two grow without stepping on each other.
    /// </summary>
    /// <summary>Prompt 29 S07: apsCapability.</summary>
    public enum ApsCapability
    {
        None,
        BuiltIn,
        RetrofitEligible,
    }

    /// <summary>Prompt 29 S07: interceptionSystem.mode (bosses keep their numbers: BossSelfAps).</summary>
    public enum InterceptionMode
    {
        SelfAps,
        PointDefense,
        BossSelfAps,
    }

    public sealed partial class VehicleDef
    {
        /// <summary>
        /// Play-test 13 (lane C): it carries no weapon (a tanker, a heavy-lift helicopter, a support building): every mount's
        /// weapon deals no damage (the placeholder "none"). The card then shows no gun rows, not a gun of 0 damage.
        /// </summary>
        public bool Unarmed
        {
            get
            {
                if (Weapon.Damage > 0f) return false;
                foreach (var m in Mounts)
                    if (m.Weapon.Damage > 0f) return false;
                return true;
            }
        }

        /// <summary>The army branch whose equipment loadout it wears (see <see cref="ArmyBranch"/>).</summary>
        public ArmyBranch Branch { get; internal set; }

        /// <summary>
        /// Everything it fires hits this many times as hard (an elite: balance.json "elites.damageScale",
        /// 1.25, unless the def names its own "damageScale"); 1 for the rest.
        /// </summary>
        public float DamageScale { get; internal set; } = 1f;

        /// <summary>
        /// Prompt 25 C1 (DECISIONS 25C): a boss's own weapons' damage multiplier (data "weaponDamage"), so its ordinary
        /// fire meets the balance sheet's target damage a second against armour 3. Only what the combat system fires at
        /// the ground takes it (never a weapon the boss system lays: a ship's main battery, the supergun's shell, the
        /// crusher; never a round at an aircraft), on top of its rank's <see cref="DamageScale"/>;
        /// <see cref="Combat.FirePower.Sustained"/> counts it too.
        /// </summary>
        public float WeaponDamage { get; internal set; } = 1f;

        /// <summary>
        /// Boss design 09/10: its guns' fire rate against the rank's and the data's, from the workbook's "gunNerf.rate" (sheet 03,
        /// the old guns' tempo; 1: unchanged). Multiplies <see cref="Entities.Vehicle.RankFire"/>.
        /// </summary>
        public float FireScale { get; internal set; } = 1f;

        /// <summary>Boss design 09/10: the DPS budget of its new hardpoints at weapon level (sheet 03 col L; 0: it adds none).</summary>
        public float NewGunDps { get; internal set; }

        /// <summary>Boss design 09/10: the whole gun DPS of a new mini boss at weapon level (sheet 05), shared evenly by all its mounts (0: not used).</summary>
        public float GunDpsAll { get; internal set; }

        /// <summary>Boss design 09/10: the damage share of "gunNerf" (already folded into <see cref="WeaponDamage"/>); new guns are scaled against it.</summary>
        public float GunNerfDamage { get; internal set; } = 1f;

        /// <summary>
        /// Prompt 29 S03 (D2, R8): this vehicle's damage on every weapon it fires (ground and air, rank and boss multipliers
        /// on top), so a card is balanced without editing a weapon other vehicles share. Fire rate, magazine, reload and
        /// round count stay the weapon's. balance.json "outgoingDamageMult", default 1.
        /// </summary>
        public float OutgoingDamageMult { get; internal set; } = 1f;

        /// <summary>Prompt 29 S04: seconds from calling the card to the vehicle landing (balance.json "dropDelay"; default 3.5).</summary>
        public float DropDelay { get; internal set; } = Economy.EconomySystem.DeliverySeconds;

        /// <summary>Prompt 29 S04 (R7): the card's base price, before any card-rank discount; bounties, supply, drop times and
        /// every balance class use it. What a call costs a side now is <see cref="Economy.TeamEconomy.RuntimeCallCost"/>.</summary>
        public int BaseCp => CpCost;

        /// <summary>Prompt 29 S06 (D6): flares as charges ("flareCharges", 0: the old cooldown flares or none).</summary>
        public int FlareCharges { get; internal set; }

        /// <summary>Seconds to get one flare charge back in the holding pattern ("flareRecharge"; null: the flare skill's cooldown).</summary>
        public float? FlareRecharge { get; internal set; }

        /// <summary>Prompt 29 S07 (D7): whether the vehicle has an APS of its own, may take a retrofit (Trophy), or neither.</summary>
        public ApsCapability ApsCapability { get; internal set; }

        /// <summary>Prompt 29 S07: how its interception works (a vehicle's own APS, a point defence, a boss's own).</summary>
        public InterceptionMode InterceptionMode => InterceptionModeData ??
            (Boss ? InterceptionMode.BossSelfAps : Static || Aps is { Burst: > 0f } ? InterceptionMode.PointDefense : InterceptionMode.SelfAps);

        /// <summary>The data's "interceptionMode", if it names one.</summary>
        internal InterceptionMode? InterceptionModeData { get; set; }

        /// <summary>Prompt 29 5.4: this vehicle's own copy of a shared missile weapon (its load and reload), by weapon id.</summary>
        internal Dictionary<string, WeaponDef>? WeaponOverrides { get; set; }

        /// <summary>The weapon a mount fires on this vehicle: its own copy where 5.4 gave one, else the shared one.</summary>
        public WeaponDef ArmOf(WeaponDef shared) => WeaponOverrides != null && WeaponOverrides.TryGetValue(shared.Id, out var own) ? own : shared;

        /// <summary>Share of a mine's blast that gets through (the armoured bulldozer's belly plate: 0.5).</summary>
        public float MineArmor { get; internal set; } = 1f;

        /// <summary>
        /// A breacher (the armoured bulldozer): it rams and ploughs structures down (its main weapon is
        /// the blade), flattens dragon's teeth it is sent at, and the commander sends it ahead of the
        /// line into an enemy base.
        /// </summary>
        public bool Breacher { get; internal set; }

        /// <summary>Shoot-and-scoot (the SP howitzer), or null.</summary>
        public ScootDef? Scoot { get; internal set; }

        /// <summary>
        /// Its main weapon's spread against a target its side has marked (a laser designator's mark, a
        /// counter-battery radar's reveal, a UAV scan over it) is multiplied by this (1: no change).
        /// </summary>
        public float MarkedSpread { get; internal set; } = 1f;

        /// <summary>A multi-part boss's parts (empty: none).</summary>
        public IReadOnlyList<BossPartDef> Parts { get; internal set; } = Array.Empty<BossPartDef>();

        /// <summary>The body is shut to damage until enough of one kind of part has broken, or null.</summary>
        public PartLockDef? PartLock { get; internal set; }

        /// <summary>A boring boss, or null.</summary>
        public BurrowDef? Burrow { get; internal set; }

        /// <summary>A landing-craft boss, or null.</summary>
        public LandingDef? Landing { get; internal set; }

        /// <summary>Prompt 18: its big attack (balance.json "bigAttacks", by the id in "bigAttack"), or null.</summary>
        public BigAttackDef? BigAttack { get; internal set; }

        /// <summary>The "bigAttack" id as written (resolved once every attack is read).</summary>
        internal string? BigAttackId { get; set; }

        /// <summary>Its own scaling of its big attack on top of the difficulty's (a mini boss: less damage, a longer cooldown; data "bigAttackScale").</summary>
        public BigAttackScale BigAttackScale { get; internal set; } = BigAttackScale.One;

        /// <summary>A super-heavy gun's map-wide shot, or null.</summary>
        public BombardDef? Bombard { get; internal set; }

        /// <summary>Prompt 16 E: the burning fuel it leaves on the ground as it drives (the Inferno), or null.</summary>
        public FireTrailDef? FireTrail { get; internal set; }

        /// <summary>Emplacements it arrives with.</summary>
        public IReadOnlyList<GuardDef> Guards { get; internal set; } = Array.Empty<GuardDef>();

        /// <summary>Extra models drawn fixed to it (view only).</summary>
        public IReadOnlyList<AttachmentDef> Attachments { get; internal set; } = Array.Empty<AttachmentDef>();

        /// <summary>Its general's radio line (a text key) when it arrives, or null.</summary>
        public string? RadioSpawn { get; internal set; }

        /// <summary>The index of a part by id, or -1.</summary>
        public int PartIndex(string id)
        {
            for (var i = 0; i < Parts.Count; i++)
                if (Parts[i].Id == id) return i;
            return -1;
        }
    }
}
