import asyncio
import time
import jwt
from typing import Optional

class LamportClock:
    def __init__(self):
        self._value = 0
        self._lock = asyncio.Lock()

    async def tick(self):
        async with self._lock:
            self._value += 1
            return self._value

    async def recv(self, other):
        async with self._lock:
            self._value = max(self._value, other) + 1
            return self._value

    async def read(self):
        async with self._lock:
            return self._value

# Adicionado: TokenManager para gerar/validar JWTs (usado pelo líder)
class TokenManager:
    def __init__(self, secret: str, algo: str = "HS256"):
        self.secret = secret
        self.algo = algo

    def create_token(self, subject: str | int, expires_in: int = 3600) -> str:
        now = int(time.time())
        payload = {"sub": str(subject), "iat": now, "exp": now + expires_in}
        return jwt.encode(payload, self.secret, algorithm=self.algo)

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algo])
            return payload
        except Exception:
            return None
