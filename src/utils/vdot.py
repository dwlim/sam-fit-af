import math

def get_running_velocity(vdot: float, pct: float) -> float:
    """Calculate running velocity in meters/second for a given VDOT and percentage of max effort.
    
    Args:
        vdot (float): VDOT score representing current fitness level
        pct (float): Percentage of max effort, typically between 0.59-1.2
        
    Returns:
        float: Running velocity in meters per second
    """
    # Original formula gives m/min, convert to m/s by dividing by 60
    meters_per_min = (
        -0.182258 + math.sqrt(0.033218 - 0.000416 * (-4.6 - (vdot * pct)))
    ) / 0.000208
    
    return meters_per_min / 60.0

def calculate_vdot(distance_in_meters: float, time_in_seconds: float) -> float:
    """Calculate VDOT (VO2max estimate) based on a race or time trial performance.
    
    Uses Dr. Jack Daniels' VDOT formula to estimate VO2max from performance data.
    
    Args:
        distance_in_meters (float): Distance covered in meters
        time_in_seconds (float): Time taken in seconds
        
    Returns:
        float: Estimated VDOT score
    """
    # Convert to minutes for the formula
    time_in_minutes = time_in_seconds / 60.0
    
    # Calculate velocity in meters/minute (required by Daniels' formula)
    v = distance_in_meters / time_in_minutes
    vo2 = -4.6 + 0.182258 * v + 0.000104 * v**2
    pct = 0.8 + 0.1894393 * math.exp(-0.012778 * time_in_minutes) + 0.2989558 * math.exp(-0.1932605 * time_in_minutes)
    vdot = vo2 / pct
    return vdot

def calculate_pace_zones(vdot: float) -> dict:
    """Calculate training pace zones based on VDOT score.
    
    Uses Dr. Jack Daniels' training intensities to calculate appropriate pace ranges
    for different types of training runs.
    
    Args:
        vdot (float): VDOT score representing current fitness level
        
    Returns:
        dict: Dictionary mapping zone names to [faster, slower] pace ranges in m/s
              Zones are: Easy, Marathon, Threshold, Interval, and Repetition
    """
    paces = {
        "Easy": (0.59, 0.74),
        "Marathon": (0.75, 0.84),
        "Threshold": (0.83, 0.88),
        "Interval": (0.95, 1),
        "Repetition": (1.05, 1.2),
    }
    pace_zones = {}
    for name, pcts in paces.items():
        # Get velocities in m/s directly
        velocities = [get_running_velocity(vdot, pct) for pct in pcts]
        slower, faster = velocities
        pace_zones[name] = [faster, slower]
    
    return pace_zones
