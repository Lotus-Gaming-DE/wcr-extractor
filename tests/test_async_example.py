import asyncio
import pytest


@pytest.mark.asyncio
async def test_async_example():
    await asyncio.sleep(0.01)
    assert True
