import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import json
from wmda_match.modules.create_patient import get_donor_data, create_patient

class TestCreatePatient(unittest.TestCase):
    
    @patch("wmda_match.modules.create_patient.sqlite3.connect")
    def test_get_donor_data(self, mock_connect):
        """Test fetching donor data from the database."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Sample donor data (matching expected schema)
        mock_cursor.fetchone.return_value = (
            "MypId-01", "1983-04-24", None, "HICA", "F", 
            "01:01", "24:02", "08:01", "07:02", "07:01", "07:02",
            "03:01", "15:01", "02:01", "06:02"
        )

        donor = get_donor_data("MypId-01")
        self.assertIsNotNone(donor)
        self.assertEqual(donor[0], "MypId-01")
        self.assertEqual(donor[1], "1983-04-24")

    @patch("wmda_match.modules.create_patient.get_bearer_token", return_value="mocked_token")
    @patch("wmda_match.modules.create_patient.requests.post")
    def test_create_patient(self, mock_post, mock_token):
        """Test patient creation with mocked API response."""
        # Mock donor data
        donor = (
            "MypId-01", "1983-04-24", None, "HICA", "F", 
            "01:01", "24:02", "08:01", "07:02", "07:01", "07:02",
            "03:01", "15:01", "02:01", "06:02"
        )

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Patient created successfully"}
        mock_post.return_value = mock_response

        create_patient(donor)

        # Verify request details
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer mocked_token")
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
        
        # Verify JSON structure
        patient_data = kwargs["json"]
        self.assertEqual(patient_data["patientId"], "MypId-01")
        self.assertEqual(patient_data["hla"]["a"]["field1"], "01:01")
        self.assertEqual(patient_data["hla"]["b"]["field2"], "07:02")

if __name__ == "__main__":
    unittest.main()
