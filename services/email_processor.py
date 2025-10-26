# # services/email_processor.py
# import os
# import base64
# import re
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from models.model import GeminiModel

# # If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# def _get_credentials():
#     """Handles Gmail API authentication and returns credentials."""
#     creds = None
#     token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'token.json')
#     credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'credentials.json')

#     if os.path.exists(token_path):
#         creds = Credentials.from_authorized_user_file(token_path, SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open(token_path, 'w') as token:
#             token.write(creds.to_json())
#     return creds

# def extract_events_from_emails():
#     """
#     Reads unread emails, extracts event details using Gemini, and returns a list of events.
#     """
#     creds = _get_credentials()
#     if not creds:
#         return "❌ Failed to get Gmail API credentials."

#     try:
#         service = build('gmail', 'v1', credentials=creds)
#         results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
#         messages = results.get('messages', [])
        
#         if not messages:
#             return "✅ No new unread emails found."
        
#         gemini_model = GeminiModel()
#         events = []

#         for message in messages:
#             msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
#             headers = msg['payload']['headers']
#             sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
#             subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            
#             parts = msg['payload'].get('parts', [])
#             body_text = ""
#             for part in parts:
#                 if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
#                     body_text += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            
#             email_content = f"Sender: {sender}\nSubject: {subject}\nBody: {body_text}"

#             # --- UPDATED PROMPT ---
#             prompt = (
#                 "The following is an email. Extract any scheduled events, including meetings, interviews, "
#                 "exams, online sessions, and deadlines. The output should be a JSON object with a list "
#                 "of events. Each event should have 'summary' (e.g., 'Interview with ABC Corp'), "
#                 "'start_time', 'end_time', 'description' (including location or link), and 'event_type' "
#                 "(e.g., 'meeting', 'exam', 'deadline', 'interview'). If no events are found, return an empty list."
#                 f"\n\nEmail: {email_content}"
#             )
            
#             gemini_response = gemini_model.generate_text(prompt)
            
#             try:
#                 extracted_events = eval(gemini_response)
#                 if extracted_events:
#                     events.extend(extracted_events)
#             except Exception as e:
#                 print(f"Failed to parse Gemini response for email from {sender}: {e}")

#         return events

#     except Exception as e:
#         return f"❌ Failed to process emails: {e}"

import os
import base64
import json
import re
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models.model import GeminiModel
from utils.auth_utils import get_credentials

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]



def extract_events_from_emails():
    """Fetch unread emails from the last 3 days, extract sender details & event info via Gemini."""
    
    gemini_model = GeminiModel()
    creds = get_credentials()
    if not creds:
        return "❌ Failed to get Gmail API credentials."

    try:
        service = build('gmail', 'v1', credentials=creds)

        # --- 1. Prepare Gmail search query for last 3 days ---
        existing_query = "is:unread"
        primary_filter = "-category:social -category:promotions -category:updates"

        # Gmail API accepts duration format (e.g. newer_than:3d)
        query = f"{existing_query} newer_than:3d {primary_filter}".strip()



        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q=query
        ).execute()
        
        total_messages = results.get('resultSizeEstimate', 0)
        #print(f"📬 Gmail returned {total_messages} messages matching query: {query}")

        messages = results.get('messages', [])
        if not messages:
            return "✅ No unread emails in the last 3 days."

        events = []

        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # --- 2. Extract sender details ---
            headers = msg['payload']['headers']
            sender_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")

            # Parse sender details: "Name <email@domain>"
            sender_name = sender_header
            sender_email = ""
            match = re.match(r'(.*)<(.+?)>', sender_header)
            if match:
                sender_name = match.group(1).strip().strip('"')
                sender_email = match.group(2).strip()

            # --- 3. Get email body text ---
            body_text = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] in ['text/plain', 'text/html']:
                        body_text += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            else:
                if 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    body_text += base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8', errors='ignore')

            # --- 4. Filter by keywords before calling Gemini ---
            event_keywords = [
                "meeting", "exam", "interview", "deadline", "schedule",
                "session", "appointment", "webinar", "conference", "event",
                "shortlisting", "offer", "join", "joining", "reporting","assignment","assessment"
            ]

            if not any(kw.lower() in body_text.lower() for kw in event_keywords):
                #print(f"Skipping Gemini call (no event keywords) for email from {sender_header}")
                continue

            # --- 5. Prepare Gemini prompt ---
            email_content = f"Sender Name: {sender_name}\nSender Email: {sender_email}\nSubject: {subject}\nBody: {body_text}"

            prompt = (
                f"You are a reliable JSON parser. The following is an email. "
                f"Extract event details (meeting, interview, exam, deadline, etc). "
                f"Output must ONLY be a JSON list, no extra text. "
                f"Each event object should have: summary, start_time, end_time, description, event_type. "
                f"If there are no events, return [].\n\nEmail:\n{email_content}"
            )

            gemini_response = gemini_model.generate_text(prompt)
            #print("RAW Gemini response:", gemini_response)

            # --- 6. Extract JSON from Gemini response ---
        
            clean_response = gemini_response.strip()
            #  Remove code fences if present
            if clean_response.startswith("```"):
                # remove all ```json and trailing ```
                clean_response = clean_response.strip("`")
                # sometimes the first line is 'json'
                if clean_response.lower().startswith("json"):
                    clean_response = clean_response[4:].strip()


            #print("Cleaned Gemini response:", clean_response)

            try:
                extracted_events = json.loads(clean_response)
                if isinstance(extracted_events, list) and extracted_events:
                    # Add sender details to each event
                    for ev in extracted_events:
                        ev['sender_name'] = sender_name
                        ev['sender_email'] = sender_email
                    events.extend(extracted_events)
            except json.JSONDecodeError as e:
                print(f"Failed to parse Gemini response: {e}")

            # --- 7. Mark email as read ---
            service.users().messages().modify(
                userId='me',
                id=message['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        return events

    except Exception as e:
        return f"❌ Failed to process emails: {e}"
