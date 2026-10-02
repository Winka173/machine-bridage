#nullable enable
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    internal sealed partial class CombatSystem
    {
        private float TowerWorth(Vehicle v, Vehicle other, WeaponDef weapon) => 1f;

        private float BossWorth(Vehicle v, Vehicle other, WeaponDef weapon) => 1f;
    }
}
