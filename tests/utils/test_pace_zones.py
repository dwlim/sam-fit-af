import unittest
from src.utils.pace_zones import calculate_pace, speed_to_pace_string, format_pace_zones

# PYTHONPATH=$(pwd)/src pytest tests/utils/test_pace_zones.py -v
class TestPaceFunctions(unittest.TestCase):

    def test_calculate_pace(self):
        # Test standard input
        self.assertEqual(calculate_pace(100, 60), "10:00")   # 100m / 60s = 10:00/km
        self.assertEqual(calculate_pace(333, 100), "5:00")   # 333m / 100s = 5:00/km

        # Test equivalent paces
        self.assertEqual(calculate_pace(100, 80), "13:20")
        self.assertEqual(calculate_pace(1.25, 1), "13:20")
        
        # Test a pace where minutes is greater than 10
        self.assertEqual(calculate_pace(40, 60), "25:00")
        
        # Test zero time
        self.assertEqual(calculate_pace(1000, 0), "0:00")     # Distance but zero time
        
        # Test zero distance
        self.assertEqual(calculate_pace(0, 600), "0:00")      # Zero distance

    def test_speed_to_pace_string(self):

        test_cases = [
            (100/60,    "10:00"),      # unrounded version should yield 10:00
            (1.6666667,  "9:59"),      # should not round up to 10:00
            (3.33,       "5:00"),      # 5:00 min/km = 12 km/h = 3.33 m/s
            (2.78,       "5:59"),      # 5:59 min/km = 10 km/h = 2.78 m/s
            (2.5,        "6:40"),      # 6:40 min/km = 9 km/h = 2.5 m/s
            (4.17,       "3:59"),      # 3:59 min/km = 15 km/h = 4.17 m/s
            (0,          "0:00"),      # Edge case: zero speed
        ]
        
        for speed, expected in test_cases:
            assert speed_to_pace_string(speed) == expected

    def test_format_pace_zones(self):
        # Test with valid input
        pace_zones = {
            "Easy": [3.33, 100/60],
            "Marathon": [3.89, 3.33],
            "Threshold": [4.44, 4.17],
            "Interval": [5.0, 4.72],
            "Repetition": [5.56, 5.28]
        }
        expected_output = {
            "Easy": ["5:00", "10:00"],
            "Marathon": ["4:17", "5:00"],
            "Threshold": ["3:45", "3:59"],
            "Interval": ["3:20", "3:31"],
            "Repetition": ["2:59", "3:09"]
        }
        self.assertEqual(format_pace_zones(pace_zones), expected_output)
        
        # Test empty input
        self.assertEqual(format_pace_zones({}), {})
        
        # Test invalid input (non-numeric speeds)
        with self.assertRaises(TypeError):
            format_pace_zones({"Easy": ["fast", "slow"]})


if __name__ == "__main__":
    unittest.main()
