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
    
# Function to fetch existing patient details from SQLite database using donor ID
def get_existing_patient_data(donor_id):
    conn = sqlite3.connect('sample_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM person_data WHERE DONN_NUMERO = ?", (donor_id,))
    donor = cursor.fetchone()
    conn.close()

    if donor:
        return donor
    else:
        print("Donor ID not found.")
        return None

# Function to update an existing patient on WMDA
def update_patient(donor):
    USER_AGENT = os.getenv("USER_AGENT")
    API_URL = os.getenv("API_URL")
    
    # Extracting the data from the donor
    patient_data = {
        "wmdaId": (donor[15]),
        "patientId": str(donor[0]),
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
    
    print("\n=== Patient Data for Update ===")
    print(json.dumps(patient_data, indent=4))

    # Get Bearer Token
    token = get_bearer_token()
    if not token:
        print("Unable to get bearer token. Aborting.")
        return

    # Send a PUT request to update an existing patient
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json-patch+json",
        "User-Agent": USER_AGENT  # Custom User Agent
    }

    response = requests.put(API_URL, headers=headers, json=patient_data)

    if response.status_code == 204:
        print("Patient updated successfully!")
    else:
        print(f"Error updating patient: {response.status_code}, Response: {response.text}")


# Main function to run the script
def main():
    donor_id = input("Enter the donor ID to update: ")

    # Retrieve existing patient data from the database
    donor = get_existing_patient_data(donor_id)

    if donor:
        # Update patient on WMDA API
        update_patient(donor)
    else:
        print("Donor not found in database.")

if __name__ == "__main__":
    main()
