# Machine Brigade: the story (prompt 22)

The campaign's story as prompt 22 pass 1 wrote it: the setting, the people, the chapters and interludes with their
missions and bosses, the opening and the ending, and the hooks for what comes later. The words themselves live in
`Tools/campaign` (story.py, act1.py-act8.py) and `Assets/MachineBrigade/Scripts/Game/Hud/CampaignText.cs`; the data in
`Resources/Data/campaign.json`. Decisions: `Docs/DECISIONS.md`, 22A. Names: `Docs/glossary.md`.

## Setting

The near future. The Meridian Coast is rich in oil and ore. When its government collapsed, a mining consortium hired
Hegemon, the largest private military company in the world, to "keep things stable". Within two years Hegemon was an
army of occupation and the coast its weapons range. The free provinces formed the Meridian Accord; its strongest force
is the 7th Mechanized Brigade, the Machine Brigade: vehicles only, dropped where they are needed, fast. The player is its
field commander. Behind everything is Director Lucien Aurel's Project Icarus, an orbital weapon that can strike anywhere
on the ground. The war lasts three years, from the landing at Stormbeach to the fall of Icarus over Helion.

## People

| Id | Name | Call sign | Side | Drive | First seen |
|---|---|---|---|---|---|
| khai | Colonel Marcus Kade | Iron | ours | calm, practical; trusts the brigade over the politicians | 1 |
| mai | Engineer Mara Lind | | ours | designed Hegemon's first Behemoth, left in shame | 1 |
| dieuhau | Lieutenant Jonah Reyes | Hawk | ours | young, reckless; Raven shot down his wingman | 1 |
| linh | Captain Nadia Kerr | | ours | intelligence; the first to doubt Thorne | 1 |
| hung | General Roland Thorne | Titan | ours, then Hegemon's | believes the Accord loses once Icarus flies; Aurel promised him the coast | 2 |
| brandt | Major Brandt | Bulwark | Hegemon's, then ours | trusts walls; surrenders in 1, builds our walls in 6 | 1 |
| varga | General Viktor Varga | Anvil | Hegemon | old, honourable; the Behemoth's father; respects the player | 2 |
| orlov | Colonel Ilya Orlov | Winter | Hegemon | cold, patient; wins from out of sight | 3 |
| kessler | Admiral Magnus Kessler | Maelstrom | Hegemon | war as a balance sheet | 4 |
| sen | Dr Elara Venn | Queen | Hegemon, then ours | built the swarm to save people; defects at the end of 5 | 5 |
| quaden | Kasimir Wolff | Raven | Hegemon | the arrogant ace; flies Morrigan | 3 |
| aurel | Director Lucien Aurel | Sol | Hegemon | whoever holds the sky holds the world; first on the radio in 11 | 11 |
| brenn | Major Otto Brenn | Ledger | ours | the quartermaster | I |
| adler | Captain Tomas Adler | Flag | ours | takes strongpoints | 4 |
| mendez | Captain Kaia Mendez | Rush | ours | fast columns; Venn's escort | II |
| dahl | Major Piet Dahl | Longshot | ours | the brigade's guns in Veyra | 7 |
| varro | Captain Ines Varro | Tide | ours | the miners' militia | 8 |
| quist | Sergeant Major Lena Quist | Magpie | ours | salvage | 8 |
| reyn | Colonel August Reyn | Crown | ours | the elite column that brings Hawk home | III |
| okoye | Captain Selma Okoye | Vault | ours | the air campaign's supply | 10 |

The ids are the old ones (saves, keys and portraits keep them); `{@lyhan}` and the other tokens of prompt 21 now read the
new names (`NameText.Table`). The eight officers who join on the way are prompt 22 F's commanders (pass 3); they speak on
the radio from the chapter that brings them in, with a portrait of their own.

## Structure: twelve chapters, three interludes (168 main missions, 19 side missions)

