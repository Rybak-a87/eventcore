import httpx
from app.core.settings import settings


async def translate_text(text: str, source: str, target: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            settings.libre_url,
            json={
                "q": text,
                "source": source, # from
                "target": target, # to
                "format": "text"
            }
        )
    return resp.json()["translatedText"]
