#nullable enable
using System;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P5 Part L: one mount's magazine picture. Two kinds exist in the game: a magazine reloaded in place (Ammo / Reload:
    /// the crew restocks standing still, moving pauses it unless gear or an ammunition carrier lets it run on the move) and a
    /// clip (Clip / ClipReload: the pause to change it runs whatever the hull does).
    /// </summary>
    public readonly struct MagazineReading
    {
        public MagazineReading(bool limited, float fraction, bool reloading, float reloadLeft, float reloadSeconds, bool reloadsOnMove)
        {
            Limited = limited;
            Fraction = fraction;
            Reloading = reloading;
            ReloadLeft = reloadLeft;
            ReloadSeconds = reloadSeconds;
            ReloadsOnMove = reloadsOnMove;
        }

        /// <summary>The weapon has a magazine or clip at all (false: endless fire, Part L does not apply).</summary>
        public bool Limited { get; }

        /// <summary>Rounds left over a full load, 0-1 (1 for an unlimited weapon).</summary>
        public float Fraction { get; }

        public bool Reloading { get; }

        /// <summary>Seconds of the reload still to go (0 when not reloading).</summary>
        public float ReloadLeft { get; }

        /// <summary>A whole reload's length (what makes it meaningful).</summary>
        public float ReloadSeconds { get; }

        /// <summary>The reload keeps running while the hull moves (a clip, Hot Swap, an ammunition carrier nearby).</summary>
        public bool ReloadsOnMove { get; }

        public static readonly MagazineReading Unlimited = new(false, 1f, false, 0f, 0f, true);
    }

    /// <summary>
    /// AI MASTER P5 Part L: ammo / reload-aware tactics. Pure rules (the tests call them); <see cref="Read"/> takes the picture
    /// off a vehicle. No rule changes a weapon value: they only decide when the AI moves, keeps a target or scoots.
    /// </summary>
    public static class AmmoTactics
    {
        /// <summary>The picture of mount <paramref name="index"/> (the main weapon by default) of <paramref name="v"/>.</summary>
        public static MagazineReading Read(SimWorld world, Vehicle v, int index = -1)
        {
            if (index < 0) index = Combat.CombatSystem.MainMount(v);
            if (index >= v.Arms.Length || index >= v.Weapons.Length) return MagazineReading.Unlimited;
            var weapon = v.Arms[index];
            var state = v.Weapons[index];
            if (weapon.Ammo > 0 && state.Ammo >= 0)
            {
                var onMove = false;
                if (state.Ammo == 0) world.Gear.ReloadRate(v, out onMove);
                return new MagazineReading(true, state.Ammo / (float)weapon.Ammo, state.Ammo == 0, state.ReloadLeft > 0f ? state.ReloadLeft : state.Ammo == 0 ? weapon.MagazineReload : 0f,
                    weapon.MagazineReload, onMove || v.Def.Static || v.Flying);
            }
            if (weapon.Clip > 0)
            {
                var left = state.ClipLeft < 0 ? weapon.Clip : state.ClipLeft;
                var reloading = left <= 0 && state.Cooldown > 0f;
                return new MagazineReading(true, left / (float)weapon.Clip, reloading, reloading ? state.Cooldown : 0f, weapon.ClipReload, true);
            }
            return MagazineReading.Unlimited;
        }

        /// <summary>The reload is long enough to plan around (Part L "meaningful magazine / reload cycles").</summary>
        public static bool Meaningful(in MagazineReading m) => m.Limited && m.ReloadSeconds >= Tun.Ammo.MeaningfulReloadS;

        /// <summary>Empty or near empty (under <c>nearEmptyShare</c>) or reloading.</summary>
        public static bool Dry(in MagazineReading m) => m.Reloading || m.Fraction < Tun.Ammo.NearEmptyShare;

        /// <summary>
        /// L1: may this unit begin (or keep driving) an exposed advance? Not with an empty / near-empty meaningful magazine,
        /// unless the objective is an emergency (urgency at or over <c>emergencyUrgency</c>) or the squad is dodging / overwhelmed.
        /// </summary>
        public static bool MayCharge(in MagazineReading m, float urgency, bool emergency) =>
            !Tun.Ammo.Enabled || !Meaningful(m) || !Dry(m) || emergency || urgency >= Tun.Ammo.EmergencyUrgency;

        /// <summary>
        /// L1 / L4 together, for a squad member on the move: hold (stop where it is) rather than drive on while its meaningful
        /// magazine reloads. An in-place magazine only reloads with the hull still, so holding is what gets it firing again
        /// soonest; a support weapon (artillery, AA, support role) holds while it cannot fire even when its reload runs on the move
        /// (it must not expose itself). A clip reload of a line unit runs on the move: no hold (L2, the move is free). A near-empty
        /// in-place magazine that is not yet reloading is not held: it reloads only once empty, so holding it would idle it.
        /// </summary>
        public static bool HoldBack(in MagazineReading m, bool advancing, bool supportRole, float urgency, bool emergency) =>
            Tun.Ammo.Enabled && advancing && Meaningful(m) && m.Reloading && !emergency && urgency < Tun.Ammo.EmergencyUrgency &&
            (!m.ReloadsOnMove || supportRole);

        /// <summary>A held unit rejoins the squad's move: reloaded, or an emergency (a reload always ends standing still: no deadlock).</summary>
        public static bool Resume(in MagazineReading m, float urgency, bool emergency) =>
            !Tun.Ammo.Enabled || !m.Reloading || emergency || urgency >= Tun.Ammo.EmergencyUrgency;

        /// <summary>
        /// L2: a reload long enough for a short reposition (clip reloads and reloads that run on the move only: moving would pause
        /// an in-place magazine reload, so for those the window is not free).
        /// </summary>
        public static bool RepositionWindow(in MagazineReading m) =>
            Tun.Ammo.Enabled && m.Limited && m.Reloading && m.ReloadsOnMove && m.ReloadLeft >= Tun.Ammo.RepositionMinReloadS;

        /// <summary>
        /// L3: artillery may scoot during its reload: a salvo fired, the reload has at least <c>scootMinReloadS</c> left and runs on
        /// the move (so the scoot costs no firing time). The counter-battery and salvo-count triggers of P3 stay as they are.
        /// </summary>
        public static bool ScootDuringReload(in MagazineReading m, int salvosFired) =>
            Tun.Ammo.Enabled && salvosFired > 0 && m.Limited && m.Reloading && m.ReloadsOnMove && m.ReloadLeft >= Tun.Ammo.ScootMinReloadS;

        /// <summary>
        /// L5: do not churn targets during a reload: a mount reloading a meaningful magazine keeps its still-valid target until it
        /// can fire again (the reload itself never restarts on a target change in this game; this keeps the turret laid).
        /// </summary>
        public static bool KeepTarget(in MagazineReading m, bool heldStillValid) =>
            Tun.Ammo.Enabled && Tun.Ammo.KeepTargetWhileReloading && heldStillValid && m.Reloading && Meaningful(m);
    }
}
