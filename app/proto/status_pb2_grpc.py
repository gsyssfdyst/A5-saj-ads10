import grpc
from . import status_pb2 as status__pb2

class StatusServiceServicer:
    async def GetStatus(self, request, context):
        raise NotImplementedError()

def add_StatusServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'GetStatus': grpc.aio.unary_unary_rpc_method_handler(
            servicer.GetStatus,
            request_deserializer=status__pb2.GetStatusRequest.FromString,
            response_serializer=status__pb2.GetStatusResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'status.StatusService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_generic_rpc_handlers((generic_handler,))
