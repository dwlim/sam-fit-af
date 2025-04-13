from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from database.activities_db import ActivityDB
from utils.data_processing import format_seconds_to_time_string
from database.weekly_summary_db import WeeklySummaryDB
from activity.Activity import Activity
from activity.constants import is_cycling, is_running, is_swimming

@dataclass
class WeeklySummary:
    """Data container for weekly training metrics."""
    # Identification
    summary_id: str
    athlete_id: int
    start_date: datetime
    end_date: datetime
    
    # Basic Metrics
    total_duration_seconds: float
    total_duration_formatted: str  # HH:MM:SS format
    total_distance_meters: float
    total_distance_formatted: str  # e.g., "42.2 km"
    num_sessions: int

    # Sport-specific basic metrics
    num_sessions_cycling: int
    num_sessions_running: int
    num_sessions_swimming: int
    total_duration_cycling_seconds: float
    total_duration_running_seconds: float
    total_duration_swimming_seconds: float

    total_duration_cycling_formatted: str
    total_duration_running_formatted: str
    total_duration_swimming_formatted: str
    
    # Training Load
    total_training_load: float
    time_in_hr_zones: Dict[int, float] # seconds
    time_in_hr_zones_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS
    
    time_in_power_zones: Dict[int, float] # seconds
    time_in_power_zones_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS

    # Sport-specific training load metrics
    total_training_load_cycling: float
    total_training_load_running: float
    total_training_load_swimming: float

    time_in_hr_zones_cycling: Dict[int, float] # seconds
    time_in_hr_zones_running: Dict[int, float] # seconds
    time_in_hr_zones_swimming: Dict[int, float] # seconds

    time_in_hr_zones_cycling_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS
    time_in_hr_zones_running_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS
    time_in_hr_zones_swimming_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS

    time_in_power_zones_cycling: Dict[int, float] # seconds
    time_in_power_zones_running: Dict[int, float] # seconds

    time_in_power_zones_cycling_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS
    time_in_power_zones_running_formatted: Dict[int, str]  # Each zone duration in HH:MM:SS
    
    # Performance Metrics
    best_5k_time: Optional[float]
    best_5k_formatted: Optional[str]  # HH:MM:SS format
    best_10k_time: Optional[float]
    best_10k_formatted: Optional[str]  # HH:MM:SS format
    
    # VO2max Tracking
    vo2max_start: Optional[float]
    vo2max_end: Optional[float]
    vo2max_change: Optional[float]
    vo2max_max: Optional[float]
    vo2max_min: Optional[float]
    
    # TODO: Training Phase
    training_phase: Optional[str] = None
    
    # Metadata
    created_at: datetime = datetime.now()


