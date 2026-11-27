from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

tasks = []


@app.route("/")
def index():
    return render_template("index.html", tasks=tasks)


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "status": data.get("status", "pending"),
    }
    tasks.append(task)
    return jsonify(task), 201


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
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == before:
        return jsonify({"error": "not found"}), 404
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
