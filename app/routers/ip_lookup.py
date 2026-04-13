from fastapi import APIRouter, Request, Query
from app.middleware.rate_limiter import limiter
from app.services.ip_service import lookup_ip, get_caller_ip

router = APIRouter()


@router.get("", summary="Lookup IP geolocation")
@limiter.limit("30/minute")
async def ip_lookup(
    request: Request,
    ip: str = Query(..., description="IP address to lookup", example="8.8.8.8"),
):
    """
    Get geolocation and network info for an IP address:
    - Country, region, city, coordinates
    - ISP and organization
    - Proxy/VPN/hosting detection
    - Timezone
    """
    return await lookup_ip(ip)


@router.get("/me", summary="Lookup caller's IP")
@limiter.limit("30/minute")
async def my_ip(request: Request):
    """Get geolocation info for the calling IP address."""
    caller_ip = await get_caller_ip(request)
    result = await lookup_ip(caller_ip)
    result["your_ip"] = caller_ip
    return result
