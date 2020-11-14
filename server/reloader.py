import importlib
import os
import threading
import importlib.util

from server import app


_config_mtime = None
_reload_lock = threading.RLock()

if "CONFIG" in os.environ:
    config_path = os.environ["CONFIG"]
else:
    config_path = os.path.join(app.root_path, 'config.py')

config_spec = importlib.util.spec_from_file_location("server.config", config_path)
config_module = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_module)
_cur_config = config_module.CONFIG


def get_config():
    """
    Returns CONFIG dictionary from config.py module.

    If config.py file was updated since the last call, get_config() reloads
    the dictionary. If an error happens during reloading, get_config() returns
    the old dictionary.

    :returns: the newest valid version of the CONFIG dictionary
    """

    global _config_mtime, _cur_config

    cur_mtime = os.stat(config_path).st_mtime_ns
    if cur_mtime != _config_mtime:
        with _reload_lock:
            if cur_mtime != _config_mtime:
                try:
                    config_spec.loader.exec_module(config_module)
                    _cur_config = config_module.CONFIG
                    app.logger.info('New config loaded')
                except Exception as e:
                    app.logger.error('Failed to reload config: %s', e)

                _config_mtime = cur_mtime

    return _cur_config
