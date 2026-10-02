using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L8 (DECISIONS "Prompt 32 L4/L5/L6/L8"): every number of the ammunition handbook matches the data. The
    /// strings it generates are compared with the damage table, the penetration row, the thermobaric value, the worked
    /// example's damage, the point defences' shell shares, the reactive armour's cap and the wall breakers' multiplier,
    /// in both languages; the detail page's chips open entries that exist. Written, not run.
    /// </summary>
    public class HandbookP32Tests
    {
        private static Catalog _catalog;
        private static Catalog C => _catalog ??= GameContent.LoadCatalog();

        private static void InBoth(System.Action check)
        {
            var was = Strings.Vietnamese;
            try
            {
                foreach (var vi in new[] { false, true })
                {
                    Strings.Vietnamese = vi;
                    check();
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        private static HandbookEntry Entry(string id) => AmmoHandbook.Build(C).Single(e => e.Id == id);

        [Test]
        public void TheDamageTypeTableIsTheDatas()
        {
            InBoth(() =>
            {
                var e = Entry(AmmoHandbook.Types);
                Assert.AreEqual(6, e.Rows.Count, "six damage types");
                for (var i = 0; i < AmmoHandbook.DamageTypes.Length; i++)
                {
                    var t = AmmoHandbook.DamageTypes[i];
                    Assert.AreEqual(AmmoHandbook.TypeName(t), e.Rows[i][0]);
                    for (var k = 0; k < AmmoHandbook.Kinds.Length; k++)
                        Assert.AreEqual(AmmoHandbook.Mult(C.Damage.Type(t, AmmoHandbook.Kinds[k])), e.Rows[i][k + 1], $"{t} on {AmmoHandbook.Kinds[k]}");
                    StringAssert.Contains(AmmoHandbook.TypeName(t), e.Lines[i]);
                }
            });
        }

        [Test]
        public void ThePenetrationRowIsTheDatas()
        {
            InBoth(() =>
            {
                var e = Entry(AmmoHandbook.Penetration);
                Assert.AreEqual(DamageTable.PenetrationSteps, e.Rows.Count);
                for (var i = 0; i < DamageTable.PenetrationSteps; i++)
                    Assert.AreEqual(AmmoHandbook.Mult(C.Damage.PenetrationStep(i)), e.Rows[i][1], $"step {i}");
                StringAssert.Contains(ArmourLevels.Max.ToString(), e.Lines[0], "bosses up to level 5");
            });
        }

        [Test]
        public void TheWorkedExampleIsComputedFromTheData()
        {
            InBoth(() =>
            {
                var e = Entry(AmmoHandbook.Penetration);
                var shooter = C.Vehicles[C.Handbook.ExampleShooter];
                var target = C.Vehicles[C.Handbook.ExampleTarget];
                var w = shooter.Mounts[0].Weapon;
                var line = e.Lines[1];
                StringAssert.Contains(Strings.Num(AmmoHandbook.ShotOn(C, w, target.Armour.Front), "0"), line, "the front hit");
                StringAssert.Contains(Strings.Num(AmmoHandbook.ShotOn(C, w, target.Armour.Side), "0"), line, "the side hit");
                StringAssert.Contains(Strings.Num(target.MaxHp, "0"), line, "the target's health");
                StringAssert.Contains(AmmoHandbook.Mult(C.Damage.Effective(w, target.Armour.Front, TargetKind.Ground)), line);
                Assert.AreEqual(w.Damage * C.Damage.Penetration(w.Penetration, target.Armour.Front, DamageTable.Overmatches(TargetKind.Ground, Armour.StrikesTop(w))) *
                    C.Damage.TypeOf(w, TargetKind.Ground), AmmoHandbook.ShotOn(C, w, target.Armour.Front), 1e-3f);
            });
        }

        [Test]
        public void TheMarksQuoteTheRules()
        {
            InBoth(() =>
            {
                var thermo = Entry(AmmoHandbook.Thermobaric).Lines[0];
                StringAssert.Contains(AmmoHandbook.Mult(C.Damage.ThermobaricStructure), thermo);
                StringAssert.Contains(AmmoHandbook.Mult(C.Damage.Type(DamageType.HighExplosive, TargetKind.Structure)), thermo);
                var alt = Entry(AmmoHandbook.Alt).Lines[0];
                StringAssert.Contains(Strings.Num(WeaponDef.RoundHoldSeconds, "0.#"), alt);
                StringAssert.Contains(Strings.Num(WeaponDef.MinSwitchSeconds, "0.#"), alt);
                var air = Entry(AmmoHandbook.Airburst).Lines[0];
                StringAssert.Contains(AmmoHandbook.Mult(C.Damage.Type(DamageType.Fragmentation, TargetKind.Air)), air);
            });
        }

        [Test]
        public void TheDefencesMatchTheLockedRules()
        {
            InBoth(() =>
            {
                var e = Entry(AmmoHandbook.Defences);
                StringAssert.Contains(AmmoHandbook.Percent(HandbookFacts.ReactiveCap), e.Lines[0], "reactive armour's cap");
                var pd = e.Lines[3];
                StringAssert.Contains(AmmoHandbook.Percent(C.Vehicles["c_ram"].Aps.Shells), pd, "the C-RAM's shell share");
                StringAssert.Contains(AmmoHandbook.Percent(C.Vehicles["laser_ad_station"].Aps.Shells), pd, "the laser's shell share");
                // SELF_APS and POINT_DEFENSE never stop a tank's shell: both lines say so (the rule is the code's too).
                StringAssert.Contains(Strings.Vietnamese ? "không chặn đạn pháo xe tăng" : "never a tank's shell", e.Lines[2]);
                StringAssert.Contains(Strings.Vietnamese ? "không chặn đạn pháo xe tăng" : "never a tank's shell", pd);
            });
        }

        [Test]
        public void TheStructureEntryIsTheDatas()
        {
            InBoth(() =>
            {
                var e = Entry(AmmoHandbook.Structures);
                Assert.AreEqual(AmmoHandbook.Mult(C.Damage.ThermobaricStructure), e.Rows[0][1], "thermobaric first");
                foreach (var row in e.Rows.Skip(1))
                {
                    var t = AmmoHandbook.DamageTypes.Single(x => AmmoHandbook.TypeName(x) == row[0]);
                    Assert.AreEqual(AmmoHandbook.Mult(C.Damage.Type(t, TargetKind.Structure)), row[1], t.ToString());
                }
                var walls = Entry(AmmoHandbook.Walls).Lines[0];
                StringAssert.Contains(AmmoHandbook.Mult(C.Base.WallBreakerMultiplier), walls);
                foreach (var id in C.Base.WallBreakers) StringAssert.Contains(Strings.Unit(id), walls);
            });
        }

        [Test]
        public void EveryChipOpensAnEntryThatExists()
        {
            var ids = AmmoHandbook.Build(C).Select(e => e.Id).ToHashSet();
            foreach (var v in C.Vehicles.Values)
                foreach (var (key, entry) in AmmoHandbook.Chips(C, v))
                {
                    Assert.IsTrue(ids.Contains(entry), $"{v.Id}: {entry}");
                    Assert.IsTrue(Strings.Has(key), key);
                }
            Assert.IsTrue(AmmoHandbook.Chips(C, C.Vehicles["armored_bulldozer"]).Any(c => c.entry == AmmoHandbook.Walls), "a wall breaker's chip");
        }
    }
}
