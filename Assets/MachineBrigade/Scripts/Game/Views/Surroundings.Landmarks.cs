using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 33 L3, the view side: the landmark models the map's "landmarks" data names but no map prop is (Capital's
    /// palace and station, Ember Ridge's cooling tower, Hollow Dam's dam face, Salt Flats' survey beacon, Veyra's clock
    /// tower, the churches and other prop looks the Siege and long files lack) and Ironport's lighthouse out at sea.
    /// Tools/maps/map_dressing.py finds each a spot (map_dressing.json "landmarks": off the props, the capture circles,
    /// rallies, slots, gates, roads, rails and the sea, on as little drivable ground as it can) and they are drawn
    /// instanced like the rest of the scenery: no collider, no sight blocking, never in the simulation (DECISIONS
    /// "Prompt 33 L2 view / L7"). One on drivable ground (<c>onPlay</c>) is driven through.
    /// </summary>
    public sealed partial class Surroundings
    {
        /// <summary>Landmark models stood (for the scenery log).</summary>
        public int LandmarksPlaced { get; private set; }

        private readonly System.Collections.Generic.List<(Vector2 centre, float radius)> _landmarkZones = new();

        /// <summary>The landmarks' ground, read before the scatter so nothing else stands in them.</summary>
        private void PrepareLandmarks(SimWorld world)
        {
            foreach (var landmark in MapDressing.LandmarksFor(world.Map.Id))
                _landmarkZones.Add((new Vector2(landmark.x, landmark.z), landmark.radius > 0f ? landmark.radius : 6f));
        }

        private bool InLandmark(Vector2 p, float margin)
        {
            foreach (var (centre, radius) in _landmarkZones)
                if ((p - centre).sqrMagnitude < (radius + margin) * (radius + margin)) return true;
            return false;
        }

        private void PlaceLandmarks(ModelLibrary models, SimWorld world)
        {
            foreach (var landmark in MapDressing.LandmarksFor(world.Map.Id))
            {
                if (string.IsNullOrEmpty(landmark.model) || !models.Has(landmark.model)) continue;
                var at = new Vector2(landmark.x, landmark.z);
                var scale = landmark.scale > 0f ? landmark.scale : 1f;
                // Out beyond the edge it stands on the outer ground's own height; on the map, on its flat ground.
                var height = Beyond(at) > 1f ? Height(at) : 0f;
                Add(models, landmark.model, at, landmark.yaw, scale, height);
                LandmarksPlaced++;
            }
        }
    }
}
