#!/usr/bin/env python3
"""Fetch Garmin sleep data using the garminconnect package.

Usage:
    python fetch_sleep_data.py
    python fetch_sleep_data.py --date 2026-05-13
    python fetch_sleep_data.py --days 7 --summary-only
    python fetch_sleep_data.py --date 2026-05-13 --output sleep.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    from garminconnect import Garmin
except ImportError:  # pragma: no cover - exercised only when dependency is missing.
    Garmin = None


TOKEN_DIR = str(Path.home() / ".garminconnect")


def login() -> Any:
    """Login to Garmin Connect and reuse saved garminconnect tokens when present."""
    if Garmin is None:
        raise RuntimeError(
            "Missing garminconnect. Install it with: "
            'pip install --upgrade "garminconnect" curl_cffi'
        )

    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    if not email or not password:
        raise RuntimeError(
            "Missing GARMIN_EMAIL or GARMIN_PASSWORD environment variables."
        )

    client = Garmin(
        email,
        password,
        prompt_mfa=lambda: input("Garmin MFA code: "),
    )
    client.login(TOKEN_DIR)
    return client


def parse_date(value: str) -> date:
    """Parse an ISO date string for argparse."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected YYYY-MM-DD."
        ) from exc


def date_range(end_date: date, days: int) -> list[date]:
    """Return an inclusive date range ending at end_date."""
    if days < 1:
        raise argparse.ArgumentTypeError("--days must be at least 1.")
    start_date = end_date - timedelta(days=days - 1)
    return [start_date + timedelta(days=offset) for offset in range(days)]


def get_nested(data: dict[str, Any], *keys: str) -> Any:
    """Read a nested value without raising when Garmin omits a section."""
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def sleep_payload(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Return the field container used by the Garmin sleep endpoint."""
    daily_sleep = raw_data.get("dailySleepDTO")
    if isinstance(daily_sleep, dict):
        return daily_sleep
    return raw_data


def seconds_to_hours(seconds: Any) -> float | None:
    """Convert Garmin second fields into rounded hours."""
    if seconds is None:
        return None
    try:
        return round(float(seconds) / 3600.0, 2)
    except (TypeError, ValueError):
        return None


def sleep_score(raw_data: dict[str, Any], payload: dict[str, Any]) -> Any:
    """Extract the most common Garmin sleep score shapes."""
    direct_score = payload.get("sleepScore") or payload.get("overallScore")
    if direct_score is not None:
        return direct_score

    sleep_scores = payload.get("sleepScores") or raw_data.get("sleepScores")
    if isinstance(sleep_scores, dict):
        return get_nested(sleep_scores, "overall", "value")
    return None


def summarize_sleep(raw_data: dict[str, Any], target_date: date) -> dict[str, Any]:
    """Build a compact summary while preserving access to raw data separately."""
    payload = sleep_payload(raw_data)

    return {
        "date": str(target_date),
        "calendar_date": payload.get("calendarDate") or raw_data.get("calendarDate"),
        "sleep_start": payload.get("sleepStartTimestampLocal")
        or payload.get("sleepStartTimestampGMT"),
        "sleep_end": payload.get("sleepEndTimestampLocal")
        or payload.get("sleepEndTimestampGMT"),
        "sleep_score": sleep_score(raw_data, payload),
        "duration_hours": {
            "total": seconds_to_hours(payload.get("sleepTimeSeconds")),
            "deep": seconds_to_hours(payload.get("deepSleepSeconds")),
            "light": seconds_to_hours(payload.get("lightSleepSeconds")),
            "rem": seconds_to_hours(payload.get("remSleepSeconds")),
            "awake": seconds_to_hours(payload.get("awakeSleepSeconds")),
            "unmeasurable": seconds_to_hours(payload.get("unmeasurableSleepSeconds")),
        },
        "sleep_heart_rate": {
            "average": payload.get("averageSleepHeartRate"),
            "lowest": payload.get("lowestSleepHeartRate"),
            "highest": payload.get("highestSleepHeartRate"),
        },
        "respiration": {
            "average": payload.get("averageSleepRespiration"),
            "lowest": payload.get("lowestSleepRespiration"),
            "highest": payload.get("highestSleepRespiration"),
        },
        "spo2": {
            "average": payload.get("averageSpO2"),
            "lowest": payload.get("lowestSpO2"),
        },
        "hrv": {
            "average": payload.get("avgSleepHrv"),
            "status": payload.get("hrvStatus"),
        },
        "body_battery_change": payload.get("bodyBatteryChange"),
        "sleep_feedback": payload.get("sleepFeedback"),
        "phase_count": len(raw_data.get("sleepLevels") or []),
        "movement_count": len(raw_data.get("sleepMovement") or []),
    }


def fetch_sleep_record(
    client: Any,
    target_date: date,
    include_raw: bool,
) -> dict[str, Any]:
    """Fetch and format sleep data for a single date."""
    raw_data = client.get_sleep_data(str(target_date))
    if not raw_data:
        return {
            "date": str(target_date),
            "status": "missing",
            "summary": None,
        }

    record = {
        "date": str(target_date),
        "status": "ok",
        "summary": summarize_sleep(raw_data, target_date),
    }
    if include_raw:
        record["raw"] = raw_data
    return record


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Garmin sleep data through garminconnect. The date represents "
            "the sleep session ending on that date."
        )
    )
    parser.add_argument(
        "--date",
        type=parse_date,
        default=date.today(),
        help="End date for the sleep session in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to fetch ending at --date. Defaults to 1.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Exclude the raw Garmin response from the JSON output.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path for the JSON output. Prints to stdout by default.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON without indentation.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        targets = date_range(args.date, args.days)
        client = login()
        records = [
            fetch_sleep_record(
                client=client,
                target_date=target,
                include_raw=not args.summary_only,
            )
            for target in targets
        ]
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output = {
        "source": "garminconnect",
        "token_dir": TOKEN_DIR,
        "record_count": len(records),
        "records": records,
    }

    indent = None if args.compact else 2
    text = json.dumps(output, indent=indent, sort_keys=True, default=str)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
