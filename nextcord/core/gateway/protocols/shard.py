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

from nextcord.client.state import State
from nextcord.dispatcher import Dispatcher

if TYPE_CHECKING:
    from asyncio import Event
    from typing import Any


class ShardProtocol(Protocol):
    """
    A gateway `shard <https://discord.dev/topics/gateway#sharding>`_ spawned by :class:`GatewayProtocol`

    Parameters
    ----------
    state: :class:`State`
        The current bot state
    shard_id: :class:`int`
        The shard_id you provide to discord in the `identify <https://discord.dev/topics/gateway#identifying>`_ payload when connecting.
    """

    shard_id: int
    """The shards ID. This is provided by :class:`GatewayProtocol`."""
    ready: Event
    """A event set when the shard has identified or resumed"""

    opcode_dispatcher: Dispatcher
    """A dispatcher that will dispatched everything that the gateway sends us."""
    event_dispatcher: Dispatcher
    """A dispatcher that gets all events dispatched via the dispatch opcode from the gateway. This should only dispatch the data"""

    def __init__(self, state: State, shard_id: int) -> None:
        ...

    async def connect(self) -> None:
        """
        Connect to the gateway

        .. note::
            This is allowed to run forever
        """
        ...

    async def send(self, data: dict[str, Any]) -> None:
        """
        Send a raw message directly to the gateway. Generally this should not be used externally as gateway version might differ.

        Parameters
        ----------
        data: :class:`dict[str, Any]`
            The raw data to send
        """
        ...

    async def close(self) -> None:
        """
        Closes the connection to the gateway

        .. note::
            This should only be run once

        Parameters
        ----------
        code: :class:`int`
            Which code to send to discord when closing. A non 1000 code will allow you to resume later.
        """
        ...
