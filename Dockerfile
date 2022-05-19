FROM python:3-slim

# Install Poetry
ENV POETRY_VERSION "1.1.13"
RUN pip install poetry==${POETRY_VERSION}
RUN poetry config virtualenvs.create false

WORKDIR /opt/server

# Install dependencies:
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY server/ ./

ENV FLAGS_DATABASE=/var/destructivefarm/flags.sqlite 
ENV FLASK_APP=/opt/server/standalone.py

VOLUME [ "/var/destructivefarm" ]
EXPOSE 5000

# Run the application:
ENTRYPOINT "cd ./server && ./server/start_server.sh"
