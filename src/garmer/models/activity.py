"""Activity data models for Garmin fitness activities."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from garmer.models.base import GarminBaseModel, parse_garmin_timestamp


class ActivityType(str, Enum):
    """Common Garmin activity types."""

    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WALKING = "walking"
    HIKING = "hiking"
    STRENGTH_TRAINING = "strength_training"
    CARDIO = "cardio"
    YOGA = "yoga"
    ELLIPTICAL = "elliptical"
    STAIR_CLIMBING = "stair_climbing"
    INDOOR_CYCLING = "indoor_cycling"
    INDOOR_RUNNING = "indoor_running"
    OPEN_WATER_SWIMMING = "open_water_swimming"
    POOL_SWIMMING = "pool_swimming"
    TRAIL_RUNNING = "trail_running"
    MOUNTAIN_BIKING = "mountain_biking"
    ROWING = "rowing"
    SKI = "ski"
    SNOWBOARD = "snowboard"
    GOLF = "golf"
    TENNIS = "tennis"
    BASKETBALL = "basketball"
    SOCCER = "soccer"
    OTHER = "other"


class Lap(GarminBaseModel):
    """Represents a lap within an activity."""

    lap_number: int = Field(alias="lapIndex", default=0)
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_seconds: float = Field(alias="duration", default=0.0)
    distance_meters: float = Field(alias="distance", default=0.0)
    calories: float = 0.0
    avg_heart_rate: int | None = Field(alias="averageHR", default=None)
    max_heart_rate: int | None = Field(alias="maxHR", default=None)
    avg_speed: float | None = Field(alias="averageSpeed", default=None)
    max_speed: float | None = Field(alias="maxSpeed", default=None)
    avg_cadence: float | None = Field(alias="averageRunCadence", default=None)
    elevation_gain: float | None = Field(alias="elevationGain", default=None)
    elevation_loss: float | None = Field(alias="elevationLoss", default=None)

    @classmethod
    def from_garmin_response(cls, data: dict[str, Any]) -> "Lap":
        """Parse lap data from Garmin response."""
        return cls(
            lap_number=data.get("lapIndex", 0),
            start_time=parse_garmin_timestamp(data.get("startTimeGMT")),
            end_time=parse_garmin_timestamp(data.get("endTimeGMT")),
            duration_seconds=data.get("duration", 0.0),
            distance_meters=data.get("distance", 0.0),
            calories=data.get("calories", 0.0),
            avg_heart_rate=data.get("averageHR"),
            max_heart_rate=data.get("maxHR"),
            avg_speed=data.get("averageSpeed"),
            max_speed=data.get("maxSpeed"),
            avg_cadence=data.get("averageRunCadence"),
            elevation_gain=data.get("elevationGain"),
            elevation_loss=data.get("elevationLoss"),
        )


class Split(GarminBaseModel):
    """Represents a split (e.g., per-mile/km) within an activity."""

    split_number: int = 0
    distance_meters: float = 0.0
    duration_seconds: float = 0.0
    avg_pace_seconds: float | None = None
    avg_heart_rate: int | None = None
    elevation_change: float | None = None


class Activity(GarminBaseModel):
    """Represents a Garmin fitness activity."""

    activity_id: int = Field(alias="activityId")
    activity_name: str = Field(alias="activityName", default="")
    activity_type: str = Field(alias="activityType", default="other")
    activity_type_key: str = Field(alias="activityTypeKey", default="other")

    # Timing
    start_time: datetime | None = Field(alias="startTimeLocal", default=None)
    start_time_gmt: datetime | None = Field(alias="startTimeGMT", default=None)
    duration_seconds: float = Field(alias="duration", default=0.0)
    elapsed_duration: float = Field(alias="elapsedDuration", default=0.0)
    moving_duration: float = Field(alias="movingDuration", default=0.0)

    # Distance and speed
    distance_meters: float = Field(alias="distance", default=0.0)
    avg_speed: float | None = Field(alias="averageSpeed", default=None)
    max_speed: float | None = Field(alias="maxSpeed", default=None)

    # Heart rate
    avg_heart_rate: int | None = Field(alias="averageHR", default=None)
    max_heart_rate: int | None = Field(alias="maxHR", default=None)
    min_heart_rate: int | None = Field(alias="minHR", default=None)

    # Calories
    calories: float = Field(default=0.0)
    active_calories: float = Field(alias="activeCalories", default=0.0)

    # Elevation
    elevation_gain: float | None = Field(alias="elevationGain", default=None)
    elevation_loss: float | None = Field(alias="elevationLoss", default=None)
    min_elevation: float | None = Field(alias="minElevation", default=None)
    max_elevation: float | None = Field(alias="maxElevation", default=None)

    # Running/cycling specific
    avg_cadence: float | None = Field(alias="averageRunningCadenceInStepsPerMinute", default=None)
    max_cadence: float | None = Field(alias="maxRunningCadenceInStepsPerMinute", default=None)
    avg_power: float | None = Field(alias="avgPower", default=None)
    max_power: float | None = Field(alias="maxPower", default=None)
    normalized_power: float | None = Field(alias="normPower", default=None)

    # Training effect
    aerobic_training_effect: float | None = Field(alias="aerobicTrainingEffect", default=None)
    anaerobic_training_effect: float | None = Field(alias="anaerobicTrainingEffect", default=None)
    training_effect_label: str | None = Field(alias="trainingEffectLabel", default=None)

    # Location
    start_latitude: float | None = Field(alias="startLatitude", default=None)
    start_longitude: float | None = Field(alias="startLongitude", default=None)
    end_latitude: float | None = Field(alias="endLatitude", default=None)
    end_longitude: float | None = Field(alias="endLongitude", default=None)

    # Steps (for walking/running)
    steps: int | None = Field(default=None)

    # Swimming specific
    avg_stroke_count: float | None = Field(alias="avgStrokes", default=None)
    total_strokes: int | None = Field(alias="strokes", default=None)
    pool_length: float | None = Field(alias="poolLength", default=None)
    avg_swolf: float | None = Field(alias="avgSwolf", default=None)

    # Laps and splits
    laps: list[Lap] = Field(default_factory=list)
    splits: list[Split] = Field(default_factory=list)

    # Device info
    device_id: int | None = Field(alias="deviceId", default=None)
    device_name: str | None = Field(default=None)

    # Raw data for additional fields
    raw_data: dict[str, Any] | None = Field(default=None, exclude=True)

    @classmethod
    def from_garmin_response(cls, data: dict[str, Any]) -> "Activity":
        """Parse activity from Garmin API response.
        
        Handles two response formats:
        1. Search results (/activitylist-service/activities/search/activities):
           - Flat structure with fields at top level
        2. Single activity (/activity-service/activity/{id}):
           - Nested structure with most fields in summaryDTO
        """
        # Helper to get value from either top level or nested in summaryDTO
        def get_field(key: str, default=None):
            """Get field from top level or summaryDTO."""
            if key in data:
                return data[key]
            summary = data.get("summaryDTO", {})
            if key in summary:
                return summary[key]
            return default
        
        # Handle nested activity type
        activity_type_data = data.get("activityType") or data.get("activityTypeDTO", {})
        if isinstance(activity_type_data, dict):
            activity_type = activity_type_data.get("typeKey", "other")
        else:
            activity_type = str(activity_type_data) if activity_type_data else "other"

        return cls(
            activity_id=data.get("activityId", 0),
            activity_name=data.get("activityName", ""),
            activity_type=activity_type,
            activity_type_key=data.get("activityTypeKey", activity_type),
            start_time=parse_garmin_timestamp(get_field("startTimeLocal")),
            start_time_gmt=parse_garmin_timestamp(get_field("startTimeGMT")),
            duration_seconds=get_field("duration", 0.0),
            elapsed_duration=get_field("elapsedDuration", 0.0),
            moving_duration=get_field("movingDuration", 0.0),
            distance_meters=get_field("distance", 0.0),
            avg_speed=get_field("averageSpeed"),
            max_speed=get_field("maxSpeed"),
            avg_heart_rate=get_field("averageHR"),
            max_heart_rate=get_field("maxHR"),
            min_heart_rate=get_field("minHR"),
            calories=get_field("calories", 0.0),
            active_calories=get_field("activeCalories", 0.0),
            elevation_gain=get_field("elevationGain"),
            elevation_loss=get_field("elevationLoss"),
            min_elevation=get_field("minElevation"),
            max_elevation=get_field("maxElevation"),
            avg_cadence=get_field("averageRunningCadenceInStepsPerMinute"),
            max_cadence=get_field("maxRunningCadenceInStepsPerMinute"),
            avg_power=get_field("avgPower"),
            max_power=get_field("maxPower"),
            normalized_power=get_field("normPower"),
            aerobic_training_effect=get_field("aerobicTrainingEffect"),
            anaerobic_training_effect=get_field("anaerobicTrainingEffect"),
            training_effect_label=get_field("trainingEffectLabel"),
            start_latitude=get_field("startLatitude"),
            start_longitude=get_field("startLongitude"),
            end_latitude=get_field("endLatitude"),
            end_longitude=get_field("endLongitude"),
            steps=get_field("steps"),
            avg_stroke_count=get_field("avgStrokes"),
            total_strokes=get_field("strokes"),
            pool_length=get_field("poolLength"),
            avg_swolf=get_field("avgSwolf"),
            device_id=data.get("deviceId"),
            raw_data=data,
        )

    @property
    def distance_km(self) -> float:
        """Get distance in kilometers."""
        return self.distance_meters / 1000.0

    @property
    def distance_miles(self) -> float:
        """Get distance in miles."""
        return self.distance_meters / 1609.344

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration_seconds / 60.0

    @property
    def pace_per_km(self) -> float | None:
        """Get pace in minutes per kilometer."""
        if self.distance_meters > 0 and self.duration_seconds > 0:
            return (self.duration_seconds / 60.0) / self.distance_km
        return None

    @property
    def pace_per_mile(self) -> float | None:
        """Get pace in minutes per mile."""
        if self.distance_meters > 0 and self.duration_seconds > 0:
            return (self.duration_seconds / 60.0) / self.distance_miles
        return None
