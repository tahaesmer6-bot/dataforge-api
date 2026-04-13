import re
import dns.resolver
from app.services.disposable_domains import is_disposable


EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

# Common free email providers
FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "mail.com", "protonmail.com", "proton.me", "zoho.com",
    "yandex.com", "yandex.ru", "gmx.com", "gmx.net", "live.com",
    "msn.com", "me.com", "mac.com", "fastmail.com", "tutanota.com",
    "inbox.com", "mail.ru", "seznam.cz", "wp.pl", "o2.pl",
}

# Common role-based prefixes
ROLE_PREFIXES = {
    "admin", "administrator", "webmaster", "postmaster", "hostmaster",
    "info", "support", "sales", "contact", "help", "abuse",
    "noreply", "no-reply", "mailer-daemon", "marketing", "media",
    "office", "billing", "compliance", "legal", "hr", "jobs",
    "careers", "recruitment", "press", "security", "privacy",
    "feedback", "newsletter", "subscribe", "unsubscribe",
}


def validate_syntax(email: str) -> dict:
    """Validate email syntax and extract parts."""
    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        return {"valid": False, "reason": "Invalid email format"}

    if len(email) > 254:
        return {"valid": False, "reason": "Email too long (max 254 chars)"}

    local, domain = email.rsplit("@", 1)

    if len(local) > 64:
        return {"valid": False, "reason": "Local part too long (max 64 chars)"}

    if ".." in email:
        return {"valid": False, "reason": "Consecutive dots not allowed"}

    return {
        "valid": True,
        "email": email,
        "local": local,
        "domain": domain,
    }


def check_mx_records(domain: str) -> dict:
    """Check if domain has valid MX records."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        records = []
        for mx in mx_records:
            records.append({
                "priority": mx.preference,
                "host": str(mx.exchange).rstrip("."),
            })
        records.sort(key=lambda x: x["priority"])
        return {"has_mx": True, "mx_records": records}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"has_mx": False, "mx_records": []}
    except dns.resolver.NoNameservers:
        return {"has_mx": False, "mx_records": [], "error": "No nameservers found"}
    except Exception:
        return {"has_mx": False, "mx_records": [], "error": "DNS lookup failed"}


def check_domain_exists(domain: str) -> bool:
    """Check if domain has any DNS records at all."""
    try:
        dns.resolver.resolve(domain, "A")
        return True
    except Exception:
        try:
            dns.resolver.resolve(domain, "AAAA")
            return True
        except Exception:
            return False


def full_validate(email: str) -> dict:
    """Run complete email validation."""
    # Syntax check
    syntax = validate_syntax(email)
    if not syntax["valid"]:
        return {
            "email": email,
            "valid": False,
            "reason": syntax["reason"],
            "score": 0,
            "checks": {"syntax": False},
        }

    domain = syntax["domain"]
    local = syntax["local"]
    checks = {"syntax": True}
    score = 20  # Base score for valid syntax
    warnings = []

    # Disposable check
    disposable = is_disposable(domain)
    checks["disposable"] = not disposable
    if disposable:
        warnings.append("Disposable/temporary email detected")
        score -= 30
    else:
        score += 20

    # Free provider check
    is_free = domain in FREE_PROVIDERS
    checks["free_provider"] = is_free
    if is_free:
        warnings.append("Free email provider")

    # Role-based check
    is_role = local.split(".")[0] in ROLE_PREFIXES or local.split("-")[0] in ROLE_PREFIXES
    checks["role_based"] = is_role
    if is_role:
        warnings.append("Role-based email address")
        score -= 5

    # MX records
    mx_result = check_mx_records(domain)
    checks["mx_records"] = mx_result["has_mx"]
    if mx_result["has_mx"]:
        score += 30
    else:
        warnings.append("No MX records found")
        score -= 20

    # Domain exists
    domain_exists = check_domain_exists(domain)
    checks["domain_exists"] = domain_exists
    if domain_exists:
        score += 20
    else:
        warnings.append("Domain does not resolve")
        score -= 30

    # Has dots in local part (common in real emails)
    if "." in local:
        score += 5

    # Reasonable length
    if 3 <= len(local) <= 30:
        score += 5

    # Clamp score
    score = max(0, min(100, score))

    # Determine overall validity
    valid = score >= 40 and not disposable and mx_result["has_mx"]

    return {
        "email": syntax["email"],
        "valid": valid,
        "score": score,
        "checks": checks,
        "details": {
            "local_part": local,
            "domain": domain,
            "is_disposable": disposable,
            "is_free_provider": is_free,
            "is_role_based": is_role,
            "mx_records": mx_result.get("mx_records", []),
            "domain_exists": domain_exists,
        },
        "warnings": warnings,
    }
