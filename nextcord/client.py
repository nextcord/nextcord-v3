"""
The MIT License (MIT)
Copyright (c) 2021-present vcokltfre & tag-epic
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from .protocols.client import Client as BaseClient

if TYPE_CHECKING:
    from typing import Any, Optional

    from .protocols.http import HTTPClient
    from .type_sheet import TypeSheet


logger = getLogger(__name__)


class Client(BaseClient):
    def __init__(
        self,
        token: str,
        *,
        type_sheet: Optional[TypeSheet] = None,
        intents: Optional[Any] = None
    ) -> None:
        self.token: str = token
        self.type_sheet: TypeSheet = type_sheet or TypeSheet.default()
        self.http: Optional[HTTPClient] = self.type_sheet.http_client(
            self.type_sheet, self.token
        )
        self.gateway = self.type_sheet.gateway(self.type_sheet, self.http)
        self.loop = asyncio.get_event_loop()

    async def connect(self) -> None:
        await self.gateway.connect()

    def run(self) -> None:
        self.loop.run_until_complete(self.connect())
