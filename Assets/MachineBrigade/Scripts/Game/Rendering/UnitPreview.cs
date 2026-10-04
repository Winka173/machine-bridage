using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// The vehicle on the detail screen: its model on a slow turntable, lit by the scene's sun,
    /// seen by a camera of its own (on a layer the battlefield camera ignores) that renders into a
    /// texture the menu shows. The camera only runs while a vehicle is shown.
    /// The texture takes the shape of the box the menu shows it in (<see cref="Fit"/>), and the
    /// camera's view is cut to what the old 4:3 texture showed in the detail page's box (DECISIONS
    /// 12E): the turntable and the In action clips are framed as before, only bigger and sharper.
    /// </summary>
    public sealed class UnitPreview
    {
        /// <summary>A layer nothing else uses: the preview model lives on it alone.</summary>
        private const int Layer = 31;

        private readonly Catalog _catalog;
        private readonly MaterialLibrary _materials;
        private readonly MeshLibrary _meshes;
        private readonly ModelLibrary _models;
        private readonly Transform _root, _turntable;
        private readonly Camera _camera;
        private GameObject _model;
        private string _shown;
        private FiringRange _range;
        private bool _pinned;

        /// <summary>The texture's caps on a phone: its longest side, and its pixels (about 1280 x 720).</summary>
        private const int MaxSide = 1600, MaxPixels = 1280 * 720;

        /// <summary>Four samples up to this many pixels (the old 640 x 480 turntable), two above: the big theatre stays about as dear.</summary>
        private const int FourSamplesUpTo = 520 * 1000;

        public UnitPreview(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Transform parent)
        {
            _catalog = catalog;
            _materials = materials;
            _meshes = meshes;
            _models = models;
            _root = new GameObject("Unit Preview").transform;
            _root.SetParent(parent, false);
            _root.position = new Vector3(0f, -600f, 0f);
            _turntable = new GameObject("Turntable").transform;
            _turntable.SetParent(_root, false);
            Texture = NewTexture(640, 480);
            var cameraObject = new GameObject("Preview Camera");
            cameraObject.transform.SetParent(_root, false);
            _camera = cameraObject.AddComponent<Camera>();
            _camera.cullingMask = 1 << Layer;
            _camera.clearFlags = CameraClearFlags.SolidColor;
            _camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            _camera.targetTexture = Texture;
            _camera.fieldOfView = 28f;
            _camera.nearClipPlane = 0.5f;
            _camera.farClipPlane = 200f;
            _camera.enabled = false;
            var data = _camera.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = false;
            data.renderShadows = false;
            // The battlefield camera never draws the preview model.
            if (Camera.main != null) Camera.main.cullingMask &= ~(1 << Layer);
        }

        public RenderTexture Texture { get; private set; }

        /// <summary>The In action clip's line of text over the picture (a CP relay's pay), or null (see <see cref="FiringRange.Readout"/>).</summary>
        public string RangeReadout => _range?.Readout;

        /// <summary>The readout is a warning (the relay under fire).</summary>
        public bool RangeAlert => _range?.ReadoutAlert ?? false;

        /// <summary>The game's sound: the In action range is heard through it while it plays.</summary>
        public Audio.AudioDirector Audio { get; set; }

        /// <summary>Development capture only: a sharper texture for the range films (the menu's box no longer resizes it).</summary>
        public void Resize(int width, int height)
        {
            _pinned = true;
            Replace(width, height);
        }

        /// <summary>
        /// Sizes the texture to the box the menu shows it in (in screen pixels): the box's shape, and
        /// about its pixels within the caps. True when the texture was replaced (the menu then shows the new one).
        /// </summary>
        public bool Fit(float width, float height)
        {
            if (_pinned || width < 8f || height < 8f) return false;
            var shrink = Mathf.Min(1f, Mathf.Min(MaxSide / Mathf.Max(width, height), Mathf.Sqrt(MaxPixels / (width * height))));
            var w = Mathf.Max(64, Mathf.RoundToInt(width * shrink));
            var h = Mathf.Max(64, Mathf.RoundToInt(height * shrink));
            // A pixel or two of layout: keep the texture.
            if (Mathf.Abs(w - Texture.width) <= 2 && Mathf.Abs(h - Texture.height) <= 2) return false;
            Replace(w, h);
            return true;
        }

        private static RenderTexture NewTexture(int width, int height) =>
            new(width, height, 24, RenderTextureFormat.ARGB32) { name = "Unit Preview", antiAliasing = width * height <= FourSamplesUpTo ? 4 : 2 };

        private void Replace(int width, int height)
        {
            var old = Texture;
            Texture = NewTexture(width, height);
            _camera.targetTexture = Texture;
            old.Release();
            Object.Destroy(old);
            Project();
            if (_range == null && _model != null && _turntable.gameObject.activeSelf) Frame();
        }

        /// <summary>
        /// The camera's view cut to what the old 4:3 texture showed, cropped to fill the detail page's
        /// box (its narrow edge at most 20 % in from the 4:3 frame's): a wide box sees as much across as
        /// that frame and a little less top to bottom, a tall one the frame's width and more above and
        /// below. The range and the turntable frame the vehicle by the camera's field of view as before.
        /// </summary>
        private void Project()
        {
            var aspect = (float)Texture.width / Texture.height;
            var framing = Mathf.Max(0.8f, 4f / 3f / aspect);
            var fov = 2f * Mathf.Atan(Mathf.Tan(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad) * framing) * Mathf.Rad2Deg;
            _camera.aspect = aspect;
            _camera.projectionMatrix = Matrix4x4.Perspective(fov, aspect, _camera.nearClipPlane, _camera.farClipPlane);
        }

        /// <summary>
        /// Shows a vehicle's model (in the player's colours) and starts the camera. Prompt 34 L8: with its card
        /// (<paramref name="def"/>) the model stands in its own setting on the turntable (<see cref="PreviewStage"/>).
        /// </summary>
        public void Show(string modelId, float scale, VehicleDef def = null)
        {
            var fromRange = _range != null;
            CloseRange();
            _turntable.gameObject.SetActive(true);
            if (fromRange && _model != null) Frame();
            if (_shown != modelId || _model == null)
            {
                if (_model != null) Object.Destroy(_model);
                // Play-test 14 lane K: a ship or space boss shows its own livery.
                var instance = _models.Spawn(modelId, 0, _turntable, castShadows: false, livery: OwnLivery.Of(def));
                _model = instance.Root;
                _model.transform.localScale = Vector3.one * scale;
                _model.transform.localRotation = Quaternion.identity;
                SetLayer(_model.transform);
                _shown = modelId;
                Frame();
            }
            Dress(def);
            Project();
            _camera.enabled = true;
        }

        private PreviewStage _stage;
        private string _stageKey;
        private Vector3 _rest;
        private bool _hover;
        private float _bob;

        /// <summary>
        /// Prompt 34 L8: the setting under the turntable's model (the biome's ground, a wavy sea at the waterline, the water's
        /// edge, a track, a base pad; an aircraft hangs over the ground and bobs). Rebuilt when the model, setting or biome changes.
        /// </summary>
        private void Dress(VehicleDef def)
        {
            if (_model == null) return;
            var setting = PreviewSettings.Of(def);
            var biome = PreviewSettings.Biome();
            var key = _shown + "|" + setting + "|" + biome;
            var renderers = _model.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) return;
            var rotation = _turntable.rotation;
            _turntable.rotation = Quaternion.identity;
            var bounds = renderers[0].bounds;
            foreach (var r in renderers) bounds.Encapsulate(r.bounds);
            _turntable.rotation = rotation;
            if (_stage == null || _stageKey != key)
            {
                _stage?.Dispose();
                // The model's own origin over its foot is where a ship rides on the water in battle; a model drawn from its keel
                // gets a fifth of its height.
                var waterline = _model.transform.localPosition.y;
                if (waterline < 0.05f || waterline > bounds.size.y * 0.6f) waterline = bounds.size.y * 0.22f;
                var lift = setting == PreviewSetting.Air ? Mathf.Clamp((def?.Altitude ?? 0f) * 0.3f, 3f, 9f) + bounds.extents.y : 0f;
                _stage = PreviewStage.ForTurntable(_materials, _turntable, setting, biome, bounds.extents, waterline, lift);
                _stageKey = key;
                SetLayer(_stage.Root);
            }
            _hover = setting == PreviewSetting.Air;
            _bob = Mathf.Clamp(bounds.size.y * 0.05f, 0.08f, 0.5f);
            _rest = _model.transform.localPosition;
            _camera.farClipPlane = Mathf.Max(_camera.farClipPlane,
                Vector3.Distance(_camera.transform.position, _turntable.position) + _stage.Radius + 10f);
        }

        /// <summary>The vehicle (or a fire support, by its card id) in action: on a little range of its own (see <see cref="FiringRange"/>).</summary>
        public void ShowRange(string vehicleId)
        {
            CloseRange();
            _turntable.gameObject.SetActive(false);
            _range = new FiringRange(_catalog, _materials, _meshes, _models, _camera, Layer, vehicleId);
            // The range set its own field of view and clip planes.
            Project();
            _camera.enabled = true;
            if (Audio != null)
            {
                _range.Sounds = Audio.ConsumeRange;
                Audio.ViewOverride = _camera;
                Audio.ReachOverride = 90f;
            }
            // The range's shots carry the sound: the menu music steps back under them.
            MachineBrigade.Game.Audio.MusicDirector.Current?.Duck(RangeMusic);
        }

        /// <summary>The menu music's level while the In action range plays.</summary>
        private const float RangeMusic = 0.45f;

        private void CloseRange()
        {
            if (_range == null) return;
            _range.Dispose();
            _range = null;
            MachineBrigade.Game.Audio.MusicDirector.Current?.Duck(1f);
            if (Audio != null)
            {
                Audio.FocusOverride = null;
                Audio.ViewOverride = null;
                Audio.ReachOverride = 0f;
            }
            // The range moved the camera and widened its view: back to the turntable's.
            _camera.orthographic = false;
            _camera.fieldOfView = 28f;
            _camera.nearClipPlane = 0.5f;
            _camera.farClipPlane = 200f;
        }

        public void Hide()
        {
            CloseRange();
            _camera.enabled = false;
        }

        /// <summary>Per frame: the turntable turns, or the range plays, while it is shown.</summary>
        public void Tick(float dt)
        {
            if (!_camera.enabled) return;
            if (_range != null)
            {
                _range.Tick(dt);
                if (Audio != null) Audio.FocusOverride = _range.Look;
            }
            else
            {
                _turntable.Rotate(0f, 22f * dt, 0f, Space.Self);
                _stage?.Tick(Time.unscaledTime);
                if (_hover && _model != null) _model.transform.localPosition = _rest + Vector3.up * Mathf.Sin(Time.unscaledTime * 1.3f) * _bob;
            }
        }

        /// <summary>Centres the model on the turntable and backs the camera off to fit it, from a little above.</summary>
        private void Frame()
        {
            var renderers = _model.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) return;
            var rotation = _turntable.rotation;
            _turntable.rotation = Quaternion.identity;
            var bounds = renderers[0].bounds;
            foreach (var r in renderers) bounds.Encapsulate(r.bounds);
            _model.transform.position -= new Vector3(bounds.center.x - _turntable.position.x, 0f, bounds.center.z - _turntable.position.z);
            _model.transform.position -= new Vector3(0f, bounds.min.y - _turntable.position.y, 0f);
            _turntable.rotation = rotation;
            var radius = Mathf.Max(bounds.extents.magnitude, 1f);
            var distance = radius / Mathf.Sin(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad) * 1.05f;
            var look = _turntable.position + Vector3.up * bounds.extents.y * 0.8f;
            var back = new Vector3(0.62f, 0.52f, -1f).normalized;
            // Play-test 8 A (DECISIONS 22Q): framed by the model's bounds as the camera really sees them (its view cut to
            // the box, see Project), at every turn of the turntable, and the far clip pushed out past the model: the
            // Leviathan's 86 m hull ran out of the picture and past the old 200 m far plane.
            distance = Mathf.Max(distance, FitDistance(bounds.extents, look - _turntable.position, back) * 1.05f);
            _camera.farClipPlane = Mathf.Max(200f, distance + radius * 2f + 10f);
            Project();
            _camera.transform.position = look + back * distance;
            _camera.transform.LookAt(look);
        }

        /// <summary>
        /// How far back along <paramref name="back"/> the camera must stand for everything the turntable can turn into view
        /// to fit its real field of view: the model's footprint swept round (a circle of its half-diagonal) at the foot and
        /// the top of its bounds, <paramref name="lift"/> being where the camera looks above the turntable.
        /// </summary>
        private float FitDistance(Vector3 extents, Vector3 lift, Vector3 back)
        {
            var aspect = (float)Texture.width / Texture.height;
            var tanV = Mathf.Tan(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad) * Mathf.Max(0.8f, 4f / 3f / aspect);
            var tanH = tanV * aspect;
            var forward = -back;
            var right = Vector3.Cross(Vector3.up, forward).normalized;
            var up = Vector3.Cross(forward, right);
            var sweep = new Vector2(extents.x, extents.z).magnitude;
            var need = 0f;
            for (var level = 0; level < 2; level++)
                for (var k = 0; k < 24; k++)
                {
                    var a = k * Mathf.PI * 2f / 24f;
                    var q = new Vector3(Mathf.Cos(a) * sweep, level * extents.y * 2f, Mathf.Sin(a) * sweep) - lift;
                    var along = Vector3.Dot(q, back);
                    need = Mathf.Max(need, along + Mathf.Max(Mathf.Abs(Vector3.Dot(q, right)) / tanH, Mathf.Abs(Vector3.Dot(q, up)) / tanV));
                }
            return need;
        }

        private static void SetLayer(Transform t)
        {
            t.gameObject.layer = Layer;
            foreach (Transform child in t) SetLayer(child);
        }
    }
}
