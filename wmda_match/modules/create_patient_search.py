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
API_URL = os.getenv("API_URL")  # Loaded from .env file
    
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


# Function to get wmdaId from the SQLite database for a specific donor
def get_wmda_id(donor_id):
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT wmdaId FROM person_data WHERE DONN_NUMERO = ?", (donor_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return result[0]
    else:
        print("wmdaId not found for DONN_NUMERO:", donor_id)
        return None

# Function to update the SearchID for a specific donor in the database
def update_search_id(donor_id, search_id):
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()

    # Update the SearchID for the given donor
    cursor.execute("UPDATE person_data SET SearchID = ? WHERE DONN_NUMERO = ?", (search_id, donor_id))
    conn.commit()
    conn.close()

    print(f"Search ID {search_id} for donor ID {donor_id} has been updated in the database.")

# Function to start/update a patient search using POST request
def start_patient_search(wmda_id, donor_id):

    USER_AGENT = os.getenv("USER_AGENT")
    API_URL = os.getenv("API_URL")
    # Define the payload for the POST request
    search_data = {
        "wmdaId": wmda_id,
        "matchEngine": 2,  # Assuming "2" is the match engine ID; adjust as needed
        "searchType": "DR",  # Assuming DR search type; adjust as needed
        "overallMismatches": 0,
        "isCbuAbLowDrb1HighResolution": False,
        "searchOnlyOwnIon": False
    }

    # Get Bearer Token
    token = get_bearer_token()
    if not token:
        print("Unable to get bearer token. Aborting.")
        return

    # Send POST request to start/update the patient search
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json-patch+json",
        "User-Agent": USER_AGENT  # Custom User Agent
    }

    response = requests.post(API_URL, headers=headers, json=search_data)

    if response.status_code == 201:
        # Successful response
        response_data = response.json()
        search_id = response_data['searchId']
        print(f"Search started/updated successfully. Search ID: {search_id}")

        # Update the database with the new search ID
        update_search_id(donor_id, search_id)
    else:
        # Handle errors (e.g., bad request, unauthenticated, etc.)
        print(f"Error starting/updating search: {response.status_code}, Response: {response.text}")

# # Main function to run the script
# def main():
#     donor_id = input("Enter the donor ID: ")

#     # Retrieve wmdaId from the database
#     wmda_id = get_wmda_id(donor_id)

#     if wmda_id:
#         # Start or update the patient search using the wmdaId
#         start_patient_search(wmda_id, donor_id)
#     else:
#         print("wmdaId not found. Aborting search.")

# if __name__ == "__main__":
#     main()

