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

        /// <summary>The fixed tilt in degrees (prompt 33 L1: the outer ring is sized from it, Views.CameraFrame).</summary>
        public const float TiltDegrees = Pitch;

        /// <summary>Whether the player can turn the view (no: the yaw is fixed per map shape).</summary>
        public const bool Rotates = false;

        /// <summary>The square maps' yaw: their south-west to north-east battle axis across the screen.</summary>
        public const float SquareYaw = -45f;

        /// <summary>
        /// A long battlefield's (prompt 17 A.4): looking west, so its south-to-north axis runs across the landscape
        /// screen, the attacker on the left as on the square maps.
        /// </summary>
        public const float LongYaw = -90f;

        private readonly float _yaw = SquareYaw;

        /// <summary>The camera's yaw in degrees (the minimap turns with it).</summary>
        public float Yaw => _yaw;
        /// <summary>
        /// How far back along its view the camera sits. The view is orthographic, so this changes
        /// nothing on screen; it only has to clear the highest thing drawn. At 60 m, aircraft near the
        /// bottom of a zoomed-out view (bombers at 46 m, a banking wing) fell behind the camera and
        /// were cut away. The near plane is pushed up to the tallest object (Atmosphere), so the
        /// shadow range is unchanged.
        /// </summary>
        public const float Distance = 130f;

        /// <summary>Depth added to everything by standing further back than the original 60 m (fog distances add it).</summary>
        public const float DepthShift = Distance - 60f;
        private const float MinZoom = 9f;
        private const float DefaultMaxZoom = 42f;

        /// <summary>The furthest the player zooms out on a square map (a long one: MatchRunner.LongMaxZoom).</summary>
        public const float PlayerMaxZoom = DefaultMaxZoom;

        /// <summary>Furthest the view zooms out (raised only by the -mb-overview device check).</summary>
        public float MaxZoom { get; set; } = DefaultMaxZoom;
        private const float TraumaDecay = 1.4f;

        private readonly Camera _camera;

        /// <summary>The map's own rectangle (a long battlefield's is not centred on the origin).</summary>
        private readonly Vector2 _mapMin, _mapMax;

        /// <summary>Where the view may centre (the play area and a margin; the whole map by default).</summary>
        private Vector2 _min, _max;

        /// <summary>How far past the play area's edge the view may go, so the edge itself shows.</summary>
        private const float AreaMargin = 12f;

        /// <summary>Keeps the view to a play area (null: the whole map again).</summary>
        public void SetArea(Vector2? min, Vector2? max)
        {
            if (min is { } a && max is { } b)
            {
                _min = new Vector2(Mathf.Max(_mapMin.x, a.x - AreaMargin), Mathf.Max(_mapMin.y, a.y - AreaMargin));
                _max = new Vector2(Mathf.Min(_mapMax.x, b.x + AreaMargin), Mathf.Min(_mapMax.y, b.y + AreaMargin));
            }
            else
            {
                _min = _mapMin;
                _max = _mapMax;
            }
            Clamp();
        }
        private float _trauma;
        private float _noiseTime;

        public RtsCamera(Camera camera, float halfSize, Vector3 focus, float zoom = 19f)
            : this(camera, new Vector2(-halfSize, -halfSize), new Vector2(halfSize, halfSize), focus, zoom)
        {
        }

        /// <summary>Over a map's rectangle (<paramref name="mapMin"/> to <paramref name="mapMax"/>), looking along <paramref name="yaw"/>.</summary>
        public RtsCamera(Camera camera, Vector2 mapMin, Vector2 mapMax, Vector3 focus, float zoom = 19f, float yaw = SquareYaw)
        {
            _camera = camera;
            _yaw = yaw;
            _mapMin = mapMin;
            _mapMax = mapMax;
            _min = mapMin;
            _max = mapMax;
            _camera.orthographic = true;
            _camera.nearClipPlane = 1f;
            _camera.farClipPlane = 320f + DepthShift;
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

        /// <summary>
        /// Camera shake is switched off for now (the user found it read as stutter); explosions,
        /// shots and cinematic moments still call <see cref="AddTrauma"/>, so turning this back on
        /// restores them all.
        /// </summary>
        public static bool ShakeEnabled { get; set; }

        public void AddTrauma(float amount)
        {
            if (!ShakeEnabled || Match.DebugFlags.Has("-mb-no-shake")) return;
            _trauma = Mathf.Min(1f, _trauma + amount * ShakeScale * Fatigue);
        }

        /// <summary>
        /// Prompt 34 L5: the one shake left on while <see cref="ShakeEnabled"/> is off: T4+ blasts and shots near the view
        /// (Effects.TierFx.Shake). Scaled by the screen shake setting (<see cref="ShakeScale"/>, off / low / full) and never
        /// past <paramref name="cap"/> in all, so a salvo of big shells does not pile up into a jolt.
        /// </summary>
        public void AddTierTrauma(float amount, float cap)
        {
            if (amount <= 0f || Match.DebugFlags.Has("-mb-no-shake")) return;
            var add = amount * ShakeScale * Fatigue;
            if (add <= 0f || _trauma >= cap) return;
            _trauma = Mathf.Min(Mathf.Min(1f, cap), _trauma + add);
        }

        /// <summary>Scales camera shake; the Reduced motion setting lowers it.</summary>
        public float ShakeScale { get; set; } = 1f;

        /// <summary>
        /// MVA W2-B (spec part AK): a boss barrage cannot shake the view on and on. After <see cref="FatigueAfter"/> s of
        /// unbroken shake, new shake counts less (down to 35 % over the next 3 s); it recovers twice as fast once the view is still.
        /// </summary>
        internal float Fatigue => 1f - 0.65f * Mathf.Clamp01((_shaking - FatigueAfter) / 3f);

        internal const float FatigueAfter = 2f;

        private float _shaking;

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

        private Vector3 _followVelocity;

        // Play-test 6: a story shot (a boss's entrance, change or fall) borrows the player's view and gives it back.
        private bool _held;
        private Vector3 _heldFocus;
        private float _heldZoom, _returning;

        /// <summary>A story shot holds the player's view, to give it back when the shot ends.</summary>
        public bool Held => _held;

        /// <summary>Remembers the player's view before a story shot; while one is held a later shot keeps the first view.</summary>
        public void Hold()
        {
            if (_held) return;
            _held = true;
            _heldFocus = Focus;
            _heldZoom = Zoom;
            _returning = 0f;
        }

        /// <summary>The player moved the view during the shot: the view is theirs, nothing is given back.</summary>
        public void Release() => _held = false;

        /// <summary>
        /// Eases back to the held view (about a second; exactly there after two at most); true once it is back and
        /// the hold is over.
        /// </summary>
        public bool ReturnHeld(float dt)
        {
            if (!_held) return true;
            _returning += Mathf.Max(0f, dt);
            var k = 1f - Mathf.Exp(-Mathf.Max(0f, dt) * 4f);
            Focus = Vector3.Lerp(Focus, _heldFocus, k);
            Zoom = Mathf.Clamp(Mathf.Lerp(Zoom, _heldZoom, k), MinZoom, MaxZoom);
            if (_returning >= 2f || ((Focus - _heldFocus).sqrMagnitude < 0.04f && Mathf.Abs(Zoom - _heldZoom) < 0.05f))
            {
                Focus = _heldFocus;
                Zoom = Mathf.Clamp(_heldZoom, MinZoom, MaxZoom);
                _held = false;
            }
            Clamp();
            return !_held;
        }

        /// <summary>
        /// Follows <paramref name="point"/> like a critically damped spring: when the point moves
        /// on, the camera's speed changes smoothly instead of lurching as an exponential chase does.
        /// </summary>
        public void Follow(Vector3 point, float dt, float smoothTime = 1.6f)
        {
            if (dt <= 0f) return;
            Focus = Vector3.SmoothDamp(Focus, new Vector3(point.x, 0f, point.z), ref _followVelocity, smoothTime, 14f, dt);
            Clamp();
        }

        /// <summary>Forgets the follow speed (after the player moved the view by hand).</summary>
        public void StopFollowing() => _followVelocity = Vector3.zero;

        /// <summary>Call once per frame after input: places the camera and applies shake.</summary>
        public void Apply(float unscaledDeltaTime)
        {
            _trauma = Mathf.Max(0f, _trauma - TraumaDecay * unscaledDeltaTime);
            _shaking = _trauma > 0.15f ? Mathf.Min(_shaking + unscaledDeltaTime, FatigueAfter + 4f) : Mathf.Max(0f, _shaking - 2f * unscaledDeltaTime);
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
            var rotation = Quaternion.Euler(Pitch, _yaw, 0f);
            _camera.orthographicSize = Zoom;
            _camera.transform.SetPositionAndRotation(Focus - rotation * Vector3.forward * Distance, rotation);
        }

        private void Clamp()
        {
            Focus = new Vector3(Mathf.Clamp(Focus.x, _min.x, _max.x), 0f, Mathf.Clamp(Focus.z, _min.y, _max.y));
        }

        private float Noise(int channel) => (Mathf.PerlinNoise(_noiseTime, channel * 10.3f) - 0.5f) * 2f;
    }
}
