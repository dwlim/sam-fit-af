from datetime import timedelta
from typing import TypedDict, Optional
from utils.types import TimeTrial

def get_time_in_seconds(data: TimeTrial) -> float:
    """Extract time information and return time in seconds.
    
    Takes a dictionary containing time data with hours, minutes and seconds
    and converts it to total seconds as a float.
    
    Args:
        data (dict): Dictionary containing hours, minutes, seconds
        
    Returns:
        float: Total time in minutes
    """
    return timedelta(
        hours=data["hours"],
        minutes=data["minutes"],
        seconds=data["seconds"]
    ).total_seconds()

def format_duration(td: timedelta) -> str:
    """Format timedelta as a string.
    
    Converts a timedelta object to a human readable string in HH:MM:SS or MM:SS format.
    Hours are only included if non-zero.
    
    Args:
        td (timedelta): Timedelta object to format
        
    Returns:
        str: Formatted duration string as either "HH:MM:SS" or "MM:SS"
    """
    s = int(td.total_seconds())
    hh, mm, ss = s // 3600, s // 60 % 60, s % 60
    if hh > 0:
        return f"{hh}:{mm:02}:{ss:02}"
    return f"{mm}:{ss:02}"

def format_seconds_to_time_string(seconds: Optional[float]) -> Optional[str]:
    """Format seconds into HH:MM:SS string.
    
    Args:
        seconds: Number of seconds to format, or None
        
    Returns:
        Formatted time string or None if input is None
    """
    if seconds is None:
        return None
    
    # Type checking
    if not isinstance(seconds, (int, float)):
        raise TypeError("Input must be a number")
    
    # Value checking
    if isinstance(seconds, float):
        if seconds != seconds:  # Check for NaN
            raise ValueError("Input cannot be NaN")
        if seconds in (float('inf'), float('-inf')):
            raise ValueError("Input cannot be infinity")
    
    if seconds < 0:
        raise ValueError("Input cannot be negative")
        
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"