"""
PDF export — exactly 3 pages, Diva Ducks branded.
Colors mirror the logo: Crimson, Forest Green, Gold, Dark, Cream.

Page 1: 1st Half Game Plan
Page 2: 2nd Half Game Plan
Page 3: Analytics — player usage bar chart, offense/defense workload chart,
         QB plan, lineup rank summary, bench pattern summary
"""
import io, os
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

# ── Logo-matched palette ────────────────────────────────────────────────────
CRIMSON      = colors.HexColor("#B31B1B")
CRIMSON_DARK = colors.HexColor("#7B1010")
FOREST       = colors.HexColor("#1A5C1A")
FOREST_LIGHT = colors.HexColor("#2E8B2E")
GOLD         = colors.HexColor("#C9A84C")
DARK         = colors.HexColor("#111111")
CREAM        = colors.HexColor("#F2E8C8")
OFF_WHITE    = colors.HexColor("#F5F0E8")
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

SECTION_STYLE = _s("Section", fontName="Helvetica-Bold", fontSize=11,
                   textColor=FOREST, spaceAfter=3)
BODY_STYLE    = _s("Body",    fontName="Helvetica",      fontSize=8.5, textColor=DARK)
OUT_STYLE     = _s("Out",     fontName="Helvetica",      fontSize=7.5,
                   textColor=colors.HexColor("#555555"))
CAPTION_STYLE = _s("Caption", fontName="Helvetica-Oblique", fontSize=7.5,
                   textColor=colors.HexColor("#444444"), spaceAfter=4)


# ── Public entry point ───────────────────────────────────────────────────────
def build_pdf(
    game_plan: List[Dict],
    players: List[Dict],
    settings: Dict,
    qb_usage: Dict,
    usage: Dict,
    bench_patterns: Optional[Dict] = None,
    version_label: str = "",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.45 * inch, leftMargin=0.45 * inch,
        topMargin=0.45 * inch,  bottomMargin=0.45 * inch,
    )

    half1 = [p for p in game_plan if p["half"] == 1]
    half2 = [p for p in game_plan if p["half"] == 2]

    story = []
    story += _half_page("1ST HALF GAME PLAN", half1, version_label)
    story += [PageBreak()]
    story += _half_page("2ND HALF GAME PLAN", half2, version_label)
    story += [PageBreak()]
    story += _stats_page(players, usage, qb_usage, game_plan, bench_patterns, version_label)

    doc.build(
        story,
        onFirstPage=_draw_page_chrome,
        onLaterPages=_draw_page_chrome,
    )

    buffer.seek(0)
    return buffer.read()


# ── Page header / footer ─────────────────────────────────────────────────────
def _draw_page_chrome(canvas, doc):
    W, H = letter
    canvas.saveState()

    # Top bar — crimson
    canvas.setFillColor(CRIMSON)
    canvas.rect(0, H - 0.38 * inch, W, 0.38 * inch, fill=1, stroke=0)

    # Gold stripe under crimson bar
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 0.42 * inch, W, 0.04 * inch, fill=1, stroke=0)

    # Logo
    if os.path.exists(LOGO_PATH):
        try:
            canvas.drawImage(
                LOGO_PATH, 0.45 * inch, H - 0.36 * inch,
                height=0.30 * inch, preserveAspectRatio=True, mask="auto",
            )
        except Exception:
            pass

    # Team name
    canvas.setFillColor(CREAM)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawCentredString(W / 2, H - 0.27 * inch, "DIVA DUCKS  ·  FLAG FOOTBALL")

    # Page number
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - 0.45 * inch, H - 0.27 * inch, f"Page {doc.page} of 3")

    # Bottom bar
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, W, 0.28 * inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 0.28 * inch, W, 0.03 * inch, fill=1, stroke=0)
    canvas.setFillColor(CREAM)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(W / 2, 0.09 * inch,
                             "Diva Ducks  |  CYO Flag Football  |  Confidential Coaching Document")

    canvas.restoreState()


# ── Page title banner ────────────────────────────────────────────────────────
def _page_title_table(title: str, version_label: str = "") -> Table:
    label_text = f"  [{version_label}]" if version_label else ""
    full_title = f"{title}{label_text}"
    t = Table([[full_title]], colWidths=[7.1 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), FOREST),
        ("TEXTCOLOR",     (0, 0), (-1, -1), CREAM),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 14),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW",     (0, 0), (-1, -1), 3, GOLD),
    ]))
    return t


