"""
Module with SQLite helpers, see http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
"""

import os
import sqlite3
import threading

from flask import g

from server import app


db_filename = os.path.join(os.path.dirname(__file__), 'flags.sqlite')


_init_started = False
_init_lock = threading.RLock()


def _init():
    app.logger.info('Creating database schema')
    with app.open_resource('schema.sql', 'r') as f:
        g.db.executescript(f.read())


def get():
    """
    get() opens a connection to the SQLite database if it wasn't opened
    in the current request already. Reopening the connection on each request
    does not have a big overhead but allows not to implement a pool of
    thread-local connections (see https://stackoverflow.com/a/14520670).

    If the database did not exist, get() creates and initializes it.
    If get() is called from other threads at the same time, they will wait
    for the end of the initialization.

    :returns: a connection to the initialized SQLite database
    """

    global _init_started

    if 'database' not in g:
        need_init = not os.path.exists(db_filename)
        g.db = sqlite3.connect(db_filename)
        g.db.row_factory = sqlite3.Row

        if need_init:
            with _init_lock:
                if not _init_started:
                    _init_started = True
                    _init()

    return g.db


def query(sql, args=()):
    return get().execute(sql, args).fetchall()


@app.teardown_appcontext
def close(_):
    if 'database' in g:
        g.database.close()
