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

from typing import TYPE_CHECKING

from .protocols.shard import ShardProtocol

if TYPE_CHECKING:
    from typing import Any


class Shard(ShardProtocol):
    def __init__(
        self,
        *,
        gateway_url: str,
        shard_id: int,
        shard_count: int,
        error_callback: Any,
        message_callback: Any
    ) -> None:
        self.gateway_url: str = gateway_url
        self.shard_id: int = shard_id
        self.shard_count: int = shard_count
        self.error_callback: Any = error_callback
        self.message_callback: Any = message_callback

    async def connect(self):
        ...
