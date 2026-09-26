#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Where a team gathers: its drop zone and retreat destination.</summary>
    public readonly struct TeamStart
    {
        public TeamStart(int team, Vector2 rally)
        {
            Team = team;
            Rally = rally;
        }

        public int Team { get; }
        public Vector2 Rally { get; }
    }

    public readonly struct PropPlacement
    {
        public PropPlacement(string defId, Vector2 position, int rotation)
        {
            DefId = defId;
            Position = position;
            Rotation = rotation;
        }

        public string DefId { get; }
        public Vector2 Position { get; }

        /// <summary>Degrees; one of 0, 90, 180, 270 so footprints stay grid-aligned.</summary>
        public int Rotation { get; }
    }

    public readonly struct UnitPlacement
    {
        public UnitPlacement(string defId, int team, Vector2 position, float heading)
        {
            DefId = defId;
            Team = team;
            Position = position;
            Heading = heading;
        }

        public string DefId { get; }
        public int Team { get; }
        public Vector2 Position { get; }

        /// <summary>Radians.</summary>
        public float Heading { get; }
    }

    /// <summary>
    /// A battlefield as data. The map is a square of <see cref="Size"/> metres centred on the
    /// origin, so coordinates run from -HalfSize to +HalfSize on both axes.
    /// </summary>
    public sealed class MapDefinition
    {
        public MapDefinition(string id, float size, IReadOnlyList<TeamStart> teams,
            IReadOnlyList<PropPlacement> props, IReadOnlyList<UnitPlacement> units)
        {
            Id = string.IsNullOrWhiteSpace(id) ? throw new ArgumentException("Map id must not be empty.") : id;
            Size = float.IsFinite(size) && size > 0 ? size : throw new ArgumentException($"Map '{id}': size must be positive.");
            Teams = teams;
            Props = props;
            Units = units;
        }

        public string Id { get; }
        public float Size { get; }
        public float HalfSize => Size * 0.5f;
        public IReadOnlyList<TeamStart> Teams { get; }
        public IReadOnlyList<PropPlacement> Props { get; }
        public IReadOnlyList<UnitPlacement> Units { get; }

        public bool Contains(Vector2 point) =>
            MathF.Abs(point.X) <= HalfSize && MathF.Abs(point.Y) <= HalfSize;

        public static MapDefinition FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "map");
            var id = root.String("id");
            var size = root.Float("size");

            var teams = new List<TeamStart>();
            foreach (var t in root.Array("teams"))
                teams.Add(new TeamStart(t.Int("team", 0), new Vector2(t.Float("x"), t.Float("z"))));

            var props = new List<PropPlacement>();
            foreach (var p in root.Array("props"))
            {
                var rotation = p.Int("rot", 0);
                if (rotation % 90 != 0) throw new FormatException($"{p.Path}.rot: must be a multiple of 90.");
                props.Add(new PropPlacement(p.String("def"), new Vector2(p.Float("x"), p.Float("z")), ((rotation % 360) + 360) % 360));
            }

            var units = new List<UnitPlacement>();
            foreach (var u in root.Array("units"))
            {
                units.Add(new UnitPlacement(u.String("def"), u.Int("team", 0), new Vector2(u.Float("x"), u.Float("z")),
                    SimMath.DegToRad(u.Float("heading", 0f))));
            }

            return new MapDefinition(id, size, teams, props, units);
        }
    }
}
