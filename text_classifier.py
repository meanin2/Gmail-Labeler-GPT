import logging
import requests
import os

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def authenticate_lmstudio():
    """
    Prepare headers for communicating with the lmstudio API.
    Authentication details are loaded from environment variables.
    """
    api_key = os.getenv('lmstudio_API_KEY')
    headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
    return headers

def classify_text(text, headers):
    """
    Send the given text to the lmstudio API for classification.
    Returns the classification result (label).
    """
    endpoint = "http://127.0.0.1:1234/v1/chat/completions"
    print("Endpoint for lmstudio API:", endpoint)  # Added print statement

    # Construct the prompt
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that can categorize emails."
            },
            {"role": "user", "content": "This is an email i got: \"" + text + "\" The categories are 'Work', 'Personal', 'Promotions', 'Social', 'Spam', or 'Unknown'. This email would be catagorized as: "}
        ],
        "mode": "instruct"
    }
    print("\n========== Prompt ========")
    print("Data being sent to lmstudio API:", data)  # Added print statement
    print("==========================\n")

    response = requests.post(endpoint, headers=headers, json=data, verify=False)
    print("Response status code:", response.status_code)  # Added print statement

    if response.status_code == 200:
        result = response.json()
        print("\n======== Response ========")
        print("API response:", result)  # Added print statement
        print("==========================\n")
        return result.get('choices')[0].get('message').get('content')
    else:
        logger.info(f'Error: Unable to classify text. Status code: {response.status_code}')
        return None

