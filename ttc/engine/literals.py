"""Helpers for formatting raw English-captured values as Python literals."""


def format_literal(value: str) -> str:
    """Format a raw value as a Python literal (number, bool, None, or string)."""
    value = (value or "").strip()
    if not value:
        return '""'
    try:
        int(value)
        return value
    except ValueError:
        pass
    try:
        float(value)
        return value
    except ValueError:
        pass
    if value.lower() in ("true", "false"):
        return value.capitalize()
    if value.lower() == "none":
        return "None"
    if ((value.startswith('"') and value.endswith('"')) or
            (value.startswith("'") and value.endswith("'"))):
        return value
    return f'"{value}"'


def format_index(key: str) -> str:
    """Format a list index or dict key for subscript access."""
    key = (key or "").strip()
    if key and key.lstrip("-").isdigit():
        return key
    escaped = key.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'
