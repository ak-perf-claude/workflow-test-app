# Workflow Test App

A simple task tracker web application built with Flask for testing Claude workflows.

## Overview

This app lets you create, view, update, and delete tasks through a clean web interface. Each task tracks its title, description, status (pending/done), subtasks, and timestamps.

### Features

- **Task Management** — Add, view, edit, toggle, and delete tasks
- **Task Description** — Optional text description for each task
- **Subtasks** — Add child tasks with independent status tracking
- **Status Tracking** — Tasks and subtasks can be marked as pending or done
- **Timestamps** — Each task records its created date and last modified date
- **Task Detail Page** — Dedicated page for viewing and editing a single task
- **Summary Bar** — Displays total, pending, and done task counts at a glance
- **REST API** — Full CRUD API for tasks and subtasks

## Tech Stack

- **Backend:** Python 3.12 / Flask 3.1.0
- **Frontend:** HTML5, CSS3, vanilla JavaScript
- **Testing:** pytest (unit), Selenium WebDriver (UI)
- **CI/CD:** GitHub Actions
- **Storage:** In-memory (resets on server restart)

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

The app will be available at **http://localhost:5000**.

## API Endpoints

| Method   | Endpoint                           | Description            |
|----------|------------------------------------|------------------------|
| `GET`    | `/`                                | Home page              |
| `GET`    | `/task/<id>`                       | Task detail page       |
| `GET`    | `/api/tasks`                       | List all tasks         |
| `GET`    | `/api/tasks/<id>`                  | Get a single task      |
| `POST`   | `/api/tasks`                       | Create a task          |
| `PATCH`  | `/api/tasks/<id>`                  | Update a task          |
| `DELETE` | `/api/tasks/<id>`                  | Delete a task          |
| `POST`   | `/api/tasks/<id>/subtasks`         | Create a subtask       |
| `PATCH`  | `/api/tasks/<id>/subtasks/<subId>` | Update a subtask       |
| `DELETE` | `/api/tasks/<id>/subtasks/<subId>` | Delete a subtask       |

### Example: Create a Task

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "Some details"}'
```

### Example: Add a Subtask

```bash
curl -X POST http://localhost:5000/api/tasks/1/subtasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Step one"}'
```

## Testing

The project has two test suites: **unit tests** (Flask test client) and **UI tests** (Selenium + Chrome).

### Run Unit Tests

```bash
pytest test_app.py -v
```

32 tests covering all API endpoints, data model validation, and error handling.

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

| Suite      | File          | Tests | What it covers                          |
|------------|---------------|-------|-----------------------------------------|
| Unit       | `test_app.py` | 32    | API contracts, status codes, data model |
| UI         | `test_ui.py`  | 16    | Browser workflows, navigation, forms    |
| **Total**  |               | **48**|                                         |

See [TEST_REPORT.md](TEST_REPORT.md) for the full test report with individual test details.

## Project Structure

```
claude-workflow-test/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── app.py                      # Flask application and all API routes
├── requirements.txt            # Python dependencies
├── test_app.py                 # Unit tests (pytest, 32 tests)
├── test_ui.py                  # UI tests (Selenium, 16 tests)
├── static/
│   └── style.css               # All application styles
├── templates/
│   ├── index.html              # Home page — task list and summary
│   └── detail.html             # Task detail page — edit, subtasks
├── README.md                   # This file — project overview
├── DOCUMENTATION.md            # Full feature documentation
└── TEST_REPORT.md              # Detailed test report
```
