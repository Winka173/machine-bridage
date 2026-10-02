#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 33 L3: a landmark seen from far off (a lighthouse, a water tower, a church, a crane ...), with its id and its
    /// names in both languages for the dialogue (prompt 30), and the words the dialogue already uses for it.
    /// </summary>
    public sealed class LandmarkDef
    {
        public LandmarkDef(string id, string kind, Vector2 position, string nameEn, string nameVi, IReadOnlyList<string> aliases, string? prop, string? model)
        {
            Id = id;
            Kind = kind;
            Position = position;
            NameEn = nameEn;
            NameVi = nameVi;
            Aliases = aliases;
            Prop = prop;
            Model = model;
        }

        /// <summary>landmarkId, "battlefield.name" (the same on every file of the battlefield).</summary>
        public string Id { get; }

        public string Kind { get; }
        public Vector2 Position { get; }
        public string NameEn { get; }
        public string NameVi { get; }

        /// <summary>How the prompt 30 dialogue already calls it ("the lighthouse", "the dam").</summary>
        public IReadOnlyList<string> Aliases { get; }

        /// <summary>The map's own prop that is it, or null.</summary>
        public string? Prop { get; }

        /// <summary>No prop of the map is it: what the view should stand there (view only), or null.</summary>
        public string? Model { get; }

        /// <summary>Its name in a language ("vi" or anything else for English).</summary>
        public string Name(string language) => language == "vi" ? NameVi : NameEn;

        internal static IReadOnlyList<LandmarkDef> ParseAll(JsonObject root)
        {
            if (!root.Has("landmarks")) return Array.Empty<LandmarkDef>();
            var list = new List<LandmarkDef>();
            foreach (var l in root.Array("landmarks"))
            {
                var name = l.Object("name");
                list.Add(new LandmarkDef(l.String("id"), l.OptionalString("kind") ?? "", new Vector2(l.Float("x"), l.Float("z")), name.String("en"),
                    name.String("vi"), l.Has("aliases") ? l.StringArray("aliases") : Array.Empty<string>(), l.OptionalString("prop"), l.OptionalString("model")));
            }
            return list;
        }
    }

    public sealed partial class MapDefinition
    {
        /// <summary>Prompt 33 L3: the static terrain tags' zones (Tools/maps/terrain.py); empty: every cell NORMAL.</summary>
        public IReadOnlyList<TerrainZoneDef> TerrainZones { get; internal set; } = Array.Empty<TerrainZoneDef>();

        /// <summary>Prompt 33 L3: the battlefield's 2-3 landmarks.</summary>
        public IReadOnlyList<LandmarkDef> Landmarks { get; internal set; } = Array.Empty<LandmarkDef>();

        /// <summary>Prompt 33 L3: why the file is asymmetric on purpose (a Siege or long battlefield's roles), or null (a versus file).</summary>
        public string? AsymmetryReason { get; internal set; }

        /// <summary>The landmark by its id, or null.</summary>
        public LandmarkDef? Landmark(string id)
        {
            foreach (var l in Landmarks)
                if (l.Id == id) return l;
            return null;
        }

        private static string? AsymmetryOf(JsonObject root) =>
            root.Has("asymmetry") && root.Object("asymmetry").Bool("intended", false) ? root.Object("asymmetry").OptionalString("reason") ?? "" : null;
    }
}
