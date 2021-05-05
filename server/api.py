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

    return Response(status=201)


@app.route('/api/graphstream')
@auth.api_auth_required
def get_flags():
    def get_history(status):
        db = database.get(context_bound=False)

        curr_cycle = db.execute(
            "SELECT MAX(sent_cycle) as cycle FROM flags").fetchone()["cycle"]
        if not curr_cycle:
            curr_cycle = 0

        ret = []

        for cycle in range(curr_cycle):
            elem = {"cycle": cycle, "sploits": {}}

            sploit_rows = db.execute(
                "SELECT sploit, COUNT(*) as n "
                "FROM flags "
                "WHERE status = ? AND sent_cycle = ? "
                "GROUP BY sploit", (status, cycle)).fetchall()

            for sploit in sploit_rows:
                sploit_name = sploit["sploit"]
                if sploit_name is None:
                    continue

                n = sploit['n']
                elem['sploits'][sploit_name] = n
            ret.append(elem)

        return ret

    status = FlagStatus.ACCEPTED

    def stream():
        history = get_history("ACCEPTED")
        if history:
            yield f"data: {json.dumps(history)}\n\n"

        queue = flag_ann.listen()
        while True:
            cycle, flags = queue.get()
            resp = {"cycle": cycle, "sploits": {}}

            for flag in flags:
                if flag.sploit in resp["sploits"]:
                    continue
                # app.logger.info(flag.status)
                resp["sploits"][flag.sploit] = sum(
                    1 for x in flags
                    if x.sploit == flag.sploit and x.status == status)

            yield f"data: {json.dumps([resp])}\n\n"

    return Response(stream(),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache"})


'''
[
  {
      cycle: 123123,
      sploits: {
          "nome_sploit": n,
          ...
      }
  }
]
'''