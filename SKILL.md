---
name: garmer
description: Extract health and fitness data from Garmin Connect including activities, sleep, heart rate, stress, steps, body composition, and training plans. Also supports direct sleep fetches and structured workout creation through Python helpers using the garminconnect API wrapper.
license: MIT
compatibility: Requires Python 3.10+, pip/uv for installation. Requires Garmin Connect account credentials for authentication. Direct sleep fetches require the garminconnect Python package. Workout creation requires the garminconnect Python package with workout support.
metadata:
  author: MoltBot Team
  version: "0.1.0"
  moltbot:
    emoji: "⌚"
    primaryEnv: "GARMER_TOKEN_DIR"
    requires:
      bins:
        - garmer
    install:
      - id: uv
        kind: uv
        package: garmer
        bins:
          - garmer
        label: Install garmer (uv)
      - id: pip
        kind: pip
        package: garmer
        bins:
          - garmer
        label: Install garmer (pip)
---

# Garmer - Garmin Data Extraction Skill

This skill enables extraction of health and fitness data from Garmin Connect for analysis and insights.

It also documents a Python helper workflow for creating structured Garmin running workouts, such as interval sessions, VO2 max workouts, threshold workouts, and scheduled workouts.

## Prerequisites

1. A Garmin Connect account with health data
2. The `garmer` CLI tool installed for data extraction
3. For direct sleep fetches, the community `garminconnect` Python package.
4. For workout creation, the community `garminconnect` Python package with workout support:

```bash
python3 -m venv .venv --copies
source .venv/bin/activate
pip install --upgrade "garminconnect[workout]" curl_cffi
```

> Important: Garmin does not provide a broadly available public personal workout-creation API. Workout creation here uses the community `garminconnect` package and may break if Garmin changes internal endpoints.

## Authentication (One-Time Setup)

Before using garmer, authenticate with Garmin Connect:

```bash
garmer login
```

This will prompt for your Garmin Connect email and password. Tokens are saved to `~/.garmer/garmin_tokens` for future use.

To check authentication status:

```bash
garmer status
```

For the direct `garminconnect` helper scripts, set Garmin credentials as environment variables:

```bash
export GARMIN_EMAIL="your@email.com"
export GARMIN_PASSWORD="your-password"
```

The direct helper scripts store tokens separately by default in `~/.garminconnect`, while the `garmer` CLI stores tokens in `~/.garmer/garmin_tokens`.

## Available Commands

### Daily Summary

Get today's health summary (steps, calories, heart rate, stress):

```bash
garmer summary
# For a specific date:
garmer summary --date 2025-01-15
# Include last night's sleep data:
garmer summary --with-sleep
garmer summary -s
# JSON output for programmatic use:
garmer summary --json
# Combine flags:
garmer summary --date 2025-01-15 --with-sleep --json
```

### Sleep Data

Get sleep analysis (duration, phases, score, HRV):

```bash
garmer sleep
# For a specific date:
garmer sleep --date 2025-01-15
```

For a direct `garminconnect` API fetch, use `fetch_sleep_data.py`. This is useful when the agent needs the raw Garmin response plus a compact summary for one day or a small date range:

```bash
python workspace/skills/garmer/src/garmer/fetch_sleep_data.py --date 2025-01-15

# Reduce tokens by excluding the raw Garmin response:
python workspace/skills/garmer/src/garmer/fetch_sleep_data.py \
  --date 2025-01-15 \
  --summary-only

# Fetch a range ending at the target date:
python workspace/skills/garmer/src/garmer/fetch_sleep_data.py \
  --date 2025-01-15 \
  --days 7 \
  --summary-only
```

The direct helper reads `GARMIN_EMAIL` and `GARMIN_PASSWORD`, reuses tokens from `~/.garminconnect`, calls `client.get_sleep_data("YYYY-MM-DD")`, and emits JSON with `source`, `record_count`, and `records`.

### Activities

List recent fitness activities:

