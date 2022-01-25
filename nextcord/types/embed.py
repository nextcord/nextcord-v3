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

import typing
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    ...

logger = getLogger(__name__)


@dataclass(frozen=True)
class EmbedFile:
    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


@dataclass(frozen=True)
class EmbedThumbnail(EmbedFile):
    ...


@dataclass(frozen=True)
class EmbedVideo(EmbedFile):
    url: Optional[str] = None


@dataclass(frozen=True)
class EmbedImage(EmbedFile):
    ...


@dataclass(frozen=True)
class EmbedProvider:
    name: Optional[str] = None
    url: Optional[str] = None


@dataclass(frozen=True)
class EmbedAuthor:
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


@dataclass(frozen=True)
class EmbedFooter:
    text: str
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


class EmbedField:
    def __init__(self, name: str, value: str, *, inline: Optional[bool] = None):
        self.name = str(name)
        self.value = str(value)
        self.inline = bool(inline)


class Embed:
    _special = {"provider": EmbedProvider, "video": EmbedVideo}
    __slots__ = (
        "title",
        "description",
        "url",
        "timestamp",
        "color",
        "footer",
        "image",
        "thumbnail",
        "author",
        "fields",
        "_provider",
        "_video",
    )

    if TYPE_CHECKING:
        _video: EmbedVideo
        _provider: EmbedProvider

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
        self.author = author if isinstance(author, EmbedAuthor) else None
        self.fields = fields if isinstance(fields, list) else []

        self._provider = None
        self._video = None

    def add_field(
        self,
        name: str,
        value: str,
        *,
        inline: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> None:
        if position is not None:
            self.fields.insert(position, EmbedField(name, value, inline=inline))
        else:
            self.fields.append(EmbedField(name, value, inline=inline))

    def edit_field(
        self,
        index: int,
        name: Optional[str] = None,
        value: Optional[str] = None,
        *,
        inline: Optional[bool] = None,
    ) -> None:
        if name is not None:
            self.fields[index].name = name
        if value is not None:
            self.fields[index].value = value
        if inline is not None:
            self.fields[index].inline = inline

    def remove_field(self, *, index: int) -> None:
        try:
            del self.fields[index]
        except IndexError:
            pass

    @property
    def video(self) -> Optional[EmbedVideo]:
        return self._video

    @property
    def provider(self) -> Optional[EmbedProvider]:
        return self._provider

    @classmethod
    def from_dict(cls, data: dict):
        embed = cls()
        typehints = typing.get_type_hints(cls.__init__)
        for key, value in data.items():
            if key in typehints:
                constr = typing.get_args(typehints[key])[0]
            elif key in cls._special:
                constr = cls._special[key]
            else:
                continue  # Invalid key, not implemented

            if value is None:
                val = None
            elif isinstance(value, dict):
                val = constr(**value)
            else:
                val = constr(value)

            if key in cls._special:
                setattr(embed, "_" + key, val)
            elif key in embed.__slots__:
                setattr(embed, key, val)
            else:
                continue  # TODO: Unknown key, should it raise an error?

        return embed

    def to_dict(self) -> dict[str, Union[str, dict[str, str]]]:
        data = {}
        for key in self.__slots__:
            key = key.lstrip("_")
            if key in self._special:
                val = getattr(self, "_" + key)
            else:
                val = getattr(self, key)
            if is_dataclass(val):
                val = asdict(val)

            data[key] = val

        return data
