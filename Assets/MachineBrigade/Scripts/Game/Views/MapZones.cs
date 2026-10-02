using MachineBrigade.Game.CameraControl;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>The four zones of a battlefield (prompt 33 L1), counted outwards from the map rectangle's edge.</summary>
    public enum MapZone
    {
        /// <summary>The map itself: navigation, objectives, bases, cover, gameplay props.</summary>
        Play,

        /// <summary>12-20 m past the edge: transition (berms, slopes, shore), decoration only.</summary>
        Edge,

        /// <summary>Past the band, as wide as the widest camera frame + 15 %: decoration only, no collider, no vision.</summary>
        Ring,

        /// <summary>Beyond the ring: the coarse range, far sea and islands, the horizon ground and the fog.</summary>
        Horizon,
    }

    /// <summary>
    /// The ground the battle camera can show (prompt 33 L1). The camera is orthographic at a fixed tilt and a fixed yaw
    /// per map shape, and its focus is clamped to the map rectangle; so the furthest it can see past an edge is the
    /// frame's half-extent along that axis with the focus on the edge: half-height zoom / sin(tilt) up the screen,
    /// zoom x aspect across it, turned by the yaw. The outer ring is that, at the furthest zoom and the widest supported
    /// screen, plus <see cref="Pad"/>.
    /// </summary>
    public static class CameraFrame
    {
        /// <summary>The supported screen shapes, narrowest to widest: 4:3 tablets, 16:9, 20:9 phones.</summary>
        public static readonly float[] Aspects = { 4f / 3f, 16f / 9f, 20f / 9f };

        /// <summary>The safety margin on the widest frame.</summary>
        public const float Pad = 0.15f;

        /// <summary>The furthest the player zooms out (orthographic half-height) on a square or a long map.</summary>
        public static float MaxZoom(bool longMap) => longMap ? Match.MatchRunner.LongMaxZoom : RtsCamera.PlayerMaxZoom;

        /// <summary>The yaw the battle camera looks along on a square or a long map.</summary>
        public static float Yaw(bool longMap) => longMap ? RtsCamera.LongYaw : RtsCamera.SquareYaw;

        /// <summary>
        /// Half-extents along world x and z of the ground an orthographic frame shows round its focus. With
        /// <paramref name="rotates"/> (a camera the player turns) every yaw is covered: the frame's half-diagonal both ways.
        /// </summary>
        public static Vector2 Reach(float yawDegrees, float tiltDegrees, float zoom, float aspect, bool rotates = false)
        {
            var across = zoom * aspect;
            var up = zoom / Mathf.Sin(tiltDegrees * Mathf.Deg2Rad);
            if (rotates)
            {
                var r = Mathf.Sqrt(across * across + up * up);
                return new Vector2(r, r);
            }
            var yaw = yawDegrees * Mathf.Deg2Rad;
            float c = Mathf.Cos(yaw), s = Mathf.Sin(yaw);
            return new Vector2(Mathf.Abs(across * c) + Mathf.Abs(up * s), Mathf.Abs(across * s) + Mathf.Abs(up * c));
        }

        /// <summary>The widest reach past the edges (x sides, z ends) over every supported screen, at the furthest zoom.</summary>
        public static Vector2 WidestReach(bool longMap)
        {
            var widest = Vector2.zero;
            foreach (var aspect in Aspects)
            {
                var r = Reach(Yaw(longMap), RtsCamera.TiltDegrees, MaxZoom(longMap), aspect, RtsCamera.Rotates);
                widest = Vector2.Max(widest, r);
            }
            // A square map's ring is the same all round (its yaw is diagonal, so x and z agree anyway).
            if (!longMap) widest = Vector2.one * Mathf.Max(widest.x, widest.y);
            return widest;
        }

        /// <summary>The outer ring's width past the x sides and the z ends: the widest reach + 15 %, whole metres up.</summary>
        public static Vector2 RingWidth(bool longMap)
        {
            var reach = WidestReach(longMap) * (1f + Pad);
            return new Vector2(Mathf.Ceil(reach.x - 1e-4f), Mathf.Ceil(reach.y - 1e-4f));
        }
    }

    /// <summary>One map's zones: the rectangle, the edge band and the ring per axis (prompt 33 L1).</summary>
    public readonly struct MapZones
    {
        public MapZones(Vector2 centre, float halfX, float halfZ, float edgeBand, float ringX, float ringZ)
        {
            Centre = centre;
            HalfX = halfX;
            HalfZ = halfZ;
            EdgeBand = edgeBand;
            RingX = ringX;
            RingZ = ringZ;
        }

        /// <summary>The zones of <paramref name="map"/> with its edge band (clamped to 12-20 m) and the camera's ring.</summary>
        public static MapZones For(MapDefinition map, float edgeBand)
        {
            var ring = CameraFrame.RingWidth(map.IsLong);
            return new MapZones(new Vector2(map.Centre.X, map.Centre.Y), map.Width * 0.5f, map.Length * 0.5f,
                Mathf.Clamp(edgeBand, MinBand, MaxBand), ring.x, ring.y);
        }

        public const float MinBand = 12f, MaxBand = 20f;

        public Vector2 Centre { get; }
        public float HalfX { get; }
        public float HalfZ { get; }
        public float EdgeBand { get; }
        public float RingX { get; }
        public float RingZ { get; }

        /// <summary>The outer ring's far edge, as half-extents round the centre.</summary>
        public float OuterX => HalfX + EdgeBand + RingX;
        public float OuterZ => HalfZ + EdgeBand + RingZ;

        /// <summary>Metres past the edge where the ring's far half begins: HLOD stand-ins replace full models beyond it.</summary>
        public float HlodStart => EdgeBand + 0.5f * Mathf.Min(RingX, RingZ);

        /// <summary>How far a point is outside the map rectangle (negative inside): its larger overshoot along x and z.</summary>
        public float Beyond(Vector2 p) => Mathf.Max(Mathf.Abs(p.x - Centre.x) - HalfX, Mathf.Abs(p.y - Centre.y) - HalfZ);

        /// <summary>Inside the outer ring's far edge.</summary>
        public bool InsideOuter(Vector2 p) => Mathf.Abs(p.x - Centre.x) <= OuterX && Mathf.Abs(p.y - Centre.y) <= OuterZ;

        public MapZone ZoneOf(Vector2 p)
        {
            var beyond = Beyond(p);
            if (beyond <= 0f) return MapZone.Play;
            if (beyond < EdgeBand) return MapZone.Edge;
            return InsideOuter(p) ? MapZone.Ring : MapZone.Horizon;
        }

        /// <summary>Ground area (m²) of the rectangle grown by <paramref name="d"/> past the edge (kept inside the outer edge).</summary>
        public float AreaWithin(float d)
        {
            var x = HalfX + Mathf.Min(Mathf.Max(d, 0f), EdgeBand + RingX);
            var z = HalfZ + Mathf.Min(Mathf.Max(d, 0f), EdgeBand + RingZ);
            return 4f * x * z;
        }
    }
}
