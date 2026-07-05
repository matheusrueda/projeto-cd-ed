import os
import sys
import unittest
from unittest.mock import ANY, patch, MagicMock
import requests

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)

from extracao_ibge import buscar_dados_ibge


class TestExtracaoIbgeSecurity(unittest.TestCase):

    @patch('extracao_ibge.get_legacy_session')
    def test_buscar_dados_ibge_uses_timeout_and_verify(self, mock_get_session):
        # Create a mock session and mock response
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [{"some": "data"}]
        mock_session.get.return_value = mock_response

        # Configure the context manager to return our mock session
        mock_get_session.return_value.__enter__.return_value = mock_session

        # Call the function
        buscar_dados_ibge("123", "456", "last12", "1", "all")

        # Check if the get method was called with verify=True and the correct timeout
        mock_session.get.assert_called_once_with(
            "https://apisidra.ibge.gov.br/values/t/123/n1/all/p/last12/v/456",
            timeout=(3.0, 15.0),
            verify=True
        )


if __name__ == '__main__':
    unittest.main()
