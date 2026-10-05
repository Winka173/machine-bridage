using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// MVA W1-B (spec parts W, X, BX; DECISIONS "Map/visual/audio W1-B (lane B)"): the runtime node contract. Stable
    /// semantic names resolve in a fixed order, legacy Blender suffixes keep their old order until a model is renamed, flare
    /// points never become weapon mounts, and every renamed model (Tools/assets/runtime_node_map.json) carries no runtime
    /// node with a Blender suffix. Written for the owner's test runs; not run by the lane (owner token rule).
    /// </summary>
    public class MvaW1bNodeContractTests
    {
        [Test]
        public void SemanticNamesParseAndLegacySuffixIsFlagged()
        {
            var tagged = RuntimeNodes.Parse("Muzzle_rocket_L");
            Assert.AreEqual(RuntimeNodes.Kind.Muzzle, tagged.Kind);
            Assert.AreEqual("rocket", tagged.Slot);
            CollectionAssert.AreEqual(new[] { "L" }, tagged.Tags);
            Assert.IsFalse(tagged.LegacySuffixed);
            Assert.IsTrue(RuntimeNodes.IsLegacySuffixed("Mount_gun.002"));
            Assert.IsFalse(RuntimeNodes.IsLegacySuffixed("Mount_gun_02"));
            Assert.AreEqual(RuntimeNodes.Kind.Part, RuntimeNodes.Parse("Part_engine_fore_L").Kind);
        }

        [Test]
        public void FlarePointsAndLowerCaseNamesAreNotRuntimeTags()
        {
            // AGENT_RULES: Mount_Flare_L / _R are flare points; the runtime must never read them as a weapon pivot.
            Assert.IsFalse(RuntimeNodes.Mount.IsMatch("Mount_Flare_L"));
            Assert.IsFalse(RuntimeNodes.Mount.IsMatch("Mount_Flare_R"));
            // Older lower-case names are their own slots or cosmetic, not side tags.
            Assert.AreEqual("door_l", RuntimeNodes.Parse("Muzzle_door_l").Slot);
            Assert.IsFalse(RuntimeNodes.Part.IsMatch("Part_aa_l"));
        }

        [Test]
        public void LegacyOrderIsTheOldOrdinalOrder()
        {
            var names = new List<string> { "Muzzle_mg.010", "Muzzle_mg.002", "Muzzle_mg", "Muzzle_mg.001" };
            var ordinal = names.OrderBy(n => n, System.StringComparer.Ordinal).ToList();
            names.Sort(RuntimeNodes.Compare);
            CollectionAssert.AreEqual(ordinal, names, "an old GLB resolves its k-th mount exactly as before");
        }

        [Test]
        public void SemanticOrderIsPlainThenTags()
        {
            var names = new List<string> { "Mount_mg_03", "Mount_mg_R", "Mount_mg", "Mount_mg_aft", "Mount_mg_02", "Mount_mg_L", "Mount_mg_fore" };
            names.Sort(RuntimeNodes.Compare);
            CollectionAssert.AreEqual(new[] { "Mount_mg", "Mount_mg_fore", "Mount_mg_aft", "Mount_mg_L", "Mount_mg_R", "Mount_mg_02", "Mount_mg_03" }, names);
        }

        [Test]
        public void FindPrefersThePlainNameAndTakesTaggedCopies()
        {
            var root = new GameObject("contract");
            try
            {
                var right = new GameObject("Part_wheel_R").transform;
                right.SetParent(root.transform);
                Assert.AreEqual(right, RuntimeNodes.Find(root.transform, "Part_wheel"), "a tagged copy stands for the plain name");
                var plain = new GameObject("Part_wheel").transform;
                plain.SetParent(root.transform);
                Assert.AreEqual(plain, RuntimeNodes.Find(root.transform, "Part_wheel"), "the plain name wins");
                Assert.IsNull(RuntimeNodes.Find(root.transform, "Part_wing"));
                Assert.IsFalse(RuntimeNodes.Matches("Part_wheelb", "Part_wheel"));
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void AttackJetResolvesStableMuzzlesInTheOldOrder()
        {
            foreach (var id in new[] { "attack_jet", "attack_jet_hd" })
            {
                var model = Resources.Load<GameObject>("Models/" + id);
                Assert.IsNotNull(model, id);
                var nodes = model.GetComponentsInChildren<Transform>(true);
                foreach (var slot in new[] { "rocket", "missile" })
                {
                    var list = nodes.Where(t => RuntimeNodes.Parse(t.name).Kind == RuntimeNodes.Kind.Muzzle && RuntimeNodes.Parse(t.name).Slot == slot).ToList();
                    RuntimeNodes.Sort(list);
                    CollectionAssert.AreEqual(new[] { "Muzzle_" + slot, "Muzzle_" + slot + "_L" }, list.Select(t => t.name).ToArray(), id + " " + slot);
                }
                Assert.IsFalse(nodes.Any(t => RuntimeNodes.IsLegacySuffixed(t.name)), id + ": no Blender suffix on a runtime node");
            }
        }

        [Test]
        public void RenamedModelsCarryNoSuffixedRuntimeNode()
        {
            var map = Path.Combine(Application.dataPath, "..", "Tools", "assets", "runtime_node_map.json");
            Assert.IsTrue(File.Exists(map), map);
            var ids = Regex.Matches(File.ReadAllText(map), "\"([a-z0-9_]+)\": \\{").Cast<Match>().Select(m => m.Groups[1].Value)
                .Where(id => id != "models").ToList();
            Assert.Greater(ids.Count, 0);
            foreach (var id in ids)
            {
                var model = Resources.Load<GameObject>("Models/" + id);
                Assert.IsNotNull(model, id);
                var suffixed = model.GetComponentsInChildren<Transform>(true).Where(t => RuntimeNodes.IsLegacySuffixed(t.name)).Select(t => t.name).ToList();
                Assert.IsEmpty(suffixed, id + ": " + string.Join(", ", suffixed));
                var ids2 = model.GetComponentsInChildren<Transform>(true).Where(t => RuntimeNodes.Parse(t.name).Valid).GroupBy(t => t.name).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
                Assert.IsEmpty(ids2, id + ": duplicate runtime ids");
            }
        }
    }
}
