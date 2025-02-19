import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import json
import wmda_match.modules.update_patient as update_patient

class TestUpdatePatient(unittest.TestCase):
    
    @patch("wmda_match.modules.update_patient.requests.post")
    def test_get_bearer_token_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value = mock_response

        token = update_patient.get_bearer_token()
        self.assertEqual(token, "mock_token")

    @patch("wmda_match.modules.update_patient.requests.post")
    def test_get_bearer_token_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid request"
        mock_post.return_value = mock_response

        token = update_patient.get_bearer_token()
        self.assertIsNone(token)

    @patch("wmda_match.modules.update_patient.sqlite3.connect")
    def test_get_existing_patient_data_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("123", "1990-01-01", "A", "Asian", "M", "A1", "A2", "B1", "B2", "C1", "C2", "DRB1_1", "DRB1_2", "DQB1_1", "DQB1_2", "WMDA123")
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        donor = update_patient.get_existing_patient_data("123")
        self.assertIsNotNone(donor)
        self.assertEqual(donor[0], "123")

    @patch("wmda_match.modules.update_patient.sqlite3.connect")
    def test_get_existing_patient_data_not_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        donor = update_patient.get_existing_patient_data("999")
        self.assertIsNone(donor)

    @patch("wmda_match.modules.update_patient.requests.put")
    @patch("wmda_match.modules.update_patient.get_bearer_token", return_value="mock_token")
    def test_update_patient_success(self, mock_get_token, mock_put):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_put.return_value = mock_response

        donor_data = ("123", "1990-01-01", "A", "Asian", "M", "A1", "A2", "B1", "B2", "C1", "C2", "DRB1_1", "DRB1_2", "DQB1_1", "DQB1_2", "WMDA123")
        update_patient.update_patient(donor_data)

        mock_put.assert_called_once()
        self.assertEqual(mock_put.call_args[1]["headers"]["Authorization"], "Bearer mock_token")

    @patch("wmda_match.modules.update_patient.requests.put")
    @patch("wmda_match.modules.update_patient.get_bearer_token", return_value="mock_token")
    def test_update_patient_failure(self, mock_get_token, mock_put):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_put.return_value = mock_response

        donor_data = ("123", "1990-01-01", "A", "Asian", "M", "A1", "A2", "B1", "B2", "C1", "C2", "DRB1_1", "DRB1_2", "DQB1_1", "DQB1_2", "WMDA123")
        update_patient.update_patient(donor_data)

        mock_put.assert_called_once()
        self.assertEqual(mock_put.call_args[1]["headers"]["Authorization"], "Bearer mock_token")

if __name__ == "__main__":
    unittest.main()
