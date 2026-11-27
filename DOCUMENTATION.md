# Workflow Test App — Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Features](#features)
  - [Task List (Home Page)](#task-list-home-page)
  - [Task Summary Bar](#task-summary-bar)
  - [Create Task](#create-task)
  - [Task Detail Page](#task-detail-page)
  - [Task Description](#task-description)
  - [Edit Task](#edit-task)
  - [Change Task Status](#change-task-status)
  - [Delete Task](#delete-task)
  - [Subtasks](#subtasks)
  - [Timestamps](#timestamps)
- [REST API Reference](#rest-api-reference)
  - [List All Tasks](#list-all-tasks)
  - [Get Single Task](#get-single-task)
  - [Create Task](#create-task-api)
  - [Update Task](#update-task-api)
  - [Delete Task](#delete-task-api)
  - [Create Subtask](#create-subtask-api)
  - [Update Subtask](#update-subtask-api)
  - [Delete Subtask](#delete-subtask-api)
- [Pages & Routes](#pages--routes)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
  - [UI Tests (Selenium)](#ui-tests-selenium)
  - [Running Tests](#running-tests)
  - [Test Coverage by Feature](#test-coverage-by-feature)
  - [Test Architecture](#test-architecture)
- [CI/CD](#cicd)

---

## Overview

Workflow Test App is a task tracker web application built with Flask. It provides a clean web interface and a REST API for managing tasks with full CRUD (Create, Read, Update, Delete) operations. Each task supports a title, description, status tracking, subtasks, and automatic timestamps.

## Architecture

The app follows a simple server-rendered architecture with client-side enhancements:

```
Browser ──► Flask (app.py) ──► In-Memory Task List
  │              │
  │              ├── GET /             → renders index.html (task list)
  │              ├── GET /task/<id>    → renders detail.html (task detail)
  │              ├── /api/tasks/*      → JSON REST API (tasks)
  │              └── /api/tasks/*/subtasks/* → JSON REST API (subtasks)
  │
  ├── static/style.css  (styling)
  └── vanilla JavaScript (async fetch for API calls)
```

- **Server-side rendering**: Pages are rendered using Jinja2 templates with initial data from the server.
- **Client-side updates**: After the initial load, JavaScript uses `fetch()` to call the REST API and updates the DOM without full page reloads.
- **In-memory storage**: Tasks are stored in a Python list. Data resets when the server restarts.

## Data Model

### Task

Each task is a dictionary with the following fields:

| Field         | Type   | Description                                      |
|---------------|--------|--------------------------------------------------|
| `id`          | int    | Auto-incremented unique identifier               |
| `title`       | string | The task title (required)                        |
| `description` | string | Optional text description (default: `""`)        |
| `status`      | string | Either `"pending"` or `"done"` (default: `"pending"`) |
| `created_at`  | string | ISO 8601 UTC timestamp, set at creation          |
| `modified_at` | string | ISO 8601 UTC timestamp, updated on every change  |
| `subtasks`    | array  | List of subtask objects (default: `[]`)          |

**Example task object:**

```json
{
  "id": 1,
  "title": "Review pull request",
  "description": "Check the auth module changes",
  "status": "pending",
  "created_at": "2026-11-27T09:14:58.435252+00:00",
  "modified_at": "2026-11-27T09:14:58.435252+00:00",
  "subtasks": [
    { "id": 1, "title": "Review code", "status": "done" },
    { "id": 2, "title": "Run tests", "status": "pending" }
  ]
}
```

### Subtask

Each subtask is a nested object within a task:

| Field    | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| `id`     | int    | Auto-incremented within the parent task           |
| `title`  | string | The subtask title (required)                     |
| `status` | string | Either `"pending"` or `"done"` (default: `"pending"`) |

---

## Features

### Task List (Home Page)

**URL:** `/`

The home page displays all tasks in a card-based list. Each task card shows:

- **Status badge** — Color-coded label (`pending` in amber, `done` in green)
- **Title** — Clickable link that navigates to the task's detail page
- **Description preview** — First 80 characters of the description (if present)
- **Subtask count** — "X/Y subtasks done" indicator (if subtasks exist)
- **Created date** — When the task was created (formatted in the user's locale)
- **Modified date** — When the task was last updated
- **Toggle button** — Switches the task status between pending and done
- **Delete button** — Removes the task from the list

The list updates dynamically without a full page reload after any action.

### Task Summary Bar

Displayed above the task list when at least one task exists. Shows:

- **Total** — Total number of tasks
- **Pending** — Count of tasks with status `"pending"` (amber)
- **Done** — Count of tasks with status `"done"` (green)

The summary bar updates automatically whenever tasks are added, modified, or deleted.

### Create Task

A form at the top of the home page with a text input and "Add" button. Enter a title and submit to create a new task. The task is created with:

- Description: empty
- Status: `pending`
- Subtasks: empty list
- Timestamps: `created_at` and `modified_at` set to the current UTC time

The task list and summary bar update immediately after creation.

### Task Detail Page

**URL:** `/task/<id>`

A dedicated page for viewing and managing a single task. Accessed by clicking a task's title on the home page. The detail page includes:

- **Back link** — Returns to the task list
- **Status badge** — Shows current status with color coding
- **Task heading** — Displays the task ID (e.g., "Task #1")
- **Title input** — Editable text field pre-filled with the current title
- **Description textarea** — Editable multi-line text area for the task description
- **Status dropdown** — Select between "Pending" and "Done"
- **Timestamps** — Created and modified dates displayed below the form
- **Save Changes button** — Saves edits to title, description, and status
- **Delete Task button** — Deletes the task after confirmation
- **Subtasks section** — Add, toggle, and delete subtasks (see below)

After saving, a green success message appears and the page updates in-place (no reload). After deleting, the user is redirected to the home page.

### Task Description

Each task has an optional text description field:

- Editable via a textarea on the detail page
- Saved along with title and status when clicking "Save Changes"
- Shown as a truncated preview (first 80 characters) on the home page task cards
- Defaults to an empty string when not provided

### Edit Task

Tasks can be edited in two ways:

1. **From the detail page** — Change the title, description, or status and click "Save Changes". All fields are sent to the API in a single PATCH request.
2. **Via the API** — Send a PATCH request with any combination of `title`, `description`, and/or `status` fields.

Every edit updates the `modified_at` timestamp automatically.

### Change Task Status

Task status can be toggled in two ways:

1. **From the home page** — Click the "Toggle" button on a task card to switch between `pending` and `done`.
2. **From the detail page** — Select the desired status from the dropdown and click "Save Changes".

### Delete Task

Tasks can be deleted in two ways:

1. **From the home page** — Click the "Delete" button on a task card. The task is removed immediately.
2. **From the detail page** — Click the "Delete Task" button. A confirmation dialog appears ("Are you sure you want to delete this task?"). On confirmation, the task is deleted and the user is redirected to the home page.

### Subtasks

Each task can have zero or more subtasks, each with its own status. Subtasks are managed from the task detail page.

**Adding a subtask:**
- A form below the "Subtasks" heading with a text input and "Add" button
- Enter a subtask title and click Add — it appears in the list immediately

**Toggling subtask status:**
- Each subtask row has a "Toggle" button to switch between `pending` and `done`
- Done subtasks display with strikethrough text styling

**Deleting a subtask:**
- Each subtask row has a "Delete" button to remove it

**Subtask indicators on home page:**
- When a task has subtasks, a "X/Y subtasks done" count appears on its card

**All subtask operations** (create, toggle, delete) automatically update the parent task's `modified_at` timestamp.

When no subtasks exist, a "No subtasks yet." placeholder is displayed.

### Timestamps

Every task records two timestamps in ISO 8601 UTC format:

- **Created date** — Set once when the task is created. Never changes.
- **Modified date** — Initially the same as the created date. Updated to the current UTC time on every PATCH request (title, description, or status change) and on every subtask operation.

Timestamps are displayed in the user's local timezone and format using `toLocaleString()`.

---

## REST API Reference

Base URL: `http://localhost:5000`

All API endpoints return JSON. Request bodies must be sent as `Content-Type: application/json`.

### List All Tasks

```
GET /api/tasks
```

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Review pull request",
    "description": "Check the auth module",
    "status": "pending",
    "created_at": "2026-11-27T09:14:58.435252+00:00",
    "modified_at": "2026-11-27T09:14:58.435252+00:00",
    "subtasks": []
  }
]
```

Returns an empty array `[]` when there are no tasks.

### Get Single Task

```
GET /api/tasks/<id>
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "title": "Review pull request",
  "description": "Check the auth module",
  "status": "pending",
  "created_at": "2026-11-27T09:14:58.435252+00:00",
  "modified_at": "2026-11-27T09:14:58.435252+00:00",
  "subtasks": [
    { "id": 1, "title": "Review code", "status": "done" }
  ]
}
```

**Error:** `404 Not Found` — Task with the given ID does not exist.

```json
{ "error": "not found" }
```

<a id="create-task-api"></a>
### Create Task

```
POST /api/tasks
```

**Request body:**

| Field         | Type   | Required | Description                        |
|---------------|--------|----------|------------------------------------|
| `title`       | string | Yes      | The task title                     |
| `description` | string | No       | Task description (default: `""`)   |
| `status`      | string | No       | `"pending"` (default) or `"done"`  |

**Example:**

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My new task", "description": "Some details"}'
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "title": "My new task",
  "description": "Some details",
  "status": "pending",
  "created_at": "2026-11-27T09:14:58.435252+00:00",
  "modified_at": "2026-11-27T09:14:58.435252+00:00",
  "subtasks": []
}
```

**Error:** `400 Bad Request` — Missing `title` field.

```json
{ "error": "title is required" }
```

<a id="update-task-api"></a>
### Update Task

```
PATCH /api/tasks/<id>
```

**Request body** (all fields optional):

| Field         | Type   | Description              |
|---------------|--------|--------------------------|
| `title`       | string | New task title           |
| `description` | string | New task description     |
| `status`      | string | `"pending"` or `"done"`  |

**Example:**

```bash
curl -X PATCH http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "description": "New details", "status": "done"}'
```

**Response:** `200 OK` — Returns the updated task. The `modified_at` field is updated automatically.

**Error:** `404 Not Found` — Task with the given ID does not exist.

<a id="delete-task-api"></a>
### Delete Task

```
DELETE /api/tasks/<id>
```

**Example:**

```bash
curl -X DELETE http://localhost:5000/api/tasks/1
```

**Response:** `204 No Content` — Task deleted successfully (empty body).

**Error:** `404 Not Found` — Task with the given ID does not exist.

<a id="create-subtask-api"></a>
### Create Subtask

```
POST /api/tasks/<taskId>/subtasks
```

**Request body:**

| Field    | Type   | Required | Description                        |
|----------|--------|----------|------------------------------------|
| `title`  | string | Yes      | The subtask title                  |
| `status` | string | No       | `"pending"` (default) or `"done"`  |

**Example:**

```bash
curl -X POST http://localhost:5000/api/tasks/1/subtasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Step one"}'
```

**Response:** `201 Created`

```json
{ "id": 1, "title": "Step one", "status": "pending" }
```

**Errors:**
- `404 Not Found` — Parent task does not exist.
- `400 Bad Request` — Missing `title` field.

Updates the parent task's `modified_at`.

<a id="update-subtask-api"></a>
### Update Subtask

```
PATCH /api/tasks/<taskId>/subtasks/<subId>
```

**Request body** (all fields optional):

| Field    | Type   | Description              |
|----------|--------|--------------------------|
| `title`  | string | New subtask title        |
| `status` | string | `"pending"` or `"done"`  |

**Example:**

```bash
curl -X PATCH http://localhost:5000/api/tasks/1/subtasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

**Response:** `200 OK` — Returns the updated subtask.

**Error:** `404 Not Found` — Parent task or subtask does not exist.

Updates the parent task's `modified_at`.

<a id="delete-subtask-api"></a>
### Delete Subtask

```
DELETE /api/tasks/<taskId>/subtasks/<subId>
```

**Example:**

```bash
curl -X DELETE http://localhost:5000/api/tasks/1/subtasks/1
```

**Response:** `204 No Content` — Subtask deleted successfully.

**Error:** `404 Not Found` — Parent task or subtask does not exist.

Updates the parent task's `modified_at`.

---

## Pages & Routes

| Route                               | Method | Description                              |
|-------------------------------------|--------|------------------------------------------|
| `/`                                 | GET    | Home page — task list with summary bar   |
| `/task/<id>`                        | GET    | Task detail page — edit, subtasks        |
| `/api/tasks`                        | GET    | API — list all tasks                     |
| `/api/tasks`                        | POST   | API — create a new task                  |
| `/api/tasks/<id>`                   | GET    | API — get a single task                  |
| `/api/tasks/<id>`                   | PATCH  | API — update a task                      |
| `/api/tasks/<id>`                   | DELETE | API — delete a task                      |
| `/api/tasks/<id>/subtasks`          | POST   | API — create a subtask                   |
| `/api/tasks/<id>/subtasks/<subId>`  | PATCH  | API — update a subtask                   |
| `/api/tasks/<id>/subtasks/<subId>`  | DELETE | API — delete a subtask                   |

---

## Project Structure

```
claude-workflow-test/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── app.py                      # Flask application and all API routes
├── requirements.txt            # Python dependencies
├── test_app.py                 # Unit tests (pytest, 32 tests)
├── test_ui.py                  # UI tests (Selenium + Chrome, 16 tests)
├── static/
│   └── style.css               # All application styles
├── templates/
│   ├── index.html              # Home page — task list and summary
│   └── detail.html             # Task detail page — edit, subtasks
├── README.md                   # Project overview and quick start
├── DOCUMENTATION.md            # This file — full feature documentation
└── TEST_REPORT.md              # Detailed test report with results
```

## Tech Stack

| Component      | Technology                        |
|----------------|-----------------------------------|
| Backend        | Python 3.12, Flask 3.1.0         |
| Frontend       | HTML5, CSS3, vanilla JavaScript   |
| Templating     | Jinja2 (via Flask)               |
| Unit Testing   | pytest 9.2.0                     |
| UI Testing     | Selenium 4.27.1, Chrome (headless) |
| CI/CD          | GitHub Actions                   |
| Storage        | In-memory Python list            |

## Getting Started

### Prerequisites

- Python 3.10 or later
- Chrome browser (for UI tests only)

### Installation

```bash
pip install -r requirements.txt
```

### Running the App

```bash
python app.py
```

The app starts at **http://localhost:5000** with debug mode enabled.

---

## Testing

The project maintains two test suites that together provide 48 tests covering all features at both the API and browser levels.

### Unit Tests

**File:** `test_app.py`
**Framework:** pytest with Flask test client
**Tests:** 32

Unit tests validate all API endpoints, data model fields, status codes, and error handling. Each test runs in isolation with a clean in-memory task list. No browser or external dependencies are needed.

| Test Class        | Tests | Coverage                                                     |
|-------------------|-------|--------------------------------------------------------------|
| TestIndex         | 1     | Home page renders with correct content                       |
| TestGetTasks      | 2     | List empty, list after creating tasks                        |
| TestGetTask       | 2     | Get existing task with all fields, 404 for nonexistent       |
| TestDetailPage    | 2     | Detail page renders with task data, 404 for nonexistent      |
| TestCreateTask    | 7     | Create with defaults, description, custom status, validation |
| TestUpdateTask    | 5     | Update title, status, description, modified_at, 404          |
| TestDeleteTask    | 3     | Delete returns 204, removes from list, 404                   |
| TestSubtasks      | 10    | Create/toggle/update/delete subtasks, parent timestamp       |

### UI Tests (Selenium)

**File:** `test_ui.py`
**Framework:** pytest + Selenium WebDriver
**Browser:** Chrome (headless mode)
**Tests:** 16

UI tests automate a real browser against a live Flask server to verify end-to-end user workflows. The Flask app runs in a background thread on port 5111 during testing. Each test gets a fresh browser instance.

| Test Class       | Tests | Coverage                                                    |
|------------------|-------|-------------------------------------------------------------|
| TestHomePage     | 6     | Page load, create task, summary bar, toggle, delete, navigation |
| TestDetailPage   | 6     | View task, edit title, edit description, change status, delete, back link |
| TestSubtasksUI   | 4     | Add subtask, toggle subtask, delete subtask, empty placeholder |

### Running Tests

**Unit tests only:**

```bash
pytest test_app.py -v
```

**UI tests only** (requires Chrome):

```bash
pytest test_ui.py -v
```

**All tests:**

```bash
pytest -v
```

**With output summary:**

```bash
pytest --tb=short
```

### Test Coverage by Feature

| Feature                    | Unit Tests | UI Tests | Total |
|----------------------------|-----------|----------|-------|
| Home page rendering        | 1         | 1        | 2     |
| Task list (GET all)        | 2         | 1        | 3     |
| Task detail (GET single)   | 2         | 1        | 3     |
| Detail page rendering      | 2         | 2        | 4     |
| Create task                | 7         | 1        | 8     |
| Update task (title)        | 1         | 1        | 2     |
| Update task (status)       | 2         | 1        | 3     |
| Update task (description)  | 1         | 1        | 2     |
| Update task (modified_at)  | 1         | —        | 1     |
| Delete task                | 3         | 2        | 5     |
| Navigation (links/back)    | —         | 2        | 2     |
| Summary bar                | —         | 1        | 1     |
| Subtask create             | 3         | 1        | 4     |
| Subtask toggle status      | 1         | 1        | 2     |
| Subtask update title       | 1         | —        | 1     |
| Subtask delete             | 2         | 1        | 3     |
| Subtask in parent response | 1         | —        | 1     |
| Subtask parent timestamp   | 1         | —        | 1     |
| Subtask empty placeholder  | —         | 1        | 1     |
| **Total**                  | **32**    | **16**   | **48**|

### Test Architecture

| Aspect           | Unit Tests (`test_app.py`)      | UI Tests (`test_ui.py`)               |
|------------------|---------------------------------|---------------------------------------|
| What is tested   | API contracts, data model       | User-facing workflows in a browser    |
| Browser needed   | No                              | Yes (Chrome)                          |
| Server           | Flask test client (in-process)  | Live Flask server (background thread) |
| Speed            | Fast (~0.03s per test)          | Slower (~7.6s per test)               |
| Isolation        | `tasks` list reset per test     | Fresh browser + task reset per test   |
| Catches          | Backend logic, validation, 404s | UI rendering, JS bugs, navigation     |
| Misses           | Frontend JS issues              | Internal API edge cases               |

---

## CI/CD

GitHub Actions runs the unit test suite automatically on every push to `main` and on pull requests. The workflow is defined in `.github/workflows/ci.yml` and:

1. Checks out the code
2. Sets up Python 3.12
3. Installs dependencies
4. Runs `pytest test_app.py -v`

UI tests (`test_ui.py`) require Chrome and are intended for local development. To run them in CI, add a Chrome/ChromeDriver setup step to the workflow.
