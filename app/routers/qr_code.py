from fastapi import APIRouter, Request, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.qr_service import generate_qr
import base64

router = APIRouter()


class QRRequest(BaseModel):
    data: str = Field(..., description="Data to encode in QR code", max_length=4296, example="https://example.com")
    size: int = Field(10, ge=1, le=40, description="Box size (pixel size of each QR module)")
    border: int = Field(4, ge=0, le=20, description="Border width in modules")
    error_correction: str = Field("M", description="Error correction level: L, M, Q, H")
    fill_color: str = Field("black", description="QR code color", example="black")
    back_color: str = Field("white", description="Background color", example="white")
    format: str = Field("PNG", description="Image format: PNG, JPEG, BMP, GIF")


@router.post("", summary="Generate QR code (base64)")
@limiter.limit("30/minute")
async def create_qr(request: Request, body: QRRequest):
    """
    Generate a QR code and return as base64-encoded image.
    Supports custom colors, sizes, error correction levels, and formats.
    """
    return generate_qr(
        data=body.data,
        size=body.size,
        border=body.border,
        error_correction=body.error_correction,
        fill_color=body.fill_color,
        back_color=body.back_color,
        image_format=body.format,
    )


@router.get("", summary="Generate QR code image directly")
@limiter.limit("30/minute")
async def create_qr_image(
    request: Request,
    data: str = Query(..., description="Data to encode", max_length=4296),
    size: int = Query(10, ge=1, le=40),
    border: int = Query(4, ge=0, le=20),
    error_correction: str = Query("M"),
    fill_color: str = Query("black"),
    back_color: str = Query("white"),
    format: str = Query("PNG"),
):
    """Generate QR code and return as direct image response."""
    result = generate_qr(
        data=data,
        size=size,
        border=border,
        error_correction=error_correction,
        fill_color=fill_color,
        back_color=back_color,
        image_format=format,
    )

    if "error" in result:
        return result

    # Return actual image
    img_bytes = base64.b64decode(result["base64"])
    return Response(
        content=img_bytes,
        media_type=result["mime_type"],
        headers={"Content-Disposition": f'inline; filename="qr.{format.lower()}"'},
    )
