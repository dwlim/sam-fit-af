from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Protocol, Dict, List, Optional, Union
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.workout_message import WorkoutMessage
from fit_tool.profile.messages.workout_step_message import WorkoutStepMessage
from fit_tool.profile.profile_type import (
    Sport, Intensity, WorkoutStepDuration, 
    WorkoutStepTarget, Manufacturer, FileType
)
from schemas.training_plan import (
    TrainingPlan, Workout
)
from fit_tool.profile.messages.workout_step_message import WorkoutStepCustomTargetValueLowField, WorkoutStepCustomTargetValueHighField

from schemas.workout_phases import (
    Phase, SinglePhase, IntervalSet, Interval
)

@dataclass
class WorkoutArtifacts:
    """Container for workout-related files and metadata."""
    fit_file_path: Path
    notes: str
    workout_id: str  # Format: week{n}_date_{type}

class UnitConverter:
    """Centralized unit conversion logic for FIT file format requirements."""
    
    @staticmethod
    def seconds_to_milliseconds(seconds: float) -> int:
        """Convert seconds to milliseconds."""
        if seconds < 0:
            raise ValueError("Duration must be positive")
        return int(seconds * 1000)
    
    @staticmethod
    def meters_to_centimeters(meters: float) -> int:
        """Convert meters to centimeters."""
        if meters < 0:
            raise ValueError("Distance must be positive")
        return int(meters * 100)
    
    @staticmethod
    def pace_to_speed(pace_seconds_per_km: float) -> int:
        """Convert pace (seconds/km) to speed (millimeters/second)."""
        if pace_seconds_per_km <= 0:
            raise ValueError("Pace must be positive")
        return int((1000 / pace_seconds_per_km) * 1000)

class WorkoutStepBuilder:
    """Builds workout steps with proper intensity and targets."""
    
    def __init__(self, converter: UnitConverter):
        self.converter = converter

    def build_step(self, phase: Phase) -> WorkoutStepMessage:
        """Build a workout step from a phase."""
        if isinstance(phase, SinglePhase):
            return self._build_single_phase(phase)
        elif isinstance(phase, Interval):
            return self._build_interval(phase)
        else:
            raise ValueError(f"Unsupported phase type: {type(phase)}")

    def _build_single_phase(self, phase: SinglePhase) -> WorkoutStepMessage:
        """Build a workout step from a single phase."""
        step = WorkoutStepMessage()
        
        # Set duration
        self._set_duration(step, phase)
        
        # Set intensity
        step.intensity = self._get_intensity(phase.type)
        
        # Set pace targets
        self._set_pace_targets(step, phase.intensity)
        
        return step

    def _build_interval(self, interval: Interval) -> WorkoutStepMessage:
        """Build a workout step from an interval."""
        step = WorkoutStepMessage()
        
        # Set duration
        self._set_duration(step, interval)
        
        # Set intensity
        step.intensity = Intensity.ACTIVE if interval.type == "work" else Intensity.RECOVERY
        
        # Set pace targets
        self._set_pace_targets(step, interval.intensity)
        
        return step

    def _set_duration(self, step: WorkoutStepMessage, phase: Union[SinglePhase, Interval]) -> None:
        """Set the duration for a workout step."""
        try:
            if phase.duration_type == "time":
                step.duration_type = WorkoutStepDuration.TIME
                step.duration_value = self.converter.seconds_to_milliseconds(phase.duration_value)
            elif phase.duration_type == "distance":
                step.duration_type = WorkoutStepDuration.DISTANCE
                step.duration_value = self.converter.meters_to_centimeters(phase.duration_value)
            else:
                raise ValueError(f"Unsupported duration type: {phase.duration_type}")
        except Exception as e:
            raise ValueError(f"Failed to set duration: {e}")

    def _set_pace_targets(self, step: WorkoutStepMessage, intensity) -> None:
        """Set pace targets for a workout step."""
        try:
            step.target_type = WorkoutStepTarget.SPEED
            # Convert m/s to m/s * 1000 for FIT file format
            speed_low = int(intensity.pace_min * 1000)   # Slower pace = lower speed
            speed_high = int(intensity.pace_max * 1000)  # Faster pace = higher speed
            
            # Set the custom target values
            field = step.get_field(WorkoutStepCustomTargetValueLowField.ID)
            if field:
                sub_field = field.get_valid_sub_field([field])
                field.set_value(0, speed_low, sub_field)
                
            field = step.get_field(WorkoutStepCustomTargetValueHighField.ID)
            if field:
                sub_field = field.get_valid_sub_field([field])
                field.set_value(0, speed_high, sub_field)
                
        except Exception as e:
            raise ValueError(f"Failed to set pace targets: {e}")

    def _get_intensity(self, phase_type: str) -> Intensity:
        """Map phase type to FIT file intensity."""
        intensity_map = {
            "warmup": Intensity.WARMUP,
            "cooldown": Intensity.COOLDOWN,
            "steady_state": Intensity.ACTIVE,
            "interval": Intensity.INTERVAL,
            "recovery": Intensity.RECOVERY
        }
        return intensity_map.get(phase_type, Intensity.ACTIVE)

