from ..cooldowns.cooldown import CooldownTimesPer
from ...exceptions import MaxConcurrencyReached


class MaxConcurrencyPer(CooldownTimesPer):
    async def __aenter__(self) -> "CooldownTimesPer":
        if self.current == 0:
            raise MaxConcurrencyReached(self._cooldown.func, self._cooldown, self.time_period)

        self.current -= 1
        return self

    async def __aexit__(self, *_) -> None:
        # Reset the concurrency by 'adding'
        # one more 'possible' call.
        if self.current < 0:
            # Possible edge case?
            return None

        elif self.current == self.limit:
            # Don't ever give more windows
            # then the passed limit
            return None

        self.current += 1
