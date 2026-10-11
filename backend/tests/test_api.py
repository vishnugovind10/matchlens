from fastapi.testclient import TestClient
from app.main import app, EVIDENCE

client = TestClient(app)


def test_health_and_observed_contract():
    assert client.get("/health").json()["status"] == "ok"
    body = client.get("/observed/latest").json()
    assert body["kind"] == "observed"
    assert body["id"] == EVIDENCE.id


def test_what_if_rejects_unknown_evidence():
    response = client.post("/what-if", json={"evidence_id": "unknown"})
    assert response.status_code == 400
