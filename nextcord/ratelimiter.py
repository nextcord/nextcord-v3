from __future__ import annotations

import time
from asyncio import Future
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


class TimesPer:
    def __init__(self, limit: int, per: int) -> None:
        self.limit: int = limit
        self.per: int = per
        self.reset_at: Optional[float] = None
        self.current: int = self.limit

        self._reserved: list[Future] = []

    async def __aenter__(self) -> "TimesPer":
        current_time = time.time()
        if self.reset_at is None:
            self.reset_at = 0
        if self.reset_at < current_time:
            self.reset_at = current_time + self.per
            self.current = self.limit

            for _ in range(self.limit):
                try:
                    self._reserved.pop().set_result(None)
                except IndexError:
                    break

        if self.current == 0:
            self._reserved.append(future := Future())
            await future

        return self

    async def __aexit__(self, *_) -> None:
        ...
