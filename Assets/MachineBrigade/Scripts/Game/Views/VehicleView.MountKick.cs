using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 14 ("giật nòng khi bắn"): a gun on its own free mount (the Leviathan's 406 mm and 155 mm turrets) kicks its
    /// barrels back as it fires and runs them out again, as a turret's main gun already does (<see cref="Recoil"/>). The
    /// barrels are the mount pivot's `*_barrels` / `*_muzzles` parts (<see cref="ModelLibrary.IsMountBarrel"/>); a mount
    /// without them does nothing. View only.
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>How long a mount's barrels take to come back after a shot (seconds; a heavy naval gun runs out slowly).</summary>
        private const float MountRecoilSeconds = 0.6f;

        private Transform[][] _mountBarrels;
        private Vector3[][] _mountBarrelRest;
        private Vector3[] _mountKickDirection;
        private float[] _mountKickAt;

        /// <summary>Starts the barrel kick of mount <paramref name="mount"/>; called when the simulation reports its shot.</summary>
        public void MountRecoil(int mount)
        {
            NoteMountShot(mount);
            if (_mounts == null || mount < 0 || mount >= _mounts.Length || _mounts[mount] == null) return;
            FindMountBarrels();
            if (_mountBarrels[mount] != null) _mountKickAt[mount] = Time.time;
        }

        private void FindMountBarrels()
        {
            if (_mountBarrels != null) return;
            var count = _mounts.Length;
            _mountBarrels = new Transform[count][];
            _mountBarrelRest = new Vector3[count][];
            _mountKickDirection = new Vector3[count];
            _mountKickAt = new float[count];
            for (var i = 0; i < count; i++)
            {
                _mountKickAt[i] = -10f;
                var mount = _mounts[i];
                if (mount == null) continue;
                var barrels = new List<Transform>();
                for (var c = 0; c < mount.childCount; c++)
                    if (ModelLibrary.IsMountBarrel(mount.GetChild(c))) barrels.Add(mount.GetChild(c));
                if (barrels.Count == 0) continue;
                // Back along the gun: from its muzzle towards the pivot, level, in the pivot's own frame.
                var forward = _muzzles[i] != null ? mount.InverseTransformPoint(_muzzles[i].position) : Vector3.forward;
                forward.y = 0f;
                if (forward.sqrMagnitude < 1e-6f) forward = Vector3.forward;
                _mountKickDirection[i] = -forward.normalized;
                _mountBarrels[i] = barrels.ToArray();
                _mountBarrelRest[i] = new Vector3[barrels.Count];
                for (var k = 0; k < barrels.Count; k++) _mountBarrelRest[i][k] = barrels[k].localPosition;
            }
        }

        /// <summary>Each frame: the mounts' barrels back by the kick, easing out to rest.</summary>
        private void KickMountBarrels()
        {
            if (_mountBarrels == null) return;
            for (var i = 0; i < _mountBarrels.Length; i++)
            {
                var barrels = _mountBarrels[i];
                if (barrels == null) continue;
                var t = (Time.time - _mountKickAt[i]) / MountRecoilSeconds;
                var kick = t >= 0f && t < 1f ? (1f - t) * (1f - t) * _recoilDistance : 0f;
                for (var k = 0; k < barrels.Length; k++)
                    if (barrels[k] != null) barrels[k].localPosition = _mountBarrelRest[i][k] + _mountKickDirection[i] * kick;
            }
        }
    }
}
