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

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

logger = getLogger(__name__)


if TYPE_CHECKING:
    from typing import Any, Optional

    from .protocols.client import Client as BaseClient
    from .protocols.http import HTTPClient
    from .type_sheet import TypeSheet


class Client(BaseClient):
    def __init__(self, *, type_sheet: TypeSheet, intents: Any) -> None:
        self.type_sheet: TypeSheet = type_sheet
        self.http: Optional[HTTPClient] = None

    async def connect(self, token: str) -> None:
        self.http = self.type_sheet.http_client()
        ...

    def run(self, token: str) -> None:
        asyncio.run(self.connect(token))
