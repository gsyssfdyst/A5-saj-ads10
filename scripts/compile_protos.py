"""
Gerar stubs Python + gRPC a partir de proto/monitor.proto
Uso:
  python scripts/compile_protos.py
Requer: grpcio-tools (já listado em requirements.txt)
"""
import os
import sys
from grpc_tools import protoc

proto_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "proto"))
out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "proto"))

os.makedirs(out_dir, exist_ok=True)

args = [
    "protoc",
    f"-I{proto_dir}",
    f"--python_out={out_dir}",
    f"--grpc_python_out={out_dir}",
    os.path.join(proto_dir, "monitor.proto"),
]

if __name__ == "__main__":
    rc = protoc.main(args)
    if rc != 0:
        print("protoc failed with code", rc, file=sys.stderr)
        sys.exit(rc)
    print("Protos compiled into", out_dir)
