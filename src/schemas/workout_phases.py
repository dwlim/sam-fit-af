"""Schema definitions for workout phases and intervals."""

from typing import List, Literal, Union
from pydantic import BaseModel

from .measurements import Intensity


class SinglePhase(BaseModel):
    """A single continuous phase of a workout (warmup, cooldown, or steady state).
    
    Attributes:
        type: The type of phase ("warmup", "cooldown", "steady_state")
        duration_type: How the duration is measured ("time" or "distance")
        duration_value: Numeric value of the duration
        duration_unit: Unit for the duration ("seconds" or "meters")
        intensity: Intensity parameters for this phase
        notes: Additional instructions or notes for this phase
    """
    type: Literal["warmup", "cooldown", "steady_state"]
    duration_type: str
    duration_value: float
    duration_unit: str
    intensity: Intensity
    notes: str


class Interval(BaseModel):
    """A single interval within an interval set.
    
    Can be either a work interval or recovery interval.
    
    Attributes:
        type: The type of interval ("work" or "recovery")
        duration_type: How the duration is measured ("time" or "distance")
        duration_value: Numeric value of the duration
        duration_unit: Unit for the duration ("seconds" or "meters")
        intensity: Intensity parameters for this interval
        notes: Additional instructions or notes for this interval
    """
    type: Literal["work", "recovery"]
    duration_type: str
    duration_value: float
    duration_unit: str
    intensity: Intensity
    notes: str


class IntervalSet(BaseModel):
    """A set of repeating intervals within a workout.
    
    Attributes:
        type: Always "interval_set" to distinguish from SinglePhase
        repetitions: Number of times to repeat the interval sequence
        intervals: List of work and recovery intervals that make up one repetition
    """
    type: Literal["interval_set"]
    repetitions: int
    intervals: List[Interval]


Phase = Union[SinglePhase, IntervalSet]
"""Represents either a single continuous phase or a set of intervals.""" 