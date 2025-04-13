"""Core training plan schema definitions."""

from typing import List
from pydantic import BaseModel, ConfigDict

from .measurements import PlanDuration
from .workout_phases import Phase
from .constants import AreaOfFocus, WorkoutSubType


class Workout(BaseModel):
    """A single training session within the plan.
    
    Attributes:
        workout_type: Primary type of workout (e.g., "run", "swim", "bike")
        workout_subtype: Specific focus (e.g., "tempo", "long_run", "recovery")
        scheduled_date: Date of the workout in ISO format
        total_distance: Total planned distance for the workout
        estimated_duration: Estimated time to complete the workout
        terrain: Type of terrain (e.g., "road", "trail", "track")
        phases: Ordered list of workout phases and interval sets
        additional_instructions: Any extra notes or instructions for the workout
    """
    model_config = ConfigDict(extra="forbid")
    workout_type: str
    workout_subtype: List[WorkoutSubType]
    scheduled_date: str
    total_distance: PlanDuration
    estimated_duration: PlanDuration
    terrain: str
    phases: List[Phase]
    additional_instructions: str


class Week(BaseModel):
    """A week of training within the plan.
    
    Attributes:
        week_number: Sequential number of the week in the plan
        start_date: Start date of the week in ISO format
        end_date: End date of the week in ISO format
        area_of_focus: Primary training focus for the week
        total_distance: Planned total distance for all workouts
        total_time: Estimated total duration of all workouts
        workouts: List of planned workouts for the week
        rest_days: List of rest days in ISO date format
        week_notes: Additional notes or instructions for the week
    """
    model_config = ConfigDict(extra="forbid")
    week_number: int
    start_date: str
    end_date: str
    area_of_focus: AreaOfFocus
    total_distance: PlanDuration
    total_time: PlanDuration
    workouts: List[Workout]
    rest_days: List[str]
    week_notes: str


class TrainingPlan(BaseModel):
    """Complete training plan generated for an athlete.
    
    Attributes:
        plan_duration: Length of the training plan
        athlete_level: Experience level of the athlete
        primary_goal: Main objective of the training plan
        weeks: List of training weeks
        plan_notes: Overall notes and instructions for the plan
    """
    model_config = ConfigDict(extra="forbid")
    plan_duration: PlanDuration
    athlete_level: str
    primary_goal: str
    weeks: List[Week]
    plan_notes: str 