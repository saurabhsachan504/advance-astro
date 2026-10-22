from datetime import datetime
from html import escape
from io import BytesIO
from math import cos, pi, sin
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .advanced import gochar_dashboard, jaimini, kundli, varshaphal, vimshottari_dasha
from .astrology import SIGNS, calculate_chart
from .config import Settings
from .nakshatra import nakshatra_studio
from .schemas import DashaRequest, GocharDashboardRequest, JaiminiRequest, KundliRequest, NakshatraRequest, PremiumReportRequest, ReportRequest, VarshaphalRequest, YogaDoshaRequest
from .yoga import yoga_dosha_analyzer


INK = HexColor("#17243a")
COPPER = HexColor("#b95c29")
PAPER = HexColor("#fffaf2")
MIST = HexColor("#f5eadc")
MUTED = HexColor("#52617a")
MIDNIGHT = HexColor("#0d1628")
GOLD = HexColor("#edbd69")
CREAM = HexColor("#fff4df")
DEVANAGARI_FONT = Path("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf")


def _font_name(language: str) -> str:
    if language == "hi" and DEVANAGARI_FONT.exists():
        name = "NotoDevanagari"
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(DEVANAGARI_FONT)))
        return name
    return "Helvetica"


def _localisation(language: str) -> dict[str, str]:
    if language == "hi":
        return {"private": "निजी ज्योतिष रिपोर्ट", "profile": "प्रोफ़ाइल", "generated": "बनाया गया", "birth": "जन्म विवरण", "chart": "कुंडली सारांश", "planets": "ग्रह स्थिति", "gochar": "व्यक्तिगत गोचर डैशबोर्ड", "dasha": "विंशोत्तरी दशा", "jaimini": "जैमिनी सारांश", "varshaphal": "वर्षफल सारांश", "notice": "यह रिपोर्ट गणना किया हुआ खगोलीय डेटा दिखाती है। इसे निश्चित भविष्यवाणी, चिकित्सा, कानूनी या वित्तीय सलाह न समझें।"}
    return {"private": "Private astrology report", "profile": "Profile", "generated": "Generated", "birth": "Birth details", "chart": "Kundli snapshot", "planets": "Planetary positions", "gochar": "Personal Gochar dashboard", "dasha": "Vimshottari Dasha", "jaimini": "Jaimini snapshot", "varshaphal": "Varshaphal snapshot", "notice": "This report shows calculated astronomical data. It is not a guaranteed forecast or medical, legal, or financial advice."}


class KundliWheel(Flowable):
    """A compact, label-first sidereal chart wheel for the PDF cover."""

    def __init__(self, bodies: list[dict], width: float = 122 * mm, height: float = 122 * mm):
        super().__init__()
        self.bodies, self.width, self.height = bodies, width, height
        self.hAlign = "CENTER"

    def draw(self) -> None:
        canvas = self.canv
        cx, cy = self.width / 2, self.height / 2
        outer, inner = min(self.width, self.height) * .45, min(self.width, self.height) * .27
        canvas.setFillColor(PAPER); canvas.setStrokeColor(COPPER); canvas.setLineWidth(.9); canvas.circle(cx, cy, outer, stroke=1, fill=1)
        canvas.setFillColor(HexColor("#fff4df")); canvas.setStrokeColor(HexColor("#c99a62")); canvas.circle(cx, cy, inner, stroke=1, fill=1)
        for index, sign in enumerate(SIGNS):
            angle = (index * 30 - 90) * pi / 180
            canvas.setStrokeColor(HexColor("#d9c2a6")); canvas.line(cx, cy, cx + cos(angle) * outer, cy + sin(angle) * outer)
            canvas.setFillColor(COPPER); canvas.setFont("Helvetica-Bold", 5.8)
            canvas.drawCentredString(cx + cos(angle + pi / 12) * (outer * .82), cy + sin(angle + pi / 12) * (outer * .82), sign[:3])
        abbreviations = {"Ascendant": "Asc", "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"}
        by_sign: dict[str, list[str]] = {}
        for body in self.bodies: by_sign.setdefault(str(body["sign"]), []).append(abbreviations.get(str(body["name"]), str(body["name"])[:2]))
        canvas.setFillColor(INK); canvas.setFont("Helvetica", 6.5)
        for index, sign in enumerate(SIGNS):
            items = " ".join(by_sign.get(sign, []))
            if items:
                angle = (index * 30 - 75) * pi / 180
                canvas.drawCentredString(cx + cos(angle) * (outer * .51), cy + sin(angle) * (outer * .51), items)
        canvas.setFillColor(INK); canvas.setFont("Helvetica-Bold", 9); canvas.drawCentredString(cx, cy + 3, "VEDA / OS")
        canvas.setFillColor(MUTED); canvas.setFont("Helvetica", 5.8); canvas.drawCentredString(cx, cy - 8, "LAHIRI SIDEREAL")


