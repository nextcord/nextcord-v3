import asyncio

import pytest

from nextcord.cooldowns import Cooldown, CooldownBucket
from nextcord.exceptions import CallableOnCooldown


async def test_cooldown():
    cooldown = Cooldown(1, 5, test_cooldown, CooldownBucket.args)

    async with cooldown:
        with pytest.raises(CallableOnCooldown):
            async with cooldown:
                pass

        async with cooldown:
            pass


asyncio.run(test_cooldown())
