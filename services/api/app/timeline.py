from datetime import datetime
from zoneinfo import ZoneInfo

from .advanced import gochar_dashboard, vimshottari_dasha
from .config import Settings
from .schemas import DashaRequest, GocharDashboardRequest, TimelineRequest

def dasha_gochar_timeline(request: TimelineRequest, settings: Settings) -> dict:
    base = request.model_dump()
    dasha = vimshottari_dasha(DashaRequest(**base, years=5), settings)
    gochar = gochar_dashboard(GocharDashboardRequest(**base), settings)
    events = []
    for period in dasha["periods"]:
        events.append({"kind": "Mahadasha", "title": f"{period['lord']} Mahadasha", "start": period["start"], "end": period["end"], "detail": "Vimshottari major period"})
        events.extend({"kind": "Antardasha", "title": f"{period['lord']} / {item['lord']}", "start": item["start"], "end": item["end"], "detail": "Vimshottari sub-period"} for item in period["antardashas"])
    events.extend({"kind": "Gochar", "title": f"{item['planet']} enters {item['to_sign']}", "start": item["detected_local_datetime"], "end": item["detected_local_datetime"], "detail": f"From {item['from_sign']}"} for item in gochar["upcoming_ingresses"])
    now = datetime.now(ZoneInfo(request.timezone)).isoformat()
    sade = gochar["current"]["sade_sati"]
    events.append({"kind": "Sade Sati", "title": f"Sade Sati: {sade['phase']}", "start": now, "end": now, "detail": f"Natal Moon {sade['natal_moon_sign']} · Saturn {sade['transit_saturn_sign']}"})
    events.extend({"kind": "Retrograde", "title": f"{item['name']} retrograde", "start": now, "end": now, "detail": item["sign"]} for item in gochar["retrograde_planets"])
    return {"range_days": request.range_days, "events": sorted(events, key=lambda item: item["start"]), "notice": "Timeline combines calculated Vimshottari periods with sidereal Lahiri transit events. It is a planning view, not a guarantee of events."}
