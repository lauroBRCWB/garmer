"""Base model configuration for all Garmin data models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class GarminBaseModel(BaseModel):
    """Base model with common configuration for all Garmin data models."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        extra="ignore",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary for serialization."""
        return self.model_dump(mode="json", exclude_none=True)

    @classmethod
    def from_garmin_response(cls, data: dict[str, Any]) -> "GarminBaseModel":
        """
        Create model instance from raw Garmin API response.
        Override in subclasses for custom parsing logic.
        """
        return cls.model_validate(data)


def parse_garmin_timestamp(timestamp: int | str | None) -> datetime | None:
    """Parse Garmin timestamp to datetime.
    
    Handles multiple formats:
    - Integer milliseconds since epoch (e.g., 1777952668000)
    - String milliseconds (e.g., "1777952668000")
    - ISO datetime strings (e.g., "2026-05-05 05:44:28")
    - None values
    """
    if timestamp is None:
        return None
    
    if isinstance(timestamp, str):
        # Try parsing as integer milliseconds first
        try:
            timestamp_int = int(timestamp)
            return datetime.fromtimestamp(timestamp_int / 1000)
        except ValueError:
            pass
        
        # Try parsing as ISO datetime string (e.g., "2026-05-05 05:44:28")
        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            pass
        
        return None
    
    # Numeric timestamps are in milliseconds
    return datetime.fromtimestamp(timestamp / 1000)


def parse_garmin_date(date_str: str | None) -> datetime | None:
    """Parse Garmin date string (YYYY-MM-DD) to datetime."""
    if date_str is None:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None
