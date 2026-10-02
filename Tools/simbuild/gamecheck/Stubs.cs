// Stubs for GameCheck.csproj only: the smallest surface the checked Game files use. Not part of the game.
using System.Collections.Generic;
using MachineBrigade.Sim.Modes;

namespace UnityEngine
{
    public class Object { public string name = ""; }
    public class TextAsset : Object { public string text = ""; }
    public static class Resources
    {
        public static T Load<T>(string path) where T : Object => null;
        public static T[] LoadAll<T>(string path) where T : Object => new T[0];
    }
    public static class Time { public static int frameCount; public static float unscaledDeltaTime; public static float timeScale; }
    public static class Mathf { public static float Min(float a, float b) => a < b ? a : b; }
}

namespace MachineBrigade.Game.Hud
{
    public static class DialogueText
    {
        public static (string speaker, string words) Split(string text, string speaker) => (speaker, text);
        public static string Text(string key, object arg) => key;
        public static string Name(string speaker) => speaker;
    }
    public static class CampaignText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new();
        public static readonly string[] Speakers = { "khai" };
    }
    public static class Strings
    {
        public static string Get(string key) => key;
        public static bool Has(string key) => true;
    }
}

namespace MachineBrigade.Game.Match
{
    internal static class Narrative
    {
        public static readonly string[] ReactGenerals = { "varga" };
        public const int ReactLines = 3;
    }

    internal class MissionSession
    {
        public MissionMode Mission;
        public IGameMode Mode;
    }
}
