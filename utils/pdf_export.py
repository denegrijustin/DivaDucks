"""
PDF export — exactly 3 pages, Diva Ducks branded.
Colors mirror the logo: Crimson, Forest Green, Gold, Dark, Cream.
"""
import io, os
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image as RLImage,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Logo-matched palette ────────────────────────────────────────────────────
CRIMSON      = colors.HexColor("#B31B1B")
CRIMSON_DARK = colors.HexColor("#7B1010")
FOREST       = colors.HexColor("#1A5C1A")
FOREST_LIGHT = colors.HexColor("#2E8B2E")
GOLD         = colors.HexColor("#C9A84C")
DARK         = colors.HexColor("#111111")
CREAM        = colors.HexColor("#F2E8C8")
OFF_WHITE    = colors.HexColor("#F5F0E8")
BG_CARD      = colors.HexColor("#1A1E1A")
WHITE        = colors.white
LIGHT_GREY   = colors.HexColor("#F0F0F0")
STRIPE       = colors.HexColor("#E8F0E8")

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "diva_ducks_logo.png"
)

# ── Styles ──────────────────────────────────────────────────────────────────
_styles = getSampleStyleSheet()

def _s(name, **kw):
    return ParagraphStyle(name, parent=_styles["Normal"], **kw)

SECTION_STYLE  = _s("Section",  fontName="Helvetica-Bold", fontSize=12,
                     textColor=FOREST, spaceAfter=4)
BODY_STYLE     = _s("Body",     fontName="Helvetica",      fontSize=9,
                     textColor=DARK)
OUT_STYLE      = _s("Out",      fontName="Helvetica",      fontSize=8,
                     textColor=colors.HexColor("#666666"))


# ── Public entry point ───────────────────────────────────────────────────────
def build_pdf(game_plan: List[Dict], players: List[Dict],
              settings: Dict, qb_usage: Dict, usage: Dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.45 * inch, leftMargin=0.45 * inch,
        topMargin=0.45 * inch,  bottomMargin=0.45 * inch,
    )

    half1 = [p for p in game_plan if p["half"] == 1]
    half2 = [p for p in game_plan if p["half"] == 2]

    story = []
    story += _half_page("1ST HALF GAME PLAN", half1)
    story += [PageBreak()]
    story += _half_page("2ND HALF GAME PLAN", half2)
    story += [PageBreak()]
    story += _stats_page(players, usage, qb_usage, game_plan)

    doc.build(story,
              onFirstPage=_draw_page_chrome,
              onLaterPages=_draw_page_chrome)

    buffer.seek(0)
    return buffer.read()


# ── Page header / footer drawn on canvas ────────────────────────────────────
def _draw_page_chrome(canvas, doc):
    W, H = letter
    canvas.saveState()

    # ── Top bar ──
    canvas.setFillColor(CRIMSON)
    canvas.rect(0, H - 0.38 * inch, W, 0.38 * inch, fill=1, stroke=0)

    # Gold stripe under crimson bar
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 0.42 * inch, W, 0.04 * inch, fill=1, stroke=0)

    # Logo (if available)
    logo_h = 0.30 * inch
    if os.path.exists(LOGO_PATH):
        try:
            canvas.drawImage(LOGO_PATH, 0.45 * inch, H - 0.36 * inch,
                             height=logo_h, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # Team name in header bar
    canvas.setFillColor(CREAM)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawCentredString(W / 2, H - 0.27 * inch, "DIVA DUCKS  ·  FLAG FOOTBALL")

    # Page number top-right
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - 0.45 * inch, H - 0.27 * inch, f"Page {doc.page} of 3")

    # ── Bottom bar ──
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, W, 0.28 * inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 0.28 * inch, W, 0.03 * inch, fill=1, stroke=0)
    canvas.setFillColor(CREAM)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(W / 2, 0.09 * inch,
                             "Diva Ducks  |  CYO Flag Football  |  Confidential Coaching Document")

    canvas.restoreState()


# ── Section page title banner ────────────────────────────────────────────────
def _page_title_table(title: str) -> Table:
    t = Table([[title]], colWidths=[7.1 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), FOREST),
        ("TEXTCOLOR",     (0, 0), (-1, -1), CREAM),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 14),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, -1), 3, GOLD),
    ]))
    return t


# ── Half-page builder ────────────────────────────────────────────────────────
def _half_page(title: str, half_plan: List[Dict]) -> list:
    items: list = []
    items.append(Spacer(1, 0.42 * inch))   # clear the top chrome
    items.append(_page_title_table(title))
    items.append(Spacer(1, 0.12 * inch))

    offense_list = [p for p in half_plan if p["type"] == "Offense"]
    defense_list = [p for p in half_plan if p["type"] == "Defense"]

    if offense_list:
        items.append(Paragraph("OFFENSE", SECTION_STYLE))
        for poss in offense_list:
            items += _possession_block(poss)

    if defense_list:
        items.append(Spacer(1, 0.08 * inch))
        items.append(Paragraph("DEFENSE", SECTION_STYLE))
        for poss in defense_list:
            items += _possession_block(poss)

    return items


