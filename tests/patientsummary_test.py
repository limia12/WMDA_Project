import unittest
import json
from unittest.mock import patch, MagicMock
from wmda_match.modules import patientsummary

class TestPatientSummary(unittest.TestCase):
    
    @patch('wmda_match.modules.patientsummary.requests.post')
    def test_get_bearer_token_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value = mock_response

        token = patientsummary.get_bearer_token()
        self.assertEqual(token, 'test_token')

    @patch('wmda_match.modules.patientsummary.requests.post')
    def test_get_bearer_token_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        token = patientsummary.get_bearer_token()
        self.assertIsNone(token)

    @patch('wmda_match.modules.patientsummary.sqlite3.connect')
    def test_get_search_id_found(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = ('26774',)
        
        search_id = patientsummary.get_search_id('5800816')
        self.assertEqual(search_id, '26774')

    @patch('wmda_match.modules.patientsummary.sqlite3.connect')
    def test_get_search_id_not_found(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None
        
        search_id = patientsummary.get_search_id('invalid_patient')
        self.assertIsNone(search_id)

    @patch('wmda_match.modules.patientsummary.requests.get')
    @patch('wmda_match.modules.patientsummary.get_bearer_token', return_value='test_token')
    def test_get_search_summary_success(self, mock_get_token, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'summary': 'Test Data'}
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            patientsummary.get_search_summary('26774')
            mock_print.assert_any_call(json.dumps({"summary": "Test Data"}, indent=4))


    @patch('wmda_match.modules.patientsummary.requests.get')
    @patch('wmda_match.modules.patientsummary.get_bearer_token', return_value='test_token')
    def test_get_search_summary_failure(self, mock_get_token, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            patientsummary.get_search_summary('invalid_search_id')
            mock_print.assert_any_call('Error retrieving search summary: 404, Response: Not Found')

if __name__ == '__main__':
    unittest.main()
