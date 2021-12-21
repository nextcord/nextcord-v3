# The MIT License (MIT)
#
# Copyright (c) 2021-present vcokltfre & tag-epic
#
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

from asyncio.futures import Future
from collections import defaultdict
from typing import TYPE_CHECKING

from ...client.state import State
from ..ratelimiter import TimesPer
from .protocols.gateway import GatewayProtocol
from .shard import Shard

if TYPE_CHECKING:
    from typing import Any, Optional

    from ...type_sheet import TypeSheet
    from ..protocols.http import HTTPClient


class Gateway(GatewayProtocol):
    def __init__(
        self,
        state: State,
        *,
        status: Any = None,
        presence: Any = None,
    ):
        self.state: State = state
        self._error_future: Future = Future()

        # Ratelimiting
        self._identify_ratelimits = defaultdict(lambda: TimesPer(1, 1))
        self.max_concurrency: Optional[int] = None

        # Shard count
        self.shard_count: Optional[int] = self.state.shard_count
        self._shard_count_locked = self.shard_count is not None

        # Shard sets
        self.shards: list[Any] = []
        # When we get disconnected for too low shard count, we start creating a second set of inactive shards.
        self._pending_shard_set: list[Any] = []
        self.recreating_shards: bool = False

    async def connect(self):
        # TODO: Connect

        r = await self.state.http.get_gateway_bot()
        gateway_info = await r.json()
        gateway_url = gateway_info["url"]

        if self.shard_count is None:
            self.shard_count = gateway_info["shards"]

        session_start_limit = gateway_info["session_start_limit"]
        self.max_concurrency = session_start_limit["max_concurrency"]

        for shard_id in range(self.shard_count):
            shard = Shard(
                self.state,
                gateway_url,
                shard_id,
            )
            await shard.connect()
            self.shards.append(shard)

        await self._error_future

    def get_identify_ratelimiter(self, shard_id):
        return self._identify_ratelimits[shard_id % self.max_concurrency]
