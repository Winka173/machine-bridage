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
    /// Prompt 31 L3 (DECISIONS "Prompt 31 L3"): the five FIRST events of the sheet "Biến cố". Each is warned 8-12 s ahead (a
    /// system notice and its places on the minimap, <see cref="EventState.Marks"/>; the line is extra), happens on a step the
    /// battle's clock and conditions decide (a replay of the same seed and commands meets it on the same step), and any ground
    /// it changes is a prebuilt state of the mission (<see cref="Navigation.NavStates"/>) switched at a tick boundary.
    /// <list type="bullet">
    /// <item>GroundChange (the factory alarm): a site ("navSite") goes to a state ("navState"): the mill gate shuts.</item>
    /// <item>SandstormTurn: the wind turns, the storm rolls over one half ("half": player, east, west, north, south): sight
    /// there times "sight", the other half times "clear", rolling in over "seconds" (20-30), clearing after "hold" (0: stays).</item>
    /// <item>CityBlackout: night falls over "seconds" and every tower on the grid ("towers", both sides') is knocked out for "outage" seconds.</item>
    /// <item>BetrayalWarning: the allied columns marked before they turn (the turning itself is the stage's Betrayal).</item>
    /// <item>OrbitalPods: pods on prebuilt landing sites ("sites", each a site with states "clear" and "landed") stand up as the
    /// enemy's "towers"; a tower destroyed opens its ground again.</item>
    /// </list>
    /// </summary>
    public sealed partial class MissionEventSystem
    {
        /// <summary>The towers that run on the city's grid (radars, searchlights, lasers, shields, fire control) unless an event names its own.</summary>
        public static readonly string[] GridTowers =
        {
            "radar_station", "ew_tower", "searchlight", "flare_searchlight_tower", "laser_ad_station", "shield_tower", "fire_control_centre",
            "targeting_station", "c_ram", "visual_jammer",
        };

        private sealed class GroundPlan
        {
            public string Site = "", State = "";
        }

        private sealed class StormPlan
        {
            public Vector2 Origin, Normal;
            public float Inside = 0.6f, Outside = 1f, Seconds = 25f, Hold = 150f;
            public double ClearFrom = -1;
        }

        private sealed class PowerPlan
        {
            public readonly WeatherPlan Weather = new() { To = "Night" };
            public readonly List<EntityId> Towers = new();
            public float Outage = 90f;
            public bool Night = true;
        }

        private sealed class PodPlan
        {
            public readonly List<(string site, string def, Vector2 at)> Drops = new();
            public readonly List<(double due, int drop)> Falling = new();
            public readonly List<(EntityId id, string site)> Landed = new();
        }

        private sealed class IcePlan
        {
            public Vector2 Centre;
            public float Radius = 30f, Seconds = 10f, Slow = 0.4f, SlowFor = 8f;

            /// <summary>When each ice-breaking vehicle on the ice came onto it (or its ice last gave): looked up, never walked.</summary>
            public readonly Dictionary<EntityId, double> Since = new();

            public double QuietUntil;
        }

        /// <summary>Whether the enemy sees one of the player's own vehicles (an infiltration found out).</summary>
        private static bool Spotted(SimWorld world)
        {
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Player && !v.Scripted && !v.Def.Static && v.IsVisibleTo(Enemy)) return true;
            return false;
        }

        /// <summary>Prompt 31 L5: the prop each "propDown" trigger watches (its instance: the prop's id, None where none stands).</summary>
        private readonly Dictionary<string, EntityId> _watchedProps = new(StringComparer.Ordinal);

        /// <summary>Prompt 31 L5: whether the prop a trigger watches (its def nearest its point, within 8 m) has been destroyed.</summary>
        private bool PropDown(SimWorld world, EventState s)
        {
            var t = s.Def.Trigger;
            if (!_watchedProps.TryGetValue(s.Def.Instance, out var id))
            {
                id = EntityId.None;
                var at = new Vector2(t.PropX, t.PropZ);
                var best = 8f * 8f;
                // The props in the order the map placed them: the same pick in every replay.
                foreach (var p in world.Props)
                {
                    if (p.Def.Id != t.PropDown) continue;
                    var d = Vector2.DistanceSquared(p.Position, at);
                    if (d > best) continue;
                    best = d;
                    id = p.Id;
                }
                _watchedProps[s.Def.Instance] = id;
            }
            return id.IsValid && world.TryGetProp(id, out var prop) && !prop.IsAlive;
        }

        private bool PrepareP31(SimWorld world, EventState s)
        {
            var e = s.Def;
            switch (e.Kind)
            {
                case MissionEventKind.GroundChange:
                {
                    var site = e.Word("navSite");
                    if (site == null || !world.NavStates.TryGet(site, out var held)) return false;
                    // Prompt 31 L5: "cycle" goes to the site's next state that passed the checks (the tide in and out, the
                    // dam's water a level higher; "wrap": false stops at the last), else the named "navState".
                    var state = e.Flag("cycle", false) ? NextState(held, e.Flag("wrap", true)) : e.Word("navState");
                    if (state == null || !world.NavStates.CanSwitch(site, state) || held.ActiveName == state) return false;
                    var to = held.Def.States[held.Def.IndexOf(state)];
                    // Prompt 31 L5: "text" picks the notice and line by the state coming in ("event.groundChange.<text>.<state>.warn").
                    s.Variant = e.Word("text") is { } text ? text + "." + state : null;
                    // The ground it closes, and (prompt 31 L5) the ground it opens: the state in force's blocks the new one has not.
                    foreach (var b in to.Blocks) s.Marks.Add((b.Center, MathF.Max(b.Width, b.Depth) * 0.5f + 6f));
                    foreach (var b in held.Def.States[held.Active].Blocks)
                    {
                        var kept = false;
                        foreach (var k in to.Blocks)
                            if (k.Center == b.Center && k.Width == b.Width && k.Depth == b.Depth) kept = true;
                        if (!kept) s.Marks.Add((b.Center, MathF.Max(b.Width, b.Depth) * 0.5f + 6f));
                    }
                    s.Where = s.Marks.Count > 0 ? s.Marks[0].at : world.Map.Centre;
                    s.Plan = new GroundPlan { Site = site, State = state };
                    return true;
                }
                case MissionEventKind.SandstormTurn:
                {
                    var plan = new StormPlan
                    {
                        Origin = world.Map.Centre,
                        Normal = StormSide(world, e.Word("half") ?? "player"),
                        Inside = e.Number("sight", 0.6f),
                        Outside = e.Number("clear", 1f),
                        Seconds = Math.Clamp(e.Number("seconds", 25f), 20f, 30f),
                        Hold = MathF.Max(0f, e.Number("hold", 150f)),
                    };
                    var quarter = world.Map.HalfSize * 0.5f;
                    var across = new Vector2(-plan.Normal.Y, plan.Normal.X);
                    for (var k = -1; k <= 1; k++) s.Marks.Add((plan.Origin + plan.Normal * quarter + across * (k * quarter * 1.2f), quarter * 0.6f));
                    s.Where = plan.Origin + plan.Normal * quarter;
                    s.Plan = plan;
                    return true;
                }
                case MissionEventKind.CityBlackout:
                {
                    var plan = new PowerPlan { Outage = MathF.Max(30f, e.Number("outage", 90f)) };
                    plan.Weather.Seconds = Math.Clamp(e.Number("seconds", 25f), 20f, 30f);
                    plan.Night = (_weatherNow ?? _host.Def.Weather) != "Night";
                    plan.Outage = MathF.Max(plan.Outage, plan.Weather.Seconds + 1f);
                    var towers = new HashSet<string>(e.Words("towers").Count > 0 ? e.Words("towers") : GridTowers);
                    foreach (var v in world.VehicleList)
                    {
                        if (!v.IsAlive || !v.Def.Static || v.Def.Boss || !towers.Contains(v.Def.Id)) continue;
                        plan.Towers.Add(v.Id);
                        if (s.Marks.Count < 8) s.Marks.Add((v.Position, 8f));
                    }
                    if (!plan.Night && plan.Towers.Count == 0) return false;
                    s.Where = s.Marks.Count > 0 ? s.Marks[0].at : world.Map.Centre;
                    s.Plan = plan;
                    return true;
                }
                case MissionEventKind.BetrayalWarning:
                {
                    foreach (var v in world.VehicleList)
                    {
                        if (!v.IsAlive || !v.Ally || v.Team != Player) continue;
                        var near = false;
                        foreach (var (at, _) in s.Marks)
                            if (Vector2.DistanceSquared(at, v.Position) < 20f * 20f) near = true;
                        if (!near && s.Marks.Count < 6) s.Marks.Add((v.Position, 12f));
                    }
                    if (s.Marks.Count == 0) return false;
                    s.Where = s.Marks[0].at;
                    return true;
                }
                case MissionEventKind.IceCrack:
                {
                    var plan = new IcePlan
                    {
                        Centre = new Vector2(e.Number("x", 0f), e.Number("z", 0f)),
                        Radius = MathF.Max(4f, e.Number("radius", 30f)),
                        Seconds = MathF.Max(1f, e.Number("seconds", 10f)),
                        Slow = Math.Clamp(e.Number("slow", 0.4f), 0.05f, 0.9f),
                        SlowFor = MathF.Max(1f, e.Number("slowFor", 8f)),
                    };
                    s.Marks.Add((plan.Centre, plan.Radius));
                    s.Where = plan.Centre;
                    s.Plan = plan;
                    return true;
                }
                case MissionEventKind.OrbitalPods:
                {
                    var plan = new PodPlan();
                    var towers = e.Words("towers").Count > 0 ? e.Words("towers") : new[] { "gun_turret" };
                    foreach (var site in e.Words("sites"))
                    {
                        if (!world.NavStates.TryGet(site, out var held) || held.ActiveName != "clear" || !world.NavStates.CanSwitch(site, "landed")) continue;
                        var landed = held.Def.States[held.Def.IndexOf("landed")];
                        var at = landed.Blocks.Count > 0 ? landed.Blocks[0].Center : world.Map.Centre;
                        var def = towers[plan.Drops.Count % towers.Count];
                        if (!world.Catalog.Vehicles.ContainsKey(def)) continue;
                        plan.Drops.Add((site, def, at));
                        s.Marks.Add((at, 10f));
                    }
                    if (plan.Drops.Count == 0) return false;
                    s.Where = plan.Drops[0].at;
                    s.Plan = plan;
                    return true;
                }
                default:
                    return true;
            }
        }

        /// <summary>
        /// Prompt 31 L5: the state after the one in force (or the one waiting to come in) that passed the load-time checks; with
        /// <paramref name="wrap"/> the last goes back to the first, without it there is none after the last (null).
        /// </summary>
        private static string? NextState(Navigation.NavSite site, bool wrap)
        {
            var count = site.Def.States.Count;
            var from = site.Pending >= 0 ? site.Pending : site.Active;
            for (var step = 1; step < count; step++)
            {
                var i = from + step;
                if (i >= count)
                {
                    if (!wrap) return null;
                    i -= count;
                }
                if (site.IsValid(i)) return site.Def.States[i].Name;
            }
            return null;
        }

        /// <summary>The half a storm rolls over: a named side, or the side the player's biggest group stands in.</summary>
        private static Vector2 StormSide(SimWorld world, string half)
        {
            switch (half)
            {
                case "east": return Vector2.UnitX;
                case "west": return -Vector2.UnitX;
                case "north": return Vector2.UnitY;
                case "south": return -Vector2.UnitY;
            }
            var at = (Group(world, Player) ?? (world.TryGetRally(Player, out var home) ? home : world.Map.Centre)) - world.Map.Centre;
            if (at.LengthSquared() < 1f) return Vector2.UnitX;
            return MathF.Abs(at.X) >= MathF.Abs(at.Y) ? new Vector2(MathF.Sign(at.X), 0f) : new Vector2(0f, MathF.Sign(at.Y));
        }

        private Outcome HappenP31(SimWorld world, EventState s)
        {
            switch (s.Def.Kind)
            {
                case MissionEventKind.GroundChange:
                {
                    var plan = (GroundPlan)s.Plan!;
                    // The switch comes in at the start of the next step, before anything moves.
                    if (!world.NavStates.Schedule(plan.Site, plan.State, world.Tick + 1, world.Tick)) Record(world, s, "refused");
                    Notice(world, s, "start", 0f);
                    return Outcome.Done;
                }
                case MissionEventKind.SandstormTurn:
                {
                    var plan = (StormPlan)s.Plan!;
                    world.SetStorm(plan.Origin, plan.Normal, world.StormInside, world.StormOutside);
                    if ((_weatherNow ?? _host.Def.Weather) != "Sandstorm") world.Emit(SimEvent.WeatherShifting("Sandstorm", plan.Seconds));
                    s.EndsAt = plan.Hold > 0f ? world.Time + plan.Seconds + plan.Hold : -1;
                    return Outcome.Running;
                }
                case MissionEventKind.CityBlackout:
                {
                    var plan = (PowerPlan)s.Plan!;
                    if (plan.Night)
                    {
                        var sight = Rules.WeatherSight;
                        var from = _weatherNow ?? _host.Def.Weather;
                        var ratio = (sight.TryGetValue("Night", out var to) ? to : 0.75f) / MathF.Max(0.1f, sight.TryGetValue(from, out var was) ? was : 1f);
                        plan.Weather.From = world.WeatherSight;
                        plan.Weather.Target = Math.Clamp(world.WeatherSight * ratio, 0.5f, 1.3f);
                        _weatherNow = "Night";
                        world.Emit(SimEvent.WeatherShifting("Night", plan.Weather.Seconds));
                    }
                    var until = world.Time + plan.Outage;
                    foreach (var id in plan.Towers)
                        if (world.TryGetVehicle(id, out var v) && v.IsAlive) world.Status.Stun(v, until);
                    s.EndsAt = until;
                    return Outcome.Running;
                }
                case MissionEventKind.IceCrack:
                    // The ice is thin from now to the end of the battle (its ring stays on the minimap).
                    s.EndsAt = -1;
                    return Outcome.Running;
                case MissionEventKind.OrbitalPods:
                {
                    var plan = (PodPlan)s.Plan!;
                    var fall = MathF.Max(2f, s.Def.Number("fall", 6f));
                    world.Catalog.TryGetSupport("pod_drop", out var pod);
                    for (var k = 0; k < plan.Drops.Count; k++)
                    {
                        var at = plan.Drops[k].at;
                        if (pod != null) world.Emit(SimEvent.StrikeWarning(Enemy, pod, at, at, fall));
                        plan.Falling.Add((world.Time + fall + k * 0.6, k));
                    }
                    Notice(world, s, "start", fall);
                    return Outcome.Running;
                }
                default:
                    // BetrayalWarning: the warning was the event; the stage's own Betrayal turns the ally.
                    return Outcome.Done;
            }
        }

        private void UpdateP31(SimWorld world, EventState s)
        {
            switch (s.Def.Kind)
            {
                case MissionEventKind.SandstormTurn:
                {
                    var plan = (StormPlan)s.Plan!;
                    if (plan.ClearFrom < 0)
                    {
                        var t = (float)Math.Clamp((world.Time - s.StartAt) / Math.Max(0.1, plan.Seconds), 0.0, 1.0);
                        world.SetStorm(plan.Origin, plan.Normal, 1f + (plan.Inside - 1f) * t, 1f + (plan.Outside - 1f) * t);
                        if (s.EndsAt >= 0 && world.Time >= s.EndsAt)
                        {
                            plan.ClearFrom = world.Time;
                            Notice(world, s, "end", 0f);
                        }
                        break;
                    }
                    var c = (float)Math.Clamp((world.Time - plan.ClearFrom) / Math.Max(0.1, plan.Seconds), 0.0, 1.0);
                    world.SetStorm(plan.Origin, plan.Normal, plan.Inside + (1f - plan.Inside) * c, plan.Outside + (1f - plan.Outside) * c);
                    if (c >= 1f) Finish(world, s, true, "end");
                    break;
                }
                case MissionEventKind.CityBlackout:
                {
                    var plan = (PowerPlan)s.Plan!;
                    if (plan.Night)
                    {
                        var t = (float)Math.Clamp((world.Time - s.StartAt) / Math.Max(0.1, plan.Weather.Seconds), 0.0, 1.0);
                        world.WeatherSight = plan.Weather.From + (plan.Weather.Target - plan.Weather.From) * t;
                    }
                    if (world.Time < s.EndsAt) break;
                    // The grid's backup comes on: the towers work again (the night stays).
                    Notice(world, s, "end", 0f);
                    Finish(world, s, true, "end");
                    break;
                }
                case MissionEventKind.OrbitalPods:
                    StepPods(world, s, (PodPlan)s.Plan!);
                    break;
                case MissionEventKind.IceCrack:
                    StepIce(world, s, (IcePlan)s.Plan!);
                    break;
            }
        }

        /// <summary>
        /// Prompt 31 L5: every vehicle that breaks ice (<see cref="VehicleDef.BreaksIce"/>: its weight class) and has been on the
        /// lake <see cref="IcePlan.Seconds"/> is slowed as the ice gives under it, and its clock starts again; off the ice it
        /// starts afresh. The vehicles in the world's order, the clocks on the battle's time: a replay cracks the same ice on the
        /// same step. Nobody is stopped or trapped: a slow only.
        /// </summary>
        private void StepIce(SimWorld world, EventState s, IcePlan plan)
        {
            var reach = plan.Radius * plan.Radius;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || !v.Def.BreaksIce || Vector2.DistanceSquared(v.Position, plan.Centre) > reach)
                {
                    plan.Since.Remove(v.Id);
                    continue;
                }
                if (!plan.Since.TryGetValue(v.Id, out var since))
                {
                    plan.Since[v.Id] = world.Time;
                    continue;
                }
                if (world.Time - since < plan.Seconds) continue;
                world.Status.Slow(v, plan.Slow, plan.SlowFor);
                plan.Since[v.Id] = world.Time;
                // The notice when the ice gives under one of ours, not more than once in 20 s.
                if (v.Team != Player || world.Time < plan.QuietUntil) continue;
                plan.QuietUntil = world.Time + 20.0;
                Notice(world, s, "start", 0f, v.Id);
            }
        }

        private void StepPods(SimWorld world, EventState s, PodPlan plan)
        {
            for (var i = 0; i < plan.Falling.Count; i++)
            {
                var (due, k) = plan.Falling[i];
                if (world.Time < due) continue;
                plan.Falling.RemoveAt(i--);
                var (site, def, at) = plan.Drops[k];
                var facing = world.TryGetRally(Player, out var home) ? home - at : -at;
                var tower = world.SpawnVehicle(def, Enemy, at, SimMath.HeadingOf(facing.LengthSquared() > 1f ? facing : Vector2.UnitY));
                // The landing site's prebuilt state holds the ground, not the tower's own anchor (it opens when the tower falls).
                world.ReleaseGround(tower);
                world.NavStates.Schedule(site, "landed", world.Tick + 1, world.Tick);
                s.Units.Add(tower.Id);
                plan.Landed.Add((tower.Id, site));
                // The minimap marks the sites while the pods fall; once down, the towers are on the map as any enemy is.
                if (plan.Falling.Count == 0) s.Marks.Clear();
            }
            var standing = 0;
            foreach (var (id, site) in plan.Landed)
            {
                if (world.TryGetVehicle(id, out var v) && v.IsAlive)
                {
                    standing++;
                    continue;
                }
                if (world.NavStates.ActiveOf(site) == "landed") world.NavStates.Schedule(site, "clear", world.Tick + 1, world.Tick);
            }
            if (plan.Falling.Count == 0 && standing == 0 && plan.Landed.Count > 0)
            {
                var open = true;
                foreach (var (_, site) in plan.Landed)
                    if (world.NavStates.TryGet(site, out var held) && (held.ActiveName == "landed" || held.Pending >= 0)) open = false;
                if (open) Finish(world, s, true);
            }
        }
    }
}
