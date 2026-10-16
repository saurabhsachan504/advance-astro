from datetime import datetime
from app.astrology import calculate_chart, calculate_multi_system
from app.advanced import kundli, vimshottari_dasha
from app.config import Settings
from app.schemas import ChartRequest, DashaRequest, KundliRequest

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

