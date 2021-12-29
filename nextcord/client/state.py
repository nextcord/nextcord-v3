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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

from asyncio.events import AbstractEventLoop, get_event_loop
from typing import TYPE_CHECKING

from ..type_sheet import TypeSheet

if TYPE_CHECKING:
    from typing import Optional

    from .protocols.client import Client


class State:
    def __init__(
        self,
        client: Client,
        type_sheet: TypeSheet,
        token: str,
        intents: int,
        shard_count: Optional[int],
    ):
        self.client: Client = client
        self.type_sheet: TypeSheet = type_sheet
        self.loop: AbstractEventLoop = get_event_loop()

        self.token: str = token
        self.intents: int = intents
        self.shard_count: Optional[int] = shard_count

        # Instances
        self.http = self.type_sheet.http_client(self)
        self.gateway = self.type_sheet.gateway(self)
