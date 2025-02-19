import unittest
from unittest.mock import patch, MagicMock
import json
import os
from dotenv import load_dotenv
from wmda_match.modules.patient_list import get_bearer_token, get_patient_data  # Import the functions from your module

# Load environment variables from the .env file
load_dotenv()

class TestPatientListAPI(unittest.TestCase):

    @patch('wmda_match.modules.patient_list.requests.post')
    def test_get_bearer_token_success(self, mock_post):
        # Mock the response of the POST request to get the bearer token
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'mock_access_token'
        }
        mock_post.return_value = mock_response

        # Call the function
        token = get_bearer_token()

        # Assert the token is correct
        self.assertEqual(token, 'mock_access_token')
        mock_post.assert_called_once_with(
            "https://login.microsoftonline.com/" + os.getenv("TENANT_ID") + "/oauth2/token",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': os.getenv("USER_AGENT")
            },
            data={
                'grant_type': 'client_credentials',
                'client_id': os.getenv("CLIENT_ID"),
                'client_secret': os.getenv("CLIENT_SECRET"),
                'resource': os.getenv("RESOURCE_ID")
            }
        )

    @patch('wmda_match.modules.patient_list.requests.get')
    def test_get_patient_data_success(self, mock_get):
        # Mock the response of the GET request to retrieve patient data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'paging': {'totalCount': 2},
            'patients': [
                {'patientId': '1', 'wmdaId': 'wmda1', 'status': 'Active', 'dateOfBirth': '1980-01-01', 'ethnicity': 'Asian', 'assignedUserName': 'user1', 'lastUpdated': '2025-02-19', 'requests': []},
                {'patientId': '2', 'wmdaId': 'wmda2', 'status': 'Inactive', 'dateOfBirth': '1990-02-02', 'ethnicity': 'Caucasian', 'assignedUserName': 'user2', 'lastUpdated': '2025-02-19', 'requests': []}
            ]
        }
        mock_get.return_value = mock_response

        # Simulate the API call with a mock bearer token
        bearer_token = 'mock_access_token'
        get_patient_data(bearer_token)

        # Assert that the GET request was called with the correct parameters
        mock_get.assert_called_once_with(
            "https://sandbox-search-api.wmda.info/api/v2/patients",
            headers={
                "Authorization": "Bearer mock_access_token",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": os.getenv("USER_AGENT")
            },
            params={
                "Limit": 100,
                "OnlyMyPatients": False,
                "Offset": 0
            }
        )

    @patch('wmda_match.modules.patient_list.requests.post')
    def test_get_bearer_token_failure(self, mock_post):
        # Mock a failure response when trying to retrieve the bearer token
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        # Call the function
        token = get_bearer_token()

        # Assert that no token was returned
        self.assertIsNone(token)
        mock_post.assert_called_once()

    @patch('wmda_match.modules.patient_list.requests.get')
    def test_get_patient_data_failure(self, mock_get):
        # Mock a failure response when trying to retrieve patient data
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Simulate the API call with a mock bearer token
        bearer_token = 'mock_access_token'
        get_patient_data(bearer_token)

        # Assert that the GET request was called
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
