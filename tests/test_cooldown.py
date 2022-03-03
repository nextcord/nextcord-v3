import asyncio
from enum import Enum

import pytest

from nextcord.checks.cooldowns import Cooldown, CooldownBucket, cooldown
from nextcord.checks.cooldowns.buckets import _HashableArguments
from nextcord.exceptions import CallableOnCooldown


@pytest.mark.asyncio
async def test_cooldown():
    cooldown = Cooldown(1, 0.25, CooldownBucket.args)

    async with cooldown:
        with pytest.raises(CallableOnCooldown):
            async with cooldown:
                pass

        await asyncio.sleep(0.3)  # Cooldown 'length'
        # This tests that cooldowns get reset
        async with cooldown:
            pass


def test_all_cooldown_bucket():
    bucket: CooldownBucket = CooldownBucket.all

    data = bucket.process(1, 2, three=3, four=4)
    assert data == ((1, 2), {"three": 3, "four": 4})


def test_args_cooldown_bucket():
    bucket: CooldownBucket = CooldownBucket.args

    data = bucket.process(1, 2, three=3, four=4)
    assert data == (1, 2)


def test_kwargs_cooldown_bucket():
    bucket: CooldownBucket = CooldownBucket.kwargs

    data = bucket.process(1, 2, three=3, four=4)
    assert data == {"three": 3, "four": 4}


def test_get_bucket():
    cooldown = Cooldown(1, 1)
    hashed_args = cooldown.get_bucket(1, 2, three=3, four=4)
    assert hashed_args == _HashableArguments(1, 2, three=3, four=4)


@pytest.mark.asyncio
async def test_cooldown_decor_simple():
    # Can be called once every second
    # Default bucket is ALL arguments
    @cooldown(1, 1, bucket=CooldownBucket.all)
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    # Call it once, so its on cooldown after this
    data = await test_func(1, two=2)
    assert data == ((1,), {"two": 2})

    with pytest.raises(CallableOnCooldown):
        # Since this uses the same arguments
        # as the previous call, it comes under
        # the same bucket, and thus gets rate-limited
        await test_func(1, two=2)

    # Shouldn't error as it comes under the
    # bucket _HashableArguments(1) rather then
    # the bucket _HashableArguments(1, two=2)
    # which are completely different
    await test_func(1)


@pytest.mark.asyncio
async def test_cooldown_args():
    @cooldown(1, 1, bucket=CooldownBucket.args)
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    data = await test_func(1, two=2)
    assert data == ((1,), {"two": 2})

    with pytest.raises(CallableOnCooldown):
        await test_func(1)

    await test_func(2)


@pytest.mark.asyncio
async def test_cooldown_kwargs():
    @cooldown(1, 1, bucket=CooldownBucket.kwargs)
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    data = await test_func(1, two=2)
    assert data == ((1,), {"two": 2})

    with pytest.raises(CallableOnCooldown):
        await test_func(two=2)

    await test_func(two=3)


@pytest.mark.asyncio
async def test_custom_buckets():
    class CustomBucket(Enum):
        first_arg = 1

        def process(self, *args, **kwargs):
            if self is CustomBucket.first_arg:
                # This bucket is based ONLY off
                # of the first argument passed
                return args[0]

    @cooldown(1, 1, bucket=CustomBucket.first_arg)
    async def test_func(*args, **kwargs):
        pass

    await test_func(1, 2, 3)

    with pytest.raises(CallableOnCooldown):
        await test_func(1)

    await test_func(2)


@pytest.mark.asyncio
async def test_stacked_cooldowns():
    # Can call ONCE time_period second using the same args
    # Can call TWICE time_period second using the same kwargs
    @cooldown(1, 1, bucket=CooldownBucket.args)
    @cooldown(2, 1, bucket=CooldownBucket.kwargs)
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    await test_func(2, one=1)
    with pytest.raises(CallableOnCooldown):
        await test_func(2)

    # Args don't matter, its a kwargs based BucketProtocol
    await test_func(1, two=2)
    await test_func(two=2)
    with pytest.raises(CallableOnCooldown):
        await test_func(two=2)


def test_sync_cooldowns():
    with pytest.raises(RuntimeError):
        # Cant use sync functions
        @cooldown(1, 1, bucket=CooldownBucket.args)
        def test_func(*args, **kwargs) -> (tuple, dict):
            return args, kwargs


@pytest.mark.asyncio
async def test_checks():
    """Ensures the check works as expected"""
    # Only apply cooldowns if the first arg is 1
    @cooldown(
        1, 1, bucket=CooldownBucket.args, check=lambda *args, **kwargs: args[0] == 1
    )
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    await test_func(1, two=2)
    await test_func(2)
    await test_func(tuple())
    with pytest.raises(CallableOnCooldown):
        await test_func(1)


@pytest.mark.asyncio
async def test_async_checks():
    """Ensures the check works as expected with async methods"""
    # Only apply cooldowns if the first arg is 1
    async def mock_db_check(*args, **kwargs):
        # You can do database calls here or anything
        # since this is an async context
        return args[0] == 1

    @cooldown(1, 1, bucket=CooldownBucket.args, check=mock_db_check)
    async def test_func(*args, **kwargs) -> (tuple, dict):
        return args, kwargs

    await test_func(1, two=2)
    await test_func(2)
    await test_func(tuple())
    with pytest.raises(CallableOnCooldown):
        await test_func(1)
