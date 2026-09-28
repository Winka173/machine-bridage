using System.Collections.Generic;
using MachineBrigade.Sim;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Device check for big battles (debug flag -mb-crowd, or -mb-crowd=N for N a side): two
    /// armies of fifty facing each other across the view, topped up as they lose vehicles, so
    /// a hundred vehicles fight in view for as long as the check runs. With -mb-perf it measures
    /// the renderer under the load of a Siege or a big operation; -mb-zoom=42 sets the view,
    /// -mb-lod=N and -mb-no-lod compare the detail levels.
    /// </summary>
    internal sealed class CrowdCheck
    {
        /// <summary>A mix of the roster: tanks, carriers, artillery, air defence and helicopters.</summary>
        private static readonly string[] Roster =
        {
            "main_battle_tank", "light_tank", "heavy_tank", "apc", "ifv", "scout_jeep", "artillery", "mlrs", "aa_vehicle",
            "tank_destroyer", "armored_car", "sam_launcher", "attack_helicopter", "grad_truck", "flame_tank", "heavy_aa",
            "mortar_carrier", "howitzer", "twin_tank", "rocket_technical",
        };

        private const float Gap = 7f;
        private const int PerTick = 8;

        private readonly List<string> _roster = new();
        private readonly int _perSide;
        private readonly Vector2 _centre;
        private float _nextAt;
        private int _next;

        private CrowdCheck(SimWorld world, Vector3 focus, int perSide)
        {
            foreach (var id in Roster)
                if (world.Catalog.Vehicles.ContainsKey(id)) _roster.Add(id);
            _perSide = perSide;
            _centre = new Vector2(focus.x, focus.z);
        }

        /// <summary>The check when -mb-crowd is set (outside the menu), else null.</summary>
        public static CrowdCheck Create(SimWorld world, Vector3 focus)
        {
            if (!DebugFlags.Has("-mb-crowd") && DebugFlags.Value("-mb-crowd=") == null) return null;
            var perSide = int.TryParse(DebugFlags.Value("-mb-crowd="), out var n) ? Mathf.Clamp(n, 1, 200) : 50;
            return new CrowdCheck(world, focus, perSide);
        }

        /// <summary>Tops both sides up to strength, a few vehicles a step so no frame stalls.</summary>
        public void Tick(SimWorld world, float now)
        {
            if (now < _nextAt || _roster.Count == 0) return;
            _nextAt = now + 0.5f;
            // Across the screen: the camera looks north-east, so its right is (1, 1)/sqrt 2.
            var across = Vector2.Normalize(new Vector2(1f, 1f));
            var along = new Vector2(across.Y, -across.X);
            for (var team = 0; team <= 1; team++)
            {
                var missing = _perSide - world.CountAlive(team);
                var side = team == 0 ? -1f : 1f;
                for (var i = 0; i < Mathf.Min(missing, PerTick); i++)
                {
                    var slot = _next++;
                    var row = slot % 10 - 4.5f;
                    var rank = (slot / 10) % 5;
                    var at = _centre + across * (side * (14f + rank * Gap)) + along * (row * Gap);
                    var heading = Mathf.Atan2(across.X, across.Y) + (team == 0 ? 0f : Mathf.PI);
                    world.SpawnVehicle(_roster[slot % _roster.Count], team, at, heading);
                }
            }
        }
    }
}
