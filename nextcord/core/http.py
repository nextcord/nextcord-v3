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
from collections import defaultdict
from logging import getLogger
from time import time
from typing import TYPE_CHECKING, Type

from aiohttp import ClientSession

from .. import __version__
from ..exceptions import CloudflareBanException, DiscordException, HTTPException
from ..utils import json
from .protocols.http import BucketProtocol, HTTPClientProtocol, RouteProtocol

if TYPE_CHECKING:
    from typing import Any, Literal, Optional

    from aiohttp import ClientWebSocketResponse
    from aiohttp.client_reqrep import ClientResponse

    from ..client.state import State


logger = getLogger(__name__)


class Route(RouteProtocol):
    """
    Metadata about a Discord API route

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
        """
        The HTTP method for this route
        """
        self.unformatted_path = path
        """
        The unformatted path
        """
        self.path = path.format(**parameters)
        """
        The route to be requested from discord
        """

        self.use_webhook_global = use_webhook_global
        """
        If this route uses the webhook global LINK MISSING
        """

        self.guild_id: Optional[int] = parameters.get("guild_id")
        self.channel_id: Optional[int] = parameters.get("channel_id")
        self.webhook_id: Optional[int] = parameters.get("webhook_id")
        self.webhook_token: Optional[str] = parameters.get("webhook_token")

    @property
    def bucket(self) -> str:  # type: ignore
        """
        The ratelimit bucket this is under
        """
        return f"{self.method}:{self.unformatted_path}:{self.guild_id}:{self.channel_id}:{self.webhook_id}:{self.webhook_token}"


class Bucket(BucketProtocol):
    """
    A simple and fast ratelimiting implementation for HTTP

    .. warning::
        This is not multiprocess safe.
    .. note::
        This is a async context manager.
    """

    def __init__(self, route: Route):
        self._remaining: Optional[int] = None
        self.limit: Optional[int] = None
        """How many requests fit in a bucket"""
        self.reset_at: Optional[float] = None
        """When the Bucket fills up again. (UTC time)"""
        self._route: Route = route
        self._pending: list[Future[None]] = []
        self._reserved: int = 0
        self._loop = get_event_loop()

    @property  # type: ignore
    def remaining(self) -> Optional[int]:  # type: ignore
        """
        How many requests are remaining.
        """
        return self._remaining

    @remaining.setter
    def remaining(self, new_value: int) -> None:
        self._remaining = new_value
        if new_value == 0:
            self._pending_reset = True
            sleep_time = self.reset_at - time()
            self._loop.call_later(sleep_time, self._reset)

    def _reset(self) -> None:
        """
        Reset the bucket usage to the top and then start attempting to release the pending requests
        """
        self._remaining = self.limit

        for _ in range(self._calculated_remaining):
            try:
                future = self._pending.pop(0)
            except IndexError:
                break  # No more pendings, ignore
            future.set_result(None)

    @property
    def _calculated_remaining(self) -> int:
        # TODO: Replace this with the getter of remaining
        if self.remaining is None:
            return 1  # We have no data, let's just assume we have one request so we can fetch the info.
        return self.remaining - self._reserved

    async def __aenter__(self) -> "Bucket":
        """
        Reserve a spot in the bucket for the request.
        If all are taken, it will add it to a queue.
        """
        # TODO: This should return same type as itself. Not sure what's wrong when I try
        if self.remaining is None:
            self._reserved += 1
            return self  # We have no ratelimiting info, let's just try
        if self._calculated_remaining <= 0:
            # Ratelimit pending, let's wait
            future: Future[None] = Future()
            self._pending.append(future)
            logger.debug("Waiting for %s to clear up. %s pending", str(self), len(self._pending))
            await future
        self._reserved += 1
        return self

    async def __aexit__(self, *_: Any) -> None:
        """
        Request finished
        """
        self._reserved -= 1
        if self.remaining is not None:
            self.remaining -= 1


class HTTPClient(HTTPClientProtocol):
    """
    A http client to interact with the Discord REST API.

    Parameters
    ----------
    state: :class:`State`
        The current state of the bot
    max_retries: :class:`int`
        How many times we will attempt to retry after a unexpected failure (server error or ratelimit issue)

    """

    def __init__(
        self,
        state: State,
        *,
        max_retries: int = 5,
    ):
        self.version = 9
        self.api_base = f"https://discord.com/api/v{self.version}"

        self.state = state

        self.max_retries = max_retries
        self._global_lock = self.state.type_sheet.http_bucket(Route("POST", "/global"))
        self._webhook_global_lock = self.state.type_sheet.http_bucket(Route("POST", "/global/webhook"))
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
        """
        Send a request to discord.
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
                    bucket.reset_at = float(r.headers["X-RateLimit-Reset"])
                    bucket.limit = int(r.headers["X-RateLimit-Limit"])
                    bucket.remaining = int(r.headers["X-RateLimit-Remaining"])
                except KeyError:
                    # Ratelimiting info is not sent on some routes and on error
                    pass

                if (status := r.status) >= 300:
                    if status == 429:
                        if "via" not in r.headers.keys():
                            raise
                        logger.debug("Ratelimit exceeded")
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
