import unittest
import sqlite3
from settings import BASE_DIR
from os import environ, path, remove
from app import application
from db import db
import jwt
import openpyxl


environ['DATABASE'] = 'test.sqlite'
application.config['TESTING'] = True
application.config['DEBUG'] = False
application.config.from_mapping(
    SECRET_KEY=environ.get('SEC_KEY', 'dev'),
    DATABASE=path.join(BASE_DIR, environ.get('DATABASE')),
)


class CommandsTesCase(unittest.TestCase):

    def setUp(self):
        self.runner = application.test_cli_runner()

    def test_init_db(self):
        self.assertTrue('Initialized the database' in self.runner.invoke(db.init_db_command).output)


class SQLTestCase(unittest.TestCase):

    def setUp(self):
        self.email = 'user@provider.com'

    def test_user_must_be_created(self):
        with application.app_context():
            self.db = db.init_db()
            conn = sqlite3.connect(environ['DATABASE'])
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.email,))
            conn.commit()
            self.assertTrue(self.email in conn.execute('SELECT * FROM user').fetchone())
            db.close_db()
            remove(environ['DATABASE'])


class ViewsTests(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()

    def test_frontpage_must_be_acessible(self):
        response = self.test.get('/')
        self.assertEqual(response.status_code, 200)


class XLSXAPITests(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()
        self.data = {'email': 'user@provider.com'}
        with application.app_context():
            self.xlsx_data = {'file': open(BASE_DIR+'/sample.xlsx', 'rb')}
            db.init_db()
            conn = sqlite3.connect(environ.get('DATABASE'))
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.data['email'],))
            conn.commit()

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
        token = jwt.encode(self.data, environ.get('SEC_KEY', ''), algorithm='HS256')
        sample = list((openpyxl.load_workbook(BASE_DIR+'/sample.xlsx').active).values)
        sample.pop(0)
        response = self.test.post(
            '/api/excel/info/', headers={'Authorization': f'Bearer {token.decode("UTF-8")}'},
            content_type='multipart/form-data', data=self.xlsx_data,
        )
        self.assertTrue('Dulce' in sample[0])
        self.assertFalse('Dulce' in response.json['rows'][0])
        self.assertTrue('Angel' in response.json['rows'][0])
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.xlsx_data['file'].close()
        remove(environ['DATABASE'])


if __name__ == "__main__":
    unittest.main()
