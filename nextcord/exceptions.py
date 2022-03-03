from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from nextcord.checks.cooldowns import Cooldown
    from nextcord.checks.concurrency.protocols import ConcurrencyBucketProtocol


class NextcordException(Exception):
    ...


class DiscordException(Exception):
    ...


class HTTPException(DiscordException):
    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message

        super().__init__(f"({self.code}) {self.message}")


class RatelimitException(DiscordException):
    ...


class CloudflareBanException(RatelimitException):
    def __init__(self) -> None:
        super().__init__(
            "You have been banned by Cloudflare. "
            "See https://discord.dev/topics/rate-limits#invalid-request-limit-aka-cloudflare-bans"
        )


class InteractionBucketFailure(RatelimitException):
    """
    You attempted to apply an Interaction based cooldown
    to a Callable which does not take Interaction as the
    first parameter.
    """


class CallableOnCooldown(RatelimitException):
    """
    This :type:`Callable` is currently on cooldown.

    Attributes
    ==========
    func: Callable
        The :type:`Callable` which is currently rate-limited
    cooldown: Cooldown
        The :class:`Cooldown` which applies to the current cooldown
    retry_after: float
        How many seconds before you can retry the :type:`Callable`
    """

    def __init__(
        self,
        func: Callable,
        cooldown: Cooldown,
        retry_after: float,
    ) -> None:
        self.func: Callable = func
        self.cooldown: Cooldown = cooldown
        self.retry_after: float = retry_after


class MaxConcurrencyReached(RatelimitException):
    """
    This :type:`Callable` has reached its concurrency limits.

    Attributes
    ==========
    func: Callable
        The :type:`Callable` which is currently concurrency limited
    bucket: ConcurrencyBucketProtocol
        The :class:`Cooldown` which applies to the current cooldown
    call_count: int
        How many times this func can be called concurrently.
    """

    def __init__(
        self,
        func: Callable,
        bucket: ConcurrencyBucketProtocol,
        call_count: int,
    ) -> None:
        self.func: Callable = func
        self.bucket: ConcurrencyBucketProtocol = bucket
        self.call_count: int = call_count
