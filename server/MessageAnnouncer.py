from queue import Queue, Full
from server.models import Flag


class FlagAnnouncer:
    def __init__(self):
        self.listeners = []

    def listen(self) -> Queue[(int, list[Flag])]:
        q = Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg: (int, list[Flag])) -> None:
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except Full:
                del self.listeners[i]
