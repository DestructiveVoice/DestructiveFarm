from .submit_loop import flag_ann
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

    def get_history(status):
        now = time.time()
        round_time = reloader.get_config()['SUBMIT_PERIOD']

        db = database.get(context_bound=False)
        time_start = db.execute("SELECT MIN(time) as min FROM flags",
                                ()).fetchall()[0]["min"]
        ret = []
        while time_start < now:
            elem = {"timestamp": time_start, "sploits": {}}
            sploit_rows = db.execute("SELECT sploit, COUNT(*) as count FROM flags WHERE status = ? AND time BETWEEN ? AND ?",
                                     (status, time_start, time_start+round_time)).fetchall()

            for row in sploit_rows:
                sploit = row["sploit"]
                if sploit is None:
                    break
                count = row["count"]
                elem["sploits"][sploit] = count
            ret.append(elem)
            time_start += round_time
            break
        # app.logger.info(ret)
        return ret

    # FIXME
    status = "ACCEPTED"

    # FIXME: RETURN FLAG AFTER BEING SENT

    def stream():
        history = get_history(status)
        if history:
            yield f"data: {json.dumps(history)}\n\n"

        queue = flag_ann.listen()
        while True:
            flags = queue.get()
            resp = {"timestamp": round(time.time()), "sploits": {}}

            for flag in flags:
                if flag.sploit in resp["sploits"]:
                    continue
                # app.logger.info(flag.status)
                resp["sploits"][flag.sploit] = sum(
                    1 for x in flags if x.sploit == flag.sploit and x.status == status)
                #

            yield f"data: {json.dumps([resp])}\n\n"

    return Response(stream(), mimetype="text/event-stream")
