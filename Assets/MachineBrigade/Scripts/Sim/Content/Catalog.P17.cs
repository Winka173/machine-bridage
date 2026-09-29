#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 17 C: the new units' and towers' data (balance.json "dome", "deploy", "wingman", "relay", "ramp", "swarm").</summary>
    public sealed partial class Catalog
    {
        private static void ParseP17(JsonObject v, VehicleDef def)
        {
            if (v.Has("dome"))
            {
                var d = v.Object("dome");
                def.Dome = new DomeDef(d.Float("radius"), d.Float("hp"), d.Float("recharge", 20f));
            }
            if (v.Has("deploy"))
            {
                var d = v.Object("deploy");
                def.Deploy = new DeployDef
                {
                    Seconds = Math.Max(0.5f, d.Float("seconds", 3f)),
                    FrontUp = Math.Clamp(d.Int("front", 2), 0, ArmourLevels.Max),
                    Range = Math.Clamp(d.Float("range", 1.3f), 1f, 3f),
                    Arc = Math.Clamp(d.Float("arc", 45f), 5f, 180f) * MathF.PI / 180f,
                };
            }
            if (v.Has("wingman"))
            {
                var w = v.Object("wingman");
                def.Wingman = new WingmanDef
                {
                    Follow = Math.Max(10f, w.Float("follow", 120f)),
                    Decoy = Math.Max(1f, w.Float("decoy", 25f)),
                    Pull = Math.Clamp(w.Float("pull", 0.4f), 0f, 1f),
                };
            }
            if (v.Has("relay"))
            {
                var r = v.Object("relay");
                def.Relay = new RelayDef
                {
                    Income = Math.Max(0f, r.Float("income", 0.1f)),
                    Second = Math.Max(0f, r.Float("second", 0.06f)),
                    Quiet = Math.Max(0f, r.Float("quiet", 5f)),
                };
            }
            def.AirCapFree = v.Bool("airCapFree", false);
            def.Sead = v.Bool("sead", false);
        }

        private static void ParseWeaponP17(JsonObject w, WeaponDef def)
        {
            if (w.Has("ramp"))
            {
                var r = w.Object("ramp");
                def.Ramp = new RampDef
                {
                    From = Math.Clamp(r.Float("from", 0.3f), 0f, 5f),
                    To = Math.Clamp(r.Float("to", 2f), 0f, 5f),
                    Seconds = Math.Max(0.1f, r.Float("seconds", 6f)),
                    Grace = Math.Max(0.1f, r.Float("grace", 1.5f)),
                };
            }
            def.SwarmReach = Math.Max(0f, w.Float("swarm", 0f));
        }
    }
}
