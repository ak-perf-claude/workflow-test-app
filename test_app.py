import pytest
from app import app, tasks


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        tasks.clear()
        yield client
        tasks.clear()


def create_task(client, title="Test task"):
    return client.post("/api/tasks", json={"title": title})


class TestIndex:
    def test_index_returns_html(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert b"Workflow Test App" in res.data


class TestGetTasks:
    def test_empty_list(self, client):
        res = client.get("/api/tasks")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_list_after_create(self, client):
        create_task(client, "Task A")
        create_task(client, "Task B")
        res = client.get("/api/tasks")
        data = res.get_json()
        assert len(data) == 2
        assert data[0]["title"] == "Task A"
        assert data[1]["title"] == "Task B"


class TestCreateTask:
    def test_create_returns_201(self, client):
        res = create_task(client, "My task")
        assert res.status_code == 201

    def test_create_sets_fields(self, client):
        res = create_task(client, "My task")
        data = res.get_json()
        assert data["title"] == "My task"
        assert data["status"] == "pending"
        assert data["id"] == 1
        assert "created_at" in data
        assert "modified_at" in data
        assert data["created_at"] == data["modified_at"]

    def test_create_with_custom_status(self, client):
        res = client.post("/api/tasks", json={"title": "Done task", "status": "done"})
        assert res.get_json()["status"] == "done"

    def test_create_missing_title_returns_400(self, client):
        res = client.post("/api/tasks", json={})
        assert res.status_code == 400

    def test_create_no_body_returns_400(self, client):
        res = client.post("/api/tasks", content_type="application/json")
        assert res.status_code == 400


class TestUpdateTask:
    def test_update_title(self, client):
        create_task(client, "Old title")
        res = client.patch("/api/tasks/1", json={"title": "New title"})
        assert res.status_code == 200
        assert res.get_json()["title"] == "New title"

    def test_update_status(self, client):
        create_task(client)
        res = client.patch("/api/tasks/1", json={"status": "done"})
        assert res.get_json()["status"] == "done"

    def test_update_changes_modified_at(self, client):
        create_task(client)
        original = client.get("/api/tasks").get_json()[0]["modified_at"]
        res = client.patch("/api/tasks/1", json={"status": "done"})
        assert res.get_json()["modified_at"] >= original

    def test_update_nonexistent_returns_404(self, client):
        res = client.patch("/api/tasks/999", json={"title": "Nope"})
        assert res.status_code == 404


class TestDeleteTask:
    def test_delete_returns_204(self, client):
        create_task(client)
        res = client.delete("/api/tasks/1")
        assert res.status_code == 204

    def test_delete_removes_task(self, client):
        create_task(client)
        client.delete("/api/tasks/1")
        res = client.get("/api/tasks")
        assert res.get_json() == []

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/api/tasks/999")
        assert res.status_code == 404
