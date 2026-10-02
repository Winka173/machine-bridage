using System;
using System.Collections.Generic;
using System.Text;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 28, the player's side: the tactic it starts with (H.4, H.14), its AI at Normal skill (K.2), the per-squad
    /// tactics kept from earlier battles (H.10), the hint line's next hint (B.7), the towers' targeting modes picked on
    /// the Base screen (E.1) and Boss Hunt's free switch between bosses (H.6). Everything here runs on the battle's own
    /// clock inside <see cref="TickAi"/>, the same whether a hint is shown or not, so a checkpoint replay matches; the
    /// player's switches go through <see cref="ApplyInput"/> (live and in a replay alike).
    /// </summary>
    internal abstract partial class ModeSession
    {
        private readonly Dictionary<int, string> _squadPresets = new();
        private readonly HashSet<int> _squadsSeen = new();
        private readonly HashSet<int> _towersSet = new();
        private bool _squadSetup;
        private double _nextHintAt, _nextTowerAt;

        /// <summary>The hint line's newest hint (B.7), taken and cleared by the HUD.</summary>
        public AiHints.Hint? PendingHint { get; set; }

        /// <summary>H.6: tactic switches are free right now (Boss Hunt's rest between bosses).</summary>
        protected virtual bool FreeSwitchNow(SimWorld world) => false;

        /// <summary>
        /// Before the first step: the player's AI starts with the picked tactic (H.4; the last one for this mode, H.14),
        /// at Normal skill whatever the battle's difficulty (K.2), and the per-squad tactics once they are open (H.10).
        /// </summary>
        public void PreparePlayerAi(SimWorld world, GameModeKind kind, CommanderDef commander)
        {
            if (PlayerAi == null) return;
            PlayerAi.Tactic ??= TacticPick.For(world.Catalog, kind, commander);
            PlayerAi.Skill ??= AiSkill.For(AiDifficulty.Normal, world.Catalog.Ai);
            _squadPresets.Clear();
            if (!TacticPick.SquadTacticsOpen) return;
            for (var id = 0; id <= 16; id++)
                if (PlayerProfile.SquadTactic(id) is { } t && world.Catalog.AiData.HasTactic(t)) _squadPresets[id] = t;
        }

        /// <summary>The per-squad presets as one journal value ("1=blitz;3=hit_and_run").</summary>
        public string SquadPresetsText
        {
            get
            {
                var b = new StringBuilder();
                foreach (var kv in _squadPresets)
                {
                    if (b.Length > 0) b.Append(';');
                    b.Append(kv.Key).Append('=').Append(kv.Value);
                }
                return b.ToString();
            }
        }

        private void SetSquadPresets(string text)
        {
            _squadPresets.Clear();
            if (string.IsNullOrEmpty(text)) return;
            foreach (var part in text.Split(';'))
            {
                var eq = part.IndexOf('=');
                if (eq > 0 && int.TryParse(part.Substring(0, eq), out var id)) _squadPresets[id] = part.Substring(eq + 1);
            }
        }

        private void TickPlayerAi(SimWorld world)
        {
            if (PlayerAi?.Commander is not { } general) return;
            if (!_squadSetup)
            {
                _squadSetup = true;
                general.SquadTactics = TacticPick.SquadTacticsOpen;
            }
            general.FreeSwitch = FreeSwitchNow(world);
            if (general.SquadTactics && _squadPresets.Count > 0)
                foreach (var squad in general.Squads.Squads)
                    if (_squadsSeen.Add(squad.Id) && _squadPresets.TryGetValue(squad.Id, out var preset))
                        general.RequestSquadTactic(world, squad, preset);
            if (world.Time >= _nextHintAt)
            {
                _nextHintAt = world.Time + 1.0;
                if (PlayerAi.Hints.Next(world, PlayerTeam, general.Squads) is { } hint) PendingHint = hint;
            }
            if (world.Time >= _nextTowerAt)
            {
                _nextTowerAt = world.Time + 1.0;
                foreach (var tower in world.Bases.Towers(PlayerTeam))
                {
                    if (!_towersSet.Add(tower.Id.Value)) continue;
                    var saved = PlayerProfile.TowerModeFor(tower.Def.Id) ?? PlayerProfile.TowerModeFor(PlayerProfile.TowerCardOf(tower.Def.Id));
                    if (saved != null && Enum.TryParse<TowerMode>(saved, out var mode)) world.SetTowerMode(PlayerTeam, tower.Id, mode);
                }
            }
        }

        /// <summary>
        /// A prompt 28 switch of the player's, live or replayed: "tactic.start", "squad.presets", "tactic", "squad.tactic"
        /// ("squad=tactic", empty tactic: the side's), "tower.mode" ("entity=mode"). False for another input.
        /// </summary>
        public bool ApplyInput(SimWorld world, string input, string value)
        {
            var general = PlayerAi?.Commander;
            switch (input)
            {
                case "tactic.start":
                    if (PlayerAi != null) PlayerAi.Tactic = string.IsNullOrEmpty(value) ? null : value;
                    return true;
                case "squad.presets":
                    SetSquadPresets(value);
                    return true;
                case "tactic":
                    general?.RequestTactic(world, value);
                    return true;
                case "squad.tactic":
                {
                    var eq = value.IndexOf('=');
                    if (general != null && eq > 0 && int.TryParse(value.Substring(0, eq), out var id) && general.Squads.Find(id) is { } squad)
                    {
                        var t = value.Substring(eq + 1);
                        general.RequestSquadTactic(world, squad, string.IsNullOrEmpty(t) ? null : t);
                    }
                    return true;
                }
                case "tower.mode":
                {
                    var eq = value.IndexOf('=');
                    if (eq > 0 && int.TryParse(value.Substring(0, eq), out var id) && Enum.TryParse<TowerMode>(value.Substring(eq + 1), out var mode))
                    {
                        _towersSet.Add(id);
                        world.SetTowerMode(PlayerTeam, new MachineBrigade.Sim.Core.EntityId(id), mode);
                    }
                    return true;
                }
            }
            return false;
        }
    }
}
