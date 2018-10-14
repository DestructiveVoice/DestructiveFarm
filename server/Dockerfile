FROM python:3-alpine

WORKDIR /app/server

COPY . .

RUN python3 -m pip install -r requirements.txt &&  apk add --no-cache dumb-init bash

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD ["./start_server.sh"]

EXPOSE 5000