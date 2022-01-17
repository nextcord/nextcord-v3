# The MIT License (MIT)
# Copyright (c) 2021-present vcokltfre & tag-epic
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


from __future__ import annotations

import time
from asyncio import Future
from asyncio.events import AbstractEventLoop, get_event_loop
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

logger = getLogger(__name__)


class TimesPer:
    def __init__(self, limit: int, per: float) -> None:
        self.limit: int = limit
        self.per: float = per
        self.current: int = self.limit

        self._reserved: list[Future[None]] = []
        self.loop: AbstractEventLoop = get_event_loop()
        self.pending_reset: bool = False

    async def __aenter__(self) -> "TimesPer":
        if self.current == 0:
            future: Future[None] = Future()
            self._reserved.append(future)
            await future
        self.current -= 1

        if not self.pending_reset:
            self.pending_reset = True
            self.loop.call_later(self.per, self.reset)

        return self

    async def __aexit__(self, *_: Any) -> None:
        ...

    def reset(self) -> None:
        logger.debug("Ratelimiter reset!")
        current_time = time.time()
        self.reset_at = current_time + self.per
        self.current = self.limit

        # Release pending
        for _ in range(self.limit):
            try:
                self._reserved.pop().set_result(None)
            except IndexError:
                break

        if len(self._reserved):
            self.pending_reset = True
            self.loop.call_later(self.per, self.reset)
        else:
            self.pending_reset = False
