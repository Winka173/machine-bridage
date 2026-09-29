using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Entities;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 17 C: the bunker vehicle's state on the unit. Left of the health bar, in flat quads like the stores
    /// icon: digging in or packing up is an amber bar that fills with the work done (a small marker pulsing
    /// beside it), dug in is a green block with a solid base (a bunker), shown while the bar is.
    /// Play-test 4 (DECISIONS 19R): digging in turns the vehicle into a pillbox, in the model's Deploy_* parts
    /// (mb_p21_models.py) over the data's seconds: the rear spades swing down and the dozer blade bites (first
    /// third), the hull sinks 0.8 m into its scrape while the spoil bank grows round it, the side plates fold out
    /// and down over the bank, and last the turret rises on its telescopic mount. Packing up runs it backwards.
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform _deployMark, _deployFill, _deployBlock;
        private Transform _spadeL, _spadeR, _dozer, _plateL, _plateR, _riser, _berm, _hull;
        private Quaternion _spadeLRest, _spadeRRest, _dozerRest, _plateLRest, _plateRRest;
        private Vector3 _riserRest, _bermRest, _bermScale, _hullRest;
        private DeployState _deployShown = DeployState.Mobile;
        private float _deployChangedAt, _deployPose;

        /// <summary>
        /// The dug-in pose on the model's hinges (degrees) and in its units: the spades' swing, the blade's bite, the
        /// side plates' fold, how deep the hull sinks and how high the turret's mount rises.
        /// </summary>
        internal const float SpadeSwing = -125f, BladeBite = 6f, PlateFold = 95f, HullSink = 0.8f, MountLift = 0.75f;

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
                switch (t.name)
                {
                    case "Deploy_spade_l": _spadeL = t; break;
                    case "Deploy_spade_r": _spadeR = t; break;
                    case "Deploy_blade": _dozer = t; break;
                    case "Deploy_plate_l": _plateL = t; break;
                    case "Deploy_plate_r": _plateR = t; break;
                    case "Deploy_riser": _riser = t; break;
                    case "Deploy_berm": _berm = t; break;
                }
            }
            if (_spadeL != null) _spadeLRest = _spadeL.localRotation;
            if (_spadeR != null) _spadeRRest = _spadeR.localRotation;
            if (_dozer != null) _dozerRest = _dozer.localRotation;
            if (_plateL != null) _plateLRest = _plateL.localRotation;
            if (_plateR != null) _plateRRest = _plateR.localRotation;
            if (_riser != null) _riserRest = _riser.localPosition;
            if (_berm != null)
            {
                _bermRest = _berm.localPosition;
                _bermScale = _berm.localScale;
                _berm.gameObject.SetActive(false);
            }
            _hull = _model.Root.transform;
            _hullRest = _hull.localPosition;
        }

        /// <summary>Share of stage [a, b] done at pose <paramref name="p"/>, eased at both ends.</summary>
        private static float Stage(float p, float a, float b)
        {
            var s = Mathf.Clamp01((p - a) / (b - a));
            return s * s * (3f - 2f * s);
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
            if (Mathf.Approximately(target, _deployPose) && Sim.Deploy is DeployState.Mobile or DeployState.Deployed) return;
            _deployPose = target;
            var spades = Stage(target, 0f, 0.35f);
            var dig = Stage(target, 0.15f, 0.7f);
            var plates = Stage(target, 0.45f, 0.85f);
            var lift = Stage(target, 0.7f, 1f);
            if (_spadeL != null) _spadeL.localRotation = _spadeLRest * Quaternion.Euler(SpadeSwing * spades, 0f, 0f);
            if (_spadeR != null) _spadeR.localRotation = _spadeRRest * Quaternion.Euler(SpadeSwing * spades, 0f, 0f);
            if (_dozer != null) _dozer.localRotation = _dozerRest * Quaternion.Euler(BladeBite * dig, 0f, 0f);
            // The model's left plate is on its +X side (Unity -X): +Z folds it outwards and down.
            if (_plateL != null) _plateL.localRotation = _plateLRest * Quaternion.Euler(0f, 0f, PlateFold * plates);
            if (_plateR != null) _plateR.localRotation = _plateRRest * Quaternion.Euler(0f, 0f, -PlateFold * plates);
            if (_riser != null) _riser.localPosition = _riserRest + Vector3.up * MountLift * lift;
            // Into the scrape: the whole model sinks, the bank stays on the ground and rises round it.
            if (_hull != null && _berm != null)
            {
                _hull.localPosition = _hullRest + Vector3.down * HullSink * dig;
                var shown = dig > 0f;
                if (_berm.gameObject.activeSelf != shown) _berm.gameObject.SetActive(shown);
                _berm.localPosition = _bermRest + Vector3.up * HullSink * dig;
                _berm.localScale = shown ? new Vector3(1f, Mathf.Max(0.03f, dig), 1f) : _bermScale;
            }
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
