# CWI Sync & Licensing

Inbound inquiry funnel for licensing the That Boy Hi Hat catalog.
**100% pre-cleared, one-stop sync** — master and publishing through Cumulative Web Inc.

- **Live site:** https://cumulativewebinc.github.io/cwi-sync/
- **License page:** https://cumulativewebinc.github.io/cwi-sync/license

## Structure

| Path | What it is |
|---|---|
| `index.html` | Funnel hub — positioning, stats, one-sheets, CTAs |
| `license.html` | The `/license/` page — what licensing covers, one-sheet downloads, inquiry entry points |
| `one-sheets/` | The three one-sheet PDFs (company, artist, “Diabolique” single) |
| `.github/ISSUE_TEMPLATE/sync-inquiry.yml` | Structured inquiry form (project type, media, timeline, budget optional, contact) |
| `assets/cwi-logo.jpg` | Official CWI badge |
| `tools/build_one_sheets.py` | Reproducible PDF builder (reportlab) |
| `tools/test_funnel.py` | Build/test gate — PDFs render, links resolve, template validates |
| `docs/claim-verification.md` | Every public claim traced to a verified fact |

## Inquiry flow (inbound only)

1. Visitor reads `/license/`, downloads one-sheets.
2. Inquires via the **GitHub issue template** (structured) or **mailto:hp@cumulativeweb.com** (freeform).
3. CWI quotes → one agreement (master + publishing) → master delivery.

No outbound solicitation runs through this repo.

## Claim discipline

Every claim on the site and one-sheets traces to the verified-facts list in
`docs/claim-verification.md`. No invented placements, quotes, or awards.
Rebuild the PDFs with `python3 tools/build_one_sheets.py` after any copy change,
then run `python3 tools/test_funnel.py` before merging.