```bash
garmer activities
# Limit number of results:
garmer activities --limit 5
# Filter by specific date:
garmer activities --date 2025-01-15
# JSON output for programmatic use:
garmer activities --json
```

### Activity Detail

Get detailed information for a single activity:

```bash
# Latest activity:
garmer activity
# Specific activity by ID:
garmer activity 12345678
# Include lap data:
garmer activity --laps
# Include heart rate zone data:
garmer activity --zones
# JSON output:
garmer activity --json
# Combine flags:
garmer activity 12345678 --laps --zones --json
```

### Health Snapshot

Get comprehensive health data for a day:

```bash
garmer snapshot
# For a specific date:
garmer snapshot --date 2025-01-15
# As JSON for programmatic use:
garmer snapshot --json
```

### Export Data

Export multiple days of data to JSON:

```bash
# Last 7 days (default)
garmer export

# Custom date range
garmer export --start-date 2025-01-01 --end-date 2025-01-31 --output my_data.json

# Last N days
garmer export --days 14
```

### Training Plans

List active training plans:

```bash
garmer training-plans
# As JSON for programmatic use:
garmer training-plans --json
```

Get details of a specific training plan:

```bash
garmer training-plan <plan-id>
# As JSON:
garmer training-plan <plan-id> --json
```

List available training plan templates:

```bash
garmer training-templates
# Filter by activity type:
garmer training-templates --activity running
# Filter by cycling:
garmer training-templates --activity cycling
# As JSON:
garmer training-templates --json
```

Create a new training plan:

```bash
garmer create-plan \
  --name "Spring Marathon Training" \
  --template-id <template-id> \
  --activity running \
  --goal "Marathon" \
  --start-date 2025-03-01 \
  --level intermediate

# Minimal (uses defaults):
garmer create-plan --name "5K Training" --template-id <id> --activity running

# Full example with cycling:
garmer create-plan \
  --name "Century Ride Prep" \
  --template-id <template-id> \
  --activity cycling \
  --goal "Century Ride" \
  --start-date 2025-04-01 \
  --level advanced \
  --json
```

Mark a workout as completed:

```bash
garmer complete-workout --plan-id <plan-id> --workout-id <workout-id>

# Specify completion date:
garmer complete-workout \
  --plan-id <plan-id> \
  --workout-id <workout-id> \
  --date 2025-01-15
```

### Create Structured Garmin Workouts

Garmer primarily extracts Garmin data. To create structured workouts in Garmin Connect, use a Python helper script based on the `garminconnect` package.

This is useful when the user asks to create workouts such as:

- Interval running workouts
- VO2 max sessions
- Threshold sessions
- Warmup + repeat intervals + cooldown structures
- Scheduled workouts on a specific date

#### Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv --copies
source .venv/bin/activate
pip install --upgrade "garminconnect[workout]" curl_cffi
```

Set Garmin credentials:

```bash
export GARMIN_EMAIL="your@email.com"
export GARMIN_PASSWORD="your-password"
```

#### Script: `create_garmin_workout.py`

```python
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
    Creates a structured running workout:

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
```

#### Usage

Create a workout only:

```bash
python create_garmin_workout.py \
  --name "VO2 max intervals" \
  --warmup 12 \
  --interval 4 \
  --recovery 2 \
  --repeats 5 \
  --cooldown 10
```

Create and schedule a workout:

```bash
python create_garmin_workout.py \
  --name "VO2 max intervals" \
  --warmup 12 \
  --interval 4 \
  --recovery 2 \
  --repeats 5 \
  --cooldown 10 \
  --date 2026-05-09
