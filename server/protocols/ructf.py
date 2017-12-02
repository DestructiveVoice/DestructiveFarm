import socket

from server import app
from server.models import FlagStatus, SubmitResult


RESPONSES = {
    FlagStatus.QUEUED: ['timeout', 'game not started', 'try again later', 'game over'],
    FlagStatus.ACCEPTED: ['accepted', 'congrat'],
    FlagStatus.REJECTED: ['bad', 'wrong', 'expired', 'unknown', 'your own', 'no such flag',
                          'too old', 'not in database', 'already submitted', 'invalid flag'],
}


def submit_flags(flags, config):
    sock = socket.create_connection((config['SYSTEM_HOST'], config['SYSTEM_PORT']),
                                    config['SYSTEM_TIMEOUT'])

    greeting = sock.recv(4096)
    if b'Enter your flags' not in greeting:
        raise Exception('Checksystem does not greet us')

    unknown_responses = set()
    for item in flags:
        sock.sendall(item.flag.encode() + b'\n')
        response = sock.recv(4096).strip().lower().decode()

        for status, substrings in RESPONSES.items():
            if any(s in response for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED
            if response not in unknown_responses:
                unknown_responses.add(response)
                app.logger.warning('Unknown checksystem response (flag will be resent): %s', response)

        yield SubmitResult(item.flag, found_status, response)

    sock.close()
