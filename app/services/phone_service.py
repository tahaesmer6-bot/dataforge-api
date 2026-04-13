import phonenumbers
from phonenumbers import (
    geocoder,
    carrier,
    timezone as pn_timezone,
    PhoneNumberFormat,
)


def validate_phone(phone: str, country_code: str = None) -> dict:
    """Validate and analyze a phone number."""
    try:
        # Parse the number
        if country_code:
            parsed = phonenumbers.parse(phone, country_code.upper())
        else:
            parsed = phonenumbers.parse(phone)

        # Validation checks
        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)

        # Format in various styles
        formats = {}
        if is_valid:
            formats = {
                "e164": phonenumbers.format_number(parsed, PhoneNumberFormat.E164),
                "international": phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL),
                "national": phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL),
                "rfc3966": phonenumbers.format_number(parsed, PhoneNumberFormat.RFC3966),
            }

        # Get additional info
        number_type_map = {
            0: "FIXED_LINE",
            1: "MOBILE",
            2: "FIXED_LINE_OR_MOBILE",
            3: "TOLL_FREE",
            4: "PREMIUM_RATE",
            5: "SHARED_COST",
            6: "VOIP",
            7: "PERSONAL_NUMBER",
            8: "PAGER",
            9: "UAN",
            10: "VOICEMAIL",
            27: "EMERGENCY",
            28: "SHORT_CODE",
            29: "STANDARD_RATE",
        }

        num_type = phonenumbers.number_type(parsed)
        type_str = number_type_map.get(num_type, "UNKNOWN")

        # Location
        location = geocoder.description_for_number(parsed, "en")

        # Carrier
        carrier_name = carrier.name_for_number(parsed, "en")

        # Timezone
        timezones = list(pn_timezone.time_zones_for_number(parsed))

        return {
            "valid": is_valid,
            "possible": is_possible,
            "phone": phone,
            "country_code": parsed.country_code,
            "national_number": str(parsed.national_number),
            "type": type_str,
            "location": location or None,
            "carrier": carrier_name or None,
            "timezones": timezones,
            "formats": formats,
        }

    except phonenumbers.NumberParseException as e:
        return {
            "valid": False,
            "phone": phone,
            "error": str(e),
        }
