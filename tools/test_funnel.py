#!/usr/bin/env python3
"""Build/test gate for the cwi-sync funnel.

Tests:
  1. PDFs render — exist, %PDF magic, parseable, exactly 1 page each,
     and contain the key verified claims.
  2. Links resolve — every local href/src in the HTML maps to a repo file;
     mailto and the GitHub issue-template URL are well-formed.
  3. Issue template validates — YAML parses and carries the required fields
     (project type, media, timeline, budget [optional], contact).

Exit 0 = gate passes. Any failure prints diagnostics and exits 1.
"""
import os
import re
import sys

import yaml
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" — " + detail) if detail and not cond else ""))
    if not cond:
        failures.append(name)


PDFS = {
    "one-sheets/cwi-sync-company-one-sheet.pdf": [
        "100% pre-cleared", "Henry Pitts", "Black Lansky", "307",
        "Shaka Zulu", "Doves", "24-track", "hp@cumulativeweb.com",
    ],
    "one-sheets/that-boy-hi-hat-artist-one-sheet.pdf": [
        "That Boy Hi Hat", "alternative rap", "307", "Shaka Zulu",
        "Diabolique", "Cue Recording Studio", "Arlington",
        "hp@cumulativeweb.com",
    ],
    "one-sheets/diabolique-single-one-sheet.pdf": [
        "Diabolique", "Cue Recording Studio", "Arlington", "Virginia",
        "100% pre-cleared", "307", "hp@cumulativeweb.com",
    ],
}

print("== PDFs render ==")
for rel, claims in PDFS.items():
    p = os.path.join(ROOT, rel)
    check(f"{rel} exists", os.path.isfile(p))
    if not os.path.isfile(p):
        continue
    with open(p, "rb") as fh:
        check(f"{rel} has %PDF magic", fh.read(5) == b"%PDF-")
    try:
        r = PdfReader(p)
        check(f"{rel} is 1 page", len(r.pages) == 1, f"got {len(r.pages)}")
        text = "\n".join((pg.extract_text() or "") for pg in r.pages)
        for c in claims:
            check(f"{rel} contains {c!r}", c in text)
        check(f"{rel} title metadata", bool(r.metadata.title), str(r.metadata.title))
    except Exception as exc:  # noqa: BLE001
        check(f"{rel} parses", False, str(exc))

print("== Links resolve ==")
HTMLS = ["index.html", "license.html"]
href_re = re.compile(r'''(?:href|src)="([^"#]+?)"''')
for rel in HTMLS:
    p = os.path.join(ROOT, rel)
    check(f"{rel} exists", os.path.isfile(p))
    if not os.path.isfile(p):
        continue
    html = open(p).read()
    for link in sorted(set(href_re.findall(html))):
        if link.startswith(("http://", "https://")):
            ok = link.startswith("https://github.com/CumulativeWebInc/cwi-sync/issues/new?template=sync-inquiry.yml") or link.startswith("https://cumulativewebinc.github.io/cwi-i18n/") or link.startswith("https://cumulativewebinc.github.io/cwi-sync/")
            check(f"{rel}: external link well-formed: {link[:60]}", ok)
        elif link.startswith("mailto:"):
            check(f"{rel}: mailto targets hp@cumulativeweb.com",
                  link.startswith("mailto:hp@cumulativeweb.com"))
        else:
            target = os.path.normpath(os.path.join(ROOT, os.path.dirname(rel), link))
            check(f"{rel}: local link resolves: {link}",
                  os.path.isfile(target), f"missing {target}")

print("== Issue template validates ==")
tpl_path = os.path.join(ROOT, ".github/ISSUE_TEMPLATE/sync-inquiry.yml")
check("sync-inquiry.yml exists", os.path.isfile(tpl_path))
if os.path.isfile(tpl_path):
    try:
        tpl = yaml.safe_load(open(tpl_path))
        check("template parses as YAML mapping", isinstance(tpl, dict))
        body = tpl.get("body", []) if isinstance(tpl, dict) else []
        ids = [f.get("id") for f in body if isinstance(f, dict)]
        for want, opt in [("project", False), ("project-type", False),
                          ("media", False), ("timeline", False),
                          ("tracks", False), ("budget", True),
                          ("contact", False), ("terms", False)]:
            check(f"template field '{want}' present", want in ids)
        budget = next(f for f in body if isinstance(f, dict) and f.get("id") == "budget")
        check("budget field is optional",
              budget.get("validations", {}).get("required") is False)
        for req_id in ("project", "project-type", "media", "timeline", "contact"):
            f = next(x for x in body if isinstance(x, dict) and x.get("id") == req_id)
            check(f"field '{req_id}' is required",
                  f.get("validations", {}).get("required") is True)
    except Exception as exc:  # noqa: BLE001
        check("template YAML parses", False, str(exc))

cfg_path = os.path.join(ROOT, ".github/ISSUE_TEMPLATE/config.yml")
check("config.yml exists", os.path.isfile(cfg_path))
if os.path.isfile(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    links = (cfg or {}).get("contact_links", [])
    check("config.yml mailto contact link",
          any("mailto:hp@cumulativeweb.com" in (l.get("url") or "") for l in links))

print()
if failures:
    print(f"GATE FAILED: {len(failures)} failing check(s)")
    sys.exit(1)
print("GATE PASSED: all checks green")
