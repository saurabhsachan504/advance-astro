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
from .schemas import CalendarMonthRequest, CalendarRequest, ChartRequest, DashaRequest, GocharDashboardRequest, JaiminiRequest, KundliRequest, MatchmakingRequest, MuhuratRequest, PrashnaRequest, TransitRequest, VarshaphalRequest

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

CHARA_KARAKAS = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"]
SIGN_LORDS = {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}


def _navamsa_sign(longitude: float) -> tuple[int, int]:
    """Classical D9 sign start rules for movable, fixed and dual signs."""
    sign = int(longitude % 360 // 30)
    part = min(8, int((longitude % 30) / (30 / 9)))
    start = sign if sign % 3 == 0 else (sign + 8) % 12 if sign % 3 == 1 else (sign + 4) % 12
    return (start + part) % 12, part + 1


def _jaimini_aspected_signs(sign: int) -> list[int]:
    movable, fixed, dual = {0, 3, 6, 9}, {1, 4, 7, 10}, {2, 5, 8, 11}
    if sign in movable:
        return sorted(fixed - {(sign + 1) % 12})
    if sign in fixed:
        return sorted(movable - {(sign - 1) % 12})
    return sorted(dual - {sign})


def jaimini(request: JaiminiRequest, settings: Settings) -> dict:
    """Return transparent Jaimini sign-based facts using a seven-karaka rule pack."""
    _, jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ascendant = swe.houses_ex(jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360
    planets = _positions(jd, True)
    position = {planet.name: planet.longitude for planet in planets}
    karaka_planets = [planet for planet in planets if planet.name in {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}]
    ranked = sorted(karaka_planets, key=lambda planet: (planet.longitude % 30, planet.longitude), reverse=True)
    karakas = [{"karaka": CHARA_KARAKAS[index], "planet": planet.name, "sign": planet.sign, "longitude": round(planet.longitude, 6), "degrees_in_sign": round(planet.longitude % 30, 6)} for index, planet in enumerate(ranked)]
    atmakaraka = ranked[0]
    karakamsha_index, navamsa_part = _navamsa_sign(atmakaraka.longitude)
    asc_sign = int(ascendant // 30)
    asc_sign_name = SIGNS[asc_sign]
    lagna_lord = SIGN_LORDS[asc_sign_name]
    lord_sign = int(position[lagna_lord] // 30)
    arudha_index = (lord_sign + (lord_sign - asc_sign) % 12) % 12
    if arudha_index in {asc_sign, (asc_sign + 6) % 12}:
        arudha_index = (arudha_index + 9) % 12
    sign_planets: dict[int, list[str]] = {index: [] for index in range(12)}
    for planet in planets:
        sign_planets[int(planet.longitude // 30)].append(planet.name)
    aspects = [{"from_sign": SIGNS[sign], "aspected_signs": [SIGNS[target] for target in _jaimini_aspected_signs(sign)], "aspecting_planets": names, "receiving_planets": [planet for target in _jaimini_aspected_signs(sign) for planet in sign_planets[target]]} for sign, names in sign_planets.items() if names]
    direction = 1 if asc_sign % 2 == 0 else -1
    cursor = request.birth_datetime.replace(tzinfo=ZoneInfo(request.timezone))
    periods = []
    elapsed_years = 0.0
    for offset in range(12):
        sign = (asc_sign + direction * offset) % 12
        lord = SIGN_LORDS[SIGNS[sign]]
        lord_position_sign = int(position[lord] // 30)
        distance = (lord_position_sign - sign) % 12 if direction == 1 else (sign - lord_position_sign) % 12
        years = 12 if distance == 0 else distance
        start, end = cursor, cursor + timedelta(days=years * DASHA_YEAR_DAYS)
        periods.append({"sign": SIGNS[sign], "lord": lord, "years": years, "start": start.isoformat(), "end": end.isoformat()})
        cursor, elapsed_years = end, elapsed_years + years
        if elapsed_years >= request.years:
            break
    return {
        "ayanamsa": "Lahiri", "chara_karakas": karakas,
        "karakamsha": {"atmakaraka": atmakaraka.name, "sign": SIGNS[karakamsha_index], "navamsa_part": navamsa_part, "method": "Atmakaraka placed by classical D9 sign-start rules"},
        "arudha_lagna": {"sign": SIGNS[arudha_index], "lagna_sign": asc_sign_name, "lord": lagna_lord, "lord_sign": SIGNS[lord_sign], "method": "Count Lagna to its sign lord and the same distance onward; apply the 1st/7th exception to the 10th."},
        "jaimini_aspects": aspects,
        "chara_dasha_periods": periods,
        "rule_pack": {"chara_karakas": "Seven-karaka system; Rahu is excluded.", "jaimini_aspects": "Movable signs aspect non-adjacent fixed signs; fixed signs aspect non-adjacent movable signs; dual signs aspect other dual signs.", "chara_dasha": "Baseline sign-dasha sequence starts from Lagna. Odd-sign Lagnas progress zodiacally and even-sign Lagnas reverse; each sign duration is the directional distance to its classical sign lord (same-sign lord = 12 years)."},
        "notice": "Jaimini systems have lineage-specific variants. This factual rule pack displays its selected rules and should be reviewed against the user's tradition before professional use.",
    }


def _wrap_angle(value: float) -> float:
    return (value + 180) % 360 - 180


def _solar_return_jd(request: VarshaphalRequest, settings: Settings, natal_sun: float, target_year: int) -> float:
    """Solve the Lahiri sidereal Sun return near the native calendar anniversary."""
    try:
        anniversary = request.birth_datetime.replace(year=target_year)
    except ValueError:  # Feb 29 profiles return on Feb 28 in non-leap years.
        anniversary = request.birth_datetime.replace(year=target_year, month=2, day=28)
    jd = _at_datetime_jd(anniversary, request.timezone, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    for _ in range(8):
        values = swe.calc_ut(jd, swe.SUN, flags)[0]
        difference = _wrap_angle(values[0] - natal_sun)
        speed = values[3]
        if abs(difference) < 0.00001 or abs(speed) < 0.00001:
            break
        jd -= difference / speed
    return jd


def _mudda_dasha(request: VarshaphalRequest, settings: Settings, start: datetime, end: datetime, natal_moon: float) -> list[dict]:
    nak_index = int(natal_moon // NAKSHATRA_SPAN)
    elapsed = (natal_moon % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    lord_index, first, cursor = nak_index % 9, True, start
    periods = []
    while cursor < end:
        proportion = VIMSHOTTARI_YEARS[lord_index] / 120
        days = DASHA_YEAR_DAYS * proportion * (1 - elapsed if first else 1)
        period_end = min(end, cursor + timedelta(days=days))
        periods.append({"lord": VIMSHOTTARI_LORDS[lord_index], "start": cursor.isoformat(), "end": period_end.isoformat(), "days": round((period_end - cursor).total_seconds() / 86400, 3)})
        cursor, lord_index, first = period_end, (lord_index + 1) % 9, False
    return periods


def varshaphal(request: VarshaphalRequest, settings: Settings) -> dict:
    """Compute a factual Lahiri solar-return / Tajika baseline for the selected year."""
    utc, natal_jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    target_year = request.year or datetime.now(ZoneInfo(request.timezone)).year
    natal_planets = _positions(natal_jd, True)
    natal_sun = next(planet.longitude for planet in natal_planets if planet.name == "Sun")
    natal_moon = next(planet.longitude for planet in natal_planets if planet.name == "Moon")
    return_jd = _solar_return_jd(request, settings, natal_sun, target_year)
    return_local = _jd_to_local(return_jd, request.timezone)
    next_return_jd = _solar_return_jd(request, settings, natal_sun, target_year + 1)
    next_return_local = _jd_to_local(next_return_jd, request.timezone)
    return_asc = swe.houses_ex(return_jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360
    return_planets = _positions(return_jd, True)
    by_name = {planet.name: planet for planet in return_planets}
    natal_asc = swe.houses_ex(natal_jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360
    age = target_year - request.birth_datetime.year
    muntha_sign_index = (int(natal_asc // 30) + age) % 12
    muntha_lord = SIGN_LORDS[SIGNS[muntha_sign_index]]
    return_lagna_lord = SIGN_LORDS[SIGNS[int(return_asc // 30)]]
    candidate_names = list(dict.fromkeys([return_lagna_lord, muntha_lord, "Sun", "Moon"]))
    candidates = []
    for priority, name in enumerate(candidate_names):
        house = _whole_sign_house(by_name[name].longitude, return_asc)
        score = 3 if house in {1, 4, 7, 10} else 2 if house in {5, 9} else 1
        candidates.append({"planet": name, "house": house, "score": score, "priority": priority})
    varshesha = sorted(candidates, key=lambda item: (-item["score"], item["priority"]))[0]
    aspects = []
    for index, first in enumerate(return_planets):
        for second in return_planets[index + 1:]:
            separation = min(abs(first.longitude - second.longitude) % 360, 360 - (abs(first.longitude - second.longitude) % 360))
            for name, angle, relation in [("conjunction", 0, "neutral"), ("sextile", 60, "supportive"), ("square", 90, "challenging"), ("trine", 120, "supportive"), ("opposition", 180, "challenging")]:
                orb = abs(separation - angle)
                if orb <= 5:
                    aspects.append({"first": first.name, "second": second.name, "aspect": name, "relation": relation, "orb": round(orb, 2)})
    return {
        "year": target_year,
        "varsha_pravesh": {"local_datetime": return_local.isoformat(), "ascendant_sign": SIGNS[int(return_asc // 30)], "sun_longitude": round(natal_sun, 6), "birth_utc": utc.isoformat()},
        "muntha": {"sign": SIGNS[muntha_sign_index], "lord": muntha_lord, "age_completed": age, "lord_return_house": _whole_sign_house(by_name[muntha_lord].longitude, return_asc)},
        "varshesha": {**varshesha, "candidates": candidates, "method": "Highest angular/trinal house score among return Lagna lord, Munthesha, Sun and Moon; ties follow candidate order."},
        "tajika_aspects": aspects,
        "mudda_dasha": _mudda_dasha(request, settings, return_local, next_return_local, natal_moon),
        "rule_pack": {"varsha_pravesh": "Exact Lahiri sidereal Sun longitude return solved iteratively with Swiss Ephemeris.", "muntha": "Natal whole-sign Lagna advanced one sign per completed solar year.", "tajika_aspects": "Configured 5° geometric orb for conjunction, sextile, square, trine and opposition; applying/separating and full Tajika yogas are not inferred.", "mudda_dasha": "Annual Vimshottari proportion scaled to one tropical year, beginning from the natal Moon nakshatra balance."},
        "notice": "Tajika and Varshaphal methods have regional rule variations. This tool exposes a deterministic baseline and its assumptions; it is not a guarantee or a complete professional judgement.",
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


def panchang_month(request: CalendarMonthRequest) -> dict:
    """Return a location-aware monthly Panchang with transparent Muhurat availability."""
    start = request.month
    next_month = date(start.year + (start.month == 12), 1 if start.month == 12 else start.month + 1, 1)
    days = []
    cursor = start
    while cursor < next_month:
        daily = panchang(CalendarRequest(date=cursor, timezone=request.timezone, latitude=request.latitude, longitude=request.longitude))
        rahu = daily["rahu_kaal"]
        favourable = [
            window for window in daily["choghadiya"]["day"]
            if window["name"] in EVENT_FAVOURABLE[request.event] and (window["end"] <= rahu["start"] or window["start"] >= rahu["end"])
        ]
        days.append({
            "date": cursor.isoformat(), "weekday": cursor.strftime("%A"), "tithi": daily["tithi"], "nakshatra": daily["nakshatra"], "yoga": daily["yoga"],
            "sunrise": daily["sunrise"], "sunset": daily["sunset"], "rahu_kaal": rahu, "choghadiya": daily["choghadiya"],
            "muhurat_windows": favourable, "muhurat_available": bool(favourable),
        })
        cursor += timedelta(days=1)
    return {
        "month": start.isoformat(), "timezone": request.timezone, "event": request.event, "days": days,
        "request": {"timezone": request.timezone, "latitude": request.latitude, "longitude": request.longitude, "event": request.event},
        "notice": "Muhurat highlights use the baseline event-favourable Choghadiya rule outside Rahu Kaal. Regional Panchang and family tradition rules are not included.",
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


def _at_datetime_jd(value: datetime, timezone: str, settings: Settings) -> float:
    local = value.replace(tzinfo=ZoneInfo(timezone))
    utc = local.astimezone(ZoneInfo("UTC"))
    swe.set_ephe_path(str(settings.ephemeris_path))
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)


def gochar(request: TransitRequest, settings: Settings) -> dict:
    """Compare current sidereal planets to natal positions, without interpretation claims."""
    _, natal_jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moment = request.transit_datetime or datetime.now(ZoneInfo(request.timezone)).replace(tzinfo=None)
    transit_jd = _at_datetime_jd(moment, request.timezone, settings)
    natal = _positions(natal_jd, True)
    transit = _positions(transit_jd, True)
    natal_asc = swe.houses_ex(natal_jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360
    # Request longitude speed explicitly.  Without this Swiss Ephemeris can
    # return a zero-filled speed slot, which makes retrograde state unreliable.
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    rows = []
    rahu_speed = swe.calc_ut(transit_jd, PLANETS["Rahu"], flags)[0][3]
    for body in transit:
        code = PLANETS.get(body.name)
        # Ketu is derived as the point opposite Rahu, so it has Rahu's motion.
        speed = rahu_speed if body.name == "Ketu" else swe.calc_ut(transit_jd, code, flags)[0][3]
        rows.append({"name": body.name, "longitude": body.longitude, "sign": body.sign, "house_from_lagna": _whole_sign_house(body.longitude, natal_asc), "speed_longitude_deg_day": round(speed, 6), "retrograde": speed < 0, "natal_sign": next(item.sign for item in natal if item.name == body.name)})
    natal_moon = next(item for item in natal if item.name == "Moon")
    transit_saturn = next(item for item in transit if item.name == "Saturn")
    moon_sign, saturn_sign = int(natal_moon.longitude // 30), int(transit_saturn.longitude // 30)
    sade_phase = {11: "Rising phase", 0: "Peak phase", 1: "Setting phase"}.get((saturn_sign - moon_sign) % 12, "Outside Sade Sati")
    contacts = []
    for moving in transit:
        for birth in natal:
            separation = min(abs(moving.longitude - birth.longitude) % 360, 360 - (abs(moving.longitude - birth.longitude) % 360))
            for name, angle, orb in [("conjunction", 0, 4), ("square", 90, 4), ("trine", 120, 4), ("opposition", 180, 4)]:
                if abs(separation - angle) <= orb:
                    contacts.append({"transit": moving.name, "natal": birth.name, "aspect": name, "orb": round(abs(separation - angle), 2)})
    return {"transit_local_datetime": moment.replace(tzinfo=ZoneInfo(request.timezone)).isoformat(), "ayanamsa": "Lahiri", "planets": rows, "sade_sati": {"natal_moon_sign": natal_moon.sign, "transit_saturn_sign": transit_saturn.sign, "phase": sade_phase}, "major_contacts": contacts, "notice": "Gochar shows astronomical positions and configured aspect geometry; it does not guarantee outcomes."}


def gochar_dashboard(request: GocharDashboardRequest, settings: Settings) -> dict:
    """Return a profile-based transit workspace for the next 7 or 30 local days.

    Ingresses are found in six-hour local-time scans.  This keeps the dashboard
    responsive while making the time precision explicit rather than claiming an
    exact ingress minute.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moment = request.transit_datetime or datetime.now(ZoneInfo(request.timezone)).replace(tzinfo=None)
    current_request = request.model_copy(update={"transit_datetime": moment})
    current = gochar(current_request, settings)
    natal_moon_sign = str(current["sade_sati"]["natal_moon_sign"])
    natal_moon_index = SIGNS.index(natal_moon_sign)
    _, natal_jd = _utc_and_jd(request, settings)
    natal_asc = swe.houses_ex(natal_jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360

    def positions_at(local_time: datetime) -> dict[str, object]:
        return {body.name: body for body in _positions(_at_datetime_jd(local_time, request.timezone, settings), True)}

    daily_overview = []
    for offset in range(request.range_days):
        day_time = (moment + timedelta(days=offset)).replace(hour=12, minute=0, second=0, microsecond=0)
        positions = positions_at(day_time)
        moon = positions["Moon"]
        saturn = positions["Saturn"]
        saturn_index = int(saturn.longitude // 30)
        phase = {11: "Rising phase", 0: "Peak phase", 1: "Setting phase"}.get((saturn_index - natal_moon_index) % 12, "Outside Sade Sati")
        daily_overview.append({
            "date": day_time.date().isoformat(),
            "moon_sign": moon.sign,
            "moon_house_from_lagna": _whole_sign_house(moon.longitude, natal_asc),
            "saturn_sign": saturn.sign,
            "sade_sati_phase": phase,
        })

    # A six-hour scan safely catches the Moon's sign changes and is transparent
    # about its precision. Each event is the first scan point after the ingress.
    previous = positions_at(moment)
    ingresses = []
    scan_time = moment
    for _ in range(request.range_days * 4):
        scan_time += timedelta(hours=6)
        next_positions = positions_at(scan_time)
        for name, body in next_positions.items():
            before = previous[name]
            if body.sign != before.sign:
                ingresses.append({
                    "planet": name,
                    "from_sign": before.sign,
                    "to_sign": body.sign,
                    "detected_local_datetime": scan_time.replace(tzinfo=ZoneInfo(request.timezone)).isoformat(),
                })
        previous = next_positions
    ingresses.sort(key=lambda event: str(event["detected_local_datetime"]))

    retrograde_planets = [
        {"name": planet["name"], "sign": planet["sign"], "speed_longitude_deg_day": planet["speed_longitude_deg_day"]}
        for planet in current["planets"]
        if planet["retrograde"]
    ]
    return {
        "range_days": request.range_days,
        "range_start": moment.date().isoformat(),
        "current": current,
        "retrograde_planets": retrograde_planets,
        "daily_overview": daily_overview,
        "upcoming_ingresses": ingresses,
        "ingress_precision": "First six-hour local scan after a sign change; not an exact ingress minute.",
        "notice": "This dashboard reports calculated sidereal positions and configured geometry only. It does not guarantee outcomes.",
    }


EXALTATION = {"Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165, "Jupiter": 95, "Venus": 357, "Saturn": 200}
NAISARGIKA_BALA = {"Sun": 60, "Moon": 51.43, "Mars": 17.14, "Mercury": 25.71, "Jupiter": 34.29, "Venus": 42.86, "Saturn": 8.57}
DIG_DIRECTIONS = {"Sun": 10, "Mars": 10, "Moon": 4, "Venus": 4, "Jupiter": 1, "Mercury": 1, "Saturn": 7}
MEAN_DAILY_MOTION = {"Sun": 0.9856, "Moon": 13.176, "Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083, "Venus": 1.2, "Saturn": 0.033}

# Classical Bhinna-Ashtakavarga bindu rules. Each tuple is the house distance
# (1-12) from the contributing body/Lagna that gives one bindu to the subject.
BAV_RULES = {
    "Sun": {"Sun": (1,2,4,7,8,9,10,11), "Moon": (3,6,10,11), "Mars": (1,2,4,7,8,9,10,11), "Mercury": (3,5,6,9,10,11), "Jupiter": (5,6,9,11), "Venus": (6,7,12), "Saturn": (1,2,4,7,8,9,10,11), "Lagna": (3,4,6,10,11)},
    "Moon": {"Sun": (3,6,7,8,10,11), "Moon": (1,3,6,7,10,11), "Mars": (2,3,5,6,9,10,11), "Mercury": (1,3,4,5,7,8,10,11), "Jupiter": (1,4,7,8,10,11), "Venus": (3,4,5,7,9,10,11), "Saturn": (3,5,6,11), "Lagna": (3,6,10,11)},
    "Mars": {"Sun": (3,5,6,10,11), "Moon": (3,6,11), "Mars": (1,2,4,7,8,10,11), "Mercury": (3,5,6,11), "Jupiter": (6,10,11,12), "Venus": (6,8,11,12), "Saturn": (1,4,7,8,9,10,11), "Lagna": (1,3,6,10,11)},
    "Mercury": {"Sun": (5,6,9,11,12), "Moon": (2,4,6,8,10,11), "Mars": (1,2,4,7,8,9,10,11), "Mercury": (1,3,5,6,9,10,11,12), "Jupiter": (6,8,11,12), "Venus": (1,2,3,4,5,8,9,11), "Saturn": (1,2,4,7,8,9,10,11), "Lagna": (1,2,4,6,8,10,11)},
    "Jupiter": {"Sun": (1,2,3,4,7,8,9,10,11), "Moon": (2,5,7,9,11), "Mars": (1,2,4,7,8,10,11), "Mercury": (1,2,4,5,6,9,10,11), "Jupiter": (1,2,3,4,7,8,10,11), "Venus": (2,5,6,9,10,11), "Saturn": (3,5,6,12), "Lagna": (1,2,4,5,6,7,9,10,11)},
    "Venus": {"Sun": (8,11,12), "Moon": (1,2,3,4,5,8,9,11,12), "Mars": (3,5,6,9,11,12), "Mercury": (3,5,6,9,11), "Jupiter": (5,8,9,10,11), "Venus": (1,2,3,4,5,8,9,10,11), "Saturn": (3,4,5,8,9,10,11), "Lagna": (1,2,3,4,5,8,9,11)},
    "Saturn": {"Sun": (1,2,4,7,8,10,11), "Moon": (3,6,11), "Mars": (3,5,6,10,11,12), "Mercury": (6,8,9,10,11,12), "Jupiter": (5,6,11,12), "Venus": (6,11,12), "Saturn": (3,5,6,11), "Lagna": (1,3,4,6,10,11)},
}

# Published classical Bhinna-Ashtakavarga table checksums.  Keeping these next
# to the rule table prevents quiet regressions when a house entry is edited.
BAV_EXPECTED_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39}
SARVASHTAKAVARGA_EXPECTED_TOTAL = 337

# Corrected entries: Sun receives bindus from Mercury and Lagna in the 12th,
# and Moon receives one from Jupiter in the 12th.
BAV_RULES["Sun"]["Mercury"] = (3, 5, 6, 9, 10, 11, 12)
BAV_RULES["Sun"]["Lagna"] = (3, 4, 6, 10, 11, 12)
BAV_RULES["Moon"]["Jupiter"] = (1, 4, 7, 8, 10, 11, 12)


def strengths(request: ChartRequest, settings: Settings) -> dict:
    """Bhinna/Sarvashtakavarga plus transparent, component-level strength factors."""
    _, jd = _utc_and_jd(request, settings)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    asc = swe.houses_ex(jd, request.latitude, request.longitude, b"W", swe.FLG_SIDEREAL)[1][0] % 360
    # FLG_SPEED is required for a meaningful Chesta-motion component.
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    positions = {}
    rows = []
    for name, code in PLANETS.items():
        if name == "Rahu":
            continue
        values = swe.calc_ut(jd, code, flags)[0]
        longitude, speed = values[0] % 360, values[3]
        positions[name] = longitude
        house = _whole_sign_house(longitude, asc)
        distance = min((longitude - EXALTATION[name]) % 360, (EXALTATION[name] - longitude) % 360)
        uchcha = round(max(0, 60 * (1 - distance / 180)), 2)
        desired = DIG_DIRECTIONS[name]
        direction_distance = min((house - desired) % 12, (desired - house) % 12)
        dig = round(max(0, 60 - direction_distance * 10), 2)
        kendra = 60 if house in {1, 4, 7, 10} else 30 if house in {2, 5, 8, 11} else 15
        cheshta = round(min(60, abs(speed) / MEAN_DAILY_MOTION[name] * 30), 2)
        rows.append({"planet": name, "house": house, "components": {"uchcha_bala": uchcha, "kendra_bala": kendra, "dig_bala": dig, "cheshta_motion_index": cheshta, "naisargika_bala": NAISARGIKA_BALA[name]}, "component_score": round(uchcha + kendra + dig + cheshta + NAISARGIKA_BALA[name], 2)})
    positions["Lagna"] = asc
    bav = {}
    for subject, contributor_rules in BAV_RULES.items():
        signs = []
        for target in range(12):
            bindus = sum(1 for contributor, allowed in contributor_rules.items() if ((target - int(positions[contributor] // 30)) % 12 + 1) in allowed)
            signs.append(bindus)
        bav[subject] = {"sign_bindus": signs, "total": sum(signs)}
    sarva = [sum(bav[planet]["sign_bindus"][sign] for planet in BAV_RULES) for sign in range(12)]
    actual_totals = {planet: data["total"] for planet, data in bav.items()}
    table_valid = actual_totals == BAV_EXPECTED_TOTALS and sum(sarva) == SARVASHTAKAVARGA_EXPECTED_TOTAL
    if not table_valid:
        raise RuntimeError("Bhinna-Ashtakavarga table checksum validation failed")
    houses = [{"house": number, "sign": SIGNS[(int(asc // 30) + number - 1) % 12], "bindus": sarva[(int(asc // 30) + number - 1) % 12]} for number in range(1, 13)]
    return {"shadbala_components": rows, "bhinna_ashtakavarga": bav, "sarvashtakavarga": {"sign_bindus": sarva, "total": sum(sarva), "houses_from_lagna": houses}, "checksums": {"valid": table_valid, "bhinna_expected_totals": BAV_EXPECTED_TOTALS, "sarvashtakavarga_expected_total": SARVASHTAKAVARGA_EXPECTED_TOTAL}, "notice": "Bhinna and Sarvashtakavarga bindu tables are deterministic and checksum-validated. Strength factors expose Uchcha, Kendra, Dig, motion and Naisargika components; full tradition-specific Shadbala additions (Kala, Drik, divisional and ayan-specific variants) require a selectable rule pack."}


def prashna(request: PrashnaRequest, settings: Settings) -> dict:
    chart_request = ChartRequest(birth_datetime=request.question_datetime, timezone=request.timezone, latitude=request.latitude, longitude=request.longitude)
    chart = kundli(KundliRequest(**chart_request.model_dump()), settings)
    calendar = panchang(CalendarRequest(date=request.question_datetime.date(), timezone=request.timezone, latitude=request.latitude, longitude=request.longitude))
    moon = next(item for item in chart["bodies"] if item["name"] == "Moon")
    return {"question": request.question, "question_datetime": request.question_datetime.replace(tzinfo=ZoneInfo(request.timezone)).isoformat(), "lagna": chart["bodies"][0], "moon": moon, "panchang": {"tithi": calendar["tithi"], "nakshatra": calendar["nakshatra"], "rahu_kaal": calendar["rahu_kaal"]}, "houses": chart["houses"], "notice": "Prashna chart facts are generated at the supplied moment and location. A trained practitioner should apply the interpretive rules."}


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
