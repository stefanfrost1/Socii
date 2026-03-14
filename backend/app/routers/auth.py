"""Domain-restricted signup via Supabase invite."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import httpx
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr


@router.post("/register", status_code=202)
async def register(body: RegisterRequest):
    domain = body.email.split("@")[-1].lower()
    allowed = settings.allowed_email_domain.lower()
    if domain != allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Registration is restricted to @{allowed} email addresses.",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.supabase_url}/auth/v1/invite",
                headers={
                    "apikey": settings.supabase_key,
                    "Authorization": f"Bearer {settings.supabase_key}",
                    "Content-Type": "application/json",
                },
                json={"email": body.email},
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Activation service timed out. Please try again.",
        )

    if resp.status_code not in (200, 201):
        body_json = resp.json()
        detail = body_json.get("msg") or body_json.get("message") or "Failed to send activation email."
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

    return {"message": "Activation email sent. Check your inbox to complete registration."}
