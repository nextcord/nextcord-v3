from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from nextcord.checks.cooldowns import Cooldown


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
        cooldown: "Cooldown",
        retry_after: float,
    ) -> None:
        self.func: Callable = func
        self.cooldown: "Cooldown" = cooldown
        self.retry_after: float = retry_after
