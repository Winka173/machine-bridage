using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Command-line builds. The editor must not have the project open while these run:
    /// <c>Unity -batchmode -quit -projectPath . -buildTarget Android -executeMethod MachineBrigade.Editor.BuildScripts.BuildAndroidDevApk</c>
    /// A failed build exits with code 1 so scripts and CI can stop on it.
    /// </summary>
    public static class BuildScripts
    {
        [MenuItem("Machine Brigade/Build/Android Dev APK")]
        public static void BuildAndroidDevApk() =>
            BuildAndroid("Builds/Android/MachineBrigade-dev.apk", appBundle: false, BuildOptions.Development);

        /// <summary>
        /// Store bundle. Until a release keystore is configured this is signed with the debug key
        /// and is only good for local checks, not for upload.
        /// </summary>
        [MenuItem("Machine Brigade/Build/Android Release AAB")]
        public static void BuildAndroidReleaseAab() =>
            BuildAndroid("Builds/Android/MachineBrigade.aab", appBundle: true, BuildOptions.None);

        /// <summary>Generates the Xcode project; compiling and signing it needs a Mac.</summary>
        [MenuItem("Machine Brigade/Build/iOS Xcode Project")]
        public static void BuildIosXcodeProject()
        {
            ProjectSetup.Apply();
            Run(new BuildPlayerOptions
            {
                scenes = EnabledScenes(),
                locationPathName = "Builds/iOS",
                target = BuildTarget.iOS,
                targetGroup = BuildTargetGroup.iOS,
                options = BuildOptions.None,
            });
        }

        private static void BuildAndroid(string path, bool appBundle, BuildOptions options)
        {
            // Every build starts from the canonical settings, so a stray editor change cannot ship.
            ProjectSetup.Apply();
            EditorUserBuildSettings.buildAppBundle = appBundle;
            Run(new BuildPlayerOptions
            {
                scenes = EnabledScenes(),
                locationPathName = path,
                target = BuildTarget.Android,
                targetGroup = BuildTargetGroup.Android,
                options = options,
            });
        }

        private static void Run(BuildPlayerOptions buildOptions)
        {
            var summary = BuildPipeline.BuildPlayer(buildOptions).summary;
            Debug.Log($"[Build] {summary.result}: {summary.outputPath} " +
                      $"({summary.totalSize / (1024 * 1024)} MB, {summary.totalTime:mm\\:ss})");
            if (Application.isBatchMode && summary.result != BuildResult.Succeeded)
                EditorApplication.Exit(1);
        }

        private static string[] EnabledScenes() =>
            EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
    }
}
