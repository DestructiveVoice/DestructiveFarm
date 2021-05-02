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

from .submit_loop import flag_ann

@app.route('/api/graphstream')
@auth.api_auth_required
def get_flags():
    # FIXME
    status = "QUEUED"

    # FIXME: RETURN FLAG AFTER BEING SENT

    def stream():
        queue = flag_ann.listen()
        while True:
            flags = queue.get()
            resp = {}

            for flag in flags:
                if flag.sploit in resp:
                    continue
                # app.logger.info(flag.status)
                resp[flag.sploit] = sum(1 for x in flags if x.sploit == flag.sploit and x.status == status)

            yield f"data: {json.dumps(resp)}\n\n"
        

    return Response(stream(), mimetype="text/event-stream")
