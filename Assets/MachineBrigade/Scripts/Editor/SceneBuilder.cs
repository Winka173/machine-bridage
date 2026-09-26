using MachineBrigade.Game.Match;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Generates the match scene from code. The scene only holds a camera, the sun, the
    /// post-processing volume and the <see cref="MatchRunner"/>; everything else is spawned
    /// at runtime from data, so the scene file stays tiny and easy to review.
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

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var cameraObject = new GameObject("Main Camera") { tag = "MainCamera" };
            var camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.Skybox;
            cameraObject.AddComponent<AudioListener>();
            var cameraData = cameraObject.AddComponent<UniversalAdditionalCameraData>();
            cameraData.renderPostProcessing = true;
            cameraObject.transform.SetPositionAndRotation(new Vector3(-40f, 45f, -70f), Quaternion.Euler(55f, 0f, 0f));

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.25f;
            sun.color = new Color(1f, 0.95f, 0.87f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(50f, -35f, 0f);

            var volume = new GameObject("Post Processing").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (volume.sharedProfile == null) Debug.LogWarning($"[SceneBuilder] Missing volume profile at {ProfilePath}.");

            new GameObject("Match").AddComponent<MatchRunner>();

            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log($"[SceneBuilder] Wrote {ScenePath} and set it as the only build scene.");
        }
    }
}
