#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 31 L3: a mission's prebuilt ground states as campaign.json writes them (Tools/campaign/nav_states.py checks them
    /// over the map data): "navStates": [{"id": "mill_gate", "initial": "open", "states": [{"name": "open"}, {"name": "shut",
    /// "blocks": [{"x": 46, "z": -2, "w": 8, "d": 2, "clearance": 1.5}]}]}]. An event switches one with the params "navSite" and
    /// "navState".
    /// </summary>
    public static class NavSiteDefs
    {
        internal static IReadOnlyList<NavSiteDef> Parse(JsonObject mission, string key)
        {
            var list = new List<NavSiteDef>();
            foreach (var o in mission.Array(key))
            {
                var states = new List<NavStateDef>();
                foreach (var s in o.Array("states"))
                {
                    var blocks = new List<NavBlock>();
                    if (s.Has("blocks"))
                        foreach (var b in s.Array("blocks"))
                        {
                            var w = b.Float("w");
                            var d = b.Float("d");
                            if (!(w > 0f) || !(d > 0f)) throw new FormatException($"{b.Path}: a block needs a positive w and d.");
                            blocks.Add(new NavBlock(new Vector2(b.Float("x"), b.Float("z")), w, d, b.Float("clearance", SimWorld.ObstacleClearance)));
                        }
                    states.Add(new NavStateDef(s.String("name"), blocks));
                }
                try
                {
                    list.Add(new NavSiteDef(o.String("id"), states, o.OptionalString("initial")));
                }
                catch (ArgumentException e)
                {
                    throw new FormatException($"{o.Path}: {e.Message}");
                }
            }
            return list;
        }
    }
}
