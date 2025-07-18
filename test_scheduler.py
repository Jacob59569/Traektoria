import unittest
from unittest.mock import patch
from scheduler import Scheduler

class TestScheduler(unittest.TestCase):
    sample = {
        "days": [
            {"id": 1, "date": "2024-10-10", "start": "09:00", "end": "18:00"},
            {"id": 2, "date": "2024-10-11", "start": "08:00", "end": "17:00"},
        ],
        "timeslots": [
            {"id": 1, "day_id": 1, "start": "11:00", "end": "12:00"},
            {"id": 2, "day_id": 2, "start": "09:30", "end": "16:00"},
        ]
    }

    @patch('scheduler.requests.get')
    def setUp(self, mock_get):
        mock_resp = mock_get.return_value
        mock_resp.json.return_value = self.sample
        mock_resp.raise_for_status.return_value = None
        self.scheduler = Scheduler(url='http://mock')

    def test_get_busy(self):
        self.assertEqual(self.scheduler.get_busy_slots("2024-10-10"), [("11:00","12:00")])
        self.assertEqual(self.scheduler.get_busy_slots("2024-10-12"), [])

    def test_get_free(self):
        self.assertEqual(self.scheduler.get_free_slots("2024-10-10"),
                         [("09:00","11:00"),("12:00","18:00")])
        self.assertEqual(self.scheduler.get_free_slots("2024-10-11"),
                         [("08:00","09:30"),("16:00","17:00")])

    def test_is_available(self):
        self.assertTrue(self.scheduler.is_available("2024-10-10","10:00","10:30"))
        self.assertFalse(self.scheduler.is_available("2024-10-10","11:30","12:30"))

    def test_find_slot(self):
        self.assertEqual(self.scheduler.find_slot_for_duration(60),
                         ("2024-10-10","09:00","10:00"))
        self.assertEqual(self.scheduler.find_slot_for_duration(90),
                         ("2024-10-10","09:00", "10:30"))

if __name__ == "__main__":
    unittest.main()
