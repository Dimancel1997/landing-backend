import os

os.environ["STORAGE_DIR"] = "/tmp/landing_backend_test_storage"
os.environ["LOG_DIR"] = "/tmp/landing_backend_test_logs"
os.environ["REQUEST_LOG_FILE"] = "/tmp/landing_backend_test_logs/requests.log"
os.environ["APP_LOG_FILE"] = "/tmp/landing_backend_test_logs/app.log"
os.environ["RATE_LIMIT_MAX_REQUESTS"] = "100"
os.environ["OPENAI_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

VALID_PAYLOAD = {
    "name": "Иван Петров",
    "phone": "+7 999 123-45-67",
    "email": "ivan@example.com",
    "comment": "Здравствуйте! Хочу узнать стоимость разработки лендинга.",
}


def test_health() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_contact_success_with_local_fallback() -> None:
    response = client.post("/api/contact", json=VALID_PAYLOAD)

    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "accepted"
    assert data["ai_analysis"] is not None
    assert data["ai_analysis"]["is_available"] is False
    assert data["ai_analysis"]["category"] == "pricing"
    assert data["ai_analysis"]["suggested_reply"]


def test_contact_validation_error() -> None:
    response = client.post(
        "/api/contact",
        json={
            "name": "A1",
            "phone": "123",
            "email": "bad",
            "comment": "short",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


def test_metrics() -> None:
    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert "total_contacts" in response.json()
