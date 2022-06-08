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
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from .snowflake import Snowflake


Role, User = None, None  # TODO: DEFINE and import

logger = getLogger(__name__)


class AllowedMentions:
    def __init__(
        self,
        *,
        everyone: bool = False,
        roles: Union[bool, list[Role], Role] = False,
        users: Union[bool, User, list[User]] = True,
        replied_user: Optional[bool] = None,
    ):
        self.everyone = everyone
        self.roles = roles
        self.users = users
        self.replied_user = replied_user

    def to_dict(self) -> dict[str, Union[list[str], list[Snowflake], bool]]:
        allowed: dict[str, Union[list[str], list[Snowflake], bool]] = {"parse": []}
        if self.everyone:
            allowed["parse"].append("everyone")

        if isinstance(self.roles, bool) and self.roles:
            allowed["parse"].append("roles")
        elif isinstance(self.roles, list):
            allowed["roles"] = [r.id for r in self.roles]
        elif isinstance(self.roles, Role):
            allowed["roles"] = [self.roles.id]

        if isinstance(self.users, bool) and self.roles:
            allowed["parse"].append("users")
        elif isinstance(self.users, list):
            allowed["users"] = [u.id for u in self.roles]
        elif isinstance(self.users, User):
            allowed["users"] = [self.users.id]

        if self.replied_user:
            allowed["replied_user"] = bool(self.replied_user)

        return allowed

    @classmethod
    def none(cls) -> AllowedMentions:
        return cls(everyone=False, roles=False, users=False, replied_user=False)

    @classmethod
    def all(cls) -> AllowedMentions:
        return cls(everyone=True, roles=True, users=True, replied_user=True)
