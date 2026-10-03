using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21H): launchers raise their launcher to fire and lower it after, as the real systems do
    /// (HIMARS and MLRS lift the pod, TOS-1A and the Grad lay the tube pack, the Buk its rails, the S-300 stands its
    /// canisters upright, the Iskander erects its missiles, the Patriot raises its box to 38 degrees, a Bradley lifts
    /// its TOW box). View only: driven by the sim's fire state (a target, the main weapon's cooldown, the magazine) and
    /// by enemies coming near (EffectsDirector marks a launcher with an enemy of its layer inside a quarter past its
    /// reach, <see cref="ThreatAt"/>), so it is up before the enemy is in reach: the sim fires a ready launcher the
    /// moment it has a target. It comes up when its next round is close and it has a target or an enemy near, stays
    /// up while rounds follow, and goes down to its travel pose while it reloads (a long cooldown or an empty
    /// magazine) or once no enemy is about. A round fired before it is up lays it at once (<see cref="LayForShot"/>).
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>How a launcher is laid to fire: at its target's range or height, or raised a fixed way (upright, a set angle).</summary>
        internal enum ErectKind { Aimed, Raised }

        /// <summary>
        /// A launcher's poses, in degrees from the pose it is drawn in (the model's own pitch, which may be off level):
        /// raised (for <see cref="ErectKind.Raised"/>) and stowed for travel (0 or below: lowered from the drawn pose),
        /// and the seconds its erector takes.
        /// </summary>
        internal readonly struct Erector
        {
            public readonly ErectKind Kind;
            public readonly float Raise, Stow, Seconds;

            public Erector(ErectKind kind, float raise, float seconds, float stow = 0f)
            {
                Kind = kind;
                Raise = raise;
                Seconds = seconds;
                Stow = stow;
            }
        }

        /// <summary>The launchers by vehicle (and tower): the systems they are drawn after, in <see cref="VehicleView"/>'s notes.</summary>
        internal static readonly Dictionary<string, Erector> Erectors = new()
        {
            ["mlrs"] = new(ErectKind.Aimed, 0f, 1.1f),
            ["elite_mlrs"] = new(ErectKind.Aimed, 0f, 1.1f),
            ["elite_grad"] = new(ErectKind.Aimed, 0f, 1.0f),
            ["heavy_rocket_artillery"] = new(ErectKind.Aimed, 0f, 1.3f),
            ["thermobaric_launcher"] = new(ErectKind.Aimed, 0f, 1.2f),
            ["rocket_technical"] = new(ErectKind.Aimed, 0f, 0.7f),
            ["sam_launcher"] = new(ErectKind.Aimed, 0f, 0.9f),
            // The S-300's canisters are drawn flat and stand upright; play-test 13: the Iskander's boom and both missiles
            // are drawn lying on it and rise together about its rear hinge, and the Typhon-class cruise missile box
            // lies flat for travel and swings up near vertical about its rear hinge to fire.
            ["long_sam"] = new(ErectKind.Raised, 84f, 1.6f),
            ["elite_long_sam"] = new(ErectKind.Raised, 84f, 1.6f),
            ["ballistic_launcher"] = new(ErectKind.Raised, 86f, 2.2f),
            ["ground_cruise_missile_vehicle"] = new(ErectKind.Raised, 80f, 2.2f),
            // The Patriot's box and the Shahed truck's rack are drawn at their firing angles and travel lowered.
            ["missile_battery"] = new(ErectKind.Raised, 0f, 1.2f, -34f),
            ["shahed_truck"] = new(ErectKind.Raised, 0f, 1.0f, -12f),
            ["lancet_truck"] = new(ErectKind.Raised, 34f, 0.8f),
        };

        /// <summary>A side ATGM box's firing angle and the seconds it takes to come up (a Bradley's TOW launcher).</summary>
        internal const float AtgmRaise = 16f, AtgmSeconds = 0.6f;

        /// <summary>After its last reason to be up, a launcher waits this long before it goes down (seconds).</summary>
        internal const float ErectHold = 1.2f;

        private float _erectUntil = -10f, _atgmUntil = -10f, _atgmPitch;
        private Transform _atgmBox;
        private Quaternion _atgmRest;
        private int _atgmMount = -1;

        /// <summary>The next round is this close (seconds) for a launcher to be up: its erector's time and a second.</summary>
        internal static float RaiseLead(Erector erector) => erector.Seconds + 1f;

        /// <summary>When an enemy was last near enough for this launcher to make ready (EffectsDirector.WarnLaunchers).</summary>
        public float ThreatAt { get; set; } = -10f;

        /// <summary>How far past a launcher's reach an enemy makes it ready (a quarter again).</summary>
        internal const float ThreatReach = 1.25f;

        /// <summary>A launcher the director warns: its reach and the layers it fires at (0 when it is no launcher).</summary>
        internal float LauncherReach(out TargetLayers layers)
        {
            layers = TargetLayers.None;
            var reach = 0f;
            if (Erectors.ContainsKey(Def.Id))
            {
                layers |= Def.Weapon.Targets;
                reach = Def.Weapon.Range;
            }
            if (_atgmBox != null)
            {
                layers |= Def.Mounts[_atgmMount].Weapon.Targets;
                reach = Mathf.Max(reach, Def.Mounts[_atgmMount].Weapon.Range);
            }
            return reach * ThreatReach;
        }

        private bool ThreatNear => Time.time - ThreatAt < 0.6f;

        /// <summary>Whether this launcher is up (or on its way up) now: see the notes above.</summary>
        private bool ErectWanted(Erector erector)
        {
            if (Sim.IsAlive && !Sim.OutOfAmmo && Sim.Cooldown <= RaiseLead(erector) && (Sim.Aiming || ThreatNear))
                _erectUntil = Time.time + ErectHold;
            return Time.time < _erectUntil;
        }

        /// <summary>
        /// A launcher's angle (degrees above level) for its fire state: <paramref name="aimed"/> (the usual laying at a
        /// target) or its raised pose when up, its travel pose when down. Returns the laying speed.
        /// </summary>
        private float ErectAngle(Erector erector, float aimed, bool snap, out float rate)
        {
            var drawn = _model.RestPitch;
            var up = erector.Kind == ErectKind.Raised ? drawn + erector.Raise : aimed;
            var stowed = drawn + erector.Stow;
            rate = Mathf.Max(20f, Mathf.Abs((erector.Kind == ErectKind.Aimed ? drawn + 40f : up) - stowed) / erector.Seconds);
            // A round fired before it was up (the sim fires a ready launcher at once): it is laid now and held up a while.
            if (snap) _erectUntil = Time.time + ErectHold;
            return snap || ErectWanted(erector) ? up : stowed;
        }

        /// <summary>Finds the side ATGM box (ModelLibrary.SideLaunchers) and the mount that fires from it.</summary>
        private void FindSideLauncher()
        {
            if (_model.Turret == null) return;
            _atgmBox = _model.Turret.Find(ModelLibrary.SideErectorName);
            if (_atgmBox == null) return;
            _atgmRest = _atgmBox.localRotation;
            for (var i = 0; i < Def.Mounts.Count; i++)
                if (Def.Mounts[i].Slot == "missile") _atgmMount = i;
            if (_atgmMount < 0) _atgmBox = null;
        }

        /// <summary>The side ATGM box comes up when its missile has a target and is nearly ready, and folds down after.</summary>
        private void RaiseSideLauncher(bool snap = false)
        {
            if (_atgmBox == null) return;
            if (snap || Sim.IsAlive && (Sim.MountTarget(_atgmMount).IsValid || ThreatNear) && Sim.MountCooldown(_atgmMount) <= AtgmSeconds + 1f)
                _atgmUntil = Time.time + ErectHold;
            var want = snap || Time.time < _atgmUntil ? AtgmRaise : 0f;
            _atgmPitch = snap ? want : Mathf.MoveTowards(_atgmPitch, want, AtgmRaise / AtgmSeconds * Time.deltaTime);
            _atgmBox.localRotation = _atgmRest * Quaternion.Euler(-_atgmPitch, 0f, 0f);
        }

        /// <summary>A missile leaves the side box: it is laid at once, as a main barrel is (<see cref="LayForShot"/>).</summary>
        internal void LaySideLauncher(int mount)
        {
            if (mount == _atgmMount) RaiseSideLauncher(snap: true);
        }
    }
}
