import time
from datetime import datetime

from flask import jsonify, render_template, request

from server import app, database, reloader


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
def index():
    distinct_values = {}
    for column in ['sploit', 'status', 'team']:
        rows = database.query('SELECT DISTINCT {} FROM flags ORDER BY {}'.format(column, column))
        distinct_values[column] = [item[column] for item in rows]

    config = reloader.get_config()

    server_tz_name = time.strftime('%Z')
    if server_tz_name.startswith('+'):
        server_tz_name = 'UTC' + server_tz_name

    return render_template('index.html',
                           flag_format=config['FLAG_FORMAT'],
                           distinct_values=distinct_values,
                           server_tz_name=server_tz_name)


FORM_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
FLAGS_PER_PAGE = 30


@app.route('/ui/show_flags', methods=['POST'])
def show_flags():
    conditions = []
    for column in ['sploit', 'status', 'team']:
        value = request.form[column]
        if value:
            conditions.append(('{} = ?'.format(column), value))
    for column in ['flag', 'checksystem-response']:
        value = request.form[column]
        if value:
            conditions.append(('INSTR(LOWER({}), ?)'.format(column), value))
    for param in ['time-since', 'time-until']:
        value = request.form['time-since'].strip()
        if value:
            timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT).timestamp())
            conditions.append(('time >= ?' if param == 'time-since' else 'time-until <= ?', timestamp))
    page_number = int(request.form['page-number'])
    if page_number < 1:
        raise ValueError('Invalid page-number')

    sql = 'SELECT * FROM flags'
    args = []
    if conditions:
        chunks, values = list(zip(conditions))
        sql += ' WHERE ' + ' AND '.join(chunks)
        args += values
    sql += ' ORDER BY time DESC LIMIT ? OFFSET ?'
    args += [FLAGS_PER_PAGE, FLAGS_PER_PAGE * (page_number - 1)]

    flags = database.query(sql, args)

    return jsonify([dict(item) for item in flags])
