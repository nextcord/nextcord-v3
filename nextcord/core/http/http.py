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

from asyncio import Future, get_event_loop
from asyncio.locks import Lock
from collections import defaultdict
from logging import getLogger
from time import time
from typing import TYPE_CHECKING, Type

from aiohttp import ClientSession

from ... import __version__
from ...exceptions import (
    CloudflareBanException,
    DiscordException,
    HTTPException,
    NextcordException,
)
from ...utils import json
from .global_lock import GlobalLock
from .protocols.http import BucketProtocol, HTTPClientProtocol, RouteProtocol

if TYPE_CHECKING:
    from typing import Any, Literal, Optional

    from aiohttp import ClientWebSocketResponse
    from aiohttp.client_reqrep import ClientResponse

    from ...client.state import State


logger = getLogger(__name__)


class Route(RouteProtocol):
    """Metadata about a Discord API route

    Parameters
    ----------
    method: :class:`str`
        The HTTP method for this route
    path: :class:`str`
        The API path
    use_webhook_global: :class:`bool`
        If this route uses the webhook global LINK MISSING
    parameters:
        Parameters to format path with. You can include guild_id, channel_id, webhook_id or webhook_token to specify ratelimit parameters.
    """

    def __init__(
        self,
        method: Literal[
            "GET",
            "HEAD",
            "POST",
            "PUT",
            "DELETE",
            "CONNECT",
            "OPTIONS",
            "TRACE",
            "PATCH",
        ],
        path: str,
        *,
        use_webhook_global: bool = False,
        **parameters: Any,
    ):
        self.method = method
        """The HTTP method for this route"""
        self.unformatted_path = path
        """The unformatted path"""
        self.path = path.format(**parameters)
        """The route to be requested from discord"""

        self.use_webhook_global = use_webhook_global
        """If this route uses the webhook global LINK MISSING"""

        self.guild_id: Optional[int] = parameters.get("guild_id")
        self.channel_id: Optional[int] = parameters.get("channel_id")
        self.webhook_id: Optional[int] = parameters.get("webhook_id")
        self.webhook_token: Optional[str] = parameters.get("webhook_token")

    @property
    def bucket(self) -> str:  # type: ignore
        """The ratelimit bucket this is under"""
        return f"{self.method}:{self.unformatted_path}:{self.guild_id}:{self.channel_id}:{self.webhook_id}:{self.webhook_token}"

    def __repr__(self) -> str:
        return self.bucket


class HTTPClient(HTTPClientProtocol):
    """A http client to interact with the Discord REST API.

    Parameters
    ----------
    state: :class:`State`
        The current state of the bot
    max_retries: :class:`int`
        How many times we will attempt to retry after a unexpected failure (server error or ratelimit issue)
    trust_local_time: :class:`bool`
        If we should trust local time for ratelimting. Turning this on is generally faster. If you have issues with it on keep your time in sync or turn this off.

    """

    def __init__(
        self,
        state: State,
        *,
        max_retries: int = 5,
        trust_local_time: bool = True
    ):
        self.version = 9
        self.api_base = f"https://discord.com/api/v{self.version}"
        self.max_retries = max_retries
        self.trust_local_time = trust_local_time

        self.state = state

        self._global_lock = GlobalLock()
        self._webhook_global_lock = GlobalLock()
        self._session = ClientSession(json_serialize=json.dumps)
        self._buckets: dict[str, BucketProtocol] = {}
        self._http_errors: defaultdict[int, Type[HTTPException]] = defaultdict((lambda: HTTPException), {})


        self._headers = {"User-Agent": "DiscordBot (https://github.com/nextcord/nextcord, {})".format(__version__)}
        if self.state.token:
            self._headers["Authorization"] = f"Bot {self.state.token}"

    async def request(
        self,
        route: RouteProtocol,
        *,
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> ClientResponse:
        """Send a request to discord.
        This automatically handles ratelimits.

        .. versionadded:: 3.0

        Parameters
        ----------
        route: :class:`RouteProtocol`
            Metadata about the route you are executing
        headers: :class:`Optional[dict[str, str]]`
            Request headers. This will add a bot token if availible
        kwargs:
            Keyword only arguments passed to `ClientSession.request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.trace_config>`_
        """
        global_lock = self._webhook_global_lock if route.use_webhook_global else self._global_lock

        if headers is None:
            headers = {}
        headers |= self._headers

        # TODO: This is a mess, please split it up

        for _ in range(self.max_retries):
            async with global_lock:
                bucket_str = route.bucket
                bucket = self._buckets.get(bucket_str)

                if bucket is None:
                    bucket = self.state.type_sheet.http_bucket(route)
                    self._buckets[bucket_str] = bucket

                async with bucket:
                    r = await self._session.request(
                        route.method,
                        self.api_base + route.path,
                        headers=headers,
                        **kwargs,
                    )
                logger.debug("%s %s", route.method, route.path)

                try:
                    limit = int(r.headers["X-RateLimit-Limit"])
                    remaining = int(r.headers["X-RateLimit-Remaining"])
                    
                    # Some users might not trust the local time. If trust_local_time is off we just trust discord to give us the slightly delayed version of it.
                    if self.trust_local_time:
                        reset_after = float(r.headers["X-RateLimit-Reset"]) - time()
                    else:
                        reset_after = float(r.headers["X-RateLimit-Reset-After"])

                    await bucket.update(limit, remaining, reset_after)
                except KeyError:
                    # Ratelimiting info is not sent on some routes and on error
                    pass

                if (status := r.status) >= 300:
                    if status == 429:
                        if "via" not in r.headers.keys():
                            raise CloudflareBanException()
                        logger.warning("Ratelimit exceeded")
                        ratelimit_data = await r.json()
                        logger.debug(ratelimit_data)
                        if ratelimit_data["global"]:
                            logger.info("Global ratelimit reached!")
                            await global_lock.lock(ratelimit_data["reset_after"])
                        continue
                    error = await r.json()
                    raise self._http_errors[status](r.status, error["code"], error["message"])

                return r

        raise DiscordException(
            f"Ratelimiting failed {self.max_retries} times. This should only happen if you are running multiple bots with the same IP."
        )

    async def ws_connect(self, url: str) -> ClientWebSocketResponse:
        return await self._session.ws_connect(url, max_msg_size=0, autoclose=False, headers=self._headers)

    async def close(self) -> None:
        await self._session.close()

    # Wrappers around the http methods
    async def get_gateway_bot(self) -> ClientResponse:
        route = Route("GET", "/gateway/bot")
        return await self.request(route)
