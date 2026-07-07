"""Tests for internal API key authentication."""

import asyncio
import os
from unittest import mock

import pytest
from fastapi import HTTPException

from src.api.security import require_api_key


def test_require_api_key_allows_when_unconfigured() -> None:
    with mock.patch.dict(os.environ, {"AI_SERVICE_KEY": ""}, clear=False):
        asyncio.run(require_api_key(authorization=""))


def test_require_api_key_rejects_missing_header() -> None:
    with mock.patch.dict(os.environ, {"AI_SERVICE_KEY": "secret-key"}, clear=False):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(require_api_key(authorization=""))
        assert exc.value.status_code == 401


def test_require_api_key_accepts_bearer_token() -> None:
    with mock.patch.dict(os.environ, {"AI_SERVICE_KEY": "secret-key"}, clear=False):
        asyncio.run(require_api_key(authorization="Bearer secret-key"))
