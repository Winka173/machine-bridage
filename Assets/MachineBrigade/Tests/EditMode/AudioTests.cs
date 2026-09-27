using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>The recorded sound set (Resources/Audio, credited in its CREDITS.md) loads, category by category.</summary>
    public class AudioTests
    {
        private static readonly string[] Categories =
        {
            "mg", "autocannon", "cannon", "heavy_cannon", "rocket_launch", "missile_launch", "flak", "flame",
            "explosion_small", "explosion_medium", "explosion_large", "explosion_huge", "collapse", "debris", "impact_metal",
            "jet_pass", "jet_loop", "rotor_loop", "fire_loop", "wind_loop", "rain_loop", "drums_loop", "thunder", "siren",
            "click",
        };

        [Test]
        public void EveryCategoryHasRecordedClips()
        {
            foreach (var category in Categories)
            {
                var clips = Resources.LoadAll<AudioClip>("Audio/" + category);
                Assert.IsNotEmpty(clips, category);
                foreach (var clip in clips)
                {
                    Assert.Greater(clip.length, 0.05f, clip.name);
                    Assert.Less(clip.length, 10f, clip.name + ": short clips only, the set is loaded whole");
                }
            }
        }

        [Test]
        public void EveryFileIsCredited()
        {
            var credits = System.IO.File.ReadAllText(Application.dataPath + "/MachineBrigade/Resources/Audio/CREDITS.md");
            foreach (var category in Categories)
                foreach (var clip in Resources.LoadAll<AudioClip>("Audio/" + category))
                    StringAssert.Contains(clip.name, credits, clip.name + " is credited");
        }
    }
}
