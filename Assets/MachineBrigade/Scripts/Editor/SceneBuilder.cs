using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Generates the match scene from code. The scene only holds a camera, the sun, the
    /// post-processing volume and the <see cref="MatchRunner"/>; everything else is spawned at
    /// runtime from data, so the scene file stays tiny and easy to review. Also configures the
    /// post-processing profile (ACES tonemapping, bloom, exposure) to match the 3d_astra look.
    /// <c>Unity -batchmode -quit -projectPath . -executeMethod MachineBrigade.Editor.SceneBuilder.Build</c>
    /// </summary>
    public static class SceneBuilder
    {
        public const string ScenePath = "Assets/MachineBrigade/Scenes/Sandbox.unity";
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";

        [MenuItem("Machine Brigade/Rebuild Sandbox Scene")]
        public static void Build()
        {
            if (!AssetDatabase.IsValidFolder("Assets/MachineBrigade/Scenes"))
                AssetDatabase.CreateFolder("Assets/MachineBrigade", "Scenes");
            var profile = ConfigureProfile();

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var cameraObject = new GameObject("Main Camera") { tag = "MainCamera" };
            var camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Atmosphere.Haze;
            camera.orthographic = true;
            cameraObject.AddComponent<AudioListener>();
            var cameraData = cameraObject.AddComponent<UniversalAdditionalCameraData>();
            cameraData.renderPostProcessing = true;
            cameraData.antialiasing = AntialiasingMode.FastApproximateAntialiasing;
            cameraObject.transform.SetPositionAndRotation(new Vector3(-20f, 45f, -60f), Quaternion.Euler(52f, -45f, 0f));

            // Warm key light from the 3d_astra sun direction (three.js offset -25, 55, 20).
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.35f;
            sun.color = new Color(1f, 0.914f, 0.792f); // #ffe9ca, Riverlands
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.85f;
            sun.transform.rotation = Quaternion.LookRotation(new Vector3(25f, -55f, 20f));

            var volume = new GameObject("Post Processing").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = profile;

            new GameObject("Match").AddComponent<MatchRunner>();

            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log($"[SceneBuilder] Wrote {ScenePath} and set it as the only build scene.");
        }

        private static VolumeProfile ConfigureProfile()
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }

            var tonemapping = Get<Tonemapping>(profile);
            tonemapping.mode.Override(TonemappingMode.ACES);

            var bloom = Get<Bloom>(profile);
            bloom.threshold.Override(1.0f);
            bloom.intensity.Override(0.45f);
            bloom.scatter.Override(0.6f);
            // No single pixel may carry enough energy to flash a whole vehicle.
            bloom.clamp.Override(6f);

            var colour = Get<ColorAdjustments>(profile);
            colour.postExposure.Override(0.35f);
            colour.contrast.Override(10f);
            colour.saturation.Override(0f);

            var vignette = Get<Vignette>(profile);
            vignette.intensity.Override(0.18f);
            vignette.smoothness.Override(0.45f);

            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        private static T Get<T>(VolumeProfile profile) where T : VolumeComponent
        {
            if (!profile.TryGet<T>(out var component))
            {
                component = profile.Add<T>(true);
                AssetDatabase.AddObjectToAsset(component, profile);
            }
            component.active = true;
            return component;
        }
    }
}
