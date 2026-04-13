import re
import httpx
from urllib.parse import urlparse


async def validate_url(url: str, check_live: bool = False) -> dict:
    """Validate URL and optionally check if it's live."""
    result = {
        "url": url,
        "valid_format": False,
    }

    # Basic format validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)

        has_scheme = parsed.scheme in ("http", "https", "ftp", "ftps")
        has_netloc = bool(parsed.netloc)
        result["valid_format"] = has_scheme and has_netloc

        result["parsed"] = {
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query or None,
            "fragment": parsed.fragment or None,
        }

        # Extract domain info
        domain = parsed.netloc.split(":")[0]  # Remove port if present
        port = parsed.port
        result["domain"] = domain
        result["port"] = port

        # Check for IP address
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        result["is_ip"] = bool(ip_pattern.match(domain))

        # Protocol info
        result["is_https"] = parsed.scheme == "https"

    except Exception as e:
        result["error"] = f"Parse error: {str(e)}"
        return result

    if not result["valid_format"]:
        return result

    # Live check
    if check_live:
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=10.0,
                verify=False,
            ) as client:
                response = await client.head(url)
                result["live_check"] = {
                    "reachable": True,
                    "status_code": response.status_code,
                    "final_url": str(response.url),
                    "redirected": str(response.url) != url,
                    "content_type": response.headers.get("content-type"),
                    "server": response.headers.get("server"),
                }
        except httpx.TimeoutException:
            result["live_check"] = {
                "reachable": False,
                "error": "Connection timed out",
            }
        except httpx.ConnectError:
            result["live_check"] = {
                "reachable": False,
                "error": "Connection refused or DNS failure",
            }
        except Exception as e:
            result["live_check"] = {
                "reachable": False,
                "error": str(e),
            }

    return result
