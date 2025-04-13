import unittest
from datetime import timedelta
from src.utils.data_processing import (
    get_time_in_seconds,
    format_duration,
    format_seconds_to_time_string
)

# PYTHONPATH=$(pwd)/src pytest tests/utils/test_data_processing.py -v
class TestDataProcessing(unittest.TestCase):

    def test_get_time_in_seconds(self):
        # Test regular cases
        self.assertEqual(get_time_in_seconds({"hours": 1, "minutes": 30, "seconds": 45}), 5445.0)
        self.assertEqual(get_time_in_seconds({"hours": 0, "minutes": 45, "seconds": 30}), 2730.0)
        self.assertEqual(get_time_in_seconds({"hours": 0, "minutes": 0, "seconds": 30}), 30.0)
    
        # Test zero case
        self.assertEqual(get_time_in_seconds({"hours": 0, "minutes": 0, "seconds": 0}), 0.0)

    def test_format_duration(self):
        # Test with hours
        self.assertEqual(format_duration(timedelta(hours=1, minutes=30, seconds=45)), "1:30:45")
        
        # Test without hours
        self.assertEqual(format_duration(timedelta(minutes=45, seconds=30)), "45:30")
        
        # Test single digit seconds
        self.assertEqual(format_duration(timedelta(minutes=5, seconds=5)), "5:05")
        
        # Test zero case
        self.assertEqual(format_duration(timedelta(seconds=0)), "0:00")

    def test_format_seconds_to_time_string(self):
        # Test regular cases
        self.assertEqual(format_seconds_to_time_string(5445.0), "01:30:45")
        self.assertEqual(format_seconds_to_time_string(2730.0), "00:45:30")
        self.assertEqual(format_seconds_to_time_string(30.0), "00:00:30")
        
        # Test edge cases
        self.assertEqual(format_seconds_to_time_string(0), "00:00:00")
        self.assertIsNone(format_seconds_to_time_string(None))
        
        # Test floating point numbers
        self.assertEqual(format_seconds_to_time_string(30.6), "00:00:30")  # Should truncate
        self.assertEqual(format_seconds_to_time_string(30.4), "00:00:30")  # Should truncate
        
        # Test large numbers
        self.assertEqual(format_seconds_to_time_string(36000.0), "10:00:00")  # 10 hours

    def test_format_seconds_to_time_string_error_cases(self):
        # Test invalid inputs
        with self.assertRaises(TypeError):
            format_seconds_to_time_string("not a number")
        
        with self.assertRaises(TypeError):
            format_seconds_to_time_string([])
        
        # Test negative numbers
        with self.assertRaises(ValueError):
            format_seconds_to_time_string(-30.0)
        
        # Test NaN
        with self.assertRaises(ValueError):
            format_seconds_to_time_string(float('nan'))
        
        # Test infinity
        with self.assertRaises(ValueError):
            format_seconds_to_time_string(float('inf'))

if __name__ == "__main__":
    unittest.main()
