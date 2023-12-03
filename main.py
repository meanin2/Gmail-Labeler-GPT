import time
import json
import logging
import email_processor
import text_classifier
from dotenv import load_dotenv
import re

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function orchestrating the email processing workflow."""
    # Load environment variables
    load_dotenv()

    # Authenticate Gmail and lmstudio services
    gmail_service = email_processor.authenticate_gmail()
    lmstudio_headers = text_classifier.authenticate_lmstudio()

    # Fetch unread emails
    unread_emails = email_processor.get_unread_emails(gmail_service)

    # Process each unread email
    for email in unread_emails:
        email_id = email['id']
        email_content = email_processor.extract_email_content(gmail_service, email_id)
        combined_content = f"{email_content['subject']} {email_content['body']}"
        
        # Enhanced print statements for better readability
        print("\n======== Email ===========")
        print("Processing Email ID:", email_id)
        print("Email Content:", email_content)
        print("==========================\n")
        
        # Wait for 5 seconds before processing the next email
        # time.sleep(3)
        
        llm_response = text_classifier.classify_text(combined_content, lmstudio_headers)
        # time.sleep(3)

        # Treat the LLM response as plain text and search for the tag
        if isinstance(llm_response, str):
            # Convert the LLM response to lowercase for case-insensitive search
            llm_response_lower = llm_response.lower()

            # Search for the tag or label you want (e.g., "Work", "Personal") within the plain text response
            if "work" in llm_response_lower:
                label = "Work"
            elif "personal" in llm_response_lower:
                label = "Personal"
            elif "promotions" in llm_response_lower:
                label = "Promotions"
            elif "social" in llm_response_lower:
                label = "Social"
            elif "spam" in llm_response_lower:
                label = "Spam"
            else:
                label = "Unknown"

            # Handle the label as needed
            if label in ['Work', 'Personal', 'Promotions', 'Social', 'Spam', 'Unknown']:
                email_processor.apply_label_to_email(gmail_service, email_id, label)
            else:
                logger.info(f'Unexpected label or no label determined for email ID: {email_id}')
        elif isinstance(llm_response, dict):
            # Normal JSON response handling (if needed)
            pass
        else:
            logger.error(f"Unexpected response format for email ID: {email_id}. Response type: {type(llm_response)}")
            continue

if __name__ == "__main__":
    main()
