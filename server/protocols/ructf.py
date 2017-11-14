import socket

from .. import app
from ..models import FlagStatus, SubmitResult


RESPONSES = {
    FlagStatus.QUEUED: ['timeout', 'game not started', 'try again later', 'game over'],
    FlagStatus.ACCEPTED: ['accepted', 'congrat'],
    FlagStatus.REJECTED: ['bad', 'wrong', 'expired', 'unknown', 'your own', 'no such flag',
                          'too old', 'not in database', 'already submitted'],
}


def submit_flags(flags, config):
    sock = socket.create_connection((config['SYSTEM_HOST'], config['SYSTEM_PORT']),
                                    config['SYSTEM_TIMEOUT'])

    greeting = sock.recv(4096)
    if b'Enter your flags' not in greeting:
        raise Exception('Checksystem does not greet us')

    for item in flags:
        sock.sendall(item.flag.encode() + b'\n')
        response = sock.recv(4096).strip().lower().decode()

        for status, substrings in RESPONSES.items():
            if any(s in response for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED
            app.logger.warning('Response is not recognized (flag will be resent): %s', response)

        yield SubmitResult(item.flag, found_status, response)

    sock.close()
