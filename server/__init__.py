import logging

from flask import Flask

app = Flask(__name__)

# Set default logging level to debug for every handler
app.logger.setLevel(logging.DEBUG)
for handler in app.logger.handlers:
    handler.setLevel(logging.DEBUG)

import prometheus_client
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Activate prometheus on /metrics
app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": prometheus_client.make_wsgi_app()}
)

import server.api

# Register /api endpoints
app.register_blueprint(server.api.bp)

import server.views

# Register / endpoints
app.register_blueprint(server.views.bp)
