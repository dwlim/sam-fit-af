from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from collections import defaultdict

from activity.Activity import Activity, fetch_recent_activities
from database.activities_db import ActivityDB
from utils.fit_file_generator import FitFileGenerator
from schemas.training_plan import TrainingPlan, Workout
from utils.types import TrainingPlanInput, GoalEvent, TimeTrial
from api_factory import create_api
from utils.upload_fit_file import upload_workout
import logging
import json
from analysis.weekly_summary import WeeklySummaryCalculator


@dataclass
class WorkoutFile:
    """Container for workout file information."""
    workout_id: str          # Format: week{n}_{date}_{type}
    external_id: str         # Format: {athlete_id}_week{n}_{date}_{type}
    fit_file_path: Path
    scheduled_date: str
    week_number: int

class Athlete:
    def __init__(
        self, 
        user_id: int, 
        email: str, 
        password: str, 
        intervals_icu_id: str,
        training_plan_input: TrainingPlanInput,
        training_plan_dir: str
    ) -> None:
        """Initialize an Athlete instance.

        Args:
            user_id: Unique identifier for the athlete
            email: Athlete's email address associated with Garmin Connect
            password: Athlete's password associated with Garmin Connect
            intervals_icu_id: Athlete's intervals.icu ID
            training_plan_input: Input parameters for generating training plan
            training_plan_dir: Directory path where workout files will be stored

        Returns:
            None
        """
        self.logger = logging.getLogger(__name__)
        self.user_id = user_id
        self.email = email
        self.password = password
        self.intervals_icu_id = intervals_icu_id
        self.training_plan_input = TrainingPlanInput.model_validate(training_plan_input)
        self.activities: Dict[str, Activity] = {}  # Use dict with activity_id as key
        
        # Setup directories and files
        self.training_plan_dir = Path(training_plan_dir)
        self.training_plan_dir.mkdir(parents=True, exist_ok=True)
        self.workout_dir = self.training_plan_dir / "workouts" # directory for prescribed workouts
        self.workout_dir.mkdir(parents=True, exist_ok=True)
        self.activities_dir = self.training_plan_dir / "activities" # directory for historical/completed activities
        self.activities_dir.mkdir(parents=True, exist_ok=True)
        self.plan_file = self.training_plan_dir / f"current_plan_{self.user_id}.json"

        # Initialize database connection
        self.activity_db = ActivityDB()

        # Load current plan if it exists
        self.current_plan = self._load_plan()

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # fit file generation related fields
        self.fit_generator = FitFileGenerator(self.workout_dir) # .fit files are stored in self.workout_dir
        self.workout_files: Dict[str, WorkoutFile] = {}  # workout_id -> WorkoutFile

    @property
    def sex(self) -> str:
        return self.training_plan_input['sex']

    @property
    def age(self) -> int:
        return self.training_plan_input['age']

    @property
    def goal_event(self) -> GoalEvent:
        return self.training_plan_input['goal_event']

    @property
    def timeline_weeks(self) -> int:
        return self.training_plan_input['timeline_weeks']

    @property
    def recent_time_trial(self) -> TimeTrial:
        return self.training_plan_input['recent_time_trial']

    @property
    def training_days_per_week(self) -> int:
        return self.training_plan_input['training_days_per_week']

    def generate_workout_files(self, training_plan: TrainingPlan) -> List[WorkoutFile]:
        """Generate FIT files for all workouts in the training plan and store them in self.workout_dir.
        
        Args:
            training_plan: Training plan containing workouts
            
        Returns:
            List of successfully generated WorkoutFiles
        """
        generated_files = []

        for week in training_plan.weeks:
            for workout in week.workouts:
                try:
                    # Generate unique IDs
                    workout_id = self._create_workout_id(week.week_number, workout)
                    external_id = self._create_external_id(workout_id)

                    # Generate FIT file
                    fit_file_path = self.fit_generator._generate_workout_file(
                        workout, 
                        week.week_number
                    )

                    # Create and store WorkoutFile
                    workout_file = WorkoutFile(
                        workout_id=workout_id,
                        external_id=external_id,
                        fit_file_path=fit_file_path,
                        scheduled_date=workout.scheduled_date,
                        week_number=week.week_number
                    )
                    
                    self.workout_files[workout_id] = workout_file
                    generated_files.append(workout_file)
                    self.logger.info(f"Generated FIT file for workout: {workout_id}")

                except Exception as e:
                    self.logger.error(f"Error generating workout for {workout.scheduled_date}: {e}")
                    continue
        return generated_files
    
    def upload_workout_files(self, workout_ids: Optional[List[str]] = None) -> List[str]:
        """Upload workout files to intervals.icu.
        
        Args:
            workout_ids: Optional list of specific workout IDs to upload.
                       If None, uploads all workouts.
            
        Returns:
            List of successfully uploaded workout IDs
        """
        uploaded_workouts = []
        
        # Determine which workouts to upload
        to_upload = (
            workout_ids if workout_ids is not None 
            else list(self.workout_files.keys())
        )

        for workout_id in to_upload:
            if workout_id not in self.workout_files:
                self.logger.error(f"Workout {workout_id} not found")
                continue

            workout_file = self.workout_files[workout_id]
            try:
                response = upload_workout(
                    file_path=str(workout_file.fit_file_path),
                    athlete_id=self.intervals_icu_id,
                    start_date=f"{workout_file.scheduled_date}T09:00:00",  # Default to 9 AM
                    external_id=workout_file.external_id
                )
                
                if response and response.status_code == 200:
                    uploaded_workouts.append(workout_id)
                    self.logger.info(f"Successfully uploaded workout: {workout_id}")
                else:
                    self.logger.error(f"Failed to upload workout {workout_id}: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"Error uploading workout {workout_id}: {e}")
                continue

        return uploaded_workouts
    
    def fetch_historical_activities(self, days: int = 30):
        """Fetch historical activities from Garmin Connect and merge with existing."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        new_activities = fetch_recent_activities(
            self.email, 
            self.password, 
            self.user_id, 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            activities_dir=self.activities_dir
        )

        # Merge new activities with existing ones, using activity_id as key
        for activity in new_activities:
            self.activities[activity["activity_id"]] = activity
        
        # Persist to database
        try:
            self.activity_db.upsert_activities(new_activities)
            self.logger.info(f"Successfully stored {len(new_activities)} activities in database")
        except Exception as e:
            self.logger.error(f"Failed to store activities in database: {e}")
            # Optionally raise the exception if you want to handle it at a higher level
            raise

    def generate_training_plan(self) -> None:
        """Generate a training plan for the athlete using the configured API."""
        try:
            api = create_api()
            # Convert to dict first, then to json string
            user_prompt = json.dumps(self.training_plan_input.model_dump())
            
            # Generate and validate plan
            plan_json = api.generate_plan(user_prompt)
            new_plan = TrainingPlan.model_validate_json(plan_json)
            
            # Save plan to disk
            self._save_plan(new_plan)
            self.current_plan = new_plan

        except Exception as e:
            self.logger.error(f"Failed to generate plan: {e}")
            raise
        
    def check_plan_progress(self) -> dict:
        """Check athlete's adherence to current training plan."""
        if not self.current_plan:
            return {"error": "No active training plan"}
            
        # Fetch recent activities
        self.fetch_historical_activities(days=7)
        
        # Get activities from the last 7 days
        recent_date = datetime.now() - timedelta(days=7)
        recent_activities = [
            activity for activity in self.activities.values()
            if datetime.fromisoformat(activity["start_time"]) >= recent_date
        ]
        
        return {
            "planned_workouts": len(self.current_plan.weeks[-1].workouts),
            "completed_workouts": len(recent_activities),
            "recent_activities": [
                {
                    "date": activity["start_time"],
                    "type": activity["activity_type"],
                    "distance": activity["distance"],
                    "duration": activity["duration"]
                }
                for activity in recent_activities
            ]
        }

    def backfill_historical_data(self, days: int = 365) -> None:
        """Public interface for historical data population. 
        This will use the activities table to backfill the weekly_summary table.
        By default, this will backfill 1 year of data.
        
        Note: this should only be called once at the beginning of onboarding the athlete.
        After this, the athlete's workouts should be fetched regularly/automatically (TODO)
        """
        try:
            self.fetch_historical_activities(days=days)
            start_date = datetime.now() - timedelta(days=days)
            self._populate_historical_weekly_summaries(start_date=start_date)
        except Exception as e:
            self.logger.error(f"Failed to backfill historical data: {e}")
            raise

    def _populate_historical_weekly_summaries(self, start_date: datetime) -> None:
        """Populate weekly summaries from historical activities. 
        Make private because:
        1. Depends on fetch_historical_activities being called first to ensure activities table is populated
        2. Should only be called through backfill_historical_data
        3. Prevents incorrect usage outside the class
        
        Args:
            start_date: Start date for fetching historical data.
        """
        try:
            # Get start (Monday) and end dates of each week from start_date to now
            week_ranges = []
            current_date = datetime.now()
            week_start = start_date - timedelta(days=start_date.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            most_recent_sunday = current_date - timedelta(days=current_date.weekday() + 1)
            # Only process weeks that have completed (ended on a Sunday). In other words,
            # we don't process weeks that are currently in progress. 
            while week_start <= most_recent_sunday:
                week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
                calculator = WeeklySummaryCalculator(
                    athlete_id=self.user_id,
                    start_date=week_start,
                    end_date=week_end
                )

                week_range = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
                self.logger.info(f"Processing week: {week_range}")
                week_ranges.append(week_range)
                
                # Calculate and store the summary
                calculator.run()
                # Increment to next week
                week_start += timedelta(days=7)
            
            self.logger.info(
                f"Successfully generated weekly summaries from {start_date} to {current_date}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to populate weekly summaries: {e}")
            raise
    
    def _create_workout_id(self, week_number: int, workout: Workout) -> str:
        """Create a unique workout ID."""
        return f"week{week_number}_{workout.scheduled_date}_{workout.workout_subtype[0]}"

    def _create_external_id(self, workout_id: str) -> str:
        """Create external ID for intervals.icu."""
        return f"{self.user_id}_{workout_id}"
    
    def _save_plan(self, plan: TrainingPlan) -> None:
        """Save current training plan to disk."""
        try:
            self.plan_file.write_text(plan.model_dump_json(indent=2))
            self.logger.info(f"Saved plan to {self.plan_file}")
        except Exception as e:
            self.logger.error(f"Failed to save plan: {e}")
            raise

    def _load_plan(self) -> Optional[TrainingPlan]:
        """Load current training plan from disk."""
        if not self.plan_file.exists():
            return None
            
        try:
            return TrainingPlan.model_validate_json(self.plan_file.read_text())
        except Exception as e:
            self.logger.error(f"Failed to load plan: {e}")
            return None