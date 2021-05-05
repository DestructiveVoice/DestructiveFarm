import re
import time
from datetime import datetime

from flask import jsonify, render_template, request, Response

from server import app, auth, database, reloader
from server.models import FlagStatus


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
@auth.auth_required
def index():
    distinct_values = {}
    for column in ['sploit', 'status']:
        rows = database.query(f'SELECT DISTINCT {column} FROM flags ORDER BY {column}')
        distinct_values[column] = [item[column] for item in rows]

    config = reloader.get_config()

    server_tz_name = time.strftime('%Z')
    if server_tz_name.startswith('+'):
        server_tz_name = 'UTC' + server_tz_name

    return render_template('index.html',
                           flag_format=config['FLAG_FORMAT'],
                           distinct_values=distinct_values,
                           server_tz_name=server_tz_name,
                           teams=config['TEAMS'])


FORM_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
FLAGS_PER_PAGE = 30


@app.route('/ui/show_flags')
@auth.auth_required
def show_flags():
    conditions = []

    for column in ['sploit', 'status']:
        value = request.args[column]
        if value:
            conditions.append((f'{column} = ?', value))

    for column in ['flag', 'checksystem_response']:
        value = request.args[column]
        if value:
            conditions.append((f'INSTR(LOWER({column}), ?)', value.lower()))

    for param in ['time-since', 'time-until']:
        value = request.args[param].strip()
        if value:
            timestamp = round(
                datetime.strptime(value, FORM_DATETIME_FORMAT).timestamp())
            sign = '>=' if param == 'time-since' else '<='
            conditions.append((f'time {sign} ?', timestamp))

    page_number = int(request.args['page-number'])
    if page_number < 1:
        raise ValueError('Invalid page-number')

    if conditions:
        chunks, values = list(zip(*conditions))
        conditions_sql = 'WHERE ' + ' AND '.join(chunks)
        conditions_args = list(values)
    else:
        conditions_sql = ''
        conditions_args = []

    teams = [
        f"'{team}'" for team in request.args.getlist('team') if team != ""
    ]
    teams_sql = ""
    if len(teams) != 0:
        if conditions_sql != '':
            teams_sql += "AND "
        else:
            teams_sql += "WHERE "
        teams_sql += f"team IN ({','.join(teams)})"

    sql = f'SELECT * FROM flags {conditions_sql} {teams_sql} ORDER BY time DESC LIMIT ? OFFSET ?'

    args = conditions_args + [
        FLAGS_PER_PAGE, FLAGS_PER_PAGE * (page_number - 1)
    ]

    flags = database.query(sql, args)

    sql = f'SELECT COUNT(*) FROM flags {conditions_sql} {teams_sql}'
    args = conditions_args
    total_count = database.query(sql, args)[0][0]

    return jsonify({
        'rows': [dict(item) for item in flags],
        'rows_per_page': FLAGS_PER_PAGE,
        'total_count': total_count,
    })


@app.route('/ui/post_flags_manual', methods=['POST'])
@auth.auth_required
def post_flags_manual():
    config = reloader.get_config()
    flags = re.findall(config['FLAG_FORMAT'], request.form['text'], re.M)

    cur_time = round(time.time())
    rows = [(item, 'Manual', '*', cur_time, FlagStatus.QUEUED.name)
            for item in flags]

    db = database.get()
    db.executemany(
        "INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
        "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()

    return Response(status=201)
