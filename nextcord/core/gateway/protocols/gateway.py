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

from typing import TYPE_CHECKING, Protocol

from nextcord.core.ratelimiter import TimesPer

if TYPE_CHECKING:
    from typing import Any, Optional

    from ....client.state import State
    from ....dispatcher import Dispatcher
    from .shard import ShardProtocol


class GatewayProtocol(Protocol):
    """
    The connector the gateway and shard manager.
    You are responsible for scaling up/down shards and distributing requests (such as member chunking)

    .. note::
        Documentation can be found `here <https://discord.dev/topics/gateway>`_


    Parameters
    ----------
    state: :class:`State`
        The current state of the bot
    shard_count: :class:`Optional[int]`
        The current shard count. If this is not None it is expected for it to error instead of changing shard count
    """
    state: State
    shard_count: Optional[int]
    """The active shard count. None if not set yet."""

    event_dispatcher: Dispatcher
    """A dispatcher for events dispatched through the dispatch opcode. This will be dispatched by :class:`ShardProtocol`"""
    raw_dispatcher: Dispatcher
    """A dispatcher from raw shard data. This will be dispatched by :class:`ShardProtocol`"""

    def __init__(self, state: State, shard_count: Optional[int] = None) -> None:
        ...

    async def connect(self) -> None:
        """
        Connect to the gateway.
        """
        ...

    async def send(self, data: dict[str, Any], *, shard_id: int = 0) -> None:
        """
        Sends a raw message to the gateway. Generally this should not be used often as gateway version might differ.

        Parameters
        ----------
        data: :class:`dict[str, Any]`
            The raw data to send to discord
        shard_id: :class:`int`
            Which shard id to send on. This defaults to shard 0
        """
        ...

    def should_reconnect(self, shard: ShardProtocol) -> bool:
        """
        Called on :class:`ShardProtocol` disconnect to check if it should auto reconnect.
        This can be used for stopping shards reconnecting temporarily while you are rescaling or similar

        Parameters
        ----------
        shard: :class:`ShardProtocol`
            The shard asking if it should reconnect
        """
        ...

    async def close(self) -> None:
        """
        Close all connections and cleanup.
        This should only be called once
        """
        ...

    def get_identify_ratelimiter(self, shard_id: int) -> TimesPer:
        """
        Get the ratelimiter the shard should use while connecting

        Parameters
        ----------
        shard_id: :class:`int`
            The shard id of the connecting shard.

        """
        ...
