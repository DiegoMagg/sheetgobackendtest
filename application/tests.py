import unittest
import sqlite3
from settings import BASE_DIR
from os import environ, path, remove, system
import jwt
import openpyxl
import subprocess
from db import db
from app import application


environ['DATABASE'] = 'test.sqlite'
application.config['TESTING'] = True
application.config['DEBUG'] = False
application.config.from_mapping(
    SECRET_KEY=environ.get('SEC_KEY', 'dev'),
    DATABASE=path.join(BASE_DIR, environ.get('DATABASE')),
)

DROPBOX_TEST_REQUIRED_PARAMS = all(
    [environ.get('DROPBOX_TOKEN'), environ.get('DROPBOX_PATH'), environ.get('DROPBOX_INVALID_FILE_PATH')],
)


class CommandsTestCase(unittest.TestCase):

    def setUp(self):
        self.runner = application.test_cli_runner()

    def test_init_db(self):
        self.assertTrue('Initialized the database' in self.runner.invoke(db.init_db_command).output)

    @unittest.skipIf(not environ.get('SEC_KEY'), 'Missing JWT secret')
    def test_jwt_generator_must_return_error_with_blank_or_invalid_email(self):
        output = subprocess.run(['python', 'generate_jwt.py'], capture_output=True).stderr.decode('UTF-8')
        self.assertTrue('Blank or invalid email' in output)
        output = subprocess.run(
            ['python', 'generate_jwt.py', 'invalid_input'], capture_output=True,
        ).stderr.decode('UTF-8')
        self.assertTrue('Blank or invalid email' in output)

    @unittest.skipIf(not environ.get('SEC_KEY'), 'Missing JWT secret')
    def test_generate_jwt_must_return_token_with_valid_email(self):
        output = subprocess.run(
            ['python', 'generate_jwt.py', 'valid@email.com'], capture_output=True,
        ).stdout.decode('UTF-8')
        decoded = jwt.decode(output.rstrip(), environ.get('SEC_KEY'), algorithms=['HS256'])
        self.assertEqual(decoded, {'email': 'valid@email.com'})


class SQLTestCase(unittest.TestCase):

    def setUp(self):
        self.email = 'user@provider.com'

    def test_user_must_be_created(self):
        with application.app_context():
            db.init_db()
            conn = sqlite3.connect(environ['DATABASE'])
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.email,))
            conn.commit()
            self.assertTrue(self.email in conn.execute('SELECT * FROM user').fetchone())
            db.close_db()
            remove(environ['DATABASE'])


class FrontPageTestCase(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()

    def test_frontpage_must_be_acessible(self):
        response = self.test.get('/')
        self.assertEqual(response.status_code, 200)


class XLSXAPITestCase(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()
        self.data = {'email': 'user@provider.com'}
        with application.app_context():
            self.xlsx_data = {'file': open('sample.xlsx', 'rb')}
            db.init_db()
            conn = sqlite3.connect(environ.get('DATABASE'))
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.data['email'],))
            conn.commit()

    def test_api_must_return_401_without_authentication_header(self):
        response = self.test.post('/api/excel/info/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'detail': 'Authentication credentials were not provided.'})

    def test_api_must_return_401_with_invalid_credentials(self):
        token = jwt.encode(self.data, 'TESTSECRET', algorithm='HS256')
        response = self.test.post(
            '/api/excel/info/', headers={'Authorization': f'Bearer {token.decode("UTF-8")}'},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'detail': 'Invalid credentials.'})

    def test_api_must_return_401_when_user_not_exists(self):
        token = jwt.encode({'email': 'otheruser@provider.com'}, environ.get('SEC_KEY', ''), algorithm='HS256')
        response = self.test.post(
            '/api/excel/info/', headers={'Authorization': f'Bearer {token.decode("UTF-8")}'},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'detail': 'Invalid credentials.'})

    def test_api_must_return_xmls_rows_alphabetically_ordered(self):
        token = jwt.encode(self.data, environ.get('SEC_KEY', ''), algorithm='HS256')
        sample = list((openpyxl.load_workbook('sample.xlsx').active).values)
        sample.pop(0)
        response = self.test.post(
            '/api/excel/info/', headers={'Authorization': f'Bearer {token.decode("UTF-8")}'},
            content_type='multipart/form-data', data=self.xlsx_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Dulce' in sample[0])
        self.assertFalse('Dulce' in response.json['rows'][0])
        self.assertTrue('Angel' in response.json['rows'][0])

    def tearDown(self):
        self.xlsx_data['file'].close()
        remove(environ['DATABASE'])


class ImageApiTestCase(unittest.TestCase):

    def setUp(self):
        self.test = application.test_client()
        self.data = {'email': 'user@provider.com'}
        self.token = jwt.encode(self.data, environ.get('SEC_KEY', ''), algorithm='HS256')
        self.params = {'format': 'png', 'file': open('sheetgo.bmp', 'rb')}
        with application.app_context():
            db.init_db()
            conn = sqlite3.connect(environ.get('DATABASE'))
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.data['email'],))
            conn.commit()

    def test_image_api_must_return_401_without_authentication_header(self):
        response = self.test.post('/api/image/convert/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'detail': 'Authentication credentials were not provided.'})

    def test_image_api_must_return_400_if_format_param_is_missing(self):
        self.params.pop('format')
        response = self.test.post(
            '/api/image/convert/', headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='multipart/form-data', data=self.params,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'detail': 'Unsupported format or format is missing.'})

    def test_image_must_be_converted_to_png(self):
        response = self.test.post(
            '/api/image/convert/', headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='multipart/form-data', data=self.params,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'image/png')
        response.close()

    def test_image_must_be_converted_to_jpeg(self):
        self.params['format'] = 'jpeg'
        response = self.test.post(
            '/api/image/convert/', headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='multipart/form-data', data=self.params,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'image/jpeg')
        response.close()

    def tearDown(self):
        self.params['file'].close()
        system(f'rm -rf {BASE_DIR + "/static/images/converted/*"}')


