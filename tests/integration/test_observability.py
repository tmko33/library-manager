"""Observability endpoint tests."""

from httpx import AsyncClient


async def test_request_id_is_echoed(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Request-ID": "test-request-id"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-id"


async def test_request_id_is_generated_when_missing(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    generated = response.headers["X-Request-ID"]
    assert generated
    assert len(generated) == 32


async def test_readiness_reports_database(client: AsyncClient) -> None:
    response = await client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "up"}


async def test_metrics_are_exposed(client: AsyncClient) -> None:
    await client.get("/health")
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
