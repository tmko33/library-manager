"""Unit tests for the security helpers."""

from datetime import timedelta

import pytest

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_round_trip() -> None:
    hashed = hash_password("super-secret")
    assert hashed != "super-secret"
    assert verify_password("super-secret", hashed)
    assert not verify_password("wrong-password", hashed)


def test_token_round_trip() -> None:
    token = create_access_token(42, extra_claims={"role": "member"})
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "member"


def test_expired_token_is_rejected() -> None:
    token = create_access_token(1, expires_delta=timedelta(seconds=-10))
    with pytest.raises(UnauthorizedError):
        decode_access_token(token)


def test_tampered_token_is_rejected() -> None:
    token = create_access_token(1)
    with pytest.raises(UnauthorizedError):
        decode_access_token(token + "tampered")
