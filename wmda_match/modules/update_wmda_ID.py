import os
import sqlite3
import requests
import json
from dotenv import load_dotenv


# Load environment variables from the .env file (e.g., API URL, user agent)
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


def get_patient_data(bearer_token):
    """
    Function to fetch patient data from an API using a GET request.

    Args:
        bearer_token (str): The Bearer token used for authentication.

    Returns:
        list: A list of patient data retrieved from the API.
    """

    # Parameters to send with the API request (limit, offset, etc.)
    params = {
        "Limit": 100,  # Set the maximum number of patients per request (100 patients)
        "OnlyMyPatients": False,  # Whether to return only the patients assigned to the current user
        "Offset": 0,  # Set the offset to 0 to start from the first page (can be adjusted for pagination)
    }

    # Headers for the HTTP request, including Authorization (with Bearer token) and Content-Type
    headers = {
        "Authorization": f"Bearer {bearer_token}",  # Authentication with Bearer token
        "Content-Type": "application/json",  # We're sending JSON data
        "Accept": "application/json",  # We expect the response to be in JSON format
        "User-Agent": USER_AGENT  # Custom User-Agent for this request
    }

    # Send a GET request to the API with the above parameters and headers
    response = requests.get(API_URL, headers=headers, params=params)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Parse the JSON response and return the 'patients' list
        response_data = response.json()  # Convert the JSON response to a Python dictionary
        return response_data['patients']  # Extract and return the list of patients
    else:
        # If the request failed, print the error status and message
        print(f"Failed to retrieve data. Status Code: {response.status_code}")
        print("Response:", response.text)
        return []  # Return an empty list if the request fails

def update_wmda_id_in_db(donn_numero, wmda_id):
    """
    Function to update the wmdaId in the SQLite database for a given donor number.

    Args:
        donn_numero (str): The donor number (DONN_NUMERO) used to identify the record.
        wmda_id (str): The new wmdaId to update in the database.
    """
    # Connect to the SQLite database where donor information is stored
    conn = sqlite3.connect('sample_data.db')  # Open a connection to the database
    cursor = conn.cursor()  # Create a cursor to execute SQL commands

    # Query the database to find the existing wmdaId for the given DONN_NUMERO
    cursor.execute(''' 
        SELECT wmdaId FROM person_data WHERE DONN_NUMERO = ? 
    ''', (donn_numero,))  # Use parameterized queries to prevent SQL injection
    existing_wmda_id = cursor.fetchone()  # Fetch the result of the query

    # Check if the wmdaId is either NULL or empty before updating
    if existing_wmda_id and (existing_wmda_id[0] == "" or existing_wmda_id[0] is None):
        # If the wmdaId is empty or NULL, update it with the new wmdaId
        cursor.execute(''' 
            UPDATE person_data 
            SET wmdaId = ? 
            WHERE DONN_NUMERO = ? 
        ''', (wmda_id, donn_numero))  # Execute the update query
        conn.commit()  # Commit the transaction to save changes
        print(f"Updated wmdaId for DONN_NUMERO {donn_numero} to {wmda_id}")  # Print success message
    else:
        # If the wmdaId is already populated, skip the update
        print(f"wmdaId already populated for DONN_NUMERO {donn_numero}, skipping update.")

    # Close the database connection to free up resources
    conn.close()

def main():
    """
    Main function to run the entire script. It retrieves the Bearer token,
    fetches patient data from the API, and updates the wmdaId for each patient
    in the SQLite database.
    """
    # Step 1: Retrieve the Bearer Token for API authentication
    bearer_token = get_bearer_token()  # Get the Bearer token using the helper function
    if not bearer_token:
        # If no token was retrieved, print an error message and exit
        print("Failed to retrieve bearer token.")
        return

    # Step 2: Retrieve patient data from the API using the Bearer token
    patients = get_patient_data(bearer_token)  # Fetch patient data from the API

    # Step 3: Loop through each patient and update their wmdaId in the database
    for patient in patients:
        donn_numero = patient.get('patientId')  # Get the patientId from the API response (matches DONN_NUMERO)
        wmda_id = patient.get('wmdaId')  # Get the wmdaId for this patient

        # If wmdaId is available, update it in the database
        if wmda_id:
            update_wmda_id_in_db(donn_numero, wmda_id)

# Run the main function to start the execution
main()


