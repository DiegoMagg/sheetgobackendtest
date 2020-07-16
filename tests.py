import unittest
from app import application


class APITests(unittest.TestCase):

    def setUp(self):
        application.config['TESTING'] = True
        application.config['DEBUG'] = False
        self.test = application.test_client()

    def test_api_must_be_acessible(self):
        response = self.test.get('/api')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
