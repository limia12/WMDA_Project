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
API_URL_SEARCH = "https://sandbox-search-api.wmda.info/api/v2/searches/{searchId}"  # Modified URL with placeholder
    
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

# Function to retrieve the SearchID from the database using Patient ID (DONN_NUMERO)
def get_search_id(patient_id):
    # Connect to SQLite database
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()

    # Query to get SearchID based on DONN_NUMERO (Patient ID)
    cursor.execute("SELECT SearchID FROM person_data WHERE DONN_NUMERO=?", (patient_id,))
    search_id = cursor.fetchone()

    # Close the connection
    conn.close()

    if search_id:
        return search_id[0]
    else:
        print(f"No SearchID found for Patient ID {patient_id}")
        return None


# Function to retrieve search summary for a specific searchId
def get_search_summary(search_id):

    # Get Bearer Token
    token = get_bearer_token()
    if not token:
        print("Unable to get bearer token. Aborting.")
        return

    # Send a GET request to fetch search summary
    url = API_URL_SEARCH.format(searchId=search_id)  # Correct formatting of the URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT  # Custom User Agent
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        search_data = response.json()
        print(f"Search Summary for SearchID: {search_id}")
        print(json.dumps(search_data, indent=4))
    else:
        print(f"Error retrieving search summary: {response.status_code}, Response: {response.text}")

# Main function to run the script
def main():
    patient_id = input("Enter the Patient ID (DONN_NUMERO): ")

    # Retrieve SearchID for the given Patient ID
    search_id = get_search_id(patient_id)

    if search_id:
        # Retrieve search summary for the found SearchID
        get_search_summary(search_id)

if __name__ == "__main__":
    main()
