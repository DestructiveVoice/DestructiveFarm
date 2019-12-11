#!/bin/bash

# Use FLASK_DEBUG=True if needed

FLASK_APP=__init__.py python3 -m flask run --host 0.0.0.0 --with-threads
