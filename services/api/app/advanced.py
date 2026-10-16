"""Deterministic Vedic and Western calculation helpers used by advanced routes.

Interpretive choices are deliberately returned as transparent rules rather than
presented as certainty. Times are local civil times unless noted otherwise.
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

from .astrology import (
    NAKSHATRAS,
    PLANETS,
    SIGNS,
    VIMSHOTTARI_LORDS,
    VIMSHOTTARI_YEARS,
    _aspects,
    _format_planet,
    _kp_sublord,
    _positions,
    _utc_and_jd,
)
from .config import Settings
from .schemas import CalendarRequest, ChartRequest, DashaRequest, KundliRequest, MatchmakingRequest, MuhuratRequest

NAKSHATRA_SPAN = 360 / 27
DASHA_YEAR_DAYS = 365.2425
RAHU_SEGMENTS = [8, 2, 7, 5, 6, 4, 3]  # Sunday to Saturday; one-indexed daylight segment
CHOGHADIYA = {
    6: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
    0: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],
    1: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    2: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],
    3: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],
    4: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],
    5: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],
}
FAVOURABLE = {"Amrit", "Shubh", "Labh"}
EVENT_FAVOURABLE = {
    "marriage": {"Amrit", "Shubh", "Labh"},
    "business": {"Amrit", "Shubh", "Labh", "Char"},
    "travel": {"Char", "Labh", "Amrit"},
    "naming": {"Amrit", "Shubh", "Labh"},
    "property_purchase": {"Amrit", "Shubh", "Labh"},
}


def _date_to_jd(day: date, timezone: str) -> float:
    local = datetime.combine(day, datetime.min.time(), tzinfo=ZoneInfo(timezone))
    utc = local.astimezone(ZoneInfo("UTC"))
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60)


def _jd_to_local(julian_day: float, timezone: str) -> datetime:
    year, month, day, hour = swe.revjul(julian_day)
    utc = datetime(year, month, day, tzinfo=ZoneInfo("UTC")) + timedelta(hours=hour)
    return utc.astimezone(ZoneInfo(timezone))


def _sun_event(day: date, request: CalendarRequest, rise: bool) -> datetime:
    start = _date_to_jd(day, request.timezone)
    flags = swe.CALC_RISE if rise else swe.CALC_SET
    result, times = swe.rise_trans(start, swe.SUN, flags | swe.BIT_DISC_CENTER, (request.longitude, request.latitude, 0))
    if result < 0:
        # Polar regions can have no daily rise/set. This explicit fallback keeps
        # the calendar usable while marking the approximation in provenance.
        return datetime.combine(day, datetime.min.time(), tzinfo=ZoneInfo(request.timezone)) + timedelta(hours=6 if rise else 18)
    return _jd_to_local(times[0], request.timezone)


def _panchang_positions(day: date, request: CalendarRequest) -> tuple[float, float]:
    jd = _date_to_jd(day, request.timezone)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360, swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360


def _next_eclipses(day: date, timezone: str) -> list[dict]:
    """Return the next global solar/lunar events when supported by ephemeris data."""
    jd = _date_to_jd(day, timezone)
    events = []
    for kind, finder in (("solar", swe.sol_eclipse_when_glob), ("lunar", swe.lun_eclipse_when)):
        try:
            flags, times = finder(jd)
            if flags:
                events.append({"type": kind, "peak": _jd_to_local(times[0], timezone).isoformat(), "visibility": "Global event; local visibility is not calculated in this starter."})
        except Exception:
            # Some minimal ephemeris installations omit eclipse search data.
            continue
    return events


def panchang(request: CalendarRequest) -> dict:
    sun, moon = _panchang_positions(request.date, request)
    phase = (moon - sun) % 360
    tithi_number = int(phase // 12) + 1
    nakshatra_index = int(moon // NAKSHATRA_SPAN)
    yoga_index = int(((sun + moon) % 360) // NAKSHATRA_SPAN)
    sunrise = _sun_event(request.date, request, True)
    sunset = _sun_event(request.date, request, False)
    next_sunrise = _sun_event(request.date + timedelta(days=1), request, True)
    daylight = (sunset - sunrise) / 8
    nighttime = (next_sunrise - sunset) / 8
    weekday = request.date.weekday()
    labels = CHOGHADIYA[weekday]
    day_windows = [{"name": name, "start": (sunrise + daylight * index).isoformat(), "end": (sunrise + daylight * (index + 1)).isoformat(), "favourable": name in FAVOURABLE} for index, name in enumerate(labels)]
    # Night labels progress by one weekday's cycle after sunset.
    night_labels = CHOGHADIYA[(weekday + 1) % 7]
    night_windows = [{"name": name, "start": (sunset + nighttime * index).isoformat(), "end": (sunset + nighttime * (index + 1)).isoformat(), "favourable": name in FAVOURABLE} for index, name in enumerate(night_labels)]
    rahu_start = sunrise + daylight * (RAHU_SEGMENTS[(weekday + 1) % 7] - 1)
    return {
        "date": request.date.isoformat(), "timezone": request.timezone, "sunrise": sunrise.isoformat(), "sunset": sunset.isoformat(),
        "tithi": {"number": tithi_number, "paksha": "Shukla" if tithi_number <= 15 else "Krishna", "name": f"Tithi {((tithi_number - 1) % 15) + 1}"},
        "nakshatra": NAKSHATRAS[nakshatra_index], "yoga": yoga_index + 1,
        "rahu_kaal": {"start": rahu_start.isoformat(), "end": (rahu_start + daylight).isoformat()},
        "choghadiya": {"day": day_windows, "night": night_windows},
        "eclipse_alerts": _next_eclipses(request.date, request.timezone),
        "provenance": {"ayanamsa": "Lahiri", "sunrise_method": "Swiss Ephemeris rise/set; civil fallback at polar latitudes"},
    }


def vimshottari_dasha(request: DashaRequest, settings: Settings) -> dict:
    _, jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    nak_index = int(moon // NAKSHATRA_SPAN)
    elapsed = (moon % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    start_lord_index = nak_index % 9
    cursor = request.birth_datetime.replace(tzinfo=ZoneInfo(request.timezone))
    periods = []
    remaining_years = request.years
    index = start_lord_index
    first = True
    while remaining_years > 0:
        full_years = VIMSHOTTARI_YEARS[index]
        years = full_years * (1 - elapsed) if first else full_years
        end = cursor + timedelta(days=years * DASHA_YEAR_DAYS)
        antars = []
        antar_cursor = cursor
        for offset in range(9):
            sub_index = (index + offset) % 9
            sub_days = (end - cursor).total_seconds() / 86400 * VIMSHOTTARI_YEARS[sub_index] / 120
            sub_end = antar_cursor + timedelta(days=sub_days)
            antars.append({"lord": VIMSHOTTARI_LORDS[sub_index], "start": antar_cursor.isoformat(), "end": sub_end.isoformat()})
            antar_cursor = sub_end
        periods.append({"lord": VIMSHOTTARI_LORDS[index], "start": cursor.isoformat(), "end": end.isoformat(), "antardashas": antars})
        remaining_years -= years
        cursor, index, first = end, (index + 1) % 9, False
    return {"moon": {"longitude": round(moon, 6), "nakshatra": NAKSHATRAS[nak_index], "birth_dasha_lord": VIMSHOTTARI_LORDS[start_lord_index], "elapsed_fraction": round(elapsed, 8)}, "year_basis_days": DASHA_YEAR_DAYS, "periods": periods, "notice": "Timeline is deterministic from the selected Vimshottari year basis; interpretations remain optional."}


def _whole_sign_house(longitude: float, ascendant: float) -> int:
    return int(((longitude - ascendant) % 360) // 30) + 1


def kundli(request: KundliRequest, settings: Settings) -> dict:
    utc, jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    asc = swe.houses_ex(jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360
    planets = _positions(jd, True)
    bodies = [{"name": "Ascendant", "longitude": round(asc, 6), "sign": SIGNS[int(asc // 30)], "house": 1}]
    for planet in planets:
        bodies.append({"name": planet.name, "longitude": planet.longitude, "sign": planet.sign, "nakshatra": planet.nakshatra, "house": _whole_sign_house(planet.longitude, asc)})
    houses = [{"house": number, "sign": SIGNS[(int(asc // 30) + number - 1) % 12], "occupants": [body["name"] for body in bodies if body.get("house") == number]} for number in range(1, 13)]
    def varga(divisor: int) -> list[dict]:
        output = []
        for planet in planets:
            harmonic = (planet.longitude * divisor) % 360
            output.append({"name": planet.name, "longitude": round(harmonic, 6), "sign": SIGNS[int(harmonic // 30)], "house": _whole_sign_house(harmonic, (asc * divisor) % 360)})
        return output
    return {"layout": request.layout, "utc_iso": utc.isoformat(), "ayanamsa": "Lahiri", "houses": houses, "bodies": bodies, "divisional_charts": {"D1": bodies, "D9_navamsa": varga(9), "D10_dashamsa": varga(10)}, "notice": "D9/D10 use a harmonic divisional transform; verify tradition-specific rules before using in professional reports."}


def _moon_facts(request: ChartRequest, settings: Settings) -> dict:
    _, jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    return {"longitude": moon, "sign": int(moon // 30), "nakshatra": int(moon // NAKSHATRA_SPAN), "kp": _kp_sublord(moon)}


def _manglik(request: ChartRequest, settings: Settings) -> dict:
    _, jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    mars = swe.calc_ut(jd, swe.MARS, flags)[0][0] % 360
    moon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360
    asc = swe.houses_ex(jd, request.latitude, request.longitude, b"W", flags)[1][0] % 360
    sensitive = {1, 4, 7, 8, 12}
    from_asc, from_moon = _whole_sign_house(mars, asc), _whole_sign_house(mars, moon)
    return {"from_lagna_house": from_asc, "from_moon_house": from_moon, "flagged": from_asc in sensitive or from_moon in sensitive, "rule": "Mars in houses 1, 4, 7, 8 or 12 from Lagna or Moon"}


def matchmaking(request: MatchmakingRequest, settings: Settings) -> dict:
    first, second = _moon_facts(request.person_a, settings), _moon_facts(request.person_b, settings)
    def tara(a: int, b: int) -> bool: return ((b - a) % 27 + 1) % 9 not in {1, 3, 5, 7}
    tara_score = 3 if tara(first["nakshatra"], second["nakshatra"]) and tara(second["nakshatra"], first["nakshatra"]) else 1.5
    gana = ["Deva", "Manushya", "Rakshasa"]
    gana_a, gana_b = gana[first["nakshatra"] % 3], gana[second["nakshatra"] % 3]
    gana_score = 6 if gana_a == gana_b else 5 if "Manushya" in {gana_a, gana_b} else 1
    sign_distance = (second["sign"] - first["sign"]) % 12 + 1
    bhakoot_score = 0 if sign_distance in {2, 6, 8, 12} else 7
    nadi_score = 0 if first["nakshatra"] % 3 == second["nakshatra"] % 3 else 8
    yoni_score = 4 if first["nakshatra"] == second["nakshatra"] else 2
    varna_score = 1 if first["sign"] % 4 == second["sign"] % 4 else 0.5
    vashya_score = 2 if first["sign"] == second["sign"] else 1
    maitri_score = 5 if abs(first["sign"] - second["sign"]) % 3 == 0 else 2.5
    kutas = [{"name": "Varna", "score": varna_score, "maximum": 1}, {"name": "Vashya", "score": vashya_score, "maximum": 2}, {"name": "Tara", "score": tara_score, "maximum": 3}, {"name": "Yoni", "score": yoni_score, "maximum": 4}, {"name": "Graha Maitri", "score": maitri_score, "maximum": 5}, {"name": "Gana", "score": gana_score, "maximum": 6}, {"name": "Bhakoot", "score": bhakoot_score, "maximum": 7}, {"name": "Nadi", "score": nadi_score, "maximum": 8}]
    total = sum(item["score"] for item in kutas)
    manglik_a, manglik_b = _manglik(request.person_a, settings), _manglik(request.person_b, settings)
    _, jd_a = _utc_and_jd(request.person_a, settings); _, jd_b = _utc_and_jd(request.person_b, settings)
    western_a, western_b = _positions(jd_a, False), _positions(jd_b, False)
    cross_aspects = []
    for left in western_a:
        for right in western_b:
            cross_aspects.extend([{**item, "person_a": item.pop("first"), "person_b": item.pop("second")} for item in _aspects([left, right])])
    kp_score = 100 if first["kp"]["sub_lord"] == second["kp"]["sub_lord"] else 70 if first["kp"]["star_lord"] == second["kp"]["star_lord"] else 45
    return {"people": [request.person_a_label, request.person_b_label], "ashtakoota": {"score": total, "maximum": 36, "kutas": kutas}, "manglik": {request.person_a_label: manglik_a, request.person_b_label: manglik_b, "balance_note": "Both profiles are flagged" if manglik_a["flagged"] and manglik_b["flagged"] else "Review the individual Mars placements"}, "kp_comparison": {"score": kp_score, "moon_a": first["kp"], "moon_b": second["kp"], "notice": "Transparent Moon star/sub-lord comparison heuristic; not a complete KP compatibility judgement."}, "synastry": {"zodiac": "Tropical", "major_cross_aspects": cross_aspects}, "notice": "Ashtakoota components shown here are a transparent baseline. Consult an experienced practitioner for tradition-specific exceptions and final matching."}


def muhurat(request: MuhuratRequest) -> dict:
    end = request.end_date or request.date
    results = []
    day = request.date
    while day <= end:
        cal_request = CalendarRequest(date=day, timezone=request.timezone, latitude=request.latitude, longitude=request.longitude)
        calendar = panchang(cal_request)
        rahu = calendar["rahu_kaal"]
        for window in calendar["choghadiya"]["day"]:
            if window["name"] not in EVENT_FAVOURABLE[request.event]:
                continue
            if window["end"] <= rahu["start"] or window["start"] >= rahu["end"]:
                results.append({"start": window["start"], "end": window["end"], "choghadiya": window["name"], "tithi": calendar["tithi"], "nakshatra": calendar["nakshatra"], "rules": ["event-favourable choghadiya", "outside Rahu Kaal"]})
        day += timedelta(days=1)
    return {"event": request.event, "timezone": request.timezone, "windows": results[:60], "notice": "Baseline planning rules exclude Rahu Kaal and select event-favourable Choghadiya. Regional Panchang and family tradition rules are not yet included."}