# ── Individual possession block ───────────────────────────────────────────────
def _possession_block(poss: Dict) -> list:
    items: list = []
    is_off   = poss["type"] == "Offense"
    hdr_bg   = FOREST if is_off else CRIMSON
    rank_txt = f"Rank: {poss['lineup_rank']:.1f}"

    # Header row
    hdr = Table([[poss["label"], rank_txt]], colWidths=[5.6 * inch, 1.5 * inch])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), hdr_bg),
        ("TEXTCOLOR",     (0, 0), (-1, -1), CREAM),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9.5),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    items.append(hdr)

    # Positions — two-column layout
    assignment = poss.get("assignment", {})
    pos_list = list(assignment.items())
    half = (len(pos_list) + 1) // 2
    col1 = pos_list[:half]
    col2 = pos_list[half:]

    rows = []
    for i in range(max(len(col1), len(col2))):
        r = []
        r += [col1[i][0], col1[i][1]] if i < len(col1) else ["", ""]
        r += [col2[i][0], col2[i][1]] if i < len(col2) else ["", ""]
        rows.append(r)

    if rows:
        pt = Table(rows, colWidths=[1.1*inch, 1.7*inch, 1.1*inch, 1.7*inch])
        row_colors = [STRIPE if i % 2 == 0 else WHITE for i in range(len(rows))]
        pt.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
            ("FONTNAME",      (0, 0), (0, -1),  "Helvetica-Bold"),
            ("FONTNAME",      (2, 0), (2, -1),  "Helvetica-Bold"),
            ("TEXTCOLOR",     (0, 0), (0, -1),  GOLD),
            ("TEXTCOLOR",     (2, 0), (2, -1),  GOLD),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS",(0, 0), (-1, -1), [STRIPE, WHITE]),
        ]))
        items.append(pt)

    # Players out
    if poss.get("players_out"):
        items.append(Paragraph(f"Out: {', '.join(poss['players_out'])}", OUT_STYLE))

    items.append(Spacer(1, 0.06 * inch))
    return items


# ── Stats / analytics page ────────────────────────────────────────────────────
def _stats_page(players, usage, qb_usage, game_plan) -> list:
    items: list = []
    items.append(Spacer(1, 0.42 * inch))
    items.append(_page_title_table("GAME ANALYTICS  &  QB PLAN"))
    items.append(Spacer(1, 0.12 * inch))

    # QB plan
    items.append(Paragraph("QB PLAN", SECTION_STYLE))
    if qb_usage:
        qb_data = [["Quarterback", "Possessions"]]
        for name, cnt in qb_usage.items():
            qb_data.append([name, str(cnt)])
        qt = Table(qb_data, colWidths=[3 * inch, 2 * inch])
        qt.setStyle(_table_style())
        items.append(qt)

    items.append(Spacer(1, 0.14 * inch))

    # Player usage
    items.append(Paragraph("PLAYER USAGE", SECTION_STYLE))
    if usage:
        udata = [["Player", "Off %", "Def %", "Total %"]]
        for name, s in sorted(usage.items(), key=lambda x: -x[1]["total_pct"]):
            udata.append([name,
                          f"{s['offense_pct']:.0f}%",
                          f"{s['defense_pct']:.0f}%",
                          f"{s['total_pct']:.0f}%"])
        ut = Table(udata, colWidths=[2.2*inch, 1.3*inch, 1.3*inch, 1.3*inch])
        ut.setStyle(_table_style())
        items.append(ut)

    items.append(Spacer(1, 0.14 * inch))

    # Strongest / weakest
    if game_plan:
        items.append(Paragraph("STRONGEST  /  WEAKEST UNITS", SECTION_STYLE))
        srt = sorted(game_plan, key=lambda x: x["lineup_rank"], reverse=True)
        strongest, weakest = srt[0], srt[-1]
        sw = [
            ["", "Label", "Rank"],
            ["💪 Strongest", strongest["label"], f"{strongest['lineup_rank']:.1f}"],
            ["🔧 Weakest",   weakest["label"],   f"{weakest['lineup_rank']:.1f}"],
        ]
        swt = Table(sw, colWidths=[1.3*inch, 4.2*inch, 1.3*inch])
        swt.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  FOREST),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  CREAM),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("BACKGROUND",    (0, 1), (-1, 1),  STRIPE),
            ("BACKGROUND",    (0, 2), (-1, 2),  colors.HexColor("#FFF0F0")),
            ("TEXTCOLOR",     (0, 1), (0, 1),   FOREST),
            ("TEXTCOLOR",     (0, 2), (0, 2),   CRIMSON),
            ("FONTNAME",      (0, 1), (0, -1),  "Helvetica-Bold"),
            ("ALIGN",         (2, 0), (2, -1),  "CENTER"),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.grey),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        items.append(swt)

    return items


# ── Shared table style ────────────────────────────────────────────────────────
def _table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  FOREST),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  CREAM),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, STRIPE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ])
