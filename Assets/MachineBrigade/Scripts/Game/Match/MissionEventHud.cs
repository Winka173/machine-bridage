using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 23 (DECISIONS 23F, lead note): the event markers read from 23A's mission events. The Accord mark and the
    /// general's label come from the vehicle; the arrows from each warned event's directions for as long as its warning runs;
    /// the side-objective row from each side objective's clock and count (its start, success and failure notices are the
    /// event system's own, so the row does not announce them again).
    /// </summary>
    internal sealed class MissionEventHud : IEventHudSource
    {
        private readonly SimWorld _world;

        public MissionEventHud(SimWorld world) => _world = world;

        public bool Accord(Vehicle unit) => unit.Accord;

        public string General(Vehicle unit) => unit.General;

        public void Arrows(List<EventArrow> into)
        {
            var now = _world.Time;
            foreach (var system in _world.MissionEvents)
                foreach (var s in system.States)
                {
                    if (s.Phase != EventPhase.Warned || s.StartAt <= now || s.Arrows.Count == 0) continue;
                    var enemy = s.Def.Kind != MissionEventKind.AllyWave;
                    foreach (var (at, inward, _) in s.Arrows)
                        into.Add(new EventArrow { Direction = -inward, SecondsLeft = (float)(s.StartAt - now), Enemy = enemy, At = at });
                }
        }

        public void SideObjectives(List<SideObjectiveInfo> into)
        {
            var now = _world.Time;
            foreach (var system in _world.MissionEvents)
                foreach (var s in system.States)
                {
                    if (s.Def.Kind != MissionEventKind.SideObjective || s.Phase is EventPhase.Waiting or EventPhase.Warned) continue;
                    var type = s.Def.Word("type") ?? "intercept";
                    into.Add(new SideObjectiveInfo
                    {
                        Id = s.Def.Id + "#" + s.Fired,
                        Text = Strings.Get("event.sideObjective." + type + ".row"),
                        SecondsLeft = s.SecondsLeft(now),
                        Count = s.Count,
                        Needed = s.Needed,
                        Outcome = s.Phase switch
                        {
                            EventPhase.Done => SideObjectiveOutcome.Succeeded,
                            EventPhase.Failed => SideObjectiveOutcome.Failed,
                            _ => SideObjectiveOutcome.Running,
                        },
                    });
                }
        }
    }
}
