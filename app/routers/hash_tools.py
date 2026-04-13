from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.hash_service import (
    generate_hash,
    generate_all_hashes,
    generate_hmac,
    compare_hash,
)

router = APIRouter()


class HashRequest(BaseModel):
    text: str = Field(..., description="Text to hash", example="Hello World")
    algorithm: str = Field(
        "sha256",
        description="Hash algorithm: md5, sha1, sha256, sha384, sha512, sha3_256, sha3_512, blake2b, blake2s",
    )


class HashAllRequest(BaseModel):
    text: str = Field(..., description="Text to hash with all algorithms", example="Hello World")


class HmacRequest(BaseModel):
    text: str = Field(..., description="Text to sign", example="important data")
    key: str = Field(..., description="Secret key for HMAC", example="my-secret-key")
    algorithm: str = Field("sha256", description="Hash algorithm")


class HashCompareRequest(BaseModel):
    text: str = Field(..., description="Original text", example="Hello World")
    hash: str = Field(..., description="Hash to compare against")
    algorithm: str = Field("sha256", description="Algorithm used")


@router.post("", summary="Generate hash")
@limiter.limit("60/minute")
async def create_hash(request: Request, body: HashRequest):
    """Generate a hash of the provided text."""
    return generate_hash(body.text, body.algorithm)


@router.post("/all", summary="Generate all hashes")
@limiter.limit("30/minute")
async def create_all_hashes(request: Request, body: HashAllRequest):
    """Generate hashes using ALL available algorithms at once."""
    return generate_all_hashes(body.text)


@router.post("/hmac", summary="Generate HMAC")
@limiter.limit("30/minute")
async def create_hmac(request: Request, body: HmacRequest):
    """Generate HMAC signature for data integrity verification."""
    return generate_hmac(body.text, body.key, body.algorithm)


@router.post("/compare", summary="Compare text against hash")
@limiter.limit("30/minute")
async def compare(request: Request, body: HashCompareRequest):
    """Check if text matches a given hash (timing-safe comparison)."""
    return compare_hash(body.text, body.hash, body.algorithm)


@router.get("", summary="Quick hash via GET")
@limiter.limit("60/minute")
async def quick_hash(
    request: Request,
    text: str = Query(..., description="Text to hash"),
    algorithm: str = Query("sha256", description="Algorithm"),
):
    """Quick hash generation via GET request."""
    return generate_hash(text, algorithm)
