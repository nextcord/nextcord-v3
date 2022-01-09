import asyncio

import pytest

from nextcord.cooldowns import Cooldown, CooldownBucket, cooldown
from nextcord.cooldowns.buckets import _HashableArguments
from nextcord.exceptions import CallableOnCooldown


@pytest.mark.asyncio
async def test_cooldown():
    cooldown = Cooldown(1, 1, CooldownBucket.args)

    async with cooldown:
        with pytest.raises(CallableOnCooldown):
            async with cooldown:
                pass

        await asyncio.sleep(1)  # Cooldown 'length'
        async with cooldown:
            pass


def test_all_cooldown_bucket():
    bucket: CooldownBucket = CooldownBucket.all

    data = bucket.process(1, 2, three=3, four=4)
    assert data == _HashableArguments(1, 2, three=3, four=4)


def test_args_cooldown_bucket():
    bucket: CooldownBucket = CooldownBucket.args

    data = bucket.process(1, 2, three=3, four=4)
    assert data == _HashableArguments(1, 2)


def test_kwargs_cooldown_bucket():
    bucket: CooldownBucket = CooldownBucket.kwargs

    data = bucket.process(1, 2, three=3, four=4)
    assert data == _HashableArguments(three=3, four=4)


@pytest.mark.asyncio
async def test_cooldown_decor():
    @cooldown(1, 1)
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    data = await test_func(1, two=2)
    assert data == ((1,), {"two": 2})

    with pytest.raises(CallableOnCooldown):
        await test_func(1, two=2)