class DropboxImageConverterApiTestCase(unittest.TestCase):
    test = 'DROPBOX_TOKEN or DROPBOX_TOKEN environment variables not found'

    def setUp(self):
        self.test = application.test_client()
        self.data = {'email': 'user@provider.com'}
        self.token = jwt.encode(self.data, environ.get('SEC_KEY', ''), algorithm='HS256')
        self.json = {
            'format': 'png', 'dropbox_token': environ.get('DROPBOX_TOKEN'),
            'path': environ.get('DROPBOX_PATH'),
        }
        with application.app_context():
            db.init_db()
            conn = sqlite3.connect(environ.get('DATABASE'))
            conn.execute('INSERT INTO user (email) VALUES (?)', (self.data['email'],))
            conn.commit()

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Missing dropbox environment variables')
    def test_dropbox_api_must_return_401_with_invalid_credentials(self):
        self.token = jwt.encode(self.data, 'TESTSECRET', algorithm='HS256')
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'detail': 'Invalid credentials.'})

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Unsupported format or format is missing.')
    def test_dropbox_api_must_return_400_if_format_param_is_missing(self):
        self.json.pop('format')
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='application/json', json=self.json,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'detail': 'Unsupported format or format is missing.'})

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Missing dropbox environment variables')
    def test_dropbox_api_must_return_400_if_dropbox_token_is_missing(self):
        self.json.pop('dropbox_token')
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='application/json', json=self.json,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'detail': 'dropbox token is missing.'})

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Missing dropbox environment variables')
    def test_dropbox_api_must_return_400_if_file_path_is_missing(self):
        self.json.pop('path')
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='application/json', json=self.json,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'detail': 'dropbox file path is missing.'})

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Missing dropbox environment variables')
    def test_image_from_dropbox_must_be_converted_to_png(self):
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='application/json', json=self.json,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'image/png')
        response.close()

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Missing dropbox environment variables')
    def test_dropbox_api_must_return_400_if_file_does_not_exists(self):
        self.json['path'] = '/test/inexistant.file'
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='application/json', json=self.json,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Check dropbox token or file path.'})

    @unittest.skipIf(not DROPBOX_TEST_REQUIRED_PARAMS, 'Missing dropbox environment variables')
    def test_dropbox_api_must_return_400_if_file_is_invalid(self):
        self.json['path'] = environ.get('DROPBOX_INVALID_FILE_PATH')
        response = self.test.post(
            '/api/convert/fromdropbox/',
            headers={'Authorization': f'Bearer {self.token.decode("UTF-8")}'},
            content_type='application/json', json=self.json,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'detail': 'Invalid file.'})
