using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// A boss's parts on its view (prompt 8): each part is its model node (a Part_ empty, a rigid group
    /// of its own, see ModelLibrary.PartPattern); when the sim breaks it the node is hidden and its
    /// charred wreck piece (wreck_engine, wreck_launcher ...) is put in at the node's origin. Also the
    /// models a boss carries along (the supergun's coupled tractors) and a boring boss sinking into the
    /// ground and breaking out again. Prompt 9 adds the fires and smoke at the breaks.
    /// </summary>
    public sealed partial class VehicleView
    {
        private ModelLibrary _partModels;
        private bool[] _partShownBroken;
        private float _burrowDepth;

        /// <summary>How far under the ground a boring boss goes (below any hull).</summary>
        private const float BurrowDepth = 9f;

        private void InitBossParts(ModelLibrary models)
        {
            _partModels = models;
            var parts = Def.Parts;
            if (parts.Count > 0)
            {
                var byName = new Dictionary<string, Transform>();
                foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
                    if (!byName.ContainsKey(t.name)) byName[t.name] = t;
                for (var i = 0; i < parts.Count; i++)
                    if (parts[i].Node != null && byName.TryGetValue(parts[i].Node, out var node)) _partNodes.Add((i, node));
                _partShownBroken = new bool[parts.Count];
            }
            // Models drawn fixed to it, placed in its model's frame (the Blender builder's: X left, Y back, Z up).
            foreach (var a in Def.Attachments)
            {
                if (!models.Has(a.Model)) continue;
                var extra = models.Spawn(a.Model, Sim.Team, _model.Root.transform);
                extra.Root.transform.localPosition = new Vector3(-a.At.X, a.At.Z, -a.At.Y);
                extra.Root.transform.localRotation = Quaternion.Euler(0f, a.Heading, 0f);
            }
        }

        private void AnimateBossParts()
        {
            if (_partShownBroken != null)
                foreach (var (i, node) in _partNodes)
                {
                    if (_partShownBroken[i] || !Sim.IsPartBroken(i)) continue;
                    _partShownBroken[i] = true;
                    ShowBroken(i, node);
                }
            if (Def.Burrow != null)
            {
                // Down while it dives and bores, the nose showing through the cracks, then out in a lunge.
                var want = Sim.Burrowed ? (Sim.Cracking != null ? BurrowDepth * 0.55f : BurrowDepth)
                    : Sim.BurrowStage == MachineBrigade.Sim.Entities.Vehicle.BurrowState.Diving ? BurrowDepth : 0f;
                var rate = want > _burrowDepth ? BurrowDepth / 2f : BurrowDepth * 3f;
                _burrowDepth = Mathf.MoveTowards(_burrowDepth, want, rate * Time.deltaTime);
                if (_burrowDepth > 0.01f) _body.localPosition += Vector3.down * _burrowDepth;
            }
        }

        /// <summary>A part broke: hidden, and its wreck piece put in where it stood.</summary>
        private void ShowBroken(int i, Transform node)
        {
            var wreck = Def.Parts[i].Wreck;
            if (wreck != null && _partModels != null && _partModels.Has(wreck) && node.parent != null)
            {
                var piece = _partModels.Spawn(wreck, Sim.Team, node.parent, castShadows: true);
                piece.Root.transform.localPosition = node.localPosition;
                piece.Root.transform.localRotation = node.localRotation;
            }
            node.gameObject.SetActive(false);
        }
    }
}
