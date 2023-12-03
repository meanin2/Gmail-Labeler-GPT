### Gmail Labeler GPT

#### Introduction
Gmail Labeler GPT is a Python-based email management system designed to automate the processing and categorization of emails. It uses modern text classification techniques and integrates with Gmail's API to streamline email workflows. This system is ideal for users looking to efficiently manage their inbox with the help of automated tools.

#### Installation
1. Clone the repository to your local machine.
2. Ensure Python 3.8 or later is installed on your system.
3. Install the requirments using pip. pip install -r requirements.txt

#### Gmail Setup
To use this application with your Gmail account, follow these steps:
1. Visit the [Google Developer Console](https://console.developers.google.com/).
2. Create a new project and enable the Gmail API.
3. In the credentials section, set up your OAuth consent screen.
4. Create OAuth client ID credentials.
5. Download the JSON file containing these credentials and place it in your project directory.
6. When you first run the application, you will be prompted to authorize access to your Gmail account.

#### Usage
Run `main.py` to start the email processing workflow. The script orchestrates interactions between the text classifier and the email processor.

#### Code Structure
- `main.py`: Orchestrates the overall workflow of the application.
- `text_classifier.py`: Handles text classification and external API interactions.
- `email_processor.py`: Manages email processing via the Gmail API.

#### Configuration
The env file is a formality and you shouldnt need the api key there. I have gotten errors when the api key was missing so i added it.

#### Dependencies
Dependencies are listed in the `requirements.txt` file, including libraries for API interaction, email processing, and text classification.

