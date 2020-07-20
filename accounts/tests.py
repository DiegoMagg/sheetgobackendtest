import unittest
from .user_manager import init_create_user_command
from settings import BASE_DIR
from os import environ, path, remove
from app import application
from db import db


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


class UserCreationCommandTestCase(unittest.TestCase):

    def setUp(self):
        self.runner = application.test_cli_runner()

    def test_raise_error_if_email_arg_is_missing(self):
        self.assertTrue(
            'Missing required argument email' in self.runner.invoke(init_create_user_command).output
        )

    def test_raise_error_if_email_is_invalid(self):
        self.assertTrue(
            'Invalid email address.' in
            self.runner.invoke(init_create_user_command, 'invalidemail.com').output,
        )

    def test_user_with_valid_email_must_be_created(self):
        with application.app_context():
            db.init_db()
            output = self.runner.invoke(init_create_user_command, 'valid@email.com').output
            self.assertTrue('User created succesfully' in output)
            remove(path.join(BASE_DIR, environ.get('DATABASE')))

    def test_raise_alert_if_email_is_already_registered(self):
        with application.app_context():
            db.init_db()
            self.runner.invoke(init_create_user_command, 'valid@email.com')
            output = self.runner.invoke(init_create_user_command, 'valid@email.com').output
            self.assertTrue('A user with this email already exists' in output)
            remove(path.join(BASE_DIR, environ.get('DATABASE')))
