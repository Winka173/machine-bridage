using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Modes;
using UnityEngine.UIElements;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 28 in battle: the tactic switch (H.6, its cooldown and transition; Boss Hunt's free switch between bosses),
    /// the per-squad tactics after chapter 6 (H.10), the enemy's tactic once a scout has seen its army (H.8), the AI
    /// hint line (B.7, Settings can turn it off) and a tower's targeting mode on a tap (E.1). Every accepted switch is
    /// written to the journal, so a checkpoint replays it (<see cref="ModeSession.ApplyInput"/>).
    /// </summary>
    public sealed partial class MatchRunner
    {
        private string _enemyTacticSeen;
        private int _pressureShown;
        private bool _finalShown;

        private void WireTactics()
        {
            _hud.TacticPressed += OpenTacticPicker;
            _selection.OwnTowerTapped += OpenTowerModes;
        }

        /// <summary>Every frame: the switch's state, the newest hint, a line when a scouted enemy changes its tactic.</summary>
        private void UpdateTactics()
        {
            // I.6, I.7: a line when the battle's pressure rises a tier, and when Conquest's final phase starts.
            if (_world.PressureTier > _pressureShown && _world.PressureTier <= 4)
            {
                _pressureShown = _world.PressureTier;
                _hud.Toast(Strings.Get("pressure.tier" + _pressureShown), seconds: 4f);
            }
            if (!_finalShown && _session.Mode is ConquestMode { InFinalPhase: true })
            {
                _finalShown = true;
                _hud.Toast(Strings.Get("pressure.final"), seconds: 4f);
            }
            var general = _session.PlayerAi?.Commander;
            if (general == null)
            {
                _hud.SetTactic(null, 0f, false, false);
                return;
            }
            var t = general.CurrentTactic;
            _hud.SetTactic(TacticText.Name(t), (float)(general.TacticReadyAt - _world.Time), general.InTransition, general.FreeSwitch);
            if (_session.PendingHint is { } hint)
            {
                _session.PendingHint = null;
                if (MatchSettings.AiHints && Strings.Has(hint.Key)) _hud.ShowAiHint(Strings.Get(hint.Key));
            }
            // H.8: the enemy's switch is news only while our scouts see its army.
            if (_world.AiCommanders.TryGetValue(EnemyTeam, out var enemy))
            {
                var now = enemy.CurrentTactic.Id;
                if (_enemyTacticSeen != null && now != _enemyTacticSeen && enemy.TacticSeenBy(_world, PlayerTeam))
                {
                    _hud.Toast(Strings.Format("tactic.line.enemySwitched", ("tactic", TacticText.Name(enemy.CurrentTactic))), seconds: 4f);
                    _enemyTacticSeen = now;
                }
                else if (_enemyTacticSeen == null) _enemyTacticSeen = now;
            }
        }

        private void OpenTacticPicker()
        {
            var general = _session.PlayerAi?.Commander;
            if (general == null) return;
            var catalog = _world.Catalog;
            var current = general.CurrentTactic;
            var status = new List<string>
            {
                Strings.Format("cmdr.line", ("label", Strings.Get("tactic.title")), ("text", TacticText.Name(current))),
            };
            var wait = (float)(general.TacticReadyAt - _world.Time);
            if (general.InTransition) status.Add(Strings.Get("tactic.transition"));
            else if (!general.FreeSwitch && wait > 0f) status.Add(Strings.Format("tactic.cooldown", ("seconds", UnityEngine.Mathf.CeilToInt(wait))));
            // H.8: the enemy's tactic only once scouted.
            if (_world.AiCommanders.TryGetValue(EnemyTeam, out var enemy))
                status.Add(enemy.TacticSeenBy(_world, PlayerTeam)
                    ? Strings.Format("tactic.enemyNow", ("tactic", TacticText.Name(enemy.CurrentTactic)))
                    : Strings.Get("tactic.enemyUnknown"));
            var tactics = new List<MachineBrigade.Sim.Content.TacticDef>();
            foreach (var t in TacticPick.Choices(catalog))
                if (TacticPick.Unlocked(t)) tactics.Add(t);
            var options = new List<(string, string, bool)>();
            foreach (var t in tactics) options.Add((TacticText.Name(t), TacticText.Core(t), t.Id == current.Id));
            _hud.ShowPicker(Strings.Get("tactic.switch"), status, options, i =>
            {
                var id = tactics[i].Id;
                var result = general.RequestTactic(_world, id);
                if (result == TacticSwitchResult.Done)
                {
                    MatchJournal.Record(_world, "tactic", id);
                    _hud.Toast(Strings.Format("tactic.line.switched", ("tactic", TacticText.Name(tactics[i]))), kind: NoticeKind.Order);
                }
                else if (result == TacticSwitchResult.Cooldown) _hud.Toast(Strings.Get("tactic.line.cooldown"), error: true);
            }, general.SquadTactics ? SquadTactics(general, tactics) : null);
        }

        /// <summary>H.10: each squad's own tactic (or the side's), each with its own cooldown; kept in the profile by squad number.</summary>
        private VisualElement SquadTactics(AiCommander general, List<MachineBrigade.Sim.Content.TacticDef> tactics)
        {
            var squads = general.Squads.Squads;
            if (squads.Count == 0) return null;
            var box = Kit.Box("");
            box.Add(Kit.Caption(Strings.Get("tactic.squad")));
            var names = new List<KitOption> { new(Strings.Get("tactic.squadShared")) };
            foreach (var t in tactics) names.Add(new KitOption(TacticText.Name(t)));
            foreach (var squad in squads)
            {
                var s = squad;
                var selected = s.TacticOverride == null ? 0 : 1 + tactics.FindIndex(t => t.Id == s.TacticOverride);
                var label = Strings.Get("tactic.squad") + " " + s.Id + " · " + s.Members.Count;
                box.Add(new KitDropdown(label, names, UnityEngine.Mathf.Max(0, selected), i =>
                {
                    var tactic = i == 0 ? null : tactics[i - 1].Id;
                    var result = general.RequestSquadTactic(_world, s, tactic);
                    if (result == TacticSwitchResult.Done)
                    {
                        MatchJournal.Record(_world, "squad.tactic", s.Id + "=" + (tactic ?? ""));
                        PlayerProfile.SetSquadTactic(s.Id, tactic);
                    }
                    else if (result == TacticSwitchResult.Cooldown) _hud.Toast(Strings.Get("tactic.line.cooldown"), error: true);
                }, thumbnail: false));
            }
            return box;
        }

        /// <summary>E.1: a tap on one of our towers that has targeting modes opens them (Default: the data's own).</summary>
        private void OpenTowerModes(EntityId id)
        {
            if (!_world.TryGetVehicle(id, out var tower) || !tower.IsAlive || tower.Team != PlayerTeam) return;
            if (!_world.Catalog.AiData.Towers.TryGetValue(tower.Def.Id, out var def) || def.Modes.Count == 0) return;
            var modes = new List<TowerMode> { TowerMode.Default };
            foreach (var m in def.Modes)
                if (m != TowerMode.Default && !modes.Contains(m)) modes.Add(m);
            var options = new List<(string, string, bool)>();
            foreach (var m in modes)
                options.Add((Strings.Get("tower.mode." + m), m == TowerMode.Default ? Strings.Get("tower.mode." + def.Mode) : null, tower.TowerMode == m));
            _hud.ShowPicker(Strings.Get("tower.mode.title"), new[] { Strings.Unit(tower.Def.Id) }, options, i =>
            {
                if (!_world.SetTowerMode(PlayerTeam, id, modes[i])) return;
                MatchJournal.Record(_world, "tower.mode", id.Value + "=" + modes[i]);
                _hud.Toast(Strings.Format("cmdr.line", ("label", Strings.Get("tower.mode.title")), ("text", Strings.Get("tower.mode." + modes[i]))));
            });
        }
    }
}