Played in this order; an interlude (numbered 13-15 so no chapter's ids move) goes with the act before it for the act
switches of prompt 20 C. The last main mission of a chapter is its operation, with its main boss; an interlude has none.

| # | Act | Chapter | General | Main | Side | Maps | Main boss | Mini bosses |
|---|---|---|---|---|---|---|---|---|
| 1 | I Landfall | Coast of Fire | Brandt | 9 | 1 | Stormbeach, Greenvale, Ashfield | Bastion | Bastion Mk.0 |
| 2 | I | Black Gold | Varga | 11 | 2 | Dunebreak, Red Rock | Behemoth | Inferno |
| 3 | I | The Long Winter | Orlov | 12 | 2 | Whiteout Pass, Frostpeak | Jötunn | Harpy; Fenrir (side) |
| I | I | Blueprints | Varga | 4 | 0 | Foundry | | Behemoth Mk.0 |
| 4 | II Counteroffensive | Iron Harbor | Kessler | 16 | 2 | Rust Yard, Ironport, Beacon Bay | Leviathan | Tempest, Juggernaut, Scylla |
| 5 | II | Burning Canopy | Venn | 13 | 2 | Jungle Pass, Emberridge | Matriarch | Locust, Hive |
| 6 | II | Counterstrike | Varga | 16 | 2 | Ashfield, Whiteout Pass, Greenvale, Stormbeach, Hollow Dam | Moloch | Charybdis, Behemoth Mk.II |
| II | II | The Queen's Choice | | 4 | 0 | Mirewood, Border Crossing | | Locust (twice) |
| 7 | III Betrayal | Veyra | Thorne | 18 | 1 | Metro City, Veyra Old Quarter, Veyra | Nemesis | Atlas; Inferno and Juggernaut again |
| 8 | III | Underworld | Thorne | 12 | 2 | Red Rock, Deepcut Mine, Hollow Dam, Dunebreak | Kronos | Ixion, Tartarus |
| 9 | III | Rough Water | Thorne | 14 | 2 | Ironport, Stormbeach, Beacon Bay, Coral Keys | Typhon | Caspian, Scylla |
| III | III | Hawk and Raven | Raven | 4 | 0 | Frostpeak (reversed), Jungle Pass (reversed) | | Morrigan |
| 10 | IV Silver Sky | War in the Sky | Raven | 14 | 2 | Frostpeak, Skyhold, Whiteout Pass | Roc | Spectre, Icarus Mk.0, Argus (side), Morrigan |
| 11 | IV | Skygate | Aurel | 11 | 1 | Rust Yard, Skyhold, Frostpeak, Skygate Array | Daedalus | Gungnir, Locust |
| 12 | IV | Helion | Aurel | 10 | 0 | Helion Launch Complex, Salt Flats and Dunebreak (reversed), Beacon Bay | Icarus | Behemoth Mk.II, Scylla, Locust |

Every chapter also has a set piece besides its operation (`setPiece` in campaign.json): the landing (1-1), the refinery
raid (c2m10), the Harpy (c3m05), the port (c4m10), the Molten Gate (c5m06), the ceasefire and the Behemoth escort (c6m14,
c6m03), the palace evacuation (c7m08), Tartarus (c8m05), Caspian (c9m05), Icarus Mk.0 and the duel (c10m05, c10m12),
Gungnir (c11m05), Kessler's last ship (c12m02).

## The beats, by mission

- **Opening**: before 1-1, a flash-forward (`campaign.flash`): the sky over Helion, a tungsten rod falling, Aurel: "They
  still don't understand." Then Stormbeach, three years earlier.
- **1 Coast of Fire**: the landing (c1m01, c1m02), the fishing village (c1m03), the outpost in Greenvale where Mara builds
  the field base (c1m04), Bastion Mk.0 (c1m05), Ashfield (c1m08-c1m10): the Bastion falls, Brandt surrenders, his files
  name Varga.
- **2 Black Gold**: Varga's soldier's greeting on the radio (c2m01); Inferno on the refinery road, Mara knows its cooling
  line (c2m05, it falls back), the refinery burns with it (c2m10); the operation at Red Rock with Thorne's army beside us
  for the first time, the Behemoth, and Mara's past told to Kade (c2m11).
- **3 The Long Winter**: the radar line and the unseen guns (c3m02, c3m11, c3m06, c3m12, c3m09); Raven with the Harpy,
  Hawk knows the mark (c3m05); Fenrir in the Whiteout blizzard (c3s2); Jötunn, and Orlov: "Winter always comes back."
  (c3m10).
- **I Blueprints**: the Foundry (i1m01), Brenn's archive (i1m02), Behemoth Mk.0 and Mara's initials on it (i1m03), out
  with the drawings (i1m04).
- **4 Iron Harbor**: Juggernaut (c4m05); Adler's strongpoints (c4m12); the manifests of Varga's Behemoths and Tempest
  (c4m16, c4m10); the first clue about Thorne, the column that never came (c4m13); Kessler runs for the sea (c4m14);
  Scylla at Beacon Bay (c4m06); the old coastal batteries and Leviathan sunk, Kessler alive without a fleet (c4m15, c4m11).
- **5 Burning Canopy**: Locust, then the Hive (c5m08, c5m05); Nadia traces the signal to Venn's laboratory, Venn speaks
  of rescue (c5m11); a second clue, "Titan" in Venn's traffic (c5m09); the swarm called off at the temple (c5m13);
  Matriarch, and Venn gives herself up with the Icarus drive (c5m10).
- **6 Counterstrike**: Ashfield, Brandt's line (c6m01, c6m13); the Whiteout evacuation (c6m02); Greenvale again (c6m16,
  c6m11); Matilda, the Behemoth Mara restarted, escorted (c6m03); Behemoth Mk.II (c6m05); Charybdis back on Stormbeach
  (c6m12, c6m08); the third clue, Thorne's HQ on a Hegemon band (c6m15); the ceasefire, Varga and Kade's only talk
  (c6m14); Moloch at the Hollow Dam, Thorne late again (c6m10).
