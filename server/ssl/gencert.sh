#!/bin/bash

openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout localhost.key -out localhost.crt