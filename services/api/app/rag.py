from uuid import uuid4
import httpx
from fastapi import HTTPException
from .config import Settings

COLLECTION = "astro_knowledge"

async def _embed(text: str, settings: Settings) -> list[float]:
    if not settings.embedding_base_url or not settings.embedding_model:
        raise HTTPException(status_code=503, detail="Local embedding service is not configured")
    headers = {"Content-Type": "application/json"}
    if settings.embedding_api_key: headers["Authorization"] = f"Bearer {settings.embedding_api_key}"
    try:
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(f"{settings.embedding_base_url.rstrip('/')}/embeddings", headers=headers, json={"model": settings.embedding_model, "input": text})
            response.raise_for_status(); return response.json()["data"][0]["embedding"]
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        raise HTTPException(status_code=502, detail="Local embedding service did not return an embedding") from exc

async def _ensure_collection(vector_size: int, settings: Settings) -> None:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"{settings.qdrant_url.rstrip('/')}/collections/{COLLECTION}")
        if response.status_code == 404:
            created = await client.put(f"{settings.qdrant_url.rstrip('/')}/collections/{COLLECTION}", json={"vectors": {"size": vector_size, "distance": "Cosine"}})
            created.raise_for_status()
        elif response.is_error: response.raise_for_status()

async def ingest_chunk(text: str, source: str, section: str | None, settings: Settings) -> str:
    vector = await _embed(text, settings); await _ensure_collection(len(vector), settings); point_id = str(uuid4())
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.put(f"{settings.qdrant_url.rstrip('/')}/collections/{COLLECTION}/points", json={"points": [{"id": point_id, "vector": vector, "payload": {"text": text, "source": source, "section": section or ""}}]})
        response.raise_for_status()
    return point_id

async def retrieve(query: str, limit: int, settings: Settings) -> list[dict]:
    vector = await _embed(query, settings)
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.qdrant_url.rstrip('/')}/collections/{COLLECTION}/points/search", json={"vector": vector, "limit": limit, "with_payload": True})
        if response.status_code == 404: return []
        response.raise_for_status()
    return [{"score": item["score"], "text": item["payload"].get("text"), "source": item["payload"].get("source"), "section": item["payload"].get("section")} for item in response.json()["result"]]
