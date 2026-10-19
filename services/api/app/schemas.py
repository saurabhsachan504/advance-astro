from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class ChartRequest(BaseModel):
    birth_datetime: datetime
    timezone: str = Field(min_length=3, max_length=64)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    ayanamsa: Literal["lahiri"] = "lahiri"

    @field_validator("birth_datetime")
    @classmethod
    def require_naive_local_time(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("birth_datetime must be local time without an offset; send timezone separately")
        return value

class Planet(BaseModel):
    name: str
    longitude: float
    sign: str
    nakshatra: str

class Provenance(BaseModel):
    engine_version: str
    ephemeris_version: str
    ayanamsa: str
    timezone: str
    utc_iso: str

class ChartResponse(BaseModel):
    ascendant: Planet
    planets: list[Planet]
    provenance: Provenance

class UploadIntentRequest(BaseModel):
    purpose: Literal["palm", "face"]
    consent_visual_analysis: bool
    retention: Literal["delete_after_analysis", "one_hour"] = "delete_after_analysis"

class ForecastCreate(BaseModel):
    profile_reference: str = Field(min_length=3, max_length=128)
    prediction: str = Field(min_length=12, max_length=2000)
    rule_key: str = Field(min_length=3, max_length=160)
    due_at: datetime
    contact_address: str | None = Field(default=None, max_length=255)

class FeedbackCreate(BaseModel):
    outcome: Literal["yes", "no", "unsure"]

class ForecastResponse(BaseModel):
    id: str
    profile_reference: str
    prediction: str
    rule_key: str
    due_at: datetime
    status: str
    outcome: str | None
    model_config = {"from_attributes": True}

class KnowledgeChunkCreate(BaseModel):
    text: str = Field(min_length=30, max_length=12000)
    source: str = Field(min_length=2, max_length=300)
    section: str | None = Field(default=None, max_length=300)

class KnowledgeSearch(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    limit: int = Field(default=5, ge=1, le=10)


class DashaRequest(ChartRequest):
    years: int = Field(default=20, ge=1, le=120)


class JaiminiRequest(ChartRequest):
    years: int = Field(default=72, ge=1, le=120)


class KPRequest(ChartRequest):
    event: Literal["marriage", "business", "travel", "naming", "property_purchase"] = "marriage"


class NumerologyRequest(ChartRequest):
    full_name: str = Field(default="Private profile", min_length=1, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2200)


class AstrocartographyRequest(ChartRequest):
    pass


class VarshaphalRequest(ChartRequest):
    year: int | None = Field(default=None, ge=1900, le=2200)


class CalendarRequest(BaseModel):
    date: date
    timezone: str = Field(min_length=3, max_length=64)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CalendarMonthRequest(BaseModel):
    month: date
    timezone: str = Field(min_length=3, max_length=64)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    event: Literal["marriage", "business", "travel", "naming", "property_purchase"] = "marriage"

    @field_validator("month")
    @classmethod
    def require_month_start(cls, value: date) -> date:
        if value.day != 1:
            raise ValueError("month must be the first day of the month")
        return value


class MuhuratRequest(CalendarRequest):
    event: Literal["marriage", "business", "travel", "naming", "property_purchase"]
    end_date: date | None = None

    @field_validator("end_date")
    @classmethod
    def range_is_limited(cls, value: date | None, info):
        start = info.data.get("date")
        if value and start and not start <= value <= start.fromordinal(start.toordinal() + 31):
            raise ValueError("end_date must be between date and 31 days after it")
        return value


class MatchmakingRequest(BaseModel):
    person_a: ChartRequest
    person_b: ChartRequest
    person_a_label: str = Field(default="Person A", min_length=1, max_length=80)
    person_b_label: str = Field(default="Person B", min_length=1, max_length=80)


class KundliRequest(ChartRequest):
    layout: Literal["north_indian", "south_indian"] = "north_indian"


class TransitRequest(ChartRequest):
    transit_datetime: datetime | None = None


class GocharDashboardRequest(TransitRequest):
    range_days: Literal[7, 30] = 7


class PrashnaRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    question_datetime: datetime
    timezone: str = Field(min_length=3, max_length=64)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ReportRequest(ChartRequest):
    report_title: str = Field(default="Advance Astro Chart Report", min_length=3, max_length=100)


class PremiumReportRequest(ChartRequest):
    report_title: str = Field(default="Private Astrology Report", min_length=3, max_length=100)
    profile_name: str = Field(default="Private profile", min_length=1, max_length=80)
    language: Literal["en", "hi"] = "en"
    gochar_range_days: Literal[7, 30] = 7
    varshaphal_year: int | None = Field(default=None, ge=1900, le=2200)

