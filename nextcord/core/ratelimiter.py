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
