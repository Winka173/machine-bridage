using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Input;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 6, the UI, camera and audio half (DECISIONS 21E): the Gunship as a deck card flying the AC-130, a
    /// dropped field tower landing clear of what stands on its mark, the wheel's zoom step, a boss's shot giving the
    /// player's view back, the compact boss bar's call sign, and the weather under the music.
    /// </summary>
    public class PlayTest6UiTests
    {
        private static SimWorld Field(IEnumerable<PropPlacement> props = null) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(props ?? Enumerable.Empty<PropPlacement>()), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void TheGunshipIsADeckCardFlyingTheAc130()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.Contains("gunship_strike", MatchSettings.AllSupports, "a card in the deck and collection lists");
            Assert.IsTrue(catalog.TryGetSupport("gunship_strike", out var card));
            Assert.AreEqual(SupportKind.Escort, card.Kind);
            Assert.IsFalse(card.Consumable || card.EventOnly, "a deck card, not an item");
            Assert.Greater(card.CpCost, 0);
            Assert.AreEqual("sky_gunship", card.Units[0], "the AC-130");
            Assert.IsFalse(CardMerges.IsGone("gunship_strike"));
            Assert.IsTrue(Progression.IsPremium("gunship_strike"), "bought in the shop like the heavy bomber");
            Assert.AreEqual("sky_gunship", CardArt.EntryFor("gunship_strike")?.model, "its card shows the AC-130");
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = false;
                Assert.AreEqual("Gunship", Strings.Card("gunship_strike"));
                Assert.AreEqual("Gunship", Strings.Short("gunship_strike"));
                // One card only reads "Gunship": the heavy helicopter is the Heavy gunship now.
                var named = MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(id => Strings.Short(id) == "Gunship").ToList();
                CollectionAssert.AreEqual(new[] { "gunship_strike" }, named);
                Assert.AreNotEqual(Strings.Card("heavy_bomber"), Strings.Card("gunship_strike"));
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        [Test]
        public void TheGunshipCardCallsAnAc130ThatLeavesAfterItsTime()
        {
            var world = Field();
            var catalog = world.Catalog;
            catalog.TryGetSupport("gunship_strike", out var card);
            var economy = new TeamEconomy(0, 60f, income: 0f, bank: 60f, supports: new[] { "artillery_barrage", "gunship_strike" });
            world.EnableEconomy(economy);
            world.EnableEconomy(new TeamEconomy(1));
            var before = economy.Cp;
            Assert.IsTrue(world.Submit(Command.Strike(0, "gunship_strike", new Vector2(0f, 0f), default)).Accepted);
            Assert.AreEqual(before - card.CpCost, economy.Cp, 0.01f, "it costs its CP");
            Assert.IsFalse(world.Submit(Command.Strike(0, "gunship_strike", new Vector2(0f, 0f), default)).Accepted, "then waits its cooldown");
            Run(world, card.Delay + 1f);
            Assert.IsTrue(world.Vehicles.Any(v => v.IsAlive && v.Team == 0 && v.Def.Id == "sky_gunship"), "the AC-130 arrived");
            Run(world, card.Duration + 1f);
            Assert.IsFalse(world.Vehicles.Any(v => v.IsAlive && v.Team == 0 && v.Def.Id == "sky_gunship"), "and left after its time");
        }

        [Test]
        public void AFieldTowerLandsClearOfWhatStandsOnItsMark()
        {
            // A house, and a mark on the last open ground before its wall: the tower's centre fits there, its hull does not.
            var world = Field(new[] { new PropPlacement("house_small", new Vector2(20f, 0f), 0) });
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            var edge = 20f;
            while (!world.Grid.IsWalkable(new Vector2(edge, 0f))) edge -= 0.1f;
            var mark = new Vector2(edge - 0.2f, 0f);
            Assert.IsTrue(world.Submit(Command.Strike(0, "field_tower", mark)).Accepted);
            Run(world, 5f);
            var tower = world.Vehicles.FirstOrDefault(v => v.IsAlive && v.Team == 0 && v.Def.Id == "guard_tower");
            Assert.IsNotNull(tower, "a tower landed");
            Assert.LessOrEqual(tower.Position.X + tower.Def.HullBound, edge + world.Grid.CellSize, "its hull is out of the house");
            Assert.Less(Vector2.Distance(tower.Position, mark), 17f, "near the mark");

            // A tank parked on the mark: the tower comes down beside it, not on it.
            var parked = Field();
            parked.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            var tank = parked.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Assert.IsTrue(parked.Submit(Command.Strike(0, "field_tower", new Vector2(0f, 0f))).Accepted);
            Run(parked, 5f);
            var beside = parked.Vehicles.First(v => v.IsAlive && v.Def.Id == "guard_tower");
            Assert.GreaterOrEqual(Vector2.Distance(beside.Position, tank.Position), beside.Def.HullBound + tank.Def.HullBound, "not inside the tank");

            // On open ground it lands on the mark itself.
            var open = Field();
            open.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            Assert.IsTrue(open.Submit(Command.Strike(0, "field_tower", new Vector2(-20f, 10f))).Accepted);
            Run(open, 5f);
            var there = open.Vehicles.First(v => v.IsAlive && v.Def.Id == "guard_tower");
            Assert.Less(Vector2.Distance(there.Position, new Vector2(-20f, 10f)), 0.01f);
        }

        [Test]
        public void AWheelNotchZoomsOneStepWhateverScaleTheSystemReports()
        {
            Assert.AreEqual(TouchGestures.WheelStep, TouchGestures.WheelZoom(1f), 1e-4f, "one notch as the uniform setting reports it");
            Assert.AreEqual(TouchGestures.WheelStep, TouchGestures.WheelZoom(120f), 1e-4f, "one notch as Windows reports it");
            Assert.AreEqual(1f / TouchGestures.WheelStep, TouchGestures.WheelZoom(-1f), 1e-4f, "and back out");
            Assert.AreEqual(Mathf.Pow(TouchGestures.WheelStep, 3f), TouchGestures.WheelZoom(5000f), 1e-3f, "at most three steps a frame");
            Assert.Greater(TouchGestures.WheelZoom(0.3f), 1.03f, "a trackpad's small scroll still zooms");
        }

        [Test]
        public void ABossShotGivesThePlayersViewBack()
        {
            var go = new GameObject("Shot Camera");
            try
            {
                var camera = new RtsCamera(go.AddComponent<Camera>(), new UnityEngine.Vector2(-100f, -100f), new UnityEngine.Vector2(100f, 100f),
                    new Vector3(-20f, 0f, 10f), 24f);
                var focus = camera.Focus;
                camera.Hold();
                // The shot goes to the boss and closes in; a second shot on top keeps the first view.
                for (var i = 0; i < 60; i++) camera.Glide(new Vector3(40f, 0f, -30f), 14f, 0.05f, 2.5f);
                camera.Hold();
                Assert.Greater(Vector3.Distance(camera.Focus, focus), 20f);
                var frames = 0;
                while (!camera.ReturnHeld(1f / 60f) && frames < 200) frames++;
                Assert.Less(frames, 130, "back within about two seconds");
                Assert.Less(Vector3.Distance(camera.Focus, focus), 0.01f, "where the player had it");
                Assert.AreEqual(24f, camera.Zoom, 0.01f, "at their zoom");
                Assert.IsFalse(camera.Held);

                // The player moved the view during the shot: nothing is given back.
                camera.Hold();
                camera.Glide(new Vector3(30f, 0f, 30f), 20f, 1f, 2.5f);
                var moved = camera.Focus;
                camera.Release();
                Assert.IsTrue(camera.ReturnHeld(0.1f));
                Assert.AreEqual(moved, camera.Focus);
            }
            finally
            {
                Object.DestroyImmediate(go);
            }
        }

        [Test]
        public void TheCompactBossBarShowsTheCallSign()
        {
            Assert.AreEqual("Juggernaut", BossBar.CallSign("Juggernaut · Armoured Train"));
            Assert.AreEqual("Harpy", BossBar.CallSign("Harpy"));
            Assert.AreEqual("", BossBar.CallSign(""));
        }

        [Test]
        public void WeatherSitsUnderTheMusicAndAlertsDuckIt()
        {
            // The battle music plays at about 0.34 (its bus, the default music volume, the battle track's trim).
            foreach (WeatherKind kind in System.Enum.GetValues(typeof(WeatherKind)))
            {
                Assert.LessOrEqual(Weather.RainLevel(kind), 0.2f, kind + " rain");
                Assert.LessOrEqual(Weather.AirLevel(kind), 0.2f, kind + " wind");
                Assert.Less(Weather.RainLevel(kind) + Weather.AirLevel(kind), 0.34f, kind + " under the music");
            }
            Assert.LessOrEqual(AudioDirector.ThunderLevel, 0.6f);
            Assert.That(MusicDirector.AlertLevel, Is.InRange(0.4f, 0.8f), "an alert takes the music down, not out");
            Assert.That(MusicDirector.AlertSeconds, Is.InRange(1f, 4f), "for a moment");
        }
    }
}