# ── Half-page builder ────────────────────────────────────────────────────────
def _half_page(title: str, half_plan: List[Dict], version_label: str = "") -> list:
    items: list = []
    items.append(Spacer(1, 0.42 * inch))
    items.append(_page_title_table(title, version_label))
    items.append(Spacer(1, 0.10 * inch))

    # Iterate in live sequence order (already interleaved O/D)
    for poss in half_plan:
        items += _possession_block(poss)

    return items


# ── Possession block ──────────────────────────────────────────────────────────
def _possession_block(poss: Dict) -> list:
    items: list = []
    is_off = poss["type"] == "Offense"
    hdr_bg = FOREST if is_off else CRIMSON
    rank_label = poss.get("rank_label", "")
    rank_txt = f"{rank_label}  ({poss['lineup_rank']:.1f})"

    hdr = Table([[poss["label"], rank_txt]], colWidths=[5.4 * inch, 1.7 * inch])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), hdr_bg),
        ("TEXTCOLOR",     (0, 0), (-1, -1), CREAM),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
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
    half_n = (len(pos_list) + 1) // 2
    col1 = pos_list[:half_n]
    col2 = pos_list[half_n:]

    rows = []
    for i in range(max(len(col1), len(col2))):
        r = []
        r += [col1[i][0], col1[i][1]] if i < len(col1) else ["", ""]
        r += [col2[i][0], col2[i][1]] if i < len(col2) else ["", ""]
        rows.append(r)

    if rows:
        pt = Table(rows, colWidths=[1.0 * inch, 1.7 * inch, 1.0 * inch, 1.7 * inch])
        pt.setStyle(TableStyle([
            ("FONTNAME",       (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",       (0, 0), (-1, -1), 8),
            ("FONTNAME",       (0, 0), (0, -1),  "Helvetica-Bold"),
            ("FONTNAME",       (2, 0), (2, -1),  "Helvetica-Bold"),
            ("TEXTCOLOR",      (0, 0), (0, -1),  GOLD),
            ("TEXTCOLOR",      (2, 0), (2, -1),  GOLD),
            ("TOPPADDING",     (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 2),
            ("LEFTPADDING",    (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [STRIPE, WHITE]),
        ]))
        items.append(pt)

    if poss.get("players_out"):
        items.append(Paragraph(f"Out: {', '.join(poss['players_out'])}", OUT_STYLE))
    items.append(Spacer(1, 0.055 * inch))
    return items


# ── Stats / analytics page ────────────────────────────────────────────────────
def _stats_page(
    players, usage, qb_usage, game_plan,
    bench_patterns: Optional[Dict] = None,
    version_label: str = "",
) -> list:
    items: list = []
    items.append(Spacer(1, 0.42 * inch))
    items.append(_page_title_table("GAME ANALYTICS", version_label))
    items.append(Spacer(1, 0.10 * inch))

    # ── QB plan table ────────────────────────────────────────────────────────
    items.append(Paragraph("QB PLAN", SECTION_STYLE))
    if qb_usage:
        qb_data = [["Quarterback", "Possessions"]]
        for name, cnt in qb_usage.items():
            qb_data.append([name, str(cnt)])
        qt = Table(qb_data, colWidths=[3 * inch, 2 * inch])
        qt.setStyle(_table_style())
        items.append(qt)
    items.append(Spacer(1, 0.10 * inch))

    # ── Player usage chart (bar) ─────────────────────────────────────────────
    if usage:
        items.append(Paragraph("PLAYER USAGE", SECTION_STYLE))
        usage_drawing = _usage_bar_drawing(usage)
        if usage_drawing:
            items.append(usage_drawing)
        items.append(Spacer(1, 0.08 * inch))

        # Usage table underneath
        udata = [["Player", "Off %", "Def %", "Total %"]]
        for name, s in sorted(usage.items(), key=lambda x: -x[1]["total_pct"]):
            udata.append([name,
                          f"{s['offense_pct']:.0f}%",
                          f"{s['defense_pct']:.0f}%",
                          f"{s['total_pct']:.0f}%"])
        ut = Table(udata, colWidths=[2.0 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch])
        ut.setStyle(_table_style())
        items.append(ut)
        items.append(Spacer(1, 0.10 * inch))

    # ── Lineup rank bar chart ────────────────────────────────────────────────
    if game_plan:
        items.append(Paragraph("LINEUP RANK BY POSSESSION", SECTION_STYLE))
        rank_drawing = _lineup_rank_drawing(game_plan)
        if rank_drawing:
            items.append(rank_drawing)
        items.append(Spacer(1, 0.08 * inch))

    # ── Bench pattern summary ────────────────────────────────────────────────
    if bench_patterns:
        items.append(Paragraph("BENCH LOAD SUMMARY", SECTION_STYLE))
        bench_data = [["Player", "Times Benched", "Bench %", "Max Streak", "Violations"]]
        for name, data in sorted(bench_patterns.items(),
                                  key=lambda x: -x[1]["total_bench"]):
            viol = data["consecutive_violations"]
            viol_str = f"⚠  {viol}" if viol else "✓  0"
            bench_data.append([
                name,
                str(data["total_bench"]),
                f"{data['bench_pct']:.0f}%",
                str(data["max_consecutive_bench"]),
                viol_str,
            ])
        bt = Table(bench_data, colWidths=[1.8*inch, 1.3*inch, 1.0*inch, 1.0*inch, 1.0*inch])
        bt.setStyle(_table_style())
        items.append(bt)

    return items


# ── ReportLab native bar chart — player usage ────────────────────────────────
def _usage_bar_drawing(usage: Dict) -> Optional[Drawing]:
    if not usage:
        return None
    names = list(usage.keys())
    off_pcts = [usage[n]["offense_pct"] for n in names]
    def_pcts = [usage[n]["defense_pct"] for n in names]
    n = len(names)

    W, H = 7.1 * inch, 1.5 * inch
    d = Drawing(W, H)

    bar_w = (W - 1.0 * inch) / max(n, 1)
    chart_x = 0.5 * inch
    chart_y = 0.25 * inch
    chart_h = H - 0.5 * inch
    max_val = max(max(off_pcts + def_pcts, default=1), 1)

    for i, name in enumerate(names):
        x = chart_x + i * bar_w
        # Offense bar (left half of slot)
        off_h = off_pcts[i] / max_val * chart_h
        d.add(Rect(x + 1, chart_y, bar_w * 0.42, off_h,
                   fillColor=FOREST_LIGHT, strokeColor=None))
        # Defense bar (right half)
        def_h = def_pcts[i] / max_val * chart_h
        d.add(Rect(x + bar_w * 0.46, chart_y, bar_w * 0.42, def_h,
                   fillColor=CRIMSON, strokeColor=None))
        # Player name label
        short = name[:6]
        d.add(String(x + bar_w / 2, chart_y - 10, short,
                     fontSize=6.5, fillColor=DARK, textAnchor="middle"))

    # Legend
    d.add(Rect(chart_x, H - 12, 10, 8, fillColor=FOREST_LIGHT, strokeColor=None))
    d.add(String(chart_x + 13, H - 12, "Offense %", fontSize=7, fillColor=DARK))
    d.add(Rect(chart_x + 75, H - 12, 10, 8, fillColor=CRIMSON, strokeColor=None))
    d.add(String(chart_x + 88, H - 12, "Defense %", fontSize=7, fillColor=DARK))

    return d


# ── ReportLab native bar chart — lineup rank ─────────────────────────────────
def _lineup_rank_drawing(game_plan: List[Dict]) -> Optional[Drawing]:
    if not game_plan:
        return None
    n = len(game_plan)
    W, H = 7.1 * inch, 1.3 * inch
    d = Drawing(W, H)

    chart_x = 0.2 * inch
    chart_y = 0.2 * inch
    chart_h = H - 0.35 * inch
    bar_w = (W - 0.4 * inch) / max(n, 1)
    max_rank = max(p["lineup_rank"] for p in game_plan) or 10.0

    for i, poss in enumerate(game_plan):
        x = chart_x + i * bar_w
        bar_h = poss["lineup_rank"] / max_rank * chart_h
        fc = FOREST_LIGHT if poss["type"] == "Offense" else CRIMSON
        d.add(Rect(x + 1, chart_y, bar_w - 2, bar_h, fillColor=fc, strokeColor=None))

    # Legend
    d.add(Rect(chart_x, H - 10, 8, 7, fillColor=FOREST_LIGHT, strokeColor=None))
    d.add(String(chart_x + 11, H - 10, "Offense", fontSize=6.5, fillColor=DARK))
    d.add(Rect(chart_x + 65, H - 10, 8, 7, fillColor=CRIMSON, strokeColor=None))
    d.add(String(chart_x + 76, H - 10, "Defense", fontSize=6.5, fillColor=DARK))

    return d


# ── Shared table style ────────────────────────────────────────────────────────
def _table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  FOREST),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  CREAM),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, STRIPE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ])
