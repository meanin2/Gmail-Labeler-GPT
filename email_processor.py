import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import re


# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import base64
from email.mime.text import MIMEText


def preprocess_email_content(email_content):
    if email_content is None:
        return ""

    # Enhanced logic for HTML content
    if bool(BeautifulSoup(email_content, "html.parser").find()):
        soup = BeautifulSoup(email_content, 'html.parser')
        
        # Remove scripts, styles, and other non-textual elements
        for script_or_style in soup(["script", "style", "meta", "link"]):
            script_or_style.extract()

        # Extract text and handle special characters/encoding
        text = soup.get_text(separator=' ')
        text = text.encode('utf-8').decode('unicode_escape')

    else:
        # For plain text, use it as is and handle special characters/encoding
        text = email_content.encode('utf-8').decode('unicode_escape')

    # Logic to remove quoted text (if applicable)
    # Example: Removing lines that start with '>' (common in quoted emails)
    text = "\n".join([line for line in text.splitlines() if not line.startswith('>')])

    # Removing URLs and email addresses (as per existing logic, can be enhanced if needed)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)  # Example of removing email addresses

    return text
def authenticate_gmail():
    """Authenticates with Gmail API and returns a service object with OAuth."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_78494116749-u7b1qfddt5cvbn8i3f6hfe6mc58pf22a.apps.googleusercontent.com.json',  # Replace with your client secret file name
                scopes=['https://www.googleapis.com/auth/gmail.modify']
            )
            creds = flow.run_local_server(port=0)


        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_unread_emails(gmail_service):
    """Fetches unread emails from Gmail."""
    """
    Fetch unread emails that are not marked as 'Processed'.
    """
    # Fetch emails that are unread and don't have the 'Processed' label
    query = 'is:unread -label:Processed'
    results = gmail_service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        logger.info('No new emails found.')
        return []
    else:
        print(f'Found {len(messages)} new emails.')
        return messages

def extract_email_content(gmail_service, email_id):
    """
    Extract the relevant content (subject, body) from the email object.
    """
    message = gmail_service.users().messages().get(userId='me', id=email_id, format='full').execute()
    
    # Decode the email subject and body
    subject, body = None, None
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            subject = header['value']
            break
    if 'data' in message['payload']['body']:
        body_bytes = base64.urlsafe_b64decode(message['payload']['body']['data'].encode('UTF-8'))
        body = body_bytes.decode('utf-8')
    elif 'parts' in message['payload']:

        # If the email body is in multipart format
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body_bytes = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
                body = body_bytes.decode('utf-8')
                break
    # Apply preprocessing to the email body
    body = preprocess_email_content(body)
    return {'subject': subject, 'body': body}

import re





def extract_label_from_response(api_response):
    valid_labels = ['Work', 'Personal', 'Promotions', 'Social', 'Spam', 'Unknown']
    try:
        label_content = api_response['choices'][0]['message']['content'].lower()
        
        for label in valid_labels:
            if label.lower() in label_content:
                return label
        return "Unknown"
    except (KeyError, IndexError):
        return "Error in response format"


def apply_label_to_email(gmail_service, email_id, label):
    """
    Apply the given label to the email with the specified email_id.
    """
    # Create a label if not exists and get label id
    label_id = create_label_if_not_exists(gmail_service, label)

    # Apply the category label to the email
    gmail_service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label_id]}).execute()

    # Additional step: Mark email as processed by applying a 'Processed' label
    processed_label_id = create_label_if_not_exists(gmail_service, 'Processed')
    gmail_service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [processed_label_id]}).execute()


def create_label_if_not_exists(gmail_service, label_name):
    """
    Create a new label if it does not exist and return the label ID.
    """
    # Fetch existing labels
    existing_labels = gmail_service.users().labels().list(userId='me').execute().get('labels', [])
    label_id = next((label['id'] for label in existing_labels if label['name'] == label_name), None)

    # Create label if not found
    if not label_id:
        label_body = {'name': label_name}
        created_label = gmail_service.users().labels().create(userId='me', body=label_body).execute()
        label_id = created_label['id']

    return label_id
