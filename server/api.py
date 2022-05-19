import importlib
from .submit_loop import flag_ann
import time

from flask import request, jsonify, Response, render_template
import json

from server import app, auth, database, reloader, config
from server.models import FlagStatus
from server.spam import is_spam_flag


@app.route("/api/get_config")
@auth.api_auth_required
def get_config():

    # Reload the config from config.py
    config = reloader.get_config()

    module = importlib.import_module("server.protocols." + config["SYSTEM_PROTOCOL"])

    # Filter PASSWORD and TOKEN keys from the sent config
    client_config = {
        key: value
        for key, value in config.items()
        if "PASSWORD" not in key and "TOKEN" not in key
    }

    # Add attack info to the config
    try:
        server_info = module.get_attack_info(config)
        if server_info:
            client_config["ATTACK_INFO"] = server_info
    except Exception:
        pass

    # Refresh teams info
    try:
        teams = module.get_teams(config)
        if teams:
            client_config["TEAMS"] = teams
    except Exception:
        pass

    return jsonify(client_config)


@app.route("/api/post_flags", methods=["POST"])
@auth.api_auth_required
def post_flags():
    flags = request.get_json()
    flags = [item for item in flags if not is_spam_flag(item["flag"])]

    cur_time = round(time.time())
    rows = [
        (item["flag"], item["sploit"], item["team"], cur_time, FlagStatus.QUEUED.name)
        for item in flags
    ]

    db = database.get()
    db.executemany(
        "INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    db.commit()

    return Response(status=201)


@app.route("/api/successful_exploits")
@auth.api_auth_required
def successful_exploits():

    max_val = database.query("SELECT MAX(sent_cycle) as max FROM flags")[0]["max"]
    if max_val == None:
        return Response(status=204)  # TODO: Qualcosa di meglio?

    min_val = max(1, max_val - 4)
    stats_team = dict()
    for team, ip in config.CONFIG["TEAMS"].items():
        stats_team[team] = dict(ip=ip, round_info=dict())

    exploit_set = set()
    rounds = {}

    for round in range(min_val, max_val + 1):
        exp_round_stat = dict()
        results = database.query(
            "SELECT team, GROUP_CONCAT(DISTINCT sploit) AS exploits "
            "FROM flags WHERE sent_cycle= ? AND status='ACCEPTED' "
            "GROUP BY team ORDER BY team",
            (round,),
        )

        for result in results:
            team = result["team"]
            exploits = result["exploits"].split(",")

            for exploit in exploits:
                if exploit not in exp_round_stat:
                    exp_round_stat[exploit] = 0
                exp_round_stat[exploit] += 1

            exploit_set.update(exploits)
            stats_team[team]["round_info"][round] = exploits

        rounds[round] = exp_round_stat

        for team in config.CONFIG["TEAMS"]:
            if round not in stats_team[team]["round_info"]:
                stats_team[team]["round_info"][round] = []

    return render_template(
        "sploitTable.html",
        # return jsonify(
        rounds=rounds,
        sploits=list(exploit_set),
        stats=stats_team,
    )


@app.route("/api/graphstream")
@auth.api_auth_required
def get_flags():
    def get_history(status):
        db = database.get(context_bound=False)

        curr_cycle = db.execute(
            "SELECT MAX(sent_cycle) as cycle FROM flags"
        ).fetchone()["cycle"]
        if not curr_cycle:
            curr_cycle = 0

        ret = []

        for cycle in range(curr_cycle):
            elem = {"cycle": cycle, "sploits": {}}

            sploit_rows = db.execute(
                "SELECT sploit, COUNT(*) as n "
                "FROM flags "
                "WHERE status = ? AND sent_cycle = ? "
                "GROUP BY sploit",
                (status, cycle),
            ).fetchall()

            for sploit in sploit_rows:
                sploit_name = sploit["sploit"]
                if sploit_name is None:
                    continue

                n = sploit["n"]
                elem["sploits"][sploit_name] = n
            ret.append(elem)

            if len(ret) % 10 == 0:
                yield ret
                ret = []

        yield ret

    status = FlagStatus.ACCEPTED

    def stream():
        for h in get_history("ACCEPTED"):
            yield f"data: {json.dumps(h)}\n\n"

        queue = flag_ann.listen()
        while True:
            cycle, flags = queue.get()
            resp = {"cycle": cycle, "sploits": {}}

            for flag in flags:
                if flag.sploit in resp["sploits"]:
                    continue
                # app.logger.info(flag.status)
                resp["sploits"][flag.sploit] = sum(
                    1 for x in flags if x.sploit == flag.sploit and x.status == status
                )

            yield f"data: {json.dumps([resp])}\n\n"

    return Response(
        stream(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


"""
[
  {
      cycle: 123123,
      sploits: {
          "nome_sploit": n,
          ...
      }
  }
]
"""
