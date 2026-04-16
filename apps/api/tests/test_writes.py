import io

from fastapi.testclient import TestClient

from app.main import app


def test_upload_create_run_smoke():
    with TestClient(app) as client:
        upload_resp = client.post(
            "/api/uploads",
            files={"file": ("sample.csv", io.BytesIO(b"a,b\n1,2\n"), "text/csv")},
        )
        assert upload_resp.status_code == 200
        upload_id = upload_resp.json()["id"]

        create_resp = client.post(
            "/api/tasks",
            json={
                "uploaded_file_id": upload_id,
                "template_slug": "descriptive-report",
                "delimiter": "comma",
                "has_header": True,
                "params_json": {},
            },
        )
        assert create_resp.status_code == 200
        task_id = create_resp.json()["id"]

        list_resp = client.get("/api/tasks")
        assert list_resp.status_code == 200
        assert any(t["id"] == task_id for t in list_resp.json())

        detail_resp = client.get(f"/api/tasks/{task_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["status"] == "pending"

        run_resp = client.post(f"/api/tasks/{task_id}/run")
        assert run_resp.status_code == 200
        assert run_resp.json()["status"] in ("completed", "failed")
