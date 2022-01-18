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

import zlib
from asyncio.locks import Event
from asyncio.tasks import sleep
from logging import getLogger
from random import random
from sys import platform
from typing import TYPE_CHECKING, Any

from aiohttp import WSMsgType

from ...dispatcher import Dispatcher
from ...exceptions import NextcordException
from ...utils import json
from ..ratelimiter import TimesPer
from .enums import CloseCodeEnum, OpcodeEnum
from .exceptions import (
    BadDataException,
    PartialDataException,
    PrivilegedIntentsRequiredException,
    ShardClosedException,
)
from .protocols.shard import ShardProtocol

if TYPE_CHECKING:
    from logging import Logger
    from typing import Optional

    from aiohttp import ClientWebSocketResponse

    from ...client.state import State

ZLIB_SUFFIX = b"\x00\x00\xff\xff"


class Shard(ShardProtocol):
    def __init__(
        self,
        state: State,
        shard_id: int,
    ) -> None:
        self.shard_id: int = shard_id

        # Events
        self.ready: Event = Event()

        # Internal things
        self._gateway_url = "wss://gateway.discord.gg?v=9&compress=zlib-stream"
        self._ws: Optional[ClientWebSocketResponse] = None
        self._state: State = state
        self._ratelimiter: TimesPer = TimesPer(120 - 3, 60)  # 3 margin for heartbeats
        self._zlib = zlib.decompressobj()
        self._buffer = bytearray()
        self._logger: Logger = getLogger(f"nextcord.shard.{self.shard_id}")

        # Discord info
        self._seq: Optional[int] = None
        self._session_id: Optional[str] = None

        # Heartbeating related
        self._has_acknowledged_heartbeat: bool = True

        # Dispatchers
        self.opcode_dispatcher: Dispatcher = Dispatcher()
        self.event_dispatcher: Dispatcher = Dispatcher()
        self.disconnect_dispatcher: Dispatcher = Dispatcher()

        # Register handles
        self.opcode_dispatcher.add_listener(self._handle_hello, OpcodeEnum.HELLO.value)
        self.opcode_dispatcher.add_listener(self._handle_heartbeat_ack, OpcodeEnum.HEARTBEAT_ACK.value)
        self.opcode_dispatcher.add_listener(self._handle_set_sequence)
        self.opcode_dispatcher.add_listener(self._handle_raw_dispatch)
        self.event_dispatcher.add_listener(self._handle_ready, "READY")
        self.event_dispatcher.add_listener(self._handle_dispatch)
        self.disconnect_dispatcher.add_listener(self._handle_disconnect)

    async def connect(self) -> None:
        self._ws = await self._state.http.ws_connect(self._gateway_url)
        self._zlib = zlib.decompressobj()
        self._state.loop.create_task(self._receive_loop())
        if self._session_id is None:
            async with self._state.gateway.get_identify_ratelimiter(self.shard_id):
                try:
                    await self.identify()
                except ShardClosedException:
                    self._logger.debug("Ignoring identify as shard closed")
                    return
            self._logger.info("Connected to the gateway")
            self.ready.set()
        else:
            await self.resume()
            self._logger.info("Reconnected to the gateway")

    async def _send(self, data: dict):
        if self._ws is None:
            raise NextcordException("Cannot send message to uninitialized WS")
        if self._ws.closed:
            raise NextcordException("Cannot send message to closed WS")
        self._logger.debug("> %s", data)
        payload = json.dumps(data)
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        try:
            await self._ws.send_bytes(payload)
        except ConnectionResetError:
            raise ShardClosedException()

    async def send(self, data: dict) -> None:
        async with self._ratelimiter:
            await self._send(data)

    async def _receive_loop(self) -> None:
        if self._ws is None:
            raise NextcordException("Receive loop got called before WS was created.")
        async for message in self._ws:
            if message.type == WSMsgType.BINARY:
                try:
                    raw_data = self._decompress(message.data)
                except PartialDataException:
                    continue
                except:
                    # Corruption/drop. Resetting is the only way as we are stateless
                    return await self.connect()
                data = json.loads(raw_data.decode("utf-8"))
                self._logger.debug("< %s", data)
                self.opcode_dispatcher.dispatch(data["op"], data)

                if data["op"] == OpcodeEnum.DISPATCH.value:
                    self.event_dispatcher.dispatch(data["t"], data["d"])
            else:
                self._logger.debug("Unknown message type %s", message.type)
        close_code = self._ws.close_code
        if close_code is None:
            return
        try:
            close_code_enum = CloseCodeEnum(close_code)
        except ValueError:
            self._logger.warning("Disconnect with unknown close code %s", close_code)
        else:
            self._logger.info("Disconnected with code %s (%s)", close_code, close_code_enum)
        self.disconnect_dispatcher.dispatch(close_code)

    async def _heartbeat_loop(self, heartbeat_interval: float) -> None:
        if self._ws is None:
            raise NextcordException("WS was None when HB loop started")
        while not self._ws.closed:
            if not self._has_acknowledged_heartbeat:
                await self._ws.close(code=1008)
                return
            self._has_acknowledged_heartbeat = False
            await self._send(
                {"op": OpcodeEnum.HEARTBEAT.value, "d": self._seq},
            )
            await sleep(heartbeat_interval)

    def _decompress(self, data) -> bytes:
        self._buffer.extend(data)

        if len(data) < 4 or data[-4:] != ZLIB_SUFFIX:
            # This might happen with big payloads like member chunking? Not sure if discord uses it or not...
            raise PartialDataException
        try:
            decompressed = self._zlib.decompress(self._buffer)
        except:
            # Most likely corrupted data. We are going to ignore it and pretend nothing happened..."
            self._buffer = bytearray()
            raise BadDataException
        self._buffer = bytearray()  # reset buffer
        return decompressed

    async def close(self, code=1000) -> None:
        if self._ws:
            await self._ws.close(code=code)
        self._buffer.clear()

    # Handles
    async def _handle_hello(self, data: dict) -> None:
        heartbeat_interval = data["d"]["heartbeat_interval"] / 1000

        intitial_wait_time = heartbeat_interval * random()
        await sleep(intitial_wait_time)
        self._state.loop.create_task(self._heartbeat_loop(heartbeat_interval))

    async def _handle_set_sequence(self, _: int, data: dict) -> None:
        if (seq := data["s"]) is not None:
            self._logger.debug("Updated sequence number to %s", seq)
            self._seq = seq

    async def _handle_heartbeat_ack(self, _: dict) -> None:
        self._has_acknowledged_heartbeat = True

    async def _handle_disconnect(self, close_code: Optional[int]) -> None:
        if close_code == None:
            # We closed somewhere else, let's let the other place worry about reconnecting
            return
        if not self._state.gateway.should_reconnect(self):
            # We shouldnt reconnect
            return
        # TODO: Handle too few shards error if it exists??
        if close_code == CloseCodeEnum.AUTHENTICATION_FAILED:
            # TODO: Error
            ...
        if close_code == CloseCodeEnum.DISALLOWED_INTENTS:
            # TODO: Error
            await self._state.client.close(PrivilegedIntentsRequiredException())
            return
        # Errors which should never happen
        if close_code in [
            CloseCodeEnum.SHARDING_REQUIRED,
            CloseCodeEnum.INVALID_SHARD,
            CloseCodeEnum.INVALID_API_VERSION,
        ]:
            # TODO: Error? These should never happen with the current sharding implementation although throwing a custom error might be a good idea?
            raise NextcordException(f"Unexpected discord close code: {CloseCodeEnum(close_code)}")

        # Errors which require a new session
        if close_code in [
            CloseCodeEnum.INVALID_SEQ,
            CloseCodeEnum.SESSION_TIMED_OUT,
        ]:
            # Cannot connect back with same session, reconnect (w/new session)
            self._session_id = None
            self._seq = None

        # Reconnect and hope it works
        await self.connect()

    async def _handle_ready(self, data: dict) -> None:
        self._session_id = data["session_id"]
        self._logger.debug("Session id set!")

    async def _handle_raw_dispatch(self, opcode: int, data: dict) -> None:
        self._state.gateway.raw_dispatcher.dispatch(opcode, self, data)

    async def _handle_dispatch(self, event_name: str, data: Any) -> None:
        self._state.gateway.event_dispatcher.dispatch(event_name, self, data)

    # Wrappers
    async def identify(self) -> None:
        await self.send(
            {
                "op": OpcodeEnum.IDENTIFY.value,
                "d": {
                    "token": self._state.token,
                    "intents": self._state.intents,
                    "properties": {
                        "$os": platform,
                        "$browser": "nextcord",
                        "$device": "nextcord",
                    },
                    "shard": (self.shard_id, self._state.gateway.shard_count),
                },
            }
        )

    async def resume(self) -> None:
        await self.send(
            {
                "op": OpcodeEnum.RESUME.value,
                "d": {
                    "token": self._state.token,
                    "session_id": self._session_id,
                    "seq": self._seq,
                },
            }
        )
