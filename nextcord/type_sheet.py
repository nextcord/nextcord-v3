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

from typing import TYPE_CHECKING

from attr import dataclass

if TYPE_CHECKING:
    from typing import Type
    from .protocols.http import Bucket, HTTPClient

from .http import Bucket as DefaultBucket
from .http import HTTPClient as DefaultHTTPClient


@dataclass
class TypeSheet:
    def __init__(
        self, *, http_client: Type[HTTPClient] = None, http_bucket: Type[Bucket] = None
    ):
        self.http_client: Type[HTTPClient] = http_client or DefaultHTTPClient
        self.http_bucket: Type[Bucket] = http_bucket or DefaultBucket
