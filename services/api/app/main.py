from datetime import datetime
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .astrology import calculate_chart
from .config import get_settings
from .database import Base, engine
from .feedback import create_forecast, dispatch_due_followups, record_feedback
from .privacy import create_upload_intent
from .schemas import ChartRequest, ChartResponse, FeedbackCreate, ForecastCreate, ForecastResponse, UploadIntentRequest
from .vision import interpret_symbolic_image

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.engine_version, docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"])

@app.on_event("startup")
def initialise_database() -> None:
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine_version": settings.engine_version}

@app.post("/v1/charts/calculate", response_model=ChartResponse)
def calculate(request: ChartRequest) -> ChartResponse:
    try:
        return calculate_chart(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/uploads/intents")
def upload_intent(request: UploadIntentRequest) -> dict:
    return create_upload_intent(request.purpose, request.consent_visual_analysis, request.retention, settings)

@app.post("/v1/visual-readings")
async def visual_reading(
    image: UploadFile = File(...),
    subject: str = Form(..., pattern="^(palm|face)$"),
    consent_visual_analysis: bool = Form(...),
) -> dict:
    """Runs a local vision model; raw images are never written to disk in this MVP."""
    if not consent_visual_analysis:
        raise HTTPException(status_code=422, detail="Explicit consent is required for visual analysis")
    content = await image.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit")
    result = await interpret_symbolic_image(content, image.content_type or "", subject, settings)
    return {"subject": subject, **result, "notice": "Visual symbolism is optional spiritual guidance; it is not identity, medical, personality, or future verification."}

@app.post("/v1/forecasts", response_model=ForecastResponse)
def add_forecast(request: ForecastCreate) -> ForecastResponse:
    forecast = create_forecast(request.profile_reference, request.prediction, request.rule_key, request.due_at, request.contact_address)
    return ForecastResponse.model_validate(forecast)

@app.post("/v1/forecasts/{forecast_id}/feedback", response_model=ForecastResponse)
def forecast_feedback(forecast_id: str, request: FeedbackCreate) -> ForecastResponse:
    return ForecastResponse.model_validate(record_feedback(forecast_id, request.outcome))

@app.post("/v1/feedback/followups/dispatch")
async def send_followups(x_internal_token: str | None = Header(default=None)) -> dict:
    if not settings.feedback_worker_secret or x_internal_token != settings.feedback_worker_secret:
        raise HTTPException(status_code=401, detail="Invalid internal worker token")
    return {"sent": await dispatch_due_followups(settings)}

