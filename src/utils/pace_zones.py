from utils.data_processing import get_time_in_seconds
from utils.vdot import calculate_vdot, calculate_pace_zones

"""Utilities for calculating and formatting running paces and training zones.

This module provides two main sets of functionality:
1. Zone Calculations: Computing training zones and speeds in m/s for use in training plan generation
2. Pace Formatting: Converting speeds to human-readable pace strings for display and validation

The core zone calculations work with m/s, while the formatting functions help convert
these speeds to more readable min/km format when needed.
"""

def calculate_zones_from_json(data: dict) -> dict:
    """Calculate training zones from user input data.
    
    Args:
        data (dict): User input data containing recent time trial and goal event info
        
    Returns:
        dict: Training zones and paces in meters/second
    """
    try:
        time_in_seconds = get_time_in_seconds(data["recent_time_trial"])
        event_distance = data["recent_time_trial"]["event"]  # in meters
        vdot_value = calculate_vdot(event_distance, time_in_seconds)
        
        # Calculate speeds in m/s
        time_trial_speed = event_distance / time_in_seconds
        goal_event_distance = data["goal_event"]["event"]  # in meters
        goal_time_in_seconds = get_time_in_seconds(data["goal_event"]["goal_time"])
        goal_event_speed = goal_event_distance / goal_time_in_seconds
        
        # Get pace zones in m/s
        pace_zones = calculate_pace_zones(vdot_value)  # m/s

        return {
            "vdot": vdot_value,
            "zones": pace_zones,  # m/s
            "time_trial_speed": time_trial_speed,  # m/s
            "goal_event_speed": goal_event_speed  # m/s
        }
    except KeyError as e:
        return {"error": f"Missing field: {e}"}

# Utility functions for human-readable pace formatting
def calculate_pace(distance_meters: float, time_seconds: float) -> str:
    """Calculate and format running pace in min/km format.
    
    Useful for displaying paces in a human-readable format and validating
    LLM-generated workout speeds.

    Args:
        distance_meters (float): Distance covered in meters
        time_seconds (float): Time taken in seconds

    Returns:
        str: Pace formatted as "M:SS" per kilometer
    """
    if time_seconds == 0:
        return "0:00"
    speed = distance_meters / time_seconds
    return speed_to_pace_string(speed)

def speed_to_pace_string(speed_meters_per_second: float) -> str:
    """Convert speed to a human-readable pace string.
    
    Useful for converting m/s speeds to min/km format for display
    and validation purposes.
    
    Args:
        speed_meters_per_second (float): Speed in meters per second
        
    Returns:
        str: Pace formatted as "M:SS" per kilometer if minutes is less than 10,
             otherwise formatted as "MM:SS" per kilometer
    """
    if speed_meters_per_second == 0:
        return "0:00"
    seconds_per_km = 1000 / speed_meters_per_second
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    return f"{minutes}:{seconds:02d}" if minutes < 10 else f"{minutes:02d}:{seconds:02d}"

def format_pace_zones(pace_zones: dict) -> dict:
    """Format pace zones dictionary with human readable pace strings.
    
    Takes pace zones with speeds in m/min and converts them to min/km pace strings.
    
    Args:
        pace_zones (dict): Dictionary mapping zone names to [faster, slower] speeds in m/min
        
    Returns:
        dict: Dictionary mapping zone names to [faster, slower] paces as "M:SS" for minutes less than 10,
              or "MM:SS" for minutes greater than or equal to 10.
    """
    formatted_zones = {}
    for zone, speeds in pace_zones.items():
        faster, slower = speeds
        formatted_zones[zone] = [
            speed_to_pace_string(faster),
            speed_to_pace_string(slower)
        ]
    return formatted_zones  
