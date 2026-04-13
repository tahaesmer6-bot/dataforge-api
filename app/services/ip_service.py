import socket
import json
import os


# Fallback IP lookup using ip-api.com (free, no key needed, 45 req/min)
import httpx


async def lookup_ip(ip: str) -> dict:
    """Look up IP geolocation information."""
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        return {
            "ip": ip,
            "error": "Cannot lookup localhost/loopback addresses",
        }

    # Validate IP format
    try:
        socket.inet_aton(ip)
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip)
        except socket.error:
            return {"ip": ip, "error": "Invalid IP address format"}

    # Use free ip-api.com service
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={
                    "fields": "status,message,country,countryCode,region,regionName,"
                              "city,zip,lat,lon,timezone,isp,org,as,asname,mobile,"
                              "proxy,hosting,query"
                },
            )
            data = response.json()

            if data.get("status") == "fail":
                return {
                    "ip": ip,
                    "error": data.get("message", "Lookup failed"),
                }

            return {
                "ip": data.get("query", ip),
                "location": {
                    "country": data.get("country"),
                    "country_code": data.get("countryCode"),
                    "region": data.get("regionName"),
                    "region_code": data.get("region"),
                    "city": data.get("city"),
                    "zip": data.get("zip"),
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon"),
                    "timezone": data.get("timezone"),
                },
                "network": {
                    "isp": data.get("isp"),
                    "organization": data.get("org"),
                    "as_number": data.get("as"),
                    "as_name": data.get("asname"),
                },
                "flags": {
                    "is_mobile": data.get("mobile", False),
                    "is_proxy": data.get("proxy", False),
                    "is_hosting": data.get("hosting", False),
                },
            }

    except httpx.TimeoutException:
        return {"ip": ip, "error": "Lookup service timed out"}
    except Exception as e:
        return {"ip": ip, "error": f"Lookup failed: {str(e)}"}


async def get_caller_ip(request) -> str:
    """Extract caller IP from request headers."""
    # Check common proxy headers
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"