```

#### Recommended workout creation workflow

When creating a Garmin workout, collect these inputs first:

1. **Sport type**
   - Running, cycling, swimming, strength, etc.
   - Current helper supports running only.

2. **Workout goal**
   - Easy aerobic
   - VO2 max
   - Threshold
   - Long run
   - Recovery
   - Race pace
   - Speed endurance

3. **Workout structure**
   - Warmup duration
   - Work interval duration or distance
   - Recovery duration or distance
   - Number of repeats
   - Cooldown duration

4. **Target type**
   - Duration only
   - Pace target
   - Heart rate zone target
   - Power target
   - Cadence target

5. **Scheduling**
   - Create only
   - Create and schedule to Garmin Calendar

6. **Safety check**
   - Avoid creating hard workouts on consecutive days unless explicitly requested.
   - Check recent activity load, sleep, HRV, resting HR, and recovery if available.

### Utility Commands

```bash
# Update garmer to latest version (git pull):
garmer update

# Show version information:
garmer version
```

## Python API Usage

For more complex data processing, use the Python API:

```python
from garmer import GarminClient
from datetime import date, timedelta

# Use saved tokens
client = GarminClient.from_saved_tokens()

# Or login with credentials
client = GarminClient.from_credentials(email="user@example.com", password="pass")
```

### User Profile

```python
# Get user profile
profile = client.get_user_profile()
print(f"User: {profile.display_name}")

# Get registered devices
devices = client.get_user_devices()
```

### Daily Summary

```python
# Get daily summary (defaults to today)
summary = client.get_daily_summary()
print(f"Steps: {summary.total_steps}")

# Get for specific date
summary = client.get_daily_summary(date(2025, 1, 15))

# Get weekly summary
weekly = client.get_weekly_summary()
```

### Sleep Data

```python
# Get sleep data (defaults to today)
sleep = client.get_sleep()
print(f"Sleep: {sleep.total_sleep_hours:.1f} hours")

# Get last night's sleep
sleep = client.get_last_night_sleep()

# Get sleep for date range
sleep_data = client.get_sleep_range(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 7)
)
```

### Activities

```python
# Get recent activities
activities = client.get_recent_activities(limit=5)
for activity in activities:
    print(f"{activity.activity_name}: {activity.distance_km:.1f} km")

# Get activities with filters
activities = client.get_activities(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31),
    activity_type="running",
    limit=20
)

# Get single activity by ID
activity = client.get_activity(12345678)
```

### Heart Rate

```python
# Get heart rate data for a day
hr = client.get_heart_rate()
print(f"Resting HR: {hr.resting_heart_rate} bpm")

# Get just resting heart rate
resting_hr = client.get_resting_heart_rate(date(2025, 1, 15))
```

### Stress & Body Battery

```python
# Get stress data
stress = client.get_stress()
print(f"Avg stress: {stress.avg_stress_level}")

# Get body battery data
battery = client.get_body_battery()
```

### Steps

```python
# Get detailed step data
steps = client.get_steps()
print(f"Total: {steps.total_steps}, Goal: {steps.step_goal}")

# Get just total steps
total = client.get_total_steps(date(2025, 1, 15))
```

### Body Composition

```python
# Get latest weight
weight = client.get_latest_weight()
print(f"Weight: {weight.weight_kg} kg")

# Get weight for specific date
weight = client.get_weight(date(2025, 1, 15))

# Get full body composition
body = client.get_body_composition()
```

### Hydration & Respiration

```python
# Get hydration data
hydration = client.get_hydration()
print(f"Intake: {hydration.total_intake_ml} ml")

# Get respiration data
resp = client.get_respiration()
print(f"Avg breathing: {resp.avg_waking_respiration} breaths/min")
```

### Comprehensive Reports

```python
# Get health snapshot (all metrics for a day)
snapshot = client.get_health_snapshot()
# Returns: daily_summary, sleep, heart_rate, stress, steps, hydration, respiration

# Get weekly health report with trends
report = client.get_weekly_health_report()
# Returns: activities summary, sleep stats, steps stats, HR trends, stress trends

# Export data for date range
data = client.export_data(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31),
    include_activities=True,
    include_sleep=True,
    include_daily=True
)
```

### Training Plans

```python
# Get active training plans
plans = client.get_active_training_plans()
for plan in plans:
    print(f"{plan.name}: {plan.goal}")
    print(f"  Progress: Week {plan.current_week}/{plan.total_weeks}")
    print(f"  Workouts: {plan.completed_workouts}/{plan.total_workouts} done")
    print(f"  Days remaining: {plan.days_remaining}")

