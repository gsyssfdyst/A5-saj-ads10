import socket
import struct
import json

class MulticastSender:
    def __init__(self, group='224.0.0.1', port=5007, ttl=2):
        self.group = group
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def send(self, obj):
        try:
            data = json.dumps(obj).encode()
            self.sock.sendto(data, (self.group, self.port))
        except Exception:
            pass