class WeeklySummaryCalculator:
    def __init__(self, athlete_id: int, start_date: datetime, end_date: datetime):
        self.athlete_id = athlete_id
        self.start_date = start_date
        # Create summary ID in format: athleteID_MM_DD_YYYY
        self.summary_id = f"{athlete_id}_{start_date.strftime('%m_%d_%Y')}"
        self.end_date = end_date
        self.activities: List[Activity] = []
        self.summary: Dict = {}
        self.activity_db = ActivityDB()
        self.weekly_summary_db = WeeklySummaryDB()

    def fetch_activities(self) -> None:
        """Retrieve all activities for the week from the database."""
        query = """
        SELECT * FROM activities 
        WHERE user_id = %s 
        AND start_time BETWEEN %s AND %s
        ORDER BY start_time ASC
        """
        with self.activity_db._get_connection() as conn:
            with conn.cursor() as cur:
                # Get column names
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'activities'
                    ORDER BY ordinal_position
                """)
                columns = [col[0] for col in cur.fetchall()]
                
                # Fetch activities
                cur.execute(query, (self.athlete_id, self.start_date, self.end_date))
                rows = cur.fetchall()
                
                # Convert tuples to dictionaries
                self.activities = [
                    dict(zip(columns, row))
                    for row in rows
                ]

    def compute_basic_metrics(self) -> None:
        """Calculate total duration, distance, and session count."""
        self.summary.update({
            'total_duration_seconds': sum(a['duration'] or 0 for a in self.activities),
            'total_distance_meters': sum(a['distance'] or 0 for a in self.activities),
            'num_sessions': len(self.activities)
        })
        # Add human-readable metrics
        self.summary['total_duration_formatted'] = format_seconds_to_time_string(self.summary['total_duration_seconds'])
        self.summary['total_distance_formatted'] = f"{self.summary['total_distance_meters'] / 1000:.2f} km"
        
        # Get sport-specific metrics

        self.summary['total_duration_cycling_seconds'] = sum(a['duration'] or 0 for a in self.activities if is_cycling(a['activity_type']))
        self.summary['total_duration_running_seconds'] = sum(a['duration'] or 0 for a in self.activities if is_running(a['activity_type']))
        self.summary['total_duration_swimming_seconds'] = sum(a['duration'] or 0 for a in self.activities if is_swimming(a['activity_type']))

        self.summary['total_duration_cycling_formatted'] = format_seconds_to_time_string(self.summary['total_duration_cycling_seconds'])
        self.summary['total_duration_running_formatted'] = format_seconds_to_time_string(self.summary['total_duration_running_seconds'])
        self.summary['total_duration_swimming_formatted'] = format_seconds_to_time_string(self.summary['total_duration_swimming_seconds'])


    def compute_training_load(self) -> None:
        """Compute training load and time in zones."""
        self.summary['total_training_load'] = sum(
            a['activity_training_load'] or 0 for a in self.activities
        )
        
        # Sport-specific training load metrics
        self.summary['num_sessions_cycling'] = sum(1 for a in self.activities if is_cycling(a['activity_type']))
        self.summary['num_sessions_running'] = sum(1 for a in self.activities if is_running(a['activity_type']))
        self.summary['num_sessions_swimming'] = sum(1 for a in self.activities if is_swimming(a['activity_type']))
        self.summary['total_training_load_cycling'] = sum(a['activity_training_load'] or 0 for a in self.activities if is_cycling(a['activity_type']))
        self.summary['total_training_load_running'] = sum(a['activity_training_load'] or 0 for a in self.activities if is_running(a['activity_type']))
        self.summary['total_training_load_swimming'] = sum(a['activity_training_load'] or 0 for a in self.activities if is_swimming(a['activity_type']))
        
        # HR zones
        hr_zones = {str(i): 0.0 for i in range(1, 6)}
        hr_zones_formatted = {str(i): 0.0 for i in range(1, 6)}

        hr_zones_cycling = {str(i): 0.0 for i in range(1, 6)}
        hr_zones_running = {str(i): 0.0 for i in range(1, 6)}
        hr_zones_swimming = {str(i): 0.0 for i in range(1, 6)}

        hr_zones_cycling_formatted = {str(i): 0.0 for i in range(1, 6)}
        hr_zones_running_formatted = {str(i): 0.0 for i in range(1, 6)}
        hr_zones_swimming_formatted = {str(i): 0.0 for i in range(1, 6)}

        # Power zones
        power_zones = {str(i): 0.0 for i in range(1, 6)}
        power_zones_formatted = {str(i): 0.0 for i in range(1, 6)}
        power_zones_cycling = {str(i): 0.0 for i in range(1, 6)}
        power_zones_running = {str(i): 0.0 for i in range(1, 6)}

        power_zones_cycling_formatted = {str(i): 0.0 for i in range(1, 6)}
        power_zones_running_formatted = {str(i): 0.0 for i in range(1, 6)}

        for activity in self.activities:
            for zone in range(1, 6):
                hr_zones[str(zone)] += activity.get(f'hr_time_z{zone}_seconds') or 0
                hr_zones_formatted[str(zone)] = format_seconds_to_time_string(hr_zones[str(zone)])

                power_zones[str(zone)] += activity.get(f'power_time_z{zone}_seconds') or 0
                power_zones_formatted[str(zone)] = format_seconds_to_time_string(power_zones[str(zone)])

                if is_cycling(activity['activity_type']):
                    hr_zones_cycling[str(zone)] += activity.get(f'hr_time_z{zone}_seconds') or 0
                    hr_zones_cycling_formatted[str(zone)] = format_seconds_to_time_string(hr_zones_cycling[str(zone)])
                    power_zones_cycling[str(zone)] += activity.get(f'power_time_z{zone}_seconds') or 0
                    power_zones_cycling_formatted[str(zone)] = format_seconds_to_time_string(power_zones_cycling[str(zone)])
                elif is_running(activity['activity_type']):
                    hr_zones_running[str(zone)] += activity.get(f'hr_time_z{zone}_seconds') or 0
                    hr_zones_running_formatted[str(zone)] = format_seconds_to_time_string(hr_zones_running[str(zone)])
                    power_zones_running[str(zone)] += activity.get(f'power_time_z{zone}_seconds') or 0
                    power_zones_running_formatted[str(zone)] = format_seconds_to_time_string(power_zones_running[str(zone)])
                elif is_swimming(activity['activity_type']):
                    hr_zones_swimming[str(zone)] += activity.get(f'hr_time_z{zone}_seconds') or 0
                    hr_zones_swimming_formatted[str(zone)] = format_seconds_to_time_string(hr_zones_swimming[str(zone)])

        # Aggregate time in HR zones
        self.summary['time_in_hr_zones'] = hr_zones
        self.summary['time_in_hr_zones_formatted'] = hr_zones_formatted

        # Sport-specific time in HR zones
        self.summary['time_in_hr_zones_cycling'] = hr_zones_cycling
        self.summary['time_in_hr_zones_running'] = hr_zones_running
        self.summary['time_in_hr_zones_swimming'] = hr_zones_swimming

        self.summary['time_in_hr_zones_cycling_formatted'] = hr_zones_cycling_formatted
        self.summary['time_in_hr_zones_running_formatted'] = hr_zones_running_formatted
        self.summary['time_in_hr_zones_swimming_formatted'] = hr_zones_swimming_formatted


        # Aggregate time in power zones
        self.summary['time_in_power_zones'] = power_zones
        self.summary['time_in_power_zones_formatted'] = power_zones_formatted

        # Sport-specific time in power zones
        self.summary['time_in_power_zones_cycling'] = power_zones_cycling
        self.summary['time_in_power_zones_running'] = power_zones_running

        self.summary['time_in_power_zones_cycling_formatted'] = power_zones_cycling_formatted
        self.summary['time_in_power_zones_running_formatted'] = power_zones_running_formatted

    def extract_performance_metrics(self) -> None:
        """Extract best performance metrics from activities."""
        # Initialize with None for no valid times
        best_5k = None
        best_10k = None
        
        # Get valid times (not None and not inf)
        valid_5k_times = [a['fastest_split_5k'] for a in self.activities 
                         if a['fastest_split_5k'] is not None]
        valid_10k_times = [a['fastest_split_10k'] for a in self.activities 
                          if a['fastest_split_10k'] is not None]
        
        # Only update if we have valid times
        if valid_5k_times:
            best_5k = min(valid_5k_times)
        if valid_10k_times:
            best_10k = min(valid_10k_times)
        
        # Update summary with times and formatted strings
        self.summary.update({
            'best_5k_time': best_5k,
            'best_10k_time': best_10k,
            'best_5k_formatted': format_seconds_to_time_string(best_5k) if best_5k is not None else None,
            'best_10k_formatted': format_seconds_to_time_string(best_10k) if best_10k is not None else None
        })

        # VO2max trend
        vo2max_readings = [a['vo2_max'] for a in self.activities if a.get('vo2_max')]
        if vo2max_readings:
            self.summary.update({
                'vo2max_start': vo2max_readings[0],
                'vo2max_end': vo2max_readings[-1],
                'vo2max_change': vo2max_readings[-1] - vo2max_readings[0],
                'vo2max_max': max(vo2max_readings),
                'vo2max_min': min(vo2max_readings)
            })
        else:
            self.summary.update({
                'vo2max_start': None,
                'vo2max_end': None,
                'vo2max_change': None,
                'vo2max_max': None,
                'vo2max_min': None
            })

    def save_summary(self) -> WeeklySummary:
        """Store the weekly summary."""
        summary = WeeklySummary(
            summary_id=self.summary_id,
            athlete_id=self.athlete_id,
            start_date=self.start_date,
            end_date=self.end_date,
            **self.summary
        )
        self.weekly_summary_db.upsert_weekly_summary(summary)
        return summary

    def run(self) -> WeeklySummary:
        """Execute the full analysis pipeline."""
        self.fetch_activities()
        self.compute_basic_metrics()
        self.compute_training_load()
        self.extract_performance_metrics()
        summary = self.save_summary()
        return summary