# Get specific training plan
plan = client.get_training_plan(plan_id)
print(f"Plan: {plan.name}")
print(f"Difficulty: {plan.difficulty_level}")

# Get all training plans (active, completed, history)
all_plans = client.get_training_plan_history()

# Get available templates to create a plan
templates = client.get_training_templates()
running_templates = client.get_training_templates(activity_type="running")

# Get details of a specific template
template = client.get_training_template(template_id)
print(f"Template: {template.name}")
print(f"Duration: {template.duration_weeks} weeks")
print(f"Level: {template.difficulty_level}")

# Create a new training plan
plan = client.create_training_plan(
    name="Spring Marathon Training",
    template_id="template_123",
    start_date=date(2025, 3, 1),
    goal="Marathon",
    activity_type="running",
    difficulty_level="intermediate",
)

# Update a training plan
updated_plan = client.update_training_plan(
    plan_id=plan.plan_id,
    name="Updated Plan Name",
    difficulty_level="advanced",
    start_date=date(2025, 3, 8),
)

# Delete a training plan
success = client.delete_training_plan(plan_id)

# Complete a workout in a plan
success = client.complete_workout(
    plan_id=plan_id,
    workout_id=workout_id,
    completed_date=date(2025, 1, 15),
)

# Update a workout in a plan
workout = client.update_workout(
    plan_id=plan_id,
    workout_id=workout_id,
    notes="Great run today!",
)

# Get plan statistics
stats = client.get_training_plan_stats(plan_id)
```

#### Training Plan Data Structure

```python
# TrainingPlan object
plan.plan_id              # str - Unique plan ID
plan.name                 # str - Plan name
plan.description          # str | None
plan.goal                 # str - "5K", "Half Marathon", "Marathon", etc.
plan.activity_type        # str - "running", "cycling", "swimming", etc.
plan.start_date           # date
plan.end_date             # date
plan.total_weeks          # int - Total weeks in plan
plan.current_week         # int - Current week number
plan.difficulty_level     # str - "beginner", "intermediate", "advanced"
plan.status               # str - "not_started", "in_progress", "completed"
plan.is_active            # bool
plan.workouts             # list[TrainingPlanWorkout] - All workouts in plan
plan.total_distance_km    # float | None
plan.total_duration_hours # float | None

# Computed properties
plan.days_remaining       # int - Days left in plan
plan.progress_percentage  # float - 0-100% complete
plan.completed_workouts   # int - Number of completed workouts
plan.total_workouts       # int - Total number of workouts
plan.next_workout         # TrainingPlanWorkout | None - Next incomplete

# TrainingPlanWorkout object
workout.workout_id           # str
workout.day_number           # int - Which day of plan
workout.name                 # str - Workout name
workout.description          # str | None
workout.activity_type        # str - "running", "cycling", etc.
workout.duration_seconds     # int | None - Total workout duration
workout.distance_meters      # float | None - Total distance
workout.intensity            # str - "easy", "moderate", "hard"
workout.target_pace_min_per_km  # float | None
workout.target_heart_rate_zone  # str | None - e.g., "Zone 2"
workout.notes                # str | None
workout.completed            # bool - Is this workout done?
workout.completed_date       # date | None
workout.segments             # list[WorkoutSegment] - Interval-based structure (see below)

# WorkoutSegment object (for interval/structured workouts)
segment.segment_id           # str - Unique segment ID
segment.segment_type         # str - "sprint", "pause", "recovery", "warmup", "cooldown", "threshold", etc.
segment.duration_seconds     # int - How long this segment lasts
segment.distance_meters      # float | None - Optional distance for this segment
segment.intensity            # str - "easy", "moderate", "hard", "max"
segment.target_pace_min_per_km   # float | None - Pace target for segment
segment.target_heart_rate_zone   # str | None - Heart rate zone (e.g., "Zone 4")
segment.order                # int - Position in sequence (0-indexed)

# TrainingPlanTemplate object (for creating plans)
template.template_id         # str - Template ID to use with create_training_plan
template.name                # str
template.description         # str
template.goal                # str - What this template is for
template.activity_type       # str
template.difficulty_level    # str - "beginner", "intermediate", "advanced"
template.duration_weeks      # int - How many weeks
template.weekly_hours        # float - Time commitment per week
template.is_popular          # bool - Popular template flag
```

## Common Workflows

### Health Check Query

When a user asks "How did I sleep?" or "What's my health summary?":

```bash
garmer snapshot --json
```

### Activity Analysis

When a user asks about workouts or exercise:

```bash
garmer activities --limit 10
```

### Trend Analysis

When analyzing health trends over time:

```bash
garmer export --days 30 --output health_data.json
```

Then process the JSON file with Python for analysis.

### Workout Creation Workflow

When the user asks to create a Garmin workout:

1. Clarify the intended training stimulus:
   - Easy aerobic
   - VO2 max
   - Threshold
   - Long run
   - Recovery
   - Race pace
   - Speed or sprint session

2. Convert the request into a structured workout:
   - Warmup
   - Main set
   - Recovery blocks
   - Cooldown

3. Use `create_garmin_workout.py` to upload it.

4. Schedule it only if the user provides a date.

Example:

```bash
python create_garmin_workout.py \
  --name "Threshold Builder" \
  --warmup 15 \
  --interval 8 \
  --recovery 3 \
  --repeats 3 \
  --cooldown 10 \
  --date 2026-05-09
```

For readiness-aware workout creation, first check recent Garmin data:

```bash
garmer snapshot --json
garmer activities --limit 7 --json
garmer sleep --json
```

Then adjust the workout:

- Poor sleep or high stress: reduce intensity or convert to Zone 2
- High recent load: reduce repeats or extend recovery
- Good recovery: proceed with planned intensity

### Training Plan Workflow

**Starting a new training plan:**

1. Browse available templates and goals:
   ```bash
   garmer training-templates --activity running
   ```

2. Choose a template and create a plan:
   ```bash
   garmer create-plan \
     --name "5K Race Prep" \
     --template-id <chosen-template-id> \
     --activity running \
     --goal "5K" \
     --start-date 2025-02-01 \
     --level intermediate
   ```

3. Check the plan details:
   ```bash
   garmer training-plan <plan-id>
   ```

4. Log workouts as you complete them:
   ```bash
   garmer complete-workout --plan-id <plan-id> --workout-id <workout-id>
   ```

5. Track progress:
   ```bash
   garmer training-plans
   ```

**Python workflow for training plan analysis:**

```python
from garmer import GarminClient
from datetime import date

client = GarminClient.from_saved_tokens()

# Get active plans
plans = client.get_active_training_plans()

for plan in plans:
    print(f"\n{plan.name} ({plan.activity_type})")
    print(f"Goal: {plan.goal}")
    print(f"Progress: {plan.completed_workouts}/{plan.total_workouts} workouts")
    print(f"Current week: {plan.current_week}/{plan.total_weeks}")

    # Get next workout
    if plan.next_workout:
        w = plan.next_workout
        print(f"Next: {w.name} (Day {w.day_number})")
        if w.duration_seconds:
            print(f"  Duration: {w.duration_seconds // 60} min")
        if w.distance_meters:
            print(f"  Distance: {w.distance_meters / 1000:.1f} km")
```

**Interval-based workouts with segments:**

Workouts can include multiple segments (intervals) to define structured training like sprint intervals with recovery pauses:

```python
from garmer import GarminClient
from garmer.models.training_plan import TrainingPlanWorkout, WorkoutSegment
from datetime import date

client = GarminClient.from_saved_tokens()

# Get active plans
plans = client.get_active_training_plans()

