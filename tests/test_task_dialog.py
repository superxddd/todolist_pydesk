from datetime import datetime


def parse_due_date(due_text: str) -> tuple[datetime | None, str | None]:
    if not due_text or not due_text.strip():
        return None, None
    try:
        return datetime.strptime(due_text.strip(), "%Y-%m-%d %H:%M"), None
    except ValueError:
        return None, "截止时间格式应为 YYYY-MM-DD HH:MM"


def test_parse_due_date_valid():
    due, error = parse_due_date("2025-04-15 14:30")
    assert error is None
    assert due is not None
    assert due.year == 2025
    assert due.month == 4
    assert due.day == 15
    assert due.hour == 14
    assert due.minute == 30


def test_parse_due_date_empty():
    due, error = parse_due_date("")
    assert error is None
    assert due is None


def test_parse_due_date_whitespace():
    due, error = parse_due_date("   ")
    assert error is None
    assert due is None


def test_parse_due_date_invalid_format_no_time():
    due, error = parse_due_date("2025-04-15")
    assert error == "截止时间格式应为 YYYY-MM-DD HH:MM"
    assert due is None


def test_parse_due_date_invalid_format_wrong_separator():
    due, error = parse_due_date("2025/04/15 14:30")
    assert error == "截止时间格式应为 YYYY-MM-DD HH:MM"
    assert due is None


def test_parse_due_date_invalid_format_wrong_order():
    due, error = parse_due_date("15-04-2025 14:30")
    assert error == "截止时间格式应为 YYYY-MM-DD HH:MM"
    assert due is None


def test_parse_due_date_invalid_format_text():
    due, error = parse_due_date("明天下午")
    assert error == "截止时间格式应为 YYYY-MM-DD HH:MM"
    assert due is None


def test_parse_due_date_invalid_date():
    due, error = parse_due_date("2025-13-45 25:99")
    assert error == "截止时间格式应为 YYYY-MM-DD HH:MM"
    assert due is None
