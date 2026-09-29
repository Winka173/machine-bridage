# Localisation report (prompt 21 H)

Audit of the two languages at `lead/integration` 06b8f75, and what prompt 21 (sections I to L) changed. The terms are
in `Docs/glossary.md`; the decisions in `Docs/DECISIONS.md`, 20L.

## What the game had

**Languages.** English and Vietnamese, both complete in structure. Every player-facing text is an entry `key → (en, vi)`
of seven C# tables in `Scripts/Game/Hud`: `Strings.cs` 2,409, `CampaignText.cs` 1,222, `BossText.cs` 269,
`GuideText.cs` 138, `BigAttackText.cs` 137, `UnitText.cs` 114, `OrbitalText.cs` 36 (4,325 entries). Data files hold keys,
never words (units, bosses, maps, missions, supports and parts are named through `unit.`, `boss.`, `map.`, `mission.`...
keys). There is no Unity Localization package. The setting (Settings, Display: Auto, English, Tiếng Việt) follows the
device when on Auto; changing it on the menu reloaded the scene in the new language; there was no way to change it in
a battle.

**Keys in one language only.** None: no entry had an empty language. One key sat in two tables (`radio.betrayal`, in
`Strings.cs` and `CampaignText.cs`; the second copy was never read). 102 entries had the same text in both languages:
all of them names, abbreviations or bare placeholders, except three untranslated ones (`boss.caspian`, `unit.caspian`
"Caspian · Ekranoplan", `part.sonar`).

**Screens that mixed the two.**

- English screens: 126 English texts held Vietnamese. Most were the story's proper names, which stay (Diều Hâu, Lý Hàn,
  Trần Khải, Lê Phong, Quạ Đen, Lam Thành, Bà Già). Real mistakes: "Bãi Đổ Bộ" for the Landing Beach map (2 texts),
  "xu" for coins in the two campaign reward lines, "Appliqué" with a mark.
- Vietnamese screens: English words in about 50 Vietnamese texts, besides the newer boss names missing from the
  allow-list. They were "map" (the Base screen's "Chỉnh riêng cho map
  này", its idle hint, its three map-setup notes and the home screen's base-set line), "tungsten" (13), "laser" (5),
  "rocket", "radio", "hangar", "sonar", "Ekranoplan", and English map names (Skyhold ×5, Ironport ×3, Ashfield ×2,
  Dunebreak, Frostpeak, "Thành Phố Metro").
- The Base screen. All 119 of its `camp.*` texts had both languages, and a scan of the built screen in Vietnamese
  (`army-base`, `army-base-picked`, `army-base-ranges`, `army-outpost`) found only the word "map". The all-English Base
  screen the owner saw does not come from the current code. The likely cause is the language on Auto on a device set to
  English (the emulator's default): the whole game is then in English, and the story screens, full of Vietnamese names,
  still look Vietnamese. `L10nTests.EveryScreenShowsOneLanguage` now fails on any screen that mixes the two.
- Map names. The story used other names than the map table: in English, Red Rock ×10, Whiteout (pass) ×8, Skyhold ×19,
  Launch Site, Orbital Gate. The table has Redrock Canyon, Whiteout Pass, Skyhold Airbase, Icarus Launch Site and Orbital
  Gateway. In Vietnamese, Tầng Mây ×14 and Skyhold ×5 for Căn Cứ Tầng Mây, and Đá Đỏ for Hẻm Đá Đỏ.
- Terms. Vietnamese called a boss "trùm" 71 times and "boss" 49 times. Percentages were written "25%" about 195 times
  and "25 %" about 70 times, in both languages.

**Generated lines.** The Behaviour and ammunition lines (`UnitLines`), branch facts (`BranchLines`), effect tables and
Strong / Weak (`Counters`, `CombatIcons`), equipment lines (`GearText`), support numbers (`SupportLines`), notices, radio,
results and defeat hints all went through the tables already. Their numbers did not: about 25 places formatted with
the platform's current culture (`ToString("0.#")`), five helpers used the platform's "vi-VN" data, and whole numbers in
filled texts had no thousands separator.

**Placeholders.** 519 texts used positional placeholders (`{0}`, `{1}`), 164 of them with two or more and 19 with the
English order different from the argument order. A translator could not tell what `{0}` was.

**Plurals.** 73 English texts would read "1 coins", "1 bosses" or "1 rounds" (`{0} coins`).

**Checks.** `LocalisationScanTests` skipped `BossText`. `UiLanguageTests` skipped `BigAttackText`, `OrbitalText` and
`BossText`, read its allow-list from a line of DECISIONS.md, and failed on about 80 texts (the newer boss names, and the
English above). Fonts: the five Barlow kit fonts were checked for Vietnamese letters; Be Vietnam Pro (the screens' text
font, four weights), Barlow Condensed Medium, Inter and JetBrains Mono were not.

**Not in the game yet.** There is no season pass, no local notification and no in-game privacy policy or terms, so there
was nothing to translate. They must be written in both languages when they come; the scans cover every table.

**Words in code.** No player-facing text is written in code, except the game's name (MACHINE BRIGADE), the language
names on the switch (English, Tiếng Việt, each in its own language), the debug FPS counter and the kit preview's
developer labels.

## What changed

- **Language setting (I1).** Auto follows the device (Vietnamese device → Vietnamese, any other → English). The menu
  still reloads in the new language. The pause menu now has the switch too: the battle HUD relabels itself in place
  (`Relabel`), and the battle under the pause is not reloaded.
- **Named placeholders (I3).** Every table text uses named placeholders (`{count}`, `{seconds:0.#}`, `{card}`), and the
  call sites pass names: `Strings.Format("camp.tooBig", ("card", name), ("size", size))`. A text with one placeholder
  still takes one value. An unknown name stays visible, so the screen scans catch it.
- **Numbers and units (I4).** `Strings.Num` and `Strings.Culture` write 184.172 and 0,75 in Vietnamese, 184,172 and 0.75
  in English, from a number format built by hand (no platform culture data). Filled texts, equipment lines, generated
  lines, the shop and the detail pages use it. Seconds are "s" in English and "giây" in Vietnamese; metres, mm and CP
  are the same in both; a percentage is written "25%" in both.
- **Plurals (I5).** English counts use `{count|# coin|# coins}`; the 73 texts are converted, and a check stops new ones.
- **Fonts (I6).** Every font the game ships, at every weight, carries every Vietnamese letter in both cases; Be Vietnam
  Pro and Barlow Condensed carry every character of every text.
- **Names (J1, J5).** The story's Vietnamese names are `{@id}` tokens filled from `NameText.Table` (439 places), so
  prompt 22 swaps each in one entry. `NameText.Kept` lists the names that stay as they are in both languages; it
  replaces the DECISIONS.md allow-list. Boss subtitles are translated and in English title case, one per boss, the
  same on its card and on its boss bar ("Icarus · Orbital Spacecraft" / "Icarus · Phi thuyền quỹ đạo").
- **Content (J3, J4).** Every text keeps both languages. The English map names and the Vietnamese ones are the map
  table's everywhere. Vietnamese has no English words left except the kept names; a boss is "boss" (mini boss,
  boss chủ lực), and the mode keeps its name, Săn trùm. `radio.betrayal` is in one table.
- **Tight spots (K).** The layout checks now also run in English at 16:9 and 4:3 and in English Large text. Fixes: the
  pause menu's language row sits on one line; the tower-branch picker shows short names and stacks its two cards in
  Large text; the icon legend's cells are wider in Large text; four gear pieces have shorter English names (Tungsten
  Core, Carousel Loader, Halon System, Camo Net); the thermobaric launcher's short name is TOS-1A.

