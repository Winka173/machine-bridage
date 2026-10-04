using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// A boss's parts on its view (prompts 8 and 9). A part is one or more model nodes ("node" in the
    /// data: names joined by '|', a trailing '*' for every node starting so, such as the barrels of a
    /// main gun), an attached model (the supergun's tractors), or only a place on the hull. When the sim
    /// breaks it, its nodes are hidden and its broken piece (a bent barrel, a burnt engine pod, a
    /// charred stump) is put in where it stood; a self-repair puts it back. The part the player has
    /// ordered fire at is outlined. Also the models a boss carries along and a boring boss sinking into
    /// the ground. The fires and smoke at the breaks are the effects director's (EffectsDirector.BossParts).
    /// </summary>
    public sealed partial class VehicleView
    {
        private ModelLibrary _partModels;
        private MaterialLibrary _partMaterials;
        private MeshLibrary _partMeshes;
        private bool[] _partShownBroken;
        private float _burrowDepth;

        /// <summary>Each part's nodes (empty: a place on the hull only).</summary>
        private List<Transform>[] _partNodeSets;

        /// <summary>Each part's broken piece while it is shown broken.</summary>
        private GameObject[] _partWrecks;

        /// <summary>The attached models (the supergun's tractors), in the data's order.</summary>
        private readonly List<GameObject> _attached = new();

        private int _outlined = -1;
        private readonly List<GameObject> _outline = new();
        private Material _outlineMaterial;
        private Material _outlineRingMaterial;

        /// <summary>How far under the ground a boring boss goes (below any hull).</summary>
        private const float BurrowDepth = 9f;

        private void InitBossParts(ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials)
        {
            _partModels = models;
            _partMeshes = meshes;
            _partMaterials = materials;
            // Prompt 20 G.3: the weapons a mini boss was built without are not drawn; a variant wears its colour.
            if (Def.HiddenNodes.Count > 0)
            {
                var nodes = _model.Root.GetComponentsInChildren<Transform>(true);
                foreach (var names in Def.HiddenNodes)
                    foreach (var pattern in names.Split('|'))
                    {
                        var prefix = pattern.EndsWith("*") ? pattern.Substring(0, pattern.Length - 1) : null;
                        foreach (var t in nodes)
                            if (t != _model.Root.transform && (prefix != null ? t.name.StartsWith(prefix) : t.name == pattern)) t.gameObject.SetActive(false);
                    }
            }
            if (Def.Tint != null) ApplyTint();
            var parts = Def.Parts;
            if (parts.Count > 0)
            {
                var all = _model.Root.GetComponentsInChildren<Transform>(true);
                _partNodeSets = new List<Transform>[parts.Count];
                for (var i = 0; i < parts.Count; i++)
                {
                    _partNodeSets[i] = new List<Transform>();
                    if (parts[i].Node == null) continue;
                    foreach (var pattern in parts[i].Node.Split('|'))
                    {
                        var prefix = pattern.EndsWith("*") ? pattern.Substring(0, pattern.Length - 1) : null;
                        foreach (var t in all)
                        {
                            if (t == _model.Root.transform) continue;
                            var match = prefix != null ? t.name.StartsWith(prefix) : t.name == pattern;
                            // Nested matches (a barrel under a barrel group) are taken with their parent.
                            if (!match || _partNodeSets[i].Contains(t) || HasAncestorIn(t, _partNodeSets[i])) continue;
                            _partNodeSets[i].Add(t);
                            if (prefix == null) break;
                        }
                    }
                    foreach (var t in _partNodeSets[i]) _partNodes.Add((i, t));
                }
                _partShownBroken = new bool[parts.Count];
                _partWrecks = new GameObject[parts.Count];
            }
            // Models drawn fixed to it, placed in its model's frame (the Blender builder's: X left, Y back, Z up).
            foreach (var a in Def.Attachments)
            {
                if (!models.Has(a.Model))
                {
                    _attached.Add(null);
                    continue;
                }
                var extra = models.Spawn(a.Model, Sim.Team, _model.Root.transform, livery: Livery);
                extra.Root.transform.localPosition = new Vector3(-a.At.X, a.At.Z, -a.At.Y);
                extra.Root.transform.localRotation = Quaternion.Euler(0f, a.Heading, 0f);
                _attached.Add(extra.Root);
            }
        }

        private static bool HasAncestorIn(Transform t, List<Transform> set)
        {
            for (var p = t.parent; p != null; p = p.parent)
                if (set.Contains(p)) return true;
            return false;
        }

        private void AnimateBossParts()
        {
            if (_partShownBroken != null)
                for (var i = 0; i < _partShownBroken.Length; i++)
                {
                    var broken = Sim.IsPartBroken(i);
                    if (broken == _partShownBroken[i]) continue;
                    _partShownBroken[i] = broken;
                    if (broken) ShowBroken(i);
                    else ShowMended(i);
                }
            if (_outline.Count > 0) PulseOutline();
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

        // ------------------------------------------------------------------ where each part is

        /// <summary>The transform a part's fire and smoke ride on: its node's parent (a turret turns them with it), its attached model, or the model.</summary>
        public Transform PartAnchor(int i)
        {
            if (_partNodeSets != null && i >= 0 && i < _partNodeSets.Length && _partNodeSets[i].Count > 0 && _partNodeSets[i][0].parent != null)
                return _partNodeSets[i][0].parent;
            var attach = i >= 0 && i < Def.Parts.Count ? Def.Parts[i].Attachment : -1;
            if (attach >= 0 && attach < _attached.Count && _attached[attach] != null) return _attached[attach].transform;
            return _model.Root.transform;
        }

        /// <summary>Where part <paramref name="i"/> is now, in the world (its node, its attached model, or its place on the hull).</summary>
        public Vector3 PartWorld(int i)
        {
            if (_partNodeSets != null && i >= 0 && i < _partNodeSets.Length && _partNodeSets[i].Count > 0) return _partNodeSets[i][0].position;
            if (i < 0 || i >= Def.Parts.Count) return Position;
            var attach = Def.Parts[i].Attachment;
            if (attach >= 0 && attach < _attached.Count && _attached[attach] != null) return _attached[attach].transform.position + Vector3.up * 1.5f;
            var p = Def.Parts[i];
            return _model.Root.transform.TransformPoint(new Vector3(p.At.X, p.Height, p.At.Y));
        }

        /// <summary>The model the boss is drawn with (its body's fires ride on it).</summary>
        public Transform ModelRoot => _model.Root.transform;

        // ------------------------------------------------------------------ broken, mended

        /// <summary>A part broke: its nodes hidden, its broken piece put in where it stood.</summary>
        private void ShowBroken(int i)
        {
            var part = Def.Parts[i];
            var nodes = _partNodeSets?[i];
            var anchor = PartAnchor(i);
            Vector3 local;
            var rotation = Quaternion.identity;
            if (nodes != null && nodes.Count > 0)
            {
                local = nodes[0].localPosition;
                rotation = nodes[0].localRotation;
                foreach (var n in nodes) n.gameObject.SetActive(false);
            }
            else if (anchor != _model.Root.transform)
            {
                // A tractor: its body stays, burnt out; the stump goes on its deck.
                local = Vector3.up * 1.2f;
            }
            else local = new Vector3(part.At.X, part.Height, part.At.Y);
            if (part.Wreck != null && _partModels != null && _partModels.Has(part.Wreck))
            {
                var piece = _partModels.Spawn(part.Wreck, Sim.Team, anchor, castShadows: true, livery: Livery);
                piece.Root.transform.localPosition = local;
                piece.Root.transform.localRotation = rotation;
                _partWrecks[i] = piece.Root;
            }
            if (_outlined == i) SetOutlinedPart(-1);
        }

        /// <summary>A self-repair put the part back: whole again, its broken piece gone.</summary>
        private void ShowMended(int i)
        {
            var nodes = _partNodeSets?[i];
            if (nodes != null)
                foreach (var n in nodes) n.gameObject.SetActive(true);
            if (_partWrecks?[i] != null)
            {
                Object.Destroy(_partWrecks[i]);
                _partWrecks[i] = null;
            }
        }

        // ------------------------------------------------------------------ the outline of the ordered part

        /// <summary>Outlines part <paramref name="i"/> (the player's part order); -1 clears it.</summary>
        public void SetOutlinedPart(int i)
        {
            if (i == _outlined) return;
            foreach (var go in _outline)
                if (go != null) Object.Destroy(go);
            _outline.Clear();
            _outlined = i;
            if (i < 0 || i >= Def.Parts.Count || _partMaterials == null) return;
            if (_outlineRingMaterial == null)
            {
                var shader = Shader.Find("MachineBrigade/Outline");
                if (shader != null)
                {
                    _outlineMaterial = new Material(shader) { name = "Part outline" };
                    _outlineMaterial.SetFloat("_Width", 0.1f);
                }
                _outlineRingMaterial = new Material(_partMaterials.SelectionRing) { name = "Part ring" };
            }
            // The part's meshes drawn again a little fatter from behind: a bright rim round them.
            if (_outlineMaterial != null && _partNodeSets != null)
                foreach (var node in _partNodeSets[i])
                foreach (var filter in node.GetComponentsInChildren<MeshFilter>(false))
                {
                    if (filter.sharedMesh == null || filter.gameObject.name == "Outline") continue;
                    var go = new GameObject("Outline");
                    go.transform.SetParent(filter.transform, false);
                    go.AddComponent<MeshFilter>().sharedMesh = filter.sharedMesh;
                    var r = go.AddComponent<MeshRenderer>();
                    r.sharedMaterial = _outlineMaterial;
                    r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                    _outline.Add(go);
                }
            // And a ring round it (the only mark for a part that is a place on the hull).
            if (_partMeshes?.Ring != null)
            {
                var ring = new GameObject("Part ring");
                ring.transform.SetParent(Root, false);
                ring.AddComponent<MeshFilter>().sharedMesh = _partMeshes.Ring;
                var rr = ring.AddComponent<MeshRenderer>();
                rr.sharedMaterial = _outlineRingMaterial;
                rr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                _outline.Add(ring);
            }
        }

        /// <summary>The ordered part's outline pulses gold, its ring follows the part.</summary>
        private void PulseOutline()
        {
            var pulse = 0.55f + 0.45f * Mathf.Sin(Time.unscaledTime * 6f);
            var colour = new Color(2.6f, 1.9f, 0.45f, 1f) * (0.6f + 0.6f * pulse);
            if (_outlineMaterial != null) _outlineMaterial.SetColor("_Color", colour);
            if (_outlineRingMaterial != null) _outlineRingMaterial.SetColor("_Color", colour);
            var ring = _outline[_outline.Count - 1];
            if (ring == null || ring.name != "Part ring" || _outlined < 0) return;
            var size = Mathf.Max(1.6f, Def.Parts[_outlined].Radius) * (1.9f + 0.25f * pulse);
            ring.transform.position = PartWorld(_outlined) + Vector3.up * 0.2f;
            ring.transform.rotation = Quaternion.identity;
            var scale = Root.lossyScale;
            ring.transform.localScale = new Vector3(size / Mathf.Max(0.01f, scale.x), 1f, size / Mathf.Max(0.01f, scale.z));
        }
    }
}
