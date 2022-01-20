from asyncio import Event, AbstractEventLoop, get_event_loop

from typing import Any


class GlobalLock:
    """A reverse :class:`asyncio.Event`"""

    def __init__(self) -> None:
        self._event: Event = Event()
        self._event.set()
        self._loop: AbstractEventLoop = get_event_loop()

    async def __aenter__(self) -> "GlobalLock":
        await self._event.wait()
        return self

    async def __aexit__(self, *_: Any) -> None:
        pass

    async def lock(self, unlock_after: int) -> None:
        """
        Lock anything which tries to wait for this until its unlocked

        Parameters
        ----------
        unlock_after: :class:`int`
            Time in seconds to unlock this after.
        """
        if not self._event.is_set():
            return
        self._event.clear()
        self._loop.call_later(unlock_after, self._event.set)
