using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L3: warnings by escape time. A boss's T4+ round (<see cref="WeaponDef.WarnSeconds"/>) shows its edge and its
    /// core on its fall point for its whole warning (the Sim keeps it in the air at least that long); a T5 salvo's shells
    /// (Leviathan's 406 mm, marked by their own strike warning) get the core ring inside the warning's edge ring. View only.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private readonly EscapeWarnings _escape;

        /// <summary>Fix prompt L5: which warning rings are drawn (<see cref="WarningGate"/>).</summary>
        private readonly WarningGate _gate = new();

        /// <summary>Fix prompt L5: the Settings choice for warning rings (MatchSettings.WarningRings): 0 Full, 1 Important only, 2 Off.</summary>
        public int WarningLevel
        {
            get => _gate.Level;
            set => _gate.Level = Mathf.Clamp(value, 0, 2);
        }

        /// <summary>The player's side (no rings for its own rounds; its units are what a ring threatens).</summary>
        private int PlayerTeam => _gate.PlayerTeam;

        private void InitWarningGate()
        {
            var rules = _catalog.Warnings;
            _gate.MaxShown = rules.MaxShown;
            _escape.Gate = _gate;
            _escape.FadeIn = rules.FadeIn;
            _escape.SalvoMerge = rules.SalvoMerge;
            _strikes.Gate = _gate;
            _strikes.WarnFadeIn = rules.FadeIn;
            _bigZones.Gate = _gate;
        }

        /// <summary>
        /// Play-test 14 (lane A), owner: "các vùng nổ của bom, đạn pháo không cần hiện vùng va chạm". A bomb's or an artillery
        /// shell's (howitzer, mortar, any lofted or indirect shell) blast shows no zone on the ground: no warning ring or stick
        /// rectangle before it lands (battle or preview) and no ring marking its damage radius when it bursts; its blast itself
        /// (fireball, smoke, the recipe's own shockwave, crater) is drawn whole. Flak, guided rounds and the T5 super weapons
        /// (the 406 mm, the 800 mm, a nuclear bomb) keep their warnings; fire supports keep their strike zones.
        /// </summary>
        internal static bool Zoneless(WeaponDef round)
        {
            if (round == null || round.Flak || round.Tier >= 5) return false;
            if (round.Projectile == ProjectileKind.Bomb) return true;
            return round.Projectile == ProjectileKind.Shell &&
                (round.Indirect || round.Family == "howitzer" || round.Family == "mortar");
        }

        /// <summary>Tests: rings the gate shows now.</summary>
        internal int WarningsShown => _gate.ShownCount;

        /// <summary>The round a fired event carried: its second round, else the mount's own weapon as the boss carries it (its edge).</summary>
        private WeaponDef FiredRound(SimEvent e, VehicleView shooter, WeaponDef fallback)
        {
            if (e.Round != null && _catalog.Weapons.TryGetValue(e.Round, out var round)) return round;
            var mounts = shooter.Sim.Def.Mounts;
            return e.Mount >= 0 && e.Mount < mounts.Count ? mounts[e.Mount].Weapon : fallback;
        }

        /// <summary>
        /// A boss's round fired: true when it is a T4+ round that warns by escape time (its rings are drawn), false to let the
        /// older 0.8 s ring (prompt 26 B.4) decide.
        /// </summary>
        private bool EscapeRing(SimEvent e, VehicleView shooter, WeaponDef weapon, float now)
        {
            var round = FiredRound(e, shooter, weapon);
            if (Zoneless(round)) return false;
            var warn = round.WarnSeconds;
            // Fix prompt L5: only the rounds the rules warn of (never a guided one, nor a beam).
            if (warn <= 0f || !_catalog.Warnings.Warns(round)) return false;
            var flight = Mathf.Max(0.05f, e.Value);
            var start = now + Mathf.Max(0f, flight - warn);
            // One shooter's mount: its salvo's rings merge into one; a T5 round is a super weapon's.
            var owner = ((long)e.Entity.Value << 8) | (uint)(e.Mount & 0xff);
            _escape.Add(Ground(e.Target, 0.13f), round.SplashRadius, round.WarnRadius, start, now + flight, now, owner, round.Tier >= 5);
            return true;
        }

        /// <summary>
        /// Prompt 34 L8: set by a preview ("In action"): every unguided blast round its unit fires shows the escape warning's
        /// pair of rings on its fall point, the edge (<see cref="WeaponDef.WarnRadius"/>) and the core, for the round's
        /// warning when it has one (T4+), else for its last <see cref="PreviewRingSeconds"/> in the air. The rings are exactly the
        /// blast's damage area. A boss's rounds that already warn (L3, prompt 26 B.4) are left to those. Off in a battle.
        /// </summary>
        public bool PreviewRings { get; set; }

        /// <summary>Prompt 34 L9: the wrecks on the field and their torn-off pieces (the stress scene's counts).</summary>
        internal int WreckCount => _wrecks.Count;

        internal int WreckPieces => _wrecks.Pieces;

        /// <summary>How long a preview's ring shows for a round with no warning of its own.</summary>
        public const float PreviewRingSeconds = 0.8f;

        /// <summary>Whether a preview draws its ring for this round, shot by <paramref name="boss"/> or not (see <see cref="PreviewRings"/>).</summary>
        public static bool PreviewRingFor(WeaponDef round, bool boss)
        {
            if (round == null || round.Guided || round.Laid || round.SplashRadius <= 0f) return false;
            if (Zoneless(round)) return false;
            return !boss || (round.WarnSeconds <= 0f && round.SplashRadius < BossShellWarnFrom);
        }

        private void PreviewRing(SimEvent e, VehicleView shooter, WeaponDef weapon, float now)
        {
            var round = FiredRound(e, shooter, weapon);
            if (!PreviewRingFor(round, shooter.Sim.Def.Boss)) return;
            var flight = Mathf.Max(0.05f, e.Value);
            var warn = round.WarnSeconds > 0f ? round.WarnSeconds : PreviewRingSeconds;
            // A preview's rings are its tool: always drawn (as a super weapon's, past the gate).
            _escape.Add(Ground(e.Target, 0.13f), round.SplashRadius, round.WarnRadius, now + Mathf.Max(0f, flight - warn), now + flight, now, 0, true);
        }

        /// <summary>Prompt 34 L4: rounds of each shooter's mount already drawn in this batch (a simultaneous volley's barrels).</summary>
        private readonly System.Collections.Generic.Dictionary<(MachineBrigade.Sim.Core.EntityId, int), int> _volley = new();

        /// <summary>
        /// Prompt 34 L4: how late this round of a simultaneous volley is drawn: 0 for the first barrel, then
        /// <see cref="WeaponDef.BarrelGap"/> a barrel (all fired in one tick, drawn one after another on their own muzzles).
        /// </summary>
        private float BarrelStagger(SimEvent e, VehicleView shooter)
        {
            if (e.Kind != SimEventKind.WeaponFired || e.DefId == null || !_catalog.Weapons.TryGetValue(e.DefId, out var gun)) return 0f;
            var round = FiredRound(e, shooter, gun);
            if (!round.Simultaneous || round.Barrels < 2) return 0f;
            var key = (e.Entity, e.Mount);
            var k = _volley.TryGetValue(key, out var seen) ? seen + 1 : 0;
            _volley[key] = k;
            return (k % round.Barrels) * WeaponDef.BarrelGap;
        }

        /// <summary>Prompt 34 L4: a volley's later barrel, drawn <paramref name="late"/> s after the Sim fired it (its shell flies that much less).</summary>
        private void LaterShot(SimEvent e, VehicleView shooter, ViewRegistry views, float at, float late)
        {
            Later(at, () =>
            {
                if (shooter == null || shooter.Root == null) return;
                _weapons.TravelCut = late;
                _weapons.Fired(e, shooter, views, Time.time);
                _weapons.TravelCut = 0f;
            });
        }

        /// <summary>A strike warning of an event barrage with a core inside its ring (the 406 mm salvo's shell): the core's ring too.</summary>
        private void StrikeCore(SimEvent e, float now)
        {
            if (e.DefId == null || !_catalog.TryGetSupport(e.DefId, out var support) || !support.EventOnly || support.IsLine) return;
            if (support.BlastRadius <= 0f || support.BlastRadius >= support.Radius - 0.25f) return;
            // Fix prompt L5: the 406 mm salvo is a super weapon's (always drawn, on top); none for a salvo of ours.
            if (e.Team == PlayerTeam) return;
            _escape.Add(Ground(e.Position, 0.13f), support.BlastRadius, support.Radius, now, now + Mathf.Max(0.2f, e.Value), now, 0, true);
        }
    }
}
