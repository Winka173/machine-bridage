#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Prompt 30 L6: the neutral sites of the V1 list. A side's ground vehicles alone on a site for a few seconds take it
    /// (another side takes it the same way). Radar: the holder sees round it. Field workshop: the holder's ground vehicles
    /// near it mend slowly. Abandoned AA site: taking it raises an AA gun for the holder (taken over by the next holder;
    /// destroyed, the site stands abandoned again a while later). Ammo depot: the holder's vehicles near it are resupplied
    /// quickly; shot to pieces, it blows up (a blast that hurts everyone). The sites a mode uses come from the data; the
    /// coastal battery, the lighthouse, the contested supply drop and the neutral convoy already exist (Naval, BattleEvents).
    /// </summary>
    public sealed class NeutralSystem
    {
        private sealed class Site
        {
            public NeutralSiteDef Def;
            public int Team = -1, ProgressTeam = -1;
            public float Progress;
            public EntityId Gun, Building;
            public double RebuildAt;
            public bool Gone;
        }

        private readonly SimWorld _world;
        private readonly List<Site> _sites = new();
        private bool _ready;
        private float _timer;

        /// <summary>Seconds between two of the sites' updates.</summary>
        private const float Interval = 0.5f;

        public NeutralSystem(SimWorld world) => _world = world;

        /// <summary>The sites in play: kind, place and holder (-1 neutral), for the HUD and the map.</summary>
        public IEnumerable<(string kind, Vector2 at, int team)> Sites
        {
            get
            {
                foreach (var s in _sites)
                    if (!s.Gone) yield return (s.Def.Kind, s.Def.At, s.Team);
            }
        }

        /// <summary>
        /// Prompt 30 L6 (read only, for the view): each site as <see cref="Sites"/> has it, with the capture under way (the side
        /// taking it, -1 none, and how far, 0-1) and whether an abandoned AA site still waits before it can be taken again.
        /// </summary>
        public IEnumerable<(string kind, Vector2 at, int team, int taking, float progress, bool waiting)> SiteStates
        {
            get
            {
                foreach (var s in _sites)
                    if (!s.Gone) yield return (s.Def.Kind, s.Def.At, s.Team, s.ProgressTeam, s.Progress, _world.Time < s.RebuildAt);
            }
        }

        /// <summary>How close a side's ground vehicles must stand to take a site (the view's capture ring).</summary>
        public float CaptureRadius => N("captureRadius", 10f);

        private float N(string key, float fallback) => _world.Catalog.Neutrals.Get(key, fallback);

        private void Ready()
        {
            _ready = true;
            var kinds = _world.Catalog.Neutrals.KindsFor(_world.ModeTag);
            foreach (var def in _world.Map.Neutrals)
            {
                if (!Has(kinds, def.Kind) || !_world.Grid.IsWalkable(def.At)) continue;
                var site = new Site { Def = def };
                // The site's building (a prop of the map, 6 m behind the spot) is watched: the ammo depot blows up with it.
                var best = float.MaxValue;
                var building = Building(def.Kind);
                foreach (var p in _world.Props)
                {
                    var d = Vector2.DistanceSquared(p.Position, def.At);
                    if (building != null && p.Def.Id == building && d < 81f && d < best)
                    {
                        best = d;
                        site.Building = p.Id;
                    }
                }
                _sites.Add(site);
            }
        }

        /// <summary>The prop that marks a kind's site (Tools/maps/neutrals.py); the AA site has none until taken.</summary>
        private static string? Building(string kind) => kind switch
        {
            "radar" => "radar_dome",
            "workshop" => "garage",
            "ammo_depot" => "ammo_dump",
            _ => null,
        };

        private static bool Has(IReadOnlyList<string> list, string value)
        {
            foreach (var x in list)
                if (x == value) return true;
            return false;
        }

        public void Step(float dt)
        {
            if (!_ready) Ready();
            if (_sites.Count == 0) return;
            _timer -= dt;
            if (_timer > 0f) return;
            var step = Interval - _timer;
            _timer = Interval;
            foreach (var s in _sites)
            {
                if (s.Gone) continue;
                Capture(s, step);
                if (s.Team is not (0 or 1)) continue;
                switch (s.Def.Kind)
                {
                    case "radar":
                        _world.Strikes.AddScan(s.Team, s.Def.At, N("radar.radius", 45f), Interval * 2f);
                        break;
                    case "workshop":
                        Mend(s, step);
                        break;
                    case "ammo_depot":
                        Resupply(s, step);
                        break;
                }
                if (s.Def.Kind == "ammo_depot" && s.Building.IsValid && !(_world.TryGetProp(s.Building, out var b) && b.IsAlive)) Blow(s);
            }
        }

        /// <summary>The one side with ground vehicles on the site (-1: nobody, or both).</summary>
        private int Holder(Vector2 at, float radius)
        {
            var side = -1;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Def.Static || v.Team is not (0 or 1)) continue;
                if (Vector2.DistanceSquared(v.Position, at) > radius * radius) continue;
                if (side >= 0 && side != v.Team) return -1;
                side = v.Team;
            }
            return side;
        }

        private void Capture(Site s, float dt)
        {
            if (s.Def.Kind == "aa_site" && s.Team >= 0 && !(_world.TryGetVehicle(s.Gun, out var gun) && gun.IsAlive))
            {
                // Its gun destroyed: abandoned, usable again after a while.
                s.Team = -1;
                s.Gun = EntityId.None;
                s.RebuildAt = _world.Time + N("aa.rebuild", 60f);
            }
            if (_world.Time < s.RebuildAt) return;
            var side = Holder(s.Def.At, N("captureRadius", 10f));
            if (side < 0 || side == s.Team)
            {
                if (side < 0) s.Progress = 0f;
                return;
            }
            s.Progress = s.ProgressTeam == side ? s.Progress + dt / N("captureSeconds", 8f) : dt / N("captureSeconds", 8f);
            s.ProgressTeam = side;
            if (s.Progress < 1f) return;
            s.Team = side;
            s.Progress = 0f;
            s.ProgressTeam = -1;
            if (s.Def.Kind == "aa_site")
            {
                if (_world.TryGetVehicle(s.Gun, out var g) && g.IsAlive) _world.Defect(g, side);
                else
                {
                    var def = _world.Catalog.Vehicles.ContainsKey("aa_turret") ? "aa_turret" : "aa_gun_tower";
                    s.Gun = _world.SpawnVehicle(def, side, s.Def.At, 0f).Id;
                }
            }
            _world.Emit(SimEvent.NeutralTaken(s.Def.Kind, s.Def.At, side));
        }

        private void Mend(Site s, float dt)
        {
            var radius = N("workshop.radius", 14f);
            var rate = N("workshop.repair", 0.015f);
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != s.Team || v.Flying || v.Def.Static || v.Def.Boss || v.Hp >= v.MaxHp) continue;
                if (Vector2.DistanceSquared(v.Position, s.Def.At) > radius * radius) continue;
                v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * rate * dt);
            }
        }

        private readonly Dictionary<EntityId, double> _resupplied = new();

        private void Resupply(Site s, float dt)
        {
            var radius = N("ammo.radius", 14f);
            var every = N("ammo.seconds", 6f);
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != s.Team || v.Def.Static || !v.NeedsAmmo) continue;
                if (Vector2.DistanceSquared(v.Position, s.Def.At) > radius * radius) continue;
                if (_resupplied.TryGetValue(v.Id, out var at) && _world.Time - at < every) continue;
                _resupplied[v.Id] = _world.Time;
                _world.Abilities.Resupply(v);
            }
        }

        /// <summary>The depot shot to pieces: it goes up, hurting everyone near.</summary>
        private void Blow(Site s)
        {
            s.Gone = true;
            _world.Damage.Splash(s.Def.At, N("ammo.blast", 14f), N("ammo.damage", 300f), DamageType.HighExplosive, Teams.Environment, EntityId.None);
        }
    }

}
