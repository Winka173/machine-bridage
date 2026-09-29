using System.Collections.Generic;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 17 C: the shield carrier's and the shield generator's domes, drawn with prompt 11's shield (the
    /// hex dome of the fortress and the Shield Dome item): exactly the sim's radius, half as high, following a
    /// moving carrier; it rises when the dome is up, ripples where a hit lands on it (the sim's DomeHit), flickers
    /// more as it runs low, and shatters when it breaks (DomeChanged). View only.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private sealed class UnitDome
        {
            public ShieldVisual Shield;
            public float Radius;
            public bool Up;
        }

        private readonly Dictionary<EntityId, UnitDome> _unitDomes = new();
        private readonly List<EntityId> _goneDomes = new();

        private void DomeEvent(in SimEvent e, ViewRegistry views, float now)
        {
            if (!_unitDomes.TryGetValue(e.Entity, out var dome)) return;
            if (e.Kind == SimEventKind.DomeHit && dome.Up) dome.Shield.Hit(new Vector3(e.Position.X, 1f, e.Position.Y), now, default, Mathf.Clamp(e.Value / 250f, 0.5f, 1.6f));
            else if (e.Kind == SimEventKind.DomeChanged && e.Value < 0.5f && dome.Up)
            {
                dome.Up = false;
                dome.Shield.Collapse(now);
                Ring(dome.Shield.Transform.position, dome.Radius * 2f, Color.white);
            }
        }

        /// <summary>Every frame: a dome for every unit that has one, where it stands, up or down as the sim says.</summary>
        private void TickUnitDomes(ViewRegistry views, float now)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (view.Def.Dome is not { } def || view.IsWreck) continue;
                var id = view.Sim.Id;
                if (!_unitDomes.TryGetValue(id, out var dome))
                {
                    var shield = new ShieldVisual("Unit Dome " + view.Def.Id, _root, ShieldVisual.Shape.Dome, def.Radius);
                    shield.Transform.localScale = new Vector3(def.Radius, def.Radius * ItemDomeHeight, def.Radius);
                    shield.SetSide(view.Team == views.PlayerTeam);
                    dome = new UnitDome { Shield = shield, Radius = def.Radius };
                    _unitDomes[id] = dome;
                }
                dome.Shield.Transform.position = new Vector3(view.Position.x, 0.05f, view.Position.z);
                var up = view.Sim.IsAlive && view.Sim.DomeUp;
                if (up && !dome.Up)
                {
                    dome.Up = true;
                    dome.Shield.Raise(now);
                }
                else if (!up && dome.Up)
                {
                    dome.Up = false;
                    dome.Shield.Collapse(now);
                }
                if (dome.Up) dome.Shield.Flicker = Mathf.Clamp01((0.4f - view.Sim.DomeShare) * 1.8f);
                dome.Shield.Tick(now);
            }
            _goneDomes.Clear();
            foreach (var (id, dome) in _unitDomes)
                if (!views.TryGet(id, out var v) || v.IsWreck || !v.Sim.IsAlive)
                {
                    if (dome.Up)
                    {
                        dome.Up = false;
                        dome.Shield.Collapse(now);
                    }
                    if (!dome.Shield.Tick(now)) _goneDomes.Add(id);
                }
            foreach (var id in _goneDomes)
            {
                Object.Destroy(_unitDomes[id].Shield.Transform.gameObject);
                _unitDomes.Remove(id);
            }
        }
    }
}
