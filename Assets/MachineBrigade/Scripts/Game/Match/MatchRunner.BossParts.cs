using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Boss parts in a battle (prompt 9): the part order from a tap on a part (on the boss, or its icon
    /// under the boss bar; the same part again cancels it), the outline on the ordered part, and the
    /// radio line when an important part breaks. Kept apart from MatchRunner.cs so the two change
    /// independently.
    /// </summary>
    public sealed partial class MatchRunner
    {
        private EntityId _outlinedBoss = EntityId.None;

        private void WireBossParts()
        {
            _hud.BossPartTapped += OrderAtPart;
            _selection.PartTapped += OrderAtPart;
        }

        /// <summary>Every unit in reach at this part of the boss; the part already ordered: the order is cancelled.</summary>
        private void OrderAtPart(EntityId boss, int part)
        {
            if (_menu || !_world.TryGetVehicle(boss, out var b) || !b.IsAlive || part < 0 || part >= b.PartCount || b.IsPartBroken(part)) return;
            var cancel = _world.TryGetPartFocus(PlayerTeam, out var focused, out var at) && focused == boss && at == part;
            var result = _world.SubmitPlayer(Command.FocusPart(PlayerTeam, boss, cancel ? null : b.Def.Parts[part].Id));
            if (!result.Accepted) return;
            _hud.Toast(cancel ? Strings.Get("toast.partFocusOff") : Strings.Format("toast.partFocus", Strings.Get("part." + b.Def.Parts[part].Kind)),
                seconds: 2.5f);
            Haptics.Pulse(40, 160);
        }

        /// <summary>Per frame: the ordered part outlined on its boss (and the outline off when the order ends).</summary>
        private void UpdateBossPartOutline()
        {
            var has = _world.TryGetPartFocus(PlayerTeam, out var boss, out var part);
            if (_outlinedBoss.IsValid && (!has || boss != _outlinedBoss) && _views.TryGet(_outlinedBoss, out var old)) old.SetOutlinedPart(-1);
            _outlinedBoss = has ? boss : EntityId.None;
            if (has && _views.TryGet(boss, out var view)) view.SetOutlinedPart(part);
        }

        /// <summary>A part broke: a radio line if it was an important one (a main gun, a shield generator, a drone bay, a locomotive), else a toast.</summary>
        private void PartBrokenToast(in SimEvent e)
        {
            if (!_world.TryGetVehicle(e.Entity, out var broken) || e.Mount < 0 || e.Mount >= broken.Def.Parts.Count) return;
            var part = broken.Def.Parts[e.Mount];
            var name = Strings.Card(broken.Def.Id);
            if (part.Radio != null && Strings.Has(part.Radio)) _hud.Toast(Strings.Format(part.Radio, name), seconds: 4.5f);
            else _hud.Toast(Strings.Format("toast.partBroken", Strings.Get("part." + part.Kind), name), seconds: 3f);
            Haptics.Pulse(90, 220);
        }

        private void PartRepairedToast(in SimEvent e)
        {
            if (!_world.TryGetVehicle(e.Entity, out var mended) || e.Mount < 0 || e.Mount >= mended.Def.Parts.Count) return;
            _hud.Toast(Strings.Format("toast.partRepaired", Strings.Get("part." + mended.Def.Parts[e.Mount].Kind), Strings.Card(mended.Def.Id)),
                error: true, seconds: 3f);
        }
    }
}
