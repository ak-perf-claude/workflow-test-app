import pytest
import app as app_module
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        app_module.tasks = []
        yield client
        app_module.tasks = []


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


class TestGetTask:
    def test_get_existing_task(self, client):
        create_task(client, "Detail task")
        res = client.get("/api/tasks/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["id"] == 1
        assert data["title"] == "Detail task"
        assert data["status"] == "pending"
        assert "created_at" in data
        assert "modified_at" in data

    def test_get_nonexistent_returns_404(self, client):
        res = client.get("/api/tasks/999")
        assert res.status_code == 404


class TestDetailPage:
    def test_detail_page_returns_html(self, client):
        create_task(client, "Detail view task")
        res = client.get("/task/1")
        assert res.status_code == 200
        assert b"Detail view task" in res.data
        assert b"Task #1" in res.data

    def test_detail_page_nonexistent_returns_404(self, client):
        res = client.get("/task/999")
        assert res.status_code == 404


class TestCreateTask:
    def test_create_returns_201(self, client):
        res = create_task(client, "My task")
        assert res.status_code == 201

    def test_create_sets_fields(self, client):
        res = create_task(client, "My task")
        data = res.get_json()
        assert data["title"] == "My task"
        assert data["description"] == ""
        assert data["status"] == "pending"
        assert data["id"] == 1
        assert data["subtasks"] == []
        assert "created_at" in data
        assert "modified_at" in data
        assert data["created_at"] == data["modified_at"]

    def test_create_with_custom_status(self, client):
        res = client.post("/api/tasks", json={"title": "Done task", "status": "done"})
        assert res.get_json()["status"] == "done"

    def test_create_with_description(self, client):
        res = client.post("/api/tasks", json={"title": "Task", "description": "Some details"})
        assert res.get_json()["description"] == "Some details"

    def test_create_default_description(self, client):
        res = create_task(client)
        assert res.get_json()["description"] == ""

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

    def test_update_description(self, client):
        create_task(client)
        res = client.patch("/api/tasks/1", json={"description": "Updated desc"})
        assert res.get_json()["description"] == "Updated desc"

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


class TestSubtasks:
    def test_create_subtask(self, client):
        create_task(client)
        res = client.post("/api/tasks/1/subtasks", json={"title": "Sub 1"})
        assert res.status_code == 201
        data = res.get_json()
        assert data["title"] == "Sub 1"
        assert data["status"] == "pending"
        assert data["id"] == 1

    def test_create_subtask_missing_title(self, client):
        create_task(client)
        res = client.post("/api/tasks/1/subtasks", json={})
        assert res.status_code == 400

    def test_create_subtask_nonexistent_task(self, client):
        res = client.post("/api/tasks/999/subtasks", json={"title": "Sub"})
        assert res.status_code == 404

    def test_subtask_in_task_response(self, client):
        create_task(client)
        client.post("/api/tasks/1/subtasks", json={"title": "Sub 1"})
        client.post("/api/tasks/1/subtasks", json={"title": "Sub 2"})
        res = client.get("/api/tasks/1")
        data = res.get_json()
        assert len(data["subtasks"]) == 2
        assert data["subtasks"][0]["title"] == "Sub 1"

    def test_toggle_subtask_status(self, client):
        create_task(client)
        client.post("/api/tasks/1/subtasks", json={"title": "Sub 1"})
        res = client.patch("/api/tasks/1/subtasks/1", json={"status": "done"})
        assert res.status_code == 200
        assert res.get_json()["status"] == "done"

    def test_update_subtask_title(self, client):
        create_task(client)
        client.post("/api/tasks/1/subtasks", json={"title": "Old"})
        res = client.patch("/api/tasks/1/subtasks/1", json={"title": "New"})
        assert res.get_json()["title"] == "New"

    def test_update_nonexistent_subtask(self, client):
        create_task(client)
        res = client.patch("/api/tasks/1/subtasks/999", json={"status": "done"})
        assert res.status_code == 404

    def test_delete_subtask(self, client):
        create_task(client)
        client.post("/api/tasks/1/subtasks", json={"title": "Sub 1"})
        res = client.delete("/api/tasks/1/subtasks/1")
        assert res.status_code == 204
        task = client.get("/api/tasks/1").get_json()
        assert len(task["subtasks"]) == 0

    def test_delete_nonexistent_subtask(self, client):
        create_task(client)
        res = client.delete("/api/tasks/1/subtasks/999")
        assert res.status_code == 404

    def test_subtask_updates_parent_modified_at(self, client):
        create_task(client)
        original = client.get("/api/tasks/1").get_json()["modified_at"]
        client.post("/api/tasks/1/subtasks", json={"title": "Sub"})
        updated = client.get("/api/tasks/1").get_json()["modified_at"]
        assert updated >= original
