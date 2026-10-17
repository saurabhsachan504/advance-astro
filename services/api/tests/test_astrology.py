from datetime import datetime
from app.astrology import calculate_chart, calculate_multi_system
from app.advanced import BAV_EXPECTED_TOTALS, gochar, jaimini, kundli, prashna, strengths, vimshottari_dasha
from app.config import Settings
from app.schemas import ChartRequest, DashaRequest, JaiminiRequest, KundliRequest, PrashnaRequest, TransitRequest

def test_chart_has_all_v1_bodies_and_valid_longitudes(tmp_path):
    request = ChartRequest(birth_datetime=datetime(1995, 8, 15, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090)
    chart = calculate_chart(request, Settings(ephemeris_path=tmp_path))
    assert chart.ascendant.name == "Ascendant"
    assert {planet.name for planet in chart.planets} == {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"}
    assert all(0 <= planet.longitude < 360 for planet in chart.planets)
    rahu = next(planet.longitude for planet in chart.planets if planet.name == "Rahu")
    ketu = next(planet.longitude for planet in chart.planets if planet.name == "Ketu")
    assert abs(((ketu - rahu) % 360) - 180) < 0.0001


def test_multi_system_returns_all_four_calculation_frameworks(tmp_path):
    request = ChartRequest(birth_datetime=datetime(1995, 8, 15, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090)
    result = calculate_multi_system(request, Settings(ephemeris_path=tmp_path))
    assert set(("vedic_parashari", "kp", "numerology", "western")).issubset(result)
    assert len(result["kp"]["cusps"]) == 12
    assert result["numerology"]["life_path"] == 11
    assert result["western"]["zodiac"] == "Tropical"


def test_dasha_and_kundli_return_structured_deterministic_data(tmp_path):
    common = dict(birth_datetime=datetime(1995, 8, 15, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090)
    dasha = vimshottari_dasha(DashaRequest(**common, years=5), Settings(ephemeris_path=tmp_path))
    chart = kundli(KundliRequest(**common), Settings(ephemeris_path=tmp_path))
    assert dasha["periods"]
    assert len(dasha["periods"][0]["antardashas"]) == 9
    assert len(chart["houses"]) == 12
    assert len(chart["divisional_charts"]["D9_navamsa"]) == 9


def test_gochar_strengths_and_prashna_return_facts(tmp_path):
    settings = Settings(ephemeris_path=tmp_path)
    common = dict(birth_datetime=datetime(1995, 8, 15, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090)
    transit = gochar(TransitRequest(**common), settings)["planets"]
    assert transit
    assert all("speed_longitude_deg_day" in planet for planet in transit)
    assert any(abs(planet["speed_longitude_deg_day"]) > 0 for planet in transit)
    strength = strengths(ChartRequest(**common), settings)
    assert len(strength["shadbala_components"]) == 7
    assert len(strength["sarvashtakavarga"]["houses_from_lagna"]) == 12
    assert set(strength["bhinna_ashtakavarga"]) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert {planet: values["total"] for planet, values in strength["bhinna_ashtakavarga"].items()} == BAV_EXPECTED_TOTALS
    assert strength["sarvashtakavarga"]["total"] == 337
    assert strength["checksums"]["valid"] is True
    assert any(row["components"]["cheshta_motion_index"] > 0 for row in strength["shadbala_components"])
    question = PrashnaRequest(question="What should I focus on?", question_datetime=datetime(2026, 10, 17, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090)
    assert prashna(question, settings)["lagna"]["name"] == "Ascendant"


def test_jaimini_engine_returns_transparent_rule_pack(tmp_path):
    request = JaiminiRequest(birth_datetime=datetime(1995, 8, 15, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090, years=72)
    result = jaimini(request, Settings(ephemeris_path=tmp_path))
    assert [row["karaka"] for row in result["chara_karakas"]] == ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    assert len(result["chara_karakas"]) == 7
    assert result["karakamsha"]["atmakaraka"] == result["chara_karakas"][0]["planet"]
    assert result["arudha_lagna"]["sign"] in {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"}
    assert result["jaimini_aspects"]
    assert result["chara_dasha_periods"]
    assert "Seven-karaka" in result["rule_pack"]["chara_karakas"]

