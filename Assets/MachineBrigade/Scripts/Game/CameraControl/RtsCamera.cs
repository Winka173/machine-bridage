using UnityEngine;

namespace MachineBrigade.Game.CameraControl
{
    /// <summary>
    /// Tilted battlefield camera. Panning is world-anchored (the ground under the finger
    /// stays under the finger), zoom keeps the pinch centre fixed, and the focus is clamped
    /// to the map so every corner stays reachable (V2 R03). Shake is applied on top.
    /// </summary>
    public sealed class RtsCamera
    {
        private const float Pitch = 55f;
        private const float MinDistance = 16f;
        private const float MaxDistance = 110f;
        private const float TraumaDecay = 1.4f;

        private readonly Camera _camera;
        private readonly float _halfSize;
        private float _trauma;
        private float _noiseTime;

        public RtsCamera(Camera camera, float halfSize, Vector3 focus, float distance = 55f)
        {
            _camera = camera;
            _halfSize = halfSize;
            _camera.fieldOfView = 40f;
            _camera.nearClipPlane = 0.5f;
            _camera.farClipPlane = 700f;
            Focus = focus;
            Distance = Mathf.Clamp(distance, MinDistance, MaxDistance);
            Clamp();
            Place();
        }

        public Camera Camera => _camera;

        /// <summary>Point on the ground the camera orbits.</summary>
        public Vector3 Focus { get; private set; }

        public float Distance { get; private set; }

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

        public void Zoom(float factor, Vector2 anchorScreen)
        {
            if (factor <= 0f) return;
            Place();
            var hadAnchor = TryGroundPoint(anchorScreen, out var before);
            Distance = Mathf.Clamp(Distance / factor, MinDistance, MaxDistance);
            Place();
            if (hadAnchor && TryGroundPoint(anchorScreen, out var after)) Focus += before - after;
            Clamp();
            Place();
        }

        public void AddTrauma(float amount) => _trauma = Mathf.Min(1f, _trauma + amount);

        /// <summary>Call once per frame after input: places the camera and applies shake.</summary>
        public void Apply(float unscaledDeltaTime)
        {
            _trauma = Mathf.Max(0f, _trauma - TraumaDecay * unscaledDeltaTime);
            _noiseTime += unscaledDeltaTime * 25f;
            Place();
            if (_trauma <= 0f) return;
            var strength = _trauma * _trauma;
            var offset = new Vector3(Noise(0), Noise(1), Noise(2)) * (0.9f * strength * Distance / 50f);
            _camera.transform.position += offset;
            _camera.transform.rotation *= Quaternion.Euler(Noise(3) * 2f * strength, Noise(4) * 2f * strength, 0f);
        }

        private void Place()
        {
            var rotation = Quaternion.Euler(Pitch, 0f, 0f);
            _camera.transform.SetPositionAndRotation(Focus - rotation * Vector3.forward * Distance, rotation);
        }

        private void Clamp()
        {
            Focus = new Vector3(Mathf.Clamp(Focus.x, -_halfSize, _halfSize), 0f, Mathf.Clamp(Focus.z, -_halfSize, _halfSize));
        }

        private float Noise(int channel) => (Mathf.PerlinNoise(_noiseTime, channel * 10.3f) - 0.5f) * 2f;
    }
}
