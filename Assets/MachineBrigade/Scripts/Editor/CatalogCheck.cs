using System;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Loads the game's data once and logs the first error, from the command line:
    /// <c>-batchmode -nographics -executeMethod MachineBrigade.Editor.CatalogCheck.Run -quit</c>. Not a test: it only
    /// checks that balance.json and campaign.json load (the owner runs tests only in the test phase).
    /// </summary>
    public static class CatalogCheck
    {
        public static void Run()
        {
            try
            {
                var catalog = MachineBrigade.Game.Match.GameContent.LoadCatalog();
                MachineBrigade.Game.Match.Campaign.All.GetHashCode();
                // Boss design 09/10: the workbook's structural rules (one 50 % phase, no radar part, capped summons carried by a part, ...).
                var breaches = MachineBrigade.Sim.Content.BossDesignRules.Check(catalog);
                if (breaches.Count > 0) throw new Exception("boss design rules broken: " + string.Join("; ", breaches));
                Debug.Log($"[CatalogCheck] OK: {catalog.Vehicles.Count} vehicles, {catalog.Weapons.Count} weapons");
            }
            catch (Exception e)
            {
                Debug.LogError("[CatalogCheck] FAILED: " + e);
                EditorExit(1);
                return;
            }
            EditorExit(0);
        }

        private static void EditorExit(int code) => UnityEditor.EditorApplication.Exit(code);
    }
}
