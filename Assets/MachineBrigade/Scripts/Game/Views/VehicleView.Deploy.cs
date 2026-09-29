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
    /// (mb_p21_models.py, the bank from mb_pt5_models.py) over the data's seconds: the rear spades swing down and the
    /// dozer blade bites (first third), the hull sinks 1.25 m into its scrape while the emplacement's bank, sandbags
    /// and net grow round it, the side plates lean out against the bank, and last the turret rises on its telescopic
    /// mount. Packing up runs it backwards.
    /// Play-test 5 (DECISIONS 20W): the siege tank (mb_p22_siege.py) sieges on the same state; play-test 6 (DECISIONS
    /// 21H) redrew it after StarCraft 2's siege tank: four legs swing out and brace, the hull lifts, the turret swings
    /// round and the siege cannon runs out, locks and is laid (<see cref="AnimateSiege"/>).
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform _deployMark, _deployFill, _deployBlock;
        private Transform _spadeL, _spadeR, _dozer, _plateL, _plateR, _riser, _berm, _hull, _tankGun;
        private Quaternion _spadeLRest, _spadeRRest, _dozerRest, _plateLRest, _plateRRest;
        private Vector3 _riserRest, _bermRest, _bermScale, _hullRest, _tankGunRest;
        private DeployState _deployShown = DeployState.Mobile;
        private float _deployChangedAt, _deployPose;

        /// <summary>
        /// The dug-in pose on the model's hinges (degrees) and in its units: the spades' swing, the blade's bite, the
        /// side plates' fold, how deep the hull sinks and how high the turret's mount rises. Play-test 5 (DECISIONS
        /// 20V) dug it in as an emplacement: hull-down (the hull top just above the ground inside the bank), the
        /// turret lifted just clear of the parapet, and the side plates leaning out only 20 degrees to line the pit's
        /// sides as revetments under the bank's crest (they folded flat over a low bank before).
        /// </summary>
        internal const float SpadeSwing = -125f, BladeBite = 6f, PlateFold = 20f, HullSink = 1.25f, MountLift = 0.55f;

        /// <summary>
        /// Play-test 6 (DECISIONS 21H): the siege tank's sieged pose (mb_p22_siege.py), after StarCraft 2's siege tank:
        /// how far each leg swings out and tilts down (degrees), the leg's hinge height, length and the pad's depth under
        /// its ram housing, how far the hull lifts, how far the twin 105 mm slides back (all the way into the turret: play-test 7), how high the turret's ring
        /// unlocks, how far the siege cannon runs out, the rear spades' swing, and the cannon's angle when it has
        /// nothing to aim at (Elevate lays it on a target).
        /// </summary>
        internal const float LegSwing = 120f, LegTilt = 25f, LegHinge = 1.2f, LegLength = 1.45f, PadUnder = 0.07f,
            SiegeHullLift = 0.25f, GunRetract = 3.0f, SiegeLift = 0.15f, BarrelRun = 1.9f, SiegeSpadeSwing = -140f,
            SiegeRestPitch = 45f;

        /// <summary>How far each ram drives its pad down to the ground once its leg has tilted (before the hull lifts).</summary>
        internal static float PadDrop => LegHinge - PadUnder - LegLength * Mathf.Sin(LegTilt * Mathf.Deg2Rad);

        /// <summary>The share of sieging done after which the siege cannon swings up (the last part of the work).</summary>
        internal const float MortarFrom = 0.88f;

        /// <summary>
        /// The siege tank's legs (front left, front right, rear left, rear right), their ram housings and rams; the
        /// telescoping barrel parts (by index into the recoil parts) and the main muzzle that runs out with them.
        /// </summary>
        private readonly Transform[] _legs = new Transform[4], _knees = new Transform[4], _rams = new Transform[4];
        private readonly Quaternion[] _legRest = new Quaternion[4], _kneeRest = new Quaternion[4];
        private readonly Vector3[] _ramRest = new Vector3[4];
        private bool[] _barrelSlides;
        private Transform _siegeMuzzle;
        private Vector3 _siegeMuzzleRest;

        /// <summary>The turret's turn off its sim heading (180 in tank mode: the model is drawn sieged) and how far the siege cannon is run in.</summary>
        private float _turretSwing, _barrelIn;

        private static readonly string[] LegNames = { "Deploy_brace_l", "Deploy_brace_r", "Deploy_leg_l", "Deploy_leg_r" },
            KneeNames = { "Deploy_braceknee_l", "Deploy_braceknee_r", "Deploy_legknee_l", "Deploy_legknee_r" },
            RamNames = { "Deploy_braceram_l", "Deploy_braceram_r", "Deploy_legram_l", "Deploy_legram_r" };

        /// <summary>Each leg's swing out (Unity yaw sign) and tilt down (the front legs lie along -Z, the rear along +Z).</summary>
        private static readonly float[] LegYaw = { 1f, -1f, -1f, 1f }, LegPitch = { -1f, -1f, 1f, 1f };

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
                    case "Deploy_gun": _tankGun = t; break;
                }
                for (var i = 0; i < LegNames.Length; i++)
                {
                    if (t.name == LegNames[i]) _legs[i] = t;
                    else if (t.name == KneeNames[i]) _knees[i] = t;
                    else if (t.name == RamNames[i]) _rams[i] = t;
                }
            }
            for (var i = 0; i < 4; i++)
            {
                if (_legs[i] != null) _legRest[i] = _legs[i].localRotation;
                if (_knees[i] != null) _kneeRest[i] = _knees[i].localRotation;
                if (_rams[i] != null) _ramRest[i] = _rams[i].localPosition;
            }
            if (Def.Deploy.Siege)
            {
                // The siege cannon's inner tube and brake telescope along the barrel with the main muzzle (drawn run in).
                _barrelSlides = new bool[_model.RecoilParts.Count];
                for (var i = 0; i < _barrelSlides.Length; i++)
                {
                    var name = _model.RecoilParts[i].name;
                    _barrelSlides[i] = name.StartsWith("Main_cannon_tube") || name.StartsWith("Muzzle_brake");
                }
                if (_model.Muzzles.TryGetValue("main", out _siegeMuzzle)) _siegeMuzzleRest = _siegeMuzzle.localPosition;
            }
            if (_spadeL != null) _spadeLRest = _spadeL.localRotation;
            if (_spadeR != null) _spadeRRest = _spadeR.localRotation;
            if (_dozer != null) _dozerRest = _dozer.localRotation;
            if (_plateL != null) _plateLRest = _plateL.localRotation;
            if (_plateR != null) _plateRRest = _plateR.localRotation;
            if (_riser != null) _riserRest = _riser.localPosition;
            if (_tankGun != null) _tankGunRest = _tankGun.localPosition;
            if (_berm != null)
            {
                _bermRest = _berm.localPosition;
                _bermScale = _berm.localScale;
                _berm.gameObject.SetActive(false);
            }
            _hull = _model.Root.transform;
            _hullRest = _hull.localPosition;
            // The siege tank starts on its tracks: the turret turned round, the siege cannon run in.
            if (Def.Deploy.Siege) AnimateSiege(0f);
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
            if (Def.Deploy.Siege)
            {
                AnimateSiege(target);
                return;
            }
            var spades = Stage(target, 0f, 0.35f);
            var dig = Stage(target, 0.15f, 0.7f);
            var plates = Stage(target, 0.45f, 0.85f);
            var lift = Stage(target, 0.7f, 1f);
            if (_spadeL != null) _spadeL.localRotation = _spadeLRest * Quaternion.Euler(SpadeSwing * spades, 0f, 0f);
            if (_spadeR != null) _spadeR.localRotation = _spadeRRest * Quaternion.Euler(SpadeSwing * spades, 0f, 0f);
            if (_dozer != null) _dozer.localRotation = _dozerRest * Quaternion.Euler(BladeBite * dig, 0f, 0f);
            // The model's left plate is on its +X side (Unity -X): +Z leans it outwards.
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

        /// <summary>
        /// Play-test 6 (DECISIONS 21H): the siege tank's parts at sieging pose <paramref name="p"/> (0 on its tracks, 1
        /// sieged), in StarCraft 2's order, over the data's 2.5 s (packing up runs it backwards): the twin 105 mm slides
        /// right into the turret, out of sight, while the four legs swing out from the pods and tilt down; the rams drive the pads on to the
        /// ground and the rear spades bite; the rams push on and lift the hull; the turret's ring unlocks and the turret
        /// swings round, bringing the siege cannon forward; the cannon runs out and its collar locks with a knock
        /// against the sleeve; last it is laid (<see cref="SiegeElevation"/>).
        /// </summary>
        private void AnimateSiege(float p)
        {
            var gun = Stage(p, 0.02f, 0.34f);
            var swing = Stage(p, 0f, 0.26f);
            var tilt = Stage(p, 0.14f, 0.36f);
            var plant = Stage(p, 0.28f, 0.46f);
            var spades = Stage(p, 0.3f, 0.5f);
            var lift = Stage(p, 0.44f, 0.62f);
            var unlock = Stage(p, 0.4f, 0.48f);
            var turn = Stage(p, 0.46f, 0.74f);
            var run = Stage(p, 0.7f, 0.86f);
            var knock = p is > 0.86f and < 0.92f ? Mathf.Sin((p - 0.86f) / 0.06f * Mathf.PI) : 0f;
            if (_tankGun != null) _tankGun.localPosition = _tankGunRest + Vector3.forward * GunRetract * gun;
            for (var i = 0; i < 4; i++)
            {
                if (_legs[i] != null)
                    _legs[i].localRotation = _legRest[i] * Quaternion.Euler(0f, LegYaw[i] * LegSwing * swing, 0f) *
                                             Quaternion.Euler(LegPitch[i] * LegTilt * tilt, 0f, 0f);
                // The ram housing stays upright whatever the leg's tilt; the ram drives straight down out of it.
                if (_knees[i] != null) _knees[i].localRotation = _kneeRest[i] * Quaternion.Euler(-LegPitch[i] * LegTilt * tilt, 0f, 0f);
                if (_rams[i] != null) _rams[i].localPosition = _ramRest[i] + Vector3.down * (PadDrop * plant + SiegeHullLift * lift);
            }
            if (_spadeL != null) _spadeL.localRotation = _spadeLRest * Quaternion.Euler(SiegeSpadeSwing * spades, 0f, 0f);
            if (_spadeR != null) _spadeR.localRotation = _spadeRRest * Quaternion.Euler(SiegeSpadeSwing * spades, 0f, 0f);
            if (_hull != null) _hull.localPosition = _hullRest + Vector3.up * SiegeHullLift * lift;
            if (_riser != null) _riser.localPosition = _riserRest + Vector3.up * SiegeLift * unlock;
            _turretSwing = 180f * (1f - turn);
            _barrelIn = BarrelRun * (1f - run) - 0.07f * knock;
            if (_siegeMuzzle != null) _siegeMuzzle.localPosition = _siegeMuzzleRest + Vector3.forward * (BarrelRun - _barrelIn);
        }

        /// <summary>How far a recoiling part is drawn along its barrel: the siege cannon's tube and brake as run out.</summary>
        private float BarrelRunOf(int part) => _barrelSlides != null && _barrelSlides[part] ? BarrelRun - _barrelIn : 0f;

        /// <summary>
        /// Play-test 5: the siege tank's cannon angle (degrees above level) at the pose shown: level on its tracks, swinging
        /// up over the last of the work, then laid by range on a target (as a mortar's) or resting at 45 degrees.
        /// </summary>
        private float SiegeElevation(float rest, float aimed)
        {
            var up = Stage(_deployPose, MortarFrom, 1f);
            var sieged = Sim.Deploy == DeployState.Deployed && !float.IsNaN(aimed) ? aimed : SiegeRestPitch;
            return Mathf.Lerp(rest, sieged, up);
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
