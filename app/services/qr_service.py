import io
import qrcode
import base64
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H


ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def generate_qr(
    data: str,
    size: int = 10,
    border: int = 4,
    error_correction: str = "M",
    fill_color: str = "black",
    back_color: str = "white",
    image_format: str = "PNG",
) -> dict:
    """Generate QR code and return as base64."""
    if not data:
        return {"error": "Data cannot be empty"}

    if len(data) > 4296:
        return {"error": "Data too long. Max 4296 characters for alphanumeric QR codes."}

    if size < 1 or size > 40:
        return {"error": "Size (box_size) must be between 1 and 40"}

    if border < 0 or border > 20:
        return {"error": "Border must be between 0 and 20"}

    ec = ERROR_LEVELS.get(error_correction.upper(), ERROR_CORRECT_M)

    image_format = image_format.upper()
    if image_format not in ("PNG", "JPEG", "BMP", "GIF"):
        return {"error": "Supported formats: PNG, JPEG, BMP, GIF"}

    try:
        qr = qrcode.QRCode(
            version=None,  # Auto-detect
            error_correction=ec,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format=image_format)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode("utf-8")

        mime_type = f"image/{image_format.lower()}"
        if image_format == "JPEG":
            mime_type = "image/jpeg"

        return {
            "data_url": f"data:{mime_type};base64,{b64}",
            "base64": b64,
            "mime_type": mime_type,
            "format": image_format,
            "qr_version": qr.version,
            "data_length": len(data),
            "image_size": {
                "width": img.pixel_size,
                "height": img.pixel_size,
            },
        }
    except Exception as e:
        return {"error": f"QR generation failed: {str(e)}"}
