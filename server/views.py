import time
from datetime import datetime

from flask import render_template, request

from server import app, database


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
def index():
    start_time = time.time()

    query = 'SELECT * FROM flags'
    conditions = []
    args = []

    for column in ['sploit', 'team', 'status']:
        if column in request.args:
            conditions.append(column + ' = ?')
            args.append(request.args[column])

    if 'last-minutes' in request.args:
        min_time = round(time.time() - int(request.args['last-minutes']) * 60)
        conditions.append('time >= ?')
        args.append(min_time)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    query += ' ORDER BY time DESC'

    query += ' LIMIT ?'
    limit = int(request.args.get('limit', 100))
    args.append(limit)

    flags = database.query(query, args)

    gen_time = time.time() - start_time
    return render_template('index.html', flags=flags,
                           limit=limit, has_conditions=bool(conditions),
                           gen_time=gen_time)