- **II The Queen's Choice**: Mendez's escort through Mirewood (i2m01), the first Locust (i2m02), the Accord militia on
  the Border Crossing (i2m03), the second Locust and Venn's choice to stay (i2m04).
- **7 Veyra**: Metro City with Thorne's wing, Nadia's warnings (c7m01-c7m07, c7m16, c7s1); Juggernaut on the freight
  line (c7m05); the Old Quarter, Inferno again, Dahl's guns (c7m12-c7m15); the island and the palace (c7m02, c7m17,
  c7m06, c7m11, c7m09, c7m18, c7m08); the liberation: Thorne's base turns, Nadia sees it first, "Have you seen what they
  are about to launch? I have.", Atlas, Nemesis stopped at the edge of the centre, Thorne out with a third of the army
  (c7m10).
- **8 Underworld**: into Deepcut Mine (c8m01-c8m03); Varro's militia (c8m11); Tartarus (c8m05); Quist's salvage and Mara:
  a fortress waiting for Icarus (c8m12); Ixion (c8m07); Kronos stopped short of our base, Thorne away to sea (c8m10).
- **9 Rough Water**: Caspian (c9m05); Venn's listening posts and buoys under Beacon Bay and the Coral Keys (c9m11-c9m13);
  Scylla again (c9m08); Typhon with Thorne aboard, his last message and "Don't let me have been right.", no body (c9m10).
- **III Hawk and Raven**: the crash site (i3m01), Morrigan hunting (i3m02), Reyn's column breaks the ring (i3m03), home
  over Frostpeak (i3m04).
- **10 War in the Sky**: Okoye's airstrip (c10m11); Icarus Mk.0, a test of something bigger (c10m05); Spectre (c10m08);
  Argus (c10s2); the duel over Skyhold (c10m12); Roc, and Hawk's last shot (c10m10).
- **11 Skygate**: Aurel's first words on the radio, the first satellite (c11m01); Gungnir, Orlov's last battle (c11m05);
  Locust, Venn's design in Aurel's hands (c11m07); Mara's guidance computer (c11m11); Daedalus (c11m10).
- **12 Helion**: the Salt Flats and Dunebreak (c12m01, c12m05, c12m03, c12m07, c12m09); Kessler's Scylla and his last
  bargain (c12m02); Varga falls like a soldier, Matilda fights beside us, the tungsten rod, Icarus falls, and Aurel
  fights on in the wreck: "They still don't understand." (c12m10).

## Mission events and the in-battle dialogue (prompt 23)

