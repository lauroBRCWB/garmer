"""Training plan extractor for Garmin Connect."""

import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional

import garth

from garmer.auth import GarminAuth
from garmer.models.training_plan import (
    TrainingPlan,
    TrainingPlanTemplate,
    TrainingPlanWorkout,
    WorkoutSegment,
)

logger = logging.getLogger(__name__)


class TrainingPlanExtractor:
    """Extract training plan data from Garmin Connect."""

    API_URL = "https://connect.garmin.com/training-api"

    def __init__(self, auth: GarminAuth):
        """Initialize the training plan extractor."""
        self.auth = auth

    def _make_request(self, endpoint: str, method: str = "GET", **kwargs: Any) -> Any:
        """Make an authenticated API request via garth."""
        self.auth.ensure_authenticated()
        return garth.connectapi(endpoint, method=method, **kwargs)

    def get_active_plans(self) -> list[TrainingPlan]:
        """Get active training plans."""
        try:
            # Fetch active plans from API
            response = self._make_request(f"{self.API_URL}/plans/active")
            return self._parse_plans(response.get("plans", []))
        except Exception as e:
            logger.error(f"Failed to fetch active plans: {e}")
            return []

    def get_plan(self, plan_id: str) -> Optional[TrainingPlan]:
        """Get a specific training plan by ID."""
        try:
            response = self._make_request(f"{self.API_URL}/plans/{plan_id}")
            plan_data = response.get("plan")
            if plan_data:
                return self._parse_plan(plan_data)
            return None
        except Exception as e:
            logger.error(f"Failed to fetch plan {plan_id}: {e}")
            return None

    def get_plan_history(self) -> list[TrainingPlan]:
        """Get all completed and in-progress training plans."""
        try:
            response = self._make_request(f"{self.API_URL}/plans/history")
            return self._parse_plans(response.get("plans", []))
        except Exception as e:
            logger.error(f"Failed to fetch plan history: {e}")
            return []

    def create_plan(
        self,
        name: str,
        template_id: str,
        start_date: date,
        goal: str,
        activity_type: str,
        difficulty_level: str = "intermediate",
    ) -> Optional[TrainingPlan]:
        """Create a new training plan."""
        try:
            payload = {
                "name": name,
                "templateId": template_id,
                "startDate": str(start_date),
                "goal": goal,
                "activityType": activity_type,
                "difficultyLevel": difficulty_level,
            }
            response = self._make_request(f"{self.API_URL}/plans", method="POST", json=payload)
            plan_data = response.get("plan")
            if plan_data:
                return self._parse_plan(plan_data)
            return None
        except Exception as e:
            logger.error(f"Failed to create training plan: {e}")
            return None

    def update_plan(
        self,
        plan_id: str,
        name: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        start_date: Optional[date] = None,
    ) -> Optional[TrainingPlan]:
        """Update an existing training plan."""
        try:
            payload = {}
            if name is not None:
                payload["name"] = name
            if difficulty_level is not None:
                payload["difficultyLevel"] = difficulty_level
            if start_date is not None:
                payload["startDate"] = str(start_date)

            response = self._make_request(f"{self.API_URL}/plans/{plan_id}", method="PUT", json=payload)
            plan_data = response.get("plan")
            if plan_data:
                return self._parse_plan(plan_data)
            return None
        except Exception as e:
            logger.error(f"Failed to update training plan: {e}")
            return None

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a training plan."""
        try:
            self._make_request(f"{self.API_URL}/plans/{plan_id}", method="DELETE")
            return True
        except Exception as e:
            logger.error(f"Failed to delete training plan: {e}")
            return False

    def complete_workout(
        self, plan_id: str, workout_id: str, completed_date: Optional[date] = None
    ) -> bool:
        """Mark a workout as completed."""
        try:
            payload = {"completedDate": str(completed_date or date.today())}
            self._make_request(
                f"{self.API_URL}/plans/{plan_id}/workouts/{workout_id}/complete",
                method="POST",
                json=payload,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to complete workout: {e}")
            return False

    def update_workout(
        self, plan_id: str, workout_id: str, **kwargs
    ) -> Optional[TrainingPlanWorkout]:
        """Update a workout in a training plan."""
        try:
            response = self._make_request(
                f"{self.API_URL}/plans/{plan_id}/workouts/{workout_id}",
                method="PUT",
                json=kwargs,
            )
            workout_data = response.get("workout")
            if workout_data:
                return self._parse_workout(workout_data)
            return None
        except Exception as e:
            logger.error(f"Failed to update workout: {e}")
            return None

    def get_templates(self, activity_type: Optional[str] = None) -> list[TrainingPlanTemplate]:
        """Get available training plan templates."""
        try:
            url = f"{self.API_URL}/templates"
            if activity_type:
                url += f"?activityType={activity_type}"
            response = self._make_request(url)
            return self._parse_templates(response.get("templates", []))
        except Exception as e:
            logger.error(f"Failed to fetch templates: {e}")
            return []

    def get_template(self, template_id: str) -> Optional[TrainingPlanTemplate]:
        """Get a specific template by ID."""
        try:
            response = self._make_request(f"{self.API_URL}/templates/{template_id}")
            template_data = response.get("template")
            if template_data:
                return self._parse_template(template_data)
            return None
        except Exception as e:
            logger.error(f"Failed to fetch template: {e}")
            return None

    def get_plan_stats(self, plan_id: str) -> dict[str, Any]:
        """Get statistics for a training plan."""
        try:
            response = self._make_request(f"{self.API_URL}/plans/{plan_id}/stats")
            return response.get("stats", {})
        except Exception as e:
            logger.error(f"Failed to fetch plan stats: {e}")
            return {}

    # -----------------------------------------------------------------------
    # Internal parsing methods
    # -----------------------------------------------------------------------

    def _parse_plans(self, plans_data: list[dict]) -> list[TrainingPlan]:
        """Parse multiple plans from API response."""
        return [self._parse_plan(p) for p in plans_data if p]

    def _parse_plan(self, plan_data: dict) -> TrainingPlan:
        """Parse a single plan from API response."""
        workouts = [
            self._parse_workout(w)
            for w in plan_data.get("workouts", [])
        ]

        return TrainingPlan(
            plan_id=plan_data.get("planId", ""),
            name=plan_data.get("name", ""),
            description=plan_data.get("description"),
            goal=plan_data.get("goal", ""),
            activity_type=plan_data.get("activityType", ""),
            start_date=self._parse_date(plan_data.get("startDate")),
            end_date=self._parse_date(plan_data.get("endDate")),
            total_weeks=plan_data.get("totalWeeks", 0),
            current_week=plan_data.get("currentWeek", 0),
            difficulty_level=plan_data.get("difficultyLevel", ""),
            status=plan_data.get("status", ""),
            is_active=plan_data.get("isActive", False),
            workouts=workouts,
            total_distance_km=plan_data.get("totalDistanceKm"),
            total_duration_hours=plan_data.get("totalDurationHours"),
        )

    def _parse_workout(self, workout_data: dict) -> TrainingPlanWorkout:
        """Parse a single workout from API response."""
        segments = [
            self._parse_segment(s, idx)
            for idx, s in enumerate(workout_data.get("segments", []))
        ]

        return TrainingPlanWorkout(
            workout_id=workout_data.get("workoutId", ""),
            day_number=workout_data.get("dayNumber", 0),
            name=workout_data.get("name", ""),
            description=workout_data.get("description"),
            activity_type=workout_data.get("activityType", ""),
            duration_seconds=workout_data.get("durationSeconds"),
            distance_meters=workout_data.get("distanceMeters"),
            intensity=workout_data.get("intensity"),
            target_pace_min_per_km=workout_data.get("targetPaceMinPerKm"),
            target_heart_rate_zone=workout_data.get("targetHeartRateZone"),
            notes=workout_data.get("notes"),
            completed=workout_data.get("completed", False),
            completed_date=self._parse_date(workout_data.get("completedDate")),
            segments=segments,
        )

    def _parse_templates(self, templates_data: list[dict]) -> list[TrainingPlanTemplate]:
        """Parse multiple templates from API response."""
        return [self._parse_template(t) for t in templates_data if t]

    def _parse_template(self, template_data: dict) -> TrainingPlanTemplate:
        """Parse a single template from API response."""
        return TrainingPlanTemplate(
            template_id=template_data.get("templateId", ""),
            name=template_data.get("name", ""),
            description=template_data.get("description", ""),
            goal=template_data.get("goal", ""),
            activity_type=template_data.get("activityType", ""),
            difficulty_level=template_data.get("difficultyLevel", ""),
            duration_weeks=template_data.get("durationWeeks", 0),
            weekly_hours=template_data.get("weeklyHours", 0),
            is_popular=template_data.get("isPopular", False),
        )

    def _parse_segment(self, segment_data: dict, order: int = 0) -> WorkoutSegment:
        """Parse a single workout segment from API response."""
        return WorkoutSegment(
            segment_id=segment_data.get("segmentId", ""),
            segment_type=segment_data.get("segmentType", ""),
            duration_seconds=segment_data.get("durationSeconds", 0),
            distance_meters=segment_data.get("distanceMeters"),
            intensity=segment_data.get("intensity"),
            target_pace_min_per_km=segment_data.get("targetPaceMinPerKm"),
            target_heart_rate_zone=segment_data.get("targetHeartRateZone"),
            order=segment_data.get("order", order),
        )

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[date]:
        """Parse a date string from API response."""
        if not date_str:
            return None
        try:
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return None
