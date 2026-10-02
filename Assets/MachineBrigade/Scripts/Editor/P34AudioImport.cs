using System.IO;
using UnityEditor;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Prompt 34 L6 (DECISIONS "Prompt 34 L5/L6/L7"): the tiered sounds' import settings, by kind (the prompt's "compress by
    /// type"): every clip mono; the short, frequent ones (T0-T3 shots and blasts, small-arms clusters) decompressed on load
    /// as ADPCM (cheap to start, no decoding while they play); the long, rarer ones (T4-T5, wrecks, crashes, horns,
    /// thermobaric) kept compressed in memory as Vorbis; the loops (rails, ship engines) Vorbis at a lower quality. All
    /// load in the background. Only Resources/Audio/p34 (Tools/sfx/build_sfx.py) is touched.
    /// </summary>
    internal sealed class P34AudioImport : AssetPostprocessor
    {
        private const string Folder = "Assets/MachineBrigade/Resources/Audio/p34/";

        private void OnPreprocessAudio()
        {
            if (!assetPath.Replace('\\', '/').StartsWith(Folder)) return;
            var importer = (AudioImporter)assetImporter;
            importer.forceToMono = true;
            importer.loadInBackground = true;
            var settings = importer.defaultSampleSettings;
            var name = Path.GetFileNameWithoutExtension(assetPath);
            var loop = name.StartsWith("train_rails") || name.StartsWith("ship_engine");
            var big = name.Contains("_t4") || name.Contains("_t5") || name.StartsWith("wreck_") || name.StartsWith("crash_") ||
                      name.Contains("horn") || name.StartsWith("blast_thermo");
            if (loop || big)
            {
                settings.loadType = AudioClipLoadType.CompressedInMemory;
                settings.compressionFormat = AudioCompressionFormat.Vorbis;
                settings.quality = loop ? 0.35f : 0.5f;
            }
            else
            {
                settings.loadType = AudioClipLoadType.DecompressOnLoad;
                settings.compressionFormat = AudioCompressionFormat.ADPCM;
            }
            settings.sampleRateSetting = AudioSampleRateSetting.OptimizeSampleRate;
            importer.defaultSampleSettings = settings;
        }
    }
}
