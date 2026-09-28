using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The enemy's elites in a battle (prompt 8 H.6): a radio line when the first elite of a wave
    /// turns up (the first of the battle, of a new numbered wave, or after a quiet spell with none),
    /// and the base cards of the elites destroyed, for the bounty and blueprints at the end.
    /// Kept apart from MatchRunner.cs so the two change independently.
    /// </summary>
    public sealed partial class MatchRunner
    {
        /// <summary>Seconds without a new elite after which the next one is the first of a new wave.</summary>
        private const float EliteRadioGap = 60f;

        private readonly List<string> _elitesSlain = new();
        private double _eliteRadioAt = -1.0;
        private int _eliteRadioWave = -1;

        private void EliteArrived(Vehicle vehicle)
        {
            if (_menu || vehicle.Team != EnemyTeam || !vehicle.Def.Elite || vehicle.Def.Boss) return;
            var now = _world.Time;
            var first = _eliteRadioAt < 0.0 || now - _eliteRadioAt > EliteRadioGap || _announcedWave != _eliteRadioWave;
            _eliteRadioAt = now;
            if (!first) return;
            _eliteRadioWave = _announcedWave;
            _hud.Toast(Strings.Format("radio.elite", Strings.Card(vehicle.Def.Id)), error: true, seconds: 4.5f);
        }
    }
}
