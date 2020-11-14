"""
Module with SQLite helpers, see http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
"""

import os
import sqlite3
import threading

from flask import g

from server import app


schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

if "FLAGS_DATABASE" in os.environ:
    db_filename = os.environ["FLAGS_DATABASE"]
else:
    db_filename = os.path.join(os.path.dirname(__file__), 'flags.sqlite')


_init_started = False
_init_lock = threading.RLock()


def _init(database):
    app.logger.info('Creating database schema')
    with app.open_resource(schema_path, 'r') as f:
        database.executescript(f.read())


def get(context_bound=True):
    """
    If there is no opened connection to the SQLite database in the context
    of the current request or if context_bound=False, get() opens a new
    connection to the SQLite database. Reopening the connection on each request
    does not have a big overhead, but allows to avoid implementing a pool of
    thread-local connections (see https://stackoverflow.com/a/14520670).

    If the database did not exist, get() creates and initializes it.
    If get() is called from other threads at this time, they will wait
    for the end of the initialization.

    If context_bound=True, the connection will be closed after
    request handling (when the context will be destroyed).

    :returns: a connection to the initialized SQLite database
    """

    global _init_started

    if context_bound and 'database' in g:
        return g.database

    need_init = not os.path.exists(db_filename)
    database = sqlite3.connect(db_filename)
    database.row_factory = sqlite3.Row

    if need_init:
        with _init_lock:
            if not _init_started:
                _init_started = True
                _init(database)

    if context_bound:
        g.database = database
    return database


def query(sql, args=()):
    return get().execute(sql, args).fetchall()


@app.teardown_appcontext
def close(_):
    if 'database' in g:
        g.database.close()
