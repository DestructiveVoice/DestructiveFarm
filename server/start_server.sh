#!/bin/bash

# Use FLASK_DEBUG=True if needed

if [[ "$AUTH_PASS" == "" ]]; then
    sed -i "/@auth.auth_required/d" views.py
fi

FLASK_APP=__init__.py flask run --host 0.0.0.0 --with-threads
