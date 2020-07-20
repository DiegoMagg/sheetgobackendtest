import sys
from os import environ
from jwt import encode
from accounts.user_manager import validate_email


def create_token(email):
    if not validate_email(email):
        sys.exit('Blank or invalid email')
    token = encode({'email': email}, environ.get('SEC_KEY'), algorithm='HS256').decode('UTF-8')
    sys.stdout.write(token)


if __name__ == "__main__":
    create_token(sys.argv[-1])
