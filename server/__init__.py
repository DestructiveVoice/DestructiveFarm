import logging

from flask import Flask


app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)
for handler in app.logger.handlers:
    handler.setLevel(logging.DEBUG)


import server.api
import server.views
