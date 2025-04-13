from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime, timedelta
from garminconnect import Garmin
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Activity(TypedDict):
    # Basic Identification
    activity_id: int
    user_id: int
    device_id: Optional[str]
    data_source: Optional[str]

    # Activity Metadata
    start_time: str
    activity_type: Optional[str]
    has_splits: Optional[bool]

    # Duration Metrics
    duration: Optional[str]
    moving_time: Optional[str]
    elapsed_time: Optional[str]

    # Distance and Speed
    distance: Optional[float]
    average_speed: Optional[float]
    max_speed: Optional[float]
    average_grade_adjusted_speed: Optional[float]

    # Heart Rate Data
    average_heart_rate: Optional[float]
    max_heart_rate: Optional[float]
    hr_time_z1_seconds: Optional[float]
    hr_time_z2_seconds: Optional[float]
    hr_time_z3_seconds: Optional[float]
    hr_time_z4_seconds: Optional[float]
    hr_time_z5_seconds: Optional[float]

    # Power Data
    average_power: Optional[float]
    max_power: Optional[float]
    power_time_z1_seconds: Optional[float]
    power_time_z2_seconds: Optional[float]
    power_time_z3_seconds: Optional[float]
    power_time_z4_seconds: Optional[float]
    power_time_z5_seconds: Optional[float]

    # Cadence
    average_cadence: Optional[float]
    max_cadence: Optional[float]

    # Elevation Data
    elevation_gain: Optional[float]
    elevation_loss: Optional[float]
    min_elevation: Optional[float]
    max_elevation: Optional[float]

    # Temperature
    average_temperature: Optional[float]
    max_temperature: Optional[float]

    # Split Times
    fastest_split_1_mile: Optional[float]
    fastest_split_1k: Optional[float]
    fastest_split_5k: Optional[float]
    fastest_split_10k: Optional[float]
    split_summaries: Optional[List[Dict[str, Any]]] # TODO: Add this to the database, not currently used because we can't add a dictionary to the database directly

    # Training Effect and Load
    training_effect_label: Optional[str]
    aerobic_training_effect: Optional[float]
    anaerobic_training_effect: Optional[float]
    aerobic_training_effect_message: Optional[str]
    anaerobic_training_effect_message: Optional[str]
    activity_training_load: Optional[float]
    vo2_max: Optional[float]

    # Intensity Minutes
    moderate_intensity_minutes: Optional[float]
    vigorous_intensity_minutes: Optional[float]

    # Energy
    calories: Optional[float]

    # FIT File Information
    fit_file_path: Optional[str]
    fit_file_downloaded_at: Optional[str]

def download_fit_file(email: str, password: str, user_id: int, activity_id: int, activities_dir: Path) -> Optional[Path]:
    """Download a specific activity's .fit file."""
    fit_dir = activities_dir
    fit_dir.mkdir(parents=True, exist_ok=True)
    fit_path = fit_dir / f"{activity_id}.fit"
    
    if fit_path.exists():
        return fit_path
        
    try:
        client = Garmin(email=email, password=password)
        client.login()
        
        fit_bytes = client.download_activity(
            activity_id, 
            dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL
        )
        
        with open(fit_path, "wb") as f:
            f.write(fit_bytes)
            
        logger.info(f"Downloaded .fit file for activity {activity_id}")
        return fit_path
        
    except Exception as e:
        logger.error(f"Failed to download .fit file for activity {activity_id}: {e}")
        return None

