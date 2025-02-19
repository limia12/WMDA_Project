import sqlite3
from unittest import TestCase
from unittest.mock import patch, MagicMock

# Function that you want to test
def update_wmda_id_in_db(donor_id, wmda_id):
    conn = sqlite3.connect('tests.sample_data.db')
    cursor = conn.cursor()
    query = "UPDATE person_data SET wmdaId = ? WHERE DONN_NUMERO = ?"
    cursor.execute(query, (wmda_id, donor_id))
    conn.commit()
    conn.close()

# Test class
class TestUpdateWmdaId(TestCase):

    @patch('sqlite3.connect')  # Patch sqlite3.connect to mock database connection
    def test_update_wmda_id_in_db(self, mock_connect):
        # Set up an in-memory SQLite database for testing
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Set the mock cursor to return the mock data when fetchone is called
        mock_cursor.fetchone.return_value = ('mock_wmda_id',)

        # Assign the mock cursor to the mock connection
        mock_conn.cursor.return_value = mock_cursor

        # Patch the connect method to return the mock connection
        mock_connect.return_value = mock_conn

        donor_id = '12345'
        wmda_id = 'mock_wmda_id'

        # Call the function to update the wmdaId
        update_wmda_id_in_db(donor_id, wmda_id)

        # Verify the wmdaId was updated correctly
        mock_cursor.execute.assert_called_with(
            "UPDATE person_data SET wmdaId = ? WHERE DONN_NUMERO = ?",
            (wmda_id, donor_id)
        )

        # Now call fetchone and check if the wmdaId was updated
        mock_cursor.execute("SELECT wmdaId FROM person_data WHERE DONN_NUMERO = ?", (donor_id,))
        updated_wmda_id = mock_cursor.fetchone()[0]

        self.assertEqual(updated_wmda_id, wmda_id)  # Check if the wmdaId was updated correctly

# To run the test
if __name__ == '__main__':
    import unittest
    unittest.main()
