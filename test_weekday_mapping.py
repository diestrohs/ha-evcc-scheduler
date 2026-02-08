import unittest
from custom_components.evcc_scheduler.mapping import weekdays_1to7_to_0to6, weekdays_0to6_to_1to7

class TestWeekdayMapping(unittest.TestCase):
    def test_1to7_to_0to6(self):
        self.assertEqual(weekdays_1to7_to_0to6([1,2,3,4,5,6,7]), [1,2,3,4,5,6,0])
        self.assertEqual(weekdays_1to7_to_0to6([7]), [0])
        self.assertEqual(weekdays_1to7_to_0to6([1,7]), [1,0])
        self.assertEqual(weekdays_1to7_to_0to6([]), [])
    def test_0to6_to_1to7(self):
        self.assertEqual(weekdays_0to6_to_1to7([0,1,2,3,4,5,6]), [7,1,2,3,4,5,6])
        self.assertEqual(weekdays_0to6_to_1to7([0]), [7])
        self.assertEqual(weekdays_0to6_to_1to7([1,0]), [1,7])
        self.assertEqual(weekdays_0to6_to_1to7([]), [])

if __name__ == "__main__":
    unittest.main()
