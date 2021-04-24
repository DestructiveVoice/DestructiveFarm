FROM python:3-slim

WORKDIR /server
COPY ./server/ ./

RUN pip3 install -r requirements.txt 

ENTRYPOINT [ "./start_server.sh" ]

