import socket
import struct
import argparse
import json

def listen(group='224.0.0.1', port=5007):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('', port))
    except Exception:
        sock.bind((group, port))
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print("Listening multicast",group,port)
    while True:
        data, addr = sock.recvfrom(65536)
        try:
            print("MSG", json.loads(data.decode()), "from", addr)
        except Exception:
            print("RAW", data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", default="224.0.0.1")
    parser.add_argument("--port", type=int, default=5007)
    args = parser.parse_args()
    listen(args.group, args.port)
