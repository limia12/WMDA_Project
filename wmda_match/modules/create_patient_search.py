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
API_URL_SEARCH = "https://sandbox-search-api.wmda.info/api/v2/searches"

# Get bearer token
def get_bearer_token():
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token"
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

    response = requests.post(token_url, headers=headers, data=payload)

    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        print("Error getting bearer token:", response.status_code, response.text)
        return None

# Get WMDA ID from database using donor ID (DONN_NUMERO)
def get_wmdaid_from_db(donor_id):
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()

    # Update the table and column names to match your structure
    query = "SELECT wmdaId FROM person_data WHERE DONN_NUMERO = ?"
    cursor.execute(query, (donor_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]  # wmdaId
    else:
        print("No matching WMDA ID found for Donor ID:", donor_id)
        return None

# Update SearchID in the database
def update_search_id_in_db(donor_id, search_id):
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()

    # Update the SearchID for the given donor ID
    query = "UPDATE person_data SET SearchID = ? WHERE DONN_NUMERO = ?"
    cursor.execute(query, (search_id, donor_id))

    conn.commit()
    conn.close()
    print(f"Search ID {search_id} updated for Donor ID {donor_id}")

# Create patient search
def create_patient_search(donor_id):
    # Get WMDA ID using donor ID
    wmda_id = get_wmdaid_from_db(donor_id)
    if not wmda_id:
        print("Unable to retrieve WMDA ID. Aborting search creation.")
        return

    # Get bearer token
    token = get_bearer_token()
    if not token:
        print("Failed to obtain bearer token. Aborting search creation.")
        return

    # Set headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'User-Agent': USER_AGENT
    }

    # Construct the request payload with all required parameters
    payload = {
        "wmdaId": wmda_id,
        "matchEngine": 2,  # Assuming '2' is the match engine value you need; replace if different
        "searchType": "DR",  # Replace with the appropriate search type if different
        "overallMismatches": 0,  # Optional, if required by your specific use case
        "isCbuAbLowDrb1HighResolution": False,  # Optional, if needed
        "searchOnlyOwnIon": False  # Optional, if needed
    }

    # Make the API request to create the patient search
    response = requests.post(API_URL_SEARCH, headers=headers, json=payload)

    # Handle the response
    if response.status_code == 201:  # Success
        # Extract searchId from response
        response_data = response.json()
        search_id = response_data.get("searchId")
        if search_id:
            print(f"Patient search created successfully! Search ID: {search_id}")
            # Update the SearchID in the database
            update_search_id_in_db(donor_id, search_id)
        else:
            print("No search ID returned in the response.")
    else:
        print(f"Failed to create patient search: {response.status_code} {response.text}")


if __name__ == "__main__":
    donor_id = input("Enter Donor ID: ")
    create_patient_search(donor_id)
