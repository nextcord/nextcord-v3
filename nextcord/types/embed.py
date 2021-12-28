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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from datetime import datetime


logger = getLogger(__name__)


(EmbedFooter, EmbedImage, EmbedThumbnail, EmbedVideo, EmbedProvider, EmbedAuthor) = None


class EmbedField:
    def __init__(self, *, name: str, value: str, inline: bool = None):
        self.name = str(name)
        self.value = str(value)
        self.inline = bool(inline)


class Embed:
    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        color: Optional[int] = None,
        footer: Optional[EmbedFooter] = None,
        image: Optional[EmbedImage] = None,
        thumbnail: Optional[EmbedThumbnail] = None,
        video: Optional[EmbedVideo] = None,
        provider: Optional[EmbedProvider] = None,
        author: Optional[EmbedAuthor] = None,
        fields: Optional[list[EmbedField]] = [],
    ):
        self.title = str(title) if title is not None else None
        self.description = str(description) if description is not None else None
        self.url = str(url) if url is not None else None
        self.color = int(color) if color is not None else None
        self.timestamp = timestamp

        self.footer = footer if isinstance(footer, EmbedFooter) else None
        self.image = image if isinstance(image, EmbedImage) else None
        self.thumbnail = thumbnail if isinstance(thumbnail, EmbedThumbnail) else None
        self.video = video if isinstance(video, EmbedVideo) else None
        self.provider = provider if isinstance(provider, EmbedProvider) else None
        self.author = author if isinstance(author, EmbedAuthor) else None
        self.fields = fields if isinstance(fields, list) else None

    def add_field(
        self, name: str, value: str, *, inline: bool = None, position: int = None
    ) -> None:
        if position is not None:
            self.fields.insert(
                position, EmbedField(name=name, value=value, inline=inline)
            )
        else:
            self.fields.append(EmbedField(name=name, value=value, inline=inline))

    def edit_field(
        self, index: int, name: str, value: str, *, inline: bool = None
    ) -> None:
        if len(self.fields) < index:
            index = len(self.fields)

        self.fields[index] = EmbedField(name=name, value=value, inline=inline)

    def remove_field(self, *, index: int) -> None:
        try:
            del self.fields[index]
        except IndexError:
            pass
