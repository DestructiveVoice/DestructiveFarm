from datetime import datetime

from flask import render_template

from server import app, database


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
def index():
    flags = database.query('SELECT * FROM flags ORDER BY time DESC')

    return render_template('index.html', flags=flags)
