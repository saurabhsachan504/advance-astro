import base64
import io
from PIL import Image, ImageStat
import httpx
from fastapi import HTTPException
from .config import Settings

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}

def inspect_image(content: bytes, content_type: str) -> dict[str, float | int | str]:
    if content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WEBP palm/face images are supported")
    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
        image.verify()
        image = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid image") from exc
    if image.width < 480 or image.height < 480:
        raise HTTPException(status_code=422, detail="Use a clear image of at least 480 × 480 pixels")
    stats = ImageStat.Stat(image.resize((96, 96)))
    brightness = sum(stats.mean) / 3
    contrast = sum(stats.var) / 3
    if brightness < 25 or brightness > 238 or contrast < 90:
        raise HTTPException(status_code=422, detail="Photo quality is too low; use evenly lit, sharp image with a plain background")
    return {"width": image.width, "height": image.height, "brightness": round(brightness, 1), "contrast": round(contrast, 1)}

async def interpret_symbolic_image(content: bytes, content_type: str, subject: str, settings: Settings) -> dict:
    quality = inspect_image(content, content_type)
    if not settings.vision_llm_base_url or not settings.vision_llm_model:
        raise HTTPException(status_code=503, detail="Vision AI is not configured. Add a local Qwen-VL/LLaVA compatible endpoint before enabling visual readings.")
    encoded = base64.b64encode(content).decode("ascii")
    system = "You are a private spiritual-symbolism assistant. Describe only visible, non-identifying symbolic features relevant to a palm or face reading. Never identify a person, infer age, gender, race, health, emotion, personality, or future certainty. Use cautious, entertainment-only language and return concise plain text."
    prompt = f"This is a user-consented {subject} image. Give 3-5 visible symbolic observations with confidence caveats. Do not claim scientific verification."
    headers = {"Content-Type": "application/json"}
    if settings.vision_llm_api_key:
        headers["Authorization"] = f"Bearer {settings.vision_llm_api_key}"
    payload = {"model": settings.vision_llm_model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{encoded}"}}]}], "temperature": 0.25, "max_tokens": 450}
    try:
        async with httpx.AsyncClient(timeout=75) as client:
            response = await client.post(f"{settings.vision_llm_base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            message = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        raise HTTPException(status_code=502, detail="Local Vision AI did not return a usable reading") from exc
    return {"quality": quality, "interpretation": message, "raw_image_retained": False}
