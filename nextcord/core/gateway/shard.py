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
from asyncio.locks import Event

from logging import getLogger
from nextcord.exceptions import NextcordException
from nextcord.dispatcher import Dispatcher
from typing import TYPE_CHECKING
import zlib
from sys import platform
from aiohttp import WSMsgType
from ...utils import json

from ...client.state import State
from ...utils import json
from ..ratelimiter import TimesPer
from .protocols.shard import ShardProtocol

if TYPE_CHECKING:
    from typing import Optional

    from aiohttp import ClientWebSocketResponse

ZLIB_SUFFIX = b'\x00\x00\xff\xff'

class Shard(ShardProtocol):
    def __init__(
        self,
        state: State,
        shard_id: int,
    ) -> None:
        self.state: State = state
        self.shard_id: int = shard_id
        self.gateway_url = "wss://gateway.discord.gg?v=9&compress=zlib-stream"

        self.ready: Event = Event()

        # Internal things
        self._ws: Optional[ClientWebSocketResponse] = None
        self._ratelimiter = TimesPer(120, 60)
        self._zlib = zlib.decompressobj()

        # Dispatchers
        self.opcode_dispatcher = Dispatcher()
        self.event_dispatcher = Dispatcher()

        self.logger = getLogger(f"nextcord.shard.{self.shard_id}")


    async def connect(self):
        self._ws = await self.state.http.ws_connect(self.gateway_url)
        self.state.loop.create_task(self._receive_loop())
        async with self.state.gateway.get_identify_ratelimiter(self.shard_id):
            await self.identify()
        self.logger.info("Connected to the gateway")
        self.ready.set()

    async def send(self, data: dict):
        async with self._ratelimiter:
            self.logger.debug("> %s", data)
            await self._ws.send_str(json.dumps(data))

    async def _receive_loop(self):
        if self._ws is None:
            raise NextcordException("Receive loop got called before WS was created.")
        async for message in self._ws:
            if message.type == WSMsgType.BINARY:
                raw_data = self._decompress(message.data)
                if raw_data is None:
                    # Incorrectly formatted
                    continue
                data = json.loads(raw_data.decode("utf-8"))
                self.logger.debug("< %s", data)
                self.opcode_dispatcher.dispatch(data["op"], data["d"])

                if data["op"] == 0:
                    self.event_dispatcher.dispatch(data["t"], data["d"])
            else:
                self.logger.debug("Unknown message type %s", message.type)

    def _decompress(self, data):
        buffer = bytearray()

        if len(data) < 4 or data[-4:] != ZLIB_SUFFIX:
            self.logger.info("Incorrectly formatted data?")
            return

        buffer.extend(data)
        return self._zlib.decompress(buffer)

        

    async def close(self):
        if self._ws is not None:
            await self._ws.close()
    
    # Wrappers
    async def identify(self):
        await self.send({
            "op": 2,
            "d": {
                "token": self.state.token,
                "intents": self.state.intents,
                "properties": {
                    "$os": platform,
                    "$browser": "nextcord",
                    "$device": "nextcord"
                }
            }
        })

