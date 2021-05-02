import time

from flask import request, jsonify, Response
import json

from server import app, auth, database, reloader
from server.models import FlagStatus
from server.spam import is_spam_flag


@app.route('/api/get_config')
@auth.api_auth_required
def get_config():
    config = reloader.get_config()
    return jsonify({
        key: value
        for key, value in config.items()
        if 'PASSWORD' not in key and 'TOKEN' not in key
    })


@app.route('/api/post_flags', methods=['POST'])
@auth.api_auth_required
def post_flags():
    flags = request.get_json()
    flags = [item for item in flags if not is_spam_flag(item['flag'])]

    cur_time = round(time.time())
    rows = [(item['flag'], item['sploit'], item['team'], cur_time,
             FlagStatus.QUEUED.name) for item in flags]

    db = database.get()
    db.executemany(
        "INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
        "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()

    return ''


@app.route('/api/graphstream')
@auth.api_auth_required
def get_flags():
    # FIXME
    status = "SKIPPED"

    def update():
        with app.app_context():
            while True:
                rows = database.query(
                    "SELECT sploit, COUNT(*) as n FROM flags WHERE status = ? ORDER BY time DESC",
                    [status])
                resp = f"data: {json.dumps([dict(res) for res in rows])}\n\n"
                yield resp
                time.sleep(5)
        

    return Response(update(), mimetype="text/event-stream")
