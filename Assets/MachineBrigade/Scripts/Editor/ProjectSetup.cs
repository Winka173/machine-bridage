using UnityEditor;
using UnityEditor.Build;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Applies the project-wide player settings from code, so they are reviewable in git
    /// and reproducible from the command line:
    /// <c>Unity -batchmode -quit -projectPath . -executeMethod MachineBrigade.Editor.ProjectSetup.Apply</c>
    /// </summary>
    public static class ProjectSetup
    {
        /// <summary>One identifier on both stores (Sticky-Wall's Android and iOS ids drifted apart).</summary>
        public const string BundleId = "com.winka.machinebrigade";

        [MenuItem("Machine Brigade/Apply Project Settings")]
        public static void Apply()
        {
            PlayerSettings.companyName = "Winka";
            PlayerSettings.productName = "Machine Brigade";
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, BundleId);
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, BundleId);

            // Landscape only: the battlefield and the deck bar are laid out for a wide screen.
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.AutoRotation;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;

            // Store builds require 64-bit; IL2CPP is also the faster runtime on phones.
            // Unity 6.6 dropped Android x86_64, so emulators run this build via ARM translation.
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.iOS, ScriptingImplementation.IL2CPP);

            // Phones use Vulkan. Under the emulator's ARM translation Vulkan presents only black
            // frames, so emulator images are denied Vulkan and fall back to OpenGL ES 3.
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                new[] { GraphicsDeviceType.Vulkan, GraphicsDeviceType.OpenGLES3 });
            PlayerSettings.Android.androidVulkanDeviceFilterListAsset = EmulatorVulkanDenyList();

            AssetDatabase.SaveAssets();
            Debug.Log($"[ProjectSetup] Applied player settings for {BundleId}.");
        }

        private const string VulkanFilterPath = "Assets/MachineBrigade/Settings/VulkanDeviceFilters.asset";

        private static VulkanDeviceFilterLists EmulatorVulkanDenyList()
        {
            var lists = AssetDatabase.LoadAssetAtPath<VulkanDeviceFilterLists>(VulkanFilterPath);
            if (lists == null)
            {
                if (!AssetDatabase.IsValidFolder("Assets/MachineBrigade/Settings"))
                    AssetDatabase.CreateFolder("Assets/MachineBrigade", "Settings");
                lists = new VulkanDeviceFilterLists();
                AssetDatabase.CreateAsset(lists, VulkanFilterPath);
            }

            lists.vulkanDeviceDenyFilters = new[]
            {
                new VulkanDeviceFilterData { productName = "sdk_gphone.*" },
            };
            EditorUtility.SetDirty(lists);
            return lists;
        }
    }
}
