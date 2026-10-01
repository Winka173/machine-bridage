#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    // Prompt 25 F2 batch A (DECISIONS 25F2-A): the data of the balance sheet's new units and structures ("Đề xuất thêm",
    // "Công trình mới"). Each class is one mechanism of the sheet's "Cơ chế" column, read from balance.json by
    // Catalog.ParseP25A and run by Abilities.FieldWorksSystem and CombatSystem.P25A.

    /// <summary>A blast wall (Hesco line): its side's towers within <see cref="Radius"/> behind it take <see cref="Cut"/> less direct fire.</summary>
    public sealed class BlastWallDef
    {
        public float Radius { get; internal set; } = 8f;
        public float Cut { get; internal set; } = 0.3f;

        /// <summary>How far off the line from the tower to the shooter the wall may stand and still cover it (radians, half cone).</summary>
        public float Cone { get; internal set; } = 50f * MathF.PI / 180f;
    }

    /// <summary>An inflatable decoy: it passes for <see cref="Mimic"/> until a scout, a radar or a UAV scan of the enemy's looks at it.</summary>
    public sealed class DecoyDef
    {
        public string Mimic { get; internal set; } = "gun_turret";
    }

    /// <summary>A fire-control centre: its side's towers within <see cref="Radius"/> hit <see cref="Damage"/> harder and gang up on one target.</summary>
    public sealed class FireControlDef
    {
        public float Radius { get; internal set; } = 30f;
        public float Damage { get; internal set; } = 0.12f;

        /// <summary>A linked tower weighs a target another linked tower is on this many times more.</summary>
        public float Focus { get; internal set; } = 2f;
    }

    /// <summary>A searchlight: at night and in the murk its side sees everything within <see cref="Radius"/>, and enemies there shoot <see cref="Dazzle"/> worse.</summary>
    public sealed class SearchlightDef
    {
        public float Radius { get; internal set; } = 35f;
        public float Dazzle { get; internal set; } = 0.2f;
    }

    /// <summary>A barrage balloon: enemy aircraft within <see cref="Radius"/> bomb with <see cref="Scatter"/> more spread; helicopters keep out.</summary>
    public sealed class BalloonDef
    {
        public float Radius { get; internal set; } = 40f;
        public float Scatter { get; internal set; } = 0.5f;
    }

    /// <summary>A visual jammer: enemies see nothing within <see cref="Radius"/> of it from further than <see cref="Close"/>, unless they are scouts.</summary>
    public sealed class SightJammerDef
    {
        public float Radius { get; internal set; } = 35f;
        public float Close { get; internal set; } = 15f;
    }

    /// <summary>A troop shelter: its side's vehicles within <see cref="Radius"/> take <see cref="Cut"/> less from lobbed rounds, bombs and strikes.</summary>
    public sealed class ShelterDef
    {
        public float Radius { get; internal set; } = 15f;
        public float Cut { get; internal set; } = 0.5f;
    }

    /// <summary>A flare tower: every <see cref="Every"/> s in the dark it lights <see cref="Radius"/> m round a point up to <see cref="Range"/> m off, for <see cref="Seconds"/> s.</summary>
    public sealed class FlareDef
    {
        public float Every { get; internal set; } = 15f;
        public float Range { get; internal set; } = 40f;
        public float Radius { get; internal set; } = 30f;
        public float Seconds { get; internal set; } = 15f;
    }

    /// <summary>A high-power microwave: every <see cref="Cooldown"/> s it downs every enemy drone in a cone of <see cref="Arc"/> (half, radians) out to <see cref="Range"/>.</summary>
    public sealed class MicrowaveDef
    {
        public float Range { get; internal set; } = 30f;
        public float Arc { get; internal set; } = 30f * MathF.PI / 180f;
        public float Cooldown { get; internal set; } = 8f;
    }

    /// <summary>An interceptor-drone launcher's hunt: an enemy drone round flying at anything within <see cref="Reach"/> takes one of its drones (the main weapon's cooldown).</summary>
    public sealed class DroneHuntDef
    {
        public float Reach { get; internal set; } = 60f;
    }

    /// <summary>A card that may be dropped by parachute where its side sees: <see cref="Proxy"/> falls from <see cref="Height"/> m for <see cref="Fall"/> s (a low-altitude target), then lands the vehicle.</summary>
    public sealed class ParadropDef
    {
        public string Proxy { get; internal set; } = "";
        public float Fall { get; internal set; } = 6f;
        public float Height { get; internal set; } = 30f;

        /// <summary>No drop closer than this to an enemy HQ (its base).</summary>
        public float BaseKeepOut { get; internal set; } = 45f;
    }

    /// <summary>A high-speed reconnaissance pass: one straight run across the map, showing a strip <see cref="Width"/> m wide for <see cref="Seconds"/> s (stealth too), then it leaves.</summary>
    public sealed class ReconPassDef
    {
        public float Width { get; internal set; } = 60f;
        public float Seconds { get; internal set; } = 20f;
    }

    /// <summary>What a weapon made for small fliers may take (the anti-drone laser, the interceptor drones).</summary>
    public enum Prey
    {
        /// <summary>Anything its targets allow.</summary>
        Any,

        /// <summary>Drones only.</summary>
        Drones,

        /// <summary>Drones and helicopters.</summary>
        Rotors,
    }

    public sealed partial class VehicleDef
    {
        public BlastWallDef? BlastWall { get; internal set; }
        public DecoyDef? Decoy { get; internal set; }
        public FireControlDef? FireControl { get; internal set; }
        public SearchlightDef? Searchlight { get; internal set; }
        public BalloonDef? Balloon { get; internal set; }
        public SightJammerDef? SightJammer { get; internal set; }
        public ShelterDef? Shelter { get; internal set; }
        public FlareDef? Flares { get; internal set; }
        public MicrowaveDef? Microwave { get; internal set; }
        public DroneHuntDef? DroneHunt { get; internal set; }
        public ParadropDef? Paradrop { get; internal set; }
        public ReconPassDef? ReconPass { get; internal set; }

        /// <summary>A towed gun's traverse: its gun stays within this many radians of its front, either way (0: all round).</summary>
        public float TurretArc { get; internal set; }

        /// <summary>A radar's sight: it sees through smoke out to its vision (the radar-guided ATGM carrier).</summary>
        public bool SmokeSight { get; internal set; }

        /// <summary>Its vision once it has stood still <see cref="StillAfter"/> s (a scout's mast up; 0: none).</summary>
        public float StillVision { get; internal set; }

        public float StillAfter { get; internal set; } = 2f;

        /// <summary>A stand-off bomber: it turns away once its glide bombs are in reach instead of flying over the target.</summary>
        public bool GlideRelease { get; internal set; }

        /// <summary>The altitude tier it flies at (a high-flying reconnaissance jet: only the high-tier weapons reach it); None: the ordinary rules.</summary>
        public AltitudeTier FlightTier { get; internal set; }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>A dual-purpose gun's reach against the ground, when shorter than its reach in the air (0: its range).</summary>
        public float GroundRange { get; internal set; }

        /// <summary>No shot at anything closer than this (a long-range air-to-air missile in a turning fight); 0: none.</summary>
        public float MinReach { get; internal set; }

        /// <summary>A heavy air-burst gun: it goes for tight groups of aircraft and big aircraft first.</summary>
        public bool GroupPriority { get; internal set; }

        /// <summary>A long-range interceptor's missile: it goes for bombers, gunships and drone motherships first.</summary>
        public bool BigGame { get; internal set; }

        /// <summary>Guided by a fibre-optic cable: jammers do nothing to it.</summary>
        public bool JamProof { get; internal set; }

        /// <summary>One round in the air at a time from its mount (a fibre-optic drone's operator flies one drone).</summary>
        public bool OneAtATime { get; internal set; }

        /// <summary>Lofted over cover (a non-line-of-sight missile): fired at what its side sees, it comes down on the roof.</summary>
        public bool Lofted { get; internal set; }

        /// <summary>A salvo whose rounds all land at once (multiple rounds simultaneous impact).</summary>
        public bool Mrsi { get; internal set; }

        /// <summary>A glide bomb: it flies at its own speed from far off, and point defences may shoot it down.</summary>
        public bool Glides { get; internal set; }

        /// <summary>What it may take among fliers (see <see cref="Content.Prey"/>).</summary>
        public Prey Prey { get; internal set; }
    }

    public sealed partial class Catalog
    {
        private static void ParseP25A(JsonObject v, VehicleDef def)
        {
            if (v.Has("blastWall"))
            {
                var o = v.Object("blastWall");
                def.BlastWall = new BlastWallDef
                {
                    Radius = MathF.Max(1f, o.Float("radius", 8f)), Cut = Math.Clamp(o.Float("cut", 0.3f), 0f, 0.9f),
                    Cone = Math.Clamp(o.Float("cone", 50f), 5f, 90f) * MathF.PI / 180f,
                };
            }
            if (v.Has("decoy")) def.Decoy = new DecoyDef { Mimic = v.Object("decoy").Has("mimic") ? v.Object("decoy").String("mimic") : "gun_turret" };
            if (v.Has("fireControl"))
            {
                var o = v.Object("fireControl");
                def.FireControl = new FireControlDef
                {
                    Radius = MathF.Max(1f, o.Float("radius", 30f)), Damage = Math.Clamp(o.Float("damage", 0.12f), 0f, 1f), Focus = Math.Clamp(o.Float("focus", 2f), 1f, 10f),
                };
            }
            if (v.Has("searchlight"))
            {
                var o = v.Object("searchlight");
                def.Searchlight = new SearchlightDef { Radius = MathF.Max(1f, o.Float("radius", 35f)), Dazzle = Math.Clamp(o.Float("dazzle", 0.2f), 0f, 0.9f) };
            }
            if (v.Has("balloon"))
            {
                var o = v.Object("balloon");
                def.Balloon = new BalloonDef { Radius = MathF.Max(1f, o.Float("radius", 40f)), Scatter = Math.Clamp(o.Float("scatter", 0.5f), 0f, 5f) };
            }
            if (v.Has("sightJammer"))
            {
                var o = v.Object("sightJammer");
                def.SightJammer = new SightJammerDef { Radius = MathF.Max(1f, o.Float("radius", 35f)), Close = MathF.Max(0f, o.Float("close", 15f)) };
            }
            if (v.Has("shelter"))
            {
                var o = v.Object("shelter");
                def.Shelter = new ShelterDef { Radius = MathF.Max(1f, o.Float("radius", 15f)), Cut = Math.Clamp(o.Float("cut", 0.5f), 0f, 0.9f) };
            }
            if (v.Has("flares"))
            {
                var o = v.Object("flares");
                def.Flares = new FlareDef
                {
                    Every = MathF.Max(1f, o.Float("every", 15f)), Range = MathF.Max(1f, o.Float("range", 40f)),
                    Radius = MathF.Max(1f, o.Float("radius", 30f)), Seconds = MathF.Max(1f, o.Float("seconds", 15f)),
                };
            }
            if (v.Has("microwave"))
            {
                var o = v.Object("microwave");
                def.Microwave = new MicrowaveDef
                {
                    Range = MathF.Max(1f, o.Float("range", 30f)), Arc = Math.Clamp(o.Float("arc", 60f), 5f, 360f) * 0.5f * MathF.PI / 180f,
                    Cooldown = MathF.Max(0.5f, o.Float("cooldown", 8f)),
                };
            }
            if (v.Has("droneHunt")) def.DroneHunt = new DroneHuntDef { Reach = MathF.Max(1f, v.Object("droneHunt").Float("reach", 60f)) };
            if (v.Has("paradrop"))
            {
                var o = v.Object("paradrop");
                def.Paradrop = new ParadropDef
                {
                    Proxy = o.String("proxy"), Fall = MathF.Max(1f, o.Float("fall", 6f)), Height = MathF.Max(5f, o.Float("height", 30f)),
                    BaseKeepOut = MathF.Max(0f, o.Float("baseKeepOut", 45f)),
                };
            }
            if (v.Has("reconPass"))
            {
                var o = v.Object("reconPass");
                def.ReconPass = new ReconPassDef { Width = MathF.Max(2f, o.Float("width", 60f)), Seconds = MathF.Max(1f, o.Float("seconds", 20f)) };
            }
            def.TurretArc = v.Has("turretArc") ? Math.Clamp(v.Float("turretArc", 180f), 5f, 180f) * MathF.PI / 180f : 0f;
            def.SmokeSight = v.Bool("smokeSight", false);
            def.StillVision = MathF.Max(0f, v.Float("stillVision", 0f));
            def.StillAfter = MathF.Max(0f, v.Float("stillAfter", 2f));
            def.GlideRelease = v.Bool("glideRelease", false);
            def.FlightTier = v.Enum("flightTier", AltitudeTier.None);
        }

        private static void ParseWeaponP25A(JsonObject w, WeaponDef def)
        {
            def.GroundRange = MathF.Max(0f, w.Float("groundRange", 0f));
            def.MinReach = MathF.Max(0f, w.Float("minReach", 0f));
            def.GroupPriority = w.Bool("groupPriority", false);
            def.BigGame = w.Bool("bigGame", false);
            def.JamProof = w.Bool("jamProof", false);
            def.OneAtATime = w.Bool("oneAtATime", false);
            def.Lofted = w.Bool("lofted", false);
            def.Mrsi = w.Bool("mrsi", false);
            def.Glides = w.Bool("glides", false);
            def.Prey = w.Enum("prey", Prey.Any);
            // Prompt 26 B.3: a two-layer blast: "edge" is the outer radius (default none), "edgeShare" its share of the damage.
            def.SplashEdge = MathF.Min(WeaponDef.MaxEdge, MathF.Max(0f, w.Float("edge", 0f)));
            def.EdgeShare = Math.Clamp(w.Float("edgeShare", 0.4f), 0f, 1f);
            def.PierceMax = Math.Max(0, w.Int("pierceMax", 0));
            if (def.SplashEdge > 0f && def.SplashEdge <= def.SplashRadius) throw new FormatException($"{w.Path}.edge: wider than its splash (the core).");
            if (def.GroundRange > 0f && def.GroundRange > def.Range) throw new FormatException($"{w.Path}.groundRange: shorter than its range.");
        }

        /// <summary>Prompt 25 F2 batch A: every id the new mechanisms name exists (a decoy's model twin, a drop's falling stand-in).</summary>
        private void FinishP25A()
        {
            foreach (var def in _vehicles.Values)
            {
                if (def.Decoy is { } decoy && !_vehicles.ContainsKey(decoy.Mimic)) throw new FormatException($"{def.Id}.decoy.mimic: unknown vehicle '{decoy.Mimic}'.");
                if (def.Paradrop is { } drop && (!_vehicles.TryGetValue(drop.Proxy, out var proxy) || !proxy.Flying || proxy.Card))
                    throw new FormatException($"{def.Id}.paradrop.proxy: '{drop.Proxy}' must be a flying vehicle that is no card.");
            }
        }
    }
}
