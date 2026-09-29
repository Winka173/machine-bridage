using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;
using RegexMatch = System.Text.RegularExpressions.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Stroke icons on a 24-unit grid (the 3d_astra set, Lucide style, plus a few of our own),
    /// drawn as vectors with Painter2D so they stay crisp at any screen density.
    /// Besides strokes, an element may carry <c>fill="1"</c> (filled, non-zero) or <c>fill="eo"</c> (even-odd, so
    /// inner sub-paths punch holes), <c>stroke="0"</c> (fill only), <c>sw="w"</c> (its own stroke width in grid
    /// units) and <c>dash="on off"</c> (a dashed stroke): the prompt 15 armour and weapon icons need them.
    /// </summary>
    public static partial class Icons
    {
        private static readonly Dictionary<string, string> Svg = new()
        {
            ["logo"] = "<path d=\"M12 2 22 20H2Z\"/><path d=\"m12 9 5 9H7Z\"/>",
            ["people"] = "<circle cx=\"9\" cy=\"7\" r=\"3\"/><path d=\"M3 21v-4a6 6 0 0 1 12 0v4M16 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3\"/>",
            ["shield"] = "<path d=\"m12 2 8 4v6c0 5-8 10-8 10S4 17 4 12V6Z\"/><path d=\"m8 11 3 3 5-6\"/>",
            ["crosshair"] = "<circle cx=\"12\" cy=\"12\" r=\"7\"/><path d=\"M12 1v6m0 10v6M1 12h6m10 0h6\"/><circle cx=\"12\" cy=\"12\" r=\"1\"/>",
            ["tank"] = "<rect x=\"3\" y=\"13\" width=\"18\" height=\"7\" rx=\"3\"/><path d=\"M7 13V8h8v5M15 9h7M7 17h1m3 0h1m3 0h1\"/>",
            ["bolt"] = "<path d=\"m14 2-9 12h7l-2 8 9-12h-7Z\"/>",
            ["move"] = "<path d=\"M12 2v20M2 12h20M8 6l4-4 4 4M8 18l4 4 4-4M6 8l-4 4 4 4m12-8 4 4-4 4\"/>",
            ["stop"] = "<rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>",
            ["pause"] = "<path d=\"M8 4v16M16 4v16\"/>",
            ["play"] = "<path d=\"m7 3 14 9-14 9Z\"/>",
            ["help"] = "<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M9 8a3 3 0 1 1 4 3c-1 1-1 1-1 3m0 3v1\"/>",
            ["arrow"] = "<path d=\"M4 12h16m-6-6 6 6-6 6\"/>",
            ["close"] = "<path d=\"m5 5 14 14M5 19 19 5\"/>",
            ["flag"] = "<path d=\"M5 22V3h14l-3 5 3 5H5\"/>",
            ["check"] = "<path d=\"m5 12 4 4L19 6\"/>",
            ["expand"] = "<path d=\"M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5\"/>",
            // Field Command 2.0 kit: the dropdown caret (the fonts have no ▾), sort, and a loading arc.
            ["caret"] = "<path d=\"m6 9 6 6 6-6\"/>",
            ["sort"] = "<path d=\"M4 6h16M7 12h10M10 18h4\"/>",
            ["spinner"] = "<path d=\"M12 3a9 9 0 1 1-9 9\"/>",
            ["info"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 11v6M12 7.5v.5\"/>",
            ["attack"] = "<path d=\"M20 4 9 15M20 4h-5M20 4v5M7 13l4 4M4 20l4-4\"/>",
            // Machine Brigade additions in the same style.
            ["plus"] = "<path d=\"M12 5v14M5 12h14\"/>",
            // The compact HUD's Auto buy (prompt 11 A2): a cart.
            ["cart"] = "<path d=\"M2 4h3l2.5 11h11L21 7H6\"/><circle cx=\"9\" cy=\"19\" r=\"1.6\"/><circle cx=\"17\" cy=\"19\" r=\"1.6\"/>",
            // Weapons: a gun on its mantlet, a belt of rounds.
            ["cannon"] = "<path d=\"M3 18h8a3 3 0 0 0 0-6H3Z\"/><path d=\"M12 14h7M19 12.5v3M21 13v2\"/>",
            ["mg"] = "<path d=\"M4 20v-9a2 2 0 0 1 4 0v9Zm6 0v-9a2 2 0 0 1 4 0v9Zm6 0v-9a2 2 0 0 1 4 0v9Z\"/><path d=\"M4 15h4m2 0h4m2 0h4\"/>",
            ["minus"] = "<path d=\"M5 12h14\"/>",
            ["restart"] = "<path d=\"M3 12a9 9 0 1 0 3-6.7L3 8\"/><path d=\"M3 3v5h5\"/>",
            ["retreat"] = "<path d=\"M9 14 4 9l5-5\"/><path d=\"M4 9h11a5 5 0 0 1 0 10h-3\"/>",
            ["reinforce"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 8v8M8 12h8\"/>",
            ["jeep"] = "<path d=\"M3 15v-3l2-4h7l3 4h5l1 3Z\"/><circle cx=\"7\" cy=\"17\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/>",
            ["artillery"] = "<rect x=\"3\" y=\"14\" width=\"14\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-4h6v4M13 11l8-5\"/>",
            ["apc"] = "<path d=\"M3 15v-4l3-3h10l4 4v3Z\"/><circle cx=\"6.5\" cy=\"17\" r=\"1.8\"/><circle cx=\"11.5\" cy=\"17\" r=\"1.8\"/><circle cx=\"16.5\" cy=\"17\" r=\"1.8\"/><path d=\"M11 8V6h6\"/>",
            ["helicopter"] = "<path d=\"M3 5h18M12 5v3\"/><path d=\"M5 12a3 3 0 0 1 3-3h7l3 3v2a2 2 0 0 1-2 2H8a3 3 0 0 1-3-3Z\"/><path d=\"M18 12h4M8 16v3m6-3v3M6 19h10\"/>",
            ["aa"] = "<rect x=\"3\" y=\"14\" width=\"16\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-3h8v3M10 11l4-7M13 11l4-6\"/>",
            ["mlrs"] = "<path d=\"M2 16v-4h4l2-3h3v7M11 16h10v-3H11ZM12 13l8-6 1 2-8 4\"/><circle cx=\"5\" cy=\"17\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/>",
            ["lighttank"] = "<rect x=\"3\" y=\"14\" width=\"15\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-3h6v3M13 12h5\"/>",
            ["armoredcar"] = "<path d=\"M3 15v-3l3-3h10l4 3v3Z\"/><circle cx=\"6\" cy=\"17\" r=\"1.6\"/><circle cx=\"11\" cy=\"17\" r=\"1.6\"/><circle cx=\"16\" cy=\"17\" r=\"1.6\"/><path d=\"M10 9V7h4v2M14 8h6\"/>",
            ["destroyer"] = "<rect x=\"3\" y=\"14\" width=\"14\" height=\"6\" rx=\"3\"/><path d=\"M6 14v-3h7v3M13 12h9\"/>",
            ["heavytank"] = "<rect x=\"2\" y=\"13\" width=\"18\" height=\"7\" rx=\"3.5\"/><path d=\"M6 13V9h9v4M15 10.5h7M9 9V7h3\"/>",
            ["sam"] = "<rect x=\"3\" y=\"15\" width=\"15\" height=\"5\" rx=\"2.5\"/><path d=\"M8 15v-2h6v2M9 13l6-8 2 1-5 7M12 13l6-6 1 2-4 4\"/>",
            ["mortar"] = "<path d=\"M3 15v-4l3-3h10l4 4v3Z\"/><circle cx=\"7\" cy=\"17\" r=\"1.8\"/><circle cx=\"15\" cy=\"17\" r=\"1.8\"/><path d=\"M11 8l5-6 1.5 1-4.5 6\"/>",
            ["technical"] = "<path d=\"M2 16v-3h8V9h5l3 4h3v3Z\"/><circle cx=\"6\" cy=\"17\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/><path d=\"M3 12l6-4M4 13.5l6-4\"/>",
            ["gunship"] = "<path d=\"M2 5h20M12 5v3\"/><path d=\"M3 12a3 3 0 0 1 3-3h9l4 3v2a2 2 0 0 1-2 2H6a3 3 0 0 1-3-3Z\"/><path d=\"M19 12h3M6 16v3M15 16v3M4 19h13M8 12h6\"/>",
            ["scoutheli"] = "<path d=\"M5 6h14M12 6v3\"/><circle cx=\"10\" cy=\"13\" r=\"4\"/><path d=\"M14 13h7M19 11v4M8 17l-1 3M12 17l1 3\"/>",
            ["jet"] = "<path d=\"M12 2c1 0 1.5 2 1.5 4v12h-3V6c0-2 .5-4 1.5-4Z\"/><path d=\"M2 11h20v2H2ZM7 20h10M9 17h6\"/>",
            ["drone"] = "<path d=\"M2 10h20M12 6v12M9 18h6M10 20l2-2 2 2\"/><circle cx=\"12\" cy=\"5\" r=\"1.5\"/>",
            ["coin"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M14.6 9.6A2.9 2.9 0 0 0 9.4 11c0 3 5.2 2 5.2 5a2.9 2.9 0 0 1-5.2 1.2M12 5.6v2M12 16.4v2\"/>",
            ["star"] = "<path d=\"M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z\"/>",
            ["lock"] = "<rect x=\"5\" y=\"11\" width=\"14\" height=\"10\" rx=\"2\"/><path d=\"M8 11V8a4 4 0 0 1 8 0v3\"/>",
            ["ad"] = "<rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"2\"/><path d=\"M10 9l5 3-5 3Z\"/>",
            ["shop"] = "<path d=\"M5 8h14l-1 12H6ZM9 8V6a3 3 0 0 1 6 0v2\"/>",
            ["campaign"] = "<path d=\"M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2ZM9 4v14M15 6v14\"/>",
            ["crown"] = "<path d=\"M3 19h18M4 16 3 7l5 4 4-6 4 6 5-4-1 9Z\"/>",
            ["swords"] = "<path d=\"M4 4l9 9M4 4h4M4 4v4M20 4l-9 9M20 4h-4M20 4v4M6 18l-2 2M18 18l2 2M8 16l-2 2M16 16l2 2\"/>",
            ["rank"] = "<path d=\"M6 3l6 4 6-4v6l-6 4-6-4ZM6 13l6 4 6-4v4l-6 4-6-4Z\"/>",
            ["paint"] = "<path d=\"M18 3l3 3-9 9-3-3ZM9 12l3 3c0 3-2 6-8 6 1-1 2-3 2-5a3 3 0 0 1 3-4\"/>",
            ["battery"] = "<rect x=\"2\" y=\"7\" width=\"17\" height=\"10\" rx=\"2\"/><path d=\"M22 11v2M6 10v4M10 10v4\"/>",
            ["shadow"] = "<circle cx=\"11\" cy=\"9\" r=\"5\"/><path d=\"M3 19c4-2.5 12-2.5 18 0M6 22c3-1 9-1 12 0\"/>",
            ["resolution"] = "<rect x=\"3\" y=\"4\" width=\"18\" height=\"13\" rx=\"2\"/><path d=\"M8 21h8M12 17v4M7 12V8h4M17 9v4h-4\"/>",
            ["edges"] = "<path d=\"M4 20v-4h4v-4h4V8h4V4h4\"/>",
            ["gauge"] = "<path d=\"M12 14l4-5M3.5 19a10 10 0 1 1 17 0\"/><circle cx=\"12\" cy=\"14\" r=\"1.5\"/>",
            ["camera"] = "<path d=\"M3 8h4l2-3h6l2 3h4v11H3Z\"/><circle cx=\"12\" cy=\"13\" r=\"3.5\"/>",
            ["resize"] = "<path d=\"M4 7V5h10v2M9 5v14M7 19h4M14 12v-1h6v1M17 11v8M15.5 19h3\"/>",
            ["snow"] = "<path d=\"M12 2v20M4 7l16 10M20 7 4 17M9 4l3 2 3-2M9 20l3-2 3 2\"/>",
            ["wind"] = "<path d=\"M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h8\"/>",
            ["fog"] = "<path d=\"M4 9h16M2 13h20M5 17h14M7 21h10\"/><path d=\"M7 9a5 5 0 0 1 10 0\"/>",
            ["moon"] = "<path d=\"M20 14A8 8 0 1 1 10 4a6 6 0 0 0 10 10Z\"/>",
            ["pine"] = "<path d=\"M12 2 6 10h3l-4 6h14l-4-6h3ZM12 16v6\"/>",
            ["dune"] = "<path d=\"M2 19c4-6 8-6 11-2s6 3 9-1M6 9a3 3 0 1 0 0-.1\"/><path d=\"M16 4v6M13 7h6\"/>",
            ["anchor"] = "<path d=\"M12 7v14M5 13a7 7 0 0 0 14 0M3 13h4M17 13h4\"/><circle cx=\"12\" cy=\"5\" r=\"2\"/>",
            ["flame"] = "<path d=\"M12 22a7 7 0 0 0 7-7c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-3 3-5 5-5 8a7 7 0 0 0 7 7Z\"/>",
            ["barrage"] = "<path d=\"M6 3v6M12 2v7M18 3v6\"/><path d=\"M4 21a8 5 0 0 1 16 0\"/><path d=\"m9 13 3 3 3-3\"/>",
            ["airstrike"] = "<path d=\"M12 2l2 7 7 3v2l-7-1-1 6 3 2v1l-4-1-4 1v-1l3-2-1-6-7 1v-2l7-3Z\"/>",
            ["missile"] = "<path d=\"M4 20 15 9M15 9l4-6 2 2-6 4M9 15l-4 1 3 3 1-4M13 11l-3-4M13 11l4 3\"/>",
            ["smoke"] = "<path d=\"M4 17a4 4 0 0 1 2-7 5 5 0 0 1 9-2 4 4 0 0 1 5 5 3 3 0 0 1-1 6H7a3 3 0 0 1-3-2Z\"/>",
            ["repair"] = "<path d=\"M15 3a5 5 0 0 0-5 6L3 16l5 5 7-7a5 5 0 0 0 6-5l-3 3-3-1-1-3Z\"/>",
            ["settings"] = "<circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2\"/>",
            ["deck"] = "<rect x=\"3\" y=\"6\" width=\"12\" height=\"15\" rx=\"2\"/><path d=\"M8 3h11a2 2 0 0 1 2 2v13\"/>",
            ["trophy"] = "<path d=\"M7 4h10v5a5 5 0 0 1-10 0ZM7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4M12 14v4M8 21h8\"/>",
            ["home"] = "<path d=\"M3 11 12 3l9 8M5 9v12h14V9\"/>",
            ["cp"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M15 9a4 4 0 1 0 0 6\"/>",
            ["globe"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18\"/>",
            ["volume"] = "<path d=\"M4 9h4l5-4v14l-5-4H4ZM16 9a4 4 0 0 1 0 6M19 6a8 8 0 0 1 0 12\"/>",
            ["sun"] = "<circle cx=\"12\" cy=\"12\" r=\"4\"/><path d=\"M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5\"/>",
            ["cloud"] = "<path d=\"M6 18a4 4 0 0 1 0-8 6 6 0 0 1 11-1 4 4 0 0 1 1 9Z\"/>",
            ["rain"] = "<path d=\"M5 14a4 4 0 0 1 2-7 5 5 0 0 1 9-1 4 4 0 0 1 3 8M8 17l-1 3M12 17l-1 3M16 17l-1 3\"/>",
            ["storm"] = "<path d=\"M5 13a4 4 0 0 1 2-7 5 5 0 0 1 9-1 4 4 0 0 1 3 8M13 13l-3 5h4l-3 5\"/>",
            ["dice"] = "<rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"3\"/><circle cx=\"9\" cy=\"9\" r=\"1\"/><circle cx=\"15\" cy=\"15\" r=\"1\"/><circle cx=\"15\" cy=\"9\" r=\"1\"/><circle cx=\"9\" cy=\"15\" r=\"1\"/>",
            ["bomb"] = "<circle cx=\"11\" cy=\"14\" r=\"7\"/><path d=\"M15 9l3-3M18 3v2M21 6h-2M20 4l-1 1\"/>",
            ["eye"] = "<path d=\"M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z\"/><circle cx=\"12\" cy=\"12\" r=\"3\"/>",
            ["mine"] = "<circle cx=\"12\" cy=\"14\" r=\"5\"/><path d=\"M3 19h18M12 9V5M9 6l3-1 3 1\"/>",
            ["jammer"] = "<path d=\"M12 21V11M9 21h6M12 11 9 5h6l-3 6M6 5c-2 3-2 6 0 9M18 5c2 3 2 6 0 9M3 3c-3 5-3 10 0 14M21 3c3 5 3 10 0 14\"/>",
            ["a10"] = "<path d=\"M12 2c.8 0 1.2 1 1.2 3v15h-2.4V5c0-2 .4-3 1.2-3Z\"/><path d=\"M2 10h20v2H2Z\"/><circle cx=\"9\" cy=\"15\" r=\"1.6\"/><circle cx=\"15\" cy=\"15\" r=\"1.6\"/><path d=\"M6 20h12M7 18v4M17 18v4\"/>",
            ["su25"] = "<path d=\"M12 2c.8 0 1.3 1.5 1.3 3.5V20h-2.6V5.5C10.7 3.5 11.2 2 12 2Z\"/><path d=\"M10.7 9 2 13v1.5l8.7-2M13.3 9 22 13v1.5l-8.7-2\"/><path d=\"M8 20h8M9.5 16.5h5\"/>",
            ["b52"] = "<path d=\"M12 2c.7 0 1 1 1 3v16h-2V5c0-2 .3-3 1-3Z\"/><path d=\"M11 8 1 15v1.5l10-4M13 8l10 7v1.5l-10-4\"/><path d=\"M5 12.5v2M8 10.5v2M16 10.5v2M19 12.5v2M8 21h8\"/>",
            ["b2"] = "<path d=\"M12 5 2 15l3 2 3-2 2 2 2-2 2 2 2-2 3 2 3-2Z\"/><path d=\"M10 10h4\"/>",
            ["ac130"] = "<path d=\"M12 2c1.2 0 2 1 2 3v14h-4V5c0-2 .8-3 2-3Z\"/><path d=\"M2 8h20v2H2Z\"/><path d=\"M5 7v4M9 7v4M15 7v4M19 7v4M8 19h8M14 13h3M14 16h3\"/>",
            ["reaper"] = "<path d=\"M12 4v16M1 10h22M12 20l-3 2M12 20l3 2\"/><circle cx=\"12\" cy=\"4\" r=\"1.5\"/>",
            ["hind2"] = "<path d=\"M2 5h20M12 5v3\"/><path d=\"M4 12a3 3 0 0 1 3-3h9l4 3v2a2 2 0 0 1-2 2H7a3 3 0 0 1-3-3Z\"/><path d=\"M20 12h3M8 12h8M9 16v2h3v-2M14 16v2h3v-2M5 16l-1 3M16 9V8\"/>",
            ["titan"] = "<rect x=\"1\" y=\"13\" width=\"20\" height=\"7\" rx=\"3.5\"/><path d=\"M5 13V8h11v5M16 9h7M16 11.5h7M8 8V5.5h5V8\"/>",
            ["twintank"] = "<rect x=\"3\" y=\"14\" width=\"17\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-4h8v4M15 10.5h7M15 13h6\"/>",
            ["siegegun"] = "<rect x=\"2\" y=\"14\" width=\"16\" height=\"6\" rx=\"3\"/><path d=\"M6 14v-3h7v3M12 11l9-7M13 13l2-1.5M2 17l-1.5 3\"/>",
            ["apstank"] = "<rect x=\"3\" y=\"14\" width=\"18\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-4h8v4M15 11h7\"/><path d=\"M11 2.5l3 1.3v2.1c0 1.6-3 3.1-3 3.1S8 7.5 8 5.9V3.8Z\"/>",
            ["command"] = "<rect x=\"2\" y=\"13\" width=\"19\" height=\"6\" rx=\"2\"/><path d=\"M5 13V9h9v4M7 9V3M7 3l4 2-4 2M17 13V6\"/><circle cx=\"6\" cy=\"20\" r=\"1.5\"/><circle cx=\"11.5\" cy=\"20\" r=\"1.5\"/><circle cx=\"17\" cy=\"20\" r=\"1.5\"/>",
            ["wheeledgun"] = "<rect x=\"2\" y=\"13\" width=\"17\" height=\"5\" rx=\"2\"/><path d=\"M6 13l2-3h6l1 3M12 11h10\"/><circle cx=\"5\" cy=\"19\" r=\"1.5\"/><circle cx=\"10\" cy=\"19\" r=\"1.5\"/><circle cx=\"15\" cy=\"19\" r=\"1.5\"/>",
            ["cbradar"] = "<rect x=\"2\" y=\"14\" width=\"19\" height=\"5\" rx=\"2\"/><path d=\"M11 14V10M7 3l8 1-1 7-8-1Z\"/><path d=\"M17 5a4 4 0 0 1 2 4M19 3a7 7 0 0 1 3 6\"/><circle cx=\"6\" cy=\"20\" r=\"1.4\"/><circle cx=\"16\" cy=\"20\" r=\"1.4\"/>",
            ["longsam"] = "<rect x=\"2\" y=\"15\" width=\"20\" height=\"4\" rx=\"2\"/><path d=\"M7 15l9-10 2 2-9 10M10 15l8-9\"/><circle cx=\"5\" cy=\"20\" r=\"1.4\"/><circle cx=\"12\" cy=\"20\" r=\"1.4\"/><circle cx=\"19\" cy=\"20\" r=\"1.4\"/>",
            ["tower"] = "<path d=\"M8 21l1-11h6l1 11M7 10h10V7H7ZM9 7V4h6v3M12 4V2\"/><path d=\"M4 5l3 2M20 5l-3 2\"/>",
            ["sead"] = "<path d=\"M3 12h11l3-3h2l-2 3 2 3h-2l-3-3\"/><path d=\"M6 12l-2 3M6 12l-2-3\"/><path d=\"M18 18a4 4 0 0 0-6 0M20 21a7 7 0 0 0-10 0\"/>",
            ["ifv"] = "<rect x=\"2\" y=\"14\" width=\"18\" height=\"6\" rx=\"3\"/><path d=\"M4 14l2-4h11l3 4\"/><path d=\"M9 10V8h5v2M14 9h7M5 9h3v1\"/>",
            ["heavyaa"] = "<rect x=\"2\" y=\"14\" width=\"17\" height=\"6\" rx=\"3\"/><path d=\"M6 14v-4h8v4M13 10l7-5M14 12l7-4M9 10V6M7 5.5h4\"/>",
            ["atgm"] = "<rect x=\"2\" y=\"14\" width=\"17\" height=\"6\" rx=\"3\"/><path d=\"M4 14l2-3h10l2 3M9 11l9-5M11 11l9-4\"/>",
            ["siegemortar"] = "<rect x=\"2\" y=\"14\" width=\"17\" height=\"6\" rx=\"3\"/><path d=\"M4 14l2-3h8l2 3M13 11 7 4M15 11 9 4M6.5 4h3\"/>",
            ["turtle"] = "<rect x=\"3\" y=\"15\" width=\"16\" height=\"5\" rx=\"2.5\"/><path d=\"M2 15l3-6h13l2 6ZM18 12h4\"/><circle cx=\"21.5\" cy=\"18\" r=\"1.5\"/>",
            ["bmpt"] = "<rect x=\"2\" y=\"14\" width=\"18\" height=\"6\" rx=\"3\"/><path d=\"M6 14v-3h9v3M15 11.5h7M15 13h6M7 11V9h4v2M20 14l2-1\"/>",
            ["truckgun"] = "<path d=\"M2 16v-4h4l2-2h3v6M11 16h9v-3h-9ZM14 13l8-6\"/><circle cx=\"5\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"13\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"18\" cy=\"17.5\" r=\"1.8\"/>",
            ["grad"] = "<path d=\"M2 16v-4h4l2-3h2v7\"/><rect x=\"10\" y=\"10\" width=\"11\" height=\"5\" rx=\"1\"/><path d=\"M11 12h9M11 13.5h9\"/><circle cx=\"5\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"12\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"18\" cy=\"17.5\" r=\"1.8\"/>",
            ["thermo"] = "<rect x=\"2\" y=\"15\" width=\"16\" height=\"5\" rx=\"2.5\"/><path d=\"M5 15l3-5h10l2 3-12 2M9 12h8\"/>",
            ["smerch"] = "<path d=\"M1 16v-4h3l2-3h2v7M8 13l13-5v4l-13 3ZM8 16h14\"/><circle cx=\"4\" cy=\"17.5\" r=\"1.6\"/><circle cx=\"9\" cy=\"17.5\" r=\"1.6\"/><circle cx=\"15\" cy=\"17.5\" r=\"1.6\"/><circle cx=\"20\" cy=\"17.5\" r=\"1.6\"/>",
            ["ballistic"] = "<path d=\"M2 17v-4h4l2-3h2v7M10 17h12M11 14l9-9 2 2-9 9ZM20 5l2-2\"/><circle cx=\"5\" cy=\"18\" r=\"1.6\"/><circle cx=\"14\" cy=\"18\" r=\"1.6\"/><circle cx=\"19\" cy=\"18\" r=\"1.6\"/>",
            ["fpvtruck"] = "<path d=\"M2 16v-4h4l2-3h3v7M11 16h10v-4H11ZM13 7h6M16 7v2M13 5.5v3M19 5.5v3\"/><circle cx=\"5\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"17\" cy=\"17.5\" r=\"1.8\"/>",
            ["engineer"] = "<rect x=\"2\" y=\"14\" width=\"17\" height=\"6\" rx=\"3\"/><path d=\"M4 14v-3h9v3M13 11l5-6 3 1M21 6v4M20 10h2\"/>",
            ["vbied"] = "<path d=\"M3 16v-3l2-3h9l3 3h3v3Z\"/><circle cx=\"7\" cy=\"17\" r=\"1.8\"/><circle cx=\"16\" cy=\"17\" r=\"1.8\"/><path d=\"M12 7V3M9 6.5 7 4.5M15 6.5l2-2\"/>",
            ["zu23"] = "<path d=\"M2 16v-3h8V9h5l3 4h3v3Z\"/><circle cx=\"6\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"17\" cy=\"17.5\" r=\"1.8\"/><path d=\"M4 12l6-7M6.5 12.5l6-7\"/>",
            ["smokecar"] = "<rect x=\"2\" y=\"15\" width=\"16\" height=\"5\" rx=\"2.5\"/><path d=\"M4 15v-4h11v4\"/><path d=\"M14 9a2 2 0 1 1 3-2 2 2 0 0 1 3 2 2 2 0 0 1-1 3h-4a2 2 0 0 1-1-3Z\"/>",
            ["lancet"] = "<path d=\"M2 16v-4h4l2-3h2v7M10 16h11v-3H10ZM12 11l7-4M15 4.5l5 2-2 3\"/><circle cx=\"5\" cy=\"17.5\" r=\"1.8\"/><circle cx=\"17\" cy=\"17.5\" r=\"1.8\"/>",
            ["shahed"] = "<path d=\"M12 3 4 17h16ZM12 3v14M4 17l-1 2M20 17l1 2\"/><circle cx=\"12\" cy=\"19.5\" r=\"1\"/>",
            ["laser"] = "<path d=\"M2 17v-4h4l2-3h2v7M10 17h11v-4H10Z\"/><circle cx=\"5\" cy=\"18\" r=\"1.6\"/><circle cx=\"17\" cy=\"18\" r=\"1.6\"/><rect x=\"13\" y=\"8\" width=\"5\" height=\"4\" rx=\"1\"/><path d=\"M18 9l4-5\"/>",
            ["railgun"] = "<path d=\"M1 17v-4h4l2-3h2v7M9 17h12v-3H9ZM11 12l11-4M11 13.5l11-4\"/><circle cx=\"4\" cy=\"18\" r=\"1.6\"/><circle cx=\"11\" cy=\"18\" r=\"1.6\"/><circle cx=\"18\" cy=\"18\" r=\"1.6\"/>",
            ["sapper"] = "<rect x=\"3\" y=\"14\" width=\"15\" height=\"6\" rx=\"3\"/><path d=\"M5 14v-3h9v3M18 11v9h3v-9ZM6 11l3-5 5 1M14 7l1 3\"/>",
            ["fighter"] = "<path d=\"M12 2l2 7 7 5v2l-7-2-1 5 3 2v1H8v-1l3-2-1-5-7 2v-2l7-5Z\"/>",
            ["elite"] = "<path d=\"M5 12l7-5 7 5M5 18l7-5 7 5M12 2l1 2h2l-1.5 1.5.5 2-2-1-2 1 .5-2L9 4h2Z\"/>",
            ["ammo"] = "<path d=\"M6 20V10l2-5 2 5v10ZM14 20V10l2-5 2 5v10ZM6 16h4M14 16h4\"/>",
            ["crate"] = "<rect x=\"4\" y=\"8\" width=\"16\" height=\"12\" rx=\"1\"/><path d=\"M4 12h16M12 8v12M7 8l2-3h6l2 3\"/>",
            ["gem"] = "<path d=\"M6 4h12l3 5-9 11L3 9Z\"/><path d=\"M3 9h18M9.5 4 12 20l2.5-16\"/>",
            ["gear"] = "<circle cx=\"12\" cy=\"12\" r=\"3.2\"/><path d=\"M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1\"/>",
            ["blueprint"] = "<path d=\"M6 3h9l4 4v14H6Z\"/><path d=\"M15 3v4h4M9 12h7M9 16h5\"/>",
            ["upgrade"] = "<path d=\"M6 14l6-6 6 6M6 20l6-6 6 6\"/>",
            ["skull"] = "<path d=\"M12 3a8 8 0 0 0-5 14v3h10v-3a8 8 0 0 0-5-14Z\"/><circle cx=\"9\" cy=\"11\" r=\"1.5\"/><circle cx=\"15\" cy=\"11\" r=\"1.5\"/><path d=\"M10 20v-2M14 20v-2\"/>",
            // Hardpoint sizes (the base screen): the same corner brackets, the footprint inside grows.
            ["slot_small"] = "<path d=\"M3 8V3h5M16 3h5v5M21 16v5h-5M8 21H3v-5\"/><rect x=\"9\" y=\"9\" width=\"6\" height=\"6\" rx=\"1\"/>",
            ["slot_medium"] = "<path d=\"M3 8V3h5M16 3h5v5M21 16v5h-5M8 21H3v-5\"/><rect x=\"7\" y=\"7\" width=\"10\" height=\"10\" rx=\"1\"/>",
            ["slot_large"] = "<path d=\"M3 8V3h5M16 3h5v5M21 16v5h-5M8 21H3v-5\"/><rect x=\"5.5\" y=\"5.5\" width=\"13\" height=\"13\" rx=\"1\"/>",
            // The headquarters (a command post with its flag) and a utility module (a chip).
            ["hq"] = "<path d=\"M3 21h18M5 21v-9l7-5 7 5v9M10 21v-5h4v5M12 7V2l5 2-5 2\"/>",
            ["module"] = "<rect x=\"6\" y=\"6\" width=\"12\" height=\"12\" rx=\"1\"/><rect x=\"10\" y=\"10\" width=\"4\" height=\"4\"/><path d=\"M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4\"/>",
            // Towers and structures (prompt 14 I): their own set, never a vehicle's icon. TowerIcons maps ids to them;
            // most stand on a ground line, so they read as built, not driven. The 3D renders (CardArt) stay for cards and panels.
            // Guard tower: cabin on splayed legs, pointed roof, a gun.
            ["t_guard"] = "<path d=\"M4 21h16M8 21l1.5-10M16 21l-1.5-10M9 16h6M7 11h10V7H7ZM5.5 7 12 3l6.5 4M17 9h4\"/>",
            // MG bunker: a domed pillbox, its firing slit and barrel.
            ["t_mg"] = "<path d=\"M2 20h20M4 20v-3.5c0-3.6 3.6-6.5 8-6.5s8 2.9 8 6.5V20\"/><rect x=\"7\" y=\"13.6\" width=\"7\" height=\"2.6\" rx=\"1.3\"/><path d=\"M14 14.9h8\"/>",
            // AA tower: twin flak barrels over a sandbag wall.
            ["t_aa"] = "<path d=\"M2 21h20M2 21v-2.5a2 2 0 0 1 4 0 2 2 0 0 1 4 0 2 2 0 0 1 4 0 2 2 0 0 1 4 0 2 2 0 0 1 4 0V21M9 16.5V13h6v3.5M10.5 13l5-8.5M14 13l5-8.5\"/>",
            // EW tower: a lattice mast between two zigzags of noise.
            ["t_ew"] = "<path d=\"M5 21h14M8.5 21 12 4l3.5 17M9.6 15.5h4.8M10.6 10.5h2.8M8.5 6.5h7M3.5 7 2 9l1.5 2L2 13M20.5 7 22 9l-1.5 2 1.5 2\"/>",
            // Dragon's teeth: three concrete pyramids.
            ["t_teeth"] = "<path d=\"M1 20h22M2 20l3-8.5 3 8.5M5 11.5 6 20M9 20l3-12 3 12M12 8l1 12M16 20l3-8.5 3 8.5M19 11.5l1 8.5\"/>",
            // Minefield: a warning sign on a post, two mines.
            ["t_mines"] = "<path d=\"M2 21h20M6 21V11M6 3l4.5 8h-9ZM11 21a3.5 3.5 0 0 1 7 0M15.5 15a2.8 2.8 0 0 1 5.6 0Z\"/>",
            // Gun turret: an armoured turret on a concrete plinth, its muzzle brake.
            ["t_gun"] = "<path d=\"M3 21l1.5-5h15l1.5 5ZM6 16v-3l2-3h5l2 3v3M15 12.5h6M21 11v3\"/>",
            // ATGM tower: a launch tube on a tripod, its missile away.
            ["t_atgm"] = "<path d=\"M4 21h16M11 13v8M7 21l4-4 4 4M3 12.5l11-4.5 1.2 3L4.2 15.5ZM17 7l4.5-1.8\"/>",
            // Rocket turret: a rocket pod, face on, on its pedestal.
            ["t_rockets"] = "<path d=\"M4 21h16M8 21l2-4h4l2 4M12 17v-3\"/><rect x=\"4\" y=\"4\" width=\"16\" height=\"10\" rx=\"1.5\"/><circle cx=\"8\" cy=\"7.2\" r=\".5\"/><circle cx=\"12\" cy=\"7.2\" r=\".5\"/><circle cx=\"16\" cy=\"7.2\" r=\".5\"/><circle cx=\"8\" cy=\"10.8\" r=\".5\"/><circle cx=\"12\" cy=\"10.8\" r=\".5\"/><circle cx=\"16\" cy=\"10.8\" r=\".5\"/>",
            // C-RAM: the radome over a gatling mount.
            // Prompt 20 L.1: the Iron Dome branch: a tilted canister launcher, two interceptor arcs over it.
            ["t_irondome"] = "<path d=\"M3 21h18M6 21l1-3h10l1 3M8 18l5-6 3.5 2.5-3.5 3.5M10.5 15.5l4-4.5\"/><path d=\"M3 10a9 9 0 0 1 18 0M6.5 10a5.5 5.5 0 0 1 11 0\"/>",
            ["t_cram"] = "<path d=\"M4 21h16M6 21l1-3h10l1 3M8 18v-6M16 18v-6\"/><circle cx=\"12\" cy=\"8.5\" r=\"4.5\"/><path d=\"M16 14h6M16 16.5h5\"/>",
            // Gun pit: a turret sunk in its pit under a camouflage net (dashed).
            ["t_pit"] = "<path d=\"M2 15h4.5v5h11v-5H22M8.5 20v-2a2.5 2.5 0 0 1 2.5-2.5h2a2.5 2.5 0 0 1 2.5 2.5v2M15 17l7-3.5M5 12.5l1.5-1.5M9 9.6l2-.5M13 9.1l2 .5M17.5 11l1.5 1.5\"/>",
            // Artillery emplacement: a shielded howitzer raised over an earth berm.
            ["t_artillery"] = "<path d=\"M2 21c1-3 3-4 6-4h8c3 0 5 1 6 4M8 17v-4.5l3-2 2 1.5V17M12 11.5l6-7.5M16 2.8l3.4 2.6\"/>",
            // Missile battery: a tilted canister box, a missile leaving it.
            ["t_patriot"] = "<path d=\"M2 21h20M4 21v-3h13v3M6 18 13 8l4 2.8-6 7.2M9.5 18l5.5-8.6M15 8.2l3-4.2\"/>",
            // Drone hangar: an arched hangar, a drone over it.
            ["t_hangar"] = "<path d=\"M2 21h20M3 21v-5c0-3.9 4-7 9-7s9 3.1 9 7v5M8 21v-6h8v6M14.5 3h3M19.5 3h3M16 3v1.5h5V3M17.5 4.5l-.8 1.5M19.5 4.5l.8 1.5\"/>",
            // Heavy fortress: a crenellated casemate, twin barrels.
            ["t_fortress"] = "<path d=\"M2 21h20M3 21V10h3v2.5h2.5V10h3v2.5H14V10h3v11M17 14h5M17 17.5h5\"/>",
            // Repair bay: a bay frame with a wrench.
            ["t_repair"] = "<path d=\"M2 21h20M4 21V5h16v16M4 8h16M15 10.5a2.8 2.8 0 0 0-3.2 3.6L8.5 17.4l1.6 1.6 3.3-3.3a2.8 2.8 0 0 0 3.6-3.2l-1.5 1.5-1.4-.4-.4-1.4Z\"/>",
            // Ammo depot: an open crate of shells.
            ["t_ammo"] = "<path d=\"M2 21h20M3 21v-7h18v7M3 17h18M6 14V9l1.5-3L9 9v5M10.5 14V9L12 6l1.5 3v5M15 14V9l1.5-3L18 9v5\"/>",
            // Airfield: a landing pad's H.
            ["t_airfield"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M9 8v8M15 8v8M9 12h6\"/>",
            // Logistics station: a fuel tank on legs, its drop.
            ["t_logistics"] = "<rect x=\"3\" y=\"6\" width=\"18\" height=\"9\" rx=\"4.5\"/><path d=\"M3 21h18M6.5 15v6M17.5 15v6M12 8c1.5 2 2 3 2 3.8a2 2 0 0 1-4 0c0-.8.5-1.8 2-3.8Z\"/>",
            // Radar station: a radome on its building, sweeping.
            // Prompt 17 C: the shield generator (a dome over a pylon) and the CP relay (a mast with a coin).
            ["t_shieldgen"] = "<path d=\"M3 21h18M2.5 17.5a9.5 9.5 0 0 1 19 0M9 21v-5h6v5M12 16V9.5\"/><circle cx=\"12\" cy=\"8\" r=\"1.8\"/>",
            ["t_relay"] = "<path d=\"M3 21h10M8 21V6M5 21 8 11l3 10M5 6.5a4 4 0 0 1 6 0M3.5 4a6.5 6.5 0 0 1 9 0\"/><circle cx=\"17.5\" cy=\"15.5\" r=\"4\"/><path d=\"M17.5 13.5v4\"/>",
            ["t_radar"] = "<path d=\"M3 21h16M7 21l1-5h6l1 5M5.5 11h11\"/><circle cx=\"11\" cy=\"11\" r=\"5.5\"/><path d=\"M17.5 4a5 5 0 0 1 2.5 3M19.5 2a8 8 0 0 1 3 4.5\"/>",
            // Spawn bastion: a crenellated keep with its gate.
            ["t_bastion"] = "<path d=\"M2 21h20M5 21V8h2.5v2h3V8h3v2h3V8H19v13M10 21v-4a2 2 0 0 1 4 0v4\"/>",
            // Bulwark post: a machine gun on a tripod over a block wall.
            ["t_post"] = "<path d=\"M2 21h20M3 21v-5h18v5M9 16v5M15 16v5M8 16l3-4 3 4M11 12v4M7 11h14\"/>",
            // Super gun: a huge barrel raised from its block.
            ["t_supergun"] = "<path d=\"M2 21h20M3 21v-4h11v4M5 17v-2.5a3 3 0 0 1 3-3h2M8 13 20 3.5l1.6 2.2L10.3 15.6M18 5l1.6 2.2\"/>",
            // Targeting station: a reticle over the post, its mast.
            ["t_targeting"] = "<path d=\"M2 21h20M4 21v-6h10v6M9 15v-2.5M9 5.5v5M6.5 8h5M18 21V10M16 10h4\"/><circle cx=\"9\" cy=\"8\" r=\"4.5\"/>",
        };

        private static readonly Dictionary<string, List<Shape>> Parsed = new();

        public static bool Exists(string name) => name != null && (Svg.ContainsKey(name) || CombatSvg.ContainsKey(name));

        /// <summary>The icon's SVG source (the path data the uniqueness test compares), or null.</summary>
        public static string Source(string name) =>
            name == null ? null : Svg.TryGetValue(name, out var s) ? s : CombatSvg.TryGetValue(name, out var c) ? c : null;

        /// <summary>Every icon name, the kit's and the combat set's.</summary>
        public static IEnumerable<string> Names
        {
            get
            {
                foreach (var k in Svg.Keys) yield return k;
                foreach (var k in CombatSvg.Keys) yield return k;
            }
        }

        internal static IReadOnlyList<Shape> Get(string name)
        {
            if (name != null && Parsed.TryGetValue(name, out var shapes)) return shapes;
            shapes = SvgParser.Parse(Source(name) ?? Svg["logo"]);
            if (name != null) Parsed[name] = shapes;
            return shapes;
        }

        /// <summary>One drawing step in 24-unit icon space.</summary>
        internal readonly struct Op
        {
            public Op(char kind, Vector2 a, Vector2 b = default, Vector2 c = default, float radius = 0f, float start = 0f,
                float end = 0f)
            {
                Kind = kind;
                A = a;
                B = b;
                C = c;
                Radius = radius;
                Start = start;
                End = end;
            }

            /// <summary>M move, L line, C cubic, Q quadratic, A arc (A = centre), Z close.</summary>
            public char Kind { get; }
            public Vector2 A { get; }
            public Vector2 B { get; }
            public Vector2 C { get; }
            public float Radius { get; }
            public float Start { get; }
            public float End { get; }
        }

        internal sealed class Shape
        {
            public readonly List<Op> Ops = new();

            /// <summary>0 no fill, 1 non-zero fill, 2 even-odd fill (inner sub-paths are holes).</summary>
            public int Fill;

            public bool Stroke = true;

            /// <summary>Its own stroke width in grid units, or 0 for the element's.</summary>
            public float Width;
        }

        /// <summary>Parses the SVG subset the icons use: path (all commands), circle and rect.</summary>
        private static class SvgParser
        {
            private static readonly Regex Element = new(@"<(path|circle|rect)\s([^>]*)/>");
            private static readonly Regex Attribute = new(@"([a-z]+)=""([^""]*)""");
            private static readonly Regex Token = new(@"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?");

            public static List<Shape> Parse(string svg)
            {
                var shapes = new List<Shape>();
                foreach (RegexMatch element in Element.Matches(svg))
                {
                    var attributes = new Dictionary<string, string>();
                    foreach (RegexMatch a in Attribute.Matches(element.Groups[2].Value)) attributes[a.Groups[1].Value] = a.Groups[2].Value;
                    var shape = new Shape();
                    switch (element.Groups[1].Value)
                    {
                        case "path":
                            PathData(attributes["d"], shape);
                            break;
                        case "circle":
                            var centre = new Vector2(F(attributes["cx"]), F(attributes["cy"]));
                            var r = F(attributes["r"]);
                            shape.Ops.Add(new Op('M', centre + new Vector2(r, 0f)));
                            shape.Ops.Add(new Op('A', centre, radius: r, start: 0f, end: Mathf.PI * 2f));
                            break;
                        case "rect":
                            Rect(F(attributes["x"]), F(attributes["y"]), F(attributes["width"]), F(attributes["height"]),
                                attributes.TryGetValue("rx", out var rx) ? F(rx) : 0f, shape);
                            break;
                    }
                    if (attributes.TryGetValue("fill", out var fill)) shape.Fill = fill == "eo" ? 2 : fill == "0" ? 0 : 1;
                    if (attributes.TryGetValue("stroke", out var stroke)) shape.Stroke = stroke != "0";
                    if (attributes.TryGetValue("sw", out var sw)) shape.Width = F(sw);
                    if (attributes.TryGetValue("dash", out var dash))
                    {
                        var parts = dash.Split(' ');
                        shape = Dashed(shape, F(parts[0]), F(parts.Length > 1 ? parts[1] : parts[0]));
                    }
                    shapes.Add(shape);
                }
                return shapes;
            }

            /// <summary>The shape's outline flattened and cut into dashes (lines only, stroked, never filled).</summary>
            private static Shape Dashed(Shape s, float on, float off)
            {
                var result = new Shape { Width = s.Width };
                var lines = new List<List<Vector2>>();
                List<Vector2> line = null;
                Vector2 start = default, current = default;
                foreach (var op in s.Ops)
                {
                    switch (op.Kind)
                    {
                        case 'M':
                            line = new List<Vector2> { op.A };
                            lines.Add(line);
                            start = current = op.A;
                            break;
                        case 'L':
                            line?.Add(op.A);
                            current = op.A;
                            break;
                        case 'C':
                            for (var k = 1; k <= 16; k++)
                            {
                                var t = k / 16f;
                                var u = 1f - t;
                                line?.Add(u * u * u * current + 3f * u * u * t * op.A + 3f * u * t * t * op.B + t * t * t * op.C);
                            }
                            current = op.C;
                            break;
                        case 'Q':
                            for (var k = 1; k <= 12; k++)
                            {
                                var t = k / 12f;
                                var u = 1f - t;
                                line?.Add(u * u * current + 2f * u * t * op.A + t * t * op.B);
                            }
                            current = op.B;
                            break;
                        case 'A':
                        {
                            var steps = Mathf.Max(4, Mathf.CeilToInt(Mathf.Abs(op.End - op.Start) / 0.2f));
                            for (var k = 1; k <= steps; k++)
                            {
                                var a = Mathf.Lerp(op.Start, op.End, k / (float)steps);
                                line?.Add(op.A + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * op.Radius);
                            }
                            current = line != null && line.Count > 0 ? line[line.Count - 1] : current;
                            break;
                        }
                        case 'Z':
                            line?.Add(start);
                            current = start;
                            break;
                    }
                }
                foreach (var points in lines)
                {
                    var drawing = true;
                    var left = on;
                    result.Ops.Add(new Op('M', points[0]));
                    for (var k = 1; k < points.Count; k++)
                    {
                        var a = points[k - 1];
                        var b = points[k];
                        var length = Vector2.Distance(a, b);
                        var walked = 0f;
                        while (length - walked > left)
                        {
                            walked += left;
                            var p = Vector2.Lerp(a, b, walked / length);
                            result.Ops.Add(new Op(drawing ? 'L' : 'M', p));
                            drawing = !drawing;
                            left = drawing ? on : off;
                        }
                        left -= length - walked;
                        if (drawing) result.Ops.Add(new Op('L', b));
                    }
                }
                return result;
            }

            private static void Rect(float x, float y, float w, float h, float r, Shape s)
            {
                r = Mathf.Min(r, w / 2f, h / 2f);
                s.Ops.Add(new Op('M', new Vector2(x + r, y)));
                s.Ops.Add(new Op('L', new Vector2(x + w - r, y)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + w - r, y + r), radius: r, start: -Mathf.PI / 2f, end: 0f));
                s.Ops.Add(new Op('L', new Vector2(x + w, y + h - r)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + w - r, y + h - r), radius: r, start: 0f, end: Mathf.PI / 2f));
                s.Ops.Add(new Op('L', new Vector2(x + r, y + h)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + r, y + h - r), radius: r, start: Mathf.PI / 2f, end: Mathf.PI));
                s.Ops.Add(new Op('L', new Vector2(x, y + r)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + r, y + r), radius: r, start: Mathf.PI, end: Mathf.PI * 1.5f));
                s.Ops.Add(new Op('Z', default));
            }

            private static void PathData(string d, Shape s)
            {
                var tokens = new List<string>();
                foreach (RegexMatch t in Token.Matches(d)) tokens.Add(t.Value);
                var i = 0;
                var command = 'M';
                Vector2 current = default, start = default, lastControl = default;
                var lastKind = ' ';
                while (i < tokens.Count)
                {
                    if (char.IsLetter(tokens[i][0])) command = tokens[i++][0];
                    var relative = char.IsLower(command);
                    var offset = relative ? current : Vector2.zero;
                    switch (char.ToUpperInvariant(command))
                    {
                        case 'M':
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            start = current;
                            s.Ops.Add(new Op('M', current));
                            command = relative ? 'l' : 'L'; // extra pairs after a move are lines
                            break;
                        case 'L':
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('L', current));
                            break;
                        case 'H':
                            current = new Vector2((relative ? current.x : 0f) + F(tokens[i++]), current.y);
                            s.Ops.Add(new Op('L', current));
                            break;
                        case 'V':
                            current = new Vector2(current.x, (relative ? current.y : 0f) + F(tokens[i++]));
                            s.Ops.Add(new Op('L', current));
                            break;
                        case 'C':
                        {
                            var c1 = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            var c2 = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('C', c1, c2, current));
                            lastControl = c2;
                            break;
                        }
                        case 'S':
                        {
                            var c1 = lastKind is 'C' or 'S' ? current * 2f - lastControl : current;
                            var c2 = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('C', c1, c2, current));
                            lastControl = c2;
                            break;
                        }
                        case 'Q':
                        {
                            var c = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('Q', c, current));
                            lastControl = c;
                            break;
                        }
                        case 'A':
                        {
                            var rx = F(tokens[i++]);
                            i += 2; // ry (icons use circular arcs) and x-axis rotation
                            var large = F(tokens[i++]) != 0f;
                            var sweep = F(tokens[i++]) != 0f;
                            var end = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            AddArc(s, current, end, rx, large, sweep);
                            current = end;
                            break;
                        }
                        case 'Z':
                            s.Ops.Add(new Op('Z', default));
                            current = start;
                            break;
                        default:
                            i++; // unknown command: skip a token rather than loop forever
                            break;
                    }
                    lastKind = char.ToUpperInvariant(command);
                }
            }

            /// <summary>SVG endpoint arc to centre form (circular arcs, no rotation).</summary>
            private static void AddArc(Shape s, Vector2 p1, Vector2 p2, float r, bool large, bool sweep)
            {
                var half = (p1 - p2) * 0.5f;
                var lambda = half.sqrMagnitude / (r * r);
                if (lambda > 1f) r *= Mathf.Sqrt(lambda);
                var sign = large != sweep ? 1f : -1f;
                var numerator = r * r * r * r - r * r * half.y * half.y - r * r * half.x * half.x;
                var denominator = r * r * half.y * half.y + r * r * half.x * half.x;
                var coefficient = sign * Mathf.Sqrt(Mathf.Max(0f, numerator / Mathf.Max(denominator, 1e-6f)));
                var centrePrime = new Vector2(coefficient * half.y, -coefficient * half.x);
                var centre = centrePrime + (p1 + p2) * 0.5f;
                var a0 = Mathf.Atan2(half.y - centrePrime.y, half.x - centrePrime.x);
                var a1 = Mathf.Atan2(-half.y - centrePrime.y, -half.x - centrePrime.x);
                var delta = a1 - a0;
                if (!sweep && delta > 0f) delta -= Mathf.PI * 2f;
                if (sweep && delta < 0f) delta += Mathf.PI * 2f;
                s.Ops.Add(new Op('A', centre, radius: r, start: a0, end: a0 + delta));
            }

            private static float F(string s) => float.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture);
        }
    }

    /// <summary>A vector icon that takes its colour from <see cref="Tint"/>.</summary>
    public sealed class IconElement : VisualElement
    {
        private static readonly CustomStyleProperty<Color> IconColor = new("--icon-color");

        private string _name;
        private Color _tint = Color.white;
        private Color _styleColor = Color.white;
        private bool _explicitTint, _hasStyleColor;

        public IconElement(string name, float strokeWidth = 1.7f)
        {
            _name = name;
            StrokeWidth = strokeWidth;
            pickingMode = PickingMode.Ignore;
            AddToClassList("icon");
            generateVisualContent += Draw;
            // Unless given a colour in code, an icon follows the stylesheet's --icon-color, so a
            // selected (amber) button can turn its icon dark.
            RegisterCallback<CustomStyleResolvedEvent>(OnStyleResolved);
        }

        private void OnStyleResolved(CustomStyleResolvedEvent e)
        {
            if (!e.customStyle.TryGetValue(IconColor, out var colour) || (_hasStyleColor && colour == _styleColor)) return;
            _styleColor = colour;
            _hasStyleColor = true;
            if (!_explicitTint) MarkDirtyRepaint();
        }

        public float StrokeWidth { get; }

        public string Name
        {
            get => _name;
            set
            {
                if (_name == value) return;
                _name = value;
                MarkDirtyRepaint();
            }
        }

        public Color Tint
        {
            get => _tint;
            set
            {
                if (_explicitTint && _tint == value) return;
                _tint = value;
                _explicitTint = true;
                MarkDirtyRepaint();
            }
        }

        private void Draw(MeshGenerationContext context)
        {
            var rect = contentRect;
            var scale = Mathf.Min(rect.width, rect.height) / 24f;
            if (scale <= 0f) return;
            var origin = rect.position + (rect.size - Vector2.one * 24f * scale) * 0.5f;
            var p = context.painter2D;
            p.strokeColor = _explicitTint || !_hasStyleColor ? _tint : _styleColor;
            p.lineWidth = StrokeWidth * scale;
            p.lineCap = LineCap.Round;
            p.lineJoin = LineJoin.Round;
            var colour = p.strokeColor;
            p.fillColor = colour;
            foreach (var shape in Icons.Get(_name))
            {
                p.lineWidth = (shape.Width > 0f ? shape.Width : StrokeWidth) * scale;
                p.BeginPath();
                foreach (var op in shape.Ops)
                {
                    switch (op.Kind)
                    {
                        case 'M': p.MoveTo(origin + op.A * scale); break;
                        case 'L': p.LineTo(origin + op.A * scale); break;
                        case 'C': p.BezierCurveTo(origin + op.A * scale, origin + op.B * scale, origin + op.C * scale); break;
                        case 'Q': p.QuadraticCurveTo(origin + op.A * scale, origin + op.B * scale); break;
                        case 'A':
                            p.Arc(origin + op.A * scale, op.Radius * scale, Angle.Radians(op.Start), Angle.Radians(op.End),
                                op.End >= op.Start ? ArcDirection.Clockwise : ArcDirection.CounterClockwise);
                            break;
                        case 'Z': p.ClosePath(); break;
                    }
                }
                if (shape.Fill > 0) p.Fill(shape.Fill == 2 ? FillRule.OddEven : FillRule.NonZero);
                if (shape.Stroke) p.Stroke();
            }
        }
    }
}
