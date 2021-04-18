FROM python:3

WORKDIR /server
ADD ./server/ ./

RUN pip3 install -r requirements.txt 

ENTRYPOINT [ "./start_server.sh" ]