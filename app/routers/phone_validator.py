from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.phone_service import validate_phone

router = APIRouter()


class PhoneRequest(BaseModel):
    phone: str = Field(..., description="Phone number to validate", example="+14155552671")
    country_code: str | None = Field(
        None,
        description="ISO 3166-1 alpha-2 country code (e.g., US, TR, DE)",
        example="US",
    )


@router.post("", summary="Validate a phone number")
@limiter.limit("30/minute")
async def validate(request: Request, body: PhoneRequest):
    """
    Validate and analyze a phone number:
    - Format in E.164, international, national
    - Detect carrier & type (mobile/landline/VOIP)
    - Get location and timezone
    """
    return validate_phone(body.phone, body.country_code)


@router.get("", summary="Quick phone validation via GET")
@limiter.limit("30/minute")
async def validate_get(
    request: Request,
    phone: str = Query(..., description="Phone number"),
    country_code: str | None = Query(None, description="Country code"),
):
    """Validate phone number via GET request."""
    return validate_phone(phone, country_code)
