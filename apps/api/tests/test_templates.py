from fastapi.testclient import TestClient

from app.main import app


def test_list_templates_smoke():
    client = TestClient(app)
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(item["slug"] == "descriptive-report" for item in data)
