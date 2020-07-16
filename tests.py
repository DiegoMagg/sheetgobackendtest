import unittest
from app import application

application.config['TESTING'] = True
application.config['DEBUG'] = False


class ViewsTests(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()

    def test_api_must_be_acessible(self):
        response = self.test.get('/')
        self.assertEqual(response.status_code, 200)


class APITests(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()

    def test_api_must_be_acessible(self):
        response = self.test.post('/api/excel/info/')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
