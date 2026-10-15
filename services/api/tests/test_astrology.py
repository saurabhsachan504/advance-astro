from datetime import datetime
from app.astrology import calculate_chart
from app.config import Settings
from app.schemas import ChartRequest

def test_chart_has_all_v1_bodies_and_valid_longitudes(tmp_path):
    request = ChartRequest(birth_datetime=datetime(1995, 8, 15, 10, 30), timezone="Asia/Kolkata", latitude=28.6139, longitude=77.2090)
    chart = calculate_chart(request, Settings(ephemeris_path=tmp_path))
    assert chart.ascendant.name == "Ascendant"
    assert {planet.name for planet in chart.planets} == {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"}
    assert all(0 <= planet.longitude < 360 for planet in chart.planets)
    rahu = next(planet.longitude for planet in chart.planets if planet.name == "Rahu")
    ketu = next(planet.longitude for planet in chart.planets if planet.name == "Ketu")
    assert abs(((ketu - rahu) % 360) - 180) < 0.0001

