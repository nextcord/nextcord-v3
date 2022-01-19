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
from logging import getLogger
from typing import TYPE_CHECKING

from nextcord.exceptions import NextcordException

from ..type_sheet import TypeSheet
from .state import State

if TYPE_CHECKING:
    from typing import Optional

    from ..flags import Intents


logger = getLogger(__name__)


class Client:
    """A wrapper against the Bot connection on discord.

    Parameters
    ----------
    token: :class:`str`
        The bot token to connect with. This can be found at the `developer portal <https://discord.com/developers/>`_
    intents: :class:`Intents`
        The intents to connect with.
    type_sheet: :class:`TypeSheet`
        What components to use for the different internals
    shard_count: :class:`Optional[int]`
        How many shards to connect with. If it is None it will be automatically fetched and kept up to date from discord

        .. note::
            This will be locked in if you set it. If your bot ever outgrows your shardcount, you will get a error
    """

    def __init__(
        self,
        token: str,
        intents: Intents,
        *,
        type_sheet: Optional[TypeSheet] = None,
        shard_count: Optional[int] = None,
    ) -> None:
        if type_sheet is None:
            type_sheet = TypeSheet.default()
        self.state: State = State(self, type_sheet, token, intents.value, shard_count)
        self._error_future: Future[
            None
        ] = Future()  # TODO: Make this return a Optional error instead of setting a attribute
        self._error: Optional[NextcordException] = None

    async def connect(self) -> None:
        """Connect to discord.

        .. note::
            This will run until the bot shuts down.
        """
        await self.state.gateway.connect()

        await self._error_future
        if self._error:
            raise self._error from None

    def run(self) -> None:
        """Connect to discord

        .. note::
            This is the sync version of :meth:`Client.connect`. If you need to run multiple bots at the same time or similar, you should use that instead.

        .. note::
            This will run until the bot shuts down.
        """
        try:
            self.state.loop.run_until_complete(self.connect())
        except KeyboardInterrupt:
            self.state.loop.run_until_complete(self.close())

    async def close(self, error: Optional[NextcordException] = None) -> None:
        """Close the client."""
        await self.state.http.close()
        await self.state.gateway.close()
        self._error = error
        self._error_future.set_result(None)
