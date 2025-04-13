from typing import Dict, Set
from enum import Enum

class ActivityCategory(str, Enum):
    CYCLING = "CYCLING"
    RUNNING = "RUNNING"
    SWIMMING = "SWIMMING"
    STRENGTH = "STRENGTH"
    OTHER = "OTHER"

# Mapping from Garmin activity types to our high-level categories
ACTIVITY_TYPE_MAPPINGS: Dict[ActivityCategory, Set[str]] = {
    ActivityCategory.CYCLING: {
        "road_biking", 
        "indoor_cycling",
        "virtual_ride"
    },
    ActivityCategory.RUNNING: {
        "running", 
        "trail_running", 
        "indoor_running", 
        "treadmill_running",
        "track_running" # TODO: check if this is correct
    },
    ActivityCategory.SWIMMING: {
        "lap_swimming",
        "open_water_swimming"
    },
}

def get_activity_category(activity_type: str) -> ActivityCategory:
    """
    Maps a specific activity type to its high-level category.
    
    Args:
        activity_type: The specific activity type from Garmin
        
    Returns:
        The high-level ActivityCategory
    """
    activity_type = activity_type.lower().replace(" ", "_")
    
    for category, types in ACTIVITY_TYPE_MAPPINGS.items():
        if activity_type in types:
            return category
            
    return ActivityCategory.OTHER 

def is_cycling(activity_type: str) -> bool:
    return get_activity_category(activity_type) == ActivityCategory.CYCLING

def is_running(activity_type: str) -> bool:
    return get_activity_category(activity_type) == ActivityCategory.RUNNING 

def is_swimming(activity_type: str) -> bool:
    return get_activity_category(activity_type) == ActivityCategory.SWIMMING