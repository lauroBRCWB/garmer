"""Training plan models for Garmin Connect."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class WorkoutSegment:
    """A segment or interval within a workout (e.g., sprint, pause, recovery)."""

    segment_id: str
    segment_type: str  # e.g., "sprint", "pause", "recovery", "warmup", "cooldown"
    duration_seconds: int
    distance_meters: Optional[float] = None
    intensity: Optional[str] = None  # e.g., "easy", "moderate", "hard", "max"
    target_pace_min_per_km: Optional[float] = None
    target_heart_rate_zone: Optional[str] = None
    order: int = 0  # Order in sequence

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "segment_id": self.segment_id,
            "segment_type": self.segment_type,
            "duration_seconds": self.duration_seconds,
            "distance_meters": self.distance_meters,
            "intensity": self.intensity,
            "target_pace_min_per_km": self.target_pace_min_per_km,
            "target_heart_rate_zone": self.target_heart_rate_zone,
            "order": self.order,
        }


@dataclass
class TrainingPlanWorkout:
    """A single workout within a training plan."""

    workout_id: str
    day_number: int
    name: str
    description: Optional[str]
    activity_type: str  # e.g., "running", "cycling"
    duration_seconds: Optional[int]
    distance_meters: Optional[float]
    intensity: Optional[str]  # e.g., "easy", "moderate", "hard"
    target_pace_min_per_km: Optional[float]
    target_heart_rate_zone: Optional[str]
    notes: Optional[str]
    completed: bool = False
    completed_date: Optional[date] = None
    segments: list[WorkoutSegment] = field(default_factory=list)  # Interval-based structure

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workout_id": self.workout_id,
            "day_number": self.day_number,
            "name": self.name,
            "description": self.description,
            "activity_type": self.activity_type,
            "duration_seconds": self.duration_seconds,
            "distance_meters": self.distance_meters,
            "intensity": self.intensity,
            "target_pace_min_per_km": self.target_pace_min_per_km,
            "target_heart_rate_zone": self.target_heart_rate_zone,
            "notes": self.notes,
            "completed": self.completed,
            "completed_date": str(self.completed_date) if self.completed_date else None,
            "segments": [s.to_dict() for s in self.segments],
        }


@dataclass
class TrainingPlan:
    """A training plan from Garmin Connect."""

    plan_id: str
    name: str
    description: Optional[str]
    goal: str  # e.g., "5K", "Half Marathon", "Marathon", "Century Ride"
    activity_type: str  # e.g., "running", "cycling"
    start_date: date
    end_date: date
    total_weeks: int
    current_week: int
    difficulty_level: str  # e.g., "beginner", "intermediate", "advanced"
    status: str  # e.g., "not_started", "in_progress", "completed"
    is_active: bool
    workouts: list[TrainingPlanWorkout]
    total_distance_km: Optional[float] = None
    total_duration_hours: Optional[float] = None

    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in plan."""
        return (self.end_date - date.today()).days

    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage."""
        if self.total_weeks == 0:
            return 0
        return (self.current_week / self.total_weeks) * 100

    @property
    def completed_workouts(self) -> int:
        """Count completed workouts."""
        return sum(1 for w in self.workouts if w.completed)

    @property
    def total_workouts(self) -> int:
        """Get total workouts."""
        return len(self.workouts)

    @property
    def next_workout(self) -> Optional[TrainingPlanWorkout]:
        """Get the next incomplete workout."""
        for workout in self.workouts:
            if not workout.completed:
                return workout
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "goal": self.goal,
            "activity_type": self.activity_type,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "total_weeks": self.total_weeks,
            "current_week": self.current_week,
            "difficulty_level": self.difficulty_level,
            "status": self.status,
            "is_active": self.is_active,
            "days_remaining": self.days_remaining,
            "progress_percentage": round(self.progress_percentage, 1),
            "completed_workouts": self.completed_workouts,
            "total_workouts": self.total_workouts,
            "total_distance_km": self.total_distance_km,
            "total_duration_hours": self.total_duration_hours,
            "workouts": [w.to_dict() for w in self.workouts],
        }


@dataclass
class TrainingPlanTemplate:
    """A training plan template available for selection."""

    template_id: str
    name: str
    description: str
    goal: str
    activity_type: str
    difficulty_level: str
    duration_weeks: int
    weekly_hours: float
    is_popular: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "goal": self.goal,
            "activity_type": self.activity_type,
            "difficulty_level": self.difficulty_level,
            "duration_weeks": self.duration_weeks,
            "weekly_hours": self.weekly_hours,
            "is_popular": self.is_popular,
        }
