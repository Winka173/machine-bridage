using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// The vehicle on the detail screen: its model on a slow turntable, lit by the scene's sun,
    /// seen by a camera of its own (on a layer the battlefield camera ignores) that renders into a
    /// texture the menu shows. The camera only runs while a vehicle is shown.
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
            Texture = new RenderTexture(640, 480, 24, RenderTextureFormat.ARGB32) { name = "Unit Preview", antiAliasing = 4 };
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

        public RenderTexture Texture { get; }

        /// <summary>Shows a vehicle's model (in the player's colours) and starts the camera.</summary>
        public void Show(string modelId, float scale)
        {
            var fromRange = _range != null;
            CloseRange();
            _turntable.gameObject.SetActive(true);
            if (fromRange && _model != null) Frame();
            if (_shown != modelId || _model == null)
            {
                if (_model != null) Object.Destroy(_model);
                var instance = _models.Spawn(modelId, 0, _turntable, castShadows: false);
                _model = instance.Root;
                _model.transform.localScale = Vector3.one * scale;
                _model.transform.localRotation = Quaternion.identity;
                SetLayer(_model.transform);
                _shown = modelId;
                Frame();
            }
            _camera.enabled = true;
        }

        /// <summary>The vehicle in action: firing at targets on a little range of its own (see <see cref="FiringRange"/>).</summary>
        public void ShowRange(string vehicleId)
        {
            CloseRange();
            _turntable.gameObject.SetActive(false);
            _range = new FiringRange(_catalog, _materials, _meshes, _models, _camera, Layer, vehicleId);
            _camera.enabled = true;
        }

        private void CloseRange()
        {
            if (_range == null) return;
            _range.Dispose();
            _range = null;
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
            if (_range != null) _range.Tick(dt);
            else _turntable.Rotate(0f, 22f * dt, 0f, Space.Self);
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
            _camera.transform.position = look + new Vector3(0.62f, 0.52f, -1f).normalized * distance;
            _camera.transform.LookAt(look);
        }

        private static void SetLayer(Transform t)
        {
            t.gameObject.layer = Layer;
            foreach (Transform child in t) SetLayer(child);
        }
    }
}
