import threading
import werkzeug.serving


from server import app
import server.submit_loop


if not werkzeug.serving.is_running_from_reloader():
    threading.Thread(target=server.submit_loop.run_loop, daemon=True).start()
    # FIXME: Don't use daemon=True, exit from the thread properly
