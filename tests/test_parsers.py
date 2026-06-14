from datetime import date, datetime

from src.helix_pipeline.parsers import parse_origination_date, parse_timestamp_utc


def test_parse_origination_date_supports_all_known_formats() -> None:
    assert parse_origination_date("2024-06-01") == date(2024, 6, 1)
    assert parse_origination_date("11-Dec-2020") == date(2020, 12, 11)
    assert parse_origination_date("01/13/2020") == date(2020, 1, 13)


def test_parse_origination_date_returns_none_for_bad_input() -> None:
    assert parse_origination_date("2024/99/01") is None
    assert parse_origination_date("") is None


def test_parse_timestamp_utc_normalizes_timezones() -> None:
    assert parse_timestamp_utc("2021-05-13T20:44:00Z") == datetime(2021, 5, 13, 20, 44, 0)
    assert parse_timestamp_utc("2024-06-30T03:58:00-08:00") == datetime(2024, 6, 30, 11, 58, 0)
    assert parse_timestamp_utc("2022-09-08T12:16:00") == datetime(2022, 9, 8, 12, 16, 0)


def test_parse_timestamp_utc_returns_none_for_bad_input() -> None:
    assert parse_timestamp_utc("definitely-not-a-timestamp") is None
