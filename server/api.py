import time
import threading

from flask import request, jsonify

from server import app, database, reloader
from server.models import FlagStatus


config_mtime = None
config_lock = threading.RLock()


@app.route('/api/get_config')
def get_config():
    return jsonify(reloader.get_config())


@app.route('/api/submit_flags', methods=['POST'])
def submit_flags():
    data = request.get_json()

    cur_time = round(time.time())
    rows = [(item, data['sploit'], data['team'], cur_time, FlagStatus.QUEUED.name)
            for item in data['flags']]

    db = database.get()
    db.executemany("INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
                   "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()

    return ''
