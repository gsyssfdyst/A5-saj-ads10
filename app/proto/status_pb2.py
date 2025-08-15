# Generated minimal protobuf message classes for GetStatusResponse and request (empty).
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection

DESCRIPTOR = _descriptor.FileDescriptor(
  name='status.proto',
  package='status',
  syntax='proto3',
)

_GETSTATUSREQUEST = _descriptor.Descriptor(
  name='GetStatusRequest',
  full_name='status.GetStatusRequest',
  filename=None,
  containing_type=None,
  fields=[],
  nested_types=[],
  enum_types=[],
)

_GETSTATUSRESPONSE = _descriptor.Descriptor(
  name='GetStatusResponse',
  full_name='status.GetStatusResponse',
  filename=None,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(name='id', full_name='status.GetStatusResponse.id', index=0, number=1, type=5, cpp_type=1, label=1),
    _descriptor.FieldDescriptor(name='leader', full_name='status.GetStatusResponse.leader', index=1, number=2, type=9, cpp_type=9, label=1),
    _descriptor.FieldDescriptor(name='lamport', full_name='status.GetStatusResponse.lamport', index=2, number=3, type=3, cpp_type=2, label=1),
    _descriptor.FieldDescriptor(name='state', full_name='status.GetStatusResponse.state', index=3, number=4, type=9, cpp_type=9, label=1),
    _descriptor.FieldDescriptor(name='cpu', full_name='status.GetStatusResponse.cpu', index=4, number=5, type=1, cpp_type=5, label=1),
    _descriptor.FieldDescriptor(name='memory', full_name='status.GetStatusResponse.memory', index=5, number=6, type=1, cpp_type=5, label=1),
    _descriptor.FieldDescriptor(name='uptime', full_name='status.GetStatusResponse.uptime', index=6, number=7, type=3, cpp_type=2, label=1),
  ],
  nested_types=[],
  enum_types=[],
)

DESCRIPTOR.message_types_by_name['GetStatusRequest'] = _GETSTATUSREQUEST
DESCRIPTOR.message_types_by_name['GetStatusResponse'] = _GETSTATUSRESPONSE

GetStatusRequest = _reflection.GeneratedProtocolMessageType('GetStatusRequest', (_message.Message,), {
  'DESCRIPTOR': _GETSTATUSREQUEST,
  '__module__': 'app.proto.status_pb2'
})
GetStatusResponse = _reflection.GeneratedProtocolMessageType('GetStatusResponse', (_message.Message,), {
  'DESCRIPTOR': _GETSTATUSRESPONSE,
  '__module__': 'app.proto.status_pb2'
})
