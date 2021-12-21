from asyncio.events import get_event_loop


class State:
    def __init__(self):
        self.loop = get_event_loop()
