from flask import render_template

from server import app, database


@app.route('/')
def index():
    flags = database.query('SELECT * FROM flags ORDER BY time DESC')

    return render_template('index.html', flags=flags)
