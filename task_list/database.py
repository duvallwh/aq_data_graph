# database.py

import os
import psycopg2
from flask import g


def get_conn():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'conn' not in g:
        g.conn = psycopg2.connect(os.getenv('DATABASE_URL'))

    return g.conn


def close_db(e=None):
    """
    If this request connected to the database, close the connection.
    """
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()
    
    return None

def init_app(app):
    """
    register db functions with flask app. this is called by application factory
    """

    app.teardown_appcontext(close_db)