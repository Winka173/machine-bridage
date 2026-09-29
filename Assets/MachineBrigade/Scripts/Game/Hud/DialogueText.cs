using System;
using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 23 H: the texts of the in-battle dialogue (the speakers' short names, the setting, the log, the notices it
    /// added) and how a line's text becomes a subtitle: the speaker's short name, then the words. Older lines carry their
    /// speaker in the text ("Kessler: \"Stand still for me.\"", "Command: the coils are charging."); that prefix names the
    /// speaker and is taken off, with the quotes round the words, so every line reads "KESSLER: Stand still for me."
    /// The words themselves are the texts as written (DECISIONS 23H).
    /// </summary>
    public static class DialogueText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // The speakers' short names on the subtitle (the others are their surnames, from char.<id>.name).
            ["dialogue.name.hq"] = ("Command", "Chỉ huy"),
            ["dialogue.name.recon"] = ("Recon", "Trinh sát"),
            ["dialogue.name.khai"] = ("Kade", "Kade"),
            ["dialogue.name.linh"] = ("Nadia", "Nadia"),
            ["dialogue.name.mai"] = ("Mara", "Mara"),
            ["dialogue.name.dieuhau"] = ("Hawk", "Hawk"),
            ["dialogue.name.hung"] = ("Thorne", "Thorne"),
            ["dialogue.name.quaden"] = ("Wolff", "Wolff"),
            ["dialogue.name.sen"] = ("Venn", "Venn"),
            // H.7: the setting.
            ["settings.dialogue"] = ("In-battle dialogue", "Thoại trong trận"),
            ["settings.dialogue.full"] = ("Full", "Đầy đủ"),
            ["settings.dialogue.important"] = ("Important only", "Chỉ quan trọng"),
            // H.6: the log, from the pause menu.
            ["dialogue.log"] = ("Dialogue log", "Nhật ký thoại"),
            ["dialogue.log.empty"] = ("Nobody has spoken yet in this battle.", "Trận này chưa ai lên tiếng."),
            // F.1: an elite's arrival as a notice of its own (its report is a dialogue line, which the setting may hide).
            ["toast.elite"] = ("Enemy elite on the field: {card}", "Tinh nhuệ địch ra trận: {card}"),
            // Prompt 23 F.3: a side objective's notices (its row on the mission bar shows the goal and the clock).
            ["toast.side.new"] = ("Side objective: {goal}", "Mục tiêu phụ: {goal}"),
            ["toast.side.done"] = ("Side objective complete: {goal}", "Hoàn thành mục tiêu phụ: {goal}"),
            ["toast.side.failed"] = ("Side objective failed: {goal}", "Mục tiêu phụ thất bại: {goal}"),
        };

        /// <summary>The speaker prefixes the older texts carry, in both languages, and whom they name.</summary>
        private static readonly Dictionary<string, string> Prefixes = new(StringComparer.Ordinal)
        {
            ["Command"] = "hq", ["Chỉ huy"] = "hq", ["Recon"] = "recon", ["Trinh sát"] = "recon",
            ["Kessler"] = "kessler", ["Varga"] = "varga", ["Orlov"] = "orlov", ["Aurel"] = "aurel", ["Brandt"] = "brandt",
            ["Thorne"] = "hung", ["Raven"] = "quaden", ["Wolff"] = "quaden", ["Dr Venn"] = "sen", ["Tiến sĩ Venn"] = "sen",
        };

        /// <summary>A speaker's short name on the subtitle: its own entry, else the surname of its full name (a story character's or a commander's).</summary>
        public static string Name(string speaker)
        {
            if (string.IsNullOrEmpty(speaker)) speaker = "hq";
            if (Strings.Has("dialogue.name." + speaker)) return Strings.Get("dialogue.name." + speaker);
            var full = CommanderText.SpeakerName(speaker);
            var space = full.LastIndexOf(' ');
            return space >= 0 && space < full.Length - 1 ? full.Substring(space + 1) : full;
        }

        /// <summary>The text of a line: its key read (and filled with <paramref name="arg"/>) in the current language.</summary>
        public static string Text(string key, object arg) => arg == null ? Strings.Get(key) : Strings.Format(key, arg);

        /// <summary>
        /// A line's text as the subtitle shows it: the speaker a prefix names (else <paramref name="speaker"/>) and the words
        /// without the prefix and without the quotes round them.
        /// </summary>
        public static (string speaker, string words) Split(string text, string speaker)
        {
            text = (text ?? "").Trim();
            var colon = text.IndexOf(": ", StringComparison.Ordinal);
            if (colon > 0 && colon <= 24 && Prefixes.TryGetValue(text.Substring(0, colon), out var named))
            {
                speaker = named;
                text = text.Substring(colon + 2).TrimStart();
            }
            if (text.Length >= 2 && text[0] == '"' && text[text.Length - 1] == '"' && text.IndexOf('"', 1) == text.Length - 1)
                text = text.Substring(1, text.Length - 2);
            return (speaker, text);
        }

        /// <summary>The subtitle as rich text: the name in capitals and bold, in <paramref name="nameColour"/> ("#RRGGBB", or null), then the words.</summary>
        public static string Subtitle(string name, string words, string nameColour)
        {
            var head = Kit.Caps(name) + ":";
            head = nameColour != null ? $"<color={nameColour}>{head}</color>" : head;
            return "<b>" + head + "</b> " + words;
        }
    }
}
