import os
from .utils import TokenManager

def parse_auth_from_headers(md: dict):
    # metadata dict-like
    if not md:
        return None
    v = md.get("authorization") or md.get("Authorization") or md.get("token")
    if not v:
        return None
    if isinstance(v, (list, tuple)):
        v = v[0]
    if v.startswith("Bearer "):
        return v.split(" ", 1)[1]
    return v

def check_token(token: str, node) -> bool:
    # node can provide token_manager or static token attribute
    if not token:
        return False
    tm = getattr(node, "token_manager", None)
    if tm:
        return tm.verify_token(token) is not None
    # fallback to simple token string match
    expected = getattr(node, "token", os.getenv("NODE_TOKEN", "secret"))
    return token == expected
