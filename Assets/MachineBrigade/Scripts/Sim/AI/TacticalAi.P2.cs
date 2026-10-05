#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>AI MASTER P2 Part J: the tactical AI's fire support stands on its doctrine's anchors.</summary>
    public sealed partial class TacticalAi
    {
        private FireSupportDirector? _fireSupport;

        /// <summary>This side's fire-support anchors (Part J).</summary>
        public FireSupportDirector FireSupport => _fireSupport ??= new FireSupportDirector(_team);

        /// <summary>The anchor slot of artillery piece <paramref name="a"/>; null when no valid spot exists (the old standoff then).</summary>
        private Vector2? AnchorStand(SimWorld world, Vehicle a, Vector2 front, Vector2 objective, Vector2 forward, bool contact)
        {
            Vector2? enemy = null;
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var e in _enemies)
                if (!e.Flying && !e.Def.Static)
                {
                    sum += e.Position;
                    n++;
                }
            if (n > 0) enemy = sum / n;
            var ctx = new FireSupportContext(front, objective, forward, contact, enemy, p => Exposed(p, StandoffMargin));
            return FireSupport.Stand(world, a, _artillery, ctx);
        }
    }
}
