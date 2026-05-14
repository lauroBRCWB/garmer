#!/usr/bin/env python3

import argparse
import os
from pathlib import Path

from garminconnect import Garmin
from garminconnect.workout import (
    RunningWorkout,
    WorkoutSegment,
    create_warmup_step,
    create_interval_step,
    create_recovery_step,
    create_cooldown_step,
    create_repeat_group,
)


TOKEN_DIR = str(Path.home() / ".garminconnect")


def login() -> Garmin:
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

    # First run creates saved tokens. Later runs reuse them.
    client.login(TOKEN_DIR)
    return client


def build_running_interval_workout(
    name: str,
    warmup_min: int,
    interval_min: int,
    recovery_min: int,
    repeats: int,
    cooldown_min: int,
) -> RunningWorkout:
    """
    Creates a workout like:

    Warmup
    Repeat N times:
      - Run interval
      - Recovery
    Cooldown
    """

    warmup_sec = warmup_min * 60
    interval_sec = interval_min * 60
    recovery_sec = recovery_min * 60
    cooldown_sec = cooldown_min * 60

    repeat_group = create_repeat_group(
        iterations=repeats,
        step_order=2,
        workout_steps=[
            create_interval_step(interval_sec, step_order=1),
            create_recovery_step(recovery_sec, step_order=2),
        ],
    )

    steps = [
        create_warmup_step(warmup_sec, step_order=1),
        repeat_group,
        create_cooldown_step(cooldown_sec, step_order=3),
    ]

    total_seconds = (
        warmup_sec
        + repeats * (interval_sec + recovery_sec)
        + cooldown_sec
    )

    return RunningWorkout(
        workoutName=name,
        estimatedDurationInSecs=total_seconds,
        description=(
            f"{warmup_min}min warmup, "
            f"{repeats}x({interval_min}min interval + {recovery_min}min recovery), "
            f"{cooldown_min}min cooldown"
        ),
        workoutSegments=[
            WorkoutSegment(
                segmentOrder=1,
                sportType={
                    "sportTypeId": 1,
                    "sportTypeKey": "running",
                    "displayOrder": 1,
                },
                workoutSteps=steps,
            )
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create and optionally schedule a Garmin running workout."
    )

    parser.add_argument("--name", default="Interval Run")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup minutes")
    parser.add_argument("--interval", type=int, default=3, help="Interval minutes")
    parser.add_argument("--recovery", type=int, default=2, help="Recovery minutes")
    parser.add_argument("--repeats", type=int, default=5, help="Number of repeats")
    parser.add_argument("--cooldown", type=int, default=10, help="Cooldown minutes")
    parser.add_argument(
        "--date",
        help="Optional schedule date in YYYY-MM-DD format, e.g. 2026-05-09",
    )

    args = parser.parse_args()

    client = login()

    workout = build_running_interval_workout(
        name=args.name,
        warmup_min=args.warmup,
        interval_min=args.interval,
        recovery_min=args.recovery,
        repeats=args.repeats,
        cooldown_min=args.cooldown,
    )

    result = client.upload_running_workout(workout)

    workout_id = result.get("workoutId") or result.get("workout", {}).get("workoutId")

    print("Workout uploaded successfully.")
    print(f"Garmin response: {result}")

    if not workout_id:
        print("Could not find workoutId in Garmin response. Not scheduling.")
        return

    print(f"Workout ID: {workout_id}")

    if args.date:
        schedule_result = client.schedule_workout(workout_id, args.date)
        print(f"Workout scheduled for {args.date}.")
        print(f"Schedule response: {schedule_result}")


if __name__ == "__main__":
    main()