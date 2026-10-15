from datetime import datetime
from zoneinfo import ZoneInfo
import swisseph as swe
from .config import Settings
from .schemas import ChartRequest, ChartResponse, Planet, Provenance

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}

def _format_planet(name: str, longitude: float) -> Planet:
    normalized = longitude % 360
    return Planet(name=name, longitude=round(normalized, 6), sign=SIGNS[int(normalized // 30)], nakshatra=NAKSHATRAS[int(normalized // (360 / 27))])

def calculate_chart(request: ChartRequest, settings: Settings) -> ChartResponse:
    """Return sidereal positions; every output is derived directly from Swiss Ephemeris."""
    try:
        local = request.birth_datetime.replace(tzinfo=ZoneInfo(request.timezone))
    except Exception as exc:
        raise ValueError("timezone must be a valid IANA zone, e.g. Asia/Kolkata") from exc
    utc = local.astimezone(ZoneInfo("UTC"))
    swe.set_ephe_path(str(settings.ephemeris_path))
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    planets = []
    for name, code in PLANETS.items():
        longitude = swe.calc_ut(jd, code, flags)[0][0]
        planets.append(_format_planet(name, longitude))
    # Ketu is always precisely opposite the mean node in this v1 rule set.
    rahu = next(item for item in planets if item.name == "Rahu")
    planets.append(_format_planet("Ketu", rahu.longitude + 180))
    cusps, ascmc = swe.houses_ex(jd, request.latitude, request.longitude, b'W', flags)
    ascendant = _format_planet("Ascendant", ascmc[0])
    return ChartResponse(
        ascendant=ascendant, planets=planets,
        provenance=Provenance(engine_version=settings.engine_version, ephemeris_version="Swiss Ephemeris/pyswisseph", ayanamsa="Lahiri", timezone=request.timezone, utc_iso=utc.isoformat())
    )