def _styles(language: str) -> dict[str, ParagraphStyle]:
    base, family = getSampleStyleSheet(), _font_name(language)
    return {
        "title": ParagraphStyle("premium-title", parent=base["Title"], fontName=family if language == "hi" else "Helvetica-Bold", textColor=INK, fontSize=24, leading=30, spaceAfter=5),
        "eyebrow": ParagraphStyle("premium-eyebrow", parent=base["BodyText"], fontName=family, textColor=COPPER, fontSize=8, leading=11, spaceAfter=6),
        "body": ParagraphStyle("premium-body", parent=base["BodyText"], fontName=family, textColor=INK, fontSize=9, leading=14),
        "muted": ParagraphStyle("premium-muted", parent=base["BodyText"], fontName=family, textColor=MUTED, fontSize=8, leading=12),
        "section": ParagraphStyle("premium-section", parent=base["Heading2"], fontName=family if language == "hi" else "Helvetica-Bold", textColor=INK, backColor=MIST, borderColor=HexColor("#d8a55a"), borderWidth=.55, borderPadding=(7, 7, 6), fontSize=15, leading=20, spaceBefore=7, spaceAfter=9),
        "cover_title": ParagraphStyle("premium-cover-title", parent=base["Title"], fontName=family if language == "hi" else "Helvetica-Bold", textColor=CREAM, fontSize=29, leading=35, spaceAfter=7),
        "cover_eyebrow": ParagraphStyle("premium-cover-eyebrow", parent=base["BodyText"], fontName=family, textColor=GOLD, fontSize=8, leading=11, spaceAfter=7),
        "cover_body": ParagraphStyle("premium-cover-body", parent=base["BodyText"], fontName=family, textColor=HexColor("#d7ddeb"), fontSize=9, leading=15),
    }


def _table(rows: list[list[str]], widths: list[float], language: str = "en") -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    family = _font_name(language)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), MIDNIGHT), ("TEXTCOLOR", (0, 0), (-1, 0), CREAM), ("TEXTCOLOR", (0, 1), (-1, -1), INK), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, MIST]), ("GRID", (0, 0), (-1, -1), .28, HexColor("#d7c5ad")), ("LINEBELOW", (0, 0), (-1, 0), 1, GOLD), ("FONTNAME", (0, 0), (-1, 0), family), ("FONTNAME", (0, 1), (-1, -1), family), ("FONTSIZE", (0, 0), (-1, 0), 7.6), ("FONTSIZE", (0, 1), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7)]))
    return table


def _page_decor(canvas, document) -> None:
    canvas.saveState(); canvas.setFillColor(MIDNIGHT); canvas.rect(0, A4[1] - 14 * mm, A4[0], 14 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(GOLD); canvas.setLineWidth(.45); canvas.line(document.leftMargin, A4[1] - 14 * mm, A4[0] - document.rightMargin, A4[1] - 14 * mm)
    canvas.setFillColor(CREAM); canvas.setFont("Helvetica-Bold", 7); canvas.drawString(document.leftMargin, A4[1] - 9.5 * mm, "VEDA / OS  |  PRIVATE ASTROLOGY LAB")
    canvas.setStrokeColor(HexColor("#d6c1a7")); canvas.line(document.leftMargin, 14 * mm, A4[0] - document.rightMargin, 14 * mm)
    canvas.setFillColor(COPPER); canvas.setFont("Helvetica-Bold", 7); canvas.drawString(document.leftMargin, 9.5 * mm, "Lahiri sidereal  |  Swiss Ephemeris")
    canvas.setFillColor(MUTED); canvas.setFont("Helvetica", 7); canvas.drawRightString(A4[0] - document.rightMargin, 9.5 * mm, f"Page {document.page}"); canvas.restoreState()


def _cover_decor(canvas, document) -> None:
    canvas.saveState(); canvas.setFillColor(MIDNIGHT); canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    canvas.setStrokeColor(HexColor("#27405e")); canvas.setLineWidth(.6)
    for offset in (42, 66, 92):
        canvas.circle(A4[0] - 25 * mm, A4[1] - 24 * mm, offset * mm, stroke=1, fill=0)
    canvas.setFillColor(GOLD)
    for x, y, radius in ((27, 262, 1.4), (45, 243, .8), (169, 255, 1), (177, 102, .9), (32, 71, .8), (157, 59, 1.1)):
        canvas.circle(x * mm, y * mm, radius * mm, stroke=0, fill=1)
    canvas.setStrokeColor(HexColor("#665036")); canvas.line(18 * mm, 15 * mm, A4[0] - 18 * mm, 15 * mm)
    canvas.setFillColor(GOLD); canvas.setFont("Helvetica-Bold", 8); canvas.drawString(18 * mm, 10 * mm, "VEDA / OS")
    canvas.setFillColor(HexColor("#aab8cd")); canvas.setFont("Helvetica", 7); canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, "PRIVATE COSMIC DOSSIER")
    canvas.restoreState()