## Checks (L)

- `L10nTests`: every key has both languages in one table; every placeholder is named and the same in both languages;
  every `{@name}` exists; no placeholder, token or brace is left once a text is filled; no Vietnamese letter in the
  English texts but in the kept names; one subtitle per boss; number formats; English plurals and the plural check;
  the default follows the device; `Relabel` turns old texts into new ones; every menu and battle screen shows one
  language; the screenshot set names real screens.
- `L10nSwitchTests`: a tap on the language on the settings screen switches, saves, and the rebuilt menu (settings,
  home, Base screen) shows only the new language; a tap in a paused battle's menu relabels the HUD once, keeps the pause
  open, and leaves no word of the old language, both ways.
- `UiLanguageTests`: no English in any Vietnamese text of any table (the kept names allowed); every font carries every
  Vietnamese letter and every text character.
- `LocalisationScanTests`: every table; named placeholders and name tokens count as leftovers on the screens.
- `UiLayoutTests`: clipped text, alignment and tap areas in Vietnamese (four shapes, Large), in English (16:9, 4:3) and
  in English Large.

## Screenshots

`UiShots` has a set for this check: the main menu and battle screens in both languages at the four shapes (208 files,
`l10n-<screen>-<en|vi>-<shape>.png`). It needs a batch run with graphics, and the emulator was running (a graphics run
beside it can crash the emulator's OpenGL driver), so the set waits for the testing phase:

```
env -u ELECTRON_RUN_AS_NODE "/c/Program Files/Unity/Hub/Editor/6000.6.3f1/Editor/Unity.exe" -batchmode -projectPath <worktree> \
  -executeMethod MachineBrigade.Editor.UiShots.KitScreens -mbShotsSet l10n -mbShotsDir Docs/ui-screens -quit -logFile <log>
```

Screens in the set: home, setup-mode, campaign, campaign-chapter, briefing, dossier, operations, army-deck,
army-towers, army-gear, army-base, army-outpost, detail, detail-weapons, detail-armour, detail-tower, shop-crates,
settings, legend; the battle's hud-score, hud-mission, hud-boss-open, hud-defend, result-win, result-loss, pause. The
Sandbox screens (prompt 21 part 1, built on its own branch) join the set when they are merged.
