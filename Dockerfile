FROM python:3-slim

WORKDIR /opt/server

# Install dependencies:
RUN python3 -m venv /opt/venv
COPY ./server/requirements.txt ./requirements.txt
RUN /opt/venv/bin/pip install -r requirements.txt

COPY ./server ./

ENV FLAGS_DATABASE=/var/server/flags.sqlite 
ENV FLASK_APP=/opt/server/standalone.py

VOLUME [ "/var/server" ]

# Run the application:
ENTRYPOINT ["/opt/venv/bin/python", "-m", "flask", "run", "--host", "0.0.0.0", "--with-threads" ]

