import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils.auth_utils import get_credentials
from datetime import datetime, timedelta
import pytz



def normalize_event_times(event, default_duration_hours=1):
    """
    Ensure the event has valid start and end times for Google Calendar.

    Rules:
    - If end_time is given but start_time is missing → use start of that day as start.
    - If both are missing → use 'now' as start and +default_duration_hours for end.
    - If end_time is missing → use start_time + default_duration_hours.
    """

    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    start_str = event.get("start_time")
    end_str = event.get("end_time")

    try:
        # Case 1: Both start and end given
        if start_str and end_str:
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)

        # Case 2: Start missing, but end provided → start = beginning of end date
        elif end_str:
            end = datetime.fromisoformat(end_str)
            start = end.replace(hour=0, minute=0, second=0, microsecond=0)  # midnight of that day

        # Case 3: Start provided, end missing → default duration
        elif start_str:
            start = datetime.fromisoformat(start_str)
            end = start + timedelta(hours=default_duration_hours)

        # Case 4: Both missing → fallback to now
        else:
            start = now
            end = now + timedelta(hours=default_duration_hours)

    except Exception as e:
        print(f"⚠️ Failed to parse date/time: {e}, falling back to defaults")
        start = now
        end = now + timedelta(hours=default_duration_hours)

    # Format for Google Calendar
    event["start"] = {
        "dateTime": start.astimezone(tz).isoformat(),
        "timeZone": "Asia/Kolkata"
    }
    event["end"] = {
        "dateTime": end.astimezone(tz).isoformat(),
        "timeZone": "Asia/Kolkata"
    }

    # Remove raw keys to avoid confusion
    event.pop("start_time", None)
    event.pop("end_time", None)

    return event

def add_events_to_calendar(events):
    # Pass all required scopes to the credentials getter
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
    ]
    creds = get_credentials()
    if not creds:
        return "❌ Failed to get Google Calendar API credentials."
    
    # ... rest of your function remains the same ...
    try:
        service = build('calendar', 'v3', credentials=creds)
        added_count = 0
        for event_data in events:
            # Check for required fields and convert time strings
            if not all(k in event_data for k in ['summary', 'start_time', 'end_time']):
                print("Skipping malformed event:", event_data)
                continue
            event = normalize_event_times(event_data)
            event = {
                'summary': event['summary'],
                'description': event.get('description', ''),
                'start': {'dateTime': event['start']['dateTime']},
                'end': {'dateTime': event['end']['dateTime']},
            }
            print("Trying to add event to calendar:", event)
            service.events().insert(calendarId='primary', body=event).execute()
            added_count += 1

        return f"✅ Successfully added {added_count} events to your calendar."
    except Exception as e:
        return f"❌ Failed to add events to calendar: {e}"