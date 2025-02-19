import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import requests
from wmda_match.modules.create_patient_search import get_bearer_token, get_wmdaid_from_db, update_search_id_in_db, create_patient_search

class TestWMDAFunctions(unittest.TestCase):

    @patch('requests.post')
    def test_get_bearer_token(self, mock_post):
        # Mock the response of the POST request to get the bearer token
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'mock_token'}
        mock_post.return_value = mock_response

        token = get_bearer_token()
        self.assertEqual(token, 'mock_token')  # Check that the token is correctly returned

    @patch('sqlite3.connect')
    def test_get_wmdaid_from_db(self, mock_connect):
        # Mock the SQLite database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        donor_id = '12345'
        mock_cursor.fetchone.return_value = ['mock_wmda_id']

        wmda_id = get_wmdaid_from_db(donor_id)
        self.assertEqual(wmda_id, 'mock_wmda_id')  # Check if wmdaId is correctly retrieved from the DB

    @patch('sqlite3.connect')
    def test_update_search_id_in_db(self, mock_connect):
        # Mock the SQLite database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        donor_id = '12345'
        search_id = '67890'

        # Test if the search ID is correctly updated
        update_search_id_in_db(donor_id, search_id)
        mock_cursor.execute.assert_called_with(
            "UPDATE person_data SET SearchID = ? WHERE DONN_NUMERO = ?",
            (search_id, donor_id)
        )  # Check that the SQL query is correctly executed

    @patch('requests.post')
    @patch('wmda_match.modules.create_patient_search.get_bearer_token')
    @patch('wmda_match.modules.create_patient_search.get_wmdaid_from_db')
    @patch('wmda_match.modules.create_patient_search.update_search_id_in_db')
    def test_create_patient_search(self, mock_update, mock_get_wmdaid, mock_get_token, mock_post):
        # Mock the helper functions
        mock_get_wmdaid.return_value = 'mock_wmda_id'
        mock_get_token.return_value = 'mock_token'
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'searchId': 'mock_search_id'}
        mock_post.return_value = mock_response
        
        donor_id = '12345'

        # Test if the patient search is created successfully
        create_patient_search(donor_id)
        
        # Check if update_search_id_in_db was called with the correct arguments
        mock_update.assert_called_with(donor_id, 'mock_search_id')
        
        # Correct the User-Agent to match the actual one in the request
        mock_post.assert_called_with(
            'https://sandbox-search-api.wmda.info/api/v2/searches',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer mock_token',
                'User-Agent': 'NHSBT-Data-Analytics/1.0 (+https://www.nhsbt.nhs.uk)'  # Corrected User-Agent
            },
            json={
                "wmdaId": 'mock_wmda_id',
                "matchEngine": 2,
                "searchType": "DR",
                "overallMismatches": 0,
                "isCbuAbLowDrb1HighResolution": False,
                "searchOnlyOwnIon": False
            }
        )

if __name__ == '__main__':
    unittest.main()
