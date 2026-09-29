using System;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>Loads the JSON data files shipped under Resources/Data.</summary>
    public static class GameContent
    {
        public static Catalog LoadCatalog()
        {
            var catalog = Catalog.FromJson(Load("Data/balance"));
            // Which model and icon each tower branch wears follows the data (tower-branch prompt C).
            Rendering.TowerArt.Learn(catalog);
            return catalog;
        }

        public static MapDefinition LoadMap(string id) => MapDefinition.FromJson(Load("Data/maps/" + id));

        public static System.Collections.Generic.IReadOnlyList<MissionDef> LoadCampaign() => MissionDef.ListFromJson(Load("Data/campaign"));

        /// <summary>The campaign file itself (its chapters and generals are read from it too).</summary>
        public static string CampaignJson => Load("Data/campaign");

        private static string Load(string path)
        {
            var asset = Resources.Load<TextAsset>(path);
            if (asset == null) throw new InvalidOperationException($"Missing data file Resources/{path}.json.");
            return asset.text;
        }
    }
}
