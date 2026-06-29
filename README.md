# Lexicon

Lexicon is a GenLayer registry for definitions, citations, revisions, moderation, semantic conflict checks and appeals.

This repository is a public proof package: it includes the product UI, the deployed GenLayer Studionet contract source, deployment metadata, finalized smoke transactions, and test evidence. Local wallet secrets are not included.

## Live System

| Surface | Link |
| --- | --- |
| App | https://lexicon-zeta-woad.vercel.app |
| GitHub | https://github.com/thorbh2/lexicon |
| Contract | https://explorer-studio.genlayer.com/contracts/0xBDa72fA79808d9221bA33D7223E9d1a5187E60A7 |
| Deploy tx | https://explorer-studio.genlayer.com/tx/0xa2fd562c77426f5c0049a35df003520035a322787f7ac21447e24b0c768226d2 |
| Vercel inspect | https://vercel.com/aspros-projects-07dbbeb8/lexicon/4G2LhEnrh8rtR6CzVWtAusHecHin |

## Why Lexicon Exists

A governed registry of terms/definitions/entries moderated by consensus. The registry has a public 'code' (editorial standard); each entry is reviewed by GenLayer against the code and its cited public sources - compliant + well-cited entries are published, conflicting/unsupported ones rejected, and semantic conflicts flagged. Entries are disputable (challenge) and appealable, with contributor reputation + audit trail.

The frontend keeps the original product experience, while the contract adds a reviewable on-chain lifecycle: source records, GenLayer reasoning, challenge and appeal paths, indexed reads, and an audit trail that can be inspected after deployment.

## Contract Architecture

| Area | Detail |
| --- | --- |
| Contract | `contracts/lexicon_v2.py` |
| Size | 37497 bytes |
| Network | GenLayer Studionet, chain id `61999` |
| Write methods | 15 |
| Read methods | 22 |
| GenLayer features | live web rendering, LLM execution, validator-comparative consensus |
| Deployment wallet | 0xD63B44f1248AC167B52ED3D7CA7670d3Ea280197 |
| Contract address | 0xBDa72fA79808d9221bA33D7223E9d1a5187E60A7 |

Architecture note:

> LexiconRegistry V2 (# v0.2.16), 37497 bytes, 15 write + 22 view. Objects: Entry, Citation, Revision, Challenge, Appeal + Reputation + AuditEntry + a governing `code` string. Lifecycle DRAFT->OPEN->UNDER_REVIEW->REVIEWED->CHALLENGE_WINDOW->APPEALED->FINALIZED->ARCHIVED. DynArray[str] stores + TreeMap status/author indexes + reputation + recent ids + clock. GenLayer nondet (web.render + exec_prompt in eq_principle.prompt_comparative) for code-compliance moderation + per-citation credibility + semantic-conflict detection + challenge/appeal rulings; strict-JSON + prompt-injection guards + INVALID_REASONING_JSON fallback. Backward-compat wrappers get_code/set_code/submit_post/moderate/get_post/get_post_count keep the original frontend working.

Core smoke flow:

```text
set_code
  -> create_entry
  -> add_citation
  -> add_revision
  -> open_review
  -> moderate_with_genlayer
  -> open_challenge_window
  -> submit_challenge
  -> resolve_challenge
  -> finalize_entry
  -> archive_entry
  -> recalculate_reputation
```

## Verification Trail

| Step | Transaction |
| --- | --- |
| Set Code | https://explorer-studio.genlayer.com/tx/0xcc01602b5737b600f91f1af5e7807b5830addb15800d9a63e837c3c7a9afc2be |
| Create Entry | https://explorer-studio.genlayer.com/tx/0x0cb2c2b18a3242ca71209a836bb2f9ba6b88dd382167100e74228912ef81fe96 |
| Add Citation | https://explorer-studio.genlayer.com/tx/0x1411d728211d8ab9c3e1bd1690f8ae280ee7e65a50cc89b7835dfef04975dde9 |
| Add Revision | https://explorer-studio.genlayer.com/tx/0xf34fec7df41d85541c0ab12579204d1f20875075e52ac0d9f130763ac302062c |
| Open Review | https://explorer-studio.genlayer.com/tx/0x2f1079f48c0f951fc1d3fbaeef45cec50f07aa2c1b11588ce46d1ea00d910254 |
| Moderate With Genlayer | https://explorer-studio.genlayer.com/tx/0x632e686176d4a1ea0349d6db3bc8cb82f0b2d490fba9dde546357096e8fad50e |
| Open Challenge Window | https://explorer-studio.genlayer.com/tx/0xeb114c24beafe8212756a8ca22e7088d4856ccbadd79ad4c4e2e18256c05e7aa |
| Submit Challenge | https://explorer-studio.genlayer.com/tx/0xc2e091b0bc63639bf4511ce965ebd849ad625fd5ead4ae7dace7cd12c7226889 |
| Resolve Challenge | https://explorer-studio.genlayer.com/tx/0xec73eb74f7cab0ea32427eb8a80822a983996aec25440c28c4391bf5ce43683a |
| Finalize Entry | https://explorer-studio.genlayer.com/tx/0x2760d3f17b0833340aca8daee2d461f9fd41367f6edb0f0c0d157ab3734dc814 |
| Archive Entry | https://explorer-studio.genlayer.com/tx/0x0a319c90232f5d0b39b91b83378f58e2a8b150dc0a241434f74636a6c3a15c98 |
| Recalculate Reputation | https://explorer-studio.genlayer.com/tx/0x3e055cc9302ae1e3cd18b19d30bae82581fb5af1b6a7fdd26a7613e02cf3b7d9 |

Test result:

```text
Schema valid
12 smoke writes finalized
27/27
Static frontend bundled for standalone Vercel deployment
```

## Frontend

Lexicon ships as a standalone static app:

- wallet connection through the bundled browser client
- GenLayer reads through `genlayer-js`
- writes routed through the connected EVM wallet
- local `shared/` client files included so Vercel does not depend on the private workspace router
- deployed contract address pinned in `app.js` and `deployment.json`

## Run Locally

From the private workspace:

```powershell
cd <private-workspace-root>
npm run preview:start
npm run preview:project -- 08-lexicon
```

Open:

```text
http://localhost:8080/08-lexicon/
```

## Publish / Redeploy

```powershell
cd <private-workspace-root>
npm run publish:project -- -Project 08-lexicon -Repo https://github.com/thorbh2/lexicon.git
```

Vercel production redeploy from a clean project folder:

```powershell
npx --yes vercel@latest --prod --yes
```

## Repository Safety

This public repository intentionally excludes local secrets:

- no private keys
- no vault files
- no `.env` files
- no `.vercel` project state
- no local dashboard data

Public files include frontend code, contract source, deployment metadata, tests, and non-sensitive proof links.
