from hashlib import sha512

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_ph = PasswordHasher()
DUMMY_HASH = _ph.hash("we_need_to_lost_time_here")


def get_argon2_hash(string: str) -> str:
    return _ph.hash(string)


def check_argon2_hash(hash: str | None, password: str) -> bool:
    try:
        _ph.verify(hash or DUMMY_HASH, password)
    except VerificationError, InvalidHashError:
        return False
    return hash is not None


def get_sha512_hash(string: str) -> str:
    return sha512(string.encode()).hexdigest()
