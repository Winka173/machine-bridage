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
    /// load in the background. Fix pass L7: the folder is Resources/Audio/sfx now (the library by size, Tools/sfx/build_sfx.py;
    /// prompt 34's p34 is gone): the big ones are the 203 mm and up, bombs, super weapons, wrecks, crashes, horns,
    /// thermobaric blasts and the big launches; the loops the rails, the ship's and the units' engines.
    /// </summary>
    internal sealed class P34AudioImport : AssetPostprocessor
    {
        private const string Folder = "Assets/MachineBrigade/Resources/Audio/sfx/";

        private void OnPreprocessAudio()
        {
            if (!assetPath.Replace('\\', '/').StartsWith(Folder)) return;
            var importer = (AudioImporter)assetImporter;
            importer.forceToMono = true;
            importer.loadInBackground = true;
            var settings = importer.defaultSampleSettings;
            var name = Path.GetFileNameWithoutExtension(assetPath);
            var loop = name.StartsWith("train_rails") || name.StartsWith("ship_engine") || name.StartsWith("engine_");
            var big = name.Contains("_s4") || name.Contains("_s406") || name.Contains("super") || name.Contains("bomb") || name.StartsWith("wreck_") ||
                      name.StartsWith("crash_") || name.Contains("horn") || name.StartsWith("blast_thermo") || name.StartsWith("launch_big");
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
