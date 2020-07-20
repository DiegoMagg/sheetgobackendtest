import sqlite3
from os import environ
import click
from re import match
from flask.cli import with_appcontext
from settings import BASE_DIR


def create_user(email):
    mail_re = r'^(\D)+(\w)*((\.(\w)+)?)+@(\D)+(\w)*((\.(\D)+(\w)*)+)?(\.)[a-z]{2,}$'
    if not match(mail_re, email):
        click.echo('Invalid email address.')
    else:
        try:
            conn = sqlite3.connect(f'{BASE_DIR}/{environ.get("DATABASE")}')
            conn.execute('INSERT INTO user (email) VALUES (?)', (email,))
            conn.commit()
            conn.close()
            click.echo('User created succesfully.')
        except sqlite3.IntegrityError:
            click.echo('A user with this email already exists.')


@click.command('create-user')
@click.argument('email', nargs=-1)
@with_appcontext
def init_create_user_command(email=None):
    """Create new user"""
    if not email:
        click.echo('Missing required argument email')
    else:
        create_user(email[0])


def init(application):
    application.cli.add_command(init_create_user_command)
