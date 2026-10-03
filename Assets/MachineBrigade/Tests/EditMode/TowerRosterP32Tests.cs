using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L1 (DECISIONS "Prompt 32 L0/L1/L2"): the tower roster 32 -> 22 and the branch rule; play-test 14 deleted
    /// eight more cards (22 -> 14). The data: 14 cards (5 small, 5 medium, 4 large), each with two declared branches of its
    /// size or noBranch, a role tag on every branch that no other card's branch shares and its sibling never does, the
    /// folded and retired towers kept as defs but no cards. The changed branches (the Stinger post, the light-only 57 mm,
    /// the lasers' shells). The save migration (roster version 7). The same validator is Tools/balance/p32_roster.py
    /// --check. Written, not run.
    /// </summary>
    public class TowerRosterP32Tests
    {
        private static Catalog _catalog;
        private static Catalog C => _catalog ??= GameContent.LoadCatalog();

        [Test]
        public void TheRosterHas16CardsFiveSmallSevenMediumFourLarge()
        {
            var cards = TowerCards.All(C);
            Assert.AreEqual(16, cards.Count, string.Join(", ", cards));
            Assert.AreEqual(5, cards.Count(c => C.Vehicles[c].Fort.Size == SlotSize.Small));
            Assert.AreEqual(7, cards.Count(c => C.Vehicles[c].Fort.Size == SlotSize.Medium));
            Assert.AreEqual(4, cards.Count(c => C.Vehicles[c].Fort.Size == SlotSize.Large));
            foreach (var gone in CardMerges.TowerInto.Keys.Concat(CardMerges.RetiredTowers))
            {
                Assert.IsTrue(C.Vehicles.ContainsKey(gone), $"{gone} stays a def (maps, missions)");
                Assert.IsFalse(cards.Contains(gone), $"{gone} is no card");
                Assert.IsFalse(TowerCards.IsCard(C, C.Vehicles[gone]), gone);
            }
            // Play-test 14 deleted some of the cards the folded towers went into (a v7 save migrates on through version 9).
            foreach (var to in CardMerges.TowerInto.Values) Assert.IsTrue(cards.Contains(to) || CardMerges.DeletedPt14.ContainsKey(to), to);
        }

        [Test]
        public void EveryCardHasTwoBranchesOfItsSizeOrNoBranch()
        {
            var failures = new List<string>();
            foreach (var card in TowerCards.All(C))
            {
                var def = C.Vehicles[card];
                var branches = TowerCards.Branches(C, card);
                if (def.NoBranch)
                {
                    if (def.DeclaredBranches.Count > 0 || branches.Count > 0) failures.Add($"{card}: noBranch but has branches");
                    continue;
                }
                if (def.DeclaredBranches.Count != 2 || branches.Count != 2 || branches[0] == branches[1])
                {
                    failures.Add($"{card}: {def.DeclaredBranches.Count} declared, {branches.Count} found");
                    continue;
                }
                foreach (var b in branches)
                {
                    var bd = C.Vehicles[b];
                    if (bd.BranchOf != card) failures.Add($"{b}: branch of {bd.BranchOf}");
                    if (bd.Fort == null || bd.Fort.Size != def.Fort.Size) failures.Add($"{b}: not {card}'s size");
                }
            }
            // No branch row its card does not declare.
            foreach (var d in C.Vehicles.Values)
                if (d.BranchOf != null && TowerCards.All(C).Contains(d.BranchOf) && !TowerCards.Branches(C, d.BranchOf).Contains(d.Id))
                    failures.Add($"{d.Id}: a branch row of {d.BranchOf} the card does not declare");
            Assert.IsEmpty(failures, string.Join("\n", failures));
            CollectionAssert.AreEquivalent(new[] { "cp_relay" }, TowerCards.All(C).Where(c => C.Vehicles[c].NoBranch));
        }

        [Test]
        public void NoTwoBranchesDoTheSameJob()
        {
            var owner = new Dictionary<string, string>();
            var failures = new List<string>();
            foreach (var card in TowerCards.All(C))
            {
                var tags = C.Vehicles[card].NoBranch
                    ? new List<string> { C.Vehicles[card].Role }
                    : TowerCards.Branches(C, card).Select(b => C.Vehicles[b].Role).ToList();
                if (tags.Count == 2 && tags[0] == tags[1]) failures.Add($"{card}: both branches are {tags[0]}");
                foreach (var t in tags)
                {
                    if (string.IsNullOrEmpty(t)) failures.Add($"{card}: a branch without a role tag");
                    else if (owner.TryGetValue(t, out var other) && other != card) failures.Add($"{card}: {t} is also {other}'s");
                    else owner[t] = card;
                }
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [Test]
        public void TheChangedBranchesDoTheirNewJob()
        {
            // The Stinger post out-reaches the 23 mm flak and fires at aircraft only.
            var stinger = C.Vehicles["aa_turret.sam"].Weapon;
            var flak = C.Vehicles["aa_turret.flak"].Weapon;
            Assert.IsTrue(stinger.CanTarget(true) && !stinger.CanTarget(false));
            Assert.Greater(stinger.Range, flak.Range, "the Stinger reaches further than the 23 mm");
            // The 57 mm: light vehicles only, no aircraft, no air-burst round.
            var gun57 = C.Vehicles["gun_turret.auto"].Weapon;
            Assert.IsFalse(gun57.CanTarget(true));
            Assert.IsNull(gun57.AirRound);
            Assert.AreEqual(Prey.Light, gun57.Prey);
            // The lasers stop no shells.
            Assert.AreEqual(0f, C.Vehicles["iron_beam"].Aps.Shells, 1e-6f);
            Assert.AreEqual(0f, C.Vehicles["laser_ad_station"].Aps.Shells, 1e-6f);
            // The guard tower's Watch branch replaces the tower's aura (the precheck: no stacking).
            Assert.AreEqual(0.15f, C.Vehicles["guard_tower.watch"].TowerRangeAura.Rate, 1e-6f);
        }

        [TearDown]
        public void Reset() => PlayerProfile.ResetForTests();

        [Test]
        public void TheSaveMovesOntoThe22Cards()
        {
            // Play-test 14 deleted the heavy flak and lighting cards, so the fold under test is the drone net into the
            // laser station (a card that survives version 9).
            PlayerProfile.LoadForTests(@"{ ""rosterVersion"": 6, ""coins"": 0,
                ""owned"": [ ""manpads_tower"", ""blast_wall"", ""drone_net_tower"", ""laser_ad_station"" ],
                ""rankIds"": [ ""drone_net_tower"", ""laser_ad_station"", ""blast_wall"", ""cp_relay"", ""aa_turret"" ], ""ranks"": [ 5, 3, 2, 7, 7 ],
                ""prints"": [ 0, 0, 0, 0, 0 ],
                ""branchTowers"": [ ""cp_relay"", ""aa_turret"" ], ""branchChoices"": [ ""cp_relay.loot"", ""aa_turret.sam"" ],
                ""baseSmall"": [ ""blast_wall"", ""guard_tower"", ""manpads_tower"" ] }");
            // The folded card keeps the higher rank; the duplicates' and the retired card's coins come back.
            Assert.AreEqual(5, PlayerProfile.Rank("laser_ad_station"), "the higher of the two ranks");
            Assert.IsFalse(PlayerProfile.Owns("drone_net_tower") || PlayerProfile.Owns("manpads_tower") || PlayerProfile.Owns("blast_wall"));
            Assert.IsTrue(PlayerProfile.Owns("laser_ad_station"));
            var expected = CardMerges.TowerPrices["manpads_tower"] + CardMerges.TowerPrices["drone_net_tower"] + CardMerges.TowerPrices["blast_wall"]
                           + CardRanks.CoinsSpent(2) + CardRanks.CoinsSpent(3);
            Assert.AreEqual(expected, PlayerProfile.Coins, "duplicates at their price, the retired card at its price and rank, the lower rank's spend");
            // Branches: none on a card without branches; a reworked branch kept with one free change and a notice.
            Assert.IsNull(PlayerProfile.TowerBranch("cp_relay"));
            Assert.AreEqual("aa_turret.sam", PlayerProfile.TowerBranch("aa_turret"));
            Assert.IsTrue(PlayerProfile.FreeBranchSwap("aa_turret"));
            CollectionAssert.Contains(PlayerProfile.TakeBranchNews(), "aa_turret");
            // The retired card's slot is emptied and the player told once.
            var (emptied, coins) = PlayerProfile.TakeRosterNews();
            CollectionAssert.AreEqual(new[] { "blast_wall" }, emptied);
            Assert.AreEqual(expected - CardRanks.CoinsSpent(3), coins, "the notice counts the roster's refunds (the rank merge's spend is the old rule's)");
            Assert.IsEmpty(PlayerProfile.TakeRosterNews().emptied, "once");
        }
    }
}
