import hmac
from _sha3 import sha3_512
from typing import Optional


def hash_string(value: str) -> bytes:
    s = sha3_512()
    if value is None:
        value = ""
    s.update(value.encode())
    return s.digest()


def compare_hash(a: Optional[bytes], b: Optional[bytes]) -> bool:
    if a is None:
        a = b""
    if b is None:
        b = b""
    return hmac.compare_digest(a, b)
