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
from typing import TYPE_CHECKING

from ...exceptions import InvalidArgument

if TYPE_CHECKING:
    from ..embed import Embed


logger = getLogger(__name__)

(
    AllowedMentions,
    MessageReference,
    MessageComponent,
    File,
    PartialAttachment,
    Sticker,
) = None  # TODO: DEFINE and import


class Messageable:
    async def send(
        self,
        content: str = None,
        *,
        tts: bool = None,
        embed: Embed = None,
        embeds: list[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        message_reference: MessageReference = None,
        components: list[MessageComponent] = None,
        stickers: list[Sticker] = None,
        file: File = None,
        files: list[File] = None,
        payload_json: str = None,
        attachments: list[PartialAttachment] = None,
    ):
        state = self._state

        if embed is not None and embeds is not None:
            raise InvalidArgument("You cannot pass both embed and embeds parameters")
        elif embed is not None:
            embeds = [embed]

        if embeds is not None:
            embeds = [emb.to_dict() for emb in embeds]

        if file is not None and files is not None:
            raise InvalidArgument("You cannot pass both file and files parameters")
        elif file is not None:
            files = [file]

        if stickers is not None:
            sticker_ids = [sticker.id for sticker in stickers]

        #
        #

        await state, sticker_ids  # ...
