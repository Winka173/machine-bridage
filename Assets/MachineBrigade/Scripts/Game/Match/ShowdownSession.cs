using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 32 L7 (DECISIONS "Prompt 32 L3 / L7 / L9"): Showdown (Đối công) in the menu. Both sides bring their full base
    /// (towers, walls, HQ type), their commander and their opening squad; the enemy's base never stands at a higher HQ level
    /// than the player's (its difficulty's level, capped there). Neutral sites of the mode's kinds (data) in the middle.
    /// Only on the battlefields the data lists (the 300 x 300 symmetric ones, <see cref="Eligible"/>).
    /// </summary>
    internal sealed class ShowdownSession : ModeSession
    {
        private ShowdownMode _mode;
        private bool _saidEscalation, _saidCutoff, _saidSudden;

        public override HudSpec Hud => new() { Mode = HudMode.Score, ScoreLabel = "stat.hq" };
        public override string Kicker => Strings.Get("mode.showdown.kicker");
        public override string Subtitle => Strings.Get("mode.showdown.sub");
        public override string StartToast => Strings.Get("mode.showdown.toast");

        /// <summary>The battlefields Showdown plays on (balance.json matchRules.modes.showdown.lists.maps).</summary>
        public static IReadOnlyList<string> Eligible(Catalog catalog) =>
            catalog.MatchRules.For("showdown")?.List("maps") ?? (IReadOnlyList<string>)Array.Empty<string>();

        /// <summary>The map Showdown plays: the chosen one when it is eligible, else the first eligible one.</summary>
        public static string MapOf(Catalog catalog, string mapId)
        {
            var maps = Eligible(catalog);
            foreach (var m in maps)
                if (m == mapId) return mapId;
            return maps.Count > 0 ? maps[0] : mapId;
        }

        protected override void Build(SimWorld world, int seed)
        {
            var rules = world.Catalog.Base;
            var player = PlayerProfile.BaseLoadoutOn(world.Map, PlayerTeam);
            // The AI's base at its difficulty's HQ level, never above the player's.
            var level = Math.Min(rules.AiLevel(Difficulty.ToString()), player.HqLevel);
            var enemy = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed, level: level, against: MatchSettings.DeckVehicles);
            _mode = new ShowdownMode(new ShowdownRules
            {
                Player = PlayerSide(18f, 1.35f), Enemy = EnemySide(18f, 1.35f, Difficulty, world.Catalog, seed),
                Bases = new BaseSetup().Set(PlayerTeam, player, BaseRole.Target).Set(EnemyTeam, enemy, BaseRole.Target),
            });
            Mode = _mode;
            _mode.Setup(world);
            world.Intel.Objectives = Objectives;
            AddEnemyCommander(_mode, seed);
            AddPlayerCommander(_mode, seed);
        }

        private static int Percent(float share) => (int)Math.Round(share * 100f);

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            hud.SetScore(Percent(_mode.HqShare(world, PlayerTeam)), Percent(_mode.HqShare(world, EnemyTeam)), 100, scratch);
            hud.SetTimer(_mode.SecondsLeft(world));
            Announce(hud, world);
        }

        /// <summary>
        /// Prompt 32 L7 (lead UI pass): one notice each at minute 6 (escalation), minute 10 (no more rebuilt towers) and when
        /// sudden death starts. Reads the Sim's clock and phase only; the times are the rules' (balance.json).
        /// </summary>
        private void Announce(BattleHud hud, SimWorld world)
        {
            if (_mode.Result != null) return;
            var rules = _mode.Rules;
            var now = world.Time;
            if (!_saidEscalation && now >= rules.EscalationAt)
            {
                _saidEscalation = true;
                hud.Toast(Strings.Format("mode.showdown.escalate", ("mult", rules.EscalationIncome.ToString("0.#", Strings.Culture))),
                    seconds: 4f, kind: NoticeKind.Reward);
            }
            if (!_saidCutoff && now >= rules.RebuildCutoff)
            {
                _saidCutoff = true;
                hud.Toast(Strings.Get("mode.showdown.cutoff"), seconds: 4f, kind: NoticeKind.Objective);
            }
            if (!_saidSudden && _mode.Phase == ShowdownPhase.SuddenDeath)
            {
                _saidSudden = true;
                hud.Toast(Strings.Format("mode.showdown.sudden", ("seconds", Math.Round(rules.SuddenDeath))), error: true, seconds: 5f,
                    kind: NoticeKind.Boss);
            }
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.showdown") };
            outcome.Rows.Add((Strings.Get("stat.hq"), Sides(Percent(_mode.HqShare(world, PlayerTeam)), Percent(_mode.HqShare(world, EnemyTeam)))));
            if (_mode.Phase == ShowdownPhase.Over && _mode.SuddenDeathDamage(PlayerTeam) + _mode.SuddenDeathDamage(EnemyTeam) > 0f)
                outcome.Rows.Add((Strings.Get("stat.suddenDeath"), Sides((int)_mode.SuddenDeathDamage(PlayerTeam), (int)_mode.SuddenDeathDamage(EnemyTeam))));
            AddRows(outcome, world, kills, losses);
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }
}
