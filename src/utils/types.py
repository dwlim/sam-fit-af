from typing import TypedDict
from pydantic import BaseModel, field_validator, Field
from typing import Literal, Dict

class GoalTime(TypedDict):
    hours: int
    minutes: int
    seconds: int

class TimeComponents(BaseModel):
    hours: int = Field(ge=0)
    minutes: int = Field(ge=0, lt=60)
    seconds: int = Field(ge=0, lt=60)

class GoalEvent(BaseModel):
    event: int = Field(gt=0)  # Distance in meters
    goal_time: TimeComponents

class TimeTrial(BaseModel):
    event: int = Field(gt=0)  # Distance in meters
    hours: int = Field(ge=0)
    minutes: int = Field(ge=0, lt=60)
    seconds: int = Field(ge=0, lt=60)

class TrainingPlanInput(BaseModel):
    sex: Literal["male", "female"]
    age: int
    goal_event: GoalEvent
    timeline_weeks: int
    recent_time_trial: TimeTrial
    training_days_per_week: int
    start_date: str

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: str) -> str:
        if not v:
            raise ValueError("Invalid value for 'start_date': must be a valid date string.")
        return v

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid value for 'age': must be a positive integer.")
        return v

    @field_validator('timeline_weeks')
    @classmethod
    def validate_timeline(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid value for 'timeline_weeks': must be a positive integer.")
        return v

    @field_validator('training_days_per_week')
    @classmethod
    def validate_training_days(cls, v: int) -> int:
        if v < 1 or v > 7:
            raise ValueError("Invalid value for 'training_days_per_week': must be an integer between 1 and 7.")
        return v

    @field_validator('recent_time_trial')
    @classmethod
    def validate_time_trial(cls, v: TimeTrial) -> TimeTrial:
        if v.event <= 0:
            raise ValueError("Invalid value for 'recent_time_trial.event': must be a positive integer.")
        return v