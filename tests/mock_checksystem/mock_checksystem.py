#!/usr/bin/env python3

import logging
import socket
import string
import threading


log_format = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=log_format, datefmt='%H:%M:%S', level=logging.DEBUG)


def handle_client(sock):
    sock.sendall(b'Hello\nEnter your flags\n')

    while True:
        flag = sock.recv(4096).strip().decode()
        if not flag:
            break

        if flag[-2] in string.digits:
            response = 'congrats brothers and sisters'
        elif flag[-2] != 'f':
            response = 'bad flag'
        else:
            response = 'come again?'
        sock.sendall(response.encode() + b'\n')

    sock.close()


def main():
    serv = socket.socket()
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind(('0.0.0.0', 31337))
    serv.listen(5)

    while True:
        sock, addr = serv.accept()
        logging.info('Got a client: {}'.format(addr))
        threading.Thread(target=handle_client, args=(sock,)).start()


if __name__ == '__main__':
    main()
