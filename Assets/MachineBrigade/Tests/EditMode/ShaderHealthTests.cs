using System.IO;
using System.Text.RegularExpressions;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 13: every warning zone and the ring under every aircraft drew as a magenta square because one variable in
    /// GroundMark.shader was named "line" (an HLSL keyword), which failed the whole shader. These checks catch a broken
    /// project shader before a play-test does. Written, not run (the owner's rule).
    /// </summary>
    public class ShaderHealthTests
    {
        private const string Folder = "Assets/MachineBrigade/Resources/Shaders";

        private static readonly string[] Names =
        {
            "MachineBrigade/Lit", "MachineBrigade/Unlit", "MachineBrigade/Particle", "MachineBrigade/GroundMark",
            "MachineBrigade/Flipbook", "MachineBrigade/Beam", "MachineBrigade/Shield", "MachineBrigade/Impostor",
            "MachineBrigade/Outline",
        };

        [Test]
        public void EveryRuntimeShaderIsFoundByName()
        {
            foreach (var name in Names) Assert.IsNotNull(Shader.Find(name), $"Shader.Find(\"{name}\") returned null");
        }

        [Test]
        public void NoProjectShaderHasCompileErrors()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Shader", new[] { Folder }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
                Assert.IsNotNull(shader, path);
                Assert.IsFalse(ShaderUtil.ShaderHasError(shader), $"{path} has compile errors (it would draw magenta)");
                Assert.IsTrue(shader.isSupported, $"{path} is not supported on this graphics API");
            }
        }

        /// <summary>A static scan, so the mistake is caught even where the editor compiles only one API.</summary>
        [Test]
        public void NoVariableUsesAnHlslKeywordAsItsName()
        {
            var declaration = new Regex(
                @"\b(?:half|float|int|uint|bool|fixed|min16float)[1-4]?(?:x[1-4])?\s+(line|point|triangle|lineadj|triangleadj|sample|linear|centroid|noperspective|precise|shared|vector|matrix|texture|sampler|register|string|pass|compile)\b");
            foreach (var path in Directory.GetFiles(Folder))
            {
                if (!path.EndsWith(".shader") && !path.EndsWith(".hlsl")) continue;
                var lines = File.ReadAllLines(path);
                for (var i = 0; i < lines.Length; i++)
                {
                    var code = lines[i];
                    var comment = code.IndexOf("//", System.StringComparison.Ordinal);
                    if (comment >= 0) code = code.Substring(0, comment);
                    var m = declaration.Match(code);
                    Assert.IsFalse(m.Success, $"{path}:{i + 1} names a variable \"{m.Groups[1].Value}\", an HLSL keyword");
                }
            }
        }
    }
}
