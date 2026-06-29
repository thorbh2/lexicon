# LexiconRegistry V2

The contract treats knowledge as a maintained ledger, with indexed entries, source checks and read models that make the registry usable from the UI.

A governed registry of terms/definitions/entries moderated by consensus.

## LexiconRegistry Brief

This repo is organized for review: the app can be opened locally, the contract source is present, and the deployed Studionet address is pinned in `deployment.json`.

- Folder: `projects/08-lexicon`
- Frontend shape: static browser app
- Contract source: `contracts/lexicon_v2.py`
- Build status: Schema-valid (37497 bytes, 15 write + 22 view); deployed + 12 write smoke txs incl 2 GenLayer reasoning calls; 27/27 read tests passed; legacy backward-compat verified; frontend repointed (no redesign).

## Registry Mechanics

LexiconRegistry V2 (# v0.2.16), 37497 bytes, 15 write + 22 view.

- Primary source: `contracts/lexicon_v2.py` (37,497 bytes)
- Public write/action methods: 16
- Read methods: 21
- GenLayer features: live web rendering, LLM adjudication, validator-comparative consensus, indexed storage, append-only collections

Typical flow: `create_entry` -> `open_review` -> `submit_challenge` -> `resolve_challenge_with_genlayer` -> `open_challenge_window` -> `submit_appeal` -> `archive_entry`

Useful reads: `get_entry`, `get_entry_count`, `get_recent_entries`, `get_entries_by_status`, `get_entries_by_author`, `get_citation`, `get_entry_citations`, `get_revisions`

## Contract Receipt

- Network: studionet (61999)
- Contract: [0xBDa72fA79808d9221bA33D7223E9d1a5187E60A7](https://explorer-studio.genlayer.com/contracts/0xBDa72fA79808d9221bA33D7223E9d1a5187E60A7)
- Deploy tx: [0xa2fd562c...8226d2](https://explorer-studio.genlayer.com/tx/0xa2fd562c77426f5c0049a35df003520035a322787f7ac21447e24b0c768226d2)
- Deployed at: 2026-06-22T23:15:32.159Z
- Smoke writes recorded: 12

Smoke coverage:

- set_code: [0xcc01602b...afc2be](https://explorer-studio.genlayer.com/tx/0xcc01602b5737b600f91f1af5e7807b5830addb15800d9a63e837c3c7a9afc2be)
- create_entry: [0x0cb2c2b1...81fe96](https://explorer-studio.genlayer.com/tx/0x0cb2c2b18a3242ca71209a836bb2f9ba6b88dd382167100e74228912ef81fe96)
- add_citation: [0x1411d728...75dde9](https://explorer-studio.genlayer.com/tx/0x1411d728211d8ab9c3e1bd1690f8ae280ee7e65a50cc89b7835dfef04975dde9)
- add_revision: [0xf34fec7d...02062c](https://explorer-studio.genlayer.com/tx/0xf34fec7df41d85541c0ab12579204d1f20875075e52ac0d9f130763ac302062c)
- open_review: [0x2f1079f4...910254](https://explorer-studio.genlayer.com/tx/0x2f1079f48c0f951fc1d3fbaeef45cec50f07aa2c1b11588ce46d1ea00d910254)
- moderate_with_genlayer: [0x632e6861...fad50e](https://explorer-studio.genlayer.com/tx/0x632e686176d4a1ea0349d6db3bc8cb82f0b2d490fba9dde546357096e8fad50e)

## Inspect The App

```powershell
cd C:\Users\aspronim\Desktop\design-skills
npm run preview:start
npm run preview:project -- 08-lexicon
```

Open http://localhost:8080/08-lexicon/.

## Shipping Notes

```powershell
cd C:\Users\aspronim\Desktop\design-skills
npm run publish:project -- -Project 08-lexicon -Repo https://github.com/aspro45/<repo-name>.git
```

## Security Notes

The repo is designed for public GitHub/Vercel release. Keep `.env`, `.vercel/`, wallet vaults, private keys and local dashboard state out of git. The publisher script enforces these ignore rules before it pushes.
