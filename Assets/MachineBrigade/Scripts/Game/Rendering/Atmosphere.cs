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
        private readonly bool _originalSrpBatcher;

        public Atmosphere(float shadowDistance = 110f)
        {
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
                _pipeline.shadowDistance = shadowDistance;
                _pipeline.shadowDepthBias = 1.6f;
                _pipeline.shadowNormalBias = 1.3f;
                _pipeline.msaaSampleCount = Match.DebugFlags.Has("-mb-no-msaa") ? 1 : Application.isMobilePlatform ? 2 : 4;
            }
        }

        public void Dispose()
        {
            if (_pipeline != null)
            {
                _pipeline.shadowDistance = _originalShadowDistance;
                _pipeline.shadowDepthBias = _originalDepthBias;
                _pipeline.shadowNormalBias = _originalNormalBias;
                _pipeline.msaaSampleCount = _originalMsaa;
                _pipeline.useSRPBatcher = _originalSrpBatcher;
            }
            if (_reflection != null) Object.Destroy(_reflection);
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
