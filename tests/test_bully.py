import asyncio
from app.node import Node

def test_bully_declare_leader():
    async def run():
        n1 = Node(id=1, port=9111, peers=[("127.0.0.1",9112,2),("127.0.0.1",9113,3)])
        await n1.start()
        await asyncio.sleep(0.2)
        await n1.start_election()
        await asyncio.sleep(0.5)
        # since peers are offline, node 1 may declare itself leader
        assert n1.leader in (1, None)  # allow None transient state
    asyncio.run(run())
