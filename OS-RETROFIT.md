# OS Retrofit — CWI Sync — One-Stop Licensing (slot 14)

Date: 2026-09-23 · OPERATION RETROFIT Wave 2 · Constitution: AGENT-OPERATING-FRAMEWORK-2026-09-23

## What changed (this retrofit)
- Brand: official CWI logo (`brand/logo.jpg`) in the page header; Cumulative Web Inc header/footer identity on every page.
- CTA + try-link: visible "Try it live" strip with a working deep link, plus a business/support secondary CTA.
- Metadata: `llms.txt`, `.well-known/agent-card.json`, `content.json`, JSON-LD `WebApplication` schema.org block, canonical + Open Graph + Twitter tags.
- Marketing: value proposition above the fold; honest-limits copy retained verbatim (truth labels NEVER upgraded).
- Business: $0 free tool; commercial/support route via hp@cumulativeweb.com; attribution via the app's own machine-readable receipts and deep links (no third-party trackers).
- OS fit: nervous-system project state `os-retrofit-14-sync` with evidence-graded claims; 21-gate theorem verdict recorded.

## Red-team pass (2026-09-23)
- Static site; no server, no secrets, no user input reflection. Attack surface is the GitHub issue template (spam-able, but inbound-only by design) and mailto.
- One-sheet PDFs are built reproducibly from tools/build_one_sheets.py — no binary blobs from untrusted sources.
- test_funnel.py link allowlist was too strict (flagged legitimate cwi-i18n hook + self-canonical as failures); allowlist extended with intent, gate now green.

## Secret scan (2026-09-23)
Pattern scan over the full repo (api keys, secrets, tokens, private keys): **0 hits**.


## Tests
tools/test_funnel.py — GATE PASSED (all checks green)

## Truth-label discipline
No label changed in this retrofit. UNVERIFIED stays UNVERIFIED; honest-limits copy untouched.
