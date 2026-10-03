using System.Collections.Generic;
using System.Text.RegularExpressions;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 13 (lead, model work): rounds carried in view on a launcher (the ballistic launcher's missiles on its erector,
    /// a cruise-missile vehicle's box cells, any launcher whose rounds are modelled) leave it when they are fired and come back
    /// with the reload. Real life: a TEL's erector is empty after the launch and stays empty until a transloader puts the next
    /// missile on; a launcher's cells show what is still loaded. Each modelled round is a node group named with an index
    /// (<c>missile_1</c>, <c>missile_2_fins</c>, <c>round_3</c>, <c>rocket_04</c>, <c>cruise_missile_1</c>, any case; every node
    /// with the same index is one round); merged parts without an index (<c>Missiles</c>, <c>Missile_bands</c>) are never
    /// touched. The rounds shown follow the sim's magazine (<see cref="MachineBrigade.Sim.Entities.Vehicle.Ammo"/>) of the
    /// first missile or rocket mount with a magazine, scaled when the magazine holds more rounds than the model shows; the
    /// lowest index leaves first. View only; the far detail level and the cards keep the full load (too small to see).
    /// </summary>
    public sealed partial class VehicleView
    {
        private static Regex RoundNode => ModelLibrary.RoundPattern;

        /// <summary>The modelled rounds, lowest index first; each is the nodes of one round.</summary>
        private List<List<Transform>> _loadedRounds;

        /// <summary>The mount whose magazine they show (-1: none), and how many are shown now (-1: not yet set).</summary>
        private int _loadedMount = -2;
        private int _loadedShown = -1;

        /// <summary>From <see cref="Render"/>: shows as many modelled rounds as the magazine holds.</summary>
        private void ShowLoadedRounds()
        {
            if (_loadedMount == -2) FindLoadedRounds();
            if (_loadedMount < 0) return;
            var magazine = Sim.Arm(_loadedMount).Ammo;
            var groups = _loadedRounds.Count;
            var left = Mathf.Clamp(Sim.Ammo(_loadedMount), 0, magazine);
            var shown = magazine <= groups ? Mathf.Min(left, groups) : Mathf.CeilToInt(left * (float)groups / magazine);
            if (shown == _loadedShown) return;
            _loadedShown = shown;
            // The first rounds fired are the lowest indices: the last `shown` groups stay.
            for (var g = 0; g < groups; g++)
            {
                var visible = g >= groups - shown;
                foreach (var node in _loadedRounds[g])
                    if (node != null && node.gameObject.activeSelf != visible) node.gameObject.SetActive(visible);
            }
        }

        private void FindLoadedRounds()
        {
            _loadedMount = -1;
            if (_model == null || _model.Root == null) return;
            var mounts = Def.Mounts;
            for (var i = 0; i < mounts.Count; i++)
            {
                var w = Sim.Arm(i);
                if (w.Ammo > 0 && w.Projectile is ProjectileKind.Missile or ProjectileKind.Rocket)
                {
                    _loadedMount = i;
                    break;
                }
            }
            if (_loadedMount < 0) return;
            var byIndex = new SortedDictionary<int, List<Transform>>();
            foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
            {
                if (t == _model.Root.transform || t.name == ModelLibrary.LodName) continue;
                var m = RoundNode.Match(t.name);
                if (!m.Success || !int.TryParse(m.Groups[2].Value, out var index)) continue;
                // A node inside another round node of the same round goes with it.
                if (!byIndex.TryGetValue(index, out var nodes)) byIndex[index] = nodes = new List<Transform>();
                var nested = false;
                foreach (var n in nodes)
                    if (t.IsChildOf(n)) nested = true;
                if (!nested) nodes.Add(t);
            }
            if (byIndex.Count == 0)
            {
                _loadedMount = -1;
                return;
            }
            _loadedRounds = new List<List<Transform>>(byIndex.Values);
        }
    }
}
