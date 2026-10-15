from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .astrology import calculate_chart
from .config import get_settings
from .privacy import create_upload_intent
from .schemas import ChartRequest, ChartResponse, UploadIntentRequest

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.engine_version, docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"])

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

