using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 23 F in a battle (DECISIONS 23F), kept apart from MatchRunner.cs: which of our units are the Meridian Accord's
    /// (F.4), the name labels over the enemy generals' vehicles with their speaking mark (F.5), and, from the event system,
    /// the direction arrows (F.2) and the side objective's row (F.3). The inputs:
    /// <list type="bullet">
    /// <item><see cref="EventHudSource"/>: the event system's adapter (<see cref="IEventHudSource"/>): the Accord's units,
    /// the generals in units, the arrows with their warning time, the side objectives. Set, it takes the arrows over from the
    /// notices.</item>
    /// <item>F.2 without it: a notice with a direction (<c>_hud.Toast(..., direction: d)</c>) or <see cref="BattleHud.Arrow"/>.</item>
    /// <item>F.4 also: the simulation's allied-unit tag (<see cref="Vehicle.Ally"/>) and <see cref="MarkAccord"/>.</item>
    /// <item>F.5 also: a def with a general (<see cref="MachineBrigade.Sim.Content.VehicleDef.General"/>) and
    /// <see cref="MarkGeneral"/>; the speaking mark follows <see cref="DialogueDirector.IsSpeaking(string)"/> or the line's unit.</item>
    /// </list>
    /// </summary>
    public sealed partial class MatchRunner
    {
        private const float EventScanSeconds = 0.25f;

        private readonly HashSet<EntityId> _accordUnits = new();
        private readonly Dictionary<EntityId, string> _generalUnits = new();
        private readonly List<(Vehicle unit, string general)> _generalsOnField = new();
        private readonly List<EventArrow> _eventArrows = new();
        private readonly List<SideObjectiveInfo> _sideObjectives = new();
        private IEventHudSource _eventHudSource;
        private float _eventScanAt;

        /// <summary>
        /// The event system's adapter for the event markers (null: none; the notices' directions draw the arrows). The lead
        /// sets it at the merge with 23A.
        /// </summary>
        internal IEventHudSource EventHudSource
        {
            get => _eventHudSource;
            set
            {
                _eventHudSource = value;
                _eventScanAt = 0f;
            }
        }

        /// <summary>
        /// F.4: marks one of our units as the Meridian Accord's (view side: its health bar and sign, its minimap blip, and
        /// the player cannot select it); false takes the mark off. For reinforcements neither the allied-unit tag nor the
        /// adapter names.
        /// </summary>
        internal void MarkAccord(EntityId unit, bool accord = true)
        {
            if (accord) _accordUnits.Add(unit);
            else _accordUnits.Remove(unit);
            if (_views != null && _views.TryGet(unit, out var view)) view.AccordMarked = accord;
        }

        /// <summary>F.4: one of the Accord's units on our side (the allied AI's), not the player's own.</summary>
        internal bool IsAccord(Vehicle v) => v.Team == PlayerTeam && (v.Ally || AccordFlag(v));

        private bool AccordFlag(Vehicle v) => _accordUnits.Contains(v.Id) || (_eventHudSource?.Accord(v) ?? false);

        /// <summary>F.5: <paramref name="general"/> (a general's id: "varga", "kessler"...) is in this enemy unit; null takes it off.</summary>
        internal void MarkGeneral(EntityId unit, string general)
        {
            if (string.IsNullOrEmpty(general)) _generalUnits.Remove(unit);
            else _generalUnits[unit] = general;
            _eventScanAt = 0f;
        }

        private string GeneralOf(Vehicle v) =>
            _generalUnits.TryGetValue(v.Id, out var general) ? general : _eventHudSource?.General(v) ?? v.Def.General;

        /// <summary>After the views are drawn: who is who a few times a second, the generals' labels every frame.</summary>
        private void TickEventHud()
        {
            if (_menu || _hud == null || _views == null) return;
            if (Time.unscaledTime >= _eventScanAt)
            {
                _eventScanAt = Time.unscaledTime + EventScanSeconds;
                ScanEvents();
            }
            PlaceGeneralTags();
        }

        private void ScanEvents()
        {
            _generalsOnField.Clear();
            foreach (var v in _world.Vehicles)
            {
                if (!v.IsAlive) continue;
                if (v.Team == PlayerTeam)
                {
                    // F.4: the flag reaches views built since (a view is made on its unit's spawn and rebuilt when it changes form).
                    var accord = AccordFlag(v);
                    if (_views.TryGet(v.Id, out var view) && view.AccordMarked != accord) view.AccordMarked = accord;
                    continue;
                }
                if (_generalsOnField.Count >= GeneralTags.Max) continue;
                var general = GeneralOf(v);
                if (!string.IsNullOrEmpty(general)) _generalsOnField.Add((v, general));
            }
            // F.2: with the adapter, the arrows come from it with their full warning time, not from the notices.
            _hud.ArrowsFromNotices = _eventHudSource == null;
            if (_eventHudSource == null) return;
            // F.2: the arrows for as long as the warnings run (a second report of a direction keeps its arrow up).
            _eventArrows.Clear();
            _eventHudSource.Arrows(_eventArrows);
            foreach (var a in _eventArrows)
                if (a.SecondsLeft > 0f) _hud.Arrow(a.Direction, a.SecondsLeft, a.Enemy, a.At);
            ShowSideObjectives();
        }

        /// <summary>F.3: the side objective on the mission bar follows the event system's (one at a time, the first running).</summary>
        private void ShowSideObjectives()
        {
            _sideObjectives.Clear();
            _eventHudSource.SideObjectives(_sideObjectives);
            var shown = _hud.SideObjectiveId;
            if (shown != null)
            {
                foreach (var s in _sideObjectives)
                {
                    if (s.Id != shown) continue;
                    if (s.Outcome == SideObjectiveOutcome.Running) _hud.SideObjective(s.Id, s.Text, s.SecondsLeft, s.Count, s.Needed);
                    else _hud.SideObjectiveDone(s.Id, s.Outcome == SideObjectiveOutcome.Succeeded);
                    return;
                }
                // Gone without an outcome: the row goes quietly.
                _hud.SideObjectiveDone(shown, false, announce: false);
            }
            foreach (var s in _sideObjectives)
                if (s.Outcome == SideObjectiveOutcome.Running)
                {
                    _hud.SideObjective(s.Id, s.Text, s.SecondsLeft, s.Count, s.Needed);
                    return;
                }
        }

        private void PlaceGeneralTags()
        {
            var tags = _hud.GeneralTags;
            if (tags == null) return;
            tags.Begin(_hud.KeepOut);
            var camera = _camera.Camera;
            foreach (var (v, general) in _generalsOnField)
            {
                // Only what the player can see: a label never gives a hidden general away.
                if (!v.IsAlive || !v.IsVisibleTo(PlayerTeam) || !_views.TryGet(v.Id, out var view)) continue;
                if (!_hud.WorldToPanel(view.LabelPoint, camera, out var at)) continue;
                var speaking = _dialogue != null && (_dialogue.IsSpeaking(general) || _dialogue.IsSpeaking(v.Id));
                tags.Place(at, general, speaking, Time.unscaledTime);
            }
            tags.End();
        }
    }
}
