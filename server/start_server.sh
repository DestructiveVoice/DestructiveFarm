#!/bin/sh

# Use FLASK_DEBUG=True if needed

export FLASK_APP="standalone.py"
export FLASK_PORT="1234"
export FLASK_HOST="0.0.0.0"

poetry run python -m flask run \
--host $FLASK_HOST \
--port $FLASK_PORT \
--with-threads
