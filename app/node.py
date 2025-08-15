import asyncio
import json
import time
import psutil
from typing import List, Tuple
from .utils import LamportClock, TokenManager
from .auth import parse_auth_from_headers, check_token
from .multicast import MulticastSender
from .grpc_service import serve_grpc
import os

HEARTBEAT_INTERVAL = 1.0
HEARTBEAT_TIMEOUT = 3.0

class Node:
    def __init__(self, id: int, host='0.0.0.0', port=9001, peers: List[Tuple[str,int,int]] = None, secret: str = "secret"):
        self.id = id
        self.host = host
        self.port = port
        self.peers = peers or []  # list of (host,port,id)
        self.clock = LamportClock()
        self.leader = None
        self.state = "running"
        self.last_hb = {}  # peer_id -> timestamp
        self.multicast = MulticastSender()
        self._start_time = time.time()
        # token manager: leader will sign tokens; nodes use it to validate incoming JWTs
        self.token_manager = TokenManager(secret)
        self.secret = secret
        # simple fallback token string for compatibility
        self.token = secret

    async def start(self):
        self._start_time = time.time()
        self.server = await asyncio.start_server(self._handle_conn, self.host, self.port)
        # start tasks
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._monitor_heartbeats())
        # start gRPC
        grpc_port = self.port + 1000
        self.grpc_server = await serve_grpc(self, grpc_port)
        asyncio.create_task(self.grpc_server.wait_for_termination())
        return self

    async def _handle_conn(self, reader, writer):
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                try:
                    msg = json.loads(data.decode())
                except Exception:
                    continue
                # accept token as plain or jwt
                token = msg.get("token")
                if not check_token(token, self):
                    continue
                # lamport
                await self.clock.recv(msg.get("lamport", 0))
                typ = msg.get("type")
                if typ == "HEARTBEAT":
                    pid = msg.get("id")
                    self.last_hb[pid] = time.time()
                elif typ == "ELECTION":
                    pid = msg.get("id")
                    # if we have higher id, reply OK and start our own election
                    if self.id > pid:
                        await self._send_to_peer(pid, {"type":"OK","id":self.id,"lamport": await self.clock.tick(),"token": self.token})
                        asyncio.create_task(self.start_election())
                elif typ == "OK":
                    # ignore detailed handling for simplicity
                    pass
                elif typ == "COORDINATOR":
                    self.leader = msg.get("id")
                elif typ == "SNAPSHOT_INIT":
                    # reply local state
                    snapshot = {"id": self.id, "state": self.state, "lamport": await self.clock.read(), "cpu": psutil.cpu_percent(None)}
                    await self._send_to_peer(msg.get("origin"), {"type":"SNAPSHOT_REPLY","data":snapshot,"lamport": await self.clock.tick(),"token": self.token})
                elif typ == "SNAPSHOT_REPLY":
                    # aggregate -> multicast
                    self.multicast.send({"snapshot": msg.get("data")})
        finally:
            writer.close()
            await writer.wait_closed()

    async def _send_to_peer(self, peer_id, obj):
        # find peer host/port by id
        for h,p,i in self.peers:
            if i == peer_id:
                try:
                    reader, writer = await asyncio.open_connection(h, p)
                    obj["lamport"] = await self.clock.tick()
                    writer.write((json.dumps(obj) + "\n").encode())
                    await writer.drain()
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
                return

    async def _heartbeat_loop(self):
        while True:
            for h,p,i in self.peers:
                msg = {"type":"HEARTBEAT","id":self.id,"lamport": await self.clock.tick(),"token": self.token}
                try:
                    reader, writer = await asyncio.open_connection(h, p)
                    writer.write((json.dumps(msg) + "\n").encode())
                    await writer.drain()
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    # failure; will be detected by monitor
                    pass
            # multicast status periodically
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            lam = await self.clock.read()
            self.multicast.send({"id": self.id, "leader": self.leader, "lamport": lam, "cpu": cpu, "memory": mem})
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def _monitor_heartbeats(self):
        while True:
            now = time.time()
            for h,p,i in self.peers:
                last = self.last_hb.get(i, 0)
                if now - last > HEARTBEAT_TIMEOUT:
                    # suspect failure -> start election
                    asyncio.create_task(self.start_election())
            await asyncio.sleep(1.0)

    async def start_election(self):
        higher = [peer for peer in self.peers if peer[2] > self.id]
        # send ELECTION to higher nodes
        for h,p,i in higher:
            try:
                reader, writer = await asyncio.open_connection(h, p)
                msg = {"type":"ELECTION","id":self.id,"lamport": await self.clock.tick(),"token": self.token}
                writer.write((json.dumps(msg) + "\n").encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        if not higher:
            # declare self leader
            self.leader = self.id
            # leader can issue tokens (JWT) for clients by calling token_manager.create_token(...)
            for h,p,i in self.peers:
                try:
                    reader, writer = await asyncio.open_connection(h, p)
                    msg = {"type":"COORDINATOR","id":self.id,"lamport": await self.clock.tick(),"token": self.token}
                    writer.write((json.dumps(msg) + "\n").encode())
                    await writer.drain()
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass

    async def initiate_snapshot(self):
        # leader initiates snapshot
        for h,p,i in self.peers:
            try:
                reader, writer = await asyncio.open_connection(h, p)
                msg = {"type":"SNAPSHOT_INIT","origin":self.id,"lamport": await self.clock.tick(),"token": self.token}
                writer.write((json.dumps(msg) + "\n").encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def issue_token(self, subject: str | int, expires_in: int = 3600) -> str:
        # only leader should issue; but method is available
        return self.token_manager.create_token(subject, expires_in)

    async def read_status(self):
        lam = await self.clock.read()
        return {"id": self.id, "leader": self.leader, "lamport": lam, "state": self.state, "uptime": int(time.time()-self._start_time)}
