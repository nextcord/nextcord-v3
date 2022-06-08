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

from logging import getLogger
from typing import TYPE_CHECKING, Optional, Protocol

if TYPE_CHECKING:
    from ...client.state import State
    from ..snowflake import Snowflake


logger = getLogger(__name__)


class UserProtocol(Protocol):
    __slots__ = (
        "id",
        "username",
        "discriminator",
        "_avatar",
        "bot",
        "system",
        "_banner",
        "_accent_color",
        "_premium_type",
        "_public_flags",
        "_state",
    )

    if TYPE_CHECKING:
        id: Snowflake
        username: str
        discriminator: str
        _avatar: Optional[str]

        bot: bool
        system: bool
        _banner: Optional[str]
        _accent_color: Optional[int]
        _public_flags: int
        _state: State

    def __init__(self, *, state: State, data: dict):
        self._state = state
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data["id"]
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        self._avatar = data["avatar"]

        self.bot = data.get("bot")
        self.system = data.get("system")
        self._banner = data.get("banner")
        self._accent_color = data.get("accent_color")
        self._public_flags = data.get("public_flags")


class ClientUser(UserProtocol):
    __slots__ = ("mfa_enabled", "locale", "verified", "email", "flags", "bio")

    if TYPE_CHECKING:
        mfa_enabled: bool
        locale: str
        verified: bool
        flags: int
        bio: str

    def __init__(self, state: State, data: dict):
        super().__init__(state=state, data=data)

    def _update(self, data: dict):
        super()._update(data)
        self.mfa_enabled = data.get("mfa_enabled")
        self.locale = data.get("locale")
        self.verified = data.get("verified")
        self.flags = data.get("flags")
        self.bio = data.get("bio")

    async def edit(self, *, username: Optional[str] = None, avatar: Optional[bytes] = None) -> None:
        payload = {}
        if username is not None:
            payload["username"] = username

        if avatar is not None:
            payload["avatar"] = ...  # TODO: convert bytes to base64 image format

        await self._state.http  # TODO: HTTP not implemented yet

    async def get_guilds(
        self,
        *,
        before: Optional[Snowflake] = None,
        after: Optional[Snowflake] = None,
        limit: Optional[int] = None,
    ):
        ...

    async def _get_guild_member(self, *, guild_id: Snowflake):
        ...

    async def _leave_guild(self, *, guild_id: Snowflake):
        ...

    async def _create_dm(self, *, recipient_id: Snowflake):
        ...
