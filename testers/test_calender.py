import unittest
from unittest.mock import patch, MagicMock
from services.calendar_service import add_events_to_calendar
import os

class TestCalendarService(unittest.TestCase):

    @patch('services.calendar_service.build')
    @patch('services.calendar_service._get_credentials')
    def test_add_events_to_calendar_success(self, mock_credentials, mock_build):
        # 1. Setup the mocks
        # Mock credentials
        mock_credentials.return_value = MagicMock(valid=True)
        
        # Mock the Calendar API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock the insert method
        mock_service.events.return_value.insert.return_value.execute.return_value = {'id': 'event_id_123'}

        # 2. Define test events
        test_events = [
            {'summary': 'Dentist Appointment', 'start_time': '2025-10-25T10:00:00', 'end_time': '2025-10-25T11:00:00', 'description': 'Checkup'}
        ]

        # 3. Call the function
        response = add_events_to_calendar(test_events)

        # 4. Assert the results
        self.assertIn("Successfully added 1 events", response)
        # Verify that the insert method was called once
        mock_service.events.return_value.insert.assert_called_once()
        # You can add a more detailed assertion to check the body of the call
        # mock_service.events.return_value.insert.assert_called_with(calendarId='primary', body=...)

if __name__ == "__main__":
    unittest.main()