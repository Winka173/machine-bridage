using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Mines on the field: ours always, the enemy's only once one of our vehicles is close
    /// enough to spot it (the simulation decides who sees what).
    /// </summary>
    internal sealed class MineViews
    {
        private readonly ModelLibrary _models;
        private readonly Transform _root;
        private readonly int _viewer;
        private readonly Dictionary<EntityId, GameObject> _views = new();
        private readonly HashSet<EntityId> _seen = new();
        private readonly List<EntityId> _gone = new();
        private readonly bool _hasModel;

        /// <param name="viewer">The team whose eyes we see through (-1 in the menu battle: every mine).</param>
        public MineViews(ModelLibrary models, Transform root, int viewer)
        {
            _models = models;
            _root = root;
            _viewer = viewer;
            _hasModel = models.Has("mine");
        }

        public void Update(SimWorld world)
        {
            if (!_hasModel) return;
            _seen.Clear();
            foreach (var mine in world.Mines)
            {
                if (!mine.IsAlive) continue;
                var visible = _viewer < 0 || mine.Team == _viewer || mine.IsVisibleTo(_viewer);
                if (!visible) continue;
                _seen.Add(mine.Id);
                if (_views.ContainsKey(mine.Id)) continue;
                var view = _models.Spawn("mine", mine.Team, _root, castShadows: false).Root;
                view.transform.SetPositionAndRotation(new Vector3(mine.Position.X, 0f, mine.Position.Y),
                    Quaternion.Euler(0f, mine.Id.Value * 71f, 0f));
                _views[mine.Id] = view;
            }
            _gone.Clear();
            foreach (var (id, view) in _views)
            {
                if (_seen.Contains(id)) continue;
                Object.Destroy(view);
                _gone.Add(id);
            }
            foreach (var id in _gone) _views.Remove(id);
        }
    }
}
