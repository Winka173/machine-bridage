using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Editor;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Field Command 2.0, section F: every fieldable vehicle, elite, tower and boss has its card
    /// picture (512 px, transparent background) in Resources/UI/Cards, the manifest names the model
    /// file it was rendered from, and that file has not changed since (its SHA-1 matches), so a
    /// new model never ships with an old picture. When this fails, render again with graphics:
    /// -executeMethod MachineBrigade.Editor.CardRenders.RenderBatch (the editor does it on import).
    /// </summary>
    public class CardRenderTests
    {
        [Test]
        public void EveryCardHasAFreshPicture()
        {
            var catalog = GameContent.LoadCatalog();
            var cards = CardRenders.Cards(catalog);
            Assert.That(cards.Count(c => c.kind == "vehicle"), Is.EqualTo(MatchSettings.AllVehicles.Length), "every fieldable vehicle");
            Assert.Greater(cards.Count(c => c.kind == "elite"), 0);
            Assert.Greater(cards.Count(c => c.kind == "boss"), 0);
            Assert.Greater(cards.Count(c => c.kind == "tower"), 0);
            var manifest = CardRenders.ReadManifest();
            var byId = manifest.entries.ToDictionary(e => e.id, e => e);
            var problems = new List<string>();
            foreach (var (id, kind, model) in cards)
            {
                if (!byId.TryGetValue(id, out var entry))
                {
                    problems.Add($"{kind} {id}: not in the manifest");
                    continue;
                }
                if (entry.model != model) problems.Add($"{id}: rendered from {entry.model}, the card now shows {model}");
                var source = CardRenders.SourceOf(model);
                if (entry.source != "Models/" + source) problems.Add($"{id}: rendered from {entry.source}, should be Models/{source}");
                if (entry.hash != CardRenders.Hash(source)) problems.Add($"{id}: {source}.glb changed since its picture was rendered");
                if (!File.Exists(Path.Combine(CardRenders.OutFolder, model + ".png"))) problems.Add($"{id}: {model}.png missing");
            }
            Assert.IsEmpty(problems, "Render the card pictures again (CardRenders.RenderBatch, with graphics):\n" + string.Join("\n", problems));
        }

        [Test]
        public void PicturesAre512SquareWithATransparentBackground()
        {
            var manifest = CardRenders.ReadManifest();
            Assert.AreEqual(CardRenders.Size, manifest.size);
            foreach (var model in manifest.entries.Select(e => e.model).Distinct())
            {
                var tex = new Texture2D(2, 2);
                Assert.IsTrue(tex.LoadImage(File.ReadAllBytes(Path.Combine(CardRenders.OutFolder, model + ".png"))), model);
                Assert.AreEqual(CardRenders.Size, tex.width, model);
                Assert.AreEqual(CardRenders.Size, tex.height, model);
                // Corners clear, the middle drawn.
                Assert.Less(tex.GetPixel(0, 0).a + tex.GetPixel(tex.width - 1, tex.height - 1).a, 0.05f, model + ": transparent corners");
                var drawn = 0;
                for (var y = 0; y < tex.height; y += 8)
                for (var x = 0; x < tex.width; x += 8)
                    if (tex.GetPixel(x, y).a > 0.9f) drawn++;
                Assert.Greater(drawn, 200, model + ": the model fills the picture");
                Object.DestroyImmediate(tex);
            }
        }

        [Test]
        public void CardArtFindsThePictureForACard()
        {
            CardArt.Reload();
            Assert.IsNotNull(CardArt.For("main_battle_tank"));
            Assert.IsNotNull(CardArt.For("headquarters"), "a tower");
            var elite = CardArt.Current.entries.First(e => e.kind == "elite");
            Assert.IsNotNull(CardArt.For(elite.id), elite.id);
            Assert.IsNull(CardArt.For("no_such_card"));
        }
    }
}
