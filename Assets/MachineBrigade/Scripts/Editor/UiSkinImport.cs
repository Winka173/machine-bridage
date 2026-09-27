using UnityEditor;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Import settings for the menu skin in Resources/UI/Skin (Tools/art/ui_skin.py): white shapes
    /// and fades tinted by the stylesheet, drawn at their own size or 9-sliced, so they stay
    /// uncompressed with no mipmaps (a soft or blocky chamfer shows at once). The hatch tiles;
    /// everything else clamps at its edges.
    /// </summary>
    public sealed class UiSkinImport : AssetPostprocessor
    {
        private const string Folder = "Assets/MachineBrigade/Resources/UI/Skin/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Folder)) return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.wrapMode = assetPath.Contains("hatch") ? UnityEngine.TextureWrapMode.Repeat : UnityEngine.TextureWrapMode.Clamp;
            importer.filterMode = UnityEngine.FilterMode.Bilinear;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            foreach (var platform in new[] { "Android", "iPhone" })
            {
                var settings = importer.GetPlatformTextureSettings(platform);
                settings.overridden = true;
                settings.format = TextureImporterFormat.RGBA32;
                importer.SetPlatformTextureSettings(settings);
            }
        }
    }
}
