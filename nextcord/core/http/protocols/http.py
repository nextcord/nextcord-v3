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

if TYPE_CHECKING:
    from typing import Any, Literal, Optional, Type, TypeVar

    from aiohttp import ClientResponse, ClientWebSocketResponse

    from ....type_sheet import TypeSheet

    T = TypeVar("T")


class RouteProtocol(Protocol):
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

    method: str
    """The HTTP method"""
    path: str
    """The route to be requested from discord"""
    bucket: str
    """The ratelimit bucket this is under"""
    use_webhook_global: bool
    """If this route uses the webhook global LINK MISSING"""

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
    ) -> None:
        ...


class BucketProtocol(Protocol):
    """Ratelimiting for HTTP!

    You have to implement a async with context manager that waits when it runs out.
    Limit remaining and reset_at will be automatically set by HTTPClient.

    .. note::
        Ratelimiting should be implemented as `specified <https://discord.dev/topics/rate-limits>`_

    Parameters
    ----------
    route: :class:`RouteProtocol`
        The route this is for
    """

    def __init__(self, route: RouteProtocol) -> None:
        ...

    async def __aenter__(self: T) -> T:
        ...

    async def __aexit__(self, *_: Any) -> None:
        ...

    async def update(self, limit: int, remaining: int, reset_after: float) -> None:
        """
        Update the current state of the :class:`BucketProtocol` with information from the headers returned from :class:`HTTPClientProtocol`
        This information is fetched from the `ratelimit <http://discord.dev/topics/rate-limits>`_ headers

        Parameters
        -----------
        limit: :class:`int`
            How many requests this bucket type can hold
        remaining: :class:`int`
            How many requests left this bucket can hold

            .. note::
                This might not always be in order. This depends on how you implement :class:`BucketProtocol`
        reset_after: :class:`float`
            How many seconds until the bucket is resetting
        """
        ...


class HTTPClientProtocol(Protocol):
    """A http client to interact with the Discord REST API.
    This should handle ratelimits.

    state: :class:`State`
        A bot state
    token: :class:`Optional[str]`
        The bot token if present.
    """

    def __init__(self, state: State, token: Optional[str] = None) -> None:
        ...

    async def request(self, route: RouteProtocol, **kwargs: Any) -> ClientResponse:
        """Send a HTTP request to the discord API

        This should use TypeSheet.http_bucket to ratelimit.

        route: :class:`RouteProtocol`
            The metadata for this API route
        kwargs:
            Keyword only arguments passed to :attr:`ClientSession.request <aiohttp.ClientSession.trace_config>`
        """
        ...

    async def ws_connect(self, url: str) -> ClientWebSocketResponse:
        """Connect to a websocket!

        .. note::
            Aiohttp has a default timeout, we recommend disabling this as its already handled by :meth:`GatewayProtocol <nextcord.core.gateway.protocols.GatewayProtocol>`

        Parameters
        ----------
        url: :class:`str`
            The URL of the websocket to connect to
        """
        ...

    async def close(self) -> None:
        """Close the client.
        This should clean up all resources the HTTPClient has created.
        Should only be called once.
        """
        ...

    async def get_gateway_bot(self) -> ClientResponse:
        """Gets gateway url and connection information

        .. note::
            `Documentation <https://discord.dev/topics/gateway#get-gateway-bot>`_
        """
        ...
