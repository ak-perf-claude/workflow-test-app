# Workflow Test App

A task tracker web application built with Flask, featuring user authentication, persistent SQLite storage, and per-user task management.

## Overview

This app lets you create an account, log in, and manage your personal tasks through a clean web interface. Each task supports a title, description, status (pending/done), subtasks, and automatic timestamps. Data persists across server restarts using SQLite.

### Features

- **User Authentication** — Signup, login, and logout with hashed passwords
- **Per-User Tasks** — Each user sees only their own tasks
- **Task Management** — Add, view, edit, toggle, and delete tasks
- **Task Description** — Optional text description for each task
- **Subtasks** — Add child tasks with independent status tracking
- **Status Tracking** — Tasks and subtasks can be marked as pending or done
- **Timestamps** — Each task records its created date and last modified date
- **Task Detail Page** — Dedicated page for viewing and editing a single task
- **Summary Bar** — Displays total, pending, and done task counts at a glance
- **Persistent Storage** — SQLite database, data survives server restarts
- **REST API** — Full CRUD API for tasks and subtasks (session-authenticated)

## Tech Stack

| Component      | Technology                         |
|----------------|------------------------------------|
| Backend        | Python 3.12, Flask 3.1.0          |
| Frontend       | HTML5, CSS3, vanilla JavaScript    |
| Database       | SQLite (via Python sqlite3)        |
| Authentication | Flask sessions, werkzeug password hashing |
| Unit Testing   | pytest 9.2.0                      |
| UI Testing     | Selenium 4.27.1, Chrome (headless) |
| CI/CD          | GitHub Actions (parallel jobs)     |

## Getting Started

### Prerequisites

- Python 3.10+
- Chrome browser (for UI tests)

### Installation

```bash
pip install -r requirements.txt
```

### Running the App

```bash
python app.py
```

The app will be available at **http://localhost:5000**. You'll be redirected to the login page — click "Sign up" to create an account.

## API Endpoints

All task/subtask API endpoints require an authenticated session (login first via the web UI).

| Method   | Endpoint                           | Auth     | Description            |
|----------|------------------------------------|----------|------------------------|
| `GET`    | `/signup`                          | Public   | Signup page            |
| `POST`   | `/signup`                          | Public   | Create account         |
| `GET`    | `/login`                           | Public   | Login page             |
| `POST`   | `/login`                           | Public   | Log in                 |
| `GET`    | `/logout`                          | Public   | Log out                |
| `GET`    | `/`                                | Required | Home page              |
| `GET`    | `/task/<id>`                       | Required | Task detail page       |
| `GET`    | `/api/tasks`                       | Required | List user's tasks      |
| `GET`    | `/api/tasks/<id>`                  | Required | Get a single task      |
| `POST`   | `/api/tasks`                       | Required | Create a task          |
| `PATCH`  | `/api/tasks/<id>`                  | Required | Update a task          |
| `DELETE` | `/api/tasks/<id>`                  | Required | Delete a task          |
| `POST`   | `/api/tasks/<id>/subtasks`         | Required | Create a subtask       |
| `PATCH`  | `/api/tasks/<id>/subtasks/<subId>` | Required | Update a subtask       |
| `DELETE` | `/api/tasks/<id>/subtasks/<subId>` | Required | Delete a subtask       |

### Example: Create a Task

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -b "session=<your-session-cookie>" \
  -d '{"title": "My first task", "description": "Some details"}'
```

## Testing

The project has two test suites: **unit tests** (Flask test client) and **UI tests** (Selenium + Chrome).

### Run Unit Tests

```bash
pytest test_app.py -v
```

43 tests covering authentication, API endpoints, per-user isolation, and error handling.

### Run UI Tests

Requires Chrome browser and ChromeDriver.

```bash
pytest test_ui.py -v
```

16 Selenium tests covering end-to-end user workflows through the browser.

### Run All Tests

```bash
pytest -v
```

### Test Summary

| Suite      | File          | Tests  | What it covers                                    |
|------------|---------------|--------|---------------------------------------------------|
| Unit       | `test_app.py` | 43     | Auth, API contracts, per-user isolation, data model |
| UI         | `test_ui.py`  | 16     | Browser workflows, navigation, forms              |
| **Total**  |               | **59** |                                                   |

See [TEST_REPORT.md](TEST_REPORT.md) for the detailed test report.

## Project Structure

```
claude-workflow-test/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI (unit + UI tests in parallel)
├── app.py                      # Flask app, auth, API routes, SQLite database
├── requirements.txt            # Python dependencies
├── test_app.py                 # Unit tests (pytest, 43 tests)
├── test_ui.py                  # UI tests (Selenium, 16 tests)
├── tasks.db                    # SQLite database (auto-created, gitignored)
├── static/
│   └── style.css               # All application styles
├── templates/
│   ├── login.html              # Login page
│   ├── signup.html             # Signup page
│   ├── index.html              # Home page — task list and summary
│   └── detail.html             # Task detail page — edit, subtasks
├── README.md                   # This file — project overview
├── DOCUMENTATION.md            # Full feature documentation
└── TEST_REPORT.md              # Detailed test report
```
