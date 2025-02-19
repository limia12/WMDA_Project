import unittest
from unittest.mock import patch, MagicMock
import json
import sqlite3

# Import the script you want to test (assuming the script is named wmda_script.py)
import wmda_match.modules.patient_search_list

class TestWMDAFunctions(unittest.TestCase):

    @patch('wmda_match.modules.patient_search_list.sqlite3.connect')
    def test_get_wmda_id(self, mock_connect):
        # Setup mock for sqlite3 connection
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('215508',)  # Simulate the returned wmdaId

        donor_id = '2255001'
        wmda_id =  wmda_match.modules.patient_search_list.get_wmda_id(donor_id)

        # Assert that the wmdaId is correctly fetched from the database
        mock_cursor.execute.assert_called_once_with("SELECT wmdaId FROM person_data WHERE DONN_NUMERO = ?", (donor_id,))
        self.assertEqual(wmda_id, '215508')

    @patch('wmda_match.modules.patient_search_list.get_bearer_token')
    @patch('wmda_match.modules.patient_search_list.requests.get')
    def test_get_patient_searches(self, mock_get, mock_get_bearer_token):
        # Setup mock for the Bearer Token and API request
        mock_get_bearer_token.return_value = 'dummy_token'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search_results": "dummy_data"}
        mock_get.return_value = mock_response

        wmda_id = '215508'
        with patch('builtins.print') as mock_print:
            wmda_match.modules.patient_search_list.get_patient_searches(wmda_id)

            # Assert the correct API URL is called
            mock_get.assert_called_once_with(
                f"https://sandbox-search-api.wmda.info/api/v2/searches/patientSearches/{wmda_id}",
                headers={"Authorization": "Bearer dummy_token", "Content-Type": "application/json", "User-Agent": "NHSBT-Data-Analytics/1.0 (+https://www.nhsbt.nhs.uk)"}
            )

            # Check if the search results are printed in the correct format
            mock_print.assert_any_call("Search Results for wmdaId:", wmda_id)
            mock_print.assert_any_call(json.dumps({"search_results": "dummy_data"}, indent=4))

    @patch('wmda_match.modules.patient_search_list.get_bearer_token')
    @patch('wmda_match.modules.patient_search_list.requests.get')
    def test_get_patient_searches_error(self, mock_get, mock_get_bearer_token):
        # Setup mock for Bearer Token failure
        mock_get_bearer_token.return_value = None

        wmda_id = '215508'
        with patch('builtins.print') as mock_print:
            wmda_match.modules.patient_search_list.get_patient_searches(wmda_id)

            # Assert the error message is printed when unable to get token
            mock_print.assert_called_with("Unable to get bearer token. Aborting.")

    @patch('wmda_match.modules.patient_search_list.get_bearer_token')
    @patch('wmda_match.modules.patient_search_list.requests.get')
    def test_get_patient_searches_api_error(self, mock_get, mock_get_bearer_token):
        # Setup mock for successful bearer token and API error response
        mock_get_bearer_token.return_value = 'dummy_token'

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_get.return_value = mock_response

        wmda_id = '215508'
        with patch('builtins.print') as mock_print:
            wmda_match.modules.patient_search_list.get_patient_searches(wmda_id)

            # Assert the error message is printed for API error
            mock_print.assert_called_with(f"Error retrieving search results: 500, Response: Internal Server Error")

if __name__ == "__main__":
    unittest.main()
