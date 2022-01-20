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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

from asyncio.events import AbstractEventLoop, get_event_loop
from asyncio.futures import Future
from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from nextcord.exceptions import NextcordException

from .protocols.http import BucketProtocol

if TYPE_CHECKING:
    from typing import Any, Optional

    from .protocols.http import RouteProtocol

logger = getLogger(__name__)


class FloodGate:
    def __init__(self):
        self._pending: list[Future[bool]] = []
        self._remove_next: bool = False

    def flood(self):
        for future in self._pending:
            future.set_result(True)
        self._pending.clear()

    def top(self):
        try:
            self._pending.pop(0).set_result(False)
        except IndexError:
            self._remove_next = True

    async def acquire(self) -> bool:
        if self._remove_next:
            self._remove_next = False
            return False
        future = Future()
        self._pending.append(future)
        return await future


class Bucket(BucketProtocol):
    def __init__(self, route: RouteProtocol):
        self.limit: Optional[int] = None
        self.reset_at: Optional[float] = None
        self.route: RouteProtocol = route

        self._pending: list[Future[None]] = []
        self._pending_reset: bool = False
        self._remaining: Optional[int] = None
        self._reserved: int = 0
        self._loop: AbstractEventLoop = get_event_loop()
        self._first_fetch_ratelimit: FloodGate = FloodGate()

        # Let the first request through
        self._first_fetch_ratelimit.top()

    async def update(self, limit: int, remaining: int, reset_after: float) -> None:
        self.limit = limit
        self._remaining = remaining

        if not self._pending_reset:
            self._pending_reset = True
            self._loop.call_later(reset_after, self.reset)

    def reset(self) -> None:
        self._pending_reset = False
        if self.limit is None:
            raise NextcordException("Can't reset when info has not been fetched")
        self._remaining = self.limit

        drop_count = self._remaining - self._reserved
        logger.debug("Dropping %s pending requests", drop_count)
        self.drop_pending(drop_count)

    def drop_pending(self, limit: int) -> None:
        for _ in range(limit):
            try:
                future = self._pending.pop(0)
            except IndexError:
                return
            future.set_result(None)

    async def __aenter__(self) -> "Bucket":
        if self._remaining is not None:
            if self._remaining - self._reserved <= 0:
                logger.debug(
                    "Reserve: %s: Remaining: %s Reserved: %s CalcRemaining: %s",
                    self,
                    self._remaining,
                    self._reserved,
                    self._remaining - self._reserved,
                )
                future = Future()
                self._pending.append(future)
                await future
            else:
                logger.debug(
                    "Insta pass: %s: Remaining: %s Reserved: %s CalcRemaining: %s",
                    self,
                    self._remaining,
                    self._reserved,
                    self._remaining - self._reserved,
                )
        else:
            flood = await self._first_fetch_ratelimit.acquire()
            if flood:
                return await self.__aenter__()
            else:
                logger.debug("Letting ratelimit fetcher through")
        self._reserved += 1
        return self

    async def __aexit__(self, *_: Any) -> None:
        self._reserved -= 1
        if self._remaining is not None:
            self._remaining -= 1
        # Initial ratelimit fetch handling
        if self._remaining is None:
            # It failed, try again.
            self._first_fetch_ratelimit.top()
        else:
            self._first_fetch_ratelimit.flood()

    def __repr__(self) -> str:
        return repr(self.route)
