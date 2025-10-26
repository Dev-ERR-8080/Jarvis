import unittest
from unittest.mock import patch, MagicMock
from services.email_processor import extract_events_from_emails

class TestEmailProcessor(unittest.TestCase):

    @patch('services.email_processor.build')
    @patch('services.email_processor._get_credentials')
    @patch('services.email_processor.GeminiModel')
    def test_extract_events_from_emails(self, mock_gemini_model, mock_credentials, mock_build):
        # 1. Setup the mocks
        mock_credentials.return_value = MagicMock(valid=True)
        
        # Mock Gemini's response
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.generate_text.return_value = '[{"summary": "Test Meeting", "start_time": "2025-10-25T10:00:00", "end_time": "2025-10-25T11:00:00", "description": "Discuss project updates", "event_type": "meeting"}]'
        mock_gemini_model.return_value = mock_gemini_instance

        # Mock the Gmail API service response
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 2. Mock a sample unread email
        # This is the corrected structure to match the Gmail API response
        mock_msg = {
            'id': '123',
            'payload': {
                'headers': [{'name': 'From', 'value': 'test@example.com'}, {'name': 'Subject', 'value': 'Meeting'}],
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': 'VGVzdCBtZWV0aW5nIGZvciB0b21vcnJvdy4=' # Base64 encoded string
                        }
                    }
                ]
            }
        }
        
        mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {'messages': [{'id': '123'}]}
        mock_service.users.return_value.messages.return_value.get.return_value.execute.return_value = mock_msg
        
        # 3. Call the function
        events = extract_events_from_emails()

        # 4. Assert the results
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['summary'], "Test Meeting")
        self.assertEqual(events[0]['event_type'], "meeting")

if __name__ == "__main__":
    unittest.main()