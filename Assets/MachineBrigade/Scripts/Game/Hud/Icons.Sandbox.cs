using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    public static partial class Icons
    {
        /// <summary>
        /// The Sandbox's controls (the lean screen, DECISIONS 21S), in the kit's Lucide style: the unit grid, search,
        /// filters, undo and redo, more, one tick, turning, copying, deleting, overlays, statistics, A/B, free rotation.
        /// </summary>
        private static readonly Dictionary<string, string> SandboxSvg = new()
        {
            ["sb_grid"] = "<rect x=\"3\" y=\"3\" width=\"7\" height=\"7\"/><rect x=\"14\" y=\"3\" width=\"7\" height=\"7\"/><rect x=\"3\" y=\"14\" width=\"7\" height=\"7\"/><rect x=\"14\" y=\"14\" width=\"7\" height=\"7\"/>",
            ["sb_search"] = "<circle cx=\"11\" cy=\"11\" r=\"7\"/><path d=\"m21 21-5-5\"/>",
            ["sb_filter"] = "<path d=\"M3 4h18l-7 8v7l-4 2v-9Z\"/>",
            ["sb_undo"] = "<path d=\"M9 13 4 8l5-5\"/><path d=\"M4 8h10a6 6 0 0 1 0 12H9\"/>",
            ["sb_redo"] = "<path d=\"m15 13 5-5-5-5\"/><path d=\"M20 8H10a6 6 0 0 0 0 12h5\"/>",
            ["sb_more"] = "<circle cx=\"5\" cy=\"12\" r=\"1.5\"/><circle cx=\"12\" cy=\"12\" r=\"1.5\"/><circle cx=\"19\" cy=\"12\" r=\"1.5\"/>",
            ["sb_step"] = "<path d=\"m5 5 10 7-10 7Z\"/><path d=\"M19 5v14\"/>",
            ["sb_turn_left"] = "<path d=\"M4 13a8 8 0 1 0 2.5-6.5L4 9\"/><path d=\"M4 4v5h5\"/><path d=\"M12 9v4l2 2\"/>",
            ["sb_turn_right"] = "<path d=\"M20 13a8 8 0 1 1-2.5-6.5L20 9\"/><path d=\"M20 4v5h-5\"/><path d=\"M12 9v4l-2 2\"/>",
            ["sb_copy"] = "<rect x=\"9\" y=\"9\" width=\"12\" height=\"12\" rx=\"1\"/><path d=\"M5 15H3V3h12v2\"/>",
            ["sb_trash"] = "<path d=\"M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7\"/>",
            ["sb_layers"] = "<path d=\"m12 3 10 5-10 5L2 8Z\"/><path d=\"m2 13 10 5 10-5\"/><path d=\"m2 18 10 5 10-5\" dash=\"2 1.5\"/>",
            ["sb_chart"] = "<path d=\"M3 3v18h18\"/><path d=\"M7 17v-5M12 17V8M17 17v-9\"/>",
            ["sb_ab"] = "<path d=\"M3 20 7 5l4 15M4.5 15h5\"/><path d=\"M14 5h4a3 3 0 0 1 0 6h-4Zm0 6h5a3 3 0 0 1 0 6h-5Z\"/>",
            ["sb_free"] = "<path d=\"M12 4a8 8 0 1 0 8 8\" dash=\"2 2\"/><path d=\"M12 12 19 5M15 5h4v4\"/>",
        };
    }
}
