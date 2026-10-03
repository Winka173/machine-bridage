using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 22 E (DECISIONS 22E): the two new battlefields (every version, labelled hardpoints, names through NameText, a
    /// guide and a picture), Behemoth Mk.0 made from the Behemoth's data alone, Morrigan (a fast stealth fighter, its salvo
    /// at aircraft and anti-air with prompt 18's warning and interrupt, its duel mode, the duel's aircraft-only deck), Mara's
    /// Behemoth (a story unit, never a card), and both new mini bosses in the Boss Hunts. The stuck probe and the access
    /// check on the sim's grid are StuckTests and MapConnectivityTests (they cover every battlefield of the list).
    /// </summary>
    public class Prompt22ContentTests
    {
        private const float Step = 0.05f;
        private static readonly string[] NewMaps = { "foundry", "veyra_old_quarter" };

        private static Catalog C => Lab.Catalog;

        private static SimWorld Field(int seed = 3)
        {
            var world = Lab.Field(seed, 320f);
            world.BigAttackSettings = BigAttackSettings.For(C.BigAttackRules, "Normal");
            world.SetBoosts(0, _ => Lab.Harmless);
            return world;
        }

        private static List<SimEvent> Run(SimWorld world, float seconds, System.Func<bool> until = null)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
                if (until != null && until()) break;
            }
            return events;
        }

        private static Vehicle Tough(SimWorld world, string def, Vector2 at, int team = 0)
        {
            var v = world.SpawnVehicle(def, team, at, 0f);
            v.HpScale = 60f;
            v.Hp = v.MaxHp;
            v.Scripted = true;
            return v;
        }

        // ------------------------------------------------------------------ E.1-2: the battlefields

        [Test]
        public void TheNewBattlefieldsHaveEveryVersionANameAGuideAndAPicture()
        {
            var was = Strings.Vietnamese;
            try
            {
                foreach (var id in NewMaps)
                {
                    var conquest = GameContent.LoadMap(id + "_conquest");
                    Assert.AreEqual(2, conquest.Bases.Count, id + ": both camps");
                    Assert.AreEqual(3, conquest.Points.Count, id + ": three objectives");
                    foreach (var camp in conquest.Bases)
                    {
                        var places = SlotPlaces.Keys(camp).Select(k => k.Place).ToList();
                        Assert.AreEqual(camp.Slots.Count, places.Count, id + ": a label for every hardpoint");
                        Assert.IsTrue(places.Contains(SlotPlace.Gate) && places.Contains(SlotPlace.Utility), $"{id} team {camp.Team}: gate and utility hardpoints");
                    }
                    Assert.IsNotNull(GameContent.LoadMap(id + "_sandbox"), id + ": Survival");
                    Assert.IsNotNull(GameContent.LoadMap(id + "_siege").Fortress, id + ": Siege");
                    Assert.IsTrue(GameContent.LoadMap(id + "_long").IsLong, id + ": the long battlefield");
                    Assert.IsTrue(MatchSettings.AllMaps.Any(m => m.Id == id), id + ": in the skirmish list (Survival, Boss Hunt, the weekly draw)");
                    Assert.IsNotNull(Resources.Load<Texture2D>("UI/Maps/" + id), id + ": its picture");
                    foreach (var key in new[] { "map." + id, "map." + id + ".sub", "guide.map." + id })
                        Assert.IsTrue(Strings.Has(key), key);
                }
                // Their names come from NameText, the same in both languages.
                foreach (var vi in new[] { false, true })
                {
                    Strings.Vietnamese = vi;
                    Assert.AreEqual("Foundry", Strings.Get("map.foundry"));
                    Assert.AreEqual("Veyra Old Quarter", Strings.Get("map.veyra_old_quarter"));
                    StringAssert.StartsWith("[[Foundry]]", Strings.Get("guide.map.foundry"));
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        // ------------------------------------------------------------------ E.3: Behemoth Mk.0

        [Test]
        public void BehemothMk0IsMadeFromTheBehemothsDataAlone()
        {
            var mk0 = C.Vehicle("behemoth_mk0");
            var main = C.Vehicle("behemoth");
            Assert.AreEqual("behemoth", mk0.VariantOf);
            Assert.AreEqual("behemoth", mk0.Model, "the Behemoth's model, no model of its own");
            Assert.IsNull(Resources.Load<GameObject>("Models/behemoth_mk0"), "no new model");
            Assert.AreEqual(BossRank.Mini, mk0.Rank);
            Assert.AreEqual("varga", mk0.General);
            Assert.AreEqual("mk0", mk0.VariantName, "the prototype's naming rule");
            Assert.IsNotNull(mk0.Tint);
            CollectionAssert.AreEquivalent(new[] { "main_gun", "side_gun_l", "side_gun_r", "rocket_pod" }, mk0.Parts.Select(p => p.Id));
            Assert.IsNull(mk0.Aps, "no protection system");
            Assert.IsFalse(mk0.Mounts.Any(m => m.Weapon.Id == "boss_flak"), "no flak");
            Assert.Greater(mk0.HiddenNodes.Count, 0, "the dropped weapons are hidden on the model");
            Assert.Less(mk0.Scale, main.Scale, "smaller than the Behemoth");
            Assert.IsNull(mk0.BigAttack, "prompt 25 C1: a mini boss has no super weapon (its barrage is gone)");
            Assert.AreEqual("behemoth_mk2", main.MiniVariant, "the Behemoth's mini version stays Mk.II");
            var world = Field();
            var boss = world.SpawnVehicle("behemoth_mk0", 1, new Vector2(0f, 40f), 0f);
            Assert.AreEqual(4, boss.PartCount);
            Assert.IsNull(boss.BigAttack);
        }

        // ------------------------------------------------------------------ E.3: the duel (Raven's Harpy since play-test 14)

        /// <summary>Play-test 14: Raven fights the Skyhold duel in the Harpy (Morrigan was deleted): alone, and it never goes dark.</summary>
        [Test]
        public void TheHarpysDuelModeFliesAlone()
        {
            var world = Field();
            var boss = world.SpawnVehicle("mega_gunship", 1, new Vector2(0f, 60f), 0f);
            Assert.IsNotNull(boss.Def.Duel, "a duel mode");
            Run(world, 1f);
            Assert.IsTrue(world.Bosses.Duel(boss), "into its duel mode");
            Assert.IsFalse(world.Bosses.Duel(boss), "once");
            Run(world, 2f);
            Assert.AreEqual(0, world.EscortsAlive(boss.Id), "no escorts in the duel");
            boss.Hp = boss.MaxHp * 0.35f;
            Run(world, 0.5f);
            Assert.IsFalse(boss.DuelDark, "a gunship never goes dark");
            // A plain boss has no duel mode.
            Assert.IsFalse(world.Bosses.Duel(world.SpawnVehicle("behemoth_mk0", 1, new Vector2(60f, 60f), 0f)));
        }

        [Test]
        public void ADuelMissionFliesTheDecksAircraftOnly()
        {
            const string json = "{\"missions\": [{\"id\": \"duel_test\", \"chapter\": 10, \"map\": \"skyhold\", \"goal\": \"Boss\", \"duel\": true, " +
                                "\"boss\": {\"def\": \"mega_gunship\", \"x\": 80, \"z\": 80}}]}";
            var mission = MissionDef.ListFromJson(json)[0];
            Assert.IsTrue(mission.Duel);
            Assert.AreEqual("air", mission.PlayerDeck);
            var deck = new[] { "main_battle_tank", "fighter_jet", "aa_vehicle", "attack_helicopter", "mara_behemoth" };
            var cut = MissionDecks.Vehicles(C, mission, deck, _ => false);
            Assert.IsTrue(cut.All(id => C.Vehicle(id).Flying), "aircraft only: " + string.Join(", ", cut));
            Assert.GreaterOrEqual(cut.Count, MissionDecks.AirMinimum - 1, "topped up from the fighters");
            Assert.Contains("fighter_jet", cut);
            Assert.IsEmpty(MissionDecks.Supports(mission, new[] { "artillery_barrage", "airstrike" }), "no support cards in a duel");
            var plain = MissionDef.ListFromJson(json.Replace("\"duel\": true, ", ""))[0];
            CollectionAssert.AreEqual(deck, MissionDecks.Vehicles(C, plain, deck), "any other mission keeps the deck");
            // The mission puts its boss into the duel mode.
            var world = new SimWorld(C, GameContent.LoadMap("skyhold_conquest"), 7);
            var mode = new MissionMode(mission, new SideSetup(), null);
            mode.Setup(world);
            var boss = world.VehicleList.First(v => v.Def.Id == "mega_gunship");
            Assert.IsTrue(boss.InDuel, "the duel's boss flies its duel mode");
        }

        // ------------------------------------------------------------------ E.4: Mara's Behemoth

        [Test]
        public void MarasBehemothIsAStoryAllyNeverInTheDeck()
        {
            var def = C.Vehicle("mara_behemoth");
            Assert.IsTrue(def.StoryOnly);
            Assert.IsFalse(def.Card, "never a card");
            Assert.IsFalse(def.Boss, "an ally, not a boss");
            Assert.AreEqual(0, def.CpCost);
            Assert.AreEqual("behemoth", def.Model, "the Behemoth's model");
            Assert.AreEqual("accord", def.Mark, "with the Accord's mark");
            Assert.IsNotNull(def.Tint);
            Assert.IsFalse(MatchSettings.AllVehicles.Contains("mara_behemoth"), "not in the card list (decks, shop, Guide)");
            Assert.IsNull(Progression.UnlockMission("mara_behemoth"), "no unlock route");
            Assert.IsFalse(PlayerProfile.Unlock("mara_behemoth"), "never unlocked");
            var access = new SandboxAccess(false, _ => true, _ => true, _ => true);
            Assert.IsFalse(access.Allowed(C, def), "not in the Sandbox's palette");
            Assert.IsFalse(ConquestAi.PickDeck(C, C.Vehicles.Keys.ToList(), AiDifficulty.Hard, 3).Contains("mara_behemoth"), "never an AI's card");
            var decks = MatchSettings.DeckVehicles;
            Assert.IsFalse(decks.Contains("mara_behemoth"));
            // Only chapter 12's missions may place it (the story pass places it in the final battle).
            foreach (var m in Campaign.All)
                foreach (var stage in new[] { m }.Concat(m.Stages.Select(s => s.Mission)))
                {
                    var names = stage.Units.Select(u => u.DefId).Concat(stage.Ally?.Units.Select(u => u.DefId) ?? Enumerable.Empty<string>());
                    if (names.Contains("mara_behemoth")) Assert.AreEqual(12, m.Chapter, m.Id + ": Mara's Behemoth only in chapter 12");
                }
            // A mission's ally places it on the player's side, as the allied AI's.
            var json = "{\"missions\": [{\"id\": \"ally_test\", \"chapter\": 12, \"map\": \"launchsite\", \"goal\": \"Capture\", \"points\": [\"town\"], " +
                       "\"ally\": {\"x\": -60, \"z\": -60, \"units\": [{\"def\": \"mara_behemoth\", \"x\": -70, \"z\": -60}]}}]}";
            var ally = MissionDef.ListFromJson(json)[0].Ally;
            Assert.AreEqual("mara_behemoth", ally.Units.Single().DefId);
        }

        // ------------------------------------------------------------------ E.5: the Boss Hunts

        /// <summary>Prompt 22 E's new mini boss in the hunts (play-test 14 deleted the other, Morrigan).</summary>
        [Test]
        public void TheNewMiniBossIsInTheBossHunts()
        {
            var story = BossHunts.Story;
            Assert.IsTrue(BossHunts.Full.Contains("behemoth_mk0"), "in the full Boss Hunt");
            Assert.IsFalse(story.First(b => b.Id == "behemoth_mk0").Main, "a mini boss");
            // In story order: Mk.0 after chapter 3's bosses (interlude I).
            var list = story.ToList();
            Assert.Less(list.FindIndex(b => b.Id == "behemoth_mk0"), list.FindIndex(b => b.Chapter == 4));
            // The week's hunt draws it too (minis drawn from the story's): within a year of weeks it comes up.
            var drawn = new HashSet<string>();
            for (var week = 202601; week <= 202652; week++)
                foreach (var id in BossHunts.Weekly(week))
                    drawn.Add(id);
            Assert.IsTrue(drawn.Contains("behemoth_mk0"), "drawn in the week's hunt");
            Assert.IsTrue(BossRushRules.Kinds.Any(k => k.Contains("behemoth_mk0")));
        }
    }
}
