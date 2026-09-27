using UnityEditor;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Import settings for the flipbook sheets in Resources/Textures/Fx. They hold data, not
    /// colour (heat, smoke light, coverage; see Flipbook.shader), so they are linear, keep alpha
    /// exactly as authored and clamp at their edges. Mobile gets ASTC 5x5 (about 0.9 MB for a
    /// 1024 sheet with mips); desktop BC7.
    /// </summary>
    public sealed class FxTextureImport : AssetPostprocessor
    {
        private const string Folder = "Assets/MachineBrigade/Resources/Textures/Fx/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Folder)) return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = false;
            importer.mipmapEnabled = true;
            importer.mipmapFilter = TextureImporterMipFilter.BoxFilter;
            importer.wrapMode = UnityEngine.TextureWrapMode.Clamp;
            importer.filterMode = UnityEngine.FilterMode.Bilinear;
            importer.anisoLevel = 0;
            importer.maxTextureSize = 1024;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;

            foreach (var platform in new[] { "Android", "iPhone" })
            {
                var settings = importer.GetPlatformTextureSettings(platform);
                settings.overridden = true;
                settings.maxTextureSize = 1024;
                settings.format = TextureImporterFormat.ASTC_5x5;
                settings.compressionQuality = 50;
                importer.SetPlatformTextureSettings(settings);
            }
        }
    }
}
