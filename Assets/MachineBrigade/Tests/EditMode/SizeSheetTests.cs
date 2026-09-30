using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 B1 (DECISIONS 25B): the balance sheet's model sizes hold in the game. A vehicle is measured as the game
    /// draws it: its model's own box through <see cref="VehicleView.DrawScaleOf(VehicleDef, float)"/>, so a model rebuilt
    /// at another size is held to the same order as the one it replaced.
    /// </summary>
    public class SizeSheetTests
    {
        private static readonly Dictionary<string, Vector3> Boxes = new();

        /// <summary>A model's box at scale 1 as Unity has it (x the span, y the height, z the length); zero without one.</summary>
        internal static Vector3 BoxOf(string model)
        {
            if (Boxes.TryGetValue(model, out var box)) return box;
            box = Vector3.zero;
            var prefab = Resources.Load<GameObject>("Models/" + model);
            if (prefab != null)
            {
                var go = Object.Instantiate(prefab);
                try
                {
                    box = VehicleView.Measure(go.transform, go.transform).size;
                }
                finally
                {
                    Object.DestroyImmediate(go);
                }
            }
            return Boxes[model] = box;
        }

        /// <summary>A vehicle's drawn length, width and height in metres, as VehicleView draws it.</summary>
        internal static Vector3 Drawn(VehicleDef def)
        {
            var box = BoxOf(def.Model);
            Assert.Greater(box.z, 0f, $"{def.Id}: its model '{def.Model}' is in Resources/Models");
            var k = VehicleView.DrawScaleOf(def, box.z);
            return new Vector3(box.z * k, box.x * k, box.y * k);
        }

        private static void Longer(string longer, string shorter, float by = 1f)
        {
            var catalog = GameContent.LoadCatalog();
            var a = Drawn(catalog.Vehicle(longer));
            var b = Drawn(catalog.Vehicle(shorter));
            Assert.Greater(a.x, b.x * by, $"{longer} ({a.x:0.00} m) is longer than {shorter} ({b.x:0.00} m){(by > 1f ? $" by {by - 1f:P0}" : "")}");
        }

        /// <summary>Clearly bigger: longer by <paramref name="by"/> and no narrower.</summary>
        private static void Bigger(string bigger, string smaller, float by)
        {
            Longer(bigger, smaller, by);
            var catalog = GameContent.LoadCatalog();
            var a = Drawn(catalog.Vehicle(bigger));
            var b = Drawn(catalog.Vehicle(smaller));
            Assert.GreaterOrEqual(a.y, b.y, $"{bigger} ({a.y:0.00} m wide) is no narrower than {smaller} ({b.y:0.00} m)");
        }

        [Test]
        public void TheMainBattleTankIsLongerThanTheIfv() => Longer("main_battle_tank", "ifv");

        [Test]
        public void TheSu27IsLongerThanTheSu25() => Longer("fighter_jet", "attack_jet", 1.2f);

        [Test]
        public void TheTwinBarrelTankIsClearlyBiggerThanTheMainBattleTank() => Bigger("twin_tank", "main_battle_tank", 1.1f);

        [Test]
        public void TheSuperTankIsClearlyBiggerThanTheHeavyTank() => Bigger("titan_tank", "heavy_tank", 1.1f);

        [Test]
        public void TheDroneMothershipAndTheAirborneGunshipShareOneFrameAtOneSize()
        {
            // The sheet: the swarm carrier and the AC-130 are one C-130 airframe, so one size (B2 built them on one frame).
            var catalog = GameContent.LoadCatalog();
            var carrier = catalog.Vehicle("swarm_carrier");
            var gunship = catalog.Vehicle("sky_gunship");
            Assert.AreEqual(carrier.FixedWing, gunship.FixedWing, "both fixed-wing");
            Assert.AreEqual(carrier.ModelLength, gunship.ModelLength, 0.01f, "the data gives them one length");
            Assert.AreEqual(carrier.ModelWidth, gunship.ModelWidth, 0.01f, "and one span");
            var a = Drawn(carrier);
            var b = Drawn(gunship);
            Assert.AreEqual(a.x, b.x, a.x * 0.02f, "one drawn length");
            Assert.AreEqual(a.y, b.y, a.y * 0.02f, "one drawn span: the same frame's shape");
            Assert.AreEqual(a.z, b.z, a.z * 0.05f, "one drawn height");
        }

        [Test]
        public void IcarusIsTheLargestThingInTheSky()
        {
            // The sheet: the orbital ship, the final boss, is the largest object in the sky (its length over every other
            // flyer's length and span, bosses and their variants included).
            var catalog = GameContent.LoadCatalog();
            var icarus = Drawn(catalog.Vehicle("silver_bug"));
            var failures = new List<string>();
            var flyers = 0;
            foreach (var v in catalog.Vehicles.Values.Where(v => v.Flying && v.Id != "silver_bug"))
            {
                if (BoxOf(v.Model).z <= 0f) continue;
                flyers++;
                var d = Drawn(v);
                if (Mathf.Max(d.x, d.y) >= icarus.x) failures.Add($"{v.Id}: {d.x:0.0} x {d.y:0.0} m");
            }
            Assert.Greater(flyers, 20, "every aircraft and flying boss is measured");
            Assert.IsEmpty(failures, $"Icarus is {icarus.x:0.0} m long; as big or bigger:\n" + string.Join("\n", failures));
        }

        [Test]
        public void EveryVehicleIsDrawnAtItsModelSizeWithItsHullInside()
        {
            // B1: the data holds the drawn box (modelSize); the hull (collision capsule, HullRadius = 0.46 x its width)
            // stays inside it, and no shorter than half of it (a long gun overhangs a hull, never more).
            var catalog = GameContent.LoadCatalog();
            var failures = new List<string>();
            var sized = 0;
            foreach (var v in catalog.Vehicles.Values.Where(v => v.ModelLength > 0f))
            {
                sized++;
                var d = Drawn(v);
                if (Mathf.Abs(d.x / v.ModelLength - 1f) > 0.01f) failures.Add($"{v.Id}: drawn {d.x:0.00} m long, its modelSize {v.ModelLength:0.00} m");
                if (v.Flying) continue; // an aircraft's hull is its hit radius
                if (v.Length > v.ModelLength * 1.02f || v.Width > v.ModelWidth * 1.02f)
                    failures.Add($"{v.Id}: its hull {v.Length:0.00} x {v.Width:0.00} m stands out of its box {v.ModelLength:0.00} x {v.ModelWidth:0.00} m");
                if (v.Length < v.ModelLength * 0.5f) failures.Add($"{v.Id}: its hull ({v.Length:0.00} m) is under half its length ({v.ModelLength:0.00} m)");
            }
            Assert.Greater(sized, 55, "every vehicle row of the sheet is sized");
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }
    }
}
