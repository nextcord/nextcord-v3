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
