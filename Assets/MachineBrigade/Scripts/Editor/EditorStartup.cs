using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Makes the project ready to press Play: the game's scene is the play-mode start scene (so
    /// Play works from whatever scene is open), and a fresh editor session with nothing open
    /// opens it. Everything else (menu, battles, settings) is built at run time.
    /// </summary>
    [InitializeOnLoad]
    internal static class EditorStartup
    {
        private const string GameScene = "Assets/MachineBrigade/Scenes/Sandbox.unity";

        static EditorStartup()
        {
            EditorApplication.delayCall += Setup;
        }

        private static void Setup()
        {
            if (Application.isBatchMode) return;
            var scene = AssetDatabase.LoadAssetAtPath<SceneAsset>(GameScene);
            if (scene == null) return;
            EditorSceneManager.playModeStartScene = scene;
            var active = EditorSceneManager.GetActiveScene();
            var untitled = string.IsNullOrEmpty(active.path) && !active.isDirty && active.rootCount <= 2;
            if (untitled && !EditorApplication.isPlayingOrWillChangePlaymode) EditorSceneManager.OpenScene(GameScene);
        }

        [MenuItem("Machine Brigade/Open Game Scene")]
        private static void Open()
        {
            if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) EditorSceneManager.OpenScene(GameScene);
        }
    }
}
