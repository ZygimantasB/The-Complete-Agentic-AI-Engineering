import os
import base64
from email.mime.text import MIMEText
from typing import Dict
from decouple import config

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agents import Agent, function_tool

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    """Authenticate and return Gmail service"""
    print("=" * 50)
    print("[DEBUG] Starting Gmail authentication...")
    creds = None

    # Token stores your access/refresh tokens
    if os.path.exists('token.json'):
        print("[DEBUG] Found existing token.json, loading credentials...")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print("[DEBUG] Credentials loaded from token.json")
    else:
        print("[DEBUG] No token.json found, will need to authenticate")

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[DEBUG] Credentials expired, refreshing...")
            creds.refresh(Request())
            print("[DEBUG] Credentials refreshed successfully")
        else:
            print("[DEBUG] Starting OAuth flow - browser should open...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("[DEBUG] OAuth flow completed successfully")

        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("[DEBUG] Credentials saved to token.json")
    else:
        print("[DEBUG] Credentials are valid")

    print("[DEBUG] Building Gmail service...")
    service = build('gmail', 'v1', credentials=creds)
    print("[DEBUG] Gmail service built successfully")
    return service


def _send_email_impl(subject: str, html_body: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body"""
    print("=" * 50)
    print("[DEBUG] send_email function called")
    print(f"[DEBUG] Subject: {subject}")
    print(f"[DEBUG] HTML body length: {len(html_body)} characters")

    service = get_gmail_service()

    to_email = config("SEND_EMAIL")
    print(f"[DEBUG] Sending to: {to_email}")

    message = MIMEText(html_body, 'html')
    message['to'] = to_email
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    print(f"[DEBUG] Message encoded, raw length: {len(raw)} characters")

    print("[DEBUG] Sending email via Gmail API...")
    try:
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        print("=" * 50)
        print(f"[SUCCESS] Email sent successfully!")
        print(f"[SUCCESS] Message ID: {result['id']}")
        print(f"[SUCCESS] Full response: {result}")
        print("=" * 50)
        return {"status": "success", "message_id": result['id']}
    except Exception as e:
        print("=" * 50)
        print(f"[ERROR] Failed to send email!")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"[ERROR] Error message: {str(e)}")
        print("=" * 50)
        raise


@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body"""
    return _send_email_impl(subject, html_body)


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)


if __name__ == "__main__":
    # Test the email sending directly
    print("=" * 50)
    print("TESTING EMAIL AGENT")
    print("=" * 50)

    test_subject = "Test Email from Email Agent"
    test_body = """
    <html>
        <body>
            <h1>Test Email</h1>
            <p>This is a test email sent from the Email Agent.</p>
            <p>If you receive this, the Gmail API is working correctly!</p>
        </body>
    </html>
    """

    # Call the implementation function directly
    result = _send_email_impl(test_subject, test_body)
    print(f"\nFinal result: {result}")
