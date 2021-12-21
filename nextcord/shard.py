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
from asyncio.futures import Future
from asyncio.locks import Lock
from logging import getLogger
from typing import TYPE_CHECKING
from .ratelimiter import TimesPer

from .protocols.shard import ShardProtocol
from .utils import json

if TYPE_CHECKING:
    from typing import Any, Optional

    from aiohttp import ClientWebSocketResponse

    from .protocols.gateway import GatewayProtocol
    from .protocols.http import HTTPClient


class Shard(ShardProtocol):
    def __init__(
        self,
        *,
        gateway: GatewayProtocol,
        gateway_url: str,
        shard_id: int,
        shard_count: int,
        error_callback: Any,
        message_callback: Any,
        http: HTTPClient,
    ) -> None:
        self.gateway_url: str = gateway_url
        self.shard_id: int = shard_id
        self.shard_count: int = shard_count

        # Internal things
        self.gateway: GatewayProtocol = gateway
        self.error_callback: Any = error_callback
        self.message_callback: Any = message_callback
        self._ws: Optional[ClientWebSocketResponse] = None
        self._http: HTTPClient = http
        self._ratelimiter = TimesPer(120, 60)

        self.logger = getLogger(f"nextcord.shard.{self.shard_id}")

    async def connect(self):
        async with self.gateway.get_identify_ratelimiter(self.shard_id):
            self._ws = await self._http.ws_connect(self.gateway_url)
        self.logger.info("Connected to the gateway")

    async def send(self, data: dict):
        async with self._ratelimiter:
            self.logger.debug("> %s", data)
            await self._ws.send_str(json.dumps(data))
