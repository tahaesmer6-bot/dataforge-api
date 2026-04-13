from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.middleware.rate_limiter import limiter
from app.routers import (
    email_validator,
    text_analyzer,
    hash_tools,
    generators,
    qr_code,
    url_validator,
    ip_lookup,
    phone_validator,
)

settings = get_settings()

app = FastAPI(
    title="DataForge API",
    description=(
        "All-in-one data validation, analysis & generation API. "
        "Email validation, text analysis, QR codes, hashing, "
        "password generation, IP geolocation, phone validation & more."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# RapidAPI proxy secret verification (optional)
@app.middleware("http")
async def verify_rapidapi_proxy(request: Request, call_next):
    if settings.rapidapi_proxy_secret:
        proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
        if proxy_secret != settings.rapidapi_proxy_secret:
            # Allow docs access without auth
            if request.url.path not in ("/docs", "/redoc", "/openapi.json", "/", "/health"):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Unauthorized. Subscribe via RapidAPI."},
                )
    return await call_next(request)


# Include routers
app.include_router(email_validator.router, prefix="/validate/email", tags=["Email Validation"])
app.include_router(phone_validator.router, prefix="/validate/phone", tags=["Phone Validation"])
app.include_router(url_validator.router, prefix="/validate/url", tags=["URL Validation"])
app.include_router(text_analyzer.router, prefix="/analyze/text", tags=["Text Analysis"])
app.include_router(hash_tools.router, prefix="/hash", tags=["Hashing"])
app.include_router(generators.router, prefix="/generate", tags=["Generators"])
app.include_router(qr_code.router, prefix="/qr", tags=["QR Code"])
app.include_router(ip_lookup.router, prefix="/lookup/ip", tags=["IP Lookup"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "DataForge API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "email_validation": "/validate/email",
            "phone_validation": "/validate/phone",
            "url_validation": "/validate/url",
            "text_analysis": "/analyze/text",
            "hashing": "/hash",
            "generators": "/generate",
            "qr_code": "/qr",
            "ip_lookup": "/lookup/ip",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
