using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 13 ("các model tháp súng đáng lẽ phải có thể quay để bắn"): gun turrets that visibly train onto what they
    /// shoot. Real life: a turret is trained onto its target first and then fires; a ship's or a railway gun's turret traverses
    /// at a few degrees to a few tens of degrees a second, it never jumps. Most turrets are already trained by the sim at their
    /// turret rate (vehicles, towers: their `Turret` node follows <c>TurretHeading</c>). Two kinds were not:
    /// <list type="bullet">
    /// <item>guns the boss systems lay (<see cref="WeaponDef.Laid"/>: the Leviathan's main turrets, the rail supergun): the sim
    /// sets their heading in the same step as the shot, so they jumped onto the aim as they fired and stood still between
    /// salvos; and</item>
    /// <item>a free main mount (mount 0 with Free aim: the command airship's, the hovercraft's guns), whose heading the sim
    /// does not train at all.</item>
    /// </list>
    /// For those the drawn mount now traverses at the unit's turret rate (at least <see cref="LaidTraverseMin"/>) and, while no
    /// salvo has just been laid, follows the unit's current target inside its own firing arc, as fire control keeps a turret on
    /// its target between salvos. View only: the sim's headings, shots and hits are untouched.
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>Slowest drawn traverse of a laid gun (degrees a second).</summary>
        private const float LaidTraverseMin = 20f;

        /// <summary>A free main mount's traverse (degrees a second; the sim's free mounts turn about this fast).</summary>
        private const float FreeTraverse = 120f;

        /// <summary>A jump of the sim's heading in one step larger than this (degrees) is a gun being laid, not trained.</summary>
        private const float LayJump = 2.5f;

        /// <summary>How long a laid gun holds its laid heading before it goes back to following the target (seconds).</summary>
        private const float LaidHold = 3f;

        /// <summary>The registry this view belongs to (to find its target's view); set by <see cref="ViewRegistry.Add"/>.</summary>
        internal ViewRegistry Registry { get; set; }

        private float[] _drawnMount;
        private float[] _laidAt;
        private float _drawnTurret = float.NaN;
        private float _turretLaidAt = -10f;

        /// <summary>
        /// Whether the sim lays this mount (or does not train it at all), so the view trains it. Play-test 14: a flagship's
        /// salvo turrets are trained by the sim now (NavalSystem.Lay), so they are drawn as it has them.
        /// </summary>
        private bool ViewTrained(int i) =>
            i < Def.Mounts.Count && Def.Mounts[i].Aim == MountAim.Free && Sim.Arm(i).Laid && Def.Salvo == null;

        /// <summary>From <see cref="Snapshot"/>: notes the steps in which the sim laid a gun (its heading jumped).</summary>
        private void NoteLays()
        {
            if (_drawnMount == null || _drawnMount.Length != _currentMount.Length)
            {
                _drawnMount = new float[_currentMount.Length];
                _laidAt = new float[_currentMount.Length];
                for (var i = 0; i < _drawnMount.Length; i++)
                {
                    _drawnMount[i] = float.NaN;
                    _laidAt[i] = -10f;
                }
            }
            for (var i = 0; i < _currentMount.Length; i++)
                if (Mathf.Abs(Mathf.DeltaAngle(_previousMount[i], _currentMount[i])) > LayJump) _laidAt[i] = Time.time;
            if (Mathf.Abs(Mathf.DeltaAngle(_previousTurret, _currentTurret)) > LayJump) _turretLaidAt = Time.time;
        }

        /// <summary>The heading (degrees, world) to draw free mount <paramref name="i"/> at, given the sim's.</summary>
        private float DrawnMountHeading(int i, float simHeading, float hull)
        {
            if (_drawnMount == null || i >= _drawnMount.Length || !ViewTrained(i)) return simHeading;
            var want = simHeading;
            // Between salvos (or always, for a free main mount the sim does not train): on the target, inside the mount's arc.
            if ((i == 0 && !Sim.Arm(i).Laid) || Time.time - _laidAt[i] > LaidHold)
                if (TargetBearing(out var bearing)) want = InArc(i, bearing, hull);
            var rate = i == 0 && !Sim.Arm(i).Laid ? FreeTraverse : Mathf.Max(LaidTraverseMin, Def.TurretTurnRate * Mathf.Rad2Deg);
            if (float.IsNaN(_drawnMount[i])) _drawnMount[i] = want;
            _drawnMount[i] = Mathf.MoveTowardsAngle(_drawnMount[i], want, rate * FrameStep);
            return _drawnMount[i];
        }

        /// <summary>
        /// The heading (degrees, world) to draw the main turret at: as the sim trains it, except a main gun the boss system lays
        /// (the rail supergun), which traverses onto its laid heading instead of jumping (it stays laid there, as designed).
        /// </summary>
        private float DrawnTurretHeading(float simTurret)
        {
            if (Def.Mounts.Count == 0 || !Sim.Arm(0).Laid || Def.Mounts[0].Aim != MountAim.Turret) return simTurret;
            if (float.IsNaN(_drawnTurret)) _drawnTurret = simTurret;
            var rate = Mathf.Max(LaidTraverseMin * 0.5f, Def.TurretTurnRate * Mathf.Rad2Deg);
            _drawnTurret = Mathf.MoveTowardsAngle(_drawnTurret, simTurret, rate * FrameStep);
            return _drawnTurret;
        }

        /// <summary>The bearing (degrees, world) from this vehicle to its current target's view.</summary>
        private bool TargetBearing(out float bearing)
        {
            bearing = 0f;
            var target = Sim.Target;
            if (!target.IsValid || Registry == null || !Registry.TryGet(target, out var view) || view == this || view.Root == null) return false;
            var to = view.Root.position - Root.position;
            if (to.x * to.x + to.z * to.z < 1f) return false;
            bearing = Mathf.Atan2(to.x, to.z) * Mathf.Rad2Deg;
            return true;
        }

        /// <summary>When each mount last fired (view time; for <see cref="DrivesPivot"/>).</summary>
        private float[] _mountShotAt;

        /// <summary>Notes a shot of mount <paramref name="mount"/> (from <see cref="MountRecoil"/>).</summary>
        private void NoteMountShot(int mount)
        {
            if (_mounts == null || mount < 0 || mount >= _mounts.Length) return;
            if (_mountShotAt == null || _mountShotAt.Length != _mounts.Length)
            {
                _mountShotAt = new float[_mounts.Length];
                for (var i = 0; i < _mountShotAt.Length; i++) _mountShotAt[i] = -10f;
            }
            _mountShotAt[mount] = Time.time;
        }

        /// <summary>
        /// Play-test 14 (lane G, the Typhon's deck gun "never turned yet fired backwards"): when a model has fewer gun pivots
        /// than the data has free mounts of that slot, several mounts share one pivot and each wrote its own heading to it in
        /// turn, the last (a gun not yet woken, never trained) winning. Now one of them turns it: the working mount that fired
        /// last (a shot leaves along its barrel), else the first working one. A pivot of its own is always its mount's.
        /// </summary>
        private bool DrivesPivot(int i)
        {
            var pivot = _mounts[i];
            var owner = -1;
            var best = float.NegativeInfinity;
            var shared = false;
            for (var j = 0; j < _mounts.Length; j++)
            {
                if (_mounts[j] != pivot || Def.Mounts[j].Aim != MountAim.Free) continue;
                if (j != i) shared = true;
                if (!Sim.MountWorks(j)) continue;
                var at = _mountShotAt != null && j < _mountShotAt.Length ? _mountShotAt[j] : -10f;
                if (owner < 0 || at > best)
                {
                    owner = j;
                    best = at;
                }
            }
            return !shared || owner < 0 || owner == i;
        }

        /// <summary>A bearing kept inside mount <paramref name="i"/>'s own firing arc (an aft turret never swings across the bridge).</summary>
        private float InArc(int i, float bearing, float hull)
        {
            var mount = Def.Mounts[i];
            if (mount.ArcHalf <= 0f) return bearing;
            var centre = hull + mount.ArcCentre * Mathf.Rad2Deg;
            var half = mount.ArcHalf * Mathf.Rad2Deg;
            return centre + Mathf.Clamp(Mathf.DeltaAngle(centre, bearing), -half, half);
        }
    }
}
