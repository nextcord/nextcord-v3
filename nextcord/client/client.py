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

from logging import getLogger
from typing import TYPE_CHECKING

from .protocols.client import Client as BaseClient
from .state import State

if TYPE_CHECKING:
    from typing import Optional

    from ..type_sheet import TypeSheet


logger = getLogger(__name__)


class Client(BaseClient):
    def __init__(
        self,
        token: str,
        *,
        type_sheet: Optional[TypeSheet] = None,
        intents: Optional[int] = None,
        shard_count: Optional[int] = None,
    ) -> None:
        self.state: State = State(type_sheet, token, intents, shard_count)

    async def connect(self) -> None:
        await self.state.gateway.connect()

    def run(self) -> None:
        try:
            self.state.loop.run_until_complete(self.connect())
        except KeyboardInterrupt:
            self.state.loop.run_until_complete(self.close())

    async def close(self):
        await self.state.http.close()
        await self.state.gateway.close()
