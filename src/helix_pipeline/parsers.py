from __future__ import annotations

from datetime import date, datetime, timezone


DATE_FORMATS = ("%Y-%m-%d", "%d-%b-%Y", "%m/%d/%Y")


def parse_origination_date(value: str | None) -> date | None:
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_timestamp_utc(value: str | None) -> datetime | None:
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed

    return parsed.astimezone(timezone.utc).replace(tzinfo=None)
