import pytest
from datetime import timedelta

from app.core.security import create_access_token, verify_access_token
from python_jose_cryptodome import ExpiredSignatureError


def test_jwt_round_trip():
    token = create_access_token({"sub": "user1"}, expires_delta=timedelta(minutes=1))
    payload = verify_access_token(token)
    assert payload["sub"] == "user1"


def test_jwt_expired():
    token = create_access_token({"sub": "user2"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ExpiredSignatureError):
        verify_access_token(token)
