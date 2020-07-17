import sqlite3
from flask import current_app, g
import settings


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource(f'{settings.BASE_DIR}/db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init(application):
    application.teardown_appcontext(close_db)
