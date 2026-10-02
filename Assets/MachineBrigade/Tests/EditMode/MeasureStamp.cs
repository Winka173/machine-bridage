using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 29 S08 (R10): the stamp a measurement writes beside its output (<c>&lt;file&gt;.stamp.json</c>): the sha256 of
    /// balance.json and campaign.json, the build commit and the rules version. Tools/docs/measure_stamp.py reads it and
    /// moves measures taken on other data to the design document's "Lịch sử đo" appendix.
    /// </summary>
    public static class MeasureStamp
    {
        /// <summary>The balance rules version (Tools/docs/measure_stamp.py RULES).</summary>
        public const string Rules = "p29";

        public static void Write(string measuredFile)
        {
            var data = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Data");
            var json = "{ \"balance\": \"" + Sha(Path.Combine(data, "balance.json")) + "\", \"campaign\": \"" + Sha(Path.Combine(data, "campaign.json")) +
                       "\", \"commit\": \"" + Commit() + "\", \"rules\": \"" + Rules + "\", \"at\": \"" + DateTime.UtcNow.ToString("u") + "\" }\n";
            File.WriteAllText(measuredFile + ".stamp.json", json, new UTF8Encoding(false));
        }

        private static string Sha(string path)
        {
            if (!File.Exists(path)) return "";
            using var sha = SHA256.Create();
            var bytes = sha.ComputeHash(File.ReadAllBytes(path));
            var b = new StringBuilder();
            foreach (var x in bytes) b.Append(x.ToString("x2"));
            return b.ToString();
        }

        private static string Commit()
        {
            try
            {
                var git = Path.Combine(Application.dataPath, "..", ".git");
                var head = File.ReadAllText(Path.Combine(git, "HEAD")).Trim();
                if (!head.StartsWith("ref: ")) return head;
                var refPath = Path.Combine(git, head.Substring(5));
                return File.Exists(refPath) ? File.ReadAllText(refPath).Trim() : head.Substring(5);
            }
            catch (IOException)
            {
                return "";
            }
        }
    }
}
