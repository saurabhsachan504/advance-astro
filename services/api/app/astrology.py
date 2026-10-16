from datetime import datetime
from zoneinfo import ZoneInfo
import swisseph as swe
from .config import Settings
from .schemas import ChartRequest, ChartResponse, Planet, Provenance

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}

def _format_planet(name: str, longitude: float) -> Planet:
    normalized = longitude % 360
    return Planet(name=name, longitude=round(normalized, 6), sign=SIGNS[int(normalized // 30)], nakshatra=NAKSHATRAS[int(normalized // (360 / 27))])

def _utc_and_jd(request: ChartRequest, settings: Settings) -> tuple[datetime, float]:
    try: local = request.birth_datetime.replace(tzinfo=ZoneInfo(request.timezone))
    except Exception as exc: raise ValueError("timezone must be a valid IANA zone, e.g. Asia/Kolkata") from exc
    utc = local.astimezone(ZoneInfo("UTC")); swe.set_ephe_path(str(settings.ephemeris_path))
    return utc, swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)

def _positions(jd: float, sidereal: bool) -> list[Planet]:
    flags = swe.FLG_SWIEPH | (swe.FLG_SIDEREAL if sidereal else 0)
    planets = [_format_planet(name, swe.calc_ut(jd, code, flags)[0][0]) for name, code in PLANETS.items()]
    rahu = next(item for item in planets if item.name == "Rahu"); planets.append(_format_planet("Ketu", rahu.longitude + 180)); return planets

def _ascendant(jd: float, request: ChartRequest, sidereal: bool, house_system: bytes = b"W") -> Planet:
    _, ascmc = swe.houses_ex(jd, request.latitude, request.longitude, house_system, swe.FLG_SIDEREAL if sidereal else 0)
    return _format_planet("Ascendant", ascmc[0])

def calculate_chart(request: ChartRequest, settings: Settings) -> ChartResponse:
    utc, jd = _utc_and_jd(request, settings); swe.set_sid_mode(swe.SIDM_LAHIRI)
    return ChartResponse(ascendant=_ascendant(jd, request, True), planets=_positions(jd, True), provenance=Provenance(engine_version=settings.engine_version, ephemeris_version="Swiss Ephemeris/pyswisseph", ayanamsa="Lahiri", timezone=request.timezone, utc_iso=utc.isoformat()))

def _kp_sublord(longitude: float) -> dict[str, str]:
    nak_span = 360 / 27; nak_index = int((longitude % 360) // nak_span); remaining = longitude % nak_span; star_index = nak_index % 9
    for position in range(9):
        lord_index = (star_index + position) % 9; segment = nak_span * VIMSHOTTARI_YEARS[lord_index] / 120
        if remaining <= segment or position == 8: return {"nakshatra": NAKSHATRAS[nak_index], "star_lord": VIMSHOTTARI_LORDS[star_index], "sub_lord": VIMSHOTTARI_LORDS[lord_index]}
        remaining -= segment
    raise RuntimeError("KP calculation failed")

def _reduce(value: int) -> int:
    while value > 9 and value not in (11, 22, 33): value = sum(int(digit) for digit in str(value))
    return value

def _aspects(planets: list[Planet]) -> list[dict[str, float | str]]:
    aspects = []
    for index, first in enumerate(planets):
        for second in planets[index + 1:]:
            separation = min(abs(first.longitude - second.longitude) % 360, 360 - (abs(first.longitude - second.longitude) % 360))
            for name, angle, orb in [("conjunction", 0, 7), ("sextile", 60, 4), ("square", 90, 6), ("trine", 120, 6), ("opposition", 180, 7)]:
                if abs(separation - angle) <= orb: aspects.append({"first": first.name, "second": second.name, "aspect": name, "orb": round(abs(separation - angle), 2)})
    return aspects

def calculate_multi_system(request: ChartRequest, settings: Settings) -> dict:
    utc, jd = _utc_and_jd(request, settings); swe.set_sid_mode(swe.SIDM_LAHIRI)
    vedic_planets, vedic_asc = _positions(jd, True), _ascendant(jd, request, True)
    western_planets, western_asc = _positions(jd, False), _ascendant(jd, request, False, b"P")
    kp_cusps, _ = swe.houses_ex(jd, request.latitude, request.longitude, b"P", swe.FLG_SIDEREAL)
    numbers = [int(char) for char in request.birth_datetime.strftime("%Y%m%d")]
    return {"provenance": {"engine_version": settings.engine_version, "ephemeris_version": "Swiss Ephemeris/pyswisseph", "utc_iso": utc.isoformat(), "timezone": request.timezone}, "vedic_parashari": {"ayanamsa": "Lahiri", "ascendant": vedic_asc.model_dump(), "planets": [p.model_dump() for p in vedic_planets]}, "kp": {"method": "KP: sidereal Placidus cusps with Vimshottari star/sub-lords", "cusps": [{"house": index + 1, "longitude": round(longitude % 360, 6), **_kp_sublord(longitude)} for index, longitude in enumerate(kp_cusps)], "points": [{"name": p.name, "longitude": p.longitude, **_kp_sublord(p.longitude)} for p in [vedic_asc, *vedic_planets]]}, "numerology": {"life_path": _reduce(sum(numbers)), "birthday_number": _reduce(request.birth_datetime.day), "attitude_number": _reduce(request.birth_datetime.month + request.birth_datetime.day)}, "western": {"zodiac": "Tropical", "houses": "Placidus", "ascendant": western_asc.model_dump(), "planets": [p.model_dump() for p in western_planets], "aspects": _aspects(western_planets)}}
