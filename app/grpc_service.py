import asyncio
import psutil
import time
import grpc
from .proto import status_pb2, status_pb2_grpc
from .auth import parse_auth_from_headers, check_token

class GRPCStatusServicer(status_pb2_grpc.StatusServiceServicer):
    def __init__(self, node):
        self.node = node
        self.start = time.time()

    async def GetStatus(self, request, context):
        md = dict(context.invocation_metadata() or {})
        token = parse_auth_from_headers(md)
        if not check_token(token, self.node):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("invalid token")
            return status_pb2.GetStatusResponse()
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        lam = await self.node.clock.read()
        uptime = int(time.time() - self.start)
        resp = status_pb2.GetStatusResponse()
        resp.id = self.node.id
        resp.leader = str(self.node.leader) if self.node.leader is not None else ""
        resp.lamport = lam
        resp.state = self.node.state
        resp.cpu = float(cpu)
        resp.memory = float(mem)
        resp.uptime = uptime
        return resp

async def serve_grpc(node, port):
    server = grpc.aio.server()
    servicer = GRPCStatusServicer(node)
    status_pb2_grpc.add_StatusServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    return server
    await server.start()
    return server
