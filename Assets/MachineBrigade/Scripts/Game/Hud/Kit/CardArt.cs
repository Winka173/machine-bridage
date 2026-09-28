using System;
using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The card pictures: 512 px renders of the high-detail models on a transparent background
    /// (Resources/UI/Cards/&lt;model&gt;.png), made by MachineBrigade.Editor.CardRenders from the same
    /// 3/4 camera and lights for every vehicle, elite, tower and boss. The manifest maps each card
    /// id to its model's picture and records the hash of the model file it was rendered from, so a
    /// changed model is re-rendered (the editor does it on import; CardRenderTests catch a stale one).
    /// </summary>
    public static class CardArt
    {
        public const string Folder = "UI/Cards/";
        public const string ManifestPath = Folder + "manifest";

        [Serializable]
        public sealed class Entry
        {
            /// <summary>The card (vehicle definition) id.</summary>
            public string id;

            /// <summary>vehicle, elite, tower or boss.</summary>
            public string kind;

            /// <summary>The model the card shows; the picture is Resources/UI/Cards/&lt;model&gt;.png.</summary>
            public string model;

            /// <summary>The model resource the picture was rendered from (the high-detail variant where one ships).</summary>
            public string source;

            /// <summary>SHA-1 of that model file when it was rendered.</summary>
            public string hash;
        }

        [Serializable]
        public sealed class Manifest
        {
            public int version;
            public int size;
            public string camera;
            public List<Entry> entries = new();
        }

        private static Manifest _manifest;
        private static Dictionary<string, Entry> _byId;
        private static readonly Dictionary<string, Texture2D> Loaded = new();

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _manifest = null;
            _byId = null;
            Loaded.Clear();
        }

        public static Manifest Current
        {
            get
            {
                if (_manifest != null) return _manifest;
                var text = Resources.Load<TextAsset>(ManifestPath);
                _manifest = text != null ? JsonUtility.FromJson<Manifest>(text.text) ?? new Manifest() : new Manifest();
                _byId = new Dictionary<string, Entry>();
                foreach (var e in _manifest.entries)
                    if (!string.IsNullOrEmpty(e.id)) _byId[e.id] = e;
                return _manifest;
            }
        }

        /// <summary>Forgets the loaded manifest (after the render tool rewrote it).</summary>
        public static void Reload() => ResetStatics();

        public static Entry EntryFor(string cardId)
        {
            _ = Current;
            return cardId != null && _byId.TryGetValue(cardId, out var e) ? e : null;
        }

        /// <summary>The card picture for a vehicle, elite, tower or boss id, or null when it has none.</summary>
        public static Texture2D For(string cardId)
        {
            if (string.IsNullOrEmpty(cardId)) return null;
            var model = EntryFor(cardId)?.model ?? cardId;
            if (Loaded.TryGetValue(model, out var tex) && tex != null) return tex;
            tex = Resources.Load<Texture2D>(Folder + model);
            Loaded[model] = tex;
            return tex;
        }
    }
}