def chart_report(request: ReportRequest, settings: Settings) -> bytes:
    """Create the existing compact factual report for backwards compatibility."""
    chart, output = calculate_chart(request, settings), BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = _styles("en")
    story = [Paragraph(escape(request.report_title), styles["title"]), Paragraph("Private astronomical chart facts - Swiss Ephemeris / Lahiri sidereal", styles["muted"]), Paragraph(f"Ascendant: <b>{chart.ascendant.sign}</b> - {chart.ascendant.longitude:.2f} degrees - {chart.ascendant.nakshatra}", styles["body"]), Spacer(1, 8 * mm)]
    rows = [["Body", "Sign", "Longitude", "Nakshatra"]] + [[item.name, item.sign, f"{item.longitude:.2f} degrees", item.nakshatra] for item in chart.planets]
    story += [_table(rows, [34 * mm, 36 * mm, 40 * mm, 54 * mm]), Spacer(1, 8 * mm), Paragraph(_localisation("en")["notice"], styles["muted"])]
    document.build(story, onFirstPage=_page_decor, onLaterPages=_page_decor)
    return output.getvalue()


def premium_report(request: PremiumReportRequest, settings: Settings) -> bytes:
    """Build a factual, branded report from the app's deterministic engines."""
    labels, styles = _localisation(request.language), _styles(request.language)
    labels.update({
        "nakshatra": "नक्षत्र एवं पाद" if request.language == "hi" else "Nakshatra & Pada",
        "yoga_dosha": "योग एवं दोष विश्लेषण" if request.language == "hi" else "Yoga & Dosha analysis",
        "yoga": "योग संकेत" if request.language == "hi" else "Yoga signals",
        "dosha": "दोष जाँच" if request.language == "hi" else "Dosha screening",
    })
    base = request.model_dump(exclude={"report_title", "profile_name", "language", "gochar_range_days", "varshaphal_year"})
    chart = calculate_chart(request, settings)
    kundli_data = kundli(KundliRequest(**base), settings)
    gochar = gochar_dashboard(GocharDashboardRequest(**base, range_days=request.gochar_range_days), settings)
    dasha = vimshottari_dasha(DashaRequest(**base, years=20), settings)
    jaimini_data = jaimini(JaiminiRequest(**base, years=72), settings)
    varsha = varshaphal(VarshaphalRequest(**base, year=request.varshaphal_year or datetime.now().year), settings)
    nakshatra = nakshatra_studio(NakshatraRequest(**base), settings)
    yoga_dosha = yoga_dosha_analyzer(YogaDoshaRequest(**base), settings)
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm, bottomMargin=18 * mm, title=request.report_title, author="VEDA / OS")
    story = [Paragraph(labels["private"].upper(), styles["cover_eyebrow"]), Paragraph(escape(request.report_title), styles["cover_title"]), Paragraph(f"{labels['profile']}: <b>{escape(request.profile_name)}</b><br/>{labels['generated']}: {datetime.now().strftime('%d %b %Y, %H:%M')}<br/>{labels['birth']}: {request.birth_datetime.strftime('%d %b %Y, %H:%M')} - {escape(request.timezone)}", styles["cover_body"]), Spacer(1, 8 * mm), KundliWheel(kundli_data["divisional_charts"]["D1"]), Spacer(1, 4 * mm), PageBreak(), Paragraph(labels["chart"], styles["section"]), Paragraph(f"Ascendant: <b>{chart.ascendant.sign}</b> - {chart.ascendant.longitude:.2f} degrees - {chart.ascendant.nakshatra}", styles["body"]), Spacer(1, 4 * mm)]
    planet_rows = [["Body", "Sign", "House", "Longitude"]] + [[body["name"], body["sign"], str(body.get("house", "-")), f"{float(body['longitude']):.2f} degrees"] for body in kundli_data["bodies"]]
    story += [_table(planet_rows, [35 * mm, 42 * mm, 30 * mm, 50 * mm], request.language), PageBreak(), Paragraph(labels["nakshatra"], styles["section"])]
    moon = nakshatra["moon"]
    story += [Paragraph(f"Moon: <b>{moon['nakshatra']}</b> - Pada {moon['pada']} - {moon['lord']} - {moon['deity']}", styles["body"]), Spacer(1, 4 * mm)]
    nakshatra_rows = [["Planet", "Sign", "Nakshatra", "Pada", "Lord", "Deity"]] + [[item["planet"], item["sign"], item["nakshatra"], str(item["pada"]), item["lord"], item["deity"]] for item in nakshatra["planets"]]
    story += [_table(nakshatra_rows, [25 * mm, 27 * mm, 31 * mm, 17 * mm, 24 * mm, 30 * mm], request.language), Spacer(1, 7 * mm), Paragraph(labels["yoga_dosha"], styles["section"])]
    for group, label in (("yogas", labels["yoga"]), ("doshas", labels["dosha"])):
        rows = yoga_dosha[group]
        story.append(Paragraph(label, styles["eyebrow"]))
        if rows:
            for item in rows:
                story += [Paragraph(f"<b>{escape(item['name'])}</b> - {escape(item['status'])}<br/>{escape(item['rule'])}", styles["body"]), Spacer(1, 2 * mm)]
        else:
            story.append(Paragraph("No configured result was detected in this compact rule set.", styles["muted"]))
    story += [Spacer(1, 4 * mm), Paragraph(escape(yoga_dosha["notice"]), styles["muted"]), PageBreak(), Paragraph(labels["gochar"], styles["section"])]
    current, sade = gochar["current"], gochar["current"]["sade_sati"]
    retrogrades = ", ".join(item["name"] for item in gochar["retrograde_planets"]) or "None"
    story += [Paragraph(f"Sade Sati: <b>{sade['phase']}</b> - Natal Moon {sade['natal_moon_sign']}; transit Saturn {sade['transit_saturn_sign']}.<br/>Retrogrades now: <b>{retrogrades}</b>.", styles["body"]), Spacer(1, 4 * mm)]
    daily_rows = [["Date", "Moon", "House", "Sade Sati"]] + [[day["date"], day["moon_sign"], str(day["moon_house_from_lagna"]), day["sade_sati_phase"]] for day in gochar["daily_overview"]]
    story += [_table(daily_rows, [35 * mm, 42 * mm, 28 * mm, 52 * mm], request.language), Spacer(1, 6 * mm), Paragraph("Upcoming sign changes", styles["section"])]
    ingress_rows = [["Planet", "From", "To", "Detected local time"]] + [[event["planet"], event["from_sign"], event["to_sign"], event["detected_local_datetime"][:16].replace("T", " ")] for event in gochar["upcoming_ingresses"][:16]]
    story += [_table(ingress_rows, [30 * mm, 36 * mm, 36 * mm, 55 * mm], request.language), PageBreak(), Paragraph(labels["dasha"], styles["section"])]
    dasha_rows = [["Maha Dasha", "Start", "End"]] + [[period["lord"], period["start"][:10], period["end"][:10]] for period in dasha["periods"]]
    story += [_table(dasha_rows, [48 * mm, 53 * mm, 53 * mm], request.language), Spacer(1, 7 * mm), Paragraph(labels["jaimini"], styles["section"])]
    karaka_rows = [["Karaka", "Planet", "Sign"]] + [[item["karaka"], item["planet"], item["sign"]] for item in jaimini_data["chara_karakas"]]
    story += [_table(karaka_rows, [55 * mm, 52 * mm, 47 * mm], request.language), Spacer(1, 7 * mm), Paragraph(labels["varshaphal"], styles["section"]), Paragraph(f"Year: <b>{varsha['year']}</b><br/>Varsha Pravesh ascendant: <b>{varsha['varsha_pravesh']['ascendant_sign']}</b><br/>Muntha: <b>{varsha['muntha']['sign']}</b> - {varsha['muntha']['lord']}<br/>Varshesha: <b>{varsha['varshesha']['planet']}</b>", styles["body"]), Spacer(1, 8 * mm), Paragraph(labels["notice"], styles["muted"])]
    document.build(story, onFirstPage=_cover_decor, onLaterPages=_page_decor)
    return output.getvalue()
