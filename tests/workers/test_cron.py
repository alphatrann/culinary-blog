from datetime import UTC, datetime, timedelta, timezone

from culinary_blog.workers.cron import seconds_until_next_run


def test_before_two_am_utc_waits_until_today_two_am():
    assert seconds_until_next_run(datetime(2026, 10, 27, 1, 0, tzinfo=UTC)) == 3600


def test_after_two_am_utc_waits_until_tomorrow_two_am():
    assert seconds_until_next_run(datetime(2026, 10, 27, 3, 0, tzinfo=UTC)) == 23 * 3600


def test_exactly_two_am_waits_a_full_day():
    assert seconds_until_next_run(datetime(2026, 10, 27, 2, 0, tzinfo=UTC)) == 24 * 3600


def test_non_utc_input_is_converted():
    local = datetime(2026, 10, 27, 9, 30, tzinfo=timezone(timedelta(hours=7)))  # 02:30 UTC
    assert seconds_until_next_run(local) == 23.5 * 3600
