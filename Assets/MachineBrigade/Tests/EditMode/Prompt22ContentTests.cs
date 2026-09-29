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
            Assert.AreEqual("behemoth_mk0_barrage", mk0.BigAttack.Id);
            Assert.AreEqual(4, mk0.BigAttack.Strikes[0].FullCount, "two pairs of the Behemoth's six rounds");
            Assert.AreEqual("behemoth_mk2", main.MiniVariant, "the Behemoth's mini version stays Mk.II");
            var world = Field();
            var boss = world.SpawnVehicle("behemoth_mk0", 1, new Vector2(0f, 40f), 0f);
            Assert.AreEqual(4, boss.PartCount);
            Assert.IsNotNull(boss.BigAttack);
        }

        // ------------------------------------------------------------------ E.3: Morrigan

        [Test]
        public void MorriganIsAFastStealthFighterWithMissilesAndGuidedBombs()
        {
            var m = C.Vehicle("morrigan");
            Assert.AreEqual(BossRank.Mini, m.Rank);
            Assert.AreEqual("quaden", m.General, "Wolff's");
            Assert.AreEqual("morrigan", m.Model);
            Assert.IsNotNull(Resources.Load<GameObject>("Models/morrigan"), "its own model");
            Assert.IsTrue(m.Flying && m.FixedWing && m.Stealth, "a stealth fighter under the aircraft rules");
            Assert.Greater(m.Speed, C.Vehicle("fighter_jet").Speed, "faster than our fighters");
            Assert.Greater(m.Speed, C.Vehicle("stealth_fighter").Speed);
            var weapons = m.Mounts.Select(x => x.Weapon.Id).ToList();
            Assert.Contains("air_to_air", weapons);
            Assert.Contains("guided_bomb", weapons);
            Assert.IsNotNull(m.Duel?.BigAttack, "a duel mode");
            // Stealth: seen only close up by a spotter on the ground.
            var world = new SimWorld(C, new MapDefinition("lab", 320f,
                new[] { new TeamStart(0, new Vector2(-120f, -120f)), new TeamStart(1, new Vector2(120f, 120f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), 5);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            tank.HoldFire = true;
            var d = tank.Def.VisionRange * 0.75f;
            var boss = world.SpawnVehicle("morrigan", 1, new Vector2(0f, d), 0f);
            boss.HoldFire = true;
            var seenFar = 0;
            var checkedFar = 0;
            for (var i = 0; i < 40; i++)
            {
                world.Step(Step);
                world.ClearEvents();
                var gap = Vector2.Distance(boss.Position, tank.Position);
                if (gap < tank.Def.VisionRange * VehicleDef.StealthSight + boss.Radius + 3f || gap > tank.Def.VisionRange - 2f) continue;
                checkedFar++;
                if (boss.IsVisibleTo(0)) seenFar++;
            }
            Assert.Greater(checkedFar, 0, "it flew inside the tank's sight but beyond its stealth range");
            Assert.AreEqual(0, seenFar, "a plain aircraft would be seen there; the stealth fighter is not");
        }

        [Test]
        public void MorrigansSalvoHuntsAircraftAndAntiAirAndCanBeInterrupted()
        {
            var world = Field();
            var boss = world.SpawnVehicle("morrigan", 1, new Vector2(0f, 60f), 0f);
            var jets = new[] { Tough(world, "fighter_jet", new Vector2(-20f, 0f)), Tough(world, "attack_helicopter", new Vector2(20f, 0f)) };
            var aa = Tough(world, "aa_vehicle", new Vector2(0f, -20f));
            var tank = Tough(world, "main_battle_tank", new Vector2(30f, -30f));
            var air = boss.Def.BigAttack.Strikes.First(s => s.Prey == BigPrey.Air);
            var ground = boss.Def.BigAttack.Strikes.First(s => s.Prey == BigPrey.AntiAir);
            Run(world, 0.2f);   // (prey must be seen: the sight is worked out as the world steps)
            var prey = world.Bosses.Prey(boss, air, 0f, 6);
            CollectionAssert.AreEquivalent(jets, prey, "its missiles hunt the aircraft");
            Assert.AreEqual(aa, world.Bosses.Prey(boss, ground, 0f, 2).Single(), "its bombs the anti-air, not the tank");
            Assert.IsFalse(world.Bosses.Prey(boss, ground, 0f, 2).Contains(tank));

            // Prompt 18's rules: a warning first, then the salvo; every round a homing flyer.
            world.Bosses.TriggerBig(boss);
            Run(world, 5f, () => boss.BigAttack.Stage == BigStage.Charging);
            Assert.AreEqual(BigStage.Charging, boss.BigAttack.Stage, "the warning");
            Assert.IsTrue(Strings.Has(boss.Def.BigAttack.RadioKey), "its radio line");
            Run(world, 8f, () => boss.BigAttack.Stage == BigStage.Firing);
            Assert.AreEqual(BigStage.Firing, boss.BigAttack.Stage);
            Assert.AreEqual(air.FullCount + ground.FullCount, boss.BigAttack.Rounds, "six missiles and two bombs");
            var next = boss.BigAttack.Next;
            Assert.GreaterOrEqual(next - boss.BigAttack.LastStart, boss.Def.BigAttack.Cooldown * 0.99, "then its cooldown");

            // Interrupted: both missile bays broken in the warning leave the bombs; every bay broken cancels it.
            var w2 = Field(4);
            var b2 = w2.SpawnVehicle("morrigan", 1, new Vector2(0f, 60f), 0f);
            Tough(w2, "fighter_jet", new Vector2(-20f, 0f));
            Tough(w2, "aa_vehicle", new Vector2(0f, -20f));
            w2.Bosses.TriggerBig(b2);
            Run(w2, 5f, () => b2.BigAttack.Stage == BigStage.Charging);
            w2.Bosses.Break(b2, b2.Def.PartIndex("bay_l"));
            w2.Bosses.Break(b2, b2.Def.PartIndex("bay_r"));
            Run(w2, 8f, () => b2.BigAttack.Stage != BigStage.Charging);
            Assert.AreEqual(ground.FullCount, b2.BigAttack.Rounds, "the missiles are lost with their bays");
            var w3 = Field(5);
            var b3 = w3.SpawnVehicle("morrigan", 1, new Vector2(0f, 60f), 0f);
            Tough(w3, "fighter_jet", new Vector2(-20f, 0f));
            w3.Bosses.TriggerBig(b3);
            Run(w3, 5f, () => b3.BigAttack.Stage == BigStage.Charging);
            foreach (var id in new[] { "bay_l", "bay_r", "bomb_bay" }) w3.Bosses.Break(b3, b3.Def.PartIndex(id));
            Run(w3, 8f, () => b3.BigAttack.Stage == BigStage.Ready);
            Assert.AreEqual(BigStage.Ready, b3.BigAttack.Stage, "cancelled");
            Assert.AreEqual(0, b3.BigAttack.Rounds, "nothing fired");
        }

        [Test]
        public void MorrigansDuelModeFliesAloneWithItsOwnSalvoAndGoesDark()
        {
            var world = Field();
            var boss = world.SpawnVehicle("morrigan", 1, new Vector2(0f, 60f), 0f);
            Run(world, 1f);
            Assert.IsTrue(world.Bosses.Duel(boss), "into its duel mode");
            Assert.IsFalse(world.Bosses.Duel(boss), "once");
            Run(world, 2f);
            Assert.AreEqual(0, world.EscortsAlive(boss.Id), "no escorts in the duel");
            Assert.AreEqual("morrigan_duel_salvo", boss.BigAttack.Def.Id, "the duel's salvo");
            Assert.IsTrue(boss.BigAttack.Def.Strikes.All(s => s.Prey == BigPrey.Air), "at aircraft only");
            Assert.IsFalse(boss.DuelDark);
            boss.Hp = boss.MaxHp * 0.65f;
            Run(world, 0.5f);
            Assert.IsTrue(boss.DuelDark && boss.HoldFire, "dark at 70 %: no fire, hidden by its stealth");
            Run(world, boss.Def.Duel.VanishSeconds + 0.5f);
            Assert.IsFalse(boss.DuelDark || boss.HoldFire, "back in the fight");
            boss.Hp = boss.MaxHp * 0.6f;
            Run(world, 0.5f);
            Assert.IsFalse(boss.DuelDark, "each mark once");
            boss.Hp = boss.MaxHp * 0.35f;
            Run(world, 0.5f);
            Assert.IsTrue(boss.DuelDark, "dark again at 40 %");
            // A plain boss has no duel mode.
            Assert.IsFalse(world.Bosses.Duel(world.SpawnVehicle("behemoth_mk0", 1, new Vector2(60f, 60f), 0f)));
        }

        [Test]
        public void ADuelMissionFliesTheDecksAircraftOnly()
        {
            const string json = "{\"missions\": [{\"id\": \"duel_test\", \"chapter\": 10, \"map\": \"skyhold\", \"goal\": \"Boss\", \"duel\": true, " +
                                "\"boss\": {\"def\": \"morrigan\", \"x\": 80, \"z\": 80}}]}";
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
            var boss = world.VehicleList.First(v => v.Def.Id == "morrigan");
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

        [Test]
        public void BothNewMiniBossesAreInTheBossHunts()
        {
            var story = BossHunts.Story;
            var full = BossHunts.Full;
            foreach (var id in new[] { "behemoth_mk0", "morrigan" })
            {
                Assert.IsTrue(full.Contains(id), id + " in the full Boss Hunt");
                var entry = story.First(b => b.Id == id);
                Assert.IsFalse(entry.Main, id + " is a mini boss");
            }
            // In story order: Mk.0 after chapter 3's bosses (interlude I), Morrigan after chapter 9's (interlude III).
            var list = story.ToList();
            int IndexOf(string id) => list.FindIndex(b => b.Id == id);
            // Interludes are numbered 13-15 but played between chapters, so compare play order, not numbers.
            var order = Campaign.Chapters.Select(c => c.Number).ToList();
            Assert.Less(IndexOf("behemoth_mk0"), list.FindIndex(b => b.Chapter == 4));
            Assert.Greater(order.IndexOf(list[IndexOf("morrigan")].Chapter), order.IndexOf(9));
            // The week's hunt draws them too (minis drawn from the story's): within a year of weeks each comes up.
            var drawn = new HashSet<string>();
            for (var week = 202601; week <= 202652; week++)
                foreach (var id in BossHunts.Weekly(week))
                    drawn.Add(id);
            Assert.IsTrue(drawn.Contains("behemoth_mk0") && drawn.Contains("morrigan"), "drawn in the week's hunt");
            Assert.IsTrue(BossRushRules.Kinds.Any(k => k.Contains("behemoth_mk0")) && BossRushRules.Kinds.Any(k => k.Contains("morrigan")));
        }
    }
}
