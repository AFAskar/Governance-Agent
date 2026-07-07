"""FastAPI contract tests (no LLM or vector DB required)."""

import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_is_public(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_route_requires_api_key(client: TestClient) -> None:
    with mock.patch.dict(os.environ, {"AI_SERVICE_KEY": "test-key"}, clear=False):
        response = client.post(
            "/api/v1/evaluations/submit",
            data={"framework_name": "NDI"},
            files=[],
        )
    assert response.status_code == 401


def test_report_download_404_for_unknown_id(client: TestClient) -> None:
    with mock.patch.dict(os.environ, {"AI_SERVICE_KEY": "test-key"}, clear=False):
        response = client.get(
            "/api/v1/evaluations/00000000-0000-0000-0000-000000000099/report",
            headers={"Authorization": "test-key"},
        )
    assert response.status_code == 404
