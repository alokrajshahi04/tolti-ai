from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_bytes


def random_token(nbytes: int = 32) -> bytes:
    return token_bytes(nbytes)


def hash_token(token: bytes) -> str:
    return sha256(token).hexdigest()


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def make_expiry(hours: int = 12) -> datetime:
    return now_utc() + timedelta(hours=hours)

