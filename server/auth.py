from functools import wraps
from flask import request, Response

from server import reloader


def unauthorized_response():
    return Response(
        response='Could not verify your access level for that URL. '
        'You have to login with proper credentials',
        status=401,
        headers={'WWW-Authenticate': 'Basic realm="Login Required"'})


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        config = reloader.get_config()
        if auth is None or auth.password != config['SERVER_PASSWORD']:
            return unauthorized_response()
        return f(*args, **kwargs)

    return decorated


def api_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        config = reloader.get_config()
        if config['ENABLE_API_AUTH']:
            if request.headers.get('X-Token', '') != config['API_TOKEN']:
                return Response('Provided token is invalid.', 403)
        return f(*args, **kwargs)

    return decorated
