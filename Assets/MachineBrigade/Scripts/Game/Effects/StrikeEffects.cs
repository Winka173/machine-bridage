using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// What fire support looks like: red telegraphs on the ground, the strike jet screaming over
    /// with bombs falling from it, the cruise missile diving in, smoke clouds and repair sparkle,
    /// and every support its own round coming down (DECISIONS 12C; see <see cref="Round"/>).
    /// Impacts themselves are explosions played by <see cref="EffectsDirector"/>.
    /// </summary>
    internal sealed class StrikeEffects
    {
        private const float JetAltitude = 24f;

        /// <summary>Play-test 6: the SEAD strike's anti-radiation missile drawn this much bigger than a Maverick.</summary>
        internal const float SeadScale = 1.8f;
        private const float BombFall = 0.8f;

        /// <summary>The heavy bomber of a bombing raid flies higher than the strike jet.</summary>
        private const float BomberAltitude = 32f;

        /// <summary>The transport of an airlift or the MOAB (the same aircraft AirDrops flies), its height and speed over the drop.</summary>
        private const string TransportModel = AirDrops.TransportModel;
        private const float TransportAltitude = 44f, TransportSpeed = 70f;

        /// <summary>Red target marks on the ground: one for an area strike, one per bomb for an airstrike.</summary>
        private sealed class Telegraph
        {
            public GroundMark[] Rings;
            public int Used;
            public float Start, Impact, End, Radius;
            public bool Active;
            public Color Edge = WarningColor, Fill = WarningFill;

            /// <summary>Fix prompt L5: an enemy's harmful support: a warning ring under the gate (Kind), drawn in the warning style.</summary>
            public bool Warns;
            public WarningKind Kind;
            public Vector3 Centre;
        }

        /// <summary>Fix prompt L5: the gate that decides which warning rings are drawn (none: all are), and their fade-in (s).</summary>
        public WarningGate Gate { get; set; }
        public float WarnFadeIn { get; set; } = 0.4f;

        /// <summary>Fix prompt L5: the warning look of an enemy support's ring (a thin edge, a faint fill).</summary>
        private static readonly Color WarnEdge = new(2.2f, 0.42f, 0.2f, 0.9f);
        private static readonly Color WarnFill = new(1.6f, 0.36f, 0.16f, 0.55f);

        private static readonly Color WarningColor = new(2.4f, 0.32f, 0.18f, 0.95f);
        private static readonly Color WarningFill = new(2.6f, 0.9f, 0.3f, 1f);

        // Support that harms no one where it lands is marked in its own colours: a scan's circle
        // in radar cyan, a tower's drop point in white.
        private static readonly Color ScanColor = new(0.3f, 1.6f, 2.2f, 0.8f);
        private static readonly Color ScanFill = new(0.4f, 1.2f, 1.6f, 0.5f);
        private static readonly Color DropColor = new(1.8f, 1.8f, 1.7f, 0.85f);

        /// <summary>A UAV scan's drone: flies in, then circles the mark until the scan ends.</summary>
        private sealed class ScanDrone
        {
            public GameObject Root;
            public Vector3 From, Centre;
            public float Arrive, End, Radius;
            public bool Active;
        }

        private readonly List<ScanDrone> _drones = new();
        private const float DroneAltitude = 22f;

        private const int RingsPerTelegraph = 10;

        private sealed class Jet
        {
            public GameObject Root;
            public string Model;
            public Transform Bombs;
            public Vector3 From, To;
            public float Start, Duration, NextPuff;
            public bool Active;

            /// <summary>Vapour and exhaust behind it (jets; not a transport).</summary>
            public bool Puffs;
        }

        private readonly Catalog _catalog;
        private readonly ModelLibrary _models;
        private readonly Emitters _emitters;
        private readonly ProjectilePool _projectiles;
        private readonly List<Telegraph> _telegraphs = new();
        private readonly List<Jet> _jets = new();
        private readonly List<(float at, Vector3 from, Vector3 to, string model)> _bombs = new();
        private readonly List<(ParticleSystem system, float until)> _smoke = new();
        private readonly SmokeScreens _screens;
        private readonly Transform _root;
        private readonly MaterialLibrary _materials;
        private readonly bool _hasJet, _hasBomb, _hasCruise;

        public StrikeEffects(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Emitters emitters,
            ProjectilePool projectiles, SmokeScreens screens, Transform parent)
        {
            _screens = screens;
            _catalog = catalog;
            _materials = materials;
            _models = models;
            _emitters = emitters;
            _projectiles = projectiles;
            _root = new GameObject("Strikes").transform;
            _root.SetParent(parent, false);
            _hasJet = models.Has("strike_jet");
            _hasBomb = models.Has("bomb");
            _hasCruise = models.Has("cruise_missile");

            for (var i = 0; i < 6; i++)
            {
                var t = new Telegraph { Rings = new GroundMark[RingsPerTelegraph] };
                for (var r = 0; r < RingsPerTelegraph; r++)
                {
                    t.Rings[r] = new GroundMark("Strike Mark", _root, meshes, materials, GroundMark.Style.Strike);
                    t.Rings[r].Visible = false;
                }
                _telegraphs.Add(t);
            }
            BuildRounds(materials, meshes);
        }

        public void Consume(in SimEvent e, float now)
        {
            if (e.DefId == null && e.Kind != SimEventKind.SmokeDeployed) return;
            switch (e.Kind)
            {
                case SimEventKind.StrikeWarning:
                    if (!_catalog.TryGetSupport(e.DefId, out var support)) return;
                    Warned(support, e.Team, Ground(e.Position), Ground(e.Target), e.Value, now);
                    break;

                case SimEventKind.AircraftPass:
                    if (!_catalog.TryGetSupport(e.DefId, out var pass)) return;
                    Passed(pass, e.Team, Ground(e.Position), Ground(e.Target), e.Value, now);
                    break;

                case SimEventKind.SmokeDeployed:
                    SpawnSmoke(Ground(e.Position), e.Value, e.Target.X, now);
                    break;
            }
        }

        /// <summary>A support called (StrikeWarning): its telegraph, and the rounds that come down with no aircraft pass or shell of the simulation's own.</summary>
        internal void Warned(SupportDef support, int team, Vector3 point, Vector3 end, float delay, float now)
        {
            ShowTelegraph(support, point, end, now, delay, team);
            var impact = now + delay;
            switch (support.Kind)
            {
                case SupportKind.Airstrike:
                    ScheduleBombs(support, point, end, impact);
                    break;
                case SupportKind.CruiseMissile when IsMoab(support):
                    DropMoab(team, point, impact);
                    break;
                case SupportKind.Emp:
                    DropWarhead(point, impact);
                    break;
                case SupportKind.Repair when support.Radius < 100f:
                    // (A field repair reaches the whole map: no crate, only the sparkle on each vehicle.)
                    DropCrate(point, impact, delay, support.Duration);
                    break;
                case SupportKind.Reinforce:
                    Airlift(support, team, point, impact, delay);
                    break;
            }
        }

        /// <summary>An aircraft or missile on its way (AircraftPass), from <paramref name="from"/> to <paramref name="to"/> in <paramref name="seconds"/>.</summary>
        internal void Passed(SupportDef pass, int team, Vector3 from, Vector3 to, float seconds, float now)
        {
            if (pass.Kind == SupportKind.CruiseMissile && IsMoab(pass)) return;
            if (pass.Kind == SupportKind.CruiseMissile) LaunchCruise(from, to, seconds, now);
            else if (pass.Kind == SupportKind.Scan) LaunchScanDrone(team, from, to, seconds, pass, now);
            else LaunchJet(pass, team, from, to, seconds, now);
        }

        public void Tick(float now)
        {
            TickLocks(now);
            foreach (var t in _telegraphs)
            {
                if (!t.Active) continue;
                if (now >= t.End)
                {
                    t.Active = false;
                    foreach (var ring in t.Rings) ring.Visible = false;
                    continue;
                }
                // The fill sweeps round until impact; the mark beats faster as it nears.
                var progress = Mathf.Clamp01((now - t.Start) / Mathf.Max(0.1f, t.Impact - t.Start));
                var urgency = Mathf.Clamp01(1f - (t.Impact - now) / 2f);
                var breathe = 1f + 0.05f * Mathf.Sin(now * Mathf.Lerp(6f, 20f, urgency));
                // Fix prompt L5: a warning ring is offered to the gate, drawn only while shown, fading in.
                var shown = true;
                var edge = t.Edge;
                if (t.Warns)
                {
                    var reach = t.Radius;
                    for (var r = 0; r < t.Used; r++) reach = Mathf.Max(reach, Vector3.Distance(t.Rings[r].Transform.position, t.Centre) + t.Radius);
                    Gate?.Offer(t, t.Centre, reach, t.Kind);
                    shown = Gate == null || Gate.Shown(t, t.Kind);
                    var fade = WarnFadeIn > 0f ? Mathf.Clamp01((now - t.Start) / WarnFadeIn) : 1f;
                    edge = new Color(edge.r, edge.g, edge.b, edge.a * fade);
                }
                for (var r = 0; r < t.Used; r++)
                {
                    t.Rings[r].Visible = shown;
                    if (!shown) continue;
                    t.Rings[r].Set(edge, t.Fill, progress, urgency);
                    t.Rings[r].Transform.localScale = Vector3.one * t.Radius * (t.Warns ? 1f : breathe);
                    // A super weapon's ring sits above the others.
                    if (t.Warns && t.Kind == WarningKind.Super)
                    {
                        var at = t.Rings[r].Transform.position;
                        t.Rings[r].Transform.position = new Vector3(at.x, Mathf.Max(at.y, 0.16f), at.z);
                    }
                }
            }

            foreach (var d in _drones)
            {
                if (!d.Active) continue;
                if (now >= d.End)
                {
                    d.Active = false;
                    d.Root.SetActive(false);
                    continue;
                }
                Vector3 p, ahead;
                if (now < d.Arrive)
                {
                    // Flying in to the start of its circle.
                    var entry = d.Centre + Vector3.back * d.Radius;
                    p = Vector3.Lerp(d.From, entry, Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(d.Arrive - 3f, d.Arrive, now)));
                    ahead = entry - d.From;
                }
                else
                {
                    // A slow circle (about 16 s a lap), banked into the turn.
                    var a = (now - d.Arrive) * 0.4f;
                    p = d.Centre + new Vector3(-Mathf.Sin(a), 0f, -Mathf.Cos(a)) * d.Radius;
                    ahead = new Vector3(-Mathf.Cos(a), 0f, Mathf.Sin(a));
                }
                d.Root.transform.position = p;
                if (ahead.sqrMagnitude > 1e-4f) d.Root.transform.rotation = Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, 0f, now < d.Arrive ? 0f : 14f);
            }

            foreach (var jet in _jets)
            {
                if (!jet.Active) continue;
                var k = (now - jet.Start) / jet.Duration;
                if (k >= 1f)
                {
                    jet.Active = false;
                    jet.Root.SetActive(false);
                    continue;
                }
                // A transport booked for later is not in the sky yet.
                if (k < 0f)
                {
                    if (jet.Root.activeSelf) jet.Root.SetActive(false);
                    continue;
                }
                if (!jet.Root.activeSelf) jet.Root.SetActive(true);
                var p = Vector3.Lerp(jet.From, jet.To, k);
                jet.Root.transform.position = p;
                jet.Root.transform.rotation = Quaternion.LookRotation(jet.To - jet.From) * Quaternion.Euler(0f, 0f, Mathf.Sin(k * 6f) * 6f);
                if (jet.Puffs && now >= jet.NextPuff)
                {
                    jet.NextPuff = now + 0.03f;
                    // Vapour off the wingtips and a hot exhaust, sized to the aircraft as drawn.
                    var scale = jet.Root.transform.localScale.x;
                    var right = jet.Root.transform.right * 4.5f * scale;
                    var back = jet.Root.transform.forward;
                    _emitters.Contrail(p + right - back * 2f * scale, 0.4f, 1.2f);
                    _emitters.Contrail(p - right - back * 2f * scale, 0.4f, 1.2f);
                    if (jet.Model == "strike_jet") _emitters.Afterburner(p - back * 5.5f * scale, back, 1.4f);
                    _emitters.Contrail(p - back * 6.5f * scale, 0.5f, 1.4f);
                }
            }

            for (var i = _bombs.Count - 1; i >= 0; i--)
            {
                var (at, from, to, model) = _bombs[i];
                if (now < at) continue;
                _bombs.RemoveAt(i);
                // Play-test 8 A (DECISIONS 22Q): each falls on the curve of a bomb keeping the aircraft's speed, not a straight line.
                if (_hasBomb)
                    _projectiles.Launch(_models.Merged(_models.Has(model) ? model : "bomb"), from, to, BombFall, 0f, 0f, now,
                        control: WeaponEffects.BombPath(from, to, false));
                // The bombs leave the wings as they fall.
                foreach (var jet in _jets)
                    if (jet.Active && jet.Bombs != null) jet.Bombs.gameObject.SetActive(false);
            }

            for (var i = _fallers.Count - 1; i >= 0; i--)
            {
                if (!Fall(_fallers[i], now)) continue;
                Kill(_fallers[i].Root);
                _fallers.RemoveAt(i);
            }

            for (var i = _smoke.Count - 1; i >= 0; i--)
            {
                var (system, until) = _smoke[i];
                if (now < until) continue;
                var emission = system.emission;
                emission.enabled = false;
                if (now > until + 9f)
                {
                    _screens?.Remove(system.transform.position);
                    Object.Destroy(system.gameObject);
                    _smoke.RemoveAt(i);
                }
            }
        }

        /// <summary>The player's side: its own harmful supports draw no warning ring (fix prompt L5).</summary>
        public int PlayerTeam { get; set; }

        /// <summary>Fix prompt L5: a support that harms where it lands (its ring is a warning).</summary>
        private static bool Harmful(SupportDef support) => support.Damage > 0f || support.Kind == SupportKind.Emp;

        private void ShowTelegraph(SupportDef support, Vector3 point, Vector3 end, float now, float delay, int team = -1)
        {
            // Fix prompt L5: no warning ring for a harmful support of ours; an enemy's harmless one (a scan) shows nothing.
            var harmful = Harmful(support);
            var ours = team == PlayerTeam;
            if (harmful && ours) return;
            if (!harmful && !ours && support.Kind != SupportKind.Tower) return;
            var t = _telegraphs.Find(x => !x.Active) ?? _telegraphs[0];
            t.Warns = harmful;
            t.Kind = support.Tier >= ExplosionTier.Ultimate ? WarningKind.Super : WarningKind.Support;
            t.Centre = (point + end) * 0.5f;
            foreach (var ring in t.Rings) ring.Restyle(harmful ? GroundMark.Style.Warning : GroundMark.Style.Strike);
            t.Active = true;
            t.Start = now;
            t.Impact = now + delay;
            t.End = now + delay + (support.Kind is SupportKind.Barrage or SupportKind.Airstrike ? support.Duration : 0.2f);
            foreach (var ring in t.Rings) ring.Visible = false;
            if (support.IsLine)
            {
                // One ring per bomb, where it will land (one warning under the gate: the salvo is one hull).
                t.Used = Mathf.Min(support.Count, RingsPerTelegraph);
                t.Radius = support.BlastRadius;
                (t.Edge, t.Fill) = (WarnEdge, WarnFill);
                for (var i = 0; i < t.Used; i++)
                {
                    var along = t.Used > 1 ? i / (float)(t.Used - 1) : 0.5f;
                    t.Rings[i].Transform.position = Vector3.Lerp(point, end, along) + Vector3.up * 0.1f;
                    t.Rings[i].Transform.localScale = Vector3.one * t.Radius;
                    t.Rings[i].Visible = true;
                }
                return;
            }
            t.Used = 1;
            // A loaned aircraft only needs its arrival point marked, not the ground it may cover.
            t.Radius = support.Kind == SupportKind.Escort ? Mathf.Min(support.Radius, 5f) : support.Radius;
            (t.Edge, t.Fill) = support.Kind switch
            {
                SupportKind.Scan => (ScanColor, ScanFill),
                SupportKind.Tower => (DropColor, DropColor),
                _ => (WarnEdge, WarnFill),
            };
            // A scan's circle stays up while the drone watches it.
            if (support.Kind == SupportKind.Scan) t.End = now + delay + support.Duration;
            t.Rings[0].Transform.position = point + Vector3.up * 0.1f;
            t.Rings[0].Transform.localScale = Vector3.one * t.Radius;
            t.Rings[0].Visible = true;
        }

        private void ScheduleBombs(SupportDef support, Vector3 start, Vector3 end, float firstImpact)
        {
            var interval = support.Count > 1 ? support.Duration / (support.Count - 1) : 0f;
            // Each bomb leaves the aircraft one fall-time before it lands and keeps the aircraft's
            // speed on the way down, so it drops out from under the aircraft and lands as it passes.
            var speed = support.Length / Mathf.Max(0.2f, support.Duration);
            var forward = (end - start).normalized;
            var altitude = IsBomberRaid(support) ? BomberAltitude : JetAltitude;
            var drops = new List<(float at, Vector3 from, Vector3 to)>();
            for (var i = 0; i < support.Count; i++)
            {
                var along = support.Count > 1 ? i / (float)(support.Count - 1) : 0.5f;
                var target = Vector3.Lerp(start, end, along);
                var release = target - forward * (speed * BombFall) + Vector3.up * altitude;
                drops.Add((firstImpact + i * interval, release, target));
            }
            if (DropsOwnRounds(support, drops, forward, speed)) return;
            // The bombs by the aircraft: the strike jet's Mk 84s, the bombing raid's FAB-500s.
            var model = IsBomberRaid(support) ? "bomb_fab" : support.Id == "airstrike" ? "bomb_mk84" : "bomb";
            foreach (var (at, from, to) in drops) _bombs.Add((at - BombFall, from, to, model));
        }

        /// <summary>The neutral bombing raid of the battle events: a heavy bomber rather than the strike jet.</summary>
        private static bool IsBomberRaid(SupportDef support) => support.Id == "air_raid";

        /// <summary>
        /// Balance pack (lane B): the height the view drops a support's bombs from (Bom_don_vi.do_cao_tha_m), in metres: a
        /// bombing run's jet or bomber (ScheduleBombs); 0 when no aircraft drops them (a glide bomb or cruise missile flies
        /// in as a missile, LaunchCruise; the rest have no aircraft pass). The simulation lands bombs on its own schedule
        /// (StrikeSystem), so this height is the picture only.
        /// </summary>
        internal static float ReleaseAltitude(SupportDef support) =>
            support.Kind == SupportKind.Airstrike ? IsBomberRaid(support) ? BomberAltitude : JetAltitude : 0f;

        /// <summary>The MOAB: dropped from a transport, not flown in like the cruise missile it shares its kind with.</summary>
        private static bool IsMoab(SupportDef support) => support.Id == "moab";

        private void LaunchJet(SupportDef support, int team, Vector3 from, Vector3 to, float seconds, float now)
        {
            var bomber = IsBomberRaid(support) && _models.Has("heavy_bomber");
            if (!bomber && !_hasJet) return;
            var model = bomber ? "heavy_bomber" : "strike_jet";
            var altitude = bomber ? BomberAltitude : JetAltitude;
            var jet = Flyer(model, team, from + Vector3.up * altitude, to + Vector3.up * altitude, now, Mathf.Max(0.5f, seconds), true);
            if (jet.Bombs != null) jet.Bombs.gameObject.SetActive(true);
        }

        /// <summary>An aircraft flying from <paramref name="from"/> to <paramref name="to"/>, setting off at <paramref name="start"/>.</summary>
        private Jet Flyer(string model, int team, Vector3 from, Vector3 to, float start, float duration, bool puffs)
        {
            var jet = _jets.Find(j => !j.Active && j.Model == model);
            if (jet == null)
            {
                jet = new Jet { Root = _models.Spawn(model, team, _root).Root, Model = model };
                var twin = model == "strike_jet" ? "attack_jet" : model == TransportModel ? AirDrops.TransportScale : model;
                if (_catalog.Vehicles.TryGetValue(twin, out var sized)) jet.Root.transform.localScale = Vector3.one * VehicleView.DrawScaleOf(sized, jet.Root);
                foreach (var t in jet.Root.GetComponentsInChildren<Transform>(true))
                    if (t.name.StartsWith("Bombs")) jet.Bombs = t;
                _jets.Add(jet);
            }
            jet.Root.SetActive(false);
            jet.From = from;
            jet.To = to;
            jet.Start = start;
            jet.Duration = Mathf.Max(0.5f, duration);
            jet.NextPuff = start;
            jet.Puffs = puffs;
            jet.Active = true;
            jet.Root.transform.SetPositionAndRotation(from, Quaternion.LookRotation(to - from));
            return jet;
        }

        private void LaunchScanDrone(int team, Vector3 from, Vector3 to, float seconds, SupportDef scan, float now)
        {
            if (!_models.Has("recon_drone")) return;
            var d = _drones.Find(x => !x.Active);
            if (d == null)
            {
                d = new ScanDrone { Root = _models.Spawn("recon_drone", team, _root).Root };
                if (_catalog.Vehicles.TryGetValue("recon_drone", out var sized)) d.Root.transform.localScale = Vector3.one * VehicleView.DrawScaleOf(sized, d.Root);
                _drones.Add(d);
            }
            d.Root.SetActive(true);
            d.Centre = to + Vector3.up * DroneAltitude;
            d.From = from + Vector3.up * DroneAltitude;
            d.Radius = Mathf.Clamp(scan.Radius * 0.55f, 8f, 20f);
            d.Arrive = now + Mathf.Max(0.3f, seconds);
            d.End = d.Arrive + scan.Duration + 0.5f;
            d.Active = true;
        }

        private void LaunchCruise(Vector3 start, Vector3 to, float seconds, float now)
        {
            var from = start + Vector3.up * 40f;
            if (_hasCruise) _projectiles.Launch(_models.Merged("cruise_missile"), from, to, seconds, 4f, 1.2f, now,
                plume: Plume.For(null, MachineBrigade.Sim.Content.ProjectileKind.Missile, "cruise_missile", true));
        }

        /// <summary>Device check (<c>-mb-smokescreen</c>): a smoke screen with no strike behind it.</summary>
        internal void DebugSmoke(Vector3 at, float now) => SpawnSmoke(at, 12f, 12f, now);

        private void SpawnSmoke(Vector3 at, float radius, float seconds, float now)
        {
            // Billowing smoke sheets on their own queue (FxQueue.Screen): whatever burns inside or
            // behind the screen shows through it only as a glow.
            var ps = PB.Create(_root, "Smoke Screen", FxMaterials.Shared.ScreenSmoke);
            ps.transform.position = at;
            var main = ps.main;
            main.loop = true;
            main.duration = 2f;
            main.maxParticles = 220;
            PB.Basics(ps, new Vector2(5f, 8f), new Vector2(0.2f, 0.8f), new Vector2(5f, 8f));
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = radius * 0.8f;
            shape.rotation = new Vector3(90f, 0f, 0f);
            PB.Flipbook(ps, loop: false, tilt: 25f, from: 0.08f, to: 0.92f);
            PB.Colors(ps, PB.Plume(0.72f, 0.82f, 0.75f));
            PB.Grow(ps, 0.6f, 1.6f);
            PB.Rise(ps, 0.2f, 0.6f);
            _screens?.Add(at, radius * 0.8f + 4f);
            var emission = ps.emission;
            emission.enabled = true;
            emission.rateOverTime = 26f;
            ps.Play();
            _smoke.Add((ps, now + seconds));
        }

        // ---------------------------------------------------------------------------------------
        // Each support's own round (second play test, DECISIONS 12C): what comes down, and how it
        // arrives, so no two cards look alike. Barrage shells ride their glowing tracer
        // (EffectsDirector draws it); smoke shells are white and burst open short of the ground;
        // mines come on rockets; the SEAD jet fires a missile; napalm canisters tumble; cluster
        // dispensers split open into bomblets; the MOAB rolls out of a transport on a drogue chute;
        // the EMP is an energy warhead; a repair drop is a crate under a parachute; reinforcements
        // are airlifted in under canopies.
        // ---------------------------------------------------------------------------------------

        /// <summary>What a round drawn here is.</summary>
        private enum Round
        {
            /// <summary>A base-ejection smoke shell: white, trailing a wisp, bursting open short of the ground.</summary>
            SmokeShell,

            /// <summary>A napalm canister: finless, tumbling end over end.</summary>
            Canister,

            /// <summary>A cluster dispenser: falls from the wing and splits open into bomblets.</summary>
            Dispenser,

            /// <summary>One of a dispenser's bomblets, tumbling onto its own mark.</summary>
            Bomblet,

            /// <summary>A supply crate under a parachute.</summary>
            Crate,

            /// <summary>An airlifted vehicle under a parachute; the real one takes over as it lands.</summary>
            Vehicle,

            /// <summary>The MOAB: out of the transport on a drogue chute, cut away, nose-first.</summary>
            Moab,

            /// <summary>The EMP's energy warhead: a ball of blue light with a crackling trail.</summary>
            Warhead,
        }

        private sealed class Faller
        {
            public Round Kind;
            public GameObject Root;
            public Transform Body, Chute;
            public Vector3 From, To, Axis;
            public float Start, End, Spin, Heading, Linger, NextPuff, Landed;
            public bool Shown, Popped, Down;
        }

        private readonly List<Faller> _fallers = new();
        private ParticleSystem _puffs, _glow, _sparks;
        private Mesh _canopy, _canister, _box;
        private Material _cloth, _white, _silver, _yellow;

        private static readonly Color WhiteSmoke = new(0.93f, 0.93f, 0.91f, 0.85f);
        private static readonly Color GreySmoke = new(0.55f, 0.54f, 0.52f, 0.7f);
        private static readonly Color EmpCore = new(0.35f, 0.62f, 1f, 1f);
        private static readonly Color EmpTrail = new(0.08f, 0.32f, 1f, 0.75f);
        private static readonly Color EmpSpark = new(0.4f, 0.75f, 1f, 1f);
        private static readonly Color HotSpark = new(1f, 0.8f, 0.45f, 1f);

        /// <summary>The meshes, materials and particle layers the rounds are drawn with.</summary>
        private void BuildRounds(MaterialLibrary materials, MeshLibrary meshes)
        {
            _canopy = Dome(12, 4);
            _box = meshes.Box;
            _cloth = materials.ForModel("Canvas", -1);
            _white = materials.ForModel("PlasterWhite", -1);
            _silver = materials.ForModel("Fuel", -1);
            _yellow = materials.ForModel("Hazard", -1);
            var capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            _canister = capsule.GetComponent<MeshFilter>().sharedMesh;
            Kill(capsule);

            // White smoke puffs: smoke shells bursting and spilling, a crate's marker.
            _puffs = Layer("Strike Puffs", FxMaterials.Shared.Smoke, 500, 0f);
            PB.Flipbook(_puffs, loop: false, tilt: 25f, from: 0.08f, to: 0.92f);
            PB.Colors(_puffs, PB.Plume(0.85f, 0.95f, 0.9f));
            PB.Grow(_puffs, 0.6f, 1.7f);
            PB.Rise(_puffs, 0.2f, 0.7f);
            // Light: the EMP warhead, its trail and its flash.
            _glow = Layer("Strike Glow", materials.Glow, 300, 0f);
            PB.Colors(_glow, PB.Fade(Color.white, Color.white, Color.white));
            PB.Grow(_glow, 1f, 1.5f);
            // Sparks: electric arcs off the warhead, a dispenser's skin blowing off.
            _sparks = Layer("Strike Sparks", materials.Sparks, 500, 1.2f);
            PB.Colors(_sparks, PB.Fade(Color.white, Color.white, Color.white));
        }

        private static readonly Color LockRed = new(1f, 0.22f, 0.14f, 0.9f);

        /// <summary>Play-test 6 (DECISIONS 21H): the SEAD missile's lock on its radar, (where, from, to), drawn while it flies.</summary>
        private readonly List<(Vector3 at, float start, float end)> _locks = new();

        private float _lockPulse;

        /// <summary>A lock on the radar at <paramref name="at"/> until the missile strikes in <paramref name="seconds"/>.</summary>
        private void LockOn(Vector3 at, float seconds, float now) => _locks.Add((at, now, now + Mathf.Max(0.2f, seconds)));

        /// <summary>Six red points turning round the locked radar and closing in on it, a red pulse over it, as the missile nears.</summary>
        private void TickLocks(float now)
        {
            for (var i = _locks.Count - 1; i >= 0; i--)
                if (now >= _locks[i].end) _locks.RemoveAt(i);
            if (_locks.Count == 0 || now < _lockPulse) return;
            _lockPulse = now + 0.1f;
            foreach (var (at, start, end) in _locks)
            {
                var t = Mathf.InverseLerp(start, end, now);
                var r = Mathf.Lerp(4.5f, 0.9f, t);
                for (var k = 0; k < 6; k++)
                {
                    var angle = k * Mathf.PI / 3f + now * 1.6f;
                    Emit(_glow, at + new Vector3(Mathf.Cos(angle) * r, 0.35f, Mathf.Sin(angle) * r), Vector3.zero, 0.7f, 0.16f, LockRed);
                }
                Emit(_glow, at + Vector3.up * 0.5f, Vector3.zero, 1f + 1.4f * t, 0.12f, LockRed);
            }
        }

        private ParticleSystem Layer(string name, Material material, int max, float gravity)
        {
            var ps = PB.Create(_root, name, material);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            main.gravityModifier = gravity;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play(true);
            return ps;
        }

        private static void Emit(ParticleSystem ps, Vector3 at, Vector3 velocity, float size, float life, Color colour) =>
            ps.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity, startSize = size, startLifetime = life, startColor = colour, applyShapeToPosition = false,
            }, 1);

        /// <summary>
        /// A fire-support round announced on its way down (ShellInbound), drawn by what it is. True
        /// when drawn here in place of the plain glowing shell (EffectsDirector draws that one for
        /// barrages, with the shell itself added here inside it).
        /// </summary>
        public bool Inbound(in SimEvent e, Vector3 from, Vector3 land, float now) =>
            e.DefId != null && _catalog.TryGetSupport(e.DefId, out var support) &&
            Inbound(support, new Vector3(e.Target.X, 0f, e.Target.Y), from, land, e.Value, now);

        /// <summary>A round of <paramref name="support"/> landing in <paramref name="seconds"/>, fired from the side <paramref name="back"/> points to.</summary>
        internal bool Inbound(SupportDef support, Vector3 back, Vector3 from, Vector3 land, float seconds, float now)
        {
            if (back.sqrMagnitude < 1e-4f) back = Vector3.left;
            back.Normalize();
            switch (support.Kind)
            {
                case SupportKind.Smoke:
                    // Base-ejection smoke shells: white rounds trailing a wisp, bursting open a few metres up.
                    Add(Round.SmokeShell, Body("shell_155", _white, 2f), from, land + Vector3.up * 0.3f, now, now + seconds);
                    return true;
                case SupportKind.Minefield:
                    // The mine-laying salvo: rockets on a low arc from the guns' side, each with its motor burning.
                    if (!_models.Has("rocket_107")) return false;
                    _projectiles.Launch(_models.Merged("rocket_107"), land + back * 55f + Vector3.up * 5f, land, seconds, 12f, 0.45f, now, wobble: 0.4f,
                        scale: 1.3f);
                    return true;
                case SupportKind.Sead:
                {
                    // Play-test 6 (DECISIONS 21H): the SEAD jet's anti-radiation missile (an AGM-88 HARM), drawn big with a
                    // long bright motor flame and a thick smoke trail: it leaves the jet, pulls up and dives steeply on to
                    // the air defence's radar (its lock marked by a red ring closing on it); the kill is EffectsDirector's.
                    var missile = _models.Has("maverick") ? "maverick" : "missile";
                    if (!_models.Has(missile)) return false;
                    var launch = land + back * 45f + Vector3.up * JetAltitude;
                    var crest = land + back * 10f + Vector3.up * (JetAltitude + 8f);
                    _projectiles.Launch(_models.Merged(missile), launch, land, seconds, 0f, 1.2f, now, boost: 0.25f, scale: SeadScale,
                        control: crest, plume: new Plume(2.4f, 0.3f, 1.9f, 1f, 0.3f));
                    LockOn(land, seconds, now);
                    return true;
                }
                case SupportKind.Barrage:
                    // The HE shell itself inside its glow, nose-first down its steep path (a super-gun's three times the size).
                    if (_models.Has("shell_155"))
                        _projectiles.Launch(_models.Merged("shell_155"), from, land, seconds, 0f, 0f, now, scale: support.Tier >= ExplosionTier.Ultimate ? 3.2f : 1.4f);
                    return false;
            }
            return false;
        }

        /// <summary>A model to drop, in its own materials or painted all over in <paramref name="paint"/>; a capsule when there is no model.</summary>
        private GameObject Body(string modelId, Material paint, float scale)
        {
            var go = new GameObject(modelId ?? "Canister", typeof(MeshFilter), typeof(MeshRenderer));
            go.transform.SetParent(_root, false);
            go.transform.localScale = Vector3.one * scale;
            var renderer = go.GetComponent<MeshRenderer>();
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            if (modelId != null && _models.Has(modelId))
            {
                var chunk = _models.Merged(modelId);
                go.GetComponent<MeshFilter>().sharedMesh = chunk.Mesh;
                if (paint == null) renderer.sharedMaterials = chunk.Materials;
                else
                {
                    var paints = new Material[chunk.Materials.Length];
                    for (var i = 0; i < paints.Length; i++) paints[i] = paint;
                    renderer.sharedMaterials = paints;
                }
            }
            else
            {
                go.GetComponent<MeshFilter>().sharedMesh = _canister;
                renderer.sharedMaterial = paint ?? _silver;
            }
            return go;
        }

        /// <summary>A finless canister (a stretched capsule), <paramref name="length"/> metres long.</summary>
        private GameObject Canister(Material paint, float length)
        {
            var go = Body(null, paint, 1f);
            go.transform.localScale = new Vector3(length * 0.36f, length * 0.5f, length * 0.36f);
            return go;
        }

        private Faller Add(Round kind, GameObject body, Vector3 from, Vector3 to, float start, float end)
        {
            var root = new GameObject(kind.ToString()).transform;
            root.SetParent(_root, false);
            root.position = from;
            body.transform.SetParent(root, false);
            root.gameObject.SetActive(false);
            var f = new Faller
            {
                Kind = kind, Root = root.gameObject, Body = body.transform, From = from, To = to, Start = start, End = Mathf.Max(start + 0.05f, end),
                Axis = Random.onUnitSphere, Spin = Random.Range(300f, 620f), Heading = Random.Range(0f, 360f),
            };
            _fallers.Add(f);
            return f;
        }

        /// <summary>Where a round is a fraction <paramref name="s"/> of the way down.</summary>
        private static Vector3 PathAt(Faller f, float s)
        {
            var p = Vector3.Lerp(f.From, f.To, s);
            p.y = f.Kind switch
            {
                // Under a canopy: fast out of the aircraft, braked soft onto the ground.
                Round.Crate or Round.Vehicle => f.To.y + (f.From.y - f.To.y) * Mathf.Pow(1f - s, 1.7f),
                Round.Warhead => Mathf.Lerp(f.From.y, f.To.y, Mathf.Pow(s, 1.4f)),
                Round.SmokeShell => p.y,
                // Dropped: keeps the aircraft's speed and falls ever faster.
                _ => Mathf.Lerp(f.From.y, f.To.y, s * s),
            };
            return p;
        }

        /// <summary>Moves one round on; true when it is done with.</summary>
        private bool Fall(Faller f, float now)
        {
            if (now < f.Start) return false;
            var t = f.Root.transform;
            if (!f.Shown)
            {
                f.Shown = true;
                f.Root.SetActive(true);
                // Canisters and dispensers leave the wings as they fall.
                if (f.Kind is Round.Canister or Round.Dispenser) HideBombs();
            }
            if (f.Down) return Settle(f, now);
            var s = Mathf.Clamp01((now - f.Start) / (f.End - f.Start));
            var here = PathAt(f, s);
            var ahead = PathAt(f, Mathf.Min(1f, s + 0.03f)) - here;
            if (ahead.sqrMagnitude < 1e-6f) ahead = f.To - f.From;
            t.position = here;
            switch (f.Kind)
            {
                case Round.Canister:
                case Round.Bomblet:
                    // Finless: tumbling end over end.
                    f.Body.localRotation = Quaternion.AngleAxis(f.Spin * (now - f.Start), f.Axis);
                    break;
                case Round.Crate:
                case Round.Vehicle:
                {
                    var sway = Mathf.Sin(now * 2.1f + f.Heading) * 5f * (1f - s);
                    t.rotation = Quaternion.Euler(sway, f.Heading, sway * 0.6f);
                    // The canopy blossoms open in the first moments.
                    var open = Mathf.Clamp01((now - f.Start) / 0.45f);
                    if (f.Chute != null) f.Chute.localScale = new Vector3(open, Mathf.Lerp(0.3f, 1f, open), open);
                    break;
                }
                default:
                    if (ahead.sqrMagnitude > 1e-6f) t.rotation = Quaternion.LookRotation(ahead);
                    break;
            }
            switch (f.Kind)
            {
                case Round.SmokeShell:
                    if (now >= f.NextPuff)
                    {
                        f.NextPuff = now + 0.035f;
                        Emit(_puffs, here, Random.insideUnitSphere * 0.2f, 0.9f, 1.1f, WhiteSmoke);
                    }
                    if (!f.Popped && s >= 0.8f)
                    {
                        // The base blows out and the canisters spill: a white burst in the air, no fire.
                        f.Popped = true;
                        for (var k = 0; k < 7; k++)
                            Emit(_puffs, here + Random.insideUnitSphere * 0.8f, Random.insideUnitSphere * 2.5f + ahead.normalized * 3f, Random.Range(2.4f, 3.8f),
                                Random.Range(1.6f, 2.4f), WhiteSmoke);
                    }
                    break;
                case Round.Warhead:
                    Emit(_glow, here, Vector3.zero, 3.4f, 0.05f, EmpCore);
                    if (now >= f.NextPuff)
                    {
                        f.NextPuff = now + 0.02f;
                        Emit(_glow, here, Random.insideUnitSphere * 0.6f, 1.8f, 0.5f, EmpTrail);
                        if (Random.value < 0.4f) Emit(_sparks, here, Random.insideUnitSphere * 7f, 0.14f, 0.3f, EmpSpark);
                    }
                    break;
                case Round.Moab:
                    // The drogue is cut away once the bomb has pitched over.
                    if (f.Chute != null && f.Chute.gameObject.activeSelf && s >= 0.45f) f.Chute.gameObject.SetActive(false);
                    break;
            }
            return s >= 1f && Arrive(f, now);
        }

        /// <summary>A round reaching the end of its fall; true when it is done with.</summary>
        private bool Arrive(Faller f, float now)
        {
            switch (f.Kind)
            {
                case Round.SmokeShell:
                    // The canisters land and pour white smoke (the screen builds from them).
                    for (var k = 0; k < 6; k++)
                        Emit(_puffs, f.To + Random.insideUnitSphere * 1.2f + Vector3.up * 0.6f,
                            Vector3.up * Random.Range(0.4f, 1.2f) + Random.insideUnitSphere * 0.8f, Random.Range(3f, 4.6f), Random.Range(2.6f, 3.8f), WhiteSmoke);
                    return true;
                case Round.Dispenser:
                    // It splits open: its skin blows off in a spray of sparks and a grey puff; the bomblets spill out.
                    for (var k = 0; k < 4; k++) Emit(_puffs, f.To + Random.insideUnitSphere * 0.8f, Random.insideUnitSphere * 1.8f, 2.4f, 1.2f, GreySmoke);
                    for (var k = 0; k < 24; k++) Emit(_sparks, f.To, Random.onUnitSphere * Random.Range(6f, 13f), 0.18f, Random.Range(0.25f, 0.5f), HotSpark);
                    return true;
                case Round.Warhead:
                    // The warhead goes off: a blue-white flash and arcs crackling out (the rings are EffectsDirector's).
                    var at = f.To + Vector3.up;
                    Emit(_glow, at, Vector3.zero, 24f, 0.35f, EmpCore);
                    Emit(_glow, at, Vector3.zero, 12f, 0.7f, EmpTrail);
                    for (var k = 0; k < 40; k++)
                        Emit(_sparks, at, (Random.onUnitSphere + Vector3.up * 0.4f) * Random.Range(8f, 20f), 0.16f, Random.Range(0.25f, 0.6f), EmpSpark);
                    return true;
                case Round.Crate:
                case Round.Vehicle:
                    _emitters.Dust(f.To, f.Kind == Round.Vehicle ? 3f : 1.4f);
                    f.Down = true;
                    f.Landed = now;
                    f.Root.transform.SetPositionAndRotation(f.To, Quaternion.Euler(0f, f.Heading, 0f));
                    // The real vehicle takes over from here; its chute stays a moment.
                    if (f.Kind == Round.Vehicle) f.Body.gameObject.SetActive(false);
                    return false;
                default:
                    return true;
            }
        }

        /// <summary>Landed under a canopy: it sags down and drifts off; a crate stays while it is used.</summary>
        private static bool Settle(Faller f, float now)
        {
            var c = Mathf.Clamp01((now - f.Landed) / 1.2f);
            if (f.Chute != null && f.Chute.gameObject.activeSelf)
            {
                f.Chute.localScale = new Vector3(1f + c * 0.4f, Mathf.Lerp(1f, 0.05f, c), 1f + c * 0.4f);
                f.Chute.localPosition = new Vector3(c * 2.5f, 0f, c * 1.5f);
                if (c >= 1f) f.Chute.gameObject.SetActive(false);
            }
            return now >= f.Landed + Mathf.Max(1.2f, f.Linger);
        }

        private void HideBombs()
        {
            foreach (var jet in _jets)
                if (jet.Active && jet.Bombs != null) jet.Bombs.gameObject.SetActive(false);
        }

        /// <summary>
        /// A canopy on four cords over <paramref name="parent"/>: <paramref name="size"/> across,
        /// its crown <paramref name="hang"/> above, the cords meeting the load <paramref name="width"/>
        /// out from its centre.
        /// </summary>
        private Transform Chute(Transform parent, float size, float hang, float width, float attach = 0.6f)
        {
            var chute = new GameObject("Parachute").transform;
            chute.SetParent(parent, false);
            var canopy = Part(chute, _canopy);
            canopy.localPosition = new Vector3(0f, hang, 0f);
            canopy.localScale = new Vector3(size, size * 0.5f, size);
            for (var k = 0; k < 4; k++)
            {
                var corner = new Vector3(k % 2 == 0 ? -1f : 1f, 0f, k < 2 ? -1f : 1f);
                var bottom = new Vector3(corner.x * width, attach, corner.z * width);
                var top = canopy.localPosition + new Vector3(corner.x * size * 0.42f, 0f, corner.z * size * 0.42f);
                var cord = Part(chute, _box);
                cord.localPosition = (top + bottom) * 0.5f;
                cord.localRotation = Quaternion.FromToRotation(Vector3.up, top - bottom);
                cord.localScale = new Vector3(0.05f, (top - bottom).magnitude, 0.05f);
            }
            return chute;
        }

        private Transform Part(Transform parent, Mesh mesh)
        {
            var go = new GameObject(mesh.name, typeof(MeshFilter), typeof(MeshRenderer));
            go.transform.SetParent(parent, false);
            go.GetComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = _cloth;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            return go.transform;
        }

        /// <summary>The napalm canisters (tumbling) or a cluster strike's dispensers and bomblets, in place of bombs.</summary>
        private bool DropsOwnRounds(SupportDef support, IReadOnlyList<(float at, Vector3 from, Vector3 to)> drops, Vector3 forward, float speed)
        {
            if (support.DamageType == DamageType.Fire)
            {
                foreach (var (at, from, to) in drops) Add(Round.Canister, Canister(_silver, 2.4f), from, to, at - BombFall, at);
                return true;
            }
            if (drops.Count < 24) return false;
            // Two dozen and more: bomblets. Dispensers of ten each fall from under the wings and split
            // open 14 m up, and their bomblets rain onto their own marks.
            for (var g = 0; g < drops.Count; g += 10)
            {
                var last = Mathf.Min(drops.Count, g + 10) - 1;
                var first = drops[g].at;
                var centre = Vector3.Lerp(drops[g].to, drops[last].to, 0.5f);
                var opens = first - 0.5f;
                var open = centre - forward * (speed * 0.5f) + Vector3.up * 14f;
                Add(Round.Dispenser, Body("bomb", null, 1.6f), drops[g].from, open, first - BombFall, opens);
                for (var k = g; k <= last; k++)
                    Add(Round.Bomblet, Canister(_yellow, 1f), open + Random.insideUnitSphere * 1.2f, drops[k].to, opens, drops[k].at);
            }
            return true;
        }

        /// <summary>The EMP's energy warhead dropping onto the mark as the strike lands.</summary>
        private void DropWarhead(Vector3 point, float impact)
        {
            var body = new GameObject("Warhead");
            body.transform.SetParent(_root, false);
            Add(Round.Warhead, body, point + new Vector3(-8f, 70f, -5f), point + Vector3.up * 0.8f, impact - 1.3f, impact);
        }

        /// <summary>A repair drop: a crate under a parachute onto the mark, staying while it repairs.</summary>
        private void DropCrate(Vector3 point, float impact, float delay, float linger)
        {
            var model = _models.Has("repair_crate") ? "repair_crate" : "supply_crate";
            var fall = Mathf.Clamp(delay, 0.4f, 2.2f);
            var f = Add(Round.Crate, Body(model, null, 1.6f), point + Vector3.up * 30f, point, impact - fall, impact);
            f.Linger = linger;
            // The crate model comes with its own canopy; the plain one gets ours.
            if (model != "repair_crate") f.Chute = Chute(f.Root.transform, 3.4f, 5.5f, 0.55f);
        }

        /// <summary>
        /// The MOAB: a transport passes over and the bomb rolls out of its ramp on a drogue chute,
        /// the chute is cut away and it falls nose-first onto the mark. A strike with no direction
        /// runs along +X, as the simulation's does.
        /// </summary>
        private void DropMoab(int team, Vector3 point, float impact)
        {
            const float fall = 2.6f, drift = 16f, altitude = 55f;
            var run = Vector3.right;
            var release = point - run * (drift * fall) + Vector3.up * altitude;
            if (_models.Has(TransportModel))
                Flyer(TransportModel, team, release - run * TransportSpeed * 2f + Vector3.up * 2f, release + run * TransportSpeed * 3f + Vector3.up * 2f,
                    impact - fall - 2f, 5f, false);
            var f = Add(Round.Moab, Body(_models.Has("bomb_mk84") ? "bomb_mk84" : "bomb", null, 2.8f), release, point + Vector3.up * 0.5f, impact - fall, impact);
            // The drogue streams behind it (the bomb's nose leads along +Z).
            f.Chute = Chute(f.Root.transform, 3f, 6f, 0.3f, 0f);
            f.Chute.localRotation = Quaternion.Euler(-90f, 0f, 0f);
        }

        /// <summary>
        /// Reinforcements by airlift: a transport passes over the mark and each vehicle comes down
        /// under a canopy onto the spot the battle hands it over at (StrikeSystem: 6 m out round
        /// the mark, facing +X, the heading of a support called with no direction).
        /// </summary>
        private void Airlift(SupportDef support, int team, Vector3 point, float impact, float delay)
        {
            var fall = Mathf.Min(2.3f, delay * 0.8f);
            var release = impact - fall;
            var over = point + Vector3.up * TransportAltitude;
            var run = Vector3.right;
            if (_models.Has(TransportModel))
                Flyer(TransportModel, team, over - run * TransportSpeed * 1.6f, over + run * TransportSpeed * 2.2f, release - 1.6f, 3.8f, false);
            var units = support.Units;
            for (var k = 0; k < units.Count; k++)
            {
                if (!_catalog.Vehicles.TryGetValue(units[k], out var def) || def.Flying || !_models.Has(def.Model)) continue;
                var angle = k * Mathf.PI * 2f / Mathf.Max(1, units.Count);
                var at = point + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * (units.Count > 1 ? 6f : 0f);
                var body = _models.Spawn(def.Model, team, _root, castShadows: false).Root;
                body.transform.localScale = Vector3.one * VehicleView.DrawScaleOf(def, body);
                var f = Add(Round.Vehicle, body, at + Vector3.up * (TransportAltitude - 4f), at, release + k * 0.12f, impact);
                f.Heading = 90f;
                f.Chute = Chute(f.Root.transform, Mathf.Max(def.Length, def.Width) * 0.65f + 0.8f, 5f + Mathf.Max(def.Length, def.Width) * 0.26f,
                    Mathf.Max(def.Length, def.Width) * 0.3f, 1.6f);
            }
        }

        /// <summary>Destroys an object in play and in the editor's batch renders alike.</summary>
        private static void Kill(Object o)
        {
            if (Application.isPlaying) Object.Destroy(o);
            else Object.DestroyImmediate(o);
        }

        /// <summary>A unit dome (radius 1, height 1) open at the bottom, its outside facing out (seen from above).</summary>
        private static Mesh Dome(int segments, int rings)
        {
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            for (var r = 0; r <= rings; r++)
            {
                var polar = r / (float)rings * Mathf.PI * 0.5f;
                for (var s = 0; s <= segments; s++)
                {
                    var azimuth = s / (float)segments * Mathf.PI * 2f;
                    var scallop = r == rings ? 0.94f + 0.06f * Mathf.Cos(azimuth * segments * 0.5f) : 1f;
                    vertices.Add(new Vector3(Mathf.Sin(polar) * Mathf.Cos(azimuth) * scallop, Mathf.Cos(polar), Mathf.Sin(polar) * Mathf.Sin(azimuth) * scallop));
                }
            }
            for (var r = 0; r < rings; r++)
                for (var s = 0; s < segments; s++)
                {
                    var a = r * (segments + 1) + s;
                    var b = a + segments + 1;
                    triangles.AddRange(new[] { a, a + 1, b, a + 1, b + 1, b });
                }
            var mesh = new Mesh { name = "Canopy" };
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Vector3 Ground(System.Numerics.Vector2 p) => new Vector3(p.X, 0f, p.Y);
    }
}
