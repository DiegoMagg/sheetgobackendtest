import unittest
import sqlite3
from settings import BASE_DIR
from os import environ, path, remove
from app import application
from db import db
import jwt

application.config['TESTING'] = True
application.config['DEBUG'] = False
application.config.from_mapping(
    SECRET_KEY=environ.get('SEC_KEY', 'dev'),
    DATABASE=path.join(BASE_DIR, 'test.sqlite'),
)


class SQLTestCase(unittest.TestCase):

    def setUp(self):
        self.email = 'user@provider.com'

    def test_user_must_be_created(self):
        with application.app_context():
            self.db = db.init_db()
            conn = sqlite3.connect(application.config['DATABASE'])
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.email,))
            conn.commit()
            self.assertTrue(self.email in conn.execute('SELECT * FROM user').fetchone())
            db.close_db()
            remove(application.config['DATABASE'])


class ViewsTests(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()

    def test_frontpage_must_be_acessible(self):
        response = self.test.get('/')
        self.assertEqual(response.status_code, 200)


class APITests(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()
        self.data = {'email': 'user@provider.com'}

    def test_api_must_return_403_without_authentication_header(self):
        response = self.test.post('/api/excel/info/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {'detail': 'Authentication credentials were not provided.'})

    def test_api_must_return_403_with_invalid_credentials(self):
        token = jwt.encode(self.data, 'TESTSECRET', algorithm='HS256')
        response = self.test.post(
            '/api/excel/info/', headers={'Authorization': f'Bearer {token.decode("UTF-8")}'},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {'detail': 'Invalid credentials.'})

    def test_api_must_return_200_with_a_valid_token(self):
        with application.app_context():
            db.init_db()
            conn = sqlite3.connect(application.config['DATABASE'])
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.data['email'],))
            conn.commit()
            breakpoint()
            token = jwt.encode(self.data, environ.get('SEC_KEY', ''), algorithm='HS256')
            response = self.test.post(
                '/api/excel/info/', headers={'Authorization': f'Bearer {token.decode("UTF-8")}'},
            )
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
