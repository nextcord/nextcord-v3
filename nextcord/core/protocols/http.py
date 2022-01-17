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

    from ...type_sheet import TypeSheet

    T = TypeVar("T")


class RouteProtocol(Protocol):
    method: str
    path: str
    bucket: str
    use_webhook_global: bool

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
        **parameters: dict[str, str],
    ):
        ...


class BucketProtocol(Protocol):
    limit: Optional[int]
    remaining: Optional[int]
    reset_at: Optional[float]

    def __init__(self, route: RouteProtocol) -> None:
        ...

    async def __aenter__(self: T) -> T:
        ...

    async def __aexit__(self, *_: Any) -> None:
        ...


class HTTPClientProtocol(Protocol):
    base_url: str

    def __init__(self, state: State, token: Optional[str] = None) -> None:
        ...

    async def request(self, route: RouteProtocol, **kwargs: Any) -> ClientResponse:
        ...

    async def ws_connect(self, url: str) -> ClientWebSocketResponse:
        ...

    async def close(self) -> None:
        ...

    async def get_gateway_bot(self) -> ClientResponse:
        ...
