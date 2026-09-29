# Owner's spec prompts

The owner's original Vietnamese specs, saved as sent, prompt 0 (the shared context) to prompt 24. At the end of each prompt file, "YÊU CẦU LẺ GẮN VÀO PROMPT NÀY" lists the owner's standalone requests that fit it, verbatim and dated; prompt 0 holds the early requests from before prompt 1, the working rules and the PDF requests. Requests no prompt covers (effects, muzzle flashes, missiles, sizes from the play tests) are in requests_vi.md. The version history is in Docs/CHANGELOG.md.

| Prompt | Subject | State |
|---|---|---|
| 0 | shared context and working rules | standing |
| 1 to 7 | bases, roster, towers, campaign, multi-stage missions, Operations, sized slots | done |
| 8 to 15 | content, boss parts, UI 2.0, compact HUD, stuck vehicles, balance, Base screen, armour and penetration | done |
| 16 | Lighthouse Bay, Leviathan and fleet, old-boss weapons, escorts | in progress |
| 17 | long maps, layered bases, roster merges, new units | in progress |
| 18 | a big attack for every boss | queued |
| 19 | the Silver Bug rebuilt as an orbital spacecraft: altitude tiers, drop pods, the tungsten-rod strike, the phase-3 crash | on hold until the owner asks |
| 20 | 12-chapter campaign, main and mini bosses, renames, Boss Hunt, towers | on hold until the owner asks |
| 21 | Sandbox mode, full Vietnamese and English | on hold until the owner asks |
| 22 | the full story, non-Vietnamese proper names, 12 chapters + 3 interludes, the Commander system, Foundry and Veyra Old Quarter, Behemoth Mk.0 and Morrigan | on hold until the owner asks |
| 23 | data-driven mission events (reinforcements by difficulty, fire, generals on the field, side goals, weather changes), one text-only dialogue line | on hold until the owner asks |
| 24 | camouflage and real-model skins (with a reserved list of real vehicles kept for future cards), all sound and adaptive music, the new-player experience | on hold until the owner asks |

Work done now should not block prompts 19 to 24. Keep internal ids stable and apart from display names (20 A), make big attacks, parts and escorts data-driven so they can become the shared boss templates (20 E), and route every new string through localisation (21 I). Prompt 19 F replaces the Silver Bug's prompt 18 big attack (the laser sweep) with the tungsten-rod rain, so keep that attack a swappable data entry. Prompt 22 renames every proper name (people, places, maps) and prompt 23 turns every "radio" line into one subtitle-style text line, so new names and radio lines should live in the text tables, not in code. Prompt 24 keeps a reserved list of real vehicles (CAESAR, Archer, T-14, BMD-4, Sprut-SD, AAV-7, BMP-3F, RAH-66, EA-18G, V-22, Leonidas) for future cards, so don't use them as skins or alternate models.
