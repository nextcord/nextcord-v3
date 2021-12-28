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
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from ...exceptions import NextcordException


class GatewayException(NextcordException):
    ...


class ShardClosedException(GatewayException):
    def __init__(self) -> None:
        super().__init__("You cannot send from a closed shard.")


class PrivilegedIntentsRequiredException(GatewayException):
    def __init__(self) -> None:
        super().__init__(
            "You cannot connect to the gateway with intents you are not authorized for. To fix this go to your developer dashboard and turn on the appropriate privileged intent switches. If you are verified, please contact support with your intent request."
        )

class NotEnoughShardsException(GatewayException):
    def __init__(self) -> None:
        super().__init__("Discord requires more shards than you specified in the client constructor. This can be solved by upping the shard count or leaving it None for automatic")
