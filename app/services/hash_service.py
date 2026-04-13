import hashlib
import hmac
import secrets
import string
import uuid


def generate_hash(text: str, algorithm: str = "sha256") -> dict:
    """Generate hash of text using specified algorithm."""
    text_bytes = text.encode("utf-8")

    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha224": hashlib.sha224,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
        "sha3_256": hashlib.sha3_256,
        "sha3_512": hashlib.sha3_512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
    }

    if algorithm not in algorithms:
        return {
            "error": f"Unknown algorithm: {algorithm}",
            "available": list(algorithms.keys()),
        }

    hash_obj = algorithms[algorithm](text_bytes)
    return {
        "algorithm": algorithm,
        "hash": hash_obj.hexdigest(),
        "length": len(hash_obj.hexdigest()),
        "input_length": len(text),
    }


def generate_all_hashes(text: str) -> dict:
    """Generate hashes using all available algorithms."""
    text_bytes = text.encode("utf-8")
    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
        "sha3_256": hashlib.sha3_256,
        "sha3_512": hashlib.sha3_512,
    }

    results = {}
    for name, func in algorithms.items():
        results[name] = func(text_bytes).hexdigest()

    return {
        "input_length": len(text),
        "hashes": results,
    }


def generate_hmac(text: str, key: str, algorithm: str = "sha256") -> dict:
    """Generate HMAC signature."""
    try:
        h = hmac.new(key.encode("utf-8"), text.encode("utf-8"), getattr(hashlib, algorithm))
        return {
            "algorithm": f"hmac-{algorithm}",
            "hmac": h.hexdigest(),
        }
    except AttributeError:
        return {"error": f"Unknown algorithm: {algorithm}"}


def compare_hash(text: str, hash_value: str, algorithm: str = "sha256") -> dict:
    """Compare text against a hash value."""
    result = generate_hash(text, algorithm)
    if "error" in result:
        return result

    matches = hmac.compare_digest(result["hash"], hash_value.lower())
    return {
        "matches": matches,
        "algorithm": algorithm,
        "provided_hash": hash_value.lower(),
        "computed_hash": result["hash"],
    }


def generate_password(
    length: int = 16,
    uppercase: bool = True,
    lowercase: bool = True,
    digits: bool = True,
    special: bool = True,
    exclude_ambiguous: bool = False,
    count: int = 1,
) -> dict:
    """Generate secure random password(s)."""
    if length < 4:
        return {"error": "Password length must be at least 4"}
    if length > 256:
        return {"error": "Password length must not exceed 256"}
    if count < 1 or count > 50:
        return {"error": "Count must be between 1 and 50"}

    chars = ""
    required = []

    up_chars = string.ascii_uppercase
    lo_chars = string.ascii_lowercase
    di_chars = string.digits
    sp_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        ambiguous = "0O1lI"
        up_chars = "".join(c for c in up_chars if c not in ambiguous)
        lo_chars = "".join(c for c in lo_chars if c not in ambiguous)
        di_chars = "".join(c for c in di_chars if c not in ambiguous)

    if uppercase:
        chars += up_chars
        required.append(secrets.choice(up_chars))
    if lowercase:
        chars += lo_chars
        required.append(secrets.choice(lo_chars))
    if digits:
        chars += di_chars
        required.append(secrets.choice(di_chars))
    if special:
        chars += sp_chars
        required.append(secrets.choice(sp_chars))

    if not chars:
        return {"error": "At least one character type must be enabled"}

    passwords = []
    for _ in range(count):
        remaining = length - len(required)
        pwd = required.copy() + [secrets.choice(chars) for _ in range(remaining)]
        # Shuffle to randomize position of required chars
        pwd_list = list(pwd)
        # Fisher-Yates shuffle using secrets
        for i in range(len(pwd_list) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            pwd_list[i], pwd_list[j] = pwd_list[j], pwd_list[i]
        passwords.append("".join(pwd_list))

    # Calculate entropy
    entropy = round(length * (len(chars)).bit_length(), 2)

    result = {
        "length": length,
        "entropy_bits": entropy,
        "charset_size": len(chars),
        "settings": {
            "uppercase": uppercase,
            "lowercase": lowercase,
            "digits": digits,
            "special": special,
            "exclude_ambiguous": exclude_ambiguous,
        },
    }

    if count == 1:
        result["password"] = passwords[0]
    else:
        result["passwords"] = passwords
        result["count"] = count

    return result


def generate_uuid_v4(count: int = 1) -> dict:
    """Generate UUID v4."""
    if count < 1 or count > 100:
        return {"error": "Count must be between 1 and 100"}

    uuids = [str(uuid.uuid4()) for _ in range(count)]

    if count == 1:
        return {"uuid": uuids[0], "version": 4}
    return {"uuids": uuids, "version": 4, "count": count}


def generate_token(length: int = 32, encoding: str = "hex") -> dict:
    """Generate secure random token."""
    if length < 8 or length > 512:
        return {"error": "Length must be between 8 and 512"}

    if encoding == "hex":
        token = secrets.token_hex(length // 2)
    elif encoding == "urlsafe":
        token = secrets.token_urlsafe(length)
    elif encoding == "base64":
        import base64
        token = base64.b64encode(secrets.token_bytes(length)).decode()
    else:
        return {"error": f"Unknown encoding: {encoding}. Use hex, urlsafe, or base64"}

    return {
        "token": token,
        "encoding": encoding,
        "length": len(token),
    }
