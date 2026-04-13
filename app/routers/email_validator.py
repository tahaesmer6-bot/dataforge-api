from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.email_service import full_validate

router = APIRouter()


class EmailRequest(BaseModel):
    email: str = Field(..., description="Email address to validate", example="user@example.com")


class BulkEmailRequest(BaseModel):
    emails: list[str] = Field(
        ...,
        description="List of email addresses to validate (max 50)",
        max_length=50,
        example=["user@gmail.com", "test@mailinator.com"],
    )


@router.post("", summary="Validate a single email address")
@limiter.limit("30/minute")
async def validate_email(request: Request, body: EmailRequest):
    """
    Full email validation including:
    - Syntax validation
    - Disposable email detection
    - MX record verification
    - Domain existence check
    - Free provider detection
    - Role-based email detection
    - Quality score (0-100)
    """
    return full_validate(body.email)


@router.get("", summary="Validate email via query parameter")
@limiter.limit("30/minute")
async def validate_email_get(
    request: Request,
    email: str = Query(..., description="Email address to validate"),
):
    """Validate email via GET request."""
    return full_validate(email)


@router.post("/bulk", summary="Validate multiple emails at once")
@limiter.limit("10/minute")
async def validate_emails_bulk(request: Request, body: BulkEmailRequest):
    """
    Validate up to 50 email addresses in a single request.
    Returns validation results for each email.
    """
    results = []
    for email in body.emails:
        results.append(full_validate(email))

    valid_count = sum(1 for r in results if r["valid"])

    return {
        "total": len(results),
        "valid": valid_count,
        "invalid": len(results) - valid_count,
        "results": results,
    }
