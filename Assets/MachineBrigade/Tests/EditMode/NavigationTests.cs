using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Tests
{
    public class NavigationTests
    {
        [Test]
        public void PathGoesAroundABlockerWithoutCrossingIt()
        {
            var grid = new NavGrid(60f, 2f);
            grid.AddBlocker(Vector2.Zero, 10f, 30f, 0f);
            var finder = new PathFinder(grid);
            var path = new List<Vector2>();

            Assert.IsTrue(finder.TryFindPath(new Vector2(-20f, 0f), new Vector2(20f, 0f), path));

            var previous = new Vector2(-20f, 0f);
            foreach (var point in path)
            {
                Assert.IsTrue(grid.LineOfSight(previous, point), $"segment {previous} -> {point} crosses the blocker");
                previous = point;
            }
            Assert.AreEqual(new Vector2(20f, 0f), path[path.Count - 1]);
        }

        [Test]
        public void GoalInsideABlockerResolvesToNearestWalkablePoint()
        {
            var grid = new NavGrid(60f, 2f);
            grid.AddBlocker(Vector2.Zero, 8f, 8f, 0f);
            var path = new List<Vector2>();

            Assert.IsTrue(new PathFinder(grid).TryFindPath(new Vector2(-20f, 0f), Vector2.Zero, path));
            Assert.IsTrue(grid.IsWalkable(path[path.Count - 1]));
        }

        [Test]
        public void OverlappingBlockersAreReferenceCounted()
        {
            var grid = new NavGrid(40f, 2f);
            grid.AddBlocker(Vector2.Zero, 6f, 6f, 0f);
            grid.AddBlocker(new Vector2(2f, 0f), 6f, 6f, 0f);

            grid.RemoveBlocker(Vector2.Zero, 6f, 6f, 0f);

            Assert.IsFalse(grid.IsWalkable(new Vector2(2f, 0f)), "the second blocker still covers this cell");
            Assert.IsTrue(grid.IsWalkable(new Vector2(-2.5f, 0f)));
        }

        [Test]
        public void DiagonalMovesDoNotCutCorners()
        {
            var grid = new NavGrid(20f, 2f);
            // Two blocked cells touching only at a corner.
            grid.AddBlocker(grid.CellCenter(4, 5), 2f, 2f, 0f);
            grid.AddBlocker(grid.CellCenter(5, 4), 2f, 2f, 0f);
            var path = new List<Vector2>();

            Assert.IsTrue(new PathFinder(grid).TryFindPath(grid.CellCenter(4, 4), grid.CellCenter(5, 5), path));
            Assert.Greater(path.Count, 1, "must detour instead of squeezing between the corners");
        }

        [Test]
        public void FormationGivesEveryUnitADistinctWalkableSlot()
        {
            var grid = new NavGrid(60f, 2f);
            var slots = Formation.Slots(Vector2.Zero, 8, 4f, grid);

            Assert.AreEqual(8, slots.Count);
            for (var i = 0; i < slots.Count; i++)
            for (var j = i + 1; j < slots.Count; j++)
                Assert.Greater(Vector2.Distance(slots[i], slots[j]), 3f);
        }
    }
}
