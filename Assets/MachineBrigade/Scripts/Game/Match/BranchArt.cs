using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The tower-branch rework (DECISIONS 19T): a rank-7 branch's own art, from its data's "art" id (the art branch's
    /// "&lt;tower&gt;_a" / "&lt;tower&gt;_b", keyed by the spec's A/B order; DECISIONS 19U has the table). Its model and its icon
    /// when the art has them; until then the tower's own, so nothing is missing before the art lands.
    /// </summary>
    public static class BranchArt
    {
        private static Catalog _catalog;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => _catalog = null;

        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        /// <summary>The model a def is drawn with: its branch art when the library has it, else its own.</summary>
        public static string Model(VehicleDef def, ModelLibrary models) =>
            def.Art != null && models.Has(def.Art) ? def.Art : def.Model;

        /// <summary>A branch's icon of its own (the art id, once the icon set has it), or null.</summary>
        public static string Icon(string id) =>
            !string.IsNullOrEmpty(id) && id.IndexOf('.') > 0 && Catalog.Vehicles.TryGetValue(id, out var def) && def.Art != null &&
            Hud.Icons.Exists(def.Art) ? def.Art : null;
    }
}
