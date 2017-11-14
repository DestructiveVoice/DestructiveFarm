from flask import Flask


app = Flask(__name__)


import server.api
import server.views


# if __name__ == '__main__':
#     app.run(threaded=True, debug=True)
