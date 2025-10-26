from services.email_service import send_email_cmd
import os

def practical_implementation():
    # Provide the recipient's email address
    to_email = "preethamreddyyelamancha@gmail.com"
    subject = "Test Email from Jarvis"
    message_body = "Hello, this is an automated test email sent from my personal AI assistant, Jarvis."
    
    # Check if credentials.json exists before attempting to send
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json file not found. Please download it from your Google Cloud Console.")
        return

    print("Attempting to send a real email...")
    response = send_email_cmd(to_email, subject, message_body)
    print(response)

if __name__ == "__main__":
    practical_implementation()