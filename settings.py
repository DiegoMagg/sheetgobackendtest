from os import path

BASE_DIR = path.dirname(path.abspath(__file__))
ACCEPTED_FORMATS = ('png', 'jpeg')
CONVERTED_FILES_PATH = f'{BASE_DIR}/static/images/converted/'
DROPBOX_CONVERTED_FILES_PATH = f'{BASE_DIR}/static/images/dropbox/'
