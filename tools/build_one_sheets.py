#!/usr/bin/env python3
"""Build the three CWI sync one-sheets as PDFs (reportlab).

Every claim on the page traces to the verified-facts list in
docs/claim-verification.md. No invented placements, quotes, or awards.
"""
import os

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGO = os.path.join(
    os.path.expanduser("~"),
    "workspace/cwi-company/fan-network/assets/cwi-logo.jpg",
)
OUT = os.path.join(ROOT, "one-sheets")

# Palette: CWI badge — black / silver / white
BLACK = HexColor("#0b0b0d")
PANEL = HexColor("#151518")
SILVER = HexColor("#c9ccd1")
WHITE = HexColor("#ffffff")
ACCENT = HexColor("#e8b23a")  # restrained gold for stat numerals only

CONTACT = "hp@cumulativeweb.com"
FOOTER_LINE = (
    "Licensing inquiries: hp@cumulativeweb.com  ·  Cumulative Web Inc  ·  "
    "100% pre-cleared, one-stop sync"
)


def styles():
    return {
        "kicker": ParagraphStyle(
            "kicker", fontName="Helvetica-Bold", fontSize=9,
            leading=12, textColor=SILVER, alignment=TA_CENTER, spaceAfter=6,
        ),
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=27,
            leading=31, textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=12,
            leading=16, textColor=SILVER, alignment=TA_CENTER, spaceAfter=14,
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Helvetica-Bold", fontSize=12,
            leading=15, textColor=WHITE, spaceBefore=14, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=10.5,
            leading=15.5, textColor=SILVER, alignment=TA_LEFT, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=10.5,
            leading=15.5, textColor=SILVER, leftIndent=14,
            bulletIndent=4, spaceAfter=4,
        ),
        "stat_num": ParagraphStyle(
            "stat_num", fontName="Helvetica-Bold", fontSize=24,
            leading=26, textColor=ACCENT, alignment=TA_CENTER,
        ),
        "stat_lbl": ParagraphStyle(
            "stat_lbl", fontName="Helvetica", fontSize=8.5,
            leading=11, textColor=SILVER, alignment=TA_CENTER,
        ),
        "cta": ParagraphStyle(
            "cta", fontName="Helvetica-Bold", fontSize=13,
            leading=17, textColor=WHITE, alignment=TA_CENTER, spaceBefore=10,
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica", fontSize=7.5,
            leading=10, textColor=HexColor("#8a8d94"), alignment=TA_CENTER,
        ),
    }


def bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLACK)
    canvas.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
    canvas.restoreState()


def footer(canvas, doc):
    bg(canvas, doc)
    canvas.saveState()
    s = styles()["footer"]
    canvas.setFillColor(HexColor("#8a8d94"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(letter[0] / 2, 0.55 * inch, FOOTER_LINE)
    canvas.restoreState()


def header(story, s, kicker, title, subtitle):
    story.append(Image(LOGO, width=1.5 * inch, height=1.5 * inch))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph(kicker, s["kicker"]))
    story.append(Paragraph(title, s["title"]))
    story.append(Paragraph(subtitle, s["subtitle"]))
    rule = Table([[""]], colWidths=[7.0 * inch])
    rule.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, SILVER),
        ("TOPPADDING", (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))
    story.append(rule)


def stat_row(story, s, stats):
    """stats: list of (number, label) — one row, N columns."""
    cell_style = ParagraphStyle(
        "statcell", parent=s["stat_lbl"], alignment=TA_CENTER,
        leading=13, spaceAfter=0, spaceBefore=0,
    )
    cols = [
        Paragraph(
            '<font color="#e8b23a" size="21"><b>%s</b></font><br/>'
            '<font color="#c9ccd1" size="8.5">%s</font>' % (n, l),
            cell_style,
        )
        for n, l in stats
    ]
    t = Table([cols], colWidths=[7.0 * inch / len(stats)] * len(stats))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(Spacer(1, 0.06 * inch))
    story.append(t)
    story.append(Spacer(1, 0.04 * inch))


def h2(story, s, text):
    story.append(Paragraph(text.upper(), s["h2"]))


def body(story, s, text):
    story.append(Paragraph(text, s["body"]))


def bullets(story, s, items):
    for it in items:
        story.append(Paragraph(it, s["bullet"], bulletText="▸"))


def build(filename, title_text, meta_title, build_fn):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, filename)
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.6 * inch, bottomMargin=0.8 * inch,
        title=meta_title, author="Cumulative Web Inc",
        subject="Sync licensing one-sheet",
    )
    s = styles()
    story = []
    header(story, s, *title_text)
    build_fn(story, s)
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph(
        'To license: email <a href="mailto:%s" color="#ffffff">%s</a>'
        % (CONTACT, CONTACT), s["cta"]))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", path, os.path.getsize(path), "bytes")


