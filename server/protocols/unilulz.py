import socket

from server import app
from server.models import FlagStatus, SubmitResult


RESPONSES = {
    FlagStatus.ACCEPTED: ['OK'],
    FlagStatus.REJECTED: ['NO'],
}

BUFSIZE = 4096
READ_TIMEOUT = 5


def recvall(sock):
    sock.settimeout(READ_TIMEOUT)
    chunks = [sock.recv(BUFSIZE)]

    sock.settimeout(APPEND_TIMEOUT)
    while True:
        try:
            chunk = sock.recv(BUFSIZE)
            if not chunk:
                break

            chunks.append(chunk)
        except socket.timeout:
            break

    sock.settimeout(READ_TIMEOUT)
    return b''.join(chunks)


def submit_flags(flags, config):
    sock = socket.create_connection((192.168.1.255,5671),
                                    READ_TIMEOUT)
    greeting = recvall(sock)
    unknown_responses = set()
    for item in flags:
        sock.sendall(item.flag.encode() + b'\n')
        response = recvall(sock).decode().strip()
        if response:
            response = response.splitlines()[0]
        response = response.replace('[{}] '.format(item.flag), '')

        response_lower = response.lower()
        for status, substrings in RESPONSES.items():
            if any(s in response_lower for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED

        yield SubmitResult(item.flag, found_status, response)

    sock.close()
