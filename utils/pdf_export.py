import io
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

GREEN = colors.HexColor("#2E7D32")
LIGHT_GREEN = colors.HexColor("#4CAF50")
RED = colors.HexColor("#C62828")
BLACK = colors.black
WHITE = colors.white
GOLD = colors.HexColor("#FFC107")
DARK_BG = colors.HexColor("#1A1F2E")

def build_pdf(game_plan: List[Dict], players: List[Dict], settings: Dict, qb_usage: Dict, usage: Dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle("Title", parent=styles["Title"], textColor=WHITE, backColor=DARK_BG, fontSize=20, alignment=TA_CENTER)
    header_style = ParagraphStyle("Header", parent=styles["Heading1"], textColor=LIGHT_GREEN, fontSize=14)
    subheader_style = ParagraphStyle("SubHeader", parent=styles["Heading2"], textColor=GOLD, fontSize=11)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], textColor=BLACK, fontSize=9)
    pos_style = ParagraphStyle("Pos", parent=styles["Normal"], textColor=BLACK, fontSize=9, fontName="Helvetica-Bold")
    
    story = []
    
    half1_plan = [p for p in game_plan if p["half"] == 1]
    half2_plan = [p for p in game_plan if p["half"] == 2]
    
    # PAGE 1: 1st Half
    story.extend(_build_half_page("1ST HALF GAME PLAN", half1_plan, body_style, header_style, subheader_style))
    
    # PAGE 2: 2nd Half
    from reportlab.platypus import PageBreak
    story.append(PageBreak())
    story.extend(_build_half_page("2ND HALF GAME PLAN", half2_plan, body_style, header_style, subheader_style))
    
    # PAGE 3: Analytics
    story.append(PageBreak())
    story.extend(_build_stats_page(players, usage, qb_usage, game_plan, body_style, header_style, subheader_style))
    
    doc.build(story, onFirstPage=_page_header_footer, onLaterPages=_page_header_footer)
    buffer.seek(0)
    return buffer.read()

def _build_header_block(title_text: str):
    from reportlab.platypus import Table, TableStyle
    header_data = [["🦆 DIVA DUCKS", title_text, "FLAG FOOTBALL"]]
    t = Table(header_data, colWidths=[2.5*inch, 3*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t

def _build_half_page(title: str, half_plan: List[Dict], body_style, header_style, subheader_style) -> list:
    items = []
    items.append(_build_header_block(title))
    items.append(Spacer(1, 0.15*inch))
    
    offense_poss = [p for p in half_plan if p["type"] == "Offense"]
    defense_poss = [p for p in half_plan if p["type"] == "Defense"]
    
    for poss in offense_poss:
        items.extend(_build_possession_block(poss, body_style))
    
    items.append(Spacer(1, 0.1*inch))
    
    for poss in defense_poss:
        items.extend(_build_possession_block(poss, body_style))
    
    return items

def _build_possession_block(poss: Dict, body_style) -> list:
    from reportlab.platypus import Table, TableStyle
    items = []
    
    label = poss["label"]
    rank = poss["lineup_rank"]
    is_offense = poss["type"] == "Offense"
    header_color = LIGHT_GREEN if is_offense else RED
    
    # Header row
    header_data = [[f"{label}", f"Rank: {rank:.1f}"]]
    ht = Table(header_data, colWidths=[6*inch, 2*inch])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), header_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    items.append(ht)
    
    # Positions
    assignment = poss.get("assignment", {})
    pos_items = list(assignment.items())
    
    # Build 2-column layout
    half = (len(pos_items) + 1) // 2
    col1 = pos_items[:half]
    col2 = pos_items[half:]
    
    rows = []
    for i in range(max(len(col1), len(col2))):
        row = []
        if i < len(col1):
            row.extend([col1[i][0], col1[i][1]])
        else:
            row.extend(["", ""])
        if i < len(col2):
            row.extend([col2[i][0], col2[i][1]])
        else:
            row.extend(["", ""])
        rows.append(row)
    
    if rows:
        pt = Table(rows, colWidths=[1.2*inch, 1.8*inch, 1.2*inch, 1.8*inch])
        pt.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), GOLD),
            ("TEXTCOLOR", (2, 0), (2, -1), GOLD),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F5")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F0F0F0")]),
        ]))
        items.append(pt)
    
    # Players out
    if poss.get("players_out"):
        out_text = f"Out: {', '.join(poss['players_out'])}"
        items.append(Paragraph(out_text, ParagraphStyle("out", fontSize=8, textColor=colors.HexColor("#666666"))))
    
    items.append(Spacer(1, 0.08*inch))
    return items

def _build_stats_page(players, usage, qb_usage, game_plan, body_style, header_style, subheader_style) -> list:
    from reportlab.platypus import Table, TableStyle, PageBreak
    items = []
    items.append(_build_header_block("GAME ANALYTICS"))
    items.append(Spacer(1, 0.15*inch))
    
    # QB Usage
    qb_label = ParagraphStyle("QL", fontSize=12, textColor=GREEN, fontName="Helvetica-Bold")
    items.append(Paragraph("QB PLAN", qb_label))
    if qb_usage:
        qb_data = [["Quarterback", "Possessions"]]
        for name, count in qb_usage.items():
            qb_data.append([name, str(count)])
        qt = Table(qb_data, colWidths=[3*inch, 2*inch])
        qt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F8FF")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        items.append(qt)
    
    items.append(Spacer(1, 0.15*inch))
    
    # Player Usage Table
    items.append(Paragraph("PLAYER USAGE", qb_label))
    if usage:
        usage_data = [["Player", "Off%", "Def%", "Total%"]]
        for name, stats in sorted(usage.items(), key=lambda x: -x[1]["total_pct"]):
            usage_data.append([
                name,
                f"{stats['offense_pct']:.0f}%",
                f"{stats['defense_pct']:.0f}%",
                f"{stats['total_pct']:.0f}%"
            ])
        ut = Table(usage_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        ut.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F8FF")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        items.append(ut)
    
    items.append(Spacer(1, 0.15*inch))
    
    # Strongest / Weakest Units
    if game_plan:
        sorted_plan = sorted(game_plan, key=lambda x: x["lineup_rank"], reverse=True)
        strongest = sorted_plan[0]
        weakest = sorted_plan[-1]
        
        sw_data = [
            ["Unit Type", "Label", "Rank"],
            ["Strongest", strongest["label"], f"{strongest['lineup_rank']:.1f}"],
            ["Weakest", weakest["label"], f"{weakest['lineup_rank']:.1f}"],
        ]
        sw_label = ParagraphStyle("SWL", fontSize=12, textColor=GREEN, fontName="Helvetica-Bold")
        items.append(Paragraph("STRONGEST / WEAKEST UNITS", sw_label))
        swt = Table(sw_data, colWidths=[1.5*inch, 4*inch, 1.5*inch])
        swt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#E8F5E9"), colors.HexColor("#FFEBEE")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        items.append(swt)
    
    return items

def _page_header_footer(canvas, doc):
    canvas.saveState()
    # Footer
    canvas.setFillColor(GREEN)
    canvas.rect(0, 0, letter[0], 0.3*inch, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(letter[0]/2, 0.1*inch, "Diva Ducks | CYO Flag Football | Confidential Coaching Document")
    canvas.drawRightString(letter[0] - 0.5*inch, 0.1*inch, f"Page {doc.page}")
    canvas.restoreState()
