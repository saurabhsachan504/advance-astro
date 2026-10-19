from datetime import datetime
from fastapi import FastAPI, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .advanced import gochar, gochar_dashboard, jaimini, kp_studio, kundli, matchmaking, muhurat, panchang, panchang_month, prashna, strengths, varshaphal, vimshottari_dasha
from .astrology import calculate_chart, calculate_multi_system
from .config import get_settings
from .database import Base, engine
from .feedback import create_forecast, dispatch_due_followups, record_feedback
from .locations import search_locations
from .privacy import create_upload_intent
from .rag import ingest_chunk, retrieve
from .reports import chart_report, premium_report
from .schemas import AstrocartographyRequest, CalendarMonthRequest, CalendarRequest, ChartRequest, ChartResponse, DashaRequest, FeedbackCreate, ForecastCreate, ForecastResponse, GocharDashboardRequest, JaiminiRequest, KPRequest, KnowledgeChunkCreate, KnowledgeSearch, KundliRequest, MatchmakingRequest, MuhuratRequest, NumerologyRequest, PrashnaRequest, PremiumReportRequest, ReportRequest, TransitRequest, UploadIntentRequest, VarshaphalRequest
from .studios import astrocartography, numerology
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

@app.get("/v1/locations/search")
async def find_locations(query: str = Query(min_length=2, max_length=120)) -> dict:
    cleaned_query = query.strip()
    if len(cleaned_query) < 2:
        raise HTTPException(status_code=422, detail="Location search needs at least 2 characters")
    try:
        return {"results": await search_locations(cleaned_query)}
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.post("/v1/charts/calculate", response_model=ChartResponse)
def calculate(request: ChartRequest) -> ChartResponse:
    try:
        return calculate_chart(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/charts/multi")
def calculate_all_systems(request: ChartRequest) -> dict:
    try:
        return calculate_multi_system(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/numerology/analyse")
def analyse_numerology(request: NumerologyRequest) -> dict:
    return numerology(request)

@app.post("/v1/astrocartography/map")
def create_astrocartography_map(request: AstrocartographyRequest) -> dict:
    try:
        return astrocartography(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/dasha/vimshottari")
def calculate_vimshottari_dasha(request: DashaRequest) -> dict:
    try:
        return vimshottari_dasha(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/jaimini/analyse")
def analyse_jaimini(request: JaiminiRequest) -> dict:
    try:
        return jaimini(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/kp/analyse")
def analyse_kp(request: KPRequest) -> dict:
    try:
        return kp_studio(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/varshaphal/analyse")
def analyse_varshaphal(request: VarshaphalRequest) -> dict:
    try:
        return varshaphal(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/kundli/interactive")
def interactive_kundli(request: KundliRequest) -> dict:
    try:
        return kundli(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/matchmaking/analyse")
def analyse_matchmaking(request: MatchmakingRequest) -> dict:
    try:
        return matchmaking(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/calendar/panchang")
def daily_panchang(request: CalendarRequest) -> dict:
    try:
        return panchang(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/calendar/month")
def monthly_panchang(request: CalendarMonthRequest) -> dict:
    try:
        return panchang_month(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/muhurat/plan")
def plan_muhurat(request: MuhuratRequest) -> dict:
    try:
        return muhurat(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/gochar/live")
def live_gochar(request: TransitRequest) -> dict:
    try:
        return gochar(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/gochar/dashboard")
def personal_gochar_dashboard(request: GocharDashboardRequest) -> dict:
    try:
        return gochar_dashboard(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/strengths/calculate")
def calculate_strengths(request: ChartRequest) -> dict:
    try:
        return strengths(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/prashna/calculate")
def calculate_prashna(request: PrashnaRequest) -> dict:
    try:
        return prashna(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/reports/chart.pdf")
def download_chart_report(request: ReportRequest) -> StreamingResponse:
    try:
        report = chart_report(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return StreamingResponse(iter([report]), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=advance-astro-chart.pdf"})

@app.post("/v1/reports/premium.pdf")
def download_premium_report(request: PremiumReportRequest) -> StreamingResponse:
    try:
        report = premium_report(request, settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return StreamingResponse(iter([report]), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=veda-os-premium-report.pdf"})

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

@app.post("/v1/knowledge/chunks")
async def add_knowledge_chunk(request: KnowledgeChunkCreate, x_knowledge_secret: str | None = Header(default=None)) -> dict:
    if not settings.knowledge_admin_secret or x_knowledge_secret != settings.knowledge_admin_secret:
        raise HTTPException(status_code=401, detail="Invalid knowledge ingestion secret")
    return {"id": await ingest_chunk(request.text, request.source, request.section, settings)}

@app.post("/v1/knowledge/search")
async def search_knowledge(request: KnowledgeSearch) -> dict:
    return {"matches": await retrieve(request.query, request.limit, settings)}

