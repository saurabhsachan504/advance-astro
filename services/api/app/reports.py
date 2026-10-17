from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .astrology import calculate_chart
from .config import Settings
from .schemas import ReportRequest


def chart_report(request: ReportRequest, settings: Settings) -> bytes:
    """Create a compact, factual chart report; no AI interpretation is included."""
    chart = calculate_chart(request, settings)
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("astro-title", parent=styles["Title"], textColor=HexColor("#18253d"), fontName="Helvetica-Bold", fontSize=22, leading=28, spaceAfter=8)
    subtitle = ParagraphStyle("astro-subtitle", parent=styles["BodyText"], textColor=HexColor("#6a583e"), fontSize=9, leading=14, spaceAfter=14)
    story = [Paragraph(request.report_title, title), Paragraph("Private astronomical chart facts - Swiss Ephemeris / Lahiri sidereal", subtitle)]
    story.append(Paragraph(f"Ascendant: <b>{chart.ascendant.sign}</b> - {chart.ascendant.longitude:.2f} degrees - {chart.ascendant.nakshatra}", styles["BodyText"]))
    story.append(Spacer(1, 8 * mm))
    rows = [["Body", "Sign", "Longitude", "Nakshatra"]] + [[item.name, item.sign, f"{item.longitude:.2f} degrees", item.nakshatra] for item in chart.planets]
    table = Table(rows, colWidths=[34 * mm, 36 * mm, 40 * mm, 54 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#192740")), ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#fff7e8")), ("TEXTCOLOR", (0, 1), (-1, -1), HexColor("#24314a")), ("GRID", (0, 0), (-1, -1), 0.35, HexColor("#cbbd9b")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#fffdf8"), HexColor("#f7f0e4")]), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story += [table, Spacer(1, 8 * mm), Paragraph("This report contains deterministic chart positions only. Astrology is spiritual guidance and not medical, legal, financial, or guaranteed-future advice.", subtitle)]
    document.build(story)
    return output.getvalue()