**The event system.** A mission's battle is more than its goal. It plays events from one library
(`Tools/campaign/events.py`, campaign.json's `eventLibrary`), and each mission names its events in
`Tools/campaign/act10.py`.

- **What an event is.** Each has a trigger: a time, the mission's progress, the boss's health, the units on the field,
  another event, or the player being outnumbered. It also has a warning, lines for the dialogue and sometimes a reward.
- **The kinds:**
  - enemy waves from several directions, made up by the mission's general;
  - Meridian Accord reinforcements;
  - fire support for both sides;
  - the enemy general taking the field;
  - timed side objectives;
  - convoys and loot;
  - supply drops;
  - Nadia's reports and the electronic storm;
  - a mid-battle mini boss, and Kade's change of plan;
  - the weather or night turning;
  - two set pieces of the story's own: the Hollow Dam's ceasefire and the satellite's test rod.
- **How many.** A mission has 2-4 events, a chapter's operation 5-8, an interlude's mission 2-3. No two missions in a row
  play the same set.
- **In the story's spirit.** Each chapter's events follow its story:
  - Stormbeach's landings and the Accord's second wave;
  - Dunebreak's oil convoys and Thorne's first support;
  - Orlov's guns and the snow;
  - Kessler's ships and trains;
  - Venn's swarms and her electronic storm;
  - Varga's counterattacks, Brandt's towers and the one morning Varga and Kade held their fire;
  - Veyra's militia and Thorne's turned columns;
  - Tartarus coming up out of the pit;
  - landings and fog at sea;
  - Raven's raids and nightfall over Skyhold;
  - the drop pods and the first test rod at Skygate;
  - at Helion, every old ally at once against reinforcements from every side.
- **The story choices.** The ferries of Iron Harbor and the miners of Deepcut come only in the option of the chapter's
  choice that saves them.
- **The generals.** Every chapter with an enemy general has the general take the field in one of its missions. The
  general drives an elite early on, their own mini boss later, and carries their passive. They break off at 30 % unless it
  is their last battle.
- **Determinism.** Everything follows the battle's seed, so a checkpoint's replay brings the events back as they were.

**Reinforcements by difficulty (C.3).**

| Difficulty | Enemy directions | Warning | Accord share of an enemy wave |
|---|---|---|---|
| Easy | 1-2 (smaller waves) | 15 s | about 70 % |
| Normal | 2 | 10 s | about 50 % |
| Hard | 2-3 | 8 s | about 30 % |
| Very Hard | 3-4, with elites | 6 s | about 15 %, and one allied wave a mission |

- Strength is prompt 13's combat value.
- No enemy wave appears within 45 m of the player's units: another point in the same direction is used.
- Reinforcements have their own cap, outside the army's.
- An Accord wave takes the place of the losing side's free drop, never on top of it.
- Chapter 12's Total Offensive is the one allied wave as strong as the enemy's.

**The in-battle dialogue (H).**

- **The line.** Every character speaks in one subtitle line just above the card tray: the speaker's short name in the
  side's colour, then the words, on a dim strip. It is at most half the screen wide and two lines long. There is no
  portrait and no voice.
- **Priorities.** One line shows at a time. Story lines and warnings queue. Event lines and the generals' reactions show
  only when the strip is free and not too soon after the last one.
- **The log and the setting.** The pause menu keeps the last 20 lines. Settings choose Full, Important only or Off; story
  lines always show.
- **Story moments.** Six times in the campaign the battle slows to half speed for two or three lines:
  - Varga's word at the Hollow Dam;
  - Venn losing her swarm;
  - Thorne's betrayal;
  - Thorne on Typhon's bridge;
  - Varga's fall;
  - Icarus falling.

## The ending

Icarus falls; Hegemon comes apart; after three years the Meridian Coast is free. Kade turns down a seat in the new
government and stays with the brigade. Mara and Venn take apart the machines they helped to build. Hawk flies one last
patrol over Skyhold. Last scene: Nadia at the orbital tracking screen, a few points of light still unexplained. Project
Icarus was never only one ship (`campaign.epilogue`).

## Hooks for later content (not content yet)

- **The other ships in orbit**: the points of light on Nadia's screen; Icarus 01 was the first finished, not the only
  one built (Venn's files, c10m05's "test flight").
- **Kessler's remnants on the inland rivers**: Kessler is taken at Beacon Bay, but his river flotillas and the sailors
  who "serve the timetable" (c9m14) are still out there.
- **A new Hegemon general every season**: Hegemon comes apart, its contracts do not; each season can bring one of its
  generals back with a passive of his or her own (prompt 22 F's system).
- **Thorne's fate**: no body in Typhon's wreck, a message sent from a buoy four minutes after it sank (c9m10's fragment).

## What pass 2 and the other agents fill in

- **Pass 2 (D, DECISIONS 22D)**: the choices `c4.pursuit` (c4m14: c4m17 *Last Boats* or c4m18 *Harbour Lights*),
  `c8.miners` (c8m09: c8m13 *The Miners of Deepcut*, +6 CP in chapter 9, or c8m14 *Straight at Kronos*) and `c11.radar`
  (c11m09: c11m12 *Blind the Array*, a blinder enemy in chapter 12, or c11m13 *The Short Road*); the front map; the
  intel files, the comic panels, the arcs and the generals' reactive radio (`Tools/campaign/narrative.py`); the story
  loot (`act9.py`).
- **P22-content**: the Foundry (`foundry`, interlude I) and the Veyra Old Quarter (`veyra_old_quarter`, c7m12-c7m15);
  Behemoth Mk.0 (`behemoth_mk0`, i1m03) and Morrigan (`morrigan`, i3m02, c10m12), fought as the Behemoth and Spectre
  until their defs exist. The missions say so in `awaits`. Mara's Behemoth fights in c12m10 (`ally:mara_behemoth`).
- **Pass 3**: c10m12 carries `commander: dieuhau` (the duel is Hawk's, aircraft only: `mode:air_duel`).
