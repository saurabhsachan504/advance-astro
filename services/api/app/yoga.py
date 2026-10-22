import swisseph as swe

from .astrology import _positions, _utc_and_jd
from .config import Settings
from .schemas import YogaDoshaRequest


CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def _distance(first: float, second: float) -> float:
    return min((first - second) % 360, (second - first) % 360)


def _same_node_half(planets: list[float], rahu: float) -> bool:
    """Return whether all seven classical planets sit on either Rahu-Ketu semicircle."""
    from_rahu = [(longitude - rahu) % 360 for longitude in planets]
    return all(longitude <= 180 for longitude in from_rahu) or all(longitude >= 180 for longitude in from_rahu)


def yoga_dosha_analyzer(request: YogaDoshaRequest, settings: Settings) -> dict:
    _, julian_day = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ascendant = swe.houses_ex(
        julian_day, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL
    )[1][0] % 360
    planets = {planet.name: planet for planet in _positions(julian_day, sidereal=True)}

    def house(name: str) -> int:
        return int(((planets[name].longitude - ascendant) % 360) // 30) + 1

    yogas: list[dict[str, str]] = []
    doshas: list[dict[str, str]] = []
    moon_jupiter = _distance(planets["Moon"].longitude, planets["Jupiter"].longitude)

    if any(abs(moon_jupiter - angle) <= 8 for angle in (0, 90, 180)):
        yogas.append({
            "name": "Gajakesari Yoga",
            "status": "Present",
            "rule": "Moon and Jupiter are in a configured kendra relationship (same, fourth, seventh, or tenth sign).",
        })

    kendra_planets = [name for name in CLASSICAL_PLANETS if house(name) in {1, 4, 7, 10}]
    if kendra_planets:
        yogas.append({
            "name": "Kendra strength",
            "status": "Present",
            "rule": f"{', '.join(kendra_planets)} occupy Kendra houses from Lagna: " + ", ".join(f"{name} H{house(name)}" for name in kendra_planets) + ".",
        })

    if house("Mars") in {1, 4, 7, 8, 12}:
        doshas.append({
            "name": "Manglik Dosha",
            "status": "Flagged",
            "rule": f"Mars is in H{house('Mars')} from Lagna. This is a screening rule; tradition-specific exceptions and both partner charts must be assessed.",
        })
    else:
        doshas.append({
            "name": "Manglik Dosha",
            "status": "Not flagged",
            "rule": f"Mars is in H{house('Mars')} from Lagna, outside the configured 1/4/7/8/12 screening houses.",
        })

    classical_longitudes = [planets[name].longitude for name in CLASSICAL_PLANETS]
    if _same_node_half(classical_longitudes, planets["Rahu"].longitude):
        doshas.append({
            "name": "Kaal Sarp pattern",
            "status": "Review",
            "rule": "All seven classical planets fall in one of the two Rahu-Ketu semicircles. Tradition-specific inclusion, conjunction and exception rules still need review.",
        })
    else:
        doshas.append({
            "name": "Kaal Sarp pattern",
            "status": "Not flagged",
            "rule": "The seven classical planets do not all occupy a single Rahu-Ketu semicircle in this configured screening rule.",
        })

    moon_sign = int(planets["Moon"].longitude // 30)
    occupied_neighbours = [
        name for name in CLASSICAL_PLANETS
        if name != "Moon" and int(planets[name].longitude // 30) in {(moon_sign - 1) % 12, (moon_sign + 1) % 12}
    ]
    if not occupied_neighbours:
        doshas.append({
            "name": "Kemadruma pattern",
            "status": "Review",
            "rule": "No classical planet other than Moon occupies either neighbouring sign from Moon. Kendra and cancellation rules are not applied in this compact screen.",
        })

    return {
        "yogas": yogas,
        "doshas": doshas,
        "chart_basis": {"ayanamsa": "Lahiri sidereal", "ascendant_longitude": round(ascendant, 4)},
        "notice": "Yoga and Dosha Analyzer shows transparent, compact classical screening rules. It is not a complete chart judgement, compatibility conclusion, or guaranteed outcome.",
    }
