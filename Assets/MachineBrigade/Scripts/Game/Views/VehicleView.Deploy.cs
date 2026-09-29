using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Entities;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 17 C: the bunker vehicle's state on the unit. Left of the health bar, in flat quads like the stores
    /// icon: digging in or packing up is an amber bar that fills with the work done (a small marker pulsing
    /// beside it), dug in is a green block with a solid base (a bunker), shown while the bar is. The model's
    /// earth spades (Spade_L, Spade_R) swing down and its front plate (Plate_front) rises as it digs in.
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform _deployMark, _deployFill, _deployBlock;
        private Transform _spadeL, _spadeR, _plate;
        private Quaternion _spadeLRest, _spadeRRest;
        private Vector3 _plateRest;
        private DeployState _deployShown = DeployState.Mobile;
        private float _deployChangedAt, _deployPose;

        /// <summary>How far the spades swing down and the plate rises, dug in (the model's hinges).</summary>
        private const float SpadeSwing = -125f, PlateRise = 0.75f;

        private void BuildDeployMark(MeshLibrary meshes, MaterialLibrary materials)
        {
            if (Def.Deploy == null) return;
            _deployMark = new GameObject("DeployMark").transform;
            _deployMark.SetParent(_bar, false);
            _deployMark.localPosition = new Vector3(-BarWidth * 0.5f - 0.72f, 0.05f, 0f);
            var back = CreateMesh("Back", _deployMark, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(0.74f, 0.74f, 1f);
            _deployFill = CreateMesh("Fill", _deployMark, meshes.Quad, materials.StoresLow, false);
            _deployFill.localPosition = new Vector3(0f, 0f, -0.01f);
            _deployBlock = new GameObject("Bunker").transform;
            _deployBlock.SetParent(_deployMark, false);
            var top = CreateMesh("Top", _deployBlock, meshes.Quad, materials.StoresFull, false);
            top.localScale = new Vector3(0.44f, 0.22f, 1f);
            top.localPosition = new Vector3(0f, 0.08f, -0.01f);
            var slit = CreateMesh("Slit", _deployBlock, meshes.Quad, materials.BarBack, false);
            slit.localScale = new Vector3(0.3f, 0.06f, 1f);
            slit.localPosition = new Vector3(0f, 0.08f, -0.02f);
            var foot = CreateMesh("Foot", _deployBlock, meshes.Quad, materials.StoresFull, false);
            foot.localScale = new Vector3(0.58f, 0.1f, 1f);
            foot.localPosition = new Vector3(0f, -0.16f, -0.01f);
            _deployMark.gameObject.SetActive(false);
            foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
            {
                if (t.name == "Spade_L") _spadeL = t;
                else if (t.name == "Spade_R") _spadeR = t;
                else if (t.name == "Plate_front") _plate = t;
            }
            if (_spadeL != null) _spadeLRest = _spadeL.localRotation;
            if (_spadeR != null) _spadeRRest = _spadeR.localRotation;
            if (_plate != null) _plateRest = _plate.localPosition;
        }

        /// <summary>Not on its tracks (the health bar shows with the mark).</summary>
        private bool DeployWanted => _deployMark != null && Sim.Deploy != DeployState.Mobile;

        /// <summary>The spades and plate follow the state (the work takes the data's seconds).</summary>
        private void AnimateDeploy()
        {
            if (_deployMark == null) return;
            if (Sim.Deploy != _deployShown)
            {
                _deployShown = Sim.Deploy;
                _deployChangedAt = Time.time;
            }
            var seconds = Mathf.Max(0.1f, Def.Deploy.Seconds);
            var target = Sim.Deploy switch
            {
                DeployState.Deploying => Mathf.Clamp01((Time.time - _deployChangedAt) / seconds),
                DeployState.Deployed => 1f,
                DeployState.Packing => 1f - Mathf.Clamp01((Time.time - _deployChangedAt) / seconds),
                _ => 0f,
            };
            _deployPose = target;
            var eased = _deployPose * _deployPose * (3f - 2f * _deployPose);
            if (_spadeL != null) _spadeL.localRotation = _spadeLRest * Quaternion.Euler(SpadeSwing * eased, 0f, 0f);
            if (_spadeR != null) _spadeR.localRotation = _spadeRRest * Quaternion.Euler(SpadeSwing * eased, 0f, 0f);
            if (_plate != null) _plate.localPosition = _plateRest + Vector3.up * PlateRise * eased;
        }

        /// <summary>Draws the state mark on the health bar.</summary>
        private void RenderDeployMark()
        {
            if (_deployMark == null) return;
            var show = Sim.Deploy != DeployState.Mobile;
            if (_deployMark.gameObject.activeSelf != show) _deployMark.gameObject.SetActive(show);
            if (!show) return;
            var dug = Sim.Deploy == DeployState.Deployed;
            _deployBlock.gameObject.SetActive(dug);
            _deployFill.gameObject.SetActive(!dug);
            if (dug) return;
            var seconds = Mathf.Max(0.1f, Def.Deploy.Seconds);
            var done = Mathf.Clamp01((Time.time - _deployChangedAt) / seconds);
            var share = Sim.Deploy == DeployState.Packing ? 1f - done : done;
            // An amber bar filling (digging in) or emptying (packing up), bottom up.
            var h = 0.08f + 0.5f * share;
            _deployFill.localScale = new Vector3(0.5f, h, 1f);
            _deployFill.localPosition = new Vector3(0f, -0.29f + h * 0.5f, -0.01f);
            _deployMark.localScale = Vector3.one * (1f + 0.06f * Mathf.Sin(Time.time * 7f));
        }
    }
}
