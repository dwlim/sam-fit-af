"""Constants and enums used in training plan validation."""

from typing import Literal

# Valid areas of focus for training weeks
AreaOfFocus = Literal[
    "aerobic_development",
    "anaerobic_development",
    "vo2_max_development",
    "base_training",
    "race_specific_development",
    "taper",
    "speed_development",
    "lactate_threshold_development",
    "endurance_development",
    "recovery"
]

# Valid workout subtypes
WorkoutSubType = Literal[
    "easy",
    "long_run",
    "medium_long_run",
    "recovery",
    "tempo",
    "threshold",
    "vo2max_intervals",
    "speed_intervals",
    "hill_repeats",
    "fartlek",
    "progression",
    "race_pace",
    "marathon_pace",
    "steady_state",
    "lactate_threshold",
    "aerobic",
    "anaerobic_intervals",
    "sprint_intervals",
    "endurance",
    "base_building",
    "taper",
    "shakeout"
] 