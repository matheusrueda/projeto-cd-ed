import unittest
from unittest.mock import ANY, patch
import requests


from src.extracao_ibge import enforce_timeout  # noqa: E402


class TestExtracaoIbgeSecurity(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()

    @patch('requests.Session.request')
    def test_enforce_timeout_adds_verify_true(self, mock_request):
        with enforce_timeout():
            self.session.request('GET', 'http://example.com')

        mock_request.assert_called_once_with(
            ANY, 'GET', 'http://example.com', timeout=(3.0, 15.0), verify=True
        )

    @patch('requests.Session.request')
    def test_enforce_timeout_respects_existing_verify(self, mock_request):
        with enforce_timeout():
            self.session.request('GET', 'http://example.com', verify='/cert')

        mock_request.assert_called_once_with(
            ANY, 'GET', 'http://example.com', verify='/cert',
            timeout=(3.0, 15.0)
        )

    @patch('requests.Session.request')
    def test_enforce_timeout_respects_existing_verify_false(self, mock_req):
        with enforce_timeout():
            self.session.request('GET', 'http://example.com', verify=False)

        mock_req.assert_called_once_with(
            ANY, 'GET', 'http://example.com', verify=False, timeout=(3.0, 15.0)
        )


if __name__ == '__main__':
    unittest.main()
