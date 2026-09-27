using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Lighting environment built at runtime, so nothing depends on baked lighting data:
    /// a hemisphere ambient (cool sky above, warm earth below, the 3d_astra palette) written into
    /// the ambient probe, a small procedural reflection cubemap that metal and glass reflect, fog,
    /// and a shadow distance long enough for the orthographic camera.
    /// </summary>
    public sealed class Atmosphere : IDisposable
    {
        public static readonly Color Sky = FromHex("#c0d9d8");
        public static readonly Color Earth = FromHex("#736145");
        public static readonly Color Haze = FromHex("#43565b");

        private const float AmbientStrength = 0.72f;

        private readonly Cubemap _reflection;
        private readonly UniversalRenderPipelineAsset _pipeline;
        private readonly float _originalShadowDistance;
        private readonly float _originalDepthBias;
        private readonly float _originalNormalBias;
        private readonly int _originalMsaa;
        private readonly float _originalScale;
        private readonly int _originalShadowResolution;
        private readonly bool _originalSrpBatcher;
        private readonly Match.ShadowLevel _shadows;
        private readonly int _originalCascades;
        private readonly float _originalBorder;
        private readonly UpscalingFilterSelection _originalUpscaling;
        private static readonly Vector2[] Corners = { new(0f, 0f), new(1f, 0f), new(0f, 1f), new(1f, 1f) };

        /// <summary>Highest thing that casts a shadow: aircraft fly up to 22 m, the flare stack is 20 m.</summary>
        /// <summary>Highest anything is drawn (bombers fly at up to 46 m): the near plane and shadows reach it.</summary>
        private const float CasterCeiling = 52f;

        /// <summary>Fade band at the edge of the shadow range, kept just off screen.</summary>
        private const float ShadowBorder = 0.05f;
        private readonly Light _sun;
        private readonly LightShadows _originalSunShadows;

        public Atmosphere(Match.GraphicsOptions options = null)
        {
            options ??= Match.GraphicsOptions.For(Match.GraphicsQuality.High);
            _shadows = options.Shadows;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = Sky * AmbientStrength;
            RenderSettings.ambientEquatorColor = Color.Lerp(Sky, Earth, 0.5f) * AmbientStrength;
            RenderSettings.ambientGroundColor = Earth * AmbientStrength;
            // Spherical harmonics are linear-space; the palette is authored in sRGB.
            RenderSettings.ambientProbe = Hemisphere(Sky.linear * AmbientStrength, Earth.linear * AmbientStrength);

            _reflection = BuildReflection(32);
            if (!Match.DebugFlags.Has("-mb-no-reflection"))
            {
                RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
                RenderSettings.customReflectionTexture = _reflection;
            }
            RenderSettings.reflectionIntensity = 1f;

            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = Haze;
            RenderSettings.fogStartDistance = 100f;
            RenderSettings.fogEndDistance = 220f;

            // Shadow and edge quality: a tight shadow range keeps texels small, extra bias stops
            // acne flickering on hulls as they move, and MSAA stops edges crawling.
            _pipeline = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (_pipeline != null)
            {
                _originalShadowDistance = _pipeline.shadowDistance;
                _originalDepthBias = _pipeline.shadowDepthBias;
                _originalNormalBias = _pipeline.shadowNormalBias;
                _originalMsaa = _pipeline.msaaSampleCount;
                _originalSrpBatcher = _pipeline.useSRPBatcher;
                // On OpenGL ES the SRP Batcher intermittently drew vehicles with the previous frame's
                // (or an older) transform: turrets flashed back to an old pose and moving tanks
                // stuttered. Measured on the emulator: 50-60 flashes per 14 s with it, none without.
                // Vulkan and Metal keep it for the CPU savings.
                if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.OpenGLES3) _pipeline.useSRPBatcher = false;
                _pipeline.shadowDepthBias = 1.6f;
                _pipeline.shadowNormalBias = 1.3f;
                // Resolution, anti-aliasing and shadow map size are the big GPU levers on phones.
                _pipeline.msaaSampleCount = Match.DebugFlags.Has("-mb-no-msaa") ? 1 : options.AntiAliasing;
                _originalScale = _pipeline.renderScale;
                // Battery saver renders a little smaller as well as slower.
                _pipeline.renderScale = options.RenderScale / 100f * (Match.MatchSettings.SavingBattery ? 0.85f : 1f);
                _originalUpscaling = _pipeline.upscalingFilter;
                // FSR 1 sharpens the upscale where the GPU supports it (it falls back to bilinear).
                _pipeline.upscalingFilter = _pipeline.renderScale < 0.99f ? UpscalingFilterSelection.FSR : UpscalingFilterSelection.Auto;
                _originalShadowResolution = _pipeline.mainLightShadowmapResolution;
                _pipeline.mainLightShadowmapResolution = options.Shadows == Match.ShadowLevel.High ? 2048 : 1024;
                // One shadow map: cascades fix perspective aliasing, which an orthographic view does not have.
                _originalCascades = _pipeline.shadowCascadeCount;
                _pipeline.shadowCascadeCount = 1;
                _originalBorder = _pipeline.cascadeBorder;
                _pipeline.cascadeBorder = ShadowBorder;
                _pipeline.shadowDistance = 110f;
            }

            // Off: no shadow pass at all. Low: hard edges. Medium and High: soft (filtered) edges.
            foreach (var light in Object.FindObjectsByType<Light>())
                if (light.type == LightType.Directional) _sun = light;
            if (_sun != null)
            {
                _originalSunShadows = _sun.shadows;
                _sun.shadows = options.Shadows switch
                {
                    Match.ShadowLevel.Off => LightShadows.None,
                    Match.ShadowLevel.Low => LightShadows.Hard,
                    _ => LightShadows.Soft,
                };
                // Four taps on phones (Unity's mobile balance); nine on desktop High.
                var data = _sun.GetUniversalAdditionalLightData();
                if (data != null)
                    data.softShadowQuality = options.Shadows == Match.ShadowLevel.High && !Application.isMobilePlatform
                        ? SoftShadowQuality.Medium
                        : SoftShadowQuality.Low;
            }
        }

        /// <summary>
        /// Fits the one shadow map to what is on screen, every frame. URP wraps the shadow map
        /// round the view between the near plane and the shadow distance, and fades shadows by
        /// straight-line distance from the camera. With the camera 60 m back, a fixed range wasted
        /// most of the map on empty air when zoomed in and lost the corners when zoomed out. So:
        /// the near plane moves up to just above the highest caster at the bottom of the screen,
        /// and the range reaches exactly the farthest visible ground corner (fade band beyond it).
        /// Zoomed in, the same map covers far less ground and edges come out about twice as sharp.
        /// </summary>
        public void FitShadows(Camera camera)
        {
            if (_pipeline == null || camera == null || _shadows == Match.ShadowLevel.Off) return;
            var t = camera.transform;
            var position = t.position;
            var forward = t.forward;
            var farthest = 0f;
            var nearest = float.MaxValue;
            foreach (var corner in Corners)
            {
                var ray = camera.ViewportPointToRay(corner);
                if (ray.direction.y > -0.01f) continue;
                var ground = ray.origin + ray.direction * (-ray.origin.y / ray.direction.y);
                farthest = Mathf.Max(farthest, (ground - position).sqrMagnitude);
                var top = ray.origin + ray.direction * ((CasterCeiling - ray.origin.y) / ray.direction.y);
                nearest = Mathf.Min(nearest, Vector3.Dot(top - position, forward));
            }
            if (nearest == float.MaxValue) return;
            var near = Mathf.Max(0.3f, nearest - 1f);
            if (Mathf.Abs(camera.nearClipPlane - near) > 0.25f) camera.nearClipPlane = near;
            var distance = Mathf.Sqrt(farthest) / (1f - ShadowBorder) + 1f;
            if (Mathf.Abs(distance - _pipeline.shadowDistance) > 0.5f) _pipeline.shadowDistance = distance;
        }

        public void Dispose()
        {
            if (_pipeline != null)
            {
                _pipeline.shadowDistance = _originalShadowDistance;
                _pipeline.shadowDepthBias = _originalDepthBias;
                _pipeline.shadowNormalBias = _originalNormalBias;
                _pipeline.msaaSampleCount = _originalMsaa;
                _pipeline.renderScale = _originalScale;
                _pipeline.mainLightShadowmapResolution = _originalShadowResolution;
                _pipeline.shadowCascadeCount = _originalCascades;
                _pipeline.cascadeBorder = _originalBorder;
                _pipeline.upscalingFilter = _originalUpscaling;
                _pipeline.useSRPBatcher = _originalSrpBatcher;
            }
            if (_sun != null) _sun.shadows = _originalSunShadows;
            if (_reflection != null) Object.Destroy(_reflection);
        }

        /// <summary>
        /// Weather mood: scales and tints the ambient light and pulls the fog in. The camera's
        /// background follows the fog so the horizon never shows a seam.
        /// </summary>
        public void SetMood(float light, Color cast, Color fog, float fogStart, float fogEnd)
        {
            RenderSettings.ambientProbe = Hemisphere((Sky * cast).linear * AmbientStrength * light,
                (Earth * cast).linear * AmbientStrength * light);
            RenderSettings.fogColor = fog;
            RenderSettings.fogStartDistance = fogStart;
            RenderSettings.fogEndDistance = fogEnd;
            if (Camera.main != null) Camera.main.backgroundColor = fog;
        }

        /// <summary>
        /// Sky/ground gradient as spherical harmonics: the mean colour plus opposite lobes up and
        /// down, whose even terms cancel and leave a smooth vertical gradient.
        /// </summary>
        private static SphericalHarmonicsL2 Hemisphere(Color sky, Color ground)
        {
            var sh = new SphericalHarmonicsL2();
            sh.AddAmbientLight((sky + ground) * 0.5f);
            var half = (sky - ground) * 0.5f;
            sh.AddDirectionalLight(Vector3.up, half, 1f);
            sh.AddDirectionalLight(Vector3.down, half * -1f, 1f);
            return sh;
        }

        private static Cubemap BuildReflection(int size)
        {
            var cube = new Cubemap(size, TextureFormat.RGBAHalf, true) { name = "Sky Reflection" };
            var pixels = new Color[size * size];
            foreach (CubemapFace face in Enum.GetValues(typeof(CubemapFace)))
            {
                if (face == CubemapFace.Unknown) continue;
                for (var y = 0; y < size; y++)
                for (var x = 0; x < size; x++)
                {
                    var u = (x + 0.5f) / size * 2f - 1f;
                    var v = (y + 0.5f) / size * 2f - 1f;
                    var up = Direction(face, u, v).normalized.y;
                    var colour = up > 0f
                        ? Color.Lerp(Color.Lerp(Sky, Color.white, 0.2f), Sky * 1.15f, up)
                        : Color.Lerp(Color.Lerp(Sky, Earth, 0.6f), Earth * 0.6f, -up);
                    pixels[y * size + x] = colour.linear;
                }
                cube.SetPixels(pixels, face);
            }
            cube.Apply(true, false);
            return cube;
        }

        private static Vector3 Direction(CubemapFace face, float u, float v) => face switch
        {
            CubemapFace.PositiveX => new Vector3(1f, -v, -u),
            CubemapFace.NegativeX => new Vector3(-1f, -v, u),
            CubemapFace.PositiveY => new Vector3(u, 1f, v),
            CubemapFace.NegativeY => new Vector3(u, -1f, -v),
            CubemapFace.PositiveZ => new Vector3(u, -v, 1f),
            _ => new Vector3(-u, -v, -1f),
        };

        private static Color FromHex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.magenta;
    }
}
