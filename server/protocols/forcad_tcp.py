# Based on https://gist.github.com/xmikasax/90a0ce5736a4274e46b9958f836951e7

import socket

from server import app
from server.models import FlagStatus, SubmitResult


RESPONSES = {
    FlagStatus.QUEUED: ['timeout', 'game not started', 'try again later', 'game over', 'is not up',
                        'no such flag'],
    FlagStatus.ACCEPTED: ['accepted', 'congrat'],
    FlagStatus.REJECTED: ['bad', 'wrong', 'expired', 'unknown', 'your own',
                          'too old', 'not in database', 'already submitted', 'invalid flag',
                          'self', 'invalid', 'already_submitted', 'team_not_found', 'too_old', 'stolen'],
}

READ_TIMEOUT = 5
APPEND_TIMEOUT = 0.05
BUFSIZE = 4096


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
    sock = socket.create_connection((config['SYSTEM_HOST'], config['SYSTEM_PORT']),
                                    READ_TIMEOUT)

    greeting = recvall(sock)
    if b'Welcome' not in greeting:
        raise Exception('Checksystem does not greet us: {}'.format(greeting))

    sock.sendall(config['TEAM_TOKEN'].encode() + b'\n')
    invite = recvall(sock)
    if b'enter your flags' not in invite:
        raise Exception('Team token seems to be invalid: {}'.format(invite))

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
            if response not in unknown_responses:
                unknown_responses.add(response)
                app.logger.warning('Unknown checksystem response (flag will be resent): %s', response)

        yield SubmitResult(item.flag, found_status, response)

    sock.close()