for plan in plans:
    for workout in plan.workouts:
        # Check if workout has interval segments
        if workout.segments:
            print(f"\n{workout.name} - Interval Workout")
            print(f"Total duration: {workout.duration_seconds // 60} min")
            print("Segments:")

            for segment in sorted(workout.segments, key=lambda s: s.order):
                print(f"  {segment.order + 1}. {segment.segment_type.title()}")
                print(f"     Duration: {segment.duration_seconds} sec")
                if segment.intensity:
                    print(f"     Intensity: {segment.intensity}")
                if segment.distance_meters:
                    print(f"     Distance: {segment.distance_meters / 1000:.2f} km")
                if segment.target_pace_min_per_km:
                    print(f"     Pace: {segment.target_pace_min_per_km:.2f} min/km")
                if segment.target_heart_rate_zone:
                    print(f"     HR Zone: {segment.target_heart_rate_zone}")
        else:
            # Simple workout without intervals
            print(f"\n{workout.name} - Simple Workout")
            print(f"Intensity: {workout.intensity}")
            if workout.duration_seconds:
                print(f"Duration: {workout.duration_seconds // 60} min")
            if workout.distance_meters:
                print(f"Distance: {workout.distance_meters / 1000:.1f} km")

# Example: Working with a specific interval workout
plan = client.get_active_training_plans()[0]
workout_with_intervals = next(
    (w for w in plan.workouts if w.segments),
    None
)

if workout_with_intervals:
    print(f"\n=== {workout_with_intervals.name} ===")

    # Total rest time
    rest_time = sum(
        s.duration_seconds for s in workout_with_intervals.segments
        if s.segment_type in ["pause", "recovery"]
    )
    print(f"Total rest time: {rest_time // 60} min")

    # Total work time
    work_time = sum(
        s.duration_seconds for s in workout_with_intervals.segments
        if s.segment_type not in ["pause", "recovery"]
    )
    print(f"Total work time: {work_time // 60} min")

    # High-intensity segments
    high_intensity = [s for s in workout_with_intervals.segments if s.intensity == "hard"]
    print(f"High-intensity segments: {len(high_intensity)}")
    for seg in high_intensity:
        print(f"  - {seg.segment_type}: {seg.duration_seconds}s at {seg.intensity}")
```

**Example interval workout structures:**

Here are common interval workout patterns supported:

```python
# 5K Speed Workout: Warmup + 6x800m with recovery + Cooldown
segments = [
    WorkoutSegment(
        segment_id="warmup_1",
        segment_type="warmup",
        duration_seconds=300,  # 5 min
        intensity="easy",
        target_pace_min_per_km=6.0,
        order=0
    ),
    # Repeat 6 times:
    WorkoutSegment(
        segment_id="sprint_1",
        segment_type="sprint",
        duration_seconds=180,  # ~3 min for 800m
        intensity="hard",
        target_pace_min_per_km=3.5,
        target_heart_rate_zone="Zone 4",
        order=1
    ),
    WorkoutSegment(
        segment_id="recovery_1",
        segment_type="recovery",
        duration_seconds=90,  # 1.5 min walk/jog
        intensity="easy",
        target_pace_min_per_km=5.5,
        order=2
    ),
    # ... (more sprints/recoveries)
    WorkoutSegment(
        segment_id="cooldown_1",
        segment_type="cooldown",
        duration_seconds=300,  # 5 min
        intensity="easy",
        target_pace_min_per_km=6.0,
        order=11
    ),
]

