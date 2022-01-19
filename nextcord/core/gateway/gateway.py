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

from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

from ...dispatcher import Dispatcher
from ..ratelimiter import TimesPer
from .exceptions import NotEnoughShardsException
from .protocols.gateway import GatewayProtocol

if TYPE_CHECKING:
    from typing import Any, Optional

    from ...client.state import State
    from ...exceptions import NextcordException
    from .protocols.shard import ShardProtocol

logger = getLogger(__name__)


class Gateway(GatewayProtocol):
    """A fast and simple :class:`GatewayProtocol` implementation

    Parameters
    ----------
    state: :class:`State`
        The current state of the bot
    shard_count: :class:`Optional[int]`
        The current shard count. If this is not None it is expected for it to error instead of changing shard count

    """

    def __init__(self, state: State, shard_count: Optional[int] = None) -> None:
        self.state: State = state

        # Ratelimiting
        self._identify_ratelimits: defaultdict[int, TimesPer] = defaultdict(lambda: TimesPer(1, 5))
        self._max_concurrency: Optional[int] = None

        # Shard count
        self.shard_count: Optional[int] = shard_count
        """The current shard count"""
        self._shard_count_locked: bool = self.shard_count is not None

        # Shard sets
        self.shards: list[ShardProtocol] = []
        """The currently active shards"""
        # When we get disconnected for too low shard count, we start creating a second set of inactive shards.
        self._pending_shard_set: list[Any] = []
        self._recreating_shards: bool = False

        # Dispatchers
        self.event_dispatcher: Dispatcher = Dispatcher()
        self.raw_dispatcher: Dispatcher = Dispatcher()

    async def connect(self) -> None:
        """Connect to the gateway"""
        r = await self.state.http.get_gateway_bot()
        gateway_info = await r.json()

        if self.shard_count is None:
            self.shard_count = gateway_info["shards"]

        session_start_limit = gateway_info["session_start_limit"]
        self._max_concurrency = session_start_limit["max_concurrency"]

        for shard_id in range(self.shard_count):
            shard = self.state.type_sheet.shard(
                self.state,
                shard_id,
            )
            self.state.loop.create_task(shard.connect())
            self.shards.append(shard)

    def get_identify_ratelimiter(self, shard_id: int) -> TimesPer:
        """Get the ratelimiter the shard should use while connecting

        Parameters
        ----------
        shard_id: :class:`int`
            The shard id of the connecting shard.

        """

        if self._max_concurrency is None:
            raise NextcordException("Cannot get identify ratelimit before max_concurrency is filled")
        return self._identify_ratelimits[shard_id % self._max_concurrency]

    def should_reconnect(self, shard: ShardProtocol) -> bool:
        """Called on :class:`ShardProtocol` disconnect to check if it should auto reconnect.
        This is used for scaling up shards to stop the old ones from connecting and wasting identifies.

        Parameters
        ----------
        shard: :class:`ShardProtocol`
            The shard asking if it should reconnect
        """
        if not self._recreating_shards:
            return True
        if shard in self.shards:
            return False

        return True

    async def close(self) -> None:
        """Close all connections and cleanup.
        This should only be called once
        """
        for shard in self.shards + self._pending_shard_set:
            await shard.close()

    # Dispatcher handles
    async def handle_rescale(self) -> None:
        if self._recreating_shards:
            # Possibly error here as this should never be dispatched?
            return
        if self._shard_count_locked:
            await self.state.client.close(NotEnoughShardsException())
            return
        self._recreating_shards = True
        # TODO: Rescale.
