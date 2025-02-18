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
API_URL_SEARCH = "https://sandbox-search-api.wmda.info/api/v2/searches/patientSearches/{wmdaId}"
    
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

# Function to retrieve all search results for a patient using their wmdaId
def get_patient_searches(wmda_id):

    # Get Bearer Token
    token = get_bearer_token()
    if not token:
        print("Unable to get bearer token. Aborting.")
        return

    # Send a GET request to fetch search results
    url = API_URL_SEARCH.format(wmdaId=wmda_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT  # Custom User Agent
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        search_data = response.json()
        print("Search Results for wmdaId:", wmda_id)
        print(json.dumps(search_data, indent=4))
    else:
        print(f"Error retrieving search results: {response.status_code}, Response: {response.text}")

# Main function to run the script
def main():
    donor_id = input("Enter the donor ID: ")

    # Retrieve wmdaId from the database
    wmda_id = get_wmda_id(donor_id)

    if wmda_id:
        # Retrieve all patient search results
        get_patient_searches(wmda_id)
    else:
        print("wmdaId not found. Aborting search retrieval.")

if __name__ == "__main__":
    main()