def fetch_recent_activities(email: str, password: str, user_id: int, start_date: str, end_date: str, activities_dir: Path, store_fit_files: bool = False) -> List[Activity]:
    """Fetch recent activities and their .fit files."""
    client = Garmin(email=email, password=password)
    client.login()
    
    # Get activities data
    activity_data = client.get_activities_by_date(
        startdate=start_date,
        enddate=end_date
    )
    
    activities: List[Activity] = []
    for activity in activity_data:
        # Create user's fit file directory if it doesn't exist
        fit_dir = activities_dir
        fit_dir.mkdir(parents=True, exist_ok=True)
        
        activity_id = activity["activityId"]
        fit_path = fit_dir / f"{user_id}_{activity_id}.fit"
        
        # Download .fit file if it doesn't exist
        # Note: for the time being, we're not storing fit files in the database because downloading
        # takes a long time, and I was getting blocked by Garmin for too many requests.
        if not fit_path.exists() and store_fit_files:
            fit_path = download_fit_file(email, password, user_id, activity_id, activities_dir)
        
        # Format activity data with all fields
        formatted_activity = {
            # Basic Identification
            "activity_id": activity["activityId"],
            "user_id": user_id,
            "device_id": activity.get("deviceId"),
            "data_source": "Garmin",
            
            # Activity Metadata
            "start_time": activity["startTimeLocal"],
            "activity_type": activity.get("activityType", {}).get("typeKey"),
            "has_splits": activity.get("hasSplits"),
            
            # Duration Metrics
            "duration": activity.get("duration"),
            "moving_time": activity.get("movingDuration"),
            "elapsed_time": activity.get("elapsedDuration"),
            
            # Distance and Speed
            "distance": activity.get("distance"),
            "average_speed": activity.get("averageSpeed"),
            "max_speed": activity.get("maxSpeed"),
            "average_grade_adjusted_speed": activity.get("avgGradeAdjustedSpeed"),
            
            # Heart Rate Data
            "average_heart_rate": activity.get("averageHR"),
            "max_heart_rate": activity.get("maxHR"),
            "hr_time_z1_seconds": activity.get("hrTimeInZone_1"),
            "hr_time_z2_seconds": activity.get("hrTimeInZone_2"),
            "hr_time_z3_seconds": activity.get("hrTimeInZone_3"),
            "hr_time_z4_seconds": activity.get("hrTimeInZone_4"),
            "hr_time_z5_seconds": activity.get("hrTimeInZone_5"),
            
            # Power Data
            "average_power": activity.get("averagePower"),
            "max_power": activity.get("maxPower"),
            "power_time_z1_seconds": activity.get("powerTimeInZone_1"),
            "power_time_z2_seconds": activity.get("powerTimeInZone_2"),
            "power_time_z3_seconds": activity.get("powerTimeInZone_3"),
            "power_time_z4_seconds": activity.get("powerTimeInZone_4"),
            "power_time_z5_seconds": activity.get("powerTimeInZone_5"),
            
            # Cadence
            "average_cadence": activity.get("averageRunningCadenceInStepsPerMinute"),
            "max_cadence": activity.get("maxRunningCadenceInStepsPerMinute"),
            
            # Elevation Data
            "elevation_gain": activity.get("elevationGain"),
            "elevation_loss": activity.get("elevationLoss"),
            "min_elevation": activity.get("minElevation"),
            "max_elevation": activity.get("maxElevation"),
            
            # Temperature
            "average_temperature": activity.get("averageTemperature"),
            "max_temperature": activity.get("maxTemperature"),
            
            # Split Times
            "fastest_split_1_mile": activity.get("fastestSplit_1609"),
            "fastest_split_1k": activity.get("fastestSplit_1000"),
            "fastest_split_5k": activity.get("fastestSplit_5000"),
            "fastest_split_10k": activity.get("fastestSplit_10000"),
            
            # Training Effect and Load
            "training_effect_label": activity.get("trainingEffectLabel"),
            "aerobic_training_effect": activity.get("aerobicTrainingEffect"),
            "anaerobic_training_effect": activity.get("anaerobicTrainingEffect"),
            "aerobic_training_effect_message": activity.get("aerobicTrainingEffectMessage"),
            "anaerobic_training_effect_message": activity.get("anaerobicTrainingEffectMessage"),
            "activity_training_load": activity.get("activityTrainingLoad"),
            "vo2_max": activity.get("vO2MaxValue"),
            
            # Intensity Minutes
            "moderate_intensity_minutes": activity.get("moderateIntensityMinutes"),
            "vigorous_intensity_minutes": activity.get("vigorousIntensityMinutes"),
            
            # Energy
            "calories": activity.get("calories"),
            
            # FIT File Information
            "fit_file_path": str(fit_path) if fit_path and fit_path.exists() else None,
            "fit_file_downloaded_at": datetime.now().isoformat() if fit_path and fit_path.exists() else None
        }
        
        activities.append(formatted_activity)
    
    return activities

def get_fit_file_path(user_id: int, activity_id: int, activities_dir: Path) -> Optional[Path]:
    """Get path to .fit file for an activity if it exists."""
    fit_path = activities_dir / f"{activity_id}.fit"
    return fit_path if fit_path.exists() else None

