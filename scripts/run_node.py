import argparse
import asyncio
import os
from app.node import Node

def parse_peers(s):
    # format host:port:id; multiple separated by comma
    if not s:
        return []
    out=[]
    for part in s.split(","):
        h,p,i = part.split(":")
        out.append((h,int(p),int(i)))
    return out

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peers", default=None)
    parser.add_argument("--secret", default=os.getenv("NODE_SECRET","secret"))
    parser.add_argument("--issue-token", action="store_true", help="Emit a sample JWT and exit")
    args = parser.parse_args()
    peers = parse_peers(args.peers)
    node = Node(id=args.id, host=args.host, port=args.port, peers=peers, secret=args.secret)
    if args.issue_token:
        tok = await node.issue_token(subject=f"node-{args.id}", expires_in=3600)
        print("JWT:", tok)
        return
    await node.start()
    print(f"Node {args.id} running on {args.host}:{args.port} (gRPC on {args.port+1000})")
    # keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
