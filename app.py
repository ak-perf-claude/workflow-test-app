import sqlite3
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, g, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["DATABASE"] = "tasks.db"
app.secret_key = "workflow-test-app-secret-key-change-in-production"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        );
    """)
    db.close()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def task_to_dict(row):
    db = get_db()
    subtasks = db.execute(
        "SELECT id, title, status FROM subtasks WHERE task_id = ? ORDER BY id",
        (row["id"],),
    ).fetchall()
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"],
        "modified_at": row["modified_at"],
        "subtasks": [dict(s) for s in subtasks],
    }


# --- Auth routes ---

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")
    if not username or not password:
        return render_template("signup.html", error="Username and password are required.")
    if len(password) < 4:
        return render_template("signup.html", error="Password must be at least 4 characters.")
    if password != confirm:
        return render_template("signup.html", error="Passwords do not match.")
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return render_template("signup.html", error="Username already taken.")
    db.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), now_iso()),
    )
    db.commit()
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        return render_template("login.html", error="Username and password are required.")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid username or password.")
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- Page routes ---

@app.route("/")
@login_required
def index():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY id", (session["user_id"],)
    ).fetchall()
    tasks = [task_to_dict(r) for r in rows]
    return render_template("index.html", tasks=tasks)


@app.route("/task/<int:task_id>")
@login_required
def task_detail(task_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not row:
        return "Task not found", 404
    return render_template("detail.html", task=task_to_dict(row))


# --- Task API ---

@app.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY id", (session["user_id"],)
    ).fetchall()
    return jsonify([task_to_dict(r) for r in rows])


@app.route("/api/tasks", methods=["POST"])
@login_required
def add_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    ts = now_iso()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO tasks (user_id, title, description, status, created_at, modified_at) VALUES (?, ?, ?, ?, ?, ?)",
        (session["user_id"], data["title"], data.get("description", ""), data.get("status", "pending"), ts, ts),
    )
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(task_to_dict(row)), 201


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(task_to_dict(row))


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
@login_required
def update_task(task_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    title = data.get("title", row["title"])
    status = data.get("status", row["status"])
    description = data.get("description", row["description"])
    ts = now_iso()
    db.execute(
        "UPDATE tasks SET title = ?, status = ?, description = ?, modified_at = ? WHERE id = ?",
        (title, status, description, ts, task_id),
    )
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return jsonify(task_to_dict(row))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return "", 204


# --- Subtask API ---

@app.route("/api/tasks/<int:task_id>/subtasks", methods=["POST"])
@login_required
def add_subtask(task_id):
    db = get_db()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not task:
        return jsonify({"error": "task not found"}), 404
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    cursor = db.execute(
        "INSERT INTO subtasks (task_id, title, status) VALUES (?, ?, ?)",
        (task_id, data["title"], data.get("status", "pending")),
    )
    db.execute("UPDATE tasks SET modified_at = ? WHERE id = ?", (now_iso(), task_id))
    db.commit()
    sub = db.execute("SELECT id, title, status FROM subtasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(sub)), 201


@app.route("/api/tasks/<int:task_id>/subtasks/<int:sub_id>", methods=["PATCH"])
@login_required
def update_subtask(task_id, sub_id):
    db = get_db()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not task:
        return jsonify({"error": "task not found"}), 404
    sub = db.execute(
        "SELECT * FROM subtasks WHERE id = ? AND task_id = ?", (sub_id, task_id)
    ).fetchone()
    if not sub:
        return jsonify({"error": "subtask not found"}), 404
    data = request.get_json()
    title = data.get("title", sub["title"])
    status = data.get("status", sub["status"])
    db.execute("UPDATE subtasks SET title = ?, status = ? WHERE id = ?", (title, status, sub_id))
    db.execute("UPDATE tasks SET modified_at = ? WHERE id = ?", (now_iso(), task_id))
    db.commit()
    sub = db.execute("SELECT id, title, status FROM subtasks WHERE id = ?", (sub_id,)).fetchone()
    return jsonify(dict(sub))


@app.route("/api/tasks/<int:task_id>/subtasks/<int:sub_id>", methods=["DELETE"])
@login_required
def delete_subtask(task_id, sub_id):
    db = get_db()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if not task:
        return jsonify({"error": "task not found"}), 404
    sub = db.execute(
        "SELECT * FROM subtasks WHERE id = ? AND task_id = ?", (sub_id, task_id)
    ).fetchone()
    if not sub:
        return jsonify({"error": "subtask not found"}), 404
    db.execute("DELETE FROM subtasks WHERE id = ?", (sub_id,))
    db.execute("UPDATE tasks SET modified_at = ? WHERE id = ?", (now_iso(), task_id))
    db.commit()
    return "", 204


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
