# Models needed after the boss design workbook (09/10)

Owner 10/10: the new mini-bosses ("boss tạo tàu chiến mini") should get their own new models; another agent (the owner's) does models and effects. This file is the hand-over.

Today each new mini is a variant that reuses its parent GLB, and the new hardpoints (also the 111 added on 24 existing bosses) have no muzzle node: shots leave from the carrying part's position.

| mini id | parent chassis (GLB reused today) | data line (balance.json) |
|---|---|---|
| roc_gunship | command_airship | `"id": "roc_gunship"` |
| daedalus_assault | daedalus | `"id": "daedalus_assault"` |
| icarus_interceptor | silver_bug | `"id": "icarus_interceptor"` |
| matriarch_flak | drone_mothership | `"id": "matriarch_flak"` |
| jotunn_artillery | mobile_fortress | `"id": "jotunn_artillery"` |
| bastion_aa | fortress_bastion | `"id": "bastion_aa"` |

Per mini: build `<id>.glb` with a mount + muzzle node for every hardpoint of its row (stable semantic names, Docs/models/RUNTIME_NODES.md; hardpoint list and weapons in REPORT.md / MAPPING.md), then give the row its own `model`. Same for the new hardpoints on existing bosses (Leviathan 22, Kraken 13, ...): add the nodes to those GLBs.

No boss summons ships today (Kraken launches stealth_naval_strike jets, the airships launch strike_drone); any future boss-summoned mini warship gets its own new model too.
