from datetime import datetime
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

