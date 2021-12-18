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

from typing import Any, Literal, Optional, Protocol

from nextcord.type_sheet import TypeSheet


class Route(Protocol):
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
        **parameters: dict[str, Any]
    ):
        self.method: str
        self.path: str
        self.bucket: str
        self.guild_id: Optional[int]
        self.channel_id: Optional[int]
        self.webhook_id: Optional[str]
        self.webhook_token: Optional[str]


class Bucket(Protocol):
    def __init__(self, route: Route):
        self.limit: Optional[int]
        self.remaining: Optional[int]
        self.reset_at: Optional[float]

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc, tb):
        ...


class HTTPClient(Protocol):
    def __init__(self, type_sheet: TypeSheet, token: Optional[str] = None):
        self.base_url: str
        self.version: int

    async def request(self, route: Route, **kwargs):
        ...
