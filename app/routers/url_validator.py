from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.url_service import validate_url

router = APIRouter()


class URLRequest(BaseModel):
    url: str = Field(..., description="URL to validate", example="https://example.com")
    check_live: bool = Field(False, description="Also check if URL is reachable")


@router.post("", summary="Validate a URL")
@limiter.limit("30/minute")
async def validate(request: Request, body: URLRequest):
    """
    Validate URL format and optionally check if it's live.
    Returns parsed components, protocol info, and live status.
    """
    return await validate_url(body.url, check_live=body.check_live)


@router.get("", summary="Quick URL validation via GET")
@limiter.limit("30/minute")
async def validate_get(
    request: Request,
    url: str = Query(..., description="URL to validate"),
    check_live: bool = Query(False, description="Check if URL is reachable"),
):
    """Validate URL via GET request."""
    return await validate_url(url, check_live=check_live)
