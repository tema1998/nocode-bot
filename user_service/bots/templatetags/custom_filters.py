import re
from datetime import datetime

from django import template


register = template.Library()


@register.filter
def iso_to_pretty(value, format_string="%d.%m.%Y %H:%M"):
    """
    Convert ISO format datetime string to a human-readable format.

    Args:
        value: Input string in ISO format (e.g., "2025-04-18T13:36:40.596863")
        format_string: strftime compatible format string (default: "%d.%m.%Y %H:%M")

    Returns:
        str: Formatted datetime string if parsing succeeds, original string if parsing fails,
             or "-" if input is empty/None

    Examples:
        {{ "2025-04-18T13:36:40.596863"|iso_to_pretty }} → "18.04.2025 13:36"
        {{ "2025-04-18T13:36:40"|iso_to_pretty:"%Y-%m-%d" }} → "2025-04-18"
        {{ None|iso_to_pretty }} → "-"
    """
    # Return placeholder if input is empty
    if not value:
        return "-"

    try:
        # Remove microseconds if present
        clean_str = re.sub(r"\.\d+", "", str(value))
        # Parse the ISO format string
        dt = datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime(format_string)
    except ValueError:
        try:
            # Fallback to fromisoformat for more flexible parsing
            dt = datetime.fromisoformat(str(value))
            return dt.strftime(format_string)
        except ValueError:
            # Return original string if all parsing attempts fail
            return str(value)
