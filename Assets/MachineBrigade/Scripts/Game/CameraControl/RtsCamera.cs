using UnityEngine;

namespace MachineBrigade.Game.CameraControl
{
    /// <summary>
    /// Orthographic battlefield camera, as in the 3d_astra reference: a fixed tilted diagonal view
    /// where sizes never change with depth. Yaw puts the south-west to north-east battle axis
    /// across the screen, which suits landscape phones. Panning is world-anchored (the ground
    /// under the finger stays under the finger), zoom keeps the pinch centre fixed, and the focus
    /// is clamped to the map so every corner stays reachable (V2 R03). Shake is added on top.
    /// </summary>
    public sealed class RtsCamera
    {
        private const float Pitch = 52f;
        private const float Yaw = -45f;
        private const float Distance = 60f; // keeps the view inside the shadow distance
        private const float MinZoom = 9f;
        private const float MaxZoom = 42f;
        private const float TraumaDecay = 1.4f;

        private readonly Camera _camera;
        private readonly float _halfSize;
        private float _trauma;
        private float _noiseTime;

        public RtsCamera(Camera camera, float halfSize, Vector3 focus, float zoom = 19f)
        {
            _camera = camera;
            _halfSize = halfSize;
            _camera.orthographic = true;
            _camera.nearClipPlane = 1f;
            _camera.farClipPlane = 320f;
            Focus = focus;
            Zoom = Mathf.Clamp(zoom, MinZoom, MaxZoom);
            Clamp();
            Place();
        }

        public Camera Camera => _camera;

        /// <summary>Point on the ground the camera looks at.</summary>
        public Vector3 Focus { get; private set; }

        /// <summary>Half the visible height in metres (the orthographic size).</summary>
        public float Zoom { get; private set; }

        public Quaternion Rotation => _camera.transform.rotation;

        public bool TryGroundPoint(Vector2 screen, out Vector3 point)
        {
            var ray = _camera.ScreenPointToRay(screen);
            point = default;
            if (ray.direction.y > -1e-4f) return false;
            point = ray.origin + ray.direction * (-ray.origin.y / ray.direction.y);
            return true;
        }

        public void Pan(Vector2 fromScreen, Vector2 toScreen)
        {
            Place(); // measure against the unshaken pose
            if (!TryGroundPoint(fromScreen, out var from) || !TryGroundPoint(toScreen, out var to)) return;
            Focus += from - to;
            Clamp();
            Place();
        }

        public void ZoomBy(float factor, Vector2 anchorScreen)
        {
            if (factor <= 0f) return;
            Place();
            var hadAnchor = TryGroundPoint(anchorScreen, out var before);
            Zoom = Mathf.Clamp(Zoom / factor, MinZoom, MaxZoom);
            Place();
            if (hadAnchor && TryGroundPoint(anchorScreen, out var after)) Focus += before - after;
            Clamp();
            Place();
        }

        public void AddTrauma(float amount)
        {
            if (Match.DebugFlags.Has("-mb-no-shake")) return;
            _trauma = Mathf.Min(1f, _trauma + amount * ShakeScale);
        }

        /// <summary>Scales camera shake; the Reduced motion setting lowers it.</summary>
        public float ShakeScale { get; set; } = 1f;

        /// <summary>Jumps the view to look at <paramref name="point"/> (minimap taps).</summary>
        public void FocusOn(Vector3 point)
        {
            Focus = new Vector3(point.x, 0f, point.z);
            Clamp();
            Place();
        }

        /// <summary>Eases the view towards <paramref name="point"/>, for the menu's drifting camera.</summary>
        public void Glide(Vector3 point, float zoom, float dt, float rate = 0.6f)
        {
            var k = 1f - Mathf.Exp(-dt * rate);
            Focus = Vector3.Lerp(Focus, new Vector3(point.x, 0f, point.z), k);
            Zoom = Mathf.Clamp(Mathf.Lerp(Zoom, zoom, k), MinZoom, MaxZoom);
            Clamp();
        }

        /// <summary>Call once per frame after input: places the camera and applies shake.</summary>
        public void Apply(float unscaledDeltaTime)
        {
            _trauma = Mathf.Max(0f, _trauma - TraumaDecay * unscaledDeltaTime);
            _noiseTime += unscaledDeltaTime * 25f;
            Place();
            if (_trauma <= 0f) return;
            var strength = _trauma * _trauma;
            var t = _camera.transform;
            t.position += (t.right * Noise(0) + t.up * Noise(1)) * (0.05f * strength * Zoom);
            t.rotation *= Quaternion.Euler(0f, 0f, Noise(2) * 1.2f * strength);
        }

        private void Place()
        {
            var rotation = Quaternion.Euler(Pitch, Yaw, 0f);
            _camera.orthographicSize = Zoom;
            _camera.transform.SetPositionAndRotation(Focus - rotation * Vector3.forward * Distance, rotation);
        }

        private void Clamp()
        {
            Focus = new Vector3(Mathf.Clamp(Focus.x, -_halfSize, _halfSize), 0f, Mathf.Clamp(Focus.z, -_halfSize, _halfSize));
        }

        private float Noise(int channel) => (Mathf.PerlinNoise(_noiseTime, channel * 10.3f) - 0.5f) * 2f;
    }
}
