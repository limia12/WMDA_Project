import os
import sqlite3
import requests
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve API credentials from environment variables
TENANT_ID = os.getenv("TENANT_ID")
RESOURCE_ID = os.getenv("RESOURCE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")  # Loaded from .env file
API_URL = "https://sandbox-search-api.wmda.info/api/v2/patients"
    
def get_bearer_token():
    # Construct the token URL
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token"
    
    # Set headers and payload for the request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': USER_AGENT
    }
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'resource': RESOURCE_ID
    }

    # Make the request to get the bearer token
    response = requests.post(token_url, headers=headers, data=payload)

    # Check the response status
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        print("Error getting bearer token:", response.status_code, response.text)
        return None


# Step 2: Retrieve patient data using GET request
def get_patient_data(bearer_token):
    USER_AGENT = os.getenv("USER_AGENT")
    API_URL = os.getenv("API_URL")
    # Parameters for the API request
    params = {
        "Limit": 100,  # Maximum number of patients per page
        "OnlyMyPatients": False,  # Set to True to only return patients assigned to the current user
        "Offset": 0,  # Starting from the first page (set as required)
    }

    # Headers for authentication, content type, and user agent
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT  # Custom User Agent
    }

    # Send GET request to the API
    response = requests.get(API_URL, headers=headers, params=params)

    # Check for successful response
    if response.status_code == 200:
        # Parse JSON response
        response_data = response.json()

        # Print patient data (example: print first patient details)
        print("Total patients found:", response_data['paging']['totalCount'])
        for patient in response_data['patients']:
            print("\nPatient ID:", patient['patientId'])
            print("WMDA ID:", patient['wmdaId'])
            print("Status:", patient['status'])
            print("Date of Birth:", patient['dateOfBirth'])
            print("Ethnicity:", patient['ethnicity'])
            print("Assigned User:", patient['assignedUserName'])
            print("Last Updated:", patient['lastUpdated'])
            print("Requests Summary:", patient['requests'][0]['summary']['summaryText'] if patient['requests'] else "No requests")
    else:
        # Handle errors
        print(f"Failed to retrieve data. Status Code: {response.status_code}")
        print("Response:", response.text)

# Main execution flow
def main():
    # Step 1: Retrieve the Bearer Token
    bearer_token = get_bearer_token()
    if not bearer_token:
        print("Failed to retrieve bearer token.")
        return

    # Step 2: Retrieve and display patient data
    get_patient_data(bearer_token)

# Run the script
main()
