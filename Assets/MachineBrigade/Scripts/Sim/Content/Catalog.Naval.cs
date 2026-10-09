#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    public sealed partial class Catalog
    {
        /// <summary>Prompt 16's ship fields: "naval", "salvo", "cruise", "craft", "fleet", "air", "navalOnly".</summary>
        private static void ParseNaval(JsonObject v, VehicleDef def)
        {
            def.NavalOnly = v.Bool("navalOnly", false);
            if (v.Has("naval"))
            {
                var n = v.Object("naval");
                def.Naval = new NavalDef
                {
                    Role = n.Enum("role", NavalRole.Flagship),
                    Lanes = n.Has("lanes") ? n.StringArray("lanes") : n.Has("lane") ? new[] { n.String("lane") } : new[] { "far" },
                    EscapePhase = n.Int("escapePhase", -1),
                    EscapeSpeed = Math.Clamp(n.Float("escapeSpeed", 0.6f), 0.1f, 2f),
                    EscapeRun = n.Float("escapeRun", 150f),
                    Station = n.Float("station", 0f),
                    Patrol = n.Has("patrol") ? n.String("patrol") : null,
                    Band = n.Has("band") && n.FloatArray("band") is { Count: 2 } band ? new[] { band[0], band[1] } : null,
                    DashW = n.Float("dashW", 48f),
                    DashEvery = n.Float("dashEvery", 26f),
                    DashHold = n.Float("dashHold", 7f),
                    Slack = n.Float("slack", 2f),
                    PassIn = MathF.Max(0f, n.Float("passIn", 0f)),
                    PassOut = MathF.Max(0f, n.Float("passOut", 0f)),
                };
            }
            if (v.Has("salvo"))
            {
                var s = v.Object("salvo");
                def.Salvo = new SalvoDef
                {
                    Every = s.Float("every", 10f), First = s.Float("first", 8f), Warn = s.Float("warn", 2.6f), Shells = Math.Max(1, s.Int("shells", 3)),
                    Damage = s.Float("damage", 300f), Radius = s.Float("radius", 7f), Spread = s.Float("spread", 16f), Range = s.Float("range", 150f),
                    Sweep = s.Float("sweep", 18f), BlindScatter = s.Float("blindScatter", 2.2f),
                    Weapon = s.Has("weapon") ? s.String("weapon") : null, Warning = s.Has("warning") ? s.String("warning") : null,
                    Edge = Math.Max(0f, s.Float("edge", 0f)),
                };
            }
            if (v.Has("cruise"))
            {
                var c = v.Object("cruise");
                def.Cruise = new CruiseDef
                {
                    Every = c.Float("every", 48f), First = c.Float("first", 18f), Phase = c.Int("phase", 1), Warn = c.Float("warn", 4.5f),
                    Damage = c.Float("damage", 520f), Radius = c.Float("radius", 16f), Final = c.Int("final", 4),
                    Weapon = c.Has("weapon") ? c.String("weapon") : null, Warning = c.Has("warning") ? c.String("warning") : null,
                    ImpactTier = c.Has("impactTier") ? (ExplosionTier?)c.Enum<ExplosionTier>("impactTier") : null,
                };
            }
            if (v.Has("craft"))
            {
                var c = v.Object("craft");
                def.Craft = new CraftDef
                {
                    Unit = c.Has("unit") ? c.String("unit") : "landing_craft", Carries = c.Has("carries") ? c.StringArray("carries") : Array.Empty<string>(),
                    Per = Math.Max(1, c.Int("per", 2)), Every = c.Float("every", 42f), First = c.Float("first", 6f), Phase = c.Int("phase", 1),
                    Max = c.Int("max", 3),
                };
            }
            if (v.Has("fleet"))
            {
                var fleet = new List<FleetShipDef>();
                foreach (var f in v.Array("fleet"))
                    fleet.Add(new FleetShipDef
                    {
                        Unit = f.String("unit"), Count = Math.Max(1, f.Int("count", 1)), Station = f.Float("at", 0f),
                        Abeam = f.Has("abeam") ? f.Float("abeam") : float.NaN,
                    });
                def.Fleet = fleet;
            }
            if (v.Has("air"))
            {
                var air = new List<AirWaveDef>();
                foreach (var a in v.Array("air"))
                    air.Add(new AirWaveDef { Phase = a.Int("phase", 1), Units = a.StringArray("units") });
                def.AirWaves = air;
            }
        }

        /// <summary>Every ship's fleet, craft and air wave names a vehicle that exists.</summary>
        private void CheckNaval()
        {
            foreach (var def in _vehicles.Values)
            {
                var names = new List<string>();
                foreach (var f in def.Fleet) names.Add(f.Unit);
                foreach (var a in def.AirWaves) names.AddRange(a.Units);
                if (def.Craft != null)
                {
                    names.Add(def.Craft.Unit);
                    names.AddRange(def.Craft.Carries);
                }
                foreach (var id in names)
                    if (!_vehicles.ContainsKey(id)) throw new FormatException($"{def.Id}: its fleet names an unknown vehicle '{id}'.");
            }
        }
    }
}
