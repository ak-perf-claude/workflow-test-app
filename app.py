from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

tasks = []


def now_iso():
    return datetime.now(timezone.utc).isoformat()


@app.route("/")
def index():
    return render_template("index.html", tasks=tasks)


@app.route("/task/<int:task_id>")
def task_detail(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return "Task not found", 404
    return render_template("detail.html", task=task)


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    ts = now_iso()
    task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": data.get("status", "pending"),
        "created_at": ts,
        "modified_at": ts,
        "subtasks": [],
    }
    tasks.append(task)
    return jsonify(task), 201


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "not found"}), 404
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    if "title" in data:
        task["title"] = data["title"]
    if "status" in data:
        task["status"] = data["status"]
    if "description" in data:
        task["description"] = data["description"]
    task["modified_at"] = now_iso()
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == before:
        return jsonify({"error": "not found"}), 404
    return "", 204


@app.route("/api/tasks/<int:task_id>/subtasks", methods=["POST"])
def add_subtask(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "task not found"}), 404
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    subtask = {
        "id": max((s["id"] for s in task["subtasks"]), default=0) + 1,
        "title": data["title"],
        "status": data.get("status", "pending"),
    }
    task["subtasks"].append(subtask)
    task["modified_at"] = now_iso()
    return jsonify(subtask), 201


@app.route("/api/tasks/<int:task_id>/subtasks/<int:sub_id>", methods=["PATCH"])
def update_subtask(task_id, sub_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "task not found"}), 404
    subtask = next((s for s in task["subtasks"] if s["id"] == sub_id), None)
    if not subtask:
        return jsonify({"error": "subtask not found"}), 404
    data = request.get_json()
    if "title" in data:
        subtask["title"] = data["title"]
    if "status" in data:
        subtask["status"] = data["status"]
    task["modified_at"] = now_iso()
    return jsonify(subtask)


@app.route("/api/tasks/<int:task_id>/subtasks/<int:sub_id>", methods=["DELETE"])
def delete_subtask(task_id, sub_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "task not found"}), 404
    before = len(task["subtasks"])
    task["subtasks"] = [s for s in task["subtasks"] if s["id"] != sub_id]
    if len(task["subtasks"]) == before:
        return jsonify({"error": "subtask not found"}), 404
    task["modified_at"] = now_iso()
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
