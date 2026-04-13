from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.hash_service import generate_password, generate_uuid_v4, generate_token

router = APIRouter()


class PasswordRequest(BaseModel):
    length: int = Field(16, ge=4, le=256, description="Password length")
    uppercase: bool = Field(True, description="Include uppercase letters")
    lowercase: bool = Field(True, description="Include lowercase letters")
    digits: bool = Field(True, description="Include digits")
    special: bool = Field(True, description="Include special characters")
    exclude_ambiguous: bool = Field(False, description="Exclude ambiguous chars (0O1lI)")
    count: int = Field(1, ge=1, le=50, description="Number of passwords to generate")


class TokenRequest(BaseModel):
    length: int = Field(32, ge=8, le=512, description="Token length in bytes")
    encoding: str = Field("hex", description="Encoding: hex, urlsafe, or base64")


@router.post("/password", summary="Generate secure password")
@limiter.limit("30/minute")
async def create_password(request: Request, body: PasswordRequest):
    """
    Generate cryptographically secure random password(s).
    Customizable length, character types, and quantity.
    """
    return generate_password(
        length=body.length,
        uppercase=body.uppercase,
        lowercase=body.lowercase,
        digits=body.digits,
        special=body.special,
        exclude_ambiguous=body.exclude_ambiguous,
        count=body.count,
    )


@router.get("/password", summary="Quick password via GET")
@limiter.limit("30/minute")
async def quick_password(
    request: Request,
    length: int = Query(16, ge=4, le=256),
    count: int = Query(1, ge=1, le=50),
):
    """Generate password via GET with default settings."""
    return generate_password(length=length, count=count)


@router.post("/uuid", summary="Generate UUID v4")
@limiter.limit("60/minute")
async def create_uuid(
    request: Request,
    count: int = Query(1, ge=1, le=100, description="Number of UUIDs"),
):
    """Generate cryptographically random UUID v4."""
    return generate_uuid_v4(count=count)


@router.get("/uuid", summary="Quick UUID via GET")
@limiter.limit("60/minute")
async def quick_uuid(
    request: Request,
    count: int = Query(1, ge=1, le=100),
):
    """Generate UUID v4 via GET request."""
    return generate_uuid_v4(count=count)


@router.post("/token", summary="Generate secure token")
@limiter.limit("30/minute")
async def create_token(request: Request, body: TokenRequest):
    """Generate cryptographically secure random token."""
    return generate_token(length=body.length, encoding=body.encoding)


@router.get("/token", summary="Quick token via GET")
@limiter.limit("30/minute")
async def quick_token(
    request: Request,
    length: int = Query(32, ge=8, le=512),
    encoding: str = Query("hex"),
):
    """Generate token via GET request."""
    return generate_token(length=length, encoding=encoding)
