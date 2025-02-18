import os
import sqlite3
import requests
import json
from dotenv import load_dotenv

# Load environment variables from the .env file, which contains sensitive information
# like the API URL, and user-agent string for API requests
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

def get_donor_data(donor_id):
    """
    Function to fetch donor details from the SQLite database using the donor ID.
    
    Args:
        donor_id (str): The unique donor ID (DONN_NUMERO) to fetch from the database.
        
    Returns:
        donor (tuple or None): Returns donor data as a tuple if found, else None if not found.
    """
    # Connect to the SQLite database (sample_data.db)
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()

    # Execute SQL query to retrieve donor data for the given donor ID
    cursor.execute("SELECT * FROM person_data WHERE DONN_NUMERO = ?", (donor_id,))

    # Fetch the donor data
    donor = cursor.fetchone()

    # Close the database connection
    conn.close()

    if donor:
        # Return donor data if found
        return donor
    else:
        # If donor not found, print message and return None
        print("Donor ID not found.")
        return None

def create_patient(donor):
    """
    Function to create a new patient on the WMDA using donor data.
    
    Args:
        donor (tuple): A tuple containing donor data retrieved from the database.
        
    This function constructs a patient data dictionary from the donor tuple and sends a
    POST request to the WMDA API to create a new patient.
    """
    # Extracting the donor data and preparing it to be sent as patient data
    patient_data = {
        "patientId": str(donor[0]),  # Convert donor ID to string for the API
        "hla": {
            "a": {"field1": donor[5], "field2": donor[6]},
            "b": {"field1": donor[7], "field2": donor[8]},
            "c": {"field1": donor[9], "field2": donor[10]},
            "drb1": {"field1": donor[11], "field2": donor[12]},
            "dqb1": {"field1": donor[13], "field2": donor[14]}
        },
        "idm": {
            "cmvStatus": "P"  # Placeholder; adjust as necessary
        },
        "dateOfBirth": donor[1],
        "diagnosis": {
            "diagnosisCode": "ALL",  # Placeholder; adjust as necessary
            "diagnosisText": "acute myeloid leukaemia",  # Placeholder; adjust as necessary
            "diagnosisDate": "2025-01-28"  # Placeholder; adjust as necessary
        },
        "diseasePhase": "PF",  # Placeholder; adjust as necessary
        "ethnicity": donor[3],
        "poolCountryCode": "NL",  # Placeholder; adjust as necessary
        "transplantCentreId": "TC X",  # Placeholder; adjust as necessary
        "abo": "A",  # Placeholder; adjust as necessary
        "rhesus": "P",  # Placeholder; adjust as necessary
        "weight": 76,  # Placeholder; adjust as necessary
        "sex": donor[4],
        "legalTerms": True  # Placeholder; adjust as necessary
    }

    # Printing the patient data to the console (for debugging purposes)
    print(patient_data)

    # Get Bearer Token for API authentication
    token = get_bearer_token()

    # Check if we successfully retrieved the token
    if not token:
        # If no token, print an error message and exit the function
        print("Unable to get bearer token. Aborting.")
        return

    # Retrieve USER_AGENT and API_URL from environment variables (loaded from .env file)
    USER_AGENT = os.getenv("USER_AGENT")
    API_URL = os.getenv("API_URL")

    # Prepare the headers for the HTTP request
    headers = {
        "Authorization": f"Bearer {token}",  # Authorization header with Bearer token
        "Content-Type": "application/json",  # Indicate that we're sending JSON data
        "User-Agent": USER_AGENT  # Custom user-agent string from environment variables
    }

    # Send a POST request to the WMDA API to create a new patient
    response = requests.post(API_URL, headers=headers, json=patient_data)

    # Check the status code of the response
    if response.status_code == 201:
        # If successful (201 Created), print a success message
        print("Patient created successfully!")
    else:
        # If an error occurred, print the status code and response text
        print(f"Error creating patient: {response.status_code}, Response: {response.text}")

def main():
    """
    Main function to run the script. This function prompts the user for a donor ID, 
    retrieves the donor data, and attempts to create a new patient on the WMDA using that data.
    """
    # Ask the user to input a donor ID
    donor_id = input("Enter the donor ID: ")

    # Retrieve donor data from the database
    donor = get_donor_data(donor_id)

    if donor:
        # If donor data is found, proceed to create the patient
        create_patient(donor)
    else:
        # If donor data is not found, print a message
        print("Donor not found in database.")

# Only execute the main function if this script is run directly (not imported as a module)
if __name__ == "__main__":
    main()
