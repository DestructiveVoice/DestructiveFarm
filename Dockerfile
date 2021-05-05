FROM python:3-slim

WORKDIR /server
COPY ./server/requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt 

COPY ./server ./

WORKDIR /
ENTRYPOINT [ "/server/start_server.sh" ]