class FitFileGenerator:
    """Generates FIT files and associated metadata for training plan workouts."""
    
    def __init__(self, output_dir: str):
        """Initialize the generator with output directory."""
        self.output_dir = Path(output_dir)
        self.converter = UnitConverter()
        self.step_builder = WorkoutStepBuilder(self.converter)
        
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create output directory: {e}")

    def generate_workout_artifacts(self, training_plan: TrainingPlan) -> Dict[str, WorkoutArtifacts]:
        """Generate FIT files and metadata for all workouts in the training plan."""
        try:
            self._validate_training_plan(training_plan)
            artifacts = {}
            
            for week in training_plan.weeks:
                for workout in week.workouts:
                    workout_id = f"week{week.week_number}_{workout.scheduled_date}_{workout.workout_subtype[0]}"
                    
                    fit_file_path = self._generate_workout_file(workout, week.week_number)
                    notes = self._collect_workout_notes(workout)
                    
                    artifacts[workout_id] = WorkoutArtifacts(
                        fit_file_path=fit_file_path,
                        notes=notes,
                        workout_id=workout_id
                    )
            
            return artifacts
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate workout artifacts: {e}")

    def _validate_training_plan(self, plan: TrainingPlan) -> None:
        """Validate training plan structure and content."""
        if not plan.weeks:
            raise ValueError("Training plan has no weeks")
        for week in plan.weeks:
            if not week.workouts:
                raise ValueError(f"Week {week.week_number} has no workouts")
            for workout in week.workouts:
                if not workout.phases:
                    raise ValueError(f"Workout on {workout.scheduled_date} has no phases")

    def _generate_workout_file(self, workout: Workout, week_number: int) -> Path:
        """Generate a FIT file for a single workout."""
        try:
            builder = FitFileBuilder(auto_define=True)
            
            # Add messages
            self._add_file_id(builder)
            self._add_workout_message(builder, workout)
            self._add_workout_steps(builder, workout)
            
            # Save file
            filename = f"week{week_number}_{workout.scheduled_date}_{workout.workout_subtype[0]}.fit"
            file_path = self.output_dir / filename
            
            fit_file = builder.build()
            fit_file.to_file(str(file_path)) # Write the workout to a .fit file
            
            return file_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate workout file: {e}")

    def _add_file_id(self, builder: FitFileBuilder) -> None:
        """Add file ID message to the builder."""
        file_id = FileIdMessage()
        file_id.type = FileType.WORKOUT
        file_id.manufacturer = Manufacturer.DEVELOPMENT.value
        file_id.product = 0
        file_id.time_created = round(datetime.now().timestamp() * 1000)
        file_id.serial_number = 0x12345678
        builder.add(file_id)

    def _add_workout_message(self, builder: FitFileBuilder, workout: Workout) -> None:
        """Add workout message to the builder."""
        workout_message = WorkoutMessage()
        workout_message.sport = Sport.RUNNING
        workout_message.num_valid_steps = self._count_total_steps(workout.phases)
        builder.add(workout_message)

    def _add_workout_steps(self, builder: FitFileBuilder, workout: Workout) -> None:
        """Add all workout steps to the builder."""
        for phase in workout.phases:
            if isinstance(phase, SinglePhase):
                step = self.step_builder.build_step(phase)
                builder.add(step)
            elif isinstance(phase, IntervalSet):
                for _ in range(phase.repetitions):
                    for interval in phase.intervals:
                        step = self.step_builder.build_step(interval)
                        builder.add(step)

    def _count_total_steps(self, phases: List[Phase]) -> int:
        """Count total number of steps in all phases."""
        total = 0
        for phase in phases:
            if isinstance(phase, SinglePhase):
                total += 1
            elif isinstance(phase, IntervalSet):
                total += phase.repetitions * len(phase.intervals)
        return total

    def _collect_workout_notes(self, workout: Workout) -> str:
        """Collect all notes and instructions for a workout."""
        notes = []
        
        if workout.additional_instructions:
            notes.append(f"Workout Instructions: {workout.additional_instructions}")
        
        for phase in workout.phases:
            if isinstance(phase, SinglePhase):
                if phase.notes:
                    notes.append(f"{phase.type.title()} Phase: {phase.notes}")
            elif isinstance(phase, IntervalSet):
                notes.append(f"Interval Set ({phase.repetitions}x):")
                for interval in phase.intervals:
                    if interval.notes:
                        notes.append(f"- {interval.type.title()}: {interval.notes}")
        
        return "\n".join(notes)