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


from __future__ import annotations

import asyncio
import functools
import time
from asyncio import Future
from asyncio.events import AbstractEventLoop, get_event_loop
from logging import getLogger
from typing import TYPE_CHECKING, Callable, Optional, TypeVar

from nextcord.cooldowns import CooldownBucket
from nextcord.cooldowns.buckets import _HashableArguments
from nextcord.exceptions import CallableOnCooldown

logger = getLogger(__name__)

T = TypeVar("T", bound=_HashableArguments)


def cooldown(limit: int, per: float, bucket: Optional[CooldownBucket] = None):
    """
    A thing

    Parameters
    ----------
    limit: int
        How many call's can be made in the time
        period specified by ``per``
    per: float
        The time period related to ``limit``
    bucket: Optional[CooldownBucket]
        The :class:`CooldownBucket` instance to use
        as a bucket to separate cooldown buckets.

        Defaults to :class:`CooldownBucket.all`

    Raises
    ------
    RuntimeError
        Expected the decorated function to be a coroutine
    CallableOnCooldown
        This call resulted in a cooldown being put into effect
    """
    bucket = bucket or CooldownBucket.all
    _cooldown: Cooldown = Cooldown(limit, per, bucket)

    def decorator(func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            raise RuntimeError("Expected `func` to be a coroutine")

        attached_cooldowns = getattr(func, "_cooldowns", [])
        attached_cooldowns.append(_cooldown)
        setattr(func, "_cooldowns", attached_cooldowns)

        @functools.wraps(func)
        async def inner(*args, **kwargs):
            async with _cooldown(*args, **kwargs):
                result = await func(*args, **kwargs)

            return result

        return inner

    return decorator


class _CooldownTimesPer:
    # Essentially TimesPer but modified
    # to throw Exceptions instead of queue
    def __init__(
        self,
        limit: int,
        per: float,
        _cooldown: Cooldown,
    ) -> None:
        self.limit: int = limit
        self.per: float = per
        self._cooldown: Cooldown = _cooldown
        self.current: int = limit
        self.loop: AbstractEventLoop = get_event_loop()
        self.pending_reset: bool = False

    async def __aenter__(self) -> "_CooldownTimesPer":
        if self.current == 0:
            raise CallableOnCooldown(self._cooldown.func, self._cooldown, self.per)

        self.current -= 1

        if not self.pending_reset:
            self.pending_reset = True
            self.loop.call_later(self.per, self.reset)

        return self

    async def __aexit__(self, *_) -> None:
        ...

    def reset(self):
        self.current = self.limit


class Cooldown:
    """Represents a cooldown for any given :type:`Callable`."""

    def __init__(
        self,
        limit: int,
        per: float,
        bucket: CooldownBucket,
        func: Optional[Callable] = None,
    ) -> None:
        """
        Parameters
        ----------
        limit: int
            How many call's can be made in the time
            period specified by ``per``
        per: float
            The time period related to ``limit``
        bucket: CooldownBucket
            The :class:`CooldownBucket` instance to use
            as a bucket to separate cooldown buckets.
        func: Optional[Callable]
            The function this cooldown is attached to
        """
        # See TimesPer for inspo, however it doesnt
        # use that due to the required changes and flexibility
        self.limit: int = limit
        self.per: float = per

        self._func: Optional[Callable] = func
        self._bucket: CooldownBucket = bucket
        self.loop: AbstractEventLoop = get_event_loop()
        self.pending_reset: bool = False
        self.last_reset_at: Optional[float] = None
        self._last_bucket: Optional[_HashableArguments] = None

        self._cache: dict[_HashableArguments, _CooldownTimesPer] = {}

    async def __aenter__(self) -> "Cooldown":
        bucket: _CooldownTimesPer = self._get_cooldown_for_bucket(self._last_bucket)
        async with bucket:
            return self

    async def __aexit__(self, *_) -> None:
        ...

    def __call__(self, *args, **kwargs):
        self._last_bucket = self._bucket.process(*args, **kwargs)
        return self

    def _get_cooldown_for_bucket(self, bucket: _HashableArguments):
        try:
            return self._cache[bucket]
        except KeyError:
            _bucket = _CooldownTimesPer(self.limit, self.per, self)
            self._cache[bucket] = _bucket
            return _bucket

    def get_bucket(self, *args, **kwargs) -> _HashableArguments:
        """
        Return the given bucket for some given arguments.

        This uses the underlying :class:`CooldownBucket`
        and will return a :class:`_HashableArguments`
        instance which is inline with how Cooldown's function.

        Parameters
        ----------
        args: Any
            The arguments to get a bucket for
        kwargs: Any
            The keyword arguments to get a bucket for

        Returns
        -------
        _HashableArguments
            An internally correct representation
            of a bucket for the given arguments.

            This can then be used in :meth:`Cooldown.reset` calls.
        """
        return self._bucket.process(*args, **kwargs)

    def reset(self, bucket: Optional[_HashableArguments] = None) -> None:
        """
        Reset the given bucket, or the entire cooldown.

        Parameters
        ----------
        bucket: Optional[_HashableArguments]
            The bucket we wish to reset

        Notes
        -----
        You can get :class:`_HashableArguments` by
        using the :meth:`Cooldown.get_bucket` method.
        """
        if not bucket:
            # Reset all buckets
            for bucket in self._cache.keys():
                self.reset(bucket)

        current_time = time.time()
        self.last_reset_at = current_time + self.per

        _bucket = self._get_cooldown_for_bucket(bucket)
        _bucket.reset()

    def __repr__(self) -> str:
        return f"Cooldown(limit={self.limit}, per={self.per}, func={self._func})"

    @property
    def bucket(self) -> CooldownBucket:
        return self._bucket

    @property
    def func(self):
        return self._func
