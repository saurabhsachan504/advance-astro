from datetime import UTC, datetime
from uuid import uuid4
import httpx
from fastapi import HTTPException
from sqlalchemy import select
from .config import Settings
from .database import SessionLocal
from .models import ForecastObservation, RuleFeedbackStat

def create_forecast(profile_reference: str, prediction: str, rule_key: str, due_at: datetime, contact_address: str | None) -> ForecastObservation:
    forecast = ForecastObservation(id=str(uuid4()), profile_reference=profile_reference, prediction=prediction, rule_key=rule_key, due_at=due_at, contact_address=contact_address)
    with SessionLocal() as db:
        db.add(forecast); db.commit(); db.refresh(forecast); db.expunge(forecast)
    return forecast

def record_feedback(forecast_id: str, outcome: str) -> ForecastObservation:
    with SessionLocal() as db:
        forecast = db.get(ForecastObservation, forecast_id)
        if not forecast: raise HTTPException(status_code=404, detail="Forecast not found")
        if forecast.status == "answered": raise HTTPException(status_code=409, detail="Feedback already recorded")
        forecast.status, forecast.outcome, forecast.feedback_at = "answered", outcome, datetime.now(UTC)
        stat = db.get(RuleFeedbackStat, forecast.rule_key) or RuleFeedbackStat(rule_key=forecast.rule_key)
        if outcome == "yes": stat.confirmed_count += 1
        elif outcome == "no": stat.declined_count += 1
        else: stat.uncertain_count += 1
        db.add(stat); db.commit(); db.refresh(forecast); db.expunge(forecast)
    return forecast

async def dispatch_due_followups(settings: Settings) -> int:
    if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_whatsapp_from]):
        raise HTTPException(status_code=503, detail="Twilio WhatsApp credentials are not configured")
    with SessionLocal() as db:
        due = db.scalars(select(ForecastObservation).where(ForecastObservation.status == "pending", ForecastObservation.due_at <= datetime.now(UTC), ForecastObservation.contact_address.is_not(None))).all()
        sent = 0
        for forecast in due:
            payload = {"From": settings.twilio_whatsapp_from, "To": forecast.contact_address, "Body": f"Advance Astro follow-up: {forecast.prediction}\nDid this happen? Reply through the secure feedback link in your app."}
            async with httpx.AsyncClient(auth=(settings.twilio_account_sid, settings.twilio_auth_token), timeout=20) as client:
                response = await client.post(f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json", data=payload)
                response.raise_for_status()
            forecast.followup_sent_at, forecast.status = datetime.now(UTC), "sent"; sent += 1
        db.commit()
    return sent
