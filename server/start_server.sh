#!/bin/bash

# Use FLASK_DEBUG=True if needed

FLASK_APP=__init__.py flask run --host 0.0.0.0 --with-threads
