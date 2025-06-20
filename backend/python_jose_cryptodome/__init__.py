"""Lightweight drop-in replacement for python-jose using PyJWT."""
from jwt import (
    encode as _encode,
    decode as _decode,
    PyJWTError as JWTError,
    ExpiredSignatureError,
    InvalidTokenError as JWTClaimsError,
)


class _JWT:
    @staticmethod
    def encode(claims, key, algorithm="HS256", headers=None, access_token=None):
        return _encode(claims, key, algorithm=algorithm, headers=headers)

    @staticmethod
    def decode(token, key, algorithms=None, options=None, **kwargs):
        return _decode(token, key, algorithms=algorithms, options=options or {})


jwt = _JWT()

__all__ = ["jwt", "JWTError", "ExpiredSignatureError", "JWTClaimsError"]
