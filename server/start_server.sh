#!/bin/sh
python3 -m gunicorn --workers=2 -b :5000 server.standalone:app
