"""Base measurement types used throughout the training plan schemas."""

from pydantic import BaseModel


class Range(BaseModel):
    """A numeric range with minimum and maximum values.
    
    Used for defining ranges in pace, heart rate, and perceived exertion.
    """
    min: float
    max: float


class PlanDuration(BaseModel):
    """Represents a duration or distance measurement with a value and unit.
    
    Used for workout distances, durations, and overall plan length.
    
    Attributes:
        value: Numeric value of the measurement
        unit: Unit of measurement (e.g., "weeks" for plan duration, "meters" for distance)
    """
    value: float
    unit: str


class Pace(BaseModel):
    """Represents a pace range with its unit of measurement.
    
    Attributes:
        value: Range object containing minimum and maximum pace values
        unit: Unit of measurement (e.g., "min/km", "m/s")
    """
    value: Range
    unit: str


class HeartRate(BaseModel):
    """Represents a heart rate range with its unit of measurement.
    
    Attributes:
        value: Range object containing minimum and maximum heart rate values
        unit: Unit of measurement (typically "bpm" - beats per minute)
    """
    value: Range
    unit: str


class PerceivedExertion(BaseModel):
    """Represents a perceived exertion range with its scale.
    
    Attributes:
        value: Range object containing minimum and maximum RPE values
        unit: Scale being used (e.g., "RPE", "Borg")
    """
    value: Range
    unit: str


class Intensity(BaseModel):
    """Defines the intensity parameters for a workout phase.
    
    Attributes:
        effort: Descriptive effort level (e.g., "easy", "moderate", "hard")
        pace_min: Minimum pace in meters per second
        pace_max: Maximum pace in meters per second
        perceived_exertion_min: Minimum RPE on scale of 1-10
        perceived_exertion_max: Maximum RPE on scale of 1-10
    """
    effort: str
    pace_min: float
    pace_max: float
    perceived_exertion_min: float
    perceived_exertion_max: float
