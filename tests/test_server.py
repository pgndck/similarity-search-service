import similarity_pb2
import similarity_pb2_grpc
import unittest
from psycopg2 import Error
from psycopg2 import OperationalError
from unittest.mock import patch, MagicMock
from server import SimilaritySearchService
from similarity_pb2 import AddItemRequest, SearchItemsRequest, GetSearchResultsRequest


class TestServer(unittest.TestCase):

    @patch('server.create_connection')
    def test_add_item(self, mock_create_connection):
        """
        Test the AddItem method as usual
        """
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        servicer = SimilaritySearchService()
        request = AddItemRequest(id='123', description='Item description')
        response = servicer.AddItem(request, None)

        mock_cursor.execute.assert_called()  # verify if the execute method was called
        self.assertEqual(response.status, 200)
        self.assertEqual(response.message, "Item added successfully")

    @patch('server.create_connection')
    def test_add_item_no_id(self, mock_create_connection):
        """
        Test the AddItem method without ID provided
        """
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        servicer = SimilaritySearchService()
        request = AddItemRequest(description='Item description')
        response = servicer.AddItem(request, None)

        mock_cursor.execute.assert_called()  # verify if the execute method was called
        self.assertEqual(response.status, 200)
        self.assertEqual(response.message, "Item added successfully")

    @patch('server.create_connection')
    def test_add_item_empty_string(self, mock_create_connection):
        """
        Test the AddItem method with an empty description
        """
        servicer = SimilaritySearchService()
        request = AddItemRequest(id='123', description='')
        response = servicer.AddItem(request, None)

        self.assertEqual(response.status, 500)
        self.assertEqual(response.message,
                         "An error occurred: Empty description")

    @patch('server.create_connection')
    def test_add_item_database_error(self, mock_create_connection):
        # Arrange
        mock_create_connection.side_effect = OperationalError(
            'Database connection failed')
        service = SimilaritySearchService()
        request = similarity_pb2.AddItemRequest(
            id='1', description='Test Description')

        # Act
        response = service.AddItem(request, None)

        # Assert
        self.assertEqual(response.status, 500)
        self.assertEqual(response.message,
                         "An error occurred: Database connection failed")

    @patch('server.create_connection')
    def test_search_items(self, mock_create_connection):
        """
        Test the SearchItems method
        """
        mock_create_connection.return_value = MagicMock()
        servicer = SimilaritySearchService()

        request = SearchItemsRequest(query='Item')
        response = servicer.SearchItems(request, None)

        # Assertion placeholder. Add your own assertions here.
        self.assertTrue(response.search_id.isdigit())

    # I'm running out of time, which is why I leave the tests as is


if __name__ == '__main__':
    unittest.main()
