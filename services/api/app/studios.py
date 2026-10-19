"""Transparent numerology and astrocartography calculation studios."""

from datetime import datetime
from math import acos, degrees, radians, tan

import swisseph as swe

from .astrology import PLANETS, _utc_and_jd
from .config import Settings
from .schemas import AstrocartographyRequest, NumerologyRequest

PYTHAGOREAN = {letter: (index % 9) + 1 for index, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
LINE_COLOURS = {"Sun": "#f6c453", "Moon": "#b9dcff", "Mercury": "#85d5c0", "Venus": "#f192b6", "Mars": "#ed7564", "Jupiter": "#b894f0", "Saturn": "#8296bb", "Rahu": "#d9a56f", "Ketu": "#c7b8a0"}


def _reduce(number: int) -> int:
    while number > 9 and number not in {11, 22, 33}:
        number = sum(int(digit) for digit in str(number))
    return number


def _digits(value: str) -> int:
    return sum(int(character) for character in value if character.isdigit())


def _letters(value: str, *, vowels: bool | None = None) -> int:
    total = 0
    for character in value.upper():
        if character not in PYTHAGOREAN:
            continue
        is_vowel = character in "AEIOU"
        if vowels is None or vowels == is_vowel:
            total += PYTHAGOREAN[character]
    return total


def numerology(request: NumerologyRequest) -> dict:
    """Return Pythagorean core-number arithmetic with each rule exposed."""
    birth = request.birth_datetime.date()
    name = request.full_name.strip() or "Private profile"
    year = request.year or datetime.now().year
    life_raw = _digits(birth.strftime("%Y%m%d"))
    birthday_raw = birth.day
    attitude_raw = birth.month + birth.day
    expression_raw = _letters(name)
    soul_raw = _letters(name, vowels=True)
    personality_raw = _letters(name, vowels=False)
    personal_year_raw = _digits(f"{birth.month:02d}{birth.day:02d}{year}")
    rows = [
        {"key": "life_path", "label": "Life Path", "value": _reduce(life_raw), "raw": life_raw, "rule": "Sum every digit in the birth date; retain 11, 22 and 33 as master numbers."},
        {"key": "birthday", "label": "Birthday", "value": _reduce(birthday_raw), "raw": birthday_raw, "rule": "Reduce the calendar day of birth, retaining master numbers."},
        {"key": "attitude", "label": "Attitude", "value": _reduce(attitude_raw), "raw": attitude_raw, "rule": "Reduce birth month plus birth day."},
        {"key": "expression", "label": "Expression", "value": _reduce(expression_raw), "raw": expression_raw, "rule": "Map all A-Z letters in the supplied name to the Pythagorean 1-9 cycle."},
        {"key": "soul_urge", "label": "Soul Urge", "value": _reduce(soul_raw), "raw": soul_raw, "rule": "Use vowels A, E, I, O and U in the supplied name."},
        {"key": "personality", "label": "Personality", "value": _reduce(personality_raw), "raw": personality_raw, "rule": "Use consonants in the supplied name."},
        {"key": "personal_year", "label": f"Personal Year {year}", "value": _reduce(personal_year_raw), "raw": personal_year_raw, "rule": "Reduce birth month, birth day and the selected calendar year."},
    ]
    return {"system": "Pythagorean numerology", "name_used": name, "birth_date": birth.isoformat(), "year": year, "core_numbers": rows, "notice": "Numerology Studio shows reproducible number reductions for reflection. It is not a guarantee, diagnosis or factual prediction."}


def _longitude(value: float) -> float:
    return round((value + 180) % 360 - 180, 6)


def _horizon_points(right_ascension: float, declination: float, sidereal: float, rising: bool) -> list[list[float]]:
    points: list[list[float]] = []
    for latitude in range(-70, 71, 5):
        cosine_hour_angle = -tan(radians(latitude)) * tan(radians(declination))
        if -1 <= cosine_hour_angle <= 1:
            hour_angle = degrees(acos(cosine_hour_angle))
            local_sidereal = right_ascension - hour_angle if rising else right_ascension + hour_angle
            points.append([_longitude(local_sidereal - sidereal), latitude])
    return points


def astrocartography(request: AstrocartographyRequest, settings: Settings) -> dict:
    """Generate reproducible tropical angular lines in equirectangular coordinates."""
    utc, julian_day = _utc_and_jd(request, settings)
    sidereal = swe.sidtime(julian_day) * 15
    lines = []
    for name, planet in PLANETS.items():
        right_ascension, declination = swe.calc_ut(julian_day, planet, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0][:2]
        mc_longitude = _longitude(right_ascension - sidereal)
        ic_longitude = _longitude(mc_longitude + 180)
        colour = LINE_COLOURS.get(name, "#e9b96e")
        lines.extend([
            {"planet": name, "angle": "MC", "color": colour, "coordinates": [[mc_longitude, -80], [mc_longitude, 80]]},
            {"planet": name, "angle": "IC", "color": colour, "coordinates": [[ic_longitude, -80], [ic_longitude, 80]]},
            {"planet": name, "angle": "ASC", "color": colour, "coordinates": _horizon_points(right_ascension, declination, sidereal, True)},
            {"planet": name, "angle": "DSC", "color": colour, "coordinates": _horizon_points(right_ascension, declination, sidereal, False)},
        ])
    return {"zodiac": "Tropical", "utc_iso": utc.isoformat(), "greenwich_sidereal_degrees": round(sidereal, 6), "lines": lines, "notice": "This astrocartography map uses geocentric tropical right ascension and declination. MC/IC lines mark meridian alignment; ASC/DSC lines solve the horizon equation at five-degree latitude intervals. It is a visual study tool, not a guaranteed outcome."}
