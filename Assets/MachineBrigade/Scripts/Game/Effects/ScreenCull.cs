using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Is a point on (or just off) the screen? Effects far outside the view are skipped: the
    /// shared particle systems span the whole map, so the engine cannot cull what they emit, and
    /// every off-screen fireball would still cost vertex work and particle simulation.
    /// </summary>
    internal sealed class ScreenCull
    {
        private readonly Camera _camera;

        public ScreenCull(Camera camera) => _camera = camera;

        /// <param name="margin">Extra room around the screen, as a fraction of it (smoke rises into view).</param>
        public bool Visible(Vector3 point, float margin = 0.2f)
        {
            if (_camera == null) return true;
            var v = _camera.WorldToViewportPoint(point);
            return v.x > -margin && v.x < 1f + margin && v.y > -margin && v.y < 1f + margin;
        }
    }
}
