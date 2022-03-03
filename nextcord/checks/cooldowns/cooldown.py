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

import asyncio
import functools
import time
from asyncio.events import AbstractEventLoop, get_event_loop
from logging import getLogger
from typing import Callable, Optional, TypeVar

from . import CooldownBucket
from .buckets import _HashableArguments
from .protocols import BucketProtocol
from ...exceptions import CallableOnCooldown
from ...utils import MaybeCoro, maybe_coro

logger = getLogger(__name__)

T = TypeVar("T", bound=_HashableArguments)


def cooldown(
    limit: int,
    time_period: float,
    bucket: BucketProtocol,
    check: Optional[MaybeCoro] = lambda *args, **kwargs: True,
):
    """
    A thing

    Parameters
    ----------
    limit: int
        How many call's can be made in the time
        period specified by ``time_period``
    time_period: float
        The time period related to ``limit``
    bucket: BucketProtocol
        The :class:`Bucket` implementation to use
        as a bucket to separate cooldown buckets.
    check: Optional[MaybeCoro]
        A Callable which dictates whether or not
        to apply the cooldown on current invoke.

        If this Callable returns a truthy value,
        then the cooldown will be used for the current call.

        I.e. If you wished to bypass cooldowns, you
        would return False if you invoked the Callable.


    Raises
    ------
    RuntimeError
        Expected the decorated function to be a coroutine
    CallableOnCooldown
        This call resulted in a cooldown being put into effect
    InteractionBucketFailure
        You attempted to use an Interaction based bucket
        on a non-interaction based Callable.
    """
    _cooldown: Cooldown = Cooldown(limit, time_period, bucket)

    def decorator(func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            raise RuntimeError("Expected `func` to be a coroutine")

        attached_cooldowns = getattr(func, "_cooldowns", [])
        attached_cooldowns.append(_cooldown)
        setattr(func, "_cooldowns", attached_cooldowns)

        @functools.wraps(func)
        async def inner(*args, **kwargs):
            use_cooldown = await maybe_coro(check, *args, **kwargs)
            if not use_cooldown:
                return await maybe_coro(func, *args, **kwargs)

            async with _cooldown(*args, **kwargs):
                result = await func(*args, **kwargs)

            return result

        return inner

    return decorator


class CooldownTimesPer:
    # Essentially TimesPer but modified
    # to throw Exceptions instead of queue
    def __init__(
        self,
        limit: int,
        time_period: float,
        _cooldown: Cooldown,
    ) -> None:
        """

        Parameters
        ----------
        limit: int
        time_period: float
        _cooldown: Cooldown
            A backref to the parent cooldown manager.
        """
        self.limit: int = limit
        self.time_period: float = time_period
        self._cooldown: Cooldown = _cooldown
        self.current: int = limit
        self.loop: AbstractEventLoop = get_event_loop()
        self.pending_reset: bool = False

    async def __aenter__(self) -> "CooldownTimesPer":
        if self.current == 0:
            raise CallableOnCooldown(
                self._cooldown.func, self._cooldown, self.time_period
            )

        self.current -= 1

        if not self.pending_reset:
            self.pending_reset = True
            self.loop.call_later(self.time_period, self.reset)

        return self

    async def __aexit__(self, *_) -> None:
        ...

    def reset(self):
        # Reset the cooldown by 'adding'
        # one more 'possible' call.
        if self.current < 0:
            # Possible edge case?
            return None

        elif self.current == self.limit:
            # Don't ever give more windows
            # then the passed limit
            return None

        self.current += 1


class Cooldown:
    """Represents a cooldown for any given :type:`Callable`."""

    def __init__(
        self,
        limit: int,
        time_period: float,
        bucket: Optional[BucketProtocol] = None,
        func: Optional[Callable] = None,
    ) -> None:
        """
        Parameters
        ----------
        limit: int
            How many call's can be made in the time
            period specified by ``time_period``
        time_period: float
            The time period related to ``limit``
        bucket: Optional[BucketProtocol]
            The :class:`Bucket` implementation to use
            as a bucket to separate cooldown buckets.

            Defaults to :class:`CooldownBucket.all`
        func: Optional[Callable]
            The function this cooldown is attached to
        """
        bucket = bucket or CooldownBucket.all
        # See TimesPer for inspo, however it doesnt
        # use that due to the required changes and flexibility
        self.limit: int = limit
        self.time_period: float = time_period

        self._func: Optional[Callable] = func
        self._bucket: BucketProtocol = bucket
        self.loop: AbstractEventLoop = get_event_loop()
        self.pending_reset: bool = False
        self.last_reset_at: Optional[float] = None
        self._last_bucket: Optional[_HashableArguments] = None

        self._cache: dict[_HashableArguments, CooldownTimesPer] = {}

    async def __aenter__(self) -> "Cooldown":
        bucket: CooldownTimesPer = self._get_cooldown_for_bucket(self._last_bucket)
        async with bucket:
            return self

    async def __aexit__(self, *_) -> None:
        ...

    def __call__(self, *args, **kwargs):
        self._last_bucket = self.get_bucket(*args, **kwargs)
        return self

    def _get_cooldown_for_bucket(self, bucket: _HashableArguments) -> CooldownTimesPer:
        try:
            return self._cache[bucket]
        except KeyError:
            _bucket = CooldownTimesPer(self.limit, self.time_period, self)
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
        data = self._bucket.process(*args, **kwargs)
        if self._bucket is CooldownBucket.all:
            return _HashableArguments(*data[0], **data[1])

        elif self._bucket is CooldownBucket.args:
            return _HashableArguments(*data)

        elif self._bucket is CooldownBucket.kwargs:
            return _HashableArguments(**data)

        return _HashableArguments(data)

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
        self.last_reset_at = current_time + self.time_period

        _bucket = self._get_cooldown_for_bucket(bucket)
        _bucket.reset()

    def __repr__(self) -> str:
        return f"Cooldown(limit={self.limit}, time_period={self.time_period}, func={self._func})"

    @property
    def bucket(self) -> BucketProtocol:
        return self._bucket

    @property
    def func(self) -> Optional[Callable]:
        return self._func
