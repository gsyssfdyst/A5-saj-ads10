import asyncio
from app.utils import LamportClock

def test_basic_tick():
    async def run():
        c = LamportClock()
        v1 = await c.tick()
        v2 = await c.tick()
        assert v2 == v1 + 1
        v3 = await c.recv(10)
        assert v3 >= 11
    asyncio.run(run())