# ---------------------------------------------------------------- company
def build_company(story, s):
    body(story, s,
         "Cumulative Web Inc (CWI), led by Henry Pitts (Black Lansky), "
         "licenses its 24-track alternative rap catalog by That Boy Hi Hat "
         "for sync. Every track is <b>100% pre-cleared, one-stop</b> \u2014 "
         "master and publishing through a single contact.")
    h2(story, s, "Why license with CWI")
    bullets(story, s, [
        "<b>100% pre-cleared.</b> Rights verified in-house \u2014 what you hear "
        "is what you can license.",
        "<b>One-stop.</b> One agreement, one signature for master and "
        "publishing.",
        "<b>Managed catalog.</b> All 24 tracks under one roof at CWI.",
    ])
    h2(story, s, "Track record")
    stat_row(story, s, [
        ("~307K", "lifetime Spotify plays<br/>\u201cZooted Zone\u201d \u2014 breakout single"),
        ("3", "catalog tracks held on<br/>Spotify playlist \u201cNew Rap Hits\u201d"),
        ("24", "tracks in the catalog<br/>100% pre-cleared, one-stop"),
    ])
    body(story, s,
         "\u201cNew Rap Hits\u201d holds: <b>#21 \u201cShaka Zulu\u201d</b>, "
         "<b>#30 \u201cZooted Zone\u201d</b>, <b>#31 \u201cDoves &amp; Diamonds\u201d</b>.")
    h2(story, s, "What licensing covers")
    body(story, s,
         "Film, TV, advertising, video games, trailers, streaming, and "
         "digital/social \u2014 master and publishing together, one stop.")
    h2(story, s, "How it works")
    body(story, s,
         "<b>Inquire \u2192 Quote \u2192 License \u2192 Deliver.</b> One contact from "
         "first email to final master.")


# ---------------------------------------------------------------- artist
def build_artist(story, s):
    body(story, s,
         "<b>That Boy Hi Hat</b> is an alternative rap artist managed by "
         "Henry Pitts (Black Lansky) at Cumulative Web Inc. His 24-track "
         "catalog is <b>100% pre-cleared, one-stop sync</b> — ready for "
         "film, TV, advertising, games, trailers, and streaming.")
    h2(story, s, "Breakout")
    stat_row(story, s, [
        ("~307K", "lifetime Spotify plays<br/>“Zooted Zone” — breakout single"),
        ("3", "tracks on Spotify<br/>playlist “New Rap Hits”"),
    ])
    body(story, s,
         "“New Rap Hits” holds: <b>#21 “Shaka Zulu”</b>, "
         "<b>#30 “Zooted Zone”</b>, <b>#31 “Doves &amp; Diamonds”</b>.")
    h2(story, s, "Sync spotlight")
    body(story, s,
         "“<b>Diabolique</b>” — the current sync-push single, recorded at "
         "Cue Recording Studio, Arlington, Virginia. One-stop licensing "
         "through Cumulative Web Inc.")
    h2(story, s, "Catalog")
    bullets(story, s, [
        "24 tracks, alternative rap — the complete That Boy Hi Hat catalog.",
        "100% pre-cleared: master and publishing cleared in-house.",
        "One-stop: a single agreement and a single contact at CWI.",
    ])


# ---------------------------------------------------------------- single
def build_single(story, s):
    body(story, s,
         "“<b>Diabolique</b>” by <b>That Boy Hi Hat</b> — the sync-push "
         "single from the 24-track Cumulative Web Inc catalog. Alternative "
         "rap, recorded at <b>Cue Recording Studio, Arlington, "
         "Virginia</b>.")
    h2(story, s, "Licensing")
    bullets(story, s, [
        "<b>100% pre-cleared.</b> Master and publishing verified in-house.",
        "<b>One-stop.</b> One agreement, one signature, one contact at CWI.",
        "Available for film, TV, advertising, video games, trailers, "
        "streaming, and digital/social campaigns.",
    ])
    h2(story, s, "Artist track record")
    stat_row(story, s, [
        ("~307K", "lifetime Spotify plays<br/>“Zooted Zone” — breakout single"),
        ("3", "catalog tracks on<br/>“New Rap Hits” (#21, #30, #31)"),
    ])
    body(story, s,
         "That Boy Hi Hat is managed by Henry Pitts (Black Lansky), "
         "Cumulative Web Inc. “New Rap Hits” holds “Shaka Zulu” (#21), "
         "“Zooted Zone” (#30), and “Doves &amp; Diamonds” (#31) — proof the "
         "catalog converts with real listeners.")


if __name__ == "__main__":
    build("cwi-sync-company-one-sheet.pdf",
          ("CUMULATIVE WEB INC · SYNC & LICENSING",
           "One-Stop Sync.<br/>Pre-Cleared Catalog.",
           "24-track alternative rap catalog · master + publishing · one signature"),
          "CWI Sync — Company One-Sheet", build_company)
    build("that-boy-hi-hat-artist-one-sheet.pdf",
          ("CUMULATIVE WEB INC · ARTIST ONE-SHEET",
           "That Boy Hi Hat",
           "Alternative rap · 24-track catalog · 100% pre-cleared, one-stop sync"),
          "That Boy Hi Hat — Artist One-Sheet", build_artist)
    build("diabolique-single-one-sheet.pdf",
          ("CUMULATIVE WEB INC · SINGLE ONE-SHEET — SYNC PUSH",
           "“Diabolique”",
           "That Boy Hi Hat · recorded at Cue Recording Studio, Arlington, Virginia"),
          "Diabolique — Single One-Sheet (Sync Push)", build_single)
