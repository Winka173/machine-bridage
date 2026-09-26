using System;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>Loads the JSON data files shipped under Resources/Data.</summary>
    public static class GameContent
    {
        public static Catalog LoadCatalog() => Catalog.FromJson(Load("Data/balance"));

        public static MapDefinition LoadMap(string id) => MapDefinition.FromJson(Load("Data/maps/" + id));

        private static string Load(string path)
        {
            var asset = Resources.Load<TextAsset>(path);
            if (asset == null) throw new InvalidOperationException($"Missing data file Resources/{path}.json.");
            return asset.text;
        }
    }
}
