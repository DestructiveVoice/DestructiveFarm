import threading

import werkzeug.serving
from flask import Flask


app = Flask(__name__)


import server.api
import server.submit_loop
import server.views


if not werkzeug.serving.is_running_from_reloader():
    threading.Thread(target=server.submit_loop.run_loop, daemon=True).start()
    # FIXME: Don't use daemon=True, exit from the thread properly


# if __name__ == '__main__':
#     app.run(threaded=True, debug=True)
