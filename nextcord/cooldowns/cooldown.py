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
from typing import TYPE_CHECKING, Callable, Optional

from nextcord.cooldowns import CooldownBucket
from nextcord.exceptions import CallableOnCooldown

logger = getLogger(__name__)


class Cooldown:
    """Represents a cooldown for any given :type:`Callable`."""

    def __init__(
        self,
        limit: int,
        per: float,
        bucket: CooldownBucket,
        func: Optional[Callable] = None,
    ) -> None:
        """
        Parameters
        ----------
        limit: int
            How many call's can be made in the time
            period specified by ``per``
        per: float
            The time period related to ``limit``
        bucket: CooldownBucket
            The :class:`CooldownBucket` instance to use
            as a bucket to separate cooldown buckets.
        func: Optional[Callable]
            The function this cooldown is attached to
        """
        # See TimesPer for inspo, however it doesnt
        # use that due to the required changes and flexibility
        self.limit: int = limit
        self.per: float = per
        self.current: int = self.limit
        self.func: Optional[Callable] = func

        self._bucket: CooldownBucket = bucket
        self._reserved: list[Future] = []
        self.loop: AbstractEventLoop = get_event_loop()
        self.pending_reset: bool = False
        self.last_reset_at: Optional[float] = None

    async def __aenter__(self) -> "Cooldown":
        if self.current == 0:
            raise CallableOnCooldown(self.func, self, self.per)

        self.current -= 1

        if not self.pending_reset:
            self.pending_reset = True
            self.loop.call_later(self.per, self.reset)

        return self

    async def __aexit__(self, *_) -> None:
        ...

    def reset(self) -> None:
        current_time = time.time()
        self.last_reset_at = current_time + self.per
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

    def __repr__(self) -> str:
        return f"Cooldown(limit={self.limit}, per={self.per}, func={self.func})"

    @property
    def bucket(self) -> CooldownBucket:
        return self._bucket