# Cycling threshold workout: Warmup + 2x8min threshold + Cooldown
segments = [
    WorkoutSegment(
        segment_id="warmup",
        segment_type="warmup",
        duration_seconds=600,  # 10 min
        intensity="easy",
        order=0
    ),
    WorkoutSegment(
        segment_id="threshold_1",
        segment_type="threshold",
        duration_seconds=480,  # 8 min
        intensity="hard",
        target_heart_rate_zone="Zone 3",
        order=1
    ),
    WorkoutSegment(
        segment_id="break",
        segment_type="pause",
        duration_seconds=300,  # 5 min recovery
        intensity="easy",
        order=2
    ),
    WorkoutSegment(
        segment_id="threshold_2",
        segment_type="threshold",
        duration_seconds=480,  # 8 min
        intensity="hard",
        target_heart_rate_zone="Zone 3",
        order=3
    ),
    WorkoutSegment(
        segment_id="cooldown",
        segment_type="cooldown",
        duration_seconds=600,  # 10 min
        intensity="easy",
        order=4
    ),
]
```

## Data Types Available

- **Activities**: Running, cycling, swimming, strength training, etc.
- **Sleep**: Duration, phases (deep, light, REM), score, HRV
- **Heart Rate**: Resting HR, samples, zones
- **Stress**: Stress levels, body battery
- **Steps**: Total steps, distance, floors
- **Body Composition**: Weight, body fat, muscle mass
- **Hydration**: Water intake tracking
- **Respiration**: Breathing rate data
- **Training Plans**: Create and track structured training plans for any activity type
  - Plan templates by activity and difficulty level
  - Workout scheduling and progression
  - Completion tracking
  - Multiple concurrent plans
  - Plan statistics and progress monitoring
- **Structured Workouts**: Create and optionally schedule running workouts through the Python helper
  - Warmup
  - Repeat groups
  - Intervals
  - Recoveries
  - Cooldown
  - Optional calendar scheduling

## Error Handling

If not authenticated:

```text
Not logged in. Use 'garmer login' first.
```

If session expired, re-authenticate:

```bash
garmer login
```

## Workout Creation Caveats

Workout creation uses the community `garminconnect` Python package, not the `garmer` CLI itself unless implemented as a garmer command.

Potential issues:

- Garmin may change private/internal endpoints.
- MFA may be required during login.
- Token storage for this helper defaults to `~/.garminconnect`, while garmer tokens default to `~/.garmer/garmin_tokens`.
- The current helper creates running interval workouts only.
- Pace, heart-rate-zone, power, and distance-based targets are not yet implemented in the helper script.
- The script assumes `upload_running_workout()` and `schedule_workout()` are available in the installed `garminconnect` version.

If upload fails, first verify:

```bash
python -c "from garminconnect import Garmin; print('garminconnect installed')"
python -c "import garminconnect.workout as w; print(dir(w))"
```

## Missing Capabilities for High-Quality Workout Prescription

The current skill is strong for data extraction, but good workout prescription requires additional guardrails and context.

Recommended future improvements:

| Missing capability | Why it matters |
|---|---|
| Workout goal classification | "Intervals" is too vague. VO2 max, threshold, tempo, and sprint workouts should be structured differently. |
| Fitness context check | Recent load, sleep, stress, HRV, and resting HR should influence the workout. |
| Target zones | Good Garmin workouts usually need pace, HR zone, power, cadence, or distance targets, not only time blocks. |
| Progression logic | A single workout is useful, but training improvement comes from progressive overload across weeks. |
| Recovery guardrails | The skill should avoid prescribing hard sessions after bad sleep, high stress, or heavy recent load. |
| Sport-specific builders | Running, cycling, swimming, and strength require different workout schemas. |
| Validation before upload | Check total duration, repeat count, impossible paces, missing cooldown, and conflicting targets. |
| Dry-run mode | Preview the workout before uploading to Garmin. |
| Workout library | Store reusable patterns like Zone 2 run, 5x4 VO2, 3x8 threshold, long run, recovery run. |

Conceptual separation:

```text
Garmin data extraction
Garmin workout creation
Garmin training plan analysis / creation
```

Do not treat Garmin workout creation as the same thing as training-plan creation.

## Environment Variables

- `GARMER_TOKEN_DIR`: Custom directory for garmer token storage
- `GARMER_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `GARMER_CACHE_ENABLED`: Enable/disable data caching (true/false)
- `GARMIN_EMAIL`: Garmin Connect email for the workout creation helper
- `GARMIN_PASSWORD`: Garmin Connect password for the workout creation helper

## References

For detailed API documentation and MoltBot integration examples, see `references/REFERENCE.md`.
