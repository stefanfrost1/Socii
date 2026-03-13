"""Supabase Storage integration for contact images and company logos."""
import io
import httpx
from PIL import Image
from fastapi import UploadFile
from app.config import settings

BUCKET = "socii-media"
MAX_SIZE = (500, 500)


def _supabase_headers():
    return {
        "Authorization": f"Bearer {settings.supabase_key}",
        "apikey": settings.supabase_key,
    }


async def _upload(path: str, data: bytes, content_type: str = "image/webp") -> tuple[str, str]:
    url = f"{settings.supabase_url}/storage/v1/object/{BUCKET}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=data,
            headers={**_supabase_headers(), "Content-Type": content_type},
        )
        response.raise_for_status()
    public_url = f"{settings.supabase_url}/storage/v1/object/public/{BUCKET}/{path}"
    return public_url, path


async def _delete(path: str):
    url = f"{settings.supabase_url}/storage/v1/object/{BUCKET}/{path}"
    async with httpx.AsyncClient() as client:
        await client.delete(url, headers=_supabase_headers())


def _process_image(data: bytes) -> bytes:
    """Resize to max 500×500, convert to WebP."""
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    img.thumbnail(MAX_SIZE, Image.LANCZOS)
    # Convert RGBA to RGB for WebP
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    out = io.BytesIO()
    bg.save(out, format="WEBP", quality=85)
    return out.getvalue()


async def upload_contact_image(contact_id: str, file: UploadFile) -> tuple[str, str]:
    raw = await file.read()
    processed = _process_image(raw)
    path = f"contacts/{contact_id}/avatar.webp"
    return await _upload(path, processed)


async def delete_contact_image(path: str):
    await _delete(path)


async def upload_company_logo(company_id: str, file: UploadFile) -> tuple[str, str]:
    raw = await file.read()
    processed = _process_image(raw)
    path = f"companies/{company_id}/logo.webp"
    return await _upload(path, processed)


async def delete_company_logo(path: str):
    await _delete(path)


async def upload_from_url(image_url: str, storage_path: str) -> tuple[str, str]:
    """Download from URL, process, upload to Supabase Storage."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        response = await client.get(image_url, headers={"User-Agent": "Socii-CRM/1.0"})
        response.raise_for_status()
    processed = _process_image(response.content)
    return await _upload(storage_path, processed)
