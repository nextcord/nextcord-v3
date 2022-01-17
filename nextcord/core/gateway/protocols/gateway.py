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
    state: State
    shard_count: Optional[int]

    event_dispatcher: Dispatcher
    raw_dispatcher: Dispatcher

    def __init__(self, state: State, shard_count: Optional[int] = None):
        ...

    async def connect(self) -> None:
        ...

    async def send(self, data: dict[str, Any], *, shard_id: int = 0) -> None:
        ...

    def should_reconnect(self, shard: ShardProtocol) -> bool:
        ...

    async def close(self) -> None:
        ...

    def get_identify_ratelimiter(self, shard_id: int) -> TimesPer:
        ...

    def _shard_dispatch(self, event_name: str, shard: ShardProtocol, *args: Any) -> None:
        ...

    def _shard_raw_dispatch(self, opcode: int, shard: ShardProtocol, *args: Any) -> None:
        ...
