import os
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from models.model import GeminiModel
from utils.auth_utils import get_credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_email_cmd(to, subject, message_text):
    """Send an email using Gmail API."""
    creds = get_credentials()

    try:
        service = build('gmail', 'v1', credentials=creds)

        # 🔹 Allow multiple emails (list or single string)
        if isinstance(to, list):
            to = ", ".join(to)

        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {'raw': raw_message}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return f"Email sent successfully. To: {to}"
    except Exception as e:
        return f"Failed to send email: {e}"

def send_formatted_email_cmd(to, subject, user_content):
    """
    Formats content using Gemini and sends an email via Gmail API in one step.
    """
    try:
        # Step 1: Format content with Gemini
        gemini_model = GeminiModel()
        prompt = f"""
        You are an AI assistant that formats user-provided content into a professional and well-structured email.
        The user will provide the core message. Your task is to:
        1. Add a professional salutation.
        2. Structure the content into clear paragraphs.
        3. Add a professional closing.
        4. Add a placeholder for a signature.

        User content to be formatted:
        
        "{user_content}"
        
        Return only the formatted email message, without any extra conversation or markdown.
        """
        
        formatted_message = gemini_model.generate_text(prompt)
        
        # Step 2: Send the formatted email using your existing logic
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        if isinstance(to, list):
            to = ", ".join(to)

        message = MIMEText(formatted_message)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {'raw': raw_message}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        
        return f"Email sent successfully. To: {to}"
    except Exception as e:
        return f"Failed to send email: {e}"