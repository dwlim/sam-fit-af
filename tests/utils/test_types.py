import pytest
from pydantic import ValidationError
from src.utils.types import TrainingPlanInput

# PYTHONPATH=$(pwd)/src pytest tests/utils/test_types.py -v
class TestTrainingPlanInput:
    @pytest.fixture
    def valid_input(self):
        return {
            "sex": "male",
            "age": 28,
            "goal_event": {
                "event": 5000,
                "goal_time": {
                    "hours": 0,
                    "minutes": 20,
                    "seconds": 0
                }
            },
            "timeline_weeks": 2,
            "recent_time_trial": {
                "event": 5000,
                "hours": 0,
                "minutes": 20,
                "seconds": 0
            },
            "training_days_per_week": 3,
            "start_date": "2025-01-01"
        }

    def test_valid_input(self, valid_input):
        try:
            TrainingPlanInput.model_validate(valid_input)
        except ValidationError as e:
            pytest.fail(f"ValidationError raised unexpectedly: {e}")

    def test_invalid_sex(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["sex"] = "other"
        with pytest.raises(ValidationError, match="Input should be 'male' or 'female'"):
            TrainingPlanInput.model_validate(invalid_input)

    def test_invalid_age(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["age"] = -1
        with pytest.raises(ValidationError, match="Invalid value for 'age': must be a positive integer"):
            TrainingPlanInput.model_validate(invalid_input)

    def test_invalid_timeline_weeks(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["timeline_weeks"] = 0
        with pytest.raises(ValidationError, match="Invalid value for 'timeline_weeks': must be a positive integer"):
            TrainingPlanInput.model_validate(invalid_input)

    def test_invalid_training_days_per_week(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["training_days_per_week"] = 8
        with pytest.raises(ValidationError, match="Invalid value for 'training_days_per_week': must be an integer between 1 and 7"):
            TrainingPlanInput.model_validate(invalid_input)

    def test_invalid_goal_time_structure(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["goal_event"]["goal_time"]["minutes"] = 70
        with pytest.raises(ValidationError, match="Input should be less than 60"):
            TrainingPlanInput.model_validate(invalid_input)

    def test_invalid_recent_time_trial_distance(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["recent_time_trial"]["event"] = -5000
        with pytest.raises(ValidationError, match="Input should be greater than 0"):
            TrainingPlanInput.model_validate(invalid_input)

    def test_valid_with_edge_case_time_values(self, valid_input):
        valid_input["goal_event"]["goal_time"]["minutes"] = 59
        valid_input["goal_event"]["goal_time"]["seconds"] = 59
        try:
            TrainingPlanInput.model_validate(valid_input)
        except ValidationError:
            pytest.fail("ValidationError raised unexpectedly with edge case time values!")

    def test_invalid_with_overflow_time_values(self, valid_input):
        invalid_input = valid_input.copy()
        invalid_input["recent_time_trial"]["seconds"] = 70
        with pytest.raises(ValidationError, match="Input should be less than 60"):
            TrainingPlanInput.model_validate(invalid_input)